#!/usr/bin/env python3
"""Chaos Monkey sound layer v2 (mix_v2): the same cues, raised by measurement, plus the cues for the v3 action, ending B.

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    $PY tools/audio/sfx/build_v2.py            # -> media/sound/mix_v2.wav, layer_v2.wav, work/sound/qa_v2.json, docs/SOUND.md "v2" block

  v4 (preview_v4, G5 "Yes" one beat late; see docs/SOUND.md "v3 mix"):
    S="inputs/Chaos Monkey - reformatted for duet - v4 yes late.wav"
    CM_SONG="$S" CM_VOCALS=work/stems/vocals_v4.wav CM_TIMING=analysis/timing_v4.json \
      $PY tools/audio/sfx/build_v2.py --tag v3 --reuse-layer media/sound/layer_v2.wav
        -> media/sound/mix_v3.wav = the approved mix_v2 + (edited song - original song): the v2 layer unchanged, ending B re-made
           from the edited song; work/sound/qa_v3.json
    Re-timed / new cues (task 2): copy docs/sound_cues.json -> docs/sound_cues_v3.json, edit, then
      CM_SONG=... CM_VOCALS=... CM_TIMING=... CM_CUES=docs/sound_cues_v3.json $PY tools/audio/sfx/build_v2.py --tag v3
        -> media/sound/mix_v3.wav, layer_v3.wav, work/sound/qa_v3.json, work/sound/SOUND_v3_auto.md (docs/SOUND.md v2 block untouched)

Inputs : docs/sound_cues.json (v2 cue sheet; v1 kept in docs/sound_cues_v1.json), docs/sound_cues_v1.json + work/sound/qa.json (v1 numbers
         for the before/after table), analysis/timing.json, the song, work/stems/vocals.wav.
Method (v1 rules kept: song untouched, mix = song + layer, layer never within 6 dB of the vocal where a word sounds):
  1. spectral placement: each cue gets a static EQ (+-5 dB, power-preserving) that moves its energy into the 1/3-octave bands where the
     song (+ vocal) is weakest in the cue's own window, and takes it out of the 1-4 kHz speech region;
  2. vocal sidechain on the LAYER BUS (3 bands: <250, 250-4000, >4000 Hz): wherever the vocal stem has a word (50 ms, >= -40 LUFS, within
     12 dB of its local peak) each band of the summed layer is held >= 7 dB under the vocal stem's SAME band (attack ~30 ms hold, ~50 ms
     release), then the broadband sum >= 6.5 dB under the vocal. Masking is band-wise: a thump at 100 Hz or air at 8 kHz does not sit on a
     vowel at 1 kHz, so placed outside the speech band a cue can be louder than v1's broadband rule allowed; inside it nothing changed;
  3. gain by measurement: median band margin (song minus cue in the cue's own bands) is brought to a per-cue target (v1: 9-25 dB, v2: 2-8 dB),
     limited by (a) the cue alone staying >= 3 dB under the song's 400 ms loudness in every live frame, (b) a peak cap, (c) never below v1;
  4. the broadband vocal rule: cue (50 ms) >= 6 dB under the vocal stem in every word frame, by a per-frame ride for events as well as beds
     (v1 lowered a whole event cue to the worst word); then an overlap pass on the summed layer; then a layer-only peak guard so the mix's
     true peak stays <= -1 dBTP (it never touches the song).
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d
from scipy.signal import fftconvolve, welch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_layer as BL                                   # noqa: E402
from build_layer import (Anchors, Cue, vocal_word, band_follow, band_margin, band_powers, ending_B, write24,   # noqa: E402
                         P, SONG, VOCALS, OUTD, WORK, ZERO_SPANS, SONG_QUIET, VOCAL_WIN, BANDS)
from dsp import (SR, N, db2a, a2db, bp, Momentary, kpow, integrated_lufs, true_peak_db, peak_db, ebur128, load)  # noqa: E402

CUES_V2 = os.environ.get("CM_CUES") or P("docs", "sound_cues.json")
TAG = "v2"
CUES_V1 = P("docs", "sound_cues_v1.json")
QA_V1 = P(WORK, "qa.json")
DOC = P("docs", "SOUND.md")
SONG_FLOOR = 3.0           # cue / summed layer never closer than this to the song's 400 ms loudness (v1: 6)
VOCAL_RULE = 6.0           # layer >= 6 dB under the vocal stem in word frames (unchanged)
VOCAL_FIT = 6.5
TP_LIMIT = -1.0


# ------------------------------------------------------------------------------------------------ spectral placement
def band_db(y, nper=8192):
    f, Pw = welch(y, SR, nperseg=nper)
    out = np.full(len(BANDS), -200.0)
    for i, fc in enumerate(BANDS):
        m = (f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))
        if m.any():
            out[i] = 10 * np.log10(Pw[m].sum() + 1e-20)
    return out


def place_eq(cy, song_seg, max_boost=7.0, max_cut=-7.0):
    """Per-band gain (dB at BANDS) moving the cue's energy to where the song is weak. None when the cue is too short to measure."""
    if cy.shape[1] < 4096 or song_seg.shape[1] < 4096:
        return None
    nper = 8192 if cy.shape[1] >= 8192 else 4096
    c_db, s_db = band_db(cy.mean(0), nper), band_db(song_seg.mean(0), nper)
    act = c_db > c_db.max() - 25
    if act.sum() < 3:
        return None
    smr = c_db - s_db
    smr = smr - np.where(BANDS <= 125, 10.0, np.where(BANDS <= 200, 5.0, 0.0)) - np.where(BANDS >= 8000, 10.0, np.where(BANDS >= 6300, 4.0, 0.0))   # laptop speakers/earbuds: little below ~150 Hz
    g = np.zeros(len(BANDS))
    g[act] = np.clip(0.5 * (smr[act] - np.median(smr[act])), max_cut, max_boost)
    speech = (BANDS >= 1000) & (BANDS <= 4000)
    g[act & speech] -= 3.0                                       # keep out of the vowel/consonant region
    g = uniform_filter1d(g, 3, mode="nearest") * act
    # power-preserving: the EQ places energy, the margin rule sets the level
    p0 = np.sum(10 ** (c_db[act] / 10))
    p1 = np.sum(10 ** ((c_db[act] + g[act]) / 10))
    g[act] -= 10 * np.log10(p1 / p0)
    return g


def apply_eq(y, g):
    if g is None:
        return y
    f = np.fft.rfftfreq(4096, 1 / SR)
    act = np.abs(g) > 0
    # outside the measured bands: hold the edge value (no boosts of floor noise: edge bands are 0 where inactive)
    gi = np.interp(np.log2(np.maximum(f, 20)), np.log2(BANDS), g)
    h = np.fft.irfft(10 ** (gi / 20))
    h = np.roll(h, 2048)[:4096] * np.hanning(4096)
    return np.stack([fftconvolve(y[0], h, mode="same"), fftconvolve(y[1], h, mode="same")])


# ------------------------------------------------------------------------------------------------ vocal sidechain (layer bus)
XO = (250.0, 4000.0)
HOP = 0.01


def split3(y):
    lo = BL.lp(y, XO[0], 4)
    mid = bp(y, XO[0], XO[1], 2)
    return lo, mid, y - lo - mid


def band_rms_db(y3, n_frames, win=VOCAL_WIN):
    """y3: three (2,n) arrays -> (3, n_frames) dB of 50 ms K-weighted power (BS.1770, as the v1 vocal rule) centred on each 10 ms frame."""
    out = []
    h = N(win) // 2
    for y in y3:
        p = np.cumsum(np.concatenate([[0.0], kpow(y)]))
        c = (np.arange(n_frames) * N(HOP))
        a_, b_ = np.clip(c - h, 0, len(p) - 1), np.clip(c + h, 0, len(p) - 1)
        out.append(10 * np.log10((p[b_] - p[a_]) / (2 * h) + 1e-14))
    return np.array(out)


class VocalBus:
    """Per-band, per-frame reduction curves that keep the summed layer >= BAND_RULE under the vocal stem's same band (>= TOTAL_RULE
    broadband) in every word frame. Curves are linear time-varying gains, so applying them to each cue = applying them to the sum."""
    BAND_RULE = 6.5
    TOTAL_RULE = 6.0
    REL = 35.0            # a vocal band more than 35 dB under the vocal's strongest band at that frame does not constrain the layer

    def __init__(self, voc, vocM, n):
        self.nf = n // N(HOP)
        self.ts = np.arange(self.nf) * HOP
        self.vb = band_rms_db(split3(voc), self.nf)
        self.vt = 10 * np.log10(sum(10 ** (self.vb / 10)) + 1e-14)
        _, word = vocal_word(vocM, self.ts)
        self.word = maximum_filter1d(word, 5)         # +-20 ms: the layer is already down when a word starts

    def curves(self, layer_cues, n):
        lay = np.zeros((2, n))
        for c in layer_cues:
            i = N(c.t0)
            y = c.y * db2a(c.gain_db)
            a, b = max(0, i), min(n, i + y.shape[1])
            if b > a:
                lay[:, a:b] += y[:, a - i:b - i]
        lb = band_rms_db(split3(lay), self.nf)
        d = np.zeros((3, self.nf))
        relevant = self.vb >= (self.vb.max(0) - self.REL)
        for _ in range(3):
            lb2 = lb + d
            need = np.minimum(0.0, self.vb - self.BAND_RULE - lb2)
            need = np.where(self.word & relevant & (lb2 > -110), need, 0.0)
            d = d + need
            lt = 10 * np.log10(sum(10 ** ((lb + d) / 10)) + 1e-14)
            nt = np.minimum(0.0, self.vt - self.TOTAL_RULE - lt)
            nt = np.where(self.word & (lt > -110), nt, 0.0)
            d = d + nt[None, :]
        d = np.minimum(0.0, d - 0.3 * (d < -0.01))
        d = uniform_filter1d(minimum_filter1d(d, 9, axis=1), 5, axis=1)
        return d

    def apply(self, c, d):
        i0 = N(c.t0)
        idx = (i0 + np.arange(c.y.shape[1])) / SR
        yl, ym, yh = split3(c.y * db2a(c.gain_db))
        g = [db2a(np.interp(idx, self.ts, d[k])) for k in range(3)]
        c.y = yl * g[0] + ym * g[1] + yh * g[2]
        c.gain_db = 0.0
        c.duck_max = float(min(0.0, np.min([np.interp(idx, self.ts, d[k]).min() for k in range(3)])))
        if c.duck_max < -0.5:
            c.rule += "; bus ride"


def follow_bed(c, song, margin, cap, lo_lim=-45.0, hi_lim=25.0):
    """Beds: ride the bed so it sits `margin` dB under the song in the bed's OWN band, frame by frame (200 ms hold, 300 ms smooth): the
    room tone comes up where the song is sparse and stays out of its holes. Static level afterwards set by the peak cap."""
    cdb = band_db(c.y.mean(0))
    act = np.where(cdb > cdb.max() - 12)[0]
    lo, hi = BANDS[act.min()] / 2 ** (1 / 6) * 0.9, min(BANDS[act.max()] * 2 ** (1 / 6) * 1.1, 20000)
    i0 = N(c.t0)
    seg = song[:, i0:i0 + c.y.shape[1]]
    if seg.shape[1] < c.y.shape[1]:
        seg = np.pad(seg, ((0, 0), (0, c.y.shape[1] - seg.shape[1])))
    w = N(0.1)
    es = uniform_filter1d(bp(seg, lo, hi, 2).mean(0) ** 2, w)
    ec = uniform_filter1d(bp(c.y, lo, hi, 2).mean(0) ** 2, w)
    need = 10 * np.log10(es + 1e-14) - margin - 10 * np.log10(ec + 1e-14)
    d = np.clip(need, lo_lim, hi_lim)
    d = uniform_filter1d(minimum_filter1d(d, N(0.2)), N(0.3))
    c.y = c.y * db2a(d)
    k = float(np.median(d[ec > ec.max() * 1e-3]))
    c.gain_db = min(0.0, cap - peak_db(c.y))
    c.rule = f"follows the song in {lo:.0f}-{hi:.0f} Hz at {margin:g} dB (median ride {k:+.1f} dB)"


# ------------------------------------------------------------------------------------------------ fit
def fit2(c, songM, song, v2, g_v1):
    if c.kind == "bed" and v2.get("follow", True):
        follow_bed(c, song, v2["band"], v2["cap"])
        return
    ts, cM, sM, act = c.frames(songM, 0.4, 0.0)
    live = act & (sM > SONG_QUIET)
    if not live.any():
        live = act
    m = sM[live] - cM[live]
    bm0 = band_margin(c, song, gain=0.0)
    hard = {"floor": float(m.min() - v2.get("floor", SONG_FLOOR)), "peak cap": v2["cap"] - peak_db(c.y)}
    opts = dict(hard)
    if bm0 is not None:
        opts["band target"] = bm0["median"] - v2["band"]
    rule = min(opts, key=opts.get)
    g = opts[rule]
    if g_v1 is not None and g < g_v1 and rule == "band target":
        g, rule = g_v1, "kept at v1 gain (band target met)"
    gh = min(hard.values())
    g_abs = v2.get("min_peak", -18.0) - peak_db(c.y)          # audible-in-absolute-terms floor: peak >= -22 dBFS (earbuds, normal level)
    if g < g_abs:
        g, rule = min(g_abs, gh), rule + f" (raised to the peak floor, hard limit {min(hard, key=hard.get)})"
    c.gain_db, c.rule = g, rule
    band_follow(c, song)


def overlap2(cues, songM, n, log, bus=None, voc=None):
    """Summed layer never closer than SONG_FLOOR to the song's 400 ms loudness (v1: 6). Trims whole cues by the excess."""
    for it in range(10):
        layM = Momentary(kpow(BL.sum_layer(cues, n)))
        trims = {}
        for c in cues:
            ts, cM, sM, act = c.frames(songM, 0.4)
            live = act & (sM > SONG_QUIET)
            if live.any():
                mm = sM[live] - layM(ts[live])
                if mm.min() < SONG_FLOOR - 0.1:
                    trims[c.id] = max(trims.get(c.id, 0), SONG_FLOOR + 0.2 - mm.min())
        if not trims:
            return
        log(f"overlap pass {it}: " + ", ".join(f"{k} -{v:.1f} dB" for k, v in trims.items()))
        for c in cues:
            if c.id in trims:
                c.gain_db -= trims[c.id]
                c.rule += "; trimmed in the sum"


def guard(song, layer, thr_db):
    """Layer-only peak guard: wherever song+layer would pass thr, scale the LAYER down (smoothed). The song is never touched."""
    thr = db2a(thr_db)
    with np.errstate(divide="ignore", invalid="ignore"):
        gp = np.where(layer > 1e-12, (thr - song) / layer, np.inf)
        gn = np.where(layer < -1e-12, (-thr - song) / layer, np.inf)
    g = np.clip(np.minimum(gp, gn), 0.0, 1.0).min(0)
    if (g >= 1.0).all():
        return layer, 0.0, 0.0
    g = minimum_filter1d(g, N(0.004))
    g = uniform_filter1d(g, N(0.006))
    g = np.minimum(g, 1.0)
    return layer * g, float((g < 0.999).sum() / SR * 1000), float(a2db(g.min()))


# ------------------------------------------------------------------------------------------------ audibility
def smr_metric(y, song, t0):
    """Best-band signal-to-masker ratio of the cue against the SONG (which holds the vocal), per 43 ms frame the cue sounds
    (within 12 dB of its loudest frame): max over its own 1/3-octave bands (within 25 dB of the frame's strongest) of
    cue_dB - song_dB. Returns (p90 over frames, median). >= -9 dB is called audible (noise-like cue, critical-band masking)."""
    i0 = N(t0)
    i1 = min(song.shape[1], i0 + y.shape[1])
    if i1 - i0 < 4096:
        return None
    cb, _ = band_powers(y[:, :i1 - i0])
    sb, _ = band_powers(song[:, i0:i1])
    k = min(cb.shape[1], sb.shape[1])
    cb, sb = cb[:, :k], sb[:, :k]
    tot = cb.sum(0)
    act = tot > tot.max() * 10 ** -1.2
    vals = []
    for j in np.where(act)[0]:
        sel = cb[:, j] >= cb[:, j].max() * 10 ** -2.5
        d = 10 * np.log10((cb[sel, j] + 1e-20) / (sb[sel, j] + 1e-20))
        vals.append(d.max())
    if not vals:
        return None
    return float(np.percentile(vals, 90)), float(np.median(vals))


# ------------------------------------------------------------------------------------------------ main
def remix(tag, layer_path, log=print):
    """mix_<tag> = mix_v2 + (ending_B(SONG) - ending_B(original song)): the approved v2 layer and mix unchanged wherever the song is
    unchanged (bit-identical there), the edited song where it was edited. Peak guard on the layer only if the edit pushed the true peak."""
    orig = BL.P("inputs", "Chaos Monkey - reformatted for duet.wav")
    song, voc = load(SONG), load(VOCALS)
    s0 = load(orig)
    v0 = load(BL.P("work", "stems", "vocals.wav"))
    songB, notesB = ending_B(song, voc)
    songB0, _ = ending_B(s0, v0)
    m2, _ = sf.read(os.path.join(OUTD, "mix_v2.wav"), always_2d=True, dtype="float64")
    lay, _ = sf.read(layer_path, always_2d=True, dtype="float64")
    m2, lay = m2.T, lay.T
    assert m2.shape == songB.shape == lay.shape, (m2.shape, songB.shape, lay.shape)
    dS = songB - songB0
    ch = np.nonzero(np.any(dS != 0, axis=0))[0]
    mix = m2 + dS
    tp = true_peak_db(mix)
    guard_note = "not needed"
    if tp > TP_LIMIT - 0.05:
        lg, ms, gmin = guard(songB, lay, -1.6)
        mix = songB + lg
        tp = true_peak_db(mix)
        guard_note = f"{ms:.0f} ms, max {gmin:.2f} dB"
    out = os.path.join(OUTD, f"mix_{tag}.wav")
    write24(out, mix)
    mx, _ = sf.read(out, always_2d=True, dtype="float64")
    mx = mx.T
    outside = np.ones(mix.shape[1], bool)
    if len(ch):
        outside[ch[0]:ch[-1] + 1] = False
    span = slice(ch[0], ch[-1] + 1) if len(ch) else slice(0, 0)
    qa = {"global": {
        "song": os.path.relpath(SONG, BL.ROOT), "vocals": os.path.relpath(VOCALS, BL.ROOT), "layer": os.path.relpath(layer_path, BL.ROOT),
        "song_changed_span_s": [ch[0] / SR, (ch[-1] + 1) / SR] if len(ch) else None,
        "mix_vs_mix_v2_nonzero_samples_outside_span": int(np.count_nonzero((mx - m2)[:, outside])),
        "mix_minus_(song+layer)_in_span_max_abs": float(np.abs(mx[:, span] - songB[:, span] - lay[:, span]).max()) if len(ch) else 0.0,
        "mix_v2_lufs": round(integrated_lufs(m2), 2), f"mix_{tag}_lufs": round(integrated_lufs(mx), 2),
        "mix_v2_tp": round(true_peak_db(m2), 2), f"mix_{tag}_tp": round(true_peak_db(mx), 2),
        "song_lufs": round(integrated_lufs(s0), 2), "song_edited_lufs": round(integrated_lufs(song), 2),
        "clipped_samples": int(np.count_nonzero(np.abs(mx) >= 1.0)), "len_s": mx.shape[1] / SR, "guard": guard_note,
        "ebur128_mix_v2": ebur128(os.path.join(OUTD, f"mix_{TAG}.wav")), f"ebur128_mix_{tag}": ebur128(out), "ending": notesB}}
    json.dump(qa, open(os.path.join(WORK, f"qa_{tag}.json"), "w"), indent=1, ensure_ascii=False)
    log(json.dumps(qa["global"], indent=1))


def main(argv):
    global TAG
    log = print
    if "--tag" in argv:
        TAG = argv[argv.index("--tag") + 1]
    if "--reuse-layer" in argv:
        return remix(TAG, argv[argv.index("--reuse-layer") + 1], log)
    os.makedirs(WORK, exist_ok=True)
    spec = json.load(open(CUES_V2))
    v1spec = {c["id"]: c for c in json.load(open(CUES_V1))["cues"]}
    qa1 = json.load(open(QA_V1))["cues"]
    A = Anchors()
    song, voc = load(SONG), load(VOCALS)
    n = song.shape[1]
    songM, vocM = Momentary(kpow(song)), Momentary(kpow(voc))
    rooms = spec["rooms"]
    cues = [Cue(s, A, rooms) for s in spec["cues"]]
    plain = {}
    bus = VocalBus(voc, vocM, n)
    for c in cues:
        v2 = c.s["v2"]
        g_v1 = qa1[c.id]["gain_db"] if c.id in qa1 else None
        plain[c.id] = c.y.copy()                              # as rendered, before placement (for the before-metrics)
        c.eq = None
        if v2.get("eq", True):
            i0 = N(c.t0)
            c.eq = place_eq(c.y, song[:, i0:i0 + c.y.shape[1]])
            c.y = apply_eq(c.y, c.eq)
        fit2(c, songM, song, v2, g_v1)
    raw = {c.id: [c.y.copy(), c.gain_db, c.rule] for c in cues}
    for rnd in range(4):
        for c in cues:                                         # restart from the un-ridden cue with its (possibly trimmed) gain
            c.y, c.gain_db, c.rule = raw[c.id][0], raw[c.id][1], raw[c.id][2]
        d = bus.curves(cues, n)
        for c in cues:
            bus.apply(c, d)
        for c in cues:
            c.trim_probe = 0.0
        overlap2(cues, songM, n, log)
        trimmed = [c for c in cues if c.gain_db < -1e-9]
        if not trimmed:
            break
        for c in trimmed:
            raw[c.id][1] += c.gain_db
            raw[c.id][2] = c.rule if "trimmed in the sum" in c.rule else raw[c.id][2] + "; trimmed in the sum"
            raw[c.id][2] = raw[c.id][2].split("; bus ride")[0]
    bus_curves = d
    # polish: K-weighted broadband check on the real layer on two interleaved 10 ms grids (offset 3.7 ms); any frame < 6.1 dB under the
    # vocal is pulled down (all cues, one smoothed curve)
    grids = []
    for off in (0.0, 0.0037):
        tg = np.arange(0.05, n / SR - 0.05, HOP) + off
        vg, wg = vocal_word(vocM, tg)
        grids.append((tg, vg, maximum_filter1d(wg, 5)))
    for it in range(5):
        layM_ = Momentary(kpow(BL.sum_layer(cues, n)))
        curves, worst = [], 0.0
        for tg, vg, wg in grids:
            lg_ = layM_(tg, win=VOCAL_WIN)
            need = np.where(wg & (lg_ > -110), np.minimum(0.0, vg - lg_ - 6.1), 0.0)
            worst = min(worst, float(need.min()))
            curves.append((tg, uniform_filter1d(minimum_filter1d(need - 0.3 * (need < 0), 9), 5)))
        if worst >= -1e-6:
            break
        log(f"polish {it}: max {worst:.1f} dB")
        for c in cues:
            idx = (N(c.t0) + np.arange(c.y.shape[1])) / SR
            g = np.minimum(np.interp(idx, curves[0][0], curves[0][1]), np.interp(idx, curves[1][0], curves[1][1]))
            c.y = c.y * db2a(g)

    # ---- layer, peak guard (layer only)
    layer = BL.sum_layer(cues, n)
    ext = N(BL.EXT_B)
    songB, notesB = ending_B(song, voc)
    layerB = np.concatenate([layer, np.zeros((2, ext))], axis=1)
    thr = -1.6
    for _ in range(8):
        lg, ms, gmin = guard(songB, layerB, thr)
        mix = songB + lg
        tp = true_peak_db(mix)
        if tp <= TP_LIMIT - 0.05:
            break
        thr -= 0.4
    layerB = lg
    for a, b in ZERO_SPANS:
        assert np.count_nonzero(layerB[:, N(a):N(b)]) == 0
    mixB = songB + layerB
    write24(os.path.join(OUTD, f"layer_{TAG}.wav"), layerB)
    write24(os.path.join(OUTD, f"mix_{TAG}.wav"), mixB)
    log(f"guard: thr {thr:.1f} dBFS, {ms:.0f} ms affected, max reduction {gmin:.2f} dB; mix TP {tp:.2f}")

    # ---- QA
    layM = Momentary(kpow(layerB))
    qa = {"cues": {}}
    for c in cues:
        ts, cM, sM, act = c.frames(songM, 0.4)
        live = act & (sM > SONG_QUIET)
        ms_ = (sM[live] - cM[live]) if live.any() else np.array([np.nan])
        msum = (sM[live] - layM(ts[live])) if live.any() else np.array([np.nan])
        ts1, cS, vS, act1 = c.frames(vocM, VOCAL_WIN)
        v, word = vocal_word(vocM, ts1)
        pres = act1 & word
        mv = (v[pres] - layM(ts1[pres], win=VOCAL_WIN)) if pres.any() else None
        bm = band_margin(c, song)
        y = c.y * db2a(c.gain_db)
        old = qa1.get(c.id)
        near = []
        for t, lab in c.onsets:
            for w, wt, lid in A.near_words(t):
                near.append({"cue_t": round(t, 3), "word": w, "line": lid, "dt_ms": round((t - wt) * 1000)})
        qa["cues"][c.id] = {
            "shot": c.s["shot"], "new": bool(c.s.get("new")), "t0": round(c.t0, 3), "t1": round(c.t1, 3),
            "times": [round(t, 3) for t in (c.events_t or [c.t0])], "end": None if c.cut_at is None else round(c.cut_at, 3),
            "kind": c.kind, "src": c.s["src"], "peak_v1": None if old is None else old["peak_dbfs"],
            "peak_dbfs": round(peak_db(y), 1), "rule": c.rule, "duck_max_db": round(c.duck_max, 1),
            "eq": None if c.eq is None else {f"{int(BANDS[i])}": round(float(x), 1) for i, x in enumerate(c.eq) if abs(x) >= 1.0},
            "song_med": round(float(np.nanmedian(ms_)), 1), "song_worst": round(float(np.nanmin(msum)), 1),
            "song_med_v1": None if old is None else old["song_med"],
            "vocal_worst": None if mv is None else round(float(mv.min()), 1),
            "band": None if bm is None else {k: round(v_, 1) for k, v_ in bm.items()},
            "band_v1": None if old is None else old["band"],
            "near_words": near, "picture_dependent": c.s.get("picture_dependent", False), "intent": c.s["intent"],
            "anchors": [e["at"] for e in c.s.get("events", [])] or [c.s.get("start"), c.s.get("end", f"+{c.s.get('end_rel')}")],
        }
    song_B = np.concatenate([song, np.zeros((2, ext))], axis=1)
    inside = np.zeros(n, bool)
    for c in cues:
        inside[max(0, N(c.t0)):min(n, N(c.t1))] = True
    outside_nonzero = int(np.count_nonzero(layerB[:, :n][:, ~inside]))
    mx, _ = sf.read(os.path.join(OUTD, f"mix_{TAG}.wav"), always_2d=True, dtype="float64")
    lx, _ = sf.read(os.path.join(OUTD, f"layer_{TAG}.wav"), always_2d=True, dtype="float64")
    readback = float(np.abs(mx.T - songB - lx.T).max())
    v1l, _ = sf.read(os.path.join(OUTD, "layer_v1.wav"), always_2d=True, dtype="float64")
    v1m, _ = sf.read(os.path.join(OUTD, "mix_v1_endB.wav"), always_2d=True, dtype="float64")
    # layer vs vocal on the final layer, 50 ms, word frames
    tsv = np.arange(0.05, n / SR - 0.05, 0.01)
    vv, wv = vocal_word(vocM, tsv)
    lv_ = layM(tsv, win=VOCAL_WIN)
    vm = vv[wv] - lv_[wv]
    tsv2 = tsv + 0.0037
    vv2, wv2 = vocal_word(vocM, tsv2)
    vm = np.concatenate([vm, (vv2 - layM(tsv2, win=VOCAL_WIN))[wv2]])
    # the 400 ms loudness relation of the whole layer to the song
    lay_b = Momentary(kpow(layerB))
    ls = songM(tsv, win=0.4)
    lm = lay_b(tsv, win=0.4)
    live = ls > SONG_QUIET
    lay1 = Momentary(kpow(np.concatenate([v1l.T, np.zeros((2, ext))], axis=1)))
    lm1 = lay1(tsv, win=0.4)
    on1, on2 = lm1 > -70, lm > -70
    qa["global"] = {
        "song_lufs": round(integrated_lufs(song), 2), "mix_v1B_lufs": round(integrated_lufs(v1m.T), 2),
        "mix_v2_lufs": round(integrated_lufs(mixB), 2), "layer_v1_lufs": round(integrated_lufs(v1l.T), 1),
        "layer_v2_lufs": round(integrated_lufs(layerB), 1),
        "layer_v1_peak": round(peak_db(v1l.T), 1), "layer_v2_peak": round(peak_db(layerB), 1),
        "song_tp": round(true_peak_db(song), 2), "mix_v1B_tp": round(true_peak_db(v1m.T), 2), "mix_v2_tp": round(true_peak_db(mixB), 2),
        "clipped_samples": int(np.count_nonzero(np.abs(mx) >= 1.0)), "len_s": mixB.shape[1] / SR,
        "guard": {"thr_dbfs": thr, "ms_affected": round(ms), "max_reduction_db": round(gmin, 2)},
        "vocal_min_margin_db": round(float(vm.min()), 2), "vocal_p5_margin_db": round(float(np.percentile(vm, 5)), 1),
        "layer_under_song_400ms_median_v1": round(float(np.median(ls[live & on1] - lm1[live & on1])), 1),
        "layer_under_song_400ms_median_v2": round(float(np.median(ls[live & on2] - lm[live & on2])), 1),
        "layer_under_song_400ms_p5_v2": round(float(np.percentile(ls[live & on2] - lm[live & on2], 5)), 1),
        "layer_under_song_400ms_min_v2": round(float((ls[live & on2] - lm[live & on2]).min()), 1),
        "null_outside_cues_nonzero": outside_nonzero, "readback_max_abs_err": readback,
        "zero_spans_exact": True, "ebur128_song": ebur128(SONG), "ebur128_mix_v2": ebur128(os.path.join(OUTD, f"mix_{TAG}.wav")),
        "ending": notesB,
        "layer_peak_after_237.94": round(peak_db(layerB[:, N(237.94):]), 1),
        "layer_peak_237.84_to_238.32": round(peak_db(layerB[:, N(237.84):N(238.32)]), 1),
        "song_B_vs_mix_B_after_238.32_rms": [round(a2db(np.sqrt(np.mean(songB[:, N(238.4):] ** 2))), 1),
                                              round(a2db(np.sqrt(np.mean(mixB[:, N(238.4):] ** 2))), 1)],
    }
    json.dump(qa, open(os.path.join(WORK, f"qa_{TAG}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump({c.id: {"times": qa["cues"][c.id]["times"], "t0": qa["cues"][c.id]["t0"], "t1": qa["cues"][c.id]["t1"],
                      "peak_dbfs": qa["cues"][c.id]["peak_dbfs"]} for c in cues},
              open(os.path.join(WORK, f"cues_resolved_{TAG}.json"), "w"), indent=1)
    write_doc(qa, cues)
    g = qa["global"]
    log(f"mix_v2 {g['mix_v2_lufs']} LUFS (song {g['song_lufs']}, v1 {g['mix_v1B_lufs']}), TP {g['mix_v2_tp']}, layer {g['layer_v1_lufs']} -> {g['layer_v2_lufs']} LUFS, "
        f"vocal min margin {g['vocal_min_margin_db']}")


# ------------------------------------------------------------------------------------------------ doc
def write_doc(qa, cues):
    g = qa["global"]
    f = lambda x, d=1: "-" if x is None else f"{x:.{d}f}"  # noqa
    rows = ["| # | cue | shot | time(s) | peak dBFS v1 -> v2 | under song (400 ms LUFS) v1 -> v2 | main band: band margin median / p10 v1 -> v2 | under vocal worst (50 ms) | audible | how |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(cues, 1):
        q = qa["cues"][c.id]
        b, b1 = q["band"], q["band_v1"]
        if c.kind == "bed":
            when = f"{q['t0']:.2f}-{(q['end'] or q['t1']):.2f}"
        else:
            when = ", ".join(f"{t:.3f}" for t in q["times"])
        band = "-" if b is None else (f"{b['band_hz']:.0f} Hz: " + (f"{b1['median']:+.0f} / {b1['p10']:+.0f} -> " if b1 else "new ") + f"{b['median']:+.0f} / {b['p10']:+.0f}")
        ok = b is not None and (b["median"] <= 12 or b["p10"] <= 6)
        aud = "yes" if ok else "weak"
        eq = ", ".join(f"{k}:{v:+.0f}" for k, v in (q["eq"] or {}).items()) or "-"
        rows.append(f"| {i} | **{c.id}**{' (new)' if q['new'] else ''} | {q['shot']} | {when} | "
                    f"{f(q['peak_v1'])} -> {q['peak_dbfs']:.1f} | {f(q['song_med_v1'])} -> {q['song_med']:.1f} (summed worst {q['song_worst']:.1f}) | {band} | "
                    f"{f(q['vocal_worst'])} | {aud} | {q['rule']}; EQ {eq} |")
    new_rows = ["| cue | shot | exact times (s) | on | what the picture should hit |", "|---|---|---|---|---|"]
    for c in cues:
        q = qa["cues"][c.id]
        if q["new"]:
            new_rows.append(f"| {c.id} | {q['shot']} | {', '.join(f'{t:.3f}' for t in q['times'])} | {', '.join(q['anchors'])} | {q['intent']} |")
    near = ["| cue | cue time | word | dt (ms) |", "|---|---|---|---|"]
    for c in cues:
        for x in qa["cues"][c.id]["near_words"]:
            near.append(f"| {c.id} | {x['cue_t']:.3f} | {x['word']} | {x['dt_ms']:+d} |")
    ver = ["| check | result |", "|---|---|",
           f"| integrated loudness | song **{g['song_lufs']} LUFS**; mix v1 (end B) {g['mix_v1B_lufs']}; **mix v2 {g['mix_v2_lufs']} LUFS** (+{g['mix_v2_lufs'] - g['song_lufs']:.2f} LU over the song); ffmpeg ebur128 song {g['ebur128_song'].get('integrated_lufs')} / mix v2 {g['ebur128_mix_v2'].get('integrated_lufs')} |",
           f"| layer alone | v1 {g['layer_v1_lufs']} LUFS (peak {g['layer_v1_peak']} dBFS) -> **v2 {g['layer_v2_lufs']} LUFS** (peak {g['layer_v2_peak']} dBFS) |",
           f"| layer under song, 400 ms, where the layer sounds | median v1 {g['layer_under_song_400ms_median_v1']} dB -> **v2 {g['layer_under_song_400ms_median_v2']} dB**; v2 5th percentile {g['layer_under_song_400ms_p5_v2']} dB, closest frame {g['layer_under_song_400ms_min_v2']} dB |",
           f"| true peak | song {g['song_tp']} dBTP; mix v1 {g['mix_v1B_tp']}; **mix v2 {g['mix_v2_tp']} dBTP** (limit -1.0); clipped samples {g['clipped_samples']}; layer-only peak guard: threshold {g['guard']['thr_dbfs']} dBFS, {g['guard']['ms_affected']} ms of layer affected, max reduction {g['guard']['max_reduction_db']} dB |",
           f"| vocal | in every 50 ms frame where a word sounds the whole layer is >= **{g['vocal_min_margin_db']} dB** under the vocal stem (rule: 6; 5th percentile {g['vocal_p5_margin_db']} dB) |",
           f"| song untouched | mix_v2 - song(end B edit only) = layer_v2 to {g['readback_max_abs_err']:.1e}; layer non-zero outside cue windows: {g['null_outside_cues_nonzero']} samples; holes 15.440-15.515 and 149.285-149.525 exactly 0 |",
           f"| ending B | length {g['len_s']:.3f} s; layer peak after 237.94: {g['layer_peak_after_237.94']} dBFS (the tick's room tail only); the song's own tails (last note 'line' and the D drone, same as v1 B) |"]
    txt = ("<!-- AUTO_V2:BEGIN (written by tools/audio/sfx/build_v2.py; edit docs/sound_cues.json) -->\n\n"
           "### Per-cue before / after (v1 -> v2)\n\n"
           "*under song* = song's 400 ms momentary loudness minus the cue (median over its live frames; smaller = louder). *band margin* = song minus cue in the cue's own "
           "1/3-octave bands (v1 and v2 measured the same way; the 12 dB line is the brief's; p10 = the cue's most prominent frames). "
           "*audible* = band margin median <= 12 dB or p10 <= 6 dB (a model, not ears). New cues show 'new'.\n\n" + "\n".join(rows) +
           "\n\n### New-action cues: exact times (s) for the picture teams\n\n" + "\n".join(new_rows) +
           "\n\n### Cues within 150 ms of a word onset (v2)\n\n" + "\n".join(near) +
           "\n\n### Verification (v2)\n\n" + "\n".join(ver) + "\n\n<!-- AUTO_V2:END -->")
    if TAG != "v2":                                  # never overwrite the approved v2 block; the lead merges a v3 block by hand
        open(os.path.join(WORK, f"SOUND_{TAG}_auto.md"), "w").write(txt)
        return
    doc = open(DOC).read()
    if "<!-- AUTO_V2:BEGIN" in doc:
        doc = re.sub(r"<!-- AUTO_V2:BEGIN.*?<!-- AUTO_V2:END -->", lambda m: txt, doc, flags=re.S)
    else:
        doc = doc.rstrip() + "\n\n## v2\n\n@@V2@@\n\n" + txt + "\n"
    open(DOC, "w").write(doc)


if __name__ == "__main__":
    main(sys.argv[1:])

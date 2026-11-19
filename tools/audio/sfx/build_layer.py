#!/usr/bin/env python3
"""Chaos Monkey sound layer: cue sheet data -> layer, mixes, ending variants, QA, docs.

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    $PY tools/audio/sfx/build_layer.py                # everything (sources are rebuilt only if missing)
    $PY tools/audio/sfx/build_layer.py --sources      # rebuild every source first (tools/audio/sfx/sounds.py)
    $PY tools/audio/sfx/build_layer.py --no-plots

Inputs : docs/sound_cues.json (the cue sheet: anchors, sources, levels, pans, intents), analysis/timing.json, docs/shots.yaml,
         inputs/Chaos Monkey - reformatted for duet.wav (the song, 16-bit), work/stems/vocals.wav (BS-RoFormer vocal stem).
Outputs: media/sound/layer_v1.wav (layer alone, 24-bit, song length), media/sound/layer_v1_endC.wav,
         media/sound/mix_v1.wav (= ending A), media/sound/mix_v1_endA.wav / _endB.wav / _endC.wav (24-bit PCM),
         work/sound/cues_resolved.json + qa.json, analysis/plots/sound_*.png, and the generated tables in docs/SOUND.md
         (between the AUTO markers; the hand-written parts of that file are kept).

Rules (Hold Fire / HALYS method): the song is never processed: mix = song + layer, sample-aligned; every cue is levelled
against the song's own momentary loudness (BS.1770, 400 ms) and the whole layer held >= 6 dB (fitted 7) under the vocal stem
(50 ms) wherever a word sounds; beds duck on the layer only, events take a lower fixed gain; the full-band hole 15.440-15.515
and the near-silence 149.285-149.525 are forced to exact zero in the layer.
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf
import yaml
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d
from scipy.signal import fftconvolve, stft

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsp import (ROOT, SR, N, db2a, a2db, lp, hp, peq, fades, stereo, pan as dpan, narrow, ir, kpow, Momentary,  # noqa
                 integrated_lufs, true_peak_db, peak_db, ebur128, load)
import sounds

P = lambda *a: os.path.join(ROOT, *a)  # noqa
# v4: song / vocal stem / timing are overridable for the v4 song ("Yes" one beat late); defaults = the v1/v2 inputs
SONG = os.environ.get("CM_SONG") or P("inputs", "Chaos Monkey - reformatted for duet.wav")
VOCALS = os.environ.get("CM_VOCALS") or P("work", "stems", "vocals.wav")
TIMING = os.environ.get("CM_TIMING") or P("analysis", "timing.json")
CUES = P("docs", "sound_cues_v1.json")
OUTD = P("media", "sound")
WORK = P("work", "sound")
PLOTS = P("analysis", "plots")
DOC = P("docs", "SOUND.md")

MIN_MARGIN = 6.0
VOCAL_ON = -40.0
VOCAL_WORD = 12.0
VOCAL_WIN = 0.05
VOCAL_FIT = 7.0
SONG_QUIET = -42.0          # song momentary below this: frame exempt from the under-the-song rule (silence / after the end)
ZERO_SPANS = [(15.440, 15.515), (149.285, 149.525)]   # full-band hole, the near-silence: layer exactly 0
TP_LIMIT = -1.0
NEAR_WORD = 0.150
EXT_B = 3.6                 # ending B: seconds added after 238.320


# ------------------------------------------------------------------------------------------------ anchors
class Anchors:
    def __init__(self):
        self.tm = json.load(open(TIMING))
        self.hits = np.array([h["t"] for h in self.tm["hits"]])
        self.beats = np.array([b["t"] for b in self.tm["beats"]])
        self.chops = [c["start"] for c in self.tm["hit_events"]["chops"]]
        self.sil = self.tm["hit_events"]["silences"]
        self.holes = [(c["start"], c["end"]) for c in self.tm["hit_events"]["chops"]] + \
            [(x["start"], x["end"]) for x in self.sil if x["start"] > 1.0]
        self.shots = {s["id"]: s["t"] for s in yaml.safe_load(open(P("docs", "shots.yaml")))["shots"]}
        self.words = []
        for ln in self.tm["lines"]:
            for w in ln["words"]:
                self.words.append((w["start"], w.get("end", w["start"]), w["w"], ln["id"], ln["text"]))

    def __call__(self, s):
        kind, _, rest = s.partition(":")
        if kind == "t":
            return float(rest)
        if kind in ("hit", "beat"):
            arr, tol = (self.hits, 0.040) if kind == "hit" else (self.beats, 0.060)
            v = float(rest)
            j = int(np.argmin(np.abs(arr - v)))
            if abs(arr[j] - v) > tol:
                raise ValueError(f"anchor {s}: nearest {kind} {arr[j]:.3f} is {abs(arr[j]-v)*1000:.0f} ms away")
            return float(arr[j])
        if kind == "chop":
            v = float(rest)
            c = min(self.chops, key=lambda x: abs(x - v))
            assert abs(c - v) < 0.01, s
            return c
        if kind in ("word", "wordend"):
            parts = rest.split(":")
            lid, txt = int(parts[0]), parts[1]
            n = int(parts[2]) if len(parts) > 2 else 1
            ws = [w for w in self.tm["lines"][lid]["words"] if w["w"] == txt]
            assert len(ws) >= n, f"anchor {s}: word not found in line {lid} '{self.tm['lines'][lid]['text']}'"
            w = ws[n - 1]
            return float(w["start"] if kind == "word" else w["end"])
        if kind == "sync":
            for sp in self.tm["sync_points"]:
                if sp["name"].startswith(rest):
                    return float(sp["t"])
            raise ValueError(s)
        if kind == "silence":
            v, edge = rest.split(":")
            for x in self.sil:
                if abs(x["start"] - float(v)) < 0.01:
                    return float(x[edge])
            raise ValueError(s)
        if kind == "section":
            name, edge = rest.split(":")
            for x in self.tm["sections"]:
                if x["name"] == name:
                    return float(x[edge])
            raise ValueError(s)
        if kind == "shot":
            return float(self.shots[rest])
        raise ValueError(f"unknown anchor {s}")

    def near_words(self, t, win=NEAR_WORD):
        return [(w[2], w[0], w[3]) for w in self.words if abs(w[0] - t) <= win]


# ------------------------------------------------------------------------------------------------ sources / rendering
_SRC = {}


def source(name):
    if name not in _SRC:
        path = P("media", "sound", "sfx", name + ".wav")
        if not os.path.exists(path):
            sounds.build(name)
        y, sr = sf.read(path, always_2d=True, dtype="float64")
        assert sr == SR
        _SRC[name] = y.T
    return _SRC[name]


def room(y, spec, seed):
    if not spec:
        return y
    h = ir(spec["rt60"] * 1.6 + 0.1, spec["rt60"], lp_hz=spec.get("lp", 8000), hp_hz=120, seed=seed, predelay=spec.get("predelay", 0.0))
    return np.stack([fftconvolve(y[0], h[0]), fftconvolve(y[1], h[1])]) * db2a(spec["wet_db"]) + \
        np.pad(y, ((0, 0), (0, h.shape[1] - 1)))


class Cue:
    def __init__(self, spec, A, rooms):
        self.s = spec
        self.id = spec["id"]
        self.kind = spec["kind"]
        self.variants = spec.get("variants", ["A", "B", "C"])
        self.onsets = []          # (t, label) transient/start times for the near-word check
        self.events_t = []
        y, t0, t_end = self.render(A, rooms)
        self.y, self.t0, self.cut_at = y, t0, t_end
        self.gain_db = 0.0
        self.duck_max = 0.0
        self.rule = ""

    @property
    def t1(self):
        return self.t0 + self.y.shape[1] / SR

    def render(self, A, rooms):
        s = self.s
        src = source(s["src"])
        cpan = s.get("pan", 0.0)
        if self.kind == "events":
            evs = []
            for e in s["events"]:
                t = A(e["at"]) + e.get("offset", 0.0)
                rate = e.get("rate", 1.0)
                src_at = e.get("src_at", 0.0)
                pre, dur = e.get("pre", 0.03), e.get("dur", src.shape[1] / SR - src_at)
                a, b = max(0, N(src_at - pre)), min(src.shape[1], N(src_at + dur))
                seg = src[:, a:b]
                if rate != 1.0:
                    seg = sounds.repitch(seg, rate)
                pre_eff = (N(src_at) - a) / SR / rate
                seg = fades(seg, a=min(0.003 if pre < 0.05 else 0.02, seg.shape[1] / SR / 4), r=min(0.04, seg.shape[1] / SR / 3))
                seg = dpan(seg, e.get("pan", cpan)) * db2a(e.get("gain", 0.0))
                evs.append((t - pre_eff, seg, t))
                self.onsets.append((t, e["at"]))
                self.events_t.append(t)
            t0 = min(x[0] for x in evs)
            n = max(N(x[0] - t0) + x[1].shape[1] for x in evs)
            y = np.zeros((2, n))
            for st, seg, _ in evs:
                i = N(st - t0)
                y[:, i:i + seg.shape[1]] += seg
            t_end = None
        else:  # bed
            t0 = A(s["start"])
            t_end = A(s["end"]) if "end" in s else t0 + s["end_rel"]
            n = N(t_end - t0)
            a, b = N(s.get("src_from", 0.0)), N(s.get("src_to", src.shape[1] / SR))
            loop = src[:, a:b]
            if n > loop.shape[1]:
                xf = N(0.5)
                out = loop.copy()
                while out.shape[1] < n:
                    w = np.linspace(0, 1, xf)
                    nxt = loop.copy()
                    out[:, -xf:] = out[:, -xf:] * np.sqrt(1 - w) + nxt[:, :xf] * np.sqrt(w)
                    out = np.concatenate([out, nxt[:, xf:]], axis=1)
                loop = out
            y = loop[:, :n].copy()
            if "gate" in s:
                g = np.zeros(n)
                for at, d in s["gate"]:
                    i = N(A(at) - t0)
                    g[i:i + N(d)] = 1.0
                g[N(A(s["steady_from"]) - t0):] = 1.0
                g = uniform_filter1d(g, N(0.003))
                y = y * g
            y = fades(y, a=s.get("fade_in", 0.01), r=s.get("fade_out", 0.0) if not s.get("cut_end") else 0.0)
            if s.get("respect_holes", True):        # beds drop out inside the song's own chops and micro-silences (after 1 s)
                g = np.ones(n)
                for a_, b_ in A.holes:
                    i, j = N(a_ - t0), N(b_ - t0)
                    if j > 0 and i < n:
                        g[max(0, i):min(n, j)] = 0.0
                g = uniform_filter1d(minimum_filter1d(g, N(0.006)), N(0.004))
                y = y * g
            if "width" in s:
                y = narrow(y, s["width"])
            y = dpan(y, cpan) if cpan else y
            self.onsets.append((t0, s["start"]))
        pr = s.get("proc", {})
        if pr.get("hp"):
            y = hp(y, pr["hp"], 2)
        if pr.get("lp"):
            y = lp(y, pr["lp"], 4)
        if pr.get("dip"):
            y = peq(y, 2600, pr["dip"], 1.0)
        y = room(y, rooms.get(pr.get("room", "none")), seed=sum(map(ord, self.id)))
        if self.kind == "bed" and s.get("cut_end"):
            k = N(t_end - t0)
            y = y[:, :k]
            y = fades(y, r=0.003)
        elif self.kind == "bed":
            y = y[:, :N(t_end - t0) + N(0.6)]
        return y, t0, t_end

    # loudness helpers (gain applied)
    def frames(self, refM, win, gain=None, tail=0.0):
        g = self.gain_db if gain is None else gain
        pad = N(0.5)
        yk = kpow(np.pad(self.y * db2a(g), ((0, 0), (pad, pad))))
        M = Momentary(yk, self.t0 - 0.5)
        ts = np.arange(self.t0, self.t1 + tail, 0.01)
        cM, sM = M(ts, win=win), refM(ts, win=win)
        act = cM > cM.max() - 20
        return ts, cM, sM, act


def vocal_word(vocM, ts):
    pad = 30
    tp = np.concatenate([ts[0] - 0.01 * np.arange(pad, 0, -1), ts, ts[-1] + 0.01 * np.arange(1, pad + 1)])
    v = vocM(tp, win=VOCAL_WIN)
    pk = maximum_filter1d(v, 2 * pad + 1)[pad:-pad]
    v = v[pad:-pad]
    return v, (v >= VOCAL_ON) & (v >= pk - VOCAL_WORD)


def band_follow(c, song):
    """Bed option 'band_follow': {lo, hi, margin}: hold the cue `margin` dB under the song inside lo-hi Hz (50 ms RMS,
    smoothed), so a bed never fills a hole the song's arrangement leaves in its band (layer-side gain only)."""
    bf = c.s.get("band_follow")
    if not bf:
        return
    i0 = N(c.t0)
    y = c.y * db2a(c.gain_db)
    seg = song[:, i0:i0 + y.shape[1]]
    if seg.shape[1] < y.shape[1]:
        seg = np.pad(seg, ((0, 0), (0, y.shape[1] - seg.shape[1])))
    from dsp import bp
    w = N(0.05)
    es = uniform_filter1d(bp(seg, bf["lo"], bf["hi"], 2).mean(0) ** 2, w)
    ec = uniform_filter1d(bp(y, bf["lo"], bf["hi"], 2).mean(0) ** 2, w)
    need = 10 * np.log10(es + 1e-14) - bf["margin"] - 10 * np.log10(ec + 1e-14)
    d = np.minimum(0.0, need)
    d = uniform_filter1d(minimum_filter1d(d, N(0.08)), N(0.06))
    c.y = c.y * db2a(d)
    c.duck_max = min(c.duck_max, float(d.min()))
    c.rule += f"; follows the song in {bf['lo']}-{bf['hi']} Hz"


def fit(c, songM, vocM, song=None):
    lv = c.s["level"]
    if "abs_lufs" in lv:
        ts, cM, sM, act = c.frames(songM, 0.4, 0.0)
        c.gain_db = lv["abs_lufs"] - float(np.median(cM[act]))
        c.rule = f"absolute {lv['abs_lufs']} LUFS (song has ended)"
    else:
        ts, cM, sM, act = c.frames(songM, 0.4, 0.0)
        live = act & (sM > SONG_QUIET)
        if not live.any():
            live = act
        m = sM[live] - cM[live]
        opts = {"median margin": float(np.median(m) - lv["margin"]),
                "worst-frame margin": float(m.min() - lv.get("floor", MIN_MARGIN))}
        cap = lv.get("cap")
        if cap is not None:
            opts["peak cap"] = cap - peak_db(c.y)
        c.rule = min(opts, key=opts.get)
        c.gain_db = opts[c.rule]
    if song is not None:
        band_follow(c, song)
    under_vocal(c, vocM)


def under_vocal(c, vocM):
    ride = c.kind == "bed" and c.s.get("duck", False)
    for _ in range(4):
        ts, cM, vS, act = c.frames(vocM, VOCAL_WIN, tail=VOCAL_WIN / 2)
        v, word = vocal_word(vocM, ts)
        pres = act & word
        if not pres.any():
            return
        need = np.where(pres, v - VOCAL_FIT - cM, np.inf)
        if need.min() >= 0:
            return
        if not ride:
            c.gain_db += float(need.min())
            c.rule += "; under the vocal"
            return
        d = np.minimum(0.0, np.where(np.isfinite(need), need, 0.0))
        d = uniform_filter1d(minimum_filter1d(d, 11), 5) - 0.3 * (d < 0)
        g = db2a(np.interp(c.t0 + np.arange(c.y.shape[1]) / SR, ts, d))
        c.y = c.y * g
        c.duck_max = min(c.duck_max, float(d.min()))
        if "ducks" not in c.rule:
            c.rule += "; ducks under the vocal"


def sum_layer(cues, n):
    lay = np.zeros((2, n))
    for c in cues:
        i = N(c.t0)
        y = c.y * db2a(c.gain_db)
        a, b = max(0, i), min(n, i + y.shape[1])
        if b > a:
            lay[:, a:b] += y[:, a - i:b - i]
    for a, b in ZERO_SPANS:
        lay[:, N(a):N(b)] = 0.0
    return lay


def overlap_pass(cues, songM, vocM, n, log):
    for it in range(10):
        layM = Momentary(kpow(sum_layer(cues, n)))
        trims = {}
        for c in cues:
            ts, cM, sM, act = c.frames(songM, 0.4)
            live = act & (sM > SONG_QUIET)
            if live.any() and "abs_lufs" not in c.s["level"]:
                m = sM[live] - layM(ts[live])
                if m.min() < MIN_MARGIN + 0.4:
                    trims[c.id] = max(trims.get(c.id, 0), MIN_MARGIN + 0.5 - m.min())
            ts1, cS, vS, act1 = c.frames(vocM, VOCAL_WIN)
            v, word = vocal_word(vocM, ts1)
            pres = act1 & word
            if pres.any():
                mv = v[pres] - layM(ts1[pres], win=VOCAL_WIN)
                if mv.min() < MIN_MARGIN + 0.4:
                    # trim whichever overlapping cue is loudest at that frame
                    j = int(np.argmin(mv))
                    tj = ts1[pres][j]
                    lv = []
                    for o in cues:
                        if o.t0 - 0.05 <= tj <= o.t1 + 0.05:
                            _, oc, _, _ = o.frames(vocM, VOCAL_WIN)
                            k = int(round((tj - o.t0) / 0.01))
                            lv.append((oc[min(max(k, 0), len(oc) - 1)], o.id))
                    top = max(lv)[0] if lv else None
                    for val, oid in lv:
                        if val >= top - 6:
                            trims[oid] = max(trims.get(oid, 0), MIN_MARGIN + 0.5 - mv.min())
        if not trims:
            return
        log(f"overlap pass {it}: " + ", ".join(f"{k} -{v:.1f} dB" for k, v in trims.items()))
        for c in cues:
            if c.id in trims:
                c.gain_db -= trims[c.id]
                c.rule += "; trimmed in the sum"


# ------------------------------------------------------------------------------------------------ QA measurements
BANDS = 1000 * 2.0 ** (np.arange(-15, 15) / 3)       # 1/3-octave centres ~31 Hz .. 16 kHz


def band_powers(y, nper=2048, hop=512):
    f, t, Z = stft(stereo(y).mean(0), SR, nperseg=nper, noverlap=nper - hop, boundary=None, padded=False)
    Pw = np.abs(Z) ** 2
    out = np.zeros((len(BANDS), Pw.shape[1]))
    for i, fc in enumerate(BANDS):
        m = (f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))
        if m.any():
            out[i] = Pw[m].sum(0)
    return out, t


def band_margin(c, song, gain=None):
    """Masking margin in the cue's own bands: per 43 ms frame where the cue is active (within 20 dB of its loudest frame),
    take the 1/3-octave bands where the cue is within 10 dB of its strongest band, and compare the song's power in those
    bands with the cue's. > 0: the song is louder than the cue where the cue lives (it sits under / blends); < 0: it sticks out."""
    g = c.gain_db if gain is None else gain
    i0 = N(c.t0)
    y = c.y * db2a(g)
    i1 = min(song.shape[1], i0 + y.shape[1])
    if i1 - i0 < 4096:
        return None
    cb, _ = band_powers(y[:, :i1 - i0])
    sb, _ = band_powers(song[:, i0:i1])
    k = min(cb.shape[1], sb.shape[1])
    cb, sb = cb[:, :k], sb[:, :k]
    tot = cb.sum(0)
    act = tot > tot.max() * 10 ** -2.0
    ms, doms, tj = [], [], []
    for j in np.where(act)[0]:
        tj.append(c.t0 + (j * 512 + 1024) / SR)
        sel = cb[:, j] >= cb[:, j].max() * 0.1
        ms.append(10 * np.log10((sb[sel, j].sum() + 1e-20) / (cb[sel, j].sum() + 1e-20)))
        doms.append(BANDS[int(np.argmax(cb[:, j]))])
    if not ms:
        return None
    ms = np.array(ms)
    return {"median": float(np.median(ms)), "min": float(ms.min()), "p10": float(np.percentile(ms, 10)),
            "band_hz": float(np.median(doms)), "t_min": float(tj[int(np.argmin(ms))])}


# ------------------------------------------------------------------------------------------------ endings
def ending_B(song, voc):
    """Song + natural tails made from its own material: (1) the last sung note 'line' (vocal stem 229.9-230.76) through a
    2.6 s RT60 room, wet only after the note ends; (2) the final D drone (song 236.30-237.84, after the last hit) through a 3 s
    RT60 hall, wet only from the drone's cut at 237.840 on, so it decays over ~3.5 s instead of stopping. The song itself is
    untouched except a 25 ms fade on its last samples (it ends on a non-zero sample: a click once anything follows)."""
    ext = N(EXT_B)
    n0 = song.shape[1]
    out = np.concatenate([song, np.zeros((2, ext))], axis=1)
    out[:, n0 - N(0.025):n0] *= np.linspace(1, 0, N(0.025)) ** 2
    # (1) 'line'
    a, b = N(229.90), N(230.76)
    note = voc[:, a:b]
    h = ir(4.0, 2.6, lp_hz=6000, hp_hz=200, seed=11, predelay=0.02)
    wet = np.stack([fftconvolve(note[0], h[0]), fftconvolve(note[1], h[1])])
    rms_note = np.sqrt(np.mean(note[:, -N(0.3):] ** 2))
    tail = wet[:, note.shape[1]:]
    tail = tail / (np.sqrt(np.mean(tail[:, :N(0.05)] ** 2)) + 1e-12) * rms_note * db2a(-12)
    tail = fades(tail, a=0.04)
    out[:, b:b + tail.shape[1]] += tail[:, :out.shape[1] - b]
    # (2) the drone
    a, b = N(236.30), N(237.84)
    dr = song[:, a:b]
    h = ir(5.0, 3.0, lp_hz=5000, hp_hz=25, seed=12)
    wet = np.stack([fftconvolve(dr[0], h[0]), fftconvolve(dr[1], h[1])])
    tail = wet[:, dr.shape[1]:]
    rms_dr = np.sqrt(np.mean(dr[:, -N(0.25):] ** 2))
    tail = tail / (np.sqrt(np.mean(tail[:, :N(0.05)] ** 2)) + 1e-12) * rms_dr * db2a(-4)
    tail = fades(tail, a=0.012)
    room_n = out.shape[1] - b
    tail = tail[:, :room_n]
    tail = fades(tail, r=0.4)
    out[:, b:b + tail.shape[1]] += tail
    notes = {"line_tail": "vocal stem 229.90-230.76 -> synthetic room RT60 2.6 s (HP 200, LP 6 kHz), wet only from 230.76, starts 12 dB under the note's last 0.3 s",
             "drone_tail": "song 236.30-237.84 (D drone after the last hit) -> synthetic hall RT60 3.0 s (HP 25, LP 5 kHz), wet only from 237.840, starts 4 dB under the drone, decays to the new end",
             "song_edit": "25 ms fade on the song's final samples (238.295-238.320); otherwise untouched",
             "length_s": out.shape[1] / SR}
    return out, notes


# ------------------------------------------------------------------------------------------------ plots
def plots(song, layer, voc, cues, A, qa):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    secs = A.tm["sections"]
    groups = [(s["name"], s["start"], s["end"]) for s in secs if s["name"] not in ("yes", "silence")]
    groups = [(n, a, (149.72 if n == "verse3_band" else b)) for n, a, b in groups]
    groups[-1] = (groups[-1][0], groups[-1][1], 238.32 + EXT_B)
    mono_s, mono_l = song.mean(0), layer.mean(0)
    kS, kL, kV = Momentary(kpow(song)), Momentary(kpow(layer)), Momentary(kpow(voc))
    files = []
    for gi, (name, a, b) in enumerate(groups):
        a0, b0 = max(0, a - 0.3), b + 0.3
        fig, ax = plt.subplots(3, 1, figsize=(18, 9), sharex=True, gridspec_kw={"height_ratios": [3, 3, 1.6]})
        for k, (y, ttl) in enumerate([(mono_s, "song (mix input)"), (mono_l, "layer alone (same scale)")]):
            i0, i1 = N(a0), min(len(y), N(b0))
            if i1 - i0 < 4096:
                continue
            f, t, Z = stft(y[i0:i1], SR, nperseg=2048, noverlap=2048 - 256)
            Pw = 10 * np.log10(np.abs(Z) ** 2 + 1e-14)
            ax[k].pcolormesh(t + a0, f, Pw, shading="auto", cmap="magma", vmin=-120, vmax=-30)
            ax[k].set_yscale("symlog", linthresh=400)
            ax[k].set_ylim(30, 16000)
            ax[k].set_ylabel(ttl + "\nHz")
        tt_ = np.arange(a0, b0, 0.02)
        ax[2].plot(tt_, kS(tt_), color="0.3", lw=1, label="song momentary (LUFS)")
        ax[2].plot(tt_, kV(tt_, win=VOCAL_WIN), color="tab:blue", lw=0.6, alpha=0.6, label="vocal stem 50 ms")
        ax[2].plot(tt_, kL(tt_), color="tab:red", lw=1.2, label="layer momentary")
        ax[2].set_ylim(-75, -5)
        ax[2].legend(loc="lower left", fontsize=7, ncol=3)
        for w in A.words:
            if a0 <= w[0] <= b0:
                for k in range(2):
                    ax[k].axvline(w[0], color="cyan", lw=0.5, alpha=0.5)
                ax[0].text(w[0], 13000, w[2], color="cyan", fontsize=6, rotation=90, va="top")
        for h in A.tm["hits"]:
            if a0 <= h["t"] <= b0 and h["strength"] >= 0.9:
                ax[2].axvline(h["t"], color="0.75", lw=0.4)
        cols = plt.cm.tab20(np.linspace(0, 1, 20))
        j = 0
        for c in cues:
            if c.t1 < a0 or c.t0 > b0:
                continue
            col = cols[j % 20]
            j += 1
            for k in range(2):
                ax[k].axvspan(max(c.t0, a0), min(c.t1, b0), color=col, alpha=0.18)
            for t in c.events_t or [c.t0]:
                ax[1].axvline(t, color=col, lw=1.2)
            q = qa["cues"].get(c.id, {})
            lab = c.id + (f"  {q.get('song_med', 0):.0f}/{q.get('song_worst', 0):.0f} dB" if q else "")
            ax[1].text(max(c.t0, a0), 60 + 25 * (j % 6), lab, color="white", fontsize=7,
                       bbox=dict(facecolor=col, alpha=0.7, pad=1, lw=0))
        ax[0].set_title(f"Chaos Monkey sound layer, section '{name}' {a:.2f}-{b:.2f} s. Cyan = word onsets; shaded = cue spans; "
                        f"labels = cue id + margin under the song (median/worst, 400 ms)", fontsize=9, loc="left")
        ax[2].set_xlim(a0, b0)
        ax[2].set_xlabel("song time (s)")
        plt.tight_layout()
        fn = os.path.join(PLOTS, f"sound_{gi:02d}_{name}.png")
        plt.savefig(fn, dpi=72)
        plt.close(fig)
        files.append(os.path.relpath(fn, ROOT))
    return files


def plot_endings(mixes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    a0, b0 = 233.0, 238.32 + EXT_B + 0.1
    fig, ax = plt.subplots(4, 1, figsize=(16, 11), sharex=True, gridspec_kw={"height_ratios": [2, 2, 2, 1.6]})
    tt_ = np.arange(a0, b0, 0.01)
    lab = {"A": "A: as the song is (hard cut 238.320)", "B": "B: natural tails ('line' + drone), +3.6 s",
           "C": "C: song cut at 237.840 + 3 s attic room tone"}
    for k, (v, y) in enumerate(mixes.items()):
        yy = np.pad(y, ((0, 0), (0, max(0, N(b0) - y.shape[1]))))
        f, t, Z = stft(yy.mean(0)[N(a0):N(b0)], SR, nperseg=2048, noverlap=2048 - 256)
        ax[k].pcolormesh(t + a0, f, 10 * np.log10(np.abs(Z) ** 2 + 1e-14), shading="auto", cmap="magma", vmin=-130, vmax=-30)
        ax[k].set_yscale("symlog", linthresh=400)
        ax[k].set_ylim(30, 16000)
        ax[k].set_ylabel(lab[v], fontsize=8)
        M = Momentary(kpow(yy))
        ax[3].plot(tt_, M(tt_, win=0.1), lw=1, label=f"{v} (100 ms loudness)")
    for t, s_ in [(235.833, "last hit / flashlight OFF"), (237.840, "drone cut / neon OFF tick"), (238.320, "song file end")]:
        for k in range(4):
            ax[k].axvline(t, color="cyan", lw=0.7)
        ax[0].text(t, 14000, s_, color="cyan", fontsize=7, va="top")
    ax[3].set_ylim(-100, -5)
    ax[3].legend(fontsize=7)
    ax[3].set_xlabel("time (s)")
    ax[0].set_title("Ending variants (mix_v1_endA/B/C.wav)", loc="left", fontsize=9)
    plt.tight_layout()
    fn = os.path.join(PLOTS, "sound_12_endings.png")
    plt.savefig(fn, dpi=72)
    plt.close(fig)
    return os.path.relpath(fn, ROOT)


# ------------------------------------------------------------------------------------------------ main
def write24(path, y):
    sf.write(path, np.clip(y, -1, 1 - 2 ** -23).T, SR, subtype="PCM_24")


def main(argv):
    log = print
    if "--sources" in argv:
        sounds.main([])
    os.makedirs(OUTD, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(PLOTS, exist_ok=True)
    spec = json.load(open(CUES))
    A = Anchors()
    song = load(SONG)
    voc = load(VOCALS)
    n = song.shape[1]
    songM, vocM = Momentary(kpow(song)), Momentary(kpow(voc))
    rooms = spec["rooms"]
    cues = [Cue(s, A, rooms) for s in spec["cues"]]
    for c in cues:
        fit(c, songM, vocM, song)
    main_cues = [c for c in cues if "A" in c.variants]
    overlap_pass(main_cues, songM, vocM, n, log)

    # true-peak guard on the mix (layer only)
    layer = sum_layer(main_cues, n)
    mix = song + layer
    tp_song, tp_mix = true_peak_db(song), true_peak_db(mix)
    if tp_mix > TP_LIMIT:
        raise SystemExit(f"mix true peak {tp_mix:.2f} dBTP > {TP_LIMIT}: lower the cue caps")

    # ---- ending variants
    nC = n + N(3.0) + N(0.02)
    cC = [c for c in cues if "C" in c.variants]
    layerC = sum_layer(cC, nC)
    # C: the song is cut at the drone's cut (237.840; 2 ms ramp, under the relay tick) so the tick is the only click; its
    # 0.48 s residual tail (-38 dBFS) and the file's own end step at 238.320 are dropped; then 3 s of faint room tone.
    kC = N(A("sync:Hum/drone"))
    songC = np.concatenate([song[:, :kC] * np.concatenate([np.ones(kC - N(0.002)), np.linspace(1, 0, N(0.002))]),
                            np.zeros((2, nC - kC))], axis=1)
    mixC = songC + layerC
    songB, notesB = ending_B(song, voc)
    layerB = np.concatenate([layer, np.zeros((2, songB.shape[1] - n))], axis=1)
    mixB = songB + layerB
    # C: trim after the room tone stops (+20 ms of digital silence)
    stopC = N(A("sync:Hum/drone") + 3.0)
    mixC, layerC = mixC[:, :stopC + N(0.02)], layerC[:, :stopC + N(0.02)]

    write24(os.path.join(OUTD, "layer_v1.wav"), layer)
    write24(os.path.join(OUTD, "layer_v1_endC.wav"), layerC)
    write24(os.path.join(OUTD, "mix_v1.wav"), mix)
    write24(os.path.join(OUTD, "mix_v1_endA.wav"), mix)
    write24(os.path.join(OUTD, "mix_v1_endB.wav"), mixB)
    write24(os.path.join(OUTD, "mix_v1_endC.wav"), mixC)

    # ---- QA
    qa = {"cues": {}}
    layM = Momentary(kpow(layer))
    for c in cues:
        ts, cM, sM, act = c.frames(songM, 0.4)
        live = act & (sM > SONG_QUIET)
        ref_layer = layM if "A" in c.variants else Momentary(kpow(layerC))
        ms = (sM[live] - cM[live]) if live.any() else np.array([np.nan])
        msum = (sM[live] - ref_layer(ts[live])) if live.any() else np.array([np.nan])
        ts1, cS, vS, act1 = c.frames(vocM, VOCAL_WIN)
        v, word = vocal_word(vocM, ts1)
        pres = act1 & word
        mv = (v[pres] - ref_layer(ts1[pres], win=VOCAL_WIN)) if pres.any() else None
        bm = band_margin(c, song if "A" in c.variants else songC)
        near = []
        for t, lab in c.onsets:
            for w, wt, lid in A.near_words(t):
                near.append({"cue_t": round(t, 3), "word": w, "word_t": wt, "line": lid, "dt_ms": round((t - wt) * 1000)})
        y = c.y * db2a(c.gain_db)
        qa["cues"][c.id] = {
            "shot": c.s["shot"], "t0": round(c.t0, 3), "t1": round(c.t1, 3),
            "times": [round(t, 3) for t in (c.events_t or [c.t0])], "end": None if c.cut_at is None else round(c.cut_at, 3),
            "gain_db": round(c.gain_db, 2), "peak_dbfs": round(peak_db(y), 1), "rule": c.rule, "duck_max_db": round(c.duck_max, 1),
            "song_med": round(float(np.nanmedian(ms)), 1), "song_worst": round(float(np.nanmin(msum)), 1),
            "song_lufs_med": round(float(np.median(sM[act])), 1),
            "vocal_worst": None if mv is None else round(float(mv.min()), 1),
            "band": None if bm is None else {k: round(v_, 1) for k, v_ in bm.items()},
            "near_words": near, "picture_dependent": c.s.get("picture_dependent", False), "variants": c.variants,
            "src": c.s["src"], "pan": c.s.get("pan", 0.0), "intent": c.s["intent"],
            "anchors": [e["at"] for e in c.s.get("events", [])] or [c.s.get("start"), c.s.get("end", f"+{c.s.get('end_rel')}")],
        }
    # null test + zero spans + loudness
    inside = np.zeros(n, bool)
    for c in main_cues:
        inside[max(0, N(c.t0)):min(n, N(c.t1))] = True
    outside_nonzero = int(np.count_nonzero(layer[:, ~inside]))
    zero_ok = all(np.count_nonzero(layer[:, N(a):N(b)]) == 0 for a, b in ZERO_SPANS)
    after_end = round(peak_db(layer[:, N(A("sync:Hum/drone")) + N(0.10):]), 1)   # the relay tick's room tail after +0.1 s
    mx, _ = sf.read(os.path.join(OUTD, "mix_v1.wav"), always_2d=True, dtype="float64")
    lx, _ = sf.read(os.path.join(OUTD, "layer_v1.wav"), always_2d=True, dtype="float64")
    readback_err = float(np.abs(mx.T - song - lx.T).max())
    qa["global"] = {
        "song_lufs": round(integrated_lufs(song), 2), "mix_lufs": round(integrated_lufs(mix), 2),
        "layer_lufs": round(integrated_lufs(layer), 1),
        "song_tp": round(tp_song, 2), "mix_tp": round(tp_mix, 2), "layer_peak": round(peak_db(layer), 1),
        "mixB_tp": round(true_peak_db(mixB), 2), "mixC_tp": round(true_peak_db(mixC), 2),
        "mixB_lufs": round(integrated_lufs(mixB), 2), "mixC_lufs": round(integrated_lufs(mixC), 2),
        "len": {"A": n / SR, "B": mixB.shape[1] / SR, "C": mixC.shape[1] / SR},
        "null_outside_cues_nonzero": outside_nonzero, "cue_span_s": round(inside.sum() / SR, 1),
        "zero_spans_exact": zero_ok, "layer_peak_after_237.94": after_end, "readback_max_abs_err": readback_err,
        "ebur128_song": ebur128(SONG), "ebur128_mix": ebur128(os.path.join(OUTD, "mix_v1.wav")),
        "endB": notesB,
        "clipped_mix": int(np.count_nonzero(np.abs(mix) >= 1.0)),
    }
    if "--no-plots" not in argv:
        qa["plots"] = plots(song, layer, voc, main_cues, A, qa)
        qa["plots"].append(plot_endings({"A": mix, "B": mixB, "C": mixC}))
    json.dump(qa, open(os.path.join(WORK, "qa.json"), "w"), indent=1, ensure_ascii=False)
    write_doc(qa, cues)
    g = qa["global"]
    log(f"cues {len(cues)}  song {g['song_lufs']} LUFS / {g['song_tp']} dBTP -> mix {g['mix_lufs']} LUFS / {g['mix_tp']} dBTP; "
        f"layer {g['layer_lufs']} LUFS; null outside {g['null_outside_cues_nonzero']}; zero spans {g['zero_spans_exact']}")


# ------------------------------------------------------------------------------------------------ doc tables
def fmt_t(x):
    return f"{x:.3f}"


def write_doc(qa, cues):
    rows = []
    rows.append("| # | cue | shot | time (s) / anchor | source | level: gain, peak | pan | under song med / worst (400 ms) | under vocal worst (50 ms) | band margin med / min @ band | pic | intent |")
    rows.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(cues, 1):
        q = qa["cues"][c.id]
        if c.kind == "bed":
            when = f"{q['t0']:.3f}-{q['end'] if q['end'] else q['t1']:.3f} (`{c.s['start']}` -> `{c.s.get('end', '+' + str(c.s.get('end_rel')))}`)"
        else:
            when = ", ".join(f"{t:.3f}" for t in q["times"]) + " (" + ", ".join(f"`{a}`" for a in q["anchors"]) + ")"
        b = q["band"]
        band = "-" if b is None else f"{b['median']:+.0f} / {b['min']:+.0f} @ {b['band_hz']:.0f} Hz"
        voc = "-" if q["vocal_worst"] is None else f"{q['vocal_worst']:.1f}"
        var = "" if c.variants == ["A", "B", "C"] else f" (end {','.join(c.variants)} only)"
        rows.append(f"| {i} | **{c.id}**{var} | {q['shot']} | {when} | `{c.s['src']}` | {q['gain_db']:+.1f} dB, {q['peak_dbfs']:.1f} dBFS ({q['rule']}) "
                    f"| {q['pan']} | {q['song_med']:.1f} / {q['song_worst']:.1f} | {voc} | {band} | {'yes' if q['picture_dependent'] else ''} | {q['intent']} |")
    near = ["| cue | cue time | word | word onset | line | dt (ms) |", "|---|---|---|---|---|---|"]
    for c in cues:
        for x in qa["cues"][c.id]["near_words"]:
            near.append(f"| {c.id} | {x['cue_t']:.3f} | {x['word']} | {x['word_t']:.3f} | {x['line']} | {x['dt_ms']:+d} |")
    g = qa["global"]
    ver = [
        "| check | result |", "|---|---|",
        f"| integrated loudness | song **{g['song_lufs']} LUFS**, mix_v1 **{g['mix_lufs']} LUFS** (delta {g['mix_lufs']-g['song_lufs']:+.2f} LU); ffmpeg ebur128 song {g['ebur128_song'].get('integrated_lufs')} / mix {g['ebur128_mix'].get('integrated_lufs')} |",
        f"| true peak | song {g['song_tp']} dBTP, mix_v1 **{g['mix_tp']} dBTP** (limit {TP_LIMIT}), end B {g['mixB_tp']}, end C {g['mixC_tp']}; clipped samples {g['clipped_mix']} |",
        f"| layer alone | {g['layer_lufs']} LUFS integrated, sample peak {g['layer_peak']} dBFS |",
        f"| song untouched | mix - song = layer; layer non-zero outside the cue windows: **{g['null_outside_cues_nonzero']}** samples (cue windows {g['cue_span_s']} s of 238.32) |",
        f"| hole 15.440-15.515 and near-silence 149.285-149.525 | layer exactly 0: **{g['zero_spans_exact']}** |",
        f"| after the neon tick | layer peak from 237.94 on (the tick's own room tail): {g['layer_peak_after_237.94']} dBFS; nothing else sounds |",
        f"| files read back | max abs(mix_v1 - song - layer_v1) = {g['readback_max_abs_err']:.2e} (24-bit rounding: <= 1.2e-07) |",
        f"| lengths | A {g['len']['A']:.3f} s, B {g['len']['B']:.3f} s, C {g['len']['C']:.3f} s |",
        f"| loudness of the ending variants | B {g['mixB_lufs']} LUFS, C {g['mixC_lufs']} LUFS |",
    ]
    auto = ("<!-- AUTO:BEGIN (written by tools/audio/sfx/build_layer.py; edit docs/sound_cues.json, not this block) -->\n\n"
            "## Cue sheet (generated)\n\n"
            "Levels: *gain* is applied to the source as rendered (after its per-event gains); *peak* is the cue's sample peak in the layer. "
            "*Under song* = the song's momentary loudness (400 ms) minus the cue alone (median) and minus the whole summed layer (worst frame), "
            "frames where the song is silent (< -42 LUFS) excluded. *Under vocal* = the vocal stem minus the summed layer in 50 ms frames where a "
            "word sounds (rule >= 6). *Band margin* = song minus cue in the cue's own 1/3-octave bands (bands within 10 dB of the cue's strongest), "
            "per 43 ms frame while the cue sounds: > 0 the cue is under the song where it lives; < 0 it pokes out of the song in its band "
            "(fine in the quiet spots where the cue is meant to be heard alone). *pic* = picture-dependent (re-time after the cut).\n\n"
            + "\n".join(rows) +
            "\n\n## Cues within 150 ms of a lyric word onset (generated)\n\n" + "\n".join(near) +
            "\n\n## Verification (generated)\n\n" + "\n".join(ver) +
            "\n\nSpectrograms with cues overlaid: " + ", ".join(f"`{p}`" for p in qa.get("plots", [])) +
            "\n\n<!-- AUTO:END -->")
    txt = open(DOC).read() if os.path.exists(DOC) else "# Chaos Monkey: sound layer\n\n"
    if "<!-- AUTO:BEGIN" in txt:
        txt = re.sub(r"<!-- AUTO:BEGIN.*?<!-- AUTO:END -->", lambda m: auto, txt, flags=re.S)
    else:
        txt = txt.rstrip() + "\n\n" + auto + "\n"
    open(DOC, "w").write(txt)


if __name__ == "__main__":
    main(sys.argv[1:])

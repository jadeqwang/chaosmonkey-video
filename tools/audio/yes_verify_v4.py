#!/usr/bin/env python3
"""Measurements for the G5 "Yes" shift (tools/audio/yes_shift_v4.py). Nobody can listen, so everything here is a number or a plot.

    TMPDIR=$PWD/work/tmp $PY tools/audio/yes_verify_v4.py   -> work/sound_v4/verify.json, work/review/sound_v4/*.png
"""
import hashlib
import json
import os

import librosa
import matplotlib
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt, stft

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)  # noqa
SR = 48000
E = json.load(open(P("work", "sound_v4", "edit.json")))
D = E["shift_samples"]
REV = P("work", "review", "sound_v4")
os.makedirs(REV, exist_ok=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def band(x, lo, hi):
    return sosfiltfilt(butter(6, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12))


def S(a, b, x):
    return x[int(round(a * SR)):int(round(b * SR))]


def main():
    o16, _ = sf.read(P(E["song_in"]), dtype="int16", always_2d=True)
    e16, _ = sf.read(P(E["song_out"]), dtype="int16", always_2d=True)
    i0, j1 = E["changed_span_samples"]
    diff = e16.astype(np.int32) - o16.astype(np.int32)
    nz = np.nonzero(np.any(diff != 0, axis=1))[0]
    outside = np.ones(len(diff), bool)
    outside[i0:j1] = False
    res = {"files": {"original_sha256": sha(P(E["song_in"])), "edited_sha256": sha(P(E["song_out"])),
                     "samples": [len(o16), len(e16)]},
           "bit_identity": {"nonzero_diff_samples_outside_span": int(np.count_nonzero(diff[outside])),
                            "first_last_changed_s": [float(nz[0] / SR), float(nz[-1] / SR)] if len(nz) else None,
                            "span_s": E["changed_span_s"]}}
    o = o16.astype(np.float64).mean(1) / 32768
    e = e16.astype(np.float64).mean(1) / 32768
    voc = sf.read(P("work", "stems", "vocals.wav"), dtype="float64", always_2d=True)[0].mean(1)
    ins = sf.read(P("work", "stems", "instrumental.wav"), dtype="float64", always_2d=True)[0].mean(1)

    # ---- the edited song = instrumental stem + moved word exactly (so the residue at the old place IS the instrumental stem there)
    wv = sf.read(P("work", "stems", "vocals_v4.wav"), dtype="float64", always_2d=True)[0].mean(1)
    a, b = 148.60, 149.95
    res["edited_equals_instrumental_plus_moved_vocal"] = {
        "rms_error_db": rms_db(S(a, b, e) - S(a, b, ins) - S(a, b, wv)), "signal_rms_db": rms_db(S(a, b, e)),
        "note": "error is the 16-bit rounding of the edited file (~-101 dBFS rms)"}
    # ---- ghost. The word is whispered (pyin finds no voicing): vowel 148.78-149.04 with energy 500-1100 Hz, then the 's'
    # 149.04-149.285 at 5-9 kHz. At the old place the edited song is the instrumental stem, so any ghost is word energy that
    # the separator left in the instrumental stem. Compare it, band by band, with the instrumental stem where there is no word.
    VOW, SIB = (148.78, 149.04), (149.04, 149.285)
    NB = {"pre_gap": (148.57, 148.70), "old_hole": (149.30, 149.58)}
    bands = {"vowel 500-1100 Hz": (500, 1100), "speech 300-4000 Hz": (300, 4000), "sibilant 5-9 kHz": (5000, 9000), "low 40-250 Hz": (40, 250)}
    g = {}
    for name, (lo, hi) in bands.items():
        ib_, vb_ = band(ins, lo, hi), band(voc, lo, hi)
        g[name] = {"word_in_vocal_stem_vowel": rms_db(S(*VOW, vb_)), "word_in_vocal_stem_s": rms_db(S(*SIB, vb_)),
                   "residue_at_old_vowel": rms_db(S(*VOW, ib_)), "residue_at_old_s": rms_db(S(*SIB, ib_)),
                   **{f"backing_{k}": rms_db(S(*w, ib_)) for k, w in NB.items()}}
    res["ghost_bands_db"] = g
    # time-aligned spectral-shape test: cosine similarity between the word's spectrum and the residue's, frame by frame (300 Hz-10 kHz),
    # at lag 0 versus lags of 50-300 ms. A ghost would make lag 0 stand out.
    def mag(x, t0, t1):
        return np.abs(librosa.stft(S(t0, t1, x), n_fft=2048, hop_length=480))
    fb = np.fft.rfftfreq(2048, 1 / SR)
    sel = (fb >= 300) & (fb <= 10000)
    Wm = mag(voc, 148.78, 149.285)[sel]
    big = mag(ins, 148.40, 149.70)[sel]
    j0 = int(round((148.78 - 148.40) * SR / 480))
    def sim(lag):
        R = big[:, j0 + lag:j0 + lag + Wm.shape[1]]
        num = (Wm * R).sum(0)
        den = np.linalg.norm(Wm, axis=0) * np.linalg.norm(R, axis=0) + 1e-20
        return float(np.mean(num / den))
    lags = [l for l in range(-30, 31) if abs(l) >= 5 and j0 + l >= 0 and j0 + l + Wm.shape[1] <= big.shape[1]]
    others = [sim(l) for l in lags]
    res["ghost_shape_similarity"] = {"lag0": sim(0), "other_lags_median": float(np.median(others)), "other_lags_max": float(np.max(others)),
                                     "other_lags_n": len(others), "lag_range_ms": [lags[0] * 10, lags[-1] * 10]}
    # self-check that the test can see a ghost: add the word 30 dB down into the residue and repeat
    big_t = mag(ins + np.concatenate([np.zeros(0), voc]) * 10 ** (-30 / 20), 148.40, 149.70)[sel]
    def sim_t(lag, B):
        R = B[:, j0 + lag:j0 + lag + Wm.shape[1]]
        return float(np.mean((Wm * R).sum(0) / (np.linalg.norm(Wm, axis=0) * np.linalg.norm(R, axis=0) + 1e-20)))
    res["ghost_shape_similarity"]["sanity_word_added_at_-30dB"] = {"lag0": sim_t(0, big_t), "other_lags_median": float(np.median([sim_t(l, big_t) for l in lags]))}
    big_t = mag(ins + voc * 10 ** (-40 / 20), 148.40, 149.70)[sel]
    res["ghost_shape_similarity"]["sanity_word_added_at_-40dB"] = {"lag0": sim_t(0, big_t), "other_lags_median": float(np.median([sim_t(l, big_t) for l in lags]))}
    W_OLD = (148.78, 149.285)
    eb, ob, ib = (band(x, 300, 5000) for x in (e, o, ins))

    # ---- clicks: the difference signal must be smooth and start/stop at 0; HF (> 6 kHz) transients in the edited window
    d = (e16.astype(np.float64) - o16.astype(np.float64)) / 32768
    res["edges"] = {"max_abs_diff_first_2ms": float(np.abs(d[i0:i0 + 96]).max()), "max_abs_diff_last_2ms": float(np.abs(d[j1 - 96:j1]).max()),
                    "diff_at_span_edges_is_zero": bool(d[i0 - 1].any() == 0 and d[j1].any() == 0)}
    hp = lambda x: sosfiltfilt(butter(4, 6000, "highpass", fs=SR, output="sos"), x)  # noqa
    he, ho = hp(e), hp(o)
    win = slice(int(148.5 * SR), int(149.62 * SR))
    fr2 = lambda x: 20 * np.log10(np.sqrt((x[win][: (len(x[win]) // 96) * 96].reshape(-1, 96) ** 2).mean(1)) + 1e-12)  # noqa  2 ms
    ce, co = fr2(he), fr2(ho)
    # a click = a 2 ms HF frame > 12 dB over the median of its 20 ms neighbourhood, in the edited file but not at the same place in the original
    from scipy.ndimage import median_filter
    pk_e = ce - median_filter(ce, 11)
    pk_o = co - median_filter(co, 11)
    res["clicks"] = {"hf_2ms_frames_over_12db_edited": int(np.sum(pk_e > 12)), "same_in_original": int(np.sum(pk_o > 12)),
                     "max_hf_jump_db_edited": float(pk_e.max()), "max_hf_jump_db_original": float(pk_o.max())}

    # ---- spectrograms
    fig, ax = plt.subplots(4, 1, figsize=(14, 13), sharex=True)
    for k, (x, ttl) in enumerate([(o, "BEFORE: original song"), (e, "AFTER: edited song (Yes +1 beat = +0.432 s)"),
                                  (e - o, "AFTER minus BEFORE (what the edit changed)"),
                                  (e - ins[:len(e)], "AFTER minus instrumental stem (= the vocal in the edited song)")]):
        seg = S(146.5, 151.0, x)
        f, t, Z = stft(seg, SR, nperseg=2048, noverlap=2048 - 240)
        im = ax[k].pcolormesh(t + 146.5, f, 20 * np.log10(np.abs(Z) + 1e-9), vmin=-130, vmax=-40, shading="auto", cmap="magma")
        ax[k].set_ylim(0, 8000)
        ax[k].set_title(ttl)
        ax[k].set_ylabel("Hz")
        for tt, lab in [(148.72, "old Yes"), (149.152, "new Yes"), (148.865, "beat"), (149.297, "beat"), (149.72, "bridge crash"),
                        (149.285, "old silence"), (149.525, "")]:
            ax[k].axvline(tt, color="cyan" if "Yes" in lab else "white", lw=0.8, ls="--" if lab in ("beat", "") else "-")
            if k == 0 and lab:
                ax[k].text(tt, 7600, lab, color="w", fontsize=8, rotation=90, va="top")
    ax[-1].set_xlabel("song time (s)")
    fig.colorbar(im, ax=ax, label="dBFS")
    fig.savefig(os.path.join(REV, "spectrogram_before_after.png"), dpi=110)
    plt.close(fig)
    # zoom: the vacated place, original vs edited vs neighbours (vocal band envelope)
    fig, ax = plt.subplots(2, 1, figsize=(14, 7))
    tt = np.arange(len(S(147.8, 150.2, o))) / SR + 147.8
    for x, lab in [(ob, "original, 300-5000 Hz"), (eb, "edited, 300-5000 Hz"), (ib, "instrumental stem, 300-5000 Hz")]:
        y = S(147.8, 150.2, x)
        m = len(y) // 480 * 480
        ax[0].plot(tt[:m:480] + 0.005, 20 * np.log10(np.sqrt((y[:m].reshape(-1, 480) ** 2).mean(1)) + 1e-12), label=lab)
    ax[0].axvspan(*W_OLD, color="r", alpha=0.08, label="old word")
    ax[0].axvspan(W_OLD[0] + D / SR, W_OLD[1] + D / SR, color="g", alpha=0.08, label="new word")
    ax[0].set_ylabel("dBFS (10 ms RMS)")
    ax[0].legend(fontsize=8)
    ax[0].set_ylim(-110, -15)
    ax[0].set_title("Vocal band envelope: the old place (red) drops to the backing; the word reappears one beat later (green)")
    for x, lab in [(e, "edited"), (o, "original")]:
        ax[1].plot(tt[:len(S(147.8, 150.2, x))], S(147.8, 150.2, x), lw=0.4, label=lab, alpha=0.8)
    ax[1].legend(fontsize=8)
    ax[1].set_xlabel("song time (s)")
    fig.savefig(os.path.join(REV, "envelope_vocal_band.png"), dpi=110)
    plt.close(fig)
    json.dump(res, open(P("work", "sound_v4", "verify.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

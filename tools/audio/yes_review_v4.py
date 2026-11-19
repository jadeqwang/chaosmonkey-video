#!/usr/bin/env python3
"""Review material for the director: 10 s excerpts around the G5 "Yes" (before = mix_v2 / original song, after = mix_v3 / edited
song), mix spectrograms and short-term loudness, local numbers. -> work/review/sound_v4/, work/sound_v4/review.json"""
import json
import os
import sys

import matplotlib
import numpy as np
import soundfile as sf
from scipy.signal import stft

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx"))
from dsp import Momentary, kpow  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)  # noqa
SR = 48000
REV = P("work", "review", "sound_v4")
A, B = 144.2, 154.2
F = {"before_mix_v2": P("media", "sound", "mix_v2.wav"), "after_mix_v3": P("media", "sound", "mix_v3.wav"),
     "before_song": P("inputs", "Chaos Monkey - reformatted for duet.wav"),
     "after_song": P("inputs", "Chaos Monkey - reformatted for duet - v4 yes late.wav")}
Y = {}
for k, p in F.items():
    y, sr = sf.read(p, always_2d=True, dtype="float64")
    Y[k] = y.T
    seg = y[int(A * SR):int(B * SR)].copy()
    r = int(0.01 * SR)
    seg[:r] *= np.linspace(0, 1, r)[:, None]
    seg[-r:] *= np.linspace(1, 0, r)[:, None]
    sf.write(os.path.join(REV, f"yes_{k}_144.2-154.2.wav"), seg, SR, subtype="PCM_24")
# A/B in one file: before, 1 s silence, after
ab = np.concatenate([Y["before_mix_v2"][:, int(A * SR):int(B * SR)], np.zeros((2, SR)), Y["after_mix_v3"][:, int(A * SR):int(B * SR)]], 1)
sf.write(os.path.join(REV, "yes_AB_mix_v2_then_mix_v3.wav"), ab.T, SR, subtype="PCM_24")
# short-term (400 ms momentary) loudness, both mixes
ts = np.arange(146.0, 151.0, 0.01)
L = {k: Momentary(kpow(Y[k]))(ts, win=0.4) for k in ("before_mix_v2", "after_mix_v3")}
L50 = {k: Momentary(kpow(Y[k]))(ts, win=0.05) for k in ("before_mix_v2", "after_mix_v3")}
fig, ax = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
for i, k in enumerate(("before_mix_v2", "after_mix_v3")):
    seg = Y[k].mean(0)[int(146.5 * SR):int(151.0 * SR)]
    f, t, Z = stft(seg, SR, nperseg=2048, noverlap=2048 - 240)
    ax[i].pcolormesh(t + 146.5, f, 20 * np.log10(np.abs(Z) + 1e-9), vmin=-130, vmax=-40, shading="auto", cmap="magma")
    ax[i].set_ylim(0, 10000)
    ax[i].set_title({"before_mix_v2": "BEFORE: mix_v2 (approved)", "after_mix_v3": "AFTER: mix_v3 ('Yes' one beat later)"}[k])
    ax[i].set_ylabel("Hz")
for k, c in (("before_mix_v2", "C0"), ("after_mix_v3", "C3")):
    ax[2].plot(ts, L50[k], c, lw=0.7, alpha=0.6, label=f"{k} 50 ms")
    ax[2].plot(ts, L[k], c, lw=1.6, label=f"{k} 400 ms")
for a in ax:
    for tt, c in ((148.72, "cyan"), (149.152, "lime"), (148.865, "w"), (149.297, "w"), (149.72, "yellow")):
        a.axvline(tt, color=c if a is not ax[2] else ("k" if c in ("w", "yellow") else c), lw=0.8, ls="--" if c == "w" else "-")
ax[2].set_ylim(-80, -5)
ax[2].set_ylabel("LUFS (momentary)")
ax[2].legend(fontsize=8, ncol=2)
ax[2].set_xlabel("song time (s); cyan = old 'Yes' 148.72, green = new 149.152, dashed = beats 148.865 / 149.297, yellow = crash 149.72")
fig.tight_layout()
fig.savefig(os.path.join(REV, "spectrogram_mix_v2_vs_mix_v3.png"), dpi=110)
plt.close(fig)
# numbers: the pause and the word in each mix (50 ms momentary)
def stat(k, a, b):
    m = (ts >= a) & (ts < b)
    return {"max": round(float(L50[k][m].max()), 1), "median": round(float(np.median(L50[k][m])), 1)}
rev = {"excerpts_s": [A, B],
       "pause_between_less_and_yes": {"mix_v2 148.60-148.70": stat("before_mix_v2", 148.60, 148.70),
                                      "mix_v3 148.60-149.15": stat("after_mix_v3", 148.60, 149.15)},
       "old_hole": {"mix_v2 149.30-149.52": stat("before_mix_v2", 149.30, 149.52), "mix_v3 149.30-149.52 (now the word)": stat("after_mix_v3", 149.30, 149.52)},
       "word": {"mix_v2 148.78-149.28": stat("before_mix_v2", 148.78, 149.28), "mix_v3 149.21-149.71": stat("after_mix_v3", 149.21, 149.71)},
       "bridge_entry_149.72-150.5": {"mix_v2": stat("before_mix_v2", 149.72, 150.5), "mix_v3": stat("after_mix_v3", 149.72, 150.5)}}
json.dump(rev, open(P("work", "sound_v4", "review.json"), "w"), indent=1)
print(json.dumps(rev, indent=1))

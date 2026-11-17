#!/usr/bin/env python3
"""Measure generated takes (no ears): level, onsets, centroid, flatness, pitch-peaks; contact sheet of spectrograms.
    $PY tools/audio/sfx/inspect_sources.py  -> work/sound/inspect.png + printout"""
import glob, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import stft, find_peaks
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsp import load, SR, ROOT

files = sorted(glob.glob(os.path.join(ROOT, "media/sound/sfx/gen/*.mp3")))
fig, axs = plt.subplots(len(files), 1, figsize=(16, 2.0 * len(files)))
for ax, f in zip(axs, files):
    y = load(f).mean(0)
    n = os.path.basename(f)[:-4]
    hop = 480
    fr = np.array([np.sqrt(np.mean(y[i:i + 960] ** 2)) for i in range(0, len(y) - 960, hop)])
    db = 20 * np.log10(fr + 1e-9)
    on, _ = find_peaks(np.diff(db, prepend=db[0]), height=6, distance=10)
    fq, tq, Z = stft(y, SR, nperseg=2048, noverlap=1536)
    P = np.abs(Z) ** 2
    cen = (fq[:, None] * P).sum(0) / (P.sum(0) + 1e-20)
    flat = np.exp(np.mean(np.log(P + 1e-20), 0)) / (np.mean(P, 0) + 1e-20)
    act = db > db.max() - 30
    S = np.abs(np.fft.rfft(y * np.hanning(len(y)))); ff = np.fft.rfftfreq(len(y), 1 / SR)
    m = (ff > 40) & (ff < 4000); pk = ff[m][np.argsort(S[m])[::-1][:6]]
    print(f"{n:18s} dur {len(y)/SR:5.2f}s peak {20*np.log10(abs(y).max()+1e-9):6.1f} rms {20*np.log10(np.sqrt(np.mean(y**2))+1e-9):6.1f} "
          f"active {act.mean()*100:4.0f}% centroid med {np.median(cen):5.0f} Hz flat {np.median(flat):.3f} "
          f"onsets {[round(i*hop/SR,2) for i in on][:14]} peaks {np.round(pk).astype(int).tolist()}")
    ax.pcolormesh(tq, fq, 10 * np.log10(P + 1e-12), shading="auto", cmap="magma", vmin=-110, vmax=-30)
    ax.set_yscale("symlog", linthresh=500); ax.set_ylim(40, 20000)
    ax2 = ax.twinx(); ax2.plot(np.arange(len(db)) * hop / SR, db, "c", lw=0.7); ax2.set_ylim(-90, 0)
    ax.set_title(n, fontsize=9, loc="left")
plt.tight_layout(); plt.savefig(os.path.join(ROOT, "work/sound/inspect.png"), dpi=60)

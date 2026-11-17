#!/usr/bin/env python3
"""Ink coverage for paper plates.  coverage.py IMG [IMG ...] [--thr=28]
paper colour = per-channel median of the brightest 40% (luma) pixels, after a 5px blur.
coverage = share of pixels whose max channel distance from paper > thr.
Also: mark centroid (x,y in 0..1), bbox of marks (5-95 pct), paper evenness (max-min of paper luma across a 3x3 grid)."""
import sys, numpy as np
from PIL import Image, ImageFilter
thr = 28
for a in sys.argv[1:]:
    if a.startswith('--thr='): thr = int(a[6:])
def measure(path):
    im = Image.open(path).convert('RGB')
    im.thumbnail((1024, 1024))
    im = im.filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(im).astype(np.float32)
    L = a @ np.array([.299, .587, .114])
    cut = np.percentile(L, 60)
    paper = np.median(a[L >= cut], axis=0)
    d = np.abs(a - paper).max(axis=2)
    m = d > thr
    cov = m.mean() * 100
    H, W = m.shape
    ys, xs = np.nonzero(m)
    if len(xs):
        cx, cy = xs.mean() / W, ys.mean() / H
        bb = (np.percentile(xs, 5) / W, np.percentile(ys, 5) / H, np.percentile(xs, 95) / W, np.percentile(ys, 95) / H)
    else:
        cx = cy = float('nan'); bb = (0, 0, 0, 0)
    ev = []
    for i in range(3):
        for j in range(3):
            blk = L[i*H//3:(i+1)*H//3, j*W//3:(j+1)*W//3]; mk = ~m[i*H//3:(i+1)*H//3, j*W//3:(j+1)*W//3]
            if mk.sum() > 500: ev.append(blk[mk].mean())
    even = (max(ev) - min(ev)) if ev else float('nan')
    return cov, cx, cy, bb, even, paper
for p in [x for x in sys.argv[1:] if not x.startswith('--')]:
    cov, cx, cy, bb, even, paper = measure(p)
    print(f"{p}\tcov={cov:5.1f}%\tcentroid=({cx:.2f},{cy:.2f})\tbbox=({bb[0]:.2f},{bb[1]:.2f})-({bb[2]:.2f},{bb[3]:.2f})\tpaper_even={even:4.1f}\tpaper=#{int(paper[0]):02x}{int(paper[1]):02x}{int(paper[2]):02x}")

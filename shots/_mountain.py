"""shots/_mountain.py: shared helpers for team MOUNTAIN's shots (the storybook's painting of 花果山).

Everything inside the book shares ONE paper: BOOK_PAPER_SEED, Paper 'new' (1988).
"""
import math

import cv2
import numpy as np

from tools.ink import *                                    # noqa: F401,F403
from tools.ink.core import F32, ROOT

BOOK_PAPER_SEED = 1988
SEAL_FONT = 'refs/fonts/chongxi-seal/崇羲篆体.otf'
KAI_FONT = 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'
PRINT_FONT = 'refs/fonts/huiwen-mincho/匯文明朝體.otf'
LATIN_FONT = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
B = 'design/plates/B_huaguoshan/'


def qianziwen(lines=160):
    """千字文 lines 1-160 (the safe range for 崇羲篆體), traditional, from the proofed text."""
    rows = [r.strip() for r in open(ROOT / 'design/text/qianziwen.txt', encoding='utf-8').read().split('\n')]
    rows = [r for r in rows if r and not r.startswith('#')]
    return ''.join(rows[:lines])


def onto_paper(raw, paper, pct=97.0, ground=None):
    """A full-bleed painted plate re-laid on OUR paper: divide out the plate's own ground (its palest common tone)
    and multiply onto the sheet, so the plate's ink sits on the film's one paper with its fibres."""
    g = np.asarray(ground, F32) if ground is not None else np.percentile(raw.reshape(-1, 3), pct, axis=0).astype(F32)
    T = np.clip(raw / np.maximum(g, 1e-3), 0, 1.0)
    return np.clip(paper.rgb * T, 0, 1).astype(F32)


def view(src, cx, cy, zoom, W, H, fill=None, render=None):
    """Camera crop of a big canvas: (cx, cy) canvas point at frame centre; zoom = frame px per canvas px at 1920
    wide (resolution independent). `src` an HxWxC array, or None with `render(box)` -> the canvas window as an array
    (render only what is seen). Sub-pixel exact (no judder on slow travel)."""
    z = zoom * W / 1920.0
    bw, bh = W / z, H / z
    x0, y0 = cx - bw / 2.0, cy - bh / 2.0
    ix0, iy0 = int(math.floor(x0)) - 2, int(math.floor(y0)) - 2
    ix1, iy1 = int(math.ceil(x0 + bw)) + 3, int(math.ceil(y0 + bh)) + 3
    if render is not None:
        win = render((ix0, iy0, ix1, iy1))
    else:
        h, w = src.shape[:2]
        pad = [(max(0, -iy0), max(0, iy1 - h)), (max(0, -ix0), max(0, ix1 - w))] + [(0, 0)] * (src.ndim - 2)
        win = src[max(0, iy0):min(h, iy1), max(0, ix0):min(w, ix1)]
        if any(p != (0, 0) for p in pad):
            win = np.pad(win, pad, mode='edge')
    M = np.array([[z, 0, (ix0 - x0) * z], [0, z, (iy0 - y0) * z]], np.float64)
    if z < 0.8:                                             # shrinking: pre-filter so fine brush lines do not alias
        k = 1.0 / z
        win = cv2.resize(win, (max(1, int(round(win.shape[1] / k))), max(1, int(round(win.shape[0] / k)))),
                         interpolation=cv2.INTER_AREA)
        sx = win.shape[1] / ((ix1 - ix0) * 1.0)
        M = np.array([[z / sx, 0, (ix0 - x0) * z], [0, z / sx, (iy0 - y0) * z]], np.float64)
    out = cv2.warpAffine(np.ascontiguousarray(win, dtype=F32), M, (W, H),
                         flags=cv2.INTER_CUBIC if z >= 0.8 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return np.clip(out, 0, 1).astype(F32)


def element(path, height_px, lo=0.05, hi=0.16, gain=1.0, flip=False):
    """A cut-out element painted on its own paper -> ink layer (transmittance) scaled to `height_px` tall."""
    T = key_paper(load_image(ROOT / path), lo=lo, hi=hi, gain=gain)
    if flip:
        T = T[:, ::-1]
    d = 1 - T.min(axis=2)
    ys, xs = np.where(d > 0.04)
    if len(ys):
        p = 6
        T = T[max(0, ys.min() - p):ys.max() + p, max(0, xs.min() - p):xs.max() + p]
    s = height_px / T.shape[0]
    T = cv2.resize(T, (max(1, int(round(T.shape[1] * s))), max(1, int(round(height_px)))), interpolation=cv2.INTER_AREA)
    return np.clip(T, 0, 1).astype(F32)


def lay_at(frame, T, x, y, opacity=1.0):
    """lay_ink with sub-pixel placement of a small layer (x, y = top-left in frame px, floats)."""
    ix, iy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - ix, y - iy
    if abs(fx) > 1e-3 or abs(fy) > 1e-3:
        M = np.array([[1, 0, fx], [0, 1, fy]], np.float64)
        T = cv2.warpAffine(T, M, (T.shape[1] + 1, T.shape[0] + 1), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=(1.0, 1.0, 1.0))
    lay_ink(frame, T, ix, iy, opacity)
    return frame


def band(x, front, lead, trail, flare=1.0):
    """A travelling band of light along x: rises over `lead` px ahead of `front`, flares at it, dies over `trail` px
    behind it (`front` moves right to left, so 'behind' is +x)."""
    d = x - front
    up = np.exp(-np.maximum(-d, 0) ** 2 / (2 * (lead * 0.5) ** 2))
    down = np.exp(-np.maximum(d, 0) / max(trail, 1e-3))
    return (np.where(d < 0, up, down) * flare).astype(F32)

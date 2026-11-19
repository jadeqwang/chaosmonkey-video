"""C5b 'the wind blew once, and that was all' (54.625-57.042 s; 58 frames). BOOK v4, candidate A.

The egg from C4 (same framing and paper), the static inscription (as v3), and the wind: a real 2D flow
(stable-fluids solve, shots/_book4_wind.py) enters from the LEFT edge already moving, travels left -> right rising
slightly, is forced round the egg (a solid obstacle: it sheds and rolls vortices in its wake) and rolls on out right.
Brush ribbons are material lines advected by that flow (they stretch, fold and wind into spirals); each is drawn as a
thick-thin dry-brush stroke whose ink only appears where the air has reached it. A pale mist (bare-paper whitening)
is advected by the same field. Everything is vector/low-res data precomputed in setup(): 1080p is a re-render.
FLOW CONTRACT: see work/book4/C5b/NOTES.md.
"""
import os

import cv2
import numpy as np

from shots._mountain import *
from shots.C4 import egg_layer, egg_inner
from shots import _book4_wind as WD
from tools.ink.inscription import inscription

T0, T1 = 1311 / 24, 1369 / 24
FADE0, FADE1 = 1.75, 2.36          # seconds after T0: the lines dry out and lift off the paper


def setup(ctx):
    global P, EGG, INN, INS, SIM, TEX, SOLIDW
    W, H = ctx.W, ctx.H
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(W, H)
    INN = egg_inner(EGG, ctx.s)
    INS = inscription(ctx, 'C5', box=(1560, 120, 240, 700), paper=P)
    SIM = WD.simulate()
    rg = np.random.default_rng(31)
    t1 = cv2.resize(rg.random((H // 24 + 2, W // 24 + 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    t2 = cv2.resize(rg.random((H // 7 + 2, W // 7 + 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    TEX = np.clip(0.55 * t1 + 0.45 * t2, 0, 1)
    SOLIDW = cv2.resize(SIM['solid'].astype(np.float32), (W, H)) if False else None


def _noise1(x, seed):
    """cheap smooth 1-D value noise in [0,1] (x array)."""
    i = np.floor(x).astype(np.int64)
    f = x - i
    f = f * f * (3 - 2 * f)
    def h(k):
        k = (k * 374761393 + seed * 668265263) & 0x7fffffff
        k = (k ^ (k >> 13)) * 1274126177 & 0x7fffffff
        return (k % 10007) / 10007.0
    return h(i) * (1 - f) + h(i + 1) * f


def _mist(f, k, ctx):
    W, H = ctx.W, ctx.H
    d = SIM['frames'][k]['dye'].astype(np.float32)
    DS = 2
    x0 = int((0 - WD.X0) / (WD.H / DS)); x1 = int((WD.ASP - WD.X0) / (WD.H / DS))
    d = d[:, x0:x1]
    d = cv2.GaussianBlur(d, (0, 0), 1.2)
    # the mist lies over the egg too: carry it across the solid by dilation, soft
    sol = cv2.resize(SIM['solid'][:, int((0 - WD.X0) / WD.H):int((WD.ASP - WD.X0) / WD.H)].astype(np.uint8), (d.shape[1], d.shape[0]),
                     interpolation=cv2.INTER_NEAREST) > 0
    ext = cv2.GaussianBlur(cv2.dilate(d, np.ones((41, 41), np.uint8)), (0, 0), 7) * 0.85
    d = np.where(sol, np.maximum(d, ext), d)
    d = cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC)
    a = np.clip(d * 2.4, 0, 1)
    a = a * (0.62 + 0.55 * TEX)
    fade = 1 - smoothstep(1.2, 2.2, k / 24.0)
    return np.clip(a, 0, 1) * 0.9 * fade


def _brush(T, st, meta, k, ctx):
    W, H = ctx.W, ctx.H
    p = st['p'].astype(np.float64)
    n = len(p)
    if n < 4:
        return
    act = st['act'].astype(np.float64)
    if act.max() < 0.03:
        return
    m = st['m'].astype(np.float64)
    u = m / max(meta['Lm'], 1e-6)
    stretch = st['stretch'].astype(np.float64)
    # smooth the polyline slightly (kills sim jitter, keeps spirals)
    kx = np.convolve(np.pad(p[:, 0], 2, mode='edge'), np.ones(5) / 5, 'valid')
    ky = np.convolve(np.pad(p[:, 1], 2, mode='edge'), np.ones(5) / 5, 'valid')
    p = np.stack([kx, ky], 1)
    px = p * H
    d = np.gradient(px, axis=0)
    ln = np.hypot(d[:, 0], d[:, 1]) + 1e-6
    nrm = np.stack([-d[:, 1], d[:, 0]], 1) / ln[:, None]
    # pressure: pointed tail (u=0), swells, long taper to the head; thinner where the line is stretched fast
    press = smoothstep(0.0, 0.28, u) ** 0.8 * (1 - 0.92 * smoothstep(0.70, 1.0, u) ** 1.6)
    press = 0.10 + 0.90 * press
    thin = np.clip(1.0 / (1 + 0.07 * (stretch - 1)), 0.55, 1.0)
    wd = meta['wmax'] * H * 1.25 * press * thin
    dry = np.clip((stretch - 1.6) / 7.0, 0, 1)
    fade = 1 - smoothstep(FADE0, FADE1, k / 24.0 + 0.0 * u)
    # ink tone: pale to mid; a little darker at the swell, lighter where dry
    tone = meta["tone"] * 0.72 * (0.70 + 0.30 * press) * (1 - 0.45 * dry)
    # the inscription is a soft obstacle: lines thin out and fade before they reach its box (+ margin)
    s_ = ctx.s
    bx0, bx1, by0, by1 = 1500 * s_, 1860 * s_, 70 * s_, 880 * s_
    dxm = np.maximum(bx0 - px[:, 0], px[:, 0] - bx1)
    dym = np.maximum(by0 - px[:, 1], px[:, 1] - by1)
    dist = np.maximum(dxm, dym)
    inbox = smoothstep(-20 * s_, 70 * s_, dist)
    base = act * fade * tone * inbox
    seglen = np.hypot(*np.diff(px, axis=0).T)
    if (seglen * (base[:-1] > 0.06)).sum() < 0.20 * H:     # no short dashes: only lines that read as lines
        return
    vis = base > 0.02
    if vis.sum() < 3:
        return
    # canvas bounding box
    idx = np.where(vis)[0]
    mrg = int(wd.max() * 2 + 6)
    xa = int(np.clip(px[idx, 0].min() - mrg, 0, W)); xb = int(np.clip(px[idx, 0].max() + mrg, 0, W))
    ya = int(np.clip(px[idx, 1].min() - mrg, 0, H)); yb = int(np.clip(px[idx, 1].max() + mrg, 0, H))
    if xb - xa < 2 or yb - ya < 2:
        return
    cv = np.zeros((yb - ya, xb - xa), np.uint8)
    off = np.array([xa, ya], np.float64)
    NB = 7
    seed = meta['seed']
    cents = np.linspace(-0.85, 0.85, NB)
    for j, c in enumerate(cents):
        cvj = np.zeros_like(cv)
        nz = _noise1(m * 48.0 + j * 7.3, seed + j)          # bristle runs: dry-brush gaps along the stroke
        thr = 0.18 + 0.55 * dry + 0.10 * np.abs(c)
        keep = smoothstep(thr - 0.05, thr + 0.12, nz)
        al = base * keep * (0.85 + 0.15 * np.cos(c * 2))
        al = np.convolve(np.pad(al, 3, mode='edge'), np.ones(7) / 7, 'valid')
        hb = np.maximum(wd * 0.5 * 0.30, 0.5)
        cen = px + nrm * (c * wd * 0.5)[:, None] - off
        L = cen + nrm * hb[:, None]; R = cen - nrm * hb[:, None]
        for i in range(n - 1):
            a8 = 0.5 * (al[i] + al[i + 1])
            if a8 < 0.02 or not (vis[i] and vis[i + 1]):
                continue
            q = np.array([L[i], L[i + 1], R[i + 1], R[i]])
            cv2.fillConvexPoly(cvj, np.round(q * 16).astype(np.int32), int(min(a8, 1.0) * 255), cv2.LINE_AA, 4)
        cv = np.maximum(cv, cvj)
    dens = cv.astype(np.float32) / 255.0 * 0.95
    T[ya:yb, xa:xb] *= ink_T(dens)


def render(t, ctx):
    W, H = ctx.W, ctx.H
    k = int(np.clip(round((t - T0) * 24), 0, len(SIM['frames']) - 1))
    f = P.frame(t)
    f *= EGG
    INN.lay(f)
    if os.environ.get('C5B_PLATE'):                      # clean plate (egg, paper, inscription) for the video candidates
        INS.draw(f)
        return f
    a = _mist(f, k, ctx)
    f += (np.clip(P.rgb * 0.55 + 0.45 * 1.0, 0, 1) - f) * a[..., None]
    T = np.ones_like(f)
    st = SIM['frames'][k]['ribbons']
    for r, meta in zip(st, SIM['meta']):
        if r is not None:
            _brush(T, r, meta, k, ctx)
    f *= T
    INS.draw(f)
    return f

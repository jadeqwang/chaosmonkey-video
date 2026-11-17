"""H5 "I'm made of the telling, not just the tale" (169.250-172.750, 84 frames). Team MOUNTAIN.

The carved cliff again (B_cliff_run and the same carving as B4, held at mid scale: zoom 0.85). The camera holds;
one thing moves, the light: a warm raking band crosses right to left and every character it reaches brightens and
stays lit, except inside a child-shaped shadow in the lower left (a small girl standing, seen from behind:
little Jade's back view from the turnaround, simplified so it could be either child): a blank in lit writing.
A loose gold brush ring floats behind her head, not touching it (no group-G plate yet: drawn with `stroke`).
"""
import numpy as np

from shots._mountain import *
from shots import B4 as _b4

T0, T1 = 4062 / 24, 4146 / 24
CX, CY, Z = 7320, 640, 0.85


def setup(ctx):
    global C, XS, SH, RING, PAPER_RING
    _b4.setup(ctx)
    C, XS = _b4.C, _b4.XS
    H, W = C.H, C.W
    # the child's shadow, in canvas space: feet near the bottom of the frame, lower left
    m = load_mask(ROOT / 'work/mountain/child_back_mask.png')
    hpx = 820                                                  # canvas px tall (about 545 px in frame)
    m = cv2.resize(m, (int(m.shape[1] * hpx / m.shape[0]), hpx), interpolation=cv2.INTER_AREA)
    fx0 = CX - 960 / Z                                         # canvas x of the frame's left edge
    x0, y0 = 6250, int(CY + 540 / Z - hpx + 40)              # over the lower half of the block 成歲律召
    SH = np.zeros((H, W), np.float32)
    h_, w_ = min(hpx, H - y0), m.shape[1]
    SH[y0:y0 + h_, x0:x0 + w_] = m[:h_]
    SH = blur(SH, 2.5)                                         # fix2: a crisper cast shadow (child-shaped blank)
    # the ring: one loose dry stroke of gold around where her head is, in frame space
    s = ctx.s
    hx = ((x0 + w_ / 2) - CX) * Z + 960
    hy = ((y0 + hpx * 0.11) - CY) * Z + 540
    R = 150
    r = rng(5, 'ring')
    pts = []
    for k in range(15):
        a = -0.4 * np.pi + k / 14 * 1.82 * np.pi
        rr = R * (1 + 0.05 * np.sin(3 * a) + r.normal(0, 0.012))
        pts.append(((hx + rr * np.cos(a)) * s, (hy - 8 + rr * 0.86 * np.sin(a)) * s, 0.55 + 0.4 * np.sin(k / 14 * np.pi)))
    PAPER_RING = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED)
    RING = stroke(pts, width=9 * s, seed=12, paper=PAPER_RING, density=0.9, dry=0.45, dry_end=0.9, tint=GOLD)


def _win2(A, box):
    x0, y0, x1, y1 = box
    h, w = A.shape
    out = np.zeros((y1 - y0, x1 - x0), np.float32)
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    if a1 > a0 and b1 > b0:
        out[b0 - y0:b1 - y0, a0 - x0:a1 - x0] = A[b0:b1, a0:a1]
    return out


def render(t, ctx):
    u = 1.25 - 1.6 * ramp(t, T0 + 0.1, T1 - 0.6, 'linear')
    front = CX + (u - 0.5) * 1920 / Z
    bnd = band(XS, front, lead=480, trail=4000, flare=1.0)                # once reached, the writing stays lit
    lit = bnd * (1 - SH) ** 2                                                 # (H, W) map: the shadow keeps the light off
    amb = 0.95 - 0.42 * lit - 0.26 * SH * bnd                             # the shadow itself is a little darker
    flat = 0.95 + 0.04 * lit - 0.17 * SH * bnd                         # her shadow: a real cast shadow
    pool = np.clip((flat - amb) / np.maximum(1 - amb, 1e-3), 0, None)
    f = view(None, CX, CY, Z, ctx.W, ctx.H,
             render=lambda box: C.render((335, 12, 1.0), fill=0.65, ambient=amb, pool=pool, warmth=0.85, box=box))
    # fix2: inside her shadow the writing is NOT lit: the cinnabar in the cuts goes dull, no red reads there
    sh = view(None, CX, CY, Z, ctx.W, ctx.H, render=lambda box: _win2(SH * bnd, box))
    if sh.max() > 0.01:
        a = np.clip(sh * 1.15, 0, 1)[..., None]
        lum = luma(f)[..., None]
        dull = lum * np.array([0.93, 0.88, 0.80], np.float32) * 0.92       # unlit stone, warm, no cinnabar
        f = f * (1 - a) + dull * a
    # the ring is there from the moment the light passes her
    p = ramp(t, 170.6, 171.6, 'sine')
    if p > 0:
        RING.lay(f, p)
    return f

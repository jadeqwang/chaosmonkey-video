"""C1 'a thousand years of soaking up light / It split apart' (41.000-45.167, 100 frames). Team MOUNTAIN.

The stone close (B_stone), held still. On 'It split apart' (43.635) the hairline crack (B_stone_crack, registered,
revealed through its mask) runs down from the top to the base in ~0.5 s. On the three measured stutter chops
(chop_clusters 43.805, 44.040, 44.385) the frame flips to its rubbing (white on black) for the length of the hole
plus a frame, and back.
"""
import numpy as np

from shots._mountain import *

T0, T1 = 41.0, 1084 / 24
T_SPLIT, DUR = 43.635, 0.5


def setup(ctx):
    global STONE, CRACK, YMAP, Y0, Y1, PAPER, RB, CHOPS
    W, H = ctx.W, ctx.H
    PAPER = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    T1_ = key_paper(load_image(B + 'B_stone.png', size=(W, H)), lo=0.03)
    T2_ = key_paper(load_image(B + 'B_stone_crack.png', size=(W, H)), lo=0.03)
    m = load_mask(B + 'B_stone_crack_mask.png', size=(W, H))
    m = np.clip(blur(m, 1.2 * ctx.s) * 1.6, 0, 1)
    STONE = PAPER.rgb * T1_
    CRACK = PAPER.rgb * T2_
    ys = np.where(m.max(axis=1) > 0.2)[0]
    Y0, Y1 = float(ys.min()), float(ys.max())
    YMAP = (np.arange(H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32), m)
    RB = Rubbing(W, H, seed=4)
    ev = ctx.timing.spans
    CHOPS = [(43.805, 43.82), (44.04, 44.06), (44.385, 44.405)]
    for c in (ev.get('chop_clusters') or []):
        if abs(c['start'] - 43.805) < 0.05:
            CHOPS = [(x, x + 0.02) for x in c['times']]


def render(t, ctx):
    f = STONE.copy()
    if t >= T_SPLIT:
        yy, m = YMAP
        u = ramp(t, T_SPLIT, T_SPLIT + DUR, 'in')
        front = Y0 + (Y1 - Y0 + 30) * u
        a = m * smoothstep(front + 6, front - 6, yy)
        f += (CRACK - f) * a[..., None]
    for a_, b_ in CHOPS:
        if a_ <= t < max(b_, a_) + 2 / 24:
            f = RB.apply(f, PAPER.rgb)
            break
    return f

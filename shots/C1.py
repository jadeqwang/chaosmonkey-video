"""C1 'a thousand years of soaking up light / It split apart' (41.000-45.167, 100 frames). BOOK team, v3.

The stone close (B_stone), held still, exactly as B5 leaves it: faint columns of 千字文 lie inside it like inclusions
(§3.1) and two last points of light read down a column. On 'It split apart' (43.635) the hairline crack (B_stone_crack,
registered, revealed through its mask) runs from the top to the base in ~0.5 s. MEDIUM SWITCH (replaces the 2-frame
rubbing flickers): on the first and third measured stutter chops (43.805, 44.385) the whole frame is shown as a stone
rubbing 拓片, clean, held 5 frames each, paper edge in frame; the second chop (44.040) is the cut back to ink.
Static inscription 一日迸裂 on the right.
"""
import numpy as np

from shots._mountain import *
from shots._carve import Inner, enclosed_region
from tools.ink.inscription import inscription
from tools.ink.medium import Mediums

T0, T1 = 41.0, 1084 / 24
T_SPLIT, DUR = 43.635, 0.5
SWITCH = [(43.805, 'rubbing'), (44.385, 'rubbing')]
READS = [(41.15, 1.25, 3), (42.2, 1.25, 4)]                     # (start, seconds to run down, column): continues B5


def stone_inner(W, H, s):
    """The stone's interior and its inclusions: shared with B5 (same framing, same columns)."""
    T = key_paper(load_image(B + 'B_stone.png', size=(W, H)), lo=0.03)
    reg = enclosed_region(T, close=int(9 * s) | 1)
    return T, Inner(reg, qianziwen(160), SEAL_FONT, 44 * s, seed=3, density=0.17)


def setup(ctx):
    global STONE, CRACK, YMAP, Y0, Y1, PAPER, MED, INN, INS
    W, H = ctx.W, ctx.H
    PAPER = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    T1_, INN = stone_inner(W, H, ctx.s)
    T2_ = key_paper(load_image(B + 'B_stone_crack.png', size=(W, H)), lo=0.03)
    m = load_mask(B + 'B_stone_crack_mask.png', size=(W, H))
    m = np.clip(blur(m, 1.2 * ctx.s) * 1.6, 0, 1)
    STONE = PAPER.rgb * T1_
    INN.lay(STONE)
    CRACK = PAPER.rgb * T2_
    INN.lay(CRACK)
    ys = np.where(m.max(axis=1) > 0.2)[0]
    Y0, Y1 = float(ys.min()), float(ys.max())
    YMAP = (np.arange(H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32), m)
    MED = Mediums(W, H, seed=4)
    INS = inscription(ctx, 'C1', box=(1620, 130, 200, 700), paper=PAPER)


def render(t, ctx):
    f = STONE.copy()
    for ts, dur, col in READS:
        if ts <= t < ts + dur + 0.4:
            u = (t - ts) / dur
            INN.read(f, col, min(u, 1.0), ctx.s, strength=1.0 if u <= 1 else max(0.0, 1 - (u - 1) * dur / 0.4))
    t_s = on_frame(T_SPLIT)                      # the crack is there on the frame containing 43.635
    if t >= t_s - 1e-9:
        yy, m = YMAP
        u = 0.34 + 0.66 * ramp(t, t_s, t_s + DUR, 'out')
        front = Y0 + (Y1 - Y0 + 30) * u
        a = m * smoothstep(front + 6, front - 6, yy)
        f += (CRACK - f) * a[..., None]
    INS.draw(f)
    return MED.switch(f, t, SWITCH, paper=PAPER.rgb, hold=5)

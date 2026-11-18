"""C4 'A stone egg, round as a ball' (49.625-52.250, 63 frames). BOOK team, v3.

The egg alone on bare paper (B_egg keyed onto the book paper, pale ink, left of centre and low). It is what the stone
held: the same faint columns lie inside it (§3.1), barely there. Still; the paper's grain breathes; one slow point of
light reads down a column. Static inscription 产一石卵 / 似圆球样大 in the upper right corner.
"""
from shots._mountain import *
from shots._carve import Inner, enclosed_region
from tools.ink.inscription import inscription

T0, T1 = 1191 / 24, 1254 / 24


def egg_layer(W, H):
    """B_egg keyed (its own kozo fibres dropped: lo raised) as a frame-sized ink layer."""
    return key_paper(load_image(B + 'B_egg.png', size=(W, H)), lo=0.06, hi=0.16)


def egg_inner(EGG, s):
    """Columns inside the egg (shared by C4, C5b, C6)."""
    reg = enclosed_region(EGG, close=int(9 * s) | 1)
    return Inner(reg, qianziwen(160), SEAL_FONT, 38 * s, seed=5, density=0.13, start=40)


def setup(ctx):
    global P, EGG, INN, INS
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(ctx.W, ctx.H)
    INN = egg_inner(EGG, ctx.s)
    INS = inscription(ctx, 'C4', box=(1560, 120, 240, 700), paper=P)


def render(t, ctx):
    f = P.frame(t)
    f *= EGG
    INN.lay(f)
    u = (t - (T0 + 0.5)) / 1.7
    if 0 <= u < 1.25:
        INN.read(f, 2, min(u, 1.0), ctx.s, strength=1.0 if u <= 1 else max(0.0, 1 - (u - 1) / 0.25))
    INS.draw(f)
    return f

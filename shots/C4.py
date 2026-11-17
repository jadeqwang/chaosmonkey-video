"""C4 'A stone egg, round as a ball' (49.625-52.250, 63 frames). Team MOUNTAIN.

The egg alone on bare paper (B_egg keyed onto the book paper, pale ink, left of centre and low). Still. The only
life is the paper itself: its fine grain breathes a fraction of a percent.
"""
from shots._mountain import *

T0, T1 = 1191 / 24, 1254 / 24


def setup(ctx):
    global P, EGG
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(ctx.W, ctx.H)


def egg_layer(W, H):
    """B_egg keyed (its own kozo fibres dropped: lo raised) as a frame-sized ink layer."""
    return key_paper(load_image(B + 'B_egg.png', size=(W, H)), lo=0.06, hi=0.16)


def render(t, ctx):
    f = P.frame(t)
    f *= EGG
    return f

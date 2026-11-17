"""H6 'one hair that can't gather, blown on the gale' (172.750-177.208, 107 frames). Team MOUNTAIN.

The emptiest frame of the film: the book paper, bare, and one hair-thin line of ink (tools.ink `hairline`, analytic,
sub-pixel) drifting right to left with a slow waver; it has left the page by the left edge just before the cut
(I1 opens on flashlight white). Nothing else.
"""
from shots._mountain import *

T0, T1 = 4146 / 24, 4253 / 24


def setup(ctx):
    global P
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)


def render(t, ctx):
    f = P.frame(t)
    u = t - T0
    T = hairline(ctx.W, ctx.H, u, seed=3, y=0.47, x=0.56, angle=-4.0, drift=(-285.0 * ctx.s, -9.0 * ctx.s),
                 length=0.33, weight=1.3 * ctx.s, density=0.6, waver=6.0 * ctx.s)
    f *= T
    return f

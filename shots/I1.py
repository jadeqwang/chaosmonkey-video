"""I1 (177.208-180.208) "Mischievous baby, Monkey's twin".  BED+CAR v4.
A) 177.2083-179.542: the animate take (ls4w_I1_a4b, 1:1 from song 176.9), first 4 frames fade in from bare paper white (H6 ends on
bare paper), very slow push 1.0->1.02.  B) 179.542-180.2083: over-the-shoulder push into the I2 page, landing on its frame 0."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 177.20833333333334, 180.20833333333334
T_OTS = 179.542
OTS_Q4 = [[274, 461], [1013, 184], [1231, 593], [500, 932]]


def setup(ctx):
    global B, P, O
    B = Take('I1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=27)
    O = OtsPush4(ctx, 'ots_I1', 'I2_page.png', 'work/bedcar4/ends/I2page_f0.png', OTS_Q4, ta=T_OTS - 0.05, tb=T1)


def render(t, ctx):
    if t >= T_OTS - 1e-6:
        return O.render(t, ctx)
    k = frame_of(t) - frame_of(T0)
    f = push(B.at(t), ctx, t, T0, T_OTS, 1.0, 1.02, cx=960, cy=540, kind='linear')
    w = max(0.0, 1 - k / 4.0)
    f = f * (1 - w) + np.array([0.93, 0.90, 0.83], F32) * w
    return fin(f, P)

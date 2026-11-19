"""I4 (187.000-189.792) "Wouldn't you? You're able."  BED+CAR v4.
1. 187.000-189.375  Take('I4') (Jade close, singing; two-pass act + animate, placed 1:1 at 186.5): no morph, no retime. Very slow
   push 1.00 -> 1.03 (linear) about her face (1150, 410 in 1080p px; measured on the take).
2. 189.375-189.792  the J1 view: j1_frame (shots/_j1v4.py), the daughter's fingertip on the page, the press at 189.620."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _j1v4 import *

T0, T1 = 187.0, 189.79166666666666
FACE = (1150, 410)


def setup(ctx):
    global J, PJ
    J = Take('I4', ctx)
    PJ = Paper(ctx.W, ctx.H, 'aged', seed=39)
    setup_j1(ctx)


def render(t, ctx):
    if t >= T_VIEW - 1e-6:
        return j1_frame(t, ctx)
    return fin(push(J.at(t), ctx, t, T0, T_VIEW, 1.0, 1.03, cx=FACE[0], cy=FACE[1], kind='linear'), PJ)

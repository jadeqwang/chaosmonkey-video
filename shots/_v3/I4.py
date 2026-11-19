"""I4 (187.000-189.792) "Wouldn't you? You're able."  BED+CAR v3.  The mother answers (REVISION_V3 section 1).

1. 187.000-187.600  a true MORPH made by the video model (Kling v4 first+last: media/kf/v3/I4_mama.jpg, Mama's 1988 face in
   red neon, same framing -> media/kf/v3/I4_jade.jpg, Jade in flashlight white): one face that flows from the mother who
   said "do what mama says" into the mother who says this. "Wouldn't you?" is sung under it.
2. 187.600-189.375  Jade, animated directly from the keyframe built on her accepted likeness refs: holds her daughter's
   eyes with a small sure smile, leans in (188.2) and says "You're able" (188.67).
3. 189.375-189.792  already the J1 view (shots/_j1v3.py): the daughter's fingertip hovers and presses on 189.620 (sound cue)
   while "able" rings on.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _j1v3 import *

T0, T1 = 187.0, 189.79166666666666
T_JADE = 187.6


def setup(ctx):
    global M, J, PJ
    M = Take('morph', ctx)
    J = Take('I4', ctx)
    PJ = Paper(ctx.W, ctx.H, 'aged', seed=39)
    setup_j1(ctx)


def render(t, ctx):
    if t >= T_VIEW - 1e-6:
        return j1_frame(t, ctx)
    if t < T_JADE - 1e-6:
        return fin(M.at(t), PJ)
    return fin(push(J.at(t), ctx, t, T_JADE, T_VIEW, 1.0, 1.04, cx=960, cy=400, kind='linear'), PJ)

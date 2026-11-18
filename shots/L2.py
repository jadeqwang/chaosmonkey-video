"""L2 (233.208-235.833) the blanket.  BED+CAR v3.  No flashlight insert.

From the foot of the bed: the daughter asleep; Jade kneels at frame left and draws the quilt up over her: the pull runs
235.33-235.78 and it is tucked under her chin on 235.780 (sound cue); the last frame (song frame 5659) holds her hands at the
chin. Match cut on 235.833 to the attic (team ATTIC's L2b: Mama, same framing, hands at the waist starting the same pull).
Kling v4 first+last (media/kf/v3/L2.jpg -> L2_end.jpg). The jacket's back lettering is under her hair in this view.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 233.20833333333334, 235.83333333333334


def setup(ctx):
    global B, P
    B = Take('L2', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=73)


def render(t, ctx):
    return fin(B.at(t), P)

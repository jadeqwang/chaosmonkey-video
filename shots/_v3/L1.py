"""L1 (228.750-233.208) after the last line.  BED+CAR v3.

The daughter asleep in Jade's lap (mouth open, one arm flung over Jade's arm, a foot out), the book closed on the rug, the
flashlight lying beside it still on. Jade looks down at her, glances at the book, breathes out, and lays her cheek on the
curls. No pull-back, no warp: a locked frame with a 3 % push. Kling v4 take of media/kf/v3/L1.jpg.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 228.75, 233.20833333333334


def setup(ctx):
    global B, P
    B = Take('L1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=71)


def render(t, ctx):
    return fin(push(B.at(t), ctx, t, T0, T1, 1.0, 1.03, cx=1100, cy=560, kind='linear'), P)

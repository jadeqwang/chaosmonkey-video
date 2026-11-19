"""F6b (120.083-121.458, 33 frames = song frames 2882-2914).  BED+CAR v4: the rear-view MIRROR shot (the v3 hair-catch is retired).

Take('F6b') = animate take (two-pass rap prompt), 1408x768, placed with frame 0 at song 119.9 and played 1:1 (never retimed);
scaled to the frame by Take. Optional slow push 1.00 -> 1.04 toward the right end of the glass (the daughter) -- centre set below.
Paper finish only, no mouth work, no calligraphy.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 120.08333333333333, 121.45833333333333
PUSH = float(os.environ.get('F6B_PUSH', '1.04'))
CX, CY = [float(v) for v in os.environ.get('F6B_C', '1480,400').split(',')]


def setup(ctx):
    global B, P
    B = Take('F6b', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=65)


def render(t, ctx):
    return fin(push(B.at(t), ctx, t, T0, T1, 1.0, PUSH, cx=CX, cy=CY, kind='linear'), P)

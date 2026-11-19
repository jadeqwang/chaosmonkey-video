"""L1 (228.750-233.208) after the last line.  BED+CAR v4.

Take('L1') = v4bc L1 t4 (daughter asleep in Jade's lap, Jade breathing out and laying her cheek on the curls). Very slow locked
push 1.00 -> 1.03 about the centre of the two of them (measured on the 1080p frame: group bbox x 620-1390, y 70-940 -> (1005, 505)).
No warp, no mouth work; paper finish only. No calligraphy.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 228.75, 233.20833333333334


def setup(ctx):
    global B, P
    B = Take('L1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=71)


def render(t, ctx):
    return fin(push(B.at(t), ctx, t, T0, T1, 1.0, 1.03, cx=1005, cy=505, kind='linear'), P)

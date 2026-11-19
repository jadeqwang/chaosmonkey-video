"""I3a (182.958-184.625; I3b by team BOOK starts at frame 4431).  BED+CAR v4: Take('I3a') (two-pass Kling act + animate,
placed 1:1 at 182.6 on the song clock), no push, no mouth work, paper fibre only."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 182.95833333333334, 184.625


def setup(ctx):
    global B, P
    B = Take('I3a', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=37)


def render(t, ctx):
    return fin(B.at(t), P)

"""F3a (111.042-112.250 = F3's first 29 frames; F3b is the last 12). BED+CAR v4. Puff from 112.146 (sound cue); palm out to frame right."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 111.04166666666667, 112.25


def setup(ctx):
    global B, P
    B = Take('F3a', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=63)


def render(t, ctx):
    return fin(B.at(t), P)

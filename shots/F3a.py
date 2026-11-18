"""F3a (111.042-112.250 = F3's first 29 frames; F3b, the match cut to 1988, is the last 12) '拔一把毫毛 吹一口气'.  BED+CAR v3.

No rapping face. In her car seat (rear right; the passenger headrest down the left edge) she squints at one plucked hair,
lays it on her palm, fills her cheeks and PUFFS it off: the puff starts on 112.146 (sound cue), and the hair is in the air
when F3b cuts to little Jade doing the same (her puff 112.372). Kling v4 first+last (media/kf/v3/F3a.jpg -> F3a_end.jpg).
Her face ends at about 0.59/0.37 of the frame (F3b's little Jade: 0.6/0.38).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 111.04166666666667, 112.25


def setup(ctx):
    global B, P
    B = Take('F3a', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=63)


def render(t, ctx):
    return fin(B.at(t), P)

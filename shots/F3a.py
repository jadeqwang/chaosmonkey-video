"""F3a (111.042-112.250 = F3's first 29 frames; F3b, the match cut to 1988, is the last 12) '拔一把毫毛 吹一口气'.
ROOMS-26.

The daughter plucks at her hair and brings her open palm up under her lips (sd25 lip-sync take 2; the amber streetlight
passing is the clip's own). Match cut: her face must sit at 0.6/0.38 of the frame on the last frame (F3b's little Jade);
the clip has it at ~0.41/0.46 at the end, so the compositor pushes in (1.0 -> 1.28, ease in) and drifts right onto it: a push in,
entering the story. Car grade, paper fibre. Lyric in WenKai on the dark headliner.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _car_grade import car_grade

T0, T1 = 111.04166666666667, 112.25
FACE = (893, 549)          # face centre in the clip on the last frame (1080p px, measured)
TARGET = (1200, 508)       # where F3b (team ATTIC) has little Jade's face on its first frame (measured: 0.625/0.47)
ZEND = 1.35


def setup(ctx):
    global B, P, WORDS
    B, _ = base_for('F3a', 'media/kf/F3a.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=41)
    WORDS = words_of(ctx, '拔一把毫毛', 111.04)


def render(t, ctx):
    f = B.at(t)
    f = car_grade(f, ctx, [(FACE[0], FACE[1], 260, 300), (930, 700, 260, 200)], dark=0.66)
    f = paper_fibre(f, P, 0.5)
    u = ramp(t, T0, T1, 'in')
    z = 1.0 + (ZEND - 1.0) * u
    # the camera centre that puts FACE at TARGET for this zoom, blended in with u
    cx = FACE[0] - (TARGET[0] - 960) / z
    cy = FACE[1] - (TARGET[1] - 540) / z
    cx, cy = 960 + (cx - 960) * u, 540 + (cy - 540) * u
    f = move(f, ctx, z, cx, cy)
    lyric(f, ctx, sung(WORDS, t, tail=0.4, sep=''), x=0.40, y=0.07, px=30)
    return f

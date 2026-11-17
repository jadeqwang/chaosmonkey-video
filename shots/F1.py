"""F1 (107.042-108.833) '石头里蹦出来 没有童年'.  ROOMS-26.

Hard cut on the pickup: 2026, dusk on the highway. The daughter in her car seat raps, deadpan (sd25 lip-sync; the
amber streetlight passing through the cabin is the clip's own: two passes, kept). Car grade (dusk-violet darks, the
face kept), paper fibre. Lyric in WenKai, small, on the dark ceiling.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _car_grade import car_grade, amber_sweep

T0, T1 = 107.04166666666667, 108.83333333333333
FACES = [(960, 330, 260, 300), (960, 640, 260, 200)]


def setup(ctx):
    global B, P, WORDS
    B, _ = base_for('F1', 'media/kf/F1.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=31)
    WORDS = words_of(ctx, '石头里蹦出来', 107.04)


def render(t, ctx):
    f = B.at(t)
    f = car_grade(f, ctx, FACES, dark=0.66)
    f = paper_fibre(f, P, 0.5)
    lyric(f, ctx, sung(WORDS, t, tail=0.4, sep=''), x=0.5, y=0.065, px=30)
    return f

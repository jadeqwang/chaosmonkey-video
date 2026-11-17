"""F4a (112.750-114.333 = F4 frames 2706-2743; F4b by team FACES from 2744) '千百个我 同时在这里'.  ROOMS-26.

The rear-view mirror holds both faces, Jade (left) and the daughter behind (right), singing together (sd25 lip-sync
take 2; an amber streetlight slides across the headliner and the mirror: the clip's own). Car grade with both
reflected faces kept; paper fibre. Lyric in WenKai, small, on the dark dashboard below the mirror.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _car_grade import car_grade

T0, T1 = 112.75, 114.33333333333333
FACES = [(330, 360, 200, 230), (790, 400, 170, 200)]


def setup(ctx):
    global B, P, WORDS
    B, _ = base_for('F4a', 'media/kf/F4a.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=42)
    WORDS = words_of(ctx, '千百个我', 112.76)


def render(t, ctx):
    f = B.at(t)
    f = car_grade(f, ctx, FACES, dark=0.66)
    f = paper_fibre(f, P, 0.5)
    lyric(f, ctx, sung(WORDS, t, tail=0.4, sep=''), x=0.5, y=0.80, px=30)
    return f

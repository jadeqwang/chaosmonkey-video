"""F4a (112.750-114.333; F4b by team STAGE follows) '千百个我 同时在这里'.  BED+CAR v3.

The rear-view mirror: Jade's eyes find her daughter in the glass and SMILE (cheeks lift, brows up); the daughter, small at
the far end of the glass in her car seat, bounces and points at the mirror, rapping at her; the second seat empty between
them. Kling v4 take of media/kf/v3/F4a.jpg. Slow 4 % push on the mirror. Nobody's mouth is the subject (plays as voice).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 112.75, 114.33333333333333


def setup(ctx):
    global B, P
    B = Take('F4a', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=67)


def render(t, ctx):
    return fin(push(B.at(t), ctx, t, T0, T1, 1.0, 1.04, cx=800, cy=330, kind='linear'), P)

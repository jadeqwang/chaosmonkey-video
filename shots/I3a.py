"""I3a (182.958-184.625; I3b by team BOOK starts at frame 4431) "You think I'd ask for a seat at the table?"  BED+CAR v3.

LAP_child_cu: the daughter in Jade's lap, a little HESITANT: eyes on the page for "You think", then she tips her head
back against her mother's chest to look up at her on "I'd ask" (183.93), really asking. Kling v4 first+last
(media/kf/v3/I3a.jpg -> I3a_end.jpg). The arc's first beat (REVISION_V3 section 1): the child doubts herself.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 182.95833333333334, 184.625


def setup(ctx):
    global B, P
    B = Take('I3a', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=37)


def render(t, ctx):
    f = push(B.at(t), ctx, t, T0, T1, 1.0, 1.03, cx=960, cy=470, kind='linear')
    return fin(f, P)

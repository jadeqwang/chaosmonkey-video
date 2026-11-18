"""K2a (210.542-212.125; K2b by team BOOK starts at frame 5091) "He opened the Book of Life and Death".  BED+CAR v3.

Over Jade's shoulder: the daughter leans in over the page (the hall of the Ten Kings, team BOOK's K2b page), her hand on
it, saying the line down into the book (her face is not seen: the line plays on the page). The camera pushes over the
shoulder INTO the page; the last third is a 2D warp on the page quad and the last frame hands over to K2b's frame 0.
Kling v4 take of media/kf/v3/ots.jpg.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 210.54166666666666, 212.125


def setup(ctx):
    global O
    O = OtsPush(ctx, 'ots_K2a', 'K2b_page.png', 'work/bedcar/ends/K2b_f0.png', ta=T0 + 0.1, tb=T1)


def render(t, ctx):
    return O.render(t, ctx)

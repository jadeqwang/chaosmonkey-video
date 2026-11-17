"""G6 near-silence (149.292-149.708, 10 frames). Team MOUNTAIN.

Bare paper, full frame: the margins are gone (see shots/_margins.py: margin_state(t) is open from 149.285).
The book paper, nothing on it, not even its breath.
"""
from shots._mountain import *

T0, T1 = 3583 / 24, 3593 / 24


def setup(ctx):
    global P
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED)


def render(t, ctx):
    return P.frame(t)

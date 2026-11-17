"""I3b (second part of I3, from 184.6 to 187.0) '...a seat at the table?'.

The heaven page: the Peach Banquet as one painted table and eight chairs on bare paper under a peach bough, a blank
name slip at every seat but one; the empty chair, front-centre, pulled out toward us (plate D_banquet, keyed onto the
2026 aged page). Still. The only motion: the torch pool drifting slowly from the table to the empty chair.
Chair coordinates for I4 are in LOG_heaven.md (CHAIR_* below, plate px -> 1080p frame px).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.ink import *
from _heaven import *

T0, T1 = 184.6, 187.0
PLATE = 'design/plates/D_heaven/D_banquet.png'
SC = 0.56
X0, Y0 = -178, 70                         # plate px at frame (0, 0) (1080p)
CHAIR_BOX = (1345, 1351, 1787, 1985)      # empty chair, plate px (PLATES.md)
CHAIR_SEAT = (1590, 1640)                 # centre of its seat, plate px
POOL_FROM = (1480, 1060)                  # plate px: over the table
POOL_TO = (1585, 1600)                    # plate px: on the empty chair


def setup(ctx):
    global BASE, WORDS
    W, H = ctx.W, ctx.H
    s = SC * ctx.s
    T = ctx.cache('i3b_banquetT', lambda: key_paper(load_image(PLATE)), deps=[PLATE])
    P = Paper(W, H, 'aged', seed=27, scale=1.4)
    BASE = (P.rgb * fit(T, W, H, s, X0, Y0, bg=(1, 1, 1))).astype(np.float32)
    WORDS = line_words(ctx, 'You think', 182.95)


def chair_frame(ctx):
    s = SC * ctx.s
    b = CHAIR_BOX
    return (to_frame(b[:2], s, X0, Y0), to_frame(b[2:], s, X0, Y0), to_frame(CHAIR_SEAT, s, X0, Y0))


def render(t, ctx):
    s = SC * ctx.s
    u = ease(clamp((t - T0) / (T1 - T0), 0, 1), 'inout')
    p = (POOL_FROM[0] + (POOL_TO[0] - POOL_FROM[0]) * u, POOL_FROM[1] + (POOL_TO[1] - POOL_FROM[1]) * u)
    L = light_field(ctx.W, ctx.H, to_frame(p, s, X0, Y0), 520 * ctx.s, ambient=0.08, gain=1.34, stretch=1.2, seed=13)
    f = lit(BASE, L)
    lyric(f, ctx, sung_words(WORDS, t, tail=0.4), y=0.06, x=0.56, px=28)
    return f

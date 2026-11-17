"""I3a (182.958-184.625; I3b by team HEAVEN starts at 184.6 = frame 4431) 'You think I'd ask for a seat at the table?'
ROOMS-26.

The daughter's deadpan close-up, face off-centre right, looking left to her mother; she sings (sd25 lip-sync on our own
keyframe media/kf/I3a.jpg, painted for this shot: alt/I3a_v1). Bedroom grade: the flashlight's white bounce from the
page below, the wall to dark violet wash; a touch of line/wash flattening; paper fibre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field

T0, T1 = 182.95833333333334, 184.625
FACES = [(1130, 430, 330, 420, 0.82)]


def setup(ctx):
    global B, P, FLD, WORDS
    B, _ = base_for('I3a', 'media/kf/I3a.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=37)
    FLD = bed_field(ctx, (1100, 2600), 300, FACES, amb=0.34, stretch=1.3, key='I3a')
    WORDS = words_of(ctx, 'You think I', 182.9)


def render(t, ctx):
    f = flatten(B.at(t), ctx, 0.35)
    f = bed_grade(f, ctx, (1100, 2600), 300, field=FLD)
    f = paper_fibre(f, P, 0.6)
    lyric(f, ctx, sung(WORDS, t, tail=0.6), x=0.40, y=0.88, px=26)
    return f

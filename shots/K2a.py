"""K2a (210.542-212.125; K2b by team HEAVEN starts at 212.1 = frame 5091) 'He opened the Book of Life and Death'.
ROOMS-26.

The daughter's face over the top edge of the book, eyes down on the pages, singing (sd25 lip-sync on our own keyframe
media/kf/K2a.jpg: alt/K2a_v1). The pages, hidden from us, throw the flashlight's white up onto her face. The cover's red
is pulled down (only pink and orange are saturated in 2026). Bedroom grade, paper fibre. A slow push in (2 %) toward
the book's edge leads into K2b's push into the painting.
Fix round 2 (QA item 7): reframed in comp (x1.40 -> 1.43) so her face sits on the left third and the book's top edge
runs out of frame to the right (no longer a centred face).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field, desat_hue

T0, T1 = 210.54166666666666, 212.125
FACES = [(870, 330, 400, 300, 0.90)]


def setup(ctx):
    global B, P, FLD, WORDS, COVER
    B, _ = base_for('K2a', 'media/kf/K2a.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=38)
    FLD = bed_field(ctx, (880, 2600), 100, FACES, amb=0.34, stretch=1.0, key='K2a')
    WORDS = words_of(ctx, 'He opened the Book', 210.5)
    COVER = np.zeros((ctx.H, ctx.W), F32)
    COVER[int(600 * ctx.s):, :] = 1
    COVER = soften(COVER, ctx, 10)


def render(t, ctx):
    f = flatten(B.at(t), ctx, 0.3)
    f = desat_hue(f, 335, 20, 0.45, COVER)
    f = bed_grade(f, ctx, (880, 2600), 100, field=FLD)
    f = paper_fibre(f, P, 0.6)
    z = 1.40 + 0.03 * ramp(t, T0, T1, 'in')
    f = move(f, ctx, z, 980 + 320 / z, 400 + 160 / z)    # face (980, 400 in the take) -> (640, 380): the left third
    lyric(f, ctx, sung(WORDS, t, tail=0.6), x=0.5, y=0.94, px=26)
    return f

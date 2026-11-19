"""A4 song frames 302-371 (70 f). ATTIC v3.
Mama's pink-from-dishwater hands (no apron in frame) take the book little Jade holds up to her; she bounces, lets go, claps once and follows the book with shining eyes.
Kling v4 take on media/kf/v3/A4.jpg (pick + retime map: media/comp/attic3/picks.json, key A4)."""
from shots._attic3 import *

T0, T1 = 302 / 24, 372 / 24
S = AtticShot([Seg(T0, T1, 'A4', key='A4', window=(1273, 65, 1603, 448), wedge=(0.10, 0.38), floor=0.6, keep=[(700, 420, 340, 340), (1300, 420, 320, 240)], cam=[(T0, 960, 540, 1.0), (T1, 900, 520, 1.08)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

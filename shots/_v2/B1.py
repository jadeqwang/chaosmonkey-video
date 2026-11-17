"""B1 15.500-22.292 (163 f). Team ROOMS-88. Little Jade three-quarter, deadpan, lit red, sings to Mama (soft at
the left edge). Seedance 2.5 lip-sync take on the vocal stem (retimed by its measured lag). No window in frame."""
from shots._rooms88 import *

T0, T1 = 372 / 24, 535 / 24
R = RoomShot(shot='B1', T0=T0, T1=T1, kf='B1', keep=[(1130, 380, 230, 280, 1.0), (300, 400, 300, 400, 0.45)], floor=0.24,
             lyrics=[('妈妈, will you tell me before I sleep', (560, 40, 520, 44)), ('how 孙悟空 came to be?', (560, 40, 520, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

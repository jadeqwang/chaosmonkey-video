"""E6 104.292-107.042 (66 f). Team ROOMS-88. A secret only he could hear: little Jade looks sideways; Mama
chuckles; on the rap pickup (107.04) her eyes go wide. Kling v4 first+last (E6 -> E6_end). Sign in the window."""
from shots._rooms88 import *

T0, T1 = 2503 / 24, 2569 / 24
R = RoomShot(shot='E6', T0=T0, T1=T1, kf='E6', window=(1440, 380, 1660, 620), sign=(1550, 500, 150, 0.0),
             keep=[(680, 240, 140, 170, 1.0), (1240, 740, 130, 160, 1.0)], floor=0.24, twos=True,
             lyrics=[('a secret only he could hear', (560, 40, 800, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

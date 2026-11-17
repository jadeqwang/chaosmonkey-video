"""E3 93.000-99.917 (166 f). Team ROOMS-88. Names and faces, I lose a few / but a spell Id remember well: little
Jade close, deadpan; Mama a warm blur at the left. Seedance 2.5 lip-sync. Sign in the window behind her."""
from shots._rooms88 import *

T0, T1 = 2232 / 24, 2398 / 24
R = RoomShot(shot='E3', T0=T0, T1=T1, kf='E3', window=(1538, 229, 1802, 483), sign=(1670, 356, 160, -2.0),
             keep=[(1160, 440, 260, 320, 1.0), (300, 500, 300, 500, 0.4)], floor=0.30,
             lyrics=[('Names and faces, I lose a few', (560, 40, 520, 44)), ("but a spell I'd remember well", (560, 40, 520, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

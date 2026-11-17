"""F3b 112.250-112.750 (12 f = the last 12 frames of F3, song frames 2694-2705). Team ROOMS-88. Match cut from
the 2026 car: little Jade blows across her open palm in the 1988 attic; hairs fly toward frame left. Kling v4, the
blow section. Mamas dark clothes kept dim (out of the light). Sign in the window."""
from shots._rooms88 import *

T0, T1 = 2694 / 24, 2706 / 24
R = RoomShot(shot='F3b', T0=T0, T1=T1, kf='F3b', window=(1590, 210, 1821, 571), sign=(1705, 390, 210, -2.0),
             keep=[(1220, 380, 200, 240, 1.0), (980, 700, 220, 120, 0.9)], floor=0.26, twos=False)


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

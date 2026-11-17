"""A3 9.708-12.583 (69 f). Team ROOMS-88. The stair door: a tall slot of warm tungsten light, Mama comes up small,
drying her hands on her apron; little Jade sits up on her mat, back to us. Kling v4 first+last (A3 -> A3_end).
The window at the right edge carries the sign."""
from shots._rooms88 import *

T0, T1 = 233 / 24, 302 / 24
R = RoomShot(shot='A3', T0=T0, T1=T1, kf='A3', window=(1815, 480, 1920, 800), sign=(1880, 640, 190, 8.0),
             keep=[(460, 420, 90, 300, 0.9), (1560, 760, 200, 300, 0.7)], floor=0.28, twos=True)


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

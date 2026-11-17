"""A4 12.583-15.500 (70 f). Team ROOMS-88. Clapper 16ths: close on Mamas wet red hands lifting the storybook off
the pillow; its red cloth cover catches the neon. Kling v4 first+last (A4 -> A4_end). A sliver of the window at the
top right edge."""
from shots._rooms88 import *

T0, T1 = 302 / 24, 372 / 24
R = RoomShot(shot='A4', T0=T0, T1=T1, kf='A4', window=(1825, 0, 1920, 230), sign=(1880, 110, 160, 0.0),
             keep=[(640, 500, 520, 330, 1.0)], floor=0.24, twos=True)


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

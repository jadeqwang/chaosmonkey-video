"""C3 46.167-49.625 (83 f). Team ROOMS-88. Not yet, that is just the start: Mama, amused, lowers little Jades
raised hands with one finger. Seedance 2.5 lip-sync, first+last frame (C3 -> C3_end). Sign in the window upper right.
The book on the floor is closed (red cover): no page."""
from shots._rooms88 import *

T0, T1 = 1108 / 24, 1191 / 24
R = RoomShot(shot='C3', T0=T0, T1=T1, kf='C3', window=(1673, 94, 1920, 498), sign=(1800, 290, 220, -6.0),
             keep=[(660, 250, 150, 180, 1.0), (1160, 420, 130, 160, 1.0), (900, 560, 200, 160, 0.8)], floor=0.24,
             lyrics=[("Not yet, that's just the start", (560, 40, 800, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

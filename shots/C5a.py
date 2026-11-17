"""C5a 52.250-54.600 (57 f, song frames 1254-1310; team MOUNTAIN C5b starts on frame 1311). Team ROOMS-88.
The wind blew once: Mama in profile leans to the page and blows; dust motes swirl in the red beam; the window and
the sign behind her. The open book on her lap carries the egg page (B_egg). Kling v4 first+last (C5a -> C5a_end)."""
from shots._rooms88 import *

T0, T1 = 1254 / 24, 1311 / 24
R = RoomShot(shot='C5a', T0=T0, T1=T1, kf='C5a', page=dict(kind='egg', roi=(560, 760, 1160, 1080), tl=(-1, -1), cthr=20),
             window=(430, 0, 1150, 530), sign=(860, 250, 300, 3.0), dust=True, pool=0.0, sign_exclude=[(560, 300, 210, 260)],
             keep=[(560, 300, 160, 200, 1.0), (880, 950, 300, 120, 1.0)], floor=0.24, twos=True,
             lyrics=[('the wind blew once, and that was all', (1100, 960, 700, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

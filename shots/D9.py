"""D9 82.500-85.833 (80 f). Team ROOMS-88. Little Jade on her mat holds the look-out pose copied from the page;
Mama laughing. Kling v4 (wobble + laugh); the compositor pulls back out of the stage to the room (zoom 1.25 -> 1.0)
and the open book on the mat carries the birth page. Sign in the window."""
from shots._rooms88 import *

T0, T1 = 1980 / 24, 2060 / 24
R = RoomShot(shot='D9', T0=T0, T1=T1, kf='D9', page=dict(kind='birth', roi=(1150, 920, 1410, 1065), tl=(-1, -1), cthr=22),
             window=(1610, 190, 1840, 600), sign=(1725, 380, 200, 0.0),
             keep=[(820, 500, 140, 170, 1.0), (1380, 300, 110, 140, 1.0), (1380, 600, 200, 330, 0.7)], floor=0.30,
             twos=True, cam=[(1980 / 24, 1250, 520, 1.25), (85.3, 1050, 540, 1.0)],
             still_cam=[(1980 / 24, 1250, 520, 1.25), (85.3, 1050, 540, 1.0)])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

"""B2 22.292-26.125 (92 f). Team ROOMS-88. Mama sings with the open book across her knees; the spread (B3s
花果山, the same page-space build as team MOUNTAIN) is mapped onto the blank pages and is the brightest thing in the
room. Seedance 2.5 lip-sync. The neon sign in the window, upper right."""
from shots._rooms88 import *

T0, T1 = 535 / 24, 627 / 24
R = RoomShot(shot='B2', T0=T0, T1=T1, kf='B2', page=dict(kind='hgs', roi=(600, 760, 1130, 990), tl=(-1, -1), cthr=26),
             window=(1689, 152, 1902, 446), sign=(1795, 290, 170, -4.0),
             keep=[(745, 330, 150, 180, 1.0), (1180, 470, 120, 140, 0.9), (860, 880, 300, 120, 1.0)], floor=0.30,
             cam=[(535 / 24, 960, 540, 1.0), (25.05, 950, 600, 1.06), (627 / 24, 850, 878, 2.1)],
             still_cam=[(535 / 24, 960, 540, 1.0), (25.05, 950, 600, 1.06), (627 / 24, 850, 878, 2.1)],
             lyrics=[('On 花果山, where the cliffs run steep', (560, 40, 800, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

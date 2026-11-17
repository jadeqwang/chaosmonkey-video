"""B2 22.292-26.125 (92 f). Team ROOMS-88. Mama sings with the open book across her knees; the spread (B3s
花果山, the same page-space build as team MOUNTAIN) is mapped onto the blank pages and is the brightest thing in the
room. Seedance 2.5 lip-sync. The neon sign in the window, upper right."""
from shots._rooms88 import *

T0, T1 = 535 / 24, 627 / 24


def _aim(R, ctx):
    """Land the push on the spread as the clip leaves it (the tracked page quad at the last frame), so the cut into
    MOUNTAIN's B3 (the flat spread filling the frame) continues the same push."""
    q = R.PT.quad(R.src.index(T1 - 1 / 24), 1.0)
    cx, cy = q.mean(0)
    wq = max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))
    z = min(2.6, 1700.0 / max(wq, 1))
    keys = [(T0, 960, 540, 1.0), (25.05, 950, 600, 1.06), (T1, float(cx), float(cy), z)]
    R.c['cam'] = keys
    R.c['still_cam'] = keys


R = RoomShot(setup=_aim, lyrics_out=25.05, shot='B2', T0=T0, T1=T1, kf='B2', page=dict(kind='hgs', roi=(600, 790, 1130, 1000), tl=(-1, -1), cthr=16, thr=175, mthr=130, mcthr=28),
             window=(1689, 152, 1902, 446), sign=(1795, 290, 170, -4.0),
             keep=[(745, 330, 150, 180, 1.0), (1180, 470, 120, 140, 0.9), (860, 880, 300, 120, 1.0)], floor=0.24,
             cam=[(535 / 24, 960, 540, 1.0), (25.05, 950, 600, 1.06), (627 / 24, 850, 878, 2.1)],
             still_cam=[(535 / 24, 960, 540, 1.0), (25.05, 950, 600, 1.06), (627 / 24, 850, 878, 2.1)],
             lyrics=[('On 花果山, where the cliffs run steep', (560, 40, 800, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

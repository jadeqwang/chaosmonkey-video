"""E6 song frames 2503-2568 (66 f). ATTIC v4.
'a secret only he could hear': the v3 acted take (Kling v4, hair and acting kept: the director's pick) with ONLY the room replaced:
BiRefNet matte of the two figures per frame (work/attic4/e6_birefnet.py), over a clean room plate that matches v4_E6
(work/attic4/e6_comp.py -> media/comp/attic4/E6_bgswap.mp4). Retimed as in v3."""
from shots._attic4 import *

T0, T1 = 2503 / 24, 2569 / 24
S = AtticShot([Seg4(T0, T1, 'E6', clip='media/comp/attic4/E6_bgswap.mp4',
                    tmap=[[104.292, 0.3], [106.6, 3.9], [106.85, 4.55], [107.042, 4.95]], floor=0.62, keep=[(1075, 500, 400, 380)], cam=[(T0, 1075, 560, 1.3), (T1, 1085, 540, 1.42)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

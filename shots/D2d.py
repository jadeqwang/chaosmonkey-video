"""D2d song frames 1531-1545 (15 f). ATTIC v3.
Last 15 frames of D2: little Jade, off Mama's lap, copies the monkey's last bow on her mat (the bow bottoms on 63.980); Mama laughs behind her.
Kling v4 take on media/kf/v3/D2d.jpg (pick + retime map: media/comp/attic3/picks.json, key D2d)."""
from shots._attic3 import *

T0, T1 = 1531 / 24, 1546 / 24
S = AtticShot([Seg(T0, T1, 'D2d', key='D2d', window=(1557, 273, 1738, 496), guide='v3_D9_a', floor=0.6, keep=[(1126, 520, 260, 380), (640, 460, 260, 300)], cam=[(T0, 940, 580, 1.3), (T1, 940, 580, 1.3)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

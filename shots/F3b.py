"""F3b song frames 2694-2705 (12 f). ATTIC v3.
Last 12 frames of F3, the match cut from the car: little Jade in the lap puffs the hairs off her flat palm (112.372) and watches them go, delighted.
Kling v4 take on media/kf/v3/F3b.jpg (pick + retime map: media/comp/attic3/picks.json, key F3b)."""
from shots._attic3 import *

T0, T1 = 2694 / 24, 2706 / 24
S = AtticShot([Seg(T0, T1, 'F3b', key='F3b', floor=0.66, keep=[(1130, 420, 380, 340)], cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

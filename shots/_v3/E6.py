"""E6 song frames 2503-2568 (66 f). ATTIC v3.
'a secret only he could hear': she twists round in the lap and gives Mama the sideways look, one eyebrow; Mama hides a laugh behind her hand; on the rap pickup (107.04) her eyes go wide.
Kling v4 take on media/kf/v3/E6.jpg (pick + retime map: media/comp/attic3/picks.json, key E6)."""
from shots._attic3 import *

T0, T1 = 2503 / 24, 2569 / 24
S = AtticShot([Seg(T0, T1, 'E6', key='E6', floor=0.62, keep=[(1075, 500, 400, 380)], cam=[(T0, 1075, 560, 1.3), (T1, 1085, 540, 1.42)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

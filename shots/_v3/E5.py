"""E5 song frames 2477-2502 (26 f). ATTIC v3.
'(ps ps ps)' 103.20: LAP_child_cu. Mama whispers behind a cupped hand at her ear; little Jade holds still, eyes sliding sideways and widening, shoulders coming up because it tickles.
Kling v4 take on media/kf/v3/E5.jpg (pick + retime map: media/comp/attic3/picks.json, key E5)."""
from shots._attic3 import *

T0, T1 = 2477 / 24, 2503 / 24
S = AtticShot([Seg(T0, T1, 'E5', key='E5', floor=0.66, keep=[(760, 560, 420, 380)], cam=[(T0, 900, 560, 1.0), (T1, 880, 560, 1.05)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

"""C5a song frames 1254-1310 (57 f). ATTIC v3.
LAP_profile, contre-jour against the window: Mama fills her cheeks and blows across the page past the child's ear (hair lifts 53.220); little Jade scrunches up (53.950) and laughs. BOOK's C5b follows from frame 1311.
Kling v4 take on media/kf/v3/C5a.jpg (pick + retime map: media/comp/attic3/picks.json, key C5a)."""
from shots._attic3 import *

T0, T1 = 1254 / 24, 1311 / 24
S = AtticShot([Seg(T0, T1, 'C5a', key='C5a', window=(950, 129, 1253, 493), wedge=(0.52, 0.80), floor=0.6, keep=[(1000, 420, 330, 300)], cam=[(T0, 1000, 500, 1.12), (T1, 1010, 480, 1.2)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

"""L2b song frames 5660-5685 (26 f). ATTIC v4. The 1988 half of the blanket match cut (the cut is ON 235.833). The v4 L2b camera
(same as bed26 v4_L2) over a sleeping little Jade: Mama's hands on the turned quilt edge at her waist draw it up (from 235.88),
tuck at the chin (236.276), then one hand rests and she looks at her. Fallen books at frame right. Kling first+last take
(media/kf/v4/L2b.jpg -> L2b_end.jpg), pick key L2b."""
from shots._attic4 import *

T0, T1 = 5660 / 24, 5686 / 24
S = AtticShot([Seg4(T0, T1, 'L2b', key='L2b', tmap=[[T0, 0.0], [T1, T1 - T0]], window=[[1277, -70], [1700, -70], [1700, 265], [1277, 265]],
                    wedge=(0.50, 0.80), floor=0.62, keep=[(1090, 380, 300, 200), (900, 480, 380, 260)],
                    cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

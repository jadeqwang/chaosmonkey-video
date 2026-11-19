"""D3 song frames 1546-1629 (84 f). ATTIC v4. Mama sings "No cradle, no lullaby, no song", mock-solemn head shakes; child mirrors; both crack up.
Two-pass: Seedance take at4ls_D3_1 (acting) -> p-video-animate (ls4w_D3_asrc1s1), clip frame 0 = 62.935. Crop x780 y100 w1800 h1012 of
media/kf/v4/D3.jpg (media/kf/v4/D3_crop.jpg). Blade wedge typeset on the painted window."""
from shots._attic4 import *

T0, T1 = 1546 / 24, 1630 / 24
S = AtticShot([Seg4(T0, T1, 'D3_crop', key='D3', floor=0.62, keep=[(350, 400, 700, 650)], window=(985, 0, 1665, 600), wedge=(0.55, 0.78),
                    cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

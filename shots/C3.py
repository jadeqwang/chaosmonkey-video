"""C3 song frames 1108-1190 (83 f). ATTIC v4. Mama sings "Not yet, that's just the start" laughing, lowers the child's raised hands.
Two-pass: Kling act ls4w_C3_act2 -> pruna p-video-animate sings it to the vocal stem (ls4w_C3_a2s2), clip frame 0 = 45.665.
The take is crop2 x384 y0 w2458 h1382 of media/kf/v4/C3.jpg (media/kf/v4/C3_crop2.jpg). Calligraphy LEFT (outer 20% dark floor/wall)."""
from shots._attic4 import *

T0, T1 = 1108 / 24, 1191 / 24
S = AtticShot([Seg4(T0, T1, 'C3_crop2', key='C3', floor=0.62, keep=[(500, 100, 700, 700)], cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

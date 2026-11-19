"""D2d song frames 1531-1545 (15 f). ATTIC v4. Little Jade, off Mama's lap, copies the monkey's last bow on her mat (bottoms
63.980); Mama amused. Kling v4 first+last take at4_D2d_k4_t3 (D2d_up -> D2d), clip frames 19.5-34.5 at speed 1."""
from shots._attic4 import *

T0, T1 = 1531 / 24, 1546 / 24
S = AtticShot([Seg4(T0, T1, 'D2d', key='D2d', tmap=[[T0, 23.5 / 24], [T1, 38.5 / 24]], floor=0.6,
                    keep=[(1100, 400, 400, 500), (600, 400, 300, 300)], cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

"""A2 5.458-9.708 (102 f). ATTIC v3. Low across the floorboards, a slow drift in toward little Jade, who lies on her back
wide AWAKE waiting for her mama: blinking up at the rafters, fingers at the quilt, the storybook hugged on her chest,
toes wriggling. Kling v4 take on media/kf/v3/A2.jpg; blade sign in the window in code."""
from shots._attic3 import *

T0, T1 = 131 / 24, 233 / 24
S = AtticShot([Seg(T0, T1, 'A2', key='A2', window=(1481, 266, 1797, 521), guide='v3_D9_a', floor=0.55,
                   keep=[(1250, 420, 260, 220)],
                   cam=[(T0, 900, 560, 1.0), (T1, 1160, 470, 1.22)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

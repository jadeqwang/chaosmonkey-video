"""D9 82.500-85.833 (80 f). ATTIC v4. The fall: ONE Kling v4 take (first D9_0 + mids D9a, D9b + last D9c; at4_D9_k4_t1) retimed
piecewise to the sound cues (steps onto the stack 83.244, wobble 83.475, topple 83.798, lands 84.127, catch 84.351, settle 84.570).
Keyframe media/kf/v4/D9_0.jpg; books end where D9c has them. Pick: media/comp/attic4/picks.json key D9."""
from shots._attic4 import *

T0, T1 = 1980 / 24, 2060 / 24
FM = [(0, 8), (18, 26), (31, 54), (39, 64), (44, 74), (50, 84), (80, 114)]
S = AtticShot([Seg4(T0, T1, 'D9_0', key='D9', tmap=[[T0 + a / 24, b / 24] for a, b in FM], floor=0.6,
                    keep=[(1350, 330, 300, 360), (560, 520, 500, 420)], cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

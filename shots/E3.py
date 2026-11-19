"""E3 ATTIC v4: cut inside the shot at song frame 2304 (96.000, the breath).
E3a (72f): shipped two-pass singing take from the crop of E3.jpg. E3b (94f): Kling act take t3, wider three-quarter angle, sword-hand cast, mouth not the subject."""
from shots._attic4 import *

T0, TC, T1 = 2232 / 24, 2304 / 24, 2398 / 24
S = AtticShot([
    Seg4(T0, TC, 'E3_crop', clip='media/gen/ls4w_E3_asrc1s1_ae0d17999b.mp4', tmap=[[91.49, 0.0], [91.49 + 10, 10.0]], cam=crop_cam(T0, TC)),
    Seg4(TC, T1, 'E3b2', clip='media/gen/at4_E3b2_k4_t2_b0ac14e677.mp4', tmap=[[96.0, 0.0], [96.0 + 10, 10.0]], cam=crop_cam(TC, T1)),
])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

"""E1 ATTIC v4: two-pass singing take (Kling act + p-video-animate) from the crop of media/kf/v4/E1.jpg, placed at its t0, speed 1."""
from shots._attic4 import *

T0, T1 = 2060 / 24, 2146 / 24
S = AtticShot([Seg4(T0, T1, 'E1_crop', clip='media/gen/ls4w_E1_asrc1s1_587711a421.mp4', tmap=[[84.345, 0.0], [84.345 + 10, 10.0]], cam=crop_cam(T0, T1))])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

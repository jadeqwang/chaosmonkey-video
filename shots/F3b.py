"""F3b song frames 2694-2705 (12 f). ATTIC v4.
Last 12 frames of F3, the match cut from the car: little Jade in the lap puffs the hairs off her flat palm (112.372), the hairs
leave toward frame RIGHT (as F3a / the SWARM entry side), she laughs. Kling v4 take at4_F3b_k4_t1 on media/kf/v4/F3b.jpg; the
take's blow is slow (clip 1.6-3.1 s), so the 12 frames are the clip's blow-and-hairs window played at about 3x."""
from shots._attic4 import *

T0, T1 = 2694 / 24, 2706 / 24
S = AtticShot([Seg4(T0, T1, 'F3b', clip='media/gen/at4_F3b_k4_t1_5bd67cb2e5.mp4', tmap=[[T0, 1.58], [T1, 3.08]], floor=0.66,
                    keep=[(1130, 420, 380, 340)], cam=crop_cam(T0, T1))])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

"""B1 song frames 372-534 (163 f). ATTIC v4. Sings on camera: little Jade ('妈妈, will you tell me before I sleep / how 孙悟空 came to be?').
Over Mama's left shoulder (v4_B1): Mama's shoulder-upper arm-elbow-forearm chain at frame right, little Jade's hand on the forearm.
Keyframe media/kf/v4/B1.jpg; the take is made from its crop media/kf/v4/B1_crop.jpg (box 330,110,2133x1200 of the 3072 keyframe,
1920x1080). One Seedance 2.5 take (at4ls_B1_4, acts and sings in one pass, no mouth pasted); clip frame 0 at its measured place
(song 13.518), speed 1. Pick in media/comp/attic4/picks.json (key B1). Calligraphy side: LEFT (outer 20 %: x 0-190 of 960)."""
from shots._attic4 import *

T0, T1 = 372 / 24, 535 / 24
S = AtticShot([Seg4(T0, T1, 'B1_crop', key='B1', tmap=[[13.5183, 0.0], [23.5183, 10.0]], floor=0.8, keep=[(500, 0, 1420, 1080)],
                    cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

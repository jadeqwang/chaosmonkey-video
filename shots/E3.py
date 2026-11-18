"""E3 song frames 2232-2397 (166 f). ATTIC v3. Sings on camera: little Jade.
'Names and faces, I lose a few / but a spell I'd remember well': lap. A big shrug with palms up on 'lose a few' (94.9), sits up and taps her temple on 'remember well' (97.3-99.1), sure of herself; Mama smiling above her.
Acted Kling v4 take on media/kf/v3/E3.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0 (shift 0).
Pick: media/comp/attic3/picks.json key E3 (falls back to the keyframe as a still if no take is picked)."""
from shots._attic3 import *

T0, T1 = 2232 / 24, 2398 / 24
S = AtticShot([Seg(T0, T1, 'E3', key='E3', tmap=[[T0, 0.0], [T0 + 7, 7.0]], floor=0.64, keep=[(1064, 510, 320, 320), (900, 230, 300, 280)], cam=[(T0, 1000, 500, 1.0), (T1, 1010, 480, 1.09)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

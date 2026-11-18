"""C3 song frames 1108-1190 (83 f). ATTIC v3. Sings on camera: Mama.
'Not yet, that's just the start': lap, close. Mama sings it laughing with her eyes and lowers the small raised hands with one finger; little Jade sneaks them up an inch, is caught, grins up at her.
Acted Kling v4 take on media/kf/v3/C3.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0 (shift 0).
Pick: media/comp/attic3/picks.json key C3 (falls back to the keyframe as a still if no take is picked)."""
from shots._attic3 import *

T0, T1 = 1108 / 24, 1191 / 24
S = AtticShot([Seg(T0, T1, 'C3', key='C3', tmap=[[T0, 0.0], [T0 + 4, 4.0]], floor=0.64, keep=[(946, 270, 300, 300), (1207, 590, 300, 300)], cam=[(T0, 1010, 500, 1.0), (T1, 1020, 480, 1.07)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

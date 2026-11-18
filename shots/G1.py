"""G1 song frames 2915-3058 (144 f). ATTIC v3. Sings on camera: little Jade.
'Why does he wear a band of gold? / Is it heavy? Is it cold?': lap. A real worry: two fingertips on her own forehead, looks from the page up to Mama and waits. The margins begin to close (shared schedule).
Acted Kling v4 take on media/kf/v3/G1.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0 (shift 0).
Pick: media/comp/attic3/picks.json key G1 (falls back to the keyframe as a still if no take is picked)."""
from shots._attic3 import *

T0, T1 = 2915 / 24, 3059 / 24
S = AtticShot([Seg(T0, T1, 'G1', key='G1', tmap=[[T0, 0.0], [T0 + 6, 6.0]], floor=0.64, keep=[(1188, 590, 320, 320), (996, 270, 300, 280)], cam=[(T0, 1090, 500, 1.0), (T1, 1090, 480, 1.1)])], margins=True, margin_state=soft_margins(0.4))


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

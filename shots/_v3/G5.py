"""G5 song frames 3515-3582 (68 f). ATTIC v3. Sings on camera: little Jade (one word).
'Yes' (148.72), over Mama's off-camera 'no less'. Her face on the centre line inside the narrowest strip: lip held, eyes down; up and away; back up to Mama, holds; the smallest 'Yes'; a blink after, and something kept back at the corner of her mouth. Not defeated: deciding. The margins snap open at 149.285.
Acted Kling v4 take on media/kf/v3/G5c.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0 (shift 0).
Pick: media/comp/attic3/picks.json key G5 (falls back to the keyframe as a still if no take is picked)."""
from shots._attic3 import *

T0, T1 = 3515 / 24, 3583 / 24
S = AtticShot([Seg(T0, T1, 'G5c', key='G5', tmap=[[T0, 0.0], [T0 + 3, 3.0]], floor=0.66, keep=[(960, 600, 340, 380)], cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])], margins=True, margin_state=soft_margins(0.4))


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

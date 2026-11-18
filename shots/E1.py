"""E1 song frames 2060-2145 (86 f). ATTIC v3. Sings on camera: Mama.
'The monkey had a memory just like you': back in her lap after the fall (toppled books on the floor). Mama's finger circles and taps her nose on 'you' (88.47); she goes cross-eyed, scrunches up and giggles.
Acted Kling v4 take on media/kf/v3/E1.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0 (shift 0).
Pick: media/comp/attic3/picks.json key E1 (falls back to the keyframe as a still if no take is picked)."""
from shots._attic3 import *

T0, T1 = 2060 / 24, 2146 / 24
S = AtticShot([Seg(T0, T1, 'E1', key='E1', tmap=[[T0, 0.0], [T0 + 4, 4.0]], floor=0.64, keep=[(700, 270, 300, 300), (974, 470, 300, 300)], cam=[(T0, 860, 500, 1.06), (T1, 850, 470, 1.16)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

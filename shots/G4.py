"""G4 song frames 3390-3514 (125 f). ATTIC v3. Sings on camera: Mama.
'Then 听话, or you'll get one to wear / Do what mama says, no more ...': no shadow play. Two-shot in the lap, composed for the narrow margin strip (faces stacked on the centre line). Mama sings it light and teasing, a finger lifted, glancing at the toppled books; little Jade listens sceptical and mischievous, a subtle lip bite, eyes going to the books, to Mama, away.
Acted Kling v4 take on media/kf/v3/G4c.jpg + lip transfer (docs/LIPSYNC_V3.md), clip frame 0 at T0 (shift 0).
Pick: media/comp/attic3/picks.json key G4 (falls back to the keyframe as a still if no take is picked)."""
from shots._attic3 import *

T0, T1 = 3390 / 24, 3515 / 24
S = AtticShot([Seg(T0, T1, 'G4c', key='G4', tmap=[[T0, 0.0], [T0 + 6, 6.0]], floor=0.66, keep=[(930, 380, 300, 380), (980, 700, 300, 300)], cam=[(T0, 960, 520, 1.08), (143.2, 960, 520, 1.08), (144.6, 895, 520, 1.08), (T1, 895, 520, 1.08)])], margins=True, margin_state=soft_margins(0.4))


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

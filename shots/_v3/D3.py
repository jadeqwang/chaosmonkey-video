"""D3 song frames 1546-1629 (84 f). ATTIC v3.
'No cradle, no lullaby, no song' (no @64.44, no @65.32, no @67.06). LAP_front, the window at the frame edge: Mama shakes her head slowly, one mock-solemn 'no' each; little Jade mirrors her half a beat late; both break into smiles. Wide enough that lips are not the subject (no singing mouth).
Kling v4 take on media/kf/v3/D3.jpg (pick + retime map: media/comp/attic3/picks.json, key D3)."""
from shots._attic3 import *

T0, T1 = 1546 / 24, 1630 / 24
S = AtticShot([Seg(T0, T1, 'D3', key='D3', floor=0.62, keep=[(960, 420, 420, 380)], cam=[(T0, 960, 470, 1.25), (T1, 960, 450, 1.38)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

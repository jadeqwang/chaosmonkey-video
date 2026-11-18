"""L2b song frames 5660-5685 (26 f). ATTIC v3, round 2. The 1988 half of the blanket match cut (the cut is ON 235.833).
Composed as a true match to BED+CAR's L2 last frame (keyframe media/kf/v3/L2m.jpg, painted from their L2_end for camera
and placement only): the same high three-quarter view; Mama kneeling lower left, seen from behind, reaching right;
little Jade's head on the pillow upper centre-right; the quilt lower right. Mama's hands arrive at her chin, tuck
(236.276), then one hand rests and she looks at her. The blade sign is the wedge in the window upper right.
Kling v4 on L2m (pick key L2m). L3 (the same scene, pulled back) follows from frame 5686."""
from shots._attic3 import *

T0, T1 = 5660 / 24, 5686 / 24
S = AtticShot([Seg(T0, T1, 'L2m', key='L2m', window=[[1610, 50], [1845, 85], [1830, 290], [1590, 250]], wedge=(0.50, 0.80),
                   floor=0.62, keep=[(1000, 420, 420, 300), (720, 300, 380, 380)],
                   cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

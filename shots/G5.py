"""G5 song frames 3515-3592 (78 f, 146.458-149.708: runs through G6's slot). ATTIC v4. Little Jade alone, 85 mm close-up (v4_G5).
She does not mouth Mama's off-camera 'no more, no less'; her eyes go away and think, back to Mama, a small nod, then the late 'Yes'
(attack 149.306). Take = Seedance act (at4ls_G5_5, motion only) -> p-video-animate with the edited vocal (vocals_v4.wav, 146.0-148.9 muted)
= ls4w_G5_asrc5s1, frame 0 = song 145.652, shift 0. Full frame, no margins."""
from shots._attic4 import *

T0, T1 = 146.4583333, 149.7083333
PLACE = 145.652

S = AtticShot([Seg4(T0, T1, 'G5', key='G5', tmap=[[T0, T0 - PLACE], [T1, T1 - PLACE]], floor=0.66, keep=[(900, 560, 420, 420)],
                    cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])], margins=False)


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
# v4 swap pick a1s2

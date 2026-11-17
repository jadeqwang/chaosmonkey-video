"""G5 146.458-149.292 (68 f). Team ROOMS-88. Drums out. Little Jade's face dead centre inside the narrowest strip
(15 %, shared margin schedule), holding Mama's look a moment too long; nothing moves but her eyes, then 'Yes'
(148.72). Seedance 2.5 lip-sync on a window whose audio is silent until 'Yes'. The margins snap open at 149.285."""
from shots._rooms88 import *

T0, T1 = 3515 / 24, 3583 / 24
R = RoomShot(shot='G5', kf='G5', T0=T0, T1=T1, window=(1494, 307, 1706, 535), sign=(1600, 421, 130, 0.0),
             keep=[(960, 450, 260, 320, 1.0)], floor=0.24, margins=True,
             cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)], still_cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

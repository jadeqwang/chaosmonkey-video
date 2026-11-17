"""G1 121.458-127.458 (144 f). Team ROOMS-88. Back to 1988: the sound narrows (121.905) and the paper margins begin to
close in (team MOUNTAIN's shared schedule, shots/_margins.py); colour drains, gold kept. 'Why does he wear a band of
gold? / Is it heavy? Is it cold?': little Jade touches her own forehead. Seedance 2.5 lip-sync, first+last frame
G1_end (hand rising) -> G1 (fingers on the brow). Her face is centred (the strip is centred)."""
from shots._rooms88 import *

T0, T1 = 2915 / 24, 3059 / 24
R = RoomShot(shot='G1', kf='G1', T0=T0, T1=T1, keep=[(960, 330, 280, 330, 1.0), (760, 200, 260, 160, 0.8)], floor=0.24,
             margins=True, cam=[(T0, 960, 540, 1.0), (T1, 960, 470, 1.08)],
             still_cam=[(T0, 960, 540, 1.0), (T1, 960, 470, 1.08)],
             lyrics=[('Why does he wear a band of gold?', (660, 64, 600, 40)), ('Is it heavy? Is it cold?', (660, 64, 600, 40))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

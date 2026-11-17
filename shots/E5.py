"""E5 103.208-104.292 (26 f). Team ROOMS-88. (ps ps ps): extreme close, Mamas cupped hand and lips at little
Jades ear (the keyframe puts the hand at her own mouth: reads as a whisper). Kling v4. No subtitle."""
from shots._rooms88 import *

T0, T1 = 2477 / 24, 2503 / 24
R = RoomShot(shot='E5', T0=T0, T1=T1, kf='E5', window=(1595, 490, 1817, 759), sign=(1706, 620, 160, -2.0),
             keep=[(360, 340, 260, 300, 1.0), (1160, 380, 230, 280, 1.0)], floor=0.30, twos=True)


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

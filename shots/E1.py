"""E1 85.833-89.417 (86 f). Team ROOMS-88. The monkey had a memory just like you: Mama taps little Jades nose
on you (88.5). Seedance 2.5 lip-sync. The open book on Mamas lap carries the troop page; sign in the window."""
from shots._rooms88 import *

T0, T1 = 2060 / 24, 2146 / 24
R = RoomShot(shot='E1', T0=T0, T1=T1, kf='E1', page=dict(kind='troop', roi=(480, 930, 900, 1078), tl=(-1, -1), cthr=22),
             window=(1654, 333, 1920, 635), sign=(1790, 480, 180, -3.0),
             keep=[(740, 360, 140, 170, 1.0), (1160, 600, 120, 150, 1.0), (680, 1010, 220, 80, 0.9)], floor=0.30,
             lyrics=[('The monkey had a memory just like you', (560, 40, 800, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

"""E1 85.833-89.417 (86 f). Team ROOMS-88. The monkey had a memory just like you: Mama taps little Jades nose
on you (88.5). Seedance 2.5 lip-sync. The open book on Mamas lap carries the troop page; sign in the window.

Fix round 2 (QA item 9): the verse-2 crash 86.998 (frame 2088) is marked in picture: the neon outside flares for
3 frames (tubes and their spill into the room) and the camera cuts in on the same frame (a hard punch from the
two-shot to a closer two-shot on Mama's hand and little Jade's face, then a slow push). Mama's hand cannot be
retimed to the hit: the take is lip-synced and she sings from 86.3 (the reach is already under way).
"""
from shots._rooms88 import *

T0, T1 = 2060 / 24, 2146 / 24
T_CRASH = 86.998
F_CRASH = frame_of(T_CRASH)                      # 2088
FLARE = {0: 1.0, 1: 0.6, 2: 0.3}                 # frames after the crash -> flare amount
WIN_C = (1790, 480)


def sign_on(t):
    return 1.0 + 0.9 * FLARE.get(frame_of(t) - F_CRASH, 0.0)


_SP = {}


def flare_spill(f, t, R):
    a = FLARE.get(frame_of(t) - F_CRASH, 0.0)
    if a <= 0:
        return f
    H, W = f.shape[:2]
    if (W, H) not in _SP:
        yy, xx = np.mgrid[0:H, 0:W].astype(F32)
        d2 = (xx - WIN_C[0] * R.s) ** 2 + (yy - WIN_C[1] * R.s) ** 2
        _SP[(W, H)] = np.exp(-d2 / (2 * (620 * R.s) ** 2)).astype(F32)[..., None]
    col, k = neon_colour(t, period=SIGN_PERIOD, phase=SIGN_PHASE, fade=0.22)
    col = np.asarray(col, F32) / max(float(np.max(col)), 1e-3)
    return np.clip(f * (1 + 0.55 * a * _SP[(W, H)] * col), 0, 0.975).astype(F32)


Z_IN = 1.16
R = RoomShot(shot='E1', T0=T0, T1=T1, kf='E1', page=dict(kind='troop', roi=(480, 930, 900, 1078), tl=(-1, -1), cthr=22),
             window=(1654, 333, 1920, 635), sign=(1790, 480, 180, -3.0), sign_on=sign_on, post=flare_spill,
             keep=[(740, 360, 140, 170, 1.0), (1160, 600, 120, 150, 1.0), (680, 1010, 220, 80, 0.9)], floor=0.24,
             cam=[(T0, 960, 540, 1.0), ((F_CRASH - 1) / 24, 960, 540, 1.0), (F_CRASH / 24, 1090, 520, Z_IN),
                  (T1, 1070, 520, Z_IN * 1.03)],
             lyrics=[('The monkey had a memory just like you', (560, 40, 800, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

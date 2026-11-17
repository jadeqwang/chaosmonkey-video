"""D2d = the last 15 frames of D2 (song frames 1531-1545, 63.792-64.417). Team ROOMS-88. The fourth bow is little Jade
on her mat in the attic, copying him: she stands with fist in palm, then on the beat 63.980 she is hard re-posed
into the bow (no in-betweens, like STAGE's puppet joints) and a small 倉 lands beside her (STAGE's seal style,
tools/stage/stage.seals), completing the 四击头 才 才 才 仓. Keyframes painted for this shot (edits of D9 so the room
is the same): media/kf/D2d_stand.jpg, media/kf/D2d.jpg (the bow)."""
from shots._rooms88 import *
from tools.stage.stage import seals

T0, T1 = 1531 / 24, 1546 / 24
T_BOW = 63.980
CFG = dict(T0=T0, T1=T1, page=dict(kind='birth', roi=(1150, 920, 1410, 1065), tl=(-1, -1), cthr=22),
           window=(1610, 190, 1840, 600), sign=(1725, 380, 200, 0.0),
           keep=[(820, 500, 140, 170, 1.0), (1330, 420, 120, 160, 1.0), (1330, 650, 200, 300, 0.7)], floor=0.24,
           cam=[(T0, 1060, 540, 1.06), (T1, 1060, 540, 1.06)])
RS = RoomShot(shot='D2d_stand', kf='D2d_stand', **CFG)
RB = RoomShot(shot='D2d', kf='D2d', **CFG)


def setup(ctx):
    global SEAL
    RS.setup(ctx)
    RB.setup(ctx)
    SEAL = seals(ctx.s)['cang_small']


def render(t, ctx):
    f = (RS if t < T_BOW - 1e-6 else RB).render(t)
    s = ctx.s
    strike(f, SEAL, t, T_BOW, (1545 * s, 760 * s), overshoot=0.16)
    if 0 <= t - T_BOW < 2 / 24:                                   # the same 2-frame jolt STAGE gives each bow
        f = shaken(f, *shake_offset(t, [T_BOW], amp=5 * s, dur=0.16))
    return f

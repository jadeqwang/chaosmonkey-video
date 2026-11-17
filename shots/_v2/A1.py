"""A1 0.000-5.458 (131 f). Team ROOMS-88. Black; on the clapper roll (0.165) the neon stutters on outside the dusty
window lower right: the room's light is the sign's light, so the plate itself blends from A1_off to A1 with the
tube's level. The sign is code (shots/_rooms88.Sign). The red breathes toward cold blue once (period 9 s). Code only.
"""
from shots._rooms88 import *

T0, T1 = 0.0, 131 / 24
WINDOW = (1400, 650, 1655, 915)
SIGN = (1525, 770, 152, -2.0)


def level(t, hits):
    """Stutter-on: a strike on each clapper of the roll, decaying between; steady from the last; one dip at the
    silence (0.605) relit on the next clapper (0.775)."""
    if t < hits[0][0] - 1e-6:
        return 0.0
    v = 0.0
    for h, s in hits:
        if t >= h - 1e-6:
            v = max(v, s * math.exp(-(t - h) / 0.035))
    last = hits[-1][0]
    if t >= last:
        v = max(v, 0.55 + 0.45 * min(1.0, (t - last) / 0.12))
    if 0.605 <= t < 0.775:
        v = min(v, 0.3)
    return min(1.0, v)


def setup(ctx):
    global ON, OFF, G, TEX, SG, HITS
    W, H = ctx.W, ctx.H
    ON, OFF = kf('A1', W, H), kf('A1_off', W, H)
    G = grade_field(ON, floor=0.22)
    TEX = paper_tex(W, H)
    SG = Sign(ON, ctx.s, WINDOW, SIGN)
    hs = [(h['t'], h['strength']) for h in ctx.timing.hits('clapper', 0.1, 0.5)]
    HITS = [(h, 0.5 + 0.5 * s) for h, s in hs] or [(0.165, 1.0)]


def plate(t, lv):
    f = OFF + (ON - OFF) * lv
    return SG.apply(f, t, on=lv)


def render(t, ctx):
    lv = level(t, HITS)
    f = plate(t, lv)
    f = finish(f, G, TEX)
    if lv <= 0:                                  # before the sign: black (the warm ink floor, paper fibre showing)
        f = f * 0.18
    return f

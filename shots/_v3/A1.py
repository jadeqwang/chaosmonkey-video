"""A1 0.000-5.458 (131 f). ATTIC v3. Black; on the clapper roll (0.165) the neon blade sign outside the dusty window
stutters on: a narrow wedge of cinnabar (LAYOUT_V3 option A), lettering in code, not mirrored. Little Jade lies awake,
a small dark shape. The title (Chaos Monkey / 混沌猴 / Jade Wang / seal) sits small at the lower left from 0.7 s to
the end of the shot. Code only (keyframes media/kf/v3/A1.jpg, A1_off.jpg)."""
from shots._attic3 import *
from shots._attic3 import finish, paper_tex, grade_field

T0, T1 = 0.0, 131 / 24
WINDOW = (1465, 395, 1680, 657)


def level(t, hits):
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
    global ON, OFF, G, TEX, BL, HITS, TA, TRGB
    W, H = ctx.W, ctx.H
    ON, OFF = kf3('A1', W, H), kf3('A1_off', W, H)
    G = grade_field(ON, floor=0.42)
    TEX = paper_tex(W, H)
    BL = Blade('v3_A1', WINDOW, ctx.s, W, H, wedge=(0.56, 0.76))
    hs = [(h['t'], h['strength']) for h in ctx.timing.hits('clapper', 0.1, 0.5)]
    HITS = [(h, 0.5 + 0.5 * s) for h, s in hs] or [(0.165, 1.0)]
    TA, TRGB = title_block(W, H, ctx.s)


def render(t, ctx):
    lv = level(t, HITS)
    f = OFF + (ON - OFF) * lv
    f = BL.apply(f, t, on=lv)
    f = finish(f, G, TEX)
    if lv <= 0:
        f = f * 0.18
    a = TA[..., None] * 0.88 * min(1.0, max(0.0, (t - 0.70) / 0.6))
    f = f * (1 - a) + TRGB * a
    return f

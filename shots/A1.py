"""A1 0.000-5.458 (131 f). ATTIC v4. Black; on the clapper roll (0.165) the neon blade sign outside the dusty window stutters
on: a narrow wedge of cinnabar, lettering in code, not mirrored. Little Jade lies awake, a small shape on her mat; Mama's mat
beside her is EMPTY with its beige quilt folded at the foot (keyframe media/kf/v4/A1.jpg, A1_off.jpg from the same painting).
If a Kling take is picked (media/comp/attic4/picks.json key A1) the ON layer plays it, the OFF layer stays still.
The title (Chaos Monkey / 混沌猴 / Jade Wang / seal) sits small at the lower left from 0.7 s to the end."""
from shots._attic4 import *
from shots._attic3 import finish, paper_tex, grade_field

T0, T1 = 0.0, 131 / 24
WINDOW = (1313, 213, 1646, 523)


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
    global SG, OFF, G, TEX, BL, HITS, TA, TRGB
    W, H = ctx.W, ctx.H
    SG = Seg4(T0, T1, 'A1', key='A1', tmap=[[T0, 0.0], [T1, T1 - T0]], window=WINDOW, wedge=(0.57, 0.75))
    SG.setup(ctx)
    OFF = kf4('A1_off', W, H)
    G = grade_field(SG.KF, floor=0.42)
    TEX = paper_tex(W, H)
    BL = SG.blade
    hs = [(h['t'], h['strength']) for h in ctx.timing.hits('clapper', 0.1, 0.5)]
    HITS = [(h, 0.5 + 0.5 * s) for h, s in hs] or [(0.165, 1.0)]
    TA, TRGB = title_block(W, H, ctx.s, x=150, y=800)


def render(t, ctx):
    lv = level(t, HITS)
    ON, _ = SG.frame(t)
    f = OFF + (ON - OFF) * lv
    f = BL.apply(f, t, on=lv)
    f = finish(f, G, TEX)
    if lv <= 0:
        f = f * 0.18
    a = TA[..., None] * 0.88 * min(1.0, max(0.0, (t - 0.70) / 0.6))
    f = f * (1 - a) + TRGB * a
    return f

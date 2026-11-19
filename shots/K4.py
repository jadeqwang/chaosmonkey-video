"""K4 (217.165-224.18) 'I turned each page, I looked for mine'; the beat cuts out at 218.715. BOOK v4: NO HAND.

The open register under the torch. The pages turn by themselves in a draught from the underworld: each leaf is a real
deformable mesh (shots/_book4_pageturn.py): the free edge lifts first and curls, a corner leads, a ripple runs out to
the edge, it goes over, slaps down. Three leaves land (on 'page' 218.22, on 'looked' 220.92 and on the wooden hit
221.805); one lifts, hangs and falls back before it goes over (219.4-220.3); in the last second the final leaf stirs.
The pages carry the typeset columns of names as in v3 (struck entry on p1 from K3). Keep the inscription (key K4).
Living detail: the torch breathes; dust turns in the beam.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math

import cv2
import numpy as np
from scipy.interpolate import PchipInterpolator

from tools.ink import *
from _heaven import *
from _book4_pageturn import Leaf, dust_motes

T0, T1 = 217.16666666666666, 224.16666666666666
SC = 0.29                       # page px -> 1080p px
PW, PH, GUT = 2200, 3300, 70    # page size; gutter between pages in a spread
SPW = 2 * PW + GUT
D_CAM = 4200.0
PI = math.pi


def strike_page(ctx):
    """The K3 strike at page resolution (density, page px)."""
    pts = [(916, 428, 0.5), (911, 900, 1.0), (906, 1600, 1.05), (903, 2150, 1.0), (868, 2390, 0.95),
           (762, 2620, 0.75), (690, 2800, 0.4)]
    pap = Paper(PW, PH, 'aged', seed=40)
    st = stroke(pts, width=92 * 1.7, seed=3, paper=pap, density=0.95, dry=0.04, dry_end=0.7, bleed=3.5)
    d = st.density(1.6, wet=0)
    d = np.maximum(d, np.minimum(np.maximum(blur(d, 2.7) * 0.5, blur(d, 7.2) * 0.22), 0.6))
    full = np.zeros((PH, PW), np.float32)
    x0, y0 = int(st.pos[0]), int(st.pos[1])
    h, w = d.shape
    ys, xs, ye, xe = max(0, y0), max(0, x0), min(PH, y0 + h), min(PW, x0 + w)
    full[ys:ye, xs:xe] = d[ys - y0:ye - y0, xs - x0:xe - x0]
    return full


def curve(pts):
    """pchip through [(t, v)] (held outside)."""
    ts = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    f = PchipInterpolator(ts, vs, extrapolate=False)

    def g(t):
        if t <= ts[0]:
            return vs[0]
        if t >= ts[-1]:
            return vs[-1]
        return float(f(t))
    return g


def make_leaves(lands):
    """The draught's script. Each leaf: spread index k (leaf = left page of spread k), th/bend/twist/amp curves, land
    time (None = never lands)."""
    a, b, c = lands
    L = []
    # 0: slow, gentle first turn, a long lift, lands on 'page'
    L.append(dict(k=0, land=a,
                  th=curve([(a - 1.0, 0), (a - 0.66, .10), (a - .44, .50), (a - .24, 1.45), (a - .10, 2.65), (a, PI)]),
                  bend=curve([(a - 1.0, 0), (a - .66, .85), (a - .44, 1.25), (a - .24, .9), (a - .10, .30), (a, 0)]),
                  twist=curve([(a - 1.0, 0), (a - .6, .5), (a - .3, .7), (a - .1, .25), (a, 0)]),
                  amp=curve([(a - 1.0, 0), (a - .6, .06), (a - .3, .12), (a - .05, .05), (a, 0)])))
    # 1: lifts, hangs and falls back (219.4-220.3), then a quick turn landing on 'looked'
    L.append(dict(k=1, land=b,
                  th=curve([(219.40, 0), (219.62, .16), (219.88, .42), (220.06, .33), (220.20, .07), (220.30, 0),
                            (b - .50, .02), (b - .36, .30), (b - .24, 1.05), (b - .14, 2.2), (b - .06, 2.9), (b, PI)]),
                  bend=curve([(219.40, 0), (219.62, .55), (219.88, 1.05), (220.06, .65), (220.20, .20), (220.30, 0),
                              (b - .50, .1), (b - .36, 1.0), (b - .24, 1.15), (b - .14, .7), (b - .06, .25), (b, 0)]),
                  twist=curve([(219.40, 0), (219.8, .9), (220.1, .3), (220.3, 0), (b - .4, .5), (b - .2, .6), (b, 0)]),
                  amp=curve([(219.40, 0), (219.8, .14), (220.2, .08), (220.3, 0), (b - .4, .08), (b - .15, .10), (b, 0)])))
    # 2: heavy and fast, lands on the wooden hit
    L.append(dict(k=2, land=c,
                  th=curve([(c - .70, 0), (c - .52, .14), (c - .40, .62), (c - .26, 1.55), (c - .12, 2.55), (c - .05, 2.95), (c, PI)]),
                  bend=curve([(c - .70, 0), (c - .52, .7), (c - .40, 1.0), (c - .26, .55), (c - .12, .2), (c, 0)]),
                  twist=curve([(c - .70, 0), (c - .4, .35), (c - .15, .2), (c, 0)]),
                  amp=curve([(c - .70, 0), (c - .35, .07), (c - .1, .05), (c, 0)])))
    # 3: the last leaf stirs and settles back (never goes over)
    L.append(dict(k=3, land=None,
                  th=curve([(222.75, 0), (223.00, .20), (223.30, .38), (223.55, .30), (223.80, .08), (223.95, .0)]),
                  bend=curve([(222.75, 0), (223.00, .55), (223.30, .85), (223.55, .60), (223.80, .20), (223.95, 0)]),
                  twist=curve([(222.75, 0), (223.2, .8), (223.7, .2), (223.95, 0)]),
                  amp=curve([(222.75, 0), (223.2, .12), (223.8, .05), (223.95, 0)])))
    return L


def setup(ctx):
    global SPREADS, PAGES, LANDS, OX, OY, S, L, WORDS, SPINE_X, INS, LEAVES, TEX, BLANK, LF, DUST
    ensure_ledger()
    W, H = ctx.W, ctx.H
    S = SC * ctx.s
    OX, OY = (W - SPW * S) / 2, (H - PH * S) / 2 + 6 * ctx.s
    pages = [load_image(LEDGER + f'E_ledger_p{k}.png') for k in range(1, 9)]
    strike = ctx.cache('k4_strike', lambda: strike_page(ctx))
    pages[0] = pages[0] * ink_T(strike)
    sp = [load_image(LEDGER + f'spread_{k}_{k + 1}.png') for k in (1, 3, 5, 7)]
    sp[0][:, PW + GUT:] = sp[0][:, PW + GUT:] * ink_T(strike)
    nightbg = blur(Paper(W, H, 'aged', seed=88).rgb, 9 * ctx.s) * 0.30
    a = fit(np.ones((PH, SPW, 1), np.float32), W, H, S, -OX / S, -OY / S)
    a = a[..., None] if a.ndim == 2 else a
    SPREADS = [fit(s_, W, H, S, -OX / S, -OY / S) * a + nightbg * (1 - a) for s_ in sp]
    SPINE_X = OX + (PW + GUT / 2) * S
    # bare paper for the last leaf's underside
    bare = blur(Paper(PW, PH, 'aged', seed=61).rgb, 2.0) * 0.96
    pages_all = pages + [bare]
    tw, th = int(round(PW * S * 2)), int(round(PH * S * 2))
    TEX = [cv2.resize(p, (tw, th), interpolation=cv2.INTER_AREA) for p in pages_all]
    tm = ctx.timing
    try:
        lands = [tm.word('I turned each page', 'page')[0], tm.word('I turned each page', 'looked')[0]]
    except Exception:
        lands = [218.22, 220.92]
    hit = [h['t'] for h in tm.hits('low_drum', 221.0, 222.5)]
    lands.append(hit[0] if hit else 221.805)
    LANDS = [on_frame(x) for x in lands]
    LEAVES = make_leaves(LANDS)
    D = PW * S * 3.0
    LF = []
    for lv in LEAVES:
        k = lv['k']
        front = TEX[2 * k + 1] if k < 3 else TEX[6]       # leaf = left page of spread k (p2, p4, p6; last: p7)
        back = TEX[2 * k + 2] if k < 3 else TEX[8]        # its back = next right page (p3, p5, p7; last: bare)
        LF.append(Leaf(front, back, SPINE_X, OY, PW * S, PH * S, (W, H, D, W * 0.5, H * 0.52)))
    L = light_field(W, H, (W * 0.5, H * 0.53), 700 * ctx.s, ambient=0.07, gain=1.34, tilt=0, stretch=1.25, seed=21)
    WORDS = line_words(ctx, 'I turned each page', 217.2)
    from tools.ink.inscription import inscription
    INS = inscription(ctx, 'K4', box=(1690, 150, 190, 640), ground='dark')
    rr = np.random.default_rng(5)
    DUST = rr.random((46, 6)).astype(np.float32)           # x, y, z-speed, size, phase, drift


def landed(t):
    return sum(1 for tl in LANDS if t >= tl - 1e-9)


def leaf_params(lv, t):
    th = lv['th'](t)
    bend = lv['bend'](t)
    tw = lv['twist'](t)
    amp = lv['amp'](t)
    if lv['land'] is not None and t >= lv['land']:         # the slap: a short damped ripple of the free edge
        d = t - lv['land']
        k = 1.0 if lv['k'] == 2 else 0.6
        bend = -0.55 * k * math.exp(-d / 0.07) * abs(math.sin(d * 26))
        amp = 0.10 * k * math.exp(-d / 0.10)
    return th, bend, tw, amp


def render(t, ctx):
    n = landed(t)
    W, H = ctx.W, ctx.H
    f = SPREADS[min(n, 3)].copy()
    act = None
    for lv, lf in zip(LEAVES, LF):
        th, bend, tw, amp = leaf_params(lv, t)
        post = lv['land'] is not None and lv['land'] <= t < lv['land'] + 0.3
        if th > 0.012 and (lv['land'] is None or t < lv['land']) or post:
            act = (lv, lf, th, bend, tw, amp, post)
    if act:
        lv, lf, th, bend, tw, amp, post = act
        k = lv['k']
        sx = int(round(SPINE_X))
        if post:
            f = SPREADS[min(k + 1, 3)].copy()
        elif k < 3:
            f = np.concatenate([SPREADS[k + 1][:, :sx], SPREADS[k][:, sx:]], 1).copy()
        else:
            f = SPREADS[3].copy()
        lf.draw(f, th, bend, tw, amp, phase=18.0 * t + 1.3 * k)
    # breathing torch and dust turning in the beam
    br = 1.0 + 0.022 * math.sin(2 * math.pi * 0.7 * t) + 0.012 * math.sin(2 * math.pi * 1.9 * t + 1.0)
    Lb = L * br
    f = lit(f, Lb)
    f = dust_motes(f, t, ctx, DUST)
    if not os.environ.get("K4_NOINS"):
        INS.draw(f)
    lyric(f, ctx, sung_words(WORDS, t, tail=1.2), y=0.955, px=28)
    return f

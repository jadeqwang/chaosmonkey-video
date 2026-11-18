"""K3 (213.805-217.165) 'and crossed out his name in a single breath'.

The ledger close: the right page (p1, the plate) with the entry 魂字一千三百五十號 孫悟空 / 天產石猴 該壽三百四十二歲 善終
under the torch, the left page (p2) falling into the dark. Camera and light hold. On 'single breath' ONE wet brush
stroke strikes the entry out top to bottom over 8 frames, its last frame on the onset of 'breath' (216.52); then a
little bleed. Nothing else moves.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json

import numpy as np

from tools.ink import *
from _heaven import *

T0, T1 = 213.79166666666666, 217.16666666666666
SPREAD = PLATE_LEDGER + 'E_ledger_spread_p1p2.png'      # left p2 | gutter 70 | right p1 (4470 x 3300)
OFFX = 2270                                              # p1 x offset in the spread
SC = 0.445                                               # page px -> frame px (1920 authoring)
X0, Y0 = 155, 385                                        # spread px at frame (0, 0)
N_STRIKE = 8                                             # frames to draw the stroke


def setup(ctx):
    global BASE, L, ST, T_END, T_START, DF, BL1, BL2, WORDS, INS
    from tools.ink.inscription import inscription
    INS = inscription(ctx, 'K3', box=(360, 170, 100, 640), ground='dark')
    W, H = ctx.W, ctx.H
    s = SC * ctx.s
    sp = load_image(SPREAD)
    BASE = fit(sp, W, H, s, X0, Y0)
    meta = json.load(open(PLATE_LEDGER + 'E_ledger.json'))
    # one breath: down the number-and-name column (魂字一千三百五十號 孫悟空, x 904) and out in a hook (勾) across the
    # foot of the note column (該壽三百四十二歲 善終, x 708). Page px.
    page_pts = [(916, 428, 0.5), (911, 900, 1.0), (906, 1600, 1.05), (903, 2150, 1.0), (868, 2390, 0.95),
                (762, 2620, 0.75), (690, 2800, 0.4)]
    pts = [((x + OFFX - X0) * s, (y - Y0) * s, p) for x, y, p in page_pts]
    paper = Paper(W, H, 'aged', seed=40)
    ST = stroke(pts, width=meta['strike']['width'] * s, seed=3, paper=paper, density=0.95, dry=0.04, dry_end=0.7,
                bleed=3.5 * s)
    try:
        b0 = ctx.timing.word('and crossed out his name in a single breath', 'breath')[0]
    except Exception:
        b0 = 216.52
    T_END = on_frame(b0)                                 # fix2: complete ON the frame containing 'breath'
    T_START = T_END - N_STRIKE / 24.0
    # fix2: bristle-tapered head. Each bristle (a thin streak across the stroke's width) arrives at its own moment,
    # and the stroke's edges lag its centre, so the advancing front is a ragged point, not a straight cut
    global STAG
    h_, w_ = ST.D.shape
    xs = np.arange(w_, dtype=np.float32)
    rr = np.random.default_rng(11)
    col = np.interp(xs, np.linspace(0, w_ - 1, max(4, w_ // 3)), rr.random(max(4, w_ // 3))).astype(np.float32)
    dens = ST.D.max(axis=0)
    on = np.where(dens > 0.05 * dens.max())[0]
    cxm = (on.min() + on.max()) / 2.0 if len(on) else w_ / 2
    hw = max((on.max() - on.min()) / 2.0, 1.0) if len(on) else w_ / 2
    edge = np.clip(np.abs(xs - cxm) / hw, 0, 1.5) ** 1.5
    STAG = (0.055 * col + 0.07 * edge)[None, :].astype(np.float32)
    DF = ST.density(1.6, wet=0)
    BL1, BL2 = blur(DF, 1.2 * ctx.s), blur(DF, 3.2 * ctx.s)
    # the torch held still over the entry; the pool is a little taller than wide (held at a slant from below)
    cx, cy = to_frame((806 + OFFX, 1598), s, X0, Y0)
    L = light_field(W, H, (cx - 30 * ctx.s, cy + 20 * ctx.s), 470 * ctx.s, ambient=0.075, gain=1.55, tilt=90, stretch=1.55, seed=7)
    WORDS = line_words(ctx, 'and crossed out', 213.8)


def render(t, ctx):
    f = BASE.copy()
    if t >= T_START:
        p = (t - T_START) / (T_END - T_START)
        if p < 1 - 1e-6:                                 # drawing: staggered bristle tips at the front
            age = p - ST.A - STAG
            d = ST.D * smoothstep(0.0, 0.06, age) * (1.0 + ST.wet * np.exp(-np.maximum(age, 0) / 0.12))
        else:
            d = ST.density(1.0 + min(p - 1, 3) * 0.12)
        if p > 1:                                        # the wet stroke keeps creeping a little into the fibres
            k = 1 - np.exp(-(t - T_END) / 0.35)
            halo = np.maximum(BL1 * 0.5, BL2 * 0.22) * k
            d = np.maximum(d, np.minimum(halo, 0.6))
        lay_ink(f, ink_T(d), int(ST.pos[0]), int(ST.pos[1]))
    f = lit(f, L)
    INS.draw(f)                               # v3: static inscription 一笔勾之, pale on the dark beside the ledger
    lyric(f, ctx, sung_words(WORDS, t, tail=0.25), y=0.955, x=0.40, px=28)
    return f

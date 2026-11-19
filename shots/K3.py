"""K3 (213.805-217.165) 'and crossed out his name in a single breath'.

The ledger close: the right page (p1, the plate) with the entry 魂字一千三百五十號 孫悟空 / 天產石猴 該壽三百四十二歲 善終
under the torch, the left page (p2) falling into the dark. Camera and light hold.

v4 (BOOK, LEDGER): K2b cuts to this shot as a MATCH ON THE BRUSH STROKE. The monkey's stroke in K2b runs straight down a
column at screen x ~0.70 and the cut lands mid-stroke; the stroke that continues here IS the strike: bold and wet from frame 0
(WIDEN x v3's width, ~34 px at 540p), its head running on at K2b's brush speed (OPEN_V) down the 孫悟空 column and out in the
hook over ~14 frames. No separate second strike: on 'single breath' (~216.2) the stroke gets its second beat, the wet ink blooms
into the fibres, darkens and sets with a slight spread. The torch breathes and dust turns in the beam. No new text.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json

import numpy as np

from tools.ink import *
from _heaven import *
from _book4_pageturn import dust_motes

T0, T1 = 213.79166666666666, 217.16666666666666
SPREAD = PLATE_LEDGER + 'E_ledger_spread_p1p2.png'      # left p2 | gutter 70 | right p1 (4470 x 3300)
OFFX = 2270                                              # p1 x offset in the spread
SC = 0.445                                               # page px -> frame px (1920 authoring)
X0, Y0 = 155, 385                                        # spread px at frame (0, 0)
N_STRIKE = 8                                             # frames to draw the stroke
OPEN_Y0 = float(os.environ.get('K3_OPEN_Y0', 0.50))      # head of the opening pass at frame 0, fraction of frame height
OPEN_V = float(os.environ.get('K3_OPEN_V', 0.037))       # head speed through the cut, fraction of frame height per frame
PALE = 1.0                                               # the stroke from K2b IS the strike: bold from frame 0
WIDEN = 1.7                                              # K3 is closer than K2b: ~34 px at 540p


def setup(ctx):
    global BASE, L, ST, T_END, T_START, DF, BL1, BL2, WORDS, INS, ROWA, DUST, LCX
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
    ST = stroke(pts, width=meta['strike']['width'] * s * WIDEN, seed=3, paper=paper, density=0.95, dry=0.04, dry_end=0.7,
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
    # arrival value along the column: the stroke's mean arrival A at each frame row (for the opening pass)
    ys0 = int(ST.pos[1])
    dm = ST.D > 0.25 * ST.D.max()
    rowA = np.full(ST.D.shape[0], np.nan, np.float32)
    for r in range(ST.D.shape[0]):
        if dm[r].any():
            rowA[r] = ST.A[r][dm[r]].mean()
    good = ~np.isnan(rowA)
    rowA = np.interp(np.arange(len(rowA)), np.where(good)[0], rowA[good]).astype(np.float32)
    ROWA = (ys0, np.maximum.accumulate(rowA))
    DUST = np.random.default_rng(9).random((40, 6)).astype(np.float32)
    LCX = cx


def render(t, ctx):
    f = BASE.copy()
    # ---- the opening pass: the cut lands mid-stroke; the pale wet head runs on down the column and out in the hook
    ys0, rowA = ROWA
    frame_i = (t - T0) * 24.0
    yh = (OPEN_Y0 + OPEN_V * frame_i) * ctx.H                  # head row in the frame
    yh_rel = int(np.clip(round(yh - ys0), 0, len(rowA) - 1))
    p_open = float(rowA[yh_rel]) if yh < ys0 + len(rowA) else 1.2
    if yh >= ys0 + len(rowA) - 1:
        p_open = 1.2
    age0 = p_open - ST.A - STAG
    d0 = ST.D * smoothstep(0.0, 0.06, age0) * PALE * (1.0 + 0.9 * ST.wet * np.exp(-np.maximum(age0, 0) / 0.05))
    k0 = 1 - np.exp(-max(t - T0, 0) / 0.9)                      # the pale line keeps soaking outward into the fibres
    d0 = np.maximum(d0, np.minimum(np.maximum(BL1 * 0.5, BL2 * 0.25) * PALE * k0, 0.35) * (smoothstep(0.0, 0.06, age0) > 0.3))
    # ---- second beat on 'single breath': the wet ink blooms into the fibres, darkens and sets, a slight spread
    kb = float(smoothstep(T_START, T_START + 0.6, t))
    if kb > 0:
        halo = np.maximum(BL1 * 0.5, BL2 * 0.30) * kb
        d0 = np.maximum(d0 * (1 + 0.22 * kb), np.minimum(halo, 0.7))
    lay_ink(f, ink_T(np.clip(d0, 0, 1.4)), int(ST.pos[0]), int(ST.pos[1]))
    br = 1.0 + 0.022 * math.sin(2 * math.pi * 0.7 * t) + 0.012 * math.sin(2 * math.pi * 1.9 * t + 1.0)
    f = lit(f, L * br)
    f = dust_motes(f, t, ctx, DUST, centre=(LCX / ctx.W, 0.5), spread=(0.30, 0.55))
    INS.draw(f)                               # v3: static inscription 一笔勾之, pale on the dark beside the ledger
    lyric(f, ctx, sung_words(WORDS, t, tail=0.25), y=0.955, x=0.40, px=28)
    return f

"""J5 (200.667-203.708: drop-2 stutter chop, '一通百通 (百通)').

The pull-back completes, mid -> far: the whole blue-green range (the mid plate, keyed) shrinks into the lower-left
corner of a bare aged page, exactly where the far plate puts it ((192, 1936), x0.34): a few strokes, ~5 %.
The torch pool, which held 花果山 in J2, opens out to light the page. 一通百通 is written as a vertical inscription in
the blank upper right, each character blooming on its sung onset; one red seal (悟空, 崇羲篆體) on the last onset (201.965);
'(百通)' at 202.46 is the same seal's faint re-press beside it. On the stutter chop 200.675: 4 frames of rubbing flip.
The last second is still: a nearly bare page.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json

import numpy as np

from tools.ink import *
from tools.ink.text import Inscription
from _heaven import *

T0, T1 = 200.66666666666666, 203.70833333333334
REG = json.load(open('design/plates/D_heaven/D_heaven_registration.json'))
FAR_W, FAR_H = REG['far']['size']
MID_POS = tuple(REG['far']['mid_rect_in_far_px'][:2])     # (192, 1936)
MID_K = REG['far']['scale']                                # 0.34
START = (192 + 2300 * MID_K, 1936 + 1100 * MID_K, 0.55 / MID_K)   # J2's last framing, in far px
END = (FAR_W / 2, FAR_H / 2, 1080 / FAR_H)
T_SETTLE = 202.70


def build():
    return key_paper(load_image('design/plates/D_heaven/D_heaven_mid.png'))


def setup(ctx):
    global SC_, BARE, CAM, RB, PAPER_RGB, INS, NAME, HITS, POSN, CHOP
    Tm = ctx.cache('j5_midT', build, deps=['design/plates/D_heaven/D_heaven_mid.png'])
    P = Paper(FAR_W, FAR_H, 'aged', seed=19, scale=2.0)
    SC_ = Scene(FAR_W, FAR_H, paper=P)
    SC_.add(Tm, kind='ink', pos=MID_POS, scale=MID_K)
    BARE = Scene(FAR_W, FAR_H, paper=P)
    CAM = Camera([(T0, *START), (T_SETTLE, *END, 'inout')])
    RB = Rubbing(ctx.W, ctx.H, seed=6)
    tm = ctx.timing
    ch = [h['t'] for h in tm.hits('chop', 200.6, 200.8)]
    CHOP = ch[0] if ch else 200.675
    words = line_words(ctx, '一通百通', 201.0)
    re_ = line_words(ctx, '(百通)', 202.4)
    s = ctx.s
    INS = Inscription('一通百通', WENKAI, region=(int(1210 * s), int(150 * s), int(170 * s), int(620 * s)),
                      size=ctx.size, vertical=True, words=words or None, start=200.735, end=202.7, mode='word',
                      seed=3, density=0.85)
    NAME = seal('悟空', SEALFONT, 92 * s, 'zhu', wear=0.3, seed=1)
    last = words[-1][1] if words else 201.965
    HITS = [last + 0.06, re_[0][1] if re_ else 202.46]
    x0, y0, bw, bh = INS.box                                # the written text
    POSN = [(x0 + bw / 2, y0 + bh + 70 * s), (x0 + bw / 2 - 108 * s, y0 + bh + 84 * s)]


def pool(t, ctx):
    st = CAM.at(t)
    hx, hy = SC_.to_frame(192 + 1880 * MID_K, 1936 + 800 * MID_K, st, ctx.size)
    u = smoothstep(T0, T_SETTLE, t)
    x = hx + (ctx.W * 0.52 - hx) * u
    y = hy + (ctx.H * 0.50 - hy) * u
    r = (420 + (1250 - 420) * u) * ctx.s
    return (x, y), r


def render(t, ctx):
    tt = min(t, T_SETTLE)                                   # the last second is still
    f = SC_.render(tt, CAM, ctx.size)
    if lyrics_on(ctx):
        INS.draw(f, t)
        echoes(f, NAME, t, list(zip(HITS, POSN)), decay=0.70, seed=8)       # fix2: the re-press reads (was 0.35)
    if on_frame(CHOP) - 1e-9 <= t < on_frame(CHOP) + 4 / 24.0:              # fix2: on the frame containing the chop
        f = RB.apply(f, paper=BARE.render(tt, CAM, ctx.size))
    (x, y), r = pool(tt, ctx)
    L = light_field(ctx.W, ctx.H, (x, y), r, ambient=0.16, gain=1.3, stretch=1.2, seed=5)
    return lit(f, L)

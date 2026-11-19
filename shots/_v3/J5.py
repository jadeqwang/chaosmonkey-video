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
from tools.ink.inscription import inscription
from tools.ink.medium import Mediums

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
    global SC_, BARE, CAM, PAPER_RGB, INS, NAME, HITS
    Tm = ctx.cache('j5_midT', build, deps=['design/plates/D_heaven/D_heaven_mid.png'])
    P = Paper(FAR_W, FAR_H, 'aged', seed=19, scale=2.0)
    SC_ = Scene(FAR_W, FAR_H, paper=P)
    SC_.add(Tm, kind='ink', pos=MID_POS, scale=MID_K)
    BARE = Scene(FAR_W, FAR_H, paper=P)
    CAM = Camera([(T0, *START), (T_SETTLE, *END, 'inout')])
    global MED, SWITCH, INS_XY
    MED = Mediums(ctx.W, ctx.H, seed=6)
    # v3: medium switch on the two measured chops of the stutter (rubbing, then shadow puppet), held 4 frames each
    SWITCH = [(200.675, 'rubbing'), (201.03, 'shadow')]
    # v3: the inscription is STATIC and lives on the page (far sheet), so the pull-back reveals it; 60 px at rest
    zf = END[2]
    def far(x, y):
        return (FAR_W / 2 + (x - 960) / zf, FAR_H / 2 + (y - 540) / zf)
    x0, y0 = far(1230, 150)
    INS = inscription((FAR_W, FAR_H), text='一通百通', box=(x0, y0, 170 / zf, 640 / zf), px=60 / zf, paper=P, seed=3)
    SC_.add(INS.T, kind='ink')
    sl = np.zeros((FAR_H, FAR_W, 4), np.float32)
    sx, sy = INS.seal_pos
    sl[sy:sy + INS.seal.shape[0], sx:sx + INS.seal.shape[1]] = INS.seal
    SC_.add(sl, kind='rgba')
    NAME = seal('悟空', SEALFONT, 60 * 0.86 * ctx.s, 'zhu', wear=0.3, seed=1)
    re_ = line_words(ctx, '(百通)', 202.4)
    HITS = [re_[0][1] if re_ else 202.46]
    INS_XY = (sx + INS.seal.shape[1] / 2 - 75 / zf, sy + INS.seal.shape[0] / 2 + 14 / zf)   # the faint re-press, beside it


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
    px, py = SC_.to_frame(INS_XY[0], INS_XY[1], CAM.at(tt), ctx.size)
    echoes(f, NAME, t, [(HITS[0], (px, py))], decay=0.70, first=0.55, seed=8)      # (百通): the faint re-press
    from tools.ink.medium import medium_at
    m = medium_at(t, SWITCH, 4)
    if m:                                                                   # a clean, full-frame print: not torch-lit
        return MED.render(m, f, BARE.render(tt, CAM, ctx.size))
    (x, y), r = pool(tt, ctx)
    L = light_field(ctx.W, ctx.H, (x, y), r, ambient=0.16, gain=1.3, stretch=1.2, seed=5)
    return lit(f, L)

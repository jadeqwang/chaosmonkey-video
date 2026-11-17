"""L2 (233.208-235.833) Jade's thumb on the flashlight switch; the white pool on the blank column.  ROOMS-26.

The keyframe still (the Kling take rotates the whole torch in her hand and slides the pool off the column: not used):
ONE thing moves: the thumb. The ledger's last page (E_ledger_p8 via spread_7_8, final column bare) is multiplied onto
the painted page so the bare column runs through the pool. The press begins 6 frames before the end (a local warp
carries the thumb onto the switch); the shot ends LIT: the click to black at 235.833 is the first frame of L3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field

T0, T1 = 233.20833333333334, 235.83333333333334
PAGE = [(520, 300), (1240, 378), (1690, 628), (430, 885)]     # painted page, measured on L2.jpg (TL TR BR BL)
POOL = (870, 712)
THUMB = (1152, 500)                                           # thumb tip, resting on the torch beside the switch
PRESS = (-16, 12)                                             # the tip presses in toward the switch (1080p px)
N_PRESS = 6


def page_tex():
    sp = load_image(os.path.join(ROOT, 'work/heaven/ledger/spread_7_8.png'))
    pg = sp[:, :2200]
    pg = cv2.resize(pg, (1100, 1650), interpolation=cv2.INTER_AREA)
    g = np.median(pg.reshape(-1, 3), axis=0)
    T = np.clip(pg / g, 0, 1)
    # shift the page 2.4 % right so the bare column (x 0.10-0.19) runs through the pool (u 0.17 of the quad)
    T = np.concatenate([np.ones((T.shape[0], 26, 3), F32), T[:, :-26]], 1)
    return (1 - 0.85 * (1 - T)).astype(F32)


def setup(ctx):
    global BASE, P, YY, XX
    P = Paper(ctx.W, ctx.H, 'aged', seed=35)
    f = load_still('media/kf/L2.jpg', ctx)
    T = ctx.cache('L2_page', page_tex, deps=['work/heaven/ledger/spread_7_8.png'])
    Tw, reg = warp_layer_quad(T, PAGE, ctx)
    hm = np.zeros((ctx.H, ctx.W), np.uint8)               # her hand, sleeve and cuff are not page
    poly = [(380, 330), (560, 60), (1000, 80), (1215, 360), (1200, 540), (1130, 560), (880, 470), (770, 500),
            (745, 640), (690, 640), (600, 560), (470, 640), (380, 520)]
    cv2.fillPoly(hm, [np.int32(np.float32(poly) * ctx.s)], 1)
    m = paper_mask(f, soften(reg, ctx, 2), warm=False, lo=0.45, soft=0.10, sat=(0.22, 0.34))
    m *= 1 - soften(hm.astype(F32), ctx, 4)
    f = lay_page(f, Tw, m, 0.95)
    fld = bed_field(ctx, POOL, 230, faces=[(1050, 330, 260, 190, 0.40)], amb=0.36, tilt=8, stretch=1.45, key='L2')
    f = bed_grade(f, ctx, POOL, 230, field=fld)
    BASE = paper_fibre(f, P, 0.55)
    YY, XX = np.mgrid[0:ctx.H, 0:ctx.W].astype(F32)


def render(t, ctx):
    k = frame_of(T1) - frame_of(t)                    # frames left (1 = last frame)
    p = 0.0 if k > N_PRESS else ease((N_PRESS - k + 1) / N_PRESS, 'in')
    if p <= 0:
        return BASE.copy()
    s = ctx.s
    r = 30 * s
    w = np.exp(-(((XX - THUMB[0] * s) ** 2 + (YY - THUMB[1] * s) ** 2) / (2 * r * r)))
    mx = (XX - PRESS[0] * s * p * w).astype(F32)
    my = (YY - PRESS[1] * s * p * w).astype(F32)
    return cv2.remap(BASE, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

"""L2 (233.208-235.833) Jade's thumb on the flashlight switch; the white pool on the blank column.  ROOMS-26.

Polish-1: new keyframe (media/kf/L2.jpg, nbp, composition in words; the rooms-26 pick with its long dark bar and the
thumb beside the switch is kept as media/kf/alt/L2_rooms26_pick.jpg). The hand, the muted-orange torch and the thumb ON
its switch sit in the lower-right third; behind them the page of the ledger (E_ledger p8 via spread_7_8) is multiplied
on, shifted so its bare last column runs through the pool. ONE thing moves: in the last 6 frames the thumb presses in
(about 4 px at 540p, a local warp) and the pool of light trembles once as the switch gives. The shot ends LIT: the
click to black at 235.833 is the first frame of L3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field

T0, T1 = 233.20833333333334, 235.83333333333334
PAGE = [(67, 269), (1258, -10), (1661, 576), (490, 1046)]     # right-hand page, measured on L2.jpg (TL TR BR BL)
POOL = (630, 390)                                             # pool centre (page u ~0.31)
THUMB = (1075, 575)                                           # thumb pad on the switch (1080p px)
PRESS = (-4.5, 7.5)                                           # the pad presses down into the torch (1080p px, ~4.4 px at 540p)
N_PRESS = 6
Z, CX, CY = 1.30, 870, 462        # comp reframe (1080p px): the thumb on its switch lands in the lower-right third
HAND = [(555, 345), (610, 292), (660, 320), (700, 370), (800, 362), (900, 380), (990, 430), (1085, 495), (1280, 480),
        (1280, 720), (950, 720), (860, 605), (760, 600), (700, 560), (650, 500), (645, 470), (600, 410)]   # 1280x720 px


def page_tex():
    sp = load_image(os.path.join(ROOT, 'work/heaven/ledger/spread_7_8.png'))
    pg = sp[:, :2200]
    pg = cv2.resize(pg, (1100, 1650), interpolation=cv2.INTER_AREA)
    g = np.median(pg.reshape(-1, 3), axis=0)
    T = np.clip(pg / g, 0, 1)
    # shift the page right so the bare column (x 0.10-0.19) runs through the pool (u ~0.31 of the quad)
    sh = 235
    T = np.concatenate([np.ones((T.shape[0], sh, 3), F32), T[:, :-sh]], 1)
    return (1 - 0.80 * (1 - T)).astype(F32)


class _Big:
    """The keyframe is built Z times larger than the frame, then cropped (the reframe keeps full detail)."""

    def __init__(self, ctx):
        self.W, self.H, self.s, self.cache = int(round(ctx.W * Z)), int(round(ctx.H * Z)), ctx.s * Z, ctx.cache
        self.x0 = int(round(CX * self.s - ctx.W / 2))
        self.y0 = int(round(CY * self.s - ctx.H / 2))


def setup(ctx0):
    global BASE, P, YY, XX, POOLM, BIG
    ctx = BIG = _Big(ctx0)
    P = Paper(ctx.W, ctx.H, 'aged', seed=35)
    f = load_still('media/kf/L2.jpg', ctx)
    T = ctx.cache('L2_page_p1', page_tex, deps=['work/heaven/ledger/spread_7_8.png'])
    Tw, reg = warp_layer_quad(T, PAGE, ctx)
    hm = np.zeros((ctx.H, ctx.W), np.uint8)               # hand, torch and sleeve are not page
    cv2.fillPoly(hm, [np.int32(np.float32(HAND) * 1.5 * ctx.s)], 1)
    hand = soften(hm.astype(F32), ctx, 3)
    m = paper_mask(f, soften(reg, ctx, 2), warm=False, lo=0.30, soft=0.12, sat=(0.22, 0.34))
    m *= 1 - hand
    f = lay_page(f, Tw, m, 0.92)
    fld = bed_field(ctx, POOL, 380, faces=[(1230, 700, 420, 300, 0.62)], amb=0.40, tilt=-20, stretch=1.25, key='L2p1')
    f = bed_grade(f, ctx, POOL, 380, field=fld)
    BASE = paper_fibre(f, P, 0.55)
    YY, XX = np.mgrid[0:ctx.H, 0:ctx.W].astype(F32)
    L = luma(BASE)
    POOLM = (smoothstep(0.45, 0.75, cv2.GaussianBlur(L, (0, 0), 6 * ctx.s)) * (1 - hand)).astype(F32)


def render(t, ctx0):
    ctx = BIG
    k = frame_of(T1) - frame_of(t)                    # frames left (1 = last frame)
    f = _render(k, ctx)
    return f[ctx.y0:ctx.y0 + ctx0.H, ctx.x0:ctx.x0 + ctx0.W].copy()


def _render(k, ctx):
    if k > N_PRESS:
        return BASE
    s = ctx.s
    p = ease((N_PRESS - k + 1) / N_PRESS, 'inout')
    r = 46 * s
    w = np.exp(-(((XX - THUMB[0] * s) ** 2 + (YY - THUMB[1] * s) ** 2) / (2 * r * r)))
    mx = (XX - PRESS[0] * s * p * w).astype(F32)
    my = (YY - PRESS[1] * s * p * w).astype(F32)
    f = cv2.remap(BASE, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # the pool trembles once as the switch gives (frames 3 and 2 from the end): a small jump and dip, then settles
    tr = {3: (3.0, -2.0, 0.90), 2: (-1.5, 1.0, 0.95)}.get(k)
    if tr:
        dx, dy, g = tr
        Mt = np.float32([[1, 0, dx * s], [0, 1, dy * s]])
        a1 = cv2.warpAffine(POOLM, Mt, (ctx.W, ctx.H), borderMode=cv2.BORDER_CONSTANT)
        # the light (not the page) moves: dim the pool, and its rim slides a few px
        f = f * (1 - (1 - g) * a1)[..., None] * (1 + 0.35 * (a1 - POOLM))[..., None]
    return f

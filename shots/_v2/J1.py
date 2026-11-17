"""J1 (189.792-190.875) four stuttered crashes 189.805 / .867 / .922 / .972: the daughter's fingertip on a carved
character; it lights; four hard flashes: page / rubbing / mis-registered / page.  ROOMS-26.

Base: Kling take of J1.jpg (the fingertip presses and stays), on twos. Page art: team HEAVEN's J1_page.png (花果山 with
千字文 lines 1-80 cut in, all on the left page); the marked character 草 is placed under the fingertip (the page is
shifted on its leaf so its (0.383, 0.788) lands at the fingertip's (0.633, 0.557) of the painted left-page quad).
The lit state is HEAVEN's J1_page_charlit.png (low warm raking light catching the cut, fuller cinnabar: not a glow),
taken in over 5 frames after the last crash. Flashes: one frame each on the first frame at/after each crash, the flat
page full-frame (framed on 草): the page / its rubbing (tools.ink.rubbing) / mis-registered (woodblock.misregister) /
the page; between and after them, the room.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field
from tools.ink.rubbing import Rubbing
from tools.ink.woodblock import misregister
from tools.ink.light import flashlight_field

T0, T1 = 189.79166666666666, 190.875
CRASH = [189.805, 189.867, 189.922, 189.972]
LEFT = [(295, 205), (1091, -153), (1500, 915), (640, 1015)]     # painted left page on the clip (TL TR BR BL)
SHIFT = (0.250, -0.258)                                        # page-uv shift that puts 草 under the fingertip
LIT_T = (190.00, 190.21)                                       # the cut catches the light


def leftpage(path):
    a = load_image(os.path.join(ROOT, path))[:, :1696]
    g = np.median(a[100:-100, 100:600].reshape(-1, 3), axis=0)
    T = np.clip(a / g, 0, 1).astype(F32)
    h, w = T.shape[:2]
    M = np.float32([[1, 0, SHIFT[0] * w], [0, 1, SHIFT[1] * h]])
    T = cv2.warpAffine(T, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    k = 1100 / w
    return cv2.resize(T, (1100, int(h * k)), interpolation=cv2.INTER_AREA).astype(F32)


def flat_page(ctx):
    """The spread flat and full-frame, framed on 草, torch-lit: what the flashes show."""
    a = load_image(os.path.join(ROOT, 'media/comp/pages/J1_page.png'))
    cx, cy = 649, 1406
    s = 1.55 * ctx.s                                            # page px -> frame px
    x0, y0 = cx - ctx.W / 2 / s, cy - ctx.H * 0.55 / s
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    sm = a if s >= 1 else a
    f = cv2.warpAffine(sm, M, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(F32)
    I = flashlight_field(ctx.W, ctx.H, (ctx.W / 2, ctx.H * 0.55), 700 * ctx.s, 0, 1.3, 4, spill=0.0)
    I = np.clip(I / np.percentile(I, 99.5), 0, 1)
    L = 0.30 + 0.70 * I[..., None]
    return np.clip(f * L, 0.012, 0.985).astype(F32), f


def setup(ctx):
    global B, P, PT, PL, REG, FLD, FLAT, RUB, MIS
    B, _ = base_for('J1', 'media/kf/J1.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=36)
    T = ctx.cache('J1_left', lambda: leftpage('media/comp/pages/J1_page.png'), deps=['media/comp/pages/J1_page.png'])
    TL = ctx.cache('J1_leftlit', lambda: leftpage('media/comp/pages/J1_page_charlit.png'),
                   deps=['media/comp/pages/J1_page_charlit.png'])
    PT, REG = warp_layer_quad(T, LEFT, ctx)
    PL, _ = warp_layer_quad(TL, LEFT, ctx)
    hm = np.zeros((ctx.H, ctx.W), np.uint8)       # the daughter's hand and the sleeves (pale: not separable by colour)
    for poly in ([(930, 700), (950, 535), (995, 530), (1040, 590), (1065, 578), (1115, 582), (1155, 578), (1205, 595),
                  (1230, 720), (1250, 800), (1330, 880), (1520, 940), (1520, 1080), (1090, 1080), (995, 820), (990, 715)],
                 [(600, 1080), (690, 880), (790, 790), (960, 790), (1060, 870), (1070, 1080)]):
        cv2.fillPoly(hm, [np.int32(np.float32(poly) * ctx.s)], 1)
    hm = cv2.dilate(hm, np.ones((int(3 * ctx.s) | 1,) * 2, np.uint8))
    REG = soften(REG, ctx, 2) * (1 - soften(hm.astype(F32), ctx, 3))
    FLD = bed_field(ctx, (1150, 420), 560, faces=[], amb=0.40, stretch=1.1, key='J1')
    FLAT, unlit = flat_page(ctx)
    RUB = Rubbing(ctx.W, ctx.H, seed=4).apply(FLAT.copy(), paper=None)
    MIS = misregister(FLAT.copy(), CRASH[2], [CRASH[2]], amount=9, paper=None, seed=3)


def flash_at(t):
    """Index of the crash whose first frame is t (frame rule ceil), else None."""
    for k, c in enumerate(CRASH):
        if frame_of(t) == frame_of(c):
            return k
    return None


def render(t, ctx):
    k = flash_at(t)
    if k is not None:
        return [FLAT, RUB, MIS, FLAT][k].copy()
    f = B.at(t)
    m = paper_mask(f, REG, warm=False, lo=0.40, soft=0.10, sat=(0.20, 0.32))
    lit = ramp(t, LIT_T[0], LIT_T[1], 'out')
    T = PT * (1 - lit) + PL * lit
    f = lay_page(f, T, m, 0.95)
    f = bed_grade(f, ctx, (1150, 420), 560, field=FLD)
    return paper_fibre(f, P, 0.5)

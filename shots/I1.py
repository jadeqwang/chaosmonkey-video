"""I1 (177.208-180.208) 'Mischievous baby, Monkey's twin'.  ROOMS-26.

2026, the dark bedroom: Jade on the floor against the bed sings (sd25 lip-sync, first+last frame I1 -> I1_end); the
daughter on her tummy reaches out and her fingertip finds little Jade's crayon monkey in the page margin.
Comp: the 花果山 page (B_master keyed onto the worn book's aged page) mapped onto the painted page (quad measured on
the keyframe, not the sidecar), the crayon monkey (A_crayon_monkey_rgba) in the outer margin where the finger lands;
bedroom grade (one white pool on the page; the light the keyframe threw on her jacket is crushed); paper fibre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field

T0, T1 = 177.20833333333334, 180.20833333333334
PAGE = [(322, 662), (790, 708), (925, 885), (600, 837)]     # the painted visible page, TL TR BR BL (far-left first)
POOL = (650, 770)
FACES = [(800, 330, 120, 150, 0.80), (1125, 585, 95, 105, 0.80), (530, 425, 40, 40, 0.9)]


def page_tex():
    src = load_image(os.path.join(ROOT, 'design/plates/A_book/A_open_worn.png'))
    pg = src[314:2733, 455:2738]                                 # the left page of the worn book (aged paper)
    pg = cv2.resize(pg, (1400, int(pg.shape[0] * 1400 / pg.shape[1])), interpolation=cv2.INTER_AREA)
    g = np.median(pg[200:-200, 200:-200].reshape(-1, 3), axis=0)
    T = 1 - 0.7 * (1 - np.clip(pg / g, 0, 1))
    H, W = T.shape[:2]
    art = load_image(os.path.join(ROOT, 'design/plates/B_huaguoshan/B_master.png'))
    art = art[:, :1900]                                          # the mountain half of the plate
    Ta = key_paper(art, gain=1.1)
    aw = int(W * 0.92); ah = int(aw * Ta.shape[0] / Ta.shape[1])
    Ta = cv2.resize(Ta, (aw, ah), interpolation=cv2.INTER_AREA)
    y0 = int(H * 0.06); x0 = int(W * 0.04)
    ah2 = min(ah, H - y0)
    T[y0:y0 + ah2, x0:x0 + aw] *= Ta[:ah2]
    # crayon monkey, wax multiplied, in the outer (right) margin low on the page
    cr = load_image(os.path.join(ROOT, 'design/plates/A_book/A_crayon_monkey_rgba.png'), alpha=True)
    cw = int(W * 0.17); chh = int(cw * cr.shape[0] / cr.shape[1])
    cr = cv2.resize(cr, (cw, chh), interpolation=cv2.INTER_AREA)
    cx0, cy0 = int(W * 0.80), int(H * 0.50)
    a = cr[..., 3:4]
    T[cy0:cy0 + chh, cx0:cx0 + cw] *= (1 - a + a * np.clip(cr[..., :3], 0, 1))
    return T.astype(F32)


def setup(ctx):
    global B, P, PT, REG, FLD, WORDS
    B, _ = base_for('I1', 'media/kf/I1.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=27)
    T = ctx.cache('I1_page', page_tex, deps=['design/plates/B_huaguoshan/B_master.png'])
    PT, REG = warp_layer_quad(T, PAGE, ctx)
    REG = soften(REG, ctx, 2)
    FLD = bed_field(ctx, POOL, 300, FACES, amb=0.34, tilt=10, stretch=1.35, key='I1')
    WORDS = words_of(ctx, 'Mischievous baby', 176.0)


def render(t, ctx):
    f = B.at(t)
    m = paper_mask(f, REG, warm=False, lo=0.30, soft=0.10, sat=(0.30, 0.42))
    f = lay_page(f, PT, m, 0.95)
    f = bed_grade(f, ctx, POOL, 300, field=FLD)
    f = paper_fibre(f, P, 0.55)
    lyric(f, ctx, sung(WORDS, t, tail=0.7), x=0.63, y=0.10, px=26)
    return f

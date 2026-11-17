"""I1 (177.208-180.208) 'Mischievous baby, Monkey's twin'.  ROOMS-26.

2026, the dark bedroom: Jade on the floor against the bed sings (sd25 lip-sync, first+last frame I1 -> I1_end); the
daughter on her tummy reaches out and her fingertip finds little Jade's crayon monkey in the page margin.
Comp: the 花果山 page (B_master keyed onto the worn book's aged page) mapped onto the painted page (quad measured on
the keyframe, not the sidecar), the crayon monkey (A_crayon_monkey_rgba) in the outer margin where the finger lands;
bedroom grade (one white pool on the page; the light the keyframe threw on her jacket is crushed); paper fibre.

Fix round 2 (QA item 11): no grey dissolve. Frame 0 (the kick 177.193) is H6's bare paper, full frame (the same
sheet: Paper 'new', BOOK_PAPER_SEED). From frame 1 that paper is a torch pool: a hard-edged ellipse of light, there
within 2 frames, its edges falling off into darkness over ~10 frames while the room outside appears dim by the
light's falloff (no second image fading in); then the camera pulls back (x2.5 -> 1) to the I1 framing, the pool
shrinking onto the real page. The torch head's painted glow halo is taken off (_bed_grade.dehalo: a pale lens).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field, dehalo, find_lens
from shots._mountain import BOOK_PAPER_SEED

T0, T1 = 177.20833333333334, 180.20833333333334
PAGE = [(313, 622), (772, 662), (872, 792), (600, 832)]     # the visible page measured on the CLIP (sd25 reframed frame 0 ~40 px up from I1.jpg), TL TR BR BL
POOL = (650, 770)
FACES = [(800, 330, 150, 190, 0.62), (1150, 590, 150, 140, 0.52), (530, 425, 40, 40, 0.9)]


def page_tex():
    src = load_image(os.path.join(ROOT, 'design/plates/A_book/A_open_worn.png'))
    pg = src[314:2733, 455:2738]                                 # the left page of the worn book (aged paper)
    pg = cv2.resize(pg, (1400, int(pg.shape[0] * 1400 / pg.shape[1])), interpolation=cv2.INTER_AREA)
    g = np.median(pg[200:-200, 200:-200].reshape(-1, 3), axis=0)
    T = 1 - 0.7 * (1 - np.clip(pg / g, 0, 1))
    H, W = T.shape[:2]
    art = load_image(os.path.join(ROOT, 'design/plates/B_huaguoshan/B_master.png'))
    art = art[:, :2300]                                          # the mountain half of the plate
    Ta = key_paper(art, gain=1.25)
    # only the band of the page above her knee is visible (v 0..0.32 of the quad): the painting sits there
    ah = int(H * 0.55); aw = int(ah * Ta.shape[1] / Ta.shape[0])
    Ta = cv2.resize(Ta, (aw, ah), interpolation=cv2.INTER_AREA)
    x0, y0 = int(W * 0.03), int(H * 0.0)
    T[y0:y0 + ah, x0:x0 + aw] *= Ta
    # crayon monkey, wax multiplied, in the outer (right) margin where her fingertip lands in I1_end
    cr = load_image(os.path.join(ROOT, 'design/plates/A_book/A_crayon_monkey_rgba.png'), alpha=True)
    cw = int(W * 0.21); chh = int(cw * cr.shape[0] / cr.shape[1])
    cr = cv2.resize(cr, (cw, chh), interpolation=cv2.INTER_AREA)
    cx0, cy0 = int(W * 0.75), int(H * 0.27)
    a = cr[..., 3:4]
    T[cy0:cy0 + chh, cx0:cx0 + cw] *= (1 - a + a * np.clip(cr[..., :3], 0, 1))
    return T.astype(F32)


LENS_BOX = (400, 300, 700, 520)                               # where the torch head sits (1080p px)
ZS, K_ON, K_POOL, K_BACK = 2.5, 1, 10, 26                     # close-up zoom; torch on; pool settled; back at I1
POOL_R = (1012, 750)                                          # pool radii on screen at ZS (1080p px): 405x300 at x1
LIT = (600, 630)                                              # the lit page in the clip (1080p px): the pool lands here


def setup(ctx):
    global B, P, PT, REG, FLD, WORDS, TR, CLIP, PB
    PB = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)     # H6's sheet
    B, CLIP = base_for('I1', 'media/kf/I1.jpg', ctx)
    TR = track_affine(B, (300, 600, 960, 900), ctx) if CLIP else None
    P = Paper(ctx.W, ctx.H, 'aged', seed=27)
    T = ctx.cache('I1_page', page_tex, deps=['design/plates/B_huaguoshan/B_master.png'])
    PT, REG = warp_layer_quad(T, PAGE, ctx)
    REG = soften(REG, ctx, 2)
    FLD = bed_field(ctx, POOL, 300, FACES, amb=0.34, tilt=10, stretch=1.35, key='I1')
    WORDS = words_of(ctx, 'Mischievous baby', 176.0)


def plate(t, ctx):
    f = B.at(t)
    pt, reg = PT, REG
    if TR is not None:
        A = TR[B.index(t)]
        pt, reg = apply_affine(PT, A, ctx, 1.0), apply_affine(REG, A, ctx, 0.0)
    m = paper_mask(f, reg, warm=False, lo=0.30, soft=0.10, sat=(0.30, 0.42))
    f = lay_page(f, pt, m, 0.95)
    f = bed_grade(f, ctx, POOL, 300, field=FLD)
    f = dehalo(f, ctx, find_lens(f, ctx, LENS_BOX), R=120)
    return paper_fibre(f, P, 0.55)


_YX = {}


def pool_mask(ctx, rx, ry, cx=960, cy=540):
    key = (ctx.W, ctx.H)
    if key not in _YX:
        _YX[key] = np.mgrid[0:ctx.H, 0:ctx.W].astype(F32) / ctx.s
    yy, xx = _YX[key]
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    th = np.arctan2(yy - cy, xx - cx)
    d = d * (1 + 0.012 * np.sin(5 * th + 1.3) + 0.008 * np.sin(11 * th))   # a reflector's slightly uneven rim
    e = 4.0 / max(min(rx, ry), 1)                              # a hard edge: ~4 px at 1080p
    m = np.clip((1 + e - d) / (2 * e), 0, 1)
    light = 0.84 + 0.16 * np.exp(-(d / 0.55) ** 2)             # the torch's core on the paper, falling to the rim
    return m.astype(F32)[..., None], light.astype(F32)[..., None]


def render(t, ctx):
    k = frame_of(t) - frame_of(T0)
    if k < K_ON:
        f = PB.frame(t)                                        # the bare paper H6 ended on
    else:
        base = plate(t, ctx)
        if k < K_BACK:
            if k <= K_POOL:                                    # the camera holds close on the pool
                z = ZS
                u = (k - K_ON) / (K_POOL - K_ON)
                g = 1.00 - 0.18 * ease(u, 'out')               # the paper's edges fall off into darkness
                rx, ry = POOL_R[0] * g, POOL_R[1] * g
                wp, dim = 1.0, (0.22 if k == K_ON else 0.45)   # torch on: the dark is there within 2 frames
            else:                                              # the pull-back to the I1 framing
                u = ease((k - K_POOL) / (K_BACK - K_POOL), 'inout')
                z = math.exp(math.log(ZS) * (1 - u))
                rx, ry = POOL_R[0] * 0.82 * z / ZS, POOL_R[1] * 0.82 * z / ZS
                wp = 1.0 - min(1.0, (k - K_POOL) / 2.0)          # the paper is the page: its detail comes up
                dim = 0.45 + 0.55 * u
            # zoom about the fixed point Q that puts the pool centre mid-frame at ZS and is the identity at x1
            qx, qy = [(c0 - ZS * p) / (1 - ZS) for c0, p in ((960, LIT[0]), (540, LIT[1]))]
            room = move(base, ctx, z, qx + (960 - qx) / z, qy + (540 - qy) / z)
            pm, light = pool_mask(ctx, rx, ry, qx + z * (LIT[0] - qx), qy + z * (LIT[1] - qy))
            lit = light * (1 - u) + u if k > K_POOL else light
            inside = (PB.frame(t) * wp + room * (1 - wp)) * lit
            pm = pm * (1 - u) if k > K_POOL else pm               # the hard pool hands over to the room's own pool
            f = inside * pm + room * dim * (1 - pm)
        else:
            f = base
    lyric(f, ctx, sung(WORDS, t, tail=0.7), x=0.63, y=0.10, px=26)
    return f

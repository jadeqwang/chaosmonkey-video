"""K1 (203.708-210.542) 'Do you want to know how he never died, / what he did on the other side?'  ROOMS-26.

Jade, softly, sings (sd25 lip-sync, first+last frame K1 -> K1_end); she lifts the page corner and turns the page toward
the last chapter; the daughter nods. Comp: the heaven spread (team HEAVEN's I2_page) on the open book until the leaf
passes its midpoint, then the underworld painting (E_king_desk: the king at his desk, the scribe, the ledger) on the
new spread. Page quads measured on the clip's first and last frames (the book drifts ~25 px: interpolated).
Bedroom grade: one white pool on the page, faces by bounce light.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field, dehalo, find_lens

T0, T1 = 203.70833333333334, 210.54166666666666
Q0 = np.float32([(530, 548), (895, 688), (750, 785), (320, 615)])    # spread on clip frame 0 (TL far-left, TR, BR, BL)
Q1 = np.float32([(540, 537), (935, 655), (790, 788), (348, 592)])    # on the last frame
FLIP = 158                                                             # clip frame where the leaf passes upright
POOL = (640, 660)
FACES = [(870, 300, 150, 190, 0.62), (1090, 640, 150, 150, 0.52), (530, 330, 40, 40, 0.9)]


def tex(path, rows=None):
    a = load_image(os.path.join(ROOT, path))
    if rows:
        a = a[rows[0]:rows[1]]
    T = key_paper(a, gain=1.15)
    w = 1600
    T = cv2.resize(T, (w, int(w / 1.9)), interpolation=cv2.INTER_AREA)            # the spread's aspect
    sp, _ = spread_texture(None, crayon=False, max_w=w)
    sp = cv2.resize(sp, (w, int(w / 1.9)), interpolation=cv2.INTER_AREA)
    return (T * sp).astype(F32)


def setup(ctx):
    global B, CLIP, P, TA, TB, FLD, W1, W2
    B, CLIP = base_for('K1', 'media/kf/K1.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=28)
    TA = ctx.cache('K1_heaven', lambda: tex('media/comp/pages/I2_page.png'), deps=['media/comp/pages/I2_page.png'])
    TB = ctx.cache('K1_underworld', lambda: tex('design/plates/E_underworld/E_king_desk.png', (300, 3400)),
                   deps=['design/plates/E_underworld/E_king_desk.png'])
    FLD = bed_field(ctx, POOL, 290, FACES, amb=0.34, tilt=-20, stretch=1.4, key='K1')
    W1 = words_of(ctx, 'Do you want to know', 203.7)
    W2 = words_of(ctx, 'what he did on the other side', 207.2)


def render(t, ctx):
    f = B.at(t)
    i = B.index(t)
    u = i / max(B.n - 1, 1)
    q = Q0 * (1 - u) + Q1 * u
    T = TA if i < FLIP else TB
    pt, reg = warp_layer_quad(T, q, ctx)
    m = paper_mask(f, soften(reg, ctx, 2), warm=False, lo=0.30, soft=0.10, sat=(0.30, 0.42))
    f = lay_page(f, pt, m, 0.92)
    f = bed_grade(f, ctx, POOL, 290, field=FLD)
    f = dehalo(f, ctx, find_lens(f, ctx, (430, 250, 640, 440)), R=110)     # fix2: the torch head has no glow halo
    f = paper_fibre(f, P, 0.55)
    txt = sung(W1, t, tail=0.5) if t < 207.19 else sung(W2, t, tail=0.6)
    lyric(f, ctx, txt, x=0.64, y=0.10, px=26)
    return f

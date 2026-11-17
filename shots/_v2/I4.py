"""I4 (187.0-189.79) 'Wouldn't you? You're able.'  ROOMS-26.

Three parts, cut on measured events (analysis/timing.json):
  I4a  187.000-187.500  Jade's face dead centre (second centred face). Mama 1988 (red, sceptical) over it at 70 % for the
                        first 8 frames, then gone in a hard 2-frame step (a ghost, not a dissolve). Under the ghost Mama
                        "asks" Wouldn't you?.
  I4b  187.500-188.417  the banquet page; on the four low drum hits 187.46 (the cut lands on it), 187.781, 188.097,
                        188.313 the daughter's small hand-shadow monkey climbs onto the EMPTY chair in four hard re-poses
                        and sits. Ends on the drum dropout (188.415).
  I4a  188.417-189.79   back to Jade, certain, singing "You're able." (lip-sync, sd25), to the end of the shot.
(The brief put I4b in the last ~1.4 s, but the measured hits are 187.46-188.31: the hits win.)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field, desat_hue
from tools.ink.light import flashlight_field

T0, T1 = 187.0, 189.79166666666666
CUT_B, CUT_C = 187.5, 188.41666666666666         # first frames of I4b and of the return to I4a
HITS = [187.46, 187.781, 188.097, 188.313]
SPREAD = [(328, 173), (1592, 173), (1538, 962), (382, 962)]   # I4b keyframe page quad (TL TR BR BL), 1080p px
POOL = (975, 600)


def setup(ctx):
    global GH, JADE, MAMA, P, PB, PAGE_T, PAGE_M, FB, SIL, CHAIR, POSES, LB, WORDS, FA
    JADE, _ = base_for('I4', 'media/kf/I4a.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=26)
    # Mama ghost: graded red, flattened, on our paper
    m = load_still('media/kf/I4_mama.jpg', ctx)
    MAMA = paper_fibre(flatten(m, ctx, 0.5), P, 0.6)
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(F32)
    d = ((xx - 960 * ctx.s) / (300 * ctx.s)) ** 2 + ((yy - 560 * ctx.s) / (420 * ctx.s)) ** 2
    GH = soften((d < 1).astype(F32), ctx, 40)                   # Mama's face (not her hair or the red ground)
    # face grade: underlight pool at the chin, the face kept by bounce light, the hair and wall to violet
    FA = bed_field(ctx, (960, 1010), 520, faces=[(960, 560, 330, 470, 0.80)], amb=0.22, stretch=1.4, key="I4a")   # polish-1: the new take paints a cream ground: amb 0.34 -> 0.22

    # ---- I4b: the banquet page on the spread
    PB = load_still('media/kf/I4b.jpg', ctx)
    def build():
        T, A = spread_art('design/plates/D_heaven/D_banquet.png', (0.232, -0.20, 1.032, 0.81), gain=1.0)
        return T, A
    T, A = ctx.cache('I4b_banquet', build, deps=['design/plates/D_heaven/D_banquet.png'])
    Hm = quad_H(T.shape, SPREAD, ctx)
    Tw, qm = warp_layer_quad(T, SPREAD, ctx)
    region = qm * (1 - soften((np.mgrid[0:ctx.H, 0:ctx.W][0] > 930 * ctx.s).astype(F32), ctx, 6))
    # hands: the daughter's (lower left) and Jade's (right edge) are not paper: static polygons from the keyframe
    hm = np.zeros((ctx.H, ctx.W), np.uint8)
    for poly in ([(370, 1080), (420, 880), (520, 790), (640, 700), (740, 715), (720, 780), (690, 840), (560, 940), (470, 1080)],
                 [(1500, 1080), (1520, 600), (1560, 470), (1660, 520), (1760, 700), (1920, 820), (1920, 1080)]):
        cv2.fillPoly(hm, [np.int32(np.float32(poly) * ctx.s)], 1)
    hands = soften(hm.astype(F32), ctx, 3)
    PAGE_M = (region * (1 - hands)).astype(F32)
    PAGE_T = Tw
    base = lay_page(PB, PAGE_T, PAGE_M, 0.92)
    base = desat_hue(base, 330, 25, 0.55, PAGE_M)          # the lacquer red: only pink and orange are saturated in 2026
    LB = flashlight_field(ctx.W, ctx.H, (POOL[0] * ctx.s, POOL[1] * ctx.s), 360 * ctx.s, 0, 1.05, 3, spill=0.0)
    LB = np.clip(LB / np.percentile(LB, 99.5), 0, 1).astype(F32)
    FB = bed_grade(base, ctx, POOL, 380, faces=[(560, 860, 160, 160, 0.30), (1650, 700, 180, 260, 0.30)], amb=0.36, key='I4b')
    FB = paper_fibre(FB, P, 0.5)
    # the empty chair in frame px (art bbox 1345,1351-1787,1985 in D_banquet px)
    c0 = map_pt(Hm, A, (1345, 1351)); c1 = map_pt(Hm, A, (1787, 1985))
    CHAIR = (c0[0] / ctx.s, c0[1] / ctx.s, c1[0] / ctx.s, c1[1] / ctx.s)
    SIL = silhouette('design/characters/monkey/handshadow_silhouette.jpg')
    x0, y0, x1, y1 = CHAIR
    cw, ch = x1 - x0, y1 - y0
    sz = ch * 0.85
    seat_y = y0 + ch * 0.52                       # the seat line of a chair seen from slightly above
    # (cx, cy, height, angle): floor beside the chair -> the front leg -> the seat edge -> sitting on the seat
    POSES = [(x0 - cw * 0.55, y1 - sz * 0.45, sz * 0.92, 18),
             (x0 + cw * 0.05, y1 - ch * 0.38, sz * 0.95, -28),
             (x0 + cw * 0.40, seat_y - sz * 0.15, sz, -8),
             (x0 + cw * 0.50, seat_y - sz * 0.42, sz, 0)]
    WORDS = words_of(ctx, "Wouldn't you", 187.0)


def face(t, ctx):
    f = JADE.at(t)
    f = flatten(f, ctx, 0.45)                       # lead note: I4a read photographic; flatten toward line + wash
    f = f * FA
    f = paper_fibre(np.clip(f, 0.012, 0.985), P, 0.6)
    return f


def render(t, ctx):
    k = frame_of(t) - frame_of(T0)                 # frame index within the shot
    if t < CUT_B - 1e-6:
        f = face(t, ctx)
        op = 0.70 if k < 8 else (0.35 if k == 8 else 0.0)
        if op > 0:
            # fix round 2 (QA item 7): a ghost OVER Jade, not a full-frame cut. Mama's face (registered on Jade's) at
            # `op`, her hair and red ground only faintly; Jade's own dark lines (eyes, glasses, mouth, hair) read
            # through from frame 0.
            a = (op * (GH + (1 - GH) * 0.30))[..., None]
            g = f * (1 - a) + MAMA * a
            f = np.minimum(g, f * 1.04 + 0.14 * (1 - op / 0.70 * 0.3))
    elif t < CUT_C - 1e-6:
        f = FB.copy()
        i = sum(1 for h in HITS if t >= h - 1e-6) - 1
        cx, cy, h, ang = POSES[max(i, 0)]
        m = place_mask(SIL, ctx, cx, cy, h, flip=True, angle=ang)
        S = soften(m, ctx, 2.2) * (0.25 + 0.75 * LB)
        f = shadow_on(f, S, 0.80)
    else:
        f = face(t, ctx)
    txt = sung(WORDS, t, tail=0.6)
    if txt and not (CUT_B <= t < CUT_C):
        lyric(f, ctx, txt, x=0.5, y=0.958, px=24, opacity=0.8)
    return f

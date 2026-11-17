"""I2 (180.208-182.958) 'you'd fight the gods and win'.  ROOMS-26.

Jade's eyeline into the spread: the heaven painting (team HEAVEN's I2_page.png, 青绿) on the pages; Jade's monkey-head
hand shadow is already on the right page; on "fight" (180.71) the daughter's smaller, identical one pops up on the left
page; they face each other and bob on the beats like sparring (hard re-poses on 180.758 181.205 181.625 182.046 182.466,
no in-betweens). The shadows remove only the torch light (strength x pool). Base: Kling take of I2.jpg (the two hands
work their fingers), on twos. Page art is kept off the hands (warm skin under the torch) and off the sleeves.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field
from tools.ink.light import flashlight_field

T0, T1 = 180.20833333333334, 182.95833333333334
SPREAD = [(328, 173), (1592, 173), (1538, 962), (382, 962)]
POOL = (960, 600)
FIGHT = 180.71
BEATS = [180.758, 181.205, 181.625, 182.046, 182.466]
# (dx, dy, angle) per beat for each shadow: they lean in and out of each other like sparring
JADE_P = [(0, 0, 0), (-14, -10, 6), (8, 6, -4), (-18, -14, 8), (6, 4, -3), (-10, -8, 5)]
GIRL_P = [(0, 0, 0), (12, -8, -6), (-6, 4, 4), (16, -12, -8), (-4, 6, 3), (10, -6, -5)]


def setup(ctx):
    global B, P, PT, REG, FLD, LB, SIL, SLEEVES, WORDS
    B, _ = base_for('I2', 'media/kf/I2.jpg', ctx, twos=True)
    P = Paper(ctx.W, ctx.H, 'aged', seed=39)
    T = ctx.cache('I2_page', lambda: page(), deps=['media/comp/pages/I2_page.png'])
    PT, REG = warp_layer_quad(T, SPREAD, ctx)
    REG = soften(REG, ctx, 2)
    sl = np.zeros((ctx.H, ctx.W), np.uint8)
    for poly in ([(380, 1080), (430, 930), (560, 900), (660, 960), (660, 1080)],
                 [(1110, 880), (1290, 750), (1420, 860), (1600, 1080), (1150, 1080)]):
        cv2.fillPoly(sl, [np.int32(np.float32(poly) * ctx.s)], 1)
    SLEEVES = soften(sl.astype(F32), ctx, 4)
    FLD = bed_field(ctx, POOL, 420, faces=[], amb=0.40, stretch=1.0, key='I2')
    LB = flashlight_field(ctx.W, ctx.H, (POOL[0] * ctx.s, POOL[1] * ctx.s), 430 * ctx.s, 0, 1.0, 5, spill=0.0)
    LB = np.clip(LB / np.percentile(LB, 99.5), 0, 1).astype(F32)
    SIL = silhouette('design/characters/monkey/handshadow_silhouette.jpg')
    WORDS = words_of(ctx, "you'd fight the gods", 180.19)


def page():
    a = load_image(os.path.join(ROOT, 'media/comp/pages/I2_page.png'))
    a = cv2.resize(a, (2200, int(2200 * a.shape[0] / a.shape[1])), interpolation=cv2.INTER_AREA)
    g = np.median(a[:200].reshape(-1, 3), axis=0)
    return np.clip(a / g, 0, 1).astype(F32)


def render(t, ctx):
    f = B.at(t)
    rb = f[..., 0] - f[..., 2]
    mx, mn = f.max(-1), f.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    hand = np.maximum(smoothstep(0.085, 0.105, rb), smoothstep(0.100, 0.125, sat)) * smoothstep(0.45, 0.6, luma(f))
    hand = np.clip(soften(hand.astype(F32), ctx, 5) * 2.2, 0, 1)          # close the holes inside the hands
    m = REG * smoothstep(0.30, 0.45, luma(f)) * (1 - hand) * (1 - SLEEVES)
    f = lay_page(f, PT, m, 0.95)
    f = bed_grade(f, ctx, POOL, 420, field=FLD)
    i = sum(1 for b in BEATS if t >= b - 1e-6)
    S = np.zeros((ctx.H, ctx.W), F32)
    dx, dy, a = JADE_P[i]
    S = np.maximum(S, place_mask(SIL, ctx, 1270 + dx, 345 + dy, 330, flip=True, angle=a))
    if t >= FIGHT - 1e-6:
        dx, dy, a = GIRL_P[i]
        S = np.maximum(S, place_mask(SIL, ctx, 640 + dx, 360 + dy, 260, flip=False, angle=a))
    f = shadow_on(f, soften(S, ctx, 3) * (0.5 + 0.5 * LB) * np.clip(m * 1.5, 0, 1), 0.88)
    f = paper_fibre(f, P, 0.5)
    lyric(f, ctx, sung(WORDS, t, tail=0.6), x=0.5, y=0.07, px=26)
    return f

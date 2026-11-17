"""F6b (120.625-121.458 = F6 frames 2895-2914; F6a by team FACES before it) the daughter and her reflection in the side
window wave at the same instant.  ROOMS-26.

Base: Kling take of F6b.jpg (she waves, deadpan; an amber streetlight passes), its first 0.5 s only, at 0.6x
(after that the model pans the camera), stabilised to its frame 0 (ECC on the cabin) with a 5 % push for the edges. The reflection
is made in code from the same frame: her upper body keyed (colour inside a box around her), mirrored about the window's
right edge, dimmed and cooled, offset a little, laid only inside the side-window pane (measured on the clip), so the two
waves are the same frame: the same instant. Car grade, paper fibre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _car_grade import car_grade

T0, T1 = 120.625, 121.45833333333333
PANE = [(385, 350), (950, 478), (945, 742), (395, 742)]
BOX = (1030, 300, 1490, 730)                  # her head, shoulders and waving hand
AXIS = 1000                                   # mirror axis (x, 1080p px), near the pane's right edge
OFFSET = (-40, 10)


def setup(ctx):
    global B, P, PM, BM, INV
    B, _ = base_for('F6b', 'media/kf/F6b.jpg', ctx)
    # the take drifts (camera pans right and tilts): lock it back to its own frame 0 on the cabin (not on her)
    TR = track_affine(B, (0, 0, 1000, 1080), ctx)
    INV = [cv2.invertAffineTransform(a) for a in TR]
    P = Paper(ctx.W, ctx.H, 'aged', seed=43)
    pm = np.zeros((ctx.H, ctx.W), np.uint8)
    cv2.fillPoly(pm, [np.int32(np.float32(PANE) * ctx.s)], 1)
    PM = soften(pm.astype(F32), ctx, 2)
    bm = np.zeros((ctx.H, ctx.W), F32)
    x0, y0, x1, y1 = [int(v * ctx.s) for v in BOX]
    bm[y0:y1, x0:x1] = 1
    BM = soften(bm, ctx, 25)


def reflection(f, ctx):
    mx, mn = f.max(-1), f.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    key = np.maximum(smoothstep(0.16, 0.26, sat), smoothstep(0.50, 0.65, luma(f))) * BM
    key = soften(key.astype(F32), ctx, 2)
    s = ctx.s
    # mirror about x = AXIS, then offset
    M = np.float32([[-1, 0, 2 * AXIS * s + OFFSET[0] * s], [0, 1, OFFSET[1] * s]])
    rf = cv2.warpAffine(f, M, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
    rk = cv2.warpAffine(key, M, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
    return rf, rk


def render(t, ctx):
    i = B.index(t)
    f = cv2.warpAffine(B.at(t), INV[i], (ctx.W, ctx.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    rf, rk = reflection(f, ctx)
    cool = np.float32([0.82, 0.84, 1.0])
    a = (0.30 * rk * PM)[..., None]
    f = f * (1 - a) + np.maximum(f, rf * cool * 0.85) * a
    f = car_grade(f, ctx, [(1290, 470, 240, 260)], dark=0.66)
    f = move(f, ctx, 1.05, 960, 540)                  # hide the stabiliser's edges
    return paper_fibre(f, P, 0.5)

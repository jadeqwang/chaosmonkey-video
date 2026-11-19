"""The J1 view (top-down LAP_hands): the daughter's fingertip presses a carved character on the page like a lift button
(press 189.620, sound cue) and it lights. Shared by I4.py (the last 10 frames of I4 are already this view, so the press
lands on its cue) and J1.py.  BED+CAR v3, round 3.

Page: the SAME painting J2 opens on (team BOOK, shots/J2.py: the carved blue-green 花果山 peak with the stone on its
summit), rendered from J2's own scene just before its downbeat (no seal, no threads) and laid on the page so that 過, the
character J2's threads start from, sits just above the pressed fingertip. It is multiplied on the take's lit blank paper
and kept off the hand by a paper mask. On the press 過 lights pale gold. The camera closes in to x3 with 過 low in frame,
right of centre, as it is in J2's first frame (there 過 is at 0.59 / 0.98 of the frame), so the cut at 4581 goes from the
finger on the lit character to the same peak full-frame with the threads leaving that character.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T_VIEW = 4545 / 24.0            # 189.375: the picture cuts to this view
T_PRESS = 189.620
TIP = (805, 498)                # where the character sits: just above the pressed fingertip (805, 530), take px at 1080p
CH = (1139.26, 1057.83)         # 過 in J2's first frame (1080p px); the art below uses the same coordinates, extended down
ART_H = 2600                   # J2's frame extended downward to below the book's bottom edge (過 is at the bottom edge in J2)
KA = 0.26                       # take px per art px: the summit stone just clears the book's top edge
Z_END, VIEW_END = 3.0, (747, 390)
GOLD = np.array([1.0, 0.86, 0.48], F32)


def _art(ctx):
    J = importlib.import_module('shots.J2')
    J.setup(ctx)
    x, y, z = J.START
    cam = Camera([(0.0, x, y + (ART_H - 1080) / 2.0 / z, z), (1e4, x, y + (ART_H - 1080) / 2.0 / z, z)])
    img = J.SC_.render(190.70, cam, (1920, ART_H))
    return key_paper(np.asarray(img, F32)).astype(F32)


def setup_j1(ctx):
    global B, P, TL, REG, GLOW
    B = Take('J1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=41)
    T = ctx.cache('j1v3_j2art2600', lambda: _art(ctx), deps=['shots/J2.py', 'design/plates/D_heaven/D_heaven_close.png'])
    if T.shape[1] != 1920:
        T = cv2.resize(T, (1920, ART_H), interpolation=cv2.INTER_AREA)
    s = ctx.s
    A = np.float32([[KA * s, 0, (TIP[0] - KA * CH[0]) * s], [0, KA * s, (TIP[1] - KA * CH[1]) * s]])
    TL = cv2.warpAffine(T, A, (ctx.W, ctx.H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    REG = cv2.warpAffine(np.ones(T.shape[:2], F32), A, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
    REG = soften(REG, ctx, 3)
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(F32)
    r = np.hypot(xx - TIP[0] * s, yy - TIP[1] * s) / (9.0 * s)
    GLOW = np.exp(-0.5 * r * r).astype(F32)


def j1_frame(t, ctx):
    f = B.at(t)
    m = paper_mask(f, REG, warm=False, lo=0.50, soft=0.10, sat=(0.30, 0.42))
    f = lay_page(f, TL, m, 0.95)
    w = float(np.clip((t - T_PRESS) / 0.17, 0, 1))                       # 過 lights as she presses
    if w > 0:
        cut = np.clip((0.80 - TL.mean(-1)) / 0.25, 0, 1)                   # the carved strokes take the gold
        a = (w * GLOW * (0.35 + 0.65 * cut) * m)[..., None]
        f = f * (1 - a) + GOLD * a
    u = ease(float(np.clip((t - T_VIEW) / (190.875 - T_VIEW), 0, 1)), 'inout')
    z = math.exp(math.log(Z_END) * u)
    cx, cy = 960 + (VIEW_END[0] - 960) * u, 540 + (VIEW_END[1] - 540) * u
    f = move(f, ctx, z, cx, cy)
    return fin(f, P)

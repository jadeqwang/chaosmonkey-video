"""K2b (second part of K2, from 212.1 to 213.79) '...the Book of Life and Death'.

The storybook's painting of the underworld (plate E_king_desk: the king at his desk, the scribe with his brush, the
register lying open) on the book's aged 2026 page, under the torch. A slow push in toward the register, easing out so
it is nearly still when K3 cuts to the ledger close. The register's painted pages carry the real ledger (the upper
halves of p2 | p1, the entry 魂字一千三百五十號 on the right page) laid into the painted inner frames in perspective, so
the cut to K3 continues the same page. The bass cut (211.515) falls before this part; the push simply eases.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np

from tools.ink import *
from _heaven import *

T0, T1 = 212.1, 213.79166666666666
PLATE = 'design/plates/E_underworld/E_king_desk.png'
# painted inner frames of the open register, plate px (TL, TR, BR, BL)
QUAD_L = [(2297, 1863), (2579, 1849), (2662, 2050), (2366, 2074)]
QUAD_R = [(2610, 1850), (2891, 1847), (2969, 2054), (2676, 2045)]
CROP = (214, 398, 1986, 1720)          # page px of our ledger laid into each inner frame (upper half of the columns)
START = (2470, 1730, 0.72)
END = (2633, 1955, 1.06)
POOL_W = (2600, 1900, 1150)            # torch pool on the page, plate px (centre, radius)


def page_density(img):
    g = np.median(np.concatenate([img[:300, :300].reshape(-1, 3), img[-200:, -200:].reshape(-1, 3)]), 0)
    T = np.clip(img / g[None, None], 0, 1)
    d = density_of(T)
    return (d * smoothstep(0.10, 0.28, d)).astype(np.float32)


def build(ctx):
    plate = load_image(PLATE)
    H, W = plate.shape[:2]
    T = key_paper(plate)
    pap = Paper(W, H, 'aged', seed=61, scale=1.6)
    for quad, pg in ((QUAD_L, 'E_ledger_p2.png'), (QUAD_R, 'E_ledger_p1.png')):
        q = np.float32(quad)
        m = np.zeros((H, W), np.float32)
        cen = q.mean(0)
        qs = cen + (q - cen) * 0.965                                  # erase the painted rules inside the frame line
        cv2.fillConvexPoly(m, np.round(qs * 4).astype(np.int32), 1.0, lineType=cv2.LINE_AA, shift=2)
        m = blur(m, 1.2)
        T = T * (1 - m[..., None]) + m[..., None]
        d = page_density(load_image(PLATE_LEDGER + pg))
        x0, y0, x1, y1 = CROP
        d = d[y0:y1, x0:x1]
        src = np.float32([[0, 0], [x1 - x0, 0], [x1 - x0, y1 - y0], [0, y1 - y0]])
        # shrink in steps so the warp does not alias the fine strokes
        sc = np.linalg.norm(q[1] - q[0]) / (x1 - x0)
        while sc < 0.5:
            d = cv2.resize(d, (d.shape[1] // 2, d.shape[0] // 2), interpolation=cv2.INTER_AREA)
            src = src / 2
            sc *= 2
        M = cv2.getPerspectiveTransform(src, q)
        dw = cv2.warpPerspective(d, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        T = T * ink_T(np.clip(dw * 0.92, 0, 1))
    return (pap.rgb * T).astype(np.float32)


def setup(ctx):
    global SC_, CAM, WORDS
    img = ctx.cache('k2b_plate_v2', lambda: build(ctx), deps=[PLATE])
    H, W = img.shape[:2]
    class _Sheet:                                   # the composited page as the Scene's paper (mip-mapped, no layers)
        rgb = img
    SC_ = Scene(W, H, paper=_Sheet())
    CAM = Camera([(T0, *START), (T1 + 0.25, *END, 'sine')])   # still moving gently at the cut to K3
    WORDS = line_words(ctx, 'He opened the Book', 210.5)


def render(t, ctx):
    st = CAM.at(t)
    f = SC_.render(t, CAM, ctx.size)
    cx, cy = SC_.to_frame(POOL_W[0], POOL_W[1], st, ctx.size)
    L = light_field(ctx.W, ctx.H, (cx, cy), POOL_W[2] * st[2] * ctx.s, ambient=0.07, gain=1.34, stretch=1.15, seed=31)
    f = lit(f, L)
    lyric(f, ctx, sung_words(WORDS, t, tail=0.1), y=0.955, px=28)
    return f

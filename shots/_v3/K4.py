"""K4 (217.165-224.18) 'I turned each page, I looked for mine'; the beat cuts out at 218.715.

The open register under the torch, held. Three leaves are turned the way a Chinese book turns: the LEFT leaf lifts at its
outer edge and falls over to the right. Each turn is a paper move in code: the leaf is three rigid panels (a slight
curl) rotating about the spine, projected with perspective (each panel a homography), the front face (the page just
read) giving way to its back (the next right page), shaded by its tilt, with a soft shadow on the pages under it.
6 frames per turn on twos (3 drawings); three turns landing on 'page' (218.22), 'looked' (220.92) and the wooden hit 221.805.
No hands (see LOG_heaven.md): the pages turn as if by the reader's unseen hand.
Spreads: (p1 struck, p2) -> (p3, p4) -> (p5, p6) -> (p7, p8 = the last page, final column bare).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math

import cv2
import numpy as np

from tools.ink import *
from _heaven import *

T0, T1 = 217.16666666666666, 224.16666666666666
SC = 0.29                       # page px -> 1080p px
PW, PH, GUT = 2200, 3300, 70    # page size; gutter between pages in a spread
SPW = 2 * PW + GUT
DRAW_THETA = [0.62, 1.62, 2.62]  # radians of the three drawings of a turn (on twos)
D_CAM = 4200.0                   # camera distance above the page (1080p px) for the perspective of the lifted leaf


def strike_page(ctx):
    """The K3 strike at page resolution (density, page px)."""
    pts = [(916, 428, 0.5), (911, 900, 1.0), (906, 1600, 1.05), (903, 2150, 1.0), (868, 2390, 0.95),
           (762, 2620, 0.75), (690, 2800, 0.4)]
    pap = Paper(PW, PH, 'aged', seed=40)
    st = stroke(pts, width=92, seed=3, paper=pap, density=0.95, dry=0.04, dry_end=0.7, bleed=3.5)
    d = st.density(1.6, wet=0)
    d = np.maximum(d, np.minimum(np.maximum(blur(d, 2.7) * 0.5, blur(d, 7.2) * 0.22), 0.6))
    full = np.zeros((PH, PW), np.float32)
    x0, y0 = int(st.pos[0]), int(st.pos[1])
    h, w = d.shape
    ys, xs, ye, xe = max(0, y0), max(0, x0), min(PH, y0 + h), min(PW, x0 + w)
    full[ys:ye, xs:xe] = d[ys - y0:ye - y0, xs - x0:xe - x0]
    return full


def hand_cutout(px):
    """v3: the small hand that turns the pages (design/plates/H_v3_pages/hand/hand_1.png) as straight-alpha RGBA,
    `px` wide. Matte = everything not connected to the border through the plate's own cream ground."""
    im = load_image('design/plates/H_v3_pages/hand/hand_1.png')
    g = np.median(im[:40].reshape(-1, 3), 0)
    diff = np.abs(im - g[None, None]).max(axis=2)
    bg = (blur(diff, 2.0) < 0.035).astype(np.uint8)
    n, lab = cv2.connectedComponents(bg)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    a = 1.0 - np.isin(lab, list(border)).astype(np.float32)
    a = blur(cv2.erode(a, np.ones((5, 5), np.uint8)), 1.5)
    rgba = np.dstack([im, a]).astype(np.float32)
    k = px / im.shape[1]
    return cv2.resize(rgba, (int(px), int(im.shape[0] * k)), interpolation=cv2.INTER_AREA)


HAND_PINCH = (0.335, 0.455)                      # the pinch point, as a fraction of the cut-out


def hand_pos(t, ctx):
    """Frame position of the pinch point at t, or None when the hand is out of frame. It comes in from the lower
    right, takes the outer bottom corner of the left page, carries it over on the leaf, lets go and withdraws."""
    W, H = ctx.W, ctx.H
    lw = PW * S
    yb = OY + PH * S * 0.74
    grab = np.array([OX + lw * 0.06, yb])
    out = np.array([W * 0.70, H * 1.45])
    for tl in LANDS:
        tl = on_frame(tl)
        ts = tl - 6 / 24.0
        if ts - 14 / 24.0 <= t < ts:                             # reaching in
            u = ease((t - (ts - 14 / 24.0)) / (14 / 24.0), 'out')
            return out + (grab - out) * u
        if ts <= t < tl:                                         # on the leaf's corner
            j = min(2, int((t - ts) * 24.0 + 1e-6) // 2)
            th = DRAW_THETA[j]
            x, y = project(SPINE_X - math.cos(th) * lw * 0.94, yb, math.sin(th) * lw * 0.94, W, H)
            return np.array([x, y])
        land = np.array([SPINE_X + lw * 0.94, yb])
        if tl <= t < tl + 5 / 24.0:                              # the page is down; the fingers rest on it
            return land
        if tl + 5 / 24.0 <= t < tl + 15 / 24.0:                  # withdrawing
            u = ease((t - tl - 5 / 24.0) / (10 / 24.0), 'in')
            return land + (out - land) * u
    return None


def setup(ctx):
    global SPREADS, PAGES, LANDS, OX, OY, S, NIGHT_BG, L, WORDS, SPINE_X, HAND, INS
    ensure_ledger()
    W, H = ctx.W, ctx.H
    S = SC * ctx.s
    OX, OY = (W - SPW * S) / 2, (H - PH * S) / 2 + 6 * ctx.s
    pages = [load_image(LEDGER + f'E_ledger_p{k}.png') for k in range(1, 9)]
    strike = ctx.cache('k4_strike', lambda: strike_page(ctx))
    pages[0] = pages[0] * ink_T(strike)
    sp = [load_image(LEDGER + f'spread_{k}_{k + 1}.png') for k in (1, 3, 5, 7)]
    sp[0][:, PW + GUT:] = sp[0][:, PW + GUT:] * ink_T(strike)
    NIGHT_BG = blur(Paper(W, H, 'aged', seed=88).rgb, 9 * ctx.s) * 0.30
    a = fit(np.ones((PH, SPW, 1), np.float32), W, H, S, -OX / S, -OY / S)
    a = a[..., None] if a.ndim == 2 else a
    SPREADS = [fit(s_, W, H, S, -OX / S, -OY / S) * a + NIGHT_BG * (1 - a) for s_ in sp]
    PAGES = [resize(p, int(round(PW * S)), int(round(PH * S))) for p in pages]
    SPINE_X = OX + (PW + GUT / 2) * S
    tm = ctx.timing
    try:
        lands = [tm.word('I turned each page', 'page')[0], tm.word('I turned each page', 'looked')[0]]
    except Exception:
        lands = [218.22, 220.92]
    hit = [h['t'] for h in tm.hits('low_drum', 221.0, 222.5)]
    lands.append(hit[0] if hit else 221.805)
    LANDS = lands
    L = light_field(W, H, (W * 0.5, H * 0.53), 700 * ctx.s, ambient=0.07, gain=1.34, tilt=0, stretch=1.25, seed=21)
    WORDS = line_words(ctx, 'I turned each page', 217.2)
    HAND = hand_cutout(900 * ctx.s)
    from tools.ink.inscription import inscription
    INS = inscription(ctx, 'K4', box=(1690, 150, 190, 640), ground='dark')     # v3: beside the ledger, on the dark


def leaf_state(t):
    """(turn index, theta) or (spread index, None) when no leaf is in the air."""
    for k, tl in enumerate(LANDS):
        tl = on_frame(tl)                       # fix2: the page is down ON the frame that contains the landing
        ts = tl - 6 / 24.0
        if ts - 1e-9 <= t < tl - 1e-9:
            j = min(2, int((t - ts) * 24.0 + 1e-6) // 2)
            return k, DRAW_THETA[j]
    n = sum(1 for tl in LANDS if t >= on_frame(tl) - 1e-9)
    return n, None


def project(X, Y, Z, W, H):
    k = D_CAM / (D_CAM - Z)
    cx, cy = W * 0.5, H * 0.52
    return cx + (X - cx) * k, cy + (Y - cy) * k


def draw_leaf(f, front, back, theta, ctx):
    """Composite the turning leaf (3 rigid panels with a slight curl) and its shadow onto f, in place."""
    W, H = ctx.W, ctx.H
    lw = PW * S
    top, bot = OY, OY + PH * S
    n = 3
    curl = 0.32 * math.sin(theta) * (1 if theta < math.pi / 2 else -1)
    us = np.linspace(0, 1, n + 1)
    X, Z = [SPINE_X], [0.0]
    ths = []
    for i in range(n):
        th = theta + curl * (i + 0.5) / n
        ths.append(th)
        du = (us[i + 1] - us[i]) * lw
        X.append(X[-1] - math.cos(th) * du)
        Z.append(Z[-1] + math.sin(th) * du)
    # shadow: the leaf's footprint pushed away from the torch, softer the higher it is
    sh = np.zeros((H, W), np.float32)
    for i in range(n):
        za, zb = Z[i], Z[i + 1]
        quad = np.array([[X[i] + 0.10 * za, top + 0.22 * za], [X[i + 1] + 0.10 * zb, top + 0.22 * zb],
                         [X[i + 1] + 0.10 * zb, bot + 0.10 * zb], [X[i] + 0.10 * za, bot + 0.10 * za]], np.float32)
        cv2.fillConvexPoly(sh, np.round(quad * 4).astype(np.int32), 1.0, lineType=cv2.LINE_AA, shift=2)
    zmean = float(np.mean(Z))
    sh = blur(sh, 4 * ctx.s + 0.06 * zmean)
    f *= (1 - 0.42 * sh)[..., None]
    # panels, back to front by height (the higher panel is nearer the camera)
    ph, pw = front.shape[:2]
    for i in sorted(range(n), key=lambda i: Z[i] + Z[i + 1]):
        th = ths[i]
        vis_front = math.cos(th) > 0
        img = front if vis_front else back
        ua, ub = us[i], us[i + 1]
        if vis_front:
            sx = [pw * (1 - ua), pw * (1 - ub)]          # left page: spine at its right edge
        else:
            sx = [pw * ua, pw * ub]                      # right page: spine at its left edge
        src = np.float32([[sx[0], 0], [sx[1], 0], [sx[1], ph], [sx[0], ph]])
        pa, pb = project(X[i], top, Z[i], W, H), project(X[i + 1], top, Z[i + 1], W, H)
        pc, pd = project(X[i + 1], bot, Z[i + 1], W, H), project(X[i], bot, Z[i], W, H)
        dst = np.float32([pa, pb, pc, pd])
        x0, y0 = np.floor(dst.min(0)).astype(int) - 2
        x1, y1 = np.ceil(dst.max(0)).astype(int) + 2
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if x1 - x0 < 2 or y1 - y0 < 2:
            continue
        M = cv2.getPerspectiveTransform(src, dst - np.float32([x0, y0]))
        rgb = cv2.warpPerspective(img, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        al = cv2.warpPerspective(np.ones((ph, pw), np.float32), M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
        shade = 0.62 + 0.38 * abs(math.cos(th))           # a tilted sheet takes less of the torch
        reg = f[y0:y1, x0:x1]
        reg[:] = reg * (1 - al[..., None]) + rgb * shade * al[..., None]
    return f


def render(t, ctx):
    k, theta = leaf_state(t)
    if theta is None:
        f = SPREADS[min(k, 3)].copy()
    else:
        old, new = SPREADS[k], SPREADS[k + 1]
        sx = int(round(SPINE_X))
        f = np.concatenate([new[:, :sx], old[:, sx:]], 1).copy()     # under the leaf: the next left page
        front, back = PAGES[2 * k + 1], PAGES[2 * k + 2]              # leaf = old left page / new right page
        draw_leaf(f, front, back, theta, ctx)
    hp = hand_pos(t, ctx)
    if hp is not None:                                            # v3: a small hand is SEEN turning the pages
        hh, hw = HAND.shape[:2]
        x, y = int(round(hp[0] - HAND_PINCH[0] * hw)), int(round(hp[1] - HAND_PINCH[1] * hh))
        sh = np.zeros(f.shape[:2], np.float32)                    # its soft shadow on the page, away from the torch
        a = HAND[..., 3]
        x0, y0 = x + int(14 * ctx.s), y + int(18 * ctx.s)
        a0, b0, a1, b1 = max(0, x0), max(0, y0), min(ctx.W, x0 + hw), min(ctx.H, y0 + hh)
        if a1 > a0 and b1 > b0:
            sh[b0:b1, a0:a1] = a[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
            f *= (1 - 0.38 * blur(sh, 9 * ctx.s))[..., None]
        over(f, HAND, x, y)
    f = lit(f, L)
    INS.draw(f)
    lyric(f, ctx, sung_words(WORDS, t, tail=1.2), y=0.955, px=28)
    return f

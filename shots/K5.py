"""K5 (224.18-228.767) 'it wasn't there on any line'.

The last page of the register (p8 of the team's ledger = the plate's p4 layout): ruled columns of entries, the final
(leftmost) column bare. The torch rests on the bare column; the filled columns fall away into the dark to the right,
the book's outer edge and the dark beyond it on the left. Hold. Nothing moves, not even on the hit at 225.254.
Lyric (if on) small in the lower right, away from the bare column.
"""
import math
import os
import sys

import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.ink import *
from _heaven import *

T0, T1 = 224.16666666666666, 228.75
# fix2 (lead's re-frame): a ledger page, not a close-up. Scale 1.20 page px -> 1080p px: the bare last column (p8
# x 208-414, between the outer frame rule and the first column rule) sits a little left of centre in the middle of the
# torch pool, from the page's top frame rule down; written columns to its right fall off to dark, the page margin and
# the book's edge on its left. Window in p8 page px: see PAGE_RECT.
SC = 1.20                         # page px -> 1080p px
BARE_X = 311                      # centre of the bare column, spread px (p8 is the LEFT page)
FX = 860                          # where the bare column sits in the frame (1080p px)
Y0 = 260                          # page y at the frame's top edge (the top frame rule is at ~350)
POOL = (860, 600, 560)            # torch centre (1080p px) and radius


GAIN = float(os.environ.get('K5_GAIN', '1.42'))
PAGE_RECT = (BARE_X - FX / SC, Y0, BARE_X - FX / SC + 1920 / SC, Y0 + 1080 / SC)


def make_base(ctx, k=1.0):
    """The page + the dark beyond the book at drift scale k about the frame point (FX, 700) (no light)."""
    W, H = ctx.W, ctx.H
    s = SC * ctx.s
    x0 = BARE_X - FX / SC
    cx, cy = FX * ctx.s, 700 * ctx.s
    pcx, pcy = x0 + cx / s, Y0 + cy / s
    s2 = s * k
    x0k, y0k = pcx - cx / s2, pcy - cy / s2
    page = fit(SP, W, H, s2, x0k, y0k)
    a = fit(np.ones(SP.shape[:2] + (1,), np.float32), W, H, s2, x0k, y0k)
    a = a[..., None] if a.ndim == 2 else a
    edge_x = (0 - x0k) * s2
    xx = np.arange(W, dtype=np.float32)[None, :, None]
    shade = 1 - 0.55 * np.exp(-np.maximum(edge_x - xx, 0) / (14 * ctx.s * k)) * (xx < edge_x)
    return page * a + NIGHT * (1 - a) * shade


def setup(ctx):
    global SP, NIGHT, LF, WORDS, INS
    from tools.ink.inscription import inscription
    INS = inscription(ctx, 'K5', box=(300, 150, 100, 700), ground='dark')      # v3: static, on the dark beyond the book
    ensure_ledger()
    W, H = ctx.W, ctx.H
    SP = load_image(LEDGER + 'spread_7_8.png')
    NIGHT = blur(Paper(W, H, 'aged', seed=88).rgb, 9 * ctx.s) * 0.30                  # what lies beyond the book's edge
    LF = light_field(W, H, (POOL[0] * ctx.s, POOL[1] * ctx.s), POOL[2] * ctx.s, ambient=0.07, gain=GAIN, tilt=88,
                     stretch=1.30, seed=11)
    build_wet(ctx)
    WORDS = line_words(ctx, 'it wasn', 224.2)


# ---- v4b: wet, never-resolved writing built from real brush strokes (Make Me a Hanzi, Arphic Public License) -------
import json
import random

MMAH = '/home/jade/Documents/vibesong/engine/data/graphics.txt'
CELLS_Y = (640, 810, 975)         # centres of the cells = the neighbouring entries 似 飛 禽 in the next column
CELL_X = 860
CELL_EM = 178.0                   # cell size (1080p px) = the neighbours' glyph size
CELL_START = (0.50, 1.20, 1.90)   # seconds when each cell begins to let go (top to bottom); cell 1 is gone at the hit
CELL_SPAN = 0.38
HIT_U = 225.254 - T0
CROP = (700, 500, 1000, 1080)     # x0, y0, x1, y1 (1080p) of the work area
SEED = int(os.environ.get('K5_SEED', '7'))


def _poly(path):
    tok = path.split()
    pts, i, cur = [], 0, None
    while i < len(tok):
        c = tok[i]
        if c == 'M' or c == 'L':
            cur = (float(tok[i + 1]), float(tok[i + 2]))
            pts.append(cur)
            i += 3
        elif c == 'Q':
            c1 = (float(tok[i + 1]), float(tok[i + 2]))
            e = (float(tok[i + 3]), float(tok[i + 4]))
            for t in np.linspace(0, 1, 8)[1:]:
                pts.append(((1 - t) ** 2 * cur[0] + 2 * t * (1 - t) * c1[0] + t * t * e[0],
                            (1 - t) ** 2 * cur[1] + 2 * t * (1 - t) * c1[1] + t * t * e[1]))
            cur = e
            i += 5
        else:
            i += 1
    return np.array([(x, 900 - y) for x, y in pts], np.float32)


def _kind(med):
    m = np.array([(x, 900 - y) for x, y in med], np.float32)
    d = m[-1] - m[0]
    ln = float(np.hypot(*d))
    if ln < 150:
        return 'dot'
    seg = m[-1] - m[-2] if len(m) > 2 else d
    ang = abs(math.degrees(math.atan2(seg[1], seg[0]) - math.atan2(d[1], d[0])))
    ang = min(ang, 360 - ang)
    if ang > 55 and ln > 150:
        return 'hook'
    if abs(d[1]) < 0.3 * abs(d[0]):
        return 'horizontal' if d[0] > 0 else 'horizontal'
    if abs(d[0]) < 0.3 * abs(d[1]):
        return 'vertical'
    return 'pie' if d[0] < 0 else 'na'


_DB = None


def load_db():
    """Strokes (polygon, median, kind, source char) from many characters, plus per-char raster for the look-alike check."""
    global _DB
    if _DB is not None:
        return _DB
    chars = []
    for ln in open(MMAH, encoding='utf8'):
        d = json.loads(ln)
        c = d['character']
        if not ('一' <= c <= '鿿') or not (3 <= len(d['strokes']) <= 14):
            continue
        chars.append(d)
    _DB = chars
    return chars


def raster(polys, n=40, box=(0, 0, 1024, 1024)):
    im = np.zeros((n, n), np.uint8)
    x0, y0, x1, y1 = box
    for p in polys:
        q = (p - np.array([x0, y0], np.float32)) * (n / max(x1 - x0, y1 - y0))
        cv2.fillPoly(im, [np.round(q).astype(np.int32)], 1)
    return cv2.dilate(im, np.ones((2, 2), np.uint8)).astype(np.float32)


# layout templates in em units (0..1024, y down): (allowed kinds, box x0,y0,x1,y1)
TEMPLATES = [
    [(('pie', 'vertical'), (110, 130, 400, 560)), (('horizontal',), (90, 560, 420, 690)), (('dot', 'hook'), (170, 740, 380, 900)),
     (('horizontal',), (500, 120, 940, 250)), (('vertical', 'hook'), (600, 280, 820, 620)), (('dot', 'pie'), (500, 420, 640, 620)),
     (('horizontal', 'na'), (520, 700, 960, 860))],
    [(('dot',), (150, 90, 330, 220)), (('horizontal', 'hook'), (330, 100, 900, 250)), (('pie', 'na'), (120, 330, 520, 700)),
     (('vertical', 'hook'), (560, 340, 760, 800)), (('dot', 'horizontal'), (160, 760, 440, 900)), (('na', 'dot'), (700, 540, 940, 900))],
    [(('horizontal',), (120, 110, 600, 240)), (('pie', 'dot'), (150, 260, 450, 520)), (('hook', 'vertical'), (480, 230, 700, 620)),
     (('dot', 'na'), (720, 300, 920, 520)), (('horizontal',), (130, 640, 520, 770)), (('pie', 'hook'), (560, 640, 900, 900)),
     (('dot',), (230, 820, 370, 930))],
]


def assemble(rnd, tpl, pool):
    """Pick one stroke per slot from `pool` (kind -> list of (poly, med, char)) and fit it to the slot, scaled/rotated a little."""
    out = []
    used = set()
    for kinds, (bx0, by0, bx1, by1) in tpl:
        for _ in range(50):
            kd = rnd.choice(kinds)
            poly, med, ch = rnd.choice(pool[kd])
            if ch in used:
                continue
            break
        used.add(ch)
        P = poly.copy()
        M = np.array([(x, 900 - y) for x, y in med], np.float32)
        a = math.radians(rnd.uniform(-9, 9))
        R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], np.float32)
        c0 = P.mean(0)
        P = (P - c0) @ R.T
        M = (M - c0) @ R.T
        w, h = np.ptp(P[:, 0]) + 1, np.ptp(P[:, 1]) + 1
        sc = min((bx1 - bx0) / w, (by1 - by0) / h, 1.35)
        sc = max(sc, 0.55) if kd != 'dot' else min(sc, 1.2)
        tx = (bx0 + bx1) / 2 + rnd.uniform(-0.12, 0.12) * (bx1 - bx0)
        ty = (by0 + by1) / 2 + rnd.uniform(-0.12, 0.12) * (by1 - by0)
        cen = (P.min(0) + P.max(0)) / 2
        P = (P - cen) * sc + np.array([tx, ty], np.float32)
        M = (M - cen) * sc + np.array([tx, ty], np.float32)
        out.append((P, M, kd, ch))
    return out


def make_cells():
    db = load_db()
    pool = {k: [] for k in ('dot', 'hook', 'horizontal', 'vertical', 'pie', 'na')}
    rr = random.Random(11)
    for d in rr.sample(db, 1400):
        for st, md in zip(d['strokes'], d['medians']):
            pool[_kind(md)].append((_poly(st), md, d['character']))
    # rasters of the database characters, by stroke count, for the look-alike check
    rast = {}
    for d in db:
        n = len(d['strokes'])
        if 5 <= n <= 10:
            rast.setdefault(n, []).append((d['character'], raster([_poly(s) for s in d['strokes']])))
    cells, info = [], []
    for ci in range(len(CELLS_Y)):
        rnd = random.Random((8, 7, 7)[ci] * 100 + ci)
        for attempt in range(120):
            st = assemble(rnd, TEMPLATES[(ci + attempt) % len(TEMPLATES)], pool)
            r = raster([p for p, _, _, _ in st])
            best, bc = 0, ''
            for n in (len(st) - 1, len(st), len(st) + 1):
                for ch, ra in rast.get(n, []):
                    iou = float((r * ra).sum() / max(1.0, np.maximum(r, ra).sum()))
                    if iou > best:
                        best, bc = iou, ch
            if best < 0.33:
                break
        cells.append(st)
        info.append((len(st), round(best, 2), bc, attempt, ''.join(c for _, _, _, c in st)))
    return cells, info


def build_wet(ctx):
    global WM, WL, WCI, WPOS, WFIB, WNZ, WCS, CELL_INFO
    s = ctx.s
    x0, y0, x1, y1 = [int(round(v * s)) for v in CROP]
    w, h = x1 - x0, y1 - y0
    cells, CELL_INFO = ctx.cache('k5_cells_v%d' % SEED, make_cells) if False else make_cells()
    M = np.zeros((h, w), np.float32)
    LP = np.zeros((h, w), np.float32)
    CI = np.full((h, w), -1, np.int32)
    k = CELL_EM / 1024.0 * s
    for ci, st in enumerate(cells):
        ox, oy = (CELL_X - CELL_EM / 2) * s - x0, (CELLS_Y[ci] - CELL_EM / 2) * s - y0
        for si, (P, Md, kd, ch) in enumerate(st):
            m = np.zeros((h, w), np.uint8)
            cv2.fillPoly(m, [np.round((P * k + [ox, oy]) * 8).astype(np.int32)], 1, lineType=cv2.LINE_AA, shift=3)
            md = (Md * k + [ox, oy]).astype(np.float32)
            m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * 2.0 * s) | 1,) * 2)).astype(np.float32)
            m = blur(m, 0.9 * s)
            # position along the stroke from its median
            ln = np.zeros((h, w), np.uint8)
            cum = np.r_[0, np.cumsum(np.hypot(*np.diff(md, axis=0).T))]
            idx = np.zeros((h, w), np.int32)
            for i in range(len(md) - 1):
                cv2.line(idx, tuple(np.round(md[i]).astype(int)), tuple(np.round(md[i + 1]).astype(int)), i + 1, 1)
            dist, lab = cv2.distanceTransformWithLabels((idx == 0).astype(np.uint8), cv2.DIST_L2, 5,
                                                        labelType=cv2.DIST_LABEL_PIXEL)
            ys, xs = np.nonzero(idx)
            lut = np.zeros(lab.max() + 1, np.int32)
            lut[lab[ys, xs]] = idx[ys, xs] - 1
            u = cum[np.minimum(lut[lab], len(cum) - 1)] / max(cum[-1], 1)
            lp = 1.0 - np.abs(2 * u - 1)
            win = m > M
            LP = np.where(win, lp, LP)
            CI = np.where(win, ci, CI)
            M = np.maximum(M, m)
    # nearest stroke's cell/lift for the pixels around (feathering, bloom)
    cl = ((M > 0.25) == 0).astype(np.uint8)
    dist, lab = cv2.distanceTransformWithLabels(cl, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(cl == 0)
    lut = np.zeros(lab.max() + 1, np.int64)
    lut[lab[ys, xs]] = ys * w + xs
    near = lut[lab]
    LP = LP.reshape(-1)[near]
    CI = np.maximum(CI.reshape(-1)[near], 0)
    WM, WL, WCI, WPOS = M, LP, CI, (x0, y0)
    WCS = np.array(CELL_START, np.float32)[CI]
    # fibrous grain: noise stretched along the paper's fibre direction
    n = rng(SEED, 'fib').random((h, w)).astype(np.float32)
    f = cv2.GaussianBlur(n, (0, 0), sigmaX=0.8 * s, sigmaY=3.5 * s)
    WFIB = (f - f.mean()) / (f.std() + 1e-6)
    WNZ = fbm(h, w, 9 * s, SEED, 'lift', octaves=3) - 0.5
    def aniso(key, sx, sy):
        q = cv2.GaussianBlur(rng(SEED, key).random((h, w)).astype(np.float32), (0, 0), sigmaX=sx * s, sigmaY=sy * s)
        return (q - q.mean()) / (q.std() + 1e-6)
    WB1, WB2 = aniso('b1', 6, 20), aniso('b2', 3, 9)
    globals().update(WB1=WB1, WB2=WB2)


def wet_state(u, ctx):
    lt = WCS + CELL_SPAN * (0.62 * WL + 0.38 * np.clip(blur(WM, 1.5), 0, 1)) + 0.05 * WNZ
    q = (u - lt) / 0.22
    keep = 1 - smoothstep(0.0, 1.0, q)
    sheen = np.exp(-((q - 0.3) / 0.45) ** 2) * (q > -0.6)
    return keep.astype(np.float32), sheen.astype(np.float32)


def wet_layers(u, ctx):
    """(T multiplier HxWx3, additive sheen HxW) for the cropped area."""
    s = ctx.s
    keep, sheen = wet_state(u, ctx)
    vis = WM * keep
    pr = smoothstep(0.0, 1.0, (u - (WCS - 0.25)) / 0.40)           # per-cell: how far the bloom has drawn back (0..1)
    wetness = 1 - pr
    # crisp-ish core with a ragged brush edge and bristle breakup
    core = smoothstep(0.42, 0.62, vis + 0.10 * WNZ) * (0.80 + 0.12 * WFIB.clip(-1.5, 1.5) * 0.5 + 0.18 * WNZ)
    # ink bleeding into the fibres: feathering along the grain at the edges
    feather = np.clip(blur(vis, 3.4 * s) * 1.55 - 0.22 + 0.34 * WFIB, 0, 1) * smoothstep(0.03, 0.14, blur(vis, 3.4 * s)) * 0.34 * (1 - core)
    # paler water bloom with a darker tide-line at its rim, drawing back onto the strokes
    Bf = blur(vis, 11 * s) + 0.075 * WB1 + 0.03 * WB2
    thr = 0.05 + 0.25 * pr
    inside = smoothstep(thr - 0.03, thr + 0.03, Bf)
    bloom = inside * 0.065 * (0.85 + 0.15 * WB2.clip(-1.5, 1.5))
    tide = np.exp(-((Bf - thr) / 0.012) ** 2) * (Bf > 0.02) * 0.085 * smoothstep(0.2, 1.1, WB1 * 0.6 + WB2 * 0.5)
    wmask = np.clip(blur(WM, 14 * s) * 6, 0, 1)                  # no bloom far from any stroke
    d = np.clip(core * 1.0 + feather + (bloom + tide) * wmask * (keep * 0.6 + 0.4 * (blur(keep, 6 * s))), 0, 1.4)
    # faint specular sheen on the wet core (upper-left rim catches the lamp)
    g = blur(vis, 1.6 * s)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    spec = np.clip(gx + gy, 0, None) * 0.9 * wetness * np.clip(vis * 2, 0, 1)
    spec = np.clip(spec, 0, 1) * 0.12
    # a paler sheen where the strokes lift
    spec = spec + 0.06 * blur(sheen * np.minimum(1, WM * 1.5), 4 * s)
    return ink_T(d), spec.astype(np.float32)


DROP_P = (CELL_X + 40, CELLS_Y[2] + 55, 15)


def render(t, ctx):
    u = t - T0
    W, H = ctx.W, ctx.H
    s = ctx.s
    dr = ease(u / (T1 - T0), 'inout')
    k = 1.0 + 0.035 * dr
    f = make_base(ctx, k)
    cx, cy = FX * s, 700 * s
    Mw = np.float32([[k, 0, cx - k * cx], [0, k, cy - k * cy]])
    T, spec = wet_layers(u, ctx)
    x0, y0 = WPOS
    h, w = spec.shape
    TF = np.ones((H, W, 3), np.float32)
    TF[y0:y0 + h, x0:x0 + w] = T
    SF = np.zeros((H, W), np.float32)
    SF[y0:y0 + h, x0:x0 + w] = spec
    # the last drop of dampness drying (a pale bloom with a darker rim, then gone)
    dw = float(smoothstep(1.5, 2.4, u) * (1 - smoothstep(2.6, 4.2, u)))
    if dw > 0:
        px, py, pr = DROP_P
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt((xx - px * s) ** 2 + (yy - py * s) ** 2) / (pr * s * (1.2 - 0.4 * (1 - dw)))
        TF *= (1 - 0.05 * dw * np.exp(-r ** 4) - 0.07 * dw * np.exp(-((r - 1.0) / 0.12) ** 2))[..., None]
        SF += 0.05 * dw * np.exp(-((xx - (px - 5) * s) ** 2 + (yy - (py - 5) * s) ** 2) / (4 * s) ** 2)
    TF = cv2.warpAffine(TF, Mw, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    SF = cv2.warpAffine(SF, Mw, (W, H), flags=cv2.INTER_LINEAR)
    f = f * TF + SF[..., None]
    breath = 1 + 0.018 * math.sin(2 * math.pi * u / 3.1) + 0.010 * math.sin(2 * math.pi * u / 1.3 + 1.0)
    breath += 0.035 * math.exp(-max(t - 225.254, -1) / 0.18) * (t >= 225.254)
    f = lit(f, LF * breath)
    g = fbm(H, W, 5 * s, 77, 'glint', octaves=2)
    ph = 0.5 + 0.5 * np.sin(u * 1.7 + 12 * fbm(H, W, 60 * s, 78, 'gp', octaves=1))
    pool = np.exp(-(((np.arange(W)[None, :] - FX * s) / (330 * s)) ** 2 + ((np.arange(H)[:, None] - 600 * s) / (420 * s)) ** 2))
    f += (0.035 * np.clip((g - 0.62) * 5, 0, 1) * ph * pool)[..., None]
    f = np.clip(f, 0, 1)
    INS.draw(f)
    lyric(f, ctx, sung_words(WORDS, t, tail=1.0), y=0.955, x=0.63, px=28)
    return f

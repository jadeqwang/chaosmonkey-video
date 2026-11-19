"""shots/_book4_strokes.py: BOOK v4 stroke engine for H5 -> H6 (candidate A, fully procedural).

The carved characters of the B4/H5 cliff are re-carved from Make Me a Hanzi stroke data (graphics.txt, Arphic Public
License; refs/data/MMAH_NOTE.md), so every stroke is an object that can leave the stone:

    strokes.py geometry  : MMAH outlines + medians -> per-stroke rest ribbon (two rails along the median, per-point
                           half-width from the outline), plane coordinates of the cliff canvas (B_cliff_run, 9040x1280)
    carving              : a tools.ink.cliff.Cliff whose glyphs are the MMAH outlines (layout identical to v3), plus
                           plane maps: stroke id, release time per pixel (the peel front), for the cinnabar fill
    girl                 : slots (paths) of a back-view girl in 白描: outline, folds, hair (flow field), cinnabar
    sim (torch, GPU)     : PBD ribbons in 3D: stretch/shear/bend constraints, shape matching to a rest shape that
                           morphs to the slot shape, anisotropic drag in a curl-noise + gust gale, gravity, peel-off
                           from one end, spring-damper steering to the slot; H6: hair rooted on her head, one strand
                           released, thrust when the monkey grows
    bake (torch, GPU)    : perspective camera, adaptive splatting of each ribbon's param-space atlas (outline, dry
                           brush, wash edge, darker underside), depth-of-field buckets, motion blur by sub-frames ->
                           per frame transmittance (uint8 npz) that the shot scripts multiply onto the sheet.

Run as a module (separate process, so the shot runner's forked workers never see CUDA):
    $PY -m shots._book4_strokes sim            # -> work/book4/H56/sim/sim.npz
    $PY -m shots._book4_strokes bake 1920x1080 # -> work/book4/H56/bake/1920x1080/f####.npz (H5+H6 frames 0..190)
"""
import json
import math
import os
import sys
from functools import lru_cache

import cv2
import numpy as np

from tools.ink.core import F32, ROOT, blur, fbm, rng, smoothstep

MMAH = '/home/jade/Documents/vibesong/engine/data/graphics.txt'
WORK = ROOT / 'work/book4/H56'
FPS = 24
# song clock: H5 = song frames 4062..4146, H6 = 4146..4253. Sim time 0 = H5 frame 0.
F_H5, F_H6, F_END = 4062, 4146, 4253
T_SONG0 = F_H5 / 24.0
NFR = F_END - F_H5                      # 191 frames in all
H5_N, H6_N = F_H6 - F_H5, F_END - F_H6

# the cliff (as v3 H5 / v2 B4)
CLIFF_SIZE = 130
BLOCKS = [(8020, 150, 330, 980), (7100, 90, 400, 1060), (6240, 190, 320, 860), (5780, 300, 200, 700),
          (4650, 110, 420, 1040), (3890, 170, 330, 960), (3260, 240, 330, 840)]
CLIFF_SEED = 4


# ----------------------------------------------------------------------------------------------------------------
# MMAH

@lru_cache(maxsize=1)
def mmah():
    d = {}
    for line in open(MMAH, encoding='utf-8'):
        o = json.loads(line)
        d[o['character']] = o
    return d


def parse_path(p, nseg=10):
    """SVG path (M L Q C Z, absolute) -> list of polygons (Nx2, MMAH em coordinates, y up)."""
    toks = p.replace(',', ' ').split()
    polys, cur, i, pos = [], [], 0, None
    while i < len(toks):
        c = toks[i]
        if c == 'M':
            if cur:
                polys.append(np.array(cur, np.float64))
            pos = (float(toks[i + 1]), float(toks[i + 2]))
            cur = [pos]
            i += 3
        elif c == 'L':
            pos = (float(toks[i + 1]), float(toks[i + 2]))
            cur.append(pos)
            i += 3
        elif c == 'Q':
            c1 = (float(toks[i + 1]), float(toks[i + 2]))
            e = (float(toks[i + 3]), float(toks[i + 4]))
            for k in range(1, nseg + 1):
                u = k / nseg
                cur.append(((1 - u) ** 2 * pos[0] + 2 * (1 - u) * u * c1[0] + u * u * e[0],
                            (1 - u) ** 2 * pos[1] + 2 * (1 - u) * u * c1[1] + u * u * e[1]))
            pos = e
            i += 5
        elif c == 'C':
            c1 = (float(toks[i + 1]), float(toks[i + 2]))
            c2 = (float(toks[i + 3]), float(toks[i + 4]))
            e = (float(toks[i + 5]), float(toks[i + 6]))
            for k in range(1, nseg + 1):
                u = k / nseg
                a, b, cc, dd = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
                cur.append((a * pos[0] + b * c1[0] + cc * c2[0] + dd * e[0],
                            a * pos[1] + b * c1[1] + cc * c2[1] + dd * e[1]))
            pos = e
            i += 7
        elif c == 'Z':
            i += 1
        else:                                        # implicit repeat (not used by MMAH): skip
            i += 1
    if cur:
        polys.append(np.array(cur, np.float64))
    return polys


def em_to_img(pts, S_em, S_img):
    """MMAH em coords (y up, baseline transform y' = 900 - y) -> glyph image px (S_img square, em box centred)."""
    k = S_em / 1024.0
    x = (pts[:, 0] - 512.0) * k + S_img / 2.0
    y = (900.0 - pts[:, 1] - 512.0) * k + S_img / 2.0
    return np.stack([x, y], 1)


def glyph_mask_mmah(ch, size, pad=0):
    """Drop-in for tools.ink.cliff.glyph_mask: the MMAH outline of ch, filled (size+2*pad square, em centred)."""
    S = int(size + 2 * pad)
    g = mmah()[ch]
    SS = 4
    im = np.zeros((S * SS, S * SS), np.uint8)
    for sp in g['strokes']:
        for poly in parse_path(sp):
            q = em_to_img(poly, size, S) * SS
            cv2.fillPoly(im, [np.round(q * 16).astype(np.int32)], 255, cv2.LINE_8, 4)
    return cv2.resize(im, (S, S), interpolation=cv2.INTER_AREA).astype(F32) / 255.0


# ----------------------------------------------------------------------------------------------------------------
# the carving: layout identical to v3 (Cliff + blocks_layout + rng 'cliff'), glyphs from MMAH

def cliff_cells(text):
    """[(ch, cx, cy, col, row, jx, jy, sc, rot)] exactly as Cliff.__init__ places them (seal-font coverage filter,
    block layout, per-cell jitter drawn from rng(seed, 'cliff') in order)."""
    from tools.ink.cliff import blocks_layout, coverage
    from shots._mountain import SEAL_FONT
    ok, _ = coverage(text.replace('\n', ''), SEAL_FONT)
    keep = set(ok)
    text = ''.join(c for c in text if c == '\n' or c in keep)
    cells, _, _ = blocks_layout(text, list(BLOCKS), CLIFF_SIZE, 0.3, 0.12, None, 'rtl')
    r = rng(CLIFF_SEED, 'cliff')
    jitter = 0.04
    out = []
    for ch, cx, cy, col, row in cells:
        jx, jy = r.normal(0, jitter * CLIFF_SIZE, 2)
        sc, rot = 1 + r.normal(0, jitter), r.normal(0, jitter * 40)
        out.append((ch, cx, cy, col, row, jx, jy, sc, rot))
    return out


def glyph_to_plane(pts_em, cell):
    """MMAH em points -> cliff plane coordinates for one carved cell (mirrors Cliff's glyph placement)."""
    ch, cx, cy, col, row, jx, jy, sc, rot = cell
    size = CLIFF_SIZE * sc
    pad = int(CLIFF_SIZE * 0.12) + 2
    S = int(size + 2 * pad)
    q = em_to_img(np.asarray(pts_em, np.float64), size, S)
    if abs(rot) > 0.05:
        M = cv2.getRotationMatrix2D((S / 2, S / 2), rot, 1.0)
        q = q @ M[:, :2].T + M[:, 2]
    gx, gy = int(round(cx + jx - S / 2)), int(round(cy + jy - S / 2))
    return q + np.array([gx, gy], np.float64)


def make_cliff(rock, text, **kw):
    """tools.ink.cliff.Cliff with MMAH glyphs (monkeypatched only while it builds, in this process)."""
    import tools.ink.cliff as tc
    from shots._mountain import SEAL_FONT, KAI_FONT
    orig = tc.glyph_mask
    M = mmah()

    def gm(ch, font, size, pad=0):
        if ch in M:
            return glyph_mask_mmah(ch, size, pad)
        return orig(ch, KAI_FONT, size, pad)                 # (none in frame) a static kaishu cut
    tc.glyph_mask = gm
    try:
        C = tc.Cliff(rock, text, SEAL_FONT, size=CLIFF_SIZE, region=BLOCKS, seed=CLIFF_SEED, **kw)
    finally:
        tc.glyph_mask = orig
    return C


# ----------------------------------------------------------------------------------------------------------------
# stroke objects

def resample(poly, n):
    p = np.asarray(poly, np.float64)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    if d[-1] < 1e-6:
        return np.repeat(p[:1], n, 0), 0.0
    u = np.linspace(0, d[-1], n)
    return np.stack([np.interp(u, d, p[:, 0]), np.interp(u, d, p[:, 1])], 1), d[-1]


def smooth_poly(p, it=2):
    p = p.copy()
    for _ in range(it):
        p[1:-1] = 0.25 * p[:-2] + 0.5 * p[1:-1] + 0.25 * p[2:]
    return p


class Stroke:
    """One stroke of one carved character, in cliff-plane coordinates.
    med (N,2) median (ends extended to the outline), h (N,) half-width of the rails, nrm (N,2) unit normal,
    outline: list of polygons; L: median length; key: (cell index, stroke index)."""
    N = 20

    def __init__(self, ci, si, cell, outline_em, median_em):
        self.ci, self.si, self.ch = ci, si, cell[0]
        self.cx, self.cy = cell[1], cell[2]
        self.outline = [glyph_to_plane(p, cell) for p in parse_path(outline_em)]
        m = glyph_to_plane(np.asarray(median_em, np.float64), cell)
        poly = np.concatenate(self.outline, 0)
        # extend the median at both ends to the outline along its end tangents
        m = self._extend(m, poly)
        m, L = resample(m, 64)
        m = smooth_poly(m, 3)
        m, L = resample(m, self.N)
        self.med, self.L = m, max(L, 1.0)
        t = np.gradient(m, axis=0)
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
        self.tan = t
        self.nrm = np.stack([-t[:, 1], t[:, 0]], 1)
        # half-width: each outline point belongs to its nearest median sample; the rail must clear it
        dense, _ = resample(m, 200)
        dd = ((poly[:, None, :] - dense[None]) ** 2).sum(-1)
        near = dd.argmin(1)
        idx = np.clip(np.round(near / 199 * (self.N - 1)).astype(int), 0, self.N - 1)
        dist = np.sqrt(dd[np.arange(len(poly)), near])
        h = np.zeros(self.N)
        np.maximum.at(h, idx, dist)
        for i in range(self.N):
            if h[i] == 0:
                h[i] = h[max(0, i - 1)]
        w = 2 * h
        self.width = np.clip(w * 0.85, 1.5, None)                     # stroke width (drag area, mass)
        self.h = np.clip(np.maximum.reduce([h, np.r_[h[1:], h[-1]], np.r_[h[0], h[:-1]]]) * 1.08 + 1.5, 3.0, None)
        self.area = float(sum(abs(cv2.contourArea(p.astype(np.float32))) for p in self.outline))

    @staticmethod
    def _extend(m, poly):
        if len(m) < 2:
            m = np.vstack([m, m + [1e-3, 0]])
        path = cv2.UMat
        out = [m]
        for end in (0, -1):
            a = m[end]
            b = m[1] if end == 0 else m[-2]
            d = a - b
            n = np.linalg.norm(d)
            if n < 1e-6:
                continue
            d /= n
            # step outward until outside the outline polygon
            ext = 0.0
            pts = poly.astype(np.float32)
            for step in np.arange(1.0, 60.0, 1.0):
                q = a + d * step
                if cv2.pointPolygonTest(pts, (float(q[0]), float(q[1])), False) < 0:
                    ext = step
                    break
            if ext > 0:
                e = a + d * ext
                if end == 0:
                    out = [e[None]] + out
                else:
                    out = out + [e[None]]
        return np.concatenate(out, 0)

    def rails(self):
        """(2, N, 2) left and right rails of the rest ribbon (plane coords)."""
        return np.stack([self.med + self.nrm * self.h[:, None], self.med - self.nrm * self.h[:, None]], 0)


def build_strokes(cells, view_box):
    """Stroke objects for every carved cell whose centre is inside view_box (x0, y0, x1, y1) and that MMAH has."""
    M = mmah()
    out = []
    x0, y0, x1, y1 = view_box
    for ci, cell in enumerate(cells):
        ch, cx, cy = cell[0], cell[1], cell[2]
        if not (x0 < cx < x1 and y0 < cy < y1) or ch not in M:
            continue
        g = M[ch]
        for si, (o, md) in enumerate(zip(g['strokes'], g['medians'])):
            out.append(Stroke(ci, si, cell, o, md))
    return out


ATLAS_S, ATLAS_B = 256, 48           # param-space atlas texels along / across each stroke


def stroke_atlas(st, seed=0):
    """(ATLAS_B, ATLAS_S) ink alpha of the stroke in its own (b across -1..1, u along 0..1) parameter space: the
    MMAH outline, a wash edge (slightly darker rim, a breath of bleed outside), dry-brush streaks toward the tail."""
    R = st.rails()
    xs = np.concatenate([R[0], R[1]], 0)
    pad = 6
    bx0, by0 = np.floor(xs.min(0)) - pad
    bx1, by1 = np.ceil(xs.max(0)) + pad
    SS = 4
    Wl, Hl = int((bx1 - bx0) * SS), int((by1 - by0) * SS)
    im = np.zeros((Hl, Wl), np.uint8)
    for p in st.outline:
        q = (p - [bx0, by0]) * SS
        cv2.fillPoly(im, [np.round(q * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    a = im.astype(F32) / 255.0
    a = blur(a, 0.6 * SS)
    # wash edge: pigment gathers at the rim; a faint capillary bleed beyond it
    inner = blur(a, 1.6 * SS)
    rim = np.clip(a - inner, 0, 1) * 1.6
    bleed = np.clip(blur(a, 2.5 * SS) - a, 0, 1) * 0.22
    a = np.clip(a * 0.86 + rim * 0.5, 0, 1.25) + bleed
    # sample in param space
    u = np.linspace(0, 1, ATLAS_S)
    b = np.linspace(-1, 1, ATLAS_B)
    ui = u * (st.N - 1)
    i0 = np.clip(np.floor(ui).astype(int), 0, st.N - 2)
    fu = ui - i0
    L = R[0][i0] * (1 - fu)[:, None] + R[0][i0 + 1] * fu[:, None]
    Rr = R[1][i0] * (1 - fu)[:, None] + R[1][i0 + 1] * fu[:, None]
    wb = (b[:, None, None] + 1) / 2                    # 0 = right rail .. 1 = left rail
    P = Rr[None] * (1 - wb) + L[None] * wb             # (B, S, 2)
    mx = ((P[..., 0] - bx0) * SS).astype(np.float32)
    my = ((P[..., 1] - by0) * SS).astype(np.float32)
    A = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # dry brush: streaks parallel to the stroke (fixed to it: they travel with it), stronger toward the end and edges
    r = rng(seed, 'dry', st.ci, st.si)
    streak = np.zeros(ATLAS_B)
    for k in range(5):
        f = r.uniform(3, 14)
        streak += r.uniform(0.3, 1.0) * np.sin(b * f * np.pi + r.uniform(0, 6.28))
    streak = (streak - streak.min()) / max(1e-6, streak.max() - streak.min())
    along = 0.25 + 0.75 * smoothstep(0.45, 1.0, u)
    edge = np.abs(b) ** 2
    nn = fbm(ATLAS_B, ATLAS_S, 6.0, seed, 'drynoise', st.ci, st.si, octaves=2)
    dry = smoothstep(0.55, 0.85, streak[:, None] * 0.6 + nn * 0.5 + edge[:, None] * 0.3) * along[None, :]
    A = A * (1 - 0.75 * dry)
    # tone: pigment a little uneven along the stroke
    A = A * (0.88 + 0.24 * fbm(ATLAS_B, ATLAS_S, 30.0, seed, 'tone', st.ci, st.si, octaves=2))
    return A.astype(F32)


# ----------------------------------------------------------------------------------------------------------------
# the girl: slots of a back-view small girl drawn in 白描 (paths in mask px of work/mountain/child_back_mask.png,
# 466 x 1227; scaled to world units by girl_height / 1227)

MASK_W, MASK_H = 466, 1227


def _mask():
    m = cv2.imread(str(ROOT / 'work/mountain/child_back_mask.png'), 0)
    return (m > 127).astype(np.uint8)


def _spline(pts, n=40):
    """Catmull-Rom through pts -> (n, 2)."""
    p = np.asarray(pts, np.float64)
    if len(p) == 2:
        return np.stack([np.linspace(p[0, 0], p[1, 0], n), np.linspace(p[0, 1], p[1, 1], n)], 1)
    P = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    segs = len(p) - 1
    for k in range(segs):
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        for u in np.linspace(0, 1, max(4, n // segs), endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    out.append(p[-1])
    return resample(np.array(out), n)[0]


def hair_halfwidth(y, m=None):
    """Half-width of the hair mass at mask row y (head contour + a little volume; widening below the head)."""
    m = _mask() if m is None else m
    def head_hw(yy):
        xs = np.where(m[int(np.clip(yy, 0, MASK_H - 1))])[0]
        return (xs.max() - xs.min()) / 2.0 if len(xs) else 0.0
    if y < 290:
        return head_hw(y) + 7
    hw0 = head_hw(289) + 7
    u = np.clip((y - 290) / 180.0, 0, 1)
    return hw0 + (150 - hw0) * (u ** 0.8)


def girl_slots(seed=3, n_strands=12):
    """Round 2: a true 白描 figure. [(kind, path (n,2) mask px, order, colour)]. Kinds: hair_lo (one long flowing
    stroke per strand, root on the crown: these stream), hair_up (the round of the head), tuft, tie (red), outline
    (long continuous contours), inner (a few folds), red (two light wash touches)."""
    m = _mask()
    r = rng(seed, 'girl2')
    CXm = 233.0
    slots = []
    HAIR_END = 470
    # hair: 12 long strands, roots spread along the crown, flowing down past the shoulders, paper between them
    for j in range(n_strands):
        f = -1 + 2 * (j + 0.5) / n_strands
        y0 = 26 + 34 * abs(f) ** 1.5 + r.uniform(-5, 5)
        y_end = HAIR_END + 55 - 40 * abs(f) ** 2 + r.uniform(-22, 22)     # down to the shoulder blades
        ys = np.linspace(y0, y_end, 10)
        ph = r.uniform(0, 6.28)
        xs = []
        for k, y in enumerate(ys):
            v = (y - y0) / (y_end - y0)
            hw = hair_halfwidth(y, m) * 0.93
            spread = 0.40 + 0.60 * smoothstep(0.0, 0.30, v)
            x = CXm + f * hw * spread + 5.0 * math.sin(v * 5.5 + ph) * smoothstep(0.2, 0.6, v)
            xs.append(x)
        path = _spline(np.stack([np.array(xs), ys], 1), 60)
        slots.append(('hair_lo', path, 0.42 + 0.30 * (1 - abs(f)) + r.uniform(0, 0.12), 'ink'))
    # the round of the head: one arc over the crown, the two sides down into the hair
    top = [(CXm + sd * (hair_halfwidth(y, m) + 1), y) for sd, y in ((-1, 80), (-1, 34), (-1, 8))]
    top = top + [(CXm, 1.0)] + [(CXm + (hair_halfwidth(y, m) + 1), y) for y in (8, 34, 80)]
    slots.append(('hair_up', _spline(top, 50), 0.36, 'ink'))
    for sd in (-1, 1):
        ys = np.linspace(70, 330, 8)
        xs = [CXm + sd * (hair_halfwidth(y, m) + 2) for y in ys]
        slots.append(('hair_up', _spline(np.stack([xs, ys], 1), 50), 0.38 + 0.01 * sd, 'ink'))
    # two little half-up ponytails, red ties
    for sd in (-1, 1):
        root = np.array([CXm + sd * 80, 98.0])
        tuft = _spline([root, root + [sd * 34, 10], root + [sd * 56, 44], root + [sd * 54, 86]], 30)
        slots.append(('tuft', tuft, 0.84 + 0.02 * sd, 'ink'))
        slots.append(('tie', _spline([root + [-sd * 5, -3], root + [sd * 7, 5]], 12), 0.95, 'red'))
    # body outline: long continuous contours below the hair
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=len)[:, 0, :].astype(np.float64)
    c = smooth_poly(np.vstack([c, c[:1]]), 8)
    keep = np.array([not (p[1] < HAIR_END - 40 and abs(p[0] - CXm) < hair_halfwidth(p[1], m) - 4) for p in c])
    idx = np.where(keep)[0]
    start = idx[np.argmax(np.diff(np.r_[idx, idx[0] + len(c)]) > 1)] + 1 if not keep.all() else 0
    c = np.roll(c, -start, 0)
    keep = np.roll(keep, -start)
    runs, cur = [], []
    for p, k in zip(c, keep):
        if k:
            cur.append(p)
        elif cur:
            runs.append(np.array(cur))
            cur = []
    if cur:
        runs.append(np.array(cur))
    for run in runs:
        if len(run) < 20:
            continue
        rs, L = resample(run, max(8, int(len(run) / 2)))
        npieces = max(1, int(round(L / 330)))
        b = np.linspace(0, len(rs) - 1, npieces + 1).astype(int)
        for a0, a1 in zip(b[:-1], b[1:]):
            seg = rs[a0 + (4 if a0 > 0 else 0):a1 + 1]
            if len(seg) >= 4:
                yc = seg[:, 1].mean()
                slots.append(('outline', resample(seg, 40)[0], 0.02 + 0.30 * (yc - 300) / 930 + r.uniform(0, 0.06),
                              'ink'))
    # a few folds
    inner = [
        [(106, 440), (96, 570), (78, 700)], [(360, 440), (370, 570), (388, 700)],      # arm against body
        [(60, 788), (150, 803), (233, 808), (318, 803), (406, 788)],                   # jacket hem
        [(233, 852), (231, 990), (236, 1122)],                                         # between the legs
        [(170, 560), (156, 650), (140, 740)],                                          # a fold of the back
    ]
    for pts in inner:
        p = _spline(pts, 40)
        slots.append(('inner', p, 0.10 + 0.30 * (p[:, 1].mean() - 400) / 800 + r.uniform(0, 0.1), 'ink'))
    # cinnabar: two light wash touches at the cuffs
    for pts in ([(4, 668), (24, 690), (48, 702)], [(462, 668), (442, 690), (418, 702)]):
        slots.append(('red', _spline(pts, 20), 0.88 + r.uniform(0, 0.05), 'red'))
    return slots


# ----------------------------------------------------------------------------------------------------------------
# the scene: where things are in the world (x, y = cliff plane px, z = 0 on the cliff, negative toward the camera)

FOCAL = 1700.0                      # 1080p px
GIRL_H = 480.0                      # world units
GIRL_X, GIRL_FEET, GIRL_Z = 6990.0, 944.0, -600.0
CAM0 = (7320.0, 640.0, -2000.0)     # H5 frame 0: the v3 framing (cliff zoom 0.85)
CAM1 = (7030.0, 700.0, -1600.0)     # H5 last frame: pushed in on her (cliff zoom 1.0)
T_H6 = H5_N / 24.0                  # sim time of H6 frame 0
# H6 events (sim seconds)
T_DETACH = T_H6 + 0.85
T_GUST = T_H6 + 1.15
T_LOOP = T_H6 + 1.55
T_GROW = T_H6 + 2.25
T_SAULT = T_H6 + 3.20
HERO_SCALE = 1.45                   # the loose strand: a long hair (its own curve, drawn out)


def girl_to_world(p):
    """mask px (466 x 1227) -> world (x, y) on the girl's plane (z = GIRL_Z)."""
    k = GIRL_H / MASK_H
    return np.stack([GIRL_X + (p[:, 0] - MASK_W / 2) * k, GIRL_FEET - (MASK_H - p[:, 1]) * k], 1)


def turning(p):
    d = np.diff(p, axis=0)
    a = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
    return float(a[-1] - a[0]) if len(a) > 1 else 0.0


def scene(seed=11):
    """Strokes, slots, assignment and schedule. Deterministic. Returns a dict (cached on disk)."""
    from shots._mountain import qianziwen
    from scipy.optimize import linear_sum_assignment
    cells = cliff_cells(qianziwen(160))
    # every stroke of every character the camera sees at any time in H5 (frame 0 is the widest)
    strokes = build_strokes(cells, (CAM0[0] - 1250, -100, CAM0[0] + 1250, 1400))
    S = len(strokes)
    r = rng(seed, 'scene')
    # peel times: the gale reaches the right columns first; within a column, top to bottom with scatter
    xs = np.array([s.cx for s in strokes])
    ys = np.array([s.cy for s in strokes])
    xn = (xs.max() - xs) / max(1.0, xs.max() - xs.min())
    t_peel = 0.14 + 1.30 * np.clip(xn - 0.36, 0, None) ** 1.1 / 0.64 ** 1.1 + 0.30 * (ys / 1300.0) + r.uniform(0, 0.35, S)
    t_peel = np.clip(t_peel, 0.14, 2.40)
    # the gale rises: a few strokes of the visible middle columns start lifting at once (f6-8)
    early = [i for i in range(S) if 7150 < xs[i] < 7450 and ys[i] < 800]
    for i in r.choice(early, size=min(12, len(early)), replace=False):
        t_peel[i] = r.uniform(0.06, 0.18)
    peel_dur = np.clip(np.array([s.L for s in strokes]) / 260.0, 0.06, 0.40) * r.uniform(0.8, 1.3, S)
    # which end lifts first: the upwind (right) end, or the top for a vertical stroke
    peel_from_end = np.array([1 if (s.med[-1, 0] - s.med[0, 0]) > 0.3 * abs(s.med[-1, 1] - s.med[0, 1]) or
                              (abs(s.med[-1, 0] - s.med[0, 0]) <= 0.3 * abs(s.med[-1, 1] - s.med[0, 1]) and
                               s.med[-1, 1] < s.med[0, 1]) else 0 for s in strokes])
    # slots
    sl = girl_slots()
    K = len(sl)
    order = np.argsort([o for _, _, o, _ in sl], kind='stable')
    t_arr = np.zeros(K)
    t_arr[order] = np.linspace(1.45, 3.20, K)
    slotL = np.array([resample(girl_to_world(p), 60)[1] for _, p, _, _ in sl])
    slotT = np.array([turning(girl_to_world(p)) for _, p, _, _ in sl])
    L = np.array([s.L for s in strokes])
    Tn = np.array([turning(s.med) for s in strokes])
    wid = np.array([s.width.mean() for s in strokes])
    cost = np.zeros((K, S))
    for k, (kind, p, o, col) in enumerate(sl):
        c = 3.0 * np.abs(np.log(L / slotL[k]))
        c += 0.6 * np.minimum(np.abs(np.abs(Tn) - abs(slotT[k])), 2.5)
        fl = t_arr[k] - t_peel
        c += 4.0 * np.clip(0.85 - fl, 0, None) + 1.5 * np.clip(fl - 2.1, 0, None)
        if kind in ('hair_up', 'hair_lo'):
            c += 0.08 * np.clip(wid - 6, 0, None)          # hair: the slenderer strokes
        if kind == 'red':
            c += 0.25 * np.clip(9 - wid, 0, None)          # colour: the broad ones
        if kind == 'tie':
            c += 0.0
        cost[k] = c
    # the hero strand: the long 乚 of 地 (a hooked stroke that springs back to its own curl when it is let go)
    hero = next((i for i, st in enumerate(strokes) if st.ch == '成' and st.si == 3), None)
    if hero is None:
        hero = int(np.argmax([st.L * abs(turning(st.med)) * (st.L > 110) for st in strokes]))
    lo = [k for k, (kd, p, o, c) in enumerate(sl) if kd == 'hair_lo']
    k_hero = min(lo, key=lambda k: girl_to_world(sl[k][1])[:, 0].mean())
    cost[:, hero] += 50
    cost[k_hero, :] += 50
    cost[k_hero, hero] = -1000
    ki, si = linear_sum_assignment(cost)
    assign = -np.ones(S, int)
    assign[si] = ki
    return dict(hero=hero, cells=cells, strokes=strokes, slots=sl, t_arr=t_arr, t_peel=t_peel, peel_dur=peel_dur,
                peel_from_end=peel_from_end, assign=assign, slotL=slotL)


WIDTH_K = {'hair_up': 0.52, 'hair_lo': 0.48, 'outline': 0.62, 'inner': 0.55, 'tuft': 0.6, 'tie': 1.0, 'red': 1.0}


PEAK_HW = {'hair_up': 3.6, 'hair_lo': 3.0, 'outline': 4.2, 'inner': 3.0, 'tuft': 2.9, 'tie': 4.2, 'red': 6.5}


def slot_pressure(kind, n, seed=0):
    """Half-width of the rails (world px) along a landed stroke: a 白描 line with brush pressure, a sharp pressed
    entry, thick-thin within the stroke, a tapering exit."""
    r = rng(seed, 'press')
    u = np.linspace(0, 1, n)
    entry = 0.45 + 0.55 * smoothstep(0.0, 0.07, u)
    body = 0.78 + 0.22 * np.sin(2 * np.pi * (u * r.uniform(0.9, 1.6)) + r.uniform(0, 6.28))
    exitp = 1 - 0.88 * smoothstep(0.62, 1.0, u) ** 0.9
    if kind in ('tie', 'red'):
        body = 0.9 + 0 * u
        exitp = 1 - 0.5 * smoothstep(0.7, 1.0, u)
    return PEAK_HW.get(kind, 2.4) * entry * body * exitp + 0.6


def slot_rails(st, path_mask, kind='outline'):
    """World rails (2, N, 3) for a stroke laid along a slot path (stroke head at the path's start), facing camera."""
    p = girl_to_world(path_mask)
    p, L = resample(p, 80)
    p = smooth_poly(p, 2)
    m, _ = resample(p, st.N)
    t = np.gradient(m, axis=0)
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
    n = np.stack([-t[:, 1], t[:, 0]], 1)
    # keep the stroke's handedness: its left rail stays on the left
    h = slot_pressure(kind, st.N, seed=int(abs(m[0, 0] * 7 + m[0, 1] * 13)) % 9973)
    R2 = np.stack([m + n * h[:, None], m - n * h[:, None]], 0)
    R = np.concatenate([R2, np.full((2, st.N, 1), GIRL_Z)], 2)
    return R


def scene_cached():
    import pickle
    p = WORK / 'sim/scene.pkl'
    src = os.path.getmtime(__file__)
    if p.exists() and os.path.getmtime(p) > src:
        return pickle.load(open(p, 'rb'))
    p.parent.mkdir(parents=True, exist_ok=True)
    sc = scene()
    pickle.dump(sc, open(p, 'wb'))
    return sc


# ----------------------------------------------------------------------------------------------------------------
# the simulation (torch; run in its own process)

SUBF = 6                                  # sub-frames per frame (motion blur)
STEPS = 20                                # sim steps per frame (480 Hz)
SUB_STEPS = (-5, -3, -1, 1, 3, 5)         # step offsets of the sub-frames around each frame time (shutter ~0.5)
N = Stroke.N


def gale(t):
    """Mean gale speed (world px/s, blowing toward -x) at sim time t."""
    up = smoothstep(-0.05, 0.75, t)
    return 120 + 640 * up - 260 * smoothstep(T_DETACH - 0.2, T_DETACH + 0.6, t)


GUSTS = [  # (time the front passes x0, x0, amplitude (fraction of gale), width px)
    (0.9, 8200, 0.55, 380), (1.6, 8000, 0.45, 300), (2.3, 7900, 0.5, 340), (3.05, 7600, 0.6, 320),
    (3.7, 7400, 0.5, 400), (4.4, 7000, 0.5, 300), (5.2, 6600, 0.45, 360), (6.1, 6200, 0.5, 400)]


class Wind:
    def __init__(self, torch, dev, seed=5):
        r = rng(seed, 'wind')
        M = 28
        lam = np.exp(r.uniform(np.log(110), np.log(650), M))
        k = r.normal(size=(M, 3))
        k /= np.linalg.norm(k, axis=1, keepdims=True)
        k *= (2 * np.pi / lam)[:, None]
        e = r.normal(size=(M, 3))
        e /= np.linalg.norm(e, axis=1, keepdims=True)
        amp = (lam / 650.0) ** 0.6
        amp /= np.sqrt((amp ** 2).sum())
        self.k = torch.tensor(k, dtype=torch.float32, device=dev)
        self.ke = torch.tensor(np.cross(k, e) / np.linalg.norm(k, axis=1, keepdims=True) * amp[:, None],
                               dtype=torch.float32, device=dev)
        self.ph = torch.tensor(r.uniform(0, 2 * np.pi, M), dtype=torch.float32, device=dev)
        self.om = torch.tensor(r.uniform(0.6, 2.4, M), dtype=torch.float32, device=dev)
        self.torch = torch

    def __call__(self, X, t, turb=0.75):
        """X (..., 3) -> wind velocity (..., 3)."""
        torch = self.torch
        U = gale(t)
        adv = torch.tensor([float(-U * 0.85 * t), 0.0, 0.0], dtype=torch.float32, device=X.device)          # turbulence rides the gale
        Xa = X - adv
        arg = Xa @ self.k.T + self.ph + self.om * t                             # (..., M)
        u = torch.cos(arg) @ self.ke                                            # divergence-free (curl of a sum)
        u = u * (U * turb)
        g = torch.zeros_like(X[..., 0])
        for (tg, x0, a, w) in GUSTS:
            xf = x0 - (U * 1.1) * (t - tg)                                      # the front travels with the gale
            g = g + a * torch.exp(-((X[..., 0] - xf) / w) ** 2)
        base = torch.zeros_like(X)
        base[..., 0] = -U * (1 + g)
        base[..., 1] = -0.06 * U * g                                            # gusts lift a little
        # off the wall: the flow peels away from the stone toward the camera
        zw = torch.exp(X[..., 2] / 160.0)                                       # 1 at the wall
        base[..., 2] = -(70 + 130 * g) * zw - 40
        return base + u


def _pairs(N):
    """Constraint index pairs over a ribbon of 2 rails x N (flattened index r * N + i), with kinds."""
    P, kind = [], []
    for r_ in (0, 1):
        for i in range(N - 1):
            P.append((r_ * N + i, r_ * N + i + 1)); kind.append(0)          # stretch along
    for i in range(N):
        P.append((i, N + i)); kind.append(1)                                # across
    for i in range(N - 1):
        P.append((i, N + i + 1)); kind.append(2)                            # shear
        P.append((N + i, i + 1)); kind.append(2)
    for r_ in (0, 1):
        for i in range(N - 2):
            P.append((r_ * N + i, r_ * N + i + 2)); kind.append(3)          # bend
        for i in range(N - 3):
            P.append((r_ * N + i, r_ * N + i + 3)); kind.append(4)          # bend, longer
    return np.array(P), np.array(kind)


def simulate(out=None, dev='cuda'):
    import torch
    torch.backends.cuda.matmul.allow_tf32 = False
    sc = scene_cached()
    strokes, slots, assign = sc['strokes'], sc['slots'], sc['assign']
    S = len(strokes)
    M2 = 2 * N
    # rest shapes (own) and slot shapes
    own = np.zeros((S, 2, N, 3))
    tgt = np.zeros((S, 2, N, 3))
    for s, st in enumerate(strokes):
        R = st.rails()
        own[s, :, :, :2] = R
        if assign[s] >= 0:
            tgt[s] = slot_rails(st, slots[assign[s]][1], slots[assign[s]][0])
        else:
            tgt[s] = own[s]
    # mass: ink load grows with the stroke's width (the pressed head is heavier); drag area with width
    wid = np.stack([np.r_[st.width] for st in strokes])                       # (S, N)
    seg = np.array([st.L / (N - 1) for st in strokes])[:, None]
    area = np.repeat((wid * seg / 2)[:, None], 2, 1)                           # (S, 2, N)
    mass = np.repeat(((wid / 8.0) ** 1.5 * seg / 2)[:, None], 2, 1) * 8.0
    # release time per particle (peel from one end)
    u = np.linspace(0, 1, N)
    t_rel = np.zeros((S, 2, N))
    for s in range(S):
        uu = (1 - u) if sc['peel_from_end'][s] else u
        t_rel[s] = sc['t_peel'][s] + sc['peel_dur'][s] * uu[None]
    kind_of = {k: kd for k, (kd, *_r) in enumerate(slots)}
    is_hair = np.array([assign[s] >= 0 and kind_of[assign[s]] in ('hair_up', 'hair_lo', 'tuft') for s in range(S)])
    is_lo = np.array([assign[s] >= 0 and kind_of[assign[s]] in ('hair_lo', 'tuft') for s in range(S)])
    t_arr = np.array([sc['t_arr'][assign[s]] if assign[s] >= 0 else 99.0 for s in range(S)])
    hero = sc['hero']
    T = lambda a: torch.tensor(a, dtype=torch.float32, device=dev)
    own_t, tgt_t = T(own.reshape(S, M2, 3)), T(tgt.reshape(S, M2, 3))
    hc = own[hero].reshape(M2, 3).mean(0)
    own_hero = T((own[hero].reshape(M2, 3) - hc) * HERO_SCALE + hc)
    X = own_t.clone()
    V = torch.zeros_like(X)
    mass_t = T(mass.reshape(S, M2))
    area_t = T(area.reshape(S, M2))
    trel_t = T(t_rel.reshape(S, M2))
    tarr_t = T(t_arr)[:, None]
    tpeel_t = T(sc['peel_from_end'] * 0 + sc['t_peel'])[:, None]
    assigned = T((assign >= 0).astype(np.float32))[:, None]
    hair_t = T(is_hair.astype(np.float32))[:, None]
    lo_t = T(is_lo.astype(np.float32))[:, None]
    hero_t = torch.zeros(S, 1, device=dev)
    hero_t[hero] = 1
    pi, kind = _pairs(N)
    pi_t = torch.tensor(pi, device=dev)
    stiff = T(np.array([1.0, 1.0, 0.7, 0.35, 0.18])[kind])
    ncon = np.zeros(M2)
    np.add.at(ncon, pi[:, 0], 1)
    np.add.at(ncon, pi[:, 1], 1)
    ncon_t = T(ncon)[None, :, None]
    root_t = torch.zeros(1, M2, device=dev)          # the root of a hair: the first two pairs
    for i in range(5):                               # round 2: the hair lies on the scalp, then flies free
        root_t[0, i] = 1
        root_t[0, N + i] = 1
    wind = Wind(torch, dev)
    dt = 1.0 / (FPS * STEPS)
    t0 = -6 * dt
    nsteps = NFR * STEPS + 12
    rec = np.zeros((NFR, SUBF, S, M2, 3), np.float32)
    want = {}
    for f in range(NFR):
        for k, o in enumerate(SUB_STEPS):
            want[f * STEPS + o] = (f, k)
    grav = T([0.0, 140.0, 0.0])
    up = T([0.0, 0.0, -1.0])
    lift_given = torch.zeros(S, M2, dtype=torch.bool, device=dev)
    loop_c = loop_v = loop_t0 = None
    for n_ in range(nsteps):
        t = t0 + n_ * dt
        released = (trel_t <= t)
        newly = released & ~lift_given
        if newly.any():
            V[newly] = V[newly] + T([-60.0, -20.0, -160.0])
            lift_given |= newly
        # morph of the rest shape: own curve -> slot curve during the approach; the hero goes back to its own
        a_steer = torch.clamp((t - (tpeel_t + 0.25)) / torch.clamp(tarr_t - tpeel_t - 0.25, min=0.3), 0, 1)
        morph = torch.clamp((a_steer - 0.35) / 0.65, 0, 1)
        morph = morph * morph * (3 - 2 * morph) * assigned
        if t > T_DETACH:
            back = min(1.0, (t - T_DETACH) / 0.5)
            morph = morph * (1 - hero_t * back)
        rest = own_t * (1 - morph[..., None]) + tgt_t * morph[..., None]
        if t > T_DETACH:
            rest = rest.clone()
            rest[hero] = own_hero * back + tgt_t[hero] * (1 - back)
        # forces
        Xr = X.view(S, 2, N, 3)
        tng = torch.zeros_like(Xr)
        tng[:, :, 1:-1] = Xr[:, :, 2:] - Xr[:, :, :-2]
        tng[:, :, 0] = Xr[:, :, 1] - Xr[:, :, 0]
        tng[:, :, -1] = Xr[:, :, -1] - Xr[:, :, -2]
        tng = tng.mean(1, keepdim=True).expand(-1, 2, -1, -1)
        acr = (Xr[:, 0] - Xr[:, 1])[:, None].expand(-1, 2, -1, -1)
        nrm = torch.cross(tng, acr, dim=-1)
        nrm = nrm / (nrm.norm(dim=-1, keepdim=True) + 1e-6)
        nrm = nrm.reshape(S, M2, 3)
        tu = tng / (tng.norm(dim=-1, keepdim=True) + 1e-6)
        tu = tu.reshape(S, M2, 3)
        landed = torch.clamp((t - tarr_t) / 0.25, 0, 1) * assigned                  # (S, 1)
        sw = float(smoothstep(T_H6 - 0.55, T_H6 - 0.2, t))                          # her hair starts to swing
        tk = float(smoothstep(T_H6 - 0.12, T_H6 + 0.30, t))                         # the gale takes it
        shelter = 1 - 0.85 * landed * (1 - hair_t * 0.55)                           # her own strokes, held
        shelter = shelter + lo_t * landed * (0.30 * sw + 1.2 * tk)                   # ... not her loose hair
        Uw = wind(X, t)
        if tk > 0:                             # in her lee the flow is steadier: the hair streams and waves
            calm = T([1.0, 0.7, 0.45]) * (hair_t * landed)[..., None] + (1 - hair_t * landed)[..., None]
            Uw = Uw * calm
            # her wake: the gale sheds eddies off her head, so the streaming hair waves (a travelling transverse flow)
            ph_ = X[..., 0] * (2 * np.pi / 95.0) + t * (2 * np.pi * 3.2)
            wk = (hair_t * landed)[..., None] * tk
            Uw = Uw + wk * torch.stack([0 * ph_, 330 * torch.sin(ph_), 160 * torch.cos(ph_ * 0.7)], -1)
        vr = Uw - V
        vn = (vr * nrm).sum(-1, keepdim=True)
        vnv = vn * nrm
        vt = vr - vnv
        vtl = (vt * tu).sum(-1, keepdim=True) * tu
        drag = (0.010 * vn.abs() * vnv + 0.0012 * vtl.norm(dim=-1, keepdim=True) * vtl + 0.30 * vr +
                0.12 * (vt - vtl))
        acc = drag * (area_t / mass_t)[..., None] * shelter[..., None] + grav
        # steering to the slot: a spring-damper that strengthens over the flight; strong once landed
        ks = (a_steer ** 3) * 160 + landed * 240
        if sw > 0:
            ks = ks * (1 - lo_t * (1 - root_t) * (0.80 * sw + 0.19 * tk)) * (1 - (hair_t - lo_t) * 0.3 * tk) \
                * (1 - hero_t * float(t > T_DETACH))
        cs = 2 * 0.32 * torch.sqrt(ks + 1e-6)
        acc = acc + (ks[..., None] * (tgt_t - X) - cs[..., None] * V) * assigned[..., None]
        # the hero: alive from T_GROW: a push to the left (he leaps), then turning over (the somersault)
        if t > T_GROW:
            # alive: he leaps (a push at the root end, so the head leads and the tail trails), then turns over
            g = min(1.0, (t - T_GROW) / 0.5)
            w_ = torch.full((1, M2, 1), 0.3, device=dev)
            w_[0, :4] = 1
            w_[0, N:N + 4] = 1
            push = T(np.array([-1.0, -0.30, 0.0]) * 3400 * g)
            acc = acc + hero_t[..., None] * w_ * push
            if t > T_SAULT:
                us = (t - T_SAULT) / 0.72
                if us < 1:
                    alpha_ = -2 * np.pi * 2.4 * math.sin(np.pi * us) * (np.pi / 2) / 0.72
                    ch = X[hero].mean(0)
                    r_ = X[hero] - ch
                    spin = torch.stack([-r_[:, 1], r_[:, 0], 0 * r_[:, 0]], -1) * alpha_
                    acc[hero] = acc[hero] + spin
        # the hero's own events: a gust pulls it straight, an eddy turns it through a loop
        if t > T_DETACH:
            c = X[hero].mean(0)
            gs = np.exp(-((t - (T_GUST + 0.15)) / 0.2) ** 2)
            # a coherent vortex: for ~0.6 s the air around the strand turns about a centre that rides the gale,
            # so its path makes one loop (and the strand turns over with it)
            wl = float(smoothstep(T_LOOP - 0.05, T_LOOP + 0.08, t) * (1 - smoothstep(T_LOOP + 0.56, T_LOOP + 0.70, t)))
            if t >= T_LOOP and loop_c is None:
                loop_c = (c + T([0.0, -70.0, 0.0])).clone()
                loop_v = V[hero].mean(0).clone()
                loop_t0 = t
            eddy = torch.zeros_like(X[hero])
            if loop_c is not None and wl > 0:
                cv_ = loop_c + loop_v * (t - loop_t0)
                dX = X[hero] - cv_
                OM = -2 * np.pi / 0.62
                u_v = loop_v + torch.stack([-dX[:, 1], dX[:, 0], 0 * dX[:, 0]], -1) * OM
                eddy = 10.0 * (u_v - V[hero]) * wl / 8.0
            # a pull at the light end only: the heavy head lags, the strand snaps straight
            tail = torch.zeros(M2, 1, device=dev)
            tail[N - 7:N] = 1
            tail[2 * N - 7:] = 1
            pull = T([-3800.0 * gs, -250.0 * gs, 0.0])
            acc[hero] = acc[hero] + pull * tail + eddy * 8.0
        if t > T_DETACH:
            zt = -600 - 300 * min(1.0, (t - T_DETACH) / 1.0)
            acc[hero, :, 2] += 5.0 * (zt - X[hero, :, 2]) - 2.0 * V[hero, :, 2]
            acc[hero, :, 1] += -175.0 - 5.0 * (X[hero, :, 1].mean() - 660.0) - 1.6 * V[hero, :, 1].mean()
            if T_LOOP + 0.6 < t < T_LOOP + 1.0:                         # after the eddy the gale takes it again
                acc[hero, :, 0] += 5.0 * (-gale(t) * 0.8 - V[hero, :, 0].mean())
        if t > T_H6 - 0.3:
            lift = min(1.0, (t - (T_H6 - 0.3)) / 0.6)
            acc = acc + (1 - assigned[..., None]) * T([-200.0, -700.0, 250.0]) * lift
        # pins: not yet released -> held on the stone
        V = V + acc * dt
        Xp = X + V * dt
        pin = ~released
        Xp = torch.where(pin[..., None], own_t, Xp)
        # hair roots held on her head once landed (until the hero is let go)
        hold = (landed >= 1) & (hair_t > 0) & (root_t > 0) & ~((hero_t > 0) & (t > T_DETACH))
        Xp = torch.where(hold[..., None], tgt_t, Xp)
        winv = (~pin & ~hold).float()[..., None] / mass_t[..., None]
        # constraints
        rl = (rest[:, pi_t[:, 1]] - rest[:, pi_t[:, 0]]).norm(dim=-1)
        for it in range(6):
            a, b = Xp[:, pi_t[:, 0]], Xp[:, pi_t[:, 1]]
            wa, wb = winv[:, pi_t[:, 0]], winv[:, pi_t[:, 1]]
            d = b - a
            ln = d.norm(dim=-1, keepdim=True) + 1e-6
            C = (ln - rl[..., None]) / ln * d * stiff[None, :, None] / (wa + wb + 1e-9)
            dp = torch.zeros_like(Xp)
            dp.index_add_(1, pi_t[:, 0], C * wa)
            dp.index_add_(1, pi_t[:, 1], -C * wb)
            Xp = Xp + 1.5 * dp / ncon_t
            # shape matching toward the (morphing) rest shape: the stroke's spring
            m = (winv > 0).float() * mass_t[..., None] + 1e-6
            cx = (Xp * m).sum(1, keepdim=True) / m.sum(1, keepdim=True)
            cr = (rest * m).sum(1, keepdim=True) / m.sum(1, keepdim=True)
            A = ((Xp - cx) * m).transpose(1, 2) @ (rest - cr)
            Uu, Ss, Vh = torch.linalg.svd(A)
            dd = torch.sign(torch.det(Uu @ Vh))
            Dm = torch.ones(S, 3, device=dev)
            Dm[:, 2] = dd
            Rm = Uu @ torch.diag_embed(Dm) @ Vh
            G = (rest - cr) @ Rm.transpose(1, 2) + cx
            alpha = (0.035 + 0.10 * morph[..., None] * (1 - hair_t[..., None] * 0.6)) * (1 - 0.8 * tk * lo_t[..., None])
            Xp = Xp + (G - Xp) * alpha * (winv > 0).float()
            Xp = torch.where(pin[..., None], own_t, Xp)
            Xp = torch.where(hold[..., None], tgt_t, Xp)
        # the stone is solid
        Xp[..., 2] = torch.clamp(Xp[..., 2], max=-0.5) * (~pin).float() + Xp[..., 2] * pin.float()
        V = (Xp - X) / dt
        V = V * 0.999
        X = Xp
        if n_ - 6 in want or (n_ - 6) in want:
            f, k = want[n_ - 6]
            rec[f, k] = X.cpu().numpy()
    out = out or (WORK / 'sim/sim.npz')
    np.savez(out, rec=rec.astype(np.float32), hero=hero, t_rel=t_rel.astype(np.float32), assign=assign,
             t_arr=t_arr.astype(np.float32))
    return out


# ----------------------------------------------------------------------------------------------------------------
# bake: the flying strokes, rendered per frame to a transmittance layer

RED_K = -np.log(np.clip(np.array([0.74, 0.16, 0.10]), 0.02, 0.98))
INK_KV = np.array([3.05, 3.12, 3.2])
COC_K, COC_MAX = 3.0, 11.0
BUCKETS = [0.0, 1.3, 2.6, 4.6, 7.5, 11.0]


def stroke_colour(sc, t):
    """(S,) redness at time t: the carved paste lifts red; strokes bound for ink lines darken to ink in flight."""
    S = len(sc['strokes'])
    r = rng(2, 'col').uniform(0, 1, S)
    red = np.ones(S)
    for s in range(S):
        k = sc['assign'][s]
        stay = (k >= 0 and sc['slots'][k][3] == 'red') or (k < 0 and r[s] < 0.38)
        if not stay:
            u = (t - (sc['t_peel'][s] + 0.10)) / 0.85
            red[s] = 1 - (np.clip(u, 0, 1) ** 1.5 * (3 - 2 * np.clip(u, 0, 1)))
    return red


def hero_thick(t):
    """How much the hero strand's root end has thickened (0..1) at time t (the monkey's body growing)."""
    return float(_ease((t - T_GROW) / 0.55))


def bake(size=(1920, 1080), frames=None, out_dir=None, dev='cuda', exclude_hero_after=None, only=None, tag=''):
    """Render the strokes for frames -> PNG transmittance layers (uint8 RGB, 1 = bare paper).
    only: None (all), 'hero' (the hero strand alone), 'nohero'."""
    import torch
    import torch.nn.functional as Fn
    W, H = size
    s_ = W / 1920.0
    sc = scene_cached()
    d = np.load(WORK / 'sim/sim.npz')
    rec, hero, t_rel = d['rec'], int(d['hero']), d['t_rel']
    cam = np.load(WORK / 'sim/cam.npy')
    strokes = sc['strokes']
    S = len(strokes)
    out_dir = out_dir or (WORK / f'bake/{W}x{H}{tag}')
    os.makedirs(out_dir, exist_ok=True)
    atl_p = WORK / 'sim/atlas.npy'
    if atl_p.exists() and os.path.getmtime(atl_p) > os.path.getmtime(WORK / 'sim/scene.pkl'):
        atlas = np.load(atl_p)
    else:
        atlas = np.stack([stroke_atlas(st) for st in strokes])
        np.save(atl_p, atlas)
    tA = torch.tensor(atlas, device=dev).reshape(S, -1)
    trel = torch.tensor(t_rel[:, 0], device=dev)
    unas = torch.tensor((sc['assign'] < 0).astype(np.float32), device=dev)
    dens = torch.tensor([0.5 if (k >= 0 and sc['slots'][k][0] == 'red') else 1.0 for k in sc['assign']],
                        dtype=torch.float32, device=dev)                              # (S, N): release time along u
    # which face is the top: the face that looked at the camera on the stone (normal toward -z)
    INKK = torch.tensor(INK_KV, dtype=torch.float32, device=dev)
    REDK = torch.tensor(RED_K, dtype=torch.float32, device=dev)
    frames = range(NFR) if frames is None else frames
    SS = 2
    HH, WW = H * SS, W * SS
    nb = len(BUCKETS)
    gk = {}
    for f in frames:
        Tacc = torch.zeros(3, H, W, device=dev)
        # sub-frames, with interpolated in-betweens where things move fast (no strobing in the motion blur)
        subs = []
        Xs = [torch.tensor(rec[f, k], device=dev) for k in range(SUBF)]
        for k in range(SUBF - 1):
            c0, c1 = cam[f, k], cam[f, k + 1]
            def scr(Xk, c):
                dz = (Xk[..., 2] - float(c[2])).clamp(min=60)
                return torch.stack([(Xk[..., 0] - float(c[0])) / dz, (Xk[..., 1] - float(c[1])) / dz], -1) * FOCAL * s_
            dmv = (scr(Xs[k + 1], c1) - scr(Xs[k], c0)).norm(dim=-1)
            ok = (Xs[k][..., 2] - float(c0[2])) > 60
            dmax = float(dmv[ok].max()) if ok.any() else 0.0
            n_int = int(min(10, max(1, math.ceil(dmax / 1.6))))
            for j in range(n_int):
                a = j / n_int
                subs.append(((f * STEPS + SUB_STEPS[k] * (1 - a) + SUB_STEPS[k + 1] * a) / (FPS * STEPS),
                             c0 * (1 - a) + c1 * a, Xs[k] * (1 - a) + Xs[k + 1] * a))
        subs.append(((f * STEPS + SUB_STEPS[-1]) / (FPS * STEPS), cam[f, -1], Xs[-1]))
        for (t, c, Xf) in subs:
            X = Xf.reshape(S, 2, N, 3)
            red = torch.tensor(stroke_colour(sc, t), dtype=torch.float32, device=dev)
            # project rails
            dz = X[..., 2] - float(c[2])
            sx = (W / 2 + FOCAL * s_ * (X[..., 0] - float(c[0])) / dz.clamp(min=1e-3)) * SS
            sy = (H / 2 + FOCAL * s_ * (X[..., 1] - float(c[1])) / dz.clamp(min=1e-3)) * SS
            # screen extents per stroke -> sample counts
            mx, my = sx.mean(1), sy.mean(1)                                       # median (S, N)
            seg = torch.sqrt((mx[:, 1:] - mx[:, :-1]) ** 2 + (my[:, 1:] - my[:, :-1]) ** 2).sum(1)
            wpx = torch.sqrt((sx[:, 0] - sx[:, 1]) ** 2 + (sy[:, 0] - sy[:, 1]) ** 2).max(1).values
            thick = torch.ones(S, device=dev)
            g = hero_thick(t)
            if g > 0:
                thick[hero] = 1 + 2.2 * g
            wpx = wpx * thick
            fl = lambda a: a.reshape(S, -1)
            vis = (fl(dz).min(1).values > 60) & (fl(sx).max(1).values > -200 * SS) & \
                  (fl(sx).min(1).values < (W + 200) * SS) & (fl(sy).max(1).values > -200 * SS) & \
                  (fl(sy).min(1).values < (H + 200) * SS)
            vis &= trel.min(1).values <= t                                       # something of it has lifted
            if only == 'hero':
                vis &= torch.arange(S, device=dev) == hero
            elif only == 'nohero':
                vis &= torch.arange(S, device=dev) != hero
            nu = (seg * 2.2 + 3).clamp(max=6000).long()
            nbv = (wpx * 2.2 + 3).clamp(max=1500).long()
            nu[~vis] = 0
            nbv[~vis] = 0
            cnt = nu * nbv
            tot = int(cnt.sum())
            if tot == 0:
                continue
            sid = torch.repeat_interleave(torch.arange(S, device=dev), cnt)
            start = torch.cumsum(cnt, 0) - cnt
            loc = torch.arange(tot, device=dev) - start[sid]
            nbs = nbv[sid]
            iu = (loc // nbs).float()
            ib = (loc % nbs).float()
            u = iu / (nu[sid] - 1).float()
            b = ib / (nbs - 1).float() * 2 - 1
            # Catmull-Rom along the rails
            fi = u * (N - 1)
            i1 = fi.floor().long().clamp(0, N - 2)
            tt_ = (fi - i1.float())[:, None]
            i0, i2, i3 = (i1 - 1).clamp(0, N - 1), i1 + 1, (i1 + 2).clamp(0, N - 1)
            def cr(Pr):
                p0, p1, p2, p3 = Pr[sid, i0], Pr[sid, i1], Pr[sid, i2], Pr[sid, i3]
                return 0.5 * ((2 * p1) + (-p0 + p2) * tt_ + (2 * p0 - 5 * p1 + 4 * p2 - p3) * tt_ ** 2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * tt_ ** 3)
            L = cr(X[:, 0])
            R = cr(X[:, 1])
            Mid = (L + R) / 2
            th = thick[sid][:, None]
            P = Mid + (L - R) / 2 * b[:, None]
            bt = b * th.squeeze(1)                                               # atlas lookup coordinate
            # normal (face orientation) from the local frame
            Ln, Rn = X[:, 0], X[:, 1]
            tg = (Ln[sid, i2] + Rn[sid, i2]) - (Ln[sid, i1] + Rn[sid, i1])
            ac = L - R
            nrm = torch.cross(tg, ac, dim=-1)
            view = P - torch.tensor(c, dtype=torch.float32, device=dev)
            back = ((nrm * view).sum(-1) > 0).float()                             # top face has normal toward -z
            dzp = (P[:, 2] - float(c[2])).clamp(min=1e-3)
            px = (W / 2 + FOCAL * s_ * (P[:, 0] - float(c[0])) / dzp) * SS
            py = (H / 2 + FOCAL * s_ * (P[:, 1] - float(c[1])) / dzp) * SS
            # atlas
            au = u * (ATLAS_S - 1)
            ab = ((bt.clamp(-1.6, 1.6) + 1) / 2) * (ATLAS_B - 1)
            inb = (ab >= 0) & (ab <= ATLAS_B - 1)
            ab = ab.clamp(0, ATLAS_B - 1)
            a0, b0 = au.floor().long().clamp(0, ATLAS_S - 2), ab.floor().long().clamp(0, ATLAS_B - 2)
            fa, fb = au - a0.float(), ab - b0.float()
            base = sid * (ATLAS_S * ATLAS_B)
            def at(bb, aa):
                return tA.view(-1)[base + bb * ATLAS_S + aa]
            alpha = ((1 - fa) * (1 - fb) * at(b0, a0) + fa * (1 - fb) * at(b0, a0 + 1) +
                     (1 - fa) * fb * at(b0 + 1, a0) + fa * fb * at(b0 + 1, a0 + 1)) * inb.float()
            # released yet? (the part still on the stone is the carving's fill)
            tr = trel[sid, i1] * (1 - tt_[:, 0]) + trel[sid, i2] * tt_[:, 0]
            alpha = alpha * (tr <= t).float()
            alpha = alpha * (1 + 0.28 * back) * dens[sid]                         # the underside, darker
            if t > T_H6 - 0.2:                                                    # the loose strokes go to mist
                fade = float(_ease((t - (T_H6 - 0.2)) / 1.0))
                alpha = alpha * (1 - fade * unas[sid])
            # the hero thickening: a fuller, wetter head
            keep = (alpha > 0.01) & (px >= 0) & (px < WW - 1) & (py >= 0) & (py < HH - 1)
            if keep.sum() == 0:
                continue
            alpha, px, py, sid_k, dzk = alpha[keep], px[keep], py[keep], sid[keep], dzp[keep]
            rr = red[sid_k]
            # depth of field
            dfoc = float(GIRL_Z - c[2])
            coc = (COC_K * (dfoc / dzk - 1).abs()).clamp(max=COC_MAX) * s_
            bk = torch.bucketize(coc / s_, torch.tensor(BUCKETS[1:], device=dev) - 0.65)
            buf = torch.zeros(nb * 2, HH * WW, device=dev)
            pix = py.long() * WW + px.long()
            buf_i = buf.view(-1)
            idx_ink = (bk * 2) * (HH * WW) + pix
            idx_red = (bk * 2 + 1) * (HH * WW) + pix
            buf_i.scatter_reduce_(0, idx_ink, alpha * (1 - rr), 'amax')
            buf_i.scatter_reduce_(0, idx_red, alpha * rr, 'amax')
            img = Fn.avg_pool2d(buf.view(1, nb * 2, HH, WW), SS).view(nb, 2, H, W)
            Dk = torch.zeros(2, H, W, device=dev)
            for j in range(nb):
                if float(img[j].max()) <= 0:
                    continue
                sg = BUCKETS[j] * 0.5 * s_
                if sg > 0.3:
                    rad = int(math.ceil(sg * 3))
                    if (rad, sg) not in gk:
                        xk = torch.arange(-rad, rad + 1, device=dev, dtype=torch.float32)
                        kk = torch.exp(-xk ** 2 / (2 * sg * sg))
                        gk[(rad, sg)] = kk / kk.sum()
                    kk = gk[(rad, sg)]
                    im = img[j][:, None]
                    im = Fn.conv2d(Fn.pad(im, (rad, rad, 0, 0), mode='replicate'), kk.view(1, 1, 1, -1))
                    im = Fn.conv2d(Fn.pad(im, (0, 0, rad, rad), mode='replicate'), kk.view(1, 1, -1, 1))
                    Dk += im[:, 0]
                else:
                    Dk += img[j]
            Tk = torch.exp(-Dk[0][None] * INKK[:, None, None]) * torch.exp(-Dk[1][None] * 0.80 * REDK[:, None, None])
            Tacc += Tk - 1
        Tacc = Tacc / len(subs) + 1
        im = (Tacc.clamp(0, 1) * 255 + 0.5).byte().permute(1, 2, 0).cpu().numpy()
        cv2.imwrite(str(out_dir / f'f{f:04d}.png'), im[..., ::-1])
    return out_dir


# ----------------------------------------------------------------------------------------------------------------
# camera

def _ease(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def camera_track(rec, hero):
    """(NFR, SUBF, 3) camera positions (cx, cy, cz). H5: the push in on her (accelerating as she completes). H6: a
    follower (critically damped spring) on the hero strand, which lets go when he somersaults out."""
    nf = rec.shape[0]
    ts = np.array([[(f * STEPS + o) / (FPS * STEPS) for o in SUB_STEPS] for f in range(nf)])
    hx = rec[:, :, hero, :, 0].mean(-1)
    hy = rec[:, :, hero, :, 1].mean(-1)
    out = np.zeros(ts.shape + (3,))
    # H5 push: slow at first, gathering as she completes (ends with a gentle velocity that H6 carries on)
    def h5(t):
        u = np.clip(t / T_H6, 0, 1)
        e = 0.62 * u ** 2 + 0.38 * _ease(u)
        return np.array([CAM0[i] + (CAM1[i] - CAM0[i]) * e for i in range(3)]), \
            np.array([(CAM1[i] - CAM0[i]) * (1.24 * u + 0.38 * 6 * u * (1 - u)) / T_H6 for i in range(3)])
    # H6 follower, integrated at the sim rate
    dt = 1.0 / (FPS * STEPS)
    p, v = h5(T_H6)
    p = p.copy()
    v = v.copy()
    track = {}
    tt = T_H6
    t_end = (nf * STEPS + 6) / (FPS * STEPS)
    hxf = hx.reshape(-1)
    hyf = hy.reshape(-1)
    tsf = ts.reshape(-1)
    order = np.argsort(tsf)
    hzf = rec[:, :, hero, :, 2].mean(-1).reshape(-1)
    def gsm(a, sig=70):
        k = np.exp(-0.5 * (np.arange(-4 * sig, 4 * sig + 1) / sig) ** 2)
        k /= k.sum()
        o_ = np.argsort(tsf)
        out_ = a.copy()
        out_[o_] = np.convolve(np.pad(a[o_], 4 * sig, mode='edge'), k, mode='same')[4 * sig:-4 * sig]
        return out_
    hxf, hyf = gsm(hxf), gsm(hyf)                                   # the camera rides the flight, not the loop
    I = lambda tq, a: np.interp(tq, tsf[order], a[order])
    X_DES, Y_DES = 1010.0, 560.0                                     # where the hero sits in frame (1080p px)
    while tt <= t_end + 1e-9:
        dz = I(tt, hzf) - p[2]
        X = I(tt, hxf) - (X_DES - 960) * dz / FOCAL
        Y = I(tt, hyf) - (Y_DES - 540) * dz / FOCAL
        vX = (I(tt + 0.05, hxf) - I(tt - 0.05, hxf)) / 0.1
        vY = (I(tt + 0.05, hyf) - I(tt - 0.05, hyf)) / 0.1
        w = _ease((tt - (T_DETACH - 0.3)) / 0.8)
        let = _ease((tt - (T_SAULT + 0.05)) / 0.4)                      # he outruns the camera
        dtt = max(0.0, tt - T_H6)
        tx = (1 - w) * (CAM1[0] - 130 * dtt ** 1.6) + w * X
        vtx = (1 - w) * (-208 * dtt ** 0.6) + w * vX
        ty = (1 - w) * CAM1[1] + w * Y
        vty = w * vY
        om = 3.0
        ax = om * om * (tx - p[0]) + 2 * om * (vtx - v[0])
        ay = om * om * (ty - p[1]) + 2 * om * (vty - v[1])
        ax = (1 - let) * ax - let * 2.5 * v[0]
        ay = (1 - let) * ay - let * 2.5 * v[1]
        v[0] += ax * dt
        v[1] += ay * dt
        v[2] *= np.exp(-dt * 4.0)
        p += v * dt
        if p[1] > 740:
            p[1], v[1] = 740.0, min(v[1], 0.0)
        lo_y = 560.0 if tt < T_H6 + 1.2 else 260.0                # (bare paper above the cliff canvas by then)
        if p[1] < lo_y:
            p[1], v[1] = lo_y, max(v[1], 0.0)
        track[round(tt * FPS * STEPS)] = p.copy()
        tt += dt
    for f in range(nf):
        for k, o in enumerate(SUB_STEPS):
            t = ts[f, k]
            if t <= T_H6:
                out[f, k] = h5(t)[0]
            else:
                out[f, k] = track[min(track, key=lambda q: abs(q - round(t * FPS * STEPS)))] \
                    if round(t * FPS * STEPS) not in track else track[round(t * FPS * STEPS)]
    return out


def project(X, cam, W=1920, H=1080):
    """World (..., 3) -> screen x, y (px at W) and distance; cam = (cx, cy, cz)."""
    s = W / 1920.0
    d = X[..., 2] - cam[2]
    x = W / 2 + FOCAL * s * (X[..., 0] - cam[0]) / np.maximum(d, 1e-3)
    y = H / 2 + FOCAL * s * (X[..., 1] - cam[1]) / np.maximum(d, 1e-3)
    return x, y, d


def cliff_zoom(cam):
    """zoom of the cliff plane (z = 0) for shots._mountain.view at this camera."""
    return FOCAL / (0 - cam[2])


def _main():
    cmd = sys.argv[1]
    if cmd == 'sim':
        import time
        t = time.time()
        print(simulate(), time.time() - t)
        d = np.load(WORK / 'sim/sim.npz')
        np.save(WORK / 'sim/cam.npy', camera_track(d['rec'], int(d['hero'])))
    elif cmd == 'bake':
        import time
        t = time.time()
        w, h = [int(v) for v in sys.argv[2].split('x')]
        fr = None
        only = None
        tag = ''
        for a in sys.argv[3:]:
            if a.startswith('frames='):
                v = a[7:]
                fr = list(range(*[int(q) for q in v.split(':')])) if ':' in v else [int(q) for q in v.split(',')]
            if a.startswith('only='):
                only = a[5:]
                tag = '_' + only
        print(bake((w, h), fr, only=only, tag=tag), time.time() - t)




if __name__ == '__main__':
    from shots import _book4_strokes as _M
    _M._main()

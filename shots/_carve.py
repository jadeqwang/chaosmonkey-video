"""shots/_carve.py: v3 carving helpers for the BOOK team's mountain shots (REVISION_V3 §3.1, §3.2).

A light, time-varying cousin of tools.ink.cliff: the cut DEPTH is a function of time (the terminator carves it), so
the engine keeps only depth maps per layer and shades a camera window per frame.

    cells = field_cells(fields, text)                    # rectangular fields of columns (a stele forest / a floorplan)
    D, cut = build_depth(cells, W, H, font)              # V-section cut depth (px) + cut mask for one layer
    frame = shade(rock, hgt, (az, el), flat, contrast)   # raking light on a height field over a painted rock window
    Dust(points, births, ...).draw(frame, t, to_frame)   # bright dust shed by the cuts, carried UP, closed form in t
"""
import math

import cv2
import numpy as np

from tools.ink.core import F32, blur, fbm, rng, smoothstep, luma
from tools.ink.cliff import glyph_mask

FRESH = np.array([0.965, 0.95, 0.90], F32)             # raw stone in a new cut
RED = np.array([0.72, 0.17, 0.10], F32)                # cinnabar rubbed into old cuts
GOLD_FLECK = np.array([0.80, 0.585, 0.17], F32)        # sun-lit dust: flecks of gold leaf (洒金)
SILVER_FLECK = np.array([0.97, 0.965, 0.93], F32)      # moon-lit dust


def field_cells(fields, text, start=0):
    """fields: [(x, y, w, h, size, col_gap, row_gap)] in reading order (rightmost first). Columns right to left, top
    to bottom; text cycles. Returns cells [(ch, cx, cy, size, field_index, col, row)] and the next text index."""
    out, k, n = [], start, len(text)
    for fi, (x, y, w, h, size, cg, rg) in enumerate(fields):
        pw, ph = size * (1 + cg), size * (1 + rg)
        ncol = max(1, int((w + size * cg) // pw))
        nrow = max(1, int((h + size * rg) // ph))
        bx = x + (w - (ncol * pw - size * cg)) / 2.0
        by = y + (h - (nrow * ph - size * rg)) / 2.0
        for c in range(ncol):
            cx = bx + (ncol - 1 - c) * pw + size / 2.0
            for r in range(nrow):
                out.append((text[k % n], cx, by + r * ph + size / 2.0, size, fi, c, r))
                k += 1
    return out, k


def between_cells(cells, fields, text, ratio=0.42, start=0):
    """The moon's finer columns: one column of small characters in every gap between the day columns of each field
    (and one beyond the last). Returns cells in the same format."""
    out, k, n = [], start, len(text)
    cols = {}
    for ch, cx, cy, size, fi, c, r in cells:
        cols.setdefault((fi, c), []).append((cx, cy, size))
    for (fi, c), lst in sorted(cols.items()):
        x, y, w, h, size, cg, rg = fields[fi]
        cx = lst[0][0] - size * (1 + cg) / 2.0                     # the gap to the LEFT of this column
        if cx - size * ratio / 2 < x - size * cg * 0.5:
            continue
        s2 = size * ratio
        y0, y1 = min(v[1] for v in lst) - size / 2, max(v[1] for v in lst) + size / 2
        ph = s2 * (1 + rg)
        nrow = max(1, int((y1 - y0 + s2 * rg) // ph))
        by = y0 + ((y1 - y0) - (nrow * ph - s2 * rg)) / 2.0
        for r in range(nrow):
            out.append((text[k % n], cx, by + r * ph + s2 / 2.0, s2, fi, c, r))
            k += 1
    return out, k


def build_depth(cells, W, H, font, weight=0.02, seed=0, scale=1.0, origin=(0.0, 0.0), jitter=0.03, chatter=0.25,
                rough=0.0):
    """Rasterise cells into one layer: returns (depth px, cut mask 0..1), HxW float32. `scale`/`origin` map canvas
    coordinates to this raster (a macro raster: scale 8, origin = canvas top-left of the window). Per-cell jitter is
    seeded by the cell's canvas position, so a macro raster repeats the wide raster exactly."""
    M = np.zeros((H, W), F32)
    for ch, cx, cy, size, *_ in cells:
        r = rng(seed, 'cell', int(cx), int(cy))
        jx, jy = r.normal(0, jitter * size, 2)
        sc, rot = 1 + r.normal(0, jitter), r.normal(0, jitter * 40)
        px = (cx + jx - origin[0]) * scale
        py = (cy + jy - origin[1]) * scale
        S = size * sc * scale
        if px < -S or py < -S or px > W + S or py > H + S:
            continue
        pad = int(S * 0.12) + 2
        g = glyph_mask(ch, font, S, pad)
        k = max(1, int(round(S * weight)))
        g = cv2.dilate(g, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
        if abs(rot) > 0.05:
            Mr = cv2.getRotationMatrix2D((g.shape[1] / 2, g.shape[0] / 2), rot, 1.0)
            g = cv2.warpAffine(g, Mr, (g.shape[1], g.shape[0]), flags=cv2.INTER_LINEAR)
        gx, gy = int(round(px - g.shape[1] / 2)), int(round(py - g.shape[0] / 2))
        a0, b0, a1, b1 = max(0, gx), max(0, gy), min(W, gx + g.shape[1]), min(H, gy + g.shape[0])
        if a1 <= a0 or b1 <= b0:
            continue
        M[b0:b1, a0:a1] = np.maximum(M[b0:b1, a0:a1], g[b0 - gy:b1 - gy, a0 - gx:a1 - gx])
    if rough > 0:                                                  # a ragged arris (macro only)
        n = fbm(H, W, 14.0, seed, 'rough', octaves=3) - 0.5
        M = np.clip(M + n * rough * smoothstep(0.02, 0.5, M) * smoothstep(0.98, 0.5, M) * 4, 0, 1)
    dt = cv2.distanceTransform((M > 0.5).astype(np.uint8), cv2.DIST_L2, 3).astype(F32)
    if chatter > 0:                                                # the chisel's bites along the wall
        dt *= 1.0 + chatter * (fbm(H, W, max(3.0, 5.0 * scale), seed, 'chatter', octaves=2) - 0.5) * 2
    D = blur(dt, 0.6)
    return D.astype(F32), smoothstep(0.25, 0.75, blur(M, 0.5)).astype(F32)


def micro_relief(rock, size=60.0, relief=0.12, seed=0):
    """Broad relief of the painted rock (the painting's strokes only; never paper grain)."""
    L = luma(rock)
    H, W = L.shape
    m = (blur(L, max(2.0, size * 0.03)) - blur(L, max(12.0, size * 0.4))) * relief * 6.0
    return m.astype(F32)


def shade(rock, hgt, light, flat=1.0, contrast=0.6, warmth=0.5, tint=None, cap=1.9):
    """Rock window lit by a raking light. hgt: height field (px, cuts negative). light = (az, el) degrees; az is where
    the light comes FROM (0 right, 270 above). flat: brightness of flat rock relative to the painting (map or scalar).
    contrast: 0 = the light is diffuse (cuts barely model), 1 = hard raking (far wall black, lit wall flares).
    tint: RGB (or HxWx3) multiplied in. Returns HxWx3."""
    az, el = float(light[0]), min(max(float(light[1]), 1.5), 90.0)
    ce, se = math.cos(math.radians(el)), math.sin(math.radians(el))
    Lx, Ly, Lz = ce * math.cos(math.radians(az)), ce * math.sin(math.radians(az)), se
    gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    inv = 1.0 / np.sqrt(gx * gx + gy * gy + 1.0)
    lam = (-gx * Lx - gy * Ly + Lz) * inv
    np.maximum(lam, 0, out=lam)
    lam *= 1.0 / max(se, 0.16)
    np.minimum(lam, cap * 1.6, out=lam)
    k = flat * ((1.0 - contrast) + contrast * lam)
    hi = np.maximum(k - 1.0, 0)
    k = np.minimum(k, 1.0) + hi / (1.0 + hi * 0.9) * 0.9
    out = rock * k[..., None]
    if warmth is not None and np.any(np.asarray(warmth) > 0):
        w = (np.clip(k - 0.6, 0, 1) * warmth)[..., None]
        out = out * (1.0 + w * np.array([0.06, 0.0, -0.12], F32))
    if tint is not None:
        out = out * tint
    return out


class Dust:
    """Dust shed where a cut is made, carried UP by the mist. Closed form in t.

    pts     (n, 2) canvas positions where each grain is born;  born (n,) birth times (song clock)
    rise    canvas px/s upward (per grain, drawn from range), drift px/s sideways, sway px
    life    seconds a grain glitters;  size in FRAME px at 1080p (grains are drawn in frame space, so they read at
            any zoom);  tail: length of the thread behind each grain in seconds of travel
    """

    def __init__(self, pts, born, seed=0, rise=(120, 380), drift=(-60, 20), sway=18.0, life=(2.5, 6.0),
                 size=(1.4, 2.6), tail=0.22, colour=GOLD_FLECK, accel=60.0):
        r = rng(seed, 'dust')
        n = len(pts)
        self.p = np.asarray(pts, np.float64).reshape(n, 2)
        self.tb = np.asarray(born, np.float64)
        self.vy = r.uniform(*rise, n)
        self.vx = r.uniform(*drift, n)
        self.life = r.uniform(*life, n)
        self.sz = r.uniform(*size, n)
        self.ph = r.uniform(0, 6.283, (n, 2))
        self.om = r.uniform(1.2, 3.0, n)
        self.tw = r.uniform(5.0, 13.0, n)
        self.sway, self.tail, self.colour, self.accel = sway, tail, np.asarray(colour, F32), accel

    def pos(self, age):
        a = np.maximum(age, 0)
        x = self.p[:, 0] + self.vx * a + self.sway * np.sin(self.om * a + self.ph[:, 0]) * np.minimum(a, 1.0)
        y = self.p[:, 1] - self.vy * a - 0.5 * self.accel * a * a
        return x, y

    def draw(self, frame, t, to_frame, s=1.0, gain=1.0, colour=None, mask=None):
        """to_frame(x, y) -> frame px (arrays). s = ctx.s. mask: optional HxW 0..1 multiplying the grains' alpha."""
        age = t - self.tb
        on = (age > 0) & (age < self.life)
        if not on.any():
            return frame
        H, W = frame.shape[:2]
        A = np.zeros((H, W), F32)
        idx = np.nonzero(on)[0]
        ag = age[idx]
        fade = np.clip(ag / 0.08, 0, 1) * np.clip((self.life[idx] - ag) / (0.35 * self.life[idx]), 0, 1)
        tw = 0.55 + 0.45 * np.sin(self.tw[idx] * t + self.ph[idx, 1])
        x1, y1 = self.pos(age)
        x0, y0 = self.pos(age - self.tail)
        fx1, fy1 = to_frame(x1[idx], y1[idx])
        fx0, fy0 = to_frame(x0[idx], y0[idx])
        for j in range(len(idx)):
            a = float(fade[j] * tw[j] * gain)
            if a <= 0.02 or not (-20 < fx1[j] < W + 20 and -20 < fy1[j] < H + 20):
                continue
            rad = self.sz[idx[j]] * s
            p1 = (int(round(fx1[j] * 16)), int(round(fy1[j] * 16)))
            p0 = (int(round(fx0[j] * 16)), int(round(fy0[j] * 16)))
            cv2.line(A, p0, p1, a * 0.22, 1, cv2.LINE_AA, 4)     # the thread
            cv2.circle(A, p1, int(round(rad * 16)), a, -1, cv2.LINE_AA, 4)                     # the grain
        if mask is not None:
            A *= mask
        np.clip(A, 0, 1, out=A)
        col = self.colour if colour is None else np.asarray(colour, F32)
        frame += (col[None, None] - frame) * A[..., None]
        return frame


def sample_points(cut, n, seed=0, box=None):
    """n random points on a cut mask (canvas px), optionally inside box (x0, y0, x1, y1)."""
    r = rng(seed, 'pts')
    if box is not None:
        x0, y0, x1, y1 = [int(v) for v in box]
        sub = cut[y0:y1, x0:x1]
    else:
        x0 = y0 = 0
        sub = cut
    step = max(1, int(math.sqrt(sub.size / 4e6)))
    ys, xs = np.nonzero(sub[::step, ::step] > 0.5)
    if len(ys) == 0:
        return np.zeros((0, 2))
    i = r.integers(0, len(ys), n)
    return np.stack([xs[i] * step + x0 + r.uniform(0, step, n), ys[i] * step + y0 + r.uniform(0, step, n)], 1)


# --------------------------------------------------------------------------------------------------------------------
# the stone that holds the text (B5, C1, C6, H5): faint columns inside a shape, and points of light reading down them

GOLD_INK = np.array([0.78, 0.55, 0.14], F32)


def enclosed_region(T, close=9, min_frac=0.01):
    """The bare area enclosed by a painted ring (a stone drawn as one ring stroke): HxW 0/1 mask. T = ink layer."""
    d = 1 - T.min(axis=2)
    ring = cv2.dilate((d > 0.07).astype(np.uint8), np.ones((close, close), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats((1 - ring).astype(np.uint8), connectivity=4)
    H, W = d.shape
    best, area = 0, 0
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if x > 0 and y > 0 and x + w < W and y + h < H and a > area:
            best, area = i, a
    if best == 0 or area < min_frac * H * W:
        return np.zeros((H, W), F32)
    m = cv2.dilate((lab == best).astype(np.uint8), np.ones((close, close), np.uint8))
    hull = cv2.convexHull(cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0][0])
    out = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(out, hull, 1)
    return out.astype(F32)


class Inner:
    """Columns of characters lying inside a shape like inclusions in jade, and the points of light that read them.

    region   HxW 0..1 mask of the shape's interior;  size = character px;  the columns run right to left.
    lay(frame, k)                    the faint columns (multiplied ink, cool grey), k = strength
    read(frame, col, u, ...)         a warm point at fraction u (0 top .. 1 foot) of column `col`; the characters
                                     under it turn to gold as it passes and fade behind it (trail=1 keeps them lit)
    """

    def __init__(self, region, text, font, size, seed=0, density=0.15, col_gap=0.5, row_gap=0.12, inset=None,
                 start=0, weight=0.018):
        H, W = region.shape
        inset = int(inset if inset is not None else size * 0.55)
        reg = cv2.erode((region > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                                                (2 * inset + 1, 2 * inset + 1)))
        ys, xs = np.nonzero(reg)
        self.H, self.W, self.size, self.cols = H, W, float(size), []
        self.M = np.zeros((H, W), F32)
        self.D = np.zeros((H, W), F32)
        if len(ys) == 0:
            return
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        pw, ph = size * (1 + col_gap), size * (1 + row_gap)
        ncol = max(1, int((x1 - x0 + size * col_gap) // pw))
        bx = x0 + ((x1 - x0) - (ncol * pw - size * col_gap)) / 2.0
        k, r = start, rng(seed, 'inner')
        for c in range(ncol):
            cx = bx + (ncol - 1 - c) * pw + size / 2.0
            col = reg[:, int(np.clip(cx, 0, W - 1))]
            yy = np.nonzero(col)[0]
            if len(yy) < size * 1.5:
                continue
            ya, yb = yy.min(), yy.max()
            nrow = int((yb - ya + size * row_gap) // ph)
            if nrow < 1:
                continue
            by = ya + ((yb - ya) - (nrow * ph - size * row_gap)) / 2.0
            for rr in range(nrow):
                ch = text[k % len(text)]
                k += 1
                g = glyph_mask(ch, font, size, 2)
                kk = max(1, int(round(size * weight)))
                g = cv2.dilate(g, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * kk + 1, 2 * kk + 1)))
                gx, gy = int(round(cx - g.shape[1] / 2)), int(round(by + rr * ph + size / 2 - g.shape[0] / 2))
                a0, b0, a1, b1 = max(0, gx), max(0, gy), min(W, gx + g.shape[1]), min(H, gy + g.shape[0])
                self.M[b0:b1, a0:a1] = np.maximum(self.M[b0:b1, a0:a1], g[b0 - gy:b1 - gy, a0 - gx:a1 - gx])
            self.cols.append((cx, by, by + nrow * ph - size * row_gap))
        # inclusions: soft, uneven, fading toward the skin of the stone
        depth = np.clip(cv2.distanceTransform((region > 0.5).astype(np.uint8), cv2.DIST_L2, 3) / (size * 2.2), 0, 1)
        vis = 0.55 + 0.45 * smoothstep(0.3, 0.7, fbm(H, W, size * 2.5, seed, 'inner_vis', octaves=2))
        self.D = (blur(self.M, max(0.7, size * 0.02)) * density * vis * smoothstep(0.1, 0.9, depth)).astype(F32)
        yy, xx = np.mgrid[0:H, 0:W].astype(F32)
        self._yy, self._xx = yy, xx

    def lay(self, frame, k=1.0, tint=(0.36, 0.40, 0.42)):
        if k > 0:
            frame *= 1.0 - (self.D * k)[..., None] * (1.0 - np.asarray(tint, F32))[None, None]
        return frame

    def read(self, frame, col, u, s=1.0, strength=1.0, trail=0.0, spot=True):
        if not self.cols or strength <= 0:
            return frame
        cx, ya, yb = self.cols[col % len(self.cols)]
        yp = ya + (yb - ya) * u
        hw = self.size * 0.62
        x0, x1 = int(max(0, cx - hw)), int(min(self.W, cx + hw))
        sig = self.size * 0.75
        yy = self._yy[:, x0:x1]
        w = np.exp(-((yy - yp) / sig) ** 2)
        behind = (yy < yp).astype(F32)
        w = np.maximum(w, behind * np.maximum(trail, 0.35 * np.exp(-(yp - yy) / (self.size * 2.2)) * behind))
        if u >= 1.0 and trail <= 0:
            w = w * 0
        a = np.clip(self.M[:, x0:x1] * w * strength, 0, 1)[..., None] * 0.9
        frame[:, x0:x1] += (GOLD_INK[None, None] - frame[:, x0:x1]) * a
        if spot and 0 <= u <= 1:
            d2 = (self._xx[:, x0:x1] - cx) ** 2 + (yy - yp) ** 2
            halo = np.exp(-d2 / (2 * (self.size * 0.42) ** 2))[..., None] * 0.20 * strength
            frame[:, x0:x1] *= 1.0 - halo * np.array([0.0, 0.16, 0.5], F32)                 # a breath of warm wash
            dot = smoothstep(4.2 * s, 2.6 * s, np.sqrt(d2))[..., None] * strength
            frame[:, x0:x1] += (np.array([0.86, 0.63, 0.16], F32) - frame[:, x0:x1]) * dot
        return frame

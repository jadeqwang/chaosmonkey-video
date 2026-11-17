"""FACES team: shared machinery for the 脸谱 album (H1-H4).

The album leaf (design/plates/F_lianpu) sits on a darker mount sheet. Painted faces are opaque gouache (rgba), each
stamped down like a seal and finished in fast strokes: pale ground -> colour fields -> black lines. Every face is
precomputed as three registered stages plus two arrival maps, so the build at any t is closed-form.

Coordinates: LEAF px (3600x2400 album leaf, cells from F_album_grid.json). The camera is (cx, cy, zoom) in leaf px,
zoom 1 = one leaf px per frame px at 1920 wide. Everything is resolution independent (ctx.s).
"""
import json
import math

import cv2
import numpy as np

from tools.ink import *
from tools.ink.core import F32

FL = 'design/plates/F_lianpu'
GRID = json.load(open(f'{FL}/F_album_grid.json'))
FACES = json.load(open(f'{FL}/F_faces.json'))['faces']
CELLS = GRID['cells_row_major_xywh']
BARE = GRID['bare_cell']['index']                      # 15: row 3, col 4
LW, LH = GRID['size']                                  # 3600 x 2400
PAD = GRID['rgba_pad']                                 # 120
FACE_SCALE = 0.80 * GRID['grid']['cell_h'] / 1120.0    # ~0.34: face box = 0.8 of the cell height
# mount: the leaf lies on an older, darker album board; the canvas is leaf px offset by MX, MY
MX, MY = 1000, 700
CW, CH = LW + 2 * MX, LH + 2 * MY
GROUND = np.array([0.935, 0.915, 0.865], F32)          # the white ground (lighter than the paper: gouache)


def cell_centre(i):
    x, y, w, h = CELLS[i]
    return x + w / 2.0, y + h / 2.0 + 6.0               # faces sit a hair low in the cell, like the reference


# ------------------------------------------------------------------------------------------------ face precompute

def _u8(a):
    return np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)


def _build_face(fid, seed):
    """-> dict of uint8 arrays at 1400 px: g (ground rgb), c (colour rgb), f (final rgb), a (alpha),
    Ac (colour arrival), Al (line arrival)."""
    info = FACES[fid]
    fin = load_image(f'{FL}/{info["file"]}')
    m = load_mask(f'{FL}/{info["mask"]}')
    if m.mean() > 0.5:
        # F21 was not normalised (its mask is the whole square sheet; the head inside is 0.78 of the shared head,
        # 8 px high, fitted by edge search): scale it up to the shared head and use F01's silhouette
        k = 1 / 0.78
        M = np.float32([[k, 0, 700 - 700 * k], [0, k, 700 - 692 * k]])
        fin = cv2.warpAffine(fin, M, (1400, 1400), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        m = load_mask(f'{FL}/{FACES["F01"]["mask"]}')
    h, w = m.shape
    bx, by, bw, bh = info['face_box_xywh']
    yy, xx = np.mgrid[0:h, 0:w].astype(F32)
    L = luma(fin)
    if 'build' in info:
        g = load_image(f'{FL}/{info["build"][0]}')
        c = load_image(f'{FL}/{info["build"][1]}')
    else:
        # fake the stages: the cap (dark top) stays from the start, everything else is a pale ground
        cap = (L < 0.33) & (yy < by + 0.24 * bh) & (m > 0.5)
        cap = cv2.morphologyEx(cap.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(F32)
        edge = np.clip(m - cv2.erode(m, np.ones((5, 5), np.uint8)), 0, 1)
        g = np.where(m[..., None] > 0.5, GROUND[None, None], fin)
        g = g * (1 - 0.45 * blur(edge, 1.0))[..., None]
        g = np.where(cap[..., None] > 0.5, fin, g)
        # colour fields: the final face with its black lines inpainted away (at half size, then pasted back)
        dark = ((L < 0.30) & (m > 0.5) & (cap < 0.5)).astype(np.uint8)
        # broad black FIELDS belong to the colour stage (a black face is painted black first); only thin lines wait
        fields = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)))
        fields = cv2.dilate(fields, np.ones((5, 5), np.uint8))
        dark = dark * (1 - fields)
        dark = cv2.dilate(dark, np.ones((5, 5), np.uint8)) * (1 - cv2.erode(fields, np.ones((7, 7), np.uint8)))
        small = cv2.resize(_u8(fin), (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        dm = cv2.resize(dark, (w // 2, h // 2), interpolation=cv2.INTER_NEAREST)
        inp = cv2.inpaint(small, dm, 7, cv2.INPAINT_TELEA)
        inp = cv2.resize(inp, (w, h), interpolation=cv2.INTER_CUBIC).astype(F32) / 255.0
        dk = blur(dark.astype(F32), 1.2)[..., None]
        c = fin * (1 - dk) + inp * dk
    # arrival of the colour field: one broad wet sweep on a slant, bristle-streaked
    r = rng(seed, fid, 'col')
    ang = math.radians(r.uniform(-40, 40) + (90 if r.random() < 0.5 else -90))
    ux, uy = math.cos(ang), math.sin(ang)
    proj = ((xx - (bx + bw / 2)) * ux + (yy - (by + bh / 2)) * uy) / (0.5 * math.hypot(bw, bh))
    # streaks run along the sweep: noise stretched along (ux, uy)
    q = (-(xx - 700) * uy + (yy - 700) * ux)
    streak = value_noise(1, 512, 6, seed, fid, 'st')[0]
    st = streak[np.clip((q + 900) / 1800 * 511, 0, 511).astype(int)]
    Ac = np.clip(0.5 + 0.42 * proj + 0.10 * (fbm(h, w, 90, seed, fid, 'cn') - 0.5) + 0.08 * (st - 0.5), 0, 1)
    # arrival of the black lines: three strokes (brows, eyes+nose, mouth+chin), each drawn from the centre line out
    band = np.clip((yy - by) / bh, 0, 0.999)
    gidx = np.floor(np.clip(band * 3.0 + 0.25 * (fbm(h, w, 160, seed, fid, 'gb') - 0.5), 0, 2.999))
    side = np.abs(xx - (bx + bw / 2)) / (0.5 * bw)
    Al = np.clip((gidx + 0.12 + 0.80 * np.clip(side, 0, 1) + 0.05 * (fbm(h, w, 40, seed, fid, 'ln') - 0.5)) / 3.0, 0, 1)
    ln = np.clip((luma(c) - luma(fin)) / 0.25, 0, 1) * m        # the black-line block alone (for mis-registration)
    return dict(g=_u8(g), c=_u8(c), f=_u8(fin), a=_u8(m), Ac=_u8(Ac), Al=_u8(Al), ln=_u8(ln))


def _mips(d, levels):
    out = [d]
    for _ in range(levels):
        p = out[-1]
        h, w = p['a'].shape
        out.append({k: cv2.resize(v, (w // 2, h // 2), interpolation=cv2.INTER_AREA) for k, v in p.items()})
    return out


class Face:
    """One painted face with its build. state(t) is closed-form."""

    def __init__(self, ctx, fid, seed=7, levels=3):
        d = ctx.cache(('face7', fid, seed), lambda: _build_face(fid, seed),
                      deps=[f'{FL}/{FACES[fid]["file"]}'])
        self.id, self.mips = fid, _mips(d, levels)

    def image(self, level, p_col, p_lin, split=False):
        """premultiplied rgba float32 at mip `level` for build progress p_col, p_lin (0..1 each).
        split=True -> (colour block, black-line block) as two layers, for woodblock mis-registration."""
        d = self.mips[level]
        a = d['a'].astype(F32) / 255.0
        if split:
            base = self.image(level, p_col, 0.0)
            rl = np.clip((p_lin * 1.05 - d['Al'].astype(F32) / 255.0) / 0.025 + 0.5, 0, 1) if p_lin < 1 else 1.0
            la = d['ln'].astype(F32) / 255.0 * rl
            f = d['f'].astype(F32) / 255.0
            return base, np.dstack([f * la[..., None], la])
        if p_lin >= 1.0:
            rgb = d['f'].astype(F32) / 255.0
        else:
            g = d['g'].astype(F32) / 255.0
            if p_col <= 0:
                rgb = g
            else:
                c = d['c'].astype(F32) / 255.0
                rc = np.clip((p_col * 1.12 - d['Ac'].astype(F32) / 255.0) / 0.06 + 0.5, 0, 1)[..., None]
                rgb = g + (c - g) * rc
                if p_lin > 0:
                    f = d['f'].astype(F32) / 255.0
                    rl = np.clip((p_lin * 1.05 - d['Al'].astype(F32) / 255.0) / 0.025 + 0.5, 0, 1)[..., None]
                    rgb = rgb + (f - rgb) * rl
        return np.dstack([rgb * a[..., None], a])


# ------------------------------------------------------------------------------------------------ the sheet

def _leaf_canvas(seed=88):
    """Mount board with the leaf (rgba plate) laid on it, uint8 CHxCWx3, plus the bare-mount copy."""
    mount = Paper(CW // 2, CH // 2, 'aged', seed=seed + 5).rgb
    mount = cv2.resize(mount, (CW, CH), interpolation=cv2.INTER_CUBIC)
    mount = mount * np.array([0.80, 0.74, 0.64], F32)                           # older, darker board
    mount *= (0.94 + 0.10 * fbm(CH, CW, 600, seed, 'mt'))[..., None]
    leaf = load_image(f'{FL}/F_album_leaf_empty_rgba.png', alpha=True)
    a = leaf[..., 3:4]
    x0, y0 = MX - PAD, MY - PAD
    lh, lw = leaf.shape[:2]
    sub = mount[y0:y0 + lh, x0:x0 + lw]
    # contact shadow of the leaf on the board (soft, lower right)
    sh = blur(np.roll(a[..., 0], (14, 18), (0, 1)), 22.0)[..., None]
    sub *= (1 - 0.35 * sh)
    sub[:] = sub * (1 - a) + leaf[..., :3] * a
    return _u8(mount)


class Album:
    """The leaf + its faces, rendered through a camera (cx, cy, zoom) in leaf px."""

    def __init__(self, ctx, plan, seed=88, face_levels=3, need=None):
        """plan: list of dicts {id, cell, t (landing), k (build speed factor; 1 = 9 frames total), big (bool)}
        need: face ids to precompute (default all in plan)."""
        self.ctx = ctx
        cv = ctx.cache(('leafcanvas2', seed), lambda: _leaf_canvas(seed),
                       deps=[f'{FL}/F_album_leaf_empty_rgba.png'])
        self.canvas = [cv]
        for _ in range(4):
            p = self.canvas[-1]
            self.canvas.append(cv2.resize(p, (p.shape[1] // 2, p.shape[0] // 2), interpolation=cv2.INTER_AREA))
        self.plan = sorted(plan, key=lambda e: e['t'])
        ids = need or sorted({e['id'] for e in plan})
        self.faces = {fid: Face(ctx, fid, levels=face_levels) for fid in ids}
        for e in self.plan:
            r = rng(seed, e['id'], e['cell'])
            e.setdefault('rot', float(r.uniform(-1.2, 1.2)))
            e.setdefault('off', (float(r.uniform(-7, 7)), float(r.uniform(-5, 5))))
            e.setdefault('k', 1.0)
            e.setdefault('scale', FACE_SCALE)
            if 'pos' not in e:
                cx, cy = cell_centre(e['cell'])
                e['pos'] = (cx + e['off'][0], cy + e['off'][1])

    # -------------------------------------------------------------------- pieces
    def bg(self, cam):
        """the bare leaf+mount seen by cam -> float32 HxWx3"""
        W, H, s = self.ctx.W, self.ctx.H, self.ctx.s
        cx, cy, z = cam
        zf = z * s                                        # canvas px -> frame px
        lev = 0
        while lev < 4 and zf * (2 ** (lev + 1)) <= 1.0:
            lev += 1
        src = self.canvas[lev]
        k = zf * (2 ** lev)
        M = np.float32([[k, 0, W / 2 - (cx + MX) / 2 ** lev * k],
                        [0, k, H / 2 - (cy + MY) / 2 ** lev * k]])
        out = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC if k > 1.0 else cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REFLECT)
        return out.astype(F32) / 255.0

    def to_frame(self, cam, x, y):
        W, H, s = self.ctx.W, self.ctx.H, self.ctx.s
        cx, cy, z = cam
        return W / 2 + (x - cx) * z * s, H / 2 + (y - cy) * z * s

    def face_state(self, e, t):
        """-> (visible, scale_mult, p_col, p_lin, shadow_u) for plan entry e at t"""
        dt = t - e['t']
        fr = int(math.floor(dt * 24 + 1e-6))
        k = e['k']
        if fr < -2:
            return None
        if fr < 0:
            return ('shadow', (fr + 3) / 3.0)
        sm = (1.10, 0.965, 1.012)[fr] if fr < 3 else 1.0
        if e.get('overshoot', 1.0) != 1.0 and fr < 3:
            sm = 1 + (sm - 1) * e['overshoot']
        if e.get('done'):
            return ('face', sm, 1.0, 1.0)
        # strokes: colour field over frames 2..5, lines over 5..9 (times k)
        p_col = clamp((dt * 24 - 2 * k) / (3.0 * k))
        p_lin = clamp((dt * 24 - 5 * k) / (4.5 * k))
        return ('face', sm, p_col, p_lin)

    def draw_faces(self, f, cam, t, only=None, tex=None, mis=None):
        W, H, s = self.ctx.W, self.ctx.H, self.ctx.s
        cx, cy, z = cam
        dent = np.zeros((H, W), F32)
        for e in self.plan:
            if only is not None and e['cell'] not in only and e['id'] not in only:
                continue
            st = self.face_state(e, t)
            if st is None:
                continue
            fx, fy = self.to_frame(cam, *e['pos'])
            sc = e['scale'] * z * s                       # source px -> frame px
            half = 700 * sc * 1.15
            if fx + half < 0 or fx - half > W or fy + half < 0 or fy - half > H:
                continue
            if st[0] == 'shadow':
                u = st[1]
                r = int(260 * sc * (1.25 - 0.25 * u))
                blk = np.zeros((H, W), F32)
                cv2.ellipse(blk, (int(fx + 30 * sc * (1 - u)), int(fy + 40 * sc * (1 - u))),
                            (int(r * 0.80), r), 0, 0, 360, 1.0, -1)
                blk = blur(blk, max(2.0, 120 * sc * (1.2 - u)))
                dent += blk * (0.10 + 0.20 * u)
                continue
            _, sm, pc, pl = st
            scale = sc * sm
            lev = 0
            while lev < len(self.faces[e['id']].mips) - 1 and scale * (2 ** (lev + 1)) <= 1.0:
                lev += 1
            k = scale * (2 ** lev)
            ang = math.radians(e['rot'])
            ca, sa = math.cos(ang) * k, math.sin(ang) * k
            if mis is None:
                layers = [(self.faces[e['id']].image(lev, pc, pl), (0.0, 0.0))]
            else:                                         # woodblock: colour block and line block print apart
                b, l = self.faces[e['id']].image(lev, pc, pl, split=True)
                layers = [(b, (mis[0], mis[1])), (l, (mis[2], mis[3]))]
            hs = layers[0][0].shape[0] / 2.0
            ext = int(hs * k * 1.45) + 4 + (int(max(map(abs, mis))) if mis else 0)
            x0, y0 = max(0, int(fx - ext)), max(0, int(fy - ext))
            x1, y1 = min(W, int(fx + ext)), min(H, int(fy + ext))
            if x1 <= x0 or y1 <= y0:
                continue
            sub = f[y0:y1, x0:x1]
            amax = None
            for img, (ox, oy) in layers:
                M = np.float32([[ca, -sa, fx + ox - x0 - (ca * hs - sa * hs)],
                                [sa, ca, fy + oy - y0 - (sa * hs + ca * hs)]])
                wp = cv2.warpAffine(img, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR if k < 1.2 else cv2.INTER_CUBIC,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
                a = wp[..., 3:4]
                pig = wp[..., :3]
                if tex is not None:                       # paper fibres show through the gouache a little
                    pig = pig * tex[y0:y1, x0:x1]
                sub[:] = sub * (1 - a) + pig
                amax = a if amax is None else np.maximum(amax, a)
            a = amax
            # the pressed paper around a freshly stamped face
            dtt = t - e['t']
            if dtt < 0.5 and e.get('big', True):
                amt = 0.22 * math.exp(-dtt / 0.12) + 0.0
                m = blur(np.roll(a[..., 0], (int(3 + 6 * sc), int(3 + 6 * sc)), (0, 1)), max(2.0, 18 * sc))
                dent[y0:y1, x0:x1] += m * (1 - a[..., 0]) * amt
        if dent.any():
            f *= (1 - np.clip(dent, 0, 0.6))[..., None]
        return f

    def render(self, t, cam, tex_amt=0.5, only=None, mis=None):
        bg = self.bg(cam)
        tex = None
        if tex_amt > 0:
            lum = luma(bg)
            tex = np.clip(lum / (blur(lum, 5.0 * self.ctx.s) + 1e-4), 0.85, 1.12) ** tex_amt
            tex = tex[..., None]
        f = bg.copy()
        self.draw_faces(f, cam, t, only=only, tex=tex, mis=mis)
        return f, bg


# ------------------------------------------------------------------------------------------------ the child

def child_figure(ctx, height_px, strength=1.0):
    """little_jade back view as a pale-ink figure (transmittance HxWx3), `height_px` tall. Desaturated, the
    jacket's blue disc and orange stripes taken out, so it could be either child."""
    def build():
        img = load_image('design/characters/little_jade/lj_A_turnaround.jpg')
        crop = img[150:1450, 1600:2120]
        T = key_paper(crop, lo=0.03, hi=0.12)
        d = density_of(T)
        d = d.mean(axis=2) if d.ndim == 3 else d
        hsv = cv2.cvtColor((crop * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(F32)
        sat = np.clip((hsv[..., 1] / 255.0 - 0.07) / 0.10, 0, 1) * (hsv[..., 2] > 90)
        blue = ((hsv[..., 0] > 88) & (hsv[..., 0] < 128) & (hsv[..., 1] > 12) & (hsv[..., 2] > 150)).astype(np.uint8)
        blue = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        blue = cv2.dilate(blue, np.ones((9, 9), np.uint8)).astype(F32)
        sat = blur(np.maximum(sat, blue), 3.0)
        d = d * (1 - 0.92 * sat)                       # disc and stripes gone
        return d.astype(F32)
    d = ctx.cache('child_back_v3', build, deps=['design/characters/little_jade/lj_A_turnaround.jpg'])
    ys, xs = np.where(d > 0.03)
    d = d[max(0, ys.min() - 6):ys.max() + 6, max(0, xs.min() - 6):xs.max() + 6]
    sc = height_px / d.shape[0]
    d = cv2.resize(d, (max(2, int(d.shape[1] * sc)), max(2, int(height_px))), interpolation=cv2.INTER_AREA)
    # pale ink: compress the range so hair is mid-grey and the jacket a breath; slight warm-grey ink
    d = np.clip(d, 0, 1.4)
    d = strength * 0.55 * d / (1 + 0.35 * d)
    return ink_T(d, tint=np.array([0.42, 0.40, 0.38], F32)).astype(F32)


def cams_frame_face(cell, frac_h, anchor, zoom_extra=1.0, s=None):
    """camera that puts the face in `cell` at frame position `anchor` (fx, fy in 0..1 of the frame) with the face
    box `frac_h` of the frame height. Returns (cx, cy, z)."""
    cx, cy = cell_centre(cell)
    face_h = 1120 * FACE_SCALE
    z = frac_h * 1080 / face_h * zoom_extra
    # point (cx, cy) must land at anchor -> camera centre offset
    ccx = cx - (anchor[0] - 0.5) * 1920 / z
    ccy = cy - (anchor[1] - 0.5) * 1080 / z
    return (ccx, ccy, z)


def mis_at(t, times, hold=0.16, amount=10.0, seed=0):
    """woodblock mis-registration offsets (colour dx, dy, line dx, dy) in frame px while within `hold` s after a
    time in `times`; the same event always gives the same slip. None otherwise."""
    for i, m in enumerate(times):
        if 0 <= t - m < hold:
            r = rng(seed, 'mis', i)
            a = r.uniform(0, 2 * math.pi)
            d = amount * r.uniform(0.7, 1.0)
            return (d * math.cos(a) * 0.45, d * math.sin(a) * 0.45, -d * math.cos(a) * 0.55, -d * math.sin(a) * 0.55)
    return None


# ------------------------------------------------------------------------------------------------ category seals (H3, H4)

SEAL_CELLS = [10, 3, 13, 14]                     # tool, threat, trick, kid
SEAL_LEAF = 66.0                                 # seal side in leaf px


def category_seal(px=220, seed=31):
    """a plain 白文 square: a cinnabar block with nothing cut in it, worn rim, starved paste (RGBA)."""
    pad = int(px * 0.12)
    S = px + 2 * pad
    m = np.zeros((S, S), F32)
    m[pad:pad + px, pad:pad + px] = 1.0
    m = rough_mask(m, 3.0, 9.0, seed, 'rim')
    paste = 0.78 + 0.22 * fbm(S, S, 18, seed, 'paste')
    starve = np.clip((fbm(S, S, 40, seed, 'starve') - 0.30) / 0.25, 0, 1)
    a = np.clip(m * paste * (0.55 + 0.45 * starve), 0, 1)
    rgb = np.ones((S, S, 3), F32) * np.asarray(CINNABAR, F32)[None, None]
    return np.dstack([rgb, a]).astype(F32)


def seal_pos(i):
    cx, cy = cell_centre(SEAL_CELLS[i])            # tucked under the jaw line, right side, inside its own cell
    return cx + 168.0, cy + 138.0


def draw_category_seals(f, cam, t, ctx, album, seal_rgba, hits):
    """press each seal at its hit (slam + dent) and keep it; positions in leaf px."""
    sc = SEAL_LEAF * cam[2] * ctx.s / (seal_rgba.shape[0] / 1.24)
    for i, th in enumerate(hits):
        if t < th - 2 / 24:
            continue
        fx, fy = album.to_frame(cam, *seal_pos(i))
        if -200 < fx < ctx.W + 200 and -200 < fy < ctx.H + 200:
            strike(f, seal_rgba, t, th, (fx, fy), scale=sc, overshoot=0.16, dent=0.8)
    return f

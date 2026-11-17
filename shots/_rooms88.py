"""shots/_rooms88.py: shared pieces for team ROOMS-88 (the 1988 attic shots).

  Source        a keyframe still or a generated clip (retimed, on twos, colour-matched to the keyframe)
  PageTrack     finds the blank lit page in every source frame (bright component in a box) -> mask + outer quad
  spread(kind)  the storybook spread in page space as an ink transmittance (B3's 花果山 build, egg, birth, troop, pilgrim)
  map_page      multiplies the spread onto the lit page (so the neon colours it); hands are not printed on
  Sign          the neon sign outside the window: mirror-reversed CHIN. IND. SPEC. REST. + 酒家 tubes, cinnabar
                breathing toward cold pale blue (period 9 s), seen through dusty glass; the room's red pool follows it
  finish        paper fibre + the shared attic grade (shots/_attic_grade.py)
  camera_move   compositor push / drift on the finished plate

All positions are authored in 1920x1080 px and scaled by ctx.s, so every script renders at 960x540 and 1920x1080.
"""
import itertools
import json
import math
import os

import cv2
import numpy as np

from tools.ink import *                                    # noqa: F401,F403
from tools.ink.core import F32, ROOT
from tools.ink.light import NEON_RED, NEON_BLUE, neon_colour
from shots._attic_grade import grade_field, attic_grade

KAI_FONT = str(ROOT / 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf')
SANS_NARROW = '/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf'
LATIN_FONT = str(ROOT / 'refs/fonts/eb-garamond/EBGaramond[wght].ttf')
SIGN_PERIOD = 9.0
SIGN_PHASE = 0.0          # the same phase on the song clock in every shot: the sign is one continuous object
CLIPS = ROOT / 'media/comp/rooms88/clips.json'


def lyrics_on(ctx):
    return getattr(ctx, 'opts', {}).get('lyrics', True)


def kf(name, W, H):
    return load_image(f'media/kf/{name}.jpg', size=(W, H))


# ----------------------------------------------------------------------------------------------------------------
# sources

def clip_pick(shot):
    """The chosen take for a shot from media/comp/rooms88/clips.json: {'path', 'lag_ms', 't_clip0', ...} or None."""
    if not CLIPS.exists():
        return None
    return json.load(open(CLIPS)).get(shot)


def _match_stats(src, ref):
    """Per-channel mean/std transfer (computed in setup on frame 0 vs the keyframe)."""
    ms, ss = src.reshape(-1, 3).mean(0), src.reshape(-1, 3).std(0) + 1e-4
    mr, sr = ref.reshape(-1, 3).mean(0), ref.reshape(-1, 3).std(0) + 1e-4
    return (sr / ss).astype(F32), (mr - ms * sr / ss).astype(F32)


class Source:
    """A still or a clip at render size. Clip time: src = (t - t_clip0) * rate, clamped (holds first/last frame).
    twos: hold every other song frame. match: colour-match the clip to the keyframe (frame 0 statistics)."""

    def __init__(self, W, H, still=None, clip=None, t_clip0=0.0, rate=1.0, twos=False, match=None, height=720,
                 src_range=None):
        self.W, self.H, self.twos, self.rate, self.t_clip0 = W, H, twos, rate, t_clip0
        self.still = still
        self.frames = None
        if clip is not None:
            from tools.ink.video import decode
            fr = [(t, (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)) for t, a in decode(clip, height=height)]
            self.times = np.array([t for t, _ in fr])
            self.frames = [a for _, a in fr]
            self.fps = 1.0 / np.median(np.diff(self.times)) if len(self.times) > 1 else 24.0
            self.dur = len(self.frames) / self.fps
            self.src_range = src_range or (0.0, self.dur - 1.0 / self.fps)
            self.gain, self.off = np.ones(3, F32), np.zeros(3, F32)
            if match is not None:
                f0 = cv2.resize(self.frames[0], (match.shape[1], match.shape[0]), interpolation=cv2.INTER_AREA)
                self.gain, self.off = _match_stats(f0.astype(F32) / 255.0, match)

    @property
    def n(self):
        return 1 if self.frames is None else len(self.frames)

    def index(self, t):
        if self.frames is None:
            return 0
        if self.twos:
            k = int(math.floor(round(t * 24) / 2.0)) * 2
            t = k / 24.0
        s = (t - self.t_clip0) * self.rate
        s = min(max(s, self.src_range[0]), self.src_range[1])
        return int(min(self.n - 1, max(0, round(s * self.fps))))

    def frame_i(self, i, W=None, H=None):
        W, H = W or self.W, H or self.H
        if self.frames is None:
            return self.still.copy()
        a = cv2.resize(self.frames[i], (W, H), interpolation=cv2.INTER_CUBIC if W > self.frames[i].shape[1] else cv2.INTER_AREA)
        return np.clip(a.astype(F32) / 255.0 * self.gain + self.off, 0, 1).astype(F32)

    def at(self, t):
        i = self.index(t)
        return self.frame_i(i), i


# ----------------------------------------------------------------------------------------------------------------
# page detection

def page_mask(img, roi, thr=None, cthr=11.0):
    """Bright, paper-coloured connected component in roi (x0, y0, x1, y1 in img px). img float RGB.
    Two passes: Otsu on lightness finds the page; then only pixels close to the page's own median chroma are kept,
    so pink fingers and thumbs over the page drop out. -> (mask uint8 full, thr)."""
    x0, y0, x1, y1 = [int(round(v)) for v in roi]
    sub = (np.clip(img[y0:y1, x0:x1], 0, 1) * 255).astype(np.uint8)
    lab = cv2.cvtColor(sub, cv2.COLOR_RGB2LAB).astype(F32)
    L = lab[..., 0].astype(np.uint8)
    if thr is None:
        thr, _ = cv2.threshold(L, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k = max(3, int(round(5 * img.shape[1] / 1920)) | 1)

    def biggest(m):
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
        n, lb, st, _ = cv2.connectedComponentsWithStats(m)
        if n < 2:
            return None
        return (lb == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)

    m = biggest(L > thr)
    full = np.zeros(img.shape[:2], np.uint8)
    if m is None:
        return full, thr
    if cthr:
        a0 = np.median(lab[..., 1][m > 0]); b0 = np.median(lab[..., 2][m > 0])
        d = np.hypot(lab[..., 1] - a0, lab[..., 2] - b0)
        m2 = biggest((L > thr - 12) & (d < cthr))
        if m2 is not None:
            m = m2
    kc = max(3, int(round(15 * img.shape[1] / 1920)) | 1)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kc, kc)))
    full[y0:y1, x0:x1] = m
    return full, thr


def fill_holes(m):
    """Fill everything the outside cannot reach (blotches, the gutter line); notches touching the edge stay."""
    h, w = m.shape
    ff = np.zeros((h + 2, w + 2), np.uint8)
    inv = (1 - m).astype(np.uint8)
    pad = np.pad(inv, 1, constant_values=1)
    cv2.floodFill(pad, None, (0, 0), 2)
    return ((pad[1:-1, 1:-1] != 2)).astype(np.uint8)


def max_quad(mask):
    """Largest-area quadrilateral with corners on the mask's convex hull."""
    pts = cv2.findNonZero(mask)
    if pts is None:
        return None
    hull = cv2.convexHull(pts)
    eps = 0.004 * cv2.arcLength(hull, True)
    ap = cv2.approxPolyDP(hull, eps, True).reshape(-1, 2).astype(np.float64)
    while len(ap) > 18:
        eps *= 1.3
        ap = cv2.approxPolyDP(hull, eps, True).reshape(-1, 2).astype(np.float64)
    if len(ap) < 4:
        return None
    best, bq = -1, None
    for c in itertools.combinations(range(len(ap)), 4):
        q = ap[list(c)]
        a = abs(cv2.contourArea(q.astype(np.float32)))
        if a > best:
            best, bq = a, q
    return bq


def order_quad(q, tl_dir):
    """Clockwise from the corner farthest along tl_dir (a unit-ish direction from the centre, image coords)."""
    c = q.mean(0)
    ang = np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0])
    q = q[np.argsort(ang)]                                   # clockwise on screen (y down)
    d = np.asarray(tl_dir, np.float64)
    k = int(np.argmax((q - c) @ d))
    return np.roll(q, -k, axis=0)


class PageTrack:
    """Page per source frame. roi and tl_dir in 1920 space. quads stored in 1920 space, temporally smoothed."""

    def __init__(self, src, roi, tl_dir=(-1, -1), thr=None, smooth=1.5, every=1, quad=None, cthr=11.0):
        self.roi, self.tl_dir, self.cthr = roi, tl_dir, cthr
        W0, H0 = 960, 540
        r = [v / 2 for v in roi]
        q_list = []
        ref = src.frame_i(0, W0, H0) if src.frames is not None else cv2.resize(src.still, (W0, H0), interpolation=cv2.INTER_AREA)
        _, self.thr = page_mask(ref, r, thr, self.cthr)
        for i in range(src.n):
            img = src.frame_i(i, W0, H0) if src.frames is not None else ref
            m, _ = page_mask(img, r, self.thr, self.cthr)
            q = max_quad(m)
            q_list.append(None if q is None else order_quad(q, tl_dir) * 2.0)
        good = [q for q in q_list if q is not None]
        fill = good[0] if good else np.array([[roi[0], roi[1]], [roi[2], roi[1]], [roi[2], roi[3]], [roi[0], roi[3]]], float)
        Q = []
        for q in q_list:
            fill = q if q is not None else fill
            Q.append(fill)
        Q = np.array(Q)
        if quad is not None:                                  # a hand-given quad (still book) overrides detection
            Q = np.repeat(np.asarray(quad, float)[None], len(Q), 0)
        if len(Q) > 2 and smooth > 0:
            from scipy.ndimage import gaussian_filter1d
            Q = gaussian_filter1d(Q, smooth, axis=0, mode='nearest')
        self.Q = Q

    def quad(self, i, s=1.0):
        return self.Q[min(i, len(self.Q) - 1)] * s

    def mask(self, img, s):
        m, _ = page_mask(img, [v * s for v in self.roi], self.thr, self.cthr)
        m = fill_holes(m)
        m = cv2.erode(m, np.ones((3, 3), np.uint8)).astype(F32)
        return cv2.GaussianBlur(m, (0, 0), max(0.6, 1.2 * s))


# ----------------------------------------------------------------------------------------------------------------
# the storybook spread (page space, ink transmittance)

SW, SH = 4585, 2420        # team MOUNTAIN's spread (A_open_book proportions)
_SPREADS = {}


def _keyed(path, lo=0.04, hi=0.14, size=(SW, SH)):
    return key_paper(load_image(path, size=size), lo=lo, hi=hi)


def spread(kind, scale=0.5):
    """kind: 'hgs' (B3's 花果山 spread + ruled column), 'egg', 'birth', 'troop', 'pilgrim'. Returns T at scale."""
    key = (kind, scale)
    if key in _SPREADS:
        return _SPREADS[key]
    P = 'design/plates/'
    if kind == 'hgs':
        import shots.B3 as b3                         # build it exactly as team MOUNTAIN does, then divide out paper
        b3.setup(None)
        page = b3.PAGE[b3.MY:b3.MY + b3.SH, b3.MX:b3.MX + b3.SW]
        bare = b3.BARE[b3.MY:b3.MY + b3.SH, b3.MX:b3.MX + b3.SW]
        T = np.clip(page / np.maximum(bare, 1e-3), 0, 1)
    elif kind == 'egg':
        T = _keyed(P + 'B_huaguoshan/B_egg.png', lo=0.06, hi=0.16)
    elif kind == 'birth':
        T = _keyed(P + 'B_huaguoshan/B_stone_crack.png')
    elif kind == 'troop':
        T = _keyed(P + 'C_elements/C_troop_plate.png')
    elif kind == 'pilgrim':
        T = _keyed(P + 'C_elements/C_pilgrim_band.png')
    else:
        raise ValueError(kind)
    T = cv2.resize(T.astype(F32), (int(SW * scale), int(SH * scale)), interpolation=cv2.INTER_AREA)
    _SPREADS[key] = T
    return T


def warp_spread(T, quad, W, H, strength=1.0):
    """Spread T -> frame (TL, TR, BR, BL quad in frame px). Outside = 1 (no ink)."""
    h, w = T.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    M = cv2.getPerspectiveTransform(src, np.float32(quad))
    out = cv2.warpPerspective(T, M, (W, H), flags=cv2.INTER_AREA if False else cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    if strength != 1.0:
        out = 1 - (1 - out) * strength
    return out


def map_page(f, T, quad, mask, strength=1.0):
    """Multiply the art onto the lit page, only where the page shows (hands and thumbs stay unprinted)."""
    H, W = f.shape[:2]
    Tw = warp_spread(T, quad, W, H, strength)
    m = mask[..., None]
    f *= (1 - m) + m * Tw
    return f


# ----------------------------------------------------------------------------------------------------------------
# the neon sign

def _glyph_mask(text, font, px, pad=None):
    from PIL import Image, ImageDraw, ImageFont
    fnt = ImageFont.truetype(font, px)
    l, t, r, b = fnt.getbbox(text)
    pad = pad if pad is not None else px // 4
    im = Image.new('L', (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=fnt, fill=255)
    return (np.asarray(im) > 127).astype(np.uint8)


def build_sign(height=600):
    """The sign's tubes as an alpha map (sign space, NOT yet mirrored). 酒家 as outline tubes, Latin as centre-line
    tubes on a condensed sans, plus a thin rectangular border tube."""
    from tools.ink.roto import thin
    cjk = _glyph_mask('酒家', KAI_FONT, 360, pad=30)
    edge = cjk - cv2.erode(cjk, np.ones((3, 3), np.uint8))
    tube_c = cv2.dilate(edge, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    lat = _glyph_mask('CHIN. IND. SPEC. REST.', SANS_NARROW, 140, pad=24)
    sk = thin(lat.astype(bool)).astype(np.uint8)
    tube_l = cv2.dilate(sk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    w = max(tube_c.shape[1], tube_l.shape[1]) + 80
    h = tube_c.shape[0] + tube_l.shape[0] + 70
    A = np.zeros((h, w), np.uint8)
    xc = (w - tube_c.shape[1]) // 2
    A[20:20 + tube_c.shape[0], xc:xc + tube_c.shape[1]] |= tube_c
    xl = (w - tube_l.shape[1]) // 2
    y = 20 + tube_c.shape[0] + 10
    A[y:y + tube_l.shape[0], xl:xl + tube_l.shape[1]] |= tube_l
    cv2.rectangle(A, (6, 6), (w - 7, h - 7), 1, 7)
    A = A.astype(F32)
    s = height / A.shape[0]
    A = cv2.resize(A, (int(A.shape[1] * s), int(height)), interpolation=cv2.INTER_AREA)
    return A


_SIGN = None


def sign_alpha():
    global _SIGN
    if _SIGN is None:
        _SIGN = build_sign()[:, ::-1].copy()            # mirror-reversed: we read it from inside the glass
    return _SIGN


class Sign:
    """window: (x0, y0, x1, y1) of the glass in 1920 px; place: (cx, cy, height, angle) of the sign in 1920 px (it may
    hang partly outside the glass: the mullions and frame hide it). The glass is found in the keyframe as its
    brightest red area. pool: the room's red light follows the sign's colour (amount)."""

    def __init__(self, kf_img, s, window, place, pool=0.35, strength=1.0, blur=1.6, halo=10.0, glass_thr=None):
        H, W = kf_img.shape[:2]
        self.s, self.strength, self.pool = s, strength, pool
        x0, y0, x1, y1 = [int(round(v * s)) for v in window]
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(W, x1), min(H, y1)
        sub = kf_img[y0:y1, x0:x1]
        L = sub.mean(axis=2)
        thr = glass_thr if glass_thr is not None else np.percentile(L, 45)
        g = np.zeros((H, W), F32)
        g[y0:y1, x0:x1] = cv2.GaussianBlur((L > thr).astype(F32), (0, 0), 1.0 * s + 0.5)
        self.glass = g
        cx, cy, hh, ang = place
        A = sign_alpha()
        sc = hh * s / A.shape[0]
        M = cv2.getRotationMatrix2D((A.shape[1] / 2, A.shape[0] / 2), ang, sc)
        M[0, 2] += cx * s - A.shape[1] / 2
        M[1, 2] += cy * s - A.shape[0] / 2
        a = cv2.warpAffine(A, M, (W, H), flags=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
        core = cv2.GaussianBlur(a, (0, 0), blur * s + 0.3)
        hal = cv2.GaussianBlur(a, (0, 0), halo * s + 0.5)
        self.core = np.clip(core * 1.4, 0, 1) * g
        self.halo = np.clip(hal * 1.2, 0, 1) * g
        red = np.clip(kf_img[..., 0] - np.maximum(kf_img[..., 1], kf_img[..., 2]), 0, 1)
        self.redness = cv2.GaussianBlur(red, (0, 0), 6 * s) / max(float(red.max()), 1e-3)
        self.box = (x0, y0, x1, y1)

    def apply(self, f, t, on=1.0):
        col, k = neon_colour(t, period=SIGN_PERIOD, phase=SIGN_PHASE, fade=0.22)
        col = np.asarray(col, F32)
        # the room's red light cools with the sign (only where the room is red)
        if k > 0:
            l = (f[..., 0] * 0.3 + f[..., 1] * 0.5 + f[..., 2] * 0.2)[..., None]
            cool = l * (np.asarray(NEON_BLUE, F32) * 0.75 + 0.25) * 1.15
            a = (np.maximum(self.redness * self.pool, self.glass * 0.75) * k * on)[..., None]
            f = f + (cool - f) * a
        if on <= 0:
            return f
        # the tubes behind dusty glass: a hot pale core, a coloured halo (light, never a bloom past the glass)
        hot = col * 0.55 + 0.45
        a = (self.halo * 0.45 * self.strength * on)[..., None]
        f = f + (np.maximum(f, col * 0.95) - f) * a
        a = (self.core * 0.9 * self.strength * on)[..., None]
        f = f + (hot - f) * a
        return np.clip(f, 0, 0.985)


# ----------------------------------------------------------------------------------------------------------------
# finish: paper + grade, and the compositor's camera

_TEX = {}


def paper_tex(W, H, seed=1988):
    key = (W, H, seed)
    if key not in _TEX:
        p = Paper(W, H, 'new', seed=seed).rgb
        tex = p / np.median(p.reshape(-1, 3), axis=0)
        _TEX[key] = tex.astype(F32)
    return _TEX[key]


def finish(f, G, tex, fibre=1.0):
    f = attic_grade(f, G)
    # the painted sheet: fibres show lighter in the dark washes, the grain sits in everything
    d = tex - 1.0
    f = f * (1 + d * 0.9 * fibre) + np.clip(d, 0, None) * 0.05 * fibre
    return np.clip(f, 0.03, 0.975).astype(F32)


def camera_move(f, t, keys):
    """keys: [(t, cx, cy, zoom), ...] in 1920 px of the plate (zoom >= 1 crops in). Linear in log zoom, sine eased."""
    if not keys:
        return f
    H, W = f.shape[:2]
    s = W / 1920.0
    if t <= keys[0][0]:
        k = keys[0][1:]
    elif t >= keys[-1][0]:
        k = keys[-1][1:]
    else:
        for a, b in zip(keys, keys[1:]):
            if a[0] <= t <= b[0]:
                u = (t - a[0]) / (b[0] - a[0])
                u = 0.5 - 0.5 * math.cos(math.pi * u)
                z = math.exp(math.log(a[3]) * (1 - u) + math.log(b[3]) * u)
                k = (a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, z)
                break
    cx, cy, z = k[0] * s, k[1] * s, k[2]
    cx = min(max(cx, W / (2 * z)), W - W / (2 * z))
    cy = min(max(cy, H / (2 * z)), H - H / (2 * z))
    M = np.array([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]], np.float64)
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(F32)


def inscription(text, region, ctx, words=None, start=None, end=None, vertical=False, px=None):
    """A small pale inscription in a dark part of the room (lyrics switch). region in 1920 px (x, y, w, h)."""
    from tools.ink.text import Inscription
    s = ctx.s
    r = tuple(int(v * s) for v in region)
    font = LATIN_FONT if all(ord(c) < 0x2E80 for c in text) else KAI_FONT
    return Inscription(text, font, region=r, size=ctx.size, vertical=vertical, words=words, start=start, end=end,
                       ground='night', mode='word', latin_font=LATIN_FONT, px=(px * s if px else None), max_px=int(40 * s))


# ----------------------------------------------------------------------------------------------------------------
# floorboard light lines and dust in the beam

def floor_lines(img, s, y_min=0.45):
    """Mask of the thin warm amber lines between the floorboards (orange, bright, thin) and the plate without them."""
    u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    hsv = cv2.cvtColor(u8, cv2.COLOR_RGB2HSV).astype(F32)
    h, sat, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    orange = ((h >= 6) & (h <= 28)).astype(F32) * np.clip((sat - 0.35) / 0.3, 0, 1) * np.clip((v - 0.35) / 0.3, 0, 1)
    k = max(3, int(9 * s) | 1)
    bg = cv2.medianBlur(u8, k).astype(F32) / 255
    thin_ = np.clip((v - bg.max(axis=2)) / 0.15, 0, 1)
    m = orange * thin_
    m[: int(img.shape[0] * y_min)] = 0
    m = cv2.GaussianBlur(cv2.dilate(m, np.ones((3, 3), np.uint8)), (0, 0), 0.8 * s + 0.3)
    return np.clip(m * 1.5, 0, 1).astype(F32), bg


def motes(f, t, beam, s, n=90, seed=3, gain=1.4):
    from tools.ink.light import dust
    return dust(f, t, beam, n=n, seed=seed, colour=(1.0, 0.82, 0.74), gain=gain, drift=(-5.0 * s, -3.0 * s),
                size=(0.8 * s + 0.4, 2.6 * s + 0.6), threshold=0.12)


def beam_field(G, kf_img, s):
    red = np.clip(kf_img[..., 0] - np.maximum(kf_img[..., 1], kf_img[..., 2]), 0, 1)
    b = cv2.GaussianBlur(red, (0, 0), 20 * s) * G['w']
    return (b / max(float(b.max()), 1e-3)).astype(F32)


# ----------------------------------------------------------------------------------------------------------------
# one room shot

class RoomShot:
    """cfg keys:
       shot, kf (keyframe name), T0, T1
       page: dict(kind, roi=(x0,y0,x1,y1), tl=(dx,dy), strength=1.0, kind_at=callable t->kind, quad=None) or None
       window: (x0,y0,x1,y1) glass box in the PAINTED keyframe, sign: (cx, cy, height, angle)   (or None)
       keep: face/page ellipses for the grade; floor: grade floor
       cam: camera keys (default for a still: a slow 4 % push on its centre)
       twos: clip on twos; still_cam: camera keys used only when no clip is picked
       dust: True -> motes in the beam
       pre(f, t, i, R) / post(f, t, R): hooks before the grade (in plate light) / after the finish
    """

    def __init__(self, **cfg):
        self.c = cfg

    def setup(self, ctx):
        c = self.c
        W, H, s = ctx.W, ctx.H, ctx.s
        self.ctx, self.s = ctx, s
        self.KF = kf(c['kf'], W, H)
        pick = clip_pick(c['shot'])
        self.pick = pick
        if pick:
            self.src = Source(W, H, clip=pick['path'], t_clip0=pick['t_clip0'], rate=pick.get('rate', 1.0),
                              twos=pick.get('twos', c.get('twos', False)), match=self.KF if pick.get('match', True) else None,
                              src_range=pick.get('src_range'))
        else:
            self.src = Source(W, H, still=self.KF)
        self.G = grade_field(self.KF, keep=c.get('keep', ()), floor=c.get('floor', 0.30))
        self.TEX = paper_tex(W, H)
        self.SG = Sign(self.KF, s, c['window'], c['sign'], pool=c.get('pool', 0.35)) if c.get('window') else \
            Sign(self.KF, s, (0, 0, 2, 2), (-500, -500, 10, 0), pool=c.get('pool', 0.35))
        pg = c.get('page')
        self.PT = None
        if pg:
            self.PT = PageTrack(self.src, pg['roi'], pg.get('tl', (-1, -1)), thr=pg.get('thr'), quad=pg.get('quad'), cthr=pg.get('cthr', 11.0))
            kinds = pg.get('kinds', [pg['kind']])
            self.SP = {k: spread(k) for k in kinds}
        self.BEAM = beam_field(self.G, self.KF, s) if c.get('dust') else None
        self.INS = []
        if lyrics_on(ctx):
            for line, region in c.get('lyrics', []):
                try:
                    w = ctx.timing.words(line)
                except Exception:
                    w = None
                self.INS.append(inscription(line.replace('(', '').replace(')', ''), region, ctx, words=w or None))
        if c.get('setup'):
            c['setup'](self, ctx)

    def plate(self, t):
        f, i = self.src.at(t)
        c = self.c
        if self.PT is not None:
            pg = c['page']
            kind = pg['kind_at'](t) if pg.get('kind_at') else pg['kind']
            q = self.PT.quad(i, self.s)
            m = self.PT.mask(f, self.s)
            f = map_page(f, self.SP[kind], q, m, pg.get('strength', 1.0))
            self.page_m = m
            self.page_q = q
            qm = np.zeros(m.shape, np.uint8)
            cv2.fillConvexPoly(qm, np.round(q).astype(np.int32), 1)
            self.page_hull = np.maximum(qm.astype(F32), m)
        if c.get('pre'):
            f = c['pre'](f, t, i, self)
        f = self.SG.apply(f, t)
        if self.BEAM is not None:
            f = motes(f, t, self.BEAM, self.s)
        return f

    def render(self, t):
        c = self.c
        f = finish(self.plate(t), self.G, self.TEX)
        if c.get('post'):
            f = c['post'](f, t, self)
        cam = c.get('cam')
        if cam is None and not self.pick:
            cam = c.get('still_cam', [(c['T0'], 960, 540, 1.0), (c['T1'], 960, 540, 1.04)])
        f = camera_move(f, t, cam or [])
        for ins in self.INS:
            ins.draw(f, t, opacity=0.8)
        return f


# ----------------------------------------------------------------------------------------------------------------
# hand shadows (cast in the neon: the umbra loses the red light, keeps the warm ambient)

def silhouette_mask(path, thr=0.45, crop=True):
    img = load_image(path)
    l = img.mean(axis=2)
    m = np.clip((thr + 0.12 - l) / 0.24, 0, 1).astype(F32)
    if crop:
        ys, xs = np.where(m > 0.5)
        m = m[max(0, ys.min() - 20):ys.max() + 20, max(0, xs.min() - 20):xs.max() + 20]
    return m


def place_mask(m, W, H, cx, cy, height, angle=0.0, flip=False):
    """Put mask m (any size) centred at (cx, cy) frame px, `height` px tall, rotated by angle degrees."""
    if flip:
        m = m[:, ::-1]
    sc = height / m.shape[0]
    M = cv2.getRotationMatrix2D((m.shape[1] / 2, m.shape[0] / 2), angle, sc)
    M[0, 2] += cx - m.shape[1] / 2
    M[1, 2] += cy - m.shape[0] / 2
    return cv2.warpAffine(np.ascontiguousarray(m, dtype=F32), M, (W, H), flags=cv2.INTER_LINEAR)


UMBRA = np.array([0.36, 0.25, 0.25], F32)        # what is left in the shadow when the red neon is taken away


def lay_shadow(f, S, soft, strength=0.9, umbra=UMBRA):
    """Multiply a cast shadow onto lit paper. S 0..1 (blurred by `soft` px for the penumbra)."""
    if soft > 0:
        S = cv2.GaussianBlur(S, (0, 0), soft)
    a = (np.clip(S, 0, 1) * strength)[..., None]
    return f * (1 - a + a * umbra)

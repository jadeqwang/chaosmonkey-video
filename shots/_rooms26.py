"""Shared helpers for team ROOMS-26 (car F1 F3a F4a F6b; bedroom I1 I2 I3a I4 J1 K1 K2a L1 L2).

A room shot = a generated clip (or the keyframe) as the base, graded to the set (shots/_bed_grade.py,
shots/_car_grade.py), then the comp layers the keyframes left out: page art mapped on the page quads (multiplied onto
the lit paper), hand shadows, reflections, lyrics (one switch: ctx.opts['lyrics'] or env INK_LYRICS=0).

Layout is authored in 1920x1080 px; every helper takes ctx and scales by ctx.s, so 960x540 and 1920x1080 both work.
"""
import json
import os

import cv2
import numpy as np

from tools.ink import *
from tools.ink.video import decode

ROOT = '/home/jade/Documents/chaosmonkey-video'
GARAMOND = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
WENKAI = 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'
PICKS = os.path.join(ROOT, 'media/gen/rooms26/picks.json')     # shot -> {clip, t0 (song time of clip frame 0)}
F32 = np.float32


# ----------------------------------------------------------------------------- base pictures
def load_still(path, ctx):
    return load_image(path, size=(ctx.W, ctx.H)).astype(F32)


def pick(name):
    """The chosen take for a shot: {'clip': path, 't0': song time of the clip's frame 0 after the lip-sync retime}."""
    if os.path.exists(PICKS):
        return json.load(open(PICKS)).get(name)
    return None


class Plate:
    """A generated room clip decoded once into uint8 frames at the render size (workers share it copy-on-write).
    at(t) -> float32 frame for song time t (clip frame 0 sits at song time t0). Clamps at both ends.
    twos=True holds every other frame (play on twos)."""

    def __init__(self, path, t0, ctx, start=0.0, dur=None, twos=False, crop=None, rate=1.0):
        self.t0, self.twos, self.rate = t0, twos, rate
        fr = []
        for st, a in decode(path, start, dur):
            if crop is not None:                       # (x0, y0, x1, y1) in source px: reframe
                x0, y0, x1, y1 = crop
                a = a[y0:y1, x0:x1]
            a = cv2.resize(a, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA if a.shape[1] > ctx.W else cv2.INTER_CUBIC)
            fr.append(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
        self.f = np.stack(fr)
        self.n = len(fr)
        self.fps = 24.0 if path.endswith('.mp4') else 24.0
        try:
            from tools.ink.video import probe
            self.fps = float(probe(path if os.path.isabs(path) else os.path.join(ROOT, path))['rate'])
        except Exception:
            pass

    def index(self, t):
        i = int(np.floor((t - self.t0) * self.fps * self.rate + 1e-3))
        if self.twos:
            i -= i % 2
        return int(np.clip(i, 0, self.n - 1))

    def at(self, t):
        return self.f[self.index(t)].astype(F32) / 255.0


# ----------------------------------------------------------------------------- paper and page art
def paper_fibre(frame, P, amount=0.55, grain_amt=0.018, t=0.0, seed=0):
    """Make a generated frame read as a painted sheet: multiply by the paper's own relief/tone (normalised to its
    ground) and add a fixed, non-boiling grain. P = Paper of the frame size."""
    if not hasattr(P, '_r26norm'):
        g = np.median(P.rgb.reshape(-1, 3), axis=0)
        n = P.rgb / g[None, None]
        P._r26norm = (1.0 + amount * (n - 1.0)).astype(F32)
        h, w = P.rgb.shape[:2]
        P._r26grain = (1.0 + grain_amt * (rng(seed, 'g').standard_normal((h, w, 1)).astype(F32))).astype(F32)
    out = frame * P._r26norm * P._r26grain
    return np.clip(out, 0.012, 0.985).astype(F32)


def flatten(frame, ctx, amount=0.5, sigma=3.0):
    """A touch of line/wash flattening: smooth the tonal gradations (bilateral) and keep the lines. For the faces that
    read photographic (lead note on I4a)."""
    a = np.clip(frame * 255, 0, 255).astype(np.uint8)
    b = cv2.bilateralFilter(a, int(9 * ctx.s) | 1, 28, sigma * 3 * ctx.s).astype(F32) / 255
    # posterise the wash slightly (flat even tones), keep dark lines from the original
    q = np.round(b * 14) / 14
    b = 0.6 * b + 0.4 * q
    lines = np.clip((luma(frame) - luma(blur(frame, 2.5 * ctx.s)))[..., None] * 1.0, -1, 0)
    out = frame * (1 - amount) + (b + lines) * amount
    return np.clip(out, 0.012, 0.985).astype(F32)


def spread_texture(art=None, art_box=None, pages='both', crayon=True, gain=1.0, max_w=2400):
    """The worn storybook's open spread (aged paper, page boxes of A_open_worn*.png) with page art keyed in, as an ink
    transmittance layer (1 = bare paper). art: path or array on cream paper; art_box: (x0, y0, x1, y1) in spread px of
    the cropped spread [455..5040 x 314..2733]; default = both pages. Returns T (HxWx3), size ~max_w wide."""
    src = load_image(os.path.join(ROOT, 'design/plates/A_book/A_open_worn_crayon.png' if crayon
                                  else 'design/plates/A_book/A_open_worn.png'))
    sp = src[314:2733, 455:5040]
    k = max_w / sp.shape[1]
    sp = cv2.resize(sp, (max_w, int(sp.shape[0] * k)), interpolation=cv2.INTER_AREA)
    g = np.median(sp[sp.shape[0] // 4: 3 * sp.shape[0] // 4, 100:-100].reshape(-1, 3), axis=0)
    T = np.clip(sp / g[None, None], 0, 1.0).astype(F32)
    # soften: pages are the multiplier for already-lit paper, so keep their tone mostly, tame the wear
    T = 1.0 - 0.75 * (1.0 - T)
    if art is not None:
        a = load_image(os.path.join(ROOT, art)) if isinstance(art, str) else art
        Ta = key_paper(a, gain=gain)
        H, W = T.shape[:2]
        x0, y0, x1, y1 = [int(v * k) for v in art_box] if art_box else (int(60 * k), int(60 * k), W - int(60 * k), H - int(60 * k))
        Ta = cv2.resize(Ta, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        T[y0:y1, x0:x1] *= Ta
    return T.astype(F32), k


def gutter_x(k):
    return int((2797 - 455) * k)


def warp_to_quad(tex, quad, ctx, border=1.0):
    """Warp a texture (its full rectangle TL,TR,BR,BL) onto a quad given in 1080p px. Returns (warped, mask)."""
    h, w = tex.shape[:2]
    srcq = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32(quad) * ctx.s
    M = cv2.getPerspectiveTransform(srcq, dst)
    out = cv2.warpPerspective(tex, M, (ctx.W, ctx.H), flags=cv2.INTER_AREA if False else cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(border,) * 3)
    m = cv2.warpPerspective(np.ones((h, w), F32), M, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR)
    return out.astype(F32), m.astype(F32)


def warp_layer_quad(tex, quad, ctx):
    """Like warp_to_quad but for a texture already pre-shrunk sensibly (mip): shrink tex to ~quad size first."""
    q = np.float32(quad) * ctx.s
    wq = max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))
    if tex.shape[1] > 2 * wq:
        f = 2 * wq / tex.shape[1]
        tex = cv2.resize(tex, (max(8, int(tex.shape[1] * f)), max(8, int(tex.shape[0] * f))), interpolation=cv2.INTER_AREA)
    return warp_to_quad(tex, quad, ctx)


def paper_mask(frame, region, warm=True, lo=0.35, soft=0.12, sat=(0.18, 0.34)):
    """Where the frame shows lit page paper (bright, low-saturation, warm-ish) inside `region` (HxW 0..1).
    Hands, sleeves and the dark beyond fall out, so page art never prints on them."""
    L = luma(frame)
    mx, mn = frame.max(-1), frame.min(-1)
    sat_ = (mx - mn) / np.maximum(mx, 1e-3)
    m = smoothstep(lo - soft, lo + soft, L) * (1 - smoothstep(sat[0], sat[1], sat_))
    if warm:   # paper is warm or neutral; skin is warm too but saturated; cool white sleeves (b > r) fall out
        m *= 1 - smoothstep(0.015, 0.06, frame[..., 2] - frame[..., 0])
    return (m * region).astype(F32)


def lay_page(frame, Tw, m, strength=1.0):
    k = (m * strength)[..., None]
    return (frame * (1 - k + k * Tw)).astype(F32)


# ----------------------------------------------------------------------------- shadows, light
def silhouette(path, thr=0.5):
    """A black silhouette on a light ground (the hand-shadow canon) -> 0..1 mask (1 = shadow)."""
    a = luma(load_image(os.path.join(ROOT, path)))
    g = np.median(a)
    return np.clip((g - a) / max(g - a.min(), 1e-3) * 1.4 - 0.2, 0, 1).astype(F32)


def place_mask(m, ctx, cx, cy, h, flip=False, angle=0.0):
    """Scale a mask so its bbox height is h (1080p px), centre its bbox at (cx, cy) (1080p px), optional flip/rotate."""
    ys, xs = np.where(m > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    c = m[y0:y1 + 1, x0:x1 + 1]
    if flip:
        c = c[:, ::-1]
    s = h * ctx.s / c.shape[0]
    M = cv2.getRotationMatrix2D((c.shape[1] / 2, c.shape[0] / 2), angle, s)
    M[0, 2] += cx * ctx.s - c.shape[1] / 2
    M[1, 2] += cy * ctx.s - c.shape[0] / 2
    return cv2.warpAffine(np.ascontiguousarray(c), M, (ctx.W, ctx.H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR).astype(F32)


def shadow_on(frame, S, strength=0.82, tint=(0.80, 0.78, 0.95)):
    """Multiply a soft shadow (0..1) onto a lit frame; the umbra keeps a little violet bounce light."""
    k = strength * S[..., None]
    return (frame * (1 - k + k * np.asarray(tint, F32) * 0.12)).astype(F32)


def soften(m, ctx, px):
    if px <= 0:
        return m
    return cv2.GaussianBlur(m, (0, 0), px * ctx.s).astype(F32)


# ----------------------------------------------------------------------------- lyrics
def lyrics_on(ctx):
    o = getattr(ctx, 'opts', None) or {}
    return bool(o.get('lyrics', os.environ.get('INK_LYRICS', '1') != '0'))


def words_of(ctx, text_start, near):
    best = None
    for l in ctx.timing.lines:
        ws = l.get('words') or []
        if not ws or not str(l.get('text', '')).startswith(text_start):
            continue
        d = abs(float(ws[0]['start']) - near)
        if best is None or d < best[0]:
            best = (d, [(str(w.get('w', w.get('word', w.get('text', '')))), float(w['start']),
                         float(w.get('end', float(w['start']) + 0.3))) for w in ws])
    return best[1] if best else []


def sung(ws, t, tail=0.8, sep=' '):
    if not ws or t < ws[0][1] - 0.02 or t > ws[-1][2] + tail:
        return None
    return sep.join(w for w, a, b in ws if a <= t + 0.02)


def lyric(frame, ctx, text, x=0.5, y=0.93, px=28, opacity=0.85):
    """Small inscription in a dark area (pale on night). Never over a face: callers pick x, y."""
    if lyrics_on(ctx) and text:
        subtitle(frame, text, GARAMOND, px=px, y=y, x=x, ground='auto', opacity=opacity, font_cjk=WENKAI)
    return frame


def zh_line(text, start, end, t):
    """Mandarin lines have no word timing in the map: reveal characters evenly across the line (spaces kept)."""
    if t < start - 0.02 or t > end + 0.8:
        return None
    chars = [c for c in text]
    n = sum(1 for c in chars if c != ' ')
    k = int(np.clip((t - start) / max(end - start, 1e-3) * n + 1, 1, n))
    out, c = '', 0
    for ch in chars:
        if ch != ' ':
            c += 1
            if c > k:
                break
        out += ch
    return out.strip()


# ----------------------------------------------------------------------------- compositor moves
def move(frame, ctx, zoom=1.0, cx=960, cy=540):
    """Scale the frame about (cx, cy) (1080p px) by zoom (>1 = push in); cubic, no edges shown for zoom >= 1."""
    if abs(zoom - 1) < 1e-4 and cx == 960 and cy == 540:
        return frame
    s = zoom
    M = np.float32([[s, 0, ctx.W / 2 - s * cx * ctx.s], [0, s, ctx.H / 2 - s * cy * ctx.s]])
    return cv2.warpAffine(frame, M, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(F32)


class Still:
    """Stand-in with the Plate interface: the keyframe itself (used when no take is picked yet, or by choice)."""

    def __init__(self, path, ctx):
        self.img = load_still(path, ctx)
        self.n = 1

    def at(self, t):
        return self.img.copy()


def base_for(name, still, ctx, twos=False, crop=None):
    """The picked take for `name` (media/gen/rooms26/picks.json) or the keyframe still. Returns (source, is_clip)."""
    p = pick(name)
    if p and os.path.exists(os.path.join(ROOT, p['clip'])):
        return Plate(p['clip'], p['t0'], ctx, twos=p.get('twos', twos), crop=crop, rate=p.get('rate', 1.0)), True
    return Still(still, ctx), False


def spread_art(art, box, crayon=False, gain=1.0, max_w=2400):
    """Aged spread texture with `art` keyed into box = fractions (u0, v0, u1, v1) of the spread (may exceed 0..1: the
    page edge clips it). Returns (T, A) where A maps art px -> spread-texture px (2x3 affine)."""
    T, k = spread_texture(None, crayon=crayon, max_w=max_w)
    H, W = T.shape[:2]
    a = load_image(os.path.join(ROOT, art)) if isinstance(art, str) else art
    Ta = key_paper(a, gain=gain)
    u0, v0, u1, v1 = box
    x0, y0, x1, y1 = u0 * W, v0 * H, u1 * W, v1 * H
    sx, sy = (x1 - x0) / a.shape[1], (y1 - y0) / a.shape[0]
    A = np.float32([[sx, 0, x0], [0, sy, y0]])
    Tw = cv2.warpAffine(Ta, A, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    return (T * Tw).astype(F32), A


def quad_H(tex_shape, quad, ctx):
    h, w = tex_shape[:2]
    return cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad) * ctx.s)


def map_pt(Hm, A, p):
    """art px -> frame px through the art affine A and the homography Hm."""
    x, y = A[0, 0] * p[0] + A[0, 2], A[1, 1] * p[1] + A[1, 2]
    v = Hm @ np.array([x, y, 1.0])
    return v[0] / v[2], v[1] / v[2]


def track_affine(plate, roi, ctx, step=1):
    """Per-frame 2x3 affine (frame px at ctx size) of the content inside roi=(x0, y0, x1, y1) (1080p px) relative to
    the plate's frame 0, by ECC on the high-passed grey ROI, chained frame to frame. For page art that must follow a
    book the model moved. Returns an (n, 2, 3) array."""
    x0, y0, x1, y1 = [int(v * ctx.s) for v in roi]
    def g(i):
        a = cv2.cvtColor(plate.f[i], cv2.COLOR_RGB2GRAY).astype(F32) / 255
        a = a - cv2.GaussianBlur(a, (0, 0), 6)
        return a
    m = np.zeros((ctx.H, ctx.W), np.uint8)
    m[y0:y1, x0:x1] = 1
    ref = g(0)
    out = [np.eye(2, 3, dtype=F32)]
    W = np.eye(2, 3, dtype=F32)
    for i in range(1, plate.n):
        cur = g(i)
        try:
            _, W2 = cv2.findTransformECC(ref, cur, W.copy(), cv2.MOTION_AFFINE,
                                         (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 60, 1e-5), m, 5)
            W = W2.astype(F32)
        except cv2.error:
            pass
        out.append(W.copy())
    return np.stack(out)


def apply_affine(img, A, ctx, border=0.0):
    """Move a layer (made for the plate's frame 0) to where the tracked content sits in frame i (A from track_affine
    maps frame-0 coords -> frame-i coords... ECC gives cur(x') = ref(x) with x' = A x)."""
    return cv2.warpAffine(img, A, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(border,) * (1 if img.ndim == 2 else img.shape[2]))

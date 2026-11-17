"""ROOMS-26 bedroom grade (2026): ONE white flashlight pool; everything outside it crushed toward dark violet ink wash;
faces stay readable by bounce light. Applied to every bedroom shot for continuity (I1 I2 I3a I4 J1 K1 K2a L1 L2).

    f = bed_grade(f, ctx, pool=(x, y), radius=r, faces=[(x, y, rx, ry)], amb=0.36)
All positions in 1080p px. The keyframes measure 20-50 points over their night ink budget (LOG_bed26), so the grade is
strong: amb is the level (0..1) outside the pool before the violet tint.
"""
import numpy as np
import cv2

from tools.ink.core import luma, smoothstep
from tools.ink.light import flashlight_field

F32 = np.float32
VIOLET = np.array([0.80, 0.74, 1.00], F32)      # the colour the dark falls to (dusk-violet ink wash)
TORCH_W = np.array([1.00, 0.99, 0.965], F32)    # flashlight white, a hair warm (never blue-white)
_CACHE = {}


def _ellipse(W, H, cx, cy, rx, ry, soft=0.9):
    yy, xx = np.mgrid[0:H, 0:W].astype(F32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.exp(-0.5 * (d / (0.75 * soft)) ** 2).astype(F32)


def bed_field(ctx, pool, radius, faces=(), amb=0.36, face_lift=0.72, tilt=0.0, stretch=1.0, seed=0, key=None):
    """The multiplier (HxWx3) for the grade; cache it when the pool does not move (pass key)."""
    s = ctx.s
    k = (key, ctx.W, ctx.H) if key is not None else None
    if k is not None and k in _CACHE:
        return _CACHE[k]
    W, H = ctx.W, ctx.H
    L = flashlight_field(W, H, (pool[0] * s, pool[1] * s), radius * s, tilt, stretch, seed, spill=0.0)
    L = np.clip(L / max(float(np.percentile(L, 99.5)), 1e-3), 0, 1)
    prot = np.zeros((H, W), F32)
    for f in faces:
        cx, cy, rx, ry = f[:4]
        lift = f[4] if len(f) > 4 else face_lift
        prot = np.maximum(prot, lift * _ellipse(W, H, cx * s, cy * s, rx * s, ry * s))
    lit = np.maximum(L, prot)
    base = amb * VIOLET
    M = base[None, None] + (TORCH_W - base)[None, None] * lit[..., None]
    M = M.astype(F32)
    if k is not None:
        _CACHE[k] = M
    return M


def bed_grade(frame, ctx, pool, radius, faces=(), amb=0.36, face_lift=0.72, tilt=0.0, stretch=1.0, seed=0, key=None,
              crush=0.85, field=None):
    M = field if field is not None else bed_field(ctx, pool, radius, faces, amb, face_lift, tilt, stretch, seed, key)
    out = frame * M
    # crush: the darks of the painting go a little deeper (a dark ink wash, not a grey veil); highlights untouched
    Lm = luma(out)[..., None]
    out = out * (crush + (1 - crush) * np.clip(Lm * 2.2, 0, 1))
    return np.clip(out, 0.012, 0.985).astype(F32)


def desat_hue(frame, h0, h1, amount=0.5, region=None):
    """Pull saturation down for hues h0..h1 (degrees, OpenCV 0..360) e.g. a red book cover; region HxW limits it."""
    hsv = cv2.cvtColor(np.ascontiguousarray(frame), cv2.COLOR_RGB2HSV)
    h = hsv[..., 0]
    m = ((h >= h0) & (h <= h1)) if h0 <= h1 else ((h >= h0) | (h <= h1))
    m = m.astype(F32)
    if region is not None:
        m *= region
    hsv[..., 1] *= 1 - amount * m
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).astype(F32)


# ----------------------------------------------------------------------------------------------------------- fix round 2
LENS = np.array([0.80, 0.79, 0.75], F32)        # the torch's pale lens: a painted object, not a light source


def find_lens(frame, ctx, box, sigma=3.0):
    """The torch lens: the brightest small blob inside box (x0, y0, x1, y1, 1080p px). Returns (x, y) in 1080p px."""
    s = ctx.s
    x0, y0, x1, y1 = [int(round(v * s)) for v in box]
    L = cv2.GaussianBlur(luma(frame[y0:y1, x0:x1]).astype(F32), (0, 0), sigma * s)
    y, x = np.unravel_index(int(np.argmax(L)), L.shape)
    return ((x + x0) / s, (y + y0) / s)


def dehalo(frame, ctx, centre, R=110, lens_r=28, lens_thr=0.62, strength=0.85):
    """Take a glow halo off a torch head (QA: 'no glow blooms'): the halo is the radial floor of the light around the
    lens (a low percentile of luma per ring), minus the room's level at R; it is subtracted (colour kept by ratio).
    The lens itself (bright pixels within lens_r) becomes a flat pale painted lens. centre/R/lens_r in 1080p px."""
    s = ctx.s
    H, W = frame.shape[:2]
    cx, cy = centre[0] * s, centre[1] * s
    Rp = R * s
    x0, x1 = int(max(0, cx - Rp)), int(min(W, cx + Rp + 1))
    y0, y1 = int(max(0, cy - Rp)), int(min(H, cy + Rp + 1))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return frame
    win = frame[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(F32)
    r = np.hypot(xx - cx, yy - cy)
    L = luma(win).astype(F32)
    nb = int(np.ceil(Rp)) + 1
    ri = np.clip(r.astype(np.int32), 0, nb - 1)
    floor = np.zeros(nb, F32)
    for b in range(nb):
        v = L[ri == b]
        floor[b] = np.percentile(v, 20) if v.size else 0
    for b in range(nb):                                        # empty bins (frame edge): carry the last value
        if floor[b] == 0 and b:
            floor[b] = floor[b - 1]
    base = float(np.median(floor[int(0.85 * nb):]))
    halo = np.clip(floor - base, 0, None)
    halo = np.maximum.accumulate(halo[::-1])[::-1]             # monotone: the glow only falls with distance
    halo *= smoothstep(Rp, 0.6 * Rp, np.arange(nb, dtype=F32))
    h2 = halo[ri] * strength
    ratio = np.clip((L - h2) / np.maximum(L, 1e-3), 0.0, 1.0)
    out = frame.copy()
    w = win * ratio[..., None]
    lm = ((L > lens_thr) & (r < lens_r * s)).astype(F32)
    lm = cv2.GaussianBlur(lm, (0, 0), 0.8 * s + 0.3)[..., None]
    w = w * (1 - lm) + LENS[None, None] * lm
    out[y0:y1, x0:x1] = w
    return out.astype(F32)

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

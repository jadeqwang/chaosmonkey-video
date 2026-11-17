"""shots/_attic_grade.py: ONE grade for every 1988 attic shot (team ROOMS-88), so they cut together.

The keyframes are painted 25-45 points brighter than their night ink budgets. This crushes everything outside the
red neon pool (and the page / faces you protect) toward a dark warm ink wash, so each frame squints as ONE pool of
light. The weight field is computed once from the shot's keyframe (static: a locked camera), then applied per frame.

    G = grade_field(kf_rgb, keep=[(cx, cy, rx, ry), ...])   # in setup; ellipses in 1920x1080 px (faces, page)
    f = attic_grade(f, G)                                   # per frame; f float sRGB at the same size as kf_rgb
"""
import cv2
import numpy as np

F32 = np.float32
INK = np.array([0.060, 0.044, 0.038], F32)      # the darkest wash: warm, never pure black
WARM = np.array([1.00, 0.80, 0.68], F32)        # the tone the darks fall to (old-wood brown ink)


def _luma(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def _ellipses(W, H, keep, s):
    m = np.zeros((H, W), F32)
    for e in keep:
        cx, cy, rx, ry = [v * s for v in e[:4]]
        w = e[4] if len(e) > 4 else 1.0
        yy, xx = np.ogrid[:H, :W]
        d = ((xx - cx) / max(rx, 1)) ** 2 + ((yy - cy) / max(ry, 1)) ** 2
        m = np.maximum(m, w * np.clip(1.6 - d, 0, 1).astype(F32) ** 0.7)
    return m


def grade_field(kf, keep=(), floor=0.30, lift=0.0, red_bias=0.55):
    """kf: HxWx3 float (the keyframe at render size). Returns the static weight field (1 = in the light)."""
    H, W = kf.shape[:2]
    s = W / 1920.0
    L = _luma(kf)
    red = np.clip(kf[..., 0] - np.maximum(kf[..., 1], kf[..., 2]), 0, 1)
    lit = L + red_bias * red                                   # the neon pool counts as light even where it is dim
    M = cv2.GaussianBlur(lit, (0, 0), 28 * s)
    lo, hi = np.percentile(M, 35), np.percentile(M, 99.3)
    w = np.clip((M - lo) / max(hi - lo, 1e-4), 0, 1)
    w = w * w * (3 - 2 * w)
    if keep:
        w = np.maximum(w, _ellipses(W, H, keep, s))
    w = np.clip(w + lift, 0, 1)
    gain = floor + (1 - floor) * w ** 0.85
    return {'w': w.astype(F32), 'gain': gain.astype(F32)}


def attic_grade(f, G, warmth=0.45):
    w, gain = G['w'][..., None], G['gain'][..., None]
    out = f * gain
    # darks lose their colour toward warm ink (the red pool keeps its cinnabar)
    l = _luma(out)[..., None]
    out = out + (l * WARM - out) * (1 - w) * warmth
    # a soft toe so nothing goes to pure black, and a shoulder so nothing clips to white
    out = INK + out * (1 - INK)
    out = np.where(out > 0.85, 0.85 + (out - 0.85) * 0.55, out)
    return np.clip(out, 0, 0.975).astype(F32)

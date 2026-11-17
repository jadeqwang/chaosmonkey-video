"""ROOMS-26 car grade (2026, dusk on the highway): dusk-violet darks, ONE amber streetlight sweep. Applied to every
car shot of the team (F1 F3a F4a F6b).

    f = car_grade(f, ctx, faces=[(x, y, rx, ry)], dark=0.62)          # base grade
    f = amber_sweep(f, ctx, t, t_mid, dur, angle=-30, width=380)      # a streetlight passing (only if the clip has none)
All positions in 1080p px.
"""
import numpy as np

from tools.ink.core import luma, smoothstep

F32 = np.float32
DUSK = np.array([0.78, 0.74, 1.00], F32)
AMBER = np.array([1.22, 0.86, 0.48], F32)


def _ellipse(W, H, cx, cy, rx, ry, soft=0.6):
    yy, xx = np.mgrid[0:H, 0:W].astype(F32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return (1 - smoothstep(1 - soft, 1 + soft * 0.3, d)).astype(F32)


_C = {}


def car_field(ctx, faces=(), dark=0.62, face_lift=0.88):
    k = (ctx.W, ctx.H, tuple(map(tuple, faces)), dark, face_lift)
    if k not in _C:
        s = ctx.s
        prot = np.zeros((ctx.H, ctx.W), F32)
        for f in faces:
            cx, cy, rx, ry = f[:4]
            prot = np.maximum(prot, _ellipse(ctx.W, ctx.H, cx * s, cy * s, rx * s, ry * s))
        lvl = dark + (face_lift - dark) * prot
        tint = DUSK[None, None] * (1 - prot[..., None] * 0.7) + prot[..., None] * 0.7
        _C[k] = (lvl[..., None] * tint).astype(F32)
    return _C[k]


def car_grade(frame, ctx, faces=(), dark=0.62, face_lift=0.88, crush=0.85):
    out = frame * car_field(ctx, faces, dark, face_lift)
    Lm = luma(out)[..., None]
    out = out * (crush + (1 - crush) * np.clip(Lm * 2.2, 0, 1))
    return np.clip(out, 0.012, 0.985).astype(F32)


def amber_sweep(frame, ctx, t, t_mid, dur, angle=-30.0, width=380.0, gain=0.55, direction=1):
    """A soft band of amber light crossing the frame once, centred on the frame at t_mid, taking `dur` s to cross.
    angle = the band's tilt (degrees); direction +1 left->right, -1 right->left. Multiplies (never adds glow)."""
    u = (t - t_mid) / dur                       # -0.5 .. 0.5 while crossing
    if abs(u) > 0.9:
        return frame
    H, W = frame.shape[:2]
    s = ctx.s
    yy, xx = np.mgrid[0:H, 0:W].astype(F32)
    a = np.deg2rad(angle)
    d = (xx - W / 2) * np.cos(a) + (yy - H / 2) * np.sin(a)
    c = direction * u * (W + 2 * width * s)
    band = np.exp(-0.5 * ((d - c) / (width * s * 0.5)) ** 2)
    k = gain * band[..., None]
    out = frame * (1 + k * (AMBER[None, None] - 1) + k * 0.35)
    return np.clip(out, 0.012, 0.985).astype(F32)

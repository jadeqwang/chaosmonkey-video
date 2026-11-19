"""F6b (120.625-121.458, 20 frames; F6a by team STAGE before it) the last hair comes home.  BED+CAR v3.

The last returning hair (a short curled line, drawn in code, flying in from the windscreen side) reaches her; she has it
in her fist, opens her hand: gone; she looks up toward the mirror and laughs. Kling v4 first+last
(media/kf/v3/F6b.jpg -> F6b_end.jpg). Pick key by ctx.opts['long'] (F6b_long = 33 frames from 120.083, if F6a gives frames).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 120.625, 121.45833333333333
FIST = (1065, 640)          # her raised fist in the take (1080p px)
HAIR_RGB = np.array([0.80, 0.58, 0.32], F32)     # lit amber by the streetlight


def setup(ctx):
    global B, P, LONG, TH0, TH1
    LONG = ctx.t0 < 120.5
    B = Take('F6b_long' if LONG else 'F6b', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=65)
    TH0 = ctx.t0
    TH1 = ctx.t0 + (10 if LONG else 5) / 24.0       # the hair is in her fist by then


def hair(f, ctx, u):
    """A curled hair riding in along an arc from the left edge to her fist; u 0..1."""
    s = ctx.s
    p0, p1, p2 = np.array([-60.0, 380.0]), np.array([520.0, 300.0]), np.array(FIST, float)
    pts = []
    for k in range(26):
        v = np.clip(u - 0.16 + 0.16 * k / 25.0, 0, 1)                 # the hair's own length along the path
        q = (1 - v) ** 2 * p0 + 2 * (1 - v) * v * p1 + v ** 2 * p2
        tang = 2 * (1 - v) * (p1 - p0) + 2 * v * (p2 - p1)
        nrm = np.array([-tang[1], tang[0]]) / max(np.linalg.norm(tang), 1e-6)
        q = q + nrm * 9.0 * math.sin(k * 0.9 + u * 14.0)              # the curl, turning as it flies
        pts.append(q * s)
    m = np.zeros(f.shape[:2], np.uint8)
    cv2.polylines(m, [np.int32(pts).reshape(-1, 1, 2)], False, 255, max(2, int(round(4 * s))), cv2.LINE_AA)
    a = (m.astype(F32) / 255.0)[..., None] * 0.9
    return f * (1 - a) + HAIR_RGB * a


def render(t, ctx):
    f = B.at(t)
    u = (t - TH0) / (TH1 - TH0)
    if u < 1.0:
        f = hair(f, ctx, max(u, 0.0))
    return fin(f, P)

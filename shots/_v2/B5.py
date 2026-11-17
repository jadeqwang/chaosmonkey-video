"""B5 'a thousand years of soaking up light' (36.417-41.000, 110 frames). Team MOUNTAIN.

Arrive at the summit from below (high distance, B_summit 9:16): a slow tilt up the peak to the smooth, uncarved
stone. When the drums drop out (37.885, measured) the camera has settled and everything stops but one band of mist
(bare paper) drifting across the peak below the stone.
"""
import numpy as np

from shots._mountain import *

T0, T1 = 874 / 24, 41.0
T_STOP = 37.885


def setup(ctx):
    global PLATE, BARE, MB
    raw = load_image(B + 'B_summit.png')
    H, W = raw.shape[:2]
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    T = key_paper(raw, lo=0.03)
    PLATE = paper.rgb * T
    BARE = paper.rgb.copy()
    MB = wavy_band(mist_band(W + 1600, 520, 130, 390, seed=8, softness=0.5, wisp=0.7), 70, 900, seed=8)   # fix2: not a straight streak


def cam(t):
    # decelerating tilt that lands exactly on the drum dropout
    u = ramp(t, T0, T_STOP, 'out')
    return 960.0, 2250 + (1150 - 2250) * u, 1.0


def render(t, ctx):
    cx, cy, z = cam(t)
    f = view(PLATE, cx, cy, z, ctx.W, ctx.H)
    H, W = PLATE.shape[:2]
    a = np.zeros((H, W), np.float32)
    x0 = int(round(-800 - 30.0 * (t - T0)))
    a[1180:1180 + MB.shape[0]] = MB[:, -x0:-x0 + W]
    am = view(a, cx, cy, z, ctx.W, ctx.H)
    bv = view(BARE, cx, cy, z, ctx.W, ctx.H)
    f += (bv - f) * np.clip(am, 0, 1)[..., None] * 0.85
    return f

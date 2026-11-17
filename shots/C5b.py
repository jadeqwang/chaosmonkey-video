"""C5b 'the wind blew once, and that was all' (inside part, 54.600-57.042; 58 frames). Team MOUNTAIN.

Cut inside from the attic (C5's first half is the room team's): the egg from C4, same framing and paper. Mama's
breath arrives as a water sleeve of mist (bare paper): a long soft band with a curling leading edge rolls in from
the right, wraps across the egg, thins, and trails off to the left. Nothing else moves.
"""
import numpy as np

from shots._mountain import *
from shots.C4 import egg_layer

T0, T1 = 54.6, 1369 / 24


def setup(ctx):
    global P, EGG, SLEEVE, YY, XX
    W, H = ctx.W, ctx.H
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(W, H)
    L = int(W * 2.6)
    band_ = mist_band(L, H, H * 0.40, H * 0.86, seed=11, softness=0.45, wisp=0.55)
    xs = np.arange(L, dtype=np.float32)[None, :]
    head = smoothstep(0, W * 0.35, xs) * smoothstep(L, L - W * 0.9, xs)       # soft rolling head, long thin tail
    tail = 0.55 + 0.45 * smoothstep(L * 0.25, L * 0.6, xs)
    SLEEVE = (band_ * head * tail).astype(np.float32)
    YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def render(t, ctx):
    W, H = ctx.W, ctx.H
    f = P.frame(t)
    f *= EGG
    u = ramp(t, T0 - 0.15, T1 + 0.2, 'sine')
    L = SLEEVE.shape[1]
    off = W - u * (L - W * 0.15)                   # sleeve's left end x on screen
    # the sleeve undulates: a slow travelling wave in y, and the head curls (rolls) upward as it moves
    wave = 34 * ctx.s * np.sin((XX - off) / (W * 0.45) * 2 * np.pi - t * 2.2)
    curl = 60 * ctx.s * np.exp(-((XX - off) / (W * 0.25)) ** 2)
    mx = (XX - off).astype(np.float32)
    my = (YY + wave + curl).astype(np.float32)
    a = cv2.remap(SLEEVE, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    f += (P.rgb - f) * (np.clip(a, 0, 1) * 0.95)[..., None]
    return f

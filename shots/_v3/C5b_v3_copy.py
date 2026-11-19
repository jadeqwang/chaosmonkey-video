"""C5b 'the wind blew once, and that was all' (inside part, 54.600-57.042; 58 frames). Team MOUNTAIN.

Cut inside from the attic (C5's first half is the room team's): the egg from C4, same framing and paper. Mama's
breath arrives as a water sleeve of mist (bare paper): a long soft band with a curling leading edge rolls in from
the right, wraps across the egg, thins, and trails off to the left. Nothing else moves.
"""
import numpy as np

from shots._mountain import *
from shots.C4 import egg_layer, egg_inner
from tools.ink.inscription import inscription

T0, T1 = 54.6, 1369 / 24


def setup(ctx):
    global P, EGG, SLEEVE, YY, XX, INN, INS
    W, H = ctx.W, ctx.H
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(W, H)
    INN = egg_inner(EGG, ctx.s)
    INS = inscription(ctx, 'C5', box=(1560, 120, 240, 700), paper=P)     # v3: static inscription
    L = int(W * 2.6)
    band_ = mist_band(L, H, H * 0.40, H * 0.86, seed=11, softness=0.45, wisp=0.55)
    xs = np.arange(L, dtype=np.float32)[None, :]
    head = smoothstep(0, W * 0.35, xs) * smoothstep(L, L - W * 0.9, xs)       # soft rolling head, long thin tail
    tail = 0.55 + 0.45 * smoothstep(L * 0.25, L * 0.6, xs)
    SLEEVE = (band_ * head * tail).astype(np.float32)
    YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
    global CLIPF, GAIN, F0
    CLIPF = None
    import os
    if os.path.exists(ROOT / CLIP_SRC):
        from tools.ink.video import decode
        CLIPF = [(np.clip(im, 0, 1) * 255).astype(np.uint8) for _, im in decode(CLIP_SRC, height=1080)]
        ours = P.rgb * EGG
        f0 = cv2.resize(CLIPF[0].astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
        GAIN = (np.percentile(ours.reshape(-1, 3), 80, axis=0) / np.maximum(np.percentile(f0.reshape(-1, 3), 80, axis=0), 1e-3)).astype(np.float32)
        F0 = f0 * GAIN


CLIP_SRC = 'media/gen/bk3_alive_C5b_h3_t2_ff24155ca2.mp4'    # v3 polish: a living sleeve of mist (minimax/h3 animated
#   from this shot's own first frame, spec media/gen/specs/bk3_alive_C5b_h3_t2.json; take 1 drew a silk ribbon: rejected)
CLIP_RATE = 2.0


def render(t, ctx):
    if CLIPF is not None:
        i = int(min(len(CLIPF) - 1, round((t - T0) * 24 * CLIP_RATE)))
        g = cv2.resize(CLIPF[i].astype(np.float32) / 255, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA) * GAIN
        f = P.frame(t)
        f *= EGG
        INN.lay(f)
        INS.draw(f)
        # the clip carries the mist (lighter than our page) and whatever it veils; keep our own page where they agree
        k = smoothstep(0.012, 0.05, np.abs(g - F0).max(axis=2))[..., None]
        return np.clip(f + (g - f) * k, 0, 1)
    W, H = ctx.W, ctx.H
    f = P.frame(t)
    f *= EGG
    INN.lay(f)
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
    INS.draw(f)                                   # the inscription is on the page, in front of the mist
    return f

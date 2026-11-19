"""C5b 'the wind blew once, and that was all' (54.625-57.042 s; 58 frames). BOOK v4. PROVISIONAL PICK: candidate C (hybrid).

Candidates (all in media/comp/_cand/, sheets work/review/comp_v4/C5b_*.jpg, notes work/book4/C5b/NOTES.md):
  A  = shots/_book4_C5b_A.py : our own stable-fluids solve (shots/_book4_wind.py) driving brush ribbons (vector, 1080p re-render)
  B  = minimax/h3 and seedance-2.0 takes on the plate (media/gen/bk4_C5b_*), inscription pasted back
  C  = THIS FILE: the minimax/h3 take 2 (media/gen/bk4_C5b_h3_t2_*.mp4) used only as a "what the wind did" layer
       (ratio of each frame to frame 0, gated to where the picture really changed, inscription box excluded),
       tilted 10 degrees so the wind rises left -> right, dissolved to bare paper from frame 42, and multiplied onto
       OUR OWN plate (egg, columns, paper, inscription as v3): egg and inscription are always ours and crisp.
Env C5B_CLIP / C5B_ANGLE / C5B_FADE0 override the clip, tilt and dissolve start (C_alt = h3 take 1, angle 0).
"""
import os

import cv2
import numpy as np

from shots._mountain import *
from shots.C4 import egg_layer, egg_inner
from tools.ink.inscription import inscription
from tools.ink.video import decode

T0, T1 = 1311 / 24, 1369 / 24
CLIP = os.environ.get('C5B_CLIP', 'media/gen/bk4_C5b_h3_t2_69e1ce7d89.mp4')
ANGLE = float(os.environ.get('C5B_ANGLE', '10'))
FADE0 = int(os.environ.get('C5B_FADE0', '42'))
PAD = 260


def setup(ctx):
    global P, EGG, INN, INS, FR, REF, BOX, S
    W, H = ctx.W, ctx.H
    S = W / 960.0
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(W, H)
    INN = egg_inner(EGG, ctx.s)
    INS = inscription(ctx, 'C5', box=(1560, 120, 240, 700), paper=P)
    FR = []
    for i, (_, im) in enumerate(decode(CLIP, height=H)):
        if i >= 58:
            break
        FR.append(cv2.resize((np.clip(im, 0, 1) * 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_AREA))
    REF = cv2.GaussianBlur(FR[0].astype(np.float32) / 255, (0, 0), 1.0 * S)
    box = np.zeros((H, W), np.float32)
    cv2.rectangle(box, (int(740 * S), int(20 * S)), (W, int(470 * S)), 1, -1)
    BOX = cv2.GaussianBlur(box, (0, 0), 10 * S)


def render(t, ctx):
    W, H = ctx.W, ctx.H
    k = int(np.clip(round((t - T0) * 24), 0, 57))
    f = P.frame(t)
    f *= EGG
    INN.lay(f)
    INS.draw(f)
    v = FR[min(k, len(FR) - 1)].astype(np.float32) / 255
    ratio = np.clip(v / np.maximum(REF, 0.05), 0, 1.35)
    dev = cv2.GaussianBlur(np.abs(ratio - 1).max(axis=2), (0, 0), 2.0 * S)
    gate = np.clip((dev - 0.05) / 0.10, 0, 1) * (1 - BOX)
    gate = cv2.GaussianBlur(gate, (0, 0), 1.5 * S)[..., None]
    ratio = 1 + (ratio - 1) * gate
    pad = int(PAD * S)
    M = cv2.getRotationMatrix2D((pad, pad + 0.5 * H), ANGLE, 1.0)
    rp = cv2.copyMakeBorder(ratio, pad, pad, pad, 0, cv2.BORDER_REPLICATE)
    rp = cv2.warpAffine(rp, M, (W + pad, H + 2 * pad), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    ratio = rp[pad:pad + H, pad:pad + W]
    fd = 1.0 if k < FADE0 else max(0.0, 1 - (k - FADE0) / (57.0 - FADE0))
    fd = fd * fd * (3 - 2 * fd)
    ratio = 1 + (ratio - 1) * fd
    return np.clip(f * ratio, 0, 1)

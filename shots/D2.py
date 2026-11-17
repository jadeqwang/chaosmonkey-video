"""D2  61.083-64.417  "He bowed four ways before the day had warmed" (stage team).

The 四击头 made by hand: there are no four crashes in the audio, so the bows land on every second beat of the grid from
"bowed" (61.321, 62.205, 63.090; the fourth, 63.980, is little Jade in the attic, owned by the room team). Each bow is a
HARD re-pose of a canon single (no in-betweens, like puppet joints) with a small 才 seal pressed beside it; the three 才
are one inking, fainter each time. D1's 亮相 holds until the first bow. From 63.817 (last 0.6 s) the frame is a clean
hold of the third bow so the room team can replace it (their 4th bow + 仓 at 63.980).
"""
import cv2
import numpy as np

from tools.ink import *
from tools.stage.stage import fig, sized, lay_at, seals, hold_index, LATIN, PAPER_SEED, d1_layout, d1_residue, lyrics_on, T_GONG

T0, T1 = 61.083333, 64.416667
POSES = ['01_liangxiang', '02_bow1_left', '03_bow2_front', '04_bow3_right']
# fix round 2: three clearly different compass bows, bigger, each displaced toward the way it bows.
# (pose, mirror, pitch deg (+ = top toward +x), height px, dx, base dy, vertical squash)
BOW_SPEC = [('04_bow3_right', False, 13.0, 900, -10, 0, 1.0),     # east: profile right, pitched over to the right
            ('03_bow2_front', False, 0.0, 1120, -30, 60, 0.80),     # south: frontal, deep (folded down), toward us
            ('04_bow3_right', True, -15.0, 930, -230, 0, 1.0)]    # west: profile left (mirrored), pitched left


def bow_layer(name, mirror, pitch, height, squash, s):
    """Canon single re-posed for a bow: sized, mirrored, squashed (a deeper fold) and pitched about the feet.
    Returns (T, foot_x_in_T, foot_y_in_T)."""
    T = sized(fig(name), height * s, flip=mirror)
    if squash != 1.0:
        T = cv2.resize(T, (T.shape[1], max(2, int(T.shape[0] * squash))), interpolation=cv2.INTER_AREA)
    h, w = T.shape[:2]
    pad = int(max(h, w) * 0.45)
    T = cv2.copyMakeBorder(T, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(1, 1, 1))
    fx, fy = pad + w / 2.0, pad + h - 4
    M = cv2.getRotationMatrix2D((fx, fy), -pitch, 1.0)
    T = cv2.warpAffine(T, M, (T.shape[1], T.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(1, 1, 1))
    return np.clip(T, 0, 1).astype(np.float32), fx, fy


def setup(ctx):
    global P, FIGS, BOWS, SEAL, INS, L, CAI_POS
    s = ctx.s
    tm = ctx.timing
    L = d1_layout(s)
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    beats = tm.beats_in(61.2, 64.2)
    b0 = min(beats, key=lambda b: abs(b - 61.33))                       # "bowed" on the grid
    i0 = list(beats).index(b0)
    BOWS = [beats[i0 + 2 * k] for k in range(3)]                        # 61.321, 62.205, 63.090
    # all bows stand on the same spot as the 亮相 (the stage does not move); height matched to the canon sheet
    FIGS = [sized(fig(POSES[0]), L['h'] * s)] + [bow_layer(n, m, p, h, q, s) for n, m, p, h, dx, dy, q in BOW_SPEC]
    SEAL = seals(s)
    CAI_POS = [(L['seal'][0] * s, (L['seal'][1] + 158 + 112 * k) * s) for k in range(3)]   # a column under 倉, like a 锣鼓经 score
    # the last 0.6 s (from 63.817) must be a clean hold for the room team: 'warmed' is set by 63.75
    words = [(w, min(a, 63.62), min(b, 63.75)) for w, a, b in tm.words('He bowed four ways before the day had warmed')]
    INS = Inscription('He bowed four ways\nbefore the day had warmed', LATIN,
                      region=(int(1058 * s), int(52 * s), int(330 * s), int(104 * s)), size=ctx.size, vertical=False,
                      words=words, mode='word', paper=P, seed=3, density=0.85)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    f *= d1_residue(ctx.W, ctx.H, s)
    k = hold_index(t, BOWS)                                             # -1: still the 亮相
    if k < 0:
        lay_at(f, FIGS[0], L['cx'] * s, L['base'] * s)
    else:
        # hard re-pose ON the frame containing the beat, thrown 18 % past its mark toward the bow, settling in 3 frames
        T, fx, fy = FIGS[k + 1]
        _, _, _, _, dx, dy, _ = BOW_SPEC[k]
        n = int(np.floor(t * 24 + 1e-6)) - int(np.floor(BOWS[k] * 24 + 1e-6))
        over_ = (1.18, 1.07, 1.02)[n] if n < 3 else 1.0
        x = (L['cx'] + dx * over_) * s - fx
        y = (L['base'] + dy) * s - fy
        lay_ink(f, T, int(round(x)), int(round(y)))
    strike(f, SEAL['cang'], t, T_GONG, (L['seal'][0] * s, L['seal'][1] * s))     # D1's seal stays on the sheet
    echoes(f, SEAL['cai'], t, list(zip(BOWS, CAI_POS)), decay=0.72, seed=5)
    if lyrics_on(ctx):
        INS.draw(f, t)
    return shaken(f, *shake_offset(t, BOWS, amp=5 * s, dur=0.16))



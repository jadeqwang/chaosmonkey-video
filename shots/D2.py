"""D2  61.083-64.417  "He bowed four ways before the day had warmed" (stage team).

The 四击头 made by hand: there are no four crashes in the audio, so the bows land on every second beat of the grid from
"bowed" (61.321, 62.205, 63.090; the fourth, 63.980, is little Jade in the attic, owned by the room team). Each bow is a
HARD re-pose of a canon single (no in-betweens, like puppet joints) with a small 才 seal pressed beside it; the three 才
are one inking, fainter each time. D1's 亮相 holds until the first bow. From 63.817 (last 0.6 s) the frame is a clean
hold of the third bow so the room team can replace it (their 4th bow + 仓 at 63.980).
"""
import numpy as np

from tools.ink import *
from tools.stage.stage import fig, sized, lay_at, seals, hold_index, LATIN, PAPER_SEED, d1_layout, d1_residue, lyrics_on, T_GONG

T0, T1 = 61.083333, 64.416667
POSES = ['01_liangxiang', '02_bow1_left', '03_bow2_front', '04_bow3_right']


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
    FIGS = [sized(fig(n), L['h'] * (1.0 if n == '01_liangxiang' else 0.86)) for n in POSES]
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
    T = FIGS[k + 1]
    # a puppet joint lands with a small jolt (2 frames), nothing in between
    dy = 0.0
    if k >= 0 and 0 <= t - BOWS[k] < 2 / 24:
        dy = -6 * s
    lay_at(f, T, L['cx'] * s, L['base'] * s, dy=dy)
    strike(f, SEAL['cang'], t, T_GONG, (L['seal'][0] * s, L['seal'][1] * s))     # D1's seal stays on the sheet
    echoes(f, SEAL['cai'], t, list(zip(BOWS, CAI_POS)), decay=0.72, seed=5)
    if lyrics_on(ctx):
        INS.draw(f, t)
    return shaken(f, *shake_offset(t, BOWS, amp=5 * s, dur=0.16))



"""F6a (118.000-120.625) '身外身法 谁是真身 / 问了也白问 个个都真' (STAGE team, v3).

The leaf is now two cells. Two identical monkeys face each other, mirror-posed, re-posed together (hard, no
in-betweens) on the measured beats 118.500 118.938 119.374 119.812 120.249. Each holds a hair-thin cinnabar thread in
its raised hand, and each thread runs to the OTHER's chest: either could be the copy. Both name slips read 真.
On 真 of '谁是真身' (119.12, frame 2858) a seal 真 is pressed into the left cell; on the beat 119.812 (frame 2875)
both salute and the same seal goes into the right cell: 个个都真. Round 2: the cut uses only this shot's first 50
frames (to song frame 2881; F6b from 2882), so everything lands by 2875 and frames 2876-2894 are a still hold. The
leaf stops at y = 860 of 1080: the band below it is left clear for the lyric layer.
v2 (two puppets on the windscreen): shots/_v2/F6a.py, media/comp/_v2/F6a.mp4.
"""
import math

from tools.ink import *
from shots.swarm_lib import *

T0, T1 = 2832 / 24, 2895 / 24
CUES = [118.5, 118.938, 119.374, 119.812]
T_SEAL = [119.12, 119.812]
FIG_H = 480
POSES = [
    dict(STAND, head=-4, arm_f=100, forearm_f=8, arm_b=-14, forearm_b=30),                       # points at the other
    dict(RIGP['shade']),                                                                         # peers at him
    dict(SIT, head=10, arm_f=168, forearm_f=64, arm_b=44, forearm_b=70),                         # scratches his head
    dict(RIGP['leap'], arm_f=120, forearm_f=10),                                                 # jumps at him
    dict(STAND, head=0, arm_f=96, forearm_f=118, arm_b=96, forearm_b=122),                       # both salute
]
LEAF2 = (150, 70, 1770, 860)


def setup(ctx):
    global P, RIG, RULES, SLIPS, SEAL, FIGS
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'aged', seed=61)
    RIG = load_rig(ctx)
    RULES = rules_T(ctx.W, ctx.H, s, LEAF2, cols=2, rows=1)
    SLIPS = []
    for i in range(2):
        x0, y0, x1, y1 = cell_box(i, LEAF2, 2, 1)
        T, w, h = slip_T('真', s, px=84)
        SLIPS.append((T, int((x1 if i == 1 else x0) * s + (-w - 20 * s if i == 1 else 20 * s)), int(y0 * s + 18 * s)))
    SEAL = done_seal(s, '真', px=120, seed=9)
    FIGS = {}


def figs(k, ctx):
    """(T of both monkeys, hand L, hand R, chest L, chest R) for pose k."""
    if k not in FIGS:
        s = ctx.s
        kk = FIG_H / RIG_H
        T = np.ones((ctx.H, ctx.W, 3), np.float32)
        pts = []
        for i in range(2):
            x0, y0, x1, y1 = cell_box(i, LEAF2, 2, 1)
            pose = dict(POSES[k])
            if i == 1:
                pose['_flip'] = True
            floor = ((x0 + x1) / 2 + (-60 if i == 0 else 60), y1 - 60)
            air = 80 if k == 3 else 0
            c = chest_on_floor(RIG, 'none', POSES[k], floor, kk, air)
            T *= RIG.puppet('none').render(pose, pos=(c[0] * s, c[1] * s), scale=kk * s, size=(ctx.W, ctx.H))
            pts.append((RIG.grip_xy('none', pose, c, kk), c))
        FIGS[k] = (T, pts)
    return FIGS[k]


def render(t, ctx):
    s = ctx.s
    k = sum(1 for c in CUES if t >= on_frame(c) - 1e-6)
    f = P.frame(t)
    f *= RULES
    for T, x, y in SLIPS:
        lay_ink(f, T, x, y)
    T, pts = figs(k, ctx)
    (hl, cl), (hr, cr) = pts
    f *= thread_T(ctx.W, ctx.H, s, hl, (cr[0], cr[1] + 20), sag=26, wd=3.0)
    f *= thread_T(ctx.W, ctx.H, s, hr, (cl[0], cl[1] + 20), sag=26, wd=3.0)
    f *= T
    for i, ts in enumerate(T_SEAL):
        x0, y0, x1, y1 = cell_box(i, LEAF2, 2, 1)
        x = (x0 + 120) if i == 0 else (x1 - 120)
        strike(f, SEAL, t, ts, (x * s, (y1 - 120) * s), overshoot=0.14)
    return np.clip(f * lamp_light(ctx.W, ctx.H, s, t), 0, 0.985)

"""F5 (116.208-118.000) '说完这句话 各自消散' (STAGE team, v3): the swarm finishes and goes home.

The same leaf as F4b. One copy per half-beat (the measured beats 116.320 116.736 117.200 117.628 and the points
midway between them; eight copies in 1.8 s do not fit one per beat) finishes its job: a small red seal 讫 is pressed
into its own cell, the copy is a hair again, and the hair flies home along its thread to the raised hand in the
centre, the thread reeling in with it. Order: clockwise from the top left. The copies still working keep advancing a
pose on every beat. Last frame: eight sealed, empty cells and the one monkey.
v2 (copies going dark in the car panes): shots/_v2/F5.py, media/comp/_v2/F5.mp4.
"""
import math

from tools.ink import *
from shots.swarm_lib import *

T0, T1 = 2789 / 24, 2832 / 24
BEATS = [116.32, 116.736, 117.2, 117.628]
FIN = [116.32, 116.528, 116.736, 116.968, 117.2, 117.414, 117.628, 117.84]
ORDER = [0, 1, 2, 5, 8, 7, 6, 3]
OFFS = [0, 1, 2, 3, 0, 1, 2, 3, 0]
FLY = 4                                    # frames a hair takes to fly home


def setup(ctx):
    global P, LEAFS, SEAL, TF
    P = Paper(ctx.W, ctx.H, 'aged', seed=61)
    LEAFS = Leaf(ctx, load_rig(ctx), P)
    SEAL = done_seal(ctx.s)
    TF = {cell: on_frame(tf) for cell, tf in zip(ORDER, FIN)}


def render(t, ctx):
    s = ctx.s
    k = 4 + sum(1 for b in BEATS if t >= on_frame(b) - 1e-6)
    fr = lambda x: int(math.floor(x * 24 + 1e-6))
    present, threads, flying = [], [], []
    home = 0
    for i in range(9):
        if i not in TF:
            present.append(True); threads.append(1.0); continue
        n = fr(t) - fr(TF[i])
        if n < 0:
            present.append(True); threads.append(1.0)
        else:
            present.append(False)
            u = min(1.0, (n + 1) / FLY)
            threads.append(max(0.0, 1 - u))
            if n < FLY - 1:
                flying.append((i, u))
            if n >= FLY - 1:
                home += 1
    f = P.frame(t)
    LEAFS.draw(f, [k + o for o in OFFS], present=present, threads=threads, hand_k=home)
    h = LEAFS.hand(home)
    for i, u in flying:
        a = LEAFS.anchor(i)
        pos = (a[0] + (h[0] - a[0]) * u, a[1] + (h[1] - a[1]) * u)
        f *= hair_T(ctx.W, ctx.H, s, pos, math.atan2(h[1] - a[1], h[0] - a[0]), seed=i)
    for i, tf in TF.items():
        fx, fy = LEAFS.floor(i)
        strike(f, SEAL, t, tf, (fx * s, (fy - 100) * s), overshoot=0.12)
    return np.clip(f * lamp_light(ctx.W, ctx.H, s, t), 0, 0.985)

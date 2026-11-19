"""F4b (114.333-116.208) '每一个都是我 每一个都算' (STAGE team, v3): the agent swarm / 身外身法.

A ruled album leaf of nine cells (the ruling of the 脸谱 album and the ledger), full frame. The original monkey sits
in the middle cell with one hand raised; a hair-thin cinnabar thread runs from that hand to each of the eight copies.
Each copy is the car's leather shadow puppet doing ONE job, with a typeset name slip: 读 reads a scroll, 写 writes
(a column of 我, one more each beat), 算 clicks an abacus, 运 carries peaches, 战 spars with the staff, 扫 sweeps,
望 keeps watch, 磨 grinds ink. On every measured beat (114.567, 115.002, 115.445, 115.882) ALL cells advance one pose
at once (hard re-posing, no in-betweens). The leaf is lit as the car's glass was: dusk paper, an amber streetlight
pool passing behind it. Layout decision and the rejected options: docs/logs/LOG_v3_stage.md §3.
v2 (puppets in the car panes + 走马灯 band): shots/_v2/F4b.py, media/comp/_v2/F4b.mp4.
"""
from tools.ink import *
from shots.swarm_lib import *

T0, T1 = 2744 / 24, 2789 / 24
BEATS = [114.567, 115.002, 115.445, 115.882]
OFFS = [0, 1, 2, 3, 0, 1, 2, 3, 0]


def setup(ctx):
    global P, LEAFS
    P = Paper(ctx.W, ctx.H, 'aged', seed=61)
    LEAFS = Leaf(ctx, load_rig(ctx), P)


def render(t, ctx):
    k = sum(1 for b in BEATS if t >= on_frame(b) - 1e-6)
    f = P.frame(t)
    LEAFS.draw(f, [k + o for o in OFFS], hand_k=k)
    return np.clip(f * lamp_light(ctx.W, ctx.H, ctx.s, t), 0, 0.985)

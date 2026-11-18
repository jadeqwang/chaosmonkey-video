"""C6 pre-hook roll (57.042-58.667, 39 frames). BOOK team, v3 (REVISION_V3 §3.1).

The egg on the summit (C4/C5b framing). The points of light that read the columns inside the stone QUICKEN: they
run down every column, faster and faster, and run together until each column is one line of light (gold: the one
time the stone glows by itself). From 57.95 the egg trembles on the 16th-note roll and fine cracks spread from its
crown; the last frame before the crash (58.673; D1 = STAGE's ink throw) is the most cracked, pressed tight.
"""
import numpy as np

from shots._mountain import *
from shots.C4 import egg_layer, egg_inner

T0, T1 = 1369 / 24, 1408 / 24
T_CUT = on_frame(57.95)
T_CRASH = 58.673


def setup(ctx):
    global P, EGG, CRACKS, ROLL, INN, RUNS
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(ctx.W, ctx.H)
    INN = egg_inner(EGG, ctx.s)
    r0 = rng(31, 'runs')
    # each column: successive runs, each quicker than the last, until they overlap into one line
    RUNS = []
    for c in range(len(INN.cols)):
        t, dur = T0 - 0.2 + float(r0.uniform(0, 0.3)), 0.55
        while t < T_CRASH:
            RUNS.append((c, t, dur))
            t += dur * 0.62
            dur = max(0.09, dur * 0.72)
    # fine cracks from the crown of the egg: each a thin dry line arriving at its own time
    s = ctx.s
    d = blur(1 - EGG.min(axis=2), 6 * ctx.s)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((d > 0.08).astype(np.uint8))
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    ys, xs = np.where(lab == big)
    cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    rx, ry = (xs.max() - xs.min()) / 2.0 * 0.86, (ys.max() - ys.min()) / 2.0 * 0.86
    global EGG_C
    EGG_C = (cx, cy)
    r = rng(17, 'cracks')
    CRACKS = []
    for k in range(7):
        a0 = -np.pi / 2 + (k - 3) * 0.32 + r.normal(0, 0.1)
        x, y = cx + np.cos(a0) * rx * 0.92, cy + np.sin(a0) * ry * 0.92
        pts = [(x, y, 0.9)]
        th = np.pi / 2 + (a0 + np.pi / 2) * 0.35 + r.normal(0, 0.15)
        for j in range(r.integers(4, 8)):
            th += r.normal(0, 0.35)
            st = r.uniform(0.18, 0.32) * ry
            x, y = x + np.cos(th) * st, y + np.sin(th) * st
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 0.95:
                break
            pts.append((x, y, r.uniform(0.4, 1.0)))
        if len(pts) < 2:
            continue
        t_on = T_CUT + 0.05 + (T_CRASH - T_CUT - 0.25) * (k / 7.0) ** 0.8
        CRACKS.append((stroke(pts, width=r.uniform(1.6, 2.8) * s, seed=40 + k, paper=P, density=0.85, dry=0.3),
                       t_on, r.uniform(0.12, 0.3)))
    ROLL = [h['t'] for h in ctx.timing.hits(None, T_CUT, T_CRASH)] if True else []


def render(t, ctx):
    f = P.frame(t)
    lay_ink(f, EGG, 0, 0)
    INN.lay(f, 1.0 + 0.6 * ramp(t, T0, T_CUT, 'linear'))
    together = ramp(t, T0 + 0.35, T_CUT + 0.1, 'in')                # the trails stop fading: lines of light
    for c, ts, dur in RUNS:
        if ts <= t < ts + dur:
            INN.read(f, c, (t - ts) / dur, ctx.s, trail=together)
    if together >= 1:
        for c in range(len(INN.cols)):
            INN.read(f, c, 1.0, ctx.s, trail=1.0, spot=False)
    for st, t_on, dur in CRACKS:
        if t >= t_on:
            st.lay(f, min(1.0, (t - t_on) / dur))
    k = ramp(t, T_CUT, T_CRASH, 'in')
    dx, dy = shake_offset(t, ROLL, amp=(1.5 + 5.0 * k) * ctx.s, dur=0.09) if ROLL else (0, 0)
    f = shaken(f, dx, dy)
    z = 1.0 + 0.3 * ramp(t, T0, T_CRASH, 'in')             # pressed tight toward the burst
    ex, ey = EGG_C
    return view(f, ex + (ctx.W / 2 - ex) / z, ey + (ctx.H / 2 - ey) / z, z, ctx.W, ctx.H)

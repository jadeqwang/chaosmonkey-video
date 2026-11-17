"""C6 pre-hook roll (57.042-58.667, 39 frames). Team MOUNTAIN.

(a) 57.042-57.95: the mid view of the carved cliff (B_cliff_mid, 千字文 cut small in columns on its six faces): the
light the characters caught runs UP the columns toward the summit as gold, column after column, right to left,
the one time the mountain glows by itself; the camera drifts up with it.
(b) 57.95-58.667: the egg on the summit (C4/C5b framing): it trembles on the 16th-note roll and fine cracks spread
from its crown, building to the last frame before the crash (58.673; D1 = team STAGE's full-sheet ink throw):
the last frame is the most cracked, pressed tight.
"""
import numpy as np

from shots._mountain import *
from shots.C4 import egg_layer

T0, T1 = 1369 / 24, 1408 / 24
T_CUT = 57.95
T_CRASH = 58.673
MID_BLOCKS = [(2140, 1120, 150, 560), (1930, 1120, 140, 560), (1590, 660, 160, 1000), (1300, 430, 170, 1050),
              (880, 480, 200, 1200), (610, 330, 150, 1050), (310, 450, 140, 1200)]


def setup(ctx):
    global CM, P, EGG, CRACKS, ROLL
    raw = load_image(B + 'B_cliff_mid.png')
    H, W = raw.shape[:2]
    pm = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    rock = pm.rgb * key_paper(raw, lo=0.03)
    CM = Cliff(rock, qianziwen(160), SEAL_FONT, size=34, region=MID_BLOCKS, seed=6, weather=0.25,
               presence='plane', weight=0.02, paint=0.6, depth=1.2)
    CM.prepare(fill=0.6, gold=True, gold_stagger=0.6)
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    EGG = egg_layer(ctx.W, ctx.H)
    # fine cracks from the crown of the egg: each a thin dry line arriving at its own time
    s = ctx.s
    cx, cy, rx, ry = 665 * s, 690 * s, 100 * s, 108 * s
    r = rng(17, 'cracks')
    CRACKS = []
    for k in range(9):
        a0 = -np.pi / 2 + r.normal(0, 0.55)
        x, y = cx + np.cos(a0) * rx * 0.92, cy + np.sin(a0) * ry * 0.92
        pts = [(x, y, 0.9)]
        th = a0 + np.pi + r.normal(0, 0.35)
        for j in range(r.integers(3, 6)):
            th += r.normal(0, 0.5)
            st = r.uniform(18, 42) * s
            x, y = x + np.cos(th) * st, y + np.sin(th) * st
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 0.95:
                break
            pts.append((x, y, r.uniform(0.4, 1.0)))
        if len(pts) < 2:
            continue
        t_on = T_CUT + 0.05 + (T_CRASH - T_CUT - 0.25) * (k / 9.0) ** 0.8
        CRACKS.append((stroke(pts, width=r.uniform(2.0, 3.4) * s, seed=40 + k, paper=P, density=0.85, dry=0.3),
                       t_on, r.uniform(0.12, 0.3)))
    ROLL = [h['t'] for h in ctx.timing.hits(None, T_CUT, T_CRASH)] if True else []


def render(t, ctx):
    if t < T_CUT:
        g = ramp(t, T0, T_CUT - 0.05, 'in')
        cy = 1150 - 260 * ramp(t, T0, T_CUT, 'inout')
        return view(None, 1150, cy, 1.0, ctx.W, ctx.H,
                    render=lambda box: CM.render((305, 28, 0.7), fill=0.6, gold=g, ambient=0.8, warmth=0.6,
                                                 gold_stagger=0.6, box=box))
    f = P.frame(t)
    lay_ink(f, EGG, 0, 0)
    for st, t_on, dur in CRACKS:
        if t >= t_on:
            st.lay(f, min(1.0, (t - t_on) / dur))
    # trembling: a small hard jolt on each roll hit, growing toward the crash
    k = ramp(t, T_CUT, T_CRASH, 'in')
    dx, dy = shake_offset(t, ROLL, amp=(1.5 + 5.0 * k) * ctx.s, dur=0.09) if ROLL else (0, 0)
    return shaken(f, dx, dy)

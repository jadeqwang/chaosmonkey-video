"""D4 '一通百通' (67.917-69.292, 33 frames). Team MOUNTAIN.

(a) one carved character, 通 (千字文 line 117 右通廣內), fills the frame: chisel facets on the V-cut walls, the
raking light swings onto it and it catches on '通' (68.09). (b) hard cut wider on '百' (68.53): the column block
around it, and the ten characters nearest it light one after another (each its own pool of raking light) through
the second '通' (68.77). Warm light only; the gold is reserved for the strike itself (C6/D5).
"""
import numpy as np

from shots._mountain import *

T0, T1 = 1630 / 24, 1663 / 24
T_TONG, T_BAI, T_TONG2 = (on_frame(x) for x in (68.09, 68.53, 68.77))   # fix2: floor frames


def setup(ctx):
    global CC, CW, POOLS
    raw = load_image(B + 'B_cliff_run.png')
    q = qianziwen(160)
    i = q.index('通')
    # (a) close: a 960x540 patch of the plane around canvas x 7300, enlarged 2x (the paint is soft, the cut is sharp)
    patch = raw[330:870, 6820:7780]
    patch = cv2.resize(patch, (1920, 1080), interpolation=cv2.INTER_CUBIC)
    pc = Paper(1920, 1080, 'new', seed=BOOK_PAPER_SEED, scale=2.0)
    rock_c = onto_paper(patch, pc, ground=np.percentile(raw.reshape(-1, 3), 97, axis=0))
    CC = Cliff(rock_c, '通', SEAL_FONT, size=820, region=(550, 120, 820, 840), seed=9, weather=0.22, chips=0.08,  # fix2: was 0.12/0.0 (bevel read digital)
               jitter=0.0, weight=0.012, paint=0.8, depth=0.7, streaks=0.25, grime=0.5)
    CC.prepare(fill=0.95)
    # (b) wide: the block of five columns, 通 in the middle
    win = raw[100:1180, 6340:8260]
    pw = Paper(1920, 1080, 'new', seed=BOOK_PAPER_SEED + 1)
    rock_w = onto_paper(win, pw, ground=np.percentile(raw.reshape(-1, 3), 97, axis=0))
    text = q[i - 12:i + 13]
    CW = Cliff(rock_w, text, SEAL_FONT, size=170, region=(380, 80, 1160, 940), rows=5, seed=4, weather=0.3,
               presence='plane', chips=0.3, streaks=0.4, jitter=0.03, weight=0.02, paint=0.8, depth=1.3)
    CW.prepare(fill=0.6)
    ci = [k for k, c in enumerate(CW.cells) if c[0] == '通'][0]
    cx0, cy0 = CW.cells[ci][1], CW.cells[ci][2]
    order = sorted(range(len(CW.cells)), key=lambda k: (CW.cells[k][1] - cx0) ** 2 + (CW.cells[k][2] - cy0) ** 2)
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    POOLS = []
    for n, k in enumerate(order[:11]):
        _, x, y, _, _ = CW.cells[k]
        g = np.exp(-(((xx - x) / 130) ** 2 + ((yy - y) / 120) ** 2)).astype(np.float32)
        t_on = T_BAI - 0.02 if n == 0 else T_BAI + 0.03 + (T_TONG2 - T_BAI + 0.05) * (n - 1) / 9.0
        POOLS.append((g, t_on))


def render(t, ctx):
    if t < T_BAI:
        k = ramp(t, T0, T_TONG, 'out')
        az = 335 - 30 * ramp(t, T0, T1, 'linear')           # the light keeps swinging slowly across, from above right
        amb = 0.94 - 0.44 * k
        f = CC.render((az % 360, 14, 1.0), fill=0.95, ambient=amb, warmth=0.8,
                      pool=np.full((1, 1), (0.96 + 0.03 * k - amb) / (1 - amb), np.float32))
    else:
        pool = np.zeros((1080, 1920), np.float32)
        for g, t_on in POOLS:
            if t >= t_on:
                pool = np.maximum(pool, g * (0.75 + 0.25 * ramp(t, t_on, t_on + 0.06, 'out')))   # fix2: lit on its frame
        amb = 0.94 - 0.44 * pool
        flat = 0.94 + 0.04 * pool                               # flat rock barely changes: the light is in the cuts
        f = CW.render((335, 11, 1.0), fill=0.6, ambient=amb, warmth=0.8,
                      pool=np.clip((flat - amb) / np.maximum(1 - amb, 1e-3), 0, None))
    if f.shape[1] != ctx.W:
        f = cv2.resize(f, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA)
    return f

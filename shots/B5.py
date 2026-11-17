"""B5 'a thousand years of soaking up light' (36.417-41.000, 110 frames). BOOK team, v3 (REVISION_V3 §3.1).

(a) 36.417-37.885: arrive at the summit from below (B_summit, high distance): a tilt up the peak. The dust the
    carving shed (B4) is still rising: fine gold flecks climb the mist along the peak and gather into the stone.
(b) 37.885 (the drums drop out): cut to the stone, close and still (B_stone; C1 continues this exact frame). It is
    smooth and uncarved, the only uncarved thing on the mountain, and it holds all of it: inside, very faint, columns
    of 千字文 lie like inclusions in jade. The last flecks sink into it. Then one point of warm light after another
    travels down a column and goes out, as if being read. Slow, few.
Static inscription 每受日精月华 / 感之既久 at the right in both halves (on the mist veil in (a), as in B4).
"""
import numpy as np

from shots._mountain import *
from shots._carve import GOLD_FLECK
from shots.C1 import stone_inner
from tools.ink.inscription import inscription

T0, T1 = 874 / 24, 41.0
T_STOP = on_frame(37.885)
STONE_XY = (970.0, 1040.0)                        # the stone on B_summit (plate px)
READS = [(38.05, 1.05, 0), (39.0, 1.05, 1), (39.9, 1.05, 2)]      # (start, seconds, column): C1 goes on with 3, 4


def setup(ctx):
    global PLATE, BARE, MB, PF, VEIL, INS_A, INS_B, GR_A, GR_B, STONE, INN, SC_XY
    raw = load_image(B + 'B_summit.png')
    H, W = raw.shape[:2]
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    PLATE = paper.rgb * key_paper(raw, lo=0.03)
    BARE = paper.rgb.copy()
    MB = wavy_band(mist_band(W + 1600, 520, 130, 390, seed=8, softness=0.5, wisp=0.7), 70, 900, seed=8)
    PF = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED)
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(np.float32)
    n = fbm(ctx.H, ctx.W, 260 * ctx.s, 31, 'veil', octaves=3) - 0.5
    VEIL = smoothstep(0.775, 0.865, xx / ctx.W + n * 0.10).astype(np.float32)         # the same veil as B4
    INS_A = inscription(ctx, 'B5', box=(1620, 120, 240, 700), paper=PF)
    INS_B = INS_A
    # (a) flecks climbing the peak: start low on the rock, end in the stone
    r = rng(5, 'b5a')
    n = 700
    GR_A = dict(x0=r.uniform(520, 1420, n), y0=r.uniform(1500, 3000, n), t0=r.uniform(T0 - 2.2, T_STOP - 0.3, n),
                dur=r.uniform(1.6, 3.0, n), ph=r.uniform(0, 6.28, n), sw=r.uniform(20, 70, n), sz=r.uniform(1.4, 2.8, n),
                tw=r.uniform(5, 12, n))
    # (b) the stone, as C1 has it
    T, INN = stone_inner(ctx.W, ctx.H, ctx.s)
    STONE = PF.rgb * T
    INN.lay(STONE)
    ys, xs = np.nonzero(INN.M > 0.3)
    SC_XY = (float(xs.mean()), float(ys.mean()), float(xs.max() - xs.min()) / 2, float(ys.max() - ys.min()) / 2)
    r = rng(6, 'b5b')
    n = 90
    ang = r.uniform(0.15 * np.pi, 0.85 * np.pi, n)                                   # from below and the sides
    GR_B = dict(a=ang, d=r.uniform(380, 900, n) * ctx.s, t0=T_STOP - r.uniform(0.2, 1.4, n), dur=r.uniform(1.5, 2.4, n),
                ex=r.uniform(-0.7, 0.7, n), ey=r.uniform(-0.6, 0.7, n), ph=r.uniform(0, 6.28, n),
                sz=r.uniform(1.4, 2.8, n), tw=r.uniform(5, 12, n))


def flecks(f, xs, ys, a, sz, s, col=GOLD_FLECK):
    A = np.zeros(f.shape[:2], np.float32)
    for x, y, al, z in zip(xs, ys, a, sz):
        if al > 0.03 and -5 < x < f.shape[1] + 5 and -5 < y < f.shape[0] + 5:
            cv2.circle(A, (int(round(x * 16)), int(round(y * 16))), int(round(z * s * 16)), float(al), -1, cv2.LINE_AA, 4)
    f += (np.asarray(col, np.float32)[None, None] - f) * np.clip(A, 0, 1)[..., None]
    return f


def cam(t):
    u = ramp(t, T0, T_STOP, 'out')
    return 960.0, 2250 + (1150 - 2250) * u, 1.0


def render(t, ctx):
    s = ctx.s
    if t < T_STOP - 1e-6:
        cx, cy, z = cam(t)
        f = view(PLATE, cx, cy, z, ctx.W, ctx.H)
        H, W = PLATE.shape[:2]
        a = np.zeros((H, W), np.float32)
        x0 = int(round(-800 - 60.0 * (t - T0)))
        a[1500:1500 + MB.shape[0]] = MB[:, -x0:-x0 + W]
        am = view(a, cx, cy, z, ctx.W, ctx.H)
        bv = view(BARE, cx, cy, z, ctx.W, ctx.H)
        f += (bv - f) * np.clip(am, 0, 1)[..., None] * 0.85
        g = GR_A
        u = np.clip((t - g['t0']) / g['dur'], 0, 1)
        e = u * u * (3 - 2 * u)
        x = g['x0'] + (STONE_XY[0] - g['x0']) * e ** 1.6 + g['sw'] * np.sin(g['ph'] + 3.0 * u) * (1 - e)
        y = g['y0'] + (STONE_XY[1] - g['y0']) * e
        al = np.clip(u / 0.1, 0, 1) * np.clip((1 - u) / 0.06, 0, 1) * (0.55 + 0.45 * np.sin(g['tw'] * t + g['ph']))
        zz = z * ctx.W / 1920.0
        flecks(f, (x - cx) * zz + ctx.W / 2, (y - cy) * zz + ctx.H / 2, al, g['sz'] * 1.5, s, col=(0.995, 0.91, 0.60))
        f += (PF.rgb - f) * VEIL[..., None]
        INS_A.draw(f)
        return f
    f = STONE.copy()
    for ts, dur, col in READS:
        if ts <= t < ts + dur + 0.4:
            u = (t - ts) / dur
            INN.read(f, col, min(u, 1.0), s, strength=1.0 if u <= 1 else max(0.0, 1 - (u - 1) * dur / 0.4))
    g = GR_B
    cx, cy, rx, ry = SC_XY
    u = np.clip((t - g['t0']) / g['dur'], 0, 1)
    e = u * u * (3 - 2 * u)
    tx, ty = cx + g['ex'] * rx, cy + g['ey'] * ry
    sx, sy = tx + np.cos(g['a']) * g['d'], ty + np.sin(g['a']) * g['d'] * 0.9
    x = sx + (tx - sx) * e + 14 * s * np.sin(g['ph'] + 4 * u) * (1 - e)
    y = sy + (ty - sy) * e
    al = np.clip(u / 0.1, 0, 1) * np.clip((1 - u) / 0.12, 0, 1) * (0.55 + 0.45 * np.sin(g['tw'] * t + g['ph']))
    flecks(f, x, y, al, g['sz'], s)
    INS_B.draw(f)
    return f

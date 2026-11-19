"""B5 'a thousand years of soaking up light' (36.417-41.000, 110 frames). WORLD v4 (REVISION_V4 §2, REVISION_V3 §3.1).

Inside the same 3D mountain as B4 (tools/world): the camera arrives at the summit of 花果山 from below, looking up
(high distance): the peak (B_summit, its painted stone removed) as a relief card, pines and mist passing, the gold-leaf
dust B4 shed still climbing the mist and gathering into the stone. The stone on top is its own card, baked from C1's
own stone (B_stone + the inclusions of shots/C1.stone_inner, the same columns), placed so that when the camera settles
(37.885, the drums drop out) the frame IS C1's frame 0: camera still, square on, the stone filling C1's framing; the
cloud sea has risen to the summit so the peak below dissolves into bare paper. From then on only mist moves, and
warm points of light travel down the inclusion columns (a 3D point + the glyphs under it turning gold, C1's reads
0..2; C1 goes on with 3, 4). Static inscription 'B5' on the right.
    $PY shots/B5.py [take] [--frames ...] [--final]          takes: a (rise from below), b (sideways arrival), c (hold wider)
"""
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import World, smooth_path, paper_grain, encode, sheet, ROOT, PAPER_RGB  # noqa: E402

FPS = 24
N = 110
F_IN = 874
def fr(t): return t * FPS - F_IN


T_STOP = 37.885
F_STOP = int(math.ceil(fr(T_STOP)))                # 35: first held frame
READS = [(38.05, 1.05, 0), (39.0, 1.05, 1), (39.9, 1.05, 2)]       # as v3 B5; C1 continues with columns 3, 4
CARDS = 'design/world/cards'
HC = 9.0                                            # the stone card: C1's whole frame, 16 x 9 units
WC = HC * 16 / 9
FOV_HOLD = 30.0
D_HOLD = HC / 2 / math.tan(math.radians(FOV_HOLD / 2))
SUMMIT_H = 120.0
SUMMIT_W = SUMMIT_H * 1738 / 3072
# the painted stone sat on the peak at plate (962, 1060) of 1920 x 3392 -> the peak top in card units
TOP_Y = SUMMIT_H * (1 - 1058 / 3392)
STONE_Y = TOP_Y + HC / 2 - 1.5                      # card centre: its frame bottom just under the summit top
STONE_Z = 1.5


def stone_card():
    """C1's stone as a card texture (RGB = world paper x C1's stone ratio, so render x paper grain = C1's pixels)."""
    import shots.C1 as C1
    from shots._carve import enclosed_region
    T, INN = C1.stone_inner(1920, 1080, 1.0)
    base = np.ones((1080, 1920, 3), np.float32) * np.array(PAPER_RGB, np.float32) * T
    INN.lay(base)
    reg = cv2.GaussianBlur(enclosed_region(T, close=9 | 1).astype(np.float32), (0, 0), 1.0)
    # exact over bare paper: alpha from the ink's darkness and colour solved so that a*tex + (1-a)*paper = paper*T
    # (what C1 shows); over rock the strokes darken it like ink, with no paper halo; the stone's body is opaque
    pap = np.array(PAPER_RGB, np.float32)
    k = np.clip(1 - base / pap, 0, 1)
    a = np.maximum(np.clip(k.max(2) / 0.25, 0, 1), reg)
    tex = pap * (1 - k / np.maximum(a, 1e-3)[..., None])
    tex = np.where(a[..., None] > 1e-3, tex, pap)
    out = os.path.join(ROOT, 'work/world/B5/stone_rgba.png')
    Image.fromarray(np.dstack([np.clip(tex, 0, 1) * 255, a * 255]).round().astype(np.uint8), 'RGBA').save(out)
    return os.path.relpath(out, ROOT), INN


TAKES = {
    'a': dict(path='rise', hold='c1'),
    'b': dict(path='side', hold='c1'),
    'c': dict(path='rise', hold='wide'),
}


def build(take='a'):
    T = TAKES[take]
    Wd = World('B5' + ('' if take == 'a' else '_' + take), N)
    Wd.fog(density=0.004, start=40)
    Wd.sea(y=0.0, soft=10.0, amp=8.0, scale=0.015, drift=(0.4, 0.15))
    tex, INN = stone_card()
    # the summit (bottom-centre anchor at its foot, far below in the cloud)
    sm = Wd.card('b5_summit', [0, 0, 0], height=SUMMIT_H, relief=16, bend=0.12, id='summit', order=-1)
    # the stone sits where the painted one sat: at the real (displaced) depth of the summit top
    global STONE_Z
    top = Wd.card_point(sm, 962 / 1920, 1058 / 3392)
    STONE_Z = float(top[2]) + 0.6
    Wd.plane(tex, [0, STONE_Y, STONE_Z], [WC, HC], id='stone', fogk=0.0, seak=0.0, order=1)
    # the range around and below (high distance: we look up past nearer shoulders at the summit)
    for nm, pos, h, yaw in [('hgs_shoulder_l_1', [-48, -10, -30], 80, 15), ('hgs_shoulder_r_2', [52, -14, -40], 74, -15),
                            ('pillar_slender_2', [-30, -20, 30], 70, 8), ('pillar_needle_1', [36, -24, 26], 62, -8),
                            ('range_mid_1', [0, -175, -260], None, 0)]:
        if h is None:
            Wd.card(nm, pos, width=600, relief=20, ink=0.6, id=nm, order=-3)
        else:
            Wd.card(nm, pos, height=h, relief=h * 0.12, yaw=yaw, ink=0.9, id=nm, bend=0.1, order=-2)
    # near pines the camera rises past (high distance, the foreground at the bottom of the frame)
    Wd.card('pine_near_1', [-9, 34, 46], height=16, relief=1.5, yaw=10, id='pine_a')
    Wd.card('pine_near_2', [10, 52, 32], height=13, relief=1.5, yaw=-12, id='pine_b')
    if T['path'] == 'side':
        Wd.card('pine_near_1', [-14, 76, 26], height=11, relief=1.2, yaw=20, id='pine_c')
    # mist: bands between the ridges and around the summit (the hold: only these move)
    rr = np.random.default_rng(5)
    for i, (y, z, w, h, op, sp) in enumerate([(30, 40, 160, 14, 0.75, 0.9), (52, 20, 140, 12, 0.7, -0.7), (66, 8, 120, 10, 0.7, 0.6),
                                              (78, -6, 120, 9, 0.8, -0.5), (84.5, -3, 90, 5, 0.75, 0.45), (90.5, -4, 90, 4, 0.55, -0.35),
                                              (95, -20, 140, 8, 0.6, 0.3)]):
        Wd.mist([0, y, z], [w, h], opacity=op, thresh=0.42, scale=0.06, band=True, edge=0.55, soft=3, nearFade=4, wash=0.25,
                speed=[sp, 0.0], seed=float(i * 7 + 2))
    # wisps in front of the stone in the hold (they drift across and thin out before the cut)
    Wd.mist([0, STONE_Y - 2.6, STONE_Z + 4.5], [40, 2.4], opacity=0.75, thresh=0.46, scale=0.25, band=True, edge=0.6, soft=0.8,
            nearFade=1.0, wash=0.45, speed=[0.45, 0], seed=61.0,
            keys=[[0, {'opacity': 0.0}], [F_STOP - 4, {'opacity': 0.0}], [F_STOP + 10, {'opacity': 0.5}], [N - 26, {'opacity': 0.4}], [N - 6, {'opacity': 0.0}]])
    Wd.mist([0, STONE_Y + 2.6, STONE_Z - 3], [50, 3.4], opacity=0.7, thresh=0.44, scale=0.2, band=True, edge=0.6, soft=1.0,
            nearFade=1.0, wash=0.5, speed=[-0.3, 0], seed=67.0,
            keys=[[0, {'opacity': 0.0}], [F_STOP, {'opacity': 0.0}], [F_STOP + 16, {'opacity': 0.45}], [N - 20, {'opacity': 0.35}], [N - 4, {'opacity': 0.0}]])
    # gold-leaf dust (B4's) climbing the mist up the peak into the stone; the last flecks sink in after the stop
    parts = []
    tgt_c = np.array([0, STONE_Y + 0.6, STONE_Z])
    for k in range(900):
        life = rng_u(k, 1.4, 3.0)
        f_end = rng_u(k + 1, 4, F_STOP + 16)
        f0 = f_end - life * FPS
        start = np.array([rng_u(k + 2, -14, 14), rng_u(k + 3, 28, 70), rng_u(k + 4, 4, 16)])
        end = tgt_c + np.array([rng_u(k + 5, -2.4, 2.4), rng_u(k + 6, -1.6, 1.6), 0.2])
        acc = np.array([0, 0.6, 0])
        vel = (end - start) / life - 0.5 * acc * life
        parts.append([*start, f0, *vel, life, rng_u(k + 7, 0.07, 0.16), rng_u(k + 8, 0, 1)])
    Wd.points(parts, id='dust_rise', acc=[0, 0.6, 0], sway=0.5, swayF=1.2, col=[0.80, 0.60, 0.26], glowCol=[1.0, 0.74, 0.32], glow=0.8,
              opacity=0.85, minPx=1.4, maxPx=9, fadeIn=0.2, fadeOut=0.25, fogk=0.6)
    # the reading points (3D): one warm point down each column, in step with the 2D gold trail of the finish
    sx, sy = WC / 1920, HC / 1080
    rd = []
    for ts, dur, col in READS:
        cx, ya, yb = INN.cols[col % len(INN.cols)]
        p0 = np.array([(cx - 960) * sx, STONE_Y + (540 - ya) * sy, STONE_Z + 0.05])
        p1 = np.array([(cx - 960) * sx, STONE_Y + (540 - yb) * sy, STONE_Z + 0.05])
        rd.append([*p0, fr(ts), *((p1 - p0) / dur), dur, 0.085, 0.5])
    Wd.points(rd, id='reads', col=[0.86, 0.63, 0.16], glowCol=[1.0, 0.72, 0.28], glow=1.6, minPx=2, maxPx=14, fadeIn=0.08, fadeOut=0.05,
              fogk=0.0, order=8)
    # ---------------- camera
    hold_p = np.array([0, STONE_Y, STONE_Z + D_HOLD]); hold_t = np.array([0, STONE_Y, STONE_Z]); hold_fov = FOV_HOLD
    if T['hold'] == 'wide':
        hold_p = np.array([0, STONE_Y - 6.0, STONE_Z + 30]); hold_t = np.array([0, STONE_Y + 0.5, STONE_Z]); hold_fov = 34
    if T['path'] == 'rise':
        K = [(0, [5, 26, 82], [0, 74, 0], 42), (14, [3, 52, 56], [0, 82, 0], 38), (26, list(hold_p + np.array([1, -6, 12])), list(hold_t + [0, 1, 0]), 33),
             (F_STOP, list(hold_p), list(hold_t), hold_fov)]
    else:
        K = [(0, [-40, 70, 46], [-6, 84, 0], 36), (16, [-18, 80, 34], [-2, 86, 0], 33), (28, list(hold_p + np.array([-4, -1, 6])), list(hold_t), 31),
             (F_STOP, list(hold_p), list(hold_t), hold_fov)]
    P = smooth_path([(f, p) for f, p, _, _ in K], N)
    Tg = smooth_path([(f, t) for f, _, t, _ in K], N)
    FV = smooth_path([(f, fv) for f, _, _, fv in K], N)
    # the cloud sea rises to the summit as we arrive: below the stone everything is bare paper by the stop
    SEA = smooth_path([(0, 4.0), (14, 20.0), (F_STOP - 4, TOP_Y - 2.0), (F_STOP, TOP_Y + 5.0), (N - 1, TOP_Y + 5.0)], N)
    Wd.camera = []
    for f in range(N):
        if f >= F_STOP:
            p, t, fv = hold_p.tolist(), hold_t.tolist(), hold_fov
        else:
            p, t, fv = list(P[f]), list(Tg[f]), float(FV[f])
        Wd.camera.append(dict(p=p, t=t, fov=fv, near=0.3, far=4000, seaY=float(SEA[f]), seaSoft=6.0 if f < F_STOP else 5.0))
    info = dict(take=take, F_STOP=F_STOP, D_HOLD=D_HOLD, TOP_Y=TOP_Y, STONE_Y=STONE_Y, cols=len(INN.cols))
    json.dump(info, open(os.path.join(Wd.dir, 'meta.json'), 'w'), indent=1)
    return Wd, INN, info


def rng_u(k, a, b):
    return float(np.random.default_rng(1000 + k * 7919).uniform(a, b))


def finish(Wd, INN, take, out=None, sheet_out=None):
    from tools.ink.inscription import inscription
    from tools.ink.paper import Paper
    G = paper_grain(1920, 1080)
    P = Paper(1920, 1080, 'new', seed=1988)
    ins = inscription((1920, 1080), 'B5', box=(1620, 120, 240, 700), paper=P)
    ims = []
    for f in range(N):
        img = Wd.finish_frame(f, grain=G, bloom=1.2, glow_gain=1.0)
        t = (f + F_IN) / FPS
        if TAKES[take]['hold'] == 'c1' and f >= F_STOP:
            # the gold trail under the reading point (the camera is locked on C1's framing, so 2D = 3D here)
            for ts, dur, col in READS:
                if ts <= t < ts + dur + 0.4:
                    u = (t - ts) / dur
                    INN.read(img, col, min(u, 1.0), 1.0, strength=1.0 if u <= 1 else max(0.0, 1 - (u - 1) * dur / 0.4), spot=False)
        ins.draw(img)
        ims.append(np.clip(img, 0, 1))
    if out:
        encode(iter(ims), out, N)
    sheet(ims, sheet_out or f'work/review/comp_v4/_cand/B5_{take}.jpg', label=f'B5{take}')
    return ims


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    frames = sys.argv[sys.argv.index('--frames') + 1] if '--frames' in sys.argv else None
    args = [a for a in args if a != frames]
    take = args[0] if args else 'a'
    Wd, INN, info = build(take)
    print(json.dumps(info))
    Wd.render(ss=2, frames=frames, passes=['beauty', 'glow'])
    if frames is None:
        final = '--final' in sys.argv
        finish(Wd, INN, take, out='media/comp/B5.mp4' if final else f'work/world/B5_{take}.mp4',
               sheet_out='work/review/comp_v4/B5.jpg' if final else None)

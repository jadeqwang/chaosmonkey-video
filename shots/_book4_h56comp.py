"""shots/_book4_h56comp.py: compositing for H5/H6 candidate A (BOOK v4). The physics and the stroke render are baked
by shots/_book4_strokes.py in its own process (GPU); this module only reads the bake (numpy, safe in forked workers).

Layers, back to front: the carved cliff (MMAH re-carve; each stroke's cinnabar leaves the cut at its own peel front,
leaving a pale ghost-mark) -> fades to bare paper in H6 -> the strokes (baked transmittance, motion blur and DOF
inside) -> the monkey drawn on along the hero strand (H6) -> the mist veil at the right edge -> the inscription.
"""
import math
import os
import subprocess
import sys

import cv2
import numpy as np

from shots._mountain import *            # noqa: F401,F403
from shots import _book4_strokes as BS

PY = sys.executable
G = {}


def ensure_bake(W, H, extra=()):
    d = BS.WORK / f'bake/{W}x{H}'
    sim = BS.WORK / 'sim/sim.npz'
    if not sim.exists() or os.path.getmtime(sim) < os.path.getmtime(BS.__file__):
        subprocess.run([PY, '-m', 'shots._book4_strokes', 'sim'], check=True, cwd=str(ROOT))
    last = d / f'f{BS.NFR - 1:04d}.png'
    if not last.exists() or os.path.getmtime(last) < os.path.getmtime(sim):
        subprocess.run([PY, '-m', 'shots._book4_strokes', 'bake', f'{W}x{H}'], check=True, cwd=str(ROOT))
    return d


def setup(ctx, key):
    G['key'] = key
    G['bake'] = ensure_bake(ctx.W, ctx.H)
    raw = load_image(B + 'B_cliff_run.png')
    H, W = raw.shape[:2]
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    G['canvas_paper'] = paper.rgb
    # bare paper for H6 once the cliff is gone: the same sheet, extended upward (the camera follows the strand there)
    top = Paper(W, 720, 'new', seed=BOOK_PAPER_SEED + 7).rgb
    G['tall_paper'] = np.concatenate([top, paper.rgb], 0)
    G['tall_off'] = 720
    rock = onto_paper(raw, paper)
    G['rock'] = rock
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wn = fbm(H, W, 220.0, 7, 'b4_w', octaves=3)
    weather = np.clip((0.08 + 0.42 * xx / W) * (0.55 + 0.9 * wn), 0, 0.85).astype(np.float32)
    C = BS.make_cliff(rock, qianziwen(160), weather=weather, presence='plane', chips=0.3, streaks=0.4, jitter=0.04,
                      weight=0.0, paint=0.8, depth=1.3, grime=0.35)
    C.prepare(fill=0.65)
    G['C'] = C
    # the peel front on the stone: release time per plane pixel
    sc = BS.scene_cached()
    d = np.load(BS.WORK / 'sim/sim.npz')
    G['cam'] = np.load(BS.WORK / 'sim/cam.npy')
    G['hero'] = int(d['hero'])
    G['rec_hero'] = d['rec'][:, :, G['hero']].copy()
    TR = np.full((H, W), 1e9, np.float32)
    for s, st in enumerate(sc['strokes']):
        pts = np.concatenate(st.outline, 0)
        x0, y0 = np.floor(pts.min(0)).astype(int) - 3
        x1, y1 = np.ceil(pts.max(0)).astype(int) + 4
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        for p in st.outline:
            cv2.fillPoly(m, [np.round((p - [x0, y0]) * 16).astype(np.int32)], 1, cv2.LINE_8, 4)
        m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        ys, xs = np.nonzero(m)
        dense, _ = BS.resample(st.med, 100)
        dd = ((np.stack([xs + x0, ys + y0], 1)[:, None, :] - dense[None]) ** 2).sum(-1)
        u = dd.argmin(1) / 99.0
        uu = (1 - u) if sc['peel_from_end'][s] else u
        tr = sc['t_peel'][s] + sc['peel_dur'][s] * uu
        cur = TR[ys + y0, xs + x0]
        TR[ys + y0, xs + x0] = np.minimum(cur, tr)
    G['TR'] = TR
    # screen paper, veil, inscription (v3 placement)
    from tools.ink.inscription import inscription
    PFR = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED)
    G['PFR'] = PFR
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(np.float32)
    nn = fbm(ctx.H, ctx.W, 260 * ctx.s, 31, 'veil', octaves=3) - 0.5
    if key == 'H5':
        G['VEIL'] = smoothstep(0.775, 0.865, xx / ctx.W + nn * 0.10).astype(np.float32)
        G['INS'] = inscription(ctx, 'H5', box=(1640, 120, 220, 720), paper=PFR)
    else:
        G['VEIL'] = smoothstep(0.700, 0.800, xx / ctx.W + nn * 0.10).astype(np.float32)
        G['INS'] = inscription(ctx, 'H6', box=(1500, 110, 340, 720), paper=PFR)
        G['VEIL0'] = smoothstep(0.775, 0.865, xx / ctx.W + nn * 0.10).astype(np.float32)
    # a mist gathers behind her as she completes (her lines read on bare paper, not on the fissured rock)
    m = cv2.imread(str(ROOT / 'work/mountain/child_back_mask.png'), 0).astype(np.float32) / 255
    PADM = 360
    m = np.pad(m, PADM)
    k = int(70)
    md = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    md = blur(md, 85)
    md = md / max(1e-6, md.max())
    nz = fbm(md.shape[0], md.shape[1], 120, 4, 'girlmist', octaves=3)
    G['MIST'] = np.clip(smoothstep(0.12, 0.75, md + (nz - 0.5) * 0.35), 0, 1).astype(np.float32)
    G['MIST_PAD'] = PADM
    G['monkey'] = None
    try:
        from shots import _book4_monkey as MK
        G['monkey'] = MK.Monkey(ctx)
    except Exception as e:                                     # the monkey module is optional while developing
        print('monkey layer off:', e)


def _cliff_window(box, t, fade):
    C, TR = G['C'], G['TR']
    light = (335.0, 13.0, 1.0)
    x0, y0, x1, y1 = box
    filled = C.render(light, fill=0.65, ambient=0.86, warmth=0.85, box=box)
    ghost = C.render(light, fill=0.0, ambient=0.86, warmth=0.85, box=box)
    rock = BS_win(G['rock'], box)
    ghost = 0.55 * ghost + 0.45 * rock                         # the cut stays, paler; the colour is gone
    tr = BS_win(TR, box, fillv=1e9)
    present = smoothstep(t - 0.03, t + 0.03, tr)[..., None]
    out = ghost + (filled - ghost) * present
    if fade > 0:
        pap = BS_win(G['canvas_paper'], box)
        out = out + (pap - out) * fade
    return out


def BS_win(A, box, fillv=None):
    x0, y0, x1, y1 = [int(v) for v in box]
    h, w = A.shape[:2]
    shp = (y1 - y0, x1 - x0) + A.shape[2:]
    out = np.full(shp, fillv if fillv is not None else 0, A.dtype)
    if fillv is None:
        out = np.zeros(shp, A.dtype)
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    if a1 > a0 and b1 > b0:
        out[b0 - y0:b1 - y0, a0 - x0:a1 - x0] = A[b0:b1, a0:a1]
    if fillv is None and A.ndim == 3:                          # edge: replicate the paper colour
        pass
    return out


def frame_index(t):
    return int(round(t * 24)) - BS.F_H5


def cliff_fade(ts):
    return float(BS._ease((ts - (BS.T_H6 + 0.0)) / 1.1))


def render(t, ctx):
    f = frame_index(t)
    ts = f / 24.0                                              # sim time
    cam = G['cam'][f]
    fade = cliff_fade(ts)
    W, H = ctx.W, ctx.H
    out = None
    if fade < 0.999:
        # cliff, with motion blur when the camera travels fast (H6)
        c0, c1 = cam[0], cam[-1]
        speed = abs(c1[0] - c0[0]) * BS.FOCAL / (-c0[2]) * ctx.s
        taps = [cam[2]] if speed < 3 else [cam[0], cam[2], cam[3], cam[5]]
        acc = None
        for c in taps:
            z = BS.cliff_zoom(c)
            v = view(None, c[0], c[1], z, W, H, render=lambda box: _cliff_window(box, ts, fade))
            acc = v if acc is None else acc + v
        out = acc / len(taps)
        # the mist behind her (screen-space warp of her silhouette, on her plane)
        mg = ramp(ts, 1.1, 2.9, 'sine') * 0.40
        if mg > 0:
            c = cam[2]
            kk = BS.GIRL_H / BS.MASK_H
            dz = BS.GIRL_Z - c[2]
            sc_ = BS.FOCAL * ctx.s / dz
            # mask px (with pad) -> screen
            ox = W / 2 + sc_ * (BS.GIRL_X - BS.MASK_W / 2 * kk - c[0]) - sc_ * kk * G['MIST_PAD']
            oy = H / 2 + sc_ * (BS.GIRL_FEET - BS.MASK_H * kk - c[1]) - sc_ * kk * G['MIST_PAD']
            M = np.float32([[sc_ * kk, 0, ox], [0, sc_ * kk, oy]])
            mm = cv2.warpAffine(G['MIST'], M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
            pap = view(G['canvas_paper'], c[0], c[1], BS.cliff_zoom(c), W, H)
            out = out + (pap - out) * (mm * mg)[..., None]
    else:
        c = cam[2]
        out = view(G['tall_paper'], c[0], c[1] + G['tall_off'], BS.cliff_zoom(c), W, H)
    T = cv2.imread(str(G['bake'] / f'f{f:04d}.png'))[..., ::-1].astype(np.float32) / 255.0
    out = out * T
    if G['monkey'] is not None and G['key'] == 'H6':
        G['monkey'].draw(out, ts, f, cam)
    veil = G['VEIL']
    if G['key'] == 'H6':
        # the H5 veil at the cut, widening to the H6 veil within the first half second
        k = BS._ease(ts - BS.T_H6) if ts > BS.T_H6 else 0.0
        veil = G['VEIL0'] + (G['VEIL'] - G['VEIL0']) * k
    out += (G['PFR'].rgb - out) * veil[..., None]
    if not os.environ.get('H56_NOINS'):
        G['INS'].draw(out)
    return np.clip(out, 0, 1).astype(np.float32)

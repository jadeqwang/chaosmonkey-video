"""shots/_dflight2.py: D4 -> D5 -> D6 flight, ROUND 2 (R2_3D; notes work/world/notes/R2_3D.md). Same range, schedule
and shared-component jumps as shots/_dflight.py (round 1, take b = current pick), plus:
  (a) veins: every jump lights its glyph and the light then runs along the glyph's carved column (irregular run lengths,
      gaps, tapering brightness); most glyphs stay dark; a thin gold vein thread along each long run reads from afar;
  (b) day -> dusk: camera paper keys go cool and dark, card lum/tint keys darken and cool the rock (post wash in
      shots/_dfinish2.py), so the lit country burns at the end;
  (c) the travelling frontier: thick frontier threads (headW bead at the drawing head), gold flecks bursting at arrivals;
  (d) mass: two side cards per palm pillar (flanks at an angle), painted outlined cloud heads in the sea and between
      ridges, near pines crossing the lens in the retreat, more far range cards (3+ bands);
  (e) D6: no cloud-bank white-out; gold rays behind the palm from 75.025 (3D, occluded by the rock); the monkey's arc is
      in _dfinish2.py.
    DF2_TAKE=r2a|r2b|r2c DF_FRAMES=0,40 DF_SS=2 DF_PASSES=beauty,glow[,typeset,typeset_a] $PY shots/_dflight2.py
Renders to work/world/Dflight_<take>/frames.
"""
import collections
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.world.scene import World, smooth_path  # noqa: E402
from tools.world.carve import Carving, qianziwen  # noqa: E402
from _dflight import (PALM, LOW, fields, comps_table, comps, fr, N, D4N, D5N, T_TONG, GEN_T, GEN_STAGGER, T_GONG,  # noqa: E402
                      GLOW)

T_LIAN = 75.025                     # 亮相: the rays
CARVE_DIR = 'work/world/Dflight_r2'
TAKES = {
    # camera variant, dusk end values
    'r2a': dict(cam='arc', paper=[0.86, 0.83, 0.77], lum=0.55, tint=[0.86, 0.92, 1.06]),
    'r2b': dict(cam='high', paper=[0.80, 0.79, 0.78], lum=0.48, tint=[0.80, 0.88, 1.10]),
    'r2c': dict(cam='low', paper=[0.85, 0.81, 0.74], lum=0.52, tint=[0.86, 0.92, 1.07]),
}


def build(take='r2a'):
    TK = TAKES[take]
    Wd = World('Dflight_' + take, N)
    Wd.fog(density=0.0009, start=100)
    Wd.sea(y=0.0, soft=16.0, amp=34.0, scale=0.010, drift=(0.6, 0.25))
    from fontTools.ttLib import TTFont
    from tools.world.carve import SEAL_FONT, ROOT as _R
    cmap = TTFont(os.path.join(_R, SEAL_FONT)).getBestCmap()
    chars = [c for c in qianziwen() if ord(c) in cmap]          # no tofu boxes: only characters the seal font has
    chars_all = chars * 6
    cursor = [0]

    def take_chars(k):
        out = [chars_all[(cursor[0] + i) % len(chars_all)] for i in range(k)]
        cursor[0] += k
        return out

    pillars = []
    idx_mid = None
    for name, x, z, h, roll, role in PALM:
        CV = Carving(f'design/world/cards/{name}_rgba.png', size=4096, seed=len(pillars))
        px = 3.0 / h * 4096
        if role == 'middle':
            dry = Carving(f'design/world/cards/{name}_rgba.png', size=4096)
            MAIN = (0.18, 0.26, 0.82, 0.60)
            cells = dry.field(MAIN, ['口'] * 4000, px=px)
            Carving._next[0] -= len(cells)
            tgt = min(range(len(cells)), key=lambda i: (cells[i]['u'] - 0.5) ** 2 + ((cells[i]['v'] - 0.40) * 2.4) ** 2)
            seq = take_chars(len(cells))
            seq = [c for c in seq if c != '通']
            fam = [c for c in dict.fromkeys(chars) if '辶' in comps(c) and c != '通']
            seq = [c for c in seq if c not in fam]
            pos = np.array([[c['u'] * h * 0.4167, c['v'] * h] for c in cells])
            d = np.hypot(*(pos - pos[tgt]).T)
            near = [i for i in np.argsort(d) if 5 < d[i] < 17][:len(fam)]
            plan = {tgt: '通'}
            rng = np.random.default_rng(3)
            rng.shuffle(near)
            for i, ch in zip(near, fam):
                plan[i] = ch
            it = iter(seq)
            order = [plan[i] if i in plan else next(it) for i in range(len(cells))]
            gl = CV.field(MAIN, order, px=px)
            gl += CV.field((0.28, 0.64, 0.74, 0.80), take_chars(800), px=2.0 / h * 4096)
            gl += CV.field((0.36, 0.11, 0.66, 0.22), take_chars(200), px=4.6 / h * 4096)
        else:
            gl = []
            for rect, gw in fields(np.random.default_rng(100 + len(pillars))):
                gl += CV.field(rect, take_chars(3000), px=gw / h * 4096)
        CV.save(f'{CARVE_DIR}/carve_{len(pillars)}_{name}')
        pillars.append(dict(name=name, CV=CV, glyphs=gl, x=x, z=z, h=h, roll=roll, role=role, ring=0 if role == 'middle' else 1, tex=4096))
        if role == 'middle':
            idx_mid = len(pillars) - 1
    for name, x, z, h, roll in LOW:
        CV = Carving(f'design/world/cards/{name}_rgba.png', size=2048, seed=len(pillars))
        gl = []
        for rect, gw in fields(np.random.default_rng(200 + len(pillars))):
            gl += CV.field(rect, take_chars(3000), px=(gw * 0.62) / h * 2048, need=0.7)
        CV.save(f'{CARVE_DIR}/carve_{len(pillars)}_{name}')
        pillars.append(dict(name=name, CV=CV, glyphs=gl, x=x, z=z, h=h, roll=roll, role='low', ring=None, tex=2048))
    dist = [math.hypot(p['x'], p['z']) for p in pillars]
    lows = sorted([i for i, p in enumerate(pillars) if p['role'] == 'low'], key=lambda i: dist[i])
    lows = [i for i in lows if pillars[i]['z'] <= 100]
    for k, i in enumerate(lows):
        pillars[i]['ring'] = 2 + int(k * 5 / len(lows))
    for p in pillars:
        if p['ring'] is None:
            p['ring'] = 6

    # ---------------- schedule: true jumps by shared component (identical to round 1)
    inst = []
    for pi, p in enumerate(pillars):
        for g in p['glyphs']:
            inst.append((pi, g))
    cols = collections.defaultdict(list)          # (pillar, px, column x) -> [k] sorted by v
    for k, (pi, g) in enumerate(inst):
        cols[(pi, round(g['px'], 2), round(g['u'] * 4000))].append(k)
    colof = {}
    for key, ks in cols.items():
        ks.sort(key=lambda k: inst[k][1]['v'])
        for j, k in enumerate(ks):
            colof[k] = (key, j)
    col_lit = collections.Counter()               # lit glyphs per column: the light prefers columns already alight
    C = comps_table(set(g['ch'] for _, g in inst))
    by_comp = collections.defaultdict(list)
    for k, (pi, g) in enumerate(inst):
        for c in C[g['ch']]:
            by_comp[c].append(k)
    lit = {}                                     # k -> (frame, gen, gain)
    edges = []
    k_tong = next(k for k, (pi, g) in enumerate(inst) if pi == idx_mid and g['ch'] == '通')
    lit[k_tong] = (fr(T_TONG), 0, 1.5)
    via = {k_tong: '辶'}
    rng = np.random.default_rng(7)
    g1 = [k for k in by_comp['辶'] if inst[k][0] == idx_mid and k != k_tong]
    g1.sort(key=lambda k: math.hypot(inst[k][1]['u'] - inst[k_tong][1]['u'], inst[k][1]['v'] - inst[k_tong][1]['v']))
    gens = [[(k_tong, k, '辶') for k in g1]]
    for _, k, c in gens[0]:
        via[k] = c
    caps = [None, 30, 60, 110, 190, 300, 380, 460]
    frontier = [k for _, k, _ in gens[0]]
    for g in range(1, len(GEN_T)):
        max_ring = g
        new = []
        used = set(lit) | set(k for gg in gens for _, k, _ in gg)
        for s in frontier:
            for c in sorted(C[inst[s][1]['ch']]):
                if c == via.get(s):
                    continue
                cand = [d for d in by_comp[c] if d not in used and pillars[inst[d][0]]['ring'] <= max_ring]
                if not cand:
                    continue
                cand.sort(key=lambda d: (-pillars[inst[d][0]]['ring'], -min(col_lit[colof[d][0]], 3) - 2 * rng.random()))
                for d in cand[:2 if g < 3 else 3]:
                    new.append((s, d, c)); used.add(d); via[d] = c; col_lit[colof[d][0]] += 1
                if len(new) >= caps[g]:
                    break
            if len(new) >= caps[g]:
                break
        if not new:
            break
        gens.append(new)
        frontier = [d for _, d, _ in new]
    for g, lst in enumerate(gens):
        t0 = GEN_T[g]
        sp = GEN_STAGGER[g]
        for j, (s, d, c) in enumerate(lst):
            f = fr(t0 + sp * j / max(1, len(lst) - 1))
            edges.append((s, d, f, g))
            lit[d] = (f + 3, g + 1, 1.35)          # a node: brighter than its vein

    # ---------------- (a) veins: the light runs along the carved column from every node
    def adjacent(a, b):
        ga, gb = inst[a][1], inst[b][1]
        H = pillars[inst[a][0]]['tex']
        return abs(ga['v'] - gb['v']) * H < ga['px'] * 1.12 * 1.6

    rv = np.random.default_rng(21)
    runs = []                                      # [(pillar, [k...], [frame...])]

    def vein(k, f, gen, g0, lo=2, hi=9, step=1.6):
        key, j = colof[k]
        ks = cols[key]
        for dr in (-1, 1):
            if rv.random() < 0.25:
                continue                            # a vein often runs one way only
            L = int(rv.integers(lo, hi + 1))
            seq, fs, prev = [k], [f], k
            for i in range(1, L + 1):
                jj = j + dr * i
                if jj < 0 or jj >= len(ks):
                    break
                nb = ks[jj]
                if not adjacent(prev, nb) or nb in lit:
                    break
                if rv.random() < 0.10:
                    break                           # the vein breaks off
                ff = f + int(round(i * step * rv.uniform(0.7, 1.3)))
                taper = max(0.22, 1.0 - i / (L + 1.5)) * rv.uniform(0.65, 1.15)
                lit[nb] = (ff, gen, g0 * taper)
                seq.append(nb); fs.append(ff); prev = nb
            if len(seq) >= 3:
                runs.append((inst[k][0], seq, fs))

    for k, (f, gen, gain) in sorted(list(lit.items()), key=lambda kv: kv[1][0]):
        if rv.random() < (0.9 if gen <= 1 else 0.45):
            vein(k, f + 1, gen, 0.95, *((1, 4) if gen <= 1 else (2, 7)))
    # on the gong the veins spread: runs grow out of lit columns, and sparse new veins wake all over the country
    fg = fr(T_GONG)
    for k in list(lit):
        if rv.random() < 0.15:
            vein(k, fg + int(rv.integers(0, 6)), 99, 0.8, 2, 8, 1.2)
    for k in range(len(inst)):
        if k not in lit and rv.random() < 0.006:
            lit[k] = (fg + int(rv.integers(0, 8)), 99, 0.9)
            vein(k, lit[k][0], 99, 0.85, 3, 12, 1.2)

    # ---------------- cards: palm + flanks, low country; dusk keys
    dusk_end = N - 1
    cards = []
    side_tex = ['pillar_stacked_1', 'pillar_needle_2', 'pillar_twin_2', 'pillar_stacked_2', 'pillar_broad_2']
    for pi, p in enumerate(pillars):
        litl = [(inst[k][1]['id'], v[0], float(v[2])) for k, v in lit.items() if inst[k][0] == pi]
        relief = p['h'] * 0.16
        kk = [[0, {'lum': 1.0, 'tint': [1, 1, 1]}], [fr(71.0), {'lum': 0.93, 'tint': [0.97, 0.98, 1.0]}],
              [fr(T_GONG), {'lum': 0.5 * (0.74 + TK['lum']) + 0.05, 'tint': [(1 + t) / 2 for t in TK['tint']]}],
              [dusk_end, {'lum': TK['lum'], 'tint': TK['tint']}]]
        o = Wd.card(p['name'], [p['x'], -40, p['z']], height=p['h'], relief=relief, roll=p['roll'], bend=0.10,
                    carve=p['CV'].spec(lit=litl, glow=GLOW, dark=0.5, base=1.1, glow_fog=0.45), seg=[160, 384] if p['role'] != 'low' else [96, 192],
                    id=f'p{pi}', lum=1.0, keys=kk)
        p['card'] = o
        cards.append(o)
        if p['role'] != 'low':
            # (d) mass: two flanks turning away behind the face (a darker, cooler rock: the side in shadow)
            w = o['size'][0]
            for s in (-1, 1):
                ang = math.radians(p['roll'])
                fx = p['x'] + s * 0.30 * w * math.cos(ang)
                kf = [[f0, dict(lum=v['lum'] * 0.74, tint=[v['tint'][0] * 0.92, v['tint'][1] * 0.96, v['tint'][2] * 1.04])] for f0, v in kk]
                Wd.card(side_tex[(pi * 2 + (s > 0)) % len(side_tex)], [fx, -40, p['z'] - 0.22 * w], height=p['h'] * rv.uniform(0.86, 0.96),
                        relief=relief * 0.8, roll=p['roll'] + s * 2, yaw=s * rv.uniform(38, 52), bend=0.12, id=f'p{pi}f{s}', seg=[96, 256],
                        order=-1, keys=kf)
    # far country: 4 bands (mid 1, mid 2, far 1, far 2) + the round-1 carved ranges
    for k, (nm, pos, wid, rel) in enumerate([('range_mid_1', [0, -235, -900], 1500, 30), ('range_far_1', [-300, -380, -1500], 2400, 40),
                                              ('range_far_2', [600, -470, -1900], 2800, 40)]):
        CVr = Carving(f'design/world/cards/{nm}_rgba.png', size=1706, pale=0.35, seed=90 + k)
        glr = []
        rr2 = np.random.default_rng(300 + k)
        for j in range(14):
            u0 = rr2.uniform(0.05, 0.9); v0 = rr2.uniform(0.3, 0.75)
            glr += CVr.field((u0, v0, u0 + rr2.uniform(0.02, 0.06), v0 + rr2.uniform(0.04, 0.12)), take_chars(400), px=10, need=0.6)
        CVr.save(f'{CARVE_DIR}/carve_range{k}')
        t_lit = fr(GEN_T[6 + min(k, 1)]) if k < 2 else fr(T_GONG)
        # far ranges: lit in short vertical runs only (a vein reads; a scatter of dots does not)
        litr = [(g['id'], t_lit + int(rng.integers(0, 10)), 0.8) for g in glr if rng.random() < 0.45]
        Wd.card(nm, pos, width=wid, relief=rel, lum=0.95, fogk=1.7,
                carve=CVr.spec(lit=litr, glow=GLOW, dark=0.3, base=1.2, glow_fog=0.3),
                keys=[[0, {'lum': 0.95, 'tint': [1, 1, 1]}], [fr(T_GONG), {'lum': 0.8}], [dusk_end, {'lum': TK['lum'] + 0.08, 'tint': TK['tint']}]])
    for k, (nm, pos, wid, lum) in enumerate([('range_mid_1', [-700, -150, -520], 1100, 0.85), ('range_far_2', [-900, -260, -1150], 1900, 0.9),
                                              ('range_far_1', [900, -300, -1250], 2000, 0.9), ('range_mid_1', [820, -170, -650], 1200, 0.85),
                                              ('range_far_1', [100, -560, -2600], 3600, 0.95)]):
        Wd.card(nm, pos, width=wid, relief=30, lum=lum, fogk=1.5, id=f'band{k}',
                keys=[[0, {'lum': lum, 'tint': [1, 1, 1]}], [dusk_end, {'lum': lum * 0.82, 'tint': TK['tint']}]])

    W_ = {}

    def wpos(k):
        if k not in W_:
            pi, g = inst[k]
            W_[k] = np.array(Wd.card_point(pillars[pi]['card'], g['u'], g['v']))
        return W_[k]

    # ---------------- (c) threads: the frontier thick, a bead at the head; flecks burst where they land
    TCAP = [99, 30, 34, 34, 30, 26, 18, 10]
    TW = [3.2, 4.6, 4.4, 4.2, 4.0, 3.8, 3.6, 3.4]
    parts = []
    for g in range(len(gens)):
        eg = [e for e in edges if e[3] == g]
        eg.sort(key=lambda e: -np.linalg.norm(wpos(e[0]) - wpos(e[1])))
        eg = [e for e in eg if (wpos(e[1])[2] < 60 and wpos(e[1])[2] > -700 and np.linalg.norm(wpos(e[1]) - wpos(e[0])) < 520) or g < 2]
        for s, d, f, _ in eg[:TCAP[g]]:
            a, b = wpos(s), wpos(d)
            L = np.linalg.norm(b - a)
            mid = (a + b) / 2 + np.array([0, 1, 0]) * min(0.40 * L, 130.0) + np.array([0, 0, 1]) * (0.05 * L)
            pts = [list(a * (1 - t) ** 2 + mid * 2 * t * (1 - t) + b * t * t) for t in np.linspace(0, 1, 32)]
            fd = 3 if L < 30 else 5 + int(L / 120)
            Wd.thread(pts, f0=f, fdraw=fd, fhold=8 if g >= 2 else 14, ffade=12, rest=0.0, width=TW[g], col=list(GLOW), glow=1.2,
                      headW=1.6, headG=1.5)
            if g >= 1:
                for _ in range(10):
                    v = rv.normal(0, 1, 3); v = v / np.linalg.norm(v) * rv.uniform(2, 7) * (1 + L / 200)
                    parts.append([*b, f + fd, *v, rv.uniform(0.35, 0.8), rv.uniform(0.3, 0.7), rv.random()])
    Wd.points(parts, id='sparks', col=[1.0, 0.86, 0.5], glowCol=[1.0, 0.72, 0.3], glow=1.6, minPx=1.4, maxPx=7, fadeIn=0.02,
              fadeOut=0.6, acc=[0, -3, 0], fogk=0.4)
    # (a) vein threads along the long runs: invisible close up (the glyphs carry it), a thin line of light from afar
    nv = 0
    for pi, seq, fs in sorted(runs, key=lambda r: -len(r[1]))[:2500]:
        o = pillars[pi]['card']
        nrm = np.array(Wd.card_normal(o))
        P = [np.array(Wd.card_point(o, inst[k][1]['u'], inst[k][1]['v'])) + nrm * 0.8 for k in seq]
        # densify between glyph centres
        pts = []
        for a, b in zip(P[:-1], P[1:]):
            for t in np.linspace(0, 1, 4, endpoint=False):
                pts.append(list(a + (b - a) * t))
        pts.append(list(P[-1]))
        g0 = inst[seq[0]][1]
        size = g0['px'] / pillars[pi]['tex'] * pillars[pi]['h']
        Wd.thread(pts, f0=fs[0], fdraw=max(1, fs[-1] - fs[0]), fhold=999, ffade=1, rest=1.0, width=1.5 if size < 4 else 1.9,
                  col=[1.0, 0.74, 0.32], glow=1.0, opacity=1.0, distFade=[30 * size / 3, 90 * size / 3], order=9)
        nv += 1

    P_t = wpos(k_tong)
    nrm = np.array([0.0, 0.0, 1.0])
    gtong = inst[k_tong][1]
    hm = pillars[idx_mid]['h']
    glyph_w = gtong['px'] / 4096 * hm
    macro = Carving('design/world/cards/granite_macro_1_rgba.png', size=2160, pale=0.0)
    gpx = int(2160 * glyph_w / 9.0); hw = gpx * 0.62 / 3840; hv = gpx * 0.62 / 2160
    mg = macro.field((0.5 - hw, 0.5 - hv, 0.5 + hw, 0.5 + hv), ['通'], px=gpx, need=0.0)
    macro.save(f'{CARVE_DIR}/carve_macro')
    Wd.overlay('design/world/cards/granite_macro_1_rgba.png', list(P_t + nrm * 0.6), [16.0, 9.0], id='macro',
               carve=macro.spec(lit=[(mg[0]['id'], fr(T_TONG), 1.0)], glow=GLOW, dark=0.55, base=0.8), round=0.55,
               keys=[[0, {'opacity': 1.0}], [13, {'opacity': 1.0}], [24, {'opacity': 0.0}]], edge=0.0)

    # ---------------- mist (round 1) minus the cloud-bank slices
    Wd.mist(list(P_t + nrm * 2.0 + np.array([-9, -0.5, 0])), [9, 2.6], opacity=0.95, thresh=0.36, scale=0.6, band=True, edge=0.6,
            soft=0.4, nearFade=0.5, wash=0.15, speed=[0.4, 0.0],
            keys=[[0, {'pos': list(P_t + nrm * 2.0 + np.array([-8, -0.6, 0])), 'opacity': 0.0}],
                  [3, {'opacity': 0.9}], [16, {'pos': list(P_t + nrm * 2.0 + np.array([6, 0.8, 0])), 'opacity': 0.8}],
                  [28, {'pos': list(P_t + nrm * 2.0 + np.array([14, 1.5, 0])), 'opacity': 0.0}]])
    rr = np.random.default_rng(11)
    for i in range(14):
        z = -60 + i * 45 + rr.uniform(-12, 12)
        y = rr.uniform(20, 95)
        Wd.mist([rr.uniform(-80, 80), y, z], [rr.uniform(300, 520), rr.uniform(18, 40)], opacity=rr.uniform(0.55, 0.8),
                thresh=rr.uniform(0.38, 0.5), scale=0.03, band=True, edge=0.5, soft=10, nearFade=12, wash=0.3,
                speed=[rr.uniform(0.6, 1.4) * rr.choice([-1, 1]), 0.0], seed=float(i))
    for i in range(6):
        Wd.mist([0, 12 + i * 7, 100], [1600, 1600], pitch=-90, opacity=0.75, thresh=0.42 + 0.03 * i, scale=0.006, edge=0.3,
                soft=12, wash=0.35, speed=[0.8, 0.3], seed=40.0 + i, nearFade=20)

    # ---------------- (d) painted cloud heads: in the sea between the fingers and the low peaks, rising with the sea
    SEA = smooth_path([(0, 0.0), (D4N + D5N, 6.0), (D4N + D5N + 18, 45), (N - 1, 80)], N)
    rc = np.random.default_rng(31)
    cl = []
    for i in range(26):
        ang = rc.uniform(0, 2 * math.pi); rad = rc.uniform(60, 700)
        x, z = rad * math.sin(ang) * 1.2, rad * math.cos(ang) - 120
        if z > 150 or (abs(x) < 170 and -80 < z < 60):
            continue
        cl.append((x, z))
    for i, (x, z) in enumerate(cl):
        nm = ['cloud_bank_1', 'cloud_head_1', 'cloud_bank_2', 'cloud_head_2'][i % 4]
        wid = rc.uniform(70, 160) * (1.6 if 'bank' in nm else 1.0) * (1 + max(0, -z) / 900)
        y0 = rc.uniform(-12, 6)
        Wd.card(nm, [x, y0, z], width=wid, relief=wid * 0.04, billboard=True, seak=0.0, fogk=1.0, edge=0.25, id=f'cloud{i}',
                keys=[[f, {'pos': [x, y0 + SEA[f] * 0.95, z], 'lum': 1.0 - 0.18 * f / (N - 1), 'tint': [1 - 0.08 * f / (N - 1), 1 - 0.04 * f / (N - 1), 1.0]}]
                      for f in (0, D4N + D5N, D4N + D5N + 18, N - 1)])
    # ---------------- camera
    KEYS = [
        (0, P_t + nrm * 6.5, P_t),
        (14, P_t + nrm * 9.5 + np.array([0.3, 0.3, 0]), P_t + np.array([0, 0.2, 0])),
        (32, P_t + nrm * 34 + np.array([2, 3, 0]), P_t + np.array([0, 1, 0])),
        (55, np.array([12, P_t[1] + 14, 100]), np.array([2, P_t[1] - 4, 0])),
        (85, np.array([-15, 172, 230]), np.array([0, 100, -40])),
        (fr(T_GONG), np.array([5, 222, 335]), np.array([0, 78, -130])),
        (D4N + D5N, np.array([0, 236, 380]), np.array([-4, 86, -100])),
        (D4N + D5N + 20, np.array([-8, 245, 405]), np.array([-12, 130, -40])),
        (N - 1, np.array([-16, 215, 420]), np.array([-16, 168, 0])),     # R2: palm lower in frame, sky for arc + rays
    ]
    if TK['cam'] == 'arc':
        sw = {55: [60, 6, -20], 85: [95, 10, -40], fr(T_GONG): [70, 0, -30], D4N + D5N: [40, 0, -10]}
    elif TK['cam'] == 'high':
        sw = {85: [0, 40, -20], fr(T_GONG): [0, 60, -10], D4N + D5N: [0, 50, 0], D4N + D5N + 20: [0, 30, 0]}
    else:   # low: weave out between the fingers at their waists, the corridor peaks pass under and beside, rise late
        sw = {55: [-26, -4, -8], 85: [-70, -70, -70], fr(T_GONG): [-60, -95, -60], D4N + D5N: [-30, -40, -20], D4N + D5N + 20: [-10, -10, 0]}
    KEYS = [(f, p + np.array(sw.get(f, [0, 0, 0]), float), t) for f, p, t in KEYS]
    P = smooth_path([(f, list(p)) for f, p, _ in KEYS], N)
    T = smooth_path([(f, list(t)) for f, _, t in KEYS], N)
    FOV = smooth_path([(0, 34), (32, 36), (D4N + D5N, 36), (N - 1, 33)], N)
    PAPER = smooth_path([(0, [0.925, 0.886, 0.800]), (fr(71.0), [0.905, 0.865, 0.785]),
                         (fr(T_GONG), list((np.array([0.88, 0.84, 0.77]) + np.array(TK['paper'])) / 2)), (N - 1, TK['paper'])], N)
    # (d) near pines crossing the lens in the retreat: boughs growing out of the palm pillars' faces near the camera
    # path; the camera pulls back past them (they come in at the frame edge and stay rooted in the cliff)
    from tools.world.scene import card_meta
    for j, (pi, u, v, side, nm, ww) in enumerate([(0, 0.22, 0.47, -1, 'pine_bough_1', 26), (0, 0.78, 0.30, 1, 'pine_bough_2', 30),
                                                 (1, 0.72, 0.40, 1, 'pine_bough_1', 34), (2, 0.28, 0.36, -1, 'pine_bough_2', 32),
                                                 (0, 0.72, 0.64, 1, 'pine_bough_1', 22)]):
        o = pillars[pi]['card']
        root = np.array(Wd.card_point(o, u, v))
        hh = ww / card_meta(nm)['aspect']
        yw = -50.0 if side > 0 else -130.0             # the card's +x (trunk -> needles) points out of the face and toward us
        xa = np.array([math.cos(math.radians(yw)), 0, -math.sin(math.radians(yw))])
        ctr = root + xa * ww * 0.5 + np.array([0, hh * 0.1, 0])
        Wd.card(nm, list(ctr), height=hh, relief=hh * 0.12, yaw=yw, anchor='center', seak=1.0, fogk=1.0, id=f'bough{j}', keys=kk)
    # ---------------- (e) D6 rays: thin ink-gold ruled strokes radiating from behind the palm (as the 1806 print)
    ctr = np.array([0.0, 172.0, -70.0])
    cend, tend = np.array(P[N - 1]), np.array(T[N - 1])
    dv = (tend - cend) / np.linalg.norm(tend - cend)
    ex = np.cross(dv, [0, 1, 0]); ex /= np.linalg.norm(ex)
    ey = np.cross(ex, dv)
    f_l = fr(T_LIAN)
    rr3 = np.random.default_rng(44)
    angs = np.sort(rr3.uniform(math.radians(22), math.radians(158), 58))
    for i, a in enumerate(angs):
        r0 = rr3.uniform(70, 125); r1 = r0 + rr3.uniform(200, 620)
        u = ex * math.cos(a) + ey * math.sin(a)
        segs = [(r0, r1)] if rr3.random() < 0.7 else [(r0, r0 + (r1 - r0) * 0.45), (r0 + (r1 - r0) * 0.55, r1)]
        for s0, s1 in segs:
            pts = [list(ctr + u * r) for r in np.linspace(s0, s1, 10)]
            Wd.thread(pts, f0=f_l - 1 + int(rr3.integers(0, 4)), fdraw=int(rr3.integers(4, 8)), fhold=int(rr3.integers(16, 22)), ffade=12,
                      rest=0.0, width=float(rr3.uniform(1.0, 2.4)), col=[0.86, 0.60, 0.22], glow=0.3, fogk=0.0, seak=0.0, opacity=0.95, order=8)
    Wd.camera = []
    for f in range(N):
        d = float(np.linalg.norm(np.array(P[f]) - np.array(T[f])))
        Wd.camera.append(dict(p=list(P[f]), t=list(T[f]), fov=float(FOV[f]), near=max(0.05, min(d * 0.05, 1.5)), far=6000,
                              seaY=float(SEA[f]), paper=list(PAPER[f])))
    meta = dict(take=take, n_inst=len(inst), gens=[len(g) for g in gens], n_lit=len(lit), runs=len(runs), vein_threads=nv,
                threads=len(Wd.S['threads']), sparks=len(parts), P_tong=P_t.tolist())
    json.dump(meta, open(os.path.join(Wd.dir, 'meta.json'), 'w'), indent=1)
    return Wd, meta


def render(take='r2a', frames=None, ss=2, passes=None):
    Wd, meta = build(take)
    print(json.dumps(meta))
    Wd.render(ss=ss, frames=frames, passes=passes or ['beauty', 'glow'])
    return Wd


if __name__ == '__main__':
    ps = os.environ.get('DF_PASSES')
    render(os.environ.get('DF2_TAKE', 'r2a'), os.environ.get('DF_FRAMES'), int(os.environ.get('DF_SS', '2')), ps.split(',') if ps else None)

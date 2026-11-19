"""shots/_dflight.py: D4 -> D5 -> D6 as ONE unbroken flight in the 3D Huangshan range (REVISION_V4 §3.1). WORLD v4.

204 frames, song 67.917 -> 76.417 (D4 33 f, D5 101 f, D6 70 f), rendered once; D4.py / D5.py / D6.py cut their frames.
1. D4: macro on the stone of the middle pillar, grain visible; a sleeve of mist crosses 通; it lights like an ember.
2. D5: the camera pulls back and rises; generation 1 jumps along the 辶 family on this cliff; then threads leave the cliff,
   arc across the gorges to other pillars, and each generation the frontier is a ridge further (rings by distance),
   through true shared components (IDS, shots/_tong.components). Behind the frontier the threads fade, the carving glows.
   On the gong (72.805) everything no jump reached lights too.
3. D6: the camera climbs through a bank of cloud; the cloud sea wells up and drowns the low peaks; the five lit pillars
   stand out of it: four tall, one short and apart: the Buddha's palm (佛掌峰), granite, pines on their shoulders.
   The monkey somersaults in from the right on his cloud and lands on the middle peak in 亮相 (STAGE element).
Env: DF_FRAMES=0,40,80 (subset), DF_SS=2, DF_TAKE=<name> (output scratch suffix), DF_MONKEY=<dir of RGBA frames>.
"""
import collections
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import World, smooth_path, paper_grain, encode, sheet, ROOT  # noqa: E402
from tools.world.carve import Carving, qianziwen  # noqa: E402

FPS = 24
F0_SONG = 1630                       # D4 in_frame
N = 204                              # 33 + 101 + 70
D4N, D5N, D6N = 33, 101, 70
def fr(t): return int(round(t * FPS)) - F0_SONG


T_TONG = 67.99
GEN_T = [68.53, 69.50, 70.146, 70.594, 71.029, 71.471, 71.925, 72.356]
GEN_STAGGER = [0.68, 0.50, 0.36, 0.30, 0.30, 0.30, 0.30, 0.30]
T_GONG = 72.805
GLOW = (1.0, 0.70, 0.26)

# ------------------------------------------------------------------------------------------- the range (world units)
# (card, x, z, height, roll, ring-hint)   bottom of every card at y = -40 (the foot is in the cloud sea)
PALM = [  # four fingers + thumb, facing +z; the middle one carries 通
    ('pillar_scripture_1', 0.0, 0.0, 232, 0.0, 'middle'),
    ('pillar_scripture_2', -54.0, -6.0, 214, 5.0, 'index'),
    ('pillar_slender_2', 50.0, -8.0, 222, -4.5, 'ring'),
    ('pillar_slender_1', 92.0, -20.0, 186, -10.0, 'little'),
    ('pillar_slender_2', -112.0, 34.0, 212, 27.0, 'thumb'),
]
def _low():
    """The country the whisper never touched: peaks around and behind the palm (lit ring by ring, farther each beat,
    visible over the fingers as the camera climbs) and a few in the corridor the camera retreats through (they pass
    the lens). Every top stays well below the fingers, so the rising cloud sea leaves only the palm."""
    names = ['pillar_needle_1', 'pillar_stacked_1', 'pillar_broad_1', 'pillar_twin_1', 'pillar_needle_2', 'pillar_broad_2',
             'pillar_stacked_2', 'pillar_twin_2', 'pillar_thumb_2', 'hgs_shoulder_l_1', 'hgs_shoulder_l_2', 'hgs_shoulder_r_1',
             'hgs_shoulder_r_2', 'pillar_slender_1', 'pillar_slender_2', 'pillar_scripture_2', 'pillar_thumb_1']
    r = np.random.default_rng(5)
    out = []
    pts = []
    while len(out) < 34:
        ang = r.uniform(-0.95, 0.95) * math.pi * 0.62 + math.pi      # mostly behind (-z) and to the sides
        rad = r.uniform(150, 760)
        x, z = rad * math.sin(ang) * 1.15, rad * math.cos(ang)
        if any(math.hypot(x - a, z - b) < 70 for a, b in pts) or abs(x) < 170 and z > -150:
            continue
        pts.append((x, z))
        out.append((names[len(out) % len(names)], round(x), round(z), round(r.uniform(95, 150)), round(r.uniform(-3, 3))))
    for x, z in [(-120, 160), (95, 210), (-60, 300), (150, 330), (-170, 260), (40, 420)]:   # the corridor
        out.append((names[len(out) % len(names)], x, z, 96, 0))
    return out


LOW = _low()


def fields(rng, main_only=False):
    """Inscription fields on a pillar face (uv rects + glyph size in world units): cliff inscriptions are rectangular
    fields of different densities separated by bare rock, not wallpaper."""
    F = []
    u0 = rng.uniform(0.18, 0.28); u1 = rng.uniform(0.72, 0.82)
    v0 = rng.uniform(0.22, 0.30); v1 = v0 + rng.uniform(0.26, 0.36)
    F.append(((u0, v0, u1, v1), rng.uniform(2.6, 3.2)))
    if rng.random() < 0.85:
        a = rng.uniform(0.25, 0.4); b = a + rng.uniform(0.25, 0.4)
        F.append(((a, v1 + 0.04, min(b, 0.82), v1 + 0.04 + rng.uniform(0.10, 0.18)), rng.uniform(1.8, 2.3)))
    if rng.random() < 0.7:
        a = rng.uniform(0.3, 0.42)
        F.append(((a, max(0.08, v0 - 0.15), 1 - a + 0.05, v0 - 0.03), rng.uniform(4.2, 5.2)))
    return F


def build(take='a', with_monkey=None):
    Wd = World('Dflight' + ('' if take == 'a' else '_' + take), N)
    Wd.fog(density=0.0009, start=100)
    Wd.sea(y=0.0, soft=16.0, amp=34.0, scale=0.010, drift=(0.6, 0.25))
    chars = qianziwen()
    chars_all = chars * 6
    cursor = [0]

    def take_chars(k):
        out = [chars_all[(cursor[0] + i) % len(chars_all)] for i in range(k)]
        cursor[0] += k
        return out

    pillars = []          # dict(card=o, glyphs=[...], ring)
    idx_mid = None
    # ---------------- the palm
    for name, x, z, h, roll, role in PALM:
        CV = Carving(f'design/world/cards/{name}_rgba.png', size=4096, seed=len(pillars))
        px = 3.0 / h * 4096                                         # glyph = 3 world units
        if role == 'middle':
            # dry layout to know the cells, then put 通 at the cell nearest (0.5, 0.42) and its 辶 family around it
            dry = Carving(f'design/world/cards/{name}_rgba.png', size=4096)
            MAIN = (0.18, 0.26, 0.82, 0.60)
            cells = dry.field(MAIN, ['口'] * 4000, px=px)
            Carving._next[0] -= len(cells)
            tgt = min(range(len(cells)), key=lambda i: (cells[i]['u'] - 0.5) ** 2 + ((cells[i]['v'] - 0.40) * 2.4) ** 2)
            seq = take_chars(len(cells))
            seq = [c for c in seq if c != '通']
            fam = [c for c in dict.fromkeys(chars) if '辶' in comps(c) and c != '通']
            seq = [c for c in seq if c not in fam]
            # family members at cells within ~6..16 units of 通
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
        CV.save(f'work/world/Dflight/carve_{len(pillars)}_{name}')
        pillars.append(dict(name=name, CV=CV, glyphs=gl, x=x, z=z, h=h, roll=roll, role=role, ring=0 if role == 'middle' else 1))
        if role == 'middle':
            idx_mid = len(pillars) - 1
    # ---------------- the low country
    for name, x, z, h, roll in LOW:
        CV = Carving(f'design/world/cards/{name}_rgba.png', size=2048, seed=len(pillars))
        px = 3.2 / h * 2048
        gl = []
        for rect, gw in fields(np.random.default_rng(200 + len(pillars))):
            gl += CV.field(rect, take_chars(3000), px=(gw * 1.1) / h * 2048, need=0.7)
        CV.save(f'work/world/Dflight/carve_{len(pillars)}_{name}')
        pillars.append(dict(name=name, CV=CV, glyphs=gl, x=x, z=z, h=h, roll=roll, role='low', ring=None))
    # rings by distance from the middle pillar (the frontier moves a ridge further every beat)
    dist = [math.hypot(p['x'], p['z']) for p in pillars]
    lows = sorted([i for i, p in enumerate(pillars) if p['role'] == 'low'], key=lambda i: dist[i])
    lows = [i for i in lows if pillars[i]['z'] <= 100]
    for k, i in enumerate(lows):
        pillars[i]['ring'] = 2 + int(k * 5 / len(lows))          # rings 2..6, outward from the palm
    for p in pillars:
        if p['ring'] is None:
            p['ring'] = 6                                         # the corridor behind the camera: lit last

    # ---------------- schedule: true jumps by shared component
    inst = []                                                     # (pillar index, glyph)
    for pi, p in enumerate(pillars):
        for g in p['glyphs']:
            inst.append((pi, g))
    C = comps_table(set(g['ch'] for _, g in inst))
    by_comp = collections.defaultdict(list)
    for k, (pi, g) in enumerate(inst):
        for c in C[g['ch']]:
            by_comp[c].append(k)
    lit = {}                                                      # inst index -> (frame, gen)
    edges = []                                                    # (src k, dst k, frame, gen)
    k_tong = next(k for k, (pi, g) in enumerate(inst) if pi == idx_mid and g['ch'] == '通')
    lit[k_tong] = (fr(T_TONG), 0)
    via = {k_tong: '辶'}
    rng = np.random.default_rng(7)
    # generation 1: the 辶 family on this cliff
    g1 = [k for k in by_comp['辶'] if inst[k][0] == idx_mid and k != k_tong]
    g1.sort(key=lambda k: math.hypot(inst[k][1]['u'] - inst[k_tong][1]['u'], inst[k][1]['v'] - inst[k_tong][1]['v']))
    gens = [[(k_tong, k, '辶') for k in g1]]
    for _, k, c in gens[0]:
        via[k] = c
    caps = [None, 30, 60, 110, 190, 300, 380, 460]
    frontier = [k for _, k, _ in gens[0]]
    for g in range(1, len(GEN_T)):
        max_ring = g                                              # gen 2 -> rings <= 1 (the other fingers), ...
        new = []
        used = set(lit) | set(k for gg in gens for _, k, _ in gg)
        for s in frontier:
            for c in sorted(C[inst[s][1]['ch']]):
                if c == via.get(s):
                    continue
                cand = [d for d in by_comp[c] if d not in used and pillars[inst[d][0]]['ring'] <= max_ring]
                if not cand:
                    continue
                # prefer the frontier ring (far), then random
                cand.sort(key=lambda d: (-pillars[inst[d][0]]['ring'], rng.random()))
                for d in cand[:2 if g < 3 else 3]:
                    new.append((s, d, c)); used.add(d); via[d] = c
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
            tt = t0 + sp * j / max(1, len(lst) - 1)
            f = fr(tt)
            edges.append((s, d, f, g))
            lit[d] = (f + 3, g + 1)
    n_rest = 0
    # (v4.1) the characters no jump reached stay dark: lit country is sparse chains of single characters, not a
    # wall of lit windows; only a few more wake on the gong
    for k in range(len(inst)):
        if k not in lit and rng.random() < 0.12:
            lit[k] = (fr(T_GONG) + int(rng.integers(0, 4)), 99); n_rest += 1

    # ---------------- cards
    cards = []
    for pi, p in enumerate(pillars):
        litl = [(g['id'], lit[k][0], float(0.6 + 0.65 * ((g['id'] * 2654435761) % 1000) / 1000)) for k, (qi, g) in enumerate(inst) if qi == pi and k in lit]
        relief = p['h'] * 0.16
        o = Wd.card(p['name'], [p['x'], -40, p['z']], height=p['h'], relief=relief, roll=p['roll'], bend=0.10,
                    carve=p['CV'].spec(lit=litl, glow=GLOW, dark=0.5, base=1.1, glow_fog=0.45), seg=[160, 384] if p['role'] != 'low' else [96, 192],
                    id=f'p{pi}', lum=1.0,
                    keys=[[0, {'lum': 1.0}], [fr(T_GONG), {'lum': 0.74}], [N - 1, {'lum': 0.70}]])
        p['card'] = o
        cards.append(o)
    # far country
    for k, (nm, pos, wid, rel) in enumerate([('range_mid_1', [0, -235, -900], 1500, 30), ('range_far_1', [-300, -380, -1500], 2400, 40),
                                              ('range_far_2', [600, -470, -1900], 2800, 40)]):
        CVr = Carving(f'design/world/cards/{nm}_rgba.png', size=1706, pale=0.35, seed=90 + k)
        glr = []
        rr2 = np.random.default_rng(300 + k)
        for j in range(14):
            u0 = rr2.uniform(0.05, 0.9); v0 = rr2.uniform(0.3, 0.75)
            glr += CVr.field((u0, v0, u0 + rr2.uniform(0.02, 0.06), v0 + rr2.uniform(0.04, 0.12)), take_chars(400), px=10, need=0.6)
        CVr.save(f'work/world/Dflight/carve_range{k}')
        t_lit = fr(GEN_T[6 + min(k, 1)]) if k < 2 else fr(T_GONG)
        Wd.card(nm, pos, width=wid, relief=rel, lum=0.95, fogk=1.7,
                carve=CVr.spec(lit=[(g['id'], t_lit + int(rng.integers(0, 10)), 0.8) for g in glr], glow=GLOW, dark=0.3, base=1.2, glow_fog=0.3),
                keys=[[0, {'lum': 0.95}], [fr(T_GONG), {'lum': 0.8}]])

    # world positions of every instance (for threads)
    W_ = {}
    def wpos(k):
        if k not in W_:
            pi, g = inst[k]
            W_[k] = np.array(Wd.card_point(pillars[pi]['card'], g['u'], g['v']))
        return W_[k]
    # threads: all of gen 1; later generations the longest jumps first (the ones that leave a cliff), capped
    TCAP = [99, 40, 50, 50, 40, 30, 15, 0]
    TW = [3.4, 2.8, 2.2, 1.9, 1.6, 1.4, 1.3, 1.2]
    for g in range(len(gens)):
        eg = [e for e in edges if e[3] == g]
        eg.sort(key=lambda e: -np.linalg.norm(wpos(e[0]) - wpos(e[1])))
        eg = [e for e in eg if (wpos(e[1])[2] < 60 and wpos(e[1])[2] > -700 and np.linalg.norm(wpos(e[1]) - wpos(e[0])) < 520) or g < 2]
        for s, d, f, _ in eg[:TCAP[g]]:
            a, b = wpos(s), wpos(d)
            L = np.linalg.norm(b - a)
            mid = (a + b) / 2 + np.array([0, 1, 0]) * min(0.40 * L, 130.0) + np.array([0, 0, 1]) * (0.05 * L)
            pts = [list(a * (1 - t) ** 2 + mid * 2 * t * (1 - t) + b * t * t) for t in np.linspace(0, 1, 28)]
            hold = 16 if g < 2 else 10
            Wd.thread(pts, f0=f, fdraw=3 if L < 30 else 5, fhold=hold, ffade=10, rest=0.0, width=TW[g], col=list(GLOW), glow=1.0)

    P_t = wpos(k_tong)
    nrm = np.array([0.0, 0.0, 1.0])
    # ---------------- D4 macro detail on 通 (overlay decal of the same stone, its own big 通 carved at the same place)
    gtong = inst[k_tong][1]
    hm = pillars[idx_mid]['h']
    glyph_w = gtong['px'] / 4096 * hm                    # world size of the pillar's 通
    macro = Carving('design/world/cards/granite_macro_1_rgba.png', size=2160, pale=0.0)
    Carving._next[0] -= 0
    gpx = int(2160 * glyph_w / 9.0); hw = gpx * 0.62 / 3840; hv = gpx * 0.62 / 2160
    mg = macro.field((0.5 - hw, 0.5 - hv, 0.5 + hw, 0.5 + hv), ['通'], px=gpx, need=0.0)
    macro.save('work/world/Dflight/carve_macro')
    Wd.overlay('design/world/cards/granite_macro_1_rgba.png', list(P_t + nrm * 0.6), [16.0, 9.0], id='macro',
               carve=macro.spec(lit=[(mg[0]['id'], fr(T_TONG), 1.0)], glow=GLOW, dark=0.55, base=0.8), round=0.55,
               keys=[[0, {'opacity': 1.0}], [13, {'opacity': 1.0}], [24, {'opacity': 0.0}]], edge=0.0)

    # ---------------- mist
    # the sleeve of mist that touches 通 (the whisper)
    Wd.mist(list(P_t + nrm * 2.0 + np.array([-9, -0.5, 0])), [9, 2.6], opacity=0.95, thresh=0.36, scale=0.6, band=True, edge=0.6,
            soft=0.4, nearFade=0.5, wash=0.15, speed=[0.4, 0.0],
            keys=[[0, {'pos': list(P_t + nrm * 2.0 + np.array([-8, -0.6, 0])), 'opacity': 0.0}],
                  [3, {'opacity': 0.9}], [16, {'pos': list(P_t + nrm * 2.0 + np.array([6, 0.8, 0])), 'opacity': 0.8}],
                  [28, {'pos': list(P_t + nrm * 2.0 + np.array([14, 1.5, 0])), 'opacity': 0.0}]])
    # bands of mist between the ridges (vertical sheets across the corridor) and flat sheets over the sea
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
    # the cloud bank D6 climbs through (slices around the camera path; fade in as crossed, then thin away)
    for i in range(7):
        z = 382 + i * 7
        f_in = fr(73.5) + 2 + i * 2
        Wd.mist([0, 236 + i * 2.5, z], [900, 420], opacity=0.0, thresh=0.22, scale=0.010, edge=0.4, soft=20, nearFade=3, wash=0.18,
                speed=[1.5, 0.2], seed=80.0 + i, billboard=True,
                keys=[[0, {'opacity': 0.0}], [f_in, {'opacity': 0.0}], [f_in + 3, {'opacity': 0.7}], [fr(73.85) + i // 2, {'opacity': 0.7}],
                      [fr(74.15) + i // 2, {'opacity': 0.0}]])

    # ---------------- camera: macro -> pull back + rise -> through the cloud -> the palm
    KEYS = [
        (0, P_t + nrm * 6.5, P_t),
        (14, P_t + nrm * 9.5 + np.array([0.3, 0.3, 0]), P_t + np.array([0, 0.2, 0])),
        (32, P_t + nrm * 34 + np.array([2, 3, 0]), P_t + np.array([0, 1, 0])),
        (55, np.array([12, P_t[1] + 14, 100]), np.array([2, P_t[1] - 4, 0])),
        (85, np.array([-15, 172, 230]), np.array([0, 100, -40])),
        (fr(T_GONG), np.array([5, 222, 335]), np.array([0, 78, -130])),
        (D4N + D5N, np.array([0, 236, 380]), np.array([-4, 86, -100])),
        (D4N + D5N + 20, np.array([-8, 245, 405]), np.array([-12, 104, -40])),
        (N - 1, np.array([-16, 215, 420]), np.array([-16, 118, 0])),
    ]
    if take == 'b':      # take b: the retreat swings in an arc round the palm (more parallax between the pillars)
        sw = {55: [60, 6, -20], 85: [95, 10, -40], fr(T_GONG): [70, 0, -30], D4N + D5N: [40, 0, -10]}
        KEYS = [(f, p + np.array(sw.get(f, [0, 0, 0]), float), t) for f, p, t in KEYS]
    if take == 'c':      # take c: a higher, steeper climb: we look down on the lit country sooner
        sw = {85: [0, 40, -20], fr(T_GONG): [0, 60, -10], D4N + D5N: [0, 50, 0], D4N + D5N + 20: [0, 30, 0]}
        KEYS = [(f, p + np.array(sw.get(f, [0, 0, 0]), float), t) for f, p, t in KEYS]
    P = smooth_path([(f, list(p)) for f, p, _ in KEYS], N)
    T = smooth_path([(f, list(t)) for f, _, t in KEYS], N)
    FOV = smooth_path([(0, 34), (32, 36), (D4N + D5N, 36), (N - 1, 31)], N)
    SEA = smooth_path([(0, 0.0), (D4N + D5N, 6.0), (D4N + D5N + 18, 45), (N - 1, 80)], N)
    PAPER = smooth_path([(0, [0.925, 0.886, 0.800]), (fr(71.0), [0.905, 0.862, 0.775]), (fr(T_GONG), [0.865, 0.815, 0.725]), (N - 1, [0.855, 0.80, 0.71])], N)
    Wd.camera = []
    for f in range(N):
        d = float(np.linalg.norm(np.array(P[f]) - np.array(T[f])))
        Wd.camera.append(dict(p=list(P[f]), t=list(T[f]), fov=float(FOV[f]), near=max(0.05, min(d * 0.05, 1.5)), far=6000,
                              seaY=float(SEA[f]), paper=list(PAPER[f])))
    meta = dict(n_inst=len(inst), gens=[len(g) for g in gens], n_rest=n_rest, threads=len(Wd.S['threads']),
                P_tong=P_t.tolist(), pillars=[(p['name'], p['role'], p['ring'], len(p['glyphs'])) for p in pillars])
    json.dump(meta, open(os.path.join(Wd.dir, 'meta.json'), 'w'), indent=1)
    return Wd, meta


_C = {}
def comps_table(chars):
    sys.path.insert(0, os.path.join(ROOT, 'shots'))
    import _tong
    return _tong.components(sorted(chars))


def comps(ch):
    if ch not in _C:
        _C.update(comps_table([ch]))
    return _C[ch]


def render(take='a', frames=None, ss=2):
    Wd, meta = build(take)
    print(json.dumps({k: v for k, v in meta.items() if k != 'pillars'}))
    Wd.render(ss=ss, frames=frames)
    return Wd


if __name__ == '__main__':
    fs = os.environ.get('DF_FRAMES')
    render(os.environ.get('DF_TAKE', 'a'), fs, int(os.environ.get('DF_SS', '2')))

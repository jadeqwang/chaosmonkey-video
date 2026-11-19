"""shots/_jworld.py: the blue-green heaven as a real 3D range, shared by J2 (the flat page becomes deep in place) and
J5 (the lit range collapses back into a few strokes on a flat page). WORLD v4, REVISION_V4 §2.

J2 (190.875-192.833, 47 f). Frame 0 is J1's page, square on, under the torch: the painted range (this world seen
through a 1.4 degree lens from far away, every card squashed onto the page plane), the carved character the
daughter pressed, lit; the Chinese columns 五官俱备 / 四肢皆全 and the English "Born fully formed" set statically on
the page beside them. On the hit (190.885) the painting acquires depth IN PLACE: the cards spread out of the page
plane to their true depths and their relief rises, while the camera dolly-zooms from 1.4 to 46 degrees in 9 frames
(the page plane keeps its size, so nothing jumps): near peaks swell toward us, far peaks fall back, mist pours forward
over the gutter, and then we fly forward and up through the range. The page text stays where it was written: a tablet
left behind in space as we pass it. The pressed character's light jumps to the other peaks by shared component.
J5 (200.667-203.708, 73 f): the same system backwards, ending on a bare aged page with the range a few strokes in the
lower-left corner and 一通百通 upper right.
    $PY shots/_jworld.py J2|J5 [--frames 0,10] [--take a]
"""
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import World, smooth_path, fov_for, paper_grain, encode, sheet, ease, ROOT  # noqa: E402
from tools.world.carve import Carving, qianziwen  # noqa: E402

FPS = 24
GLOW = (1.0, 0.80, 0.42)
PAGE_H = 100.0                    # world units of page height in frame at f0
ASP = 16 / 9
D0 = 4000.0                       # camera distance at f0 (1.43 degree lens: flat)
LATIN = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'

# (card, x, z, height, roll): z = 0 is the page plane; + toward the camera (stands out of the page), - behind
RANGE = [
    ('ql_peak_a_1', -30, -10, 100, 0, 'hero'),
    ('ql_peak_b_1', 8, 24, 70, -2, ''), ('ql_peak_d_1', -82, -60, 104, 2, ''), ('ql_peak_c_1', 40, -90, 52, 0, ''),
    ('ql_peak_b_2', -62, 46, 60, 3, ''), ('ql_peak_a_2', 72, -40, 58, -3, ''), ('ql_peak_d_2', -8, -170, 112, 0, ''),
    ('ql_peak_c_2', -118, 10, 50, 0, ''), ('ql_peak_c_1', 4, 70, 36, 0, ''), ('ql_peak_b_2', 60, 58, 40, -4, ''),
    ('ql_peak_c_2', 104, 30, 34, 0, ''),
]


def _deep():
    r = np.random.default_rng(9)
    names = ['ql_peak_a_1', 'ql_peak_a_2', 'ql_peak_b_1', 'ql_peak_b_2', 'ql_peak_c_1', 'ql_peak_c_2', 'ql_peak_d_1', 'ql_peak_d_2']
    out, pts = [], []
    while len(out) < 26:
        x, z = r.uniform(-420, 420), r.uniform(-760, -200)
        if any(math.hypot(x - a, z - b) < 70 for a, b in pts):
            continue
        pts.append((x, z))
        out.append((names[len(out) % 8], round(x), round(z), round(r.uniform(70, 125)), 0, ''))
    return out


RANGE += _deep()
SEA_Y = -38.0
J5_FA, J5_FB = 16, 36           # J5 take b: deep until FA, dolly-zoom out to flat until FB, then the painting draws in


def page_texture(shot, w=3556, h=2000):
    """The page plane: transparent paper carrying the static text, the gutter shadow, the torch-warm tone (RGBA)."""
    sys.path.insert(0, ROOT)
    from tools.ink.inscription import inscription
    from tools.ink.paper import Paper
    P = Paper(w, h, 'aged', seed=2026)
    img = np.zeros((h, w, 4), np.float32)
    s = w / 1920 / (PAGE_H * ASP / 177.78)          # page px per 1080p frame px at f0 (=1.85)
    ink = np.ones((h, w, 3), np.float32)
    if shot == 'J2':
        ins = inscription((w, h), 'D1', box=(int(w * 0.83), int(h * 0.09), int(w * 0.12), int(h * 0.62)), paper=P, px=60 * s)
        ins.draw(ink)
        # the English, set statically on the page beside the columns (small caps of a book's printed line)
        pil = Image.fromarray((ink * 255).astype(np.uint8))
        d = ImageDraw.Draw(pil)
        f = ImageFont.truetype(os.path.join(ROOT, LATIN), int(66 * s))
        try:
            f.set_variation_by_axes([430])
        except Exception:  # noqa: BLE001
            pass
        for k, line in enumerate(['Born', 'fully formed']):
            d.text((int(w * 0.64), int(h * 0.11) + k * int(84 * s)), line, font=f, fill=(44, 36, 30))
        ink = np.array(pil).astype(np.float32) / 255
    else:
        ins = inscription((w, h), None, box=(int(w * 0.80), int(h * 0.08), int(w * 0.12), int(h * 0.62)), paper=P, px=60 * s,
                          text='一通百通')
        ins.draw(ink)
    a = 1 - ink.min(2)
    img[..., :3] = ink
    img[..., 3] = np.clip(a * 1.15, 0, 1)
    # gutter: a soft fold shadow at x = 18 % of the page plane
    xx = np.arange(w, dtype=np.float32)[None, :] / w
    g = np.exp(-((xx - 0.18) / 0.012) ** 2) * 0.32 + np.exp(-((xx - 0.18) / 0.05) ** 2) * 0.10
    ga = np.broadcast_to(g, (h, w))
    gc = np.array([0.42, 0.34, 0.26], np.float32)
    out = img.copy()
    A = out[..., 3]
    out[..., :3] = (out[..., :3] * A[..., None] + gc * ga[..., None] * (1 - A[..., None])) / np.maximum(A + ga * (1 - A), 1e-4)[..., None]
    out[..., 3] = A + ga * (1 - A)
    p = f'work/world/{shot}/page_plane.png'
    os.makedirs(os.path.join(ROOT, os.path.dirname(p)), exist_ok=True)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, p))
    return p


def flat_keys(o, C0, u_frames, relief):
    """Keys that squash card o onto the page plane z=0 as seen from C0 at u=0 and release it to its true place at u=1.
    u_frames: [(frame, u), ...]."""
    P = np.array(o['pos'], float)
    zp = 0.03 * P[2]                                  # keep the depth ORDER on the page (no z-fighting), not the depth
    k = (C0[2] - zp) / max(C0[2] - P[2], 1e-3)
    Pf = C0 + (P - C0) * k
    keys = []
    for f, u in u_frames:
        keys.append([f, {'pos': list(Pf + (P - Pf) * u), 'scale': float(k + (1 - k) * u), 'relief': relief * u}])
    return keys


D1 = PAGE_H / 2 / math.tan(math.radians(46 / 2))


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def cam_path(take, f, n=47):
    """Round-2 J2 camera after the pop (f >= 9): returns (p, t, fov, roll). f9 = p [0,0,D1] looking at the page, fov 46."""
    v = (f - 9) / (n - 10)
    b = _sm(v / 0.16)
    if take == 'e':      # straight push, a slight rise, low in the corridor
        z = D1 - 345 * v
        p = [9 * math.sin(v * 2.2) * min(1, v * 5), 3 + 16 * v, z]
        fwd = [p[0] + 6, p[1] - 5, p[2] - 160]
        fov = 46 + 7 * v
        roll = 0.0
    elif take == 'f':    # banking slalom between gates
        z = D1 - 330 * v
        p = [26 * math.sin(v * 2 * math.pi * 1.25) * _sm(v * 4) + 8 * _sm(v * 3), 2 + 12 * v - 6 * math.sin(v * math.pi), z]
        ahead = D1 - 330 * min(1.0, v + 0.07)
        xa = 26 * math.sin(min(1.0, v + 0.07) * 2 * math.pi * 1.25) * _sm(min(1.0, v + 0.07) * 4) + 8 * _sm(min(1.0, v + 0.07) * 3)
        fwd = [xa, p[1] - 2, ahead - 90]
        fov = 48 + 5 * v
        roll = -9.0 * math.sin(v * 2 * math.pi * 1.25 + 0.5) * _sm(v * 5)
    elif take == 'h':    # under the tablet, then out of the corridor and up onto a vista
        z = D1 - 330 * v
        y = 2 - 9 * _sm(v / 0.35) + 56 * _sm((v - 0.4) / 0.6)
        p = [24 * _sm(v * 3) - 10 * _sm((v - 0.4) / 0.6), y, z]
        fwd = [8, y + 14 - 40 * _sm((v - 0.5) / 0.5), z - 150]
        fov = 46 + 6 * v
        roll = -4.0 * math.sin(v * math.pi) if v > 0.3 else 0.0
    else:                # g: rise over the range
        z = D1 - 280 * v
        y = 2 + 150 * (v ** 1.5)
        p = [14 * _sm(v * 2) - 6 * v, y, z]
        fwd = [4, -22 - 40 * v + 20 * (1 - v), p[2] - 140]
        fov = 46 + 9 * v
        roll = 0.0
    t = [b * fwd[0], b * fwd[1], b * fwd[2]]
    return (p, t, fov, roll)


def _columns(gl):
    """Split a carved field's glyph list (columns right->left, top->bottom) into columns."""
    cols, cur = [], []
    for g in gl:
        if cur and (g['v'] <= cur[-1]['v'] or abs(g['u'] - cur[-1]['u']) > 1e-3):
            cols.append(cur); cur = []
        cur.append(g)
    if cur:
        cols.append(cur)
    return cols


def _fields(rng, scale=1.0):
    F = []
    u0 = rng.uniform(0.18, 0.28); u1 = rng.uniform(0.72, 0.82)
    v0 = rng.uniform(0.22, 0.30); v1 = v0 + rng.uniform(0.26, 0.36)
    F.append(((u0, v0, u1, v1), rng.uniform(2.6, 3.2) * scale))
    if rng.random() < 0.85:
        a = rng.uniform(0.25, 0.4); b = a + rng.uniform(0.25, 0.4)
        F.append(((a, v1 + 0.04, min(b, 0.82), v1 + 0.04 + rng.uniform(0.10, 0.18)), rng.uniform(1.8, 2.3) * scale))
    if rng.random() < 0.7:
        a = rng.uniform(0.3, 0.42)
        F.append(((a, max(0.08, v0 - 0.15), 1 - a + 0.05, v0 - 0.03), rng.uniform(4.2, 5.2) * scale))
    return F


def vein_lit(gl, rng, f_start, p_col=0.45, span=10, gk=1.15):
    """Veins: per column, one or two runs of 2-10 glyphs lit in sequence with tapering gain; the rest stays dark."""
    lit = []
    for col in _columns(gl):
        if len(col) < 3 or rng.random() > p_col:
            continue
        for _ in range(1 + int(rng.random() < 0.3)):
            L = int(rng.integers(2, min(10, len(col)) + 1))
            a = int(rng.integers(0, len(col) - L + 1))
            run = col[a:a + L]
            if rng.random() < 0.5:
                run = run[::-1]
            f0 = f_start + int(rng.integers(0, span))
            fa = 0.0
            for i, g in enumerate(run):
                fa += rng.uniform(0.7, 1.5)
                gain = gk * (1 - 0.6 * i / max(L - 1, 1)) * rng.uniform(0.85, 1.1)
                lit.append([g['id'], max(10, int(f0 + fa)), round(gain, 3)])
    return lit


def granite_range(Wd, take, pillars, press_w, fr):
    """Round-2 J2: the great carved range. Adds granite pillar cards along the camera path in several depth bands, far
    ranges, mist bands, veins on every pillar and gold threads arcing between pillars from the pressed character."""
    rng = np.random.default_rng({'e': 21, 'f': 22, 'g': 23, 'h': 24}[take])
    SEA = SEA_Y
    G = ['pillar_scripture_1', 'pillar_scripture_2', 'pillar_slender_1', 'pillar_slender_2', 'pillar_broad_1', 'pillar_broad_2',
         'pillar_twin_1', 'pillar_twin_2', 'pillar_stacked_1', 'pillar_stacked_2', 'pillar_needle_1', 'pillar_needle_2',
         'pillar_thumb_1', 'pillar_thumb_2']
    Q = ['ql_peak_a_1', 'ql_peak_a_2', 'ql_peak_b_1', 'ql_peak_b_2', 'ql_peak_c_1', 'ql_peak_c_2', 'ql_peak_d_1', 'ql_peak_d_2']
    chars = qianziwen() * 40
    ci = [int(rng.integers(0, 300))]
    spec = []     # (name, x, z, h, roll, yaw, band)
    cfg = {'e': dict(step=26, off=(50, 84), hh=(105, 170), K=345), 'f': dict(step=36, off=(52, 80), hh=(115, 185), K=330),
           'g': dict(step=42, off=(50, 82), hh=(150, 230), K=280),
           'h': dict(step=28, off=(50, 84), hh=(105, 175), K=330)}[take]
    k = 0
    zc = -12.0
    while zc > -300:
        vv = (D1 - zc) / cfg['K']
        fk = 9 + 37 * vv
        p, _, _, _ = cam_path(take, int(min(fk, 46)))
        px = p[0] if fk <= 46 else p[0]
        if take == 'f':      # gates: a pillar on the outside of each turn, offset against the swing
            sgn = -1 if math.sin(vv * 2 * math.pi * 1.25) > 0 else 1
        else:
            sgn = 1 if k % 2 == 0 else -1
        off = rng.uniform(*cfg['off']) * (1.8 if take == 'h' and zc < -140 else 1.0)
        h = rng.uniform(*cfg['hh'])
        nm = G[(k * 5 + int(rng.integers(0, 3))) % len(G)] if (rng.random() < 0.8 or take == 'h') else Q[int(rng.integers(0, 8))]
        spec.append((nm, px + sgn * off, zc, h, rng.uniform(-3, 3), rng.uniform(-14, 14), 'near'))
        if rng.random() < 0.7:      # a second one on the other side, further out
            spec.append((G[int(rng.integers(0, len(G)))], px - sgn * rng.uniform(95, 160), zc - rng.uniform(10, 40),
                         rng.uniform(100, 180), rng.uniform(-3, 3), rng.uniform(-20, 20), 'mid'))
        zc -= cfg['step'] * rng.uniform(0.8, 1.2)
        k += 1
    for i in range(22 if take == 'h' else 14):      # mid / far bands across the range, left and right and ahead
        z = rng.uniform(-420, -150) if i < (14 if take == 'h' else 9) else rng.uniform(-700, -420)
        x = rng.uniform(-260, 260) if i < (14 if take == 'h' else 9) else rng.uniform(-420, 420)
        nm = G[int(rng.integers(0, len(G)))] if i % 3 else Q[int(rng.integers(0, 8))]
        spec.append((nm, x, z, rng.uniform(130, 200), rng.uniform(-3, 3), rng.uniform(-15, 15), 'far'))
    cam_z = lambda f: cam_path(take, min(f, 46))[0][2] if f <= 46 else cam_path(take, 46)[0][2] - 8 * (f - 46)  # noqa: E731
    allp = list(pillars)
    new = []
    for i, (nm, x, z, h, roll, yaw, band) in enumerate(spec):
        CV = Carving(f'design/world/cards/{nm}_rgba.png', size=2048, pale=0.18, seed=500 + i)
        gl = []
        rg = np.random.default_rng(900 + i + {'e': 0, 'f': 100, 'g': 200, 'h': 300}[take])
        for rect, gw in _fields(rg, scale=max(1.0, h / 105.0)):
            gl += CV.field(rect, chars[ci[0]:ci[0] + 3000], px=gw / h * 2048, need=0.7)
            ci[0] += 211
        CV.save(f'work/world/J2_{take}/carve_g{i}')
        far_k = {'near': 1.0, 'mid': 1.0, 'far': 1.35}[band]
        o = Wd.card(nm, [x, SEA - 0.12 * h, z], height=h, relief=h * 0.16, roll=roll, yaw=yaw, bend=0.10, id=f'g{i}',
                    carve=CV.spec(lit=[], glow=GLOW, dark=0.45, base=1.0 if take != 'h' else 1.35, glow_fog=0.5 if take != 'h' else 0.12), seg=[128, 256],
                    lum=1.0 if band != 'far' else 0.93, fogk=far_k if take != 'h' else (0.7 if band == 'mid' or (band == 'near') else 1.0))
        P = np.array(o['pos'])
        low = P + np.array([0, -0.85 * h - 20, 0])
        o['keys'] = [[1, {'pos': list(low), 'opacity': 0.0, 'relief': 0.0}], [3, {'opacity': 1.0}],
                     [10 + int(abs(z) / 120), {'pos': list(P), 'relief': h * 0.16}]]
        new.append(dict(o=o, glyphs=gl, x=x, z=z))
    # far ranges (paler, lower)
    for nm, pos, wid, lum in [('range_mid_1', [-60, SEA - 22, -470], 1100, 0.9), ('range_far_1', [260, SEA - 36, -820], 1900, 0.88),
                              ('range_far_2', [-340, SEA - 44, -1050], 2300, 0.85), ('ql_range_far_2', [120, SEA - 34, -700], 1500, 0.9)]:
        o = Wd.card(nm, pos, width=wid, relief=30, lum=lum, fogk=1.4, seak=1.0)
        o['keys'] = [[1, {'opacity': 0.0}], [4, {'opacity': 1.0}]]
    # veins on everything (granite, ql peaks): lit as the camera approaches
    for p in allp + new:
        zc = p['z']
        f_a = 10
        for f in range(10, 47):
            if cam_z(f) - zc < 190:
                f_a = f
                break
        else:
            f_a = 40
        p['o']['carve']['lit'] = vein_lit(p['glyphs'], rng, f_a + int(rng.integers(0, 3)), p_col=(0.5 if p in new else 0.4) if take != 'h' else (0.8 if p in new else 0.6), gk=1.15 if take != 'h' else 1.7)
        p['lit'] = p['o']['carve']['lit']
    # gold threads: from the pressed character to the nearest pillars, then across the gorges between lit columns
    def lit_pt(p, first=True):
        if not p['lit']:
            return None, None
        gid = min(p['lit'], key=lambda l: l[1])[0] if first else max(p['lit'], key=lambda l: l[1])[0]
        gg = next(g for g in p['glyphs'] if g['id'] == gid)
        f = [l for l in p['lit'] if l[0] == gid][0][1]
        return np.array(Wd.card_point(p['o'], gg['u'], gg['v'])), f
    pool = [p for p in new if p['z'] > -330 and p['lit']]
    pool.sort(key=lambda p: -p['z'])
    def arc(a, b, lift):
        L = np.linalg.norm(b - a)
        mid = (a + b) / 2 + np.array([0, min(lift * L, 70), 0])
        return [list(a * (1 - t) ** 2 + mid * 2 * t * (1 - t) + b * t * t) for t in np.linspace(0, 1, 28)]
    for i, p in enumerate(pool[:5]):
        b, f = lit_pt(p)
        Wd.thread(arc(press_w, b, 0.3), f0=11 + 2 * i, fdraw=7, fhold=10, ffade=8, rest=0.0, width=4.2 - 0.3 * i, headW=1.5, col=list(GLOW), glow=1.2)
    if take == 'h':
        pool = [p for p in new if p['z'] > -420 and p['lit']]
        pool.sort(key=lambda p: -p['z'])
        pairs = [(i, i + 1) for i in range(0, len(pool) - 1, 2)] + [(i, i + 3) for i in range(0, len(pool) - 3, 3)]
        for k, (i, j) in enumerate(pairs):
            a, _ = lit_pt(pool[i], first=False)
            b, _ = lit_pt(pool[j])
            if a is None or b is None:
                continue
            Wd.thread(arc(a, b, 0.5), f0=14 + int(k * 30 / len(pairs)), fdraw=6, fhold=34, ffade=12, rest=0.25,
                      width=float(rng.uniform(4.0, 6.0)), headW=1.6, col=list(GLOW), glow=1.2)
    for i in range(0 if take == 'h' else len(pool) - 1):
        a, fa = lit_pt(pool[i], first=False)
        b, fb = lit_pt(pool[i + 1])
        if a is None or b is None:
            continue
        w = float(np.clip(5.0 - 0.18 * i, 2.5, 5.0))
        Wd.thread(arc(a, b, 0.28), f0=int(max(fa, 12)) + 1, fdraw=5, fhold=40, ffade=14, rest=0.1, width=w, headW=1.5, col=list(GLOW), glow=1.1)
    # painted clouds: heads riding the sea and between ridges (billboards), banks low in the gorges
    rc = np.random.default_rng(77)
    for i in range(14):
        z = D1 - 20 - i * 28 + rc.uniform(-8, 8)
        x = cam_path(take, int(min(46, max(10, 9 + 37 * (D1 - z) / 330))))[0][0] + rc.choice([-1, 1]) * rc.uniform(40, 110)
        bank = i % 3 == 0
        nm = ('cloud_bank_%d' if bank else 'cloud_head_%d') % (1 + i % 2)
        h = rc.uniform(26, 44) if not bank else rc.uniform(22, 32)
        y = SEA + (rc.uniform(2, 10) if bank else rc.uniform(6, 40))
        o = Wd.card(nm, [x, y, z], height=h, relief=0.0, billboard=True, anchor='center', fogk=1.0, seak=0.0, opacity=0.0,
                    lum=1.0, id=f'cl{i}')
        o['keys'] = [[1, {'opacity': 0.0}], [12, {'opacity': float(rc.uniform(0.55, 0.85))}]]
    if take in 'fg':      # a pine bough crossing the lens once
        fb = 26 if take == 'f' else 20
        pb = cam_path(take, fb)[0]
        o = Wd.card('pine_bough_%d' % (1 if take == 'f' else 2), [pb[0] + 6, pb[1] + 4, pb[2] - 14], height=30, relief=0.0, billboard=True,
                    anchor='center', fogk=0.0, seak=0.0, opacity=0.0, id='bough')
        o['keys'] = [[1, {'opacity': 0.0}], [fb - 3, {'opacity': 0.0}], [fb - 2, {'opacity': 1.0}], [fb + 3, {'opacity': 1.0}], [fb + 4, {'opacity': 0.0}]]
    # mist between ridges: vertical bands in the gaps, keyed in with the pop
    rr = np.random.default_rng(31)
    for i in range(11):
        z = D1 - 30 - i * 38 + rr.uniform(-10, 10)
        y = rr.uniform(-22, 28)
        o = Wd.mist([rr.uniform(-60, 60), y, z], [rr.uniform(260, 420), rr.uniform(20, 38)], opacity=0.0, thresh=rr.uniform(0.40, 0.5),
                    scale=0.03, band=True, edge=0.5, soft=8, nearFade=9, wash=0.3, speed=[rr.uniform(0.6, 1.4) * rr.choice([-1, 1]), 0.0],
                    seed=70.0 + i)
        op = float(rr.uniform(0.5, 0.75))
        o['keys'] = [[1, {'opacity': 0.0}], [12, {'opacity': op}]]



def build(shot, take='a'):
    n = 47 if shot == 'J2' else 73
    Wd = World(shot + ('' if take == 'a' else '_' + take), n)
    Wd.fog(density=0.0022 if take != 'h' else 0.0012, start=80 if take != 'h' else 120)
    Wd.sea(y=SEA_Y, soft=8, amp=7, scale=0.03, drift=(0.8, 0.2))
    t0 = 190.875 if shot == 'J2' else 200.6667
    def fr(t): return int(round((t - t0) * FPS))
    C0 = np.array([0.0, 0.0, D0])
    C1 = np.array([0.0, 0.0, PAGE_H / 2 / math.tan(math.radians(46 / 2))])   # the deep camera: the page IS its view, flattened
    if shot == 'J2':
        U = [(0, 0.0), (1, 0.0)] + [(1 + i, ease(i / 8, 'inout')) for i in range(1, 9)]
    else:   # J5: deep -> flat over the last 2/3, held flat at the end
        U = [(0, 1.0), (fr(201.3), 1.0)] + [(fr(201.3) + i, 1 - ease(i / 22, 'inout')) for i in range(1, 23)]
    chars = qianziwen() * 3
    ci = [0]
    pillars = []
    dd = take in ('d', 'e', 'f', 'g', 'h')
    RNG_ = [r for r in RANGE if not (dd and r[5] == 'hero')]
    if take in 'efgh':
        RNG_ = [r for r in RNG_ if (r[2] < -190 and not (take == 'h' and r[2] > -420 and abs(r[1] - 20) < 75)) or abs(r[1] - cam_path(take, 9 + int((117.8 - r[2]) / 8.6))[0][0]) > 60]
    for i, (name, x, z, h, roll, role) in enumerate(RNG_):
        CV = Carving(f'design/world/cards/{name}_rgba.png', size=2048, pale=0.18, seed=i)
        gl = []
        rr = np.random.default_rng(i)
        for j in range(3):
            u0 = rr.uniform(0.25, 0.45); v0 = rr.uniform(0.25, 0.55)
            gl += CV.field((u0, v0, u0 + rr.uniform(0.12, 0.25), v0 + rr.uniform(0.12, 0.25)),
                           chars[ci[0]:ci[0] + 300], px=(3.6 if role == 'hero' else 2.4) / h * 2048, need=0.55)
            ci[0] += 300
        CV.save(f'work/world/{shot}/carve_{i}')
        o = Wd.card(name, [x, SEA_Y - 0.12 * h, z], height=h, relief=h * 0.22, roll=roll, bend=0.08, id=f'q{i}',
                    carve=CV.spec(lit=[], glow=GLOW, dark=0.35, base=0.9, glow_fog=0.5), seg=[128, 256])
        pillars.append(dict(o=o, glyphs=gl, role=role, x=x, z=z))
    # far range behind
    Wd.card('ql_range_far_1', [0, SEA_Y - 30, -600], width=1300, relief=30, id='far1')
    Wd.card('ql_range_far_2', [300, SEA_Y - 40, -900], width=1600, relief=30, id='far2')
    # lighting: the pressed character (J1) is lit from f0; the light jumps on the beats to other peaks
    hero = pillars[0] if not dd else dict(o=None, glyphs=[], x=-44.0, z=0.0)
    press = min(hero['glyphs'], key=lambda g: (g['u'] - 0.5) ** 2 + (g['v'] - 0.40) ** 2) if hero['glyphs'] else None
    beats = [191.315, 191.739, 192.172, 192.602]
    rng = np.random.default_rng(4)
    lit = {id(p): [] for p in pillars}
    if shot == 'J2':
        for pi, p in enumerate(pillars):
            for g in p['glyphs']:
                if press is not None and g['id'] == press['id']:
                    f = -10
                elif pi == 0:
                    f = fr(beats[0]) + int(rng.integers(0, 4))
                else:
                    ring = min(3, int(math.hypot(p['x'] - hero['x'], p['z'] - hero['z']) / 160))
                    f = fr(beats[min(ring, 3)]) + int(rng.integers(0, 5))
                lit[id(p)].append([g['id'], f, 1.0])
    else:
        for p in pillars:
            for g in p['glyphs']:
                lit[id(p)].append([g['id'], -10, 1.0])
    for p in pillars:
        p['o']['carve']['lit'] = lit[id(p)]
    # threads in J2 from the pressed character to the first characters lit on each peak
    if shot == 'J2' and press is not None and not dd:
        a = np.array(Wd.card_point(hero['o'], press['u'], press['v']))
        for pi, p in enumerate(pillars[1:9], 1):
            if not p['glyphs']:
                continue
            g = p['glyphs'][len(p['glyphs']) // 2]
            b = np.array(Wd.card_point(p['o'], g['u'], g['v']))
            L = np.linalg.norm(b - a)
            mid = (a + b) / 2 + np.array([0, 0.3 * L, 0])
            pts = [list(a * (1 - t) ** 2 + mid * 2 * t * (1 - t) + b * t * t) for t in np.linspace(0, 1, 24)]
            ring = min(3, int(math.hypot(p['x'] - hero['x'], p['z'] - hero['z']) / 70))
            Wd.thread(pts, f0=fr(beats[min(ring, 3)]) - 3, fdraw=4, fhold=8, ffade=10, rest=0.0, width=2.6, col=list(GLOW))
    # flatten everything onto the page at u=0
    # take a: the world is squashed onto the page as the deep camera sees it and released on the hit;
    # take b: no squashing: a pure dolly zoom (orthographic page -> perspective world), depth grows monotonically.
    if dd:
        # J1 ends flat and square on BOOK's page (media/comp/pages/J1_page_charlit_v4.png, window x 0..2560, y 100..1540
        # = the frame). The page itself is a card at the page plane: its painted 花果山 lifts into relief on the hit,
        # its text and gutter stay where they are; the blue-green country rises out of the cloud behind and around it.
        PX_U = 1440.0 / PAGE_H
        SPL = 1770.0                                     # split just left of the gutter: the right part (gutter, bare
        cy = -(892.5 - 820) / PX_U                       # right page) is washed away by the mist pouring over the gutter
        Wd.card('j1page', [(SPL / 2 - 1280) / PX_U, cy, 0.0], width=SPL / PX_U, height=1785 / PX_U, anchor='center', id='j1page',
                relief=0.0, fogk=0.0, seak=0.0, seg=[256, 256], uvRect=[0, 0, SPL / 3392, 1],
                keys=[[1, {'relief': 0.0}], [9, {'relief': 26.0}]])
        Wd.card('j1page', [((SPL + 3392) / 2 - 1280) / PX_U, cy, 0.0], width=(3392 - SPL) / PX_U, height=1785 / PX_U, anchor='center',
                id='j1page_r', relief=0.0, fogk=0.0, seak=0.0, seg=[64, 64], uvRect=[SPL / 3392, 0, 1, 1],
                keys=[[1, {'opacity': 1.0}], [8, {'opacity': 0.0}]])
        gx = (1949 - 1280) / PX_U
        for j in range(3):
            Wd.mist([gx, -8 + 14 * j, 2], [40, 70], opacity=0.0, thresh=0.33, scale=0.07, soft=3, nearFade=2, wash=0.15,
                    speed=[-0.4, 0.5], seed=60.0 + j,
                    keys=[[0, {'opacity': 0.0, 'pos': [gx, -8 + 14 * j, 2]}], [2, {'opacity': 0.9}],
                          [14, {'opacity': 0.6, 'pos': [gx - 20, -10 + 14 * j, 60]}], [26, {'opacity': 0.0, 'pos': [gx - 35, -14 + 14 * j, 110]}]])
        press_w = np.array([(650 - 1280) / PX_U, -(1403 - 820) / PX_U, 2.0])
        for o in Wd.S['cards']:
            if o['id'] in ('j1page', 'j1page_r'):
                continue
            P = np.array(o['pos']); hh = o['size'][1]
            low = P + np.array([0, -0.85 * hh - 20, 0])
            o['keys'] = [[1, {'pos': list(low), 'opacity': 0.0, 'relief': 0.0}], [3, {'opacity': 1.0}],
                         [10 + int(abs(P[2]) / 120), {'pos': list(P), 'relief': o.get('relief', 0)}]]
        if take in 'efgh':
            granite_range(Wd, take, pillars, press_w, fr)
        for pi, p in enumerate(pillars[:8] if take == 'd' else []):
            if not p['glyphs']:
                continue
            g = p['glyphs'][len(p['glyphs']) // 2]
            b = np.array(Wd.card_point(p['o'], g['u'], g['v']))
            L = np.linalg.norm(b - press_w)
            mid = (press_w + b) / 2 + np.array([0, min(0.35 * L, 60), 0])
            pts = [list(press_w * (1 - t) ** 2 + mid * 2 * t * (1 - t) + b * t * t) for t in np.linspace(0, 1, 24)]
            Wd.thread(pts, f0=12 + 3 * pi, fdraw=4, fhold=8, ffade=10, rest=0.0, width=2.6, col=list(GLOW))
    for o in ([] if dd else Wd.S['cards']):
        if take == 'b':
            if shot == 'J2':
                o['keys'] = [[f, {'relief': o.get('relief', 0) * u}] for f, u in U]
            else:   # J5: once flat (orthographic), the whole painting draws in to a few strokes in the lower-left corner
                P = np.array(o['pos']); corner = np.array([-64.0, -34.0, P[2] * 0.02])
                o['truePos'] = list(P)
                far = o['id'].startswith('far')
                o['keys'] = [[J5_FB, {'pos': list(P), 'scale': 1.0, 'opacity': 1.0}],
                             [J5_FB + 20, {'pos': list(corner + (P - corner) * np.array([0.10, 0.10, 1.0])), 'scale': 0.15,
                                           'opacity': 0.0 if far else 1.0}],
                             [J5_FA, {'relief': o.get('relief', 0)}], [J5_FB, {'relief': 0.0}]]
            continue
        o['keys'] = flat_keys(o, C1, U, o.get('relief', 0))
        o['truePos'] = list(o['pos'])
    # the page plane (text + gutter) at z=0, exactly the frame at f0
    pt = page_texture(shot) if not dd else None
    if pt: Wd.plane(pt, [0, 0, 0.5], [PAGE_H * ASP, PAGE_H], id='page', fogk=0, seak=0, depthWrite=False, order=5)
    # mist: bands between the rows; for J2 a sheet that pours forward over the gutter on the hit
    for i, (z, y) in enumerate([(-30, -18), (-110, -10), (-200, -4), (40, -26)]):
        Wd.mist([0, y, z], [600, 26], band=True, opacity=0.75, thresh=0.42, scale=0.04, soft=6, nearFade=6, wash=0.3,
                speed=[1.2 * (-1) ** i, 0], seed=float(i),
                keys=[[f, {'opacity': 0.75 * u}] for f, u in U])
    if shot == 'J2':
        gx = -PAGE_H * ASP / 2 + 0.18 * PAGE_H * ASP
        Wd.mist([gx, -10, 0], [30, 110], opacity=0.0, thresh=0.36, scale=0.08, soft=3, nearFade=3, wash=0.25, speed=[0.0, 0.6],
                keys=[[0, {'opacity': 0.0, 'pos': [gx, -10, 0]}], [2, {'opacity': 0.9}], [16, {'opacity': 0.7, 'pos': [gx + 10, -14, 60]}],
                      [30, {'opacity': 0.0, 'pos': [gx + 20, -18, 110]}]])
        Wd.mist([gx + 8, -24, 0], [60, 24], pitch=-90, opacity=0.0, thresh=0.34, scale=0.06, soft=3, nearFade=3, wash=0.2, speed=[0.3, 1.2],
                keys=[[0, {'opacity': 0.0, 'pos': [gx + 8, -24, 0]}], [3, {'opacity': 0.9}], [22, {'opacity': 0.6, 'pos': [gx + 20, -26, 80]}],
                      [36, {'opacity': 0.0, 'pos': [gx + 30, -28, 130]}]])
    # camera
    cams = []
    if shot == 'J2':
        d1 = PAGE_H / 2 / math.tan(math.radians(46 / 2))
        for f in range(n):
            if f <= 9:
                u = 0.0 if f <= 1 else ease((f - 1) / 8, 'inout')
                d = math.exp(math.log(D0) + (math.log(d1) - math.log(D0)) * u)
                p = [0.0, 0.0, d]; t = [0.0, 0.0, 0.0]; fov = fov_for(PAGE_H, d)
            elif take in 'efgh':
                (p, t, fov, roll) = cam_path(take, f)
            else:
                v = (f - 9) / (n - 10)
                e = ease(v, 'out') * 0.35 + v * 0.65
                p = [10 * e, 60 * e, d1 - 230 * e]
                t = [4 * e, -40 * e, -60 - 320 * e]
                fov = 46 + 6 * e
            cams.append(dict(p=p, t=t, fov=fov, near=max(0.2, min(p[2] * 0.02, 5)), far=D0 + 3000,
                             fogStart=(80 if take != 'h' else 120) + max(0.0, p[2] - d1)))
            if take in 'efgh' and f > 9:
                cams[-1]['roll'] = roll
    else:
        # J5: start deep, high over the range, pull back and down to square-on; then dolly-zoom out to flat, and the
        # page recedes (the camera keeps retreating along the axis) so the range ends small in the lower-left corner.
        d1 = PAGE_H / 2 / math.tan(math.radians(46 / 2))
        fa, fb = (fr(201.3), fr(201.3) + 22) if take != 'b' else (J5_FA, J5_FB)
        for f in range(n):
            if f < fa:
                v = f / max(fa, 1)
                e = ease(v, 'inout')
                p = [-6 * (1 - e), 34 * (1 - e), d1 - 150 * (1 - e)]
                t = [-10 * (1 - e), -16 * (1 - e), -180 * (1 - e)]
                fov = 50 - 4 * e
            elif f < fb:
                u = ease((f - fa) / (fb - fa), 'inout')
                d = math.exp(math.log(d1) + (math.log(D0) - math.log(d1)) * u)
                p = [0.0, 0.0, d]; t = [0.0, 0.0, 0.0]; fov = fov_for(PAGE_H, d)
            else:
                p = [0.0, 0.0, D0]; t = [0.0, 0.0, 0.0]; fov = fov_for(PAGE_H, D0)
            cams.append(dict(p=p, t=t, fov=fov, near=max(0.2, min(p[2] * 0.02, 5)), far=D0 + 3000,
                             fogStart=80 + max(0.0, p[2] - d1)))
    Wd.camera = cams
    return Wd


def torch(h, w, k):
    """The flashlight pool on the page (J1's light): centre warm white, edges falling off to dim paper; k 0..1."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - w * 0.46) / (w * 0.55), (yy - h * 0.5) / (h * 0.75))
    pool = 1.08 - 0.42 * np.clip(r, 0, 1.4) ** 2
    return 1 + (pool[..., None] * np.array([1.0, 0.98, 0.94], np.float32) - 1) * k


def finish(shot, Wd, take='a'):
    n = Wd.n
    G = paper_grain(1920, 1080, seed=2026, variant='aged')
    ims = []
    for f in range(n):
        img = Wd.finish_frame(f, grain=G, bloom=1.4)
        k = 1 - ease(f / 10, 'inout') if shot == 'J2' else ease((f - (n - 30)) / 20, 'inout')
        img = img * torch(1080, 1920, k)
        ims.append(np.clip(img, 0, 1))
    out = f'media/comp/{shot}.mp4' if take == 'a' else f'work/world/_cand/{shot}_{take}.mp4'
    encode(iter(ims), out, n)
    sheet(ims, f'work/review/comp_v4/{shot}.jpg' if take == 'a' else f'work/review/comp_v4/_cand/{shot}_{take}.jpg', label=shot)
    return ims


if __name__ == '__main__':
    shot = sys.argv[1]
    fs = sys.argv[sys.argv.index('--frames') + 1] if '--frames' in sys.argv else None
    take = sys.argv[sys.argv.index('--take') + 1] if '--take' in sys.argv else 'a'
    Wd = build(shot, take)
    Wd.render(ss=2, frames=fs)
    if fs is None:
        finish(shot, Wd, take)


def write_j1_page(take='b'):
    """media/comp/pages/J1_page_world_J2b.png: J2's frame 0 picture with a 25 % margin on every side (2400x1350): the
    central 1920x1080 is exactly J2 frame 0 (before the torch pool and grain). For BED+CAR's J1 page."""
    import json as _j
    import subprocess
    Wd = build('J2', take)
    c = dict(Wd.camera[0]); c['fov'] = 2 * math.degrees(math.atan(math.tan(math.radians(c['fov'] / 2)) * 1.25))
    S = _j.loads(_j.dumps(Wd.S, default=lambda x: None)); S['camera'] = [c]
    for o in S['cards']:
        o.pop('_D', None)
        if o.get('id') == 'page':      # the page plane must cover the margin too: scale it
            o['size'] = [v * 1.25 for v in o['size']]
    p = os.path.join(Wd.dir, 'j1page_scene.json'); _j.dump(S, open(p, 'w'))
    subprocess.run(['node', 'tools/world/render.mjs', '--scene', os.path.relpath(p, ROOT), '--out', os.path.relpath(os.path.join(Wd.dir, 'j1page'), ROOT),
                    '--w', '2400', '--h', '1350', '--ss', '1', '--frames', '0', '--passes', 'beauty,glow'], check=True, cwd=ROOT)
    b = cv2.imread(os.path.join(Wd.dir, 'j1page/beauty/0000.png')).astype(np.float32) / 255
    g = cv2.imread(os.path.join(Wd.dir, 'j1page/glow/0000.png')).astype(np.float32) / 255
    b = 1 - (1 - b) * (1 - np.clip(cv2.GaussianBlur(g, (0, 0), 8) * 1.4, 0, 1))
    cv2.imwrite(os.path.join(ROOT, 'media/comp/pages/J1_page_world_J2b.png'), (np.clip(b, 0, 1) * 255).astype(np.uint8))
    print('wrote media/comp/pages/J1_page_world_J2b.png')

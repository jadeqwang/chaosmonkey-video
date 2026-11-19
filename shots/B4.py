"""B4 'Sunlight by day and moonlight by night' (29.292-36.417, 171 frames). WORLD v4 (REVISION_V4 §2, REVISION_V3 §3.1).

A REAL camera track along the carved face of 花果山, built in the 3D painted world (tools/world).
- The face: the v3 cliff plate (B_cliff_run, 9040x1280) cut along its own dark clefts into vertical slabs, each a
  relief card (tiled Depth-Anything + the painting's own light/dark), set on a gently undulating plan with alternate
  slabs stepped forward / back, so when the camera travels the near buttress passes the recessed one behind it.
- LIGHT IS THE CARVER: each slab carries `light` (sun, warm) and `light2` (moon, cold). The carving is
  `reveal='light'`: strokes exist only behind the moving terminator (per pixel: at the opening one stroke of one
  character is cut as the edge crosses it). Day fields are cut by the sun moving right to left; at 'moonlight' (32.3)
  the moon-edge crosses left to right and cuts finer columns in the gaps (layer 1, cold glow).
- Every cut sheds bright dust (engine `points`), lifted by the mist up the cliff.
- Opens very close on a hi-res decal of the same rock (the plate region x8 + stone grain, its own big carving in
  register with the wall's glyph), which hands over to the wall as the camera pulls back and travels left.
- Near pine/ledge and a free-standing buttress pass the lens; mist sheets lie between the planes.
- Static inscription 'B4' on the right, present from frame 0.
    $PY shots/B4.py [take] [--frames 0,40] [--prep] [--ss 2] [--final]   takes a b c (default c = the pick);
    --final writes media/comp/B4.mp4 + work/review/comp_v4/B4.jpg, else work/world/B4_<take>.mp4 + _cand sheet
"""
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import World, smooth_path, paper_grain, encode, sheet, ROOT, load_depth  # noqa: E402
from tools.world.carve import Carving, qianziwen  # noqa: E402

FPS = 24
N = 171
F_IN = 703
def fr(t): return t * FPS - F_IN


T_MOON = 32.30
PLATE = 'design/plates/B_huaguoshan/B_cliff_run.png'
CARDS = 'design/world/cards'
UP = 2                                   # slab textures at 2x the plate (plus stone grain)
WALL_H = 40.0                            # world height of the plate
PW, PH = 9040, 1280
UNIT = PH / WALL_H                       # plate px per world unit
REF = np.array([240, 232, 214], np.float32)


# ------------------------------------------------------------------------------------------------ prep (cached)
def _grain(h, w, seed, scales=((0.8, 0.10), (2.0, 0.07), (6.0, 0.05))):
    r = np.random.default_rng(seed)
    g = np.zeros((h, w), np.float32)
    for s, a in scales:
        n = cv2.GaussianBlur(r.standard_normal((h, w)).astype(np.float32), (0, 0), s)
        g += n / (n.std() + 1e-6) * a
    return g


def seams(lum, n_target=16, seed=0):
    """Dark clefts of the plate as top-to-bottom min-cost paths: x(y) for each cut."""
    h, w = lum.shape
    prof = cv2.GaussianBlur(lum[int(h * 0.1):int(h * 0.9)].mean(0)[None], (0, 0), 6)[0]
    # local minima, strongest first, at least 380 px apart
    cand = [x for x in range(30, w - 30) if prof[x] == prof[max(0, x - 40):x + 41].min()]
    cand.sort(key=lambda x: prof[x])
    picked = []
    for x in cand:
        if all(abs(x - p) > 380 for p in picked) and 250 < x < w - 250:
            picked.append(x)
        if len(picked) >= n_target:
            break
    picked.sort()
    out = []
    cost = cv2.GaussianBlur(lum, (0, 0), 2.0)
    for x0 in picked:
        a, b = max(0, x0 - 70), min(w, x0 + 71)
        C = cost[:, a:b] + np.abs(np.arange(a, b) - x0)[None] * 0.0015
        D = C.copy()
        for y in range(1, h):
            prev = D[y - 1]
            m = np.minimum(prev, np.minimum(np.r_[prev[1:], 9], np.r_[9, prev[:-1]]))
            D[y] += m
        xs = np.zeros(h, int)
        xs[-1] = int(np.argmin(D[-1]))
        for y in range(h - 2, -1, -1):
            c = xs[y + 1]
            lo, hi = max(0, c - 1), min(b - a, c + 2)
            xs[y] = lo + int(np.argmin(D[y, lo:hi]))
        xs = cv2.GaussianBlur((xs + a).astype(np.float32)[None], (0, 0), 3)[0]
        out.append(xs)
    return out


def tiled_depth(rgb):
    from tools.world.prep import depth_of
    h, w = rgb.shape[:2]
    T, S_ = h, h // 2
    acc = np.zeros((h, w), np.float32); wt = np.zeros((h, w), np.float32)
    xs = list(range(0, w - T, S_)) + [w - T]
    win = np.hanning(T).astype(np.float32)[None] * np.ones((h, 1), np.float32) + 1e-3
    for x in xs:
        d = depth_of(rgb[:, x:x + T])
        lo, hi = np.percentile(d, 2), np.percentile(d, 98)
        d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
        acc[:, x:x + T] += d * win; wt[:, x:x + T] += win
    return acc / wt


def prep(force=False):
    meta_p = os.path.join(ROOT, CARDS, 'b4_slabs.json')
    if os.path.exists(meta_p) and not force:
        return json.load(open(meta_p))
    rgb = np.array(Image.open(os.path.join(ROOT, PLATE)).convert('RGB'))
    paper = np.percentile(rgb.reshape(-1, 3), 97, axis=0).astype(np.float32)
    lum = rgb.astype(np.float32).mean(2) / 255
    sm = seams(lum)
    # depth: tiled DA (big forms) + the painting's own light (pale faces stand forward, dark clefts recede)
    da = tiled_depth(rgb)
    lb = cv2.GaussianBlur(lum, (0, 0), 10)
    lb = (lb - np.percentile(lb, 2)) / (np.percentile(lb, 98) - np.percentile(lb, 2))
    dep = np.clip(0.55 * da + 0.45 * np.clip(lb, 0, 1), 0, 1)
    dep = cv2.GaussianBlur(dep, (0, 0), 3)
    col = np.clip(rgb.astype(np.float32) / paper[None, None] * REF[None, None], 0, 255)
    bounds = [np.zeros(PH)] + sm + [np.full(PH, PW - 1.0)]
    M = 200                                                   # overlap margin (plate px) for recessed slabs
    slabs = []
    for i in range(len(bounds) - 1):
        L, R = bounds[i], bounds[i + 1]
        front = i % 2 == 0
        xa = int(max(0, L.min() - (0 if front else M))); xb = int(min(PW, R.max() + (0 if front else M)))
        if front:
            xa, xb = int(max(0, L.min() - 8)), int(min(PW, R.max() + 8))
        c = col[:, xa:xb]
        h, w = c.shape[:2]
        # alpha: inside the clefts (front slabs end exactly on the dark line, feathered, a little ragged)
        X = np.arange(w)[None].astype(np.float32) + xa
        rag = _grain(h, 1, 100 + i, ((6.0, 1.0),))[:, :1] * 3
        if front:
            a = np.clip((X - L[:, None] + 2 + rag) / 4, 0, 1) * np.clip((R[:, None] - X + 2 + rag) / 4, 0, 1)
            if i == 0:
                a = np.clip((X + 1e3) / 4, 0, 1) * np.clip((R[:, None] - X + 2 + rag) / 4, 0, 1)
            if i == len(bounds) - 2:
                a = np.clip((X - L[:, None] + 2 + rag) / 4, 0, 1)
        else:
            a = np.ones((h, w), np.float32)
        # 2x + stone grain (fine sand, mottling, rare quartz glints), stronger on the pale faces
        c2 = cv2.resize(c, (w * UP, h * UP), interpolation=cv2.INTER_CUBIC)
        a2 = cv2.resize(a.astype(np.float32), (w * UP, h * UP), interpolation=cv2.INTER_LINEAR)
        g = _grain(h * UP, w * UP, 7 + i)
        l2 = c2.mean(2) / 255
        c2 = np.clip(c2 * (1 + 0.28 * g * (0.3 + 0.7 * l2))[..., None], 0, 255)
        rgba = np.dstack([c2, a2 * 255]).astype(np.uint8)
        name = f'b4_slab_{i:02d}'
        Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, CARDS, name + '_rgba.png'))
        d = cv2.resize(dep[:, xa:xb], (w * UP, h * UP), interpolation=cv2.INTER_CUBIC)
        from tools.world.prep import save_depth
        save_depth(os.path.join(ROOT, CARDS, name + '_depth.png'), d)
        json.dump(dict(src=PLATE, w=w * UP, h=h * UP, aspect=w / h, x0=xa, x1=xb), open(os.path.join(ROOT, CARDS, name + '.json'), 'w'))
        slabs.append(dict(name=name, x0=xa, x1=xb, front=front, L=float(np.median(L)), R=float(np.median(R))))
    meta = dict(slabs=slabs, seams=[s[::32].tolist() for s in sm])
    json.dump(meta, open(meta_p, 'w'), indent=1)
    return meta


# ------------------------------------------------------------------------------------------------ takes
TAKES = {
    # a: eye level, wall undulates gently, camera looks ahead-left along it; pine + buttress + ledge pass
    'a': dict(A=7.0, B=1.5, step=2.4, yaw_end=34, d_end=42, y_end=24, travel=85, fov_end=44, fg='pine,ledge'),
    # b: low, looking up the face (high distance), deeper steps, faster travel, the ledge and pines pass low
    'b': dict(A=6.5, B=2.0, step=2.6, yaw_end=30, d_end=34, y_end=11, look_up=9, travel=100, fov_end=42, fg='ledge,pine2,buttress'),
    # c: high, descending a little, strong oblique (the wall recedes deep), two buttresses
    'c': dict(A=4.0, B=1.2, step=2.2, yaw_end=38, d_end=46, y_end=27, look_up=-4, travel=80, fov_end=36, fg='buttress,buttress2,pine'),
}
DAY_GLOW, MOON_GLOW = (1.0, 0.74, 0.32), (0.72, 0.84, 1.0)
DAY_CUT, MOON_CUT = (1.0, 0.80, 0.70), (0.86, 0.92, 1.0)


def smoothc(keys, n):
    """Monotone piecewise-cubic (pchip-like via smoothstep between keys) for terminators."""
    F = np.array([k[0] for k in keys], float); V = np.array([k[1] for k in keys], float)
    out = np.empty(n)
    for f in range(n):
        if f <= F[0]:
            out[f] = V[0]; continue
        if f >= F[-1]:
            out[f] = V[-1]; continue
        i = int(np.searchsorted(F, f) - 1)
        u = (f - F[i]) / (F[i + 1] - F[i])
        # ease-in for the first segment only (the edge starts slowly over the stroke), linear-ish otherwise
        out[f] = V[i] + (V[i + 1] - V[i]) * (u * u * (3 - 2 * u) * 0.5 + u * 0.5)
    return out


def build(take='a'):
    T = TAKES[take]
    meta = prep()
    Wd = World('B4' + ('' if take == 'a' else '_' + take), N)
    Wd.fog(density=0.006, start=25)
    Wd.sea(y=3.0, soft=4.0, amp=3.0, scale=0.05, drift=(0.5, 0.1))
    rng = np.random.default_rng(4)
    from fontTools.ttLib import TTFont
    cmap = TTFont(os.path.join(ROOT, 'refs/fonts/chongxi-seal/崇羲篆体.otf')).getBestCmap()
    chars = [c for c in qianziwen() if ord(c) in cmap]          # 7 of the 1000 have no seal form in the font (no tofu)
    cur = [0]
    def take_chars(k):
        # a generator over the text from where the last field stopped (fields consume what they place)
        def gen():
            while True:
                yield chars[cur[0] % len(chars)]; cur[0] += 1
        return gen()

    def zc(X):                                    # plan of the wall (z of the face at along-wall X)
        return T['A'] * math.sin(X / 37.0 + 0.6) + T['B'] * math.sin(X / 13.0 + 1.0)
    def dz(X):
        return T['A'] / 37.0 * math.cos(X / 37.0 + 0.6) + T['B'] / 13.0 * math.cos(X / 13.0 + 1.0)
    def wx(px):
        return (px - PW / 2) / UNIT

    slabs = meta['slabs']
    hero_slab = 12
    # ---------------- terminators in plate u (sun right->left; moon left->right after 'moonlight')
    fm = fr(T_MOON)                                # ~72.2
    sl = slabs[hero_slab]
    u_hero_guess = (sl['L'] + sl['R']) / 2 / PW
    # carve the hero slab first so the hero glyph is known
    carv = {}
    glyphs = {}
    for i, s_ in enumerate(slabs):
        CV = Carving(f'{CARDS}/{s_["name"]}_rgba.png', size=4096, pale=0.40, seed=i)
        ppu = 4096 / WALL_H                       # carving px per world unit
        r = np.random.default_rng(50 + i)
        # the visible face of this slab (inside its clefts) in its own u
        fa = (max(s_['L'], s_['x0']) - s_['x0']) / (s_['x1'] - s_['x0'])
        fb = (min(s_['R'], s_['x1']) - s_['x0']) / (s_['x1'] - s_['x0'])
        if i == 0:
            fa = 0.02
        inset = 0.9 * UNIT / (s_['x1'] - s_['x0'])
        u0, u1 = fa + inset, fb - inset
        if u1 - u0 < 0.08:
            carv[i] = (CV, [], []); continue
        # rectangular fields stacked down the face, separated by straight bare channels
        nf = int(r.choice([1, 2, 3, 3]))
        cuts = sorted(r.uniform(0.25, 0.7, nf - 1)) if nf > 1 else []
        vs = [r.uniform(0.10, 0.2)] + list(cuts) + [r.uniform(0.80, 0.88)]
        day, moon = [], []
        for k in range(nf):
            va, vb = vs[k] + (0.025 if k else 0), vs[k + 1] - (0.025 if k < nf - 1 else 0)
            if vb - va < 0.06:
                continue
            gw = float(r.choice([0.6, 0.8, 1.1, 1.5, 1.9]))
            if i == hero_slab and k == 0:
                gw = 1.3
            px = gw * ppu
            cp = float(r.uniform(1.75, 2.1))
            # narrow sub-field: not every field spans the face
            if r.random() < 0.35 and u1 - u0 > 0.3:
                w_ = (u1 - u0) * r.uniform(0.5, 0.8); a_ = u0 + r.uniform(0, (u1 - u0) - w_)
                ua, ub = a_, a_ + w_
            else:
                ua, ub = u0, u1
            day += [dict(g, layer=0) for g in CV.field((ua, va, ub, vb), take_chars(4000), px=px, col_pitch=cp, need=0.55)]
            # moon: finer columns in the gaps between the day columns (same field, half a pitch over)
            pm = px * 0.42
            x1d = ub * CV.W
            x1m = x1d - 0.6 * px - 0.5 * cp * px + 0.6 * pm
            moon += [dict(g, layer=1) for g in CV.field((ua, va + 0.004, x1m / CV.W, vb), take_chars(6000), px=pm,
                                                         col_pitch=cp * px / pm, row_pitch=1.12, need=0.55)]
        CV.save(f'work/world/B4/carve_{i:02d}')
        carv[i] = (CV, day, moon)
    # the hero glyph: on the hero slab's first field, nearest the middle of the face, upper-middle
    _, dh, _ = carv[hero_slab]
    hero = min(dh, key=lambda g: (g['u'] - 0.5) ** 2 + (g['v'] - 0.40) ** 2 * 0.5)
    shs = slabs[hero_slab]
    u_h = (shs['x0'] + hero['u'] * (shs['x1'] - shs['x0'])) / PW
    gw_u = hero['px'] / 4096 * WALL_H * UNIT / PW              # glyph width in plate u
    US = smoothc([(0, u_h + 0.22 * gw_u), (22, u_h - 0.62 * gw_u), (34, u_h - 0.02), (48, u_h - 0.055), (60, u_h - 0.12), (fm - 3, -0.03)], N)
    UM = smoothc([(fm - 2, 0.10), (fm + 20, 0.36), (fm + 60, 0.62), (N - 1, 0.86)], N)
    SUN_W = smoothc([(0, 0.45), (fm - 8, 0.45), (fm + 2, 0.0)], N)
    MOON_W = smoothc([(fm - 4, 0.0), (fm + 8, 0.5), (N - 1, 0.5)], N)
    LUM = smoothc([(0, 1.0), (fm - 6, 1.0), (fm + 6, 0.94), (N - 1, 0.94)], N)
    # ---------------- slab cards
    cards = []
    for i, s_ in enumerate(slabs):
        CV, day, moon = carv[i]
        Xc = wx((s_['x0'] + s_['x1']) / 2)
        z = zc(Xc) + (T['step'] if s_['front'] else -T['step'])
        yaw = -math.degrees(math.atan(dz(Xc)))
        span = (s_['x1'] - s_['x0'])
        loc = lambda U: (U * PW - s_['x0']) / span                                     # noqa: E731
        keys = [[f, {'light': [loc(US[f]), 0.25 * UNIT / span, -1, float(SUN_W[f])],
                     'light2': [loc(UM[f]), 0.25 * UNIT / span, 1, float(MOON_W[f])], 'lum': float(LUM[f])}] for f in range(N)]
        lit = [(g['id'], 0, float(0.7 + 0.5 * rng.random()), g['layer']) for g in day + moon]
        carve = None
        if lit:
            carve = CV.spec(lit=lit, glow=DAY_GLOW, glow2=MOON_GLOW, col=DAY_CUT, col2=MOON_CUT, dark=0.45, base=0.08, glow_fog=0.6,
                            reveal='light', revW=0.12 * UNIT / span, flashW=1.6 * UNIT / span)
        dy = float(np.random.default_rng(900 + i).uniform(-5, 3))
        o = Wd.card(s_['name'], [Xc, -2.0 + dy, z], height=WALL_H, relief=3.2, yaw=yaw, seg=[max(16, int(span / 12)), 256],
                    light={'v': keys[0][1]['light'], 'col': [1.0, 0.95, 0.86], 'wig': [0.9 * UNIT / span, 5.0]},
                    light2={'v': keys[0][1]['light2'], 'col': [0.86, 0.93, 1.06], 'wig': [0.7 * UNIT / span, 7.0]},
                    carve=carve, keys=keys, id=f'slab{i}', tint=[0.98, 0.97, 0.96],
                    order=-1 if s_['front'] else -2)   # recessed slabs draw first: no gap behind a feathered front edge
        cards.append((o, s_, day, moon, CV))
    o_h, s_h = cards[hero_slab][0], cards[hero_slab][1]
    P_h = np.array(Wd.card_point(o_h, hero['u'], hero['v']))
    n_h = np.array(Wd.card_normal(o_h))
    t_h = np.array([math.cos(math.radians(o_h['yaw'])), 0, -math.sin(math.radians(o_h['yaw']))])
    # ---------------- the macro decal: the same rock x8 with stone grain and its own big cut of the hero glyph
    allg = carv[hero_slab][1] + carv[hero_slab][2]
    decals = []
    for tag, DW, DH, fade, blur_k in (('mid', 8.0, 4.5, [0, 30, 44], 3.0), ('near', 3.2, 1.8, [0, 20, 32], 3.0),
                                      ('macro', 1.2, 0.675, [0, 12, 22], 3.0)):
        dec_tex, dec_cv, dec_gl = macro_decal(s_h, hero, allg, DW, DH, tag=tag)
        dloc = lambda U, DW=DW: 0.5 + ((U - u_h) * PW / UNIT) / DW                          # noqa: E731
        dkeys = [[f, {'light': [dloc(US[f]), 0.1 / DW, -1, float(SUN_W[f]) * 0.6], 'opacity': float(np.interp(f, fade, [1, 1, 0]))}] for f in range(N)]
        Wd.overlay(dec_tex, list(P_h + n_h * 0.06), [DW, DH], yaw=o_h['yaw'], id=tag, round=0.5,
                   light={'v': dkeys[0][1]['light'], 'col': [1.0, 0.95, 0.86], 'wig': [0.9 / DW, 5.0 * DH / WALL_H]},
                   carve=dec_cv.spec(lit=[(g['id'], 0, 0.15, g['layer']) for g in dec_gl], glow=DAY_GLOW, col=(0.97, 0.93, 0.90), dark=0.30,
                                     base=0.05, reveal='light', revW=0.03 / DW, flashW=0.4 / DW, bevelPx=5.0, bevelK=0.9),
                   keys=dkeys, visible=[0, fade[-1] + 1])
        decals.append((tag, DW, DH, dec_cv, dec_gl))
    _, DW, DH, dec_cv, dec_gl = decals[-1]
    # ---------------- dust: every cut sheds bright grains; the mist carries them up the cliff
    parts_d, parts_m = [], []
    fsu = lambda U: float(np.interp(-U, -US, np.arange(N)))                             # noqa: E731
    fmu = lambda U: float(np.interp(U, UM, np.arange(N)))                               # noqa: E731
    for o, s_, day, moon, CV in cards:
        span = s_['x1'] - s_['x0']
        for layer, gl, out in ((0, day, parts_d), (1, moon, parts_m)):
            for g in gl:
                Ug = (s_['x0'] + g['u'] * span) / PW
                if layer == 0 and Ug < US[-1]:
                    continue
                if layer == 1 and Ug > UM[-1]:
                    continue
                near = abs((s_['x0'] + g['u'] * span) / PW - u_h) * PW / UNIT < 45
                k = (28 if near else 8) if layer == 0 else 6
                for _ in range(k):
                    du, dv = rng.uniform(-0.4, 0.4, 2) * g['px'] / np.array([CV.W, CV.H])
                    u, v = g['u'] + du, g['v'] + dv
                    f0 = (fsu if layer == 0 else fmu)((s_['x0'] + u * span) / PW) + rng.uniform(0, 3)
                    p = np.array(Wd.card_point(o, u, v)) + np.array(Wd.card_normal(o)) * 0.15
                    vel = np.array(Wd.card_normal(o)) * rng.uniform(0.05, 0.35) + np.array([rng.uniform(-0.3, 0.3), rng.uniform(0.3, 1.1), 0])
                    out.append([*p, f0, *vel, rng.uniform(2.5, 6.0), rng.uniform(0.03, 0.07) * (1 if layer == 0 else 0.8) * rng.choice([1, 1, 1.7]), rng.random()])
    # the dust is gold leaf by day and silver leaf by night (金箔 / 銀箔 flecks: a painter's material, darker than the
    # paper so it reads as pigment, warm in the glow pass so it catches the light)
    Wd.points(parts_d, id='dust_day', acc=[0.05, 0.35, 0], sway=0.35, swayF=1.1, col=[0.80, 0.60, 0.26], glowCol=[1.0, 0.74, 0.32],
              glow=0.9, opacity=0.9, minPx=1.4, maxPx=12, fadeIn=0.12, fadeOut=0.5, fogk=0.8)
    Wd.points(parts_m, id='dust_moon', acc=[0.05, 0.3, 0], sway=0.3, swayF=1.3, col=[0.97, 0.98, 1.0], glowCol=[0.72, 0.84, 1.0],
              glow=1.1, opacity=0.95, minPx=1.3, maxPx=10, fadeIn=0.12, fadeOut=0.5, fogk=0.8)
    # macro dust: grains torn from the stroke where the edge cuts it (seen huge at the opening)
    pc = []
    cov = dec_cv.cov.copy()
    hg = next(g for g in dec_gl if g['hero'])
    hx, hy, hr = int(hg['u'] * dec_cv.W), int(hg['v'] * dec_cv.H), int(hg['px'] * 0.7)
    m = np.zeros_like(cov); m[max(0, hy - hr):hy + hr, max(0, hx - hr):hx + hr] = 1
    ys, xs = np.nonzero((cov > 0.5) & (m > 0))
    sel = rng.choice(len(xs), min(420, len(xs)), replace=False)
    R = np.array([t_h, [0, 1, 0], n_h]).T
    for j in sel:
        u, v = xs[j] / dec_cv.W, ys[j] / dec_cv.H
        U = u_h + (u - 0.5) * DW * UNIT / PW
        f0 = fsu(U) + rng.uniform(0, 1.5)
        p = P_h + R @ np.array([(u - 0.5) * DW, (0.5 - v) * DH, 0.08])
        vel = n_h * rng.uniform(0.02, 0.10) + np.array([rng.uniform(-0.05, 0.05), rng.uniform(0.06, 0.22), 0])
        pc.append([*p, f0, *vel, rng.uniform(0.8, 2.0), rng.uniform(0.003, 0.008) * rng.choice([1, 1, 1, 1.8]), rng.random()])
    Wd.points(pc, id='dust_macro', acc=[0, 0.10, 0], sway=0.015, swayF=2.0, col=[0.84, 0.66, 0.32], glowCol=[1.0, 0.76, 0.36], glow=0.5, opacity=0.85,
              minPx=1.4, maxPx=26, fadeIn=0.08, fadeOut=0.5, keys=[[0, {'opacity': 1.0}], [26, {'opacity': 1.0}], [38, {'opacity': 0.0}]])
    # ---------------- foreground and mist
    Xh = float(P_h[0])
    def fg_card(name, dX, dzf, y0, h, **kw):
        X = Xh + dX
        return Wd.card(name, [X, y0, zc(X) + dzf], height=h, yaw=-math.degrees(math.atan(dz(X))) * 0.5, **kw)
    for item in T['fg'].split(','):
        if item == 'pine':
            fg_card(grey_card('pine_near_1'), -31, 10.0, 1.0, 15, relief=1.2, ink=0.95, id='fg_pine')
            fg_card(grey_card('pine_near_2'), -70, 27.0, -4.0, 17, relief=1.2, ink=1.0, lum=0.92, id='fg_pine_n')
        if item == 'pine2':
            fg_card(grey_card('pine_near_2'), -47, 12.0, -1.0, 14, relief=1.2, ink=0.9, id='fg_pine2')
        if item in ('buttress', 'buttress2'):
            src = cards[6 if item == 'buttress' else 10][0]
            dX, dzf = (-60, 14.0) if item == 'buttress' else (-36, 11.0)
            o = fg_card(os.path.basename(src['tex'])[:-len('_rgba.png')], dX, dzf, -6.0, 46, relief=4, ink=1.0, id='fg_' + item, bend=0.15,
                        light=src['light'], light2=src['light2'], carve=src['carve'], keys=src['keys'], lum=0.95)
        if item == 'ledge':
            fg_card(grey_card('hgs_ledge_near_1'), -52, 22.0, -3.0, 9, relief=2, ink=0.9, id='fg_ledge')
    # mist: sheets parallel to the face (one hugging it and rising: it carries the dust), bands between the planes
    st = T['step']
    for k, (dzm, y, h, op, th, sp) in enumerate([(st + 1.0, 10, 10, 0.55, 0.50, [0.25, -0.45]), (st + 1.4, 27, 8, 0.45, 0.52, [-0.2, -0.4]),
                                                 (st + 1.2, 41.5, 9, 0.95, 0.30, [0.3, -0.1]), (-6.0, 43, 12, 0.9, 0.3, [0.2, 0]),
                                                 (6.0, 7, 9, 0.7, 0.44, [0.5, 0]), (12.0, 15, 10, 0.45, 0.50, [-0.6, 0]),
                                                 (20.0, 5, 12, 0.55, 0.46, [0.7, 0]), (30.0, 26, 9, 0.35, 0.54, [-0.5, 0])]):
        X = Xh - 45
        Wd.mist([X, y, zc(X) + dzm], [260, h], yaw=0, opacity=op, thresh=th, scale=0.09, band=True, edge=0.55, soft=1.2 + dzm * 0.15,
                nearFade=1.5, wash=0.28, speed=sp, seed=float(k * 3 + 1))
    Wd.card('range_mid_1', [Xh - 70, 18, -160], width=420, relief=20, ink=0.55, id='far_range', fogk=0.6, order=-3)
    Wd.mist([Xh - 45, 4.0, 0], [400, 200], pitch=-90, opacity=0.8, thresh=0.40, scale=0.04, edge=0.3, soft=3, wash=0.3, speed=[0.5, 0.15], seed=30.0)
    # ---------------- camera: one stroke -> pull back + travel right to left + widen
    ys_end = T['y_end']
    KEYS = [  # (frame, along-wall X offset, distance, height offset, yaw deg (look ahead-left), fov)
        (0, 0.20, 0.42, 0.05, 0, 30),
        (18, 0.08, 0.95, 0.02, 0, 30),
        (36, -1.2, 4.6, 0.4, 6, 32),
        (62, -16, 15.0, 1.5, 20, 36),
        (105, -T['travel'] * 0.48, T['d_end'] * 0.6, (ys_end - P_h[1]) * 0.55, T['yaw_end'] * 0.75, (34 + T['fov_end']) / 2),
        (N - 1, -T['travel'], T['d_end'], ys_end - P_h[1], T['yaw_end'], T['fov_end']),
    ]
    cam = smooth_path([(f, [dx, d, dy, yw, fv]) for f, dx, d, dy, yw, fv in KEYS], N)
    Wd.camera = []
    lu = T.get('look_up', 0)
    for f in range(N):
        dx, d, dy, yw, fv = cam[f]
        X = Xh + dx
        nz = np.array([math.sin(math.atan(dz(X))) * -1, 0, 1.0]); nz /= np.linalg.norm(nz)
        base = np.array([X, P_h[1] + dy, zc(X) + (T['step'] if s_h['front'] else -T['step'])])
        if f < 30:   # stay registered on the hero glyph while close
            k = 1 - smooth01((f - 14) / 16)
            base = base * (1 - k) + (P_h + t_h * dx + np.array([0, dy, 0])) * k
            nz = nz * (1 - k) + n_h * k
        p = base + nz * d
        ang = math.radians(yw)
        look = -nz * math.cos(ang) + np.array([-1, 0, 0]) * math.sin(ang)
        lk = lu * smooth01((f - 40) / 100)
        t = p + look * max(d, 1.0) + np.array([0, max(d, 1.0) * math.tan(math.radians(lk)), 0])
        Wd.camera.append(dict(p=p.tolist(), t=t.tolist(), fov=float(fv), near=max(0.02, min(d * 0.05, 0.5)), far=3000,
                              paper=list(np.array([0.925, 0.886, 0.800]) * (1 - night(f)) + np.array([0.880, 0.884, 0.872]) * night(f))))
    info = dict(take=take, hero=hero['ch'], u_h=u_h, n_day=sum(len(c[2]) for c in cards), n_moon=sum(len(c[3]) for c in cards),
                dust=[len(parts_d), len(parts_m), len(pc)], P_h=P_h.tolist())
    json.dump(info, open(os.path.join(Wd.dir, 'meta.json'), 'w'), indent=1)
    return Wd, info


def grey_card(name):
    """A near element from the shared cards, desaturated to the cliff's grey ink (same alpha and depth)."""
    out = f'b4g_{name}'
    p = os.path.join(ROOT, CARDS, out + '_rgba.png')
    if not os.path.exists(p):
        a = np.array(Image.open(os.path.join(ROOT, CARDS, name + '_rgba.png')).convert('RGBA')).astype(np.float32)
        l = a[..., :3].mean(2, keepdims=True)
        a[..., :3] = l + (a[..., :3] - l) * 0.25
        Image.fromarray(a.astype(np.uint8), 'RGBA').save(p)
        import shutil
        shutil.copy(os.path.join(ROOT, CARDS, name + '_depth.png'), os.path.join(ROOT, CARDS, out + '_depth.png'))
        shutil.copy(os.path.join(ROOT, CARDS, name + '.json'), os.path.join(ROOT, CARDS, out + '.json'))
    return out


def smooth01(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def night(f):
    return smooth01((f - (fr(T_MOON) - 6)) / 14)


def place_glyph(CV, ch, u, v, px):
    """One glyph into a Carving at (u, v) (same maths as Carving.field; for registering a decal with the wall)."""
    g = CV._glyph(ch, px)
    gh, gw = g.shape
    cx, cy = int(u * CV.W), int(v * CV.H)
    ya, xa = cy - gh // 2, cx - gw // 2
    sl = (slice(max(ya, 0), min(ya + gh, CV.H)), slice(max(xa, 0), min(xa + gw, CV.W)))
    if sl[0].stop <= sl[0].start or sl[1].stop <= sl[1].start:
        return None
    gs = g[sl[0].start - ya:sl[0].stop - ya, sl[1].start - xa:sl[1].stop - xa]
    gid = Carving._next[0]; Carving._next[0] += 1
    CV.cov[sl] = np.maximum(CV.cov[sl], gs)
    r = int(px * 0.5)
    CV.ids[max(cy - r, 0):min(cy + r, CV.H), max(cx - r, 0):min(cx + r, CV.W)] = gid
    rec = dict(id=gid, ch=ch, u=u, v=v, px=px)
    CV.glyphs.append(rec)
    return rec


def macro_decal(s_, hero, glyphs, DW=8.0, DH=4.5, W=3840, H=2160, tag='macro'):
    """The plate around the hero glyph at x15 (the painting carries nothing at this scale: keep its tone), with the
    stone's grain (fine sand, pits, a few quartz glints), and the wall's own glyphs in the region carved again at
    this resolution, in register (same chars, places, sizes, layers)."""
    out = os.path.join(ROOT, f'work/world/B4/{tag}_rgba.png')
    rgb = np.array(Image.open(os.path.join(ROOT, f'{CARDS}/{s_["name"]}_rgba.png')).convert('RGB')).astype(np.float32)
    hh, ww = rgb.shape[:2]
    cx, cy = hero['u'] * ww, hero['v'] * hh
    ppu = hh / WALL_H
    x0, y0 = cx - DW / 2 * ppu, cy - DH / 2 * ppu
    M = np.float32([[W / (DW * ppu), 0, -x0 * W / (DW * ppu)], [0, H / (DH * ppu), -y0 * H / (DH * ppu)]])
    c = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    c = cv2.GaussianBlur(c, (0, 0), 2)
    c = c * 0.5 + cv2.GaussianBlur(c, (0, 0), 18) * 0.5
    g = _grain(H, W, 77, ((0.9, 0.10), (2.0, 0.08), (4.5, 0.04)))
    r = np.random.default_rng(78)
    glint = cv2.GaussianBlur((r.random((H, W)) > 0.9975).astype(np.float32), (0, 0), 1.1) * 5
    pits = (cv2.GaussianBlur(r.standard_normal((H, W)).astype(np.float32), (0, 0), 1.6) < -1.25).astype(np.float32) * 0.12
    lum = c.mean(2) / 255
    c = np.clip(c * (1 + 0.45 * g * (0.4 + 0.6 * lum))[..., None] * (1 - pits[..., None]) + np.clip(glint, 0, 1)[..., None] * 45, 0, 255)
    Image.fromarray(np.dstack([c, np.full((H, W), 255, np.float32)]).astype(np.uint8), 'RGBA').save(out)
    CV = Carving(os.path.relpath(out, ROOT), size=H, pale=0.0, seed=hero['id'])
    placed = []
    sc = (H / DH) / (4096 / WALL_H)                   # decal carving px per wall carving px
    for gl in glyphs:
        du = (gl['u'] - hero['u']) * ww / ppu; dv = (gl['v'] - hero['v']) * hh / ppu
        if abs(du) > DW / 2 + 1 or abs(dv) > DH / 2 + 1:
            continue
        rec = place_glyph(CV, gl['ch'], 0.5 + du / DW, 0.5 + dv / DH, gl['px'] * sc)
        if rec:
            rec['layer'] = gl['layer']; rec['hero'] = gl['id'] == hero['id']
            placed.append(rec)
    CV.cov = cv2.GaussianBlur(CV.cov, (0, 0), 3.0)            # chisel walls: a bevel the light can catch
    CV.save(f'work/world/B4/carve_{tag}')
    return os.path.relpath(out, ROOT), CV, placed


# ------------------------------------------------------------------------------------------------ finish
def finish(Wd, take, out=None, sheet_out=None):
    from tools.ink.inscription import inscription
    from tools.ink.paper import Paper
    G = paper_grain(1920, 1080)
    P = Paper(1920, 1080, 'new', seed=1988)
    ins = inscription((1920, 1080), 'B4', box=(1650, 110, 210, 720), paper=P)
    # a veil of bare paper at the right edge (mist in front of the face) on which the inscription stands
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    nz = cv2.resize(np.random.default_rng(31).random((14, 24)).astype(np.float32), (1920, 1080), interpolation=cv2.INTER_CUBIC) - 0.5
    veil = np.clip((xx / 1920 + nz * 0.10 - 0.80) / 0.09, 0, 1)
    veil = veil * veil * (3 - 2 * veil)
    ims = []
    for f in range(N):
        img = Wd.finish_frame(f, grain=G, bloom=1.3, glow_gain=1.0)
        pap = np.array(Wd.camera[f]['paper'], np.float32) * G
        img = img + (pap - img) * veil[..., None] * 0.97
        ins.draw(img)
        ims.append(np.clip(img, 0, 1))
    if out:
        encode(iter(ims), out, N)
    sheet(ims, sheet_out or f'work/review/comp_v4/_cand/B4_{take}.jpg', label=f'B4{take}')
    return ims


if __name__ == '__main__':
    if '--prep' in sys.argv:
        m = prep(force=True)
        print(len(m['slabs']), [(s['x0'], s['x1'], s['front']) for s in m['slabs']])
        sys.exit()
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    take = args[0] if args else 'c'                 # the pick (LOG_v4_world.md, B4/B5)
    frames = None
    if '--frames' in sys.argv:
        frames = sys.argv[sys.argv.index('--frames') + 1]
        args = [a for a in args if a != frames]
    ss = int(sys.argv[sys.argv.index('--ss') + 1]) if '--ss' in sys.argv else 2
    Wd, info = build(take)
    print(json.dumps(info))
    Wd.render(ss=ss, frames=frames)
    if frames is None:
        final = '--final' in sys.argv
        finish(Wd, take, out='media/comp/B4.mp4' if final else f'work/world/B4_{take}.mp4',
               sheet_out='work/review/comp_v4/B4.jpg' if final else None)

#!/usr/bin/env python
"""dcomp: D-FLIGHT comp tool. One painted/video flight (12 s Kling take, or a stand-in) -> the 204-frame shot D4+D5+D6.

  PY tools/dflight/dcomp.py work/dflight/dcomp_standin.json [--w 960 --h 540] [--frames 0,40,80] [--no-encode]
                            [--name NAME] [--no-track]
  s = 0..203 (song frame 1630 + s, t = 67.917 + s/24). Output media/comp/_cand/DFLIGHT_<name>.mp4 (+ _D4 s0-32, _D5 s33-133,
  _D6 s134-203), sheets work/review/comp_v4/DFLIGHT_<name>.jpg + DFLIGHT_<name>_dense.jpg, work/dflight/cut_to_D7.jpg.

Stages (all authored in 960x540 reference units, scaled by W/960, so --w 1920 --h 1080 is a pure re-render):
  1 retime   piecewise-linear map s -> source frame (PCHIP-smoothed), DIS interpolation when slower than 1:1 (tools/swarm4/vcomp.py
             Retimer, imported). Base frames cached in work/dflight/<name>/base_*.
  2 track    the carving panel: config gives its quad (corners of panel rect `ref_rect`, panel units = 1 glyph) at KEY frames; between keys
             the quad is propagated frame to frame by RANSAC homographies from LK features around the panel (forward from key a, backward
             from key b, blended linearly: drift is spread out). Frames where tracking fails fall back to corner interpolation.
  3 carve    typeset glyph columns (seal font) as incised cuts: multiply into the plate, dark upper-left wall, light lower-right lip.
  4 light    ember on the sung 通, then IDS component jumps (real decomposition, shots/_tong rules) drawn as gold threads that snap taut in
             3 frames then fade to a faint line; glow lives inside the cut strokes (+ a tight halo). Schedule logged to work/dflight/jumps_<name>.json.
  5 frontier optional screen-space grade (lit / edge / dark country) + fine arcing gold threads. Off by default.
  6 inscription (same code and boxes as shots/_dfinish2.py), landing bloom (+ optional 倉 seal), outputs.
Config: see work/dflight/dcomp_standin.json and the README block at the end of work/dflight/COMP_NOTES.md.
"""
import argparse, collections, hashlib, json, math, os, re, subprocess, sys
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from tools.swarm4.vcomp import Retimer          # noqa: E402  (PCHIP retime + DIS interpolation)
F32 = np.float32
REF_W, REF_H = 960, 540
T0, FPS, NF = 67.917, 24.0, 204
SEAL_FONT = 'refs/fonts/chongxi-seal/崇羲篆体.otf'
SYLLABLE_FONT = 'refs/fonts/guangekai/館閣楷-Regular.ttf'
IDC = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻')
DENY = set('⺀𫝀龶𠂇一丿丶丨亅乚乙𠃌𠂊二八丷亠冂冖厶䒑儿コ十人入凵匚冫丆𠂉𠂆乛⺊卜丄丅𠄌㇀㇏①②③④⑤⑥⑦⑧⑨⑩')
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def smooth(x, a, b):
    t = np.clip((np.asarray(x, F32) - a) / max(b - a, 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


# ============================================================================================== 1 retime
def stage_base(cfg, W, H, name):
    src = cfg['source']
    st = os.stat(os.path.join(ROOT, src['file']))
    key = json.dumps([src['file'], st.st_size, int(st.st_mtime), cfg['map'], W, H, NF], sort_keys=True)
    d = os.path.join(ROOT, 'work/dflight', name, f'base_{W}x{H}_' + hashlib.md5(key.encode()).hexdigest()[:8])
    if len([f for f in os.listdir(d) if f.startswith('b')]) == NF if os.path.isdir(d) else False:
        return d
    os.makedirs(d, exist_ok=True)
    rt = Retimer(dict(sources=[dict(name='k', v0=0, file=src['file'])], map=cfg['map']), W, H)
    log(f'retime: source {rt.srcs[0].n} frames; v(s) at s=0,33,134,203 = {[round(rt.v(s), 2) for s in (0, 33, 134, 203)]}')
    for s in range(NF):
        cv2.imwrite(f'{d}/b{s:04d}.png', rt.frame(s))
    json.dump([rt.v(s) for s in range(NF)], open(d + '/v.json', 'w'))
    return d


# ============================================================================================== 2 tracking
def _quad_mask(shape, quad, grow):
    m = np.zeros(shape, np.uint8)
    q = np.clip(np.asarray(quad, np.float64), -3e5, 3e5).astype(np.int32)
    cv2.fillConvexPoly(m, q, 255)
    return cv2.dilate(m, np.ones((grow, grow), np.uint8)) if grow else m


def step_H(a, b, quad, grow=61):
    """Homography taking frame a coords -> frame b coords, from LK features on/around the quad. (H, n_inliers) or (None, 0)."""
    m = _quad_mask(a.shape, quad, grow)
    pts = cv2.goodFeaturesToTrack(a, 600, 0.002, 5, mask=m, blockSize=5)
    if pts is None or len(pts) < 12:
        return None, 0
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(a, b, pts, None, winSize=(21, 21), maxLevel=4)
    back, st2, _ = cv2.calcOpticalFlowPyrLK(b, a, nxt, None, winSize=(21, 21), maxLevel=4)
    ok = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(back - pts, axis=2)[:, 0] < 0.8)
    if ok.sum() < 12:
        return None, int(ok.sum())
    H, inl = cv2.findHomography(pts[ok], nxt[ok], cv2.RANSAC, 1.5)
    if H is not None and inl.sum() >= 10 and inl.sum() >= 0.4 * ok.sum():
        sc = math.sqrt(abs(np.linalg.det(H[:2, :2])))
        if 0.7 < sc < 1.4:
            return H, int(inl.sum())
    A, inl = cv2.estimateAffinePartial2D(pts[ok], nxt[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if A is not None and inl.sum() >= 10:
        return np.vstack([A, [0, 0, 1]]), int(inl.sum())
    return None, 0


def chain(grays, s_from, s_to, quad):
    """Propagate quad from frame s_from to s_to. -> {s: quad}, {s: n_inliers or 0 (lost)}"""
    d = 1 if s_to > s_from else -1
    out, nin = {s_from: np.array(quad, np.float64)}, {s_from: 99}
    cur = out[s_from]
    s = s_from
    while s != s_to:
        H, n = step_H(grays[s], grays[s + d], cur)
        if H is not None:
            cur = cv2.perspectiveTransform(cur[None].astype(np.float64), H.astype(np.float64))[0]
        s += d
        out[s], nin[s] = cur.copy(), n
    return out, nin


def track_panel(cfg, base_dir, name, W, H, use_track=True):
    keys = sorted(cfg['panel']['keys'], key=lambda k: k['s'])
    kq = [np.array(k['corners'], np.float64) for k in keys]
    ks = [int(k['s']) for k in keys]
    sig = hashlib.md5((base_dir + json.dumps(cfg['panel']['keys']) + str(use_track)).encode()).hexdigest()[:8]
    cache = os.path.join(ROOT, 'work/dflight', name, f'track_{sig}.json')
    if os.path.exists(cache):
        j = json.load(open(cache))
        log('tracking: cached', cache)
        return [np.array(q) for q in j['quads']], j['mode']
    grays = []
    for s in range(NF):
        im = cv2.imread(f'{base_dir}/b{s:04d}.png')
        grays.append(cv2.cvtColor(cv2.resize(im, (REF_W, REF_H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY))
    quads, mode = [None] * NF, ['interp'] * NF
    fwd, bwd = {}, {}
    for i, (s, q) in enumerate(zip(ks, kq)):
        if use_track and i + 1 < len(ks):
            fwd[i] = chain(grays, s, ks[i + 1], q)
        if use_track and i > 0:
            bwd[i] = chain(grays, s, ks[i - 1], q)
    for s in range(NF):
        j = max([i for i in range(len(ks)) if ks[i] <= s], default=None)
        if j is None:                                           # before the first key: backward chain of key 0
            if use_track:
                qs, ns = chain(grays, ks[0], 0, kq[0]) if s == 0 or 'pre' not in fwd else fwd['pre']
                fwd['pre'] = (qs, ns) if 'pre' not in fwd else fwd['pre']
                quads[s], mode[s] = fwd['pre'][0][s], 'track'
            else:
                quads[s] = kq[0]
            continue
        if j + 1 >= len(ks):                                    # after the last key: forward chain
            if use_track:
                if 'post' not in fwd:
                    fwd['post'] = chain(grays, ks[-1], NF - 1, kq[-1])
                quads[s], mode[s] = fwd['post'][0][s], 'track'
            else:
                quads[s] = kq[-1]
            continue
        a, b = ks[j], ks[j + 1]
        u = (s - a) / float(b - a)
        lin = kq[j] * (1 - u) + kq[j + 1] * u
        if not use_track:
            quads[s] = lin
            continue
        qa, na = fwd[j]
        qb, nb = bwd[j + 1]
        oka = all(na[t] > 0 for t in range(a + 1, s + 1))
        okb = all(nb[t] > 0 for t in range(b - 1, s - 1, -1))
        if oka and okb:
            quads[s], mode[s] = qa[s] * (1 - u) + qb[s] * u, 'track'
        elif oka:
            quads[s], mode[s] = qa[s] * (1 - u) + lin * u, 'fwd'
        elif okb:
            quads[s], mode[s] = qb[s] * u + lin * (1 - u), 'bwd'
        else:
            quads[s] = lin
    # report drift of each chain at its far key
    for i in fwd:
        if isinstance(i, int):
            qa, na = fwd[i]
            e = np.abs(qa[ks[i + 1]] - kq[i + 1]).max()
            lost = sum(1 for t, n in na.items() if n == 0)
            log(f'tracking: keys {ks[i]}->{ks[i + 1]}: forward chain lands {e:.1f} px (ref) from key corners; lost steps {lost}; '
                f'median inliers {int(np.median([n for t, n in na.items() if t != ks[i]])) if len(na) > 1 else 0}')
    json.dump(dict(quads=[q.tolist() for q in quads], mode=mode), open(cache, 'w'))
    log('tracking modes:', dict(collections.Counter(mode)))
    return quads, mode


# ============================================================================================== 3 panel + schedule
def ids_table():
    ids = {}
    for l in open(os.path.join(ROOT, 'refs/data/cjkvi-ids/ids.txt'), encoding='utf-8'):
        if l.startswith('#') or '\t' not in l:
            continue
        p = l.rstrip('\n').split('\t')
        if len(p) >= 3:
            ids[p[1]] = re.sub(r'\[[^\]]*\]', '', p[2])
    return ids


def components(chars):
    """{char: set of recognisable components (two levels of IDS)}: same rules as shots/_tong.py"""
    ids = ids_table()

    def comps(ch, depth=0):
        out = set()
        for c in ids.get(ch, ch):
            if c in IDC or c == ch:
                continue
            if c not in DENY and ord(c) > 0x2E7F:
                out.add(c)
            if depth < 1 and c in ids and ids[c] != c:
                out |= comps(c, depth + 1)
        return out
    return {ch: comps(ch) for ch in chars}


def chain_gens(chars, start='通', first='辶', per_jump=3, gens=16, seed=2):
    """True jumps by shared component (shots/_tong.py chain, same rules): [[(src, dst, comp)] per generation]."""
    C = components(chars)
    inv = collections.defaultdict(list)
    for ch in chars:
        for c in C[ch]:
            inv[c].append(ch)
    r = np.random.default_rng(seed)
    lit = {start: None}
    out = [[(start, d, first) for d in inv[first] if d != start]]
    for _, d, c in out[0]:
        lit[d] = c
    frontier = [d for _, d, _ in out[0]]
    for g in range(2, gens + 1):
        new, cap = [], (per_jump if g <= 5 else 99)
        for s in frontier:
            for c in sorted(C[s]):
                if c == lit[s] or len(inv[c]) < 2:
                    continue
                cand = [d for d in inv[c] if d not in lit]
                r.shuffle(cand)
                for d in cand[:cap]:
                    lit[d] = c
                    new.append((s, d, c))
        if not new:
            break
        out.append(new)
        frontier = [d for _, d, _ in new]
    return out, C


class Panel:
    """The carved panel in its own units (1 unit = 1 glyph size; column pitch cp, row pitch rp; 通 at (0, 0)):
    texture pyramids (coverage / id / seed-distance), glyph list, the IDS jump schedule."""

    def __init__(self, cfg):
        from PIL import Image, ImageDraw, ImageFont
        from fontTools.ttLib import TTFont
        P = cfg['panel']
        self.cp, self.rp = P.get('col_pitch', 1.3), P.get('row_pitch', 1.12)
        self.cmin, self.cmax = P.get('cols', [-7, 7])
        self.rmin, self.rmax = P.get('rows', [-9, 9])
        self.G0 = int(P.get('g0', 224))
        self.ref_rect = P.get('ref_rect', [-3.0, -2.5, 3.0, 2.5])
        J = cfg.get('jumps', {})
        rng = np.random.default_rng(P.get('seed', 11))
        cmap = TTFont(os.path.join(ROOT, SEAL_FONT)).getBestCmap()
        pool = list(dict.fromkeys(c for c in open(os.path.join(ROOT, 'design/text/qianziwen.txt'), encoding='utf-8').read()
                                  if '一' <= c <= '鿿' and ord(c) in cmap))
        times = J.get('times', [])
        gens, C = chain_gens(pool, per_jump=J.get('per_jump', 3), gens=len(times))
        caps = J.get('caps', [14, 22, 30, 40, 50, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60])
        cells = [(c, r) for c in range(self.cmin, self.cmax + 1) for r in range(self.rmin, self.rmax + 1)]
        dist = {cr: math.hypot(cr[0] * self.cp, cr[1] * self.rp) + rng.uniform(-0.5, 0.5) for cr in cells}
        order = sorted(cells, key=lambda cr: dist[cr])
        self.edges, chosen, used = [], ['通'], {'通'}
        budget = int(len(cells) * J.get('lit_fraction', 0.8))
        glist = [['通']]
        for gi, g in enumerate(gens):
            sel = [(s, d, c) for (s, d, c) in g if s in used and d not in used]
            sel = sel[:caps[min(gi, len(caps) - 1)]]
            sel = sel[:max(0, budget - len(chosen))]
            for s, d, c in sel:
                used.add(d); chosen.append(d)
            self.edges.append(sel)
            glist.append([d for _, d, _ in sel])
        self.gen_of = {ch: gi for gi, gl in enumerate(glist) for ch in gl}
        # placement: lit chars take the cells nearest the centre in generation order (jittered ring structure)
        free = list(order)
        self.cell_char = {}
        for ch in chosen:
            self.cell_char[free.pop(0)] = ch
        rest = [c for c in pool if c not in used]
        free.sort(key=lambda cr: (-cr[0], cr[1]))            # reading order: right to left, top to bottom
        for cr, ch in zip(free, rest):
            self.cell_char[cr] = ch
        self.char_cell = {ch: cr for cr, ch in self.cell_char.items()}
        self.glyphs = []                                      # id = index + 1
        for (c, r), ch in sorted(self.cell_char.items(), key=lambda kv: kv[0]):
            self.glyphs.append(dict(ch=ch, c=c, r=r, x=c * self.cp, y=r * self.rp, id=len(self.glyphs) + 1,
                                    gen=self.gen_of.get(ch, -1), comps=sorted(C.get(ch, []))))
        self.by_char = {g['ch']: g for g in self.glyphs}
        self.build_texture(Image, ImageDraw, ImageFont, rng, P)
        # light schedule -> per-glyph lit frame; edges -> thread timing
        self.build_schedule(cfg, times)

    # ---------------------------------------------------------------- texture
    def build_texture(self, Image, ImageDraw, ImageFont, rng, P):
        G = self.G0
        self.x0, self.y0 = self.cmin * self.cp - 0.9, self.rmin * self.rp - 0.8
        x1, y1 = self.cmax * self.cp + 0.9, self.rmax * self.rp + 0.8
        TW, TH = int(math.ceil((x1 - self.x0) * G)), int(math.ceil((y1 - self.y0) * G))
        self.TW, self.TH = TW, TH
        cov = np.zeros((TH, TW), np.uint8)
        idm = np.zeros((TH, TW), np.uint16)
        font = ImageFont.truetype(os.path.join(ROOT, SEAL_FONT), int(G * P.get('glyph_size', 0.92)))
        self.glyph_boxes = {}
        # stone roughness in cut floor, attached to the panel
        n = cv2.GaussianBlur(rng.standard_normal((TH // 4, TW // 4)).astype(F32), (0, 0), G / 40)
        n = cv2.resize(n / (n.std() + 1e-6), (TW, TH), interpolation=cv2.INTER_LINEAR)
        n2 = cv2.GaussianBlur(rng.standard_normal((TH // 2, TW // 2)).astype(F32), (0, 0), 2)
        n2 = cv2.resize(n2 / (n2.std() + 1e-6), (TW, TH), interpolation=cv2.INTER_LINEAR)
        for g in self.glyphs:
            cx, cy = (g['x'] - self.x0) * G, (g['y'] - self.y0) * G
            S = int(G * 1.3)
            im = Image.new('L', (S, S), 0)
            ImageDraw.Draw(im).text((S // 2, S // 2), g['ch'], fill=255, font=font, anchor='mm')
            a = np.asarray(im, F32) / 255
            xa, ya = int(cx - S // 2), int(cy - S // 2)
            sl = (slice(ya, ya + S), slice(xa, xa + S))
            roughness = 0.90 + 0.07 * n[sl] + 0.03 * n2[sl]
            erode = 0.05 * np.clip(-n[sl], 0, None)
            a = np.clip(a * roughness - erode, 0, 1)
            cov[sl] = np.maximum(cov[sl], (a * 255).astype(np.uint8))
            hw, hh = int(self.cp * G / 2), int(self.rp * G / 2)
            idm[int(cy) - hh:int(cy) + hh, int(cx) - hw:int(cx) + hw] = g['id']
        self.cov = [cov]
        self.idm = [idm]
        for _ in range(6):
            self.cov.append(cv2.pyrDown(self.cov[-1]))
            self.idm.append(self.idm[-1][::2, ::2].copy())
        self.TW0, self.TH0 = TW, TH

    # ---------------------------------------------------------------- schedule
    def build_schedule(self, cfg, times):
        J = cfg.get('jumps', {})
        st = J.get('stagger', 4)
        self.lit_s = {}                     # char -> (first visible frame, rise frames, is_ember)
        ember_s = J.get('ember_s', 4.2)
        self.lit_s['通'] = (int(math.floor(ember_s)), J.get('ember_rise', 6), True)
        self.thread = []                    # dict(src, dst, s0, gen, comp)
        for gi, sel in enumerate(self.edges):
            t = times[gi]
            n = len(sel)
            stg = st[gi] if isinstance(st, list) else st
            srt = sorted(sel, key=lambda e: math.hypot(self.by_char[e[0]]['x'] - self.by_char[e[1]]['x'],
                                                        self.by_char[e[0]]['y'] - self.by_char[e[1]]['y']))
            for j, (s, d, c) in enumerate(srt):
                s0 = int(round(t + stg * j / max(1, n - 1)))
                self.thread.append(dict(src=s, dst=d, s0=s0, gen=gi + 1, comp=c))
                self.lit_s[d] = (s0 + 2, 4, False)
        # seed point (panel units, relative to the glyph centre) where the light enters each glyph: towards its source
        self.seed = {'通': tuple(cfg.get('jumps', {}).get('ember_seed', [-0.40, 0.40]))}
        for e in self.thread:
            a, b = self.by_char[e['src']], self.by_char[e['dst']]
            v = np.array([a['x'] - b['x'], a['y'] - b['y']])
            v = v / (np.linalg.norm(v) + 1e-9) * 0.42
            self.seed[e['dst']] = (float(v[0]), float(v[1]))
        # rebuild the phase map from seeds
        G, TH, TW = self.G0, self.TH0, self.TW0
        ph = np.full((TH, TW), 255, np.uint8)
        hw, hh = int(self.cp * G / 2), int(self.rp * G / 2)
        yy, xx = np.mgrid[-hh:hh, -hw:hw].astype(F32)
        for g in self.glyphs:
            if g['ch'] not in self.seed:
                continue
            cx, cy = (g['x'] - self.x0) * G, (g['y'] - self.y0) * G
            sx, sy = self.seed[g['ch']]
            d = np.hypot(xx - sx * G, yy - sy * G) / (1.15 * G)
            ph[int(cy) - hh:int(cy) + hh, int(cx) - hw:int(cx) + hw] = np.clip(d * 255, 0, 255).astype(np.uint8)
        self.ph = [ph]
        for _ in range(6):
            self.ph.append(cv2.pyrDown(self.ph[-1]))
        N = len(self.glyphs)
        self.s_lit = np.full(N + 1, 10 ** 6, np.int64)
        self.rise = np.ones(N + 1, F32) * 4
        self.ember = np.zeros(N + 1, bool)
        for ch, (s, r, em) in self.lit_s.items():
            i = self.by_char[ch]['id']
            self.s_lit[i], self.rise[i], self.ember[i] = s, r, em
        self.phi = np.random.default_rng(5).uniform(0, 6.28, N + 1).astype(F32)
        self.centres = np.array([[0, 0]] + [[g['x'], g['y']] for g in self.glyphs], np.float64)

    def log_schedule(self, name):
        out = dict(ember=dict(ch='通', s=self.lit_s['通'][0]), edges=[], n_glyphs=len(self.glyphs), n_lit=len(self.lit_s))
        for e in sorted(self.thread, key=lambda e: (e['s0'], e['gen'])):
            out['edges'].append(dict(s=e['s0'], t=round(T0 + e['s0'] / FPS, 3), gen=e['gen'], src=e['src'], dst=e['dst'], via=e['comp']))
        json.dump(out, open(os.path.join(ROOT, f'work/dflight/jumps_{name}.json'), 'w'), ensure_ascii=False, indent=1)
        per = collections.Counter(e['gen'] for e in self.thread)
        log(f'jumps: ember 通 lights at s{self.lit_s["通"][0]}; {len(self.thread)} jumps, {len(self.lit_s)} glyphs lit of {len(self.glyphs)} on the panel')
        for gi, sel in enumerate(self.edges):
            ss = [e['s0'] for e in self.thread if e['gen'] == gi + 1]
            if ss:
                ex = ' '.join(f'{e[0]}>{e[1]}({e[2]})' for e in sel[:4])
                log(f'  gen{gi + 1}: s{min(ss)}..{max(ss)} (t {T0 + min(ss) / FPS:.2f}), {len(sel)} jumps: {ex} ...')


# ============================================================================================== render helpers
def unit_to_screen(quad, ref_rect, k):
    """3x3 H mapping panel units -> output pixels from the 4 corners (TL, TR, BR, BL) of ref_rect."""
    x0, y0, x1, y1 = ref_rect
    src = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    return cv2.getPerspectiveTransform(src, (np.asarray(quad, np.float64) * k).astype(np.float32))


def proj(H, pts):
    pts = np.asarray(pts, np.float64).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(pts, H.astype(np.float64)).reshape(-1, 2)


def local_px(H, xy):
    """screen px per panel unit at (x, y) units (mean of the two axes)"""
    p = proj(H, [xy, (xy[0] + 1, xy[1]), (xy[0], xy[1] + 1)])
    return 0.5 * (np.linalg.norm(p[1] - p[0]) + np.linalg.norm(p[2] - p[0]))


def shift(a, dx, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT)


class Carver:
    def __init__(self, cfg, panel, W, H):
        self.P, self.W, self.H, self.k = panel, W, H, W / REF_W
        self.cfg = cfg
        P = cfg['panel']
        cut = P.get('cut', {})
        self.cutcol = np.array(cut.get('colour', [0.36, 0.34, 0.34]), F32)       # multiplier at full depth (RGB)
        self.lip = cut.get('lip', 0.38)
        self.fade_px = P.get('fade_px', [6.5, 11.0])               # carve visibility by glyph px at 540p ref
        self.gfade_px = P.get('glow_fade_px', [1.2, 3.0])          # glow visibility
        self.glow = cfg.get('light', {})
        self.hot = np.array(self.glow.get('hot', [1.0, 0.86, 0.52]), F32)
        self.warm = np.array(self.glow.get('warm', [1.0, 0.50, 0.12]), F32)
        self.gold = np.array(self.glow.get('thread', [1.0, 0.78, 0.30]), F32)
        self.thr_rest = self.glow.get('thread_rest', 0.14)
        self.thr_w = self.glow.get('thread_px', 0.9)              # ref px
        self.sag = self.glow.get('sag', 0.16)

    def setup_clean(self, base0, quad0):
        """clean tablet from frame 0 (mist tip painted out by patches) to cover the model's own lights on the panel while the typeset layer lives."""
        C = self.cfg.get('clean')
        self.clean_on = bool(C and C.get('on', True))
        if not self.clean_on:
            return
        self.C = C
        b = cv2.resize(base0, (self.W, self.H), interpolation=cv2.INTER_AREA).copy()
        for (x0, y0, x1, y1, dy) in C.get('patch', []):
            x0, y0, x1, y1, dy = [int(round(v * self.k)) for v in (x0, y0, x1, y1, dy)]
            m = np.zeros(b.shape[:2], F32)
            m[y0:y1, x0:x1] = 1
            m = cv2.GaussianBlur(m, (0, 0), 3 * self.k)[..., None]
            src = np.roll(b, -dy, axis=0)
            b = b * (1 - m) + src * m
        self.base0 = b
        self.H0 = unit_to_screen(quad0, self.P.ref_rect, self.k)

    def clean(self, img, s, H, cvis_centre):
        if not getattr(self, 'clean_on', False) or cvis_centre <= 0.01:
            return img
        P = self.P
        Hrel = H @ np.linalg.inv(self.H0)
        warped = cv2.warpPerspective(self.base0, Hrel, (self.W, self.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        r = P.ref_rect
        inset = self.C.get('inset', 0.06)
        poly = proj(H, [(r[0] + inset, r[1] + inset), (r[2] - inset, r[1] + inset), (r[2] - inset, r[3] - inset), (r[0] + inset, r[3] - inset)])
        m = np.zeros((self.H, self.W), np.uint8)
        cv2.fillConvexPoly(m, np.round(np.clip(poly, -3e5, 3e5)).astype(np.int32), 255)
        inside = m > 0
        if inside.sum() < 30:
            return img
        # colour match (median of tablet interior: robust to the model's sparse lights)
        med_s, med_w = np.median(img[inside], 0), np.median(warped[inside], 0)
        warped = warped * (med_s / np.maximum(med_w, 1e-3))[None, None]
        # where the model's own light is: bright and warm compared with the tablet median
        lum = img.mean(2)
        warm = img[..., 0] - img[..., 2]
        thr = self.C.get('thr', 0.10)
        lit = ((lum - np.median(lum[inside])) > thr) & (warm > np.median(warm[inside]) + 0.04)
        lit = lit.astype(F32) * (m > 0)
        lit = cv2.dilate(lit, np.ones((int(2 * self.k * self.C.get('grow', 4)) | 1,) * 2, np.uint8))
        lit = cv2.GaussianBlur(lit, (0, 0), 1.5 * self.k) * (cv2.GaussianBlur(m.astype(F32) / 255, (0, 0), 1.2 * self.k))
        a = (lit * cvis_centre)[..., None]
        return img * (1 - a) + warped * a

    # ---------------------------------------------------------------- tables
    def tables(self, s, H):
        P = self.P
        N = len(P.glyphs)
        j = s - P.s_lit.astype(np.float64)
        prog = np.where(j >= 0, np.clip((j + 1) / P.rise, 0, 1), 0).astype(F32)
        jj = np.clip(j, 0, None)
        flare = 1 + np.where(P.ember, 1.0, 0.40) * np.exp(-np.clip(j - P.rise, 0, None) / 5.0)
        base = 0.82 + 0.18 * np.exp(-jj / 25.0)
        amp = np.where(P.ember, 0.10, 0.045)
        fl = 1 + amp * (0.6 * np.sin(2 * np.pi * 0.31 * s + P.phi) + 0.4 * np.sin(2 * np.pi * 0.83 * s + 2 * P.phi))
        I = (flare * base * fl).astype(F32)
        I[j < 0] = 0
        # glyph screen size (ref px) for visibility
        c = P.centres
        p0 = proj(H, c)
        px = 0.5 * (np.linalg.norm(proj(H, c + [1, 0]) - p0, axis=1) + np.linalg.norm(proj(H, c + [0, 1]) - p0, axis=1)) / self.k
        px[0] = 0
        cv = smooth(px, *self.fade_px).astype(F32)
        gv = smooth(px, *self.gfade_px).astype(F32)
        cv[0] = gv[0] = 0
        return prog, I, cv, gv, px

    def warp(self, H, lvl, arr, interp):
        P = self.P
        sc = P.G0 / 2 ** lvl
        S = np.array([[sc, 0, -P.x0 * sc], [0, sc, -P.y0 * sc], [0, 0, 1]], np.float64)   # units -> texture px at this level
        M = H @ np.linalg.inv(S)
        return cv2.warpPerspective(arr, M, (self.W, self.H), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    def threads_canvas(self, s, H, px, gv):
        P = self.P
        tv = smooth(px, *self.glow.get('thread_fade_px', [9, 16])).astype(F32)
        SS = 2
        cv_ = np.zeros((self.H * SS, self.W * SS), np.uint8)
        items = []
        for e in P.thread:
            j = s - e['s0']
            if j < 0:
                continue
            a, b = P.by_char[e['src']], P.by_char[e['dst']]
            vis = float(tv[b['id']] * tv[a['id']] ** 0.5)
            if vis <= 0.01:
                continue
            p = min(1.0, (j + 1) / 3.0)
            ease = 1 - (1 - p) ** 2
            if j < 2:
                lev = 1.0
            else:
                lev = self.thr_rest + (1 - self.thr_rest) * math.exp(-(j - 2) / 6.0)
            lev *= vis
            A, B = np.array([a['x'], a['y']]), np.array([b['x'], b['y']])
            ch = B - A
            L = np.linalg.norm(ch) + 1e-9
            nrm = np.array([-ch[1], ch[0]]) / L
            sag = self.sag * L * (1 - p) ** 2 + 0.012 * L
            tr = min(0.48 / L, 0.3)
            t = tr + np.linspace(0, ease, 18) * (1 - 2 * tr)
            pts = A[None] + ch[None] * t[:, None] + nrm[None] * (sag * np.sin(np.pi * t))[:, None] * (1 if e['gen'] % 2 else -1)
            items.append((lev, proj(H, pts) * self.k * SS))
        items.sort(key=lambda it: it[0])
        wpx = max(1, int(round(self.thr_w * self.k * SS)))
        for lev, pp in items:
            cv2.polylines(cv_, [np.round(pp * 16).astype(np.int32)], False, int(255 * min(lev, 1.0)), wpx, cv2.LINE_AA, 4)
        return cv2.resize(cv_, (self.W, self.H), interpolation=cv2.INTER_AREA).astype(F32) / 255

    def draw(self, img, s, quad):
        """img: HxWx3 float RGB 0..1, modified (returned)."""
        P, W, Hh = self.P, self.W, self.H
        H = unit_to_screen(quad, P.ref_rect, self.k)
        cen = np.array([(P.ref_rect[0] + P.ref_rect[2]) / 2, (P.ref_rect[1] + P.ref_rect[3]) / 2])
        su = local_px(H, cen)
        lvl = int(np.clip(math.floor(math.log2(max(P.G0 / max(su, 1e-3), 1.0))), 0, 6))
        prog, I, cvis, gvis, px = self.tables(s, H)
        img = self.clean(img, s, H, float(cvis[P.by_char['通']['id']]))
        if cvis.max() <= 0 and gvis.max() <= 0:
            return img
        cov = self.warp(H, lvl, P.cov[lvl], cv2.INTER_LINEAR).astype(F32) / 255
        idw = self.warp(H, lvl, P.idm[lvl], cv2.INTER_NEAREST)
        if not idw.any():
            return img
        A = cov * cvis[idw]
        # ---- incised cut: multiply into the plate; shadow wall upper-left, light lip lower-right
        d = float(np.clip(0.03 * su, 0.8, 3.2) * 1.0)
        As = cv2.GaussianBlur(A, (0, 0), max(0.45, 0.005 * su))
        sh = np.clip(As - shift(As, d, d), 0, 1)
        lit = np.clip(shift(As, d, d) - As, 0, 1)
        mul = 1 - As[..., None] * (1 - self.cutcol)[None, None] - 0.30 * sh[..., None]
        out = img * np.clip(mul, 0, 1)
        out = out * (1 + self.lip * lit[..., None]) + 0.06 * lit[..., None]
        # ---- light inside the cut
        on = (prog > 0)
        if on.any():
            phw = self.warp(H, lvl, P.ph[lvl], cv2.INTER_LINEAR).astype(F32) / 255
            pr = prog[idw]
            w = 0.35
            lp = np.clip((pr * (1 + w) - phw) / w, 0, 1)
            lp = lp * lp * (3 - 2 * lp)
            Iw = I[idw]
            gw = gvis[idw]
            E = As * lp * gw
            core = cv2.GaussianBlur(E, (0, 0), max(0.7, 0.05 * su))
            hotk = np.clip(core * 1.6, 0, 1) ** 1.5
            col = self.warm[None, None] + (self.hot - self.warm)[None, None] * hotk[..., None]
            inner = smooth(cv2.GaussianBlur(As, (0, 0), max(0.8, 0.045 * su)), 0.30, 0.85)      # stroke core: the wall stays darker
            e1 = np.clip(E * np.minimum(Iw, 1.0) * (0.55 + 0.45 * inner), 0, 1)[..., None]
            out = out * (1 - e1) + col * e1
            ex = (E * np.clip(Iw - 1.0, 0, 1.2))[..., None]
            out = out + ex * self.hot[None, None] * 0.7                 # kindle flare above steady
            Lrad = E * Iw
            h1 = cv2.GaussianBlur(Lrad, (0, 0), max(0.8, 0.07 * su))     # tight halo hugging the strokes
            h2 = cv2.GaussianBlur(Lrad, (0, 0), max(2.0, 0.35 * su))     # faint wide warmth
            halo = (0.55 * h1 + 0.16 * h2)[..., None]
            out = 1 - (1 - np.clip(out, 0, 1)) * (1 - np.clip(halo * self.warm[None, None] * 1.2, 0, 1))
            out = out * (1 - 0.20 * h2[..., None] * (1 - self.warm)[None, None])      # warm multiply helps on pale stone
            # ---- threads
            T = self.threads_canvas(s, H, px, gvis)
            if T.max() > 0.003:
                Tg = cv2.GaussianBlur(T, (0, 0), max(0.8, 1.0 * self.k))
                out = out * (1 - T[..., None]) + self.gold[None, None] * T[..., None]
                out = 1 - (1 - out) * (1 - np.clip(Tg[..., None] * 0.5, 0, 1) * self.gold[None, None])
        return np.clip(out, 0, 1)


# ============================================================================================== 5 frontier
class Frontier:
    def __init__(self, cfg, W, H):
        F = cfg.get('frontier', {})
        self.on = F.get('on', False)
        self.W, self.H, self.k = W, H, W / REF_W
        if not self.on:
            return
        d = np.array(F.get('dir', [1.0, -0.25]), F32)
        self.d = d / np.linalg.norm(d)                 # points into the dark country
        self.p0, self.step = F.get('p0', -0.2), F.get('step', 0.09)
        self.beats = F.get('beats', [21.8, 32.3, 42.9, 53.5, 64.2, 74.7, 85.3, 96.2, 106.5, 117.3, 128.1, 138.5, 149.2])
        self.wob = F.get('wobble', 0.05)
        self.soft = F.get('soft', 0.10)
        self.dark = F.get('dark', 0.55)
        self.lift = F.get('lift', 0.55)
        self.arcs = F.get('arcs_per_beat', 4)
        self.s_end = F.get('s_end', 203)
        self.radial = F.get('mode') == 'radial'
        self.env = F.get('env', [56, 64, 106, 114])           # fade in (s0,s1) / out (s2,s3) of the whole layer
        self.edge_g = F.get('edge', 0.35)
        self.origin = np.array(F.get('origin', [230, 300]), F32) * self.k
        self.ang = F.get('arc_angles', [-80, 20])
        yy, xx = np.mgrid[0:H, 0:W].astype(F32)
        self.u = (xx / W * self.d[0] * W / H + yy / H * self.d[1]) / (abs(self.d[0]) * W / H + abs(self.d[1]) + 1e-9)
        self.u = (self.u - self.u.min()) / (self.u.max() - self.u.min())
        if self.radial:
            diag = math.hypot(W, H)
            self.u = np.hypot(xx - self.origin[0], (yy - self.origin[1]) * 1.15) / diag
        rng = np.random.default_rng(3)
        n = cv2.GaussianBlur(rng.standard_normal((H // 4, W // 4)).astype(F32), (0, 0), 14)
        self.n = cv2.resize(n / n.std(), (W, H), interpolation=cv2.INTER_LINEAR)
        self.rng = np.random.default_rng(9)
        self.arc_list = []                              # (s0, P0, P1, bulge)
        for b in self.beats:
            for q in range(self.arcs):
                self.arc_list.append((b + q * 1.5, self.rng.uniform(-1, 1), self.rng.uniform(0.10, 0.22), self.rng.uniform(0.25, 0.5)))

    def pos(self, s):
        return self.p0 + self.step * sum(float(smooth(s, b, b + 5)) for b in self.beats)

    def apply(self, img, s):
        if not self.on or s > self.s_end:
            return img
        e = self.pos(s)
        en = float(smooth(s, self.env[0], self.env[1]) * (1 - smooth(s, self.env[2], self.env[3]))) if self.radial else 1.0
        if en <= 0.001:
            return img
        dd = (self.u + self.wob * self.n * 0.3 - e) / self.soft            # >0 dark country ahead, <0 lit behind
        ahead = smooth(dd, -0.2, 1.0)
        behind = 1 - smooth(dd, -1.5, 0.2)
        lum = img.mean(2, keepdims=True)
        dark = img * (1 - en * self.dark * ahead[..., None] * (1 - np.array([0.62, 0.70, 0.95], F32)[None, None]))
        lift = dark + (lum ** 2) * behind[..., None] * (self.lift * en) * np.array([0.55, 0.30, 0.05], F32)[None, None]
        edge = np.exp(-(dd / 0.45) ** 2)[..., None]
        out = 1 - (1 - np.clip(lift, 0, 1)) * (1 - np.clip(edge * self.edge_g * en, 0, 1) * np.array([1.0, 0.72, 0.28], F32)[None, None])
        # fine arcing threads at the edge
        cv_ = np.zeros((self.H * 2, self.W * 2), np.uint8)
        nrm = np.array([-self.d[1], self.d[0]])
        for (s0, lat, ln, bu) in self.arc_list:
            j = s - s0
            if j < 0 or j > 14:
                continue
            ee = self.pos(s0)
            if self.radial:
                th = math.radians(self.ang[0] + (self.ang[1] - self.ang[0]) * (lat * 0.5 + 0.5))
                dv = np.array([math.cos(th), math.sin(th)])
                c = (self.origin + dv * ee * math.hypot(self.W, self.H) - dv * 0.02 * self.W) / [self.W, self.H]
                A = c * [self.W, self.H]
                B = A + dv * ln * 0.8 * self.W
                ch = B - A
                nn = np.array([-ch[1], ch[0]]) / (np.linalg.norm(ch) + 1e-9)
                if nn[1] > 0:
                    nn = -nn
                p = min(1.0, (j + 1) / 3.0)
                t = np.linspace(0, 1 - (1 - p) ** 2, 16)
                pts = A[None] + ch[None] * t[:, None] + nn[None] * (bu * np.linalg.norm(ch) * np.sin(np.pi * t))[:, None]
                lev = (1.0 if j < 2 else 0.2 + 0.8 * math.exp(-(j - 2) / 4.0)) * en
                cv2.polylines(cv_, [np.round(pts * 2 * 16).astype(np.int32)], False, int(255 * lev), max(1, int(round(self.k * 2.0))), cv2.LINE_AA, 4)
                continue
            # edge point in screen units (0..1): solve u = ee along d from centre, lateral by nrm
            c = np.array([0.5, 0.5]) + self.d * (ee - 0.5) * 0.9 + nrm * lat * 0.45
            c = c - self.d * 0.02
            A = c * [self.W, self.H]
            B = (c + self.d * ln * 0.8) * [self.W, self.H]
            ch = B - A
            nn = np.array([-ch[1], ch[0]]) / (np.linalg.norm(ch) + 1e-9)
            if nn[1] > 0:
                nn = -nn
            p = min(1.0, (j + 1) / 3.0)
            t = np.linspace(0, 1 - (1 - p) ** 2, 16)
            pts = A[None] + ch[None] * t[:, None] + nn[None] * (bu * np.linalg.norm(ch) * np.sin(np.pi * t))[:, None]
            lev = 1.0 if j < 2 else 0.2 + 0.8 * math.exp(-(j - 2) / 4.0)
            cv2.polylines(cv_, [np.round(pts * 2 * 16).astype(np.int32)], False, int(255 * lev), max(1, int(round(self.k * 2.2))), cv2.LINE_AA, 4)
        T = cv2.resize(cv_, (self.W, self.H), interpolation=cv2.INTER_AREA).astype(F32) / 255
        if T.max() > 0.003:
            out = out * (1 - T[..., None]) + np.array([1.0, 0.78, 0.30], F32)[None, None] * T[..., None]
        return np.clip(out, 0, 1)


# ============================================================================================== 6 inscription / landing
class Inscriptions:
    def __init__(self, cfg, W, H, base_dir):
        from tools.ink.inscription import inscription
        from tools.ink.paper import Paper
        self.W, self.H, self.items = W, H, []
        P = Paper(W, H, 'new', seed=1988)
        k = W / 1920.0
        for it in cfg.get('inscription', [dict(text='一通百通', s0=0, s1=32), dict(key='D5', s0=33, s1=133)]):
            box = tuple(v * k for v in it.get('box', (1650, 110, 210, 720)))
            kw = dict(box=box, paper=P, seal=it.get('seal', '悟空'))
            lt = inscription((W, H), key=it.get('key'), text=it.get('text'), **kw)
            dk = inscription((W, H), key=it.get('key'), text=it.get('text'), ground='dark', **kw) if it.get('ground', 'auto') != 'paper' else None
            self.items.append(dict(it=it, light=lt, dark=dk, box=lt.bbox))
        self.base_dir = base_dir

    def draw(self, img, s):
        for r in self.items:
            if not (r['it'].get('s0', 0) <= s <= r['it'].get('s1', NF)):
                continue
            x0, y0, x1, y1 = [int(v) for v in r['box']]
            patch = img[max(y0, 0):y1, max(x0, 0):x1]
            lum = float(patch.mean()) if patch.size else 1.0
            wl = 1.0 if r['dark'] is None else float(smooth(lum, 0.52, 0.66))
            if r['it'].get('ground') == 'dark':
                wl = 0.0
            if wl >= 0.999:
                r['light'].draw(img)
            elif wl <= 0.001 and r['dark'] is not None:
                r['dark'].draw(img)
            else:
                a, b = img.copy(), img.copy()
                r['light'].draw(a)
                r['dark'].draw(b)
                img[:] = a * wl + b * (1 - wl)
        return img


class Landing:
    def __init__(self, cfg, W, H):
        L = cfg.get('landing', {})
        self.on = bool(L)
        self.W, self.H, self.k = W, H, W / REF_W
        if not self.on:
            return
        self.s = L.get('s', 170.6)
        self.f0 = int(math.floor(self.s))                  # the frame that CONTAINS the audio event (sync rule)
        self.pts = L.get('pts') or [[0, *L.get('pt', [480, 400])]]
        self.r = L.get('radius', 70)
        self.gain = L.get('gain', 0.95)
        self.col = np.array(L.get('colour', [1.0, 0.76, 0.40]), F32)
        self.decay = L.get('decay_frames', 10)
        self.pulse = L.get('pulse')
        self.seal = None
        S = L.get('seal')
        if S and S.get('on', False):
            from tools.ink.seal import seal
            self.seal = seal(S.get('ch', '倉'), SYLLABLE_FONT, int(S.get('px', 52) * self.k), 'bai', wear=0.28, seed=7, weight=0.016, stretch=1.12)
            self.seal_pt = S.get('pt', [700, 200])
            self.seal_over = S.get('overshoot', 0.12)

    def point(self, s):
        p = np.array(self.pts, float)
        return np.array([np.interp(s, p[:, 0], p[:, 1]), np.interp(s, p[:, 0], p[:, 2])])

    def level(self, s):
        j = s - self.f0
        if j < 0:
            return 0.0
        if j < 2:
            return 0.5 + 0.5 * j                         # 2-frame rise
        return math.exp(-(j - 1) / (self.decay / 3.0))   # ~10 frame decay to ~5 %

    def pulse_draw(self, img, s):
        """the landing light runs down the lit gold texture of the pillars: a warm lift on gold pixels below the feet, front moving downward."""
        P = self.pulse
        j = s - self.f0
        n = P.get('frames', 12)
        if j < 0 or j > n + 10:
            return img
        c = self.point(s) * self.k
        span = P.get('span', 330) * self.k
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(F32)
        front = c[1] + span * min(j / float(n), 1.0) ** 0.85
        band = np.exp(-((yy - front) / (0.10 * span + 4)) ** 2)
        trail = np.exp(-np.clip(front - yy, 0, None) / (0.45 * span)) * (yy > c[1]) * (yy < front)
        fall = max(0.0, 1.0 - max(j - n, 0) / 10.0)
        prof = (band * 0.9 + trail * 0.45) * fall
        lat = np.exp(-((xx - c[0]) / (P.get('x_half', 260) * self.k)) ** 2)
        lum = img.mean(2)
        warm = np.clip((img[..., 0] - img[..., 2]) / 0.25, 0, 1) * smooth(lum, 0.28, 0.55)
        warm = cv2.GaussianBlur(warm, (0, 0), 1.2 * self.k)
        g = (prof * lat * (0.25 + 0.75 * warm) * P.get('gain', 0.55))[..., None]
        add = g * np.array([1.0, 0.62, 0.22], F32)[None, None]
        return np.clip(1 - (1 - img) * (1 - np.clip(add, 0, 1)), 0, 1)

    def draw(self, img, s):
        if not self.on:
            return img
        lv = self.level(s)
        if lv > 0.01:
            c = self.point(s) * self.k
            r = self.r * self.k * (0.85 + 0.3 * (1 - lv))
            yy, xx = np.mgrid[0:self.H, 0:self.W].astype(F32)
            d2 = ((xx - c[0]) ** 2 + (yy - c[1]) ** 2)
            g = np.exp(-d2 / (2 * (r * 0.6) ** 2)) * 0.7 + np.exp(-d2 / (2 * (r * 0.14) ** 2)) * 0.45
            g = (g * lv * self.gain)[..., None]
            img = 1 - (1 - img) * (1 - np.clip(g * self.col[None, None], 0, 1))
            img = img + g * 0.12 * np.array([1, 0.9, 0.7], F32)[None, None] * (g > 0.4)
        if self.pulse:
            img = self.pulse_draw(img, s)
        if self.seal is not None:
            from tools.ink.seal import strike
            t = T0 + s / FPS
            im = np.ascontiguousarray(np.clip(img, 0, 1), F32)
            strike(im, self.seal, t, self.s / FPS + T0, np.array(self.seal_pt) * self.k, overshoot=self.seal_over)
            img = im
        return np.clip(img, 0, 1)


def push(im, s, P):
    """gentle push-in on the hold: scale 1 -> 1+k about `pt` (ref units) between s0 and s1 (smoothstep) so the landed 亮相 is not frozen."""
    if not P or s < P['s0']:
        return im
    u = float(smooth((s - P['s0']) / float(P['s1'] - P['s0']), 0, 1))
    k = 1 + P['k'] * u
    H, W = im.shape[:2]
    cx, cy = P.get('pt', [480, 270])[0] * W / REF_W, P.get('pt', [480, 270])[1] * H / REF_H
    M = np.float32([[k, 0, cx * (1 - k)], [0, k, cy * (1 - k)]])
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


# ============================================================================================== outputs
def ffw(path, W, H):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24',
                             '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-an', path],
                            stdin=subprocess.PIPE)


def label(im, text, scale=0.5):
    cv2.putText(im, text, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(im, text, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, scale, (60, 60, 255), 1, cv2.LINE_AA)


def sheets(frames, name, dense=(0, 100)):
    os.makedirs(os.path.join(ROOT, 'work/review/comp_v4'), exist_ok=True)
    idx = [int(round(v)) for v in np.linspace(0, NF - 1, 16)]
    tiles = []
    for s in idx:
        t = cv2.resize(frames[s], (480, 270), interpolation=cv2.INTER_AREA)
        label(t, f's{s}  t {T0 + s / FPS:.3f}')
        tiles.append(t)
    g = np.vstack([np.hstack(tiles[i * 4:i * 4 + 4]) for i in range(4)])
    cv2.imwrite(os.path.join(ROOT, f'work/review/comp_v4/DFLIGHT_{name}.jpg'), cv2.cvtColor(g, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    idx = list(range(dense[0], dense[1] + 1, 2))
    tiles = []
    for s in idx:
        t = cv2.resize(frames[s], (320, 180), interpolation=cv2.INTER_AREA)
        label(t, f's{s}', 0.45)
        tiles.append(t)
    while len(tiles) % 6:
        tiles.append(np.zeros_like(tiles[0]))
    g = np.vstack([np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)])
    cv2.imwrite(os.path.join(ROOT, f'work/review/comp_v4/DFLIGHT_{name}_dense.jpg'), cv2.cvtColor(g, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])


def cut_check(last, cfg):
    cap = cv2.VideoCapture(os.path.join(ROOT, cfg.get('d7', 'media/comp/D7.mp4')))
    ok, f = cap.read()
    if not ok:
        return
    a = cv2.cvtColor(cv2.resize(last, (960, 540), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR)
    b = cv2.resize(f, (960, 540), interpolation=cv2.INTER_AREA)
    label(a, 'DFLIGHT last frame (s203)')
    label(b, 'D7 first frame')
    cv2.imwrite(os.path.join(ROOT, 'work/dflight/cut_to_D7.jpg'), np.hstack([a, b]), [cv2.IMWRITE_JPEG_QUALITY, 92])
    d = float(np.abs(a.astype(F32) - b.astype(F32)).mean())
    log(f'cut to D7: mean abs diff {d:.1f}/255; mean colour last {a.reshape(-1, 3).mean(0)[::-1].round(0)}, D7 first {b.reshape(-1, 3).mean(0)[::-1].round(0)}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--w', type=int, default=960)
    ap.add_argument('--h', type=int, default=540)
    ap.add_argument('--frames', default=None, help='comma list: render only these s and write work/dflight/<name>/dbg_<s>.png')
    ap.add_argument('--name', default=None)
    ap.add_argument('--no-encode', action='store_true')
    ap.add_argument('--no-track', action='store_true')
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    name = a.name or cfg['name']
    W, H = a.w, a.h
    os.makedirs(os.path.join(ROOT, 'work/dflight', name), exist_ok=True)
    base = stage_base(cfg, W, H, name)
    quads, mode = track_panel(cfg, base, name, W, H, not a.no_track)
    panel = Panel(cfg)
    panel.log_schedule(name)
    carver = Carver(cfg, panel, W, H)
    carver.setup_clean(cv2.cvtColor(cv2.imread(f'{base}/b0000.png'), cv2.COLOR_BGR2RGB).astype(F32) / 255, quads[0])
    front = Frontier(cfg, W, H)
    ins = Inscriptions(cfg, W, H, base)
    land = Landing(cfg, W, H)
    sel = [int(x) for x in a.frames.split(',')] if a.frames else range(NF)
    frames = {}
    for s in sel:
        im = cv2.cvtColor(cv2.imread(f'{base}/b{s:04d}.png'), cv2.COLOR_BGR2RGB).astype(F32) / 255
        im = push(im, s, cfg.get('push'))
        im = front.apply(im, s)
        im = carver.draw(im, s, quads[s])
        im = ins.draw(im, s)
        im = land.draw(im, s)
        frames[s] = (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)
        if a.frames:
            cv2.imwrite(os.path.join(ROOT, f'work/dflight/{name}/dbg_{s:03d}.png'), cv2.cvtColor(frames[s], cv2.COLOR_RGB2BGR))
        elif s % 20 == 0:
            print('frame', s, flush=True)
    if a.frames or a.no_encode:
        return
    out = os.path.join(ROOT, 'media/comp/_cand')
    parts = [('', 0, NF), ('_D4', 0, 33), ('_D5', 33, 134), ('_D6', 134, NF)]
    for suf, s0, s1 in parts:
        p = ffw(f'{out}/DFLIGHT_{name}{suf}.mp4', W, H)
        for s in range(s0, s1):
            p.stdin.write(frames[s].tobytes())
        p.stdin.close()
        p.wait()
    sheets(frames, name, tuple(cfg.get('dense', (0, 100))))
    cut_check(frames[NF - 1], cfg)
    log(f'wrote media/comp/_cand/DFLIGHT_{name}.mp4 (+ _D4 33 f, _D5 101 f, _D6 70 f), sheet work/review/comp_v4/DFLIGHT_{name}.jpg')
    open(os.path.join(ROOT, f'work/dflight/{name}/run.log'), 'w').write('\n'.join(LOG))


if __name__ == '__main__':
    main()

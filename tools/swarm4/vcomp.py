#!/usr/bin/env python
"""vcomp: video-model take(s) -> the final 176-frame swarm shot (F4F5F6a), driven by a JSON config.

  PY tools/swarm4/vcomp.py work/swarm/C/comp_C.json [--w 960 --h 540] [--stage base|all] [--frames 0,10,20]
                                                    [--no-encode] [--sheet-only] [--cand C]

Stages
  base     retime: output frame s -> float virtual source position v(s) (monotone PCHIP through the config's map points),
           sources joined on one virtual axis (clip k covers [v0, v0 + n - 1]); fractional positions are interpolated with
           DIS optical flow (computed once at 480x270 so the result is resolution independent; warp at output size).
           Cached in work/swarm/<cand>/base_<w>x<h>_<hash>/b%04d.png
  overlay  beat wave (lantern flare ring), seal-beat sector darkening + tiny 讫 seals, 真 seals and name slips (LK-tracked
           to the stone), light paper grain. Everything is authored in 960x540 units and scaled by W/960; tracking and blob
           detection run on a 960x540 copy of the base frame, so --w 1920 --h 1080 is a pure re-render.
  encode   media/comp/F4F5F6a_<cand>.mp4 (176 f, 24 fps, no audio), sheet + strips in work/review/comp_v4/.
Config keys: see work/swarm/C/comp_C.json.
"""
import argparse, glob, hashlib, json, os, subprocess, sys
import numpy as np
import cv2
from scipy.interpolate import PchipInterpolator

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
T0, FPS = 112.75, 24.0
FLOW_W, FLOW_H = 480, 270
REF_W, REF_H = 960, 540
F32 = np.float32


def smooth(x, a, b):
    t = np.clip((x - a) / max(b - a, 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------------------------ retime / base
class Source:
    def __init__(self, spec, W, H):
        self.name, self.v0 = spec['name'], float(spec['v0'])
        cap = cv2.VideoCapture(os.path.join(ROOT, spec['file']))
        self.fr, self.small = [], []
        while True:
            ok, f = cap.read()
            if not ok:
                break
            self.fr.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA) if f.shape[1] != W else f)
            self.small.append(cv2.cvtColor(cv2.resize(f, (FLOW_W, FLOW_H), interpolation=cv2.INTER_AREA),
                                           cv2.COLOR_BGR2GRAY))
        self.n = len(self.fr)
        self.W, self.H = W, H
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        self.cache = {}
        yy, xx = np.mgrid[0:H, 0:W].astype(F32)
        self.xx, self.yy = xx, yy

    def flows(self, i):
        if i not in self.cache:
            a, b = self.small[i], self.small[i + 1]
            f01 = self.dis.calc(a, b, None)
            f10 = self.dis.calc(b, a, None)
            up = lambda f: np.dstack([cv2.resize(f[..., 0], (self.W, self.H)) * (self.W / FLOW_W),
                                      cv2.resize(f[..., 1], (self.W, self.H)) * (self.H / FLOW_H)]).astype(F32)
            F01, F10 = up(f01), up(f10)
            # forward-backward consistency (flow of 1 sampled where 0 lands)
            m = cv2.remap(F10, self.xx + F01[..., 0], self.yy + F01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            err = np.hypot(F01[..., 0] + m[..., 0], F01[..., 1] + m[..., 1])
            err = cv2.GaussianBlur(err, (0, 0), 2.0)
            self.cache[i] = (F01, F10, np.clip(err / (3.0 * self.W / FLOW_W), 0, 1))
            if len(self.cache) > 12:
                self.cache.pop(next(iter(self.cache)))
        return self.cache[i]

    def at(self, u):
        u = float(np.clip(u, 0, self.n - 1))
        i = int(np.floor(u))
        t = u - i
        if t < 0.03 or i >= self.n - 1:
            return self.fr[min(i, self.n - 1)]
        if t > 0.97:
            return self.fr[i + 1]
        F01, F10, bad = self.flows(i)
        a, b = self.fr[i], self.fr[i + 1]
        aw = cv2.remap(a, self.xx - t * F01[..., 0], self.yy - t * F01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        bw = cv2.remap(b, self.xx - (1 - t) * F10[..., 0], self.yy - (1 - t) * F10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        warped = aw.astype(F32) * (1 - t) + bw.astype(F32) * t
        plain = a.astype(F32) * (1 - t) + b.astype(F32) * t
        m = bad[..., None]
        return np.clip(warped * (1 - m) + plain * m, 0, 255).astype(np.uint8)


class Retimer:
    def __init__(self, cfg, W, H):
        self.srcs = [Source(s, W, H) for s in cfg['sources']]
        pts = np.array(cfg['map'], float)
        self.spline = PchipInterpolator(pts[:, 0], pts[:, 1])
        self.s_end = pts[-1, 0]

    def v(self, s):
        return float(self.spline(np.clip(s, 0, self.s_end)))

    def frame(self, s):
        v = self.v(s)
        src = self.srcs[0]
        for sc in self.srcs:
            if v >= sc.v0 - 1e-6:
                src = sc
        return src.at(v - src.v0)


def base_dir(cfg, W, H):
    key = json.dumps({'sources': cfg['sources'], 'map': cfg['map'], 'n': cfg.get('nframes', 176), 'w': W, 'h': H}, sort_keys=True)
    h = hashlib.md5(key.encode()).hexdigest()[:8]
    return os.path.join(ROOT, 'work/swarm', cfg['cand'], f'base_{W}x{H}_{h}')


def stage_base(cfg, W, H, force=False):
    d = base_dir(cfg, W, H)
    n = cfg.get('nframes', 176)
    if not force and len(glob.glob(d + '/b*.png')) == n:
        return d
    os.makedirs(d, exist_ok=True)
    rt = Retimer(cfg, W, H)
    for s in range(n):
        cv2.imwrite(f'{d}/b{s:04d}.png', rt.frame(s))
    json.dump({'v': [rt.v(s) for s in range(n)]}, open(d + '/v.json', 'w'))
    return d


# ------------------------------------------------------------------------------------------------ tracking
def track_item(grays, s_ref, p, r, s_lo, s_hi):
    """LK feature tracking in a patch of radius r (REF px) around p at frame s_ref, both directions.
    -> {s: (x, y, scale, rot)} accumulated similarity relative to s_ref (p0 -> position/scale/rotation)."""
    out = {s_ref: (float(p[0]), float(p[1]), 1.0, 0.0)}
    for direction in (1, -1):
        c = np.array(p, F32)
        sc, rot = 1.0, 0.0
        s = s_ref
        while 0 <= s + direction < len(grays) and (s_lo <= s + direction <= s_hi):
            a, b = grays[s], grays[s + direction]
            m = np.zeros(a.shape, np.uint8)
            cv2.circle(m, (int(c[0]), int(c[1])), int(r * sc), 255, -1)
            pts = cv2.goodFeaturesToTrack(a, 60, 0.005, 3, mask=m, blockSize=5)
            M = None
            if pts is not None and len(pts) >= 4:
                nxt, st, _ = cv2.calcOpticalFlowPyrLK(a, b, pts, None, winSize=(21, 21), maxLevel=3)
                back, st2, _ = cv2.calcOpticalFlowPyrLK(b, a, nxt, None, winSize=(21, 21), maxLevel=3)
                ok = (st[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm(back - pts, axis=2)[:, 0] < 1.0)
                if ok.sum() >= 4:
                    M, inl = cv2.estimateAffinePartial2D(pts[ok], nxt[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
            if M is not None:
                c = (M[:, :2] @ c + M[:, 2]).astype(F32)
                k = float(np.hypot(M[0, 0], M[1, 0]))
                sc *= k
                rot += float(np.arctan2(M[1, 0], M[0, 0]))
            s += direction
            out[s] = (float(c[0]), float(c[1]), sc, rot)
    return out


# ------------------------------------------------------------------------------------------------ lantern mask
def lantern_mask(img8):
    """Soft 0..1 mask of lantern-like pixels: bright, warm (orange-yellow), brighter than their surround."""
    hsv = cv2.cvtColor(img8, cv2.COLOR_BGR2HSV).astype(F32)
    h, sat, v = hsv[..., 0], hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    sig = max(2.0, 9.0 * img8.shape[1] / REF_W)
    local = v - cv2.GaussianBlur(v, (0, 0), sig)
    m = smooth(v, 0.34, 0.62) * smooth(sat, 0.30, 0.55) * smooth(h, 4, 10) * (1 - smooth(h, 30, 38)) * smooth(local, 0.025, 0.12)
    return m.astype(F32)


# ------------------------------------------------------------------------------------------------ small art
def tiny_seal(ch, px_ref, k):
    """White-lettered (白文) cinnabar seal, rendered big and reduced: RGBA float, px_ref*k px."""
    from shots.swarm_lib import done_seal
    big = done_seal(1.0, ch, 160, seed=7)
    n = max(3, int(round(px_ref * k)))
    return cv2.resize(big[..., [2, 1, 0, 3]], (n, n), interpolation=cv2.INTER_AREA)       # RGB -> BGR


def zhen_seal(px_ref, k, style='bai', seed=3):
    """真 seal, tested on the lit rock: 白文 with wear ~0 and no weight is the most legible (朱文 reads as thin red on dark)."""
    from tools.ink.seal import seal, has_glyph
    from shots.swarm_lib import SEALF
    ch = '真' if has_glyph('真', SEALF) else '眞'
    big = seal(ch, SEALF, 240, style, wear=0.05, seed=seed, weight=0.0)
    n = max(8, int(round(px_ref * k)))
    return cv2.resize(big[..., [2, 1, 0, 3]], (n, n), interpolation=cv2.INTER_AREA)


def slip_art(ch, glyph_px_ref, k, seed=1):
    """Vertical name slip (榜题): pale paper strip ~1.4 x 2.6 glyphs, ink border, one brush glyph. RGBA, BGR order."""
    from tools.ink.seal import glyph
    scale = 5
    gp = int(glyph_px_ref * k * scale)
    g = glyph(ch, 'refs/fonts/mashanzheng/MaShanZheng-Regular.ttf', gp)
    gh, gw = g.shape
    w, h = int(gp * 1.45), int(gp * 2.6)
    r = np.random.RandomState(seed)
    paper = np.empty((h, w, 3), F32)
    paper[:] = np.array([0.56, 0.70, 0.80], F32)       # BGR: warm pale paper, dimmed for night
    paper += (cv2.GaussianBlur(r.randn(h, w).astype(F32), (0, 0), gp * 0.08) * 0.10)[..., None]
    ink = np.zeros((h, w), F32)
    y0 = int(h * 0.30 - gh / 2)
    ink[max(0, y0):max(0, y0) + gh, (w - gw) // 2:(w - gw) // 2 + gw] = g[:h - max(0, y0)]
    bw = max(2, int(gp * 0.05))
    cv2.rectangle(ink, (bw, bw), (w - 1 - bw, h - 1 - bw), 0.9, bw)
    cv2.line(ink, (w // 2, int(h * 0.58)), (w // 2, int(h * 0.92)), 0.35, max(1, bw // 2))   # a faint ruled column below the glyph
    col = paper * (1 - ink[..., None]) + np.array([0.08, 0.07, 0.07], F32) * ink[..., None]
    rgba = np.dstack([np.clip(col, 0, 1), np.ones((h, w), F32)])
    return cv2.resize(rgba, (max(4, int(round(w / scale))), max(6, int(round(h / scale)))), interpolation=cv2.INTER_AREA)


def blit(img, art, cx, cy, alpha=1.0, scale=1.0, rot=0.0, tint=None):
    """Alpha-composite RGBA float `art` (BGR) onto img float32 at centre (cx, cy) with scale/rotation (radians)."""
    if alpha <= 0.001:
        return
    h, w = art.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -np.degrees(rot), scale)
    ow, oh = int(np.ceil((abs(w * M[0, 0]) + abs(h * M[0, 1])) + 4)), int(np.ceil((abs(w * M[1, 0]) + abs(h * M[1, 1])) + 4))
    M[0, 2] += ow / 2 - w / 2
    M[1, 2] += oh / 2 - h / 2
    A = cv2.warpAffine(art, M, (ow, oh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    x0, y0 = int(round(cx - ow / 2)), int(round(cy - oh / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(img.shape[1], x0 + ow), min(img.shape[0], y0 + oh)
    if X1 <= X0 or Y1 <= Y0:
        return
    sub = A[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    a = sub[..., 3:4] * alpha
    rgb = sub[..., :3] if tint is None else sub[..., :3] * tint
    img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1] * (1 - a) + rgb * a


# ------------------------------------------------------------------------------------------------ overlay
def interp_keys(keys, s):
    k = np.array(keys, float)
    return np.array([np.interp(s, k[:, 0], k[:, 1]), np.interp(s, k[:, 0], k[:, 2])])


class Overlay:
    def __init__(self, cfg, W, H, nbase):
        self.cfg, self.W, self.H = cfg, W, H
        self.k = W / REF_W
        self.n = nbase
        self.beats = [float(b) for b in cfg.get('beats_s', [])]
        self.seal_beats = [float(b) for b in cfg.get('seal_beats_s', [])]
        yy, xx = np.mgrid[0:H, 0:W].astype(F32)
        self.xx, self.yy = xx / self.k, yy / self.k          # REF coordinates
        self.tracks = {}
        self.flashes = []                                    # active 讫 flashes: dict(x, y, age, sec)
        self.seal_cache = {}
        self.log = []

    # -- tracking on a 960x540 copy of the base frames
    def prepare_tracks(self, base_frames_ref_gray):
        cfg = self.cfg
        for i, z in enumerate(cfg.get('zhen', [])):
            self.tracks[('z', i)] = track_item(base_frames_ref_gray, int(round(z['s'])), z['p'], z.get('patch', 36),
                                               int(round(z['s'])), len(base_frames_ref_gray) - 1)
        for i, sl in enumerate(cfg.get('slips', [])):
            self.tracks[('s', i)] = track_item(base_frames_ref_gray, int(sl['ref_s']), sl.get('tc', sl['p']), sl.get('patch', 30),
                                               int(sl['s_in']) - 2, int(sl['s_out']) + 2)

    def root(self, s):
        return interp_keys(self.cfg['root'], s)

    def rmax(self, c):
        return max(np.hypot(x - c[0], y - c[1]) for x in (0, REF_W) for y in (0, REF_H)) * 1.05

    # -- beat wave
    def wave_weight(self, s, c):
        cfg = self.cfg.get('ring', {})
        dur, rm = cfg.get('frames', 8.0), self.rmax(c)
        dist = np.hypot(self.xx - c[0], self.yy - c[1])
        w = np.zeros_like(dist)
        for b in self.beats:
            a = s - b
            if a < -0.01 or a > dur + 6:
                continue
            r = rm * (a / dur) ** cfg.get('ease', 0.85)
            d = dist - r
            sf, sb = cfg.get('front', 0.035) * rm, cfg.get('back', 0.16) * rm
            prof = np.where(d > 0, np.exp(-(d / sf) ** 2), np.exp(d / sb))
            w = np.maximum(w, prof * cfg.get('amp', 1.0))
        return w

    # -- dark sectors
    def sector_dark(self, s, c):
        cfg = self.cfg.get('dark', {})
        if not cfg:
            return None, []
        rm = self.rmax(c)
        ang = np.degrees(np.arctan2(self.yy - c[1], self.xx - c[0])) % 360
        dist = np.hypot(self.xx - c[0], self.yy - c[1])
        D = np.zeros_like(dist)
        fronts = []
        dur = cfg.get('frames', 6.0)
        rel = cfg.get('release', [1e9, 1e9 + 1])
        env = 1 - smooth(s, rel[0], rel[1])
        for i, (a0, a1) in enumerate(cfg['sectors']):
            if i >= len(self.seal_beats):
                break
            p = np.clip((s - self.seal_beats[i]) / dur, 0, 1)
            if p <= 0:
                fronts.append(None)
                continue
            rf = rm * (1 - p) ** 1.0
            lo, hi = a0 % 360, a1 % 360
            span = (a1 - a0) % 360 or 360
            rel_a = (ang - a0) % 360
            edge = cfg.get('edge_deg', 5.0)
            sec = smooth(rel_a, -edge, edge) * (1 - smooth(rel_a, span - edge, span + edge)) if span < 359 else 1.0
            # wrap-around fix: angles just below a0 appear as ~360
            sec = np.maximum(sec, smooth(rel_a - 360, -edge, edge)) if span < 359 else sec
            front = smooth(dist - rf, -0.03 * rm, 0.03 * rm) if p < 1 else np.ones_like(dist)
            D = np.maximum(D, sec * front)
            fronts.append((rf, a0, span, p))
        pr = cfg.get('protect')
        if pr:
            k_ = np.array(pr, float)
            if k_[0, 0] <= s <= k_[-1, 0]:
                cx, cy, rx, ry = [np.interp(s, k_[:, 0], k_[:, j]) for j in (1, 2, 3, 4)]
                e = np.hypot((self.xx - cx) / rx, (self.yy - cy) / ry)
                D = D * smooth(e, 0.8, 1.15)
        return D * env, fronts

    def seal_img(self, ch, px, key):
        if key not in self.seal_cache:
            self.seal_cache[key] = tiny_seal(ch, px, self.k)
        return self.seal_cache[key]

    def render(self, s, base8, base_ref8):
        cfg, k = self.cfg, self.k
        img = base8.astype(F32) / 255.0
        c = self.root(s)
        lamp = None
        need_lamp = bool(self.beats) or bool(cfg.get('dark'))
        if need_lamp:
            lamp = lantern_mask(base8)
        # beat wave
        if self.beats:
            w = self.wave_weight(s, c)
            if w.max() > 0.01:
                rc = cfg.get('ring', {})
                g = rc.get('gain', 1.6) - 1
                Lw = lamp * w
                # glow: soft bloom of the flared lanterns
                src = img * Lw[..., None]
                b1 = cv2.GaussianBlur(src, (0, 0), 5 * k)
                b2 = cv2.GaussianBlur(src, (0, 0), 16 * k)
                img = img * (1 + g * Lw[..., None]) + rc.get('bloom', 0.9) * b1 + rc.get('bloom2', 0.6) * b2
        # darkening sectors
        D, fronts = self.sector_dark(s, c)
        if D is not None and D.max() > 0.01:
            dc = cfg['dark']
            lamp_s = cv2.GaussianBlur(lamp, (0, 0), 1.5 * k)
            drop = dc.get('lantern_to', 0.15)
            img = img * (1 - D[..., None] * lamp_s[..., None] * (1 - drop))
            img = img * (1 - dc.get('dim', 0.10) * D[..., None])
        # 讫 seal flashes
        if D is not None and fronts:
            self.update_flashes(s, lamp, fronts, c, D)
            for f in self.flashes:
                a = [0.55, 1.0, 1.0, 0.6][min(f['age'], 3)]
                sz = f['px']
                blit(img, self.seal_img('讫', sz, sz), f['x'] * k, f['y'] * k, alpha=a * cfg['dark'].get('seal_alpha', 0.95),
                     scale=1.0 + 0.08 * (f['age'] == 0))
            for f in self.flashes:
                f['age'] += 1
            self.flashes = [f for f in self.flashes if f['age'] < 4]
        # 真 seals
        for i, z in enumerate(cfg.get('zhen', [])):
            a_ = s - z['s']
            if a_ < -0.95:
                continue
            tr = self.tracks[('z', i)].get(s)
            if tr is None:
                continue
            x, y, sc, rot = tr
            ph = np.clip((a_ + 1.0) / 3.0, 0, 1)
            op = smooth(ph, 0, 0.85)
            scl = (1.15 - 0.15 * smooth(ph, 0, 1)) * sc
            zk = ('z', z.get('size', 36), z.get('style', 'bai'), i)
            if zk not in self.seal_cache:
                self.seal_cache[zk] = zhen_seal(z.get('size', 36), k, z.get('style', 'bai'), seed=3 + i)
            art = self.seal_cache[zk]
            if ph < 1:                                # ink spread: a soft darker bleed on the press
                bleed = cv2.GaussianBlur(art[..., 3], (0, 0), 1.4 * k)
                art = art.copy()
                art[..., 3] = np.clip(np.maximum(art[..., 3], bleed * 0.7), 0, 1)
            lum = cv2.GaussianBlur(img.mean(axis=2), (0, 0), 8 * k)
            ix, iy = int(np.clip(x * k, 0, self.W - 1)), int(np.clip(y * k, 0, self.H - 1))
            tint = float(np.clip(0.75 + 1.4 * lum[iy, ix], 0.75, 1.15))
            gl = (1 - smooth(a_, 0.5, 7.0)) * smooth(a_, -0.9, 0.5)       # brief warm glow around the fresh impression
            if gl > 0.01:
                rr = z.get('size', 36) * k * 1.1
                d2 = ((self.xx * k - x * k) ** 2 + (self.yy * k - y * k) ** 2) / (rr * rr)
                img += (np.exp(-d2)[..., None] * gl * 0.28 * np.array([0.35, 0.65, 1.0], F32))
            blit(img, art, x * k, y * k, alpha=op * z.get('alpha', 0.95), scale=scl, rot=rot, tint=tint)
        # name slips
        for i, sl in enumerate(cfg.get('slips', [])):
            if not (sl['s_in'] <= s <= sl['s_out']):
                continue
            tr = self.tracks[('s', i)].get(s)
            if tr is None:
                continue
            x, y, sc, rot = tr
            fade = min(smooth(s, sl['s_in'], sl['s_in'] + 6), 1 - smooth(s, sl['s_out'] - 6, sl['s_out']))
            key = ('slip', sl['ch'], sl.get('glyph', 14))
            if key not in self.seal_cache:
                self.seal_cache[key] = slip_art(sl['ch'], sl.get('glyph', 14), k)
            art = self.seal_cache[key]
            tc = sl.get('tc', sl['p'])
            ox, oy = sl['p'][0] - tc[0], sl['p'][1] - tc[1]
            # offset follows the tracked scale/rotation
            ca, sa = np.cos(rot), np.sin(rot)
            px = x + sc * (ca * ox - sa * oy)
            py = y + sc * (sa * ox + ca * oy)
            # tiny shadow
            blit(img, np.dstack([np.zeros(art.shape[:2] + (3,), F32), art[..., 3] * 0.5]), px * k + 1.0 * k, py * k + 1.2 * k,
                 alpha=fade * 0.6, scale=sc, rot=rot)
            blit(img, art, px * k, py * k, alpha=fade * 0.95, scale=sc, rot=rot)
        # thread contrast (thin red pixels), wide shots
        th = cfg.get('thread')
        if th and th['s'][0] <= s <= th['s'][1]:
            e = smooth(s, th['s'][0], th['s'][0] + 4) * (1 - smooth(s, th['s'][1] - 4, th['s'][1]))
            hsv = cv2.cvtColor(np.clip(img * 255, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(F32)
            hh, ss, vv = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
            red = (1 - smooth(hh, 6, 14)) + smooth(hh, 168, 176)
            thin = smooth(vv - cv2.GaussianBlur(vv, (0, 0), 2.5 * k), 0.02, 0.07)
            m = np.clip(red, 0, 1) * smooth(ss, 0.35, 0.6) * thin
            img = img * (1 + (th.get('gain', 1.4) - 1) * e * m[..., None])
        # ink puff + the hair that arrives into it
        pf = cfg.get('puff')
        if pf:
            self.puff(img, s, pf)
        # grain
        gr = cfg.get('grain', 0.0)
        if gr > 0:
            r = np.random.RandomState(1000 + s)
            n = cv2.GaussianBlur(r.randn(self.H, self.W).astype(F32), (0, 0), 0.8 * max(k, 1))
            img += gr * n[..., None] * (0.5 + img.mean(axis=2, keepdims=True))
        return np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)

    def puff(self, img, s, pf):
        k = self.k
        cx, cy = pf['p']
        st = pf['streak']
        # hair streak: a thin dark quadratic curve drawn progressively toward the puff centre
        a0 = pf['s0'] - st['frames'] - 0.5
        if a0 <= s <= pf['s0'] + 2:
            u1 = np.clip((s - a0) / st['frames'], 0, 1)
            fade = 1 - smooth(s, pf['s0'], pf['s0'] + 2)
            P0, P2 = np.array(st['from'], float), np.array([cx, cy], float)
            P1 = np.array(st['ctrl'], float)
            u0 = max(0.0, u1 - 0.55)
            pts = [((1 - u) ** 2 * P0 + 2 * (1 - u) * u * P1 + u * u * P2) * k for u in np.linspace(u0, u1, 24)]
            layer = np.zeros((self.H, self.W), F32)
            cv2.polylines(layer, [np.int32(np.array(pts) * 8)], False, 1.0, max(1, int(round(1.6 * k))), cv2.LINE_AA, shift=3)
            layer = cv2.GaussianBlur(layer, (0, 0), 0.7 * k)
            img *= (1 - 0.88 * fade * layer)[..., None]
            img += (0.02 * fade * layer)[..., None]
        age = s - pf['s0']
        if age < -0.01 or age > pf['frames']:
            return
        u = age / pf['frames']
        r = pf['r'] * k * (0.35 + 0.65 * np.sqrt(u + 0.05))
        r_core = pf['r'] * k * 0.55 * (0.5 + u)
        rng = np.random.RandomState(pf.get('seed', 5))
        if not hasattr(self, '_pn'):
            n1 = cv2.GaussianBlur(rng.randn(self.H, self.W).astype(F32), (0, 0), 7 * k)
            n2 = cv2.GaussianBlur(rng.randn(self.H, self.W).astype(F32), (0, 0), 2.2 * k)
            n3 = cv2.GaussianBlur(rng.randn(self.H, self.W).astype(F32), (0, 0), 0.9 * k)
            self._pn = [x / (x.std() + 1e-6) for x in (n1, n2, n3)]
        n1, n2, n3 = self._pn
        dx, dy = self.xx * k - cx * k, self.yy * k - cy * k
        d = np.sqrt(dx * dx + (dy / pf.get('aspect', 1.0)) ** 2)
        warp = 1 + 0.18 * n1 * 0.6 + 0.08 * n2 * 0.5
        e = d / (r * warp + 1e-6)
        body = 1 - smooth(e, 0.55, 1.0)                       # soft radial spread with a ragged edge
        grain = np.clip(0.8 + 0.22 * n2 + 0.12 * n3, 0.2, 1.2)
        dens = pf.get('alpha', 0.97) * (1 - smooth(u, 0.2, 0.85)) ** 1.2          # thinning as it expands
        a = np.clip(body * grain * dens, 0, 1)
        core = np.clip((1 - smooth(d / (r_core + 1e-6), 0.4, 1.0)) * (1 - smooth(u, 0.15, 0.55)), 0, 1)
        a = np.maximum(a, core * 0.98)
        ink = np.array([0.06, 0.055, 0.05], F32)
        img[:] = img * (1 - a[..., None]) + ink * a[..., None]

    def update_flashes(self, s, lamp, fronts, c, D=None):
        """Blobs the dark front has just passed (this frame) get a 4-frame 讫 seal; capped per frame."""
        dc = self.cfg['dark']
        b = (lamp > 0.5).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(b, connectivity=8)
        if n <= 1:
            return
        k = self.k
        sc = []
        for j in range(1, n):
            area = st[j, cv2.CC_STAT_AREA]
            if area < 2:
                continue
            x, y = cen[j] / k
            sc.append((float(lamp[lab == j].sum()) if area < 400 else area, x, y, j))
        sc.sort(reverse=True)
        rm = self.rmax(c)
        per_frame = dc.get('per_frame', 5)
        for i, fr in enumerate(fronts):
            if fr is None:
                continue
            rf, a0, span, p = fr
            if p >= 1.0 and s - self.seal_beats[i] > dc.get('frames', 6) + 1:
                continue
            prev = rm * (1 - max(0.0, (s - 1 - self.seal_beats[i]) / dc.get('frames', 6)))
            taken = 0
            for scr, x, y, j in sc:
                d = np.hypot(x - c[0], y - c[1])
                ang = np.degrees(np.arctan2(y - c[1], x - c[0]))
                if (ang - a0) % 360 > span:
                    continue
                if rf <= d <= prev + 1e-6 and d > 0 and 0 <= x < REF_W and 0 <= y < REF_H:
                    if D is not None and D[int(y * k), int(x * k)] < 0.35:      # protected (monkeys) or not yet dark
                        continue
                    if any(np.hypot(f['x'] - x, f['y'] - y) < dc.get('min_gap', 14) for f in self.flashes):
                        continue
                    self.flashes.append({'x': x, 'y': y, 'age': 0, 'sec': i, 'px': dc.get('seal_px', 12) + (2 if scr > 40 else 0)})
                    taken += 1
                    if taken >= per_frame:
                        break
            if taken:
                self.log.append((s, i, taken))


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--w', type=int, default=960)
    ap.add_argument('--h', type=int, default=540)
    ap.add_argument('--stage', default='all')
    ap.add_argument('--frames', default=None)
    ap.add_argument('--cand', default=None)
    ap.add_argument('--no-encode', action='store_true')
    ap.add_argument('--force-base', action='store_true')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    if a.cand:
        cfg['cand'] = a.cand
    cand, W, H = cfg['cand'], a.w, a.h
    n = cfg.get('nframes', 176)
    bd = stage_base(cfg, W, H, a.force_base)
    print('base', bd)
    if a.stage == 'base':
        return
    out = a.out or os.path.join(ROOT, 'work/swarm', cand, 'frames' + ('' if (W, H) == (960, 540) else f'_{W}x{H}'))
    os.makedirs(out, exist_ok=True)
    base = [cv2.imread(f'{bd}/b{s:04d}.png') for s in range(n)]
    ref = [cv2.resize(b, (REF_W, REF_H), interpolation=cv2.INTER_AREA) if b.shape[1] != REF_W else b for b in base]
    grays = [cv2.cvtColor(r, cv2.COLOR_BGR2GRAY) for r in ref]
    ov = Overlay(cfg, W, H, n)
    ov.prepare_tracks(grays)
    sel = [int(x) for x in a.frames.split(',')] if a.frames else range(n)
    for s in range(n):
        im = ov.render(s, base[s], ref[s])          # sequential: flashes are stateful
        if s in sel:
            cv2.imwrite(f'{out}/f{s:04d}.png', im)
    print('flashes per frame:', ov.log)
    print('frames ->', out)
    if a.no_encode or a.frames:
        return
    mp4 = a.out and None or os.path.join(ROOT, 'media/comp', f'F4F5F6a_{cand}.mp4' if (W, H) == (960, 540) else f'F4F5F6a_{cand}_{W}x{H}.mp4')
    subprocess.run([sys.executable, 'tools/swarm4/encode.py', out, mp4, '--expect', str(n)], check=True)
    rv = os.path.join(ROOT, 'work/review/comp_v4')
    os.makedirs(rv, exist_ok=True)
    if (W, H) == (960, 540):
        sh = lambda name, extra: subprocess.run([sys.executable, 'tools/swarm4/sheet.py', out, f'{rv}/{name}'] + extra, check=True)
        sh(f'swarm_{cand}.jpg', ['--n', '16', '--cols', '4', '--w', '480'])
        sh(f'swarm_{cand}_strip_a.jpg', ['--frames', ','.join(str(x) for x in range(0, 49, 2)), '--cols', '5', '--w', '384'])
        sh(f'swarm_{cand}_strip_b.jpg', ['--frames', ','.join(str(x) for x in range(70, 131, 2)), '--cols', '5', '--w', '384'])


if __name__ == '__main__':
    main()

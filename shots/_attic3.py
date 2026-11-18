"""shots/_attic3.py: the 1988 attic, preview_v3 (team ATTIC). Builds on shots/_rooms88.py (v2 copy in shots/_v2/).

  Seg          one camera setup inside a shot: a v3 keyframe (media/kf/v3/<kf>.jpg) or a generated clip registered and
               colour-matched to it, retimed piecewise (tmap: [(song t, clip t), ...]) so the action lands on the cues
  Blade        the neon blade sign (LAYOUT_V3 option A) drawn in code: the sidecar's sign-face and lettering quads are
               carried from the guide's window onto the PAINTED window by a homography; lettering 酒 家 CHIN. IND. SPEC.
               REST. reads normally (not mirrored); it only shows through glowing glass (per-frame mask), so people
               and mullions in front hide it
  PageArt      page art multiplied onto the blank lit spread (tracked quad; locked when the book is still) + the cast
               shadow of whatever is over the page (the REAL hand mask of the frame, shifted away from the light)
  title_block  A1's title: Chaos Monkey / 混沌猴 / Jade Wang / seal, typeset
  AtticShot    segments + sign + page + grade + compositor camera + margins + hooks

All positions are authored in 1920x1080 px and scaled by ctx.s.
"""
import json
import math
import os

import cv2
import numpy as np

from shots._rooms88 import (Source, PageTrack, spread, warp_spread, map_page, clean_page, paper_tex, finish, camera_move,
                            motes, beam_field, lay_shadow, KAI_FONT, SANS_NARROW, LATIN_FONT, _glyph_mask, UMBRA)
from shots._attic_grade import grade_field
from tools.ink import *                                    # noqa: F401,F403
from tools.ink.core import F32, ROOT
from tools.ink.light import neon_colour

KF3 = 'media/kf/v3/'
LAY = ROOT / 'media/layout/attic88'
BRUSH_FONT = None
for _p in sorted((ROOT / 'refs/fonts/mashanzheng').glob('*.ttf')):
    BRUSH_FONT = str(_p)
PICKS = ROOT / 'media/comp/attic3/picks.json'


def kf3(name, W, H):
    return load_image(f'{KF3}{name}.jpg', size=(W, H))


def pick(key):
    """media/comp/attic3/picks.json: {key: {'path': clip, 'tmap': [[song_t, clip_t], ...], 'twos': bool}}"""
    if not PICKS.exists():
        return None
    return json.load(open(PICKS)).get(key)


# ----------------------------------------------------------------------------------------------------------------
class Seg:
    def __init__(self, t0, t1, kf, key=None, clip=None, tmap=None, twos=False, keep=(), floor=0.5, cam=None, window=None,
                 guide=None, page=None, sign_gain=1.0, match=True, wedge=(0.50, 0.78)):
        self.__dict__.update(locals())
        del self.__dict__['self']

    def setup(self, ctx):
        W, H = ctx.W, ctx.H
        self.s = ctx.s
        self.KF = kf3(self.kf, W, H)
        p = pick(self.key) if self.key else None
        clip, tmap, twos = self.clip, self.tmap, self.twos
        if p:
            clip, tmap, twos = p['path'], p.get('tmap', tmap), p.get('twos', twos)
        self.has_clip = bool(clip and os.path.exists(str(ROOT / clip)))
        if self.has_clip:
            self.src = Source(W, H, clip=clip, match=self.KF if self.match else None)
            self.tm = np.array(tmap or [[self.t0, 0.42], [self.t1, 0.42 + (self.t1 - self.t0)]], float)
        else:
            self.src = Source(W, H, still=self.KF)
        self.twos = twos
        self.G = grade_field(self.KF, keep=self.keep, floor=self.floor)
        self.blade = Blade(self.guide, self.window, ctx.s, W, H, gain=self.sign_gain, kf=self.KF, wedge=self.wedge) if self.window else None
        self.PA = PageArt(self, ctx, **self.page) if self.page else None

    def index(self, t):
        if not self.has_clip:
            return 0
        if self.twos:
            t = math.floor(round(t * 24) / 2.0) * 2 / 24.0
        c = float(np.interp(t, self.tm[:, 0], self.tm[:, 1]))
        return int(min(self.src.n - 1, max(0, round(c * self.src.fps))))

    def frame(self, t):
        i = self.index(t)
        return self.src.frame_i(i), i


# ----------------------------------------------------------------------------------------------------------------
# the blade sign

def _tube(text, cjk):
    if cjk:
        m = _glyph_mask(text, KAI_FONT, 300, pad=24)
        edge = m - cv2.erode(m, np.ones((3, 3), np.uint8))
        return cv2.dilate(edge, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))).astype(F32)
    from tools.ink.roto import thin
    m = _glyph_mask(text, SANS_NARROW, 200, pad=16)
    sk = thin(m.astype(bool)).astype(np.uint8)
    return cv2.dilate(sk, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))).astype(F32)


_TUBES = {}


def tube(text):
    if text not in _TUBES:
        _TUBES[text] = _tube(text, any(ord(c) > 0x2E80 for c in text))
    return _TUBES[text]


class Blade:
    """ONE sign in every shot (round 2): a vertical blade hung perpendicular to the wall, seen through the window as a narrow
    foreshortened wedge of cinnabar tubes, 酒 over 家. window: the PAINTED window's outer box (x0, y0, x1, y1) in 1920 px or a
    quad TL TR BR BL. wedge=(u0, u1): the blade's near and far edge as fractions of the window width (door-end cameras see
    it edge-on: about 0.2 wide; from the mats it is wider, about 0.3, never frontal). The far edge is drawn shorter
    (perspective). Colour is constant cinnabar (no breathing to blue). It shows only through glowing glass, so people,
    mullions and frames in front hide it. guide is kept for compatibility and ignored."""

    def __init__(self, guide, window, s, W, H, gain=1.0, kf=None, wedge=(0.50, 0.78)):
        self.kf = kf
        if np.ndim(window[0]) == 0:
            x0, y0, x1, y1 = window
            wq = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
        else:
            wq = np.float32(window)
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), wq * s)
        u0, u1 = wedge
        k = 0.10                                                  # the far edge is this much shorter top and bottom

        def quad(v0, v1, pad=0.0):
            a, b = u0 + pad * (u1 - u0), u1 - pad * (u1 - u0)
            q = np.float32([[a, v0], [b, v0 + k * (v1 - v0) * 0.5], [b, v1 - k * (v1 - v0) * 0.5], [a, v1]])
            return cv2.perspectiveTransform(q[None], Hm)[0]
        self.s, self.gain = s, gain
        self.box = (max(0, int(wq[:, 0].min() * s) - 2), max(0, int(wq[:, 1].min() * s) - 2),
                    min(W, int(wq[:, 0].max() * s) + 3), min(H, int(wq[:, 1].max() * s) + 3))
        body = np.zeros((H, W), F32)
        cv2.fillConvexPoly(body, np.round(quad(-0.4, 1.6)).astype(np.int32), 1.0)
        self.body = cv2.GaussianBlur(body, (0, 0), 0.8 * s + 0.3)
        a = np.zeros((H, W), F32)
        for text, v0, v1 in (('酒', 0.05, 0.47), ('家', 0.53, 0.95)):
            T = tube(text)
            h, w = T.shape
            M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), quad(v0, v1, 0.08))
            a = np.maximum(a, cv2.warpPerspective(T, M, (W, H), flags=cv2.INTER_AREA))
        edge = np.zeros((H, W), F32)                              # the border tube down both edges of the blade
        qq = np.round(quad(-0.4, 1.6)).astype(np.int32)
        cv2.polylines(edge, [qq], True, 1.0, max(1, int(round(2.2 * s))))
        a = np.maximum(a, edge * 0.8)
        self.core = np.clip(cv2.GaussianBlur(a, (0, 0), 0.5 * s + 0.2) * 1.3, 0, 1)
        self.halo = np.clip(cv2.GaussianBlur(a, (0, 0), 5.0 * s + 0.5) * 1.6, 0, 1)

    def glass(self, f):
        x0, y0, x1, y1 = self.box
        sub = f[y0:y1, x0:x1]
        L = sub.mean(axis=2)
        red = sub[..., 0] - sub[..., 2]
        g = np.zeros(f.shape[:2], F32)
        m = ((red > 0.10) & (L > 0.16)).astype(F32)
        if self.kf is not None:                    # only where the frame still shows the keyframe's own glowing glass
            k = self.kf[y0:y1, x0:x1]
            kg = ((k[..., 0] - k[..., 1] > 0.22) & (k[..., 0] > 0.40)).astype(F32)
            diff = np.abs(cv2.GaussianBlur(sub, (0, 0), 1.5 * self.s + 0.3) - cv2.GaussianBlur(k, (0, 0), 1.5 * self.s + 0.3)).max(axis=2)
            m = m * kg * np.clip(1.6 - diff * 9.0, 0, 1)
        g[y0:y1, x0:x1] = cv2.GaussianBlur(m, (0, 0), 0.8 * self.s + 0.3)
        return g

    def apply(self, f, t, on=1.0):
        if on <= 0:
            return f
        g = self.glass(f) * on * self.gain
        col = np.array([0.93, 0.20, 0.11], F32)                       # cinnabar, constant
        f = f * (1 - 0.30 * (self.body * g)[..., None])                 # the blade's own dark body against the glow
        a = (self.halo * g * 0.55)[..., None]
        f = f + (np.maximum(f, col) - f) * a
        hot = np.array([1.0, 0.52, 0.36], F32)                         # a hot tube core: orange-red, never white or blue
        a = (self.core * g * 0.95)[..., None]
        f = f + (hot - f) * a
        return np.clip(f, 0, 0.985)


# ----------------------------------------------------------------------------------------------------------------
# page art + the cast shadow of the hands

def art_T(kind):
    """Ink transmittance of a spread. kind: a _rooms88.spread kind, or 'file:<path>' (unlit flat page art)."""
    if kind.startswith('shift:'):                 # 'shift:du,dv:<kind>': move the art on the spread (fractions)
        _, sh, rest = kind.split(':', 2)
        du, dv = [float(v) for v in sh.split(',')]
        T = art_T(rest)
        h, w = T.shape[:2]
        M = np.float32([[1, 0, du * w], [0, 1, dv * h]])
        return cv2.warpAffine(T, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
    if kind.startswith('right:'):                 # a plate set on the RIGHT page only (left page bare)
        from shots._rooms88 import SW, SH, key_paper
        a = key_paper(load_image(kind[6:], size=(SW // 4, int(SW // 4 * 0.5625))), lo=0.04, hi=0.14)
        T = np.ones((SH // 2, SW // 2) + a.shape[2:], F32)
        h, w = a.shape[:2]
        x0 = SW // 4 + (SW // 4 - w) // 2 - 10
        y0 = (SH // 2 - h) // 2 + 30
        T[y0:y0 + h, x0:x0 + w] = a
        return T
    if kind.startswith('file:'):
        a = load_image(kind[5:])
        if a.shape[1] > 2400:
            a = cv2.resize(a, (2304, int(a.shape[0] * 2304 / a.shape[1])), interpolation=cv2.INTER_AREA)
        ground = np.percentile(a.reshape(-1, 3), 92, axis=0)
        return np.clip(a / ground, 0, 1).astype(F32)
    return spread(kind)


class PageArt:
    """kind: art; roi: where the page is (1920 px box); tl: direction of the spread's top-left corner from its centre;
    quad: fixed quad (1920 px) overriding detection; lock: use the median quad for all frames when the book barely
    moves; shadow: dict(d=(dx, dy) px at 1920 = throw of the shadow away from the light, soft=px, strength, grow=1.03)
    strength: art strength."""

    def __init__(self, seg, ctx, kind, roi, tl=(-1, -1), quad=None, lock=True, shadow=None, strength=1.0, thr=None,
                 cthr=11.0, clean=True, kinds=None, kind_at=None, plate=False, dthr=0.055):
        self.plate, self.dthr = plate, dthr
        self.seg, self.s, self.shadow, self.strength, self.clean = seg, ctx.s, shadow, strength, clean
        self.kind, self.kind_at = kind, kind_at
        self.PT = PageTrack(seg.src, roi, tl, thr=thr, quad=quad, cthr=cthr)
        Q = self.PT.Q
        self.move = float(np.abs(Q - np.median(Q, axis=0)).max()) if len(Q) > 1 else 0.0
        if lock and (quad is None) and self.move < 14:
            self.PT.Q = np.repeat(np.median(Q, axis=0)[None], len(Q), 0)
        self.T = {k: art_T(k) for k in (kinds or [kind])}

    def apply(self, f, t, i):
        s = self.s
        q = self.PT.quad(i, s)
        H, W = f.shape[:2]
        hull = np.zeros((H, W), np.uint8)
        cv2.fillConvexPoly(hull, np.round(q).astype(np.int32), 1)
        if self.plate:                               # paper = inside the quad and still looking like the clean keyframe
            k = self.seg.KF
            d = np.abs(cv2.GaussianBlur(f, (0, 0), 1.2 * s + 0.3) - cv2.GaussianBlur(k, (0, 0), 1.2 * s + 0.3)).max(axis=2)
            kl = k.mean(axis=2)
            paper0 = (kl > 0.42).astype(np.uint8) & hull       # the keyframe's own bare paper inside the quad
            diff = (d > self.dthr).astype(np.uint8)
            diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            n_, lb_, st_, _c = cv2.connectedComponentsWithStats(diff)          # only real things (hands, sleeves), not grain
            keep_ = np.zeros(n_, np.uint8)
            keep_[1:] = st_[1:, cv2.CC_STAT_AREA] > 2500 * s * s
            diff = keep_[lb_]
            kc = max(5, int(27 * s) | 1)
            diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kc, kc)))
            diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            from shots._rooms88 import fill_holes
            diff = fill_holes(diff)
            m = cv2.GaussianBlur((paper0 & (1 - diff)).astype(F32), (0, 0), max(0.6, 1.0 * s))
            self.diff = (diff & hull).astype(F32)
        else:
            m = self.PT.mask(f, s, i)
        if self.clean:
            f = clean_page(f, m, s, 31)
        kind = self.kind_at(t) if self.kind_at else self.kind
        f = map_page(f, self.T[kind], q, m, self.strength)
        if self.shadow:
            sh = self.shadow
            # whatever is over the page and is not paper (hands, sleeves) casts the shadow
            inner = cv2.erode(hull, np.ones((5, 5), np.uint8)).astype(F32)
            if self.plate:
                caster = self.diff * inner
            else:
                caster = np.clip(inner - cv2.dilate(m, np.ones((3, 3), np.uint8)), 0, 1)
                caster = cv2.morphologyEx(caster, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            dx, dy = sh['d'][0] * s, sh['d'][1] * s
            g = sh.get('grow', 1.03)
            ys, xs = np.nonzero(caster > 0.5)
            if len(xs) > 50:
                soft = sh.get('soft', 14) * s
                if sh.get('sil'):
                    # the monkey-head hand shadow (layout/assets/monkey_silhouette.json: unit = its height, origin = the
                    # wrists, y up, profile faces +x), standing on the wrists of the real hands in THIS frame and thrown
                    # by the offset; the hands themselves stay on top, so the shadow is joined to them
                    hh = sh['h'] * s * g
                    top = np.percentile(ys, 2)
                    sel = ys < top + 0.45 * hh
                    ox, oy = xs[sel].mean() + sh.get('ox', 0) * s + dx, top + sh.get('up', 0.80) * hh + dy
                    st = getattr(self, '_sil', None)
                    cur = np.array([ox, oy])
                    self._sil = cur if st is None else st * 0.6 + cur * 0.4            # steady, follows the hands
                    ox, oy = self._sil
                    d = json.load(open(ROOT / 'layout/assets/monkey_silhouette.json'))
                    S = np.zeros((H, W), F32)
                    P = np.array(d['outer'], float)
                    cv2.fillPoly(S, [np.round(np.c_[ox + P[:, 0] * hh, oy - P[:, 1] * hh]).astype(np.int32)], 1.0)
                    for hole in d.get('holes', []):
                        Q = np.array(hole, float)
                        cv2.fillPoly(S, [np.round(np.c_[ox + Q[:, 0] * hh, oy - Q[:, 1] * hh]).astype(np.int32)], 0.0)
                else:
                    cx, cy = xs.mean(), ys.mean()
                    M = np.float32([[g, 0, cx * (1 - g) + dx], [0, g, cy * (1 - g) + dy]])
                    S = cv2.warpAffine(caster, M, (W, H), flags=cv2.INTER_LINEAR)
                S = cv2.GaussianBlur(S, (0, 0), soft, sigmaY=soft * sh.get('aniso', 0.6))
                S = S * m                                             # falls on paper only, never on the hand itself
                f = lay_shadow(f, S, 0, strength=sh.get('strength', 0.85))
            self.caster = caster
        self.q, self.m = q, m
        return f


# ----------------------------------------------------------------------------------------------------------------
# A1's title

def title_block(W, H, s, x=540, y=742):
    """-> (alpha HxW, rgb HxWx3): 'Chaos Monkey' (EB Garamond) / 混沌猴 (brush kai) / 'Jade Wang' smaller / one red seal."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(LATIN_FONT, int(round(64 * s)))
    try:
        f1.set_variation_by_axes([500])
    except Exception:
        pass
    f2 = ImageFont.truetype(BRUSH_FONT or KAI_FONT, int(round(74 * s)))
    f3 = ImageFont.truetype(LATIN_FONT, int(round(30 * s)))
    d.text((x * s, y * s), 'Chaos Monkey', font=f1, fill=255)
    d.text((x * s + 2 * s, (y + 84) * s), '混沌猴', font=f2, fill=255)
    # tracked small caps-ish name
    xx = x * s + 3 * s
    for ch in 'Jade Wang':
        d.text((xx, (y + 186) * s), ch, font=f3, fill=255)
        xx += f3.getlength(ch) + 2.2 * s
    a = np.asarray(im).astype(F32) / 255
    rgb = np.ones((H, W, 3), F32) * np.array([0.90, 0.84, 0.74], F32)
    # the seal, right of the Chinese title
    from tools.ink.seal import seal
    sz = int(round(58 * s))
    sl = seal('猴', KAI_FONT, size=sz, style='zhu', wear=0.25, seed=7)
    sx, sy = int((x + 250) * s), int((y + 98) * s)
    h, w = sl.shape[:2]
    sa = sl[..., 3] if sl.shape[2] == 4 else np.ones((h, w), F32)
    a[sy:sy + h, sx:sx + w] = np.maximum(a[sy:sy + h, sx:sx + w], sa * 0.95)
    rgb[sy:sy + h, sx:sx + w] = np.where(sa[..., None] > 0.05, sl[..., :3], rgb[sy:sy + h, sx:sx + w])
    return a, rgb


# ----------------------------------------------------------------------------------------------------------------
class AtticShot:
    """segs: [Seg, ...] in time order. Optional: margins=True (G shots), sign_on(t) -> level, post(f, t, shot),
    pre(f, t, i, seg) before the grade, dust=False."""

    def __init__(self, segs, margins=False, margin_state=None, sign_on=None, post=None, pre=None, fibre=1.0):
        self.segs, self.margins, self.margin_state = segs, margins, margin_state
        self.sign_on, self.post, self.pre, self.fibre = sign_on, post, pre, fibre

    def setup(self, ctx):
        self.ctx = ctx
        for sg in self.segs:
            sg.setup(ctx)
        self.TEX = paper_tex(ctx.W, ctx.H)

    def seg_at(self, t):
        for sg in self.segs:
            if t < sg.t1 - 1e-6:
                return sg
        return self.segs[-1]

    def render(self, t):
        sg = self.seg_at(t)
        f, i = sg.frame(t)
        if sg.PA is not None:
            f = sg.PA.apply(f, t, i)
        if self.pre:
            f = self.pre(f, t, i, sg)
        if sg.blade is not None:
            f = sg.blade.apply(f, t, on=self.sign_on(t) if self.sign_on else 1.0)
        f = finish(f, sg.G, self.TEX, self.fibre)
        f = camera_move(f, t, sg.cam or [])
        if self.post:
            f = self.post(f, t, self, sg)
        if self.margins:
            from shots._margins import apply_margins, make_margins
            if not hasattr(self, 'M'):
                self.M = make_margins(f.shape[1], f.shape[0])
            if self.margin_state:
                from tools.ink.margins import desaturate
                st = self.margin_state(t, f.shape[1], f.shape[0])
                if not st['open']:
                    if st['desat'] > 0:
                        f = desaturate(f, st['desat'], paper=self.M.paper.ground)
                    f = self.M.lay(f, st['rect'])
            else:
                f = apply_margins(f, t, self.M)
        return f


def fr(n):
    return n / 24.0


def soft_margins(k=0.4):
    """The shared margin schedule (shots/_margins.py: same rect, same timing) with the drain to grey scaled by k: in the
    room the people must keep warm skin (the full drain turns faces grey and the blush blue-grey)."""
    from shots._margins import margin_state

    def f(t, W, H):
        st = dict(margin_state(t, W, H))
        st['desat'] = st['desat'] * k
        return st
    return f

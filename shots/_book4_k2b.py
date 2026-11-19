"""shots/_book4_k2b.py: K2b v4 (BOOK, LEDGER sub-team): the ledger turned a quarter-turn, the monkey (costume B) draws one
stroke straight down a column; a plunge from the whole spread into the ledger.

The page is the v3 plate with the monkey+ledger crop R (page px 1640..2920 x 760..1480) repainted by gpt-image-2
(work/book4/LEDGER/K2b_v4_plate.jpg). A video clip animated from that crop (2560x1440 first frame = R) is keyed to our
paper and laid over R (feathered); camera, torch, the typeset inscription outside R are ours.
"""
import glob
import os
import sys

import cv2
import numpy as np

from tools.ink import *
from tools.ink.core import ROOT
from tools.ink.paper import key_paper
from tools.ink.video import decode
from shots import _pages3 as P3
from shots._pages3 import SW, SH, Z0, torch, push_cam

R = (1640, 760, 2920, 1480)        # page px, the animated crop
RS = 2.0                           # clip px per page px
PLATE = 'work/book4/LEDGER/K2b_v4_plate.jpg'


# ---- the ledger's writing on the turned book (same entries and column order as K3: struck column = 1350, under the brush)
NUM = '〇一二三四五六七八九'


def _cnum(n):
    s_ = ''
    th, hu, te, on = n // 1000, n // 100 % 10, n % 10 * 0 + n // 10 % 10, n % 10
    if th:
        s_ += NUM[th] + '千'
    if hu:
        s_ += NUM[hu] + '百'
    if te:
        s_ += NUM[te] + '十'
    if on:
        s_ += NUM[on]
    return s_


# (kind, strings); right page cells right->left then left page cells right->left (cell 1 of the left page = the struck one)
NOTES = {1346: ['似飛禽', '不受鳳凰轄', '該壽四十七歲'], 1347: ['似走獸', '不伏麒麟管', '該壽九十六歲', '善終'],
         1348: ['似人相', '不入人名', '該壽一百三十六歲'], 1349: ['似臝蟲', '不居國界', '該壽一百零四歲', '善終'],
         1350: ['天產石猴', '該壽三百四十二歲', '善終'], 1351: ['似飛禽', '不受鳳凰轄', '該壽四十七歲'],
         1352: ['似走獸', '不伏麒麟管', '該壽七十七歲', '善終'], 1353: ['似人相', '不入人名', '該壽八十一歲'],
         1354: ['似臝蟲', '不居國界', '該壽一百一十二歲', '善終']}
# page quads in clip px (TL, TR, BR, BL) read off the plate's ruled frames, and the number of ruled cells
QUAD_RIGHT = ([(1057, 812), (1325, 832), (1360, 1188), (1057, 1178)], 8)
QUAD_LEFT = ([(695, 802), (997, 803), (993, 1178), (657, 1170)], 9)
CELL = 64


def _cols_right():
    out = []
    for n in (1346, 1347, 1348, 1349):
        out += [('main', n), ('note', n)]
    return out


def _cols_left():
    out = []
    for n in (1350, 1351, 1352, 1353):
        out += [('main', n), ('note', n)]
    out += [('main', 1354)]
    return out


def _page_texture(cols, ncell, fontpath):
    from PIL import Image, ImageDraw, ImageFont
    Wt, Ht = ncell * CELL * 2, 11 * CELL * 2
    im = Image.new('L', (Wt, Ht), 0)
    d = ImageDraw.Draw(im)
    cw = CELL * 2
    for i, (kind, n) in enumerate(cols):          # right to left
        cx = Wt - (i + 0.5) * cw
        if kind == 'main':
            g = int(cw * 0.74)
            f = ImageFont.truetype(fontpath, g)
            strs = [f'魂字{_cnum(n)}號', '孫悟空' if n == 1350 else '猴屬']
            y = Ht * 0.035
            for si, st in enumerate(strs):
                for ch in st:
                    d.text((cx, y + g / 2), ch, font=f, fill=255, anchor='mm')
                    y += g * 1.0
                y += g * 0.45
        else:
            g = int(cw * 0.54)
            f = ImageFont.truetype(fontpath, g)
            y = Ht * 0.115
            for st in NOTES[n]:
                for ch in st:
                    d.text((cx, y + g / 2), ch, font=f, fill=255, anchor='mm')
                    y += g * 1.02
                y += g * 0.45
    return np.asarray(im, np.float32) / 255.0


def ledger_text_alpha(shape=(1440, 2560)):
    """Coverage (0..1) of the typeset entries, warped onto the two page quads of the turned ledger."""
    fontpath = str(ROOT / 'refs/fonts/guangekai/館閣楷-Regular.ttf')
    out = np.zeros(shape, np.float32)
    for quad, ncell, cols in ((QUAD_RIGHT[0], QUAD_RIGHT[1], _cols_right()), (QUAD_LEFT[0], QUAD_LEFT[1], _cols_left())):
        tex = _page_texture(cols, ncell, fontpath)
        th, tw = tex.shape
        src = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]])
        dst = np.float32(quad)
        k = 0.5                                   # texture is 2x the CELL; bring it to ~1x before warping (no aliasing)
        tex2 = cv2.resize(tex, (int(tw * k), int(th * k)), interpolation=cv2.INTER_AREA)
        M = cv2.getPerspectiveTransform(np.float32(src * k), dst)
        out = np.maximum(out, cv2.warpPerspective(tex2, M, (shape[1], shape[0]), flags=cv2.INTER_LINEAR))
    return np.clip(cv2.GaussianBlur(out, (0, 0), 0.7), 0, 1)


def paper_weight(im, quadmask):
    """1 where the frame shows bare page paper (text may lie there), 0 where the monkey, brush or wet stroke is."""
    bg = np.array([0.94, 0.90, 0.82], np.float32)
    ref = cv2.GaussianBlur(im, (0, 0), 25)
    d = np.abs(im - bg).max(2)
    nonpaper = ((d > 0.16)).astype(np.uint8)
    # thin ruled lines are not occluders: keep only blobs wider than ~9 px
    occ = cv2.morphologyEx(nonpaper, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    occ = cv2.dilate(occ, np.ones((7, 7), np.uint8)).astype(np.float32)
    return 1.0 - cv2.GaussianBlur(occ, (0, 0), 2.0)


def register():
    if 'K2b4' not in P3.PAGES:
        P3.PAGES['K2b4'] = dict(P3.PAGES['K2b'], plate=PLATE)


class LedgerShot:
    def __init__(self, ctx, t0, t1, clip, clip_start, focus, z1, tip, settle=0.40, torch_r=(2300, 800), clip_keys=None, writing=True):
        register()
        self.t0, self.t1, self.focus, self.z1, self.tip = t0, t1, focus, z1, tip
        self.page, self.bare, _ = P3.build('K2b4')
        self.cam = Camera([(t0, SW / 2, SH / 2, Z0), (t0 + 0.10, SW / 2, SH / 2, Z0),
                           (t1 - settle, focus[0], focus[1], z1, 'inout'),
                           (t1 + 0.2, focus[0], focus[1] - 6, z1 * 1.02, 'linear')])
        self.radius, self.clip_start = torch_r, clip_start
        self.fr = None
        self.keys = clip_keys or [(0, 0), (40, 40)]
        if clip:
            x0, y0, x1, y1 = R
            paper = cv2.resize(self.bare[y0:y1, x0:x1], (int((x1 - x0) * RS), int((y1 - y0) * RS)), interpolation=cv2.INTER_CUBIC)
            TXT = ledger_text_alpha() if writing else None
            nout = int(round((t1 - t0) * 24)) + 2
            kk = np.array(self.keys, np.float64)
            cmap = [float(np.interp(i, kk[:, 0], kk[:, 1])) for i in range(nout)]
            slope = [abs(float(np.interp(i + 0.5, kk[:, 0], kk[:, 1]) - np.interp(i - 0.5, kk[:, 0], kk[:, 1]))) for i in range(nout)]
            cmax = int(np.ceil(max(cmap) + max(slope))) + 2

            def work():
                raw = []
                for ts, im in decode(str(ROOT / clip), start=clip_start, dur=cmax / 24.0 + 0.3, height=1440):
                    raw.append(np.clip(im, 0, 1).astype(np.float32))
                    if len(raw) >= cmax + 1:
                        break
                out = []
                for i in range(nout):
                    c, sl = cmap[i], slope[i]
                    if sl > 1.5:                       # temporal blur = motion smear while the clip is run fast
                        n = int(sl / 2) + 1
                        w = np.linspace(c - sl / 4, c + sl / 4, n)
                        acc = 0
                        for cc in w:
                            j = int(np.clip(cc, 0, len(raw) - 1.001)); fr_ = cc - j if cc < len(raw) - 1 else 0
                            acc = acc + (raw[j] * (1 - fr_) + raw[min(j + 1, len(raw) - 1)] * fr_)
                        im = acc / n
                    else:
                        j = int(np.clip(c, 0, len(raw) - 1.001)); fr_ = c - j
                        im = raw[j] * (1 - fr_) + raw[min(j + 1, len(raw) - 1)] * fr_
                    if im.shape[1] != 2560:
                        im = cv2.resize(im, (2560, 1440), interpolation=cv2.INTER_CUBIC)
                    if writing:
                        wgt = paper_weight(im, None)
                        im = im * (1 - 0.82 * (TXT * wgt))[..., None]
                    out.append((np.clip(paper * key_paper(im, lo=0.035, hi=0.13, feather=0.0), 0, 1) * 255).astype(np.uint8))
                return np.stack(out)
            self.fr = ctx.cache('k2b4_' + os.path.basename(clip) + f'_{clip_start}_{hash(tuple(map(tuple, self.keys))) & 0xffff}_w{int(writing)}', work)
            h, w = self.fr.shape[1:3]
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            e = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
            m = smoothstep(0, 260, e)
            self.M = np.dstack([m, m, m]).astype(np.float32)

    def clip_index(self, t):
        return int(np.clip(round((t - self.t0) * 24), 0, len(self.fr) - 1))

    def render(self, t, ctx):
        from shots._mountain import view
        cx, cy, z = self.cam.at(t)[:3]
        f = view(self.page, cx, cy, z, ctx.W, ctx.H)
        if self.fr is not None:
            x0, y0 = R[0], R[1]
            ccx, ccy = (cx - x0) * RS, (cy - y0) * RS
            src = self.fr[self.clip_index(t)].astype(np.float32) / 255.0
            fc = view(src, ccx, ccy, z / RS, ctx.W, ctx.H)
            m = view(self.M, ccx, ccy, z / RS, ctx.W, ctx.H)
            f = f * (1 - m) + fc * m
        zz = z * ctx.W / 1920.0
        fx, fy = (self.tip[0] - cx) * zz + ctx.W / 2, (self.tip[1] - cy) * zz + ctx.H / 2
        u = ramp(t, self.t0, self.t1, 'inout')
        r = (self.radius[0] + (self.radius[1] - self.radius[0]) * u) * ctx.s
        return torch(f, (fx, fy), r, ctx.s, ambient=0.26 - 0.18 * u, gain=0.98 + 0.45 * u)

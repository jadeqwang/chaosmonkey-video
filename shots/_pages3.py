"""shots/_pages3.py: the four traditional-episode pages of v3 (REVISION_V3 §3.5, §15): I2, I3b, K1, K2b.

Each is ONE flat spread, 3072x2048 (1.5:1 = the layout's spread quad), on the 2026 aged paper, UNLIT, with its static
inscription: `python -m shots._pages3` writes media/comp/pages/<ID>_page.png (+ pages_v3.json: focus points, plate
rects). The room teams map these onto the book; the full-frame comps (shots/I3b.py, K2b.py, I2page.py, K1page.py)
push from the whole spread (the LAP_ots_push_end framing, u 0.031..0.969 v 0.105..0.895) into the picture under the torch.
"""
import json

import cv2
import numpy as np

from tools.ink import *
from tools.ink.core import ROOT
from tools.ink.inscription import inscription, FONT as BRUSH_FONT
from tools.ink.cliff import load_font
from PIL import Image, ImageDraw

SW, SH = 3072, 2048
Z0 = 1920.0 / (0.938 * SW)
PXI = 60.0 / Z0                                       # inscription px on the page: 60 px at the full-spread framing
D = 'design/plates/H_v3_pages/'
SLIPS = [(3449, 1896), (3687, 1960), (3935, 2026), (4173, 2092), (4444, 2162), (4704, 2231), (4947, 2298)]
NAMES = ['佛老', '菩萨', '罗汉', None, '观音', '圣帝', '玄灵']       # 西游记 ch.5's guest list; the 4th place is bare

# id: plate, inscription key, inscription box on the page (blank corner opposite the picture's mass), focus (page px)
PAGES = {
    'I2': dict(plate=D + 'I2_a_2.jpg', plate_b=D + 'I2_b_1.jpg', key='I2', box=(820, 830, 340, 830), focus=(560, 1500)),
    'I3b': dict(plate=D + 'I3b_1.jpg', key='I3', box=(330, 1010, 330, 760), focus=(2540, 1290)),
    'K1': dict(plate=D + 'K1_2.jpg', key=None, box=None, focus=(1150, 1330)),
    'K2b': dict(plate=D + 'K2b_1.jpg', key='K2', box=(1560, 260, 200, 700), focus=(2420, 1420)),
}


def banquet_slips(raw):
    """I3b: remove the slip at the bare seat, typeset a name on every other slip (never model-drawn)."""
    h, w = raw.shape[:2]
    k = w / 5056.0
    img = (np.clip(raw, 0, 1) * 255).astype(np.uint8)
    x, y = SLIPS[3]
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (int((x - 52) * k), int((y - 78) * k)), (int((x + 52) * k), int((y + 70) * k)), 255, -1)
    x0, y0, x1, y1 = int((x - 150) * k), int((y - 170) * k), int((x + 150) * k), int((y + 170) * k)
    img[y0:y1, x0:x1] = cv2.inpaint(img[y0:y1, x0:x1], m[y0:y1, x0:x1], 9, cv2.INPAINT_TELEA)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    px = int(38 * k)
    f = load_font(BRUSH_FONT, px)
    for (x, y), name in zip(SLIPS, NAMES):
        if name:
            for i, ch in enumerate(name):
                d.text((x * k, (y - 22 + i * 40) * k), ch, font=f, fill=(38, 32, 28), anchor='mm')
    return np.asarray(im, np.float32) / 255.0


def build(pid, which='plate'):
    """-> (page RGB unlit, bare paper RGB, info)."""
    p = PAGES[pid]
    paper = Paper(SW, SH, 'aged', seed=27, gutter=SW // 2)
    raw = load_image(ROOT / p[which])
    if pid == 'I3b':
        raw = banquet_slips(raw)
    if pid == 'K1':                                   # the gate's signboard, typeset (plaques read right to left)
        k = raw.shape[1] / 5056.0
        im = Image.fromarray((np.clip(raw, 0, 1) * 255).astype(np.uint8))
        f = load_font('refs/fonts/guangekai/館閣楷-Regular.ttf', int(78 * k))
        for i, ch in enumerate('界冥幽'):
            ImageDraw.Draw(im).text(((612 + i * 88) * k, 774 * k), ch, font=f, fill=(40, 30, 26), anchor='mm')
        raw = np.asarray(im, np.float32) / 255.0
    raw = cv2.resize(raw, (SW, SH), interpolation=cv2.INTER_AREA if raw.shape[1] > SW else cv2.INTER_CUBIC)
    T = key_paper(raw, lo=0.015, hi=0.08, gain=2.6) if pid == 'K1' else key_paper(raw, lo=0.035, hi=0.13)
    page = paper.rgb * T
    if p['key']:
        ins = inscription((SW, SH), p['key'], p['box'], px=PXI, paper=paper, seed=7)
        ins.draw(page)
    return np.clip(page, 0, 1).astype(np.float32), paper.rgb, p


def torch(frame, pos, radius, s, ambient=0.10, gain=1.3, seed=3):
    """The flashlight on the page (same field as the v2 heaven shots)."""
    from shots._heaven import light_field, lit
    H, W = frame.shape[:2]
    return lit(frame, light_field(W, H, pos, radius, ambient=ambient, gain=gain, stretch=1.15, seed=seed))


class PageShot:
    """A full-frame comp of one page: push from the whole spread into the picture, torch following the focus."""

    def __init__(self, ctx, pid, t0, t1, z1=1.25, focus=None, focus_b=None, t_b=None, radius=(1500, 620), hold=0.2,
                 ambient=0.26, start=None, clip=None, clip_start=0.3):
        self.page, self.bare, p = build(pid)
        self.page_b = build(pid, 'plate_b')[0] if t_b is not None else None
        self.t_b = t_b
        self.focus = focus or p['focus']
        self.cam = push_cam(t0, t1, self.focus, z1, hold) if start is None else Camera(
            [(t0, start[0], start[1], start[2]), (t1 + 0.3, self.focus[0], self.focus[1], z1, 'inout')])
        self.t0, self.t1, self.radius, self.ambient = t0, t1, radius, ambient
        # §13 alive pass: a video-model clip of THIS page (first frame = the page at the full-spread framing, locked
        # camera) replaces the still inside that framing; camera and torch stay ours. Tone is matched to the still.
        self.clip = None
        if clip:
            from tools.ink.video import decode
            x0, x1, y0, y1 = int(.031 * SW), int(.969 * SW), int(.105 * SH), int(.895 * SH)
            n = int(round((t1 - t0) * 24)) + 2
            fr = []
            for ts, im in decode(str(ROOT / clip), start=clip_start, dur=n / 24.0 + 0.2, height=1440):
                fr.append((np.clip(im, 0, 1) * 255).astype(np.uint8))
            ref = self.page[y0:y1, x0:x1]
            f0 = cv2.resize(fr[0].astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC)
            gain = blur(ref, 60) / np.maximum(blur(f0, 60), 1e-3)                 # low-frequency tone match
            yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0].astype(np.float32)
            e = np.minimum(np.minimum(xx, x1 - x0 - 1 - xx), np.minimum(yy, y1 - y0 - 1 - yy))
            self.clip = dict(fr=fr, box=(x0, y0, x1, y1), gain=np.clip(gain, 0.8, 1.25).astype(np.float32),
                             feather=smoothstep(0, 40, e)[..., None].astype(np.float32))

    def page_at(self, t):
        if self.t_b is not None and t >= on_frame(self.t_b) - 1e-9:
            return self.page_b
        if self.clip is None:
            return self.page
        c = self.clip
        x0, y0, x1, y1 = c['box']
        i = int(np.clip(round((t - self.t0) * 24), 0, len(c['fr']) - 1))
        im = cv2.resize(c['fr'][i].astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC) * c['gain']
        pg = self.page.copy()
        pg[y0:y1, x0:x1] += (im - pg[y0:y1, x0:x1]) * c['feather']
        return pg

    def render(self, t, ctx):
        from shots._mountain import view
        cx, cy, z = self.cam.at(t)[:3]
        src = self.page_at(t)
        f = view(src, cx, cy, z, ctx.W, ctx.H)
        zz = z * ctx.W / 1920.0
        fx, fy = (self.focus[0] - cx) * zz + ctx.W / 2, (self.focus[1] - cy) * zz + ctx.H / 2
        u = ramp(t, self.t0, self.t1, 'inout')
        r = (self.radius[0] + (self.radius[1] - self.radius[0]) * u) * ctx.s
        return torch(f, (fx, fy), r, ctx.s, ambient=self.ambient, gain=0.98)


def push_cam(t0, t1, focus, z1, hold=0.25, ease='inout'):
    return Camera([(t0, SW / 2, SH / 2, Z0), (t0 + hold, SW / 2, SH / 2, Z0), (t1 + 0.3, focus[0], focus[1], z1, ease)])


if __name__ == '__main__':
    import os, sys
    os.makedirs(ROOT / 'media/comp/pages', exist_ok=True)
    meta = {}
    for pid in (sys.argv[1:] or PAGES):
        if not os.path.exists(ROOT / PAGES[pid]['plate']):
            print('missing plate for', pid)
            continue
        page, _, p = build(pid)
        save_image(ROOT / f'media/comp/pages/{pid}_page.png', page)
        meta[pid] = dict(file=f'media/comp/pages/{pid}_page.png', size=[SW, SH], gutter_x=SW // 2, focus=p['focus'],
                         inscription_key=p['key'], inscription_box=p['box'], unlit=True, paper="Paper('aged', seed=27)")
        if pid == 'I2' and os.path.exists(ROOT / PAGES[pid]['plate_b']):
            pb, _, _ = build(pid, 'plate_b')
            save_image(ROOT / 'media/comp/pages/I2_page_b.png', pb)
        print('wrote', pid)
    fn = ROOT / 'media/comp/pages/pages_v3.json'
    old = json.load(open(fn)) if os.path.exists(fn) else {}
    old.update(meta)
    json.dump(old, open(fn, 'w'), indent=1, ensure_ascii=False)

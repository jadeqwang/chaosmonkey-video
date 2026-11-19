"""tools/world/carve.py: typeset carved characters into a card's UV space (they are part of the rock: they cannot drift).

    from tools.world.carve import Carving
    CV = Carving(card_rgba='design/world/cards/pillar_scripture_rgba.png', size=4096)    # texture height in px
    CV.field((0.30, 0.25, 0.70, 0.80), chars, px=70)        # uv rect (u0, v0, u1, v1), columns top->bottom, right->left
    CV.save('work/world/D5/carve_pillar')                     # -> <base>_cov.png (coverage) + <base>_id.png (glyph ids)
    o = Wd.card('pillar_scripture', ..., carve=CV.spec(lit=[(id, frame, gain), ...]))
    CV.glyphs  # [{id, ch, u, v, bbox}] ; world position: Wd.card_point(o, g['u'], g['v'])

Glyphs are placed only where the painted rock is solid and pale (alpha > 0.9, luminance above `pale`), so they sit on
the smooth faces and skip clefts. Ids start at 1 and are unique across all Carving objects made with the same `idbase`.
Font: the v3 carved-cliff seal script (崇羲篆体, refs/fonts/chongxi-seal) unless font= is given.
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEAL_FONT = 'refs/fonts/chongxi-seal/崇羲篆体.otf'


def qianziwen():
    s = open(os.path.join(ROOT, 'design/text/qianziwen.txt'), encoding='utf-8').read()
    return [c for c in s if '一' <= c <= '鿿']


class Carving:
    _next = [1]

    def __init__(self, card_rgba, size=4096, font=SEAL_FONT, pale=0.45, seed=0):
        im = Image.open(os.path.join(ROOT, card_rgba)).convert('RGBA')
        a = np.array(im).astype(np.float32) / 255
        self.H = size
        self.W = int(round(size * im.width / im.height))
        a = cv2.resize(a, (self.W, self.H), interpolation=cv2.INTER_AREA)
        lum = a[..., :3].mean(2)
        self.ok = ((a[..., 3] > 0.9) & (lum > pale)).astype(np.float32)
        self.ok = cv2.erode(self.ok, np.ones((5, 5), np.uint8))
        self.cov = np.zeros((self.H, self.W), np.float32)
        self.ids = np.zeros((self.H, self.W), np.int32)
        self.font_path = os.path.join(ROOT, font)
        self.glyphs = []
        self.rng = np.random.default_rng(seed)

    def _glyph(self, ch, px):
        f = ImageFont.truetype(self.font_path, int(px))
        im = Image.new('L', (int(px * 1.3), int(px * 1.3)), 0)
        ImageDraw.Draw(im).text((int(px * 0.65), int(px * 0.65)), ch, fill=255, font=f, anchor='mm')
        g = np.array(im).astype(np.float32) / 255
        # chisel: slightly weathered edge, a little uneven depth
        n = cv2.GaussianBlur(self.rng.random(g.shape).astype(np.float32), (0, 0), max(1, px / 40))
        n = (n - n.mean()) / (n.std() + 1e-6)
        g = np.clip(g * (0.9 + 0.1 * n) - 0.04 * np.clip(-n, 0, None), 0, 1)
        return g

    def field(self, rect, chars, px=64, col_pitch=1.25, row_pitch=1.12, need=0.8):
        """Fill uv rect with columns (right->left, top->bottom). chars: iterable consumed as needed. Returns placed glyphs."""
        u0, v0, u1, v1 = rect
        x0, x1, y0, y1 = u0 * self.W, u1 * self.W, v0 * self.H, v1 * self.H
        it = iter(chars)
        placed = []
        x = x1 - px * 0.6
        while x - px * 0.6 >= x0:
            y = y0 + px * 0.6
            while y + px * 0.6 <= y1:
                cx, cy = int(x), int(y)
                r = int(px * 0.5)
                cell = self.ok[max(cy - r, 0):cy + r, max(cx - r, 0):cx + r]
                if cell.size and cell.mean() >= need:
                    try:
                        ch = next(it)
                    except StopIteration:
                        return placed
                    g = self._glyph(ch, px)
                    gh, gw = g.shape
                    ya, xa = cy - gh // 2, cx - gw // 2
                    sl = (slice(max(ya, 0), min(ya + gh, self.H)), slice(max(xa, 0), min(xa + gw, self.W)))
                    gs = g[sl[0].start - ya:sl[0].stop - ya, sl[1].start - xa:sl[1].stop - xa]
                    gid = Carving._next[0]; Carving._next[0] += 1
                    self.cov[sl] = np.maximum(self.cov[sl], gs)
                    # the id fills the glyph's whole cell so the lookup is constant across its strokes
                    c0, c1 = max(cy - r, 0), min(cy + r, self.H)
                    d0, d1 = max(cx - r, 0), min(cx + r, self.W)
                    self.ids[c0:c1, d0:d1] = gid
                    rec = dict(id=gid, ch=ch, u=cx / self.W, v=cy / self.H, px=px,
                               bbox=[(cx - r) / self.W, (cy - r) / self.H, (cx + r) / self.W, (cy + r) / self.H])
                    self.glyphs.append(rec); placed.append(rec)
                y += px * row_pitch
            x -= px * col_pitch
        return placed

    def save(self, base):
        os.makedirs(os.path.dirname(os.path.join(ROOT, base)), exist_ok=True)
        self.base = base
        Image.fromarray((self.cov * 255).astype(np.uint8), 'L').save(os.path.join(ROOT, base + '_cov.png'))
        idrgb = np.dstack([(self.ids >> 8).astype(np.uint8), (self.ids & 255).astype(np.uint8), np.zeros_like(self.ids, np.uint8)])
        Image.fromarray(idrgb, 'RGB').save(os.path.join(ROOT, base + '_id.png'))
        return base

    def spec(self, lit=(), glow=(1.0, 0.72, 0.25), dark=0.55, base=0.75, col=(1, 1, 1), glow_fog=1.0, reveal=False, **kw):
        """reveal=True: a glyph appears at its lit frame. reveal='light': a glyph's strokes exist only behind its light's
        terminator (per pixel); lit entries (id, frame, gain, layer): layer 0 is cut by the card's `light`, 1 by `light2`.
        kw (reveal='light'): glow2, col2 (layer-1 glow / cut tint), revW (u over which a cut comes up), flashW (u over
        which the fresh-cut flash decays behind the edge)."""
        d = dict(cov=self.base + '_cov.png', id=self.base + '_id.png', lit=[list(x) for x in lit], glow=list(glow), dark=dark,
                 base=base, col=list(col), glowFog=glow_fog, reveal=reveal)
        for k in ('glow2', 'col2'):
            if k in kw:
                d[k] = list(kw.pop(k))
        d.update(kw)
        return d

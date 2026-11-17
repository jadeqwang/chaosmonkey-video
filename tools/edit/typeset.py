"""Minimal type for the edit: variable-font faces, tracked text on a baseline, rows fitted to a safe width, a soft dark
'shade' halo and a glow (after holdfire's render/src/type.js: shade = void #05070d halo, blur 0.45 x size).

Coordinates are design pixels at 1920x1080; pass `k` (output width / 1920) to scale everything.
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import FONTS

# holdfire palette (render/src/palette.js)
CREAM = (0xf3, 0xee, 0xe4)
GOLD = (0xf4, 0xb4, 0x43)
GOLD_PALE = (0xff, 0xe2, 0xa3)
BOOK_GOLD = (0xb8, 0xa8, 0x8a)
DIM = (219, 209, 189)          # rgb(.86,.82,.74)
VOID = (0x05, 0x07, 0x0d)

FACES = {
    'Archivo': FONTS / 'Archivo-VF.ttf',
    'OpenSans': FONTS / 'OpenSans-VF.ttf',
    'CormorantI': FONTS / 'CormorantGaramond-Italic-VF.ttf',
    'Mono': FONTS / 'IBMPlexMono-Medium.ttf',
}


@lru_cache(maxsize=256)
def font(face, size, weight=None, width=None):
    """A FreeType font at a (float) pixel size with its variable axes set by name (Weight, Width)."""
    f = ImageFont.truetype(str(FACES[face]), size=max(1.0, float(size)))
    try:
        axes = f.get_variation_axes()
    except OSError:          # not a variable font
        return f
    vals = []
    for ax in axes:
        name = ax['name'].decode() if isinstance(ax['name'], bytes) else ax['name']
        v = {'Weight': weight, 'Width': width}.get(name)
        vals.append(min(max(v if v is not None else ax['default'], ax['minimum']), ax['maximum']))
    f.set_variation_by_axes(vals)
    return f


def measure(text, st, k=1.0):
    """Advance width in output px of `text` in style st = {face, size, weight, width, track (em)}."""
    f = font(st['face'], st['size'] * k, st.get('weight'), st.get('width'))
    tr = st.get('track', 0) * st['size'] * k
    return f.getlength(text) + tr * max(0, len(text) - 1)


def draw_text(mask, text, x, y, st, k=1.0):
    """Draw text (white) into an 'L' mask with its left-baseline at (x, y) output px. Tracking keeps kerning: char i sits
    at getlength(text[:i]) + i * track."""
    f = font(st['face'], st['size'] * k, st.get('weight'), st.get('width'))
    d = ImageDraw.Draw(mask)
    tr = st.get('track', 0) * st['size'] * k
    if not tr:
        d.text((x, y), text, font=f, fill=255, anchor='ls')
        return
    for i, ch in enumerate(text):
        d.text((x + f.getlength(text[:i]) + i * tr, y), ch, font=f, fill=255, anchor='ls')


class Layer:
    """An RGBA text layer built from styled runs; colour is kept premultiplied by alpha (so 'over' is exact)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)

    def _over(self, color, alpha):
        c = np.asarray(color, np.float32)[None, None, :] / 255.0
        self.rgb = self.rgb * (1 - alpha[..., None]) + c * alpha[..., None]
        self.a = self.a + alpha * (1 - self.a)

    def text(self, runs, y, k=1.0, cx=960, safe=864, min_px=22, shade=0.75, glow=0, alpha=1.0, min_check=True):
        """A centred row of runs [(text, style), ...] on baseline y (design px), shrunk to fit `safe` design px.
        Raises if fitting would push any run under min_px design px."""
        ws = [measure(t, s) for t, s in runs]
        tot = sum(ws)
        fit = min(1.0, safe / tot) if tot else 1.0
        if min_check:
            for (t, s) in runs:
                if s['size'] * fit < min_px - 1e-6:
                    raise ValueError(f'{t!r} would be {s["size"] * fit:.1f} px (< {min_px}) to fit {safe} px')
        x = (cx - tot * fit / 2) * k
        mask = Image.new('L', (self.w, self.h), 0)
        sizes = []
        for (t, s), w in zip(runs, ws):
            s2 = dict(s, size=s['size'] * fit)
            draw_text(mask, t, x, y * k, s2, k)
            x += w * fit * k
            sizes.append(s2['size'])
        m = np.asarray(mask, np.float32) / 255.0
        size = max(sizes) * k
        if shade:   # dark halo first (soft, wide), as holdfire's type.js
            h = np.asarray(mask.filter(ImageFilter.GaussianBlur(size * 0.45 / 2)), np.float32) / 255.0
            self._over(VOID, np.clip(h * 1.6, 0, 1) * shade * alpha)
        # colour per run: redraw each run into its own mask so runs can differ in colour
        x = (cx - tot * fit / 2) * k
        for (t, s), w in zip(runs, ws):
            rm = Image.new('L', (self.w, self.h), 0)
            draw_text(rm, t, x, y * k, dict(s, size=s['size'] * fit), k)
            x += w * fit * k
            ra = np.asarray(rm, np.float32) / 255.0
            if glow:
                g = np.asarray(rm.filter(ImageFilter.GaussianBlur(glow * k / 2)), np.float32) / 255.0
                self._over(s.get('color', CREAM), np.clip(g * 0.9, 0, 1) * 0.9 * alpha * s.get('alpha', 1))
            self._over(s.get('color', CREAM), ra * alpha * s.get('alpha', 1))
        return m

    def rule(self, y, width, thick, color, alpha, k=1.0, cx=960):
        a = np.zeros((self.h, self.w), np.float32)
        y0 = int(round((y - thick / 2) * k))
        y1 = max(y0 + 1, int(round((y + thick / 2) * k)))
        x0, x1 = int(round((cx - width / 2) * k)), int(round((cx + width / 2) * k))
        a[y0:y1, x0:x1] = alpha
        self._over(color, a)

    def rgba8(self):
        """Straight (un-premultiplied) RGBA, as PNG expects."""
        straight = self.rgb / np.maximum(self.a, 1e-6)[..., None]
        out = np.dstack([np.clip(straight, 0, 1), np.clip(self.a, 0, 1)])
        return (out * 255 + 0.5).astype(np.uint8)

    def on_black8(self):
        return (np.clip(self.rgb, 0, 1) * 255 + 0.5).astype(np.uint8)

"""Shared helpers for the HEAVEN & LEDGER shots (I3b J2 J5 K2b K3 K4 K5 + page art for I2/J1).

2026 light: everything is aged paper under a small white torch pool, darkness around (light.flashlight_field,
multiplied, never added). Lyrics are one switch: ctx.opts['lyrics'] (default on) or env INK_LYRICS=0.
"""
import os
import subprocess
import sys

import cv2
import numpy as np

from tools.ink import *
from tools.ink.light import flashlight_field, TORCH, NIGHT

ROOT = '/home/jade/Documents/chaosmonkey-video'
LEDGER = 'work/heaven/ledger/'
PLATE_LEDGER = 'design/plates/E_underworld/ledger/'
GARAMOND = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
WENKAI = 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'
SEALFONT = 'refs/fonts/chongxi-seal/崇羲篆体.otf'


from tools.ink.opts import lyrics_on   # noqa: E402  the one switch: ctx.opts['lyrics'] (env INK_LYRICS, default off)


def ensure_ledger():
    """The 8-page ledger (p1, p2 = plate; p7, p8 = plate p3/p4 layouts) for the page turns; built once."""
    if not os.path.exists(LEDGER + 'spread_7_8.png'):
        subprocess.run([sys.executable, 'shots/_heaven_ledger_pages.py'], check=True)


def light_field(W, H, pos, radius, ambient=0.12, gain=1.32, tilt=0.0, stretch=1.0, seed=0):
    """HxWx3 multiplier: torch pool + dim night. pos/radius in frame px."""
    I = flashlight_field(W, H, pos, radius, tilt, stretch, seed)
    L = I[..., None] * (gain * np.asarray(TORCH, np.float32))[None, None] + ambient * np.asarray(NIGHT, np.float32)
    return L.astype(np.float32)


def lit(frame, L):
    if os.environ.get('HL_NOLIGHT'):                     # QA: measure the ink of the page itself (qa reads the pool)
        return frame
    out = frame * L
    return np.clip(out, 0.012, 0.985, out=out).astype(np.float32)


def fit(img, W, H, scale, x0, y0, bg=None):
    """The image scaled by `scale` with its pixel (x0, y0) at frame (0, 0); area filter, sub-pixel exact."""
    M = np.float32([[scale, 0, -x0 * scale], [0, scale, -y0 * scale]])
    src = img
    s = scale
    # pre-shrink by powers of two so the affine stays sharp but not aliased
    k = 1
    while s * 2 <= 1.0 and min(src.shape[:2]) > 64:
        src = cv2.resize(src, (src.shape[1] // 2, src.shape[0] // 2), interpolation=cv2.INTER_AREA)
        s *= 2
        k *= 2
    M = np.float32([[s, 0, -x0 * scale], [0, s, -y0 * scale]])
    bv = (0, 0, 0, 0) if bg is None else tuple(float(v) for v in bg)
    out = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC if s > 1 else cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=bv)
    return out.astype(np.float32)


def to_frame(p, scale, x0, y0):
    return ((p[0] - x0) * scale, (p[1] - y0) * scale)


def lyric(frame, ctx, text, y=0.93, x=0.5, px=30, opacity=1.0, ground='auto'):
    if lyrics_on(ctx) and text:
        subtitle(frame, text, GARAMOND, px=px, y=y, x=x, ground=ground, opacity=opacity, font_cjk=WENKAI)
    return frame


def line_at(ctx, t, lines):
    """lines: [(text, start, end)] -> the text due at t (with a short tail)."""
    for txt, a, b in lines:
        if a - 0.05 <= t < b + 0.25:
            return txt
    return None


def sung(ctx, line, t, tail=0.8):
    """The words of `line` already sung at t (word onsets), or None after the line + tail."""
    try:
        ws = ctx.timing.words(line)
    except Exception:
        return None
    if not ws or t < ws[0][1] - 0.02 or t > ws[-1][2] + tail:
        return None
    return ' '.join(w for w, a, b in ws if a <= t + 0.02)


def line_words(ctx, text_start, near):
    """[(word, start, end)] of the lyric line starting with `text_start` whose first word is nearest song time `near`
    (the same line text recurs; Timing.words() returns the first)."""
    best = None
    for l in ctx.timing.lines:
        ws = l.get('words') or []
        if not ws or not str(l.get('text', '')).startswith(text_start):
            continue
        d = abs(float(ws[0]['start']) - near)
        if best is None or d < best[0]:
            best = (d, [(str(w.get('w', w.get('word', w.get('text', '')))), float(w['start']),
                         float(w.get('end', float(w['start']) + 0.3))) for w in ws])
    return best[1] if best else []


def sung_words(ws, t, tail=0.8):
    if not ws or t < ws[0][1] - 0.02 or t > ws[-1][2] + tail:
        return None
    return ' '.join(w for w, a, b in ws if a <= t + 0.02)

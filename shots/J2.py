"""J2 (190.875-192.833, drop 2 downbeat) 'the page lights, then the mountain'.

Starts on the carved, lit 花果山 peak (heaven close plate, columns of 千字文 cut into its faces with tools.ink.cliff, raking
warm light, cinnabar in the cuts) and begins the film's second and last pull-back: 花果山 becomes one lit peak among many
in the blue-green heaven (close -> mid on the plates' registration chain, crossfaded while both are at the same scale,
so the crossing is invisible). The torch stays on 花果山 (anchored to the page), so its pool shrinks as we pull back.
Seal: the name seal 悟空 is pressed on the downbeat (190.885), then pressed again without re-inking on the echoes
'(formed)' 191.51 and 192.37 (`echoes`); under each echo, for ~10 frames, a small head keyed as pale ink: Mama
(from mama_B_expressions), then little Jade (lj_C_expressions_mouths). No chops fall inside J2: no mis-registration.

Polish-1: the first ~20 frames are back on paper: the aged page under a wide flashlight-white pool (J5's end-of-shot
light: centre near white, the bare paper falling off softly to a dim paper tone at the frame edges, never black), the
peak lit; from frame ~16 to ~30 the light narrows to the original torch pool on 花果山 as the pull-back runs.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json

import cv2
import numpy as np

from tools.ink import *
from tools.ink.cliff import Cliff
from _heaven import *

T0, T1 = 190.875, 192.83333333333334
REG = json.load(open('design/plates/D_heaven/D_heaven_registration.json'))
CLOSE_POS = (786.0, 242.0)
CLOSE_K = 1.0 / REG['close']['scale_close_per_mid_px']
STONE = tuple(REG['huaguoshan_stone']['mid_px'])          # (1880, 452)
START = (1878, 640, 2.05)                                  # mid px, zoom (2.05 mid -> ~0.97 close px per frame px)
END = (2300, 1100, 0.55)
POOL = (1880, 700, 560)                                    # torch on 花果山 (mid px, radius)
HEADS = [('design/characters/mama/mama_B_expressions.jpg', (1390, 150, 2060, 860)),
         ('design/characters/little_jade/lj_C_expressions_mouths.jpg', (160, 170, 480, 560))]


def carved_close(cells_only=False):
    im = load_image('design/plates/D_heaven/D_heaven_close.png')
    x0, y0, x1, y1 = 1750, 600, 3000, 2600
    crop = im[y0:y1, x0:x1].copy()
    lines = [l.strip() for l in open('design/text/qianziwen.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
    text = ''.join(lines[:60])
    c = Cliff(crop, text, SEALFONT, size=64, region=(120, 230, 1180, 1960), weather=0.25, moss=0.0,
              presence='auto', seed=3)
    if cells_only:                                       # v3: where each character sits, in mid-plate px
        return {ch: (CLOSE_POS[0] + (x0 + cx) * CLOSE_K, CLOSE_POS[1] + (y0 + cy) * CLOSE_K) for ch, cx, cy, _, _ in c.cells}
    out = c.render(light=(200, 10, 0.9), fill=0.55)
    im[y0:y1, x0:x1] = out
    return key_paper(im)


def build_mid():
    T = key_paper(load_image('design/plates/D_heaven/D_heaven_mid.png'))
    P = Paper(T.shape[1], T.shape[0], 'aged', seed=19, scale=2.0)
    return (P.rgb * T).astype(np.float32), P.rgb.astype(np.float32)


def head(path, box, px):
    im = load_image(path)
    x0, y0, x1, y1 = box
    c = im[y0:y1, x0:x1]
    g = np.median(np.concatenate([c[:20].reshape(-1, 3), c[:, :20].reshape(-1, 3)]), 0)
    d = np.clip(1 - luma(c) / luma(g[None, None]), 0, 1)
    d = d * smoothstep(0.05, 0.2, d)
    # soft oval vignette so the crop has no edge
    h, w = d.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w * 0.5), (yy - h * 0.47) / (h * 0.52))
    d = d * smoothstep(1.0, 0.8, r)
    s = px / h
    return resize(d.astype(np.float32), int(w * s), int(h * s)) ** 1.4 * 0.30


def pool_field(W, H, pos, radius, stretch=1.25, seed=5):
    """fix2: a hard-edged torch pool (no bloom): flat plateau, a narrow uneven edge, intensity 0..1."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (xx - pos[0]) / stretch, yy - pos[1]
    r = np.hypot(dx, dy) / max(radius, 1.0)
    th = np.arctan2(dy, dx)
    wob = 0.03 * np.sin(3 * th + seed) + 0.02 * np.sin(7 * th + 2.1 * seed)
    edge = smoothstep(1.0 + wob + 0.035, 1.0 + wob - 0.035, r)
    plate = 1.0 - 0.10 * smoothstep(0.2, 1.0, r)                     # the plateau falls off a touch toward its rim
    return (edge * plate).astype(np.float32)


def setup(ctx):
    global SC_, CAM, CLOSE_T, NAME, HITS, POSN, HEAD_D, PAPER_MID
    Tc = ctx.cache('j2_close_carved', carved_close, deps=['design/plates/D_heaven/D_heaven_close.png'])
    mid, PAPER_MID = ctx.cache('j2_mid_aged', build_mid, deps=['design/plates/D_heaven/D_heaven_mid.png'])

    class _Sheet:
        rgb = mid
    SC_ = Scene(mid.shape[1], mid.shape[0], paper=_Sheet())
    zc = lambda t: CAM.at(t)[2]
    # the close plate over the mid, at its registered rect; it hands over while both are below 1:1
    SC_.add(Tc, kind='ink', pos=CLOSE_POS, scale=CLOSE_K,
            opacity=lambda t: float(smoothstep(1.05, 1.55, zc(t))))
    CAM = Camera([(T0, *START), (T1 + 0.12, *END, 'sine')])
    NAME = seal('悟空', SEALFONT, 150 * ctx.s, 'zhu', wear=0.3, seed=1)
    tm = ctx.timing
    kick = [h['t'] for h in tm.hits('kick', 190.80, 190.95)]
    HITS = [kick[0] if kick else 190.885, 191.51, 192.37]
    # in the bare sky right of 花果山, then left of it, then lower right: each press a little off the last
    POSN = [(1440 * ctx.s, 250 * ctx.s), (1650 * ctx.s, 470 * ctx.s), (330 * ctx.s, 200 * ctx.s)]
    HEAD_D = [head(p, b, 230 * ctx.s) for p, b in HEADS]
    global WORDS, EDGES
    WORDS = line_words(ctx, 'Born', 190.0)
    # v3 (§3.2): the threads of D5 again, on this peak: true component jumps from 道 (辶), three generations on the
    # downbeat and the two beats after it; they fade as the pull-back takes the carving below reading size
    from shots import _tong
    cells = carved_close(cells_only=True)
    C_ = _tong.components(list(cells))
    st_ = next((c for c in '道過遐邇通' if c in cells), None) or next(c for c in cells if '辶' in C_[c])
    gens = _tong.chain(list(cells), start=st_, first='辶', per_jump=4, gens=3, pos=cells)
    _, ed = _tong.schedule(gens, [190.885, 191.0, 191.2], [0.08, 0.18, 0.3])
    EDGES = [(cells[a][0], cells[a][1], cells[b][0], cells[b][1], tt, g) for a, b, tt, g in ed]
    print('J2 threads from', st_, [len(g) for g in gens])


def render(t, ctx):
    st = CAM.at(t)
    f = SC_.render(t, CAM, ctx.size)
    cx, cy = SC_.to_frame(POOL[0], POOL[1], st, ctx.size)
    # fix2: the fullest frame of the film. The page stays lit to the edges (warm room light, the blue-green
    # neighbours readable), and a hard-edged torch pool holds 花果山 brighter; the pool keeps a good size in frame
    # while the camera pulls back (anchored to the peak, radius in frame px eased from 900 to 470)
    rad = (760 + (400 - 760) * float(smoothstep(T0, T1, t))) * ctx.s
    I = pool_field(ctx.W, ctx.H, (cx, cy), rad, stretch=1.2)
    warm = np.array([1.0, 0.93, 0.80], np.float32)
    L = (0.62 * warm)[None, None] + (I * 0.42)[..., None] * np.asarray(TORCH, np.float32)[None, None]
    u = float(smoothstep(T0 + 16 / 24, T0 + 30 / 24, t))
    if u < 1:                                   # polish-1: the page light of J5's end (wide pool, paper to the edges)
        Lp = light_field(ctx.W, ctx.H, (ctx.W * 0.5, ctx.H * 0.46), 1250 * ctx.s, ambient=0.16, gain=1.3, stretch=1.2,
                         seed=5)
        L = Lp * (1 - u) + L * u
    f = lit(f, L)
    from shots import _tong
    _tong.threads(f, t, EDGES, lambda x, y: SC_.to_frame(x, y, st, ctx.size), ctx.s, t_end=191.75,
                  colour=(1.0, 0.86, 0.42))
    # pale heads under the echo presses, ~10 frames each
    for k in ():                               # fix2: heads dropped (a smudge at speed; the echo must read as a seal)
        dt = t - HITS[k]
        if -1 / 48 <= dt < 10 / 24:
            a = 1.0 - smoothstep(7 / 24, 10 / 24, dt)
            d = HEAD_D[k - 1]
            x, y = POSN[k]
            lay_ink(f, ink_T(d * a), int(x - d.shape[1] / 2), int(y - d.shape[0] * 0.42))
    echoes(f, NAME, t, list(zip(HITS, POSN)), decay=0.80, seed=4)
    lyric(f, ctx, sung_words(WORDS, t, tail=0.0), y=0.955, px=28)
    return f

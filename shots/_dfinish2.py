"""shots/_dfinish2.py: finish a round-2 D flight render (shots/_dflight2.py) into D4 / D5 / D6 candidates. WORLD R2_3D.

Per frame: the 3D beauty (+ in D6 the monkey on his arc with a cloud trail, composited into the world BEFORE the grade)
-> day->dusk grade (ink-blue wash from the top, cooler, darker; the glow is NOT graded, so the lit country burns)
-> glow bloom (stronger toward dusk) -> screen-fixed paper grain -> the shot's static inscription.
    DF2_TAKE=r2a $PY shots/_dfinish2.py D4 D5 D6 [--full] [--typeset]
--typeset: also write the typeset-only composite frames work/world/Dflight_<take>/typeset_rgba/NNNN.png (RGBA:
typeset premult / alpha from the render's typeset + typeset_a passes, plus the bloomed glow added into RGB, plus the
2D inscription) for the paint team.
Candidates: work/world/_cand/<SHOT>_<take>.mp4, sheets work/review/comp_v4/_cand/<SHOT>_<take>.jpg.
"""
import json
import math
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.world.scene import paper_grain, encode, sheet, ROOT  # noqa: E402
from tools.ink.inscription import inscription  # noqa: E402
from tools.ink.paper import Paper  # noqa: E402
from _dmonkey import project, summit, STAGE_T, STAGE_FOOT  # noqa: E402

RANGES = {'D4': (0, 33), 'D5': (33, 134), 'D6': (134, 204)}
INS = {'D4': dict(text='一通百通'), 'D5': dict(key='D5'), 'D6': None}
TAKE = os.environ.get('DF2_TAKE', 'r2a')
SRC = os.path.join(ROOT, f'work/world/Dflight_{TAKE}')
GRADE = {'r2a': dict(wash=0.55, warm=0.0), 'r2b': dict(wash=0.85, warm=0.0), 'r2c': dict(wash=0.6, warm=0.07)}[TAKE]
INK = np.array([0.46, 0.54, 0.72], np.float32)        # ink-blue dusk wash (multiplied in at the top of the sky)
F_D6 = 134
MK_S = 0.36                                            # element scale: the standing figure ~440 px -> ~158 px (15 %)


def rd(ps, f):
    im = cv2.imread(os.path.join(SRC, 'frames', ps, f'{f:04d}.png'), cv2.IMREAD_COLOR)
    return None if im is None else cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def dusk_k(f):
    u = min(max((f - 40) / 125.0, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def grade(img, f):
    k = dusk_k(f)
    if k <= 0:
        return img
    H = img.shape[0]
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    g = np.clip(1 - y / 0.62, 0, 1) ** 1.5                                     # strongest at the top of the frame
    img = img * (1 - k * GRADE['wash'] * g * (1 - INK))
    img = img * np.array([1 - 0.07 * k, 1 - 0.05 * k, 1 - 0.01 * k], np.float32)
    if GRADE['warm']:
        band = np.exp(-((y - 0.62) / 0.10) ** 2)
        img = img * (1 + k * GRADE['warm'] * band * np.array([1.0, 0.55, 0.1], np.float32))
    return img


def bloom(img, glw, f):
    k = dusk_k(f)
    W = glw.shape[1]
    b = cv2.GaussianBlur(glw, (0, 0), W / 1920 * 6) * 0.9 + cv2.GaussianBlur(glw, (0, 0), W / 1920 * 22) * 0.7
    img = 1 - (1 - img) * (1 - np.clip(b * (1.6 + 1.8 * k), 0, 1))
    return img + glw * 0.15 * (1.2 + 2.4 * k), b


class Monkey:
    """STAGE's element on a somersault arc across the sky (relative to the summit as the camera sees it), landing on
    the middle pillar's summit at ~15 % of frame height; a trail of painted cloud puffs behind him."""

    def __init__(self):
        self.S = json.load(open(os.path.join(SRC, 'scene.json')))
        self.top = summit(self.S)
        self.c = {}
        for g in range(70):
            T = cv2.imread(os.path.join(ROOT, STAGE_T % g), 0).astype(np.float32) / 255
            ys, xs = np.nonzero(T < 0.7)
            self.c[g] = np.array([xs.mean(), ys.mean()])
        a = cv2.imread(os.path.join(ROOT, 'design/world/cards/cloud_head_1_rgba.png'), cv2.IMREAD_UNCHANGED)
        a = cv2.resize(a, (320, int(320 * a.shape[0] / a.shape[1])), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        self.cloud = (cv2.cvtColor(a[..., :3], cv2.COLOR_BGR2RGB), a[..., 3])
        self.pins = {}

    def pin(self, f):
        if f not in self.pins:
            self.pins[f] = project(self.S['camera'][f], self.top)
        return self.pins[f]

    def arc(self, g, f):
        pin = self.pin(f)
        P0 = pin + np.array([1150.0, -120.0]); P1 = pin + np.array([520.0, -560.0])
        P2 = pin + (self.c[30] - np.array(STAGE_FOOT)) * MK_S
        u = min(max(g / 30.0, 0.0), 1.0)
        return (1 - u) ** 2 * P0 + 2 * u * (1 - u) * P1 + u * u * P2

    def __call__(self, img, f):
        g = f - F_D6
        if g < 0:
            return img
        H, W = img.shape[:2]
        sc = H / 1080
        paper = np.array(self.S['camera'][f].get('paper', [0.925, 0.886, 0.8]), np.float32)
        # the trail first (behind him): puffs dropped along the arc, swelling and thinning away
        crgb, ca = self.cloud
        for k in range(1, 12):
            gp = g - 1.6 * k
            if gp < 0 or gp > 30:
                continue
            fade = (1 - k / 12.0) * (1 - min(max((g - 30) / 16.0, 0), 1))
            if fade <= 0.01:
                continue
            p = self.arc(gp, f) + np.array([0, 40 * MK_S / 0.36])
            w = (70 + 9 * k) * sc
            s = w / crgb.shape[1]
            M = np.array([[s, 0, p[0] * sc - crgb.shape[1] * s / 2], [0, s, p[1] * sc - crgb.shape[0] * s / 2]], np.float32)
            aw = cv2.warpAffine(ca, M, (W, H), flags=cv2.INTER_AREA)[..., None] * 0.85 * fade
            cw = cv2.warpAffine(crgb, M, (W, H), flags=cv2.INTER_AREA)
            img = img * (1 - aw) + cw * paper * aw
        p = os.path.join(ROOT, STAGE_T % min(g, 69))
        T = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        s = MK_S * sc
        if g < 30:
            t = self.arc(g, f) - self.c[g] * MK_S
        else:
            t = self.pin(f) - np.array(STAGE_FOOT) * MK_S + np.array([0, 2 * MK_S])
        M = np.array([[s, 0, t[0] * sc], [0, s, t[1] * sc]], np.float32)
        Tw = cv2.warpAffine(T, M, (W, H), flags=cv2.INTER_AREA, borderValue=(1.0, 1.0, 1.0))
        return img * Tw


def frames(shot, monkey=None, ts_out=None):
    a, b = RANGES[shot]
    G = paper_grain(1920, 1080)
    P = Paper(1920, 1080, 'new', seed=1988)
    ins = None
    if INS[shot]:
        ins = inscription((1920, 1080), INS[shot].get('key'), box=(1650, 110, 210, 720), paper=P, text=INS[shot].get('text'))
    for f in range(a, b):
        img = rd('beauty', f)
        glw = rd('glow', f)
        if monkey is not None:
            img = monkey(img, f)
        img = grade(img, f)
        img, blm = bloom(img, glw, f)
        img = img * G
        if ins is not None:
            ins.draw(img)
        if ts_out is not None:
            ts, ta = rd('typeset', f), rd('typeset_a', f)
            if ts is not None:
                A = ta[..., :1]
                rgb = ts + np.clip(blm * (1.6 + dusk_k(f)), 0, 1) * (1 - A) * 0.6     # glyphs + threads + halo
                A2 = np.clip(np.maximum(A[..., 0], (rgb.max(2))), 0, 1)
                ink = np.ones_like(img)
                if ins is not None:
                    ins.draw(ink)
                ia = 1 - ink.min(2)
                rgb = rgb * (1 - ia[..., None]) + ink * ia[..., None]
                A2 = np.maximum(A2, ia)
                os.makedirs(ts_out, exist_ok=True)
                out = np.dstack([np.clip(rgb, 0, 1), A2])
                cv2.imwrite(os.path.join(ts_out, f'{f:04d}.png'), cv2.cvtColor((out * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
        yield np.clip(img, 0, 1)


def run(shot, full=False, typeset=False):
    n = RANGES[shot][1] - RANGES[shot][0]
    out = f'work/world/_cand/{shot}_{TAKE}.mp4' if not full else f'work/world/_cand/full/{shot}_{TAKE}.mp4'
    mk = Monkey() if shot == 'D6' else None
    ims = list(frames(shot, mk, os.path.join(SRC, 'typeset_rgba') if typeset else None))
    encode(iter(ims), out, n, w=1920 if full else 960, h=1080 if full else 540)
    sheet(ims, f'work/review/comp_v4/_cand/{shot}_{TAKE}.jpg', label=f'{shot} {TAKE}')
    print(shot, n, '->', out)


if __name__ == '__main__':
    full = '--full' in sys.argv
    for s in [a for a in sys.argv[1:] if not a.startswith('--')]:
        run(s, full, '--typeset' in sys.argv)

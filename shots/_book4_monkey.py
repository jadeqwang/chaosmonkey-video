"""shots/_book4_monkey.py: the monkey that grows along the hero strand in H6 (BOOK v4 candidate A).

The drawing (gpt-image-2, tag bk4_H6_monkey_leap_notail: costume B in a few brush strokes, no tail of its own) is keyed
onto our paper, split into line (dark ink) and colour (washes), and drawn on through an ORDER map built from a
skeleton walked from the tail root: spine -> head and cap -> scarf -> arms -> legs; the colour follows the line.
It is anchored, every sub-frame, at the root of the hero strand (the strand IS his tail), turned to the strand's
local direction (smoothed), scaled with its depth. Numpy only (safe in forked workers).
"""
import math

import cv2
import numpy as np

from shots._mountain import *            # noqa: F401,F403
from shots import _book4_strokes as BS

SRC = 'work/book4/H56/monkey/bk4_H6_leap_notail.png'
ROOT_PX = np.array([1300.0, 752.0])       # where the tail leaves him (drawing px, 2048 x 1536)
TAIL_DIR = np.array([1.0, -0.12])         # the direction a tail would leave him in the drawing
BODY_PX = 1150.0                          # hip -> hands (drawing px)
# round 2: a second drawing for the somersault (tucked), crossfaded in while he turns over
SRC2 = 'work/book4/H56/monkey/bk4_H6_sault_notail.png'
ROOT2_PX = np.array([1335.0, 757.0])
TAIL2_DIR = np.array([1.0, 0.35])
BODY2_PX = 1000.0
SKEL = [
    [((1300, 750), .00), ((1120, 690), .10), ((950, 660), .20), ((820, 600), .28), ((720, 470), .36)],   # spine->head
    [((720, 470), .36), ((700, 400), .42), ((760, 320), .47), ((800, 240), .52)],                       # head, cap
    [((820, 600), .30), ((1000, 520), .42), ((1160, 470), .52)],                                          # scarf
    [((1300, 750), .02), ((1260, 860), .14), ((1200, 960), .24)],                                         # seat, skirt
    [((900, 660), .44), ((600, 690), .56), ((370, 700), .64), ((150, 620), .72)],                         # arm
    [((950, 760), .48), ((700, 860), .60), ((500, 960), .68), ((280, 1010), .76)],                        # arm
    [((1250, 800), .52), ((1550, 830), .64), ((1750, 840), .74), ((1910, 860), .82)],                     # leg
    [((1250, 900), .56), ((1500, 1050), .70), ((1700, 1110), .78), ((1880, 1190), .86)],                  # leg
]
DS = 2                                    # the drawing is kept at half resolution (1024 x 768)


def _order_map(h, w):
    pts, ts = [], []
    for chain in SKEL:
        for (a, ta), (b, tb) in zip(chain[:-1], chain[1:]):
            for u in np.linspace(0, 1, 40):
                pts.append((np.array(a) * (1 - u) + np.array(b) * u) / DS)
                ts.append(ta * (1 - u) + tb * u)
    pts, ts = np.array(pts), np.array(ts)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    best = np.full((h, w), 1e9, np.float32)
    order = np.zeros((h, w), np.float32)
    for p, t in zip(pts, ts):
        d = np.sqrt((xx - p[0]) ** 2 + (yy - p[1]) ** 2)
        m = d < best
        best[m] = d[m]
        order[m] = t
    return order + 0.06 * np.clip(best / (300.0 / DS), 0, 2)


class Monkey:
    @staticmethod
    def _load(src):
        """-> (line T, colour T): the ink line kept to its firm strokes (light fur hatching dropped), the colour
        thinned to a pale wash with the paper showing through and a little less saturation."""
        img = load_image(ROOT / src)
        img = cv2.resize(img, (img.shape[1] // DS, img.shape[0] // DS), interpolation=cv2.INTER_AREA)
        T = key_paper(img, lo=0.03, hi=0.12, gain=1.08)
        L = luma(img)
        sat = img.max(2) - img.min(2)
        dark = smoothstep(0.58, 0.34, L) * smoothstep(0.30, 0.12, sat)
        dark = np.clip(dark, 0, 1)[..., None]
        dl = (1 - T) * dark
        firm = smoothstep(0.22, 0.55, blur(dl.max(2), 1.2))[..., None]
        Tl = 1 - dl * (0.25 + 0.75 * firm)
        redm = smoothstep(0.18, 0.40, img[..., 0] - img[..., 1])[..., None]          # face and scarf keep their red
        dc = (1 - T) * (1 - dark) * (0.50 + 0.35 * redm)
        Tc = 1 - dc
        Tc = 0.78 * Tc + 0.22 * Tc.mean(2, keepdims=True)
        return Tl.astype(np.float32), Tc.astype(np.float32)

    def __init__(self, ctx):
        self.Tl, self.Tc = self._load(SRC)
        self.Tl2, self.Tc2 = self._load(SRC2)
        h, w = self.Tl.shape[:2]
        O = _order_map(h, w)
        O += (fbm(h, w, 6.0, 3, 'mk_ord', octaves=2) - 0.5) * 0.04
        self.O = O.astype(np.float32)
        self.s = ctx.s
        self.W, self.H = ctx.W, ctx.H
        # the anchor of every sub-frame, and the smoothed turn
        d = np.load(BS.WORK / 'sim/sim.npz')
        hero = int(d['hero'])
        rec = d['rec'][:, :, hero].reshape(BS.NFR, BS.SUBF, 2, BS.N, 3)
        cam = np.load(BS.WORK / 'sim/cam.npy')
        mid = rec.mean(2)                                                   # (F, K, N, 3)
        cc = cam[:, :, None, :]
        dz = mid[..., 2] - cc[..., 2]
        sx = self.W / 2 + BS.FOCAL * self.s * (mid[..., 0] - cc[..., 0]) / dz
        sy = self.H / 2 + BS.FOCAL * self.s * (mid[..., 1] - cc[..., 1]) / dz
        self.ax, self.ay = sx[..., 0], sy[..., 0]
        # his heading: the root's own flight direction (world), smoothed; the tail trails behind it
        F, K = BS.NFR, BS.SUBF
        rx = mid[..., :, 0].mean(-1).reshape(-1)
        ry = mid[..., :, 1].mean(-1).reshape(-1)
        def gsm(a, sig):
            k = np.exp(-0.5 * (np.arange(-4 * sig, 4 * sig + 1) / sig) ** 2)
            k /= k.sum()
            return np.convolve(np.pad(a, 4 * sig, mode='edge'), k, mode='same')[4 * sig:-4 * sig]
        vx = np.gradient(gsm(rx, 30))
        vy = np.gradient(gsm(ry, 30))
        head = np.unwrap(np.arctan2(vy, vx))
        body0 = math.atan2(-TAIL_DIR[1], -TAIL_DIR[0])
        # the turn of the strand itself (its root tangent): the somersault comes from the simulation's spin
        tx = (sx[..., 1:7].mean(-1) - sx[..., 0]).reshape(-1)
        ty = (sy[..., 1:7].mean(-1) - sy[..., 0]).reshape(-1)
        phi = np.unwrap(np.arctan2(ty, tx))
        ts = np.array([[(f * BS.STEPS + o) / (BS.FPS * BS.STEPS) for o in BS.SUB_STEPS] for f in range(F)]).reshape(-1)
        i0 = int(np.argmin(np.abs(ts - BS.T_SAULT)))
        wsp = np.clip((ts - BS.T_SAULT) / 0.15, 0, 1)
        th = np.where(ts < BS.T_SAULT, head - body0, head[i0] - body0) + wsp * (gsm(phi, 6) - gsm(phi, 6)[i0])
        self.th = gsm(th, 12).reshape(F, K)
        L_world = BS.scene_cached()['strokes'][hero].L * BS.HERO_SCALE
        mag = BS.FOCAL * self.s / dz[..., 0]
        self.scale = 0.85 * L_world * mag / (BODY_PX / DS)
        self.scale2 = self.scale * BODY_PX / BODY2_PX
        self.th2 = self.th + math.atan2(TAIL_DIR[1], TAIL_DIR[0]) - math.atan2(TAIL2_DIR[1], TAIL2_DIR[0])

    def progress(self, ts):
        pl = ramp(ts, BS.T_GROW + 0.10, BS.T_GROW + 0.82, 'linear')
        pc = ramp(ts, BS.T_GROW + 0.42, BS.T_GROW + 0.95, 'linear')
        return pl, pc

    def layer(self, ts):
        pl, pc = self.progress(ts)
        if pl <= 0:
            return None
        Al = smoothstep(pl * 1.08 - 0.05, pl * 1.08, -self.O + 2 * pl * 1.08 - 0.0) if False else \
            smoothstep(self.O - 0.03, self.O + 0.03, np.float32(pl * 1.06))
        Ac = smoothstep(self.O - 0.10, self.O + 0.10, np.float32(pc * 1.15))
        T = (1 - (1 - self.Tl) * Al[..., None]) * (1 - (1 - self.Tc) * Ac[..., None])
        return T.astype(np.float32)

    def tuck(self, ts):
        return float(smoothstep(BS.T_SAULT + 0.02, BS.T_SAULT + 0.16, ts) *
                     (1 - smoothstep(BS.T_SAULT + 0.56, BS.T_SAULT + 0.72, ts)))

    def draw(self, frame, ts, f, cam):
        T = self.layer(ts)
        if T is None:
            return frame
        wt = self.tuck(ts)
        T2 = (self.Tl2 * self.Tc2) if wt > 0 else None
        acc = np.zeros_like(frame)
        # 9 taps across the shutter, interpolated between the simulation's sub-frames (a smooth blur, no fan)
        rad = float(self.scale[f].max()) * 1100 / DS
        arc = abs(self.th[f, -1] - self.th[f, 0]) * rad + math.hypot(self.ax[f, -1] - self.ax[f, 0],
                                                                    self.ay[f, -1] - self.ay[f, 0])
        taps = np.linspace(2.0, BS.SUBF - 3.0, int(np.clip(math.ceil(arc / 4.0 * self.W / 1920 * 2), 5, 32)))   # a short shutter for him
        for q in taps:
            k0 = int(min(BS.SUBF - 2, math.floor(q)))
            u = q - k0
            L = lambda arr: arr[f, k0] * (1 - u) + arr[f, k0 + 1] * u
            a, sc, axp, ayp = L(self.th), L(self.scale), L(self.ax), L(self.ay)
            c, s_ = math.cos(a) * sc, math.sin(a) * sc
            rx, ry = ROOT_PX / DS
            M = np.float32([[c, -s_, axp - (c * rx - s_ * ry)], [s_, c, ayp - (s_ * rx + c * ry)]])
            Wp = cv2.warpAffine(T, M, (self.W, self.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                borderValue=(1.0, 1.0, 1.0))
            if T2 is not None:
                a2, sc2 = L(self.th2), L(self.scale2)
                c2, s2 = math.cos(a2) * sc2, math.sin(a2) * sc2
                qx, qy = ROOT2_PX / DS
                M2 = np.float32([[c2, -s2, axp - (c2 * qx - s2 * qy)], [s2, c2, ayp - (s2 * qx + c2 * qy)]])
                W2 = cv2.warpAffine(T2, M2, (self.W, self.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=(1.0, 1.0, 1.0))
                Wp = 1 - ((1 - Wp) * (1 - wt) + (1 - W2) * wt)
            acc += Wp
        frame *= acc / len(taps)
        return frame

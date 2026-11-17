"""FACES team: the 皮影 monkey rig cut from the canon puppet sheets, and car panes as shadow screens (F2 F4b F5 F6a).

Rig: parts are cut from design/characters/monkey/puppet_parts_colour.jpg (registered with the silhouette sheet; the
openwork and pivot holes stay open), pinned at the holes found on the sheet. The leather look is the colour sheet
divided by its paper and lifted (translucent hide against a lamp). Heads for 七十二变 come from the coloured row of
puppet_heads_swap.jpg (monkey, pine, bird, fish, cat), scaled to the rig's neck rivet.

Panes: a pane is a quad in the room plate (measured on the painted keyframe, media/kf/<SHOT>.jpg; the layout
sidecar quads do not match the paintings) plus a glass mask (the quad minus anything in front of the glass:
heads, headrests, mirror). A streetlight sweep is a hot spot passing across the pane; the puppet exists only where
it is lit: frame = plate * (1 - L) + L * lamp * T_puppet.
"""
import math
import os

import cv2
import numpy as np

from tools.ink import *
from tools.ink.core import F32
from tools.ink.puppet import Part, Puppet, LAMP, pose_at, cue_index, POSES

MK = 'design/characters/monkey'

# (bbox x, y, w, h on the sheet, pivot (own hole), {name: hole}) from the hole search on the parts sheets
PARTS = {
    'torso':   ((1306, 219, 404, 831), (1501, 521), {'neck': (1507, 256), 'shoulder': (1501, 421),
                                                     'hip_b': (1452, 683), 'hip_f': (1560, 682)}),
    'head':    ((375, 191, 282, 360), (476, 516), {'plume_b': (460, 242), 'plume_f': (564, 240)}),
    'plume':   ((1038, 170, 190, 753), (1171, 891), {}),
    'uarm_f':  ((2080, 234, 174, 384), (2124, 271), {'elbow': (2204, 560)}),
    'uarm_b':  ((1796, 231, 176, 383), (1928, 268), {'elbow': (1845, 557)}),
    'farm_f':  ((2102, 686, 111, 555), (2148, 727), {'grip': (2160, 1150)}),
    'farm_b':  ((1816, 676, 115, 561), (1880, 719), {}),
    'thigh':   ((1051, 1004, 211, 550), (1101, 1042), {'knee': (1098, 1511)}),
    'shin':    ((1572, 1116, 218, 481), (1624, 1156), {}),
    'staff':   ((219, 456, 52, 1097), (244, 1000), {}),
}
HEADS = {   # coloured row of the swap sheet: bbox, neck rivet
    'monkey': ((67, 812, 540, 736), (422, 1479)),
    'pine':   ((751, 880, 525, 669), (1068, 1478)),
    'bird':   ((1366, 890, 420, 661), (1655, 1479)),
    'fish':   ((1949, 871, 442, 679), (2159, 1479)),
    'cat':    ((2472, 921, 451, 631), (2767, 1479)),
}
HEAD_SCALE = 0.64           # swap-sheet rivets are 1.56x the parts-sheet rivets


def _cut(img, ground, bbox, pad=6, thr=0.16, scale=1.0):
    x, y, w, h = bbox
    H, W = img.shape[:2]
    x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(W, x + w + pad), min(H, y + h + pad)
    c = img[y0:y1, x0:x1]
    T = np.clip(c / ground[None, None], 0, 1)
    d = -np.log(np.clip(T, 1e-3, 1)).max(axis=2)
    m = (d > thr).astype(np.uint8)
    # keep the main piece and anything inside its outline (eyes, ear pieces); drop neighbours' fragments
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        main = 1 + int(np.argmax(st[1:, 4]))
        cnts, _ = cv2.findContours((lab == main).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        fill = np.zeros_like(m)
        cv2.drawContours(fill, cnts, -1, 1, -1)
        fill = cv2.dilate(fill, np.ones((5, 5), np.uint8))
        m = m * fill
    mk = blur(m.astype(F32), 0.7)
    # translucent hide: the dye lifted toward the light; burnished dark cut edge
    Tl = np.power(T, 0.55)
    edge = np.clip(mk - cv2.erode(mk, np.ones((5, 5), np.uint8)), 0, 1)
    Tl = Tl * (1 - 0.6 * edge[..., None])
    Tp = 1 - mk[..., None] * (1 - Tl)
    if scale != 1.0:
        Tp = cv2.resize(Tp, (int(Tp.shape[1] * scale), int(Tp.shape[0] * scale)), interpolation=cv2.INTER_AREA)
        mk = cv2.resize(mk, (Tp.shape[1], Tp.shape[0]), interpolation=cv2.INTER_AREA)
    return Tp.astype(F32), mk.astype(F32), (x0, y0)


def _ground(img):
    return np.median(np.concatenate([img[4:40, 4:40].reshape(-1, 3), img[-40:-4, -40:-4].reshape(-1, 3)]), axis=0)


def build_rig():
    """-> dict name -> (T, mask, pivot_local, holes_local) for parts and heads (picklable for ctx.cache)."""
    img = load_image(f'{MK}/puppet_parts_colour.jpg')
    g = _ground(img)
    out = {}
    for name, (bb, piv, holes) in PARTS.items():
        T, m, (x0, y0) = _cut(img, g, bb)
        out[name] = (T, m, (piv[0] - x0, piv[1] - y0), {k: (v[0] - x0, v[1] - y0) for k, v in holes.items()})
    hs = load_image(f'{MK}/puppet_heads_swap.jpg')
    g2 = _ground(hs)
    for name, (bb, piv) in HEADS.items():
        T, m, (x0, y0) = _cut(hs, g2, bb, scale=HEAD_SCALE)
        out['h_' + name] = (T, m, ((piv[0] - x0) * HEAD_SCALE, (piv[1] - y0) * HEAD_SCALE), {})
    return out


def _part(rig, key, name, parent=None, attach=(0, 0), z=0, rest=0.0, flip=False):
    T, m, piv, holes = rig[key]
    if flip:
        T, m = T[:, ::-1].copy(), m[:, ::-1].copy()
        piv = (m.shape[1] - 1 - piv[0], piv[1])
    p = Part(name, m, pivot=piv, parent=parent, attach=attach, z=z, rest=rest, outline=0)
    p.T = T
    return p


def make_puppet(rig, plumes=True, head='head'):
    """the monkey: torso root (pivot at the chest rivet). Faces right."""
    tor = rig['torso'][3]
    hd = rig['head'][3]
    ua_f, ua_b = rig['uarm_f'][3], rig['uarm_b'][3]
    th = rig['thigh'][3]
    parts = [
        _part(rig, 'torso', 'torso', z=0),
        _part(rig, 'uarm_b', 'arm_b', 'torso', tor['shoulder'], z=-3),
        _part(rig, 'farm_b', 'forearm_b', 'arm_b', ua_b['elbow'], z=-4),
        _part(rig, 'thigh', 'thigh_b', 'torso', tor['hip_b'], z=-2),
        _part(rig, 'shin', 'shin_b', 'thigh_b', th['knee'], z=-2.5),
        _part(rig, 'thigh', 'thigh_f', 'torso', tor['hip_f'], z=1),
        _part(rig, 'shin', 'shin_f', 'thigh_f', th['knee'], z=1.5),
        _part(rig, 'uarm_f', 'arm_f', 'torso', tor['shoulder'], z=3),
        _part(rig, 'farm_f', 'forearm_f', 'arm_f', ua_f['elbow'], z=4),
        _part(rig, 'staff', 'staff', 'forearm_f', rig['farm_f'][3]['grip'], z=5),
    ]
    if head == 'head':
        parts.append(_part(rig, 'head', 'head', 'torso', tor['neck'], z=2))
        if plumes:
            parts.append(_part(rig, 'plume', 'plume_b', 'head', hd['plume_b'], z=1.8, rest=34))
            parts.append(_part(rig, 'plume', 'plume_f', 'head', hd['plume_f'], z=2.2, rest=18))
    else:
        parts.append(_part(rig, head, 'head', 'torso', tor['neck'], z=2))
    return Puppet(parts, reach=1500)            # chest pivot to plume tip / staff end, sheet px


def head_parts(rig):
    tor = rig['torso'][3]
    return {k: _part(rig, 'h_' + k, 'head', 'torso', tor['neck'], z=2) for k in HEADS}


# poses: degrees, + swings a hanging limb forward (to the right); staff angle is relative to the forearm.
# A 武生 vocabulary in hard holds: stand, guard, strike, shade (hand shading the eyes), crouch, leap, salute.
P = {
    'stand':  dict(head=0, arm_f=25, forearm_f=70, staff=-80, arm_b=-12, forearm_b=15, thigh_f=8, shin_f=-6,
                   thigh_b=-8, shin_b=-3),
    'guard':  dict(head=-6, arm_f=70, forearm_f=75, staff=-150, arm_b=110, forearm_b=45, thigh_f=55, shin_f=-75,
                   thigh_b=-25, shin_b=-8, _y=20),
    'strike': dict(head=8, arm_f=110, forearm_f=10, staff=-30, arm_b=-60, forearm_b=-25, thigh_f=65, shin_f=-55,
                   thigh_b=-48, shin_b=12, _rot=10, _y=30),
    'shade':  dict(head=12, arm_f=150, forearm_f=95, staff=20, arm_b=-30, forearm_b=65, thigh_f=95, shin_f=-110,
                   thigh_b=-5, shin_b=0),
    'crouch': dict(head=4, arm_f=60, forearm_f=90, staff=-95, arm_b=40, forearm_b=95, thigh_f=85, shin_f=-120,
                   thigh_b=55, shin_b=-115, _y=95, _rot=8),
    'leap':   dict(head=-10, arm_f=155, forearm_f=15, staff=60, arm_b=-95, forearm_b=-20, thigh_f=80, shin_f=-95,
                   thigh_b=-65, shin_b=-45, _y=-110, _rot=-12),
    'salute': dict(head=-4, arm_f=95, forearm_f=120, staff=-120, arm_b=95, forearm_b=125, thigh_f=20, shin_f=-15,
                   thigh_b=-20, shin_b=-5),
}


def run_poses(n=8):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        s, c = math.sin(a), math.cos(a)
        out.append(dict(head=-4 + 4 * c, arm_f=50 * s + 25, forearm_f=70 + 20 * s, staff=-95 - 15 * s,
                        arm_b=-50 * s + 10, forearm_b=55 - 20 * s, thigh_f=48 * s + 14,
                        shin_f=-50 + (35 * c if s < 0 else -10), thigh_b=-48 * s + 14,
                        shin_b=-50 + (-35 * c if s > 0 else -10), _rot=12, _y=-16 * abs(c)))
    return out


# ------------------------------------------------------------------------------------------------ room and panes

def room_plate(shot, W, H):
    """the painted keyframe if it exists, else the layout's lit render; cover-fit to W x H."""
    p = f'media/kf/{shot}.jpg'
    if not os.path.exists(p):
        p = f'media/layout/car26/{shot}_lit.png'
    im = load_image(p)
    sc = H / im.shape[0]
    w = int(round(im.shape[1] * sc))
    if w < W:
        sc = W / im.shape[1]
        w = W
    h = int(round(im.shape[0] * sc))
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    x0, y0 = (w - W) // 2, (h - H) // 2
    return np.ascontiguousarray(im[y0:y0 + H, x0:x0 + W]).astype(F32), p


def glass_mask(plate, poly, s, exclude=()):
    """quad/poly (1080p px) -> HxW mask of the glass inside it (violet dusk glass, or amber-lit glass), minus
    anything dark or textured in front of it, minus explicit `exclude` polygons."""
    H, W = plate.shape[:2]
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.int32(np.array(poly) * s)], 1)
    hsv = cv2.cvtColor((plate * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(F32)
    h, sat, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    vv = cv2.GaussianBlur(v, (0, 0), 1.5 * s)
    tex = cv2.GaussianBlur(np.abs(cv2.Laplacian(vv, cv2.CV_32F)), (0, 0), 5 * s)
    violet = (h > 108) & (h < 150) & (v > 105)
    amber = (h > 5) & (h < 30) & (v > 165) & (sat < 150)
    g = ((violet | amber) & (tex < 2.2)).astype(np.uint8)
    k = max(3, int(9 * s) | 1)
    g = cv2.morphologyEx(g, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    poly_m = m.copy()
    m = m * g
    # grow back to the painted frame lines (the texture test leaves a rim), but never over dark paint
    kd = max(3, int(15 * s) | 1)
    m = cv2.dilate(m, np.ones((kd, kd), np.uint8)) * cv2.dilate(poly_m, np.ones((kd, kd), np.uint8))
    for ex in exclude:
        cv2.fillPoly(m, [np.int32(np.array(ex) * s)], 0)
    gate = np.clip((v / 255.0 - 0.30) / 0.15, 0, 1)
    return blur(m.astype(F32) * gate, 1.0 * s)


class Pane:
    """a glass pane as a shadow screen. quad = TL, TR, BR, BL in 1080p frame px; local screen is lw x lh px."""

    def __init__(self, ctx, plate, quad, exclude=(), lw=900, poly=None):
        s = ctx.s
        self.ctx = ctx
        q = np.float32(quad) * s
        wq = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
        hq = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
        self.lw, self.lh = int(lw), int(lw * hq / wq)
        src = np.float32([[0, 0], [self.lw, 0], [self.lw, self.lh], [0, self.lh]])
        self.Hm = cv2.getPerspectiveTransform(src, q)
        self.mask = glass_mask(plate, poly if poly is not None else quad, s, exclude)
        ys, xs = np.nonzero(self.mask > 0.01)
        self.box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else (0, 0, 1, 1)
        self.yy, self.xx = np.mgrid[0:self.lh, 0:self.lw].astype(F32)
        self.grain = 0.93 + 0.07 * fbm(self.lh, self.lw, 40, 7, 'pane', len(quad))

    def light(self, lx, ly, radius, inten):
        """local light field: a lamp behind the glass at local (lx, ly)."""
        r = np.hypot(self.xx - lx, self.yy - ly) / radius
        I = 0.70 * np.exp(-(r / 0.75) ** 2) + 0.30 / (1.0 + (r / 1.0) ** 2) ** 2
        return np.clip(I * inten, 0, 1.0)

    def lay(self, f, T_local, L_local, lift=0.04, light_xy=None, colour=LAMP, gain=1.0):
        """composite into frame f (in place): the lit glass with the puppet shadow on it."""
        if L_local.max() < 0.01:
            return f
        T = T_local
        if lift > 0 and light_xy is not None:              # the hide stands off the glass: magnified, softened
            k = 1 + lift
            lx, ly = light_xy
            M = np.float32([[k, 0, lx * (1 - k)], [0, k, ly * (1 - k)]])
            T = cv2.warpAffine(T, M, (self.lw, self.lh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                               borderValue=(1, 1, 1))
            T = blur(T, 1.0 + 18 * lift)
        lit = (L_local * gain)[..., None] * np.asarray(colour, F32)[None, None] * self.grain[..., None]
        img = np.dstack([lit * (0.03 + 0.97 * T), L_local])
        x0, y0, x1, y1 = self.box
        Hs = np.float64([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]]) @ self.Hm
        w = cv2.warpPerspective(img, Hs, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                borderValue=(0, 0, 0, 0))
        a = (w[..., 3] * self.mask[y0:y1, x0:x1])[..., None]
        sub = f[y0:y1, x0:x1]
        # the lamp replaces the dusk on the glass (lit hide over amber), the plate shows where it is dark
        sub[:] = sub * (1 - 0.92 * a) + np.clip(w[..., :3], 0, 0.985) * 0.92 * (a / np.maximum(w[..., 3:4], 1e-4))
        return f


def sweep(t, t_on, t_off, lw, lh, direction, radius_k=2.0, travel=0.5):
    """a streetlight passing behind a pane: (lx, ly, intensity, radius) in local px, or None when dark.
    The hot spot crosses the pane along `direction` between t_on and t_off; it rises and falls in 2 frames."""
    if t < t_on or t >= t_off:
        return None
    u = (t - t_on) / (t_off - t_on)
    dx, dy = direction
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    span = 0.5 * (abs(dx) * lw + abs(dy) * lh) * travel
    lx = lw / 2 + dx * span * (2 * u - 1)
    ly = lh / 2 + dy * span * (2 * u - 1)
    edge = min(1.0, (t - t_on) * 20, (t_off - t) * 20)      # ~1 frame up and down
    return lx, ly, 1.0 * edge, radius_k * math.hypot(lw, lh) * 0.5


def puppet_local(pup, pose, pane, pos, height, swaps=None, flip=False, rig_h=1450.0):
    """the puppet's transmittance on the pane's local screen; pos = chest pivot in local px, height in local px."""
    p = dict(pose)
    if flip:
        p['_flip'] = True
    return pup.render(p, pos=pos, scale=height / rig_h, size=(pane.lw, pane.lh), swaps=swaps, pins=True)


WENKAI = 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'


def lyric(ctx, line, region, max_px=46, start=None):
    """the sung line as a pale vertical inscription on the night picture (one switch: ctx.opts['lyrics']).
    region (x, y, w, h) in 1080p px, inside the centred 4:5 area."""
    from tools.ink.opts import lyrics_on
    if not lyrics_on(ctx):
        return None
    from tools.ink.text import Inscription
    s = ctx.s
    lines = [line] if isinstance(line, str) else list(line)
    words = sum((ctx.timing.words(l) for l in lines), [])
    return Inscription('\n'.join(lines), WENKAI, tuple(int(v * s) for v in region), size=ctx.size, vertical=True,
                       max_px=max_px * s, words=words, mode='stroke', ground='night', seed=3)

"""STAGE team v3: the agent swarm / 身外身法 (F4b, F5, F6a) as a ruled album leaf of shadow-puppet workers.

One leaf, 3 x 3 ruled cells (the same ruling as the 脸谱 album and the ledger). The original monkey sits in the
middle cell, one hand raised; a hair-thin cinnabar thread runs from that hand to each of the eight cells. In each
cell one copy does ONE job, with a typeset name slip (榜题): 读 写 算 运 战 扫 望 磨. Every copy is the leather
shadow puppet of the car panes (shots/puppet_lib.py rig), re-posed hard on the beats; the leaf is lit like the car
glass (dusk paper, an amber streetlight pool passing behind it), so the leaf is the window become an album.

Everything is authored in 1920x1080 px and scaled by s = W / 1920.
"""
import math

import cv2
import numpy as np

from tools.ink import *
from tools.ink.core import F32
from tools.ink.puppet import Part, Puppet, leather, HIDE, DYE_RED, DYE_OCHRE, DYE_BLACK, DYE_GREEN, LAMP
from tools.ink.seal import glyph, has_glyph
from shots.puppet_lib import build_rig, _part, P as RIGP, run_poses, MK

KAI = 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'
BRUSH = 'refs/fonts/mashanzheng/MaShanZheng-Regular.ttf'
SEALF = 'refs/fonts/guangekai/館閣楷-Regular.ttf'
RIG_H = 1450.0
CIN = np.array([0.80, 0.20, 0.13], F32)

# the leaf: outer rule box and the 3 x 3 cells (authoring px)
LEAF = (86, 62, 1834, 1018)                      # x0, y0, x1, y1
CELL_JOBS = ['读', '写', '算', '运', None, '战', '扫', '望', '磨']       # row-major; None = the original, centre
EN = {'读': 'read', '写': 'write', '算': 'reckon', '运': 'carry', '战': 'spar', '扫': 'sweep', '望': 'watch',
      '磨': 'grind'}


def cell_box(i, leaf=LEAF, cols=3, rows=3):
    x0, y0, x1, y1 = leaf
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    c, r = i % cols, i // cols
    return (x0 + c * cw, y0 + r * ch, x0 + (c + 1) * cw, y0 + (r + 1) * ch)


# ------------------------------------------------------------------------------------------------------- props
def _blank(w, h):
    return np.zeros((h, w), np.float32)


def _mk(name, layers, pivot, parent='forearm_f', attach=(0, 0), z=5, pattern=None):
    """layers: [(mask, dye)], multiplied (each its own dyed hide). -> Part"""
    m = np.clip(sum(l[0] for l in layers), 0, 1)
    p = Part(name, m, pivot=pivot, parent=parent, attach=attach, z=z, outline=0)
    T = np.ones(m.shape + (3,), np.float32)
    for k, (mk, dye) in enumerate(layers):
        T *= leather(mk, dye, seed=11 + k, outline=3, pattern=pattern if k == 0 else None)
    p.T = T.astype(np.float32)
    return p


def prop_parts(grip):
    """Hand props in rig px (figure = 1450 px tall), pinned at the front hand's grip hole."""
    out = {}
    # scroll: two rollers and the sheet between, cut with columns of small slits (writing)
    w, h = 440, 560
    m = _blank(w, h)
    cv2.rectangle(m, (30, 30), (w - 30, h - 30), 1, -1)
    rol = _blank(w, h)
    for y in (18, h - 18):
        cv2.rectangle(rol, (6, y - 14), (w - 6, y + 14), 1, -1)
    pat = _blank(w, h)
    for cx in range(76, w - 50, 60):
        for cy in range(70, h - 80, 44):
            cv2.line(pat, (cx, cy), (cx, cy + 22), 1, 10)
    out['scroll'] = _mk('staff', [(m, HIDE * 0.97), (rol, DYE_BLACK)], (w / 2, h - 18), attach=grip, pattern=pat)
    # brush
    w, h = 90, 520
    st = _blank(w, h)
    cv2.rectangle(st, (36, 0), (54, 380), 1, -1)
    tu = _blank(w, h)
    cv2.fillPoly(tu, [np.int32([(20, 370), (70, 370), (50, 516), (40, 516)])], 1)
    out['brush'] = _mk('staff', [(st, DYE_OCHRE), (tu, DYE_BLACK)], (45, 150), attach=grip)
    # carrying pole with two baskets of peaches
    w, h = 1240, 560
    pole = _blank(w, h)
    cv2.rectangle(pole, (0, 20), (w, 44), 1, -1)
    bas = _blank(w, h)
    pe = _blank(w, h)
    for cx in (150, w - 150):
        cv2.line(pole, (cx, 32), (cx - 110, 350), 1, 8)
        cv2.line(pole, (cx, 32), (cx + 110, 350), 1, 8)
        cv2.fillPoly(bas, [np.int32([(cx - 135, 350), (cx + 135, 350), (cx + 96, 540), (cx - 96, 540)])], 1)
        for dx, dy in ((-70, 0), (70, 0), (0, -74)):
            cv2.circle(pe, (cx + dx, 310 + dy), 66, 1, -1)
            cv2.fillPoly(pe, [np.int32([(cx + dx - 22, 310 + dy - 56), (cx + dx + 22, 310 + dy - 56),
                                        (cx + dx, 310 + dy - 100)])], 1)
    pe = pe * (1 - bas)
    out['pole'] = _mk('staff', [(pole, DYE_BLACK), (bas, DYE_OCHRE), (pe, DYE_RED)], (w / 2, 32), attach=grip)
    # broom
    w, h = 360, 1150
    st = _blank(w, h)
    cv2.rectangle(st, (168, 0), (192, 800), 1, -1)
    br = _blank(w, h)
    cv2.fillPoly(br, [np.int32([(156, 740), (204, 740), (350, 1140), (10, 1140)])], 1)
    pat = _blank(w, h)
    for k in range(-5, 6):
        cv2.line(pat, (180 + k * 6, 820), (180 + k * 30, 1140), 1, 6)
    out['broom'] = _mk('staff', [(br, DYE_OCHRE), (st, DYE_BLACK)], (180, 300), attach=grip, pattern=pat)
    # ink stick
    w, h = 80, 260
    st = _blank(w, h)
    cv2.rectangle(st, (8, 0), (72, 258), 1, -1)
    out['stick'] = _mk('staff', [(st, DYE_BLACK)], (40, 30), attach=grip)
    # nothing in the hand
    out['none'] = _mk('staff', [(_blank(8, 8), DYE_BLACK)], (4, 4), attach=grip)
    return out


def _static(layers, pattern=None):
    m = np.clip(sum(l[0] for l in layers), 0, 1)
    T = np.ones(m.shape + (3,), np.float32)
    for k, (mk, dye) in enumerate(layers):
        T *= leather(mk, dye, seed=31 + k, outline=3, pattern=pattern if k == 0 else None)
    return T.astype(np.float32)


def abacus_T(state):
    """An abacus on a low table, rig px (bottom centre = the floor point). `state` deals the beads."""
    w, h = 560, 420
    fr = _blank(w, h)
    cv2.rectangle(fr, (40, 20), (w - 40, 250), 1, 16)
    cv2.line(fr, (40, 96), (w - 40, 96), 1, 12)
    be = _blank(w, h)
    r = np.random.RandomState(100 + state)
    for k, x in enumerate(range(86, w - 60, 66)):
        cv2.line(fr, (x, 20), (x, 250), 1, 4)
        up = r.rand() < 0.5
        cv2.ellipse(be, (x, 50 if up else 76), (25, 13), 0, 0, 360, 1, -1)
        n = r.randint(1, 5)
        for j in range(4):
            y = 122 + j * 27 if j < n else 150 + j * 27
            cv2.ellipse(be, (x, min(y, 236)), (25, 12), 0, 0, 360, 1, -1)
    tb = _blank(w, h)
    cv2.rectangle(tb, (0, 262), (w, 290), 1, -1)
    for x in (40, w - 64):
        cv2.rectangle(tb, (x, 290), (x + 24, h), 1, -1)
    return _static([(fr, DYE_BLACK), (be * (1 - (fr > 0)), DYE_RED), (tb, DYE_OCHRE)])


def inkstone_T():
    w, h = 420, 150
    m = _blank(w, h)
    cv2.fillPoly(m, [np.int32([(20, 60), (w - 20, 60), (w - 50, h), (50, h)])], 1)
    pat = _blank(w, h)
    cv2.ellipse(pat, (w // 2, 84), (130, 9), 0, 0, 360, 1, -1)
    return _static([(m, DYE_BLACK)], pattern=pat)


def banner_T(n, s=1.0, ch='我'):
    """A hanging paper strip with n typeset characters written down it so far (rig px)."""
    w, h = 190, 760
    m = _blank(w, h)
    cv2.rectangle(m, (24, 30), (w - 24, h - 30), 1, -1)
    rol = _blank(w, h)
    for y in (18, h - 18):
        cv2.rectangle(rol, (0, y - 16), (w, y + 16), 1, -1)
    T = _static([(m, HIDE), (rol, DYE_BLACK)])
    g = glyph(ch, BRUSH, 125)
    for k in range(n):
        gh, gw = g.shape
        x, y = (w - gw) // 2, 50 + k * 132
        T[y:y + gh, x:x + gw] *= (1 - 0.93 * g)[..., None]
    return T


def books_T(n):
    w, h = 420, 520
    m = _blank(w, h)
    pat = _blank(w, h)
    for k in range(n):
        y = h - 70 * (k + 1)
        x = 30 + (k % 2) * 26
        cv2.rectangle(m, (x, y + 6), (x + 330, y + 68), 1, -1)
        cv2.line(pat, (x + 40, y + 10), (x + 40, y + 64), 1, 6)
    return _static([(m, DYE_OCHRE)], pattern=pat)


# ------------------------------------------------------------------------------------------------------- workers
def _fix(pose, world):
    """Set the hand prop's angle so that it sits at `world` degrees in the picture whatever the arm does."""
    p = dict(pose)
    p['staff'] = world - p.get('_rot', 0) - p.get('torso', 0) - p.get('arm_f', 0) - p.get('forearm_f', 0)
    return p


SIT = dict(thigh_f=104, shin_f=-150, thigh_b=76, shin_b=-142, _y=95, _rot=4)
STAND = dict(thigh_f=10, shin_f=-8, thigh_b=-10, shin_b=-4)


def job_cycles():
    """job -> (prop name, [poses]); every pose is one beat."""
    run = run_poses(8)
    c = {}
    c['读'] = ('scroll', [_fix(dict(SIT, head=14, arm_f=62, forearm_f=42, arm_b=50, forearm_b=60), 0),
                         _fix(dict(SIT, head=-10, arm_f=70, forearm_f=46, arm_b=58, forearm_b=62), -6),
                         _fix(dict(SIT, head=16, arm_f=56, forearm_f=40, arm_b=46, forearm_b=58), 4),
                         _fix(dict(SIT, head=4, arm_f=78, forearm_f=50, arm_b=64, forearm_b=60), -10)])
    c['写'] = ('brush', [_fix(dict(STAND, head=6, arm_f=118, forearm_f=22, arm_b=-14, forearm_b=30, _rot=6), 60),
                         _fix(dict(STAND, head=10, arm_f=100, forearm_f=14, arm_b=-10, forearm_b=34, _rot=9), 72),
                         _fix(dict(STAND, head=12, arm_f=84, forearm_f=10, arm_b=-6, forearm_b=40, _rot=12), 80),
                         _fix(dict(STAND, head=14, arm_f=66, forearm_f=12, arm_b=-2, forearm_b=44, _rot=15), 84)])
    c['算'] = ('none', [dict(SIT, head=12, arm_f=74, forearm_f=22, arm_b=40, forearm_b=70),
                        dict(SIT, head=8, arm_f=58, forearm_f=52, arm_b=64, forearm_b=34),
                        dict(SIT, head=14, arm_f=84, forearm_f=10, arm_b=36, forearm_b=80),
                        dict(SIT, head=6, arm_f=64, forearm_f=40, arm_b=70, forearm_b=24)])
    c['运'] = ('pole', [_fix(dict(run[(2 * k) % 8], arm_f=46, forearm_f=128, head=-2), (4 if k % 2 else -4))
                        for k in range(4)])
    c['战'] = ('staff', [RIGP['guard'], RIGP['strike'], RIGP['leap'], RIGP['strike'] | {'_rot': -6, 'arm_f': 80}])
    c['扫'] = ('broom', [_fix(dict(STAND, head=10, arm_f=44, forearm_f=30, arm_b=30, forearm_b=40, _rot=10), 32),
                         _fix(dict(STAND, head=6, arm_f=72, forearm_f=22, arm_b=58, forearm_b=30, _rot=4,
                                   thigh_f=26, thigh_b=-22), -8),
                         _fix(dict(STAND, head=12, arm_f=40, forearm_f=34, arm_b=26, forearm_b=44, _rot=12), 36),
                         _fix(dict(STAND, head=4, arm_f=76, forearm_f=18, arm_b=62, forearm_b=26, _rot=2,
                                   thigh_f=30, thigh_b=-26), -12)])
    sh = dict(RIGP['shade'])
    c['望'] = ('none', [dict(sh), dict(sh, _flip=True, head=6), dict(sh, head=20), dict(sh, _flip=True, head=16)])
    c['磨'] = ('stick', [_fix(dict(SIT, head=14, arm_f=48, forearm_f=44, arm_b=30, forearm_b=60), 12),
                         _fix(dict(SIT, head=12, arm_f=62, forearm_f=22, arm_b=30, forearm_b=60), -6),
                         _fix(dict(SIT, head=14, arm_f=72, forearm_f=30, arm_b=30, forearm_b=60), -16),
                         _fix(dict(SIT, head=12, arm_f=56, forearm_f=56, arm_b=30, forearm_b=60), 4)])
    # the original: sitting, the front hand raised (giving the word), re-posed slightly on the beat
    c[None] = ('none', [dict(SIT, head=-2, arm_f=150, forearm_f=24, arm_b=40, forearm_b=80, _rot=0),
                        dict(SIT, head=4, arm_f=142, forearm_f=34, arm_b=44, forearm_b=76, _rot=0)])
    return c


class Rig:
    """The puppet rig with a prop for each job; .puppet(job) -> Puppet."""

    def __init__(self, rig):
        self.rig = rig
        tor = rig['torso'][3]
        hd = rig['head'][3]
        ua_f, ua_b = rig['uarm_f'][3], rig['uarm_b'][3]
        th = rig['thigh'][3]
        self.grip = rig['farm_f'][3]['grip']
        self.base = [
            _part(rig, 'torso', 'torso', z=0),
            _part(rig, 'uarm_b', 'arm_b', 'torso', tor['shoulder'], z=-3),
            _part(rig, 'farm_b', 'forearm_b', 'arm_b', ua_b['elbow'], z=-4),
            _part(rig, 'thigh', 'thigh_b', 'torso', tor['hip_b'], z=-2),
            _part(rig, 'shin', 'shin_b', 'thigh_b', th['knee'], z=-2.5),
            _part(rig, 'thigh', 'thigh_f', 'torso', tor['hip_f'], z=1),
            _part(rig, 'shin', 'shin_f', 'thigh_f', th['knee'], z=1.5),
            _part(rig, 'uarm_f', 'arm_f', 'torso', tor['shoulder'], z=3),
            _part(rig, 'farm_f', 'forearm_f', 'arm_f', ua_f['elbow'], z=4),
            _part(rig, 'head', 'head', 'torso', tor['neck'], z=2),
        ]
        self.props = prop_parts(self.grip)
        self.props['staff'] = _part(rig, 'staff', 'staff', 'forearm_f', self.grip, z=5)
        self._pup = {}

    def puppet(self, prop):
        if prop not in self._pup:
            self._pup[prop] = Puppet(self.base + [self.props[prop]], reach=1500)
        return self._pup[prop]

    def grip_xy(self, prop, pose, pos, scale):
        """Frame position of the front hand's grip hole."""
        pup = self.puppet(prop)
        M = pup.matrices(pose)['forearm_f']
        v = M @ np.array([self.grip[0], self.grip[1], 1.0])
        sx = -scale if pose.get('_flip') else scale
        return pos[0] + sx * v[0], pos[1] + scale * v[1]


def load_rig(ctx=None):
    deps = [f'{MK}/puppet_parts_colour.jpg', f'{MK}/puppet_heads_swap.jpg']
    rig = ctx.cache('puppet_rig_v1', build_rig, deps=deps) if ctx is not None else build_rig()
    return Rig(rig)


# ------------------------------------------------------------------------------------------------------- the leaf
def rules_T(W, H, s, leaf=LEAF, cols=3, rows=3, seed=5):
    """The ruled leaf (乌丝栏): a double outer rule and single inner rules, in ink, slightly uneven like a ruled line
    drawn with a brush along a straightedge. -> transmittance HxWx3"""
    d = np.zeros((H, W), np.float32)
    x0, y0, x1, y1 = [v * s for v in leaf]

    def line(a, b, wd, k):
        cv2.line(d, (int(round(a[0] * 8)), int(round(a[1] * 8))), (int(round(b[0] * 8)), int(round(b[1] * 8))), k,
                 max(1, int(round(wd))), cv2.LINE_AA, shift=3)
    o = 9 * s
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        line(a, b, 5.0 * s, 0.95)
    for (a, b) in (((x0 - o, y0 - o), (x1 + o, y0 - o)), ((x1 + o, y0 - o), (x1 + o, y1 + o)),
                   ((x1 + o, y1 + o), (x0 - o, y1 + o)), ((x0 - o, y1 + o), (x0 - o, y0 - o))):
        line(a, b, 2.0 * s, 0.8)
    for c in range(1, cols):
        x = x0 + (x1 - x0) * c / cols
        line((x, y0), (x, y1), 3.0 * s, 0.85)
    for r in range(1, rows):
        y = y0 + (y1 - y0) * r / rows
        line((x0, y), (x1, y), 3.0 * s, 0.85)
    d = d * (0.80 + 0.35 * fbm(H, W, 30 * s, seed, 'rule'))
    return ink_T(np.clip(d, 0, 1) * 0.9)


def slip_T(ch, s, px=62, font=KAI):
    """A name slip (榜题): the character in a small ruled cartouche. -> (T, w, h) in frame px."""
    g = glyph(ch, font, int(px * s))
    gh, gw = g.shape
    pad = int(12 * s)
    w, h = gw + 2 * pad, gh + 2 * pad
    d = np.zeros((h, w), np.float32)
    d[pad:pad + gh, pad:pad + gw] = g * 0.97
    cv2.rectangle(d, (1, 1), (w - 2, h - 2), 0.8, max(1, int(round(2.4 * s))))
    return ink_T(d), w, h


def thread_T(W, H, s, a, b, sag=0.0, k0=0.0, k1=1.0, wd=2.6):
    """A hair-thin cinnabar thread from a to b (authoring px), drawn from share k0 to k1 of its length."""
    d = np.zeros((H, W), np.float32)
    n = 28
    pts = []
    for i in range(n + 1):
        u = k0 + (k1 - k0) * i / n
        x = a[0] + (b[0] - a[0]) * u
        y = a[1] + (b[1] - a[1]) * u + sag * math.sin(math.pi * u)
        pts.append((x * s, y * s))
    cv2.polylines(d, [np.int32(np.array(pts) * 8)], False, 1.0, max(1, int(round(wd * s))), cv2.LINE_AA, shift=3)
    return 1 - d[..., None] * (1 - CIN[None, None] * 0.9)


def hair_T(W, H, s, pos, ang, seed=0, length=64):
    """One plucked hair: a short curled ink stroke at pos (authoring px), heading along `ang` (radians)."""
    d = np.zeros((H, W), np.float32)
    pts = []
    for i in range(13):
        u = i / 12 - 0.5
        lx = u * length
        ly = 9 * math.sin(u * 5.0 + seed)
        x = pos[0] + lx * math.cos(ang) - ly * math.sin(ang)
        y = pos[1] + lx * math.sin(ang) + ly * math.cos(ang)
        pts.append((x * s, y * s))
    cv2.polylines(d, [np.int32(np.array(pts) * 8)], False, 1.0, max(1, int(round(3.2 * s))), cv2.LINE_AA, shift=3)
    return ink_T(d * 0.95)


def chest_on_floor(rig, prop, pose, floor, k, air=0.0):
    """Chest pin (authoring px) that stands this pose's lowest FOOT on the floor point (props ignored).
    k = authoring px per rig px."""
    fx, fy = floor
    pup = rig.puppet(prop)
    M = pup.matrices(pose)
    low = 0.0
    for name in ('shin_f', 'shin_b', 'thigh_f', 'thigh_b'):
        part = pup.parts[name]
        h, w = part.mask.shape
        for (x, y) in ((0, 0), (w, 0), (0, h), (w, h), (w / 2, h)):
            v = M[name] @ np.array([x, y, 1.0])
            low = max(low, v[1])
    return (fx, fy - (low - 40) * k - air)


def lamp_light(W, H, s, t):
    """The one streetlight rhythm of the swarm leaf (F4b, F5, F6a): continuous across the three shots."""
    return street_light(W, H, s, t, 114.0, 116.6, n=2)


def done_seal(s, ch='讫', px=104, seed=3):
    """The small red 'finished' seal (白文). Falls back to the traditional form if the face lacks the simplified one."""
    from tools.ink import seal
    alt = {'讫': '訖', '真': '眞'}
    c = ch if has_glyph(ch, SEALF) else (alt.get(ch, ch) if has_glyph(alt.get(ch, ch), SEALF) else ch)
    font = SEALF if has_glyph(c, SEALF) else KAI
    return seal(c, font, int(px * s), 'bai', wear=0.22, seed=seed, weight=0.012)


class Leaf:
    """The whole swarm leaf. state per cell: pose index k (int), present (bool).
    draw(frame, steps, present, light) lays everything except seals/hairs (the shot script times those)."""

    def __init__(self, ctx, rig, paper, leaf=LEAF, jobs=CELL_JOBS, cols=3, rows=3, fig_h=205, slips=True, seed=5):
        self.ctx, self.rig, self.P = ctx, rig, paper
        self.W, self.H, self.s = ctx.W, ctx.H, ctx.s
        self.leaf, self.jobs, self.cols, self.rows = leaf, jobs, cols, rows
        self.fig_h = fig_h
        self.sc = fig_h / RIG_H * self.s                       # rig px -> frame px
        self.cyc = job_cycles()
        self.rules = rules_T(self.W, self.H, self.s, leaf, cols, rows, seed)
        self.slips = []
        s = self.s
        for i, j in enumerate(jobs):
            x0, y0, x1, y1 = cell_box(i, leaf, cols, rows)
            ch = j or '我'
            T, w, h = slip_T(ch, s)
            self.slips.append((T, int(x1 * s - w - 16 * s), int(y0 * s + 14 * s)))
        self._static = {}
        self._cache = {}

    # where things are (authoring px)
    def floor(self, i):
        x0, y0, x1, y1 = cell_box(i, self.leaf, self.cols, self.rows)
        return ((x0 + x1) / 2 - 30, y1 - 26)

    def chest(self, i, pose):
        fx, fy = self.floor(i)
        sit = pose.get('_y', 0) > 60
        return (fx, fy - self.fig_h * (0.50 if sit else 0.62))

    def chest_for(self, i, prop, pose, air=0.0):
        return chest_on_floor(self.rig, prop, pose, self.floor(i), self.fig_h / RIG_H, air)

    def worker_T(self, i, k):
        """Transmittance of cell i's worker in its k-th pose (cached per (i, k mod n))."""
        j = self.jobs[i]
        prop, poses = self.cyc[j]
        k = k % len(poses)
        key = (i, k)
        if key in self._cache:
            return self._cache[key]
        pose = dict(poses[k])
        c = i % self.cols
        flip = c == self.cols - 1                                # right column faces the centre
        if flip:
            pose['_flip'] = not pose.get('_flip', False)
        s = self.s
        fx, fy = self.floor(i)
        cx, cy = self.chest_for(i, prop, pose)
        T = self.rig.puppet(prop).render(pose, pos=(cx * s, cy * s), scale=self.sc, size=(self.W, self.H), pins=True)
        sgn = -1 if flip else 1
        for (St, dx) in self.statics(j, k):
            St = cv2.resize(St, (max(2, int(St.shape[1] * self.sc * 1.5)), max(2, int(St.shape[0] * self.sc * 1.5))),
                            interpolation=cv2.INTER_AREA)
            if flip:
                St = St[:, ::-1]
            x = int((fx + sgn * dx) * s - St.shape[1] / 2)
            y = int(fy * s - St.shape[0])
            T = T * place(St, self.W, self.H, x, y)
        self._cache[key] = T.astype(np.float32)
        return self._cache[key]

    def statics(self, j, k):
        """Cell furniture in rig px: [(T, dx from the floor point in authoring px)]."""
        if j == '算':
            return [(self._st(('ab', k), lambda: abacus_T(k)), 135)]
        if j == '磨':
            return [(self._st('stone', inkstone_T), 105)]
        if j == '写':
            return [(self._st(('ban', k), lambda: banner_T(k + 1)), 165)]
        if j == '读':
            return [(self._st(('books', 3), lambda: books_T(3)), -140)]
        return []

    def _st(self, key, fn):
        if key not in self._static:
            self._static[key] = fn()
        return self._static[key]

    def hand(self, k=0):
        """The original's raised hand (authoring px): where every thread starts."""
        i = self.jobs.index(None)
        prop, poses = self.cyc[None]
        pose = poses[k % len(poses)]
        cx, cy = self.chest_for(i, prop, pose)
        x, y = self.rig.grip_xy(prop, pose, (cx, cy), self.fig_h / RIG_H)
        return (x, y)

    def anchor(self, i):
        """Where cell i's thread ends: above the worker's head."""
        fx, fy = self.floor(i)
        return (fx, fy - self.fig_h * 0.56)

    def draw(self, f, steps, present=None, threads=None, hand_k=0):
        """steps: pose index per cell (list of 9 ints); present: bools; threads: per cell share (0..1) of the
        thread still out, measured from the centre (1 = whole)."""
        n = len(self.jobs)
        present = present or [True] * n
        threads = threads if threads is not None else [1.0] * n
        f *= self.rules
        for T, x, y in self.slips:
            lay_ink(f, T, x, y)
        h = self.hand(hand_k)
        for i in range(n):
            if self.jobs[i] is None:
                f *= self.worker_T(i, steps[i])
                continue
            if threads[i] > 0.01:
                f *= thread_T(self.W, self.H, self.s, h, self.anchor(i), sag=0, k0=0, k1=threads[i])
            if present[i]:
                f *= self.worker_T(i, steps[i])
        return f


def street_light(W, H, s, t, t0, t1, n=2, y=0.42, seed=0):
    """Dusk paper with amber streetlight pools passing right to left behind it (the car glass). -> HxWx3 gain."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    amb = np.array([0.74, 0.70, 0.78], np.float32)
    L = np.zeros((H, W), np.float32)
    for k in range(n):
        u = (t - t0) / (t1 - t0) * 1.0 + k / n
        u = u % 1.0
        cx = W * (1.35 - 1.7 * u)
        r = np.hypot((xx - cx) / (0.52 * W), (yy - H * y) / (0.95 * H))
        L += np.exp(-(r / 0.75) ** 2)
    L = np.clip(L, 0, 1)[..., None]
    lamp = np.array([1.06, 0.95, 0.74], np.float32)
    return amb[None, None] * (1 - L) + lamp[None, None] * L

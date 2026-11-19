"""BOOK v4 C5b: the wind as a real 2D flow (stable fluids) driving brush ribbons and a mist dye.

Units: screen height = 1.0, screen width = 16/9. Sim domain x in [X0, X1] (the left margin is off-screen so the jet
is already moving when it enters), y in [0, 1] downward like the image. Everything here is deterministic and
size-independent: `simulate()` returns plain arrays (cached on disk); `draw_*` render them at any resolution.
"""
import os
import pickle
from pathlib import Path

import cv2
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import splu

ROOT = Path(__file__).resolve().parent.parent
ASP = 16 / 9
X0, X1 = -0.55, ASP + 0.30
NY = 192
H = 1.0 / NY
NX = int(round((X1 - X0) / H))
FPS = 24
SUB = 5                      # sim substeps per frame
DT = 1.0 / (FPS * SUB)
NF = 58
PRE = 0.42                   # seconds of sim before frame 0 (jet already running, front near x=0 at frame 0)

PARAMS = dict(
    yc=0.54,                 # wind axis at the left edge (fraction of H); band 0.40-0.65 H
    sigma=0.075,
    U=3.1,                  # wind speed inside the packet (units/s)
    rise=0.07,               # v/u (up)
    vf=1.45, Lg=1.45, edge=0.07, tail=0.25, k=7.0,
    xf0=-0.52,   # front crosses x=0 at sim t = PRE - 0.05 (see PRE)
    dye=1.0, dye_decay=0.5,
    conf=1.0,
    visc=0.0,
)


def _egg_solid():
    from shots.C4 import egg_layer
    from shots._carve import enclosed_region
    E = egg_layer(960, 540)
    reg = enclosed_region(E, close=9) > 0.5
    reg = cv2.dilate(reg.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0       # rim included, plus a skin
    return reg


def _solid_grid(reg):
    """Solid mask on the sim grid (NY, NX)."""
    s = np.zeros((NY, NX), np.float32)
    ys, xs = np.mgrid[0:NY, 0:NX]
    wx = X0 + (xs + 0.5) * H
    wy = (ys + 0.5) * H
    px = np.clip((wx / ASP * 960).astype(int), 0, 959)
    py = np.clip((wy * 540).astype(int), 0, 539)
    inside = (wx >= 0) & (wx <= ASP)
    s = (reg[py, px] & inside)
    return s


class Fluid:
    def __init__(self, solid):
        self.solid = solid
        self.fl = ~solid
        self.u = np.zeros((NY, NX), np.float32)
        self.v = np.zeros((NY, NX), np.float32)
        self.gx, self.gy = np.meshgrid(np.arange(NX, dtype=np.float32), np.arange(NY, dtype=np.float32))
        self._build()

    def _build(self):
        idx = -np.ones((NY, NX), np.int64)
        fl = self.fl
        idx[fl] = np.arange(fl.sum())
        n = fl.sum()
        rows, cols, vals = [], [], []
        diag = np.zeros(n)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ys, xs = np.nonzero(fl)
            y2, x2 = ys + dy, xs + dx
            i = idx[ys, xs]
            inb = (y2 >= 0) & (y2 < NY) & (x2 >= 0) & (x2 < NX)
            nb = np.full(len(ys), -1)
            nb[inb] = idx[y2[inb], x2[inb]]
            fluid_nb = nb >= 0
            rows.append(i[fluid_nb]); cols.append(nb[fluid_nb]); vals.append(np.full(fluid_nb.sum(), -1.0))
            diag[i[fluid_nb]] += 1
            # right edge: Dirichlet p = 0 (open outflow): neighbour outside counts in the diagonal
            if dx in (1, -1):
                out = ~inb & ((x2 >= NX) | (x2 < 0))
                diag[i[out]] += 1
        rows.append(np.arange(n)); cols.append(np.arange(n)); vals.append(diag + 1e-6)
        A = sp.csc_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
        self.lu = splu(A)
        self.idx = idx

    # ---- advection (MacCormack with clamping) ----
    def _sl(self, q, u, v, dt):
        sx = self.gx - u * dt / H
        sy = self.gy - v * dt / H
        return cv2.remap(q, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    def advect(self, q, u, v, dt):
        f = self._sl(q, u, v, dt)
        b = self._sl(f, -u, -v, dt)
        c = f + 0.5 * (q - b)
        # clamp to the local min/max of the source neighbourhood
        sx = self.gx - u * dt / H
        sy = self.gy - v * dt / H
        ix = np.floor(sx).astype(int); iy = np.floor(sy).astype(int)
        ix = np.clip(ix, 0, NX - 2); iy = np.clip(iy, 0, NY - 2)
        nb = np.stack([q[iy, ix], q[iy, ix + 1], q[iy + 1, ix], q[iy + 1, ix + 1]])
        return np.clip(c, nb.min(0), nb.max(0))

    def project(self):
        u, v = self.u, self.v
        u = np.where(self.solid, 0, u); v = np.where(self.solid, 0, v)
        div = np.zeros_like(u)
        div[:, 1:-1] += (u[:, 2:] - u[:, :-2]) * 0.5
        div[1:-1, :] += (v[2:, :] - v[:-2, :]) * 0.5
        div[:, 0] += (u[:, 1] - 0.0) * 0.5
        div[:, -1] += (0.0 - u[:, -2]) * 0.5
        div[0, :] += (v[1, :] - v[0, :]); div[-1, :] += (v[-1, :] - v[-2, :])
        rhs = -div[self.fl].astype(np.float64)
        p = np.zeros((NY, NX), np.float32)
        p[self.fl] = self.lu.solve(rhs)
        # ghost values in solid cells: copy mean of fluid neighbours
        pf = p * self.fl
        w = cv2.blur(self.fl.astype(np.float32), (3, 3)) + 1e-6
        ghost = cv2.blur(pf, (3, 3)) / w
        pe = np.where(self.fl, p, ghost)
        gx = np.zeros_like(u); gy = np.zeros_like(u)
        gx[:, 1:-1] = (pe[:, 2:] - pe[:, :-2]) * 0.5
        gx[:, -1] = (0 - pe[:, -2]) * 0.5            # open right edge: p=0 outside
        gx[:, 0] = (pe[:, 1] - 0) * 0.5              # open left edge
        gy[1:-1, :] = (pe[2:, :] - pe[:-2, :]) * 0.5
        self.u = np.where(self.solid, 0, u - gx).astype(np.float32)
        self.v = np.where(self.solid, 0, v - gy).astype(np.float32)

    def vort_conf(self, eps, dt):
        u, v = self.u, self.v
        w = np.zeros_like(u)
        w[1:-1, 1:-1] = ((v[1:-1, 2:] - v[1:-1, :-2]) - (u[2:, 1:-1] - u[:-2, 1:-1])) * 0.5 / H
        a = np.abs(w)
        gx = np.zeros_like(u); gy = np.zeros_like(u)
        gx[:, 1:-1] = (a[:, 2:] - a[:, :-2]) * 0.5
        gy[1:-1, :] = (a[2:, :] - a[:-2, :]) * 0.5
        n = np.sqrt(gx * gx + gy * gy) + 1e-6
        nx_, ny_ = gx / n, gy / n
        fx = ny_ * w; fy = -nx_ * w
        self.u += eps * H * fx * dt
        self.v += eps * H * fy * dt
        self.u[self.solid] = 0; self.v[self.solid] = 0
        return w

    def gust(self, t, P, dt):
        """Nudge the flow toward a travelling packet of wind (front speed vf, length Lg, soft edges)."""
        xs = X0 + (np.arange(NX) + 0.5) * H
        yy = (np.arange(NY) + 0.5) * H
        xf = P['xf0'] + P['vf'] * t
        xi = xf - xs                                   # distance behind the front
        g = 1 / (1 + np.exp(-xi / P['edge'])) * (1 - 1 / (1 + np.exp(-(xi - P['Lg']) / P['tail'])))
        yc = P['yc'] - P['rise'] * (xs - X0) * 0.5      # axis rises along x
        lobes = 1 + 0.30 * np.sin(yy * 41 + 1.3)[:, None] + 0.18 * np.sin(yy * 83 + 0.4)[:, None]
        prof = np.exp(-((yy[:, None] - yc[None, :]) / P['sigma']) ** 2) * lobes
        ut = P['U'] * prof * g[None, :]
        vt = -P['rise'] * ut
        w = np.clip(g[None, :] * (prof > 0.02), 0, 1) * (1 - np.exp(-P['k'] * dt))
        self.u += (ut - self.u) * w
        self.v += (vt - self.v) * w
        self.u[self.solid] = 0; self.v[self.solid] = 0
        return g, prof


def _env(t, P):
    if t < 0:
        return 0.0
    a = np.clip(t / P['t_on'], 0, 1); a = a * a * (3 - 2 * a)
    d = np.clip((t - P['t_hold']) / (P['t_off'] - P['t_hold']), 0, 1); d = d * d * (3 - 2 * d)
    return float(a * (1 - d))


def _bilin(F, px, py):
    """Sample field F (NY,NX) at sim-grid coordinates."""
    x = np.clip(px, 0, NX - 1.001); y = np.clip(py, 0, NY - 1.001)
    x0 = x.astype(int); y0 = y.astype(int)
    fx = x - x0; fy = y - y0
    return (F[y0, x0] * (1 - fx) * (1 - fy) + F[y0, x0 + 1] * fx * (1 - fy)
            + F[y0 + 1, x0] * (1 - fx) * fy + F[y0 + 1, x0 + 1] * fx * fy)


def _w2g(p):
    return (p[:, 0] - X0) / H - 0.5, p[:, 1] / H - 0.5


# ------------------------------------------------------------------ ribbons
class Ribbon:
    def __init__(self, p, birth, wmax, tone, seed, ds):
        self.ds = ds
        self.birth = birth
        self.p = p.astype(np.float64)
        seg = np.hypot(*np.diff(self.p, axis=0).T)
        self.m = np.concatenate([[0], np.cumsum(seg)])
        self.Lm = self.m[-1]
        self.act = np.zeros(len(p))
        self.wmax = wmax
        self.tone = tone
        self.seed = seed
        self.alive = False

    def resample(self, ds):
        seg = np.hypot(*np.diff(self.p, axis=0).T)
        s = np.concatenate([[0], np.cumsum(seg)])
        if s[-1] < ds * 2:
            return
        n = max(int(s[-1] / ds) + 1, 2)
        sn = np.linspace(0, s[-1], n)
        self.p = np.stack([np.interp(sn, s, self.p[:, 0]), np.interp(sn, s, self.p[:, 1])], 1)
        self.m = np.interp(sn, s, self.m)
        self.act = np.interp(sn, s, self.act)


VORT = [(1.05, +0.10, +1), (1.45, -0.08, -1), (1.72, +0.10, +1)]
# (x, dy from the axis, sign): eddies lying in the path (clockwise below the axis, counter-clockwise above: the sense
# the wind's own shear favours); the wind reveals and rolls them on.
# eddies EMITTED at the left edge while the gust is born: each becomes a curled head of a ribbon train
EMIT = [(0.02, -0.06, -1), (0.15, +0.06, +1), (0.28, -0.06, -1), (0.41, +0.06, +1), (0.54, -0.06, -1)]
EMIT_X = -0.47


def add_vortex(fl, P, cx, cy, sg, r0=0.05, G=0.55):
    gx, gy = np.meshgrid(X0 + (np.arange(NX) + 0.5) * H, (np.arange(NY) + 0.5) * H)
    dx = gx - cx; dyy = gy - cy
    r2 = dx * dx + dyy * dyy + 1e-9
    f = (1 - np.exp(-r2 / r0 ** 2)) / r2 * G * sg / (2 * np.pi)
    fl.u += (-dyy * f).astype(np.float32)
    fl.v += (dx * f).astype(np.float32)
    fl.u[fl.solid] = 0; fl.v[fl.solid] = 0


def axis_y(P, x):
    return P['yc'] - P['rise'] * (x - X0) * 0.5


def seed_vortices(fl, P, r0=0.05, G=0.55):
    for cx, dy, sg in VORT:
        add_vortex(fl, P, cx, axis_y(P, cx) + dy, sg, r0, G)


def make_ribbons(P):
    rg = np.random.default_rng(1988)
    ds = 0.0065
    rib = []
    yc = P['yc']

    def add(x0, y0, L, birth, wmax, tone, slope=0.0):
        n = max(int(L / ds), 4)
        x = np.linspace(x0, x0 + L, n)
        y = y0 + slope * (x - x0) + 0.004 * np.sin(np.linspace(0, 5, n) + rg.uniform(0, 6))
        rib.append(Ribbon(np.stack([x, y], 1), birth, wmax, tone, int(rg.integers(1 << 30)), ds))

    # A) a few lines lying at rest across the path; the wind reveals them (ink appears where air moves)
    for k in range(4):
        x0 = 0.15 + k * 0.40 + rg.normal(0, 0.04)
        y0 = yc - 0.04 * (x0 / ASP) + rg.normal(0, 0.07)
        add(x0, y0, rg.uniform(0.20, 0.42), 0.0, rg.uniform(0.0105, 0.0150), rg.uniform(0.26, 0.48))
    for cx, dy, sg in VORT:
        cy = axis_y(P, cx) + dy
        for o in (-0.02, 0.02):
            add(cx - rg.uniform(0.12, 0.2), cy + o + rg.normal(0, 0.006), rg.uniform(0.26, 0.40), 0.0,
                rg.uniform(0.0105, 0.0150), rg.uniform(0.30, 0.50))
    # B) lines born in the packet: two through each emitted eddy's core, and some straight streaks
    for te, dy, sg in EMIT:
        cy = axis_y(P, EMIT_X) + dy
        for o in (0.0,):
            add(EMIT_X - 0.09, cy + o, 0.20, te, rg.uniform(0.0105, 0.0150), rg.uniform(0.30, 0.50))
    for k in range(5):
        y0 = yc + (k - 2) * 0.034 + rg.normal(0, 0.006)
        add(-0.52, y0, rg.uniform(0.15, 0.30), rg.uniform(0.0, 0.45), rg.uniform(0.0095, 0.0140), rg.uniform(0.26, 0.46))
    solid = _solid_grid(_egg_solid())
    keep = []
    for r in rib:
        gx, gy = _w2g(r.p)
        if solid[np.clip(gy.astype(int), 0, NY - 1), np.clip(gx.astype(int), 0, NX - 1)].any():
            continue
        keep.append(r)
    rib = keep
    return rib


def simulate(P=None, cache=None, force=False):
    P = P or PARAMS
    cache = cache or (ROOT / 'work/book4/C5b/sim_cache.pkl')
    if cache.exists() and not force:
        with open(cache, 'rb') as f:
            return pickle.load(f)
    solid = _solid_grid(_egg_solid())
    fl = Fluid(solid)
    seed_vortices(fl, P)
    rib = make_ribbons(P)
    DS = 2                                           # dye at 2x sim resolution
    DNX, DNY = NX * DS, NY * DS
    dye = np.zeros((DNY, DNX), np.float32)
    dgx, dgy = np.meshgrid(np.arange(DNX, dtype=np.float32), np.arange(DNY, dtype=np.float32))
    solid_d = cv2.resize(solid.astype(np.float32), (DNX, DNY), interpolation=cv2.INTER_NEAREST) > 0.5
    rg = np.random.default_rng(7)
    nz = [cv2.GaussianBlur(rg.standard_normal((DNY, 1)).astype(np.float32), (1, 0), 3) for _ in range(1)]

    def sl_dye(q, u, v, dt, sgn=1.0):
        return cv2.remap(q, dgx - sgn * u * dt / (H / DS), dgy - sgn * v * dt / (H / DS), cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REPLICATE)

    # noise for dye inlet streaks
    yy = (np.arange(DNY) + 0.5) * (H / DS)
    band = np.exp(-((yy - P['yc']) / (P['sigma'] * 1.6)) ** 2)
    streak_t = np.cumsum(rg.standard_normal((400, DNY)), 0)
    frames = []                                      # per frame: (ribbon states, dye, speed)
    nsteps = int((PRE + NF / FPS) * (1 / DT)) + 1
    f_of_step = {}
    for fi in range(NF):
        f_of_step[int(round((PRE + fi / FPS) / DT))] = fi
    for st in range(nsteps):
        t = st * DT
        # advect velocity
        u0, v0 = fl.u.copy(), fl.v.copy()
        fl.u = fl.advect(u0, u0, v0, DT)
        fl.v = fl.advect(v0, u0, v0, DT)
        fl.vort_conf(P['conf'], DT)
        g, prof = fl.gust(t, P, DT)
        for te, dy, sg in EMIT:
            if te <= t < te + DT:
                add_vortex(fl, P, EMIT_X, axis_y(P, EMIT_X) + dy, sg, 0.045, 0.40)
        fl.project()
        # dye
        ud = cv2.resize(fl.u, (DNX, DNY), interpolation=cv2.INTER_LINEAR)
        vd = cv2.resize(fl.v, (DNX, DNY), interpolation=cv2.INTER_LINEAR)
        f1 = sl_dye(dye, ud, vd, DT)
        b1 = sl_dye(f1, ud, vd, DT, -1.0)
        dd = f1 + 0.5 * (dye - b1)
        dye = np.clip(dd, 0, 1.2)
        gd = cv2.resize(g[None, :].astype(np.float32), (DNX, 1), interpolation=cv2.INTER_LINEAR)[0]
        pd = cv2.resize(prof.astype(np.float32), (DNX, DNY), interpolation=cv2.INTER_LINEAR)
        src = np.clip(pd * gd[None, :] * (0.65 + 0.35 * np.tanh(streak_t[min(st // 2, 399)] * 0.4))[:, None], 0, 1)
        src[:, DNX // 3:] = 0                           # mist is made where the wind is born (left third)
        dye = np.maximum(dye, src * P['dye'])
        dye *= (1 - P['dye_decay'] * DT)
        dye[solid_d] = 0
        # ribbons
        for r in rib:
            if not r.alive and t >= r.birth:
                r.alive = True
        pts = [r.p for r in rib if r.alive]
        if pts:
            allp = np.concatenate(pts)
            gx, gy = _w2g(allp)
            ua = _bilin(fl.u, gx, gy); va = _bilin(fl.v, gx, gy)
            mid = allp + 0.5 * DT * np.stack([ua, va], 1)
            gx2, gy2 = _w2g(mid)
            u2 = _bilin(fl.u, gx2, gy2); v2 = _bilin(fl.v, gx2, gy2)
            newp = allp + DT * np.stack([u2, v2], 1)
            spd = np.hypot(u2, v2)
            dgx_ = (allp[:, 0] - X0) / (H / DS) - 0.5; dgy_ = allp[:, 1] / (H / DS) - 0.5
            xx = np.clip(dgx_, 0, DNX - 1.001); yy_ = np.clip(dgy_, 0, DNY - 1.001)
            dgate = np.clip((dye[yy_.astype(int), xx.astype(int)] - 0.004) * 40, 0, 1)
            o = 0
            for r in rib:
                if not r.alive:
                    continue
                n = len(r.p)
                r.p = newp[o:o + n]
                r.act = np.maximum(r.act, np.clip((spd[o:o + n] - 0.30) / 0.9, 0, 1) * dgate[o:o + n])
                o += n
                if st % 2 == 0:
                    r.resample(r.ds)
        if st in f_of_step:
            states = []
            for r in rib:
                if not r.alive:
                    states.append(None); continue
                dm = np.maximum(np.gradient(r.m), 1e-5)
                dsp = np.maximum(np.hypot(*np.gradient(r.p, axis=0).T), 1e-5)
                stretch = dsp / dm
                states.append(dict(p=r.p.astype(np.float32).copy(), m=r.m.astype(np.float32).copy(),
                                   act=r.act.astype(np.float32).copy(), stretch=stretch.astype(np.float32)))
            spd_f = np.hypot(fl.u, fl.v)
            frames.append(dict(ribbons=states, dye=dye.astype(np.float16).copy(), spd=spd_f.astype(np.float16)))
    meta = [dict(Lm=float(r.Lm), wmax=r.wmax, tone=r.tone, seed=r.seed) for r in rib]
    out = dict(frames=frames, meta=meta, P=P, solid=solid)
    cache.parent.mkdir(parents=True, exist_ok=True)
    with open(cache, 'wb') as f:
        pickle.dump(out, f)
    return out

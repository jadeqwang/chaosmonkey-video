"""B4 'Sunlight by day and moonlight by night' (29.292-36.417, 171 frames). BOOK team, v3 (REVISION_V3 §3.1).

LIGHT IS THE CARVER. No carvers, no ladders: only stone, cut and light.
- Opens very close: one character of 千字文 (小篆, 崇羲篆體), chisel-fresh. The edge of the sunlight crosses it from
  the right; behind the edge the stroke is CUT (raw pale stone, the wall toward the sun flaring), ahead of it the rock
  is blank and in shade. Every cut sheds a thread of bright dust; the dust rises.
- The shot widens and travels right to left (time). The terminator runs ahead across the wall; behind it the columns
  stand in rectangular FIELDS of different densities separated by straight channels (cliff inscriptions, a stele
  forest; from this height, a floorplan). Cinnabar seeps into the cuts well behind the edge.
- 'moonlight' (word onset): the page falls to night. A pale moon-edge crosses the OTHER way (left to right) and cuts
  a second, finer column in every gap between the day's columns. Two passes, two layers, interleaved.
- The dust does not fall: it drifts up into the band of mist (bare paper) and on toward the summit (B5).
- Inscription 日沐天光 / 夜沐月华 static on a veil of mist at the right edge.
"""
import numpy as np

from shots._mountain import *
from shots._carve import *
from tools.ink.inscription import inscription

T0, T1 = 703 / 24, 874 / 24
MZ = 6                                    # macro raster: px per canvas px
MW, MH = 800, 450                         # macro window in canvas px
BAND_Y = 1280                             # the seam between the two rows of cliff, hidden in mist
SUN = (335.0, 12.0)
MOON = (222.0, 13.0)


def make_fields(W):
    """Rectangular fields along both rows of the wall, right to left; some split in two by a horizontal channel."""
    r = rng(11, 'fields')
    sizes = [110, 84, 64, 84, 110, 64, 96, 72]
    out = []
    for (ya, yb), off in (((1440, 2480), 0), ((90, 1130), 3)):
        x, k = W - 70, off
        while x > 120:
            size = sizes[k % len(sizes)]
            w = float(r.uniform(4.2, 7.5)) * size * 1.62
            w = min(w, x - 60)
            if w < size * 3:
                break
            if r.uniform() < 0.34 and size <= 84:
                cut = ya + (yb - ya) * float(r.uniform(0.42, 0.6))
                out.append((x - w, ya, w, cut - 40 - ya, size, 0.62, 0.12))
                s2 = sizes[(k + 3) % len(sizes)]
                out.append((x - w, cut + 40, w, yb - cut - 40, s2, 0.62, 0.12))
            else:
                out.append((x - w, ya, w, yb - ya, size, 0.62, 0.12))
            x -= w + float(r.uniform(70, 120))
            k += 1
    return out


def build(ctx):
    raw = load_image(B + 'B_cliff_run.png')
    h, W = raw.shape[:2]
    H = 2 * h
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    rock = np.empty((H, W, 3), np.float32)
    rock[h:] = onto_paper(raw, type('P', (), {'rgb': paper.rgb[h:]})())
    rock[:h] = onto_paper(raw[:, ::-1], type('P', (), {'rgb': paper.rgb[:h]})())
    text = qianziwen(160)
    fields = make_fields(W)
    day, k = field_cells(fields, text)
    moon, _ = between_cells(day, fields, text, ratio=0.42, start=k)
    Dd, cd = build_depth(day, W, H, SEAL_FONT, weight=0.022, seed=4)
    Dm, cm = build_depth(moon, W, H, SEAL_FONT, weight=0.03, seed=5)
    # the carving breaks off over the dark fissures of the painting
    pres = smoothstep(0.42, 0.62, blur(luma(rock) / np.maximum(luma(paper.rgb), 1e-3), 6.0))
    Dd, cd, Dm, cm = Dd * pres, cd * pres, Dm * pres, cm * pres
    micro = micro_relief(rock, 70.0, 0.12) * 3.0
    noise = fbm(H, W, 34.0, 9, 'b4n', octaves=3).astype(np.float32)
    # the macro character: a size-110 cell nearest (7350, 1960)
    big = [c for c in day if c[3] >= 108 and c[2] > 1500]
    mc = min(big, key=lambda c: (c[1] - 7350) ** 2 + (c[2] - 1960) ** 2)
    mx, my = mc[1], mc[2]
    ox, oy = mx - MW / 2, my - MH / 2
    near = [c for c in day + moon if abs(c[1] - mx) < MW and abs(c[2] - my) < MH]
    nd = [c for c in near if c[3] > 60]
    nm = [c for c in near if c[3] <= 60]
    mDd, mcd = build_depth(nd, MW * MZ, MH * MZ, SEAL_FONT, weight=0.022, seed=4, scale=MZ, origin=(ox, oy),
                           chatter=0.35, rough=0.5)
    mDm, mcm = build_depth(nm, MW * MZ, MH * MZ, SEAL_FONT, weight=0.03, seed=5, scale=MZ, origin=(ox, oy))
    x0, y0 = int(round(ox)), int(round(oy))
    crop = rock[y0:y0 + MH, x0:x0 + MW]
    mrock = cv2.resize(crop, (MW * MZ, MH * MZ), interpolation=cv2.INTER_CUBIC)
    g = fbm(MH * MZ, MW * MZ, 3.0, 21, 'grain', octaves=3) - 0.5                 # the stone's grain, seen close
    g2 = smoothstep(0.62, 0.8, fbm(MH * MZ, MW * MZ, 7.0, 22, 'pits', octaves=2))
    mrock = np.clip(mrock * (1 + 0.035 * g - 0.04 * g2)[..., None], 0, 1).astype(np.float32)
    mmicro = cv2.resize(micro[y0:y0 + MH, x0:x0 + MW], (MW * MZ, MH * MZ), interpolation=cv2.INTER_CUBIC) * MZ
    mmicro = (mmicro * 0.5 + g * 0.07 - g2 * 0.25).astype(np.float32)
    mpres = cv2.resize(pres[y0:y0 + MH, x0:x0 + MW], (MW * MZ, MH * MZ), interpolation=cv2.INTER_LINEAR)
    mnoise = cv2.resize(noise[y0:y0 + MH, x0:x0 + MW], (MW * MZ, MH * MZ), interpolation=cv2.INTER_LINEAR)
    mpaper = cv2.resize(paper.rgb[y0:y0 + MH, x0:x0 + MW], (MW * MZ, MH * MZ), interpolation=cv2.INTER_CUBIC)
    # mist: one band of bare paper over the seam, lumpy, drifting
    mw, mh = W + 2400, 520                                         # a soft, lumpy band (no fine wisps: it hides the seam)
    yy = np.arange(mh, dtype=np.float32)[:, None]
    lump = cv2.resize(fbm(mh // 4, mw // 4, 110.0, 5, 'mistl', octaves=3), (mw, mh), interpolation=cv2.INTER_CUBIC)
    edge = np.abs(yy - mh / 2) / (mh / 2) + (lump - 0.5) * 0.9
    mist = smoothstep(0.92, 0.38, edge).astype(np.float32)
    wig = ((fbm(H, 64, 90.0, 3, 'wig', octaves=3) - 0.5) * 2).astype(np.float32)[:, :1]     # the edge follows the rock
    return dict(rock=rock, paper=paper.rgb, Dd=Dd, cd=cd, Dm=Dm, cm=cm, micro=micro, noise=noise, mist=mist, wig=wig,
                macro=dict(rock=mrock, Dd=mDd * mpres, cd=mcd * mpres, Dm=mDm * mpres, cm=mcm * mpres, micro=mmicro,
                           noise=mnoise, paper=mpaper, origin=(x0, y0)),
                mc=(mx, my), W=W, H=H, day=len(day), moon=len(moon))


def setup(ctx):
    global S, CAM, T_MOON, XS_K, XM_K, DUST_S, DUST_M, DUST_C, INS, VEIL, PF
    S = build(ctx)
    mx, my = S['mc']
    T_MOON = ctx.timing.word('Sunlight by day and moonlight by night', 'moonlight')[0]
    CAM = Camera([(T0, mx, my, 8.5), (30.05, mx - 12, my, 7.6, 'linear'), (31.6, mx - 650, 1950, 1.0, 'inout'),
                  (T_MOON, 5900, 1840, 0.8, 'linear'), (T1 + 0.2, 5000, 1290, 0.5, 'sine')])
    # terminators (canvas x over time)
    XS_K = np.array([(T0 - 0.1, mx + 75), (29.6, mx + 30), (30.1, mx - 62), (31.6, mx - 720), (T_MOON - 0.15, 4650),
                     (T_MOON + 0.3, -400)], np.float64)
    XM_K = np.array([(T_MOON + 0.2, 4450), (T1 - 0.1, 9200)], np.float64)
    W, H = S['W'], S['H']
    # dust: born where and when the edges cut
    p = sample_points(S['cd'], 9000, seed=1)
    p = p[p[:, 0] > 4300]
    tb = t_of_x(XS_K, p[:, 0])
    DUST_S = Dust(p, tb + rng(2, 'j').uniform(0, 0.25, len(p)), seed=3, life=(2.0, 5.0), size=(1.6, 3.0), tail=0.14)
    mo = S['macro']['origin']
    pc = sample_points(S['macro']['cd'], 260, seed=4)
    pc = np.stack([mo[0] + pc[:, 0] / MZ, mo[1] + pc[:, 1] / MZ], 1)
    DUST_C = Dust(pc, t_of_x(XS_K, pc[:, 0]) + rng(5, 'j').uniform(0, 0.12, len(pc)), seed=6, rise=(14, 60),
                  drift=(-8, 4), sway=3.0, life=(0.9, 2.2), size=(2.0, 4.0), tail=0.2, accel=20.0)
    pm = sample_points(S['cm'], 7000, seed=7)
    pm = pm[pm[:, 0] > 4450]
    DUST_M = Dust(pm, t_of_x(XM_K, pm[:, 0]) + rng(8, 'j').uniform(0, 0.25, len(pm)), seed=9, life=(1.6, 4.0),
                  colour=SILVER_FLECK, size=(1.6, 2.8), tail=0.14)
    # the veil of mist at the right edge of the frame, and the inscription on it
    PF = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED + 7)
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(np.float32)
    n = fbm(ctx.H, ctx.W, 260 * ctx.s, 31, 'veil', octaves=3) - 0.5
    VEIL = smoothstep(0.775, 0.865, xx / ctx.W + n * 0.10).astype(np.float32)
    INS = inscription(ctx, 'B4', box=(1660, 120, 200, 640), paper=PF)


def t_of_x(keys, x):
    """Time at which a terminator with keys [(t, x)] (monotone in x) reaches canvas x."""
    ts, xs = keys[:, 0], keys[:, 1]
    if xs[0] > xs[-1]:
        return np.interp(-np.asarray(x), -xs, ts)
    return np.interp(np.asarray(x), xs, ts)


def state(t):
    xs = float(np.interp(t, XS_K[:, 0], XS_K[:, 1]))
    xm = float(np.interp(t, XM_K[:, 0], XM_K[:, 1])) if t > XM_K[0, 0] else -1e6
    night = ramp(t, T_MOON - 0.3, T_MOON + 0.25, 'sine')
    return xs, xm, night


def lit_frame(L, box, t, z, scale=1.0, origin=(0.0, 0.0)):
    """Shade one window of a raster (wide canvas or macro) at song time t. box in raster px."""
    xs, xm, night = state(t)
    x0, y0, x1, y1 = box
    Hh, Ww = L['rock'].shape[:2]
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(Ww, x1), min(Hh, y1)
    out = np.empty((y1 - y0, x1 - x0, 3), np.float32)
    out[:] = 0.5
    if a1 <= a0 or b1 <= b0:
        return out
    sl = (slice(b0, b1), slice(a0, a1))
    X = (origin[0] + (np.arange(a0, a1, dtype=np.float32) + 0.5) / scale)[None, :]         # canvas x
    Yi = np.clip((origin[1] + (np.arange(b0, b1) + 0.5) / scale).astype(int), 0, S['H'] - 1)
    wig = (S['wig'][Yi] * 46.0 + (L['noise'][sl] - 0.5) * 60.0) * float(np.clip(1.4 / z, 0.06, 1.0))
    rw = float(np.clip(46.0 / z, 5.0, 70.0))                       # depth comes up over this many px behind the edge
    ew = float(np.clip(22.0 / z, 2.5, 50.0))
    ds = X - xs + wig                                              # > 0: the sun has passed
    dm = xm - X + wig
    lit_s = smoothstep(-ew, ew, ds)
    lit_m = smoothstep(-ew, ew, dm)
    m_d = smoothstep(0.0, rw, ds)
    m_m = smoothstep(0.0, rw, dm)
    cd, cm = L['cd'][sl] * m_d, L['cm'][sl] * m_m
    hgt = L['micro'][sl] - (L['Dd'][sl] * m_d + L['Dm'][sl] * m_m) * 0.9
    alb = L['rock'][sl].copy()
    lum = luma(alb)[..., None]
    fresh = (cd * (0.16 + 0.30 * np.exp(-np.maximum(ds, 0) / 400.0)) + cm * 0.40)[..., None]
    alb += (FRESH[None, None] * (0.55 + 0.45 * lum) - alb) * np.clip(fresh, 0, 1)
    red = (cd * smoothstep(260.0, 900.0, ds) * (0.5 + 0.5 * smoothstep(0.3, 0.7, L['noise'][sl])) * 0.86)[..., None]
    alb += (RED[None, None] * (0.8 + 0.3 * lum) - alb) * red
    flat = (0.87 + 0.13 * lit_s) * (1 - night) + (0.76 + 0.20 * lit_m) * night
    con_d = 0.20 + lit_s * (0.30 + 0.28 * np.exp(-np.maximum(ds, 0) / 520.0))
    con_n = 0.20 + lit_m * (0.32 + 0.26 * np.exp(-np.maximum(dm, 0) / 520.0))
    turn = abs(2 * night - 1)                                       # the light turns over between sun and moon
    con = np.minimum(con_d if night < 0.5 else con_n, 0.74 - 0.2 * float(smoothstep(1.5, 4.0, z))) * turn
    tint_n = np.array([0.975, 0.935, 0.865], np.float32)[None, None] * (1 - lit_m[..., None]) \
        + np.array([0.975, 0.975, 0.955], np.float32)[None, None] * lit_m[..., None]
    tint = 1.0 * (1 - night) + tint_n * night
    f = shade(alb, hgt, SUN if night < 0.5 else MOON, flat, con, warmth=0.75 * (1 - night) * lit_s, tint=tint)
    # mist: bare paper over the seam (wide canvas only matters; the macro window sits far below it)
    bm = S['mist']
    my0 = BAND_Y - bm.shape[0] // 2
    Y = origin[1] + (np.arange(b0, b1, dtype=np.float32) + 0.5) / scale
    if Y.max() > my0 and Y.min() < my0 + bm.shape[0]:
        dr = 1200.0 + 46.0 * (t - T0)
        xi = ((X[0] + dr) % (bm.shape[1] - 1)).astype(np.float32)
        yi = (Y - my0).astype(np.float32)
        mm = cv2.remap(bm, np.repeat(xi[None], len(yi), 0), np.repeat(yi[:, None], len(xi), 1), cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        bare = L['paper'][sl] * (flat[..., None] if isinstance(flat, np.ndarray) else flat) * tint
        f += (bare - f) * (mm * 0.96)[..., None]
    out[b0 - y0:b1 - y0, a0 - x0:a1 - x0] = f
    return out


def render(t, ctx):
    cx, cy, z = CAM.at(t)[:3]
    xs, xm, night = state(t)
    wm = float(smoothstep(np.log(2.5), np.log(3.4), np.log(z)))            # 1 = macro raster, 0 = wide canvas
    f = None
    if wm < 1:
        f = view(None, cx, cy, z, ctx.W, ctx.H, render=lambda box: lit_frame(S, box, t, z))
    if wm > 0:
        M = S['macro']
        ox, oy = M['origin']
        g = view(None, (cx - ox) * MZ, (cy - oy) * MZ, z / MZ, ctx.W, ctx.H,
                 render=lambda box: lit_frame(M, box, t, z, scale=MZ, origin=(ox, oy)))
        f = g if f is None else f + (g - f) * wm
    zz = z * ctx.W / 1920.0

    def to_frame(x, y):
        return (x - cx) * zz + ctx.W / 2, (y - cy) * zz + ctx.H / 2

    close = float(smoothstep(1.2, 3.0, z))
    if close < 1:
        DUST_S.draw(f, t, to_frame, ctx.s, gain=(1 - close) * (1 - 0.6 * night))
    if close > 0:
        DUST_C.draw(f, t, to_frame, ctx.s, gain=close)
    if night > 0:
        DUST_M.draw(f, t, to_frame, ctx.s, gain=night)
    # the veil and the inscription (static in frame)
    lvl = (1 - night) + 0.88 * night
    f += (PF.rgb * lvl - f) * VEIL[..., None]
    INS.draw(f)
    return np.clip(f, 0, 1)

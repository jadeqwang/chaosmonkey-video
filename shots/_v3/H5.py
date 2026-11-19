"""H5 "I'm made of the telling, not just the tale" (169.250-172.750, 84 frames). Team MOUNTAIN.

The carved cliff again (B_cliff_run and the same carving as B4, held at mid scale: zoom 0.85). The camera holds;
one thing moves, the light: a warm raking band crosses right to left and every character it reaches brightens and
stays lit, except inside a child-shaped shadow in the lower left (a small girl standing, seen from behind:
little Jade's back view from the turnaround, simplified so it could be either child): a blank in lit writing.
A loose gold brush ring floats behind her head, not touching it (no group-G plate yet: drawn with `stroke`).
"""
import numpy as np

from shots._mountain import *
from shots._v2 import B4 as _b4          # v3: the v2 carved cliff (B4 itself was rebuilt)

T0, T1 = 4062 / 24, 4146 / 24
CX, CY, Z = 7320, 640, 0.85


def setup(ctx):
    global C, XS, SH, RING, PAPER_RING, INS, VEIL, PFR
    _b4.setup(ctx)
    C, XS = _b4.C, _b4.XS
    H, W = C.H, C.W
    # the child's shadow, in canvas space: feet near the bottom of the frame, lower left
    m = load_mask(ROOT / 'work/mountain/child_back_mask.png')
    hpx = 900                                                  # canvas px tall (about 545 px in frame)
    m = cv2.resize(m, (int(m.shape[1] * hpx / m.shape[0]), hpx), interpolation=cv2.INTER_AREA)
    fx0 = CX - 960 / Z                                         # canvas x of the frame's left edge
    # v3 (lead): a child-shaped BLANK in lit writing again, and the ring clear of characters. The raking light comes
    # from the upper right, so her cast shadow slants down to the left: the head (and the ring) fall in the uncarved
    # gap between two inscription blocks (x 6560-7100), the body falls across the columns of the block on the left.
    LEAN = 0.30                                                # px of x per px of y
    HEAD_X = 6695
    hy_m = hpx * 0.11
    Msh = np.float32([[1, -LEAN, LEAN * hpx], [0, 1, 0]])
    m = cv2.warpAffine(m, Msh, (m.shape[1] + int(LEAN * hpx), hpx), flags=cv2.INTER_LINEAR)
    head_col = (m.shape[1] - int(LEAN * hpx)) / 2.0 + LEAN * (hpx - hy_m)      # the head's x inside the slanted mask
    x0, y0 = int(HEAD_X - head_col), int(CY + 540 / Z - hpx + 40)
    SH = np.zeros((H, W), np.float32)
    h_, w_ = min(hpx, H - y0), m.shape[1]
    SH[y0:y0 + h_, x0:x0 + w_] = m[:h_]
    SH = blur(SH, 2.5)                                         # fix2: a crisper cast shadow (child-shaped blank)
    # the ring: one loose dry stroke of gold around where her head is, in frame space
    s = ctx.s
    hx = (HEAD_X - CX) * Z + 960
    hy = ((y0 + hpx * 0.11) - CY) * Z + 540
    R = 110                                                    # stays inside the gap: no character under it
    r = rng(5, 'ring')
    pts = []
    for k in range(15):
        a = -0.4 * np.pi + k / 14 * 1.82 * np.pi
        rr = R * (1 + 0.05 * np.sin(3 * a) + r.normal(0, 0.012))
        pts.append(((hx + rr * np.cos(a)) * s, (hy - 8 + rr * 0.86 * np.sin(a)) * s, 0.55 + 0.4 * np.sin(k / 14 * np.pi)))
    PAPER_RING = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED)
    # v3: static inscription on a veil of mist at the right edge (as B4)
    from tools.ink.inscription import inscription
    PFR = PAPER_RING
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(np.float32)
    nn = fbm(ctx.H, ctx.W, 260 * ctx.s, 31, 'veil', octaves=3) - 0.5
    VEIL = smoothstep(0.775, 0.865, xx / ctx.W + nn * 0.10).astype(np.float32)
    INS = inscription(ctx, 'H5', box=(1640, 120, 220, 720), paper=PFR)
    # v3 (§3.1): she is made of the same stuff as the stone: inside her shadow the same faint columns lie like
    # inclusions (her own, not the cliff's), and points of light read down them
    from shots._carve import Inner
    shf = view(None, CX, CY, Z, ctx.W, ctx.H, render=lambda box: _win2(SH, box))
    global INN, SHF
    SHF = np.clip(shf, 0, 1).astype(np.float32)
    INN = Inner((SHF > 0.5).astype(np.float32), qianziwen(160), SEAL_FONT, 40 * ctx.s, seed=8, density=0.20, start=120,
                inset=int(16 * ctx.s))
    RING = stroke(pts, width=9 * s, seed=12, paper=PAPER_RING, density=0.9, dry=0.45, dry_end=0.9, tint=GOLD)


def _win2(A, box):
    x0, y0, x1, y1 = box
    h, w = A.shape
    out = np.zeros((y1 - y0, x1 - x0), np.float32)
    a0, b0, a1, b1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    if a1 > a0 and b1 > b0:
        out[b0 - y0:b1 - y0, a0 - x0:a1 - x0] = A[b0:b1, a0:a1]
    return out


def render(t, ctx):
    u = 1.25 - 1.6 * ramp(t, T0 + 0.1, T1 - 0.6, 'linear')
    front = CX + (u - 0.5) * 1920 / Z
    bnd = band(XS, front, lead=480, trail=4000, flare=1.0)                # once reached, the writing stays lit
    lit = bnd * (1 - SH) ** 2                                                 # (H, W) map: the shadow keeps the light off
    amb = 0.95 - 0.42 * lit - 0.26 * SH * bnd                             # the shadow itself is a little darker
    flat = 0.95 + 0.04 * lit - 0.17 * SH * bnd                         # her shadow: a real cast shadow
    pool = np.clip((flat - amb) / np.maximum(1 - amb, 1e-3), 0, None)
    f = view(None, CX, CY, Z, ctx.W, ctx.H,
             render=lambda box: C.render((335, 12, 1.0), fill=0.65, ambient=amb, pool=pool, warmth=0.85, box=box))
    # fix2: inside her shadow the writing is NOT lit: the cinnabar in the cuts goes dull, no red reads there
    sh = view(None, CX, CY, Z, ctx.W, ctx.H, render=lambda box: _win2(SH * bnd, box))
    if sh.max() > 0.01:
        a = np.clip(sh * 1.15, 0, 1)
        pres = float(a.max())
        sc = ctx.s
        # smooth translucent stone: pale, a little light inside, the rock's fissures only just showing through, and
        # a soft wet rim like the ring stroke the stone itself is drawn with
        inner = smoothstep(0.35, 1.0, blur(SHF, 26 * sc))
        through = blur(f, 9 * sc)
        pale = PFR.rgb * np.array([0.965, 0.97, 0.965], np.float32) * (0.90 + 0.08 * inner)[..., None]
        stone = 0.80 * pale + 0.20 * through
        rim = SHF * (1 - smoothstep(0.50, 0.97, blur(SHF, 5 * sc)))
        stone = stone * (1 - 0.30 * rim[..., None] * (0.7 + 0.6 * fbm(ctx.H, ctx.W, 30 * sc, 6, 'h5rim')[..., None]))
        g = f.copy()
        g[:] = stone
        INN.lay(g, 1.0)
        for k in range(min(5, len(INN.cols))):
            ts = 170.2 + 0.45 * k
            u = (t - ts) / 1.05
            if 0 <= u < 1.3:
                INN.read(g, k, min(u, 1.0), sc, strength=1.0 if u <= 1 else max(0.0, 1 - (u - 1) / 0.3))
        f = f + (g - f) * a[..., None]
    # the ring is there from the moment the light passes her
    p = ramp(t, 170.6, 171.6, 'sine')
    if p > 0:
        RING.lay(f, p)
    f += (PFR.rgb - f) * VEIL[..., None]
    INS.draw(f)
    return f

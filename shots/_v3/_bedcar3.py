"""Shared helpers for team BED+CAR v3 (car F1 F3a F4a F6b; bedroom I1 I3a I4 J1 J4 K1 K2a L1 L2). Builds on _rooms26.

A v3 room shot = a Kling v4 take of a gpt-image-2 keyframe (media/kf/v3/), placed on the song clock by a piecewise time map
(work/bedcar/picks.json: shot -> {clip, map: [[song_t, src_t], ...]}), finished with paper fibre only: the v3 keyframes
already carry the room's light (one flashlight pool / dusk + amber), so the v2 crush grade is not applied (it greyed skin).
Layout authored in 1920x1080 px; everything scales by ctx.s.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *          # noqa: F401,F403
from tools.ink.video import decode, probe

PICKS3 = os.path.join(ROOT, 'work/bedcar/picks.json')


def pick3(name):
    return json.load(open(PICKS3))[name]


class Take:
    """A take on the song clock. map = [(song_t, src_t), ...] piecewise linear, clamped at both ends (holds).
    at(t) -> float32 frame; src(t) -> source seconds; twos=(ta, tb) plays that song interval on twos."""

    def __init__(self, name, ctx, crop=None):
        p = pick3(name)
        self.map = sorted([tuple(m) for m in p['map']])
        self.lips = False
        lp = p.get('lips')
        lpp = os.path.join(ROOT, lp['clip']) if lp else None
        if lp and not lp.get('paste') and os.path.exists(lpp) and os.path.getsize(lpp) > 50000 and not os.environ.get('BEDCAR_NO_LIPS'):
            # the LIPSYNC team's transfer onto the conformed take: plays 1:1 from song time t0 (docs/LIPSYNC_V3.md)
            p = dict(p, clip=lp['clip'])
            self.map = [(lp['t0'], 0.0), (lp['t0'] + 30.0, 30.0)]
            self.lips = True
        s0 = max(0.0, min(m[1] for m in self.map) - 0.05)
        s1 = max(m[1] for m in self.map) + 0.1
        if self.lips:
            s0, s1 = 0.0, 30.0
        path = os.path.join(ROOT, p['clip'])
        self.fps = float(probe(path)['rate'])
        self.s0 = s0
        fr = []
        for st, a in decode(path, s0, s1 - s0):
            if crop is not None:
                x0, y0, x1, y1 = crop
                a = a[y0:y1, x0:x1]
            a = cv2.resize(a, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA if a.shape[1] > ctx.W else cv2.INTER_CUBIC)
            fr.append(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
        self.f = np.stack(fr)
        self.n = len(fr)
        # lips.paste = [x, y] (1080p px): the LIPSYNC transfer was made on a native 1280x720 crop of this take (face big
        # enough for the transfer and the gate) baked through the same map; its frames go back over that region, 1:1
        # from song time lips.t0, so the framing stays free and only the lower face differs from the acted take.
        self.patch = None
        pl = pick3(name).get('lips') or {}
        pp = os.path.join(ROOT, pl['clip']) if pl.get('paste') and crop is None else None
        if pp and os.path.exists(pp) and os.path.getsize(pp) > 50000 and not os.environ.get('BEDCAR_NO_LIPS'):
            k = ctx.W / 1920.0
            x0, y0 = int(round(pl['paste'][0] * k)), int(round(pl['paste'][1] * k))
            pf = []
            for st, a in decode(pp, 0, None):
                w, h = int(round(a.shape[1] * k)), int(round(a.shape[0] * k))
                a = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
                pf.append(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
            self.patch = (np.stack(pf), x0, y0, float(pl['t0']))

    def src(self, t):
        xs = [m[0] for m in self.map]
        ys = [m[1] for m in self.map]
        return float(np.interp(t, xs, ys))

    def index(self, t):
        return int(np.clip(round((self.src(t) - self.s0) * self.fps), 0, self.n - 1))

    def at(self, t):
        f = self.f[self.index(t)].astype(F32) / 255.0
        if self.patch is not None:
            pf, x0, y0, pt0 = self.patch
            k = int(round((t - pt0) * 24.0))
            if 0 <= k < len(pf):
                h, w = pf[k].shape[:2]
                f[y0:y0 + h, x0:x0 + w] = pf[k].astype(F32) / 255.0
        return f


def fin(f, P, amount=0.5):
    return paper_fibre(f, P, amount)


def push(f, ctx, t, t0, t1, z0=1.0, z1=1.04, cx=960, cy=540, kind='inout'):
    """Zoom z0 -> z1 keeping the point (cx, cy) (1080p px) FIXED on screen (so z=1 is the untouched frame)."""
    u = ease(float(np.clip((t - t0) / max(t1 - t0, 1e-6), 0, 1)), kind)
    z = z0 + (z1 - z0) * u
    return move(f, ctx, z, cx + (960 - cx) / z, cy + (540 - cy) / z)


# ----------------------------------------------------------------------------- over-the-shoulder push into the page
PAGES = os.path.join(ROOT, 'media/comp/pages')
# the BOOK team's first frame shows this window of the spread (their B3 contract; K2b / I2 / I3b follow it)
UV_END = (0.031, 0.105, 0.969, 0.895)


def first_existing(names):
    for n in names:
        p = n if os.path.isabs(n) else os.path.join(PAGES, n)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(names)


SW3, SH3 = 3072, 2048                                   # the BOOK team's page-art size
Z0_3 = 1920.0 / (0.938 * SW3)                           # their whole-spread framing (frame px at 1080p per art px)
VIEW_SPREAD = (SW3 / 2, SH3 / 2, Z0_3)                  # (cx, cy, z) of a PageShot's frame 0


def view_rect(view):
    """Art-px rectangle (TL TR BR BL) that a PageShot camera (cx, cy, z) shows at 1920x1080."""
    cx, cy, z = view
    x0, x1, y0, y1 = cx - 960 / z, cx + 960 / z, cy - 540 / z, cy + 540 / z
    return np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])


def end_quad(view=VIEW_SPREAD):
    """Spread quad (1080p px, TL TR BR BL) at the end of the push: the camera `view` of the page art fills the frame."""
    cx, cy, z = view
    x0, y0 = 960 - cx * z, 540 - cy * z
    return np.float32([[x0, y0], [x0 + SW3 * z, y0], [x0 + SW3 * z, y0 + SH3 * z], [x0, y0 + SH3 * z]])


def _similarity(src, dst):
    """Best-fit similarity (2x3) taking quad src to quad dst."""
    M, _ = cv2.estimateAffinePartial2D(np.float32(src), np.float32(dst), method=cv2.LMEDS)
    return M


class PagePush:
    """Camera pushes from an over-shoulder plate into the page until the spread is the frame.
    q0: spread quad on the plate (1080p px, TL TR BR BL as read). art: flat page art path (both pages, on its own paper).
    The move is a similarity (scale + roll about the page: nothing bends) with the perspective correction blended in over
    the last `persp` of the move (the 2D warp on the page quad); the art crossfades from ink multiplied on the plate's lit
    paper to the BOOK shot's own first frame, so the last frame is exactly their frame 0."""

    def __init__(self, ctx, q0, art, end_img, view=VIEW_SPREAD, persp=0.40, lit=0.9):
        """end_img: the BOOK shot's own first frame at 1920x1080 (work/bedcar/ends/<ID>_f0.png); view: its camera."""
        self.ctx = ctx
        self.q0 = np.float32(q0)
        self.q1 = end_quad(view)
        a = load_image(art)
        if a.shape[1] != SW3:
            a = cv2.resize(a, (SW3, SH3), interpolation=cv2.INTER_AREA)
        self.end = load_image(end_img).astype(F32)
        self.vrect = view_rect(view)
        self.T = key_paper(a).astype(F32)                       # ink transmittance of the art
        self.S1 = _similarity(self.q0, self.q1)
        self.persp, self.lit = persp, lit
        h, w = a.shape[:2]
        self.rect = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

    def quad(self, u):
        """Spread quad at move progress u (0 = plate, 1 = flat page fills the frame)."""
        S = np.eye(2, 3, dtype=F32) * (1 - u) + self.S1 * u      # similarity interpolated (small roll: fine linearly)
        qs = (self.q0 @ S[:, :2].T) + S[:, 2]
        w = smoothstep(1 - self.persp, 1.0, u)
        return (qs * (1 - w) + self.q1 * w).astype(F32)

    def frame(self, plate, u, mask=None):
        """plate: HxWx3 at ctx size (the room frame, no art). mask: HxW where art may print (hands excluded)."""
        ctx = self.ctx
        s = ctx.s
        q0s = self.q0 * s
        Ha = cv2.getPerspectiveTransform(self.rect, q0s)                         # art -> plate
        Tw = cv2.warpPerspective(self.T, Ha, (ctx.W, ctx.H), flags=cv2.INTER_AREA, borderValue=(1, 1, 1))
        reg = cv2.warpPerspective(np.ones(self.T.shape[:2], F32), Ha, (ctx.W, ctx.H))
        m = reg if mask is None else reg * mask
        f = plate * (1 - m[..., None] * self.lit + m[..., None] * self.lit * Tw)
        if u <= 0:
            return f.astype(F32)
        qu = self.quad(u) * s
        Hc = cv2.getPerspectiveTransform(q0s, qu)                                # plate -> screen at u
        out = cv2.warpPerspective(f, Hc, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        w = smoothstep(0.55, 1.0, u)                                             # the sheet itself takes over
        if w > 0:
            Hp = cv2.getPerspectiveTransform(self.rect, qu)                      # art px -> screen at u
            dst = cv2.perspectiveTransform(self.vrect.reshape(1, 4, 2), Hp).reshape(4, 2)
            eh, ew = self.end.shape[:2]
            Hs = cv2.getPerspectiveTransform(np.float32([[0, 0], [ew, 0], [ew, eh], [0, eh]]), dst)
            sharp = cv2.warpPerspective(self.end, Hs, (ctx.W, ctx.H), flags=cv2.INTER_AREA)
            rm = cv2.warpPerspective(np.ones((eh, ew), F32), Hs, (ctx.W, ctx.H))
            rm = cv2.GaussianBlur(cv2.erode(rm, np.ones((int(40 * s) | 1,) * 2, np.uint8)), (0, 0), 14 * s) * (1 - w) + rm * w
            if mask is not None:
                mk = cv2.warpPerspective(mask.astype(F32), Hc, (ctx.W, ctx.H))
                rm = rm * (mk * (1 - w) + w)                                      # hands stay on top until late
            k = (rm * w)[..., None]
            out = out * (1 - k) + sharp * k
        return np.clip(out, 0, 1).astype(F32)


OTS_Q = [(285, 446), (1002, 192), (1208, 590), (510, 908)]     # the blank spread on the ots take (1080p px, TL TR BR BL as read)


class OtsPush:
    """The over-the-shoulder take with a BOOK page on its spread, pushed in to land on that BOOK shot's frame 0."""

    def __init__(self, ctx, take, art, end_img, view=VIEW_SPREAD, ta=None, tb=None, seed=45):
        self.B = Take(take, ctx)
        self.PP = PagePush(ctx, OTS_Q, first_existing([art]), os.path.join(ROOT, end_img), view)
        self.P = Paper(ctx.W, ctx.H, 'aged', seed=seed)
        self.ta, self.tb = ta, tb
        self.reg = np.ones((ctx.H, ctx.W), F32)

    def render(self, t, ctx):
        f = self.B.at(t)
        m = paper_mask(f, self.reg, warm=False, lo=0.55, soft=0.10, sat=(0.30, 0.45))
        u = ease(float(np.clip((t - self.ta) / (self.tb - self.ta), 0, 1)), 'inout')
        out = self.PP.frame(f, u, m)
        g = smoothstep(0.75, 1.0, u)                         # our fibre fades out as their sheet takes over
        return out if g >= 1 else fin(out, self.P, 0.5 * (1 - g))

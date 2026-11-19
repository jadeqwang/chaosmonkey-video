"""H6 'one hair that can't gather, blown on the gale' (172.750-177.208, 107 frames). BOOK team, v3.

Still the emptiest frame of the film: the bare book paper and ONE hair. v3: the hair is CURLED and the wind is visible
in it: it rides right to left on a rising and falling path, tumbles through a loop, is pulled out almost straight by
each gust and springs back into its curl. Over the last second and a half, as it nears the left edge, it begins to
become a monkey in a few strokes (the hair is his back and tail; then a head, two plumes, an arm, two legs, the red of
the face) and leaves the page mid-leap. Static inscription 一根毫毛 / 被狂风刮在半空 / 如何拢得身 upper right.
"""
import math

import numpy as np

from shots._mountain import *
from tools.ink.inscription import inscription

T0, T1 = 4146 / 24, 4253 / 24
GUSTS = [173.55, 174.9, 176.0]                      # the wind pulls it straight here (seconds)
T_MONKEY = T1 - 2.0
SS = 4                                              # supersampling of the little figure


def setup(ctx):
    global P, INS
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    INS = inscription(ctx, 'H6', box=(1440, 110, 380, 720), paper=P)
    global FIG, ORDER
    im = load_image('design/characters/monkey/monkey_storybook_figures.jpg')[195:475, 1150:1610][:, ::-1]
    T = key_paper(np.ascontiguousarray(im), lo=0.04, hi=0.14, gain=1.7)
    k = 250 * ctx.s / T.shape[0]
    FIG = cv2.resize(T, (int(T.shape[1] * k), int(T.shape[0] * k)), interpolation=cv2.INTER_AREA)
    fh, fw = FIG.shape[:2]
    xx = np.arange(fw, dtype=np.float32)[None, :] / fw
    ORDER = ((1 - xx) * 0.8 + 0.2 * fbm(fh, fw, 14 * ctx.s, 4, 'h6ord', octaves=2)).astype(np.float32)   # tail root first


def hair_pts(t, s):
    """The hair as a polyline in frame px (head end first), and its frame (origin, unit vectors, scale)."""
    u = (t - T0) / (T1 - T0)
    W, H = 1920 * s, 1080 * s
    x = (0.72 - 0.70 * u - 0.10 * max(0.0, u - 0.82) / 0.18) * W
    y = (0.50 + 0.085 * math.sin(u * 6.8 + 0.6) - 0.05 * u) * H
    straight = max(math.exp(-((t - g) / 0.16) ** 2) for g in GUSTS)
    mk = ramp(t, T_MONKEY, T_MONKEY + 0.5, 'inout')
    straight = max(straight, 0.55 * mk)
    curl = (1 - 0.88 * straight)
    tumble = 2 * math.pi * ramp(t, 174.0, 174.75, 'inout') * (1 - mk)      # one loop between the first two gusts
    ang0 = -0.22 + 0.25 * math.sin(u * 9.0) + tumble
    L = 300 * s
    n = 60
    pts = []
    px, py, a = x, y, ang0
    for i in range(n):
        v = i / (n - 1)
        pts.append((px, py))
        # curvature: a tight curl toward the tail, loosened by the gusts; a travelling ripple is the wind in it
        k = curl * (2.2 + 9.5 * v ** 1.6) + 1.3 * math.sin(v * 7.0 - t * 9.0) * (0.35 + 0.65 * v)
        a += k / n
        px += math.cos(a) * L / n
        py += math.sin(a) * L / n
    return pts, (x, y, ang0, mk)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    pts, (x, y, a0, mk) = hair_pts(t, s)
    D = np.zeros((ctx.H * SS // 1, ctx.W * SS // 1), np.float32) if False else None
    # draw in a local window, supersampled
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    pad = 220 * s
    bx0, by0 = int(min(xs) - pad), int(min(ys) - pad)
    bw, bh = int(max(xs) - min(xs) + 2 * pad), int(max(ys) - min(ys) + 2 * pad)
    D = np.zeros((bh * SS, bw * SS), np.float32)
    R = np.zeros_like(D)

    def to(p):
        return (int(round((p[0] - bx0) * SS * 16)), int(round((p[1] - by0) * SS * 16)))

    n = len(pts)
    for i in range(n - 1):
        v = i / (n - 1)
        w = (1.5 + 2.5 * mk * max(0.0, 1 - v / 0.3)) * s * (1 - 0.6 * v ** 3)     # the head end thickens into a back
        cv2.line(D, to(pts[i]), to(pts[i + 1]), 0.62 + 0.3 * mk * (v < 0.42), max(1, int(round(w * SS))), cv2.LINE_AA, 4)
    D = cv2.resize(D, (bw, bh), interpolation=cv2.INTER_AREA)
    R = cv2.resize(R, (bw, bh), interpolation=cv2.INTER_AREA)
    D = np.clip(D * (1 - R), 0, 1)
    D *= 0.72 + 0.5 * fbm(bh, bw, 5.0 * s, 9, 'h6dry', octaves=2)          # a dry brush, not a pen
    lay_ink(f, ink_T(np.clip(blur(D, 0.45 * s) * 1.05, 0, 1.2)), bx0, by0)
    if R.max() > 0:
        over(f, np.dstack([np.broadcast_to(CINNABAR, R.shape + (3,)), np.clip(R, 0, 1) * 0.92]).astype(np.float32),
             bx0, by0)
    if mk > 0:
        # the hair is his tail: the canon storybook monkey (running, mirrored to face the way the wind goes) comes up
        # out of it stroke by stroke, from the tail root forward to the head and the red of his face, as he leaves
        p = ramp(t, T_MONKEY + 0.2, T1 - 0.75, 'linear')
        fh, fw = FIG.shape[:2]
        A = smoothstep(0.0, 0.16, p * 1.2 - ORDER)
        T = 1 - (1 - FIG) * A[..., None]
        lay_at(f, T, x - fw * 0.80, y - fh * 0.42)
    INS.draw(f)
    return f

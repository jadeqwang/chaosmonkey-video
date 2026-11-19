"""E4 'The master leaned in close to his ear' (99.917-103.208, 79 frames). BOOK team, v4.

v4 (director: "the tail is moving with the finger ... let a video model do it"): the painting plate was repainted with
the monkey in costume B (gpt-image-2, work/book4/E4/repaint_c.png) and animated by kling-v4 (work/book4/E4/take_kling4_t3.mp4, clip frames 0-78 at native 24 fps,
first frame = the plate at this shot's framing): the master's finger curls and the monkey's tail flicks independently,
by the model. The clip is keyed to OUR paper (transmittance), tone-matched by the key; the sleeve leans from 100.9 as one
rigid piece (small rotation about the upper-right corner, the monkey kept out of the warp by a soft mask). The inscription
(key E4) is composited crisp on top. v3 script: shots/_v3/E4.py.
"""
import numpy as np

from shots._mountain import *
from tools.ink.inscription import inscription

T0, T1 = 2398 / 24, 2477 / 24
T_LEAN0, T_LEAN1 = 100.9, 103.1
import os
CLIP = os.environ.get('E4_CLIP', 'work/book4/E4/take_kling4_t3.mp4')
SPAN = float(os.environ.get('E4_SPAN', '78'))                         # clip frames spread over the shot's 79 frames (<78 = slow-mo)
CLIP_START = int(__import__('os').environ.get('E4_START', '0'))      # first clip frame used (clip is 24 fps, 121 frames)


def setup(ctx):
    global P, FR, MASK, INS
    W, H = ctx.W, ctx.H
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    cap = cv2.VideoCapture(str(ROOT / CLIP) if 'ROOT' in globals() else CLIP)
    raw = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        raw.append(f)
    n = int(round((T1 - T0) * 24))
    FR = []
    g0 = None
    for i in range(n):
        x = CLIP_START + i * SPAN / (n - 1)
        a = min(int(round(x)), len(raw) - 1); b = a; w = 0.0     # native rate: integer source frames
        f = cv2.addWeighted(raw[a], 1 - w, raw[b], w, 0) if w > 1e-3 else raw[a]
        f = cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32) / 255.0
        if g0 is None:
            g0 = np.median(f[int(H * .05):int(H * .25), int(W * .05):int(W * .25)].reshape(-1, 3), axis=0)
        FR.append(key_paper(f, ground=g0, lo=0.03, gain=1.5, feather=0.0, flat_field=False).astype(np.float32))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx / W - 0.435) / 0.098) ** 2 + ((yy / H - 0.66) / 0.23) ** 2)
    MASK = np.clip((1.0 - d) / 0.25 + 0.5, 0, 1)[..., None].astype(np.float32)          # 1 on the monkey, soft edge
    INS = inscription(ctx, 'E4', box=(170, 130, 220, 700), paper=P)


def render(t, ctx):
    i = min(max(int(round((t - T0) * 24)), 0), len(FR) - 1)
    T = FR[i]
    f = P.frame(t)
    f *= 1.0 - MASK * (1.0 - T)                           # monkey, unwarped
    u = ramp(t, T_LEAN0, T_LEAN1, 'inout')
    M = cv2.getRotationMatrix2D((ctx.W - 1.0, 0.0), -2.0 * u, 1.0)
    M[1, 2] += 22 * ctx.s * u
    S = cv2.warpAffine(1.0 - (1.0 - MASK) * (1.0 - T).astype(np.float32), M, (ctx.W, ctx.H),
                       flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(1.0, 1.0, 1.0))
    f *= np.clip(S, 0, 1)
    INS.draw(f)
    return f

"""D5 'One whisper, and the hundred come along' (69.292-73.500, 101 frames). BOOK team, v3 (REVISION_V3 §3.2).

The film's first pull-back, continuing D4's last frame. Structure carries the lesson: on each measured beat every
newly lit character passes the light on through its OTHER component to characters it has never touched, wherever
they are on the cliff (true IDS decomposition of the carved 千字文; chain in shots/_tong.py, listed in the log). Each
jump is a fine gold thread, drawn in three frames, that sinks to a faint line: by 'hundred' (70.97) more than a
hundred are lit and the threads are a constellation across the mountain. The last generations arrive without new
threads; on the gong (72.805) the few characters no jump could reach light too, the threads fade, and only the
carving glows. No rubbing flips or mis-registration (no measured chop falls in D5).
Static inscription 一窍通时 / 百窍通 on the veil of mist at the right (bare sky by the end of the pull-back).
"""
import numpy as np

from shots._mountain import *
from shots.D4 import build_wide, wide_frame, start_cam, Z_WIDE
from tools.ink.inscription import inscription

T0, T1 = 1663 / 24, 1764 / 24
T_GONG = on_frame(72.805)


def setup(ctx):
    global S, CAM, PF, VEIL, INS
    S = build_wide(ctx)
    C = S['C']
    cx, cy = start_cam(S)
    CAM = Camera([(T0, cx, cy, Z_WIDE), (72.75, C.W / 2 + 420, C.H / 2, 1920.0 / C.W * 1.04, 'sine')])
    PF = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED)
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(np.float32)
    n = fbm(ctx.H, ctx.W, 260 * ctx.s, 31, 'veil', octaves=3) - 0.5
    VEIL = smoothstep(0.775, 0.865, xx / ctx.W + n * 0.10).astype(np.float32)
    INS = inscription(ctx, 'D5', box=(1640, 120, 220, 700), paper=PF)


def render(t, ctx):
    cx, cy, z = CAM.at(t)[:3]
    f = wide_frame(S, t, cx, cy, z, ctx, t_end=T_GONG)
    f += (PF.rgb - f) * VEIL[..., None]
    INS.draw(f)
    return f

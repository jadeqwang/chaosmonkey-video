"""D8  79.292-82.500  the perch (stage team).

He plants the staff, goes up it and perches on top with a hand shading his eyes (搭凉棚), looking out over the
unpainted sea (bare paper to the left). Motion: Kling v4 first+last frame clip (canon 12 thrust -> canon 08 perched,
media/gen/stage/clips/stg_d8_kling4.mp4), keyed onto our sheet, on twos. Freeze on the snare 80.806 (亮相) with the
seal 倉; the clip's own settle plays after 8 frames (plumes a beat late). From 81.45 his ink, the staff and the seal
bleed back into the paper (bloom.dissolve) and the shot ends on nearly bare paper for the attic cut (D9).
"""
import numpy as np

from tools.ink import *
from tools.ink.video import Clip
from tools.stage.stage import seals, KeyRetime, clip_bbox, PAPER_SEED

T0, T1 = 79.291667, 82.5
T_HIT = 80.806                  # snare 0.89 on the beat grid
SRC_PERCH = 2.70                # clip time when he is up and set on the staff (measured)
SRC_END = 3.55                  # held from here (the dissolve needs a still figure)
T_DIS0, T_DIS1 = 81.45, 82.45   # the bleed back into the paper
SCALE = 0.92
STAFF_FOOT = (1270, 1040)       # where the staff foot stands (authoring px); the sea is the bare left


def setup(ctx):
    global P, CL, RT, POS, SEAL, BL, SEAL_POS, SC
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = Clip('work/ink_clips/stg_d8')
    SC = SCALE * s * 1920 / CL.w
    b = clip_bbox(CL, int(SRC_END * CL.fps))
    foot = ((b[0] + b[2]) / 2, b[3])
    POS = (int(STAFF_FOOT[0] * s - foot[0] * SC), int(STAFF_FOOT[1] * s - foot[1] * SC))
    RT = KeyRetime([(T0, 0.20), (T_HIT, SRC_PERCH), (T_HIT + 8 / 24, SRC_PERCH), (T_DIS0, SRC_END)],
                   twos=[(T0, T_HIT)], duration=CL.duration)
    SEAL = seals(s)
    SEAL_POS = ((STAFF_FOOT[0] + 250) * s, (STAFF_FOOT[1] - 640) * s)
    # the still figure that dissolves: its final pose on a full canvas
    full = np.ones((ctx.H, ctx.W, 3), np.float32)
    lay_ink(full, _layer(SRC_END), POS[0], POS[1])
    BL = bloom(full, seed=8, order='light')


def _layer(src):
    a = CL.at(src)
    w, h = int(round(CL.w * SC)), int(round(CL.h * SC))
    return np.clip(resize(a, w, h), 0, 1)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    q = ramp(t, T_DIS0, T_DIS1, 'in')
    if t < T_DIS0:
        lay_ink(f, _layer(RT.src(t)), POS[0], POS[1])
    else:
        f *= BL.dissolve(min(q * 1.08, 1.0))
    sl = f.copy()
    strike(sl, SEAL['cang'], t, T_HIT, SEAL_POS, overshoot=0.15)
    a = 1.0 - 0.92 * q                                   # the paste sinks back last, never quite gone
    f = f * (1 - a) + sl * a
    return shaken(f, *shake_offset(t, [T_HIT], amp=6 * s, dur=0.2))

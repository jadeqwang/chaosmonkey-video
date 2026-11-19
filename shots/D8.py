"""D8  79.292-82.500  the look-out perch (STAGE team, v4: costume B; staging as v2/v3).

He plants the staff, goes up it and perches on top with a hand shading his eyes (搭凉棚), looking out over the
unpainted sea (bare paper to the left). The hand goes up to his brow exactly on the snare 80.806 = 亮相 (freeze 8
frames) with the seal 倉; on that hit the pose is shown for 4 held frames as a stone rubbing (medium switch). From
81.45 his ink, the yellow, the staff and the seal sink back into the paper and the shot ends on nearly bare paper for
the attic cut (D9).
v4 motion: Kling v4 multi-keyframe (costume-B 03 lunge -> 13 plant -> 14 low -> 15 high -> 16 perched, one staff
length in all keyframes), media/gen/stage/v4/clips/s4_d8_k4a.mp4, keyed (pick of 3, blind rank 1). Fix for v3's
teleport frames: every climbing phase is a keyframe, so the climb is continuous in the source; the shot starts with the
staff already planted (clip f19; the abrupt swing-up at f16-17 is never shown) and is NOT put on twos (every source
pose is shown, ~2.1x). v3: shots/_v3/D8.py, media/comp/_v3/D8.mp4. v2: shots/_v2/D8.py.
"""
import numpy as np

from tools.ink import *
from tools.stage.stage3 import *

T0, T1 = 79.291667, 82.5
T_HIT = on_frame(80.806)
SRC = dict(start=19 / 24, up=73 / 24, perch=91 / 24, end=100 / 24)      # on top by `up`, hand at his brow by `perch`
T_UP = on_frame(80.36)
T_DIS0, T_DIS1 = 81.45, 82.45
SWITCH = [(80.806, 'rubbing')]
SCALE = 1.0
STAFF_FOOT = (1270, 1040)


def setup(ctx):
    global P, CL, RT, POS, SEAL, SEAL_POS, SC, DEN, FIB, COLR, MED
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = clip('s4_d8_k4a')
    SC = SCALE * s * 1920 / CL.w
    b = clip_bbox(CL, int(SRC['end'] * CL.fps))
    foot = ((b[0] + b[2]) / 2, b[3])
    POS = (int(STAFF_FOOT[0] * s - foot[0] * SC), int(STAFF_FOOT[1] * s - foot[1] * SC))
    RT = KeyRetime([(T0, SRC['start']), (T_UP, SRC['up']), (T_HIT, SRC['perch']), (T_HIT + 8 / 24, SRC['perch']),
                    (T_DIS0, SRC['end'])], duration=CL.duration)
    SEAL = seals(s)
    SEAL_POS = ((STAFF_FOOT[0] + 300) * s, (STAFF_FOOT[1] - 640) * s)
    full = np.ones((ctx.H, ctx.W, 3), np.float32)
    lay_ink(full, layer(CL, SRC['end'], SC), POS[0], POS[1])
    DEN = np.clip(full, 1e-3, 1)                       # the still figure (transmittance, colour kept)
    FIB = fbm(ctx.H, ctx.W, 5 * s, 8, 'd8fibre', octaves=3).astype(np.float32)
    COLR = None
    MED = Mediums(ctx.W, ctx.H, seed=9)


def render(t, ctx):
    s = ctx.s
    tp = hold_t(t, SWITCH)
    f = P.frame(t)
    q = ramp(t, T_DIS0, T_DIS1, 'sine')
    if t < T_DIS0:
        lay_ink(f, layer(CL, RT.src(tp), SC), POS[0], POS[1])
    else:
        u = min(q * 1.08, 1.0)
        # the whole figure sinks into the paper at once: its wash spreads (blur grows) and thins along the fibre
        d = blur(DEN, (0.5 + 6.0 * u) * s) if u > 0 else DEN
        keep = np.clip((1 - u) ** 1.6 * (1.0 + 0.6 * (FIB - 0.5) * u), 0, 1)
        f *= np.power(d, keep[..., None])
    sl = f.copy()
    strike(sl, SEAL['cang'], t, T_HIT, SEAL_POS, overshoot=0.15)
    a = 1.0 - 0.92 * q
    f = f * (1 - a) + sl * a
    f = shaken(f, *shake_offset(t, [T_HIT], amp=6 * s, dur=0.2))
    return switched(MED, f, t, SWITCH, P.rgb)

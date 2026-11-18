"""D7  76.417-79.292  staff flower 舞花 (STAGE team, v3: the yellow monkey; staging as v2).

Closer. The suona phrase is the stroke: the spinning staff lays rings of dry-brush 飞白 round him, wet where the staff
is and drying behind it, and what it has written STAYS on the paper (RingStain: the running maximum of the model's
own brush rings, so the persistent stroke is the one the living brush laid, not a drawn-on ellipse as in v2). He
drops into the lunge and the thrust lands 亮相 on the snare 78.808 (freeze 8 frames) with a 倉. Medium switches (the
same pose, 4 held frames): leather shadow puppet on the kick 77.919, red paper-cut on the landing 78.808 (v2 had a
hard jump inside the clip there).
Motion: Seedance 2.0 first+last (v3 canon 09 -> 12), media/gen/stage/v3/clips/s3_d7_sd20.mp4, keyed, on twos.
v2: shots/_v2/D7.py, media/comp/_v2/D7.mp4.
"""
import numpy as np

from tools.ink import *
from tools.stage.stage3 import *

T0, T1 = 76.416667, 79.291667
T_CUT, T_HIT = on_frame(77.919), on_frame(78.808)
SRC = dict(start=4 / 24, cut=60 / 24, hit=80 / 24, end=3.9)
SWITCH = [(77.919, 'shadow'), (78.808, 'papercut')]
SCALE = 0.98
CENTER = (930, 560)


def setup(ctx):
    global P, CL, RT, POS, SC, SEAL, MED, STAIN
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = clip('s3_d7_sd20')
    SC = SCALE * s * 1920 / CL.w
    POS = (int(CENTER[0] * s - CL.w * SC / 2), int(CENTER[1] * s - CL.h * SC / 2))
    RT = KeyRetime([(T0, SRC['start']), (T_CUT, SRC['cut']), (T_HIT, SRC['hit']), (T_HIT + 8 / 24, SRC['hit']),
                    (T1 + 0.05, SRC['end'])], twos=[(T0, T_CUT)], duration=CL.duration)
    STAIN = ctx.cache('s3_d7_stain2', lambda: RingStain(CL, 4, 76), deps=['work/ink_clips/s3_d7_sd20/meta.json'])
    SEAL = seals(s)
    MED = Mediums(ctx.W, ctx.H, seed=8)


def render(t, ctx):
    s = ctx.s
    tp = hold_t(t, SWITCH)
    f = P.frame(t)
    src = RT.src(tp)
    STAIN.lay(f, src, SC, POS, CL)
    lay_ink(f, layer(CL, src, SC), POS[0], POS[1])
    strike(f, SEAL['cang'], t, T_HIT, (1600 * s, 300 * s), overshoot=0.15)
    f = shaken(f, *shake_offset(t, [T_HIT], amp=7 * s, dur=0.2))
    return switched(MED, f, t, SWITCH, P.rgb)

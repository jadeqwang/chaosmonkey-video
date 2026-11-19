"""D7  76.417-79.292  staff flower 舞花 (STAGE team, v4: costume B; staging as v2/v3).

Closer. The suona phrase is the stroke: the spinning staff lays rings of dry-brush 飞白 round him, wet where the staff
is and drying behind it, and what it has written STAYS on the paper (RingStain: the running maximum of the model's
own brush rings, so the persistent stroke is the one the living brush laid, not a drawn-on ellipse as in v2). He
drops into the lunge and the thrust lands 亮相 on the snare 78.808 (freeze 8 frames) with a 倉. Medium switches (the
same pose, 4 held frames): leather shadow puppet on the kick 77.919, red paper-cut on the landing 78.808 (v2 had a
hard jump inside the clip there).
v4 motion: Kling v4 multi-keyframe (costume-B singles 09 staff flower -> 10 overhead spin -> 03 lunge),
media/gen/stage/v4/clips/s4_d7_k4a.mp4, keyed (pick of 3, blind rank 1: big black dry-brush fans, overhead spin, a
real one-handed thrust). The thrust at clip f88 is the 亮相 and is held to the end: the take's later re-pose to the
two-handed keyframe (f90-95) smears, so it is never shown. The clip is laid slightly larger than the frame (the
model's own frame edge cut the overhead spin's staff; now the staff simply leaves the frame).
v3: shots/_v3/D7.py, media/comp/_v3/D7.mp4. v2: shots/_v2/D7.py.
"""
import numpy as np

from tools.ink import *
from tools.stage.stage3 import *
from tools.ink.medium import medium_at

T0, T1 = 76.416667, 79.291667
T_CUT, T_HIT = on_frame(77.919), on_frame(78.808)
SRC = dict(start=2 / 24, cut=60 / 24, hit=88 / 24, end=89.5 / 24)
SWITCH = [(77.919, 'shadow'), (78.808, 'papercut')]
SCALE = 1.04
CENTER = (960, 536)


def setup(ctx):
    global P, CL, RT, POS, SC, SEAL, MED, STAIN
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = clip('s4_d7_k4a')
    SC = SCALE * s * 1920 / CL.w
    POS = (int(CENTER[0] * s - CL.w * SC / 2), int(CENTER[1] * s - CL.h * SC / 2))
    RT = KeyRetime([(T0, SRC['start']), (T_CUT, SRC['cut']), (T_HIT, SRC['hit']), (T_HIT + 8 / 24, SRC['hit']),
                    (T1 + 0.05, SRC['end'])], twos=[(T0, T_CUT)], duration=CL.duration)
    STAIN = ctx.cache('s4_d7_stain', lambda: RingStain(CL, 2, 86), deps=['work/ink_clips/s4_d7_k4a/meta.json'])
    STAIN.keep, STAIN.soft = 0.30, 12.0         # v4: a pale lasting ring, not blocky dashes
    SEAL = seals(s)
    MED = Mediums(ctx.W, ctx.H, seed=8)


def render(t, ctx):
    s = ctx.s
    tp = hold_t(t, SWITCH)
    f = P.frame(t)
    src = RT.src(tp)
    if medium_at(t, SWITCH, 4) is None:          # the print shows the figure only (the stain would cut as blobs)
        STAIN.lay(f, src, SC, POS, CL)
    lay_ink(f, layer(CL, src, SC), POS[0], POS[1])
    strike(f, SEAL['cang'], t, T_HIT, (1600 * s, 300 * s), overshoot=0.15)
    f = shaken(f, *shake_offset(t, [T_HIT], amp=7 * s, dur=0.2))
    return switched(MED, f, t, SWITCH, P.rgb)

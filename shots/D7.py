"""D7  76.417-79.292  staff flower 舞花 (stage team).

Closer. The suona phrase (72.02-79.91, the whole shot) is the stroke: the spinning staff leaves rings of dry-brush
飞白 that STAY on the paper (StaffTrail tracked from the clip's staff), on top of the rings the model paints and
lets fade. Motion: Seedance 2.0 first+last frame clip (canon 09 staff flower -> canon 12 thrust,
media/gen/stage/clips/stg_d7_sd20.mp4), keyed, on twos. On the kick 77.919 a HARD re-pose (a cut inside the clip,
no in-betweens) into the leap; he lands the thrust on the snare 78.808 = 亮相 (freeze 8 frames) with a 倉; the thrust
writes one straight line; the clip's settle then plays (plumes a beat late).
"""
import numpy as np

from tools.ink import *
from tools.ink.video import Clip
from tools.ink.roto import StaffTrail
from tools.stage.stage import seals, KeyRetime, PAPER_SEED, ring_path, tip_line

T0, T1 = 76.416667, 79.291667
T_CUT, T_HIT = 77.919, 78.808
SRC_A0, SRC_A1 = 0.30, 2.85      # the flower (rings)
SRC_B0, SRC_HIT, SRC_END = 3.25, 3.95, 4.35
SCALE = 0.98
CENTER = (930, 560)


def setup(ctx):
    global P, CL, RT, POS, SC, TR1, TR2, SEAL
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = Clip('work/ink_clips/stg_d7')
    SC = SCALE * s * 1920 / CL.w
    POS = (int(CENTER[0] * s - CL.w * SC / 2), int(CENTER[1] * s - CL.h * SC / 2))
    RT = KeyRetime([(T0, SRC_A0), (T_CUT - 1e-4, SRC_A1), (T_CUT, SRC_B0), (T_HIT, SRC_HIT),
                    (T_HIT + 8 / 24, SRC_HIT), (T1 + 0.05, SRC_END)], twos=[(T0, T_HIT)], duration=CL.duration)
    # 'staff' tracking locks onto his legs in this clip, so the staff ends are keypoints wheeling round his chest
    # (both ends write: two rings half a turn apart), 2.2 + 1.6 turns over the flower, and the thrust is one line
    ring_a = ctx.cache('stg_d7_ring_a2', lambda: ring_path(CL, SRC_A0, SRC_A1, 410, 2.2, 0.6),
                       deps=['work/ink_clips/stg_d7/meta.json'])
    ring_b = ctx.cache('stg_d7_ring_b2', lambda: ring_path(CL, SRC_A0 + 0.5, SRC_A1, 395, 1.6, 0.6 + np.pi),
                       deps=['work/ink_clips/stg_d7/meta.json'])
    line = ctx.cache('stg_d7_line', lambda: tip_line(CL, int(SRC_HIT * CL.fps), SRC_HIT - 0.3, SRC_HIT),
                     deps=['work/ink_clips/stg_d7/meta.json'])
    TR1 = [StaffTrail(r, width=w * s, scale=SC, pos=POS, paper=P, seed=4 + k, density=0.72, dry=0.62, chunk=900)
           for k, (r, w) in enumerate([(ring_a, 32), (ring_b, 18)])]
    TR2 = StaffTrail(line, width=20 * s, scale=SC, pos=POS, paper=P, seed=7, density=0.8, dry=0.75)
    SEAL = seals(s)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    src = RT.src(t)
    for tr in TR1:
        tr.lay(f, min(src, SRC_A1) if t < T_CUT else SRC_A1)
    if t >= T_CUT:
        TR2.lay(f, src)
    a = CL.at(src)
    L = np.clip(resize(a, int(round(CL.w * SC)), int(round(CL.h * SC))), 0, 1)
    lay_ink(f, L, POS[0], POS[1])
    strike(f, SEAL['cang'], t, T_HIT, (1560 * s, 330 * s), overshoot=0.15)
    return shaken(f, *shake_offset(t, [T_HIT], amp=7 * s, dur=0.2))

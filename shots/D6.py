"""D6  73.500-76.417  suona lead, no voice: the tumbling pass (stage team).

The monkey crosses the bare sheet right to left in a tumbling pass (筋斗), small against the corner mountain
(B_master keyed, the burst stone painted out), and lands in 亮相 on the strong kick 75.025. Motion: Kling v4
first+last frame clip (canon 14 running -> canon 01 亮相 on blank paper, media/gen/stage/clips/stg_d6_kling4.mp4),
keyed onto our sheet, played fast on twos, the layer drifting left as he tumbles so the pass spans the sheet.
On the landing: freeze 8 frames (亮相), woodblock mis-registration for two frames, a small 倉 seal; then the clip's
own last second plays at 1x (plumes and breath settling a beat late).
"""
import numpy as np

from tools.ink import *
from tools.ink.video import Clip
from tools.stage.stage import mountain, seals, KeyRetime, clip_bbox, PAPER_SEED

T0, T1 = 73.5, 76.416667
T_LAND = 75.025                 # kick 1.0 on the beat grid
SRC_LAND = 4.15                 # clip time where he settles in 亮相 (f~100, measured motion)
SCALE = 0.52                    # clip px -> authoring px (figure ~245 px tall against a 520 px mountain)
LAND_AT = (790, 1000)           # where his feet land (authoring px): just right of the mountain
DRIFT = 640                     # extra right-to-left travel of the layer during the tumble (px)


def setup(ctx):
    global P, CL, RT, MT, POS, SEAL, SC
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = Clip('work/ink_clips/stg_d6')
    SC = SCALE * s * 1920 / CL.w
    b = clip_bbox(CL, int(SRC_LAND * CL.fps))
    feet = ((b[0] + b[2]) / 2, b[3])
    POS = (LAND_AT[0] * s - feet[0] * SC, LAND_AT[1] * s - feet[1] * SC)
    RT = KeyRetime([(T0, 0.25), (T_LAND, SRC_LAND), (T_LAND + 8 / 24, SRC_LAND), (T1 + 0.1, SRC_LAND + 0.8)],
                   twos=[(T0, T_LAND)], duration=CL.duration)
    MT = mountain(ctx.W, ctx.H, s, x=36, base=1068, height=520)
    SEAL = seals(s)


def drift(t):
    """Extra leftward travel: DRIFT px at the start, 0 at the landing (stays put after)."""
    u = clamp((t - T0) / (T_LAND - T0), 0, 1)
    return DRIFT * (1 - u)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    f *= MT
    src = RT.src(t)
    L = _layer(src)
    lay_ink(f, L, int(POS[0] + drift(t) * s), int(POS[1]))
    strike(f, SEAL['cang_small'], t, T_LAND, ((LAND_AT[0] + 190) * s, (LAND_AT[1] - 250) * s), overshoot=0.12)
    if T_LAND <= t < T_LAND + 2 / 24:
        f = misregister(f, t, [T_LAND], amount=7 * s, paper=P.rgb, seed=6)
    return f


def _layer(src):
    a = CL.at(src)
    w, h = int(round(CL.w * SC)), int(round(CL.h * SC))
    return np.clip(resize(a, w, h), 0, 1)

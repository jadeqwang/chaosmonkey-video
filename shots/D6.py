"""D6  73.500-76.417  suona lead, no voice: the somersault across the Buddha's palm (STAGE team, v3; REVISION §3.5).

The whole composition is in frame from the first frame to the last: five colossal pillars stand in a sea of cloud at
the edge of the sky (left), after the 1806 絵本西遊記 leaf "悟空自驚在佛掌中" (refs/paintings/v3/02_buddha_palm_wuxingshan).
The yellow monkey comes in from the right in two great tucked somersaults (筋斗): he touches the cloud on the kick
74.353, lands on the kick 74.800 and snaps into 亮相 at the foot of the pillars on the kick 75.025 (freeze 8 frames,
small 倉). On that hit the page is shown for 4 held frames as a red paper-cut: five fingers, nails and all: the
pillars are a hand. (Replaces v2's 2-frame mis-registration.) Then the clip's own settle plays (scarf a beat late).

Plate: design/plates/D6_palm/D6_palm.jpg (sd5, our hand, from the public-domain print). With PLATE_CLIP present
(the same plate animated by a video model: slow travel, parallax between the fingers, mist; REVISION §13) the plate
is that clip, keyed; otherwise the still with layered parallax in code (stage3.palm_layers).
Monkey: Kling v4 first+last (v3 canon 14 -> 01), media/gen/stage/v3/clips/s3_d6_kling4.mp4, keyed, on twos.
v2 (dark monkey, corner mountain cropped at the top): shots/_v2/D6.py, media/comp/_v2/D6.mp4.
"""
import os
import numpy as np

from tools.ink import *
from tools.stage.stage3 import *

T0, T1 = 73.5, 76.416667
T_TOUCH, T_DOWN, T_LAND = on_frame(74.353), on_frame(74.800), on_frame(75.025)
SRC = dict(start=2 / 24, touch=42 / 24, down=73 / 24, land=92 / 24, end=4.6)
SWITCH = [(75.025, 'papercut')]
SCALE = 0.60                    # clip px (1920 wide) -> authoring px
LAND_AT = (1210, 935)           # his feet in the 亮相 (authoring px): on the cloud, right of the thumb
PLATE_CLIP = 'work/ink_clips/s3_d6pl'


def setup(ctx):
    global P, CL, RT, POS, SEAL, SC, PLATE, MED
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = clip('s3_d6_kling4')
    SC = SCALE * s * 1920 / CL.w
    b = clip_bbox(CL, int(SRC['land'] * CL.fps) + 8)
    feet = ((b[0] + b[2]) / 2, b[3])
    POS = (LAND_AT[0] * s - feet[0] * SC, LAND_AT[1] * s - feet[1] * SC)
    RT = KeyRetime([(T0, SRC['start']), (T_TOUCH, SRC['touch']), (T_DOWN, SRC['down']), (T_LAND, SRC['land']),
                    (T_LAND + 8 / 24, SRC['land']), (T1 + 0.1, SRC['end'])], twos=[(T0, T_LAND)], duration=CL.duration)
    PLATE = Palm(ctx)
    SEAL = seals(s)
    MED = Mediums(ctx.W, ctx.H, seed=7)


def render(t, ctx):
    s = ctx.s
    tp = hold_t(t, SWITCH)
    f = P.frame(t)
    dx = PLATE.lay(f, tp, T0, T1)                       # the plate; returns the near layer's shift (frame px)
    lay_ink(f, layer(CL, RT.src(tp), SC), int(POS[0] + dx), int(POS[1]))
    strike(f, SEAL['cang_small'], t, T_LAND, ((LAND_AT[0] + 210) * s + dx, (LAND_AT[1] - 300) * s), overshoot=0.12)
    return switched(MED, f, t, SWITCH, P.rgb)

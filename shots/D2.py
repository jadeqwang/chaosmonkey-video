"""D2  61.083-64.417  "He bowed four ways before the day had warmed" (STAGE team, v3: the yellow monkey).

Jade: "the animation could be smoother here, can we have a video model do it?" The four bows are now ONE performed
movement from a video model (Kling v4 from the v3 canon 亮相, media/gen/stage/v3/clips/s3_d2_kling4ff.mp4), keyed
onto our sheet: east (profile right), south (to us), west (profile left), north (his back to us). The take is
retimed so each bow's lowest point lands on its beat (61.321, 62.205, 63.090, 63.980: every second grid beat from
"bowed") and holds 2 frames; a seal is pressed on each: 才 才 才 仓 in a column under D1's 倉, like a 锣鼓经 score.
The wind-up for the first bow is in D1's last 21 frames (same clip, tools/stage/stage3.d2_retime).
Static inscription: key D2. From 63.817 the attic team's D2d (little Jade copies the last bow) may replace the tail.
Takes: s3_d2_kling4 (first+last: only S, W, N), s3_d2_sd20 (E S W N but steps on threes): see LOG_v3_stage.
v2 (hard re-poses of canon stills): shots/_v2/D2.py, media/comp/_v2/D2.mp4.
"""
import numpy as np

from tools.ink import *
from tools.ink.inscription import inscription
from tools.stage.stage import T_GONG
from tools.stage.stage3 import *

T0, T1 = 61.083333, 64.416667
SEAL_POS = (1410, 500)                  # D1's 倉


def setup(ctx):
    global P, CL, RT, SEAL, INS, SC, CAI
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = clip(D2_TAKE)
    SC = ctx.W / CL.w
    RT = d2_retime(CL.duration)
    SEAL = seals(s)
    CAI = [(SEAL_POS[0] * s, (SEAL_POS[1] + 150 + 106 * k) * s) for k in range(4)]
    INS = inscription(ctx, 'D2', box=(1560, 120, 260, 620), paper=P)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    lay_ink(f, layer(CL, RT.src(t), SC), 0, 0)
    INS.draw(f)
    strike(f, SEAL['cang'], t, T_GONG, (SEAL_POS[0] * s, SEAL_POS[1] * s))          # D1's seal stays on the sheet
    echoes(f, SEAL['cai'], t, list(zip(D2_BOWS[:3], CAI[:3])), decay=0.8, seed=5)
    strike(f, SEAL['cang_small'], t, D2_BOWS[3], CAI[3], overshoot=0.12)
    return shaken(f, *shake_offset(t, D2_BOWS, amp=4 * s, dur=0.14))

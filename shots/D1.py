"""D1  58.667-61.083  CRASH: the birth, the film's first full frame (STAGE team, v4: costume B).

One throw of ink crosses the sheet from the upper right and slaps down ON the hook gong (58.673, frame 1408 = the
shot's first frame), bursts and bleeds into the paper, and gathers into the brush-drawn monkey in 亮相 by 58.96; from
the beat 59.126 the 藤黄 wash floods through the figure from the chest (REVISION_V3 §3.4: "the yellow floods in as he
lands") and he is whole by the echo's second word. Seal 倉 beside him on the gong. Static inscription 五官俱备 / 四肢皆全
(key D1). Medium switches on the echo "(born fully formed)": the pose as a red paper-cut on "born" (59.595) and as a
stone rubbing on "fully" (60.02), 4 held frames each, the same pose (replaces v2's 2-frame rubbing flip). From frame
1445 (60.208) he lowers his leg and winds up for the first bow: these last 21 frames are the start of D2's clip
(its first frame is this shot's 亮相), so that the east bow can land on its beat 0.24 s into D2.

v4 (REVISION_V4 §1.4, §5 D): costume B (key-fret, leopard trim, red scarf). Source: MiniMax h3 2K first+last frame
(blank sheet -> costume-B 亮相, media/gen/stage/v4/clips/s4_d1_h3.mp4, 2560x1440, keyed at 1080): the splat bursts,
a black silhouette in the pose surfaces out of the blot, thins to an ink figure and the colour floods through.
Fixes v3's weak points: the pose is readable from ~59.1 and complete in colour by the paper-cut switch (59.595), and
the wind-up into D2 starts at frame 1451 (was 1445), so the 亮相 holds ~1.4 s (colour complete ~0.85 s); source is 2K.
Takes: s4_d1_h3 (pick, blind rank 1), s4_d1_sd20a/b/c (Seedance 2.0 1080p): see docs/logs/LOG_v4_stage.md.
v3 (all-yellow costume A): shots/_v3/D1.py, media/comp/_v3/D1.mp4. v2: shots/_v2/D1.py.
"""
import os
import numpy as np

from tools.ink import *
from tools.ink.inscription import inscription
from tools.stage.stage import T_GONG
from tools.stage.stage4 import *

T0, T1 = 58.666667, 61.083333
TAKE = os.environ.get('STAGE_D1_TAKE', 's4_d1_h3')
# clip times (s) measured on the take (tools/stage/prep3.py): impact, line figure set, flood starts, flood done
# h3: splat lands f7, the blot's peak f41, black silhouette in the pose f62, colour complete f84, hold to f123
SRC = {'s4_d1_h3': dict(hit=7 / 24, line=41 / 24, flood0=62 / 24, flood1=84 / 24, alive=110 / 24),
       's4_d1_sd20a': dict(hit=20 / 24, line=32 / 24, flood0=40 / 24, flood1=50 / 24, alive=90 / 24)}[TAKE]
TG = on_frame(T_GONG)
T_LINE, T_FLOOD0, T_FLOOD1 = on_frame(58.85), on_frame(59.15), on_frame(59.55)
SWITCH = [(59.595, 'papercut'), (60.02, 'rubbing')]
SEAL_POS = (1410, 500)


def setup(ctx):
    global P, CL, RT, SC, SEAL, INS, MED
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    CL = clip(TAKE)
    SC = ctx.W / CL.w
    RT = KeyRetime([(TG, SRC['hit']), (T_LINE, SRC['line']), (T_FLOOD0, SRC['flood0']), (T_FLOOD1, SRC['flood1']),
                    (D2_PRE, SRC['alive']), (T1 + 0.1, SRC['alive'] + 0.3)], duration=CL.duration)
    global CL2, RT2
    CL2 = clip(D2_TAKE)
    RT2 = d2_retime(CL2.duration)
    SEAL = seals(s)
    INS = inscription(ctx, 'D1', box=(1560, 120, 260, 620), paper=P)
    MED = Mediums(ctx.W, ctx.H, seed=6)


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    tp = hold_t(t, SWITCH)
    if t >= D2_PRE - 1e-6:
        lay_ink(f, layer(CL2, RT2.src(t), ctx.W / CL2.w), 0, 0)
    else:
        lay_ink(f, layer(CL, RT.src(tp), SC), 0, 0)
    INS.draw(f)
    strike(f, SEAL['cang'], t, T_GONG, (SEAL_POS[0] * s, SEAL_POS[1] * s), overshoot=0.16)
    f = shaken(f, *shake_offset(t, [T_GONG], amp=9 * s, dur=0.25))
    return switched(MED, f, t, SWITCH, P.rgb)

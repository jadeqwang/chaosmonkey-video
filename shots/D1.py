"""D1  58.667-61.083  CRASH: the film's first full frame (stage team).

One throw of splashed ink crosses the whole sheet from the upper right (airborne on frame 1408) and slaps down on the
hook gong 58.673 (frame 1409), gathering into the newborn in 亮相 (canon single 01, Liang Kai's splashed ink); the
excess dries to a pale rimmed stain that stays on the stage (D2 keeps it). Seal 倉 slams beside him on the gong.
"Born fully formed" as a small inscription; on the echo "(born fully formed)" (59.595) the sheet flips to a rubbing
for two frames. The 亮相 holds; the plumes settle a beat late (a small lag on the plume region).

SOURCE (env STAGE_D1): 'procedural' = the splash gathers into the canon single; 'hybrid' (default) = the same
procedural throw (flight, impact on the gong, spatter and the pale stain across the sheet) with the figure gathering
out of it taken from the Seedance 2.0 first+last clip (blank -> canon 01, media/gen/stage/clips/stg_d1_sd20.mp4: the
most real wet-ink bleed in the bake-off), its impact frame placed on the gong and its 1.5 s of gathering played 3x
on twos so he is set by the beat 59.126; then the 亮相 holds.
"""
import os
import numpy as np

from tools.ink import *
from tools.stage.stage import (d1_splash, d1_layout, seals, lyrics_on, T_GONG, LATIN, LATIN_IT, PAPER_SEED)

T0, T1 = 58.666667, 61.083333
SOURCE = os.environ.get('STAGE_D1', 'hybrid')
T_SET = 59.126                     # beat: he is set in 亮相
# fix round 2: the gong (58.673) falls inside frame 1408, D1's FIRST frame, so the impact is that frame (the splat
# with the throw's trailing streak, 倉 at full strength); the old in-flight throw frame is gone (it put the hit +1).
TG = on_frame(T_GONG)
DT0 = 0.014                        # the splat's age on its first frame (what the old frame 1409 showed)


def setup(ctx):
    global P, SP, TF, POS, SEAL, INS, ECHO, RB, T_ECHO, COL, L
    s = ctx.s
    tm = ctx.timing
    L = d1_layout(s)
    P = Paper(ctx.W, ctx.H, 'new', seed=PAPER_SEED)
    SP, TF, POS, COL = d1_splash(ctx.W, ctx.H, s, figure=(SOURCE == 'procedural'))   # COL: colour laid as he settles
    if SOURCE == 'hybrid':
        global CL, RT, CPOS, CSC
        from tools.ink.video import Clip
        from tools.stage.stage import KeyRetime, clip_bbox
        CL = Clip('work/ink_clips/stg_d1')
        b = clip_bbox(CL, 100)
        CSC = L['h'] * s / (b[3] - b[1])
        CPOS = (int(L['cx'] * s - (b[0] + b[2]) / 2 * CSC), int(L['base'] * s - b[3] * CSC))
        RT = KeyRetime([(TG - DT0, 1.50), (on_frame(T_SET), 3.10), (T1 + 0.1, 3.40)], twos=[(TG, on_frame(T_SET))],
                       duration=CL.duration)
    SEAL = seals(s)
    words = [(w, max(a, T_GONG + 0.04 * i), max(b, T_GONG + 0.04 * i + 0.1))
             for i, (w, a, b) in enumerate(tm.words('Born fully formed'))]
    INS = Inscription('Born fully formed', LATIN, region=(int(1058 * s), int(52 * s), int(330 * s), int(52 * s)),
                      size=ctx.size, vertical=False, words=words, mode='word', paper=P, seed=2, density=0.88)
    ew = [('born', 59.595, 59.98), ('fully', 60.02, 60.42), ('formed', 60.46, 61.0)]      # AUDIO_MAP line 13
    ECHO = Inscription('born fully formed', LATIN_IT, region=(int(1073 * s), int(112 * s), int(280 * s), int(40 * s)),
                       size=ctx.size, vertical=False, words=ew, start=59.595, end=60.6, mode='word', paper=P,
                       seed=4, density=0.45)
    T_ECHO = 59.595
    RB = Rubbing(ctx.W, ctx.H, seed=6)


def _has(tm, line):
    try:
        tm.words(line)
        return True
    except Exception:
        return False


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    dt = t - TG + DT0
    if SOURCE == 'hybrid':
        if dt >= 0:
            SP.draw(f, dt)
        # frame 1408 (6 ms before the gong): the clip's own wet throw in the air, not the procedural gob
        a = CL.at(RT.src(t) if dt >= 0 else 1.25)
        lay_ink(f, np.clip(resize(a, int(round(CL.w * CSC)), int(round(CL.h * CSC))), 0, 1), CPOS[0], CPOS[1])
    else:
        SP.draw(f, dt)
    # colour arrives with the figure's resolve
    k = smoothstep(0.15, 0.55, dt) if SOURCE == 'procedural' else 0
    if k > 0:
        C = 1 - (1 - COL) * k
        lay_ink(f, C, POS[0], POS[1])
    strike(f, SEAL['cang'], t, T_GONG, (L['seal'][0] * s, L['seal'][1] * s), overshoot=0.16)
    if lyrics_on(ctx):
        INS.draw(f, t)
        ECHO.draw(f, t)
    if flip_on(t, [T_ECHO], hold=2 / 24):
        f = RB.apply(f, P.rgb)
    return shaken(f, *shake_offset(t, [T_GONG], amp=9 * s, dur=0.25))

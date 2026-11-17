"""J3  192.833-196.625  drop 2: "before the day had warmed (warmed)" (stage team).

The full staff form across the blue-green heaven (D_heaven_mid, its densest window, ~73 % marks), the monkey larger
and wilder than in the hook. Motion: Kling v4 first+last frame clip (canon 11 overhead sweep -> canon 12 thrust,
media/gen/stage/clips/stg_j3_kling4.mp4), keyed, on twos. The staff tip writes a dry-brush stroke that STAYS
(StaffTrail tracked from the clip). The page cuts between 1988 (new paper, lit cinnabar by the neon) and 2026 (aged
paper under the flashlight) on the strongest drum hits (no chops are measured inside this shot): red -> white 193.459
-> red 194.103 -> white 194.963. The last sweep runs across that last cut: one stroke begun on the red page,
finished on the white. Thrust lands in 亮相 on 195.181 with a 倉; the echo "(warmed)" 195.650 re-presses it fainter.
A slow pull-back on the plate continues the J2-J5 pull-back.
"""
import os
import numpy as np

from tools.ink import *
from tools.ink.video import Clip
from tools.ink.roto import StaffTrail
from tools.stage.stage import heaven, seals, KeyRetime, lyrics_on, LATIN, PAPER_SEED, ring_path, sweep_to_tip

T0, T1 = 192.833333, 196.625
CUTS = [193.459, 194.103, 194.963]           # red -> white -> red -> white
T_LIANG, T_ECHO = 195.181, 195.650
SRC_SWEEP0, SRC_LIANG, SRC_END = 3.00, 3.85, 4.5     # measured: big sweep f72-f88, set f92     # clip times: last sweep starts / thrust set / tail
T_SWEEP0 = 194.70
SCALE = 1.12
CENTER = (960, 600)


def setup(ctx):
    global PN, PA, HN, HA, CL, RT, POS, SC, TRAIL, NF, FL, SEAL, INS, ECHO_POS, SEAL_POS
    s, W, H = ctx.s, ctx.W, ctx.H
    PN = Paper(W, H, 'new', seed=PAPER_SEED + 2)
    PA = Paper(W, H, 'aged', seed=PAPER_SEED + 2)
    HV = heaven(W, H)
    HN, HA = HV, aged_ink(HV, PA, 0.8)
    CL = Clip('work/ink_clips/stg_j3')
    SC = SCALE * s * 1920 / CL.w
    POS = (int(CENTER[0] * s - CL.w * SC / 2), int(CENTER[1] * s - CL.h * SC / 2))
    RT = KeyRetime([(T0, 0.25), (T_SWEEP0, SRC_SWEEP0), (T_LIANG, SRC_LIANG), (T_LIANG + 8 / 24, SRC_LIANG),
                    (T1 + 0.05, SRC_END)], twos=[(T0, T_LIANG)], duration=CL.duration)
    # 'staff' tracking locks onto his legs in these clips: the staff end is keypointed from the figure instead
    dep = ['work/ink_clips/stg_j3/meta.json']
    spin = ctx.cache('stg_j3_spin2', lambda: ring_path(CL, 0.3, 1.3, 470, 1.5, 0.0, squash=0.30, follow=0.3,
                                                      offset=(0, -240)), deps=dep)
    low = ctx.cache('stg_j3_low', lambda: ring_path(CL, 1.5, 2.3, 540, 0.8, 2.6, squash=0.45, follow=0.6,
                                                    offset=(0, 150)), deps=dep)
    last = ctx.cache('stg_j3_last', lambda: sweep_to_tip(CL, SRC_SWEEP0, SRC_LIANG, int(SRC_LIANG * CL.fps)), deps=dep)
    TRAIL = [StaffTrail(spin, width=26 * s, scale=SC, pos=POS, paper=PN, seed=3, density=0.7, dry=0.65, chunk=900),
             StaffTrail(low, width=30 * s, scale=SC, pos=POS, paper=PN, seed=4, density=0.75, dry=0.6, chunk=900),
             StaffTrail(last, width=44 * s, scale=SC, pos=POS, paper=PN, seed=5, density=0.9, dry=0.55, chunk=4000)]
    NF = neon_field(W, H, source=(2300 * s, -400 * s), reach=3200 * s)
    FL = flashlight_field(W, H, (980 * s, 560 * s), 1350 * s, tilt=-12, stretch=1.3)
    SEAL = seals(s)
    SEAL_POS = (1530 * s, 300 * s)
    ECHO_POS = (1530 * s + 18 * s, 300 * s + 190 * s)
    words = [('before', 192.83, 193.2), ('the', 193.23, 193.4), ('day', 193.43, 193.8), ('had', 193.83, 194.6),
             ('warmed', 194.69, 195.46)]                 # AUDIO_MAP line 57 (drop 2)
    INS = Inscription('before the day had warmed', LATIN, region=(int(560 * s), int(1006 * s), int(800 * s), int(50 * s)),
                      size=ctx.size, vertical=False, words=words, mode='word', paper=PN, seed=5, density=0.9)


def page_red(t):
    k = 0
    for c in CUTS:
        if t >= c:
            k += 1
    return k % 2 == 0


def pull(T, t, s):
    """Slow pull-back on the plate (1.10 -> 1.00 over the shot)."""
    z = 1.10 - 0.10 * ramp(t, T0, T1, 'linear')
    return transform(T, scale=z, out_size=(T.shape[1], T.shape[0]))      # about the centre


def render(t, ctx):
    s = ctx.s
    red = page_red(t)
    P, Hp = (PN, HN) if red else (PA, HA)
    f = P.frame(t)
    f *= pull(Hp, t, s)
    src = RT.src(t)
    for tr in TRAIL:
        tr.lay(f, src)
    a = CL.at(src)
    L = np.clip(resize(a, int(round(CL.w * SC)), int(round(CL.h * SC))), 0, 1)
    lay_ink(f, L, POS[0], POS[1])
    strike(f, SEAL['cang'], t, T_LIANG, SEAL_POS, overshoot=0.16)
    echoes(f, SEAL['cang'], t, [(T_ECHO, ECHO_POS)], first=0.45, seed=21)
    if lyrics_on(ctx):
        INS.draw(f, t)
    if os.environ.get('STAGE_NOLIGHT'):
        return f                                      # QA: coverage of the page itself, before the room's light
    if red:
        f = neon(f, 1.0, period=60.0, phase=0.0, field=NF, gain=0.82, ambient=0.16, tungsten=0.30)
    else:
        f = flashlight(f, (980 * s, 560 * s), 1350 * s, t=t, ambient=0.30, field=FL)
    return shaken(f, *shake_offset(t, [T_LIANG], amp=8 * s, dur=0.22))

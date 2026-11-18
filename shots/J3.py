"""J3  192.833-196.625  drop 2: "before the day had warmed (warmed)" (STAGE team, v3: the yellow monkey; staging as v2).

The full staff form across the blue-green heaven (D_heaven_mid, its densest window), the monkey larger and wilder
than in the hook. Motion: Kling v4 first+last (v3 canon 11 overhead sweep -> 12 thrust,
media/gen/stage/v3/clips/s3_j3_kling4.mp4), keyed, on twos. What the staff writes STAYS (RingStain: the running
maximum of the model's own wet dry-brush sweeps, laid by its living brush; v2 drew keypointed ellipses).
The page is the 1988 page (new paper under the red neon) until the kick 194.963, then the 2026 page (aged paper
under the flashlight): ONE cut, and the last great sweep runs across it: begun on the red page, finished on the
white (v2 cut red/white three times; with the medium switches that would be four changes of picture in two bars).
Medium switches (same pose, 4 held frames, on the strongest measured hits; no chops are measured in this shot):
red paper-cut on the snare 193.459, stone rubbing on the kick 194.103. Thrust lands in 亮相 on 195.181 with a 倉;
the echo "(warmed)" 195.650 re-presses it fainter. A slow pull-back on the plate continues the J2-J5 pull-back.
No Chinese inscription: the heaven fills the page (no blank), and the lyric layer carries the line.
v2: shots/_v2/J3.py, media/comp/_v2/J3.mp4.
"""
import os
import numpy as np

from tools.ink import *
from tools.ink.video import Clip
from tools.stage.stage import heaven
from tools.stage.stage3 import *

T0, T1 = 192.833333, 196.625
CUTS = [on_frame(194.963)]                           # red (1988) -> white (2026), once
SWITCH = [(193.459, 'papercut'), (194.103, 'rubbing')]
T_LIANG, T_ECHO = on_frame(195.181), on_frame(195.650)
SRC_SWEEP0, SRC_LIANG, SRC_END = 78 / 24, 95 / 24, 4.6     # last sweep starts / thrust set / tail
T_SWEEP0 = 194.70
SCALE = 1.12
from tools.ink.light import NEON_RED, TORCH as TORCH_C
CENTER = (960, 600)


def setup(ctx):
    global PN, PA, HN, HA, CL, RT, POS, SC, STAIN, NF, FL, SEAL, INS, ECHO_POS, SEAL_POS, MED
    s, W, H = ctx.s, ctx.W, ctx.H
    PN = Paper(W, H, 'new', seed=PAPER_SEED + 2)
    PA = Paper(W, H, 'aged', seed=PAPER_SEED + 2)
    HV = heaven(W, H)
    HN, HA = HV, aged_ink(HV, PA, 0.8)
    CL = clip('s3_j3_kling4')
    MED = Mediums(W, H, seed=10)
    SC = SCALE * s * 1920 / CL.w
    POS = (int(CENTER[0] * s - CL.w * SC / 2), int(CENTER[1] * s - CL.h * SC / 2))
    RT = KeyRetime([(T0, 0.25), (T_SWEEP0, SRC_SWEEP0), (T_LIANG, SRC_LIANG), (T_LIANG + 8 / 24, SRC_LIANG),
                    (T1 + 0.05, SRC_END)], twos=[(T0, T_LIANG)], duration=CL.duration)
    STAIN = ctx.cache('s3_j3_stain2', lambda: RingStain(CL, 6, 92, keep=0.8), deps=['work/ink_clips/s3_j3_kling4/meta.json'])
    # fix round 2 (QA 14): the 1988 red is LIGHT raking across the painting from the window (upper right), not a
    # filter: strong falloff to dark warm ink on the far side, the paper's tooth catching it, hot near the window
    global RED_L, WHITE_L
    I = neon_field(W, H, source=(2450 * s, -260 * s), reach=1400 * s, power=1.45)
    rake = 1.0 + 0.55 * (PN.height - 0.5) * (0.4 + 0.6 * I)           # raking light finds the fibre
    hot = smoothstep(0.50, 1.0, I) * 0.55
    col = NEON_RED[None, None] * (1 - hot[..., None]) + np.array([1.0, 0.70, 0.58], np.float32)[None, None] * hot[..., None]
    amb = np.array([0.20, 0.15, 0.125], np.float32)                     # dark warm ink, the greens still faintly there
    RED_L = ((I * rake * 1.18)[..., None] * col + amb[None, None]).astype(np.float32)
    # the 2026 page: a torch pool with real falloff (was ambient 0.30, a flat white)
    FL = flashlight_field(W, H, (980 * s, 560 * s), 1080 * s, tilt=-12, stretch=1.3)
    WHITE_L = (FL[..., None] * 1.04 * np.asarray(TORCH_C, np.float32)[None, None]
               + 0.075 * np.array([0.80, 0.74, 0.70], np.float32)[None, None]).astype(np.float32)
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
    tp = hold_t(t, SWITCH)
    sw = medium_at(t, SWITCH, 4) is not None
    f = P.frame(t)
    hv = pull(Hp, tp, s)
    if sw:                                   # in the other medium the heaven is a few ridge lines, he is the image
        hv = 1 - (1 - hv) * 0.22
    f *= hv
    src = RT.src(tp)
    STAIN.lay(f, src, SC, POS, CL)
    L = layer(CL, src, SC)
    # he is painted in body colour over the landscape (the yellow wash would vanish into the blue-green):
    # the paper is reserved under his silhouette, as a painter leaves the figure's place bare
    m = np.ones((ctx.H, ctx.W, 3), np.float32)
    lay_ink(m, L, POS[0], POS[1])
    k = np.clip((blur((1 - m.min(axis=2) > 0.10).astype(np.float32), 5 * s) - 0.35) / 0.3, 0, 1)[..., None]
    f = f * (1 - k) + P.frame(t) * k
    lay_ink(f, L, POS[0], POS[1])
    strike(f, SEAL['cang'], t, T_LIANG, SEAL_POS, overshoot=0.16)
    echoes(f, SEAL['cang'], t, [(T_ECHO, ECHO_POS)], first=0.62, seed=21)
    if lyrics_on(ctx):
        INS.draw(f, t)
    f = switched(MED, f, t, SWITCH, P.rgb)
    if os.environ.get('STAGE_NOLIGHT'):
        return f                                      # QA: coverage of the page itself, before the room's light
    f = np.clip(f * (RED_L if red else WHITE_L), 0, 0.985)
    return shaken(f, *shake_offset(t, [T_LIANG], amp=8 * s, dur=0.22))

"""D5 'One whisper, and the hundred come along' (69.292-73.500, 101 frames). Team MOUNTAIN.

The film's first pull-back. (1) From one face of the carved cliff (B_cliff_mid) the camera pulls back while the
columns light one after another (gold running up each, right to left). (2) On the measured fast roll
(71.692-71.925, five hits) the frame flips to its rubbing on every hit, and inside the flips the picture crosses to
the whole mountain (B_master): (3) the pull-back continues until 花果山 stands entire and lit on the page (its rock
carved as far texture, all gold), with a woodblock mis-registration on the gong (72.805). The four characters
一通百通 land as one vertical inscription in the blank (LXGW WenKai) with one red seal (lyrics switch:
ctx.opts['lyrics']).
"""
import numpy as np

from shots._mountain import *
from shots.C6 import MID_BLOCKS

T0, T1 = 1663 / 24, 1764 / 24
ROLL = [71.692, 71.76, 71.815, 71.87, 71.925]
T_GONG = 72.805
MS = 1920 / 3392.0                        # B_master zoom that shows the whole page


def setup(ctx):
    global CM, MASTER, MP, CAMB, INS, RB, ROLL_, PM
    raw = load_image(B + 'B_cliff_mid.png')
    H, W = raw.shape[:2]
    PM = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    CM = Cliff(PM.rgb * key_paper(raw, lo=0.03), qianziwen(160), SEAL_FONT, size=34, region=MID_BLOCKS, seed=6,
               weather=0.25, presence='plane', weight=0.02, paint=0.6, depth=1.2)
    CM.prepare(fill=0.4, gold=True, gold_stagger=0.7)
    raw = load_image(B + 'B_master.png')
    H, W = raw.shape[:2]
    MP = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    rock = MP.rgb * key_paper(raw, lo=0.03)
    text = qianziwen(160) * 6
    r = rng(8, 'cols')
    blocks = []
    for x in np.linspace(1240, 330, 15):                  # thin columns on the faces, right to left, as far texture
        x = float(x + r.uniform(-20, 20))
        top = 820 + 600 * abs(x - 780) / 520.0 + r.uniform(0, 120)
        blocks.append((x, top, 20, 1700 - top - r.uniform(0, 200)))
    cm = Cliff(rock, text, SEAL_FONT, size=13, region=blocks, row_gap=0.25, seed=8,
               weather=0.2, presence='auto', weight=0.02, paint=0.5)
    cm.prepare(fill=0.4, gold=True, gold_stagger=0.5)
    lit = cm.render((315, 30, 0.6), fill=0.4, gold=1.0, ambient=0.9, warmth=0.5, gold_stagger=0.5)
    MASTER = rock + (lit - rock) * 0.8
    RB = Rubbing(ctx.W, ctx.H, seed=6)
    ROLL_ = [h['t'] for h in ctx.timing.hits(None, 71.6, 72.0)] or ROLL
    INS = None
    if getattr(ctx, 'opts', {}).get('lyrics', True):
        s = ctx.s
        INS = Inscription('一通百通', KAI_FONT, region=(1520 * s, 160 * s, 150 * s, 600 * s), size=ctx.size,
                          vertical=True, start=71.95, end=72.75, mode='word', seal='悟空', seal_font=SEAL_FONT,
                          paper=Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED), seed=3)


def stage(t):
    """0: carved cliff; 1: whole mountain. The cross happens on the third roll hit, inside the flips."""
    return 0 if t < ROLL[2] else 1


def render(t, ctx):
    W, H = ctx.W, ctx.H
    if stage(t) == 0:
        u = ramp(t, T0, ROLL[2], 'linear')
        z = math.exp(math.log(1.7) + (math.log(0.66) - math.log(1.7)) * ease(u, 'out'))
        cx, cy = 1700 - 164 * u, 980 - 116 * u
        g = ramp(t, T0, 71.5, 'linear')
        f = view(None, cx, cy, z, W, H, render=lambda box: CM.render((310, 25, 0.8), fill=0.4, gold=g, ambient=0.85,
                                                                       warmth=0.6, gold_stagger=0.7, box=box))
        pv = view(PM.rgb, cx, cy, z, W, H)
    else:
        u = ramp(t, ROLL[2], T1, 'out')
        z = math.exp(math.log(1.35) + (math.log(MS) - math.log(1.35)) * u)
        cx, cy = 780 + (1696 - 780) * u, 1250 + (960 - 1250) * u
        f = view(MASTER, cx, cy, z, W, H)
        pv = view(MP.rgb, cx, cy, z, W, H)
        if INS is not None:
            INS.draw(f, t)
        if T_GONG <= t < T_GONG + 0.25:
            f = misregister(f, t, [T_GONG], amount=7 * ctx.s, paper=pv, seed=3, n=4)
    # rubbing on every hit of the roll: flipped from one hit to the next, back after the last
    k = sum(1 for x in ROLL_ if x <= t)
    if 0 < k < len(ROLL_) + 1 and t < ROLL_[-1] + 2 / 24 and k % 2 == 1:
        f = RB.apply(f, pv)
    return f

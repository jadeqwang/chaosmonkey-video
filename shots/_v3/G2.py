"""G2 'He wouldn't listen, so the gold pulls tight (听话) / on the monkey who picked a fight (听话)'
(127.458-134.375, 166 frames). Team MOUNTAIN.

The painted pilgrim monkey (C_pilgrim_band: grey robe, crouching, clutching his head), held still and framed so his
head sits at the centre of the strip the margins are closing to. Everything is grey; the band is the only colour:
gold. On each 听话 (130.175, 133.690, measured) the paper margins step in one notch (shared schedule:
shots/_margins.py) and the band pulls tight (it shrinks toward the centre of his head in a 3-frame snap, and his
head and hands give a small jolt).
"""
import numpy as np

from shots._mountain import *
from shots._margins import apply_margins, make_margins, T_STEP1, T_STEP2

T0, T1 = 3059 / 24, 3225 / 24
S = 0.5                                     # plate scale onto the canvas
PAD = 950                                   # bare paper to the left of the plate
HEAD = (1010, 1510)                         # head centre in plate px (band centre)


CLIP_SRC = 'media/gen/bk3_G2_kling4_t1_0f0c8d5083.mp4'      # v3: he TUGS at the band (kling-v4 from our plate)
CROP = (129.0, 1204.0, 3225.0 / 1920.0)                      # the clip's frame in plate px: x0, y0, plate px per clip px


def setup(ctx):
    global PIC, M, CXY, CLIP, RT, CPOS, CS, INS_A, INS_B, T_B
    from tools.ink.video import Clip, Retime
    from tools.ink.inscription import inscription
    H, W = int(3072 * S), int(5504 * S) + PAD
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    PIC = paper.rgb
    CLIP = Clip.prepare(CLIP_SRC, ground='light', height=1080, stabilise=False, smooth=0.4, lo=0.04, hi=0.14)
    RT = Retime(t0=T0, src0=0.4, rate=(CLIP.duration - 0.5) / (T1 - T0), duration=CLIP.duration)
    CS = CROP[2] * S * 1920.0 / CLIP.w                      # clip px -> canvas px
    CPOS = (PAD + CROP[0] * S, CROP[1] * S)
    hx, hy = PAD + HEAD[0] * S, HEAD[1] * S
    CXY = (hx, hy + 110)                     # camera: his head at frame (960, 430)
    M = make_margins(ctx.W, ctx.H, ground='paper')
    # v3: the sung lines as inscriptions on the page, in lieu of subtitles; the second arrives with its line
    PF = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED + 3)
    INS_A = inscription(ctx, 'G2a', box=(1560, 100, 240, 560), paper=PF)
    INS_B = inscription(ctx, 'G2b', box=(1260, 100, 240, 560), paper=PF, seed=2)
    T_B = on_frame(131.075)


def render(t, ctx):
    pic = PIC.copy()
    L = CLIP.layer(on_frame(t) if int(t * 24 + 1e-6) % 2 == 0 else on_frame(t) - 1 / 24.0, RT, scale=CS)   # on twos
    lay_ink(pic, L, int(round(CPOS[0])), int(round(CPOS[1])))
    jx = jy = 0.0
    for c in (on_frame(T_STEP1), on_frame(T_STEP2)):          # a jolt on each 听话
        d = t - c + 1e-9
        if 0 <= d < 0.25:
            jx += 3.0 * (1 - d / 0.25) * np.sin(d * 70)
            jy += 2.0 * (1 - d / 0.25)
    f = view(pic, CXY[0] - jx, CXY[1] - jy, 1.0, ctx.W, ctx.H)
    f = apply_margins(f, t, M)
    INS_A.draw(f)
    if t >= T_B - 1e-9:
        INS_B.draw(f)
    return f

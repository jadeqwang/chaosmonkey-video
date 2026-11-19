"""G2 'He wouldn't listen, so the gold pulls tight (听话) / on the monkey who picked a fight (听话)'
(127.458-134.375, 166 frames). Team MOUNTAIN.

The painted pilgrim monkey (C_pilgrim_band: grey robe, crouching, clutching his head), held still and framed so his
head sits at the centre of the strip the margins are closing to. Everything is grey; the band is the only colour:
gold. On each 听话 (130.175, 133.690, measured) the paper margins step in one notch (shared schedule:
shots/_margins.py) and the band pulls tight (it shrinks toward the centre of his head in a 3-frame snap, and his
head and hands give a small jolt).
"""
import os
import numpy as np

from shots._mountain import *
from shots._margins import apply_margins, make_margins, T_STEP1, T_STEP2

T0, T1 = 3059 / 24, 3225 / 24
GRADE = 1.0                                 # extra gain on the margin sheets (set by the measurement in NOTES)


CLIP_SRC = os.environ.get('G2_CLIP') or 'media/gen/bk4_G2_kling4_t3_3f08ff0f29.mp4'   # v4: costume B plate (gpt-image-2 t1), kling-v4 take 3
HEAD_CLIP = (595.0, 230.0)                                   # band centre in the clip frame (1920x1080 px)
ZOOM = 1.2                                                   # clip px -> frame px (the head about as big as v3's)
TH_SCALE = 1.6                                               # the child's 听话 is 1.6x the column text
TH_BOX = (300, 330, 150, 240)                                # blank, left margin (1080p authoring px): never over the monkey
TH_BOX2 = (150, 330, 150, 240)                               # the second 听话 stands beside the first (to its left)
TH_COLOUR = (0.62, 0.17, 0.12)                               # cinnabar: the child's voice vs the narrator's black columns
INK_FRAMES = 6


def setup(ctx):
    global PIC, M, CXY, CLIP, RT, CPOS, CS, INS_A, INS_B, T_B, TH, TH_T
    from tools.ink.video import Clip, Retime
    from tools.ink.inscription import inscription
    from shots._margins import SHEET_LIFT
    H, W = 1900, 3400
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    PIC = paper.rgb
    CLIP = Clip.prepare(CLIP_SRC, ground='light', height=1080, stabilise=False, smooth=0.4, lo=0.04, hi=0.14)
    RT = Retime(t0=T0, src0=0.4, rate=(CLIP.duration - 0.5) / (T1 - T0), duration=CLIP.duration)
    CS = ZOOM * 1920.0 / CLIP.w                             # clip px -> canvas px
    CPOS = (1200.0, 400.0)
    hx, hy = CPOS[0] + ZOOM * HEAD_CLIP[0], CPOS[1] + ZOOM * HEAD_CLIP[1]
    CXY = (hx, hy + 110)                     # camera: his head at frame (960, 430)
    M = make_margins(ctx.W, ctx.H, ground='paper')
    # v4 grade: the margin sheets sat ~9 levels above the neighbouring room shots (G1, G3); undo the SHEET_LIFT
    M.paper.rgb = np.clip(M.paper.rgb / SHEET_LIFT * GRADE, 0, 0.975).astype(np.float32)
    # v3: the sung lines as inscriptions on the page, in lieu of subtitles; the second arrives with its line
    PF = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED + 3)
    INS_A = inscription(ctx, 'G2a', box=(1560, 100, 240, 560), paper=PF)
    INS_B = inscription(ctx, 'G2b', box=(1260, 100, 240, 560), paper=PF, seed=2)
    T_B = on_frame(131.075)
    # v4: the child's two sung (听话), her own element: 1.6x, cinnabar, no narrator's seal. Lyric-file line (proposed):
    # G2c | G2 | (听话) | 听话   # NEW, BOOK v4, for Jade's proofread
    TH = [inscription(ctx, None, box=TH_BOX, paper=PF, text='听话', px=60 * TH_SCALE, seal=None, seed=21,
                      colour=TH_COLOUR),
          inscription(ctx, None, box=TH_BOX2, paper=PF, text='听话', px=60 * TH_SCALE, seal=None, seed=22,
                      colour=TH_COLOUR)]
    TH_T = [on_frame(T_STEP1), on_frame(T_STEP2)]


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
    for ins, t0 in zip(TH, TH_T):                              # (听话): 6-frame ink-in on the sung word, then static
        d = (t - t0) * 24.0 + 1e-6
        if d >= 0:
            ins.draw(f, opacity=float(min(1.0, (d + 1) / INK_FRAMES)))
    return f

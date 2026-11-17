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


def setup(ctx):
    global PIC, BAND, BAND_POS, M, CXY, HEADM
    raw = load_image('design/plates/C_elements/C_pilgrim_band.png')
    # the gold band: warm, saturated pixels around the head; cut it out and paint it back as hair under it
    r_, g_, b_ = raw[..., 0], raw[..., 1], raw[..., 2]
    box = np.zeros(raw.shape[:2], bool)
    box[1380:1660, 760:1280] = True
    gm = ((r_ - b_) > 0.16) & (r_ > 0.45) & box
    gm8 = cv2.dilate(gm.astype(np.uint8), np.ones((7, 7), np.uint8))
    clean = cv2.inpaint((raw * 255).astype(np.uint8), gm8, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    Tp = key_paper(clean, lo=0.04)
    Tp = cv2.resize(Tp, (int(Tp.shape[1] * S), int(Tp.shape[0] * S)), interpolation=cv2.INTER_AREA)
    H, W = Tp.shape[0], Tp.shape[1] + PAD
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    PIC = paper.rgb.copy()
    lay_ink(PIC, Tp, PAD, 0)
    ys, xs = np.where(gm8 > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    a = blur(gm[y0:y1, x0:x1].astype(np.float32), 1.0)
    band = np.dstack([raw[y0:y1, x0:x1], np.clip(a * 1.2, 0, 1)])
    BAND = cv2.resize(band, (int((x1 - x0) * S), int((y1 - y0) * S)), interpolation=cv2.INTER_AREA)
    BAND_POS = (PAD + x0 * S, y0 * S)
    hx, hy = PAD + HEAD[0] * S, HEAD[1] * S
    CXY = (hx, hy + 110)                     # camera: his head at frame (960, 430)
    M = make_margins(ctx.W, ctx.H, ground='paper')   # polish-1: lit page vs brighter bare-paper margins


def tight(t):
    """0 -> 1 -> 2 notches of tightening, each a 3-frame snap on a 听话."""
    k = 0.0
    for c in (on_frame(T_STEP1), on_frame(T_STEP2)):          # fix2: on the frame containing the 听话
        if t >= c - 1e-9:
            k += 0.75 + 0.25 * ease(min(1.0, (t - c) / (2 / 24)), 'out')
    return k


def render(t, ctx):
    pic = PIC.copy()
    k = tight(t)
    sc = 1.0 - 0.035 * k                    # the band pulls in toward the head
    bh, bw = BAND.shape[:2]
    nb = cv2.resize(BAND, (max(1, int(bw * sc)), max(1, int(bh * sc))), interpolation=cv2.INTER_AREA)
    bx = BAND_POS[0] + (bw - nb.shape[1]) / 2.0
    by = BAND_POS[1] + (bh - nb.shape[0]) / 2.0
    over(pic, nb, int(round(bx)), int(round(by)))
    # a small jolt of the whole figure on each 听话 (hands clench)
    jx = jy = 0.0
    for c in (on_frame(T_STEP1), on_frame(T_STEP2)):
        d = t - c + 1e-9
        if 0 <= d < 0.25:
            jx += 3.0 * (1 - d / 0.25) * np.sin(d * 70)
            jy += 2.0 * (1 - d / 0.25)
    f = view(pic, CXY[0] - jx, CXY[1] - jy, 1.0 * ctx.W / ctx.W, ctx.W, ctx.H)
    return apply_margins(f, t, M)

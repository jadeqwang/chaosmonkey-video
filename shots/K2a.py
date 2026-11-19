"""K2a (210.542-212.125; K2b by team BOOK starts at frame 5091 = 212.125) "He opened the Book of Life and Death".  BED+CAR v4.
Take('K2a') (two-pass act + animate, placed 1:1 at 210.2): the girl leaning over the open book, saying the line.  The room holds
on the take (the BOOK page print fades onto the open spread 211.45-211.70, i.e. as 'Book' opens), then from 211.70 the camera
pushes INTO the page (_bedcar3.PagePush, view VIEW_SPREAD: BOOK kept their whole-spread start) and the last frame (212.0833) is
BOOK's K2b frame 0 (work/bedcar4/ends/K2b_f0.png).  The girl's arm/hand stay on top (paper mask) until late in the move."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 210.54166666666666, 212.125
T_PUSH0 = float(os.environ.get('K2A_PUSH0', 211.70))
T_PUSH1 = 212.125 - 1 / 24.0          # the comp's last frame
T_PRINT0, T_PRINT1 = 211.45, 211.70
Q0 = [(785, 622), (1295, 822), (1094, 1165), (505, 858)]       # open spread on the take at src 1.5 (1080p px, TL TR BR BL)


def setup(ctx):
    global B, PP, P, REG
    B = Take('K2a', ctx)
    PP = PagePush(ctx, Q0, first_existing(['K2b_page_v4.png']), os.path.join(ROOT, 'work/bedcar4/ends/K2b_f0.png'), VIEW_SPREAD)
    P = Paper(ctx.W, ctx.H, 'aged', seed=45)
    REG = np.zeros((ctx.H, ctx.W), np.float32)
    cv2.fillPoly(REG, [np.int32(np.round(np.float32(Q0) * ctx.s))], 1.0)
    REG = cv2.GaussianBlur(REG, (0, 0), 1.5 * ctx.s)


def pmask(f):
    return paper_mask(f, REG, warm=False, lo=0.50, soft=0.10, sat=(0.30, 0.42))


def render(t, ctx):
    f = B.at(t)
    m = pmask(f)
    u = ease(float(np.clip((t - T_PUSH0) / (T_PUSH1 - T_PUSH0), 0, 1)), 'inout')
    out = PP.frame(f, u, m)
    w = float(np.clip((t - T_PRINT0) / (T_PRINT1 - T_PRINT0), 0, 1))
    if u <= 0 and w < 1:
        out = f * (1 - w) + out * w
    g = smoothstep(0.75, 1.0, u)
    return out if g >= 1 else fin(out, P, 0.5 * (1 - g))

"""E4 'The master leaned in close to his ear' (99.917-103.208, 79 frames). BOOK team, v3.

In the painting: the Master's long pale sleeve and hand enter from the upper right (the Master never seen whole); the
tiny storybook monkey bows toward the fingertip. v3: the hand is redrawn (C_master_sleeve_v3_1: a natural hand, index
finger extended, all joints joined; nano-banana-pro edit of the v2 plate, prompt beside it). The plate is split into
sleeve and monkey by connected components (the monkey is the component that holds the red face). When the band drops
away (100.9) the sleeve leans slowly toward the small monkey's ear; nothing else moves. Static inscription
祖师附耳 / 低言妙法 in the blank on the left.
"""
import numpy as np

from shots._mountain import *
from tools.ink.inscription import inscription

T0, T1 = 2398 / 24, 2477 / 24
T_LEAN0, T_LEAN1 = 100.9, 103.1
PLATE = 'design/plates/C_elements/elements_E4/C_master_sleeve_v3_1.jpg'


def setup(ctx):
    global P, SLEEVE, MONKEY, INS
    W, H = ctx.W, ctx.H
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    K = 1.45                                    # v3: closer, so the hand reads at 540p (monkey near frame centre-left)
    big = load_image(PLATE, size=(int(W * K), int(H * K)))
    ox, oy = int(855 * ctx.s), int(360 * ctx.s)
    raw = np.ascontiguousarray(big[oy:oy + H, ox:ox + W])
    T = key_paper(big, lo=0.03, gain=1.5)[oy:oy + H, ox:ox + W]
    d = 1 - T.min(axis=2)
    m = cv2.dilate((d > 0.05).astype(np.uint8), np.ones((int(9 * ctx.s) | 1,) * 2, np.uint8))
    n, lab = cv2.connectedComponents(m)
    red = (raw[..., 0] - raw[..., 2]) * (raw[..., 0] - raw[..., 1])
    red[:, int(W * 0.75):] = 0
    yy, xx = np.unravel_index(int(np.argmax(blur(red, 3 * ctx.s))), red.shape)
    mk = cv2.dilate((lab == lab[yy, xx]).astype(np.uint8), np.ones((int(15 * ctx.s) | 1,) * 2, np.uint8)) > 0
    MONKEY = np.where(mk[..., None], T, 1.0).astype(np.float32)
    SLEEVE = np.where(mk[..., None], 1.0, T).astype(np.float32)
    INS = inscription(ctx, 'E4', box=(170, 130, 220, 700), paper=P)


def render(t, ctx):
    f = P.frame(t)
    f *= MONKEY
    u = ramp(t, T_LEAN0, T_LEAN1, 'inout')
    ang = -3.0 * u                              # degrees, about the upper-right corner: the hand moves left
    M = cv2.getRotationMatrix2D((ctx.W - 1.0, 0.0), ang, 1.0)
    M[1, 2] += 40 * ctx.s * u                   # and sinks a little toward the ear
    S = cv2.warpAffine(SLEEVE, M, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                       borderValue=(1.0, 1.0, 1.0))
    f *= np.clip(S, 0, 1)
    INS.draw(f)
    return f

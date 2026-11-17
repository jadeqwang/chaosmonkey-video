"""E4 'The master leaned in close to his ear' (99.917-103.208, 79 frames). Team MOUNTAIN.

In the painting: the Master's long pale sleeve and hand enter from the upper right (the Master never seen whole);
the tiny canon storybook monkey bows toward the fingertip. Two keyed stills from C_master_sleeve: the sleeve layer
and the monkey. When the band drops away (100.9) the sleeve leans, slowly, toward the small monkey's ear (a small
rotation about the sleeve's upper-right corner, plus a little sink); nothing else moves.
"""
import numpy as np

from shots._mountain import *

T0, T1 = 2398 / 24, 2477 / 24
T_LEAN0, T_LEAN1 = 100.9, 103.1
MBOX = (2246, 1142, 486, 432)                # monkey box in plate px (PLATES.md)


def setup(ctx):
    global P, SLEEVE, MONKEY
    W, H = ctx.W, ctx.H
    P = Paper(W, H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    T = key_paper(load_image('design/plates/C_elements/C_master_sleeve.png', size=(W, H)), lo=0.03)
    k = W / 3840.0
    x, y, w, h = [int(round(v * k)) for v in MBOX]
    pad = int(14 * ctx.s)
    MONKEY = np.ones_like(T)
    MONKEY[y - pad:y + h + pad, x - pad:x + w + pad] = T[y - pad:y + h + pad, x - pad:x + w + pad]
    SLEEVE = T.copy()
    SLEEVE[y - pad:y + h + pad, x - pad:x + w + pad] = 1.0


def render(t, ctx):
    f = P.frame(t)
    f *= MONKEY
    u = ramp(t, T_LEAN0, T_LEAN1, 'inout')
    ang = -1.4 * u                              # degrees, about the upper-right corner: the hand moves left
    M = cv2.getRotationMatrix2D((ctx.W - 1.0, 0.0), ang, 1.0)
    M[1, 2] += 22 * ctx.s * u                   # and sinks a little toward the ear
    S = cv2.warpAffine(SLEEVE, M, (ctx.W, ctx.H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                       borderValue=(1.0, 1.0, 1.0))
    f *= np.clip(S, 0, 1)
    return f

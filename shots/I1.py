"""I1 (177.208-180.208) "Mischievous baby, Monkey's twin".  BED+CAR v3.

LAP_front, bedroom: Jade on the rug against the bed, the daughter in her lap, the book in front of both, flashlight in
hand. Jade reads the line like a dare; the daughter looks up at her; on "twin" (178.99) the squeeze, and the daughter
wriggles and laughs. Kling v4 first+last (media/kf/v3/I1.jpg -> I1_end.jpg), take in work/bedcar/picks.json.
In: out of the white page (H6 ends on bare paper): frame 0 is the lit page close (x3), pulled back to the room over 14
frames; then a very slow push on the two of them.
Round 2: the sung words play on a CLOSE lap two-shot (x1.5 on the same take, the LIPSYNC transfer for Jade pasted in:
picks.json I1.lips), widening to the full lap framing as she squeezes on "twin".
Out: from frame 56 (179.542) over Jade's shoulder onto the spread (the I2 page, team BOOK) and into it: the push lands
exactly on frame 0 of media/comp/pages/I2_full.mp4 (their whole-spread framing).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 177.20833333333334, 180.20833333333334
PAGE_C = (1270, 860)        # the lit right page in the take (1080p px)
FIG_C = (1330, 520)
N_OUT = 14
FACE_C, Z_CU = (980, 395), 1.5       # the close lap two-shot: Jade's face about 135 px high at 540p
T_WIDE0, T_WIDE1 = 178.80, 179.20   # widen as she squeezes on 'twin' (178.99)
T_OTS = 4309 / 24.0


def setup(ctx):
    global B, P
    B = Take('I1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=27)
    global O
    O = OtsPush(ctx, 'ots_I1', 'I2_page.png', 'work/bedcar/ends/I2page_f0.png', ta=T_OTS - 0.05, tb=T1)


def render(t, ctx):
    if t >= T_OTS - 1e-6:
        return O.render(t, ctx)
    k = frame_of(t) - frame_of(T0)
    f = B.at(t)
    if k < N_OUT:                                            # out of the white page onto the two faces, close
        u = ease(k / N_OUT, 'expo_out')
        z = math.exp(math.log(3.0) * (1 - u) + math.log(Z_CU) * u)
        cx, cy = PAGE_C[0] + (FACE_C[0] - PAGE_C[0]) * u, PAGE_C[1] + (FACE_C[1] - PAGE_C[1]) * u
        f = move(f, ctx, z, cx, cy)
        w = max(0.0, 1 - k / 4.0) * 0.85                     # the page's white, gone in 4 frames
        f = f * (1 - w) + np.array([0.93, 0.90, 0.83], F32) * w
    else:                                                    # close on the sung words, then out to the wide for the squeeze
        u = ease(float(np.clip((t - T_WIDE0) / (T_WIDE1 - T_WIDE0), 0, 1)), 'inout')
        z = math.exp(math.log(Z_CU) * (1 - u))
        cx, cy = FACE_C[0] + (960 - FACE_C[0]) * u, FACE_C[1] + (540 - FACE_C[1]) * u
        f = move(f, ctx, z, cx, cy)
    return fin(f, P)

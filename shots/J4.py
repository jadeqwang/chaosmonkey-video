"""J4 (196.625-200.667) "No cradle, no song (no song)".  BED+CAR v3: the split screen of the two storytimes.

Left half: 1988, the attic in red neon (team ATTIC: media/comp/J4_1988.mp4, 960x540, the song frames of J4; columns
240..720 of it). Right half: 2026, the bedroom in flashlight white (Kling v4 take of media/kf/v3/J4_2026.jpg, the columns
around Jade and the daughter). Each mother with her child in her lap, the book in front of both, same framing; a thin strip
of bare paper between the halves. All four sing; on the echo hit 198.833 both children throw their arms up at once (agreed
with ATTIC: arms start 198.74, up by 198.833, held to the cut).
Until ATTIC's half exists the left half is their keyframe media/kf/v3/J4.jpg as a still (placeholder).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 196.625, 200.66666666666666
LEFT = 'media/comp/J4_1988.mp4'
LEFT_X = (240, 720)            # columns of the 960-wide attic comp
RIGHT_X = (500, 1460)          # columns of my 1920-wide take (the pair sits at x ~980)
STRIP = 22                     # bare paper between the halves (1080p px)


def setup(ctx):
    global B, P, PB, L, LSTILL
    B = Take('J4', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=47)
    PB = Paper(ctx.W, ctx.H, 'new', seed=48)
    L, LSTILL = None, None
    hw = (ctx.W - int(STRIP * ctx.s)) // 2
    if os.path.exists(os.path.join(ROOT, LEFT)):
        fr = []
        for st, a in decode(os.path.join(ROOT, LEFT), 0, None):
            a = a[:, LEFT_X[0] * a.shape[1] // 960: LEFT_X[1] * a.shape[1] // 960]
            fr.append(np.clip(cv2.resize(a, (hw, ctx.H), interpolation=cv2.INTER_CUBIC) * 255 + 0.5, 0, 255).astype(np.uint8))
        L = np.stack(fr)
    else:
        a = load_image(os.path.join(ROOT, 'media/kf/v3/J4.jpg'))
        w = a.shape[1]
        LSTILL = cv2.resize(a[:, w // 4: 3 * w // 4], (hw, ctx.H), interpolation=cv2.INTER_AREA).astype(F32)


def render(t, ctx):
    s = ctx.s
    hw = (ctx.W - int(STRIP * s)) // 2
    f = PB.frame(t)
    if L is not None:
        k = int(np.clip(frame_of(t) - frame_of(T0), 0, len(L) - 1))
        left = L[k].astype(F32) / 255.0
    else:
        left = fin(LSTILL, P)[:, :hw] if False else LSTILL
    r = fin(B.at(t), P)
    x0, x1 = int(RIGHT_X[0] * s), int(RIGHT_X[1] * s)
    right = cv2.resize(r[:, x0:x1], (hw, ctx.H), interpolation=cv2.INTER_AREA)
    f[:, :hw] = left
    f[:, ctx.W - hw:] = right
    return f

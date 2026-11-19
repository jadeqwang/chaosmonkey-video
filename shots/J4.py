"""J4 (196.625-200.667) "No cradle, no song (no song)".  BED+CAR v4: the split screen of the two storytimes.
Left half: 1988, the attic in red neon (team ATTIC: media/comp/J4_1988.mp4, 960x540, 97 frames; columns 240..720).  Right half: 2026,
Take('J4R') (two-pass act + animate, placed 1:1 at 196.3; flashlight white), columns RIGHT_X of the 1920 frame.  Thin strip of bare
paper between.  EXPOSURE: ATTIC's half is bright/pink, the bedroom is dark, so each half gets one constant RGB gain (hue kept) that
brings its mean luma to the mean of the two (clamped to 0.75..1.6); faces are not re-coloured otherwise.
Re-renders when ATTIC replaces J4_1988.mp4 (the gains are recomputed in setup)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 196.625, 200.66666666666666
LEFT = 'media/comp/J4_1988.mp4'
LEFT_X = (240, 720)            # columns of the 960-wide attic comp
RIGHT_X = (480, 1440)          # columns of my 1920-wide take (Jade + daughter at x ~ 700-1420, her arms out to ~620 when up)
STRIP = 22                     # bare paper between the halves (1080p px)
GAIN_CLAMP = (0.75, 1.6)


def _luma(a):
    return float((0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).mean())


def setup(ctx):
    global B, P, PB, L, GL, GR, MEANS
    B = Take('J4R', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=47)
    PB = Paper(ctx.W, ctx.H, 'new', seed=48)
    hw = (ctx.W - int(STRIP * ctx.s)) // 2
    fr = []
    for st, a in decode(os.path.join(ROOT, LEFT), 0, None):
        a = a[:, LEFT_X[0] * a.shape[1] // 960: LEFT_X[1] * a.shape[1] // 960]
        fr.append(np.clip(cv2.resize(a, (hw, ctx.H), interpolation=cv2.INTER_CUBIC) * 255 + 0.5, 0, 255).astype(np.uint8))
    L = np.stack(fr)
    ml = float(np.mean([_luma(f[::4, ::4].astype(F32) / 255.0) for f in L[::3]]))
    s = ctx.s
    x0, x1 = int(RIGHT_X[0] * s), int(RIGHT_X[1] * s)
    mr = float(np.mean([_luma(B.f[i][::4, x0:x1:4].astype(F32) / 255.0) for i in range(0, B.n, 3)]))
    tgt = 0.5 * (ml + mr)
    GL = float(np.clip(tgt / ml, *GAIN_CLAMP))
    GR = float(np.clip(tgt / mr, *GAIN_CLAMP))
    MEANS = (ml, mr, tgt, GL, GR)
    print('J4 means left %.3f right %.3f target %.3f gains L %.3f R %.3f' % MEANS)


def render(t, ctx):
    s = ctx.s
    hw = (ctx.W - int(STRIP * s)) // 2
    f = PB.frame(t)
    k = int(np.clip(frame_of(t) - frame_of(T0), 0, len(L) - 1))
    left = np.clip(L[k].astype(F32) / 255.0 * GL, 0, 1)
    r = fin(B.at(t), P)
    x0, x1 = int(RIGHT_X[0] * s), int(RIGHT_X[1] * s)
    right = np.clip(cv2.resize(r[:, x0:x1], (hw, ctx.H), interpolation=cv2.INTER_AREA) * GR, 0, 1)
    f[:, :hw] = left
    f[:, ctx.W - hw:] = right
    return f

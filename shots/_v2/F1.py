"""F1 (107.042-108.833) '石头里蹦出来 没有童年'.  ROOMS-26; fix round 2 (QA items 7 and 9).

Hard cut on the pickup: 2026, dusk on the highway. The daughter in her car seat raps, deadpan (sd25 lip-sync).
Fix 2: the clip's own amber passes are taken out (a low-frequency light ratio against the take's darkest plate:
the static cabin keeps its detail, only the passing light goes), and ONE streetlight sweep slams across the cabin
on the rap crash 107.975 (frame 2592): there within 4 frames, then it passes left to right. Reframed in comp
(x1.30) so her face sits on the right third and the side window on the left carries the sweep. Car grade, fibre.
Lyric unchanged (WenKai, top centre).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _car_grade import car_grade, amber_sweep

T0, T1 = 107.04166666666667, 108.83333333333333
FACES = [(960, 330, 260, 300), (960, 640, 260, 200)]
T_CRASH = 107.975
F_CRASH = frame_of(T_CRASH)                     # 2592
Z, CX, CY = 1.30, 714, 470                     # face (960, 330) -> x 1280 (right third), y 358


def setup(ctx):
    global B, P, WORDS, CLEAN
    B, _ = base_for('F1', 'media/kf/F1.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=31)
    WORDS = words_of(ctx, '石头里蹦出来', 107.04)
    CLEAN = None
    if hasattr(B, 'f'):
        # the darkest plate (no streetlight), as low-frequency light per channel
        dark_i = np.argsort(B.f.reshape(B.n, -1).mean(1))[: max(3, B.n // 6)]
        ref = B.f[dark_i].astype(F32).mean(0) / 255.0
        CLEAN = cv2.GaussianBlur(ref, (0, 0), 30 * ctx.s) + 1e-3


def unlight(f, ctx):
    """Take the clip's passing amber out: scale each pixel by the darkest plate's low-frequency light over this frame's."""
    if CLEAN is None:
        return f
    lf = cv2.GaussianBlur(f, (0, 0), 30 * ctx.s) + 1e-3
    r = np.clip(CLEAN / lf, 0.45, 1.05)
    return np.clip(f * r, 0, 1).astype(F32)


def render(t, ctx):
    fi = frame_of(t)
    f = unlight(B.at(t), ctx)
    f = car_grade(f, ctx, FACES, dark=0.66)
    if fi >= F_CRASH:                           # the slam: full within 4 frames, then it passes
        env = min(1.0, (fi - F_CRASH + 1) / 4.0)
        f = amber_sweep(f, ctx, t, T_CRASH + 0.28, 0.80, angle=-28, width=440, gain=1.25 * env)
    f = paper_fibre(f, P, 0.5)
    f = move(f, ctx, Z, CX, CY)
    lyric(f, ctx, sung(WORDS, t, tail=0.4, sep=''), x=0.5, y=0.065, px=30)
    return f

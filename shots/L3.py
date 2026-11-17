"""L3 235.833-238.333 (60 f). Team ROOMS-88; fix round 2 (QA item 1: the click-off).

The flashlight clicks off on the last hit (235.833 = frame 5660, L3's frame 0): 2026 is dark. L3 opens on the film's
night black (A1's pre-sign black, never #000) held for 10 frames. Then the 1988 window is simply there in the dark,
lower right, small, its neon humming cinnabar: it comes up over 3 frames as the eye adjusts, the rest of the attic
barely visible (darker than A1). At 237.840 (frame 5709) the hum cuts and the neon goes off between one frame and the
next: the bare dusty glass stays a faint grey for 2 frames, then night black to the end of audio.
"""
from shots._rooms88 import *
import shots.A1 as A1

T0, T1 = 5660 / 24, 5720 / 24
F_CLICK = frame_of(235.833)          # 5660: the flashlight's off (the last hit)
N_BLACK = 10                         # night black
N_ADJUST = 3                         # the eye adjusts: the window comes up over 3 frames
F_OFF = frame_of(237.840)            # 5709: the hum cuts, the neon goes off hard
N_GREY = 2                           # the glass stays a faint grey, then black
ROOM = 0.55                          # the attic outside the window, against A1's level (barely visible)


def setup(ctx):
    global BLACK, WIN, OFFG
    A1.setup(ctx)
    W, H, s = ctx.W, ctx.H, ctx.s
    b0 = finish(A1.OFF.copy(), A1.G, A1.TEX) * 0.18                   # A1's black before the sign ...
    ink = np.median(b0.reshape(-1, 3), axis=0)                          # ... as one flat night tone (no window
    BLACK = (ink * (1 + (A1.TEX - 1) * 0.9)).astype(F32)                # ghost in it), paper fibre showing
    x0, y0, x1, y1 = A1.WINDOW
    m = np.zeros((H, W), F32)
    pad = 40
    cv2.rectangle(m, (int((x0 - pad) * s), int((y0 - pad) * s)), (int((x1 + pad) * s), int((y1 + pad) * s)), 1.0, -1)
    WIN = cv2.GaussianBlur(m, (0, 0), 45 * s)[..., None]               # the window and its own red spill
    glass = cv2.GaussianBlur(A1.SG.glass, (0, 0), 1.5 * s)[..., None]
    off = finish(A1.OFF.copy(), A1.G, A1.TEX)
    OFFG = BLACK + (np.maximum(off, BLACK) - BLACK) * np.clip(glass * 1.4, 0, 1) * 0.75   # the glass a faint grey


def render(t, ctx):
    fi = frame_of(t)
    k = fi - F_CLICK
    if k < N_BLACK or fi >= F_OFF + N_GREY:
        return BLACK.copy()
    if fi >= F_OFF:
        return OFFG.copy()
    # humming: the sign held at its cinnabar phase (sign clock from 1.0 s: u < 0.28, k = 0), a faint mains hum
    hum = 1.0 - 0.025 * (0.5 + 0.5 * math.sin(t * 2 * math.pi * 6.0))
    ts = 1.0 + (t - T0)
    f = A1.OFF + (A1.ON - A1.OFF) * hum
    f = A1.SG.apply(f, ts, on=hum)
    lit = finish(f, A1.G, A1.TEX)
    lit = lit * (ROOM + (1 - ROOM) * WIN)                               # the room darker than A1; the window full
    a = min(1.0, (k - N_BLACK + 1) / N_ADJUST)
    a = a * a * (3 - 2 * a)
    return np.maximum(BLACK + (lit - BLACK) * a, BLACK).astype(F32)

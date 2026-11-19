"""C5a song frames 1254-1310 (57 f). ATTIC v4. Lap profile: Mama blows across the page past the child's ear (hair lifts ~53.22),
the child scrunches and laughs (~53.95). Kling v4 first+last frame take at4_C5a_k4_t1 (keyframes C5a, C5a_end), started at clip
frame 5. BOOK's C5b follows at 1311."""
from shots._attic4 import *

T0, T1 = 1254 / 24, 1311 / 24
import cv2
import numpy as np


def ribbons(f, t, shot, sg):
    """A few faint thin ink wind ribbons (BOOK's brush vocabulary: pointed tail, swell, long taper to the head, dry-brush bristle gaps,
    pale to mid ink) leave Mama's lips past the child's ear and exit the RIGHT edge inside y 0.25-0.65 H over the last ~12 frames,
    moving left->right and rising slightly, so the same flow enters C5b at its left edge."""
    k = (t - T0) * 24 - 42.0                                   # frame index inside the last 15 frames, 0 = first ribbon frame
    if k < 0:
        return f
    H, W = f.shape[:2]
    out = f.copy()
    rng = np.random.RandomState(7)
    lips = np.array([0.472 * W, 0.395 * H])
    # (exit y/H, speed px-of-W per frame, length frac of W, start delay f, thickness)
    spec = [(0.30, 0.060, 0.30, 0.0, 3.2), (0.345, 0.052, 0.36, 1.0, 2.4), (0.275, 0.066, 0.24, 2.0, 2.0),
            (0.385, 0.056, 0.28, 3.0, 2.6), (0.325, 0.070, 0.20, 4.0, 1.8)]
    for yi, sp, ln, d, th in spec:
        kk = k - d
        if kk < 0:
            continue
        head = lips[0] + sp * W * kk
        n = 60
        xs = np.linspace(max(lips[0], head - ln * W), head, n)
        u = (xs - lips[0]) / max(1.0, (W - lips[0]))
        ys = lips[1] + (yi * H - lips[1]) * np.clip(u, 0, 1.3) + 5 * np.sin(u * 7 + d) * (1 - np.exp(-3 * u))
        s = np.linspace(0, 1, n)
        wid = th * W / 960.0 * np.sin(np.pi * np.clip(s, 0, 1) ** 0.6) ** 0.9 + 0.3
        fade = min(1.0, kk / 3.0)
        lay = np.zeros((H, W), np.float32)
        for b in range(5):
            off = (b - 2) * 0.55 * th * W / 960.0
            keep = rng.rand(n) > 0.07 * b / 4
            for i in range(n - 1):
                if keep[i] and 0 <= xs[i] < W:
                    cv2.line(lay, (int(xs[i]), int(ys[i] + off * wid[i] / (th + 0.1))), (int(xs[i + 1]), int(ys[i + 1] + off * wid[i] / (th + 0.1))), 1.0, 1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 0.7)
        a = np.clip(lay * 0.8 * fade, 0, 0.8)[..., None]
        ink = np.array([0.93, 0.80, 0.66], np.float32)
        out = out * (1 - a) + ink * a if out.dtype != np.uint8 else (out * (1 - a) + ink * 255 * a).astype(np.uint8)
    return out


S = AtticShot([Seg4(T0, T1, 'C5a', key='C5a', tmap=[[T0, 5 / 24], [T1, 5 / 24 + (T1 - T0)]], floor=0.62,
                    keep=[(1000, 420, 330, 300)], cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])])


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

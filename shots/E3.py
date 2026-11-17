"""E3 93.000-99.917 (166 f). Team ROOMS-88. Names and faces, I lose a few / but a spell Id remember well: little
Jade close, deadpan. Seedance 2.5 lip-sync. Sign in the window behind her.

Fix round 2 (QA item 2): the keyframe's 'Mama blur' (a huge beige shoulder + stick in the left third) is painted out
with the attic's own dark wash (row colours sampled from the room beside it, falling darker to the left edge, paper
fibre on top): little Jade sits right of centre, the left third is dark room. Mask: media/comp/rooms88/E3_blob_mask.png
(the blob's footprint over all 166 frames of the take, dilated). Clip retimed 2 frames earlier (lip-sync +102 ms).
"""
from shots._rooms88 import *

T0, T1 = 2232 / 24, 2398 / 24
_FILL = {}


def _paint_out(f, t, R):
    H, W = f.shape[:2]
    if (W, H) not in _FILL:
        m = cv2.resize(cv2.imread(str(ROOT / 'media/comp/rooms88/E3_blob_mask.png'), 0), (W, H),
                       interpolation=cv2.INTER_LINEAR).astype(F32) / 255.0
        hard = m > 0.5
        L = f.mean(-1)
        xs = np.arange(W)[None, :].repeat(H, 0)
        ok = (~hard) & (xs < 0.54 * W) & (L < 0.32)                 # the dark room beside the blob (not Jade, not text)
        ok[: int(0.09 * H)] = False
        prof = np.zeros((H, 3), F32)
        have = np.zeros(H, bool)
        for y in range(H):
            sel = ok[y]
            if sel.sum() > 8:
                prof[y] = np.median(f[y][sel], axis=0)
                have[y] = True
        yy = np.arange(H)
        for c in range(3):
            prof[:, c] = np.interp(yy, yy[have], prof[have, c])
        prof = cv2.GaussianBlur(prof[:, None, :], (0, 0), sigmaX=1, sigmaY=70 * R.s)[:, 0, :]
        hue = np.median(prof, axis=0) / max(float(np.median(prof.mean(1))), 1e-4)     # one warm room hue
        prof = prof.mean(1, keepdims=True) * hue[None, :]                               # (no blue quilt band)
        fall = (0.62 + 0.38 * np.clip(np.arange(W) / (0.45 * W), 0, 1) ** 1.5).astype(F32)   # darker to the left edge
        fill = prof[:, None, :] * fall[None, :, None]
        d = R.TEX - 1.0
        fill = fill * (1 + d * 0.9) + np.clip(d, 0, None) * 0.05
        ms = cv2.GaussianBlur(m, (0, 0), 14 * R.s)[..., None]
        _FILL[(W, H)] = (np.clip(fill, 0.03, 0.975).astype(F32), np.clip(ms * 1.15, 0, 1).astype(F32))
    fill, ms = _FILL[(W, H)]
    return f * (1 - ms) + fill * ms


R = RoomShot(shot='E3', T0=T0, T1=T1, kf='E3', window=(1538, 229, 1802, 483), sign=(1670, 356, 160, -2.0),
             keep=[(1160, 440, 260, 320, 1.0)], floor=0.24, post=_paint_out,
             lyrics=[('Names and faces, I lose a few', (560, 40, 520, 44)), ("but a spell I'd remember well", (560, 40, 520, 44))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

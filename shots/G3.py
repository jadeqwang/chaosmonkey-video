"""G3 134.375-141.250 (165 f). Team ROOMS-88. 'It isn't fair, it isn't fair / I don't want it in his hair': little
Jade puts her small hand flat over the picture (the pilgrim-with-band page, C_pilgrim_band); the SHADOW of her flat
hand (comp layer) settles over the painted gold band, sharpening as the hand comes down. Seedance 2.5 lip-sync,
take 2 (first frame G3: the hand already flat). The frame stays narrow (shared margins, 28 % -> 25 %); the column
(her face above, hand and page below) is centred in the strip. Mama kept dim (her clothes are off-model dark). Take 2 is used (forced): take 1 scored a little higher (0.29 vs 0.23,
both weak) but drew two faces on the blank pages."""
from shots._rooms88 import *

T0, T1 = 3225 / 24, 3390 / 24
BAND = (0.18, 0.50)                # the gold band on the pilgrim spread (u, v), measured on the plate
HAND = None


def pre(f, t, i, R):
    s = R.s
    n = R.src.n
    p = 1.0 if R.src.frames is None else min(1.0, i / max(1, n * 0.55))    # the hand is down by ~half the take
    p = p * p * (3 - 2 * p)
    q = R.page_q
    bx, by = spread_point(q, *BAND)
    grow = 1.35 - 0.35 * p
    S = place_mask(HAND, f.shape[1], f.shape[0], bx - 18 * s * (1 - p), by + 10 * s, 250 * s * grow, angle=-12)
    S *= cv2.GaussianBlur(R.page_hull, (0, 0), 2 * s)
    return lay_shadow(f, S, (14 - 10 * p) * s, strength=0.55 + 0.35 * p)


def _setup(R, ctx):
    global HAND
    HAND = flat_hand_mask(400)


R = RoomShot(shot='G3', kf='G3', T0=T0, T1=T1, page=dict(kind='pilgrim', roi=(600, 560, 1230, 1010), tl=(-1, -1), cthr=18),
             keep=[(960, 200, 160, 180, 1.0), (880, 700, 330, 220, 1.0), (300, 300, 300, 400, 0.15)], floor=0.22,
             margins=True, pre=pre, setup=_setup,
             cam=[(T0, 925, 560, 1.06), (T1, 925, 560, 1.10)], still_cam=[(T0, 925, 560, 1.06), (T1, 925, 560, 1.10)])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

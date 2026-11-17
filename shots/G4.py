"""G4 141.250-146.458 (125 f). Team ROOMS-88. 'Then 听话, or you'll get one to wear' (Mama, off-screen; no lip-sync):
over the spread from above Mama, little Jade on her tummy at the page edge. On the left page: the SHADOW of little
Jade's head, and the shadow of Mama's finger-and-thumb ring lowering onto its brow (enlarged so it reads as a band
settling on the head's shadow), landing on 'wear' (word onset from the timing map). Both shadows are comp layers.
Page art: the pilgrim-with-band page. The strip is at its narrowest (15 %, shared schedule) from 141.45: the
compositor frames the head-shadow in the centre column. The keyframe still (the Kling take's hands doubled after 3 s): only the shadows move."""
from shots._rooms88 import *

T0, T1 = 3390 / 24, 3515 / 24
HEAD_C = (600, 655)                # where the head's shadow sits on the left page (plate px, 1920)
HEAD_H = 290
HEAD = RING = None
T_WEAR = 143.65


def pre(f, t, i, R):
    s = R.s
    H, W = f.shape[:2]
    on = cv2.GaussianBlur(R.page_m, (0, 0), 1.5 * s)      # on the paper only: Mama's real hand stays over the shadows
    S = place_mask(HEAD, W, H, HEAD_C[0] * s, HEAD_C[1] * s, HEAD_H * s)
    f = lay_shadow(f, S * on, 5 * s, strength=0.80)
    # the ring: hangs above, lowers from ~142.0, lands on the brow on 'wear'; nearer the page it sharpens
    brow_y = HEAD_C[1] - HEAD_H * 0.27
    u = ramp(t, 142.0, T_WEAR, 'inout')
    y = (brow_y - 230) + 230 * u
    settle = 4 * math.exp(-max(0.0, t - T_WEAR) / 0.12) * math.sin(max(0.0, t - T_WEAR) * 40) if t > T_WEAR else 0
    R_ = place_mask(RING, W, H, (HEAD_C[0] - 4) * s, (y + settle) * s, (70 + 40 * (1 - u)) * s, angle=-6)
    return lay_shadow(f, R_ * on, (9 - 6 * u) * s, strength=0.65 + 0.25 * u)


def _setup(R, ctx):
    global HEAD, RING
    HEAD = head_mask(400)
    RING = ring_mask(300, 70, 16)
    try:
        global T_WEAR
        T_WEAR = ctx.timing.word("Then 听话, or you'll get one to wear", 'wear')[0]
    except Exception:
        pass


R = RoomShot(shot='G4', kf='G4', T0=T0, T1=T1, page=dict(kind='pilgrim', roi=(420, 300, 1450, 870), tl=(-1, -1), cthr=18),
             window=(1508, 274, 1715, 469), sign=(1611, 371, 120, 0.0),
             keep=[(440, 360, 140, 170, 1.0), (930, 560, 520, 300, 1.0)], floor=0.22, margins=True, pre=pre, setup=_setup,
             cam=[(T0, 680, 600, 1.05), (141.45, 625, 600, 1.18), (T1, 615, 600, 1.22)],
             still_cam=[(T0, 680, 600, 1.05), (141.45, 625, 600, 1.18), (T1, 615, 600, 1.22)])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

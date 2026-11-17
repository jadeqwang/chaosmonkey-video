"""G4 141.250-146.458 (125 f). Team ROOMS-88. 'Then 听话, or you'll get one to wear' (Mama, off-screen; no lip-sync):
over the spread from above Mama, little Jade on her tummy at the page edge. On the clean right page (the left one is crossed by Mama's real hand): the SHADOW of little
Jade's head, and the shadow of Mama's finger-and-thumb ring lowering onto its brow (enlarged so it reads as a band
settling on the head's shadow), landing on 'wear' (word onset from the timing map). Both shadows are comp layers.
Page art: the pilgrim-with-band page. The strip is at its narrowest (15 %, shared schedule) from 141.45: the
compositor frames the head-shadow in the centre column. The keyframe still (the Kling take's hands doubled after 3 s): only the shadows move."""
from shots._rooms88 import *

T0, T1 = 3390 / 24, 3515 / 24
HEAD_C = (1128, 700)                # where the head's shadow sits on the left page (plate px, 1920)
HEAD_H = 300
HEAD = RING = None
T_WEAR = 143.65


T_TIGHT = 144.111                    # the next beat after 'wear': the band tightens
RING_W = 1.12                        # the band's width against the head-shadow's width


def pre(f, t, i, R):
    """Fix round 2 (QA item 12): no halo. The ring comes in already touching the top of the head-shadow, slides down
    and LANDS around its brow on 'wear' like a band seen nearly edge-on: its front arc crosses the forehead (a darker
    band on the shadow), its back arc is hidden behind the head; on the next beat it tightens by 3.5 %. The head's
    tuft is a round bun (it read as a horn)."""
    s = R.s
    H, W = f.shape[:2]
    on = cv2.GaussianBlur(R.page_hull, (0, 0), 1.5 * s)
    S = place_mask(HEAD, W, H, HEAD_C[0] * s, HEAD_C[1] * s, HEAD_H * s)
    f = lay_shadow(f, S * on, 5 * s, strength=0.80)
    t_land, t_in = on_frame(T_WEAR), on_frame(T_WEAR) - 0.75
    if t < t_in:
        return f
    head_r = 0.26 * HEAD_H                                  # head circle (head_mask): centre 0.38 h of the mask
    head_cy = HEAD_C[1] - HEAD_H * 0.5 + 0.38 * HEAD_H
    brow_y = head_cy - 0.22 * head_r
    top_y = head_cy - 0.80 * head_r                         # touching the crown
    u = ease(min(1.0, (t - t_in) / (t_land - t_in)), 'in')  # it drops onto the brow (lands, no float)
    y = top_y + (brow_y - top_y) * u
    tight = 1.0 - 0.035 * ease(min(1.0, max(0.0, (t - on_frame(T_TIGHT)) / (2 / 24))), 'out') if t >= on_frame(T_TIGHT) else 1.0
    w = 2 * head_r * RING_W * tight * (0.94 + 0.06 * u)     # narrower at the crown, the head's width at the brow
    h = w * 0.20                                            # nearly edge-on
    m = np.zeros((H, W), F32)
    cv2.ellipse(m, (int(round(HEAD_C[0] * s * 8)), int(round(y * s * 8))), (int(w * s * 4), int(h * s * 4)), -4,
                0, 360, 1.0, max(1, int(round(11 * s))), lineType=cv2.LINE_AA, shift=3)
    yy = np.arange(H, dtype=F32)[:, None]
    front = (yy >= y * s).astype(F32)                       # the lower (near) arc crosses the forehead
    m = m * front                                           # the far arc is behind the head (never a halo above it)
    return lay_shadow(f, m * on, 2.0 * s, strength=0.85)


def bun_head(h=400):
    """head_mask with the tuft as a round bun (QA: the pointed tuft read as a horn / elf ear)."""
    w = int(h * 0.9)
    m = np.zeros((h, w), np.uint8)
    cx = w // 2
    cv2.circle(m, (cx, int(h * 0.38)), int(h * 0.26), 1, -1)
    cv2.circle(m, (int(cx + 0.22 * w), int(h * 0.17)), int(h * 0.085), 1, -1)                     # bun
    cv2.rectangle(m, (int(cx - 0.11 * w), int(h * 0.58)), (int(cx + 0.11 * w), int(h * 0.78)), 1, -1)
    cv2.ellipse(m, (cx, int(h * 0.98)), (int(w * 0.48), int(h * 0.22)), 0, 180, 360, 1, -1)
    return cv2.GaussianBlur(m.astype(F32), (0, 0), 2.0)


def _setup(R, ctx):
    global HEAD, RING
    HEAD = bun_head(400)
    RING = None
    try:
        global T_WEAR
        T_WEAR = ctx.timing.word("Then 听话, or you'll get one to wear", 'wear')[0]
    except Exception:
        pass


R = RoomShot(shot='G4', kf='G4', T0=T0, T1=T1, page=dict(kind='pilgrim', roi=(420, 300, 1450, 870), tl=(-1, -1), cthr=18),
             window=(1508, 274, 1715, 469), sign=(1611, 371, 120, 0.0),
             keep=[(440, 360, 140, 170, 1.0), (930, 560, 520, 300, 1.0)], floor=0.22, margins=True, pre=pre, setup=_setup,
             cam=[(T0, 1100, 640, 1.05), (141.45, 1128, 650, 1.18), (T1, 1128, 650, 1.22)],
             still_cam=[(T0, 1100, 640, 1.05), (141.45, 1128, 650, 1.18), (T1, 1128, 650, 1.22)])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

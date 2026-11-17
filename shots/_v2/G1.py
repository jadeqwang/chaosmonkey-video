"""G1 121.458-127.458 (144 f). Team ROOMS-88. Back to 1988: the sound narrows (121.905) and the paper margins begin to
close in (team MOUNTAIN's shared schedule, shots/_margins.py); colour drains, gold kept. 'Why does he wear a band of
gold? / Is it heavy? Is it cold?': little Jade touches her own forehead. Seedance 2.5 lip-sync, first+last frame
G1_end (hand rising) -> G1 (fingers on the brow).

Fix round 2:
- margins (QA item 9): the shared schedule starts at 121.905 but from a width of 1.04 W with a slow ease, so the sheets
  stayed outside the frame until 124.75 (f2994, 68 frames late). G1 reads the schedule through margin_g1(): the sheets
  enter the frame edges ON frame 2926 (121.917) and creep in linearly; from ~125.6 on it is exactly margin_state(t),
  so the strip at the cut into G2 is unchanged.
- framing (QA item 7): her face sits on the left third (comp reframe x1.15 -> 1.21); the frame's right edge past the
  plate is the room's dark tone, so the right margin closes toward her across dark wall.
- lip-sync: the take plays 1 frame earlier (clips.json t_clip0 121.773 -> 121.731; 2 frames overshot to -107 ms).
"""
from shots._rooms88 import *
from shots._margins import margin_state, _width, T_START

T0, T1 = 2915 / 24, 3059 / 24
F_START = frame_of(T_START)                          # 2926
W_IN, CREEP = 0.985, 0.035                           # G1's sheets enter at 1.5 % of W a side, creep 3.5 %/s


def margin_g1(t, W, H):
    if frame_of(t) < F_START:
        return margin_state(t, W, H)
    w = min(_width(t), W_IN - CREEP * (t - T_START))
    p = float(np.clip((1.04 - w) / (1.04 - 0.22), 0, 1))
    half = w * W / 2.0
    tb = (-0.03 + (0.045 + 0.03) * p) * H
    return {'rect': (W / 2.0 - half, tb, W / 2.0 + half, H - tb), 'desat': float(min(1.0, p ** 0.7 * 1.08)),
            'progress': p, 'open': False}


FACE = (975, 330)                                     # her face in the plate (1920 px)
ZK = [(T0, 1.15, 520), (T1, 1.21, 455)]               # (t, zoom, cy): the old push (540 -> 470) kept
_D = {}


def reframe(f, t, R):
    H, W = f.shape[:2]
    s = R.s
    u = min(1.0, max(0.0, (t - T0) / (T1 - T0)))
    u = 0.5 - 0.5 * math.cos(math.pi * u)
    z = ZK[0][1] * (ZK[1][1] / ZK[0][1]) ** u
    cy = (ZK[0][2] + (ZK[1][2] - ZK[0][2]) * u) * s
    cx = (FACE[0] + (960 - 640) / z) * s                 # the face lands at x = 640 (left third)
    M = np.float32([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]])
    out = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if (W, H) not in _D:
        # the room's dark tone beyond the plate's right edge, with a soft fall into it
        tone = np.median(f[:, int(0.88 * W):].reshape(-1, 3), axis=0) * 0.9
        _D[(W, H)] = tone.astype(F32)
    edge = W / 2 - z * cx + z * W                         # screen x of the plate's right edge
    xs = np.arange(W, dtype=F32)
    ramp = np.clip((xs - (edge - 260 * s)) / (280 * s), 0, 1) ** 1.6
    d = R.TEX - 1.0
    tone = _D[(W, H)][None, None] * (1 + d * 0.9)
    out = out * (1 - ramp[None, :, None]) + tone * ramp[None, :, None]
    return out.astype(F32)


R = RoomShot(shot='G1', kf='G1', T0=T0, T1=T1, keep=[(960, 330, 280, 330, 1.0), (760, 200, 260, 160, 0.8)], floor=0.24,
             margins=True, margin_state=margin_g1, cam=[], post=reframe,
             still_cam=[(T0, 960, 540, 1.0), (T1, 960, 470, 1.08)],
             lyrics=[('Why does he wear a band of gold?', (660, 64, 600, 40)), ('Is it heavy? Is it cold?', (660, 64, 600, 40))])


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

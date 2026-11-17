"""D3 64.417-67.917 (84 f). Team ROOMS-88. No cradle, no lullaby, no song.
D3a (64.417-65.333, frames 1546-1567): the right page low in frame; two thin gold beams leave the top of the sheet and
shoot up out of frame (the birth is the only self-lit moment): the painted beams are inpainted out of the keyframe
and redrawn as gold strokes that fly up in 0.2 s, then hold, shimmering. Page art: the birth page (stone cracked).
D3b (65.333-67.917, frames 1568-1629): Mama and little Jade side by side on the mats singing in octaves, the book open
between them (birth page). Seedance 2.5 lip-sync (both voices); faces small (wide), kept wide per the lead."""
from shots._rooms88 import *

T0, T1 = 1546 / 24, 1630 / 24
T_B = 1568 / 24
BEAMS = [((942, 690), (898, -40)), ((982, 690), (1024, -40))]
GOLD_LIT = np.array([1.0, 0.86, 0.46], F32)


def _setup_a(R, ctx):
    """Inpaint the painted beams out of the keyframe (they are redrawn as strokes)."""
    global BEAM_A
    s = ctx.s
    k = R.KF
    r, g, b = k[..., 0], k[..., 1], k[..., 2]
    m = ((r > 0.6) & (g > 0.45) & (r - b > 0.18)).astype(np.uint8)
    xx = np.arange(k.shape[1])[None, :] / s
    yy = np.arange(k.shape[0])[:, None] / s
    m &= ((xx > 860) & (xx < 1060) & (yy < 730)).astype(np.uint8)
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
    u8 = (np.clip(k, 0, 1) * 255).astype(np.uint8)
    clean = cv2.inpaint(u8, m * 255, 6, cv2.INPAINT_TELEA).astype(F32) / 255
    R.KF = clean
    R.src.still = clean
    # the beams: thin anti-aliased lines, a hot core and a little gold air around them
    A = np.zeros(k.shape[:2], F32)
    for (x0, y0), (x1, y1) in BEAMS:
        cv2.line(A, (int(x0 * s * 16), int(y0 * s * 16)), (int(x1 * s * 16), int(y1 * s * 16)), 1.0,
                 max(1, int(round(2.2 * s))), cv2.LINE_AA, shift=4)
    BEAM_A = A


def beams(f, t, R):
    s = R.s
    u = (t - T0) / 0.2                                            # fly up in 0.2 s from the top of the page
    if u <= 0:
        return f
    yy = np.arange(f.shape[0], dtype=F32)[:, None] / s
    front = 690 - (690 + 40) * min(1.0, u)
    reach = np.clip((yy - front) / 30.0, 0, 1)
    shimmer = 0.9 + 0.1 * math.sin(t * 31.0)
    core = cv2.GaussianBlur(BEAM_A, (0, 0), 0.6 * s + 0.3) * reach * shimmer
    air = cv2.GaussianBlur(BEAM_A, (0, 0), 7 * s) * reach * 0.5
    f = f + (np.maximum(f, GOLD_LIT * 0.8) - f) * np.clip(air, 0, 1)[..., None]
    f = f + (GOLD_LIT * 1.05 - f) * np.clip(core * 1.6, 0, 1)[..., None]
    return np.clip(f, 0, 0.985)


RA = RoomShot(shot='D3a', kf='D3a', T0=T0, T1=T_B, page=dict(kind='birth_r', roi=(0, 480, 1720, 1080), tl=(-1, -1), cthr=18,
              strength=0.75), window=(1440, 103, 1687, 363), sign=(1563, 233, 150, 0.0), setup=_setup_a,
              keep=[(900, 860, 700, 260, 1.0)], floor=0.30, still_cam=[(T0, 960, 540, 1.0), (T_B, 960, 520, 1.02)])
RB = RoomShot(shot='D3b', kf='D3b', T0=T_B, T1=T1, page=dict(kind='birth', roi=(780, 900, 1140, 1080), tl=(-1, -1), cthr=22),
              window=(1389, 285, 1679, 509), sign=(1534, 397, 140, 0.0),
              keep=[(740, 380, 130, 160, 1.0), (1180, 460, 110, 140, 1.0), (960, 980, 220, 100, 0.9)], floor=0.30,
              lyrics=[('No cradle, no lullaby, no song', (560, 40, 800, 44))])


def setup(ctx):
    RA.setup(ctx)
    RB.setup(ctx)


def render(t, ctx):
    if t < T_B - 1e-6:
        return beams(RA.render(t), t, RA)
    return RB.render(t)

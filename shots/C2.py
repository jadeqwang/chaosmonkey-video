"""C2 45.167-46.167 (24 f). Team ROOMS-88. THUMBNAIL. 'Monkey!': little Jade's hands (window side, upper left)
throw a monkey-head hand shadow across the left page in the red neon, popping up ON 'Monkey!' (45.275). The shadow is
big; the painted 花果山 small under it (B3's spread, mapped onto the page). Kling v4 clip (hands settle) or the
keyframe. The shadow is a comp layer from design/characters/monkey/handshadow_silhouette.jpg.
"""
from shots._rooms88 import *

T0, T1 = 1084 / 24, 1108 / 24
T_POP = 45.275
SIL = None


def red_light(f, R):
    """The page catches the neon from the window side (left): cinnabar falling off toward the right."""
    s = R.s
    xx = np.arange(f.shape[1], dtype=F32)[None, :] / s
    yy = np.arange(f.shape[0], dtype=F32)[:, None] / s
    d = np.clip(1.0 - np.hypot(xx - 120, yy - 160) / 1500, 0, 1) ** 0.8
    tint = 1 - (1 - np.array([1.0, 0.60, 0.52], F32)) * (0.55 + 0.45 * d)[..., None]
    m = cv2.dilate(R.page_m, np.ones((5, 5), np.uint8))[..., None]
    return f * (1 - m + m * tint)


def pre(f, t, i, R):
    f = red_light(f, R)
    if t < T_POP - 1e-6:
        return f
    s = R.s
    u = t - T_POP
    # it snaps up big and settles a touch (a child's hands finding the shape), then trembles very slightly
    grow = 1.0 + 0.06 * math.exp(-u / 0.07)
    wob = 0.6 * math.sin(u * 7.3) + 0.35 * math.sin(u * 13.1 + 1.0)
    S = place_mask(SIL, f.shape[1], f.shape[0], 660 * s, 470 * s, 600 * s * grow, angle=-8 + wob)
    # fade the neck toward the hands (the arm's shadow leaves the page)
    yy = np.arange(f.shape[0], dtype=F32)[:, None] / s
    S *= np.clip((790 - yy) / 120, 0, 1)
    S *= cv2.GaussianBlur(R.page_hull, (0, 0), 2 * s)          # it lands on the page; the room beyond is far and dark
    return lay_shadow(f, S, 5.0 * s, strength=0.92)


def _setup(R, ctx):
    global SIL
    SIL = silhouette_mask('design/characters/monkey/handshadow_silhouette.jpg')


R = RoomShot(shot='C2', kf='C2', T0=T0, T1=T1,
             page=dict(kind='hgs', roi=(250, 250, 1330, 900), tl=(-1, -1)),
             window=None, sign=None, keep=[(780, 540, 520, 330, 1.0), (150, 200, 220, 160, 0.6)], floor=0.28,
             still_cam=[(T0, 960, 540, 1.0), (T1, 900, 500, 1.04)], pre=pre, setup=_setup, twos=True)


def setup(ctx):
    R.setup(ctx)


def render(t, ctx):
    return R.render(t)

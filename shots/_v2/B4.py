"""B4 'Sunlight by day and moonlight by night' (29.292-36.417, 171 frames). Team MOUNTAIN.

Close on the carved cliff of 花果山, travelling right to left along B_cliff_run (time passing; the carving gets
younger to the left). 千字文 lines 1-160 in 崇羲篆體, cut as V-section 摩崖石刻 into the flat planes of the painted
rock, cinnabar in the cuts. A low warm sun rakes across from the right: a band of light travels right to left
faster than the camera, the characters flare as it reaches them and die behind it. On 'moonlight' (word onset
33.04) the page darkens to night and a cool-silver moon makes the same pass. Tiny carvers on ladders, different
ones on each pass.
"""
import numpy as np

from shots._mountain import *

T0, T1 = 703 / 24, 874 / 24
CY, ZOOM = 640, 1.0
X_FROM, X_TO = 7650, 3950
SIZE = 130
BLOCKS = [(8020, 150, 330, 980), (7100, 90, 400, 1060), (6240, 190, 320, 860), (5780, 300, 200, 700),
          (4650, 110, 420, 1040), (3890, 170, 330, 960), (3260, 240, 330, 840)]
SUN = dict(az=335.0, el=12.0)
MOON = dict(az=322.0, el=13.0)


def cam_x(t):
    return X_FROM + (X_TO - X_FROM) * min(max((t - T0) / (T1 - T0), 0.0), 1.0)


def setup(ctx):
    global C, XS, T_MOON, CARVERS
    raw = load_image(B + 'B_cliff_run.png')
    H, W = raw.shape[:2]
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    rock = onto_paper(raw, paper)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # age: the right end (oldest) is the most weathered; younger to the left
    wn = fbm(H, W, 220.0, 7, 'b4_w', octaves=3)
    weather = np.clip((0.08 + 0.42 * xx / W) * (0.55 + 0.9 * wn), 0, 0.85).astype(np.float32)
    C = Cliff(rock, qianziwen(160), SEAL_FONT, size=SIZE, region=BLOCKS, seed=4, weather=weather,
              presence='plane', chips=0.3, streaks=0.4, jitter=0.04, weight=0.02, paint=0.8, depth=1.3, grime=0.35)
    C.prepare(fill=0.65)
    XS = np.arange(W, dtype=np.float32)[None, :]
    T_MOON = ctx.timing.word('Sunlight by day and moonlight by night', 'moonlight')[0]
    # carvers: the sun pass gets the fine wash figures on ladders, the moon pass the abbreviated dab figures
    def car(i, h, flip=False):
        name = [f for f in sorted((ROOT / B / 'carvers').glob(f'B_carver_{i:02d}_*.png'))][0]
        return element(str(name.relative_to(ROOT)), h, flip=flip)
    # (layer, canvas x of its right edge, canvas y of its foot, pass)
    CARVERS = [
        (car(9, 270), 8040, 1185, 'sun'),              # on a ladder, carving the foot of the second column
        (car(13, 250), 7150, 1190, 'sun'),
        (car(14, 125), 6255, 1078, 'sun'),             # kneeling on a plank under a finished column
        (car(4, 200), 6150, 1010, 'moon'),             # the dab figures face left: right of their column
        (car(7, 190), 4720, 1185, 'moon'),
        (car(5, 175), 3600, 1060, 'moon'),
    ]


def light_at(t):
    """(az, el), ambient row, pool row, tint, ambient tint, warmth for time t."""
    cx = cam_x(t)
    night = ramp(t, T_MOON - 0.45, T_MOON + 0.1, 'sine')
    if t < T_MOON - 0.2:
        u = 1.3 - 1.65 * ramp(t, T0, T_MOON - 0.35, 'linear')     # the sun front: frame right edge -> past the left
        L = SUN
    else:
        u = 1.3 - 1.65 * ramp(t, T_MOON - 0.05, T1 - 0.15, 'linear')
        L = MOON
    front = cx + (u - 0.5) * 1920
    bnd = band(XS, front, lead=420, trail=520, flare=1.0)
    if L is SUN:
        bnd = bnd * (1.0 - night)
    else:
        bnd = bnd * night
    # outside the band the page is as painted; inside it the cuts go deep with shadow and the walls flare, while
    # the flat rock brightens only a few percent (no glow): the light is visible in the carving
    amb_out = 0.95 - 0.07 * night                                 # fix2: was 0.13 (cement-grey night)
    amb = amb_out - (0.42 - 0.10 * night) * bnd
    flat = amb_out + (0.05 - 0.02 * night) * bnd                 # target brightness of flat rock
    pool = np.clip((flat - amb) / np.maximum(1.0 - amb, 1e-3), 0, None)
    tint = np.array([1.0, 1.0, 1.0]) * (1 - night) + np.array([0.975, 0.955, 0.915]) * night        # fix2: warm moon (was cool 0.93/0.955/0.985)
    atint = np.array([1.0, 1.0, 1.0]) * (1 - night) + np.array([0.97, 0.955, 0.925]) * night
    warmth = 0.85 * (1 - night) + 0.35 * night
    return (L['az'], L['el'], 1.0), amb.astype(np.float32), pool.astype(np.float32), tint, atint, warmth, night


def render(t, ctx):
    light, amb, pool, tint, atint, warmth, night = light_at(t)
    cx = cam_x(t)
    f = view(None, cx, CY, ZOOM, ctx.W, ctx.H,
             render=lambda box: C.render(light, fill=0.65, ambient=amb, pool=pool, warmth=warmth, tint=tint,
                                         ambient_tint=atint, box=box))
    z = ZOOM * ctx.W / 1920.0
    for T, xr, yf, which in CARVERS:
        if (which == 'sun') == (night < 0.5):
            x = (xr - T.shape[1] - cx) * z + ctx.W / 2
            y = (yf - T.shape[0] - CY) * z + ctx.H / 2
            if -T.shape[1] * z < x < ctx.W and -T.shape[0] * z < y < ctx.H:
                L = T if z == 1 else cv2.resize(T, (max(1, int(T.shape[1] * z)), max(1, int(T.shape[0] * z))),
                                                interpolation=cv2.INTER_AREA)
                # the figures stand in the same light as the rock behind them
                lay_at(f, 1 - (1 - L) * (0.85 + 0.15 * (1 - night)), x, y)
    return f

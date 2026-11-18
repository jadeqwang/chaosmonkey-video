"""L3 (second part) song frames 5686-5719 (34 f), after L2b (5660-5685). ATTIC v3, round 2. Continuous with L2b: the
same night, the camera pulled back and up (keyframe media/kf/v3/L2w.jpg, the L2b painting extended outward): Mama still
kneeling beside her, a hand on the quilt, breathing; the scattered books; the blade sign's wedge in the window. At
237.840 (f5709) the neon goes off hard: the red light leaves the room (computed from the lit frame: red pool removed,
the glass a cold grey for two frames), then the room sinks to night black. Kling v4 on L2w (pick key L2w)."""
from shots._attic3 import *
from shots._attic3 import finish, paper_tex, camera_move

CAM = [(5686 / 24, 1130, 700, 1.6), (5720 / 24, 1120, 690, 1.5)]      # the wide is very wide: sit closer, easing back

T0, T1 = 5686 / 24, 5720 / 24
WINDOW = (1455, 425, 1600, 580)
T_OFF = 237.840
SG = Seg(T0, T1, 'L2w', key='L2w', window=WINDOW, wedge=(0.50, 0.78), floor=0.62,
         keep=[(1270, 620, 320, 240)], tmap=[[T0, 0.4], [T1, 0.4 + 34 / 24]])


def setup(ctx):
    global TEX, F_OFF
    SG.setup(ctx)
    TEX = paper_tex(ctx.W, ctx.H)
    F_OFF = math.ceil(T_OFF * 24 - 1e-6)


def unlit(f, s):
    """The same frame with the neon gone: the red excess is taken out, what is left is a dim cold-warm night."""
    l = (f[..., 0] * 0.25 + f[..., 1] * 0.6 + f[..., 2] * 0.15)[..., None]
    red = np.clip(f[..., :1] - np.maximum(f[..., 1:2], f[..., 2:3]), 0, 1)
    g = np.minimum(f, l * np.array([0.95, 1.0, 1.08], F32)) * (1 - 0.75 * np.clip(red * 3.0, 0, 1))
    return (g * 0.42).astype(F32)


def render(t, ctx):
    k = round(t * 24)
    f, i = SG.frame(t)
    if k < F_OFF:
        hum = 1.0 - 0.04 * (0.5 + 0.5 * math.sin(2 * math.pi * 50 / 6.0 * t))        # a faint mains flutter
        f = SG.blade.apply(f, t, on=hum)
        return camera_move(finish(f, SG.G, TEX), t, CAM)
    d = k - F_OFF
    x0, y0, x1, y1 = [int(v * ctx.s) for v in WINDOW]
    g = unlit(f, ctx.s)
    if d < 2:                                                    # the bare glass, cold grey, for two frames
        g[y0:y1, x0:x1] = np.maximum(g[y0:y1, x0:x1], f[y0:y1, x0:x1].mean(axis=2, keepdims=True) * np.array([0.42, 0.46, 0.52], F32))
    g = finish(g, SG.G, TEX)
    return camera_move(g * (1.0 if d < 2 else max(0.25, 1.0 - 0.12 * (d - 1))), t, CAM)

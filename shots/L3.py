"""L3 song frames 5686-5719 (34 f), after L2b. ATTIC v4. The A1 wide camera: both asleep (Mama on her mat under the beige quilt, little
Jade beside her), the nine fallen books on the boards at the lower right. Neon off on frame 5709 (237.840): hard cut to the painted
L3_off (window cold blue-grey, no red anywhere), two frames of bare cold glass, then the room sinks. CUT does the 3 s ring-out
over black. Kling take of breathing sleep (pick key L3) until the neon goes off; a still is acceptable."""
from shots._attic4 import *
from shots._attic3 import finish, paper_tex

T0, T1 = 5686 / 24, 5720 / 24
WINDOW = (1313, 213, 1646, 523)
T_OFF = 237.840
SG = Seg4(T0, T1, 'L3', key='L3', tmap=[[T0, 0.0], [T1, T1 - T0]], window=WINDOW, wedge=(0.57, 0.75), floor=0.62,
          keep=[(900, 470, 520, 300)])


def setup(ctx):
    global TEX, F_OFF, OFFKF, GOFF
    SG.setup(ctx)
    TEX = paper_tex(ctx.W, ctx.H)
    F_OFF = math.ceil(T_OFF * 24 - 1e-6)
    OFFKF = kf4('L3_off', ctx.W, ctx.H)
    GOFF = grade_field(OFFKF, floor=0.62)


def render(t, ctx):
    k = round(t * 24)
    if k < F_OFF:
        f, i = SG.frame(t)
        hum = 1.0 - 0.04 * (0.5 + 0.5 * math.sin(2 * math.pi * 50 / 6.0 * t))        # a faint mains flutter
        f = SG.blade.apply(f, t, on=hum)
        return finish(f, SG.G, TEX)
    d = k - F_OFF
    g = OFFKF.copy()
    x0, y0, x1, y1 = [int(v * ctx.s) for v in WINDOW]
    if d < 2:                                                    # the bare glass, cold grey, for two frames
        g[y0:y1, x0:x1] = np.maximum(g[y0:y1, x0:x1], g[y0:y1, x0:x1].mean(axis=2, keepdims=True) * np.array([1.6, 1.8, 2.2], F32))
    g = finish(g, GOFF, TEX)
    return g * (1.0 if d < 2 else max(0.3, 1.0 - 0.07 * (d - 1)))

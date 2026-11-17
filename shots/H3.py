"""H3 (162.625-165.958): 'Tool or threat, trick or kid'. Four painted faces stamped in a row on the album's old
paper, one on each noun's measured onset; small in the lower-left corner under them, a child seen from behind in
pale ink (little Jade's back view, desaturated, so it could be either child); her own face is never seen.

Measured word onsets (analysis/timing.json): Tool 162.630, threat 163.480, trick 164.360, kid 165.240.
Faces: tool = F06 (yellow 尖三块瓦), threat = F13 (crooked 歪脸), trick = F21 (water-white 水白), kid = F14 (clown).
"""
from tools.ink import *
from tools.ink.text import Inscription
from shots.faces_lib import *

T0, T1 = 162.625, 165.95833
ROW = [('F06', 'Tool'), ('F13', 'threat'), ('F21', 'trick'), ('F14', 'kid')]
GARAMOND = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'


def setup(ctx):
    global P, AL, CHILD, CPOS, INS, LAND, CAM
    s = ctx.s
    tm = ctx.timing
    words = dict((w, a) for w, a, b in tm.words('Tool or threat, trick or kid'))
    LAND = [words[w] for _, w in ROW]
    P = Paper(ctx.W, ctx.H, 'aged', seed=88)
    face_h = 0.29 * 1080
    xs = [430, 790, 1150, 1510]
    plan = []
    for i, (fid, w) in enumerate(ROW):
        r = rng(3, i)
        plan.append(dict(id=fid, cell=i, t=LAND[i], k=0.8, scale=face_h / 1120.0,
                         pos=(xs[i] + r.uniform(-12, 12), 360 + (18 if i % 2 else -10) + r.uniform(-6, 6)),
                         rot=float(r.uniform(-2.0, 2.0))))
    AL = Album(ctx, plan)
    CAM = (960, 540, 1.0)                        # identity: plan positions are 1080p frame px
    CHILD = child_figure(ctx, 0.235 * ctx.H)
    CPOS = (int(250 * s), int(ctx.H - CHILD.shape[0] - 70 * s))
    INS = None
    if getattr(ctx, 'opts', {}).get('lyrics', True):
        INS = Inscription('Tool or threat, trick or kid', GARAMOND, (int(905 * s), int(880 * s), int(480 * s), int(60 * s)),
                          size=ctx.size, vertical=False, max_px=34 * s, words=tm.words('Tool or threat, trick or kid'),
                          mode='word', paper=P, seed=4, align='end')


def render(t, ctx):
    f = P.frame(t)
    lay_ink(f, CHILD, *CPOS)
    lum = luma(f)
    tex = (np.clip(lum / (blur(lum, 5.0 * ctx.s) + 1e-4), 0.85, 1.12) ** 0.5)[..., None]
    AL.draw_faces(f, CAM, t, tex=tex)
    if INS is not None:
        INS.draw(f, t)
    dx, dy = shake_offset(t, LAND, amp=5 * ctx.s, dur=0.16)
    return shaken(f, dx, dy) if (dx or dy) else f

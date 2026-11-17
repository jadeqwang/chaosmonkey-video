"""H3 (162.625-165.958): 'Tool or threat, trick or kid'. We stay ON the album H2 completed. On each noun's
measured onset a hard cut to a close framing of ONE face in the finished grid (off-centre, alternating sides), and a
small plain 白文 cinnabar seal is pressed beside it: the face is stamped as a category. The fourth cut (kid) also
holds the bare cell; the child from behind (pale ink, unpainted) stands at its foot. The last ~10 frames widen to
H4's opening framing, so the cut into H4's pull-out is continuous.

Measured word onsets (analysis/timing.json): Tool 162.630, threat 163.480, trick 164.360, kid 165.240.
Faces (existing cells): tool = F04 blue (cell 10), threat = F02 black (cell 3), trick = F21 water-white (cell 13),
kid = F14 clown (cell 14, beside the bare cell 15). Widen 165.54 -> 165.958 (ease out) to H4.CAM0.
"""
from tools.ink import *
from tools.ink.text import Inscription
from shots.faces_lib import *
from shots.H2 import album_plan
from shots import H4 as _H4

T0, T1 = 162.625, 165.95833
GARAMOND = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
LINE = 'Tool or threat, trick or kid'
NOUNS = ['Tool', 'threat', 'trick', 'kid']
# cell, face height share of frame, anchor of the face in frame
SHOTS = [(10, 0.66, (0.36, 0.50)), (3, 0.74, (0.64, 0.52)), (13, 0.62, (0.35, 0.47)), (14, 0.60, (0.31, 0.50))]
WIDEN = 165.54


def setup(ctx):
    global AL, SEAL, HITS, CAMS, CHILD, INS
    tm = ctx.timing
    words = dict((w, a) for w, a, b in tm.words(LINE))
    HITS = [words[w] for w in NOUNS]
    AL = Album(ctx, album_plan(tm))
    CAMS = [cams_frame_face(c, fh, anc) for c, fh, anc in SHOTS]
    SEAL = category_seal()
    CHILD = child_figure(ctx, 640, strength=1.7)
    INS = None
    if getattr(ctx, 'opts', {}).get('lyrics', True):
        s = ctx.s
        INS = Inscription(LINE, GARAMOND, (int(905 * s), int(985 * s), int(480 * s), int(60 * s)),
                          size=ctx.size, vertical=False, max_px=34 * s, words=tm.words(LINE), mode='word', seed=4,
                          align='end')


def cam_at(t):
    if t >= WIDEN:
        u = ease(clamp((t - WIDEN) / (T1 - WIDEN)), 'out')
        a, b = CAMS[3], _H4.CAM0
        z = math.exp(lerp(math.log(a[2]), math.log(b[2]), u))
        return (lerp(a[0], b[0], u), lerp(a[1], b[1], u), z)
    k = max(0, sum(1 for h in HITS[1:] if t >= on_frame(h) - 1e-9))
    return CAMS[k]


def render(t, ctx):
    cam = cam_at(t)
    f, bg = AL.render(t, cam)
    k = sum(1 for h in HITS if t >= on_frame(h) - 1e-9)
    if k >= 4:                                     # she is there from the kid cut on (the bare cell is in frame)
        _H4.lay_child(f, cam, ctx, AL, CHILD)
    draw_category_seals(f, cam, t, ctx, AL, SEAL, HITS)
    if INS is not None:
        INS.draw(f, t)
    dx, dy = shake_offset(t, HITS, amp=4 * ctx.s, dur=0.14)
    return shaken(f, dx, dy) if (dx or dy) else f

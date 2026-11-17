"""H4 (165.958-169.250): 'the categories arrived before I did'. Pull out (scale revealed) from the one bare cell
- the child standing small in it, back to us, unpainted - to the whole weathered album leaf on its board: soft
corners, foxed, older than she is. The lyric is inscribed in the opposite (upper-left) margin of the leaf, word by
word on the measured onsets. Nothing else moves.

Measured (analysis/timing.json): words the 165.94, categories 166.12, arrived 167.12, before 167.68, I 168.64,
did 168.76. Pull-out 165.958 -> 168.30 (settles on the bar line 168.785 region), hold to the cut.
"""
from tools.ink import *
from tools.ink.text import Inscription
from shots.faces_lib import *
from shots.H2 import album_plan

T0, T1 = 165.95833, 169.25
GARAMOND = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
LINE = 'the categories arrived before I did'
CH_H = 250.0                                   # the child's height in leaf px (cell is 475 tall)
X0, Y0, X1, Y1 = BARE_CELL = CELLS[BARE][0], CELLS[BARE][1], CELLS[BARE][0] + CELLS[BARE][2], CELLS[BARE][1] + CELLS[BARE][3]
CHILD_FOOT = ((X0 + X1) / 2 + 30, Y1 - 22)    # she stands on the cell's lower rule, a little right of centre
INS_LEAF = (780, 80)                           # top-left of the inscription block, leaf px (upper-left margin)
INS_SIZE = (1350, 120)
# start: the bare cell with the kid face beside it (H3 ends exactly here); end: the whole leaf on its board
CAM0 = ((X0 + X1) / 2 - 170, (Y0 + Y1) / 2 - 10, 1.55)
CAM1 = (LW / 2, LH / 2 + 20, 0.405)
HITS_H3 = [162.63, 163.48, 164.36, 165.24]      # the category seals pressed in H3 (word onsets)


def setup(ctx):
    global AL, CHILD, INS, TP0, TP1, SEAL
    AL = Album(ctx, album_plan(ctx.timing))
    SEAL = category_seal()
    CHILD = child_figure(ctx, 640, strength=1.7)   # hi-res; warped per frame; darker, she ends small
    INS = None
    from tools.ink.opts import lyrics_on
    if lyrics_on(ctx):
        INS = Inscription(LINE, GARAMOND, (20, 10, INS_SIZE[0] - 40, INS_SIZE[1] - 20), size=INS_SIZE, vertical=False,
                          max_px=68, words=ctx.timing.words(LINE), mode='stroke', seed=9, density=0.85)
    TP0, TP1 = T0, 168.30


def cam_at(t):
    u = ease(clamp((t - TP0) / (TP1 - TP0)), 'inout')
    z = math.exp(lerp(math.log(CAM0[2]), math.log(CAM1[2]), u))
    # position follows the zoom (the bare cell keeps a straight path on screen)
    v = (1 / z - 1 / CAM0[2]) / (1 / CAM1[2] - 1 / CAM0[2])
    return (lerp(CAM0[0], CAM1[0], v), lerp(CAM0[1], CAM1[1], v), z)


def _warp_ink(f, T, cam, leaf_xy, src_scale, ctx, album=None):
    """lay a transmittance layer whose top-left sits at leaf_xy (leaf px), src px = src_scale leaf px."""
    cx, cy, z = cam
    k = src_scale * z * ctx.s
    fx, fy = (album or AL).to_frame(cam, *leaf_xy)
    src = T
    while k < 0.6 and min(src.shape[:2]) > 8:
        src = cv2.resize(src, (src.shape[1] // 2, src.shape[0] // 2), interpolation=cv2.INTER_AREA)
        k *= 2
    M = np.float32([[k, 0, fx], [0, k, fy]])
    w = cv2.warpAffine(src, M, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                       borderValue=(1, 1, 1))
    f *= w


def lay_child(f, cam, ctx, album, child):
    sc = CH_H / child.shape[0]
    _warp_ink(f, child, cam, (CHILD_FOOT[0] - child.shape[1] * sc / 2, CHILD_FOOT[1] - CH_H), sc, ctx, album)


def render(t, ctx):
    cam = cam_at(t)
    f, bg = AL.render(t, cam)
    lay_child(f, cam, ctx, AL, CHILD)
    draw_category_seals(f, cam, t, ctx, AL, SEAL, HITS_H3)
    if INS is not None:
        d = INS.density(t)
        x0, y0, bw, bh = INS.box
        T = np.ones((INS_SIZE[1], INS_SIZE[0], 3), F32)
        T[y0:y0 + bh, x0:x0 + bw] = ink_T(d)
        _warp_ink(f, T, cam, INS_LEAF, 1.0, ctx, AL)
    return f

"""L1 (228.750-233.208) Percussion returns. Pull back out of the ledger, out through the painting to the page, to the bed.
ROOMS-26.

Frame 0 IS team HEAVEN's K5 last frame (K5's own setup is run read-only to build it): the ledger's last page (p8,
final column bare) in the flashlight pool. Over the first 4 frames K5's dark surround hands over to our composite; then a
slow compositor pull-back: the page (p8, lit in page space with the same pool) flies from K5's frontal framing into the
book lying open on the blanket in the room (Kling clip of L1.jpg: Jade and the sleeping daughter breathe), the room
scaled with it so the page always sits on the book. Near the end the page is multiplied onto the room's lit paper, which
also covers the scribble "text" the keyframe painted on that page. Bedroom grade: the only light is the pool on the book.
"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rooms26 import *
from _bed_grade import bed_grade, bed_field, dehalo, find_lens
from tools.ink.light import flashlight_field

T0, T1 = 228.75, 233.20833333333334
T_MOVE0, T_MOVE1 = 228.80, 232.70
# p8 page corners (TL TR BR BL) in K5's frame, 1080p px (K5: spread px -> frame = (p - (-1867.2, 314)) * 0.38)
# fix round 2: K5 was reframed by the book fixer (LOG_fix2_book "K5 re-frame"); read its framing from shots/K5.py
# (frame = (page - PAGE_RECT[:2]) * SC; p8 is 2200x3300 page px) so L1's frame 0 follows K5 if it moves again.
def _k5_consts():
    import ast
    src = open(os.path.join(ROOT, 'shots/K5.py')).read()
    v = {}
    for name in ('SC', 'BARE_X', 'FX', 'Y0', 'POOL'):
        for line in src.splitlines():
            if line.startswith(name + ' ='):
                v[name] = ast.literal_eval(line.split('=', 1)[1].split('#')[0].strip())
    return v


_K5 = _k5_consts()
_K5S = float(_K5['SC'])
_K5O = np.float32([_K5['BARE_X'] - _K5['FX'] / _K5S, _K5['Y0']])
QK5 = (np.float32([(0, 0), (2200, 0), (2200, 3300), (0, 3300)]) - _K5O) * _K5S
K5_TORCH = ((_K5['POOL'][0] / _K5S + _K5O[0]), (_K5['POOL'][1] / _K5S + _K5O[1]), _K5['POOL'][2] / _K5S)   # page px
LENS_BOX = (1235, 455, 1360, 575)            # the torch lens on the bed, room px (1080p)
# the same page lying in the room (measured on the L1 clip): far edge on top
QROOM = np.float32([(1200, 620), (1303, 643), (1250, 686), (1175, 651)])
POOL_ROOM = (1255, 640)


def load_k5(ctx):
    spec = importlib.util.spec_from_file_location('k5_for_l1', os.path.join(ROOT, 'shots/K5.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup(ctx)
    return m.F.copy()


def page_plate():
    sp = load_image(os.path.join(ROOT, 'work/heaven/ledger/spread_7_8.png'))
    pg = sp[:, :2200]
    h, w = pg.shape[:2]
    k = 0.5
    pg = cv2.resize(pg, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
    # K5's torch in page px (read from shots/K5.py), stretch 1.30, tilt 88
    I = flashlight_field(pg.shape[1], pg.shape[0], (K5_TORCH[0] * k, K5_TORCH[1] * k), K5_TORCH[2] * k, 88, 1.30, 11)
    L = I[..., None] * 1.36 * np.float32([1.0, 0.985, 0.95]) + 0.06 * np.float32([0.55, 0.68, 1.0])
    T = pg / np.median(pg.reshape(-1, 3), axis=0)
    return np.clip(pg * L, 0.012, 0.985).astype(F32), np.clip(T, 0, 1).astype(F32)


def setup(ctx):
    global KF, B, P, PG, PT, FLD, WORDS
    WORDS = words_of(ctx, 'it wasn', 224.2)
    KF = load_k5(ctx)
    B, _ = base_for('L1', 'media/kf/L1.jpg', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=33)
    PG, PT = ctx.cache('L1_page_fix2b', page_plate, deps=['work/heaven/ledger/spread_7_8.png'])
    FLD = bed_field(ctx, POOL_ROOM, 120, faces=[(1010, 520, 70, 80, 0.45), (1150, 590, 60, 60, 0.45)], amb=0.42,
                    key='L1')


def quad_at(u):
    """Page quad at pull-back progress u: centre and scale interpolated in log space, shape linearly."""
    def cs(q):
        c = q.mean(0)
        d1, d2 = q[2] - q[0], q[3] - q[1]
        s = np.sqrt(abs(d1[0] * d2[1] - d1[1] * d2[0]) / 2)
        return c, s
    c0, s0 = cs(QK5); c1, s1 = cs(QROOM)
    s = np.exp(np.log(s0) * (1 - u) + np.log(s1) * u)
    # centre follows the scale (a straight push line, like Camera): progress in log-scale space
    v = (np.log(s0) - np.log(s)) / (np.log(s0) - np.log(s1))
    c = c0 * (1 - v) + c1 * v
    n0, n1 = (QK5 - c0) / s0, (QROOM - c1) / s1
    sh = n0 * (1 - u) + n1 * u
    return c + sh * s, s / s1, c, c1


def render(t, ctx):
    u = ease(np.clip((t - T_MOVE0) / (T_MOVE1 - T_MOVE0), 0, 1), 'inout')
    q, z, c, c1 = quad_at(u)
    # room: warped by the same homography that carries its page onto the current page quad, so the page always lies
    # on the book (the whole painting tilts out from under the camera); the surround stays in the dark until mid-move
    room = B.at(t)
    room = bed_grade(room, ctx, POOL_ROOM, 120, field=FLD)
    room = dehalo(room, ctx, find_lens(room, ctx, LENS_BOX), R=70, lens_r=16)     # fix2: no glow on the torch head
    Hr = cv2.getPerspectiveTransform(QROOM * ctx.s, np.float32(q) * ctx.s)
    room = cv2.warpPerspective(room, Hr, (ctx.W, ctx.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    room = room * float(0.16 + 0.84 * smoothstep(0.30, 0.80, u))
    pw, pm = warp_layer_quad(PG, q, ctx)
    tw, _ = warp_layer_quad(PT, q, ctx)
    pm = soften(pm, ctx, max(0.6, 2.0 * (1 - u)))[..., None]
    w = float(smoothstep(0.50, 0.88, u))                     # opaque lit page -> page ink multiplied on the room's paper
    page = pw * (1 - w) + room * tw * w
    f = room * (1 - pm) + page * pm
    f = paper_fibre(np.clip(f, 0.012, 0.985), P, 0.5 * w + 0.15)
    k = 1.0 - ramp(t, T0, T0 + 4 / 24, 'linear')              # frame 0 = K5's last frame exactly
    if k > 0:
        f = KF * k + f * (1 - k)
    f = f.astype(F32)
    lyric(f, ctx, sung(WORDS, t, tail=1.0), x=0.63, y=0.955, px=28, opacity=1.0)   # continues K5's line ("line")
    return f

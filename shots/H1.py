"""H1 (149.708-156.292): CRASH, full band. The categories arrive: painted faces stamped one per measured beat, close,
hard cuts, off-centre placement alternating corners; each face is stamped as a pale ground and finished in strokes
(colour field sweep, then the black lines drawn on in three wipes). The last bar widens.

Measured events used (analysis/timing.json):
  landings = beats 149.720 150.162 150.588 151.024 151.463 151.894 152.325 152.762 153.195 153.628 (10 faces)
  widening cuts = beats 154.061 154.496 154.930 155.364 155.810
  rubbing flips (2 frames) = 151.675 (kick 1.0), 155.147 (perc 1.0)   [no breakbeat chops are measured in the bridge]
  woodblock mis-registration (colour block vs line block, 0.16 s) = 151.241 (perc .94), 152.978 (kick .93),
    154.714 (snare), 155.810 (snare 1.0)
"""
from tools.ink import *
from shots.faces_lib import *

T0, T1 = 149.70833, 156.29167

# face -> cell for the ten H1 faces (all six real 3-stage builds land here, close)
H1_FACES = [('F01', 8), ('F02', 3), ('F21', 13), ('F06', 19), ('F04', 10), ('F23', 1), ('F16', 20), ('F08', 6),
            ('F09', 17), ('F11', 22)]
# close framing per landing: (face height as share of frame, anchor) - alternating corners, varied scale
H1_FRAMES = [(0.86, (0.36, 0.47)), (0.64, (0.67, 0.56)), (0.74, (0.33, 0.58)), (0.94, (0.64, 0.44)),
             (0.70, (0.31, 0.44)), (0.60, (0.69, 0.58)), (0.90, (0.38, 0.55)), (0.66, (0.66, 0.43)),
             (0.78, (0.34, 0.56)), (0.72, (0.65, 0.52))]


def setup(ctx):
    global AL, CUTS, FLIPS, MIS, LAND, RB
    tm = ctx.timing
    beats = [b for b in tm.beats_in(149.6, 156.3)]
    LAND = beats[:10]
    plan = [dict(id=fid, cell=c, t=LAND[i], k=1.0) for i, (fid, c) in enumerate(H1_FACES)]
    AL = Album(ctx, plan)
    CUTS = []
    for i, (fh, anc) in enumerate(H1_FRAMES):
        CUTS.append((on_frame(LAND[i]) if i else -1e9, cams_frame_face(H1_FACES[i][1], fh, anc)))
    # widening on the last bar: two faces, a pair, a block, then most of the upper sheet
    wide = beats[10:15]
    c = lambda i: cell_centre(i)
    mid = lambda a, b: ((c(a)[0] + c(b)[0]) / 2, (c(a)[1] + c(b)[1]) / 2)
    CUTS += [(wide[0], (*mid(19, 20), 1.30)),
             (wide[1], (*mid(8, 10), 1.10)),
             (wide[2], (*mid(13, 20), 0.92)),
             (wide[3], (*mid(1, 10), 0.80)),
             (wide[4], (mid(8, 20)[0] + 120, mid(8, 20)[1] - 60, 0.68))]
    FLIPS = [151.675, 155.147]
    MIS = [151.241, 152.978, 154.714, 155.810]
    RB = Rubbing(ctx.W, ctx.H, seed=21)


def cam_at(t):
    cam = CUTS[0][1]
    for tc, c in CUTS:
        if t >= on_frame(tc) - 1e-9:              # fix2: cut on the frame containing the beat
            cam = c
    return cam


def render(t, ctx):
    cam = cam_at(t)
    f, bg = AL.render(t, cam, mis=mis_at(t, MIS, hold=0.16, amount=16 * ctx.s * cam[2], seed=5))
    if flip_on(t, FLIPS, hold=2 / 24):
        f = RB.apply(f, bg)
    dx, dy = shake_offset(t, LAND[:1], amp=10 * ctx.s, dur=0.25)
    if not (dx or dy):
        dx, dy = shake_offset(t, LAND[1:], amp=4 * ctx.s, dur=0.14)
    return shaken(f, dx, dy) if (dx or dy) else f

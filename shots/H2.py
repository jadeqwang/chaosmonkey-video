"""H2 (156.292-162.625): wider and faster. The rows fill two faces per beat, then four on the fast roll; hard cuts
step the camera out until the whole grid is in frame; the last face lands alone on the bar line and the camera holds
for the last half bar on the full album leaf with ONE cell bare (row 3, col 4).

Measured events used (analysis/timing.json):
  pairs on beats 156.668 157.104 157.537 157.972; four on the fast roll 158.255 158.310 158.365 158.420
  (roll 158.191-158.420); last face on the downbeat 161.886, then hold 161.886-162.625
  cuts: 156.29 (in), 157.104, 157.537, 157.972, 158.191, 158.850, 160.143
  woodblock mis-registration: snares 159.277 159.711 160.583; rubbing flip (2 frames): kick 160.143 (strength 1.0)
"""
from tools.ink import *
from shots.faces_lib import *
from shots.H1 import H1_FACES

T0, T1 = 156.29167, 162.625

H2_LAND = [(156.668, [('F07', 0), ('F05', 2)]), (157.104, [('F03', 4), ('F22', 5)]),
           (157.537, [('F10', 7), ('F12', 9)]), (157.972, [('F18', 11), ('F19', 12)]),
           (158.255, [('F20', 16)]), (158.310, [('F13', 18)]), (158.365, [('F15', 21)]), (158.420, [('F17', 23)]),
           (161.886, [('F14', 14)])]


def album_plan(tm):
    """every face on the leaf with its landing time (H1 + H2), for any shot that shows the leaf after 156.3"""
    beats = tm.beats_in(149.6, 156.3)
    plan = [dict(id=fid, cell=c, t=beats[i], k=1.0) for i, (fid, c) in enumerate(H1_FACES)]
    for t, lst in H2_LAND:
        for fid, c in lst:
            plan.append(dict(id=fid, cell=c, t=t, k=0.6 if t < 161 else 1.0))
    return plan


def setup(ctx):
    global AL, CUTS, FLIPS, MIS, BIG, RB
    AL = Album(ctx, album_plan(ctx.timing))
    c = cell_centre
    mid = lambda *ii: (sum(c(i)[0] for i in ii) / len(ii), sum(c(i)[1] for i in ii) / len(ii))
    e = 1 / 48
    CUTS = [(-1e9, (*mid(1, 7), 0.95)),
            (157.104 - e, (*mid(4, 11), 0.92)),
            (157.537 - e, (*mid(7, 9, 13), 0.80)),
            (157.972 - e, (*mid(11, 12), 0.62)),
            (158.191 - e, (*mid(16, 23, 18, 21), 0.70)),
            (158.850 - e, (mid(0, 23)[0] - 90, mid(0, 23)[1] + 40, 0.60)),
            (160.143 - e, (*mid(0, 23), 0.555))]
    MIS = [159.277, 159.711, 160.583]
    FLIPS = [160.143]
    BIG = [156.668, 157.104, 157.537, 157.972, 161.886]
    RB = Rubbing(ctx.W, ctx.H, seed=22)


def cam_at(t):
    cam = CUTS[0][1]
    for tc, c in CUTS:
        if t >= tc:
            cam = c
    return cam


def render(t, ctx):
    cam = cam_at(t)
    f, bg = AL.render(t, cam, mis=mis_at(t, MIS, hold=0.16, amount=26 * ctx.s * cam[2], seed=6))
    if flip_on(t, FLIPS, hold=2 / 24):
        f = RB.apply(f, bg)
    dx, dy = shake_offset(t, BIG[-1:], amp=9 * ctx.s, dur=0.25)
    if not (dx or dy):
        dx, dy = shake_offset(t, BIG[:-1], amp=4 * ctx.s, dur=0.14)
    return shaken(f, dx, dy) if (dx or dy) else f

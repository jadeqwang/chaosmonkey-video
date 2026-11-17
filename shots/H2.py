"""H2 (156.292-162.625): wider and faster. The rows fill two faces per beat, then four on the fast roll; hard cuts
step the camera out until the whole grid is in frame; the last face lands alone on the bar line and the camera holds
for the last half bar on the full album leaf with ONE cell bare (row 3, col 4).

Measured events used (analysis/timing.json):
  pairs on beats 156.668 157.104 157.537 157.972; four on the fast roll 158.255 158.310 158.365 158.420
  (roll 158.191-158.420); last face on the downbeat 161.886, then hold 161.886-162.625
  cuts: 156.29 (in), 157.104, 157.537, 157.972, 158.191, 158.850, 160.143
  v3 MEDIUM SWITCH (replaces mis-registration and the 2-frame flip), held 4 frames, <= 2 per bar: snare 159.277
  paper-cut, kick 160.143 (the cut to the full leaf) rubbing, snare 160.583 shadow puppet.
"""
from tools.ink import *
from shots.faces_lib import *
from shots.H1 import H1_FACES

T0, T1 = 156.29167, 162.625

_L = lambda *cells: [(ALBUM[c], c) for c in cells]
H2_LAND = [(156.668, _L(0, 2)), (157.104, _L(4, 5)), (157.537, _L(7, 9)), (157.972, _L(11, 12)),
           (158.255, _L(16)), (158.310, _L(18)), (158.365, _L(21)), (158.420, _L(23)),
           (161.886, _L(14))]


def album_plan(tm):
    """every face on the leaf with its landing time (H1 + H2), for any shot that shows the leaf after 156.3"""
    beats = tm.beats_in(149.6, 156.3)
    plan = [dict(id=fid, cell=c, t=beats[i], k=1.0) for i, (fid, c) in enumerate(H1_FACES)]
    for t, lst in H2_LAND:
        for fid, c in lst:
            plan.append(dict(id=fid, cell=c, t=t, k=0.6 if t < 161 else 1.0))
    return plan


def setup(ctx):
    global AL, CUTS, SWITCH, BIG, MED
    AL = Album(ctx, album_plan(ctx.timing))
    c = cell_centre
    mid = lambda *ii: (sum(c(i)[0] for i in ii) / len(ii), sum(c(i)[1] for i in ii) / len(ii))
    e = 0.0
    CUTS = [(-1e9, (*mid(1, 7), 0.95)),
            (157.104 - e, (*mid(4, 11), 0.92)),
            (157.537 - e, (*mid(7, 9, 13), 0.80)),
            (157.972 - e, (*mid(11, 12), 0.62)),
            (158.191 - e, (*mid(16, 23, 18, 21), 0.70)),
            (158.850 - e, (mid(0, 23)[0] - 90, mid(0, 23)[1] + 40, 0.60)),
            (160.143 - e, (*mid(0, 23), 0.555))]
    SWITCH = [(159.277, 'papercut'), (160.143, 'rubbing'), (160.583, 'shadow')]
    BIG = [156.668, 157.104, 157.537, 157.972, 161.886]
    MED = FaceMediums(ctx, seed=22)


def cam_at(t):
    cam = CUTS[0][1]
    for tc, c in CUTS:
        if t >= on_frame(tc) - 1e-9:              # fix2: cut on the frame containing the beat
            cam = c
    return cam


def render(t, ctx):
    cam = cam_at(t)
    if medium_at(t, SWITCH, hold=4):
        return MED.switch(AL, t, cam, SWITCH, hold=4)
    f, bg = AL.render(t, cam)
    dx, dy = shake_offset(t, BIG[-1:], amp=9 * ctx.s, dur=0.25)
    if not (dx or dy):
        dx, dy = shake_offset(t, BIG[:-1], amp=4 * ctx.s, dur=0.14)
    return shaken(f, dx, dy) if (dx or dy) else f

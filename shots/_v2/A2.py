"""A2 5.458-9.708 (102 f). Team ROOMS-88. Code only: the A2 keyframe with a slow compositor drift left across the
attic floor; the thin warm lines between the floorboards come up (the kitchen light below); dust in the red beam.
The window is out of frame (sidecar), but the room's red pool breathes with the sign.
"""
from shots._rooms88 import *

T0, T1 = 131 / 24, 233 / 24
CAM = [(T0, 1010, 560, 1.10), (T1, 905, 560, 1.10)]


def setup(ctx):
    global KF, G, TEX, LINES, BG, BEAM, SG
    W, H, s = ctx.W, ctx.H, ctx.s
    KF = kf('A2', W, H)
    G = grade_field(KF, keep=[(1330, 560, 260, 200, 0.6)], floor=0.26)
    TEX = paper_tex(W, H)
    LINES, BG = floor_lines(KF, s)
    BEAM = beam_field(G, KF, s)
    SG = Sign(KF, s, (0, 0, 2, 2), (-500, -500, 10, 0))      # no glass in frame: only the pool follows the sign


def render(t, ctx):
    lv = 0.15 + 0.85 * ramp(t, T0 + 0.4, T0 + 2.6, 'sine')          # the floor lines come up
    m = (LINES * (1 - lv))[..., None]
    f = KF + (BG - KF) * m
    f = SG.apply(f, t)
    f = motes(f, t, BEAM, ctx.s)
    f = finish(f, G, TEX)
    return camera_move(f, t, CAM)

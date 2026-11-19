"""Shared helpers for team BED+CAR v4 (car F1 F3a F6b; bedroom I1 I3a I4 J1 J4 K1 K2a L1 L2). Builds on shots/_bedcar3.py.

Same model as v3: a room shot = a video-model take placed on the song clock by a piecewise time map, finished with paper fibre.
Picks live in work/bedcar4/picks4.json (shot -> {clip, map: [[song_t, src_t], ...], why}). Singing takes (Seedance 2.5 or the
two-pass Kling act -> pruna/p-video-animate, docs/LIPSYNC_V4.md) are placed 1:1: map [[place, 0], [place + 30, 30]] where place is
the song time of the clip's frame 0. No mouth is pasted, warped or transferred anywhere (REVISION_V4 §1.2): the v3 `lips` /
`paste` mechanism of _bedcar3.Take is switched off here (BEDCAR_NO_LIPS) and picks4.json has no `lips` keys.
Everything is authored in 1920x1080 px and scales by ctx.s, so 1080p is a re-render (--size 1920x1080).
"""
import os
import sys

os.environ['BEDCAR_NO_LIPS'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _bedcar3
from _bedcar3 import *          # noqa: F401,F403

_bedcar3.PICKS3 = os.path.join(ROOT, 'work/bedcar4/picks4.json')
ENDS4 = os.path.join(ROOT, 'work/bedcar4/ends')


def placed(clip, place, why=''):
    """A pick entry for a 1:1 clip whose frame 0 sits at song time `place`."""
    return {'clip': clip, 'map': [[place, 0.0], [place + 30.0, 30.0]], 'why': why}


class OtsPush4(_bedcar3.OtsPush):
    """OtsPush with the spread quad q0 given per take (_bedcar3.OTS_Q is for the v3 take): 1080p px, TL TR BR BL as read."""

    def __init__(self, ctx, take, art, end_img, q0, view=_bedcar3.VIEW_SPREAD, ta=None, tb=None, seed=45):
        self.B = Take(take, ctx)
        self.PP = _bedcar3.PagePush(ctx, q0, _bedcar3.first_existing([art]), os.path.join(ROOT, end_img), view)
        self.P = Paper(ctx.W, ctx.H, 'aged', seed=seed)
        self.ta, self.tb = ta, tb
        self.reg = np.ones((ctx.H, ctx.W), np.float32)

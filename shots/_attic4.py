"""shots/_attic4.py: the 1988 attic, preview_v4 (team ATTIC). Everything from shots/_attic3.py (Seg, Blade, PageArt, AtticShot,
title_block, soft_margins, fr), with v4 sources:

  Seg4(...)   = Seg, but its keyframe is media/kf/v4/<kf>.jpg and its pick comes from media/comp/attic4/picks.json
               {key: {'path': clip, 'tmap': [[song_t, clip_t], ...], 'twos': bool}}.
               A lip-sync take (tools/gen/lipsync_v4.py, Seedance 2.5) is placed by its measured lag:
               tmap = [[place_frame0_at, 0.0], [place_frame0_at + 10, 10.0]]  (speed 1, never retimed).
  crop_cam(cx, cy, z)  a static compositor camera at a crop of the 1920x1080 frame (the comp is authored in 1080p pixels).

Comps are rendered by tools/ink/run.py at --size 960x540 for the preview; 1080p is the same command with --size 1920x1080.
"""
import json
import os

import shots._attic3 as _a3
from shots._attic3 import *                                   # noqa: F401,F403
from tools.ink import load_image                              # noqa: F401
from tools.ink.core import ROOT

KF4 = 'media/kf/v4/'
PICKS4 = ROOT / 'media/comp/attic4/picks.json'


def kf4(name, W, H):
    return load_image(f'{KF4}{name}.jpg', size=(W, H))


def pick4(key):
    if not PICKS4.exists():
        return None
    return json.load(open(PICKS4)).get(key)


def set_pick(key, path, tmap, twos=False, **extra):
    """record a pick (used by the team's scripts, not at render time)"""
    d = json.load(open(PICKS4)) if PICKS4.exists() else {}
    d[key] = dict(path=path, tmap=tmap, twos=twos, **extra)
    PICKS4.parent.mkdir(parents=True, exist_ok=True)
    json.dump(d, open(PICKS4, 'w'), indent=1, ensure_ascii=False)


class Seg4(_a3.Seg):
    def setup(self, ctx):
        save = (_a3.kf3, _a3.pick)
        _a3.kf3, _a3.pick = kf4, pick4
        try:
            super().setup(ctx)
        finally:
            _a3.kf3, _a3.pick = save


def crop_cam(t0, t1, cx=960, cy=540, z=1.0, z1=None, cx1=None, cy1=None):
    return [(t0, cx, cy, z), (t1, cx if cx1 is None else cx1, cy if cy1 is None else cy1, z if z1 is None else z1)]

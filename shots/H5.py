"""H5 "I'm made of the telling, not just the tale" (169.250-172.750, 84 frames). BOOK v4, candidate A (procedural).

The carved gorge of v3 H5 (B_cliff_run, the B4 carving re-cut from Make Me a Hanzi strokes). A gale rises right to
left; the characters come off the stone stroke by stroke (each a PBD ribbon in 3D, peeling from its upwind end,
fluttering in curl-noise turbulence and travelling gusts) and assemble into the small girl seen from behind, drawn
in 白描 strokes (outline, folds, hair along a flow field, a few cinnabar strokes on the jacket), while the camera
pushes in. The stone keeps pale ghost-marks. Engine: shots/_book4_strokes.py (sim + bake), shots/_book4_h56comp.py.
"""
from shots import _book4_h56comp as HC

T0, T1 = 4062 / 24, 4146 / 24


def setup(ctx):
    HC.setup(ctx, 'H5')


def render(t, ctx):
    return HC.render(t, ctx)

"""H6 "one hair that can't gather, blown on the gale" (172.750-177.208, 107 frames). BOOK v4, candidate A.

Continuous from H5 (one simulation): the gale takes the girl's hair (strand physics, roots held on her head); the
camera drifts left with the wind, leaving her into the mist at the right; the cliff dissolves to bare paper. One
strand (a long hooked stroke) works loose and rides the gale alone (a gust pulls it straight, an eddy loops it, it
tumbles); from 2.2 s its root thickens and the monkey grows along it: the strand is his tail, then spine, cap and
limbs are drawn on in order, then the colour. He somersaults out to the left; the last 0.4 s is bare paper.
"""
from shots import _book4_h56comp as HC

T0, T1 = 4146 / 24, 4253 / 24


def setup(ctx):
    HC.setup(ctx, 'H6')


def render(t, ctx):
    return HC.render(t, ctx)

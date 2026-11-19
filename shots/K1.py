"""K1 (203.708-210.542) BED+CAR v4. A room take (very slow push) / B over-the-shoulder push into the page / C BOOK's K1page comp unchanged."""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 203.70833333333334, 210.54166666666666
T_OTS, T_PAGE = 4941 / 24.0, 4973 / 24.0
OTS_Q4 = [[274, 461], [1013, 184], [1231, 593], [500, 932]]     # spread on v4bc_ots_t1 at src 1.0 (measured, 1080p px, TL TR BR BL)


def setup(ctx):
    global B, P, O, KP
    B = Take('K1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=43)
    O = OtsPush4(ctx, 'ots_K1', 'K1_page.png', 'work/bedcar4/ends/K1page_f0.png', OTS_Q4, view=(2050, 1150, 0.82), ta=T_OTS + 0.15, tb=T_PAGE)
    KP = importlib.import_module('shots.K1page')
    KP.setup(ctx)


def render(t, ctx):
    if t >= T_PAGE - 1e-6:
        return KP.render(t, ctx)
    if t >= T_OTS - 1e-6:
        return O.render(t, ctx)
    return fin(push(B.at(t), ctx, t, T0, T_OTS, 1.0, 1.05, cx=900, cy=390, kind='linear'), P)

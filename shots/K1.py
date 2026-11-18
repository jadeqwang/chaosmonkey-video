"""K1 (203.708-210.542) "Do you want to know how he never died, / what he did on the other side?"  BED+CAR v3.

A. 203.708-205.875  LAP_34, close: Jade lowers her voice to a secret, her mouth in her daughter's curls (no singing mouth
   on camera: mirrors the attic whisper E5); the daughter's eyes slide to her and she is nodding before the question ends.
   Kling v4 take of media/kf/v3/K1.jpg.
B. 205.875-207.208  over Jade's shoulder onto the spread (team BOOK's K1 page: the road to the underworld) and INTO it:
   the push lands exactly on frame 0 of their full-page comp.
C. 207.208-210.542  team BOOK's page comp (shots/K1page.py rendered here unchanged: the camera travels along the rope from
   the sleeper under the pine to the gate 幽冥界).
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 203.70833333333334, 210.54166666666666
T_OTS, T_PAGE = 4941 / 24.0, 4973 / 24.0


def setup(ctx):
    global B, P, O, KP
    B = Take('K1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=43)
    O = OtsPush(ctx, 'ots_K1', 'K1_page.png', 'work/bedcar/ends/K1page_f0.png', view=(2050, 1150, 0.82), ta=T_OTS + 0.15, tb=T_PAGE)
    KP = importlib.import_module('shots.K1page')
    KP.setup(ctx)


def render(t, ctx):
    if t >= T_PAGE - 1e-6:
        return KP.render(t, ctx)
    if t >= T_OTS - 1e-6:
        return O.render(t, ctx)
    return fin(push(B.at(t), ctx, t, T0, T_OTS, 1.0, 1.05, cx=820, cy=420, kind='linear'), P)

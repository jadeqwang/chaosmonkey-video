"""J1 (189.792-190.875) the fingertip on the page.  BED+CAR v4.

She presses a carved character like a lift button (the press itself is at 189.620, in I4.py's last frames: same view, same
take); here it is lit under her finger and the camera closes in and squares onto the page art, so the last frame is the
flat page (x 0..2560, y 100..1540 of J1_page_v4) full-frame with a soft flashlight falloff: J2 can start on it.
See shots/_j1v4.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _j1v4 import *

T0, T1 = 189.79166666666666, 190.875


def setup(ctx):
    setup_j1(ctx)


def render(t, ctx):
    return j1_frame(t, ctx)

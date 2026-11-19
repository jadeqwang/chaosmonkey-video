"""J1 (189.792-190.875) the fingertip on the page.  BED+CAR v3.

The daughter, encouraged, has pressed a carved character like a lift button (the press itself is on 189.620, inside the
last frames of I4.py: same view, same take); here it is lit under her finger and the camera closes on it as drop 2 hits.
See shots/_j1v3.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _j1v3 import *

T0, T1 = 189.79166666666666, 190.875


def setup(ctx):
    setup_j1(ctx)


def render(t, ctx):
    return j1_frame(t, ctx)

"""F1 (107.042-108.833) '石头里蹦出来 没有童年'.  BED+CAR v4.  Take('F1') (two-pass rap take, placed 1:1 at 106.8), tiny push
1.00 -> 1.03.  Alternate: media/comp/F1_alt.mp4 from Take('F1_alt') (Seedance, placed 1:1 at 106.275):
  --opt alt=1   or env F1_ALT=1.  v4 re-make: default Take('F1') (F1hold t1 + animate ahold1s1, run-up audio, virtual frame0 105.13);
  env F1_B=1 -> Take('F1_b') (arun2s1).  Old pick = Take('F1_ar9').   Push is about the frame centre (z=1 untouched at the first frame)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar4 import *

T0, T1 = 107.04166666666667, 108.83333333333333
CX, CY = 960, 540


def setup(ctx):
    global B, P
    alt = str(ctx.opts.get('alt', os.environ.get('F1_ALT', '0'))) not in ('0', 'False', '')
    b = str(ctx.opts.get('b', os.environ.get('F1_B', '0'))) not in ('0', 'False', '')
    B = Take('F1_alt' if alt else ('F1_b' if b else 'F1'), ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=61)


def render(t, ctx):
    return fin(push(B.at(t), ctx, t, T0, T1, 1.0, 1.03, cx=CX, cy=CY, kind='linear'), P)

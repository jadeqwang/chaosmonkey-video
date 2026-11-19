"""F1 (107.042-108.833) '石头里蹦出来 没有童年'.  BED+CAR v3, round 2.

The BACK seat: the daughter in her child seat, the EMPTY second seat at frame right. Kling v4 take of media/kf/v3/F1.jpg.
Two framings of the same take (ctx.opts['face'] or env F1_FACE=1 picks the second):
- default (media/comp/F1.mp4): the rap played on her BODY: hands chopping apart, feet kicking, shoulders bouncing; her face
  is above the frame, so no unsynced singing mouth is on screen (REVISION_V3 section 2.6). Used because the lip transfer
  did not pass the gate (see docs/logs/LOG_v3_bedcar.md, round 2).
- face (media/comp/F1_face.mp4): tighter on her with the face in frame (about 127 px high at 540p), the LIPSYNC transfer
  pasted into the take (picks.json F1.lips).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bedcar3 import *

T0, T1 = 107.04166666666667, 108.83333333333333
HANDS = (140, 400, 1210)       # x0, y0, width of the 16:9 window on the take (1080p px)
FACE = (0, 20, 1440)


def setup(ctx):
    global B, P, R
    face = str(ctx.opts.get('face', os.environ.get('F1_FACE', '0'))) not in ('0', 'False', '')
    if not face:
        os.environ['BEDCAR_NO_LIPS'] = '1'
    B = Take('F1', ctx)
    P = Paper(ctx.W, ctx.H, 'aged', seed=61)
    R = FACE if face else HANDS


def render(t, ctx):
    x0, y0, w = R
    z = 1920.0 / w
    u = (t - T0) / (T1 - T0)
    z2 = z * (1.0 + 0.03 * u)
    cx, cy = x0 + w / 2, y0 + w * 9 / 32
    return fin(move(B.at(t), ctx, z2, cx, cy), P)

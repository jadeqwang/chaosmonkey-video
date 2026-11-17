"""F6a (118.000-120.625; F6 = F6a + F6b, split at frame 2895 = 120.625 s, just after the 120.6 wave cue): '身外身法
谁是真身 / 问了也白问 个个都真'. Two identical puppet monkeys face each other across the windscreen's centre line,
mirror-posed, re-posed together (hard, no in-betweens) on the measured beats; both lit by the same passing lamp, so
neither is the copy. Light travels from the upper left (0.44, 0.9), as painted in the keyframe.

Cues: 118.000 (身, line onset), 118.500, 118.938, 119.374, 119.812, 120.249 (beats). Each pose lives in its own
streetlight sweep; one frame of dusk glass between sweeps. Room plate: media/kf/F6a.jpg (fallback F6a_lit.png).
"""
import math

from tools.ink import *
from shots.puppet_lib import *

T0, T1 = 2832 / 24, 2895 / 24
CUES = [118.0, 118.5, 118.938, 119.374, 119.812, 120.249]
POSESEQ = ['guard', 'strike', 'salute', 'shade', 'crouch', 'leap']
QUAD = [(460, 247), (1493, 247), (1387, 567), (560, 567)]
def _rrect(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


MIRROR = _rrect(841, 277, 1085, 349, 22)          # the mirror's own outline (glass inside it is the reflection)
STEM = [(948, 238), (975, 238), (975, 274), (948, 274)]
DIR = (0.44, 0.9)


def setup(ctx):
    global PLATE, PANE, PUP, INS
    PLATE, _ = room_plate('F6a', ctx.W, ctx.H)
    PANE = Pane(ctx, PLATE, QUAD, exclude=[MIRROR, STEM])
    rig = ctx.cache('puppet_rig_v1', build_rig, deps=[f'{MK}/puppet_parts_colour.jpg', f'{MK}/puppet_heads_swap.jpg'])
    PUP = make_puppet(rig)
    INS = lyric(ctx, ['身外身法 谁是真身', '问了也白问 个个都真'], (1290, 590, 100, 440), max_px=40)


def render(t, ctx):
    f = PLATE.copy()
    k = cue_index(t, CUES) - 1
    if k >= 0:
        nxt = CUES[k + 1] if k + 1 < len(CUES) else T1 + 0.3
        sw = sweep(t, CUES[k], nxt - 1 / 24, PANE.lw, PANE.lh, DIR)
        if sw:
            lx, ly, inten, rad = sw
            pose = P[POSESEQ[k]]
            h = PANE.lh * 0.78
            T = puppet_local(PUP, pose, PANE, (PANE.lw * 0.27, PANE.lh * 0.50), h)
            T = T * puppet_local(PUP, pose, PANE, (PANE.lw * 0.73, PANE.lh * 0.50), h, flip=True)
            PANE.lay(f, T, PANE.light(lx, ly, rad, inten), lift=0.03, light_xy=(lx, ly))
    if INS is not None:
        INS.draw(f, t)
    return f

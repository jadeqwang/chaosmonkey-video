"""F2 (108.833-111.042): '一声耳语 学会七十二变 (七十二变)'. Her side window is a shadow screen: the jointed 皮影
monkey (cut from the canon puppet sheets) back-lit amber by each passing streetlight, its HEAD swapped on every
measured beat / syllable cluster (monkey -> pine -> bird -> fish -> cat -> monkey) and the body re-posed hard on the
same cues, no in-betweens. Each state lives in its own streetlight sweep (top of the pane to the bottom, the
keyframe's / sidecar's light direction 0.05, 1.0); between sweeps the pane is dusk for about a frame.

Cues (analysis/timing.json): 108.840 (一, line onset), 109.300 (beat), 109.740 (beat; 七 109.68), 110.175 (beat, kick
1.0), 110.380 (echo 七), 110.800 (echo 变). Room plate: media/kf/F2.jpg (falls back to the layout's F2_lit.png).
Pane quad measured on the painted keyframe (the sidecar's rear_right quad does not match the painting).

v3 (STAGE team): the puppet layer is unchanged (same rig as the swarm leaf, F4b-F6a). The PLATE is the car team's:
as soon as `media/kf/v3/F2.jpg` (re-blocked car: the daughter rear right, in profile at frame right, watching and
pointing) or an acted plate clip `media/kf/v3/F2_plate.mp4` (53 frames, 24 fps) exists, this script uses it, with the
pane quad from `media/layout/car26/v3_F2.json` (rear_right) or, if the painting drifted from the layout, from
`media/kf/v3/F2_pane.json` ({"quad": [[x, y] x4 TL TR BR BL in 1920x1080 px], "poly": optional}). Until then it
renders exactly as v2 (v2 plate and quad). v2 copy: shots/_v2/F2.py.
"""
import json
import os
from tools.ink import *
from shots.puppet_lib import *

T0, T1 = 2612 / 24, 2665 / 24
CUES = [108.84, 109.30, 109.74, 110.175, 110.38, 110.80]
HEADSEQ = ['monkey', 'pine', 'bird', 'fish', 'cat', 'monkey']
POSESEQ = ['stand', 'guard', 'leap', 'crouch', 'strike', 'shade']
QUAD = [(110, 170), (993, 131), (933, 576), (107, 753)]
POLY = [(107, 753), (113, 487), (307, 267), (440, 167), (993, 131), (933, 576)]
DIR = (0.05, 1.0)


V3_STILL, V3_CLIP, V3_PANE = 'media/kf/v3/F2.jpg', 'media/kf/v3/F2_plate.mp4', 'media/kf/v3/F2_pane.json'
V3_LAYOUT = 'media/layout/car26/v3_F2.json'


def _v3_plate(ctx):
    """(still plate, frames or None, quad, poly, light dir) for the re-blocked car, or None if no v3 plate yet."""
    if not (os.path.exists(V3_STILL) or os.path.exists(V3_CLIP)):
        return None
    lay = json.load(open(V3_LAYOUT))
    quad = [tuple(p) for p in lay['panes']['rear_right']['px']]
    poly = None
    d = tuple(lay['pane_backlight']['rear_right']['light_travel_dir_px'])
    if os.path.exists(V3_PANE):
        j = json.load(open(V3_PANE))
        quad, poly = [tuple(p) for p in j['quad']], ([tuple(p) for p in j['poly']] if j.get('poly') else None)
    frames = None
    if os.path.exists(V3_CLIP):
        import av
        with av.open(V3_CLIP) as c:
            frames = [cv2.resize(f.to_ndarray(format='rgb24'), (ctx.W, ctx.H), interpolation=cv2.INTER_AREA)
                      for f in c.decode(video=0)]
        still = frames[0].astype(np.float32) / 255
    else:
        still = cv2.resize(load_image(V3_STILL), (ctx.W, ctx.H), interpolation=cv2.INTER_AREA).astype(np.float32)
    return still, frames, quad, poly, d


def setup(ctx):
    global PLATE, PANE, PUP, HEADS, INS, SRC, FRAMES, DIR
    FRAMES = None
    v3 = _v3_plate(ctx)
    if v3:
        PLATE, FRAMES, quad, poly, DIR = v3
        PANE = Pane(ctx, PLATE, quad, poly=poly)
    else:
        PLATE, SRC = room_plate('F2', ctx.W, ctx.H)
        PANE = Pane(ctx, PLATE, QUAD, poly=POLY)
    rig = ctx.cache('puppet_rig_v1', build_rig, deps=[f'{MK}/puppet_parts_colour.jpg', f'{MK}/puppet_heads_swap.jpg'])
    PUP = make_puppet(rig, head='h_monkey')
    HEADS = head_parts(rig)
    INS = lyric(ctx, '一声耳语 学会七十二变', (1005, 170, 60, 470))


def render(t, ctx):
    if FRAMES is not None:
        f = FRAMES[min(len(FRAMES) - 1, max(0, int(round((t - T0) * 24))))].astype(np.float32) / 255
    else:
        f = PLATE.copy()
    k = cue_index(t, CUES) - 1
    if k >= 0:
        nxt = CUES[k + 1] if k + 1 < len(CUES) else T1 + 0.2
        sw = sweep(t, CUES[k], nxt - 1 / 24, PANE.lw, PANE.lh, DIR)
        if sw:
            lx, ly, inten, rad = sw
            pose = P[POSESEQ[k]]
            T = puppet_local(PUP, pose, PANE, (PANE.lw * 0.50, PANE.lh * 0.42), PANE.lh * 0.86,
                             swaps={'head': HEADS[HEADSEQ[k]]})
            PANE.lay(f, T, PANE.light(lx, ly, rad, inten), lift=0.035, light_xy=(lx, ly))
    if INS is not None:
        INS.draw(f, t)
    return f

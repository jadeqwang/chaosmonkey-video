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
# round 3 poses: first = the staff planted upright in a closed hand (it read as floating off the fingertips);
# last = the BACK hand shades the eyes from behind the head, so the head is never covered
POSE3 = {0: dict(P['stand'], arm_f=40, forearm_f=95, staff=-135),
         5: dict(P['shade'], arm_f=40, forearm_f=95, staff=-135, arm_b=140, forearm_b=100)}


V3_STILL, V3_CLIP, V3_PANE = 'media/kf/v3/F2.jpg', 'media/kf/v3/F2_plate.mp4', 'media/kf/v3/F2_pane.json'
V3_LAYOUT = 'media/layout/car26/v3_F2.json'
V3_MATTE = 'media/kf/v3/F2_fg_matte.mp4'       # white = her hand and forearm in front of the glass
V3_QUAD = [(177, 0), (1098, 93), (1035, 638), (78, 777)]          # TL TR BR BL, 1920x1080 px
V3_POLY = [(177, 0), (1030, 62), (1098, 110), (1035, 638), (78, 777)]


def _v3_plate(ctx):
    """(still plate, frames or None, quad, poly, light dir) for the re-blocked car, or None if no v3 plate yet."""
    if not (os.path.exists(V3_STILL) or os.path.exists(V3_CLIP)):
        return None
    # the painted pane does not match the layout sidecar (BED+CAR log): quad measured on media/kf/v3/F2.jpg
    quad, poly = V3_QUAD, V3_POLY
    d = (0.05, 1.0)
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
    global PLATE, PANE, PUP, HEADS, INS, SRC, FRAMES, DIR, MATTE
    FRAMES, MATTE = None, None
    v3 = _v3_plate(ctx)
    if v3:
        PLATE, FRAMES, quad, poly, DIR = v3
        # the screen's own quad must CONTAIN the glass polygon (the measured quad's top and right edges cut across
        # it, leaving bare blue glass): top edge lifted, right and bottom edges pushed out a few px
        quad = [(quad[0][0] - 6, quad[0][1] - 60), (quad[1][0] + 11, quad[1][1] - 109), (quad[2][0] + 15, quad[2][1] + 7),
                (quad[3][0] - 6, quad[3][1] + 6)]
        PANE = Pane(ctx, PLATE, quad, poly=poly)
        # round 3: the screen is the whole measured glass polygon grown 5 px (the colour test left blue slivers of
        # bare glass along the top and right); what is in front of the glass comes back from the car team's matte
        m = np.zeros((ctx.H, ctx.W), np.uint8)
        cv2.fillPoly(m, [np.int32(np.array(poly if poly is not None else quad) * ctx.s)], 1)
        g = max(3, int(round(11 * ctx.s)) | 1)
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (g, g)))
        PANE.mask = blur(m.astype(np.float32), 1.0 * ctx.s)
        ys, xs = np.nonzero(PANE.mask > 0.01)
        PANE.box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        if os.path.exists(V3_MATTE):
            import av
            with av.open(V3_MATTE) as c:
                MATTE = [cv2.resize(fr.to_ndarray(format='gray'), (ctx.W, ctx.H), interpolation=cv2.INTER_AREA)
                         for fr in c.decode(video=0)]
    else:
        PLATE, SRC = room_plate('F2', ctx.W, ctx.H)
        PANE = Pane(ctx, PLATE, QUAD, poly=POLY)
    rig = ctx.cache('puppet_rig_v1', build_rig, deps=[f'{MK}/puppet_parts_colour.jpg', f'{MK}/puppet_heads_swap.jpg'])
    PUP = make_puppet(rig, plumes=False)        # v3: the capped head, no plumes (the yellow monkey's silhouette)
    HEADS = head_parts(rig)
    INS = lyric(ctx, '一声耳语 学会七十二变', (1005, 170, 60, 470))


def render(t, ctx):
    if FRAMES is not None:
        i = min(len(FRAMES) - 1, max(0, int(round((t - T0) * 24))))
        f = FRAMES[i].astype(np.float32) / 255
        src = f.copy()
    else:
        f = PLATE.copy()
    k = cue_index(t, CUES) - 1
    if k >= 0:
        nxt = CUES[k + 1] if k + 1 < len(CUES) else T1 + 0.2
        sw = sweep(t, CUES[k], nxt - 1 / 24, PANE.lw, PANE.lh, DIR)
        if sw:
            lx, ly, inten, rad = sw
            pose = POSE3.get(k, P[POSESEQ[k]]) if FRAMES is not None else P[POSESEQ[k]]
            T = puppet_local(PUP, pose, PANE, (PANE.lw * 0.50, PANE.lh * (0.50 if FRAMES is not None else 0.42)),
                             PANE.lh * (0.74 if FRAMES is not None else 0.86),
                             swaps=None if HEADSEQ[k] == 'monkey' else {'head': HEADS[HEADSEQ[k]]})
            PANE.lay(f, T, PANE.light(lx, ly, rad, inten), lift=0.035, light_xy=(lx, ly))
    if FRAMES is not None and MATTE is not None:            # her pointing hand and forearm, back over the screen
        m = blur(MATTE[min(i, len(MATTE) - 1)].astype(np.float32) / 255, 1.2 * ctx.s)[..., None]
        f = f * (1 - m) + src * m
    if INS is not None:
        INS.draw(f, t)
    return f

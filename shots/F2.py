"""v4 (SWARM team): the puppet now shows the novel's chase with Erlang (Journey to the West ch. 6): monkey -> sparrow
(109.30) -> cormorant (109.74) -> fish (110.175) -> water snake (110.38) -> little earth-god temple with his tail as the
flagpole (110.80, held). Forms: work/f2/forms/*.png (gpt-image-2, tag sw4_F2_*), hard cuts. Plate is graded to the
F1/F3a warm night and the glass shows a dark night highway between/before the sweeps. Log: docs/logs/LOG_v4_swarm.md.

F2 (108.833-111.042): '一声耳语 学会七十二变 (七十二变)'. Her side window is a shadow screen: the jointed 皮影
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
AMBER = np.float32([1.0, 0.70, 0.34])         # v4: a deeper sodium amber (v3's cream read washed out)
FORMS = [None, 'sparrow', 'cormorant', 'fish', 'snake', 'temple']      # novel order; None = the monkey rig
# per form: (target height as a fraction of the screen height, centre x, centre y as fractions, rotation deg)
FORM_PLACE = {'sparrow': (0.68, 0.50, 0.52, 0), 'cormorant': (0.66, 0.50, 0.46, 0), 'fish': (0.58, 0.50, 0.52, 0),
              'snake': (0.74, 0.50, 0.55, 0), 'temple': (0.80, 0.50, 0.56, 0)}
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


# ---------------------------------------------------------------------------------------------- v4 additions
def _cut_form(path, maxside=700):
    """a form on flat white -> (T, ) leather transmittance on a tight crop (1 = open), lifted like the rig's parts."""
    im = load_image(path)
    k = maxside / max(im.shape[:2])
    im = cv2.resize(im, (int(im.shape[1] * k), int(im.shape[0] * k)), interpolation=cv2.INTER_AREA)
    T = np.clip(im / 1.0, 0, 1)
    d = -np.log(np.clip(T, 1e-3, 1)).max(axis=2)
    m = cv2.dilate((d > 0.10).astype(np.uint8), np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(m)
    pad = 8
    x0, x1, y0, y1 = max(0, xs.min() - pad), xs.max() + pad, max(0, ys.min() - pad), ys.max() + pad
    T, m = T[y0:y1, x0:x1], m[y0:y1, x0:x1]
    mk = blur(m.astype(F32), 0.7)
    Tl = np.power(T, 0.55)
    edge = np.clip(mk - cv2.erode(mk, np.ones((5, 5), np.uint8)), 0, 1)
    Tl = Tl * (1 - 0.6 * edge[..., None])
    return Tl.astype(F32)


def form_local(F, spec, pane):
    """a form's transmittance on the pane's local screen (1 elsewhere)."""
    hfrac, cx, cy, rot = spec
    h0, w0 = F.shape[:2]
    sc = min(hfrac * pane.lh / h0, 0.80 * pane.lw / w0)
    M = cv2.getRotationMatrix2D((w0 / 2, h0 / 2), rot, sc)
    M[0, 2] += cx * pane.lw - w0 / 2
    M[1, 2] += cy * pane.lh - h0 / 2
    return cv2.warpAffine(F, M, (pane.lw, pane.lh), flags=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))


def _cabin_lut(plate_frames, poly, s_ref=None):
    """per-channel percentile match of the plate's cabin (outside the glass) to the F1/F3a cabin: 9-point curves."""
    import av
    qs = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    ref = []
    for p in ('media/comp/F1.mp4', 'media/comp/F3a.mp4'):
        with av.open(p) as c:
            ref += [f.to_ndarray(format='rgb24') for i, f in enumerate(c.decode(video=0)) if i % 5 == 0]
    ref = np.concatenate([r.reshape(-1, 3) for r in ref]).astype(np.float32) / 255
    H, W = plate_frames[0].shape[:2]
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.int32(np.array(poly) * W / 1920)], 1)
    m = cv2.dilate(m, np.ones((15, 15), np.uint8)) == 0
    src = np.concatenate([f[m] for f in plate_frames[::5]]).astype(np.float32) / 255
    lut = []
    for c in range(3):
        a = np.percentile(src[:, c], qs)
        b = np.percentile(ref[:, c], qs)
        lut.append((np.concatenate([[0], a, [1]]), np.concatenate([[0], np.maximum.accumulate(b), [1]])))
    return lut


def grade(f, lut):
    out = np.empty_like(f)
    for c in range(3):
        out[..., c] = np.interp(f[..., c], lut[c][0], lut[c][1])
    return out


def road_local(t, lw, lh):
    """the night highway seen through the side glass, in pane-local px: dark sky with a warm horizon, streetlights
    (poles with amber heads) sliding past in two parallax layers, tail lights of far cars; deliberately dark."""
    sk = np.linspace(0, 1, lh, dtype=F32)[:, None]
    hz = 0.60
    top, hor, grd = np.float32([0.035, 0.040, 0.085]), np.float32([0.20, 0.13, 0.12]), np.float32([0.020, 0.020, 0.028])
    u = np.clip(sk / hz, 0, 1)[..., None]
    img = np.where(sk[..., None] < hz, top + (hor - top) * u ** 2.2, grd + 0.02 * (sk[..., None] - hz))
    img = np.repeat(img, lw, axis=1).astype(F32)
    cv2.rectangle(img, (0, int(lh * (hz - 0.012))), (lw, int(lh * hz + 3)), (0.02, 0.02, 0.03), -1)    # far tree line
    glow = np.zeros((lh, lw, 3), F32)
    sharp = np.zeros((lh, lw, 3), F32)
    for k, (speed, period, base, sc) in enumerate([(420, 330, 0.60, 0.55), (1100, 520, 0.80, 1.0)]):
        for j in range(-1, lw // period + 3):
            x = (j * period - speed * t) % (period * (lw // period + 3)) - period
            ytop = base * lh - 0.34 * lh * sc
            cv2.line(sharp, (int(x), int(base * lh)), (int(x), int(ytop)), (0.16, 0.12, 0.13), max(1, int(3 * sc)))
            cv2.line(sharp, (int(x), int(ytop)), (int(x - 28 * sc), int(ytop + 3 * sc)), (0.16, 0.12, 0.13), max(1, int(3 * sc)))
            cv2.circle(glow, (int(x - 28 * sc), int(ytop + 6 * sc)), max(4, int(15 * sc)), (1.0, 0.62, 0.22), -1)
    for j in range(3):          # far cars, tail lights drifting slowly
        x = (150 + 330 * j - 60 * t) % lw
        y = int(hz * lh + 5 + 6 * j)
        for dx in (-9, 9):
            cv2.circle(glow, (int(x + dx), y), 3, (1.0, 0.12, 0.08), -1)
    g1, g2 = blur(glow, 3.0), blur(glow, 22.0)
    img = np.where(sharp.max(axis=2, keepdims=True) > 0, sharp, img) + 0.9 * g1 + 1.6 * g2
    return np.clip(img, 0, 1) * 0.95


def lay_road(f, pane, road_local_img, a=0.92):
    x0, y0, x1, y1 = pane.box
    Hs = np.float64([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]]) @ pane.Hm
    w = cv2.warpPerspective(road_local_img, Hs, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
    m = (pane.mask[y0:y1, x0:x1] * a)[..., None]
    sub = f[y0:y1, x0:x1]
    # darkened, softly reflected: the road is seen through the plate's own faint glass tone
    sub[:] = sub * (1 - m) + (w * 0.95 + sub * 0.10) * m
    return f


def setup(ctx):
    global PLATE, PANE, PUP, HEADS, INS, SRC, FRAMES, DIR, MATTE, LUT, FORMIM, FORMT
    LUT, FORMT = None, {}
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
    FORMIM = {k: _cut_form(f'work/f2/forms/{k}.png') for k in FORMS if k}
    FORMT = {k: form_local(FORMIM[k], FORM_PLACE[k], PANE) for k in FORMIM}
    if FRAMES is not None:
        LUT = _cabin_lut(FRAMES, poly if poly is not None else quad)
    INS = lyric(ctx, '一声耳语 学会七十二变', (1005, 170, 60, 470))


def render(t, ctx):
    if FRAMES is not None:
        i = min(len(FRAMES) - 1, max(0, int(round((t - T0) * 24))))
        f = FRAMES[i].astype(np.float32) / 255
        if LUT is not None:
            f = grade(f, LUT)
        src = f.copy()
    else:
        f = PLATE.copy()
    lay_road(f, PANE, road_local(t, PANE.lw, PANE.lh))
    k = cue_index(t, CUES) - 1
    if k >= 0:
        nxt = CUES[k + 1] if k + 1 < len(CUES) else T1 + 0.2
        sw = sweep(t, CUES[k], nxt - 1 / 24, PANE.lw, PANE.lh, DIR, radius_k=1.25)
        if sw:
            lx, ly, inten, rad = sw
            if k == 0:                      # the first streetlight rises out of the road reflection over ~6 frames
                inten *= float(smoothstep(0.0, 0.26, t - CUES[0]))
            pose = POSE3.get(k, P[POSESEQ[k]]) if FRAMES is not None else P[POSESEQ[k]]
            if FORMS[k]:
                T = FORMT[FORMS[k]]
            else:
              T = puppet_local(PUP, pose, PANE, (PANE.lw * 0.50, PANE.lh * (0.50 if FRAMES is not None else 0.42)),
                             PANE.lh * (0.74 if FRAMES is not None else 0.86),
                             swaps=None if HEADSEQ[k] == 'monkey' else {'head': HEADS[HEADSEQ[k]]})
            PANE.lay(f, T, PANE.light(lx, ly, rad, inten), lift=0.035, light_xy=(lx, ly), colour=AMBER, gain=1.0)
    if FRAMES is not None and MATTE is not None:            # her pointing hand and forearm, back over the screen
        m = blur(MATTE[min(i, len(MATTE) - 1)].astype(np.float32) / 255, 1.2 * ctx.s)[..., None]
        f = f * (1 - m) + src * m
    if INS is not None:
        INS.draw(f, t)
    return f

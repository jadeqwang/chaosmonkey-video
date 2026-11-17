"""The three swarm layouts as stills -> work/review/comp_v3/_swarm_options.jpg (each panel 960x540).
A: the car's panes are the cells (v2 keyframe plate).  B: a ruled album leaf, full frame, intercut with the car.
C: the album leaf seen across the windscreen glass."""
import sys, types
sys.path.insert(0, '.')
import cv2, numpy as np
from tools.ink import *
from tools.ink.puppet import LAMP
from shots.swarm_lib import *
from shots.puppet_lib import Pane, room_plate
from tools.stage.swarm_mock import ctx_of, leaf_still

W, H = 1920, 1080
ctx = ctx_of(W, H)
rig = load_rig()
cyc = job_cycles()
STEPS = (0, 1, 2, 3, 0, 1, 2, 3, 0)

# ---- B
B, _ = leaf_still(W, H, STEPS, rig=rig)

# ---- A: panes as cells
plate, _ = room_plate('F4b', W, H)
SIDE = {'left_rear': [(0, 200), (160, 213), (193, 627), (0, 720)],
        'left_front': [(273, 251), (400, 264), (387, 627), (267, 653)],
        'right_front': [(1533, 287), (1733, 253), (1780, 547), (1547, 533)]}
WIND = [(520, 253), (1493, 253), (1400, 571), (747, 571)]
A = plate.copy()
def pane_worker(pane, job, k, xs, hfrac, flip=False, slip=True):
    prop, poses = cyc[job]
    pose = dict(poses[k % len(poses)])
    if flip:
        pose['_flip'] = not pose.get('_flip', False)
    h = pane.lh * hfrac
    T = rig.puppet(prop).render(pose, pos=(pane.lw * xs, pane.lh * 0.52), scale=h / RIG_H, size=(pane.lw, pane.lh))
    if slip:
        g = glyph(job or '我', KAI, int(pane.lh * 0.16))
        gh, gw = g.shape
        x, y = int(pane.lw * xs + h * 0.30), int(pane.lh * 0.08)
        x = min(x, pane.lw - gw - 4)
        T[y:y + gh, x:x + gw] *= (1 - 0.95 * g)[..., None]
        cv2.rectangle(T, (x - 6, y - 6), (x + gw + 6, y + gh + 6), (0.1, 0.1, 0.1), 2)
    return T
wp = Pane(ctx, plate, WIND, lw=1000)
T = pane_worker(wp, None, 0, 0.50, 0.70) * pane_worker(wp, '读', 0, 0.16, 0.62) * pane_worker(wp, '战', 1, 0.84, 0.62, True)
wp.lay(A, T, np.ones((wp.lh, wp.lw), np.float32) * 0.95, lift=0)
for (name, q), job, k in zip(SIDE.items(), ['算', '写', '扫'], [0, 1, 2]):
    pn = Pane(ctx, plate, q, lw=400)
    pn.lay(A, pane_worker(pn, job, k, 0.5, 0.55, name.startswith('right')), np.ones((pn.lh, pn.lw), np.float32) * 0.95, lift=0)
# threads from the centre of the windscreen to each copy
cen = (1005, 400)
for e in [(690, 400), (1320, 400), (90, 440), (335, 440), (1650, 410)]:
    cv2.line(A, cen, e, (0.92, 0.22, 0.14), 3, cv2.LINE_AA)

# ---- C: the leaf across the windscreen
plateC, _ = room_plate('F4b', W, H)
C = plateC.copy()
wp = Pane(ctx, plateC, WIND, lw=1400)
c2 = ctx_of(wp.lw, wp.lh)
c2.s = wp.lw / 1920
leaf = (30, 14, 1890, int(wp.lh / c2.s) - 14)
Pp = Paper(wp.lw, wp.lh, 'aged', seed=61)
L = Leaf(c2, rig, Pp, leaf=leaf, fig_h=int((leaf[3] - leaf[1]) / 3 * 0.66))
f = np.ones((wp.lh, wp.lw, 3), np.float32)
L.draw(f, list(STEPS))
wp.lay(C, f, np.ones((wp.lh, wp.lw), np.float32) * 0.97, lift=0)

def lab(img, text):
    im = (np.clip(resize(img, 960, 540), 0, 1) * 255).astype(np.uint8).copy()
    cv2.rectangle(im, (0, 0), (960, 30), (20, 20, 20), -1)
    cv2.putText(im, text, (10, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 235, 120), 1, cv2.LINE_AA)
    return im
row = np.concatenate([lab(A, 'A  the car panes are the cells'), lab(B, 'B  ruled album leaf, full frame (intercut with the car)'),
                      lab(C, 'C  the album leaf seen across the windscreen')], axis=1)
import os
os.makedirs('work/review/comp_v3', exist_ok=True)
cv2.imwrite('work/review/comp_v3/_swarm_options.jpg', row[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
small = cv2.resize(row, (1400, int(540 * 1400 / 2880)), interpolation=cv2.INTER_AREA)
cv2.imwrite('work/stage/v3/tmp/swarm_options_small.jpg', small[..., ::-1])
for k, im in enumerate((A, B, C)):
    cv2.imwrite(f'work/stage/v3/tmp/swarm_opt_{"ABC"[k]}.jpg', (np.clip(resize(im, 960, 540), 0, 1) * 255).astype(np.uint8)[..., ::-1])

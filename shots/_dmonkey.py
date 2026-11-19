"""shots/_dmonkey.py: the costume-B monkey element (STAGE, media/gen/stage/v4/clips/s4_d6_*.mp4) somersaulting in from
the right on his cloud and landing on the middle pillar of the palm in 亮相, composited into the D6 frames of the flight.

The clip is keyed off its paper, retimed to the music (touch 74.353, land 74.800, 亮相 75.025, as v3 D6) and pinned
so that his feet at the landing sit on the summit of the middle pillar as the 3D camera sees it in every frame (the
summit's screen position is projected from the scene camera). Env DF_MONKEY_CLIP overrides the take.
"""
import json
import math
import os
import sys

import av
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import ROOT, rot_yxz  # noqa: E402
from tools.world import prep  # noqa: E402

CLIP = os.environ.get('DF_MONKEY_CLIP', 'media/gen/stage/v4/clips/s4_d6_k4d.mp4')
F_D6 = 134                    # first flight frame of D6
SCALE = float(os.environ.get('DF_MONKEY_SCALE', '0.34'))
# (D6 frame, clip frame) retime: ride + somersault fast (on twos), crouch, 亮相 on 75.025, then the clip's own settle
RETIME = [(0, 6), (20, 44), (31, 77), (37, 106), (69, 142)]


def project(cam, X, W=1920, H=1080):
    p, t = np.array(cam['p']), np.array(cam['t'])
    f = t - p; f /= np.linalg.norm(f)
    up = np.array(cam.get('up', [0, 1, 0]), float)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    d = np.array(X) - p
    x, y, z = d @ r, d @ u, d @ f
    th = math.tan(math.radians(cam['fov']) / 2)
    return np.array([W / 2 + x / z / th * H / 2, H / 2 - y / z / th * H / 2])


def summit(scene, card_id='p0'):
    """World position of the summit of the middle pillar (top of its painted rock at the card's centre line)."""
    o = next(c for c in scene['cards'] if c.get('id') == card_id)
    from PIL import Image
    a = np.array(Image.open(os.path.join(ROOT, o['tex'])))[..., 3]
    col = a[:, a.shape[1] * 4 // 10:a.shape[1] * 6 // 10].max(1)
    v = np.argmax(col > 128) / a.shape[0]
    w, h = o['size']
    x, y = 0.0, (1 - v) * h
    R = rot_yxz(o.get('yaw', 0), o.get('pitch', 0), o.get('roll', 0))
    return (np.array(o['pos']) + R @ np.array([x, y, 0.0])).tolist()


def load_clip(path):
    out = []
    with av.open(os.path.join(ROOT, path)) as c:
        for fr in c.decode(video=0):
            out.append(fr.to_ndarray(format='rgb24'))
    return out


STAGE_T = 'media/el/stage_v4/D6_monkey_B_T_png/%04d.png'     # STAGE's element: ink transmittance, 1 = nothing
STAGE_FOOT = (731.0, 926.0)                                    # standing foot of the final 亮相, element px


def monkey_layer(scene_path='work/world/Dflight/scene.json'):
    """STAGE's D6 element (enters right on a small ink cloud, somersault, crouch-land, 亮相 on 75.025), pinned by its
    standing foot to the summit of the middle pillar as the 3D camera sees it, scaled to ~12 % of frame height."""
    if os.environ.get('DF_MONKEY_CLIP'):
        return monkey_layer_clip(scene_path)
    S = json.load(open(os.path.join(ROOT, scene_path)))
    top = summit(S)
    sc = float(os.environ.get('DF_MONKEY_SCALE', '0.32'))

    def layer(img, f):
        g = f - F_D6
        p = os.path.join(ROOT, STAGE_T % g)
        if g < 0 or not os.path.exists(p):
            return img
        T = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        H, W = img.shape[:2]
        s = sc * H / 1080
        pin = project(S['camera'][f], top) * (H / 1080)
        u = min(1.0, g / 30.0)                                   # in from the right edge, the drift dies at the landing
        dx, dy = 820.0 * (1 - u) ** 2 * H / 1080, 120.0 * (1 - u) ** 2 * H / 1080
        M = np.array([[s, 0, pin[0] - STAGE_FOOT[0] * s + dx], [0, s, pin[1] - STAGE_FOOT[1] * s + 2 * s + dy]], np.float32)
        Tw = cv2.warpAffine(T, M, (W, H), flags=cv2.INTER_AREA, borderValue=(1.0, 1.0, 1.0))
        return img * Tw
    return layer


def monkey_layer_clip(scene_path='work/world/Dflight/scene.json'):
    S = json.load(open(os.path.join(ROOT, scene_path)))
    frames = load_clip(CLIP)
    H0, W0 = frames[0].shape[:2]
    paper = prep.paper_colour(frames[0])
    top = summit(S)
    cache = {}

    def keyed(k):
        if k not in cache:
            rgb = frames[min(k, len(frames) - 1)]
            a = prep.key_alpha(rgb, paper, 0.05, 0.22)
            a = cv2.GaussianBlur(a, (0, 0), 0.6)
            # a little ink-line weight survives the downscale
            cache[k] = (rgb.astype(np.float32) / 255, a.astype(np.float32))
        return cache[k]

    # landing anchor in the clip: bottom centre of the figure in the 亮相 frame
    _, a_land = keyed(RETIME[3][1] + 10)
    ys, xs = np.nonzero(a_land > 0.5)
    anchor = np.array([np.median(xs[ys > ys.max() - 12]), ys.max()], float)
    fx = [r[0] for r in RETIME]; fc = [r[1] for r in RETIME]

    def layer(img, f):
        g = f - F_D6
        if g < 0:
            return img
        k = int(round(np.interp(g, fx, fc)))
        if g < RETIME[3][0]:
            k -= k % 2                                            # on twos in the air, like the stage shots
        rgb, a = keyed(k)
        H, W = img.shape[:2]
        s = SCALE * H / 1080
        pin = project(S['camera'][f], top) * (H / 1080)
        # in from the right: an extra drift that dies away at the landing
        u = min(1.0, g / RETIME[2][0])
        drift = np.array([1150.0, 380.0]) * (1 - (1 - (1 - u) ** 2)) * (H / 1080)
        M = np.array([[s, 0, pin[0] - anchor[0] * s + drift[0]], [0, s, pin[1] - anchor[1] * s + 2 * s + drift[1]]], np.float32)
        ar = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_AREA)
        cr = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_AREA)
        return img * (1 - ar[..., None]) + cr * ar[..., None]
    return layer

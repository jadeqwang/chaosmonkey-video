"""Stage team: first/last frames for first+last-frame video generation.
Each canon single is keyed off its own paper and laid onto ONE blank sheet (blank_sd5) at a chosen place and height,
so every frame of a chain shares the same paper and the figure scale is consistent.
    PY tools/stage/make_frames.py
"""
import sys, os, json
import numpy as np
sys.path.insert(0, '.')
from tools.ink import load_image, save_image, key_paper, resize, lay_ink

S = 'design/characters/monkey/singles/'
OUT = 'media/gen/stage/frames/'
W, H = 2560, 1440
BLANK = resize(load_image('media/vbake/_frames/blank_sd5.jpg'), W, H)

def fig(name):
    img = load_image(S + name)
    T = key_paper(img, lo=0.03)
    d = 1 - T.mean(axis=2)
    ys, xs = np.where(d > 0.08)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    pad = 10
    y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
    return T[y0:y1 + pad, x0:x1 + pad]

def frame(name, cx, cy, h_frac, out, flip=False):
    T = fig(name)
    if flip:
        T = T[:, ::-1]
    h = int(H * h_frac); w = int(T.shape[1] * h / T.shape[0])
    T = resize(T, w, h)
    f = BLANK.copy()
    lay_ink(f, T, int(cx * W - w / 2), int(cy * H - h / 2))
    save_image(OUT + out, f)
    return dict(src=name, cx=cx, cy=cy, h=h_frac, flip=flip, box=[int(cx * W - w / 2), int(cy * H - h / 2), w, h])

M = {}
M['blank.jpg'] = None
save_image(OUT + 'blank.jpg', BLANK)
# D1: blank -> 亮相 standing a little left of centre (thrown from the upper right)
M['d1_last.jpg'] = frame('01_liangxiang.jpg', 0.42, 0.53, 0.78, 'd1_last.jpg')
# D6: running in from the right -> 亮相 at the left (tumbling pass right to left)
M['d6_first.jpg'] = frame('14_cartwheel_b.jpg', 0.80, 0.56, 0.50, 'd6_first.jpg')
M['d6_last.jpg'] = frame('01_liangxiang.jpg', 0.22, 0.56, 0.52, 'd6_last.jpg')
# D7: staff flower a -> thrust (closer)
M['d7_first.jpg'] = frame('09_staff_flower_a.jpg', 0.50, 0.52, 0.88, 'd7_first.jpg')
M['d7_last.jpg'] = frame('12_thrust.jpg', 0.50, 0.58, 0.62, 'd7_last.jpg')
# D8: thrust -> perched on the planted staff, shading his eyes
M['d8_first.jpg'] = frame('12_thrust.jpg', 0.45, 0.68, 0.45, 'd8_first.jpg')
M['d8_last.jpg'] = frame('08_perched_on_staff.jpg', 0.45, 0.50, 0.88, 'd8_last.jpg')
# J3: overhead sweep -> thrust, large
M['j3_first.jpg'] = frame('11_overhead_sweep.jpg', 0.50, 0.50, 0.90, 'j3_first.jpg')
M['j3_last.jpg'] = frame('12_thrust.jpg', 0.48, 0.58, 0.66, 'j3_last.jpg')
json.dump(M, open(OUT + 'frames.json', 'w'), indent=1)
print(json.dumps(M, indent=1))

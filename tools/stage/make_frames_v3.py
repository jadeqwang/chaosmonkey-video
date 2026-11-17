"""Stage team v3 (yellow monkey): first/last frames for first+last-frame video generation.
Each v3 single is keyed off its own paper and laid onto ONE blank sheet (blank_sd5) at a chosen place and height.
    PY tools/stage/make_frames_v3.py   -> media/gen/stage/v3/frames/*.jpg (+ frames.json), 2048 refs in media/gen/refs/s3_*"""
import sys, os, json
import numpy as np
sys.path.insert(0, '.')
from tools.ink import load_image, save_image, key_paper, resize, lay_ink

S = 'design/characters/monkey/v3/singles/'
OUT = 'media/gen/stage/v3/frames/'
os.makedirs(OUT, exist_ok=True)
W, H = 2560, 1440
BLANK = resize(load_image('media/vbake/_frames/blank_sd5.jpg'), W, H)
_F = {}

def fig(name):
    if name not in _F:
        img = load_image(S + name)
        T = key_paper(img, lo=0.025)
        d = 1 - T.min(axis=2)
        ys, xs = np.where(d > 0.08)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        pad = 10
        y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
        _F[name] = T[y0:y1 + pad, x0:x1 + pad]
    return _F[name]

def frame(name, cx, cy, h_frac, out, flip=False, base=None):
    """cy = centre (share of H) unless base (share of H where the feet stand) is given."""
    T = fig(name)
    if flip:
        T = T[:, ::-1]
    h = int(H * h_frac); w = int(T.shape[1] * h / T.shape[0])
    T = resize(T, w, h)
    f = BLANK.copy()
    y = int(base * H - h) if base is not None else int(cy * H - h / 2)
    lay_ink(f, T, int(cx * W - w / 2), y)
    save_image(OUT + out, f)
    from PIL import Image
    im = Image.open(OUT + out).convert('RGB'); im.thumbnail((2048, 2048), Image.LANCZOS)
    im.save('media/gen/refs/s3_' + out, 'JPEG', quality=92)
    return dict(src=name, cx=cx, h=h_frac, flip=flip, box=[int(cx * W - w / 2), y, w, h])

M = {}
save_image(OUT + 'blank.jpg', BLANK)
from PIL import Image
im = Image.open(OUT + 'blank.jpg').convert('RGB'); im.thumbnail((2048, 2048)); im.save('media/gen/refs/s3_blank.jpg', quality=92)
h01 = fig('01_liangxiang.jpg').shape[0]
rel = lambda n: fig(n).shape[0] / h01            # the sheet's own relative heights (same hand, same scale)
# D1: blank -> 亮相 a little left of centre
M['d1_last.jpg'] = frame('01_liangxiang.jpg', 0.42, None, 0.74, 'd1_last.jpg', base=0.93)
# D2: 亮相 -> the fourth bow (north, away), standing on the same spot at the same scale
M['d2_last.jpg'] = frame('05_bow_north.jpg', 0.42, None, 0.74 * rel('05_bow_north.jpg'), 'd2_last.jpg', base=0.93)
# D6: running in from the right -> 亮相 at the left (the tumbling pass)
M['d6_first.jpg'] = frame('14_cartwheel_b.jpg', 0.82, None, 0.46 * rel('14_cartwheel_b.jpg'), 'd6_first.jpg', base=0.80)
M['d6_last.jpg'] = frame('01_liangxiang.jpg', 0.22, None, 0.46, 'd6_last.jpg', base=0.80)
# D7: staff flower a -> thrust
M['d7_first.jpg'] = frame('09_staff_flower_a.jpg', 0.50, 0.52, 0.80, 'd7_first.jpg')
M['d7_last.jpg'] = frame('12_thrust.jpg', 0.50, 0.60, 0.80 * rel('12_thrust.jpg') / rel('09_staff_flower_a.jpg'), 'd7_last.jpg')
# D8: thrust -> perched on the planted staff
M['d8_first.jpg'] = frame('12_thrust.jpg', 0.45, None, 0.42, 'd8_first.jpg', base=0.95)
M['d8_last.jpg'] = frame('08_perched_on_staff.jpg', 0.45, None, 0.88, 'd8_last.jpg', base=0.95)
# J3: overhead sweep -> thrust, large
M['j3_first.jpg'] = frame('11_overhead_sweep.jpg', 0.50, 0.50, 0.88, 'j3_first.jpg')
M['j3_last.jpg'] = frame('12_thrust.jpg', 0.48, 0.60, 0.88 * rel('12_thrust.jpg') / rel('11_overhead_sweep.jpg'), 'j3_last.jpg')
json.dump(M, open(OUT + 'frames.json', 'w'), indent=1)
# overview
import cv2
names = ['d1_last', 'd2_last', 'd6_first', 'd6_last', 'd7_first', 'd7_last', 'd8_first', 'd8_last', 'j3_first', 'j3_last']
tiles = [cv2.resize(cv2.imread(OUT + n + '.jpg'), (480, 270)) for n in names]
rows = [np.concatenate(tiles[i:i + 5], axis=1) for i in (0, 5)]
cv2.imwrite('work/stage/v3/tmp/frames_overview.jpg', np.concatenate(rows, axis=0))

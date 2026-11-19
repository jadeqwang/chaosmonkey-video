"""Stage team v4 (costume B): keyframes for first/middle/last-frame video generation. Each costume-B single
(design/characters/monkey/v4/singles) is keyed off its paper and laid on ONE blank sheet at a chosen place, all at one
shared pixel scale per shot (so the figure never changes size between keyframes).
    PY tools/stage/make_frames_v4.py -> media/gen/stage/v4/frames/*.jpg (+ frames.json, overview), refs media/gen/refs/s4_*"""
import sys, os, json
import numpy as np
sys.path.insert(0, '.')
from tools.ink import load_image, save_image, key_paper, resize, lay_ink

S = 'design/characters/monkey/v4/singles/'
OUT = 'media/gen/stage/v4/frames/'
os.makedirs(OUT, exist_ok=True); os.makedirs('work/stage/v4/tmp', exist_ok=True)
W, H = 2560, 1440
BLANK = resize(load_image('media/vbake/_frames/blank_sd5.jpg'), W, H)
_F = {}


def fig(name):
    if name not in _F:
        T = key_paper(load_image(S + name + '.jpg'), lo=0.025)
        d = 1 - T.min(axis=2)
        ys, xs = np.where(d > 0.08)
        _F[name] = T[max(0, ys.min() - 8):ys.max() + 8, max(0, xs.min() - 8):xs.max() + 8]
    return _F[name]


def restaff(T, band, new_len):
    """Resize only the rows of a staff-only band (bare staff, nothing else in those rows) to new_len rows, so the
    staff is the same length in every climbing keyframe."""
    y0, y1 = band
    mid = resize(T[y0:y1], T.shape[1], new_len)
    return np.concatenate([T[:y0], mid, T[y1:]], axis=0)


def foot_x(T):
    d = 1 - T.min(axis=2)
    ys, xs = np.where(d[-60:] > 0.15)
    return xs.mean()


def frame(T, x, base, sc, out, flip=False, anchor='centre', extra=None):
    """Lay T at scale sc with its bottom at base*H; x = share of W of the figure centre (anchor 'centre') or of the
    staff foot (anchor 'foot')."""
    if flip:
        T = T[:, ::-1]
    h, w = int(T.shape[0] * sc), int(T.shape[1] * sc)
    ax = (foot_x(T) * sc) if anchor == 'foot' else w / 2
    Ts = resize(T, w, h)
    f = BLANK.copy()
    x0, y0 = int(x * W - ax), int(base * H - h)
    lay_ink(f, Ts, x0, y0)
    save_image(OUT + out, f)
    from PIL import Image
    im = Image.open(OUT + out).convert('RGB'); im.thumbnail((2048, 2048), Image.LANCZOS)
    im.save('media/gen/refs/s4_' + out, 'JPEG', quality=93)
    return dict(box=[x0, y0, w, h], sc=sc, flip=flip)


M = {}
save_image(OUT + 'blank.jpg', BLANK)
from PIL import Image
im = Image.open(OUT + 'blank.jpg').convert('RGB'); im.thumbnail((2048, 2048)); im.save('media/gen/refs/s4_blank.jpg', quality=93)

# D1 / D2: 亮相 a little left of centre, the four bows on the same spot at the same scale
sc = 0.74 * H / fig('01_liangxiang').shape[0]
M['d1_last.jpg'] = frame(fig('01_liangxiang'), 0.42, 0.93, sc, 'd1_last.jpg')
M['d2_e.jpg'] = frame(fig('05_bow_profile_left_A'), 0.42, 0.93, sc, 'd2_e.jpg', flip=True)    # profile facing right
M['d2_s.jpg'] = frame(fig('06_bow_front'), 0.42, 0.93, sc, 'd2_s.jpg')
M['d2_w.jpg'] = frame(fig('07_bow_profile_left_B'), 0.42, 0.93, sc, 'd2_w.jpg')
M['d2_n.jpg'] = frame(fig('08_bow_back'), 0.42, 0.93, sc, 'd2_n.jpg')

M['d2_se.jpg'] = frame(fig('25_salute_profile_left_A'), 0.42, 0.93, sc, 'd2_se.jpg', flip=True)
M['d2_ss.jpg'] = frame(fig('26_salute_front'), 0.42, 0.93, sc, 'd2_ss.jpg')
M['d2_sw.jpg'] = frame(fig('27_salute_profile_left_B'), 0.42, 0.93, sc, 'd2_sw.jpg')
M['d2_sn.jpg'] = frame(fig('28_salute_back'), 0.42, 0.93, sc, 'd2_sn.jpg')

# D6 element (for WORLD): riding the cloud in at the right -> somersault -> 亮相 left of centre
sc6 = 0.42 * H / fig('01_liangxiang').shape[0]
M['d6_first.jpg'] = frame(fig('21_cloud_ride'), 0.84, 0.62, sc6, 'd6_first.jpg')
M['d6_mid.jpg'] = frame(fig('22_cloud_somersault'), 0.60, 0.55, sc6, 'd6_mid.jpg')
M['d6_layout.jpg'] = frame(fig('19_somersault_layout'), 0.50, 0.62, sc6, 'd6_layout.jpg')
M['d6_crouch.jpg'] = frame(fig('20_landing_crouch'), 0.40, 0.86, sc6, 'd6_crouch.jpg')
M['d6_last.jpg'] = frame(fig('01_liangxiang'), 0.38, 0.86, sc6, 'd6_last.jpg')

# D7: staff flower -> overhead spin -> thrust lunge (closer)
sc7 = 0.80 * H / fig('09_staff_flower').shape[0]
M['d7_first.jpg'] = frame(fig('09_staff_flower'), 0.50, 0.92, sc7, 'd7_first.jpg')
M['d7_mid.jpg'] = frame(fig('10_staff_overhead_spin'), 0.50, 0.92, sc7, 'd7_mid.jpg')
M['d7_last.jpg'] = frame(fig('03_thrust_lunge'), 0.50, 0.92, sc7, 'd7_last.jpg')

# D8: thrust (as D7 ends, smaller) -> plant -> climb low -> climb high -> perched; one staff length, one foot point
L = 1640
c13 = fig('13_climb_plant'); c14 = fig('14_climb_low')
c15 = restaff(fig('15_climb_high'), (1130, 1900), 1900 - 1130 - 235)
c16 = restaff(fig('16_perched_lookout'), (760, 2020), 2020 - 760 + 300)
sc8 = 0.90 * H / c16.shape[0]
FOOT = 0.47
M['d8_first.jpg'] = frame(fig('03_thrust_lunge'), FOOT, 0.95, sc8, 'd8_first.jpg')
M['d8_plant.jpg'] = frame(c13, FOOT, 0.95, sc8, 'd8_plant.jpg', anchor='foot')
M['d8_low.jpg'] = frame(c14, FOOT, 0.95, sc8, 'd8_low.jpg', anchor='foot')
M['d8_high.jpg'] = frame(c15, FOOT, 0.95, sc8, 'd8_high.jpg', anchor='foot')
M['d8_last.jpg'] = frame(c16, FOOT, 0.95, sc8, 'd8_last.jpg', anchor='foot')

# J3: overhead strike -> low sweep -> overhead spin -> thrust, large
scj = 0.88 * H / fig('11_overhead_strike').shape[0]
M['j3_first.jpg'] = frame(fig('11_overhead_strike'), 0.50, 0.95, scj, 'j3_first.jpg')
M['j3_sweep.jpg'] = frame(fig('12_low_sweep'), 0.50, 0.95, scj, 'j3_sweep.jpg')
M['j3_spin.jpg'] = frame(fig('10_staff_overhead_spin'), 0.50, 0.95, scj, 'j3_spin.jpg')
M['j3_last.jpg'] = frame(fig('03_thrust_lunge'), 0.48, 0.92, scj, 'j3_last.jpg')
json.dump(M, open(OUT + 'frames.json', 'w'), indent=1)

import cv2
names = list(M)
tiles = []
for n in names:
    t = cv2.resize(cv2.imread(OUT + n), (480, 270)); cv2.putText(t, n, (4, 16), 0, 0.5, (0, 0, 200), 1); tiles.append(t)
while len(tiles) % 5: tiles.append(np.full_like(tiles[0], 255))
rows = [np.concatenate(tiles[i:i + 5], axis=1) for i in range(0, len(tiles), 5)]
cv2.imwrite('work/stage/v4/tmp/frames_overview.jpg', np.concatenate(rows, axis=0))
print(len(M), 'frames')

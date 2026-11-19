"""Cut the v4 costume-B pose sheets into singles: ink components grouped to the nearest figure seed, each figure
cropped with padding on its own sheet's paper colour (no neighbour bits).  PY tools/stage/cut4.py"""
import cv2, numpy as np, os
V = 'design/characters/monkey/v4/'
K = 1.92
SHEETS = {
 'poses_A_liang': [('01_liangxiang', 230, 450), ('02_heshi_do_not_use_as_salute', 715, 500), ('03_thrust_lunge', 1200, 560), ('04_newborn_crouch', 1730, 750)],
 'poses_B_bows': [('05_bow_profile_left_A', 300, 500), ('06_bow_front', 760, 500), ('07_bow_profile_left_B', 1250, 500), ('08_bow_back', 1720, 500)],
 'poses_C_staff': [('09_staff_flower', 250, 600), ('10_staff_overhead_spin', 700, 500), ('11_overhead_strike', 1180, 500), ('12_low_sweep', 1650, 800)],
 'poses_D_climb': [('13_climb_plant', 330, 650), ('14_climb_low', 760, 600), ('15_climb_high', 1200, 400), ('16_perched_lookout', 1650, 300)],
 'poses_E_tumble': [('17_launch', 300, 500), ('18_somersault_tuck', 750, 500), ('19_somersault_layout', 1180, 500), ('20_landing_crouch', 1650, 800)],
 'poses_G_salute': [('25_salute_profile_left_A', 300, 550), ('26_salute_front', 730, 550), ('27_salute_profile_left_B', 1190, 550), ('28_salute_back', 1680, 550)],
 'poses_F_cloud_swarm': [('21_cloud_ride', 300, 500), ('22_cloud_somersault', 800, 500), ('23_pluck_hair', 1250, 600), ('24_seated_palm_open', 1680, 700)],
}
os.makedirs(V + 'singles', exist_ok=True)
lines = []
for sh, figs in SHEETS.items():
    img = cv2.imread(V + f'monkey_v4b_{sh}.jpg'); H, W = img.shape[:2]
    sm = cv2.GaussianBlur(img, (5, 5), 0).astype(np.float32)
    lum = sm.mean(axis=2)
    paper = np.median(sm[lum >= np.percentile(lum, 60)], axis=0)
    mark = (np.abs(sm - paper).max(axis=2) > 26).astype(np.uint8)
    mark = cv2.morphologyEx(mark, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    grow = cv2.dilate(mark, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(grow, 8)
    seeds = np.array([(x * K, y * K) for _, x, y in figs])
    owner = np.full(n, -1)
    for i in range(1, n):
        if st[i, 4] < 60:
            continue
        # owner = the seed nearest to any pixel of the component (sampled)
        ys, xs = np.where(lab[::4, ::4] == i)
        pts = np.stack([xs * 4, ys * 4], 1).astype(np.float32)
        d = np.sqrt(((pts[:, None, :] - seeds[None]) ** 2).sum(-1)).min(0)
        owner[i] = int(d.argmin())
    for k, (name, _, _) in enumerate(figs):
        m = np.isin(lab, np.where(owner == k)[0]) & (mark > 0)
        m = cv2.dilate(m.astype(np.uint8), np.ones((15, 15), np.uint8))
        m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3)
        ys, xs = np.where(m > 0.02)
        pad = 60
        y0, y1, x0, x1 = max(0, ys.min() - pad), min(H, ys.max() + pad), max(0, xs.min() - pad), min(W, xs.max() + pad)
        out = img[y0:y1, x0:x1].astype(np.float32) * m[y0:y1, x0:x1, None] + paper * (1 - m[y0:y1, x0:x1, None])
        p = V + f'singles/{name}.jpg'
        cv2.imwrite(p, out.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
        lines.append(f'{name}.jpg\tfrom monkey_v4b_{sh}.jpg\tbox {x0},{y0},{x1-x0},{y1-y0}')
open(V + 'singles/README.txt', 'w').write('Costume-B singles cut by tools/stage/cut4.py (ink components grouped to the nearest figure).\n'
    '05/07 and 25/27 both face screen LEFT (the model drew two left profiles): for a right profile mirror 05.\n'
    '02 is a 合十 prayer-hands pose: never use it as the martial salute 抱拳.\n' + '\n'.join(lines) + '\n')
print('\n'.join(lines))

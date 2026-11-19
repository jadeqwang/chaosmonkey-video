"""Cut design/world/cards/hgs_master into layer cards b3l_* (polygons in 1536x869 view coords of the 3072x1738 card)."""
import json, os, shutil, sys
import cv2, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = os.path.join(ROOT, 'design/world/cards')
PARTS = {
 'crown': [(228, 420), (250, 300), (300, 255), (345, 255), (392, 300), (408, 400), (400, 440), (300, 470), (230, 470)],
 'face': [(215, 470), (232, 380), (255, 310), (330, 280), (395, 310), (408, 400), (432, 470), (490, 520), (505, 600), (480, 700), (445, 825), (180, 835), (148, 780), (200, 700), (205, 560)],
 'lbut': [(112, 492), (122, 462), (150, 440), (190, 424), (226, 440), (226, 482), (236, 560), (206, 640), (185, 745), (150, 805), (40, 790), (70, 730), (110, 670), (148, 630), (158, 520)],
 'rbut': [(422, 495), (428, 452), (470, 428), (528, 442), (532, 470), (498, 484), (498, 585), (540, 582), (582, 640), (610, 690), (665, 785), (705, 800), (690, 830), (450, 830), (432, 700), (440, 560)],
 'fall': [(396, 515), (420, 510), (440, 600), (450, 700), (448, 812), (414, 818), (418, 700), (404, 600)],
 'foot': [(0, 738), (60, 772), (140, 800), (250, 832), (420, 822), (600, 800), (690, 785), (712, 800), (700, 845), (540, 869), (0, 869)],
}
# the back copy: whole plate minus the crown and the two ledge trees (they live only in their own layers: no double ink)
HOLES = [[(205, 200), (420, 200), (420, 428), (205, 428)], [(105, 405), (230, 405), (230, 487), (105, 487)], [(418, 405), (540, 405), (540, 487), (418, 487)]]
FEATHER = {'crown': 14, 'face': 8, 'lbut': 6, 'rbut': 6, 'fall': 3, 'foot': 14}
def main():
    rgba = np.array(Image.open(os.path.join(C, 'hgs_master_rgba.png')))
    H, W = rgba.shape[:2]
    meta = json.load(open(os.path.join(C, 'hgs_master.json')))
    s = W / 1536.0
    # remove the pale silhouette halo (paper-coloured pixels at partial alpha): it shows as a white contour when a layer slides over rock
    al = rgba[..., 3].astype(np.float32) / 255
    er = cv2.GaussianBlur(cv2.erode(rgba[..., 3], np.ones((3, 3), np.uint8), iterations=3).astype(np.float32) / 255, (0, 0), 1.5)
    al2 = np.clip((er - 0.35) / 0.5, 0, 1)
    keep = np.zeros(al.shape, np.float32)          # trees and the crown keep their fine alpha (needles, stone)
    for (x0, y0, x1, y1) in [(100, 0, 545, 492), (200, 240, 420, 430)]:
        keep[int(y0 * s):int(y1 * s), int(x0 * s):int(x1 * s)] = 1
    keep = cv2.GaussianBlur(keep, (0, 0), 8)
    al2 = al2 * (1 - keep) + keep
    rgba = rgba.copy(); rgba[..., 3] = (np.minimum(al, 1) * al2 * 255).astype(np.uint8)
    for n, poly in PARTS.items():
        m = np.zeros((H, W), np.uint8)
        cv2.fillPoly(m, [(np.array(poly) * s).astype(np.int32)], 255)
        f = FEATHER[n] * s
        m = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=3), (0, 0), f).astype(np.float32) / 255
        o = rgba.copy(); o[..., 3] = (o[..., 3] * m).astype(np.uint8)
        if n in ('lbut', 'rbut'):       # translucent near-paper pixels (the plate's haze) show as a white contour over the face
            lum = o[..., :3].astype(np.float32).mean(2) / 255
            a = o[..., 3].astype(np.float32) / 255
            kill = np.clip((lum - 0.68) / 0.10, 0, 1) * (a < 0.995) * (np.arange(a.shape[0])[:, None] > 440 * s)
            o[..., 3] = (a * (1 - kill) * 255).astype(np.uint8)
        Image.fromarray(o, 'RGBA').save(os.path.join(C, f'b3l_{n}_rgba.png'))
        shutil.copy(os.path.join(C, 'hgs_master_depth.png'), os.path.join(C, f'b3l_{n}_depth.png'))
        meta2 = dict(meta); meta2['src'] = 'hgs_master polygon cut: ' + n
        json.dump(meta2, open(os.path.join(C, f'b3l_{n}.json'), 'w'), indent=1)
    m = np.ones((H, W), np.float32)
    for poly in HOLES:
        h = np.zeros((H, W), np.uint8); cv2.fillPoly(h, [(np.array(poly) * s).astype(np.int32)], 255)
        m *= 1 - cv2.GaussianBlur(h, (0, 0), 10 * s).astype(np.float32) / 255
    o = rgba.copy(); o[..., 3] = (o[..., 3] * m).astype(np.uint8)
    Image.fromarray(o, 'RGBA').save(os.path.join(C, 'b3l_back_rgba.png'))
    shutil.copy(os.path.join(C, 'hgs_master_depth.png'), os.path.join(C, 'b3l_back_depth.png'))
    json.dump(dict(meta, src='hgs_master minus crown and ledge trees'), open(os.path.join(C, 'b3l_back.json'), 'w'), indent=1)
    print('ok')
main()

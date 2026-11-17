"""J4 heads: crop singing heads from the canon expression sheets (boxes in 1600-px preview coords of each sheet),
key them off their paper, and (Jade) transplant mouths from the face row onto one head. Writes work/stage/heads/*.npy
(transmittance) and a review sheet.   PY tools/stage/heads.py"""
import sys, os
import numpy as np
sys.path.insert(0, '.')
from tools.ink import load_image, save_image, key_paper, resize, contact_strip, blur

C = 'design/characters/'
SHEETS = {'mama': C + 'mama/mama_B_expressions.jpg', 'lj': C + 'little_jade/lj_C_expressions_mouths.jpg',
          'jade': C + 'jade/jade_B_expressions_details.jpg', 'dau': C + 'daughter/daughter_B_poses_mouths.jpg'}
# name: (sheet, (x0, y0, x1, y1) in 1600-wide preview px)
BOX = {
    'mama_open': ('mama', (172, 22, 378, 298)),
    'lj_shut': ('lj', (92, 92, 252, 312)),
    'lj_open': ('lj', (588, 478, 748, 698)),
    'lj_o': ('lj', (840, 478, 1000, 698)),
    'jade_shut': ('jade', (540, 36, 740, 312)),
    'dau_shut': ('dau', (996, 622, 1170, 795)),
    'dau_open': ('dau', (1172, 622, 1346, 795)),
    'dau_o': ('dau', (1342, 622, 1516, 795)),
}
# Jade's mouths come from the face row (same face, same glasses): donor mouth centre and face width (preview px),
# pasted onto jade_shut at its mouth centre / face width
JADE_MOUTH = {'open': (660, 607), 'o': (935, 607)}
DONOR_FACE_W, JADE_FACE_W, JADE_MOUTH_AT = 150, 112, (639, 236)

IMG = {}


def sheet(k):
    if k not in IMG:
        IMG[k] = load_image(SHEETS[k])
    return IMG[k]


def crop(k, box):
    im = sheet(k)
    sc = im.shape[1] / 1600
    x0, y0, x1, y1 = [int(v * sc) for v in box]
    return im[y0:y1, x0:x1].copy(), sc


def jade_mouth(kind):
    base, sc = crop('jade', BOX['jade_shut'][1])
    im = sheet('jade')
    mx, my = JADE_MOUTH[kind]
    r = 26                                              # half-size of the donor patch (preview px)
    don = im[int((my - r * 0.8) * sc):int((my + r * 0.8) * sc), int((mx - r) * sc):int((mx + r) * sc)]
    f = JADE_FACE_W / DONOR_FACE_W
    dh, dw = int(don.shape[0] * f), int(don.shape[1] * f)
    don = resize(don, dw, dh)
    # soft ellipse
    yy, xx = np.mgrid[0:dh, 0:dw]
    e = ((xx - dw / 2) / (dw / 2)) ** 2 + ((yy - dh / 2) / (dh / 2)) ** 2
    a = np.clip((1 - e) / 0.35, 0, 1)[..., None]
    cx = int((JADE_MOUTH_AT[0] - BOX['jade_shut'][1][0]) * sc)
    cy = int((JADE_MOUTH_AT[1] - BOX['jade_shut'][1][1]) * sc)
    y0, x0 = cy - dh // 2, cx - dw // 2
    reg = base[y0:y0 + dh, x0:x0 + dw]
    base[y0:y0 + dh, x0:x0 + dw] = reg * (1 - a) + don * a
    return base


def transplant(base_name, sheet_k, donor_c, r, f, at, ry=0.8):
    """Paste a mouth from elsewhere on the same sheet (centre donor_c, half-size r, scale f) onto a cropped head
    at preview point `at`."""
    k, box = BOX[base_name]
    base, sc = crop(k, box)
    im = sheet(sheet_k)
    mx, my = donor_c
    don = im[int((my - r * ry) * sc):int((my + r * ry) * sc), int((mx - r) * sc):int((mx + r) * sc)]
    dh, dw = int(don.shape[0] * f), int(don.shape[1] * f)
    don = resize(don, dw, dh)
    yy, xx = np.mgrid[0:dh, 0:dw]
    e = ((xx - dw / 2) / (dw / 2)) ** 2 + ((yy - dh / 2) / (dh / 2)) ** 2
    a = np.clip((1 - e) / 0.4, 0, 1)[..., None]
    cx, cy = int((at[0] - box[0]) * sc), int((at[1] - box[1]) * sc)
    y0, x0 = cy - dh // 2, cx - dw // 2
    base[y0:y0 + dh, x0:x0 + dw] = base[y0:y0 + dh, x0:x0 + dw] * (1 - a) + don * a
    return base


def main():
    os.makedirs('work/stage/heads', exist_ok=True)
    out = {}
    for name, (k, box) in BOX.items():
        out[name] = crop(k, box)[0]
    out['jade_open'] = transplant('jade_shut', 'jade', (660, 610), 24, 0.95, (637, 241), 0.8)
    out['jade_o'] = transplant('jade_shut', 'jade', (936, 612), 17, 1.0, (637, 241), 0.95)
    out['mama_shut'] = transplant('mama_open', 'mama', (624, 223), 25, 0.8, (277, 223), 0.5)
    prev = []
    for name, img in out.items():
        T = key_paper(img, lo=0.03).astype(np.float32)
        np.save(f'work/stage/heads/{name}.npy', T)
        prev.append(resize(T, int(T.shape[1] * 360 / T.shape[0]), 360))
    w = max(p.shape[1] for p in prev)
    prev = [np.pad(p, ((0, 0), (0, w - p.shape[1]), (0, 0)), constant_values=1) for p in prev]
    save_image(sys.argv[1] if len(sys.argv) > 1 else 'work/stage/heads/_sheet.jpg', contact_strip(prev, 6))
    print(list(out))


if __name__ == '__main__':
    main()

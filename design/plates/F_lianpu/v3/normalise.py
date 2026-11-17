"""FACES v3: normalise picked candidates into faces_v3/<ID>.png (+ _mask.png) and write F_faces_v3.json.
The face (cap to chin) is scaled to exactly 1120 px tall, centred on a 1400 sheet (as v1 plates).
Usage: PY design/plates/F_lianpu/v3/normalise.py   (reads picks.json: id -> take letter)"""
import json, sys
import cv2, numpy as np
D = 'design/plates/F_lianpu/v3'
SPEC = json.load(open(f'{D}/faces_v3.json'))
PICKS = json.load(open(f'{D}/picks.json'))
import os
os.makedirs(f'{D}/faces', exist_ok=True)
out = {}
FLIP = {'XIAHOUDUN'}          # the arrow wound is under HIS left eye (viewer's right)
for fid, take in PICKS.items():
    im = cv2.imread(f'{D}/_cand/{fid}_{take}.png').astype(np.float32) / 255
    if fid in FLIP:
        im = im[:, ::-1].copy()
    h, w = im.shape[:2]
    border = np.concatenate([im[:40].reshape(-1, 3), im[-40:].reshape(-1, 3), im[:, :40].reshape(-1, 3), im[:, -40:].reshape(-1, 3)])
    paper = np.median(border, axis=0)
    lowp = cv2.GaussianBlur(im, (0, 0), 60)                       # the sheet's slow tone
    d = np.abs(im - lowp).max(axis=2) + 0.0
    d2 = np.abs(im - paper[None, None]).max(axis=2)
    mk = ((np.minimum(d, d2) > 0.07) | (d2 > 0.16)).astype(np.uint8)
    mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    # fill: everything not connected to the border through non-mark pixels
    ff = (1 - mk).copy()
    ffm = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, ffm, (2, 2), 2)
    sil = (ff != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(sil)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    sil = (lab == i).astype(np.uint8)
    sil = cv2.morphologyEx(sil, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    x, y, bw, bh = cv2.boundingRect(sil)
    k = 1120.0 / bh
    M = np.float32([[k, 0, 700 - (x + bw / 2) * k], [0, k, 140 - y * k]])
    o = cv2.warpAffine(im, M, (1400, 1400), flags=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    m = cv2.warpAffine(sil.astype(np.float32), M, (1400, 1400), flags=cv2.INTER_LINEAR)
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    m = np.clip((m - 0.35) / 0.3, 0, 1)
    cv2.imwrite(f'{D}/faces/{fid}.png', np.clip(o * 255 + .5, 0, 255).astype(np.uint8))
    cv2.imwrite(f'{D}/faces/{fid}_mask.png', (m * 255).astype(np.uint8))
    ys, xs = np.where(m > 0.5)
    fill = sil.sum() / (bw * bh)
    out[fid] = dict(name=SPEC[fid]['name'], file=f'v3/faces/{fid}.png', mask=f'v3/faces/{fid}_mask.png', size=[1400, 1400],
                    face_box_xywh=[int(xs.min()), int(ys.min()), int(xs.max() - xs.min()), int(ys.max() - ys.min())], take=take)
    print(fid, 'bbox', (x, y, bw, bh), 'k %.3f' % k, 'fill %.2f' % fill, 'OK' if 0.6 < fill < 0.85 and bh > 700 else 'CHECK')
json.dump({'faces': out}, open(f'{D}/../F_faces_v3.json', 'w'), indent=1, ensure_ascii=False)

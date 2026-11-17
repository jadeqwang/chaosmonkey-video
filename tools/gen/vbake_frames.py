#!/usr/bin/env python3
"""First/last frames for the video bake-off (docs/VIDEO_BAKEOFF.md), written to media/vbake/_frames/.

    $PY tools/gen/vbake_frames.py

- blank_sd5.jpg      : media/look/L3/sd5_v2.jpg with the monkey erased (bare paper of the same sheet) -> V3 first frame
- pose2.jpg, pose3.jpg, pose5.jpg, pose6.jpg : one pose of media/look/L3/nbp_pose_v1.jpg, centred on that sheet's own
                       paper with the other five figures erased -> Kling first+last tests (V2d)
Erasing = every marked pixel (and a margin) is replaced by paper copied from a shifted copy of the same sheet where
that copy is bare, feathered; so paper grain and tone are the sheet's own.
"""
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "media", "vbake", "_frames")


def marks(img, thr=12, grow=31):
    g = cv2.GaussianBlur(img, (0, 0), 2).astype(np.float32)
    paper = np.median(g[g.sum(2) > np.percentile(g.sum(2), 60)], axis=0)
    d = np.abs(g - paper).max(2)
    m = (d > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow))) > 0


def erase(img, mask, shifts=None):
    H, W = mask.shape
    shifts = shifts or [(dx, dy) for dx in (-900, 900, -1300, 1300, -600, 600, -1700, 1700, -2100, 2100)
                        for dy in (0, -300, 300)]
    out = img.copy()
    todo = mask.copy()
    for dx, dy in shifts:
        if not todo.any():
            break
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        src = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        srcm = cv2.warpAffine(mask.astype(np.uint8), M, (W, H), borderValue=1) > 0
        ok = todo & ~srcm
        out[ok] = src[ok]
        todo &= ~ok
    if todo.any():
        out = cv2.inpaint(out, todo.astype(np.uint8), 15, cv2.INPAINT_TELEA)
    a = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 6)[..., None]
    return (out * a + img * (1 - a)).astype(np.uint8)


def main():
    os.makedirs(OUT, exist_ok=True)
    sd5 = cv2.imread(os.path.join(ROOT, "media/look/L3/sd5_v2.jpg"))
    cv2.imwrite(os.path.join(OUT, "blank_sd5.jpg"), erase(sd5, marks(sd5)), [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(os.path.join(OUT, "monkey_sd5.jpg"), sd5, [cv2.IMWRITE_JPEG_QUALITY, 95])

    sheet = cv2.imread(os.path.join(ROOT, "media/look/L3/nbp_pose_v1.jpg"))
    H, W = sheet.shape[:2]
    m = marks(sheet, grow=41)
    blank = erase(sheet, m, [(dx, dy) for dx in (-160, 160, -800, 800, -330, 330) for dy in (0, -770, 770, -400, 400)])
    cv2.imwrite(os.path.join(OUT, "pose_blank.jpg"), blank, [cv2.IMWRITE_JPEG_QUALITY, 95])
    cols = [(262, 895), (1054, 1713), (1807, 2563)]
    rows = [(72, 765), (797, 1434)]
    n = 0
    for (y0, y1) in rows:
        for (x0, x1) in cols:
            n += 1
            pad = 40
            xa, xb, ya, yb = max(0, x0 - pad), min(W, x1 + pad), max(0, y0 - pad), min(H, y1 + pad)
            cell = sheet[ya:yb, xa:xb].astype(np.float32)
            cm = m[ya:yb, xa:xb].astype(np.float32)
            a = cv2.GaussianBlur(cm, (0, 0), 10)[..., None]
            a = np.clip(a * 1.5, 0, 1)
            canvas = blank.astype(np.float32).copy()
            h, w = cell.shape[:2]
            cx, cy = W // 2 - w // 2, H // 2 - h // 2 + 60
            region = canvas[cy:cy + h, cx:cx + w]
            canvas[cy:cy + h, cx:cx + w] = cell * a + region * (1 - a)
            cv2.imwrite(os.path.join(OUT, f"pose{n}.jpg"), canvas.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
    print("wrote", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()

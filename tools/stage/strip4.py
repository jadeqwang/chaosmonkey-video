"""Consecutive frames of a clip, cropped to the union ink box: PY tools/stage/strip4.py CLIP F0 F1 OUT.jpg [cols=8]"""
import sys, av, cv2, numpy as np
p, f0, f1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 8
with av.open(p) as c:
    fr = [f.to_ndarray(format='rgb24') for i, f in enumerate(c.decode(video=0)) if f0 <= i <= f1]
g = np.stack([cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in fr]).min(0).astype(np.float32)
bg = np.median(g[:30]); ys, xs = np.where(bg - g > 40)
H, W = g.shape
x0, x1 = max(0, xs.min() - 20), min(W, xs.max() + 20); y0, y1 = max(0, ys.min() - 20), min(H, ys.max() + 20)
tiles = []
for k, f in enumerate(fr):
    t = cv2.resize(f[y0:y1, x0:x1], (int((x1 - x0) * 360 / (y1 - y0)), 360), interpolation=cv2.INTER_AREA).copy()
    cv2.putText(t, f'f{f0 + k}', (4, 16), 0, 0.5, (200, 30, 30), 1)
    tiles.append(t)
while len(tiles) % cols: tiles.append(np.full_like(tiles[0], 255))
s = np.concatenate([np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)], 0)
if s.shape[1] > 2400: s = cv2.resize(s, (2400, int(s.shape[0] * 2400 / s.shape[1])))
cv2.imwrite(out, s[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])

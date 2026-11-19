"""Every k-th frame of a clip between F0 and F1, cropped to the union ink box.
    PY tools/stage/strip4b.py CLIP F0 F1 STEP OUT.jpg [cols=10] [h=300]"""
import sys, av, cv2, numpy as np
p, f0, f1, st, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 10
hh = int(sys.argv[7]) if len(sys.argv) > 7 else 300
with av.open(p) as c:
    fr = [(i, f.to_ndarray(format='rgb24')) for i, f in enumerate(c.decode(video=0)) if f0 <= i <= f1 and (i - f0) % st == 0]
g = np.stack([cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for _, f in fr]).min(0).astype(np.float32)
bg = np.median(g[:30]); ys, xs = np.where(bg - g > 40)
H, W = g.shape
x0, x1 = max(0, xs.min() - 20), min(W, xs.max() + 20); y0, y1 = max(0, ys.min() - 20), min(H, ys.max() + 20)
tiles = []
for i, f in fr:
    t = cv2.resize(f[y0:y1, x0:x1], (max(1, int((x1 - x0) * hh / (y1 - y0))), hh), interpolation=cv2.INTER_AREA).copy()
    cv2.putText(t, f'f{i}', (4, 16), 0, 0.5, (200, 30, 30), 1)
    tiles.append(t)
while len(tiles) % cols: tiles.append(np.full_like(tiles[0], 255))
s = np.concatenate([np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)], 0)
if s.shape[1] > 2400: s = cv2.resize(s, (2400, int(s.shape[0] * 2400 / s.shape[1])))
cv2.imwrite(out, s[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])

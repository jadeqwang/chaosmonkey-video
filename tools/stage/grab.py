"""Frames of a comp side by side: PY tools/stage/grab.py media/comp/D1.mp4 OUT.jpg i j k ... (frame indices in the clip)"""
import sys, av, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
idx = [int(x) for x in sys.argv[3:]]
with av.open(src) as c:
    fr = [f.to_ndarray(format='rgb24') for f in c.decode(video=0)]
tiles = [cv2.resize(fr[min(i, len(fr) - 1)], (700, 394), interpolation=cv2.INTER_AREA) for i in idx]
cols = 2 if len(tiles) > 1 else 1
while len(tiles) % cols:
    tiles.append(np.zeros_like(tiles[0]))
sheet = np.concatenate([np.concatenate(tiles[r:r + cols], axis=1) for r in range(0, len(tiles), cols)], axis=0)
cv2.imwrite(out, sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 85])

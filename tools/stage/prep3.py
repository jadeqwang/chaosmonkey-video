"""Prepare v3 stage clips (key onto our paper) into work/ink_clips/s3_<name>/ and print a motion/ink profile.
    PY tools/stage/prep3.py TAG [height] [lo]     e.g. s3_d1_sd20b 720"""
import sys
sys.path.insert(0, '.')
import numpy as np
from tools.ink.video import Clip
tag = sys.argv[1]
height = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
lo = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
c = Clip.prepare(f'media/gen/stage/v3/clips/{tag}.mp4', out=f'work/ink_clips/{tag}', ground='light', height=height, lo=lo)
print(tag, c.n, c.w, c.h, c.fps, c.meta.get('stab_lost'))
prev = None
rows = []
for i in range(c.n):
    d = c.density(i)
    ys, xs = np.where(d > 0.15)
    box = (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else (0, 0, 0, 0)
    mot = float(np.abs(d - prev).mean() * 1000) if prev is not None else 0
    prev = d
    rows.append((i, float(d.mean() * 1000), mot) + box)
for r in rows[::2]:
    print('f%3d ink %6.1f mot %6.2f box %4d %4d %4d %4d' % r)

"""Per-frame profile of a keyed store: top/bottom/left/right of the dense ink, centroid, change vs previous frame.
    PY tools/stage/prof3.py TAG [step]"""
import sys
sys.path.insert(0, '.')
import numpy as np
from tools.ink.video import Clip
c = Clip('work/ink_clips/' + sys.argv[1]); step = int(sys.argv[2]) if len(sys.argv) > 2 else 2
prev = None
for i in range(0, c.n):
    d = 1 - np.clip(c.frame(i), 0, 1).min(axis=2)
    ys, xs = np.where(d > 0.35)
    ch = float(np.abs(d - prev).mean() * 1000) if prev is not None else 0
    prev = d
    if i % step == 0 and len(xs):
        print('f%3d top %4d bot %4d left %4d right %4d cx %4d cy %4d area %6d chg %5.1f' % (i, ys.min(), ys.max(), xs.min(), xs.max(), xs.mean(), ys.mean(), len(xs), ch))

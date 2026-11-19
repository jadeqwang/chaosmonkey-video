"""Key a v4 stage clip onto our paper -> work/ink_clips/<tag>/ (Clip store) and print a short motion profile.
    PY tools/stage/prep4.py TAG [height=1080] [lo=0.03]"""
import sys
sys.path.insert(0, '.')
import numpy as np
from tools.ink.video import Clip
tag = sys.argv[1]
height = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
lo = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
c = Clip.prepare(f'media/gen/stage/v4/clips/{tag}.mp4', out=f'work/ink_clips/{tag}', ground='light', height=height, lo=lo)
print(tag, c.n, c.w, c.h, c.fps, c.meta.get('stab_lost'))

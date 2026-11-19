"""PY clipkey.py NAME VIDEO [fps]: video (green) -> media/swarm4/clips/NAME/f%04d.png (RGBA, shared crop) + clip.json"""
import sys, os, json, subprocess, glob
sys.path.insert(0, 'tools/swarm4')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from key import key
name, vid = sys.argv[1:3]
d = f'media/swarm4/clips/{name}'; tmp = f'work/swarm/fr/{name}'
os.makedirs(d, exist_ok=True); os.makedirs(tmp, exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, f'{tmp}/%04d.png'], check=True)
fs = sorted(glob.glob(tmp + '/*.png')); R = []
for f in fs:
    R.append(key(np.array(Image.open(f).convert('RGB')), mode='sat'))
A = np.stack([r[..., 3] for r in R]) > 40
# remove stray specks that are not hair-like: components < 6 px
ys, xs = np.where(A.any(0)); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
bots, cxs = [], []
for a in A:
    lab, n = ndi.label(a)
    if n == 0: continue
    sz = ndi.sum(a, lab, range(1, n + 1)); big = lab == (1 + int(np.argmax(sz)))
    yy, xx = np.where(big); b = yy.max(); bots.append(b)
    low = yy > b - 0.06 * (b - yy.min()); cxs.append((xx[low].min() + xx[low].max()) / 2)
by, bx = int(np.median(bots)), int(np.median(cxs))
for i, r in enumerate(R):
    Image.fromarray(r[y0:y1, x0:x1], 'RGBA').save(f'{d}/f{i:04d}.png')
json.dump(dict(fps=24, frames=len(R), anchor_px=[bx - int(x0), by - int(y0)], w=int(x1 - x0), h=int(y1 - y0), crop_in_source=[int(x0), int(y0), int(x1), int(y1)], source_size=[1920, 1080], source=vid), open(d + '/clip.json', 'w'))
print(name, len(R), d, x1 - x0, y1 - y0, (bx - x0, by - y0))

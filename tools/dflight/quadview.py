#!/usr/bin/env python
"""quadview.py CFG [s,s,...]: draw the tracked panel quad on the base frames -> work/dflight/<name>/quad_<s>.jpg + a montage (to pick key corners)."""
import glob, json, os, sys
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
cfg = json.load(open(sys.argv[1])); n = cfg['name']
ss = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(range(0, 70, 6))
base = sorted(glob.glob(f'work/dflight/{n}/base_960x540_*'), key=os.path.getmtime)[-1]
Q = json.load(open(sorted(glob.glob(f'work/dflight/{n}/track_*.json'), key=os.path.getmtime)[-1]))
keys = {k['s'] for k in cfg['panel']['keys']}
tiles = []
for s in ss:
    im = cv2.imread(f'{base}/b{s:04d}.png')
    q = np.array(Q['quads'][s])
    cv2.polylines(im, [np.round(q).astype(np.int32)], True, (0, 255, 0) if s in keys else (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(im, f's{s} {Q["mode"][s]}', (6, 16), 0, 0.5, (0, 255, 255), 1)
    cv2.imwrite(f'work/dflight/{n}/quad_{s:03d}.jpg', im)
    tiles.append(cv2.resize(im, (640, 360)))
while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(f'work/dflight/{n}/quads.jpg', np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]))

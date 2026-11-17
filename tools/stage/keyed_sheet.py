"""Sheet of a keyed store on white: PY tools/stage/keyed_sheet.py TAG [n]"""
import sys
sys.path.insert(0, '.')
import numpy as np, cv2
from tools.ink.video import Clip
tag = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
c = Clip('work/ink_clips/' + tag)
idx = np.linspace(0, c.n - 1, n).round().astype(int)
tiles = []
for i in idx:
    im = (np.clip(c.frame(i), 0, 1) * 255).astype(np.uint8)
    im = cv2.resize(im, (280, 158), interpolation=cv2.INTER_AREA).copy()
    cv2.putText(im, str(i), (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 30, 30), 1)
    tiles.append(im)
sheet = np.concatenate([np.concatenate(tiles[r:r + 5], axis=1) for r in range(0, n, 5)], axis=0)
cv2.imwrite(f'work/stage/v3/tmp/keyed_{tag}.jpg', sheet[..., ::-1])

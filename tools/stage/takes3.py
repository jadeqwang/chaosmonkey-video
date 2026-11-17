"""Copy finished s3_* clips to media/gen/stage/v3/clips/ and write a 15-frame sheet per take
(work/stage/v3/takes/<tag>.jpg, 1400 px wide).  PY tools/stage/takes3.py"""
import glob, os, shutil, sys
import av, cv2, numpy as np
os.makedirs('media/gen/stage/v3/clips', exist_ok=True)
os.makedirs('work/stage/v3/takes', exist_ok=True)
for p in sorted(glob.glob('media/gen/s3_*.mp4')):
    tag = os.path.basename(p).rsplit('_', 1)[0]
    dst = f'media/gen/stage/v3/clips/{tag}.mp4'
    if not os.path.exists(dst):
        shutil.copy(p, dst)
    out = f'work/stage/v3/takes/{tag}.jpg'
    if os.path.exists(out):
        continue
    with av.open(dst) as c:
        fr = [f.to_ndarray(format='rgb24') for f in c.decode(video=0)]
    idx = np.linspace(0, len(fr) - 1, 15).round().astype(int)
    tiles = []
    for i in idx:
        im = cv2.resize(fr[i], (280, 158), interpolation=cv2.INTER_AREA).copy()
        cv2.putText(im, f'{i}', (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 30, 30), 1, cv2.LINE_AA)
        tiles.append(im)
    sheet = np.concatenate([np.concatenate(tiles[r * 5:r * 5 + 5], axis=1) for r in range(3)], axis=0)
    cv2.imwrite(out, sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(tag, len(fr), fr[0].shape)

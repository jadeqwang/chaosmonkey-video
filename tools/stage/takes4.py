"""Copy finished s4_* clips to media/gen/stage/v4/clips/ and write per take a 16-frame sheet
(work/stage/v4/takes/<tag>.jpg) and a zoom strip (work/stage/v4/takes/<tag>_zoom.jpg: 8 frames cropped to the
figure's ink box, for hands and face).  PY tools/stage/takes4.py [--force] [--anon]
--anon also writes copies named by a neutral letter (work/stage/v4/blind/) for blind ranking."""
import glob, os, shutil, sys, json
import av, cv2, numpy as np
os.makedirs('media/gen/stage/v4/clips', exist_ok=True)
os.makedirs('work/stage/v4/takes', exist_ok=True)


def frames(p):
    with av.open(p) as c:
        return [f.to_ndarray(format='rgb24') for f in c.decode(video=0)]


def label(im, s):
    cv2.rectangle(im, (0, 0), (8 + 9 * len(s), 18), (255, 255, 255), -1)
    cv2.putText(im, s, (3, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 30, 30), 1, cv2.LINE_AA)


def ink_box(fr):
    g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY).astype(np.float32)
    bg = np.median(g[:40])
    m = (bg - g > 40).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ys, xs = np.where(m > 0)
    if len(xs) < 50:
        return None
    x0, x1 = np.percentile(xs, [0.5, 99.5]); y0, y1 = np.percentile(ys, [0.5, 99.5])
    return int(x0), int(y0), int(x1), int(y1)


def sheets(src, out_base, name):
    fr = frames(src)
    n = len(fr)
    idx = np.linspace(0, n - 1, 16).round().astype(int)
    tiles = []
    for i in idx:
        im = cv2.resize(fr[i], (480, 270), interpolation=cv2.INTER_AREA).copy()
        label(im, f'{name} f{i}')
        tiles.append(im)
    sheet = np.concatenate([np.concatenate(tiles[r * 4:r * 4 + 4], axis=1) for r in range(4)], axis=0)
    cv2.imwrite(out_base + '.jpg', sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
    zt = []
    for i in np.linspace(0, n - 1, 8).round().astype(int):
        b = ink_box(fr[i])
        H, W = fr[i].shape[:2]
        if b is None:
            b = (0, 0, W, H)
        x0, y0, x1, y1 = b
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        h = max(y1 - y0, (x1 - x0) * 0.75) * 1.08
        w = h / 0.75
        X0, Y0 = int(max(0, cx - w / 2)), int(max(0, cy - h / 2))
        crop = fr[i][Y0:int(min(H, cy + h / 2)), X0:int(min(W, cx + w / 2))]
        im = cv2.resize(crop, (480, 640) if crop.shape[0] > crop.shape[1] else (640, 480), interpolation=cv2.INTER_AREA)
        im = cv2.resize(crop, (int(crop.shape[1] * 600 / crop.shape[0]), 600), interpolation=cv2.INTER_AREA).copy()
        label(im, f'{name} f{i}')
        zt.append(im)
    hmax = 600
    row1 = np.concatenate(zt[:4], axis=1); row2 = np.concatenate(zt[4:], axis=1)
    wmax = max(row1.shape[1], row2.shape[1])
    pad = lambda r: np.concatenate([r, np.full((hmax, wmax - r.shape[1], 3), 255, np.uint8)], axis=1)
    z = np.concatenate([pad(row1), pad(row2)], axis=0)
    if z.shape[1] > 2400:
        z = cv2.resize(z, (2400, int(z.shape[0] * 2400 / z.shape[1])), interpolation=cv2.INTER_AREA)
    cv2.imwrite(out_base + '_zoom.jpg', z[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
    return n, fr[0].shape


for p in sorted(glob.glob('media/gen/s4_*.mp4')):
    tag = os.path.basename(p).rsplit('_', 1)[0]
    dst = f'media/gen/stage/v4/clips/{tag}.mp4'
    if not os.path.exists(dst):
        shutil.copy(p, dst)
    out = f'work/stage/v4/takes/{tag}'
    if os.path.exists(out + '.jpg') and '--force' not in sys.argv:
        continue
    n, sh = sheets(dst, out, tag)
    print(tag, n, sh)
if '--anon' in sys.argv:
    os.makedirs('work/stage/v4/blind', exist_ok=True)
    key = {}
    rs = np.random.RandomState(7)
    by = {}
    for p in sorted(glob.glob('media/gen/stage/v4/clips/s4_*.mp4')):
        tag = os.path.basename(p)[:-4]; shot = tag.split('_')[1]
        by.setdefault(shot, []).append(tag)
    for shot, tags in by.items():
        order = list(rs.permutation(len(tags)))
        for k, j in enumerate(order):
            L = chr(65 + k); t = tags[j]
            key[f'{shot}_{L}'] = t
            sheets(f'media/gen/stage/v4/clips/{t}.mp4', f'work/stage/v4/blind/{shot}_{L}', f'{shot} take {L}')
    json.dump(key, open('work/stage/v4/tmp/blind_key.json', 'w'), indent=1)
    print('blind', len(key))

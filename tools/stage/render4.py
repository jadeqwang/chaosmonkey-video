"""v4 render (16-frame sheet): a stage shot at its exact frame count (docs/shots.json), then a 12-frame review sheet in
work/review/comp_v4/<ID>.jpg and a <=1400 px copy in work/stage/v4/tmp/sheet_<ID>.jpg.
    PY tools/stage/render3.py F4b [--size 960x540] [--jobs 8] [--out path]"""
import json, subprocess, sys, os
sys.path.insert(0, '.')
sid = sys.argv[1]
size = sys.argv[sys.argv.index('--size') + 1] if '--size' in sys.argv else '960x540'
SH = {s['id']: s for s in json.load(open('docs/shots.json'))['shots']}
SH['F4b'] = dict(in_frame=2744, out_frame=2789, frames=45)      # sub-shots (splice ranges, LOG_faces)
SH['F6a'] = dict(in_frame=2832, out_frame=2895, frames=63)
sh = SH[sid]
t0, t1 = sh['in_frame'] / 24 - 1e-6, sh['out_frame'] / 24 - 1e-6
out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else (
    f'media/comp/{sid}.mp4' if size == '960x540' else f'work/stage/v4/{sid}_{size}.mp4')
cmd = [sys.executable, '-m', 'tools.ink.run', f'shots/{sid}.py', '--t0', f'{t0:.6f}', '--t1', f'{t1:.6f}', '--size', size,
       '--out', out, '--fresh']
if '--jobs' in sys.argv:
    cmd += ['--jobs', sys.argv[sys.argv.index('--jobs') + 1]]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    print('RENDER FAILED', r.stderr[-1500:]); sys.exit(1)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '', r.stderr[-1500:] if r.returncode else '')
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip())
print(f'{sid}: {n} frames, expected {sh["frames"]}', 'OK' if n == sh['frames'] else 'MISMATCH')
import av, numpy as np, cv2
with av.open(out) as c:
    fr = [f.to_ndarray(format='rgb24') for f in c.decode(video=0)]
idx = np.linspace(0, len(fr) - 1, 16).round().astype(int)
tiles = []
for i in idx:
    im = cv2.resize(fr[i], (640, 360), interpolation=cv2.INTER_AREA).copy()
    cv2.rectangle(im, (0, 0), (150, 22), (20, 20, 20), -1)
    cv2.putText(im, f'f{sh["in_frame"] + int(i)} {(sh["in_frame"] + int(i)) / 24:.2f}', (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 235, 120), 1, cv2.LINE_AA)
    tiles.append(im)
sheet = np.concatenate([np.concatenate(tiles[r * 4:r * 4 + 4], axis=1) for r in range(4)], axis=0)
os.makedirs('work/review/comp_v4', exist_ok=True)
if size == '960x540' and '--out' not in sys.argv:
    cv2.imwrite(f'work/review/comp_v4/{sid}.jpg', sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
sm = cv2.resize(sheet, (1400, int(sheet.shape[0] * 1400 / sheet.shape[1])), interpolation=cv2.INTER_AREA)
cv2.imwrite(f'work/stage/v4/tmp/sheet_{sid}.jpg', sm[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
print('sheet', f'work/review/comp_v4/{sid}.jpg')

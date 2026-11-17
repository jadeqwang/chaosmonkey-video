"""Render a stage shot at its exact frame count from docs/shots.json, then write the 8-frame review sheet.
    PY tools/stage/render.py D1 [--size 960x540] [--jobs 12]"""
import json, subprocess, sys
sys.path.insert(0, '.')
sid = sys.argv[1]
size = sys.argv[sys.argv.index('--size') + 1] if '--size' in sys.argv else '960x540'
sh = {s['id']: s for s in json.load(open('docs/shots.json'))['shots']}[sid]
t0, t1 = sh['in_frame'] / 24 - 1e-6, sh['out_frame'] / 24 - 1e-6
out = f'media/comp/{sid}.mp4' if size == '960x540' else f'work/stage/{sid}_{size}.mp4'
cmd = [sys.executable, '-m', 'tools.ink.run', f'shots/{sid}.py', '--t0', f'{t0:.6f}', '--t1', f'{t1:.6f}', '--size', size,
       '--out', out]
cmd += ['--fresh']   # tools/stage/*.py is not in the runner's cache key
if '--jobs' in sys.argv:
    cmd += ['--jobs', sys.argv[sys.argv.index('--jobs') + 1]]
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-2000:])
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip())
print(f'{sid}: {n} frames, expected {sh["frames"]}', 'OK' if n == sh['frames'] else 'MISMATCH')
if size == '960x540':
    from tools.ink import save_image, contact_strip
    import av, numpy as np
    frames = []
    with av.open(out) as c:
        fr = [f.to_ndarray(format='rgb24') for f in c.decode(video=0)]
    idx = np.linspace(0, len(fr) - 1, 8).round().astype(int)
    from tools.ink import save_image, contact_strip
    sheet = contact_strip([fr[i].astype(np.float32) / 255 for i in idx], 4)
    import os
    os.makedirs('work/review/comp', exist_ok=True)
    save_image(f'work/review/comp/{sid}.jpg', sheet)
    print('sheet', f'work/review/comp/{sid}.jpg', 'frames', [sh['in_frame'] + int(i) for i in idx])

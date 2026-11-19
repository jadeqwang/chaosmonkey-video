"""16 evenly spaced frames of a swarm4 render, labelled with s and song time.
   python tools/swarm4/sheet.py work/swarm/render/A work/review/comp_v4/swarm_A.jpg [--n 16] [--cols 4] [--w 480] [--frames 0,40,80]
"""
import argparse, glob, os, re
from PIL import Image, ImageDraw, ImageFont

T0, FPS = 112.75, 24.0
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--n', type=int, default=16); ap.add_argument('--cols', type=int, default=4); ap.add_argument('--w', type=int, default=480)
ap.add_argument('--frames', default=None); ap.add_argument('--prefix', default='f')
a = ap.parse_args()
files = {int(re.search(r'(\d+)\.png$', f).group(1)): f for f in glob.glob(os.path.join(a.src, a.prefix + '[0-9]*.png'))}
if not files: raise SystemExit('no frames in ' + a.src)
keys = sorted(files)
if a.frames:
    pick = [int(x) for x in a.frames.split(',') if int(x) in files]
else:
    n = min(a.n, len(keys))
    pick = [keys[round(i * (len(keys) - 1) / max(1, n - 1))] for i in range(n)]
im0 = Image.open(files[pick[0]]); w = a.w; h = round(im0.height * w / im0.width)
rows = (len(pick) + a.cols - 1) // a.cols
sheet = Image.new('RGB', (a.cols * w + (a.cols + 1) * 4, rows * (h + 22) + 4), (18, 18, 20))
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 14)
except Exception: font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i, s in enumerate(pick):
    x = 4 + (i % a.cols) * (w + 4); y = 4 + (i // a.cols) * (h + 22)
    sheet.paste(Image.open(files[s]).convert('RGB').resize((w, h), Image.LANCZOS), (x, y + 18))
    t = T0 + s / FPS
    d.text((x + 2, y + 1), f's{s:03d}  t={t:7.3f}  ({int(t // 60)}:{t % 60:06.3f})', fill=(230, 220, 200), font=font)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
sheet.save(a.out, quality=88)
print(a.out, len(pick), 'frames')

"""Finish rendered frames of a world scratch dir into a sheet: python tools/world/peek.py work/world/X OUT.jpg [f,f,..] [--bloom 1]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.world.scene import World, paper_grain, sheet
d, out = sys.argv[1], sys.argv[2]
fs = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
bloom = float(sys.argv[sys.argv.index('--bloom') + 1]) if '--bloom' in sys.argv else 1.0
Wd = World('_peek', 1, work=d); Wd.out = os.path.join(d, 'frames')
if fs is None:
    fs = sorted(int(f[:4]) for f in os.listdir(os.path.join(Wd.out, 'beauty')))
G = paper_grain(1920, 1080)
ims = {f: Wd.finish_frame(f, grain=G, bloom=bloom) for f in fs}
sheet(lambda f: ims[f], out, idx=fs, cols=4 if len(fs) > 6 else len(fs), width=640 if len(fs) <= 12 else 480)
print(out)

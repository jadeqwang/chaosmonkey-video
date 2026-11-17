"""Demo 2: multiplane camera. Push into a page of synthetic brush mountains with mist bands, travel right to left,
pull back. Run:  python -m tools.ink.run tools/ink/demos/d02_camera.py --out work/ink_demo/d02_camera.mp4"""
import cv2
import numpy as np

from tools.ink import *

T0, T1 = 0.0, 12.0
CW, CH = 4400, 2000


def ridge(seed, base, amp, cell, density, paper, rough=1.0):
    """A synthetic ink mountain range: a noise skyline, dark at the crest and washed out downward (so its foot is mist)."""
    n = fbm(1, CW, cell, seed, 'ridge', octaves=5, gain=0.55)[0]
    sky = base - amp * (n - 0.3) * 2
    yy = np.arange(CH, dtype=np.float32)[:, None]
    below = yy - sky[None, :]
    m = smoothstep(0, 3, below) * smoothstep(amp * 2.2, amp * 0.2, below)
    tex = fbm(CH, CW, 90, seed, 'tex', octaves=5, gain=0.6)
    strokes = smoothstep(0.42, 0.62, tex + 0.25 * smoothstep(amp * 0.9, 0, below))
    d = wash(m * (0.35 + 0.65 * strokes * rough), paper.height, seed, density, bleed=5, edge=0.4)
    crest = np.exp(-(below / 7.0) ** 2) * (below > 0) * (0.6 + 0.8 * value_noise(CH, CW, 50, seed, 'crest'))
    return ink_T(d + crest * density * 0.8)


def setup(ctx):
    global SC, CAM
    paper = Paper(CW, CH, 'new', seed=11, breathe=0.5)
    SC = Scene(CW, CH, paper)
    SC.add(ridge(1, 760, 150, 900, 0.16, paper, 0.4), depth=4.0, name='far')
    SC.mist(780, 1000, depth=3.4, drift=-9, seed=1)
    SC.add(ridge(2, 1000, 230, 700, 0.38, paper, 0.8), depth=2.4, name='mid')
    SC.mist(1100, 1380, depth=1.8, drift=-16, seed=2)
    SC.add(ridge(3, 1420, 330, 520, 0.85, paper), depth=1.0, occlude=True, name='near')
    CAM = Camera([(0.0, 2200, 1000, 0.44), (4.0, 3300, 1250, 1.0, 'inout'), (9.0, 1100, 1250, 1.0, 'sine'),
                  (12.0, 2200, 1000, 0.44, 'inout')])


def render(t, ctx):
    return SC.render(t, CAM, ctx.size)

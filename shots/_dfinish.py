"""shots/_dfinish.py: finish the rendered D flight (shots/_dflight.py) into D4 / D5 / D6 comps. WORLD v4.

Per frame: the 3D render + glow bloom, the screen-fixed book paper, a faint dusk wash from the top (D5 -> D6), the
static inscription of the shot (D4 一通百通, D5 一窍通时/百窍通; D6 none), and in D6 the monkey element (STAGE) if present.
    $PY shots/_dfinish.py D4 D5 D6 [--full]       # --full: 1920x1080 master instead of 960x540
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import World, paper_grain, encode, sheet, ROOT  # noqa: E402
from tools.ink.inscription import inscription  # noqa: E402
from tools.ink.paper import Paper  # noqa: E402

RANGES = {'D4': (0, 33), 'D5': (33, 134), 'D6': (134, 204)}
INS = {'D4': dict(text='一通百通'), 'D5': dict(key='D5'), 'D6': None}
SRC = os.environ.get('DF_SRC', 'work/world/Dflight')


def dusk(h, w, k):
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    return 1 - k * (1 - y) ** 1.5 * np.array([0.20, 0.25, 0.30], np.float32)


def frames(shot, monkey=None):
    a, b = RANGES[shot]
    Wd = World('_fin', 1, work=os.path.join(ROOT, SRC)); Wd.out = os.path.join(ROOT, SRC, 'frames')
    G = paper_grain(1920, 1080)
    P = Paper(1920, 1080, 'new', seed=1988)
    ins = None
    if INS[shot]:
        ins = inscription((1920, 1080), INS[shot].get('key'), box=(1650, 110, 210, 720), paper=P, text=INS[shot].get('text'))
    for f in range(a, b):
        img = Wd.finish_frame(f, grain=G, bloom=1.6, glow_gain=1.2)
        k = float(np.clip((f - 60) / 74, 0, 1))
        img = img * dusk(1080, 1920, k)
        if monkey is not None:
            img = monkey(img, f)
        if ins is not None:
            ins.draw(img)
        yield np.clip(img, 0, 1)


def run(shot, full=False):
    n = RANGES[shot][1] - RANGES[shot][0]
    tk = os.environ.get('DF_TAKE', 'a')
    out = (f'media/comp/{shot}.mp4' if tk == 'a' else f'work/world/_cand/{shot}_{tk}.mp4') if not full else f'media/comp/full/{shot}.mp4'
    mk = None
    try:
        from shots._dmonkey import monkey_layer
        mk = monkey_layer(os.path.join(SRC, 'scene.json')) if shot == 'D6' else None
    except Exception as e:  # noqa: BLE001
        print('no monkey layer:', e)
    ims = list(frames(shot, mk))
    encode(iter(ims), out, n, w=1920 if full else 960, h=1080 if full else 540)
    sheet(ims, f'work/review/comp_v4/{shot}.jpg' if tk == 'a' else f'work/review/comp_v4/_cand/{shot}_{tk}.jpg', label=shot)
    print(shot, n, '->', out)


if __name__ == '__main__':
    full = '--full' in sys.argv
    for s in [a for a in sys.argv[1:] if not a.startswith('--')]:
        run(s, full)

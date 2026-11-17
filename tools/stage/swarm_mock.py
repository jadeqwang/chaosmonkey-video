"""Swarm option stills (B: full-frame ruled leaf). PY tools/stage/swarm_mock.py -> work/stage/v3/swarm_B.png"""
import sys, types
sys.path.insert(0, '.')
import numpy as np
from tools.ink import *
from shots.swarm_lib import *

def ctx_of(W, H):
    c = types.SimpleNamespace(W=W, H=H, s=W / 1920, size=(W, H))
    c.cache = lambda key, fn, deps=None: fn()
    return c

def leaf_still(W=1920, H=1080, steps=(0,) * 9, light_t=0.35, rig=None):
    ctx = ctx_of(W, H)
    rig = rig or load_rig()
    P = Paper(W, H, 'aged', seed=61)
    L = Leaf(ctx, rig, P)
    f = P.frame(0)
    L.draw(f, list(steps))
    return np.clip(f * street_light(W, H, ctx.s, light_t, 0, 1), 0, 0.985), L

if __name__ == '__main__':
    f, L = leaf_still(steps=(0, 1, 2, 3, 0, 1, 2, 3, 0))
    save_image('work/stage/v3/swarm_B.png', f)
    save_image('work/stage/v3/tmp/swarm_B_540.jpg', resize(f, 960, 540))

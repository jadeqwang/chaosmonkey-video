"""F5 (116.208-118.000): '说完这句话 各自消散'. Four puppet copies on the rear glass (left side window, the rear
window twice, right side window), each lit by its own passing streetlight; the lights pass and each copy goes dark
with its light, one per measured beat, until the glass is empty dusk. Light travels from above (0.27, 0.96), as in
the keyframe.

Beats used (analysis/timing.json): 116.320, 116.736, 117.200, 117.628 (one copy dark on each); empty glass
117.628-118.000. Each lamp has been crossing its pane since before the cut (its sweep started 1.1-1.5 s earlier), so
the copies are at different points of their light. Room plate: media/kf/F5.jpg (fallback F5_lit.png).
"""
from tools.ink import *
from shots.puppet_lib import *

T0, T1 = 2789 / 24, 2832 / 24
BEATS = [116.32, 116.736, 117.2, 117.628]
DIR = (0.27, 0.96)
PANES = {
    'right': [(1693, 253), (1920, 250), (1920, 590), (1720, 560)],
    'rear':  [(540, 250), (1593, 250), (1560, 402), (553, 402)],
    'left':  [(0, 240), (190, 247), (200, 580), (0, 600)],
}
# (pane, x as share of the pane width, pose, flip, beat it goes dark on, sweep start offset)
COPIES = [('right', 0.52, 'guard', True, 0, 1.15),
          ('rear', 0.86, 'strike', True, 1, 1.40),
          ('rear', 0.56, 'shade', False, 2, 1.25),
          ('left', 0.50, 'crouch', False, 3, 1.50)]


def setup(ctx):
    global PLATE, PN, PUP, INS
    PLATE, _ = room_plate('F5', ctx.W, ctx.H)
    PN = {k: Pane(ctx, PLATE, q, lw=900) for k, q in PANES.items()}
    rig = ctx.cache('puppet_rig_v1', build_rig, deps=[f'{MK}/puppet_parts_colour.jpg', f'{MK}/puppet_heads_swap.jpg'])
    PUP = make_puppet(rig)
    INS = lyric(ctx, '说完这句话 各自消散', (1305, 470, 70, 440), max_px=42)


def render(t, ctx):
    f = PLATE.copy()
    for name, pane in PN.items():
        T = None
        L = None
        lxy = None
        for pn, xs, pose, flip, bi, off in COPIES:
            if pn != name:
                continue
            t_off = BEATS[bi]
            sw = sweep(t, t_off - off, t_off, pane.lw, pane.lh, DIR, radius_k=1.6, travel=0.6)
            if not sw:
                continue
            lx, ly, inten, rad = sw
            Li = pane.light(lx, ly, rad, inten)
            h = min(pane.lh * 0.80, pane.lw * 0.9)
            Ti = puppet_local(PUP, P[pose], pane, (pane.lw * xs, pane.lh * 0.45), h, flip=flip)
            # this copy is lit only by its own lamp: mix where its lamp dominates
            T = Ti if T is None else T * Ti
            L = Li if L is None else np.maximum(L, Li)
            lxy = (lx, ly)
        if T is not None:
            pane.lay(f, T, L, lift=0.03, light_xy=lxy)
    if INS is not None:
        INS.draw(f, t)
    return f

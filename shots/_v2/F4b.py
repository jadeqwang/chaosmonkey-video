"""F4b (114.333-116.208; F4 = F4a + F4b, split at frame 2744 = 114.333 s, the onset of '每一个都是我' at 114.32):
'每一个都是我 每一个都算'. Every side pane carries its own shadow-puppet copy, each lit by its own passing
streetlight (out of phase), and across the windscreen a 走马灯: a ring of running monkeys turning on a drum, seen as
a band of shadows sliding across the glass (cylinder projection: fast in the middle, crowding at the edges; the
far side of the ring shows faint and reversed). The ring is built from the rig's 8-pose run cycle; on every
measured beat each figure re-poses one step of the cycle (hard, no in-betweens).

Deviation: the brief puts the band on the rear window, which is behind the camera in F4b (only its reflection in
the mirror is visible, ~120 px wide), so the band runs across the windscreen.
Beats used: 114.567, 115.002, 115.445, 115.882 (run-cycle steps; side-pane lamps re-pose their copies on them).
Room plate: media/kf/F4b.jpg (fallback F4b_lit.png); light from the upper left (0.47, 0.88) as painted.
"""
import math

from tools.ink import *
from tools.ink.puppet import lantern_strip
from shots.puppet_lib import *

T0, T1 = 2744 / 24, 2789 / 24
BEATS = [114.567, 115.002, 115.445, 115.882]
DIR = (0.47, 0.88)
SIDE = {
    'left_rear':   [(0, 200), (160, 213), (193, 627), (0, 720)],
    'left_front':  [(273, 251), (400, 264), (387, 627), (267, 653)],
    'right_front': [(1533, 287), (1733, 253), (1780, 547), (1547, 533)],
}
WIND = [(520, 253), (1493, 253), (1400, 571), (747, 571)]
def _rrect(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


MIRROR = _rrect(921, 265, 1088, 318, 18)
STEM = [(988, 238), (1012, 238), (1012, 266), (988, 266)]
# side copies: pane -> (sweeps [(t_on, t_off)], poses per beat, flip)
SWEEPS = {'left_rear': [(114.10, 115.00), (115.05, 116.00)],
          'left_front': [(114.40, 115.40), (115.45, 116.40)],
          'right_front': [(113.90, 114.75), (114.80, 115.85), (115.90, 116.60)]}
SIDE_POSES = {'left_rear': ['guard', 'strike', 'leap', 'shade', 'salute'],
              'left_front': ['shade', 'crouch', 'guard', 'strike', 'leap'],
              'right_front': ['strike', 'leap', 'salute', 'guard', 'crouch']}
RPM = 16.0


def setup(ctx):
    global PLATE, PN, WP, PUP, STRIPS, INS, UMAP
    PLATE, _ = room_plate('F4b', ctx.W, ctx.H)
    PN = {k: Pane(ctx, PLATE, q, lw=500) for k, q in SIDE.items()}
    WP = Pane(ctx, PLATE, WIND, exclude=[MIRROR, STEM], lw=1000)
    rig = ctx.cache('puppet_rig_v1', build_rig, deps=[f'{MK}/puppet_parts_colour.jpg', f'{MK}/puppet_heads_swap.jpg'])
    PUP = make_puppet(rig)
    run = run_poses(8)
    band_h = int(WP.lh * 0.62)
    tile = (int(band_h * 0.95), band_h)
    figs = [PUP.render(p, pos=(tile[0] * 0.5, band_h * 0.42), scale=band_h * 0.80 / 1450.0, size=tile) for p in run]
    # strip k: figure i shows run pose (i + k) % 8 -> every beat each runner steps one pose on
    STRIPS = [lantern_strip([figs[(i + k) % 8] for i in range(8)], gap=0.45) for k in range(8)]
    # cylinder projection of the windscreen band
    r = WP.lw * 0.62
    xs = (np.arange(WP.lw, dtype=np.float32) - WP.lw / 2) / r
    th = np.arcsin(np.clip(xs, -0.999, 0.999))
    UMAP = th
    INS = lyric(ctx, ['每一个都是我', '每一个都算'], (1262, 18, 125, 228), max_px=34)


def band(t):
    sh, sw = STRIPS[0].shape[:2]
    k = cue_index(t, BEATS)
    strip = STRIPS[k % 8]
    rot = t * RPM / 60.0
    y0 = int(WP.lh * 0.30)
    T = np.ones((WP.lh, WP.lw, 3), np.float32)
    v = np.linspace(0, sh - 1, sh, dtype=np.float32)
    u = (((UMAP / (2 * math.pi) + rot) % 1.0) * sw).astype(np.float32)
    ub = ((((math.pi - UMAP) / (2 * math.pi)) + rot) % 1.0 * sw).astype(np.float32)
    mu, mv = np.meshgrid(u, v)
    mub, _ = np.meshgrid(ub, v)
    front = cv2.remap(strip, mu, mv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    back = blur(cv2.remap(strip, mub, mv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP), 3.0)
    T[y0:y0 + sh] = front * (1 - 0.25 * (1 - back))
    return T


def render(t, ctx):
    f = PLATE.copy()
    # the lantern band: one long lamp crossing the windscreen for the whole shot
    sw = sweep(t, T0 - 0.6, T1 + 0.6, WP.lw, WP.lh, DIR, radius_k=2.2, travel=0.5)
    if sw:
        lx, ly, inten, rad = sw
        WP.lay(f, band(t), WP.light(lx, ly, rad, inten), lift=0.02, light_xy=(lx, ly))
    k = cue_index(t, BEATS)
    for name, pane in PN.items():
        for i, (a, b) in enumerate(SWEEPS[name]):
            s2 = sweep(t, a, b, pane.lw, pane.lh, DIR, radius_k=1.8, travel=0.6)
            if s2:
                lx, ly, inten, rad = s2
                pose = P[SIDE_POSES[name][k % 5]]
                T = puppet_local(PUP, pose, pane, (pane.lw * 0.5, pane.lh * 0.42), pane.lh * 0.78,
                                 flip=name.startswith('right'))
                pane.lay(f, T, pane.light(lx, ly, rad, inten), lift=0.03, light_xy=(lx, ly))
    if INS is not None:
        INS.draw(f, t)
    return f

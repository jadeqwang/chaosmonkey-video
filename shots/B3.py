"""B3 'a stone looked over the sea' (26.125-29.292, 76 frames). WORLD v4 (REVISION_V4 §2: "a true dolly").

Frame 0 is the flat spread exactly as the attic's over-shoulder push ends (contract in LOG_v3_book.md, unchanged:
spread u 0.031..0.969, v 0.105..0.895 fills the frame): 花果山 lower left, sea and sky bare paper, far ridges on the
right page, the inscription upper right. But the picture on the page IS the 3D world (tools/world), seen from the
page camera: so when the push continues, the page's surface gives way: the page plane (gutter, inscription, its
paper) grows past the lens while the world behind it opens in depth (the lens widens 14 -> 48 degrees as we travel),
the pines and the near rocks at the mountain's foot pass under the lens, mist bands lie between them, and the peak
stands in depth above a sea of mist; we end close under the summit, the stone above us (B4 cuts in to the cliff).
    $PY shots/B3.py [--frames 0,40] [--take a] [--page]       # --page: (re)write media/comp/pages/B3_page.png
Page art for the room team: media/comp/pages/B3_page.png (3072x2048, unlit) = the same world rendered over the whole
spread + book paper + gutter + inscription, so B2's warp ends on exactly B3's frame 0.
"""
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.world.scene import World, smooth_path, fov_for, paper_grain, encode, sheet, ease, ROOT, PAPER_RGB  # noqa: E402

N = 76
SW, SH = 3072, 2048
SPW = 177.78 / 0.938                   # spread width in world units (frame 0 shows 177.78 x 100)
SPH = SPW / 1.5
FOV0 = 28.0
D1 = 50.0 / math.tan(math.radians(FOV0 / 2))          # page camera distance
PX = 60.0 / (1920.0 / (0.938 * SW))                  # inscription size on the spread (60 px at frame 0)


def page_xy(sx, sy):
    return (sx / SW - 0.5) * SPW, (0.5 - sy / SH) * SPH


def placed(Wd, name, rect, z, **kw):
    """Card whose painted rect (spread px x, y, w; bottom-anchored) lands at that place on the page as seen from the
    page camera, while standing at depth z."""
    x, y, w = rect
    m = __import__('tools.world.scene', fromlist=['card_meta']).card_meta(name)
    h = w / m['aspect']
    k = D1 / (D1 - z)
    X, Ybot = page_xy(x + w / 2, y + h)
    return Wd.card(name, [X / k, Ybot / k, z], width=(w / SW * SPW) / k, **kw)


def overlay_texture():
    """The page itself: gutter shadow + inscription on transparent paper (RGBA, the spread)."""
    from tools.ink.inscription import inscription
    from tools.ink.paper import Paper
    P = Paper(SW, SH, 'new', seed=1988)
    ink = np.ones((SH, SW, 3), np.float32)
    inscription((SW, SH), 'B3', (2560, 300, 330, 1100), px=PX, paper=P).draw(ink)
    a = 1 - ink.min(2)
    xx = np.abs(np.arange(SW, dtype=np.float32) - SW / 2) / 40
    g = 0.07 * np.exp(-(xx / 0.35) ** 2)
    g = np.broadcast_to(g[None, :], (SH, SW))
    rgba = np.zeros((SH, SW, 4), np.float32)
    gc = np.array([0.45, 0.38, 0.30], np.float32)
    A = a + g * (1 - a)
    rgba[..., :3] = (ink * a[..., None] + gc * g[..., None] * (1 - a[..., None])) / np.maximum(A, 1e-4)[..., None]
    rgba[..., 3] = A
    p = 'work/world/B3/page_overlay.png'
    os.makedirs(os.path.join(ROOT, 'work/world/B3'), exist_ok=True)
    Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, p))
    return p, P


def build(take='a'):
    if take.startswith('r2'):
        return build_r2(take)
    Wd = World('B3' + ('' if take == 'a' else '_' + take), N)
    Wd.fog(density=0.0010, start=200)
    sea_y = -64.0
    Wd.sea(y=sea_y, soft=6, amp=5, scale=0.03, drift=(0.6, 0.1))
    # far ridges on the right page, the peak, its spurs, the rocks and pines at its foot
    placed(Wd, 'C_ridge_02', (1250, 1040, 1700), -900, relief=6, id='ridge2', lum=1.0, ink=0.6)
    placed(Wd, 'C_ridge_01', (1900, 1150, 1300), -650, relief=6, id='ridge1', ink=0.55)
    pk = placed(Wd, 'hgs_master', (0, 150, 3072), -130, relief=40, bend=0.05, id='peak', seg=[384, 256])
    placed(Wd, 'hgs_shoulder_l_1', (-40, 820, 700), -210, relief=30, id='shl', ink=0.8)
    placed(Wd, 'hgs_shoulder_r_2', (860, 1180, 560), -95, relief=24, id='shr', ink=0.9)
    placed(Wd, 'hgs_ledge_near_1', (120, 1430, 900), -55, relief=14, id='ledge', ink=1.0)
    placed(Wd, 'C_pine_02', (150, 1260, 520), -42, relief=4, id='pine_a')
    placed(Wd, 'C_pine_04', (1235, 1455, 330), -70, relief=3, id='pine_b')
    placed(Wd, 'C_pine_03', (560, 1560, 430), -22, relief=3, id='pine_c')
    placed(Wd, 'C_pine_05', (880, 1640, 360), -12, relief=3, id='pine_d')
    placed(Wd, 'pine_near_1', (1040, 1380, 300), 30, relief=4, id='pine_near', ink=1.0)
    placed(Wd, 'hgs_ledge_near_2', (980, 1720, 520), 20, relief=6, id='ledge_r')
    # mist: a band across the peak's waist, sheets over the sea at its foot, wisps between foot rocks and peak
    for i, (y, z, w, op) in enumerate([(-12, -62, 420, 0.9), (-34, -45, 380, 0.9), (-50, -20, 300, 0.8), (6, -70, 260, 0.7), (-58, -75, 500, 0.95)]):
        Wd.mist([-60, y, z], [w, 26], band=True, opacity=op * 0.85, thresh=0.42, scale=0.05, soft=8, nearFade=8, wash=0.12, edge=0.8,
                speed=[0.9 * (-1) ** i, 0.0], seed=float(i))
    for i in range(4):
        Wd.mist([-40, sea_y + 3 + i * 3, -200], [700, 700], pitch=-90, opacity=0.6, thresh=0.48 + 0.03 * i, scale=0.012,
                soft=6, wash=0.12, speed=[0.8, 0.2], seed=20.0 + i, nearFade=10)
    ov, P = overlay_texture()
    Wd.plane(ov, [0, 0, 0], [SPW, SPH], id='page', fogk=0, seak=0, depthWrite=False, order=5)
    # camera: continue the push; the lens opens while we travel toward the summit, passing over the pines
    G = [pk['pos'][0], pk['pos'][1], pk['pos'][2]]
    top = Wd.card_point(pk, 0.165, 0.37)            # just under the summit stone (B_master: stone at ~u 0.2, v 0.2)
    end_p = [top[0] + 6, top[1] - 10, top[2] + 46]
    mid = np.array(top)
    keys = [(0, [0.0, 0.0, D1]), (16, [-14.0, -24.0, 70.0]), (34, [-34.0, -26.0, -10.0]), (54, [-36.0, -8.0, -50.0]), (N - 1, end_p)]
    P_ = smooth_path(keys, N)
    T_ = smooth_path([(0, [0.0, 0.0, 0.0]), (16, list(mid + np.array([6, -30, 0]))), (40, list(mid + np.array([0, -8, 0]))), (N - 1, list(mid + np.array([0, 6, 0])))], N)
    F_ = smooth_path([(0, FOV0), (30, 36), (N - 1, 42)], N)
    Wd.camera = [dict(p=list(P_[f]), t=list(T_[f]), fov=float(F_[f]), near=0.5, far=4000) for f in range(N)]
    return Wd, P


# ---------------------------------------------------------------- round 2 (R2_B3): layered peak, near boughs, far range, mist sea
K0 = D1 / (D1 + 130.0)


def layer(Wd, part, z, relief0=40.0, **kw):
    """One b3l_<part> layer of the hgs_master cut, placed so frame 0 projects as the single card did."""
    k = D1 / (D1 - z)
    return placed(Wd, 'b3l_' + part, (0, 150, 3072), z, relief=relief0 * K0 / k, bend=0.05, id='L_' + part, seg=[384, 256], **kw)


def fade(f0, f1, a=1.0):
    return [[0, dict(opacity=0.0)], [f0, dict(opacity=0.0)], [f1, dict(opacity=a)]]


def r2_near(Wd, take):
    """Things that pass the lens: they enter from the frame edge after frame 6 (opacity ramp while still far and veiled)."""
    if take == 'r2c':
        # fully opaque, placed outside the frustum of frames 0-14 (checked with _dmonkey.project): they enter from the left edge as the camera travels
        Wd.card('hgs_shoulder_l_2', [-176, -80, -80], height=95, relief=16, id='sh_pass', ink=0.95)
        Wd.card('pine_bough_1', [-178, -20, -60], width=70, relief=3, anchor='center', id='bough_l')
        Wd.card('b4g_pine_near_1', [-172, -80, -70], height=60, relief=4, yaw=10, id='bough_r')
    elif take == 'r2a':
        Wd.card('pine_bough_1', [-52, -8, 10], width=46, relief=3, yaw=0, anchor='center', id='bough_l', keys=fade(8, 22), visible=[8, N])
        Wd.card('b4g_pine_near_1', [-6, -66, -22], height=58, relief=4, yaw=-10, id='bough_r', keys=fade(10, 22), visible=[10, N])
        Wd.card('hgs_shoulder_l_2', [-88, -75, -30], height=95, relief=16, id='sh_pass', ink=0.95, keys=fade(8, 24), visible=[8, N])
    else:
        Wd.card('pine_bough_2', [26, 6, 2], width=40, relief=3, yaw=180, anchor='center', id='bough_l', keys=fade(8, 22), visible=[8, N])
        Wd.card('C_pine_01', [-64, -66, -24], height=75, relief=3, yaw=8, id='pine_l', keys=fade(8, 22), visible=[8, N])
        Wd.card('hgs_ledge_near_2', [12, -70, -34], width=70, relief=10, id='sh_pass', keys=fade(10, 24), visible=[10, N])
        Wd.card('pine_near_1', [22, -60, -30], height=50, relief=4, yaw=-14, id='bough_r', keys=fade(10, 22), visible=[10, N])


def r2_mist(Wd, take):
    """Mist between the ranges that parts as we rise: bands slide apart and thin f18-56."""
    for i, (y, z, w, x0) in enumerate([(-8, -300, 700, -60), (-30, -520, 900, 60), (-52, -160, 500, -50), (-18, -80, 260, -60)]):
        d = 150 if i % 2 == 0 else -150
        Wd.mist([x0, y, z], [w, 30], band=True, opacity=0.0, thresh=0.42, scale=0.04, soft=8, nearFade=8, wash=0.12, edge=0.8,
                speed=[0.6, 0.0], seed=40.0 + i,
                keys=[[0, dict(opacity=0.0, pos=[x0, y, z])], [14, dict(opacity=0.8, pos=[x0, y, z])], [56, dict(opacity=0.0, pos=[x0 + d, y + 12, z])]])


def r2_clouds(Wd, take):
    """The sea of mist: painted cloud banks lie below the peak and open (slide apart, sink) as the camera rises."""
    if take == 'r2c':
        import random
        rnd = random.Random(7)
        names = ['cloud_bank_1', 'cloud_bank_2', 'cloud_head_1', 'cloud_head_2']
        for i in range(14):
            nm = names[i % 4]; z = -50 - 38 * i - rnd.uniform(0, 30)
            w = 70 + 8 * (i % 3) + 0.2 * (-z) if 'bank' in nm else 40 + 0.08 * (-z)
            x = -70 + 150 * ((i * 0.618) % 1) + (-z) * 0.15 * (1 if i % 2 else -1)
            h = w / (2.4 if 'bank' in nm else 1.78)
            yf = -54                     # final base (sunk partly in the sea)
            y0 = -66 - h - 8                           # start: wholly below the cloud sea surface (dissolved, invisible at f0)
            d = (1 if i % 2 else -1) * 0.25 * w
            Wd.card(nm, [x, y0, z], width=w, relief=0, billboard=True, ink=0.8, id=f'cl{i}', fogk=0.5,
                    keys=[[0, dict(pos=[x, y0, z])], [10, dict(pos=[x, y0, z])], [40, dict(pos=[x, yf + 6, z])], [75, dict(pos=[x + d, yf - 4, z])]])
        return
    spec = [('cloud_bank_1', -40, -58, -120, 200, 1), ('cloud_bank_2', 70, -60, -260, 300, -1), ('cloud_bank_1', -170, -58, -380, 360, -1),
            ('cloud_bank_2', 190, -56, -480, 420, 1), ('cloud_head_1', -75, -62, -90, 70, -1), ('cloud_head_2', 60, -62, -170, 90, 1)]
    for i, (nm, x, y, z, w, d) in enumerate(spec):
        Wd.card(nm, [x, y, z], width=w, relief=0, billboard=True, ink=0.8, id=f'cl{i}', seak=0, fogk=0.5,
                keys=[[0, dict(opacity=0.0, pos=[x, y, z])], [16, dict(opacity=0.0, pos=[x, y + 4, z])], [30, dict(opacity=0.9, pos=[x, y + 8, z])],
                      [75, dict(opacity=0.9, pos=[x + d * 0.35 * w, y - 12, z])]])


def r2c_far(Wd):
    """Far ranges and a cloud-sea horizon placed from the END camera so they stand behind and below the summit in the last frames.
    They rise out of the sea with the camera (pos keys), invisible (below the cloud sea) at frame 0."""
    sys.path.insert(0, os.path.join(ROOT, 'shots'))
    from _dmonkey import project
    cam = Wd.camera[N - 1]
    th = math.tan(math.radians(cam['fov']) / 2)
    def put(nm, sx, z, top_sy, ink, i, aspect, fogk=1.0):
        dist = cam['p'][2] - z
        x = cam['p'][0] + (sx - 960) / 540.0 * th * dist
        lo, hi = 5.0, 900.0
        for _ in range(40):                       # height whose top projects to screen row top_sy at the last frame
            h = (lo + hi) / 2
            sy = project(cam, [x, -52 + h, z])[1]
            lo, hi = (h, hi) if sy > top_sy else (lo, h)
        h = (lo + hi) / 2
        y_end, y0 = -52.0, -66.0 - h - 6
        Wd.card(nm, [x, y0, z], height=h, relief=3, id=i, ink=ink, fogk=fogk,
                keys=[[0, dict(pos=[x, y0, z])], [14, dict(pos=[x, y0, z])], [52, dict(pos=[x, y_end, z])]])
    put('range_far_1', 330, -1900, 520, 0.85, 'rf1', 2.4)
    put('range_far_2', 1700, -1500, 560, 0.9, 'rf2', 2.4)
    put('range_mid_1', 200, -950, 640, 0.95, 'rm1', 2.4)
    put('range_far_2', 120, -1300, 600, 0.9, 'rf3', 2.4)
    put('cloud_bank_2', 260, -700, 760, 0.7, 'hz1', 2.4, 0.6)
    put('cloud_bank_1', 1750, -640, 800, 0.7, 'hz2', 2.4, 0.6)


def build_r2(take):
    Wd = World('B3_' + take, N)
    Wd.fog(density=0.0010, start=200)
    sea_y = -64.0
    Wd.sea(y=sea_y, soft=6, amp=5, scale=0.03, drift=(0.6, 0.1))
    A = take in ('r2a', 'r2c')
    C = take == 'r2c'
    # far country: the page's two ridges stay; more ranges stand behind them and come up out of the mist as we rise
    placed(Wd, 'C_ridge_02', (1250, 1040, 1700), -900, relief=6, id='ridge2', lum=1.0, ink=0.6)
    placed(Wd, 'C_ridge_01', (1900, 1150, 1300), -650, relief=6, id='ridge1', ink=0.55)
    fr = [[0, dict(opacity=0.0)], [20, dict(opacity=0.0)], [50, dict(opacity=1.0)]]
    for nm, x, z, h, ink, i in ([] if C else [('range_far_1', 150, -2000, 300, 0.45, 'rf1'), ('range_far_2', -500, -1500, 230, 0.5, 'rf2'),
                                ('range_mid_1', 380, -1000, 150, 0.6, 'rm1'), ('range_far_2', 700, -1800, 260, 0.42, 'rf3')]):
        Wd.card(nm, [x, -52, z], height=h, relief=4, id=i, ink=ink, keys=fr)
    # the peak, cut in layers (back to front); the back copy is the whole plate (infill behind the cuts)
    sp = 1.0 if A else 0.55          # r2b: gentler separation between the peak's layers
    zz = lambda z: -130 + (z + 130) * sp
    layer(Wd, 'back', zz(-200), ink=0.88)
    pk = layer(Wd, 'face', zz(-130))
    layer(Wd, 'fall', zz(-128.5))
    layer(Wd, 'crown', zz(-128))
    layer(Wd, 'lbut', zz(-104))
    layer(Wd, 'rbut', zz(-108 if C else -90))
    placed(Wd, 'hgs_shoulder_l_1', (-40, 820, 700), -210, relief=30, id='shl', ink=0.8)
    placed(Wd, 'hgs_shoulder_r_2', (860, 1180, 560), -95, relief=24, id='shr', ink=0.9)
    layer(Wd, 'foot', zz(-70))
    placed(Wd, 'hgs_ledge_near_1', (120, 1430, 900), -55, relief=14, id='ledge', ink=1.0)
    placed(Wd, 'C_pine_02', (150, 1260, 520), -42, relief=4, id='pine_a')
    placed(Wd, 'C_pine_04', (1235, 1455, 330), -70, relief=3, id='pine_b')
    placed(Wd, 'C_pine_03', (560, 1560, 430), -22, relief=3, id='pine_c')
    placed(Wd, 'C_pine_05', (880, 1640, 360), -12, relief=3, id='pine_d')
    placed(Wd, 'pine_near_1', (1040, 1380, 300), 30, relief=4, id='pine_near', ink=1.0)
    placed(Wd, 'hgs_ledge_near_2', (980, 1720, 520), 20, relief=6, id='ledge_r')
    for i, (y, z, w, op) in enumerate([(-12, -62, 420, 0.9), (-34, -45, 380, 0.9), (-50, -20, 300, 0.8), (6, -70, 260, 0.7), (-58, -75, 500, 0.95)]):
        Wd.mist([-60, y, z], [w, 26], band=True, opacity=op * 0.85, thresh=0.42, scale=0.05, soft=8, nearFade=8, wash=0.12, edge=0.8,
                speed=[0.9 * (-1) ** i, 0.0], seed=float(i))
    for i in range(4):
        Wd.mist([-40, sea_y + 3 + i * 3, -200], [700, 700], pitch=-90, opacity=0.6, thresh=0.48 + 0.03 * i, scale=0.012,
                soft=6, wash=0.12, speed=[0.8, 0.2], seed=20.0 + i, nearFade=10)
    r2_near(Wd, take)
    r2_mist(Wd, take)
    r2_clouds(Wd, take)
    ov, P = overlay_texture()
    Wd.plane(ov, [0, 0, 0], [SPW, SPH], id='page', fogk=0, seak=0, depthWrite=False, order=5, typeset=True)
    top = Wd.card_point(pk, 0.165, 0.37)
    end_p = [top[0] + 6, top[1] - 10, top[2] + 46]
    mid = np.array(top)
    if A:
        keys = [(0, [0.0, 0.0, D1]), (16, [-14.0, -24.0, 70.0]), (34, [-34.0, -26.0, -10.0]), (54, [-36.0, -8.0, -50.0]), (N - 1, end_p)]
        T_ = smooth_path([(0, [0.0, 0.0, 0.0]), (16, list(mid + np.array([6, -30, 0]))), (40, list(mid + np.array([0, -8, 0]))), (N - 1, list(mid + np.array([0, 6, 0])))], N)
    else:       # r2b: swing out to the right of the mountain, rise along its flank, end under the stone from the right
        end_b = [top[0] + 20, top[1] - 16, top[2] + 44]
        keys = [(0, [0.0, 0.0, D1]), (16, [-2.0, -20.0, 72.0]), (34, [-12.0, -34.0, 0.0]), (54, [0.0, -22.0, -44.0]), (N - 1, end_b)]
        T_ = smooth_path([(0, [0.0, 0.0, 0.0]), (16, list(mid + np.array([2, -34, 0]))), (40, list(mid + np.array([-3, -14, 0]))), (N - 1, list(mid + np.array([-3, 4, 0])))], N)
    P_ = smooth_path(keys, N)
    F_ = smooth_path([(0, FOV0), (30, 36), (N - 1, 42)], N)
    if C:
        for f in range(N):
            P_[f][0] += 14.0 * ease(min(1, max(0, (f - 48) / 27)), 'inout')        # slight lateral drift: the summit passes the far range
    Wd.camera = [dict(p=list(P_[f]), t=list(T_[f]), fov=float(F_[f]), near=0.5, far=4000) for f in range(N)]
    if C:
        r2c_far(Wd)
    return Wd, P


def page_quad(cam, W=1920, H=1080):
    """Screen corners of the page plane (TL, TR, BR, BL) for a camera dict, or None if behind."""
    sys.path.insert(0, os.path.join(ROOT, 'shots'))
    from _dmonkey import project
    pts = [(-SPW / 2, SPH / 2, 0), (SPW / 2, SPH / 2, 0), (SPW / 2, -SPH / 2, 0), (-SPW / 2, -SPH / 2, 0)]
    if cam['p'][2] <= 1.0:
        return None
    return np.array([project(cam, p, W, H) for p in pts], np.float32)


def finish(Wd, P, take='a'):
    Gs = paper_grain(1920, 1080)
    Gp = (P.rgb.astype(np.float32) / np.array(PAPER_RGB, np.float32))       # the book's paper, fixed to the page
    src = np.array([[0, 0], [SW, 0], [SW, SH], [0, SH]], np.float32)
    ims = []
    for f in range(N):
        k = 1 - ease(min(1, max(0, (f - 4) / 16)), 'inout')                 # page grain -> screen grain as the page goes
        g = Gs
        if k > 0:
            q = page_quad(Wd.camera[f])
            Gw = cv2.warpPerspective(Gp, cv2.getPerspectiveTransform(src, q), (1920, 1080), flags=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_REPLICATE)
            g = Gw * k + Gs * (1 - k)
        img = Wd.finish_frame(f, grain=g, bloom=0)
        ims.append(np.clip(img, 0, 1))
    out = 'media/comp/B3.mp4' if take == 'a' else f'work/world/_cand/B3_{take}.mp4'
    encode(iter(ims), out, N)
    sheet(ims, 'work/review/comp_v4/B3.jpg' if take == 'a' else f'work/review/comp_v4/_cand/B3_{take}.jpg', label='B3')
    return ims


def write_page(Wd, P):
    """media/comp/pages/B3_page.png: the world over the whole spread + book paper + gutter + inscription."""
    import json
    c = dict(Wd.camera[0]); c['fov'] = 2 * math.degrees(math.atan(SPH / 2 / D1))
    S = json.loads(json.dumps(Wd.S, default=lambda x: None)); S['camera'] = [c]
    S['cards'] = [o for o in S['cards'] if o.get('id') != 'page']
    for o in S['cards']:
        o.pop('_D', None)
    p = os.path.join(Wd.dir, 'page_scene.json'); json.dump(S, open(p, 'w'))
    import subprocess
    subprocess.run(['node', 'tools/world/render.mjs', '--scene', os.path.relpath(p, ROOT), '--out', os.path.relpath(os.path.join(Wd.dir, 'page'), ROOT),
                    '--w', str(SW), '--h', str(SH), '--ss', '1', '--frames', '0'], check=True, cwd=ROOT)
    r = cv2.cvtColor(cv2.imread(os.path.join(Wd.dir, 'page/beauty/0000.png')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    art = P.rgb.astype(np.float32) * (r / np.array(PAPER_RGB, np.float32))
    ov = np.array(Image.open(os.path.join(ROOT, 'work/world/B3/page_overlay.png'))).astype(np.float32) / 255
    art = art * (1 - ov[..., 3:]) + ov[..., :3] * P.rgb.astype(np.float32) * ov[..., 3:]
    Image.fromarray((np.clip(art, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(ROOT, 'media/comp/pages/B3_page.png'))
    print('wrote media/comp/pages/B3_page.png')


if __name__ == '__main__':
    fs = sys.argv[sys.argv.index('--frames') + 1] if '--frames' in sys.argv else None
    take = sys.argv[sys.argv.index('--take') + 1] if '--take' in sys.argv else 'a'
    Wd, P = build(take)
    if '--page' in sys.argv:
        write_page(Wd, P)
    Wd.render(ss=2, frames=fs, passes=['beauty'])
    if fs is None:
        finish(Wd, P, take)

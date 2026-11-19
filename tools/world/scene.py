"""tools/world/scene.py: build a 3D painted-world scene in Python, render it headless, finish it as ink on paper.

    from tools.world.scene import World, card_meta, smooth_path, dolly_zoom
    Wd = World('B3', frames=76)                     # work/world/B3/
    Wd.fog(density=0.012, start=20); Wd.sea(y=0, soft=3, amp=2, scale=0.04)
    Wd.card('hgs_peak', pos=[0, 0, -40], height=30, relief=6)          # design/world/cards/hgs_peak_{rgba,depth}.png
    Wd.mist(pos=[0, 8, -30], size=[80, 20], pitch=-90, opacity=0.8)     # horizontal sheet of paper-coloured vapour
    Wd.overlay_text(...)  /  Wd.thread(pts, f0, ...)  /  Wd.camera = [dict(p=.., t=.., fov=..), ...] (one per frame)
    Wd.render(ss=2)                                   # -> work/world/B3/frames/beauty/0000.png ...
    frames = Wd.finish(grain=True, bloom=True)        # paper grain fixed to the screen, glow pass bloomed in
    Wd.encode('media/comp/B3.mp4', frames)           # 960x540 (or --full 1920x1080), 24 fps, exact count

World units are metres-ish; the camera dicts take p (position), t (target), fov (vertical degrees), optional up, roll,
near, far, ortho (vertical extent, for a true orthographic frame). See README.md for the material model.
"""
import json
import math
import os
import subprocess

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CARDS = 'design/world/cards'
PAPER_RGB = (0.925, 0.886, 0.800)
FFMPEG = 'ffmpeg'


def card_meta(name, cards=CARDS):
    return json.load(open(os.path.join(ROOT, cards, name + '.json')))


def load_depth(path):
    a = np.array(Image.open(os.path.join(ROOT, path)).convert('RGB')).astype(np.float32)
    return (a[..., 0] * 256 + a[..., 1]) / 65535


def rot_yxz(yaw, pitch, roll=0.0):
    """Rotation matching three.js Euler(pitch, yaw, roll, 'YXZ') (degrees)."""
    y, x, z = map(math.radians, (yaw, pitch, roll))
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    Rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def smooth_path(keys, n, kind='catmull'):
    """keys: [(frame, value(s)), ...] -> n samples. 'catmull' = centripetal-ish Catmull-Rom through the keys with
    eased time between keys; 'linear'. Values may be scalars or sequences."""
    ks = sorted(keys, key=lambda k: k[0])
    F = np.array([k[0] for k in ks], float)
    V = np.array([np.atleast_1d(k[1]).astype(float) for k in ks])
    out = []
    for f in range(n):
        if f <= F[0]:
            out.append(V[0]); continue
        if f >= F[-1]:
            out.append(V[-1]); continue
        i = int(np.searchsorted(F, f) - 1)
        u = (f - F[i]) / (F[i + 1] - F[i])
        if kind == 'linear' or len(ks) < 3:
            out.append(V[i] + (V[i + 1] - V[i]) * u); continue
        p0 = V[max(i - 1, 0)]; p1 = V[i]; p2 = V[i + 1]; p3 = V[min(i + 2, len(V) - 1)]
        # tangents scaled by segment duration so velocity is continuous across keys of unequal spacing
        d0 = F[i + 1] - F[i]
        m1 = (p2 - p0) / max(F[min(i + 1, len(F) - 1)] - F[max(i - 1, 0)], 1e-6) * d0
        m2 = (p3 - p1) / max(F[min(i + 2, len(F) - 1)] - F[i], 1e-6) * d0
        u2, u3 = u * u, u * u * u
        out.append((2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * m2)
    return [v if len(v) > 1 else float(v[0]) for v in out]


def ease(u, kind='inout'):
    u = min(max(u, 0.0), 1.0)
    if kind == 'in':
        return u * u
    if kind == 'out':
        return 1 - (1 - u) ** 2
    if kind == 'sine':
        return 0.5 - 0.5 * math.cos(math.pi * u)
    return u * u * (3 - 2 * u)


def fov_for(height_at_dist, dist):
    """Vertical fov (deg) that shows `height_at_dist` world units at distance `dist`."""
    return math.degrees(2 * math.atan(height_at_dist / 2 / dist))


def dolly_zoom(target, direction, frame_h, d0, d1, n, u=None):
    """Camera dicts for a dolly zoom: the plane through `target` (normal = -direction) keeps `frame_h` of height in
    frame while the camera travels from distance d0 (telephoto, flat) to d1 (wide, deep). u: per-frame 0..1."""
    tgt = np.array(target, float); dirv = np.array(direction, float); dirv /= np.linalg.norm(dirv)
    out = []
    for i in range(n):
        uu = u[i] if u is not None else i / max(n - 1, 1)
        # interpolate in log distance so the change of perspective is even
        d = math.exp(math.log(d0) + (math.log(d1) - math.log(d0)) * uu)
        p = tgt - dirv * d
        out.append(dict(p=p.tolist(), t=tgt.tolist(), fov=fov_for(frame_h, d), near=max(0.05, d * 0.02), far=d + 4000))
    return out


class World:
    def __init__(self, shot, frames, w=1920, h=1080, fps=24, paper=PAPER_RGB, work=None):
        self.shot, self.n, self.w, self.h, self.fps = shot, frames, w, h, fps
        self.dir = work or os.path.join(ROOT, 'work/world', shot)
        os.makedirs(self.dir, exist_ok=True)
        self.S = dict(w=w, h=h, fps=fps, paper=list(paper), cards=[], mists=[], threads=[], overlays=[], camera=[])
        self.camera = []

    # ------------------------------------------------------------------ environment
    def fog(self, density=0.01, start=0.0):
        self.S['fog'] = dict(density=density, start=start)

    def sea(self, y=0.0, soft=2.0, amp=1.0, scale=0.05, drift=(0.3, 0.1)):
        """Cloud sea: everything below y (+- amp of slow noise) dissolves into bare paper over `soft` units."""
        self.S['sea'] = dict(y=y, soft=soft, amp=amp, scale=scale, drift=list(drift))

    # ------------------------------------------------------------------ objects
    def card(self, name, pos, height=None, width=None, relief=0.0, yaw=0.0, pitch=0.0, cards=CARDS, tex=None, depth=None,
             **kw):
        """A painted element as a displaced relief card. pos = bottom centre (anchor='bottom') or centre. Size from the
        card's aspect if only height or width is given. kw: bend, ink, lum, tint, edge, fogk, seak, opacity, keys, anim,
        carve, light, seg, uvRect, billboard, visible=[f0, f1], order."""
        if tex is None:
            m = card_meta(name, cards)
            tex = f'{cards}/{name}_rgba.png'
            dp = f'{cards}/{name}_depth.png'
            depth = depth if depth is not None else (dp if os.path.exists(os.path.join(ROOT, dp)) else None)
            asp = m['aspect']
        else:
            im = Image.open(os.path.join(ROOT, tex)); asp = im.width / im.height
        if height is None and width is None:
            height = 10.0
        if width is None:
            width = height * asp
        if height is None:
            height = width / asp
        o = dict(id=kw.pop('id', name), tex=tex, depth=depth, pos=list(map(float, pos)), size=[width, height], relief=relief,
                 yaw=yaw, pitch=pitch, **kw)
        self.S['cards'].append(o)
        return o

    def mist(self, pos, size, yaw=0.0, pitch=0.0, **kw):
        """Paper-coloured vapour sheet (soft against geometry by scene depth). pitch=-90 lies flat. kw: opacity, scale
        (noise cells per unit), speed [u, v] units/s, thresh (0.3 dense .. 0.6 wisps), edge, soft, wash, tone, band,
        nearFade, keys, billboard, seed."""
        o = dict(pos=list(map(float, pos)), size=list(size), yaw=yaw, pitch=pitch, **kw)
        self.S['mists'].append(o)
        return o

    def thread(self, pts, f0, **kw):
        """Gold thread drawn from pts[0] to pts[-1] starting at frame f0. kw: fdraw, fhold, ffade, rest, width (px at
        1080p), col, glow, opacity."""
        o = dict(pts=[list(map(float, p)) for p in pts], f0=float(f0), **kw)
        self.S['threads'].append(o)
        return o

    def points(self, parts=None, file=None, **kw):
        """Dust / flecks (B4): parts = Nx10 float array [x, y, z, f0 (birth frame), vx, vy, vz (units/s), life (s),
        size (world units), seed 0..1]; written to <work>/<id>.f32 and loaded by the page. kw: acc [x, y, z] (units/s^2),
        sway (units), swayF, col (beauty), glowCol, glow (glow-pass gain), opacity, minPx, maxPx (px at 1080p), fadeIn (s),
        fadeOut (fraction of life), grow (size growth per s), fogk, keys (opacity), id, order."""
        if parts is not None:
            a = np.asarray(parts, np.float32).reshape(-1, 10)
            pid = kw.pop('id', f'points{len(self.S.get("points", []))}')
            file = os.path.relpath(os.path.join(self.dir, pid + '.f32'), ROOT)
            a.tofile(os.path.join(ROOT, file))
            kw['id'] = pid
        o = dict(file=file, **kw)
        self.S.setdefault('points', []).append(o)
        return o

    def overlay(self, tex, pos, size, yaw=0.0, pitch=0.0, **kw):
        """Flat textured plane drawn over the scene's opaque pass (page planes, tablets, inscriptions). Not depth
        tested: use for things that are in front of everything near them, or set order."""
        o = dict(id=kw.pop('id', os.path.basename(tex)), tex=tex, pos=list(map(float, pos)), size=list(size), yaw=yaw, pitch=pitch,
                 anchor=kw.pop('anchor', 'center'), **kw)
        self.S['overlays'].append(o)
        return o

    def plane(self, tex, pos, size, yaw=0.0, pitch=0.0, **kw):
        """Flat textured plane in the opaque pass (depth tested, occludes and is occluded): a carved tablet, a page."""
        return self.card(None, pos, height=size[1], width=size[0], yaw=yaw, pitch=pitch, tex=tex, depth=None,
                         anchor=kw.pop('anchor', 'center'), id=kw.pop('id', os.path.basename(tex)), **kw)

    # ------------------------------------------------------------------ geometry helpers (same maths as the shader)
    def card_point(self, o, u, v, frame=None):
        """World position of texture point (u, v) (u left->right, v top->bottom, 0..1) on card o, displaced."""
        w, h = o['size']
        x = (u - 0.5) * w
        y = (1 - v) * h if o.get('anchor', 'bottom') == 'bottom' else (0.5 - v) * h
        z = 0.0
        if o.get('depth'):
            if '_D' not in o:
                o['_D'] = load_depth(o['depth'])
            D = o['_D']
            uu, vv = o.get('uvRect', [0, 0, 1, 1])[0] + u * (o.get('uvRect', [0, 0, 1, 1])[2] - o.get('uvRect', [0, 0, 1, 1])[0]), v
            d = D[min(int(vv * D.shape[0]), D.shape[0] - 1), min(int(uu * D.shape[1]), D.shape[1] - 1)]
            z += (d - 0.5) * o.get('relief', 0)
        xn = x / (w * 0.5)
        z -= o.get('bend', 0) * xn * xn * w * 0.5
        R = rot_yxz(o.get('yaw', 0), o.get('pitch', 0), o.get('roll', 0))
        s = o.get('scale', 1)
        s = np.array(s if isinstance(s, (list, tuple)) else [s, s, s], float)
        return (np.array(o['pos']) + R @ (np.array([x, y, z]) * s)).tolist()

    def card_normal(self, o):
        R = rot_yxz(o.get('yaw', 0), o.get('pitch', 0), o.get('roll', 0))
        return (R @ np.array([0, 0, 1.0])).tolist()

    # ------------------------------------------------------------------ render + finish
    def write(self):
        self.S['camera'] = [dict(c) for c in self.camera]
        assert len(self.S['camera']) == self.n, (len(self.S['camera']), self.n)
        S = json.loads(json.dumps(self.S, default=lambda x: None))
        for o in S['cards']:
            o.pop('_D', None)
        p = os.path.join(self.dir, 'scene.json')
        json.dump(S, open(p, 'w'))
        return p

    def render(self, ss=2, passes=None, frames=None, w=None, h=None, out=None):
        p = self.write()
        passes = passes or (['beauty', 'glow'] if self.S['threads'] or any(c.get('carve') for c in self.S['cards']) else ['beauty'])
        out = out or os.path.join(self.dir, 'frames')
        cmd = ['node', os.path.join(ROOT, 'tools/world/render.mjs'), '--scene', os.path.relpath(p, ROOT), '--out', os.path.relpath(out, ROOT),
               '--w', str(w or self.w), '--h', str(h or self.h), '--ss', str(ss), '--passes', ','.join(passes)]
        if frames is not None:
            cmd += ['--frames', frames if isinstance(frames, str) else ','.join(map(str, frames))]
        subprocess.run(cmd, check=True, cwd=ROOT)
        self.out = out
        return out

    def frame(self, f, ps='beauty'):
        im = cv2.imread(os.path.join(self.out if hasattr(self, 'out') else os.path.join(self.dir, 'frames'), ps, f'{f:04d}.png'), cv2.IMREAD_COLOR)
        return None if im is None else cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255

    def finish_frame(self, f, grain=None, bloom=0.0, glow_gain=1.0):
        """Rendered frame -> float RGB 0..1 with the screen-fixed paper grain and the glow pass bloomed in."""
        img = self.frame(f)
        if bloom or glow_gain:
            g = self.frame(f, 'glow')
            if g is not None:
                H, W = g.shape[:2]
                b = cv2.GaussianBlur(g, (0, 0), W / 1920 * 6) * 0.9 + cv2.GaussianBlur(g, (0, 0), W / 1920 * 22) * 0.7
                img = 1 - (1 - img) * (1 - np.clip(b * bloom, 0, 1))          # screen-add the halo
                img = img + g * 0.15 * glow_gain
        if grain is not None:
            img = img * grain
        return np.clip(img, 0, 1)


def paper_grain(w, h, seed=1988, variant='new'):
    """Screen-fixed paper: multiply the render (whose ground is the flat paper colour) by this ratio."""
    import sys
    sys.path.insert(0, ROOT)
    from tools.ink.paper import Paper
    P = Paper(w, h, variant, seed=seed)
    rgb = P.rgb.astype(np.float32)
    return rgb / np.array(PAPER_RGB, np.float32)[None, None]


def encode(frames_iter, out, n, w=960, h=540, fps=24, crf=14):
    """Write frames (float RGB 0..1, any size) to out as h264 yuv420p, exactly n frames, no audio."""
    os.makedirs(os.path.dirname(os.path.join(ROOT, out)), exist_ok=True)
    tmp = os.path.join(ROOT, out) + '.tmp.mp4'
    p = subprocess.Popen([FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
                          '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp],
                         stdin=subprocess.PIPE)
    k = 0
    for img in frames_iter:
        if img.shape[1] != w or img.shape[0] != h:
            img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        p.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()); k += 1
    p.stdin.close(); p.wait()
    assert k == n, (k, n)
    os.replace(tmp, os.path.join(ROOT, out))
    return out


def sheet(frames, out, idx=None, cols=4, width=480, label=None):
    """16-frame review sheet (frames = list of float RGB images or a callable f -> image)."""
    n = len(frames) if not callable(frames) else None
    idx = idx if idx is not None else np.linspace(0, n - 1, 16).round().astype(int).tolist()
    ims = []
    for i in idx:
        im = frames(i) if callable(frames) else frames[i]
        im = cv2.resize(im, (width, int(width * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_AREA)
        im = (np.clip(im, 0, 1) * 255).astype(np.uint8).copy()
        cv2.putText(im, f'{label or ""} f{i}', (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 30, 30), 1, cv2.LINE_AA)
        ims.append(im)
    rows = [np.concatenate(ims[r:r + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[r:r + cols])), 1) for r in range(0, len(ims), cols)]
    big = np.concatenate(rows, 0)
    os.makedirs(os.path.dirname(os.path.join(ROOT, out)), exist_ok=True)
    cv2.imwrite(os.path.join(ROOT, out), cv2.cvtColor(big, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return out

#!/usr/bin/env python3
"""Assemble HALYS from docs/shots.json + docs/picks.json: one H.264 file per shot, then a stream-copy concat plus the song.

Every shot renders to exactly its frame count at 24 fps CFR. A shot with no pick is a slate (dark card: id, timecode,
cut anchor, the start of its picture description). A pick that cannot fill its shot (video too short at the requested
rate, missing file, bad pick) is slated too, with the reason in red, and the run exits non-zero after building the cut.
Shots are cached: work/edit/<name>/shots/<id>.mp4 + <id>.json, re-rendered only when the shot record, its pick, its
source files (size + mtime), the render options or this code change. Restart-safe: every output is written as
.partial and renamed when complete and verified.

    .venv/bin/python tools/edit/assemble.py --name animatic_v0 --profile animatic
    .venv/bin/python tools/edit/assemble.py --name preview_v1 --profile preview --burn-in
    .venv/bin/python tools/edit/assemble.py --name master_v1  --profile master --audio work/sound/mix.wav
    .venv/bin/python tools/edit/assemble.py --name animatic_v0 --range C1:D4     # renders + joins only those shots
    .venv/bin/python tools/edit/assemble.py --name animatic_v0 --only C3,G4      # renders only those (no join)

Per-frame order: source -> pre-grade overlays -> grade (phase + shot: lift/gamma/gain, 3D LUTs, time-varying "to") ->
halation + print LUT (phase_grades["print"]) -> overlays -> film grain -> letterbox -> burn-in. The grade is built by
tools/grade/build.py from docs/grade.json (tools/edit/README.md, "Grade"). Colour: RGB frames are converted to BT.709 limited range through ffmpeg's scale (accurate_rnd,
full_chroma_int) and tagged bt709/tv (docs/HARVEST.md section 6, the colour-matrix trap); video sources are decoded
with their tagged matrix/range, or BT.709 limited when untagged at >= 720 lines.
"""
import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from common import FPS, PICKS, ROOT, SHOTS, SONG, load_json, select_range, tc

PROFILES = {
    # name: size, crf, preset, tune, burn-in, grain strength, audio bitrate
    # grain_mode: dynamic = a new grain field every frame (living grain; static read as a dirty lens, QA_PREVIEW_V2 #1)
    'animatic': dict(size='960x540', crf=20, preset='veryfast', tune=None, burn_in=True, grain=0.0, abr='256k',
                     grain_mode='static'),
    'preview': dict(size='960x540', crf=18, preset='medium', tune='grain', burn_in=False, grain=0.035, abr='256k',
                    grain_mode='dynamic'),
    'master': dict(size='1920x1080', crf=14, preset='slow', tune='grain', burn_in=False, grain=0.035, abr='320k',
                   grain_mode='dynamic'),
}
LB_ASPECT = 2.39
CODE_FILES = ['assemble.py', 'common.py', 'typeset.py']
RED = (255, 92, 74)


class ShotProblem(Exception):
    """A pick that cannot fill its shot: the shot is slated with this message."""


# ---------------------------------------------------------------------------------------------------------------------
# small helpers

def rel(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def file_sig(p):
    """Cheap identity of a source file (size + mtime); a changed file re-renders its shots."""
    p = rel(p)
    if not p.exists():
        return ['missing', str(p)]
    st = p.stat()
    return [str(p), st.st_size, st.st_mtime_ns]


def dir_sig(d, pattern):
    files = sorted(glob.glob(str(rel(d) / pattern)))
    return [str(rel(d)), len(files)] + [[os.path.basename(f), os.path.getsize(f), os.path.getmtime(f)] for f in files]


def frame_files(d, pattern):
    files = sorted(glob.glob(str(rel(d) / pattern)))
    return files


def ease(x, kind='inout'):
    x = min(max(x, 0.0), 1.0)
    if kind == 'linear':
        return x
    return x * x * (3 - 2 * x)          # smoothstep


def even(x):
    return int(2 * round(x / 2.0))


def lb_bar(w, h):
    """Bar height (px, rounded to even for clean 4:2:0 chroma) of a 2.39:1 letterbox in w x h."""
    return max(0, even((h - w / LB_ASPECT) / 2.0))


def lb_amount(f, opts):
    """0..1 letterbox amount at global frame f: 1 before the hit, eased to 0 over N frames from the hit (N=0: hard)."""
    hit, n = opts['lb_frame'], opts['lb_open']
    if f < hit:
        return 1.0
    if n <= 0 or f >= hit + n:
        return 0.0
    return 1.0 - ease((f - hit) / n)


# ---------------------------------------------------------------------------------------------------------------------
# framing: crop (normalised source rect) -> cover-fit to the output aspect -> optional zoom/pan -> resample

def view_box(sw, sh, W, H, crop=None, zoom=1.0, cx=None, cy=None):
    """Source-pixel box (x0, y0, x1, y1) that fills W x H. crop = [x, y, w, h] in 0..1 of the source; zoom > 1 pushes
    in; cx, cy = centre of view in 0..1 of the source (default: centre of the crop). Clamped inside the crop."""
    x, y, w, h = crop or [0, 0, 1, 1]
    rx0, ry0, rw, rh = x * sw, y * sh, w * sw, h * sh
    A = W / H
    if rw / rh > A:
        bh, bw = rh, rh * A
    else:
        bw, bh = rw, rw / A
    bw, bh = bw / zoom, bh / zoom
    ccx = rx0 + rw / 2 if cx is None else cx * sw
    ccy = ry0 + rh / 2 if cy is None else cy * sh
    ccx = min(max(ccx, rx0 + bw / 2), rx0 + rw - bw / 2)
    ccy = min(max(ccy, ry0 + bh / 2), ry0 + rh - bh / 2)
    return (ccx - bw / 2, ccy - bh / 2, ccx + bw / 2, ccy + bh / 2)


def fit(img, W, H, crop=None, zoom=1.0, cx=None, cy=None):
    """PIL image -> float32 HxWx3 (0..1) of the view box, Lanczos with a sub-pixel box (no jitter on slow moves)."""
    box = view_box(img.width, img.height, W, H, crop, zoom, cx, cy)
    out = img.resize((W, H), Image.LANCZOS, box=box)
    return np.asarray(out, np.float32) / 255.0


def to_rgb(img):
    if img.mode == 'RGBA':
        bg = Image.new('RGB', img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert('RGB')


# ---------------------------------------------------------------------------------------------------------------------
# sources: each yields exactly n float32 frames or raises ShotProblem before the first frame where it can

def src_still(pick, n, W, H):
    p = rel(pick['src'])
    if not p.exists():
        raise ShotProblem(f'MISSING SOURCE {pick["src"]}')
    img = to_rgb(Image.open(p))
    mv = pick.get('move') or {}
    a, b = mv.get('from', {}), mv.get('to', mv.get('from', {}))
    kind = mv.get('ease', 'inout')
    crop = pick.get('crop')
    if not mv:
        fr = fit(img, W, H, crop)
        for _ in range(n):
            yield fr
        return
    # default centre of view = centre of the crop (0..1 of the source)
    cx_ = (crop[0] + crop[2] / 2) if crop else 0.5
    cy_ = (crop[1] + crop[3] / 2) if crop else 0.5
    x0, x1 = a.get('x', cx_), b.get('x', a.get('x', cx_))
    y0, y1 = a.get('y', cy_), b.get('y', a.get('y', cy_))
    z0, z1 = a.get('zoom', 1.0), b.get('zoom', a.get('zoom', 1.0))
    for i in range(n):
        u = ease(i / (n - 1) if n > 1 else 0.0, kind)
        z = z0 * (z1 / z0) ** u          # zoom interpolated geometrically, so a push feels constant
        yield fit(img, W, H, crop, z, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)


def probe_video(path):
    import av
    with av.open(str(path)) as c:
        s = c.streams.video[0]
        rate = float(s.average_rate or s.guessed_rate or 24)
        n = s.frames
        if s.duration is not None:
            dur = float(s.duration * s.time_base)
        elif c.duration is not None:
            dur = c.duration / 1e6
        else:
            dur = n / rate if n else 0.0
        if n:   # frame count is the most reliable for CFR takes
            dur = n / rate
        cc = s.codec_context
        return dict(rate=rate, frames=n, duration=dur, width=cc.width, height=cc.height,
                    colorspace=int(cc.colorspace or 2), color_range=int(cc.color_range or 0))


def video_matrix(info):
    """(src_colorspace, src_color_range) for PyAV's reformatter. Untagged HD is BT.709 limited (not ffmpeg's 601)."""
    cs = info['colorspace']
    if cs == 1:
        m = 'ITU709'
    elif cs in (5, 6):
        m = 'ITU601'
    elif cs == 9:
        m = 'BT2020'
    else:
        m = 'ITU709' if info['height'] >= 720 else 'ITU601'
    r = 'JPEG' if info['color_range'] == 2 else 'MPEG'
    return m, r


def src_video(pick, n, W, H):
    import av
    from av.video.reformatter import VideoReformatter
    p = rel(pick['src'])
    if not p.exists():
        raise ShotProblem(f'MISSING SOURCE {pick["src"]}')
    info = probe_video(p)
    t_in = float(pick.get('in', 0.0))
    rate = float(pick.get('rate', 1.0))
    if rate <= 0 or t_in < 0:
        raise ShotProblem(f'BAD PICK: in {t_in}, rate {rate}')
    # every output frame k samples source time t_in + k*rate/24; the last sample must fall on a real source frame
    need = t_in + (n - 1) * rate / FPS
    if need >= info['duration'] - 1e-6:
        have = max(0.0, info['duration'] - t_in)
        raise ShotProblem(f'TOO SHORT: source {info["duration"]:.2f} s, from in {t_in:.2f} s gives {have:.2f} s; '
                          f'shot needs {n / FPS * rate:.2f} s at rate {rate:g}')
    interp = pick.get('interp', 'hold')
    m, r = video_matrix(info)
    crop, flip = pick.get('crop'), pick.get('flip', False)
    ref = VideoReformatter()
    fdur = 1.0 / info['rate']

    def frames():
        with av.open(str(p)) as c:
            s = c.streams.video[0]
            s.thread_type = 'AUTO'
            t0 = float(s.start_time * s.time_base) if s.start_time is not None else 0.0
            if t_in > 1.0:
                c.seek(int((t_in - 1.0 + t0) / s.time_base), stream=s, backward=True)
            for fr in c.decode(s):
                t = float(fr.pts * s.time_base) - t0 if fr.pts is not None else None
                yield t, fr

    def to_arr(fr):
        rgb = ref.reformat(fr, format='rgb24', src_colorspace=m, src_color_range=r, dst_color_range='JPEG',
                           interpolation='BICUBIC')
        img = Image.fromarray(rgb.to_ndarray(), 'RGB')
        a = fit(img, W, H, crop)
        return a[:, ::-1] if flip else a

    it = frames()
    prev = None          # (t, frame) with t <= sample time
    nxt = None
    cache = {}
    for k in range(n):
        ts = t_in + k * rate / FPS + 1e-6
        # advance until the next decoded frame starts after ts
        while True:
            if nxt is None:
                try:
                    nxt = next(it)
                except StopIteration:
                    nxt = (math.inf, None)
            if nxt[0] <= ts:
                prev, nxt = nxt, None
                continue
            break
        if prev is None:
            raise ShotProblem(f'TOO SHORT: no source frame at {ts:.3f} s')
        if prev[0] + fdur * 1.5 < ts and nxt[1] is None:
            raise ShotProblem(f'TOO SHORT: source ends at {prev[0] + fdur:.3f} s, shot needs {ts:.3f} s')
        key = prev[0]
        if key not in cache:
            cache = {key: to_arr(prev[1])}       # keep only the current frame
        a = cache[key]
        if interp == 'blend' and nxt[1] is not None and nxt[0] != math.inf:
            w = (ts - prev[0]) / max(1e-9, nxt[0] - prev[0])
            if w > 1e-3:
                a = a * (1 - w) + to_arr(nxt[1]) * w
        yield a


def src_frames(pick, n, W, H):
    files = frame_files(pick['dir'], pick.get('pattern', '*.png'))
    start = int(pick.get('start', 0))
    if not files:
        raise ShotProblem(f'MISSING SOURCE frames in {pick["dir"]}')
    if len(files) - start < n:
        raise ShotProblem(f'TOO SHORT: {len(files) - start} frames from {start} in {pick["dir"]}, shot needs {n}')
    crop, flip = pick.get('crop'), pick.get('flip', False)
    for i in range(n):
        a = fit(to_rgb(Image.open(files[start + i])), W, H, crop)
        yield a[:, ::-1] if flip else a


SOURCES = {'still': src_still, 'video': src_video, 'frames': src_frames}


# ---------------------------------------------------------------------------------------------------------------------
# layers

def load_overlays(pick, n, W, H):
    """Overlay specs -> list of (spec, getter(i) -> (rgb, alpha) float arrays)."""
    out = []
    for ov in pick.get('overlay', []) or []:
        if 'src' in ov:
            p = rel(ov['src'])
            if not p.exists():
                raise ShotProblem(f'MISSING OVERLAY {ov["src"]}')
            im = Image.open(p).convert('RGBA').resize((W, H), Image.LANCZOS)
            a = np.asarray(im, np.float32) / 255.0
            rgb, al = a[..., :3], a[..., 3]
            out.append((ov, lambda i, rgb=rgb, al=al: (rgb, al)))
        elif 'dir' in ov:
            files = frame_files(ov['dir'], ov.get('pattern', '*.png'))
            st = int(ov.get('start', 0))
            if len(files) - st < n:
                raise ShotProblem(f'TOO SHORT overlay {ov["dir"]}: {len(files) - st} frames, needs {n}')

            def get(i, files=files, st=st):
                a = np.asarray(Image.open(files[st + i]).convert('RGBA').resize((W, H), Image.LANCZOS), np.float32) / 255.0
                return a[..., :3], a[..., 3]
            out.append((ov, get))
        else:
            raise ShotProblem('BAD PICK: overlay needs src or dir')
    return out


def blend(base, rgb, al, mode, opacity):
    a = (al * opacity)[..., None]
    if mode == 'over':
        return base * (1 - a) + rgb * a
    if mode == 'screen':
        return 1 - (1 - base) * (1 - rgb * a)
    if mode == 'add':
        return np.minimum(1.0, base + rgb * a)
    raise ShotProblem(f'BAD PICK: blend {mode!r}')


LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def grade_lgg(x, g):
    """Simple grade: lift/gamma/gain per channel then saturation about Rec.709 luma, on display-referred 0..1."""
    lift = np.asarray(g.get('lift', 0.0), np.float32)
    gamma = np.asarray(g.get('gamma', 1.0), np.float32)
    gain = np.asarray(g.get('gain', 1.0), np.float32)
    sat = float(g.get('sat', 1.0))
    x = gain * (x + lift * (1 - x))
    x = np.clip(x, 0, None) ** (1.0 / gamma)
    if sat != 1.0:
        y = (x @ LUMA)[..., None]
        x = y + (x - y) * sat
    return np.clip(x, 0, 1)


_LUTS = {}


def load_cube(path):
    """.cube 3D LUT -> float32 (N, N, N, 3) indexed [b, g, r] (red fastest in the file). Cached per process."""
    p = rel(path)
    if p not in _LUTS:
        if not p.exists():
            raise ShotProblem(f'MISSING LUT {path} (run tools/grade/build.py)')
        n, rows, lo, hi = None, [], [0.0] * 3, [1.0] * 3
        for line in p.read_text().splitlines():
            t = line.split()
            if not t or t[0].startswith('#') or t[0] == 'TITLE':
                continue
            if t[0] == 'LUT_3D_SIZE':
                n = int(t[1])
            elif t[0] == 'DOMAIN_MIN':
                lo = [float(v) for v in t[1:4]]
            elif t[0] == 'DOMAIN_MAX':
                hi = [float(v) for v in t[1:4]]
            elif t[0][0].isdigit() or t[0][0] in '-.':
                rows.append([float(v) for v in t[:3]])
        if not n or len(rows) != n ** 3 or lo != [0.0] * 3 or hi != [1.0] * 3:
            raise ShotProblem(f'BAD LUT {path}: need a 0..1 LUT_3D_SIZE N with N^3 rows')
        _LUTS[p] = np.asarray(rows, np.float32).reshape(n, n, n, 3)
    return _LUTS[p]


def apply_lut(x, lut):
    """Trilinear 3D LUT on HxWx3 float 0..1."""
    n = lut.shape[0]
    flat = lut.reshape(-1, 3)
    v = np.clip(x, 0.0, 1.0) * (n - 1)
    i = np.minimum(v.astype(np.int32), n - 2)
    f = v - i
    r, g, b = i[..., 0], i[..., 1], i[..., 2]
    fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    base = (b * n + g) * n + r
    out = 0
    for db, wb in ((0, 1 - fb), (1, fb)):
        for dg, wg in ((0, 1 - fg), (1, fg)):
            w = wb * wg
            k = base + (db * n + dg) * n
            out = out + w * ((1 - fr) * flat[k] + fr * flat[k + 1])
    return out


def blur(x, sigma):
    import cv2
    return cv2.GaussianBlur(np.ascontiguousarray(x, np.float32), (0, 0), sigma) if sigma > 0.05 else x


def matte_frame(m, i, W, H):
    files = frame_files(m['dir'], m.get('pattern', '*.png'))
    k = int(m.get('start', 0)) + i
    if k >= len(files):
        raise ShotProblem(f'TOO SHORT matte {m["dir"]}: no frame {k}')
    im = Image.open(files[k]).convert('L')
    if im.size != (W, H):
        im = im.resize((W, H), Image.BILINEAR)
    return np.asarray(im, np.float32)[..., None] / 255.0


def grade_one(x, g, W, i=0):
    """One grade dict: optional "blur" (px at 1920 wide), the simple lift/gamma/gain/sat keys, a "lut", then
    "mattes": [{"dir", "pattern", "start", "lut"}] secondaries (that LUT applied inside a per-frame grey matte)."""
    if g.get('blur'):
        x = blur(x, float(g['blur']) * W / 1920.0)
    if any(k in g for k in ('lift', 'gamma', 'gain', 'sat')):
        x = grade_lgg(x, g)
    if g.get('lut'):
        x = apply_lut(x, load_cube(g['lut']))
    for m in g.get('mattes') or []:
        a = matte_frame(m, i, W, x.shape[0])
        x = x * (1 - a) + apply_lut(x, load_cube(m['lut'])) * a
    if g.get('window'):
        x = window(x, g['window'])
    return x


def window(x, w):
    """Soft elliptical window (a printer's dodge): outside it the picture goes `outside` stops darker.
    {"center": [x, y] in 0..1 of the frame, "radius": [rx, ry] in 0..1 of the frame width, "soft": 0..1, "outside": -0.4}"""
    H, W = x.shape[:2]
    cx, cy = w.get('center', [0.5, 0.5])
    rx, ry = w.get('radius', [0.3, 0.3])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx / W - cx) / rx) ** 2 + ((yy / W - cy * H / W) / ry) ** 2)
    s = float(w.get('soft', 0.6))
    m = np.clip((d - (1 - s)) / max(1e-6, s), 0, 1)
    m = m * m * (3 - 2 * m)
    return x * (2.0 ** (float(w.get('outside', -0.4)) * m / 2.4))[..., None]


def grade(x, g, u=0.0, W=1920, i=0):
    """A grade dict, optionally time-varying: {"...": start, "to": {grade dict}, "ease": "inout"|"linear",
    "span": [u0, u1]} blends the two graded results by the eased shot position u (0 first frame, 1 last)."""
    a = grade_one(x, g, W, i)
    if isinstance(g.get('to'), dict):
        u0, u1 = g.get('span', [0.0, 1.0])
        w = ease((u - u0) / max(1e-6, u1 - u0), g.get('ease', 'inout'))
        if w > 0:
            a = a * (1 - w) + grade_one(x, g['to'], W, i) * w
    return np.clip(a, 0, 1)


def halation(x, h, W):
    """Film halation: light above a threshold bleeds back through the base as a soft red-orange glow."""
    if not h or not h.get('strength'):
        return x
    y = x.max(-1, keepdims=True)
    t = float(h.get('threshold', 0.9))
    m = np.clip((y - t) / max(1e-6, 1 - t), 0, 1) * x
    if not m.any():
        return x
    r = float(h.get('radius', 18)) * W / 1920.0
    glow = 0.6 * blur(m, r) + 0.4 * blur(m, r * 3)
    return x + float(h['strength']) * glow * np.asarray(h.get('tint', [1.0, 0.45, 0.2]), np.float32)


def grain_field(seed, W, H):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((H, W, 1), dtype=np.float32)


def grain_fields(seed, W, H, model, size=1.0):
    """Unit-variance grain fields for the film model: fine and coarse luma grain plus a 3-channel chroma field.
    Sizes are Gaussian sigmas in px at 1920 wide (scaled to the output), times `size`."""
    rng = np.random.default_rng(seed)
    k = W / 1920.0 * size
    out = {}
    for name, sig, ch in (('fine', model.get('fine', 0.6), 1), ('coarse', model.get('coarse', 1.3), 1),
                          ('chroma', model.get('chroma_size', 1.6), 3)):
        f = rng.standard_normal((H, W, ch), dtype=np.float32)
        f = blur(f, sig * k).reshape(H, W, ch)
        out[name] = f / max(1e-6, float(f.std()))
    return out


def apply_grain(x, strength, model, fl):
    """Luma-weighted film grain: amplitude follows model["curve"] [[luma, mult], ...]; fine grain in the highlights,
    coarser in the shadows; a little chroma grain ("chroma", relative)."""
    L = x @ LUMA
    c = np.asarray(model.get('curve', [[0, 0.6], [0.3, 1.0], [0.7, 0.75], [1, 0.35]]), np.float32)
    amp = np.interp(L, c[:, 0], c[:, 1]).astype(np.float32)[..., None] * strength
    wc = np.clip(1.0 - L * 1.6, 0, 1)[..., None]           # coarse in the dark, fine in the light
    n = fl['coarse'] * wc + fl['fine'] * (1 - wc)
    n = n / np.sqrt(wc * wc + (1 - wc) ** 2)                 # keep unit variance across the mix
    return x + amp * (n + float(model.get('chroma', 0.25)) * fl['chroma'])


# ---------------------------------------------------------------------------------------------------------------------
# slate and burn-in

def wrap(text, f, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.getlength(t) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def slate_image(shot, W, H, status=None):
    from typeset import BOOK_GOLD, CREAM, DIM, font
    k = W / 1920.0
    img = Image.new('RGB', (W, H), (38, 38, 38))
    d = ImageDraw.Draw(img)
    x0 = 190 * k
    fid = font('Archivo', 120 * k, 800, 100)
    d.text((x0, 330 * k), shot['id'], font=fid, fill=CREAM, anchor='ls')
    xs = x0 + fid.getlength(shot['id']) + 44 * k
    d.text((xs, 284 * k), f'{shot["section"]}. {shot["section_title"]}', font=font('OpenSans', 30 * k, 600), fill=DIM,
           anchor='ls')
    ph = shot.get('phase_label') or '(no phase)'
    ds = ' · '.join(x for x in [shot.get('dir'), shot.get('sun')] if x)
    d.text((xs, 328 * k), ph + (f'   ·   {ds}' if ds else ''), font=font('OpenSans', 26 * k, 500), fill=BOOK_GOLD,
           anchor='ls')
    n = shot['out_frame'] - shot['in_frame']
    d.text((x0, 400 * k), f'{tc(shot["in_frame"])} – {tc(shot["out_frame"])}   {n} f  {n / FPS:.2f} s   '
                          f'cut on {shot["anchor"]["label"]}', font=font('Mono', 26 * k), fill=CREAM, anchor='ls')
    desc = shot.get('picture', '').replace('**', '').replace('*', '')     # Markdown emphasis from SHOTLIST.md
    if len(desc) > 120:
        cut = desc[:120].rsplit(' ', 1)[0]
        desc = cut.rstrip(',;:.') + ' …'
    fd = font('OpenSans', 40 * k, 500)
    y = 480 * k
    for line in wrap(desc, fd, 1540 * k)[:4]:
        d.text((x0, y), line, font=fd, fill=(225, 222, 214), anchor='ls')
        y += 56 * k
    if status:
        fs = font('OpenSans', 32 * k, 700)
        y = max(y + 20 * k, 800 * k)
        for line in wrap(status, fs, 1540 * k)[:2]:
            d.text((x0, y), line, font=fs, fill=RED, anchor='ls')
            y += 44 * k
    return np.asarray(img, np.float32) / 255.0


def burn_in(arr8, shot, f, i, n, bar):
    from typeset import font
    H, W = arr8.shape[:2]
    k = W / 1920.0
    img = Image.fromarray(arr8)
    d = ImageDraw.Draw(img, 'RGBA')
    fm = font('Mono', max(11, 22 * k))
    txt = f'{shot["id"]}  {tc(f)}  f{f}  {i + 1}/{n}'
    x, y = 20 * k, H - bar - 14 * k
    w = fm.getlength(txt)
    d.rectangle([x - 6 * k, y - 22 * k - 4, x + w + 6 * k, y + 8 * k], fill=(0, 0, 0, 150))
    d.text((x, y), txt, font=fm, fill=(240, 240, 240, 255), anchor='ls')
    return np.asarray(img)


# ---------------------------------------------------------------------------------------------------------------------
# one shot

def ffmpeg_encode_cmd(out, W, H, o):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-an',
           '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,'
           # tag the frames themselves (the encoder takes trc/primaries from the frames; -color_* alone left them unset)
           'setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv',
           '-c:v', 'libx264', '-preset', o['preset'], '-crf', str(o['crf']), '-profile:v', 'high', '-level:v', '4.1',
           '-g', '48', '-x264-params', 'stitchable=1', '-threads', str(o['threads']),
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
           '-video_track_timescale', str(FPS * 512), '-f', 'mp4', str(out)]
    if o.get('tune'):
        cmd[cmd.index('-g'):cmd.index('-g')] = ['-tune', o['tune']]
    return cmd


def count_packets(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
                        'stream=nb_read_packets', '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    try:
        return int(r.stdout.strip().split(',')[0])
    except ValueError:
        return -1


def render_shot(job):
    """Worker: render one shot to <id>.mp4 (via .partial). Returns a status dict."""
    shot, pick, o, out, key = job['shot'], job['pick'], job['opts'], Path(job['out']), job['key']
    W, H = o['W'], o['H']
    n = shot['out_frame'] - shot['in_frame']
    t0 = time.time()
    status, kind, problem = 'ok', (pick or {}).get('kind', 'slate'), None
    overlays = []
    frames_iter = None
    try:
        if pick and pick.get('kind'):
            if pick['kind'] not in SOURCES:
                raise ShotProblem(f'BAD PICK: unknown kind {pick["kind"]!r}')
            frames_iter = SOURCES[pick['kind']](pick, n, W, H)
            first = next(frames_iter)           # surfaces TOO SHORT / MISSING before encoding starts
            frames_iter = _chain(first, frames_iter)
        if pick:
            overlays = load_overlays(pick, n, W, H)
    except ShotProblem as e:
        problem, frames_iter, kind, status = str(e), None, 'slate', 'problem'
        overlays = []

    for attempt in range(2):
        try:
            _encode(shot, pick, o, out, n, frames_iter, overlays, problem)
            break
        except ShotProblem as e:            # failed mid-shot (a source ran out): slate it instead
            problem, frames_iter, kind, status, overlays = str(e), None, 'slate', 'problem', []
    got = count_packets(out.with_suffix('.partial.mp4'))
    if got != n:
        raise RuntimeError(f'{shot["id"]}: encoded {got} frames, expected {n}')
    os.replace(out.with_suffix('.partial.mp4'), out)
    meta = dict(id=shot['id'], key=key, frames=n, kind=kind, status=status, problem=problem,
                secs=round(time.time() - t0, 2), pick=pick)
    out.with_suffix('.json').write_text(json.dumps(meta, indent=1))
    return meta


def _chain(first, rest):
    yield first
    yield from rest


def _encode(shot, pick, o, out, n, frames_iter, overlays, problem):
    W, H = o['W'], o['H']
    part = out.with_suffix('.partial.mp4')
    proc = subprocess.Popen(ffmpeg_encode_cmd(part, W, H, o), stdin=subprocess.PIPE)
    try:
        slate = slate_image(shot, W, H, problem or (None if frames_iter else 'NO PICK')) if frames_iter is None else None
        pk = pick or {}
        g_on = frames_iter is not None and pk.get('grade', True) is not False
        pgs = o['phase_grades']
        phase_g = pgs.get(shot.get('phase')) or {}
        shot_g = pk['grade'] if isinstance(pk.get('grade'), dict) else {}
        grades = []
        if g_on and o['phase_grade'] and pk.get('phase_grade', True) and phase_g:
            grades.append(phase_g)
        if g_on and shot_g:
            grades.append(shot_g)
        prn = pgs.get('print') if g_on and o['phase_grade'] and shot_g.get('print', True) is not False else None
        hal = (prn or {}).get('halation')
        if isinstance(shot_g.get('halation'), dict):
            hal = dict(hal or {}, **shot_g['halation'])
        elif shot_g.get('halation') is False:
            hal = None
        gs = pk.get('grain', None)
        strength = o['grain'] if gs is None or gs is True else (0.0 if gs is False else float(gs))
        if frames_iter is None:
            strength = 0.0                  # slates are cards: no grain
        model = (pgs.get('print') or {}).get('grain')          # the film grain model (None: the flat field)
        strength *= float(phase_g.get('grain_scale', 1.0)) if model else 1.0
        seed = int(pk.get('seed', zlib.crc32(shot['id'].encode())))

        def fields(s):
            if model:
                return grain_fields(s, W, H, model, float(phase_g.get('grain_size', 1.0)))
            return grain_field(s, W, H)
        gf = fields(seed) if strength > 0 and o['grain_mode'] == 'static' else None
        bar_full = lb_bar(W, H)
        for i in range(n):
            f = shot['in_frame'] + i
            u = i / (n - 1) if n > 1 else 0.0
            x = next(frames_iter) if frames_iter is not None else slate
            for ov, get in overlays:
                if ov.get('pre_grade'):
                    rgb, al = get(i)
                    x = blend(x, rgb, al, ov.get('blend', 'over'), float(ov.get('opacity', 1.0)))
            for g in grades:
                x = grade(x, g, u, W, i)
            if prn:
                x = halation(x, hal, W)
                if prn.get('lut'):
                    x = apply_lut(x, load_cube(prn['lut']))
            for ov, get in overlays:
                if not ov.get('pre_grade'):
                    rgb, al = get(i)
                    x = blend(x, rgb, al, ov.get('blend', 'over'), float(ov.get('opacity', 1.0)))
            if strength > 0:
                field = gf if gf is not None else fields(seed * 100003 + i)
                x = apply_grain(x, strength, model, field) if model else x + strength * field
            a8 = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
            amt = lb_amount(f, o)
            bar = int(round(bar_full * amt / 2.0)) * 2 if amt < 1 else bar_full
            if bar > 0:
                a8 = a8.copy() if not a8.flags.writeable else a8
                a8[:bar] = 0
                a8[H - bar:] = 0
            if o['burn_in']:
                a8 = burn_in(a8, shot, f, i, n, bar)
            proc.stdin.write(np.ascontiguousarray(a8).tobytes())
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f'ffmpeg failed on {shot["id"]}')
    except BaseException:
        proc.kill()
        proc.wait()
        if part.exists():
            part.unlink()
        raise


# ---------------------------------------------------------------------------------------------------------------------
# cache keys

def code_sig():
    h = hashlib.sha256()
    for f in CODE_FILES:
        h.update((Path(__file__).parent / f).read_bytes())
    return h.hexdigest()[:16]


def pick_sig(pick):
    if not pick:
        return None
    sig = {'pick': pick}
    if pick.get('kind') in ('still', 'video'):
        sig['src'] = file_sig(pick['src'])
    if pick.get('kind') == 'frames':
        sig['src'] = dir_sig(pick['dir'], pick.get('pattern', '*.png'))
    sig['overlay'] = [file_sig(ov['src']) if 'src' in ov else dir_sig(ov['dir'], ov.get('pattern', '*.png'))
                      for ov in pick.get('overlay', []) or []]
    return sig


def shot_key(shot, pick, o, code):
    lbf = o['lb_frame'] + max(0, o['lb_open'])
    relevant = {k: o[k] for k in ('W', 'H', 'crf', 'preset', 'tune', 'burn_in', 'grain', 'grain_mode', 'phase_grade')}
    pgs = o['phase_grades']
    relevant['phase_grade_values'] = pgs.get(shot.get('phase')) if o['phase_grade'] else None
    relevant['print'] = pgs.get('print') if o['phase_grade'] else None
    relevant['grain_model'] = [(pgs.get('print') or {}).get('grain'), (pgs.get(shot.get('phase')) or {}).get('grain_scale'),
                               (pgs.get(shot.get('phase')) or {}).get('grain_size')]
    # LUT files by content identity (a rebuilt LUT re-renders the shots that use it)
    g = (pick or {}).get('grade')
    luts = [d.get('lut') for d in (relevant['phase_grade_values'], relevant['print'],
                                   g if isinstance(g, dict) else None,
                                   g.get('to') if isinstance(g, dict) and isinstance(g.get('to'), dict) else None)
            if isinstance(d, dict) and d.get('lut')]
    mattes = (g.get('mattes') or []) if isinstance(g, dict) else []
    luts += [m['lut'] for m in mattes if m.get('lut')]
    relevant['luts'] = [file_sig(p) for p in luts]
    relevant['mattes'] = [dir_sig(m['dir'], m.get('pattern', '*.png')) for m in mattes]
    relevant['lb'] = [lb_amount(f, o) for f in range(shot['in_frame'], shot['out_frame'])] \
        if shot['in_frame'] < lbf else 0
    blob = json.dumps({'shot': shot, 'pick': pick_sig(pick), 'opts': relevant, 'code': code}, sort_keys=True,
                      default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:20]


# ---------------------------------------------------------------------------------------------------------------------
# join, mux, verify

def probe_json(path, *args):
    r = subprocess.run(['ffprobe', '-v', 'error', '-of', 'json', *args, str(path)], capture_output=True, text=True)
    return json.loads(r.stdout or '{}')


def join(shot_files, audio, a_start, a_dur, out, abr):
    """Stream-copy concat of the shot files (no re-encode, no drift), plus the audio from a_start for a_dur (or all)."""
    lst = out.with_suffix('.concat.txt')
    lst.write_text(''.join(f"file '{p}'\n" for p in shot_files))
    part = out.with_name(out.stem + '.partial.mp4')
    a_in = ['-i', str(audio)] if a_start is None else ['-ss', f'{a_start:.6f}', '-t', f'{a_dur:.6f}', '-i', str(audio)]
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), *a_in,
           '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', abr,
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
           '-movflags', '+faststart', str(part)]
    subprocess.run(cmd, check=True)
    return part


def verify(path, n_expected, a_expected):
    """Frame count (packets and decoded), regular 1/24 timestamps, durations, a/v agreement, colour tags."""
    res, bad = {}, []
    v = probe_json(path, '-select_streams', 'v:0', '-count_frames', '-show_entries',
                   'stream=nb_read_frames,r_frame_rate,avg_frame_rate,duration,color_space,color_range,'
                   'color_transfer,color_primaries,width,height,pix_fmt')['streams'][0]
    a = probe_json(path, '-select_streams', 'a:0', '-show_entries', 'stream=duration,sample_rate,codec_name')['streams'][0]
    pk = probe_json(path, '-select_streams', 'v:0', '-show_entries', 'packet=pts', )['packets']
    pts = sorted(int(p['pts']) for p in pk)
    tb_frames = [(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    res.update(frames=int(v['nb_read_frames']), video_s=float(v['duration']), audio_s=float(a['duration']),
               rate=v['r_frame_rate'], avg_rate=v['avg_frame_rate'], size=f'{v["width"]}x{v["height"]}',
               pix_fmt=v['pix_fmt'],
               color=f'{v.get("color_space")}/{v.get("color_range")}/{v.get("color_transfer")}/{v.get("color_primaries")}',
               pts_steps=sorted(set(tb_frames)))
    if res['frames'] != n_expected:
        bad.append(f'decoded {res["frames"]} frames, expected {n_expected}')
    if len(set(tb_frames)) > 1:
        bad.append(f'irregular frame timestamps: steps {sorted(set(tb_frames))}')
    if v['r_frame_rate'] != '24/1' or v['avg_frame_rate'] != '24/1':
        bad.append(f'rate {v["r_frame_rate"]} / avg {v["avg_frame_rate"]}')
    if abs(res['video_s'] - n_expected / FPS) > 1e-3:
        bad.append(f'video duration {res["video_s"]} != {n_expected / FPS:.4f}')
    if abs(res['audio_s'] - res['video_s']) > 1.0 / FPS + 1e-3:
        bad.append(f'audio {res["audio_s"]:.4f} s vs video {res["video_s"]:.4f} s (> 1 frame)')
    if a_expected is not None and abs(res['audio_s'] - a_expected) > 0.005:
        bad.append(f'audio {res["audio_s"]:.4f} s, expected {a_expected:.4f}')
    if res['color'] != 'bt709/tv/bt709/bt709':
        bad.append(f'colour tags {res["color"]}')
    if res['pix_fmt'] != 'yuv420p':
        bad.append(f'pix_fmt {res["pix_fmt"]}')
    return res, bad


def wav_duration(p):
    import wave
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


# ---------------------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', required=True, help='output folder work/edit/<name>/ and file chaosmonkey_<name>.mp4')
    ap.add_argument('--profile', choices=sorted(PROFILES), default='animatic')
    ap.add_argument('--size', help='WxH (default from the profile: 960x540 or 1920x1080)')
    ap.add_argument('--crf', type=int)
    ap.add_argument('--preset')
    bi = ap.add_mutually_exclusive_group()
    bi.add_argument('--burn-in', dest='burn_in', action='store_true', default=None, help='shot id + timecode + frame')
    bi.add_argument('--no-burn-in', dest='burn_in', action='store_false')
    ap.add_argument('--grain', type=float, help='grain strength (0 = off; HF used 0.035)')
    ap.add_argument('--grain-mode', choices=['static', 'dynamic'],
                    help='dynamic = new field per frame (default for preview/master), static = one seeded field per '
                         'shot (HARVEST 6; reads as a dirty lens)')
    ap.add_argument('--no-phase-grade', dest='phase_grade', action='store_false', help='turn the phase grades and the print off (shot grades stay)')
    ap.add_argument('--letterbox-open', type=int, default=0, help='frames over which the bars open from the hit (0 = cut)')
    ap.add_argument('--audio', default=str(SONG), help='audio (default: the song, untouched); e.g. a mix wav')
    ap.add_argument('--abr', help='AAC bitrate (default from the profile)')
    ap.add_argument('--range', help='A1:C4 (inclusive): render and join only these shots')
    ap.add_argument('--only', help='C3,G4: render only these shots (no join)')
    ap.add_argument('--jobs', type=int, default=max(1, min(8, (os.cpu_count() or 4) // 3)))
    ap.add_argument('--force', action='store_true', help='re-render every selected shot')
    ap.add_argument('--shots', default=str(SHOTS))
    ap.add_argument('--picks', default=str(PICKS))
    args = ap.parse_args()

    prof = dict(PROFILES[args.profile])
    W, H = (int(x) for x in (args.size or prof['size']).split('x'))
    data = load_json(args.shots)
    shots, meta = data['shots'], data['meta']
    picks_doc = load_json(args.picks) if Path(args.picks).exists() else {}
    picks = {k: v for k, v in (picks_doc.get('picks') or {}).items() if not k.startswith('_')}
    unknown = set(picks) - {s['id'] for s in shots}
    if unknown:
        sys.exit(f'picks.json names unknown shots: {sorted(unknown)}')
    phase_grades = {k: v for k, v in (picks_doc.get('phase_grades') or {}).items() if not k.startswith('_')}
    o = dict(W=W, H=H, crf=args.crf if args.crf is not None else prof['crf'], preset=args.preset or prof['preset'],
             tune=prof['tune'], burn_in=prof['burn_in'] if args.burn_in is None else args.burn_in,
             grain=prof['grain'] if args.grain is None else args.grain,
             grain_mode=args.grain_mode or prof['grain_mode'],
             phase_grade=args.phase_grade, phase_grades=phase_grades,
             lb_frame=meta['letterbox_until']['frame'], lb_open=args.letterbox_open,
             threads=max(2, (os.cpu_count() or 4) // max(1, args.jobs)))
    abr = args.abr or prof['abr']

    sel = select_range(shots, args.range, args.only)
    root = ROOT / 'work' / 'edit' / args.name
    sdir = root / 'shots'
    sdir.mkdir(parents=True, exist_ok=True)
    code = code_sig()
    jobs, cached = [], []
    for s in sel:
        pick = picks.get(s['id'])
        key = shot_key(s, pick, o, code)
        out = sdir / f'{s["id"]}.mp4'
        side = out.with_suffix('.json')
        if not args.force and out.exists() and side.exists():
            m = json.loads(side.read_text())
            if m.get('key') == key and m.get('frames') == s['out_frame'] - s['in_frame']:
                cached.append(m)
                continue
        jobs.append(dict(shot=s, pick=pick, opts=o, out=str(out), key=key))
    print(f'{args.name}: {len(sel)} shots selected, {len(cached)} cached, {len(jobs)} to render at {W}x{H} '
          f'(crf {o["crf"]}, burn-in {o["burn_in"]}, grain {o["grain"]}, phase grade {o["phase_grade"]}, '
          f'letterbox open {o["lb_open"]} f)')
    results = {m['id']: m for m in cached}
    t0 = time.time()
    with cf.ProcessPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(render_shot, j): j['shot']['id'] for j in jobs}
        for fu in cf.as_completed(futs):
            m = fu.result()
            results[m['id']] = m
            print(f'  {m["id"]:4s} {m["kind"]:6s} {m["frames"]:4d} f  {m["secs"]:5.1f} s'
                  + (f'  ** {m["problem"]}' if m.get('problem') else ''), flush=True)
    print(f'rendered {len(jobs)} shots in {time.time() - t0:.1f} s')

    problems = [(i, results[i]['problem']) for i in [s['id'] for s in sel] if results[i].get('problem')]
    log = dict(name=args.name, opts={k: v for k, v in o.items() if k != 'phase_grades'}, audio=args.audio,
               shots={s['id']: {k: results[s['id']].get(k) for k in ('kind', 'status', 'problem', 'frames')} for s in sel})
    exit_code = 0
    if args.only:
        print('--only: shots rendered, not joined')
    else:
        # contiguous selection -> join
        n = sum(s['out_frame'] - s['in_frame'] for s in sel)
        full = len(sel) == len(shots)
        out = root / (f'chaosmonkey_{args.name}.mp4' if full else f'chaosmonkey_{args.name}_{sel[0]["id"]}-{sel[-1]["id"]}.mp4')
        audio = rel(args.audio)
        if full:
            a_start, a_dur, a_exp = None, None, wav_duration(audio)
        else:
            a_start, a_dur = sel[0]['in_frame'] / FPS, n / FPS
            a_exp = a_dur
        part = join([sdir / f'{s["id"]}.mp4' for s in sel], audio, a_start, a_dur, out, abr)
        res, bad = verify(part, n, a_exp)
        log['verify'] = res
        log['verify_problems'] = bad
        if bad:
            print('VERIFY FAILED (left as .partial):')
            for b in bad:
                print('  ' + b)
            exit_code = 2
        else:
            os.replace(part, out)
            print(f'wrote {out.relative_to(ROOT)}: {res["frames"]} frames, video {res["video_s"]:.4f} s, audio '
                  f'{res["audio_s"]:.4f} s, {res["size"]} {res["pix_fmt"]} {res["color"]}')
    (root / 'render_log.json').write_text(json.dumps(log, indent=1, default=str))
    if problems:
        print('\nSHOTS SLATED BECAUSE THEIR PICK COULD NOT FILL THEM:')
        for i, p in problems:
            print(f'  {i:4s} {p}')
        exit_code = exit_code or 3
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

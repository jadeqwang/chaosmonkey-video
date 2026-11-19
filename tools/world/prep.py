#!/usr/bin/env python3
"""tools/world/prep.py: turn a painted element (ink on bare paper) into a relief card for the 3D world.

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    $PY tools/world/prep.py IMG [IMG ...] --out design/world/cards [--name NAME] [--crop x,y,w,h]
        [--solid 0.5] [--keylo 0.035] [--keyhi 0.20] [--maxside 3072] [--nodepth] [--sam]

Writes, per element NAME (default: image basename):
    NAME_rgba.png    colour divided by the plate's own paper (so it sits on the world's paper) + alpha
    NAME_depth.png   16-bit grey, Depth-Anything-V2-Large, normalised inside the alpha: 65535 = nearest
    NAME.json        {w, h, aspect, paper_rgb, bbox_px, src}
Alpha = max(ink key, filled silhouette): washes and pine needles stay translucent at their edges, the body of a rock
is opaque (far rock never shows through near rock). --solid scales how much of the key is filled solid (0 = key only,
for mist-like or very wet elements). The paper colour is estimated from the border of the image.
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DA = None


def depth_model():
    global _DA
    if _DA is None:
        import torch
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        name = 'depth-anything/Depth-Anything-V2-Large-hf'
        proc = AutoImageProcessor.from_pretrained(name)
        model = AutoModelForDepthEstimation.from_pretrained(name).to('cuda').eval()
        _DA = (proc, model, torch)
    return _DA


def depth_of(rgb, long_side=1036):
    """Relative inverse depth (bigger = nearer), same size as rgb. Runs at ~1036 px on the long side (multiple of 14)."""
    proc, model, torch = depth_model()
    h, w = rgb.shape[:2]
    s = long_side / max(h, w)
    sw, sh = int(round(w * s / 14)) * 14, int(round(h * s / 14)) * 14
    small = cv2.resize(rgb, (sw, sh), interpolation=cv2.INTER_AREA)
    inp = proc(images=Image.fromarray(small), return_tensors='pt', do_resize=False, do_rescale=True)
    with torch.no_grad():
        pv = inp['pixel_values'].to('cuda')
        out = model(pixel_values=pv).predicted_depth[0].float().cpu().numpy()
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_CUBIC)


def save_depth(path, dn):
    """Depth 0..1 (1 = nearest) packed in an 8-bit RGB PNG: R = high byte, G = low byte (browsers load PNGs as 8 bit)."""
    v = (np.clip(dn, 0, 1) * 65535).astype(np.uint32)
    rgb = np.dstack([(v >> 8).astype(np.uint8), (v & 255).astype(np.uint8), (v >> 8).astype(np.uint8)])
    Image.fromarray(rgb, 'RGB').save(path)


def load_depth(path):
    a = np.array(Image.open(path).convert('RGB')).astype(np.float32)
    return (a[..., 0] * 256 + a[..., 1]) / 65535


def fill_depth(dn, a, blur_px=2.0, body=None):
    """Depth without cliffs at the silhouette. The solid body (minus a rim, where Depth-Anything puts edges far) keeps
    its depth; everything else (pines, wisps, the rim, outside) takes the depth of the nearest body edge, propagated
    outward by grey dilation, so thin parts sit on the rock they grow from and the mesh never stretches at an edge."""
    h, w = dn.shape
    m = (body if body is not None else (a > 0.85)).astype(np.uint8)
    r = max(4, int(max(h, w) * 0.006))
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    if m.sum() < 50:
        return np.full_like(dn, 0.5)
    acc = np.where(m > 0, dn, 0).astype(np.float32)
    filled = m.copy()
    k5 = np.ones((5, 5), np.uint8)
    # work at quarter size for speed, then upsample the fill
    sm = cv2.resize(acc, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    sf = cv2.resize(filled.astype(np.float32), (w // 4, h // 4), interpolation=cv2.INTER_AREA) > 0.99
    sm = np.where(sf, sm, 0)
    for _ in range(max(h, w) // 8):
        if sf.all():
            break
        d2 = cv2.dilate(sm, k5)
        f2 = cv2.dilate(sf.astype(np.uint8), k5) > 0
        new = f2 & ~sf
        sm[new] = d2[new]
        sf = f2
    sm[~sf] = dn[m > 0].mean()
    sm = cv2.GaussianBlur(sm, (0, 0), 3)
    fillv = cv2.resize(sm, (w, h), interpolation=cv2.INTER_CUBIC)
    k = cv2.GaussianBlur(cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r + 1, r + 1))).astype(np.float32), (0, 0), r * 0.5)
    res = dn * k + fillv * (1 - k)
    if blur_px:
        res = cv2.GaussianBlur(res, (0, 0), blur_px)
    return np.clip(res, 0, 1)


def paper_colour(rgb):
    b = max(8, min(rgb.shape[:2]) // 40)
    border = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3), rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
    lum = border.mean(1)
    keep = border[lum >= np.percentile(lum, 40)]
    return np.median(keep, 0)


def key_alpha(rgb, paper, lo, hi):
    """How much ink / pigment is on the paper at each pixel (0 bare .. 1 covered)."""
    f = rgb.astype(np.float32)
    trans = f / np.maximum(paper[None, None], 1)                     # 1 = bare paper
    dark = 1 - trans.min(2)                                          # ink darkness
    sat = (f.max(2) - f.min(2)) / 255 - (paper.max() - paper.min()) / 255   # pigment saturation above the paper's
    k = np.maximum(dark, sat * 1.3)
    k = cv2.GaussianBlur(k, (0, 0), 1.0)
    key_alpha.raw = k
    return np.clip((k - lo) / (hi - lo), 0, 1)


def silhouette(k, solid, min_frac=0.002):
    """Fill the body of the painted mass: threshold the key, close gaps, fill holes, keep big components."""
    h, w = k.shape
    m = (k > 0.35).astype(np.uint8)
    r = max(3, int(min(h, w) * 0.012))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    # fill holes
    ff = m.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 1)
    holes = (ff == 0)
    m = np.maximum(m, holes.astype(np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= min_frac * h * w:
            keep[lab == i] = 1
    # erode a little so the filled body never extends past the painted edge, then feather
    # the solid body is the massive rock only: an opening with a big kernel removes pines, branches and spurs, which
    # keep their own (translucent) ink key
    R = max(5, int(min(h, w) * 0.035))
    keep = cv2.morphologyEx(keep, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * R + 1, 2 * R + 1)))
    e = max(1, r // 3)
    keep = cv2.erode(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * e + 1, 2 * e + 1)))
    soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), max(1.0, e * 0.8))
    return np.clip(soft * solid, 0, 1)


def prep(src, out, name=None, crop=None, solid=1.0, lo=0.035, hi=0.20, maxside=3072, nodepth=False, depth_blur=None):
    name = name or os.path.splitext(os.path.basename(src))[0]
    rgb = np.array(Image.open(src).convert('RGB'))
    if crop:
        x, y, w, h = crop
        rgb = rgb[y:y + h, x:x + w]
    s = min(1.0, maxside / max(rgb.shape[:2]))
    if s < 1:
        rgb = cv2.resize(rgb, (int(rgb.shape[1] * s), int(rgb.shape[0] * s)), interpolation=cv2.INTER_AREA)
    paper = paper_colour(rgb)
    k = key_alpha(rgb, paper, lo, hi)
    if solid > 0:
        # the filled body is solid only where there is pigment: bare paper between pine needles stays transparent
        pig = cv2.GaussianBlur(key_alpha.raw, (0, 0), 2.0)
        pig = np.clip((pig - 0.012) / 0.04, 0, 1)
        a = np.maximum(k, silhouette(k, solid) * pig)
    else:
        a = k
    # colour relative to the plate's paper (1 = paper); stored as rgb * (world paper 236,226,204 / plate paper) later
    # in the shader. Here: normalise to a neutral paper of (240, 232, 214) so all cards share one paper.
    ref = np.array([240, 232, 214], np.float32)
    col = np.clip(rgb.astype(np.float32) / paper[None, None] * ref[None, None], 0, 255)
    # unpremultiply-safe: where alpha is low, colour is the ink colour (keep), bleed the colour outward a little
    rgba = np.dstack([col, a * 255]).astype(np.uint8)
    os.makedirs(out, exist_ok=True)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(out, name + '_rgba.png'), optimize=False)
    ys, xs = np.where(a > 0.05)
    meta = dict(src=os.path.relpath(src, ROOT), w=rgb.shape[1], h=rgb.shape[0], aspect=rgb.shape[1] / rgb.shape[0],
                paper_rgb=[float(v) for v in paper], bbox_px=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None)
    if not nodepth:
        d = depth_of(rgb)
        inside = a > 0.5
        if inside.sum() > 100:
            lo_d, hi_d = np.percentile(d[inside], 1), np.percentile(d[inside], 99.5)
        else:
            lo_d, hi_d = d.min(), d.max()
        dn = np.clip((d - lo_d) / max(hi_d - lo_d, 1e-6), 0, 1)
        dn = fill_depth(dn, a, depth_blur if depth_blur is not None else max(rgb.shape[:2]) * 0.004)
        save_depth(os.path.join(out, name + '_depth.png'), dn)
    json.dump(meta, open(os.path.join(out, name + '.json'), 'w'), indent=1)
    return meta


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('imgs', nargs='+')
    ap.add_argument('--out', default=os.path.join(ROOT, 'design/world/cards'))
    ap.add_argument('--name')
    ap.add_argument('--crop')
    ap.add_argument('--solid', type=float, default=1.0)
    ap.add_argument('--keylo', type=float, default=0.035)
    ap.add_argument('--keyhi', type=float, default=0.20)
    ap.add_argument('--maxside', type=int, default=3072)
    ap.add_argument('--nodepth', action='store_true')
    a = ap.parse_args()
    for im in a.imgs:
        m = prep(im, a.out, a.name if len(a.imgs) == 1 else None, [int(v) for v in a.crop.split(',')] if a.crop else None,
                 a.solid, a.keylo, a.keyhi, a.maxside, a.nodepth)
        print(im, '->', a.out, m['w'], 'x', m['h'])

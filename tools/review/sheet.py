#!/usr/bin/env python3
"""Frame sheets and 1:1 crops for any clip (not tied to bake-off names).

  sheet.py sheet CLIP.mp4 OUT.jpg [--n=10] [--cols=5] [--w=768] [--t=a,b,c ...] [--from=S] [--to=S]
      N evenly spaced frames (or the listed times), labelled with source seconds and frame number.
  sheet.py crop CLIP.mp4 OUT.jpg x y w h t1 t2 ... [--scale=1]
      the same region (x y w h in 1920x1080 coords) at each time, side by side, 1:1 unless --scale.
  sheet.py frame CLIP.mp4 OUT.png t
      one full-resolution frame (nearest frame to t).
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except OSError:
        return ImageFont.load_default()


def read_all(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr, fps


def label(img, text, sz=22):
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(im)
    f = font(sz)
    d.rectangle([0, 0, d.textlength(text, font=f) + 12, sz + 10], fill=(0, 0, 0))
    d.text((6, 4), text, fill=(255, 255, 0), font=f)
    return im


def opts(args):
    o, rest = {}, []
    for a in args:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            o[k] = v
        else:
            rest.append(a)
    return o, rest


def sheet(clip, out, o):
    fr, fps = read_all(clip)
    n = len(fr)
    if "t" in o:
        idx = [min(n - 1, round(float(t) * fps)) for t in o["t"].split(",")]
    else:
        k = int(o.get("n", 10))
        a = round(float(o.get("from", 0)) * fps)
        b = min(n - 1, round(float(o["to"]) * fps)) if "to" in o else n - 1
        idx = [round(a + (b - a) * i / (k - 1)) for i in range(k)]
    cols, w = int(o.get("cols", 5)), int(o.get("w", 768))
    tiles = []
    for i in idx:
        f = fr[i]
        h = round(f.shape[0] * w / f.shape[1])
        tiles.append(label(cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA), f"{i / fps:.2f}s f{i}"))
    rows = (len(tiles) + cols - 1) // cols
    th = tiles[0].height
    canvas = Image.new("RGB", (cols * w, rows * th + 36), (20, 20, 20))
    ImageDraw.Draw(canvas).text((8, 6), f"{os.path.basename(clip)}  {n} frames @ {fps:g} fps  "
                                f"{fr[0].shape[1]}x{fr[0].shape[0]}", fill=(255, 255, 255), font=font(22))
    for k, t in enumerate(tiles):
        canvas.paste(t, ((k % cols) * w, 36 + (k // cols) * th))
    canvas.save(out, quality=88)
    print(out)


def crop(clip, out, a, o):
    x, y, w, h = map(int, a[:4])
    times = [float(t) for t in a[4:]]
    fr, fps = read_all(clip)
    sx, sy = fr[0].shape[1] / 1920, fr[0].shape[0] / 1080
    sc = float(o.get("scale", 1))
    tiles = []
    for t in times:
        i = min(len(fr) - 1, round(t * fps))
        c = fr[i][round(y * sy):round((y + h) * sy), round(x * sx):round((x + w) * sx)]
        if sc != 1:
            c = cv2.resize(c, (round(c.shape[1] * sc), round(c.shape[0] * sc)), interpolation=cv2.INTER_AREA)
        tiles.append(label(c, f"{i / fps:.2f}s f{i}", 18))
    canvas = Image.new("RGB", (sum(t.width for t in tiles) + 4 * (len(tiles) - 1), tiles[0].height), (0, 0, 0))
    xx = 0
    for t in tiles:
        canvas.paste(t, (xx, 0))
        xx += t.width + 4
    canvas.save(out, quality=92)
    print(out)


def frame(clip, out, t):
    fr, fps = read_all(clip)
    i = min(len(fr) - 1, round(float(t) * fps))
    cv2.imwrite(out, fr[i])
    print(out, f"f{i}")


def main():
    o, a = opts(sys.argv[1:])
    if len(a) < 3:
        raise SystemExit(__doc__)
    os.makedirs(os.path.dirname(os.path.abspath(a[2])), exist_ok=True)
    if a[0] == "sheet":
        sheet(a[1], a[2], o)
    elif a[0] == "crop":
        crop(a[1], a[2], a[3:], o)
    elif a[0] == "frame":
        frame(a[1], a[2], a[3])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

"""Bake-off sheets.

  sheets  : per clip, 10 evenly spaced frames, 5x2 at 768 px wide, labelled -> work/review/bakeoff/sheets/<tag>.jpg
  compare : per shot and time, all models tiled (3 cols x 640 px) -> work/review/bakeoff/cmp/<SHOT>_t<sec>.jpg
  crop    : 1:1 crops of one region for all models at given times -> work/review/bakeoff/crops/<SHOT>_<name>.jpg

usage:
  bakeoff_sheets.py sheets [SHOT ...]
  bakeoff_sheets.py compare SHOT t1 t2 ...
  bakeoff_sheets.py crop SHOT name x y w h t1 t2 ... [--models=a,b] [--scale=1]   (x y w h in 1920x1080 keyframe coords)
"""
import glob, os, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "work/review/bakeoff")
ORDER = ["veo31", "kling4", "sd20", "sd25", "hh11", "wan27", "omni12", "gen45", "vidu3"]
NAMES = {"veo31": "Veo 3.1", "kling4": "Kling v4", "sd20": "Seedance 2.0", "sd25": "Seedance 2.5 (720p)",
         "hh11": "HappyHorse 1.1", "wan27": "Wan 2.7", "omni12": "Gemini Omni 1.2 Flash", "gen45": "Runway Gen-4.5 (720p)",
         "vidu3": "Vidu Q3 Pro"}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except OSError:
        return ImageFont.load_default()


def clips(shot):
    out = {}
    for p in glob.glob(os.path.join(ROOT, f"media/gen/bk_{shot}_*_t1_*.mp4")):
        out[os.path.basename(p).split("_")[2]] = p
    return {m: out[m] for m in ORDER if m in out}


def read_all(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr, fps


def fit(img, W, H):
    """letterbox into WxH keeping aspect"""
    h, w = img.shape[:2]
    s = min(W / w, H / h)
    r = cv2.resize(img, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((H, W, 3), np.uint8)
    y, x = (H - r.shape[0]) // 2, (W - r.shape[1]) // 2
    canvas[y:y + r.shape[0], x:x + r.shape[1]] = r
    return canvas


def label(img_bgr, text, sz=22):
    im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(im)
    f = font(sz)
    bb = d.textbbox((0, 0), text, font=f)
    d.rectangle([0, 0, bb[2] + 12, bb[3] + 10], fill=(0, 0, 0))
    d.text((6, 4), text, font=f, fill=(255, 230, 120))
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def sheets(shots):
    os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
    for shot in shots:
        for m, p in clips(shot).items():
            fr, fps = read_all(p)
            n = len(fr)
            idx = [round(i * (n - 1) / 9) for i in range(10)]
            tiles = []
            for i in idx:
                t = fit(fr[i], 768, 432)
                tiles.append(label(t, f"{shot} {NAMES[m]}  f{i}  {i / fps:.2f}s", 18))
            rows = [np.hstack(tiles[r * 5:(r + 1) * 5]) for r in range(2)]
            tag = os.path.basename(p).replace(".mp4", "")
            cv2.imwrite(os.path.join(OUT, "sheets", tag + ".jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
            print("sheet", tag)


def compare(shot, times, cols=3, tw=640):
    os.makedirs(os.path.join(OUT, "cmp"), exist_ok=True)
    cl = clips(shot)
    data = {m: read_all(p) for m, p in cl.items()}
    kf = cv2.imread(os.path.join(ROOT, f"media/kf/{shot}_pick_1080.jpg"))
    th = tw * 9 // 16
    for t in times:
        tiles = []
        for m, (fr, fps) in data.items():
            i = min(int(round(t * fps)), len(fr) - 1)
            tiles.append(label(fit(fr[i], tw, th), f"{NAMES[m]}  {i / fps:.2f}s", 18))
        if t == 0:
            tiles.insert(0, label(fit(kf, tw, th), "KEYFRAME", 18))
        while len(tiles) % cols:
            tiles.append(np.zeros((th, tw, 3), np.uint8))
        rows = [np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)]
        out = os.path.join(OUT, "cmp", f"{shot}_t{t:04.1f}.jpg")
        cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(out)


def crop(shot, name, x, y, w, h, times, models=None, scale=1.0):
    """1:1 crop (in 1080p coordinates; clips at other sizes are resized to 1920x1080 first, 21:9 letterboxed)"""
    os.makedirs(os.path.join(OUT, "crops"), exist_ok=True)
    cl = clips(shot)
    if models:
        cl = {m: p for m, p in cl.items() if m in models}
    rows = []
    for m, p in cl.items():
        fr, fps = read_all(p)
        row = []
        for t in times:
            i = min(int(round(t * fps)), len(fr) - 1)
            f = fr[i]
            if f.shape[:2] != (1080, 1920):
                f = fit(f, 1920, 1080)
            c = f[y:y + h, x:x + w]
            if scale != 1.0:
                c = cv2.resize(c, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA)
            row.append(label(c.copy(), f"{m} {i / fps:.2f}s", 14))
        rows.append(np.hstack(row))
    out = os.path.join(OUT, "crops", f"{shot}_{name}.jpg")
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    opts = {k[2:].split("=")[0]: k.split("=", 1)[1] for k in a if k.startswith("--")}
    a = [x for x in a if not x.startswith("--")]
    if a[0] == "sheets":
        sheets(a[1:] or ["A1", "C2", "C7", "C9", "F1"])
    elif a[0] == "compare":
        compare(a[1], [float(t) for t in a[2:]])
    elif a[0] == "crop":
        crop(a[1], a[2], *map(int, a[3:7]), [float(t) for t in a[7:]],
             models=opts.get("models", "").split(",") if opts.get("models") else None, scale=float(opts.get("scale", 1)))

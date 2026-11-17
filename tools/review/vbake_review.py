#!/usr/bin/env python3
"""Review for the video bake-off (docs/VIDEO_BAKEOFF.md): measures, contact sheets and synced grids.

    $PY tools/review/vbake_review.py intake TEST [CLIP ...]   # metrics for media/vbake/TEST/*.mp4 (+ 10-frame sheets)
    $PY tools/review/vbake_review.py grid TEST [--cols=4]     # work/review/bakeoff/vbake_TEST_grid.mp4 (synced, labelled)
    $PY tools/review/vbake_review.py compare TEST t1 t2 ...   # media/vbake/_sheets/TEST_cmp.jpg: every model at each time

Metrics (all on a 480-px-wide copy unless noted), written to work/review/bakeoff/vbake_TEST.json:
  ff_corr / ff_ssim  first frame vs the input still (the still resized to the clip's frame)
  ff_reframe         ORB similarity still -> frame 0 (scale, dx, dy in 960-px units): did the model recompose?
  cam_max / zoom     camera drift: ORB similarity frame 0 -> every 6th frame, max shift (960-px units) and zoom range
  flow / flow95      Farneback mean flow per frame (px at 480), mean and 95th percentile over the clip
  std_ink_up         median per-pixel temporal std (grey, 0-255) over the upper two thirds of what is ink in frame 0
                     (for V1: the rock above the mist band; ~0.5 = locked like a still, >3 = the painting is redrawing)
  std_paper          the same over bare-paper pixels; moving% = share of pixels with temporal std > 6
  cov0/covmax/covend ink coverage (coverage.py rule, paper colour from frame 0) at the first, max and last sampled frame
  new_ink / lost_ink % of pixels that are paper in frame 0 and ink at the end (invented marks), and the reverse
  chroma0 / chromaend mean chroma (Lab a,b distance from the paper colour): invented colour shows as a rise
  dups               frames identical to the previous one (stutter / frame repeats)
"""
import glob
import json
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VB = os.path.join(ROOT, "media", "vbake")
SHEETS = os.path.join(VB, "_sheets")
REV = os.path.join(ROOT, "work", "review", "bakeoff")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
sys.path.insert(0, os.path.join(ROOT, "tools", "gen"))


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


def first_still(test):
    import vbake
    return os.path.join(ROOT, vbake.TESTS[test]["first"])


def ssim(a, b):
    a = a.astype(np.float64); b = b.astype(np.float64)
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu1 = cv2.GaussianBlur(a, (11, 11), 1.5); mu2 = cv2.GaussianBlur(b, (11, 11), 1.5)
    s1 = cv2.GaussianBlur(a * a, (11, 11), 1.5) - mu1 ** 2
    s2 = cv2.GaussianBlur(b * b, (11, 11), 1.5) - mu2 ** 2
    s12 = cv2.GaussianBlur(a * b, (11, 11), 1.5) - mu1 * mu2
    return float((((2 * mu1 * mu2 + C1) * (2 * s12 + C2)) / ((mu1 ** 2 + mu2 ** 2 + C1) * (s1 + s2 + C2))).mean())


ORB = cv2.ORB_create(3000)


def similarity(a, b):
    ka, da = ORB.detectAndCompute(a, None)
    kb, db = ORB.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 15 or len(kb) < 15:
        return None
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
    if len(m) < 15:
        return None
    pa = np.float32([ka[x.queryIdx].pt for x in m]); pb = np.float32([kb[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=3)
    if M is None or inl.sum() < 10:
        return None
    sc = float(np.hypot(M[0, 0], M[1, 0]))
    W, H = a.shape[1], a.shape[0]
    c = np.array([W / 2, H / 2])
    cx, cy = M[:, :2] @ c + M[:, 2] - c
    return dict(scale=round(sc, 4), dx=round(float(cx), 1), dy=round(float(cy), 1), inliers=int(inl.sum()))


def paper_of(img):
    a = cv2.GaussianBlur(img, (0, 0), 2).astype(np.float32)
    L = a @ np.array([.114, .587, .299], np.float32)
    return np.median(a[L >= np.percentile(L, 60)], axis=0)


def marks(img, paper, thr=28):
    a = cv2.GaussianBlur(img, (0, 0), 2).astype(np.float32)
    return np.abs(a - paper).max(2) > thr


def chroma(img, paper):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    pl = cv2.cvtColor(np.uint8(paper.reshape(1, 1, 3)), cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]
    return float(np.hypot(lab[..., 1] - pl[1], lab[..., 2] - pl[2]).mean())


def analyse(path, still):
    fr, fps = read_all(path)
    if not fr:
        return None
    H0, W0 = fr[0].shape[:2]
    W, H = 480, round(480 * H0 / W0)
    small = [cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA) for f in fr]
    grey = [cv2.cvtColor(s, cv2.COLOR_BGR2GRAY) for s in small]
    r = dict(file=os.path.relpath(path, ROOT), w=W0, h=H0, fps=round(fps, 3), frames=len(fr), dur=round(len(fr) / fps, 2))
    try:
        import gen
        r["audio"] = any(s["codec_type"] == "audio" for s in gen.probe(path)["streams"])
    except Exception:  # noqa: BLE001
        pass
    st = cv2.imread(still)
    if st is not None:
        sh, sw = st.shape[:2]
        # fit the still into the clip aspect (centre crop) before comparing
        ar = W0 / H0
        if abs(sw / sh - ar) > 0.01:
            if sw / sh > ar:
                nw = round(sh * ar); st = st[:, (sw - nw) // 2:(sw - nw) // 2 + nw]
            else:
                nh = round(sw / ar); st = st[(sh - nh) // 2:(sh - nh) // 2 + nh]
        sg = cv2.cvtColor(cv2.resize(st, (W, H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        r["ff_corr"] = round(float(np.corrcoef(sg.ravel(), grey[0].ravel())[0, 1]), 3)
        r["ff_ssim"] = round(ssim(sg, grey[0]), 3)
        r["ff_reframe"] = similarity(cv2.resize(cv2.cvtColor(st, cv2.COLOR_BGR2GRAY), (960, round(960 * H / W))),
                                     cv2.resize(cv2.cvtColor(fr[0], cv2.COLOR_BGR2GRAY), (960, round(960 * H / W))))
    # camera drift
    g960 = [cv2.resize(cv2.cvtColor(fr[i], cv2.COLOR_BGR2GRAY), (960, round(960 * H / W))) for i in range(0, len(fr), 6)]
    sims = [similarity(g960[0], g) for g in g960[1:]]
    ok = [s for s in sims if s]
    if ok:
        r["cam_max"] = round(max(np.hypot(s["dx"], s["dy"]) for s in ok), 1)
        r["zoom"] = [round(min(s["scale"] for s in ok), 3), round(max(s["scale"] for s in ok), 3)]
        r["cam_end"] = ok[-1]
    r["cam_lost"] = len(sims) - len(ok)
    # flow
    mags = []
    for i in range(1, len(grey)):
        f = cv2.calcOpticalFlowFarneback(grey[i - 1], grey[i], None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mags.append(float(np.hypot(f[..., 0], f[..., 1]).mean()))
    r["flow"] = round(float(np.mean(mags)), 3) if mags else 0
    r["flow95"] = round(float(np.percentile(mags, 95)), 3) if mags else 0
    r["flow_per_s"] = [round(float(np.mean(mags[int(s * fps):int((s + 1) * fps)])), 2)
                       for s in range(int(np.ceil(len(mags) / fps))) if mags[int(s * fps):int((s + 1) * fps)]]
    r["dups"] = int(sum(np.abs(grey[i].astype(int) - grey[i - 1].astype(int)).mean() < 0.15 for i in range(1, len(grey))))
    # temporal stability
    stack = np.stack(grey).astype(np.float32)
    std = stack.std(0)
    paper = paper_of(small[0])
    m0 = marks(small[0], paper)
    ys, xs = np.nonzero(m0)
    if len(ys) > 50:
        y0, y1 = np.percentile(ys, 2), np.percentile(ys, 98)
        up = m0 & (np.arange(H)[:, None] < y0 + (y1 - y0) * 2 / 3)
        r["std_ink_up"] = round(float(np.median(std[up])), 2) if up.any() else None
        r["std_ink"] = round(float(np.median(std[m0])), 2)
    r["std_paper"] = round(float(np.median(std[~m0])), 2) if (~m0).any() else None
    r["moving_pct"] = round(float((std > 6).mean() * 100), 1)
    # coverage drift and invented marks / colour
    idx = np.linspace(0, len(fr) - 1, 10).round().astype(int)
    covs = [float(marks(small[i], paper).mean() * 100) for i in idx]
    r["cov0"], r["covmax"], r["covend"] = round(covs[0], 1), round(max(covs), 1), round(covs[-1], 1)
    mend = marks(small[-1], paper)
    r["new_ink"] = round(float((mend & ~m0).mean() * 100), 2)
    r["lost_ink"] = round(float((m0 & ~mend).mean() * 100), 2)
    r["chroma0"], r["chromaend"] = round(chroma(small[0], paper), 2), round(chroma(small[-1], paper), 2)
    lum = [float(g.mean()) for g in grey]
    r["lum_range"] = round(max(lum) - min(lum), 1)
    return r


def label(img, text, sz=22):
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(im)
    f = font(sz)
    d.rectangle([0, 0, d.textlength(text, font=f) + 12, sz + 10], fill=(0, 0, 0))
    d.text((6, 4), text, fill=(255, 230, 120), font=f)
    return im


def sheet(path, out, n=10, cols=5, w=576):
    fr, fps = read_all(path)
    idx = np.linspace(0, len(fr) - 1, n).round().astype(int)
    tiles = []
    for i in idx:
        f = fr[i]
        h = round(f.shape[0] * w / f.shape[1])
        tiles.append(label(cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA), f"{i / fps:.2f}s"))
    rows = (len(tiles) + cols - 1) // cols
    th = tiles[0].height
    canvas = Image.new("RGB", (cols * w, rows * th + 34), (20, 20, 20))
    ImageDraw.Draw(canvas).text((8, 6), f"{os.path.relpath(path, VB)}  {len(fr)} f @ {fps:g} fps  {fr[0].shape[1]}x{fr[0].shape[0]}",
                                fill=(255, 255, 255), font=font(20))
    for k, t in enumerate(tiles):
        canvas.paste(t, ((k % cols) * w, 34 + (k // cols) * th))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    canvas.save(out, quality=85)
    return out


def clips(test):
    return sorted(glob.glob(os.path.join(VB, test, "*.mp4")))


def intake(test, only=None):
    os.makedirs(REV, exist_ok=True)
    jp = os.path.join(REV, f"vbake_{test}.json")
    allr = json.load(open(jp)) if os.path.exists(jp) else {}
    still = first_still(test)
    for p in clips(test):
        name = os.path.basename(p)[:-4]
        if only and name not in only:
            continue
        r = analyse(p, still)
        if r is None:
            print(name, "unreadable"); continue
        allr[name] = r
        sheet(p, os.path.join(SHEETS, test, name + ".jpg"))
        print(f"{test} {name:18s} {r['w']}x{r['h']} {r['fps']:g}fps {r['dur']}s aud={int(r.get('audio', 0))} "
              f"ff={r.get('ff_corr')}/{r.get('ff_ssim')} rf={(r.get('ff_reframe') or {}).get('scale')} "
              f"cam={r.get('cam_max')} z={r.get('zoom')} flow={r['flow']} stdInkUp={r.get('std_ink_up')} "
              f"stdPaper={r.get('std_paper')} mov={r['moving_pct']}% cov={r['cov0']}/{r['covmax']}/{r['covend']} "
              f"new={r['new_ink']} lost={r['lost_ink']} chroma={r['chroma0']}->{r['chromaend']} dups={r['dups']}", flush=True)
        json.dump(allr, open(jp, "w"), indent=1)


def grid(test, cols=4, tw=480, th=270):
    items = clips(test)
    if not items:
        return
    durs = []
    for p in items:
        fr = cv2.VideoCapture(p)
        durs.append(fr.get(cv2.CAP_PROP_FRAME_COUNT) / (fr.get(cv2.CAP_PROP_FPS) or 24))
    longest = max(durs)
    n = len(items)
    rows = (n + cols - 1) // cols
    inputs, f = [], []
    for i, p in enumerate(items):
        inputs += ["-i", p]
        lab = os.path.basename(p)[:-4].replace(":", r"\:")
        f.append(f"[{i}:v]fps=24,scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:black,"
                 f"setsar=1,tpad=stop_mode=clone:stop_duration={longest:.3f},trim=duration={longest:.3f},setpts=PTS-STARTPTS,"
                 f"drawtext=fontfile={FONT}:text='{lab}':x=6:y=6:fontsize=18:fontcolor=0xFFE678:box=1:boxcolor=black@0.7:boxborderw=4,"
                 f"drawtext=fontfile={FONT}:text='%{{pts\\:flt}}':x=w-tw-6:y=6:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=3[v{i}]")
    for k in range(n, rows * cols):
        f.append(f"color=c=black:s={tw}x{th}:r=24:d={longest:.3f}[v{k}]")
    layout = "|".join(f"{(j % cols) * tw}_{(j // cols) * th}" for j in range(rows * cols))
    f.append("".join(f"[v{j}]" for j in range(rows * cols)) + f"xstack=inputs={rows * cols}:layout={layout},format=yuv420p[out]")
    out = os.path.join(REV, f"vbake_{test}_grid.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f), "-map", "[out]", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "21", "-movflags", "+faststart", "-an", out], check=True)
    print(out, f"{n} clips {longest:.2f}s")


def compare(test, times, w=480):
    items = clips(test)
    rows = []
    for p in items:
        fr, fps = read_all(p)
        tiles = []
        for t in times:
            i = min(len(fr) - 1, round(t * fps))
            f = fr[i]
            tiles.append(label(cv2.resize(f, (w, round(f.shape[0] * w / f.shape[1])), interpolation=cv2.INTER_AREA),
                               f"{os.path.basename(p)[:-4]} {t:.1f}s", 16))
        rows.append(tiles)
    th = max(t.height for r in rows for t in r)
    canvas = Image.new("RGB", (w * len(times), th * len(rows)), (20, 20, 20))
    for y, r in enumerate(rows):
        for x, t in enumerate(r):
            canvas.paste(t, (x * w, y * th))
    out = os.path.join(SHEETS, f"{test}_cmp.jpg")
    os.makedirs(SHEETS, exist_ok=True)
    canvas.save(out, quality=82)
    print(out)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = {x[2:].partition("=")[0]: x[2:].partition("=")[2] for x in sys.argv[1:] if x.startswith("--")}
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "intake":
        intake(a[1], set(a[2:]) or None)
    elif a[0] == "grid":
        grid(a[1], int(o.get("cols", 4)))
    elif a[0] == "compare":
        compare(a[1], [float(t) for t in a[2:]])
    else:
        raise SystemExit(__doc__)

"""Bake-off intake: per-clip facts, first-frame match, motion, camera drift, flicker, C7 sun tracking.

usage: .venv/bin/python tools/review/bakeoff_intake.py [SHOT ...]
writes work/review/bakeoff/intake.json (merged) and prints a table.
"""
import glob, json, os, re, subprocess, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "work/review/bakeoff")
SHOTS = ["A1", "C2", "C7", "C9", "F1"]


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                        "stream=width,height,r_frame_rate,nb_read_frames,bit_rate,codec_name,pix_fmt:format=duration,bit_rate",
                        "-of", "json", path], capture_output=True, text=True)
    d = json.loads(r.stdout)
    s, f = d["streams"][0], d["format"]
    n, dd = s["r_frame_rate"].split("/")
    return dict(w=s["width"], h=s["height"], fps=round(int(n) / int(dd), 3), frames=int(s["nb_read_frames"]),
                dur=round(float(f["duration"]), 3), kbps=round(int(f.get("bit_rate") or s.get("bit_rate") or 0) / 1000),
                codec=s["codec_name"], pix=s["pix_fmt"])


def frames(path):
    cap = cv2.VideoCapture(path)
    out = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        out.append(fr)
    return out


def ssim(a, b):
    a = a.astype(np.float64); b = b.astype(np.float64)
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu1 = cv2.GaussianBlur(a, (11, 11), 1.5); mu2 = cv2.GaussianBlur(b, (11, 11), 1.5)
    s1 = cv2.GaussianBlur(a * a, (11, 11), 1.5) - mu1 ** 2
    s2 = cv2.GaussianBlur(b * b, (11, 11), 1.5) - mu2 ** 2
    s12 = cv2.GaussianBlur(a * b, (11, 11), 1.5) - mu1 * mu2
    m = ((2 * mu1 * mu2 + C1) * (2 * s12 + C2)) / ((mu1 ** 2 + mu2 ** 2 + C1) * (s1 + s2 + C2))
    return float(m.mean())


def similarity(a, b):
    """affine (scale+rot+trans) from ORB matches, b relative to a, both grey same size"""
    orb = cv2.ORB_create(3000)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 20 or len(kb) < 20:
        return None
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
    if len(m) < 20:
        return None
    pa = np.float32([ka[x.queryIdx].pt for x in m]); pb = np.float32([kb[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=3)
    if M is None:
        return None
    sc = float(np.hypot(M[0, 0], M[1, 0]))
    return dict(scale=round(sc, 4), dx=round(float(M[0, 2]), 1), dy=round(float(M[1, 2]), 1), inliers=int(inl.sum()))


def sun_track(fr):
    """C7: the sun = largest very bright blob; returns centroid, area, bbox, solidity (bite makes it < 1)"""
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(g, 245, 255, cv2.THRESH_BINARY)
    n, lab, st, cen = cv2.connectedComponentsWithStats(th)
    if n < 2:
        return None
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    mask = (lab == i).astype(np.uint8)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    sol = cv2.contourArea(c) / max(cv2.contourArea(hull), 1)
    x, y, w, h = st[i, :4]
    return dict(cx=float(cen[i][0]), cy=float(cen[i][1]), area=int(st[i, 4]), w=int(w), h=int(h), sol=round(float(sol), 3))


def analyse(shot, path):
    tag = os.path.basename(path)
    model = tag.split("_")[2]
    info = probe(path)
    fr = frames(path)
    kf = cv2.imread(os.path.join(ROOT, f"media/kf/{shot}_pick_1080.jpg"))
    H, W = 270, 480
    kg = cv2.cvtColor(cv2.resize(kf, (W, H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    f0 = cv2.resize(fr[0], (W, H), interpolation=cv2.INTER_AREA)
    g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
    corr = float(np.corrcoef(kg.ravel(), g0.ravel())[0, 1])
    ss = ssim(kg, g0)
    # reframe estimate at 960 wide
    kb = cv2.cvtColor(cv2.resize(kf, (960, 540)), cv2.COLOR_BGR2GRAY)
    fb = cv2.cvtColor(cv2.resize(fr[0], (960, 540)), cv2.COLOR_BGR2GRAY)
    reframe = similarity(kb, fb)
    # colour / exposure shift in Lab
    kl = cv2.cvtColor(cv2.resize(kf, (W, H)), cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float)
    fl = cv2.cvtColor(f0, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float)
    dlab = (fl.mean(0) - kl.mean(0))
    dlab = dict(dL=round(dlab[0] * 100 / 255, 1), da=round(dlab[1] - 0, 1), db=round(dlab[2], 1),
                dcontrast=round(float(fl[:, 0].std() / max(kl[:, 0].std(), 1e-6)), 3))
    # motion: Farneback on 480x270 grey
    greys = [cv2.cvtColor(cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for f in fr]
    mag_all, glob_mag, loc_mag, cam = [], [], [], []
    dup = 0
    lum = [float(g.mean()) for g in greys]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for i in range(1, len(greys)):
        d = np.abs(greys[i].astype(int) - greys[i - 1].astype(int)).mean()
        if d < 0.15:
            dup += 1
        flow = cv2.calcOpticalFlowFarneback(greys[i - 1], greys[i], None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.hypot(flow[..., 0], flow[..., 1])
        # global (camera) motion: robust affine fit on a sparse grid of flow vectors
        sl = (slice(4, H - 4, 8), slice(4, W - 4, 8))
        src = np.stack([xx[sl].ravel(), yy[sl].ravel()], 1)
        dst = src + np.stack([flow[..., 0][sl].ravel(), flow[..., 1][sl].ravel()], 1)
        M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=1.0)
        if M is None:
            M = np.array([[1, 0, 0], [0, 1, 0]], float)
        pred = np.stack([xx, yy], -1) @ M[:, :2].T + M[:, 2]
        res = np.hypot(xx + flow[..., 0] - pred[..., 0], yy + flow[..., 1] - pred[..., 1])
        mag_all.append(float(mag.mean()))
        gm = float(np.hypot(*(M[:, 2] + (M[:, :2] - np.eye(2)) @ np.array([W / 2, H / 2]))))
        glob_mag.append(gm)
        loc_mag.append(float(np.percentile(res, 95)))
        cam.append((float(M[0, 2] + (M[0, 0] - 1) * W / 2 - M[0, 1] * H / 2),
                    float(M[1, 2] + (M[1, 1] - 1) * H / 2 + M[1, 0] * W / 2),
                    float(np.hypot(M[0, 0], M[1, 0]))))
    cam = np.array(cam)
    # cumulative camera path (in 480-px units, scale product)
    cx, cy = np.cumsum(cam[:, 0]), np.cumsum(cam[:, 1])
    zs = np.cumprod(cam[:, 2])
    # whole-clip drift first->last via ORB
    drift = similarity(cv2.resize(greys[0], (960, 540)) if False else cv2.cvtColor(cv2.resize(fr[0], (960, 540)), cv2.COLOR_BGR2GRAY),
                       cv2.cvtColor(cv2.resize(fr[-1], (960, 540)), cv2.COLOR_BGR2GRAY))
    fps = info["fps"]
    # per-second summaries
    persec = []
    for s in range(int(np.ceil(len(mag_all) / fps))):
        a, b = int(s * fps), int(min((s + 1) * fps, len(mag_all)))
        if a >= b:
            break
        persec.append(dict(t=s, flow=round(float(np.mean(mag_all[a:b])), 2), cam=round(float(np.mean(glob_mag[a:b])), 2),
                           local95=round(float(np.mean(loc_mag[a:b])), 2)))
    jumps = [round(i / fps, 2) for i in range(1, len(lum)) if abs(lum[i] - lum[i - 1]) > 4]
    # scene cut detector: big frame difference spike
    diffs = [np.abs(greys[i].astype(int) - greys[i - 1].astype(int)).mean() for i in range(1, len(greys))]
    md = np.median(diffs) + 1e-6
    cuts = [round(i / fps, 2) for i, d in enumerate(diffs, 1) if d > 6 * md and d > 12]
    r = dict(shot=shot, model=model, file=os.path.relpath(path, ROOT), **info,
             ff_corr=round(corr, 3), ff_ssim=round(ss, 3), ff_reframe=reframe, ff_lab=dlab,
             flow_mean=round(float(np.mean(mag_all)), 2), flow_p95=round(float(np.percentile(mag_all, 95)), 2),
             cam_mean=round(float(np.mean(glob_mag)), 2), local_mean=round(float(np.mean(loc_mag)), 2),
             cam_path_px480=dict(dx=round(float(cx[-1]), 1), dy=round(float(cy[-1]), 1), zoom=round(float(zs[-1]), 3),
                                 maxdev=round(float(np.max(np.hypot(cx, cy))), 1)),
             first_last=drift, dup_frames=dup, lum_jumps=jumps[:20], cut_candidates=cuts,
             lum_range=round(max(lum) - min(lum), 1), persec=persec)
    if shot == "C7":
        tr = [sun_track(f) for f in fr]
        ok = [t for t in tr if t]
        s0 = ok[0] if ok else None
        if ok:
            r["sun"] = dict(first=s0, last=ok[-1],
                            max_shift_px=round(max(np.hypot(t["cx"] - s0["cx"], t["cy"] - s0["cy"]) for t in ok), 1),
                            area_min_max=[min(t["area"] for t in ok), max(t["area"] for t in ok)],
                            sol_min_max=[min(t["sol"] for t in ok), max(t["sol"] for t in ok)],
                            per_sec=[tr[int(i * fps)] for i in range(int(len(fr) / fps)) if tr[int(i * fps)]])
        kt = sun_track(cv2.resize(kf, (info["w"], info["h"])))
        r["sun_kf"] = kt
    np.save(os.path.join(OUT, "motion", tag.replace(".mp4", ".npy")),
            np.array([mag_all, glob_mag, loc_mag]))
    return r


def main():
    shots = sys.argv[1:] or SHOTS
    os.makedirs(os.path.join(OUT, "motion"), exist_ok=True)
    jp = os.path.join(OUT, "intake.json")
    allr = json.load(open(jp)) if os.path.exists(jp) else {}
    for shot in shots:
        for p in sorted(glob.glob(os.path.join(ROOT, f"media/gen/bk_{shot}_*_t1_*.mp4"))):
            r = analyse(shot, p)
            allr[f"{shot}_{r['model']}"] = r
            print(f"{shot} {r['model']:7s} {r['w']}x{r['h']} {r['fps']}fps {r['frames']}f {r['dur']}s {r['kbps']}kbps "
                  f"corr={r['ff_corr']} ssim={r['ff_ssim']} rf={r['ff_reframe']} lab={r['ff_lab']} "
                  f"flow={r['flow_mean']} cam={r['cam_mean']} loc={r['local_mean']} path={r['cam_path_px480']} "
                  f"fl={r['first_last']} dup={r['dup_frames']} cuts={r['cut_candidates']} jumps={r['lum_jumps'][:5]}"
                  + (f" sun={ {k: v for k, v in r.get('sun', {}).items() if k != 'per_sec'} } kf={r.get('sun_kf')}" if shot == 'C7' else ""),
                  flush=True)
            json.dump(allr, open(jp, "w"), indent=1)


if __name__ == "__main__":
    main()

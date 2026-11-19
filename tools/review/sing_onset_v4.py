#!/usr/bin/env python3
"""Mechanical audit: does the singer's mouth actually move when words are sung?  (v4 singing shots)

    python tools/review/sing_onset_v4.py [ID ...] [--out work/review/sing_v4] [--no-strips]

Needs mediapipe: the script re-runs itself in the venv named by MP_PY (as tools/review/lipsync_gate.py does) when the
current Python has none.  Writes <out>/audit.tsv, audit_words.tsv, audit.md, <ID>_everyframe.jpg, <ID>_series.json.

Measurement (reuses the FaceMesh landmarks of lipsync_gate.py: inner-lip gap 13-14)
  g[f] = inner-lip gap / face height (landmarks 10 forehead -> 152 chin) for the SINGER's face, every frame.
  Singer pick: FaceMesh is run on the whole frame (up to 4 faces); the shot table below gives the singer's nose position
  in frame 0 (picked by looking at the frames), and each later frame takes the face nearest to the previous position
  (within 0.7 face heights, size within +-40 %).  When nothing is found there, the same window is cut out, upscaled 3x and
  searched again (small faces).  A frame with no such face is "untracked" (NaN) and never counts as movement.
  rest = 10th percentile of g over tracked frames; R = 90th - 10th percentile.
  th   = max(0.015, 0.12 R)  (jitter of g, MAD of first differences, is reported but not used: real singing inflates it).
Per word (analysis/timing_v4.json, non-echo lines of the singer's kind, onset frame = ceil((start - t0) * 24))
  window = onset-2 .. min(end, onset+10) frames.  moved = (max g - min g in the window) >= th and the window is >= 60 % tracked.
  opened = max g in the window - rest >= max(0.012, 0.30 R)
Per shot
  first_syl  = onset frame of the first sung word;  first_move = first tracked frame >= first_syl-3 with g - rest >= max(0.012, 0.30 R)
  delay      = first_move - first_syl (frames; <= 0 = in time).  share = words moved / words measured.
  longest still run = longest run of consecutive sung, tracked frames in which g stays within th over a +-2 frame window.
Flags: FAIL / SUSPECT / OK / NOT MEASURABLE (face < 70 px tall, tracked on < 70 % of sung frames, or > 40 % of sung words
  not visible).  The thresholds were set with media/comp/F1.mp4 (first syllable on frame 0, mouth nearly shut to about frame 20) as the
  known FAIL; they are guesses beyond that one case, see NOTES.md.
"""
import json, math, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MP_PY = os.environ.get("MP_PY", "/home/jade/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python")
FPS = 24.0
CJK_FONT = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
LATIN_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# id: file, song time of the file's frame 0 (own start for spliced parts), seed = singer's nose in frame 0 (px, 960x540),
#     kinds = timing line singers that count, frames = measure only the first N frames (B2: first half only), only = words to keep
SHOTS = {
    "B1":  dict(t0=15.5,               seed=(443, 209), kinds=("child", "both"), who="little girl"),
    "B2":  dict(t0=535 / 24,           seed=(457, 193), kinds=("mom", "both"),   who="mother", frames=57, note="first half (lap) only: cut to the over-the-shoulder part is at 24.6 s"),
    "C3":  dict(t0=1108 / 24,          seed=(445, 184), kinds=("mom", "both"),   who="mother"),
    "D3":  dict(t0=1546 / 24,          seed=(272, 237), kinds=("mom", "both", "child"), who="mother (duet line)"),
    "E1":  dict(t0=2060 / 24,          seed=(347, 226), kinds=("mom", "both"),   who="mother"),
    "E3":  dict(t0=2232 / 24,          seed=(481, 286), kinds=("child", "both"), who="little girl"),
    "G1":  dict(t0=2915 / 24,          seed=(510, 255), kinds=("child", "both"), who="little girl"),
    "G4":  dict(t0=3390 / 24,          seed=(417, 183), kinds=("mom", "both"),   who="mother"),
    "G5":  dict(t0=3515 / 24,          seed=(503, 252), kinds=("child",),        who="little girl", only=("Yes",), note="G5.mp4 is 78 f over the G5+G6 slots; 'Yes' is in the G6 part"),
    "F1":  dict(t0=2569 / 24,          seed=(551, 271), kinds=("child", "both"), who="daughter (rap)"),
    "F6b": dict(t0=2882 / 24,          seed=(719, 252), kinds=("child", "both"), who="daughter, small in the mirror", upscale=True),
    "I1":  dict(t0=4253 / 24,          seed=(577, 165), kinds=("mom", "both"),   who="adult Jade"),
    "I3a": dict(t0=4391 / 24,          seed=(486, 345), kinds=("child", "both"), who="daughter"),
    "I4":  dict(t0=4488 / 24,          seed=(573, 229), kinds=("mom", "both"),   who="Jade"),
    "J4":  dict(t0=4719 / 24,          seed=(264, 146), kinds=("mom", "both", "child"), who="four singers; mother's face measured", note="left half only (mother); the other three faces are smaller"),
    "K2a": dict(t0=5053 / 24,          seed=(540, 235), kinds=("child", "both"), who="daughter"),
}
ORDER = list(SHOTS)


def reexec():
    try:
        import mediapipe  # noqa: F401
    except ImportError:
        if os.environ.get("SING_REEXEC") != "1":
            sys.exit(subprocess.run([MP_PY, os.path.abspath(__file__)] + sys.argv[1:], env=dict(os.environ, SING_REEXEC="1")).returncode)
        raise SystemExit("mediapipe not available (set MP_PY)")


def read_frames(path):
    import cv2
    cap = cv2.VideoCapture(path)
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr


class Tracker:
    def __init__(self):
        import mediapipe as mp
        self.fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=4, refine_landmarks=True,
                                                  min_detection_confidence=0.2)

    def faces(self, img, ox=0, oy=0, sc=1.0):
        import cv2
        h, w = img.shape[:2]
        r = self.fm.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        out = []
        for F in (r.multi_face_landmarks or []):
            L = F.landmark
            P = lambda i: np.array([L[i].x * w / sc + ox, L[i].y * h / sc + oy])  # noqa: E731
            fh = np.linalg.norm(P(10) - P(152))
            if fh < 20:
                continue
            out.append(dict(nose=P(1), fh=fh, gap=np.linalg.norm(P(13) - P(14)) / fh,
                            mouth=(P(61) + P(291)) / 2, width=np.linalg.norm(P(61) - P(291)) / fh,
                            yaw=(P(1)[0] - (P(33)[0] + P(263)[0]) / 2) / (np.linalg.norm(P(33) - P(263)) + 1e-6)))
        return out

    def find(self, img, pos, fh_prev, upscale=False):
        """singer face nearest to pos.  Full frame first; a small face (< 110 px) or upscale=True is re-detected on a 3x
        upscaled window around pos, which gives a steadier mouth gap for small faces (F6b: full-frame boxes jump between 90 and 200 px)."""
        import cv2
        rad = 0.7 * (fh_prev or 130)
        def pick(fs, ratio=True):
            fs = [f for f in fs if np.linalg.norm(f["nose"] - pos) <= rad and (not ratio or not fh_prev or abs(f["fh"] / fh_prev - 1) <= 0.4)]
            return min(fs, key=lambda f: np.linalg.norm(f["nose"] - pos)) if fs else None
        def crop_pick():
            H, W = img.shape[:2]
            half = int(max(110, (fh_prev or 130) * 1.1))
            x0, y0 = int(max(0, pos[0] - half)), int(max(0, pos[1] - half))
            x1, y1 = int(min(W, pos[0] + half)), int(min(H, pos[1] + half))
            crop = img[y0:y1, x0:x1]
            if crop.size == 0:
                return None
            sc = 3.0
            up = cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
            return pick(self.faces(up, x0, y0, sc), ratio=not upscale)
        if upscale:
            return crop_pick() or pick(self.faces(img), ratio=False)
        f = pick(self.faces(img))
        if f is None or f["fh"] < 110:
            c = crop_pick()
            return c or f
        return f


def track(frames, seed, upscale=False):
    T = Tracker()
    pos, fh_prev = np.array(seed, float), None
    rows = []
    for k, f in enumerate(frames):
        face = T.find(f, pos, fh_prev, upscale)
        if face is None:
            rows.append(None)
            continue
        pos, fh_prev = face["nose"], face["fh"] if fh_prev is None else 0.7 * fh_prev + 0.3 * face["fh"]
        rows.append(face)
    return rows


def words_for(sid, cfg, n, nm):
    T = json.load(open(os.path.join(ROOT, "analysis/timing_v4.json")))
    t0 = cfg["t0"]
    ws = []
    for l in T["lines"]:
        if l.get("echo") or l["singer"] not in cfg["kinds"]:
            continue
        for w in l["words"]:
            if cfg.get("only") and w["w"] not in cfg["only"]:
                continue
            on = math.ceil((w["start"] - t0) * FPS - 1e-6)
            en = math.ceil((w["end"] - t0) * FPS - 1e-6)
            en = max(en, on + 1)
            if on >= nm or en - max(on, 0) < 2:       # starts after the measured part, or fewer than 2 frames inside the shot
                continue
            ws.append(dict(w=w["w"], on=on, end=min(en, nm), conf=w.get("confidence", ""), t=round(w["start"], 3), line=l["id"]))
    return ws


def analyse(sid, cfg):
    path = os.path.join(ROOT, "media/comp", sid + ".mp4")
    r = dict(shot=sid, who=cfg["who"], t0=round(cfg["t0"], 4), file_ok=os.path.exists(path))
    if not r["file_ok"]:
        r.update(flag="MISSING", reason="media/comp/%s.mp4 does not exist" % sid)
        return r, None, None, None
    frames = read_frames(path)
    n = len(frames)
    nm = min(n, cfg.get("frames", n))
    rows = track(frames, cfg["seed"], cfg.get("upscale", False))
    g = np.array([x["gap"] if x else np.nan for x in rows], float)
    fh = np.array([x["fh"] if x else np.nan for x in rows], float)
    yaw = np.array([x["yaw"] if x else np.nan for x in rows], float)
    ws = words_for(sid, cfg, n, nm)
    tr = ~np.isnan(g)
    sung = np.zeros(n, bool)
    for w in ws:
        sung[max(w["on"], 0):w["end"]] = True
    idx = np.where(sung)[0]                      # a gap of <= 4 frames between words is still phrase (word ends are tight)
    for a_, b_ in zip(idx[:-1], idx[1:]):
        if 1 < b_ - a_ <= 5:
            sung[a_:b_] = True
    r.update(frames=n, measured_frames=nm, tracked_pct=round(100 * tr[:nm].mean(), 1),
             face_px=int(np.nanmedian(fh)) if tr.any() else 0, yaw_med=round(float(np.nanmedian(np.abs(yaw))), 2) if tr.any() else None,
             n_words=len(ws), sung_tracked_pct=round(100 * (tr & sung).sum() / max(1, sung.sum()), 1))
    if tr.sum() < 5 or not ws:
        r.update(flag="NOT MEASURABLE", reason="no usable face track" if not ws == [] else "no sung words in the window")
        return r, g, rows, ws
    rest, p90 = np.nanpercentile(g, 10), np.nanpercentile(g, 90)
    R = p90 - rest
    d = np.diff(g[tr[:-1] & tr[1:]]) if False else np.array([g[i + 1] - g[i] for i in range(n - 1) if tr[i] and tr[i + 1]])
    jit = 1.4826 * np.median(np.abs(d - np.median(d))) / math.sqrt(2) if len(d) > 3 else 0.0
    th = max(0.015, 0.12 * R)
    clear = max(0.012, 0.30 * R)
    r.update(rest=round(float(rest), 4), range=round(float(R), 4), jitter=round(float(jit), 4), th=round(float(th), 4))
    for w in ws:
        a, b = max(w["on"] - 2, 0), min(w["end"], w["on"] + 10, n - 1)
        seg = g[a:b + 1]
        vis = float(np.mean(~np.isnan(seg))) if len(seg) else 0.0
        w["visible"] = vis >= 0.6
        if w["visible"]:
            w["range"] = round(float(np.nanmax(seg) - np.nanmin(seg)), 4)
            w["peak"] = round(float(np.nanmax(seg) - rest), 4)
            w["moved"] = bool(w["range"] >= th)
            w["opened"] = bool(w["peak"] >= clear)
        else:
            w["range"] = w["peak"] = None; w["moved"] = w["opened"] = None
    vis_w = [w for w in ws if w["visible"]]
    r["words_visible"] = len(vis_w)
    r["share_moved"] = round(sum(w["moved"] for w in vis_w) / len(vis_w), 2) if vis_w else None
    first = min(w["on"] for w in ws)
    fs = max(first, 0)
    r["first_syl"] = first
    fm = next((f for f in range(max(0, first - 3), n) if tr[f] and g[f] - rest >= clear), None)
    r["first_move"] = fm
    r["delay"] = (fm - first) if fm is not None else None
    # longest still run over sung tracked frames
    best, cur, bs, cs = 0, 0, None, None
    for f in range(n):
        if sung[f] and tr[f]:
            seg = g[max(0, f - 2):f + 3]
            still = np.nanmax(seg) - np.nanmin(seg) < th
            if still:
                cur += 1; cs = f if cur == 1 else cs
                if cur > best:
                    best, bs = cur, cs
                continue
        cur = 0
    r["still_run"] = best
    # longest run of sung tracked frames with the mouth shut (gap below half the 'clear' level above rest)
    sb, sc_, ss, s0 = 0, 0, None, None
    for f in range(n):
        if sung[f] and tr[f] and g[f] - rest < 0.5 * clear:
            sc_ += 1; s0 = f if sc_ == 1 else s0
            if sc_ > sb: sb, ss = sc_, s0
        else:
            sc_ = 0
    r["shut_run"] = sb
    r["shut_at"] = "%d-%d" % (ss, ss + sb - 1) if sb else ""
    r["still_at"] = "%d-%d" % (bs, bs + best - 1) if best else ""
    # --- measurability and flag
    why_nm = []
    if r["face_px"] < 70: why_nm.append("face only %d px tall" % r["face_px"])
    if r["sung_tracked_pct"] < 70: why_nm.append("face found on only %.0f %% of the sung frames" % r["sung_tracked_pct"])
    if vis_w and len(vis_w) < 0.6 * len(ws): why_nm.append("only %d of %d words have the face in view" % (len(vis_w), len(ws)))
    if not vis_w: why_nm.append("no sung word with the face in view")
    if r["yaw_med"] is not None and r["yaw_med"] > 0.45: why_nm.append("face turned (yaw %.2f)" % r["yaw_med"])
    if why_nm:
        r.update(flag="NOT MEASURABLE", reason="; ".join(why_nm))
        return r, g, rows, ws
    bad, soft = [], []
    dl = r["delay"]
    if dl is None: bad.append("mouth never opens clearly")
    elif dl >= 8: bad.append("first clear mouth movement %d f after the first syllable (syllable on f%d, mouth at f%d)" % (dl, first, fm))
    elif dl >= 4: soft.append("first clear mouth movement %d f after the first syllable" % dl)
    sh = r["share_moved"]
    if sh < 0.5: bad.append("only %d %% of the words show mouth movement" % round(100 * sh))
    elif sh < 0.75: soft.append("%d %% of the words show mouth movement" % round(100 * sh))
    if best >= 14: bad.append("mouth frozen for %d f during sung words (f%s)" % (best, r["still_at"]))
    elif best >= 8: soft.append("mouth frozen for %d f during sung words (f%s)" % (best, r["still_at"]))
    sr = r["shut_run"]
    if sr >= 12: bad.append("mouth shut or nearly shut (gap < half the clear-open level) for %d f while words are sung (f%s)" % (sr, r["shut_at"]))
    elif sr >= 8: soft.append("mouth shut or nearly shut (gap < half the clear-open level) for %d f while words are sung (f%s)" % (sr, r["shut_at"]))
    if R < 0.03: soft.append("small articulation range %.3f of face height" % R)
    if r["face_px"] < 100 and (bad or soft):
        soft.append("CAVEAT face only %d px tall, measurement noisy" % r["face_px"])
    lowc = sum(1 for w in ws if w["conf"] not in ("high", "")) / max(1, len(ws))
    cav = []
    if lowc > 0.5: cav.append("%d %% of the word times are medium/low confidence in timing_v4" % round(100 * lowc))
    if cfg.get("note") and sid == "J4": cav.append("mother's face only (four singers)")
    if bad:
        r.update(flag="FAIL", reason="; ".join(bad + soft))
    elif soft:
        r.update(flag="SUSPECT", reason="; ".join(soft))
    else:
        r.update(flag="OK", reason="mouth moves with %d %% of the words, first movement %+d f from the first syllable, longest still run %d f, longest shut run %d f" % (round(100 * sh), dl, best, sr))
    if cav:
        r["reason"] += "; CAVEAT " + "; ".join(cav)
    return r, g, rows, ws


def strip(sid, frames, rows, g, ws, nm, out):
    import cv2
    from PIL import Image, ImageDraw, ImageFont
    fhs = [x["fh"] for x in rows if x]
    if not fhs:
        return
    fh = float(np.median(fhs))
    box = int(max(60, fh * 0.9))
    sc = 2
    cw = box * sc
    lab_h = 54
    cols = max(4, min(8, 2400 // cw))
    nrows = math.ceil(len(frames) / cols)
    font = ImageFont.truetype(CJK_FONT, 15); small = ImageFont.truetype(LATIN_FONT, 11); latin = ImageFont.truetype(LATIN_FONT, 15)
    W, H = cols * cw, nrows * (cw + lab_h)
    img = Image.new("RGB", (W, H), (22, 20, 15)); dr = ImageDraw.Draw(img)
    word_at = {}
    for w in ws:
        for f in range(max(w["on"], 0), w["end"]):
            word_at.setdefault(f, w)
    last = None
    gv = np.where(np.isnan(g), 0, g); gmax = max(0.05, float(np.nanmax(g)) if (~np.isnan(g)).any() else 0.05)
    for k, f in enumerate(frames):
        x = rows[k]
        if x:
            c = 0.5 * x["nose"] + 0.5 * x["mouth"]; last = c
        elif last is None:
            continue
        c = last
        x0, y0 = int(c[0] - box / 2), int(c[1] - box / 2)
        H0, W0 = f.shape[:2]
        pad = cv2.copyMakeBorder(f, box, box, box, box, cv2.BORDER_CONSTANT, value=(20, 20, 20))
        crop = pad[y0 + box:y0 + 2 * box, x0 + box:x0 + 2 * box]
        crop = cv2.resize(crop, (cw, cw), interpolation=cv2.INTER_CUBIC)
        cimg = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        cx, cy = (k % cols) * cw, (k // cols) * (cw + lab_h)
        img.paste(cimg, (cx, cy))
        w = word_at.get(k)
        on = w is not None and w["on"] == k
        col = (255, 120, 90) if x is None else ((120, 230, 140) if w else (190, 190, 190))
        dr.rectangle([cx, cy + cw, cx + cw - 1, cy + cw + lab_h - 1], fill=(40, 36, 28) if not on else (70, 60, 30))
        dr.text((cx + 4, cy + cw + 2), ("f%d" % k) + ("  no face" if x is None else "") + ("  ONSET" if on else ""), font=small, fill=col)
        if w:
            dr.text((cx + 4, cy + cw + 16), w["w"] + ("?" if w["conf"] not in ("high", "") else ""), font=(font if any(ord(ch) > 0x2e80 for ch in w["w"]) else latin), fill=(120, 230, 140))
        if x is not None:
            bw = int((cw - 8) * min(1.0, g[k] / gmax))
            dr.rectangle([cx + 4, cy + cw + lab_h - 10, cx + 4 + bw, cy + cw + lab_h - 4], fill=(217, 180, 90))
        if on:
            dr.rectangle([cx, cy, cx + cw - 1, cy + cw - 1], outline=(255, 90, 60), width=3)
    img.save(out, quality=82)


def md_table(rs):
    L = ["| shot | flag | delay f | words moved | still run f | reason |", "|---|---|---|---|---|---|"]
    for r in rs:
        L.append("| %s | %s | %s | %s | %s | %s |" % (r["shot"], r["flag"], r.get("delay", "-") if r.get("delay") is not None else "-",
                 ("%d %% (%d words)" % (round(100 * r["share_moved"]), r["words_visible"])) if r.get("share_moved") is not None else "-",
                 r.get("still_run", "-"), r["reason"]))
    return "\n".join(L)


def main():
    a = sys.argv[1:]
    out = os.path.join(ROOT, "work/review/sing_v4")
    nostrip = "--no-strips" in a
    a = [x for x in a if x != "--no-strips"]
    if "--out" in a:
        i = a.index("--out"); out = os.path.abspath(a[i + 1]); del a[i:i + 2]
    ids = a or ORDER
    reexec()
    os.makedirs(out, exist_ok=True)
    tsv = os.path.join(out, "audit.tsv")
    old = {}
    if os.path.exists(tsv):
        import csv
        for row in csv.DictReader(open(tsv), delimiter="\t"):
            old[row["shot"]] = row
    res, wrows = {}, []
    wtsv = os.path.join(out, "audit_words.tsv")
    oldw = [l.rstrip("\n").split("\t") for l in open(wtsv)][1:] if os.path.exists(wtsv) else []
    for sid in ids:
        r, g, rows, ws = analyse(sid, SHOTS[sid])
        if SHOTS[sid].get("note"):
            r["note"] = SHOTS[sid]["note"]
        res[sid] = r
        print("%-4s %-14s delay=%s moved=%s still=%s | %s" % (sid, r["flag"], r.get("delay"), r.get("share_moved"), r.get("still_run"), r["reason"]), flush=True)
        if g is not None:
            frames = read_frames(os.path.join(ROOT, "media/comp", sid + ".mp4"))
            json.dump(dict(shot=sid, t0=SHOTS[sid]["t0"], g=[None if np.isnan(v) else round(float(v), 4) for v in g], words=ws, summary=r),
                      open(os.path.join(out, sid + "_series.json"), "w"))
            if not nostrip:
                strip(sid, frames, rows, g, ws, r["measured_frames"], os.path.join(out, sid + "_everyframe.jpg"))
    # merge with previous results for shots not re-run, keep canonical order
    cols = ["shot", "flag", "reason", "who", "t0", "frames", "face_px", "tracked_pct", "sung_tracked_pct", "n_words", "words_visible",
            "share_moved", "first_syl", "first_move", "delay", "still_run", "still_at", "shut_run", "shut_at", "rest", "range", "th", "yaw_med", "note"]
    allr = {}
    for k, row in old.items():
        allr[k] = row
    for k, r in res.items():
        allr[k] = {c: ("" if r.get(c) is None else r.get(c)) for c in cols}
    with open(tsv, "w") as fo:
        fo.write("\t".join(cols) + "\n")
        for k in ORDER:
            if k in allr:
                fo.write("\t".join(str(allr[k].get(c, "")).replace("\t", " ") for c in cols) + "\n")
    # words
    ww = {}
    for l in oldw:
        ww.setdefault(l[0], []).append(l)
    for sid in ids:
        j = os.path.join(out, sid + "_series.json")
        ww.pop(sid, None)
        if os.path.exists(j):
            for w in json.load(open(j))["words"]:
                ww.setdefault(sid, []).append([sid, w["w"], str(w["on"]), str(w["end"]), w["conf"], str(w.get("visible")), str(w.get("range")), str(w.get("peak")),
                                               str(w.get("moved")), str(w.get("opened"))])
    with open(wtsv, "w") as fo:
        fo.write("\t".join(["shot", "word", "onset_f", "end_f", "timing_conf", "face_visible", "range", "peak_above_rest", "moved", "opened"]) + "\n")
        for k in ORDER:
            for l in ww.get(k, []):
                fo.write("\t".join(l) + "\n")
    # md
    import csv
    rows = list(csv.DictReader(open(tsv), delimiter="\t"))
    rank = {"FAIL": 0, "SUSPECT": 1, "NOT MEASURABLE": 2, "OK": 3, "MISSING": 0}
    rows.sort(key=lambda r: (rank.get(r["flag"], 9), r["shot"]))
    with open(os.path.join(out, "audit.md"), "w") as fo:
        fo.write("# Singing-shot mouth audit (tools/review/sing_onset_v4.py)\n\nFlags: FAIL / SUSPECT / OK / NOT MEASURABLE. delay = frames from the first sung "
                 "syllable to the first clear mouth movement (<= 0 is in time). Machine measurement only: nobody has watched these in motion.\n\n")
        fo.write("| shot | singer | flag | delay f | words moved | still run f | face px | reason |\n|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            sm = ("%d %%" % round(100 * float(r["share_moved"]))) if r["share_moved"] not in ("", None) else "-"
            fo.write("| %s | %s | %s | %s | %s | %s | %s | %s |\n" % (r["shot"], r["who"], r["flag"], r["delay"] or "-", sm, r["still_run"] or "-", r["face_px"], r["reason"]))
        fo.write("\nPer-word detail: audit_words.tsv.  Every-frame strips: <ID>_everyframe.jpg (green = sung word, red box = onset frame, bar = gap/face height).\n")


if __name__ == "__main__":
    main()

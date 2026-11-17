#!/usr/bin/env python3
"""Measure every collected lip-sync bake-off take (tag ls3_*): gate + acting numbers + 12-frame sheet.
    $PY tools/review/ls3_measure.py [substring ...]     -> work/review/lipsync_gate/ls3_table.tsv (+ strips, sheets)
Runs under the MediaPipe venv (re-execs). Acting numbers: blinks (eyelid gap dips), head travel (% of frame height),
roll range, brow travel (brow-to-eye distance range / inter-ocular), ff = correlation of frame 0 with the start frame."""
import glob, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import lipsync as LS
try:
    import mediapipe as mp
except ImportError:
    sys.exit(subprocess.run([LS.MP_PY, os.path.abspath(__file__)] + sys.argv[1:]).returncode)
import cv2, numpy as np
OUT = os.path.join(ROOT, "work/review/lipsync_gate")
PY = sys.executable

def acting(path, start_img):
    frames, fps = LS.read_frames(path)
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True,
                                         min_detection_confidence=0.2, min_tracking_confidence=0.2)
    lid, nose, roll, brow, iris = [], [], [], [], []
    for f in frames:
        h, w = f.shape[:2]
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            continue
        L = r.multi_face_landmarks[0].landmark
        P = lambda i: np.array([L[i].x * w, L[i].y * h])
        iod = np.linalg.norm(P(33) - P(263)) + 1e-6
        lid.append((np.linalg.norm(P(159) - P(145)) + np.linalg.norm(P(386) - P(374))) / 2 / iod)
        nose.append(P(1) / h); e = P(263) - P(33); roll.append(np.degrees(np.arctan2(e[1], e[0])))
        brow.append((np.linalg.norm(P(105) - P(159)) + np.linalg.norm(P(334) - P(386))) / 2 / iod)
        # iris centre relative to the eye corners (gaze proxy), left eye 468 between 33 and 133
        iris.append(np.dot(P(468) - P(33), P(133) - P(33)) / (np.linalg.norm(P(133) - P(33)) ** 2 + 1e-6))
    res = dict(frames=len(frames), fps=round(fps, 2), w=frames[0].shape[1], h=frames[0].shape[0])
    if len(lid) > 10:
        lid = np.array(lid); thr = np.median(lid) * 0.55
        res["blinks"] = int(np.sum((lid[1:] < thr) & (lid[:-1] >= thr)))
        nose = np.array(nose)
        res["head_travel_pct"] = round(float(np.sum(np.linalg.norm(np.diff(nose, axis=0), axis=1))) * 100, 1)
        res["head_range_pct"] = round(float(np.max(np.linalg.norm(nose - nose[0], axis=1))) * 100, 1)
        res["roll_deg"] = round(float(np.max(roll) - np.min(roll)), 1)
        res["brow_range"] = round(float(np.percentile(brow, 97) - np.percentile(brow, 3)), 3)
        res["gaze_range"] = round(float(np.percentile(iris, 97) - np.percentile(iris, 3)), 3)
    if start_img and os.path.exists(start_img):
        a = cv2.cvtColor(cv2.resize(frames[0], (320, 180)), cv2.COLOR_BGR2GRAY).astype(float).ravel()
        b = cv2.cvtColor(cv2.resize(cv2.imread(start_img), (320, 180)), cv2.COLOR_BGR2GRAY).astype(float).ravel()
        res["ff"] = round(float(np.corrcoef(a, b)[0, 1]), 3)
        a = cv2.cvtColor(cv2.resize(frames[-1], (320, 180)), cv2.COLOR_BGR2GRAY).astype(float).ravel()
        res["lf"] = round(float(np.corrcoef(a, b)[0, 1]), 3)
    return res

def main():
    subs = sys.argv[1:]
    man = json.load(open(os.path.join(ROOT, "media/gen/manifest.json"))) if os.path.exists(os.path.join(ROOT, "media/gen/manifest.json")) else None
    rows = []
    for spec in sorted(glob.glob(os.path.join(ROOT, "media/gen/specs/ls3_*.json"))):
        S = json.load(open(spec)); tag = S["tag"]
        if subs and not any(s in tag for s in subs):
            continue
        clips = sorted(glob.glob(os.path.join(ROOT, f"media/gen/{tag}_*.mp4")))
        if not clips:
            continue
        clip = clips[-1]
        img = next((v for k, v in S["input"].items() if k in ("image", "image_url", "first_frame")), None)
        img = os.path.join(ROOT, img[5:]) if img and img.startswith("file:") else None
        c24 = os.path.join(OUT, "c24", tag + ".mp4"); os.makedirs(os.path.dirname(c24), exist_ok=True)
        if not os.path.exists(c24):
            subprocess.run([LS.FFMPEG, "-v", "error", "-y", "-i", clip, "-an", "-vf", "fps=24,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
                            "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", c24], check=True)
        row = dict(tag=tag, model=S["model"].split("/")[-1])
        try:
            row.update(acting(clip, img))
        except Exception as e:
            row["acting_err"] = str(e)[:80]
        if "kling" not in tag:
            p = subprocess.run([PY, os.path.join(HERE, "lipsync_gate.py"), c24, "--t0", str(S["t0"]), "--name", tag, "--json", "--check"],
                               capture_output=True, text=True, env=dict(os.environ, LIPSYNC_REEXEC="1"))
            try:
                g = json.loads(p.stdout.strip().splitlines()[-1])
                for k in ("face_found_pct", "articulation", "env_lag_ms", "r", "sharp", "env_trust", "viseme_shift_f", "viseme_margin",
                          "viseme_trust", "shift_f", "shift_from", "closed", "open", "drift_f", "verdict", "reason"):
                    row[k] = g.get(k)
            except Exception as e:
                row["gate_err"] = (p.stderr or str(e))[-200:]
        sheet = os.path.join(OUT, "sheets", tag + ".jpg"); os.makedirs(os.path.dirname(sheet), exist_ok=True)
        if not os.path.exists(sheet):
            n = row.get("frames", 96)
            subprocess.run([LS.FFMPEG, "-v", "error", "-y", "-i", c24, "-vf", f"select='not(mod(n\\,{max(1, n // 12)}))',scale=480:270,tile=4x3", "-frames:v", "1", sheet])
        rows.append(row)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(os.path.join(OUT, "ls3_table.tsv"), "w") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    json.dump(rows, open(os.path.join(OUT, "ls3_table.json"), "w"), ensure_ascii=False, indent=1)
    for r in rows:
        print(r["tag"], "|", r.get("w"), "x", r.get("h"), r.get("frames"), "f | ff", r.get("ff"), "lf", r.get("lf"), "| blinks", r.get("blinks"), "head", r.get("head_travel_pct"),
              "roll", r.get("roll_deg"), "brow", r.get("brow_range"), "gaze", r.get("gaze_range"), "| art", r.get("articulation"), "env", r.get("env_lag_ms"), "r", r.get("r"), "sh", r.get("sharp"),
              "vis", r.get("viseme_shift_f"), "m", r.get("viseme_margin"), "shift", r.get("shift_f"), "closed", r.get("closed"), "open", r.get("open"), "drift", r.get("drift_f"),
              "|", r.get("verdict"), "|", r.get("reason") or r.get("gate_err") or "")

if __name__ == "__main__":
    main()

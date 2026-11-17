#!/usr/bin/env python3
"""Automatic lip-sync measure: estimate a take's audio lag and a sync score, so nobody has to pick lag by ear.

    $PY tools/review/lipsync.py CLIP --audio STEM.wav --t0 T [--box x,y,w,h] [--maxlag 1.2] [--plot OUT.png] [--json]

CLIP  a generated singing take (its frame 0 is meant to sit at song time T)
STEM  the separated vocal stem (work/stems/vocals.wav); T = the song time where the reference-audio window began

1. Mouth opening per frame:
   - MediaPipe FaceMesh (if importable; otherwise the script re-runs itself in a venv that has it, see MP_PY):
     inner-lip gap (landmarks 13-14) over the inter-ocular distance (33-263). Also head drift (nose tip, px at
     clip size) and roll (eye-line angle) for a head-stability number.
   - Fallback (no face found / no mediapipe): darkness inside a mouth box (--box in clip pixels, or the lower-middle of
     an OpenCV Haar face box): share of pixels darker than the box's 70th percentile minus 25 grey levels.
2. Vocal envelope of STEM over the same window: RMS of the 1-3 kHz band at the video frame rate, in dB (the band
   dips at every consonant even on legato singing; the broadband envelope does not).
3. Both series are high-passed (minus a 0.6 s moving average) and z-scored; Pearson r is computed for every lag in
   +-maxlag (frame steps). lag > 0 means the mouth moves AFTER the voice (the picture is late).
   r_best = sync score; sharp = r_best - median r over all lags (how clearly one lag wins).
   A take whose audio is known to be in sync measures about BIAS_MS = -60 ms (mouths open before the sound), so
   lag_vs_synced = lag + 60 ms. Suggested retime: play the clip so that its frame 0 lands at song time
   T - lag_vs_synced. In tools/ink: Retime(t0=T - lag_vs_synced, src0=0).
Rule of thumb from the bake-off (docs/VIDEO_BAKEOFF.md): r_best >= 0.4 with sharp >= 0.35 is a usable take (the
known-in-sync pass-through takes score 0.45-0.51);
< 0.25 means the mouth is not following the words (chewing or re-sung). articulation = p95-p5 of the inner-lip gap over
the inter-ocular distance; below 0.04 the mouth hardly moves and r is landmark noise (a still image scores r ~0.4).
"""
import json
import os
import subprocess
import sys

import numpy as np

MP_PY = os.environ.get("MP_PY", "/home/jade/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python")
FFMPEG = os.environ.get("FFMPEG", "/usr/bin/ffmpeg")
BIAS_MS = -60   # measured lag of takes whose audio is known to be in sync (p-video-avatar pass-through: -42, -83 ms)


def args():
    a = sys.argv[1:]
    o = {"maxlag": 1.2}
    pos = []
    i = 0
    while i < len(a):
        if a[i].startswith("--"):
            k = a[i][2:]
            if k in ("json", "no-mp"):
                o[k] = True; i += 1
            else:
                o[k] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    if not pos or "audio" not in o or "t0" not in o:
        raise SystemExit(__doc__)
    return pos[0], o


def read_frames(path):
    import cv2
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr, fps


def mouth_mediapipe(frames):
    import mediapipe as mp
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True,
                                         min_detection_confidence=0.2, min_tracking_confidence=0.2)
    import cv2
    op, nose, roll, width, ok = [], [], [], [], 0
    for f in frames:
        h, w = f.shape[:2]
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            op.append(np.nan); nose.append((np.nan, np.nan)); roll.append(np.nan); width.append(np.nan); continue
        ok += 1
        L = r.multi_face_landmarks[0].landmark
        P = lambda i: np.array([L[i].x * w, L[i].y * h])  # noqa: E731
        iod = np.linalg.norm(P(33) - P(263)) + 1e-6
        op.append(np.linalg.norm(P(13) - P(14)) / iod)
        width.append(np.linalg.norm(P(61) - P(291)) / iod)
        nose.append(tuple(P(1)))
        e = P(263) - P(33)
        roll.append(np.degrees(np.arctan2(e[1], e[0])))
    return np.array(op), np.array(nose), np.array(roll), np.array(width), ok


def mouth_dark(frames, box=None):
    import cv2
    if box is None:
        g = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        cc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
        faces = cc.detectMultiScale(g, 1.1, 4, minSize=(60, 60))
        if len(faces) == 0:
            raise SystemExit("no face found; pass --box x,y,w,h (mouth region in clip pixels)")
        x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
        box = (x + w // 4, y + int(h * 0.62), w // 2, int(h * 0.3))
    x, y, w, h = box
    out = []
    for f in frames:
        g = cv2.cvtColor(f[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY).astype(np.float32)
        thr = np.percentile(g, 70) - 25
        out.append(float((g < thr).mean()))
    return np.array(out), box


def envelope(stem, t0, n, fps, band=(1000, 3000)):
    """Vocal energy in the 1-3 kHz band (consonant bursts and upper formants), in dB at the video frame rate. On sung
    (legato) lines the broadband envelope barely dips between syllables; this band dips at every consonant, which is
    where the mouth closes. Chosen on the pass-through p-video-avatar takes (known 0-offset audio): broadband r 0.33/0.40,
    1-3 kHz r 0.51/0.45 with the peak at -42/-83 ms."""
    from scipy.signal import butter, sosfiltfilt
    sr = 16000
    raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{max(0.0, t0):.3f}", "-t", f"{n / fps + 0.1:.3f}", "-i", stem,
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    if t0 < 0:
        x = np.concatenate([np.zeros(int(-t0 * sr), np.float32), x])
    x = sosfiltfilt(butter(4, list(band), btype="band", fs=sr, output="sos"), x)
    hop = sr / fps
    env = []
    for i in range(n):
        a, b = int(i * hop), int((i + 1) * hop)
        seg = x[a:b] if b <= len(x) else np.zeros(1)
        env.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9))
    return np.array(env)


def hp_z(v, fps):
    v = np.array(v, float)
    if np.isnan(v).any():
        idx = np.arange(len(v)); good = ~np.isnan(v)
        v = np.interp(idx, idx[good], v[good]) if good.sum() > 2 else np.zeros_like(v)
    k = max(3, int(0.6 * fps) | 1)
    ma = np.convolve(np.pad(v, k // 2, mode="edge"), np.ones(k) / k, mode="valid")
    d = v - ma
    return (d - d.mean()) / (d.std() + 1e-9)


def xcorr(m, e, fps, maxlag):
    L = int(round(maxlag * fps))
    lags, rs = [], []
    for lag in range(-L, L + 1):
        # mouth(t) vs env(t - lag): mouth late by lag frames
        if lag >= 0:
            a, b = m[lag:], e[:len(e) - lag]
        else:
            a, b = m[:lag], e[-lag:]
        if len(a) < fps:
            continue
        rs.append(float(np.corrcoef(a, b)[0, 1])); lags.append(lag)
    rs = np.array(rs)
    i = int(np.nanargmax(rs))
    return lags[i] / fps, rs[i], rs[i] - float(np.nanmedian(rs)), np.array(lags) / fps, rs


def plot(out, m, e, lag, fps, title):
    import cv2
    W, H = 1200, 300
    img = np.full((H, W, 3), 255, np.uint8)
    n = len(m)
    def line(v, col, shift=0.0):
        v = (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v) + 1e-9)
        pts = [(int((i + shift) / n * W), int(H - 20 - v[i] * (H - 60))) for i in range(n) if not np.isnan(v[i])]
        cv2.polylines(img, [np.array(pts, np.int32)], False, col, 2)
    line(e, (200, 120, 0))
    line(m, (0, 0, 220), -lag * fps)
    for s in range(int(n / fps) + 1):
        cv2.line(img, (int(s * fps / n * W), 0), (int(s * fps / n * W), H), (220, 220, 220), 1)
    cv2.putText(img, title, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(img, "blue = vocal envelope, red = mouth opening shifted by -lag", (8, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
    cv2.imwrite(out, img)


def main():
    clip, o = args()
    try:
        import mediapipe  # noqa: F401
        have_mp = True
    except ImportError:
        have_mp = False
    if not have_mp and not o.get("no-mp") and os.path.exists(MP_PY) and os.environ.get("LIPSYNC_REEXEC") != "1":
        env = dict(os.environ, LIPSYNC_REEXEC="1")
        sys.exit(subprocess.run([MP_PY, os.path.abspath(__file__)] + sys.argv[1:], env=env).returncode)
    frames, fps = read_frames(clip)
    t0 = float(o["t0"])
    res = {"clip": clip, "fps": round(fps, 3), "frames": len(frames), "t0": t0}
    m, method = None, None
    if have_mp and not o.get("box"):
        op, nose, roll, width, ok = mouth_mediapipe(frames)
        res["face_found_pct"] = round(100 * ok / max(1, len(frames)), 1)
        if ok >= 0.6 * len(frames):
            m, method = op, "facemesh"
            good = ~np.isnan(nose[:, 0])
            h = frames[0].shape[0]
            res["head_drift_px"] = round(float(np.nanmax(np.linalg.norm(nose[good] - nose[good][0], axis=1))), 1)
            res["head_jitter_pct_h"] = round(float(np.nanstd(np.diff(nose[good], axis=0))) / h * 100, 3)
            res["roll_range_deg"] = round(float(np.nanmax(roll) - np.nanmin(roll)), 1)
            res["mouth_open_p5_p95"] = [round(float(np.nanpercentile(op, 5)), 3), round(float(np.nanpercentile(op, 95)), 3)]
            res["mouth_width_range"] = [round(float(np.nanpercentile(width, 5)), 3), round(float(np.nanpercentile(width, 95)), 3)]
    if m is None:
        box = tuple(int(v) for v in o["box"].split(",")) if o.get("box") else None
        m, box = mouth_dark(frames, box)
        method = f"dark-area box {box}"
    res["method"] = method
    e = envelope(o["audio"], t0, len(frames), fps)
    mz, ez = hp_z(m, fps), hp_z(e, fps)
    lag, r, sharp, lags, rs = xcorr(mz, ez, fps, float(o["maxlag"]))
    res.update(lag_ms=round(lag * 1000), r_best=round(r, 3), sharp=round(sharp, 3),
               r_at_0=round(float(rs[np.argmin(np.abs(lags))]), 3),
               second_peak_lag_ms=None)
    # second-best separated peak (ambiguity check)
    far = np.abs(lags - lag) > 0.25
    if far.any():
        j = int(np.nanargmax(np.where(far, rs, -9)))
        res["second_peak_lag_ms"], res["second_peak_r"] = round(lags[j] * 1000), round(float(rs[j]), 3)
    res["verdict"] = ("usable" if r >= 0.4 and sharp >= 0.35 else "weak" if r >= 0.25 else "not following the words")
    if method == "facemesh":
        art = res["mouth_open_p5_p95"][1] - res["mouth_open_p5_p95"][0]
        res["articulation"] = round(art, 3)
        if art < 0.04:   # a still face measures ~0.003; singing takes 0.08-0.4 (inner-lip gap / inter-ocular distance)
            res["verdict"] = "mouth barely moves (score is landmark noise)"
    shift = lag - BIAS_MS / 1000.0     # a perfectly synced take still measures BIAS_MS (the mouth leads the sound)
    res["lag_vs_synced_ms"] = round(shift * 1000)
    res["suggested"] = (f"place clip frame 0 at song time {t0 - shift:.3f} "
                        f"(shift picture {'earlier' if shift > 0 else 'later'} by {abs(shift) * 1000:.0f} ms)")
    if o.get("plot"):
        plot(o["plot"], m, e, lag, fps, f"{os.path.basename(clip)}  lag {lag * 1000:+.0f} ms  r {r:.2f}  sharp {sharp:.2f}  [{method}]")
        res["plot"] = o["plot"]
    if o.get("json"):
        print(json.dumps(res))
    else:
        for k, v in res.items():
            print(f"{k:22s} {v}")


if __name__ == "__main__":
    main()

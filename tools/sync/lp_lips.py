#!/usr/bin/env python3
"""Two-stage lip-sync, stage 2 (local, free): put the MOUTH of a synced driver take onto an ACTED take.

    $PY tools/sync/lp_lips.py ACTED.mp4 DRIVER.mp4 OUT.mp4 [--offset N] [--mask jaw|mouth] [--gain 1.0]

ACTED   the performance to keep (Kling v4, no lip-sync): head, eyes, brows, hands, timing, the painting.
DRIVER  a take of the SAME start frame whose mouth is in sync (pruna/p-video-avatar: its audio is the stem, offset 0).
Both are read at 24 fps; frame i of ACTED gets the lips of frame i+N of DRIVER.
LivePortrait (ONNX, tools/sync/liveportrait.py) splits each face into head pose + expression keypoints. The acted frame
keeps its pose and all expression keypoints except the six lip/jaw ones (6, 12, 14, 17, 19, 20), which are taken from
the driver frame; the generator redraws the face crop and only the lower face is blended back (feathered mask), so the
eyes, glasses, hair and everything outside the face are the acted take's own pixels.
Landmarks come from MediaPipe in the MP venv (the script calls itself there with `lm`)."""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MP_PY = os.environ.get("MP_PY", "/home/jade/Documents/1-music-shipped/orbital-sunrise-video/video/out/.venv/bin/python")
LIP_IDX = [6, 12, 14, 17, 19, 20]


def read(path):
    import cv2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "fps=24", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True, check=True).stdout
    cap = cv2.VideoCapture(path); w, h = int(cap.get(3)), int(cap.get(4)); cap.release()
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def lm_main(path, out):
    import cv2, mediapipe as mp
    fr = read(path)
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True,
                                         min_detection_confidence=0.2, min_tracking_confidence=0.2)
    res = []
    for f in fr:
        h, w = f.shape[:2]
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            res.append(None); continue
        L = r.multi_face_landmarks[0].landmark
        P = lambda i: [L[i].x * w, L[i].y * h]
        # 5 points (left eye, right eye, nose tip, mouth corners) + lower-face outline for the mask
        res.append(dict(p5=[P(468), P(473), P(1), P(61), P(291)],
                        jaw=[P(i) for i in (234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454)],
                        nose=P(2), mouth=[P(i) for i in (61, 291, 0, 17)]))
    for i, r in enumerate(res):          # fill gaps with the nearest found frame
        if r is None:
            res[i] = next((res[j] for d in range(1, len(res)) for j in (i - d, i + d) if 0 <= j < len(res) and res[j]), None)
    json.dump(res, open(out, "w"))


def landmarks(path):
    out = path + ".lm.json"
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(path):
        subprocess.run([MP_PY, os.path.abspath(__file__), "lm", path, out], check=True, stderr=subprocess.DEVNULL)
    return json.load(open(out))


def main():
    a = sys.argv[1:]
    if a and a[0] == "lm":
        return lm_main(a[1], a[2])
    opt = {a[i][2:]: a[i + 1] for i in range(len(a)) if a[i].startswith("--")}
    acted, driver, out = [x for i, x in enumerate(a) if not x.startswith("--") and not (i and a[i - 1].startswith("--"))][:3]
    off, gain, mask_kind = int(opt.get("offset", 0)), float(opt.get("gain", 1.0)), opt.get("mask", "jaw")
    import cv2
    sys.path.insert(0, HERE)
    import liveportrait as LP
    A, D = read(acted), read(driver)
    la, ld = landmarks(acted), landmarks(driver)
    n = len(A); H, W = A[0].shape[:2]
    pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                             "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    # smooth the acted take's crop transform over time (jitter in the 5 points would make the face swim)
    P5 = np.array([l["p5"] for l in la], np.float32)
    k = 5
    P5s = np.stack([np.convolve(np.pad(P5[:, i, j], k // 2, mode="edge"), np.ones(k) / k, "valid") for i in range(5) for j in range(2)], 1).reshape(n, 5, 2)
    for i in range(n):
        j = min(max(i + off, 0), len(D) - 1)
        ca, Ma = LP.crop_face(A[i], P5s[i]); cd, _ = LP.crop_face(D[j], ld[j]["p5"])
        body, drv = LP.Face(ca), LP.Face(cd)
        ex = body.ex.copy()
        ex[:, LIP_IDX, :] = body.ex[:, LIP_IDX, :] * (1 - gain) + drv.ex[:, LIP_IDX, :] * gain
        kp = (body.sc * (body.mp @ body.R.T + ex) + body.tr).astype(np.float32)
        new = LP.draw(body, kp, body.kp)                                  # 512 crop, BGR
        Mi = cv2.invertAffineTransform(Ma)
        back = cv2.warpAffine(new, Mi, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        m = np.zeros((H, W), np.float32)
        jaw = np.array(la[i]["jaw"], np.float32); nose = np.array(la[i]["nose"], np.float32)
        mc = np.array(la[i]["mouth"], np.float32); wm = np.linalg.norm(mc[0] - mc[1])
        if mask_kind == "mouth":
            c = mc.mean(0); cv2.ellipse(m, (int(c[0]), int(c[1])), (int(wm * 1.1), int(wm * 0.95)), 0, 0, 360, 1.0, -1)
        else:   # lower face: jaw outline below the nose line, pulled in 6 % so the silhouette stays the acted take's
            cen = jaw.mean(0); poly = cen + (jaw - cen) * 0.94
            top = nose[1] + 0.10 * wm
            poly = np.array([[x, max(y, top)] for x, y in poly], np.int32)
            cv2.fillPoly(m, [poly], 1.0)
        s = max(3, int(wm * 0.35)) | 1
        m = cv2.GaussianBlur(m, (s, s), 0)[..., None]
        pipe.stdin.write((A[i] * (1 - m) + back * m).astype(np.uint8).tobytes())
    pipe.stdin.close(); pipe.wait()
    print(out, n, "frames")


if __name__ == "__main__":
    main()

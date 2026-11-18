#!/usr/bin/env python3
"""Two-stage lip-sync, stage 2 (local, free): put the MOUTH of a synced driver take onto an ACTED take.

    $PY tools/sync/lp_lips.py ACTED.mp4 DRIVER.mp4 OUT.mp4 [--offset N] [--mask jaw|mouth] [--gain 1.0] [--t0 T] [--pick x,y]

--pick x,y  two or more faces in ACTED: the singer is the face whose nose is nearest to pixel x,y in frame 0 (tracked after).

--t0 T  song time of frame 0 (both takes). With it, every bilabial closure in analysis/timing.json (m/b/p, 妈 没 蹦 ...)
        is FORCED: on the two frames before the word's onset the lips come from the driver's most closed frame, so the
        closures land on the measured onsets whatever the driver did, and the mouth rests wherever timing.json has
        no lead word (the driver also mouths backing echoes and reverb tails; those are muted). CPU only here (about 4 s per frame).

ACTED   the performance to keep (Kling v4, no lip-sync): head, eyes, brows, hands, timing, the painting.
DRIVER  a take of the SAME start frame whose mouth is in sync (pruna/p-video-avatar: its audio is the stem, offset 0).
Both are read at 24 fps; frame i of ACTED gets the lips of frame i+N of DRIVER.
LivePortrait (ONNX, tools/sync/liveportrait.py) splits each face into head pose + expression keypoints. The acted frame
keeps its pose and expression. LivePortrait's lip retargeter sets its lip gap/width ratio to the driver frame's ratio
(times --rgain, default 1.0; 0 on forced closures), and the driver's lip shape (its six lip keypoints 6, 12, 14, 17, 19,
20 minus those of the driver's most closed frame, times --shape, default 0.5) is added, so the mouth is as open as the
driver's and shut wherever it must be, whatever the acted take's own mouth did (--mode replace = the first variant that
copies the driver's lip keypoints: it leaves the mouth ajar when the acted take's jaw is open). --frames a:b renders a
range only (tests). The generator redraws the face crop and only the lower face is blended back (feathered mask), so the
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


def lm_main(path, out, pick=None):
    import cv2, mediapipe as mp
    fr = read(path)
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=4 if pick else 1, refine_landmarks=True,
                                         min_detection_confidence=0.2, min_tracking_confidence=0.2)
    res = []
    last = [float(v) for v in pick.split(",")] if pick else None      # x,y in pixels of the singer's nose in frame 0
    for f in fr:
        h, w = f.shape[:2]
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            res.append(None); continue
        faces = r.multi_face_landmarks
        if last is not None:
            faces = sorted(faces, key=lambda F: (F.landmark[1].x * w - last[0]) ** 2 + (F.landmark[1].y * h - last[1]) ** 2)
            last = [faces[0].landmark[1].x * w, faces[0].landmark[1].y * h]
        L = faces[0].landmark
        P = lambda i: [L[i].x * w, L[i].y * h]
        # 5 points (left eye, right eye, nose tip, mouth corners) + lower-face outline for the mask
        res.append(dict(p5=[P(468), P(473), P(1), P(61), P(291)],
                        jaw=[P(i) for i in (234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454)],
                        nose=P(2), mouth=[P(i) for i in (61, 291, 0, 17)],
                        gap=float(((L[13].x - L[14].x) ** 2 * w * w + (L[13].y - L[14].y) ** 2 * h * h) ** 0.5)))
    for i, r in enumerate(res):          # fill gaps with the nearest found frame
        if r is None:
            res[i] = next((res[j] for d in range(1, len(res)) for j in (i - d, i + d) if 0 <= j < len(res) and res[j]), None)
    json.dump(res, open(out, "w"))


def landmarks(path, pick=None):
    tmp = os.path.join(os.path.dirname(os.path.dirname(HERE)), "work/lipsync/cache"); os.makedirs(tmp, exist_ok=True)
    out = os.path.join(tmp, os.path.basename(path) + (".pick" + pick.replace(",", "_") if pick else "") + ".lm.json")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(path):
        subprocess.run([MP_PY, os.path.abspath(__file__), "lm", path, out] + ([pick] if pick else []), check=True, stderr=subprocess.DEVNULL)
    return json.load(open(out))


def main():
    a = sys.argv[1:]
    if a and a[0] == "lm":
        return lm_main(a[1], a[2], a[3] if len(a) > 3 else None)
    opt = {a[i][2:]: a[i + 1] for i in range(len(a)) if a[i].startswith("--")}
    acted, driver, out = [x for i, x in enumerate(a) if not x.startswith("--") and not (i and a[i - 1].startswith("--"))][:3]
    off, gain, mask_kind = int(opt.get("offset", 0)), float(opt.get("gain", 1.0)), opt.get("mask", "jaw")
    import cv2
    sys.path.insert(0, HERE)
    import liveportrait as LP
    A, D = read(acted), read(driver)
    la, ld = landmarks(acted, opt.get("pick")), landmarks(driver)
    n = len(A); H, W = A[0].shape[:2]
    pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                             "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    # smooth the acted take's crop transform over time (jitter in the 5 points would make the face swim)
    P5 = np.array([l["p5"] for l in la], np.float32)
    k = 5
    P5s = np.stack([np.convolve(np.pad(P5[:, i, j], k // 2, mode="edge"), np.ones(k) / k, "valid") for i in range(5) for j in range(2)], 1).reshape(n, 5, 2)
    # driver expressions for every frame (motion extractor only)
    DEX = []
    for j in range(len(D)):
        cd, _ = LP.crop_face(D[j], ld[j]["p5"]); DEX.append(LP.Face(cd, motion_only=True).ex)
    force = np.zeros(n, np.float32)
    active = np.ones(n, np.float32)
    mode = opt.get("mode", "ratio")
    rgain, shape = float(opt.get("rgain", 1.0)), float(opt.get("shape", 0.5))
    dratio = np.array([l["gap"] / (np.hypot(l["mouth"][0][0] - l["mouth"][1][0], l["mouth"][0][1] - l["mouth"][1][1]) + 1e-6) for l in ld])
    dratio = np.convolve(np.pad(dratio, 1, mode="edge"), [0.2, 0.6, 0.2], "valid")     # light smoothing of landmark noise
    dmin = float(np.percentile(dratio, 2))
    f_a, f_b = (int(v) for v in opt.get("frames", f"0:{n}").split(":"))
    gaps = [l["gap"] for l in ld]
    jc = int(np.argmin(gaps)); closed_ex = DEX[jc]
    if "t0" in opt:
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "review"))
        import lipsync_gate as G
        t0 = float(opt["t0"])
        for e in G.events(t0 - 0.2, t0 + n / 24.0 + 0.2):
            if e["kind"] != "B" or e["tag"] == "mid":
                continue
            f1 = int(np.floor((e["t"] + 0.03 - t0) * 24 - 1e-6)) if e["tag"] == "init" else int(round((e["t"] - t0) * 24))
            for f, wgt in ((f1 - 2, 0.6), (f1 - 1, 1.0), (f1, 0.5)) if e["tag"] == "init" else ((f1 - 1, 0.6), (f1, 1.0), (f1 + 1, 1.0), (f1 + 2, 0.5)):
                if 0 <= f < n:
                    force[f] = max(force[f], wgt)
        # sing only where the lead sings: outside the measured words (non-echo lines) and the loud parts of the stem the
        # mouth goes to rest, so the driver's mouthing of backing echoes, breaths and reverb tails never reaches the picture
        T = json.load(open(G.TIMING))
        active[:] = 0.0
        WL = sorted((w["start"], max(w["end"], w["start"] + 0.06), w.get("confidence")) for l in T["lines"] if not l.get("echo") for w in l["words"])
        for k_, (st, en, conf) in enumerate(WL):
            if conf == "low":      # a low-confidence word time: do not mute anything between its neighbours
                st = WL[k_ - 1][1] if k_ else st
                en = WL[k_ + 1][0] if k_ + 1 < len(WL) else en
            a_, b_ = int(np.floor((st - 0.12 - t0) * 24)), int(np.ceil((en + 0.10 - t0) * 24))
            active[max(a_, 0):max(min(b_, n), 0)] = 1.0
        # ... or wherever the vocal stem itself is loud (within 10 dB of the window's loud level): word ends in
        # timing.json are conservative, and held notes ring past them
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t0, 0):.3f}", "-t", f"{n / 24 + 0.1:.3f}", "-i", G.STEM, "-ac", "1",
                              "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
        xs = np.frombuffer(raw, np.float32); hop = 16000 / 24
        lv = np.array([20 * np.log10(np.sqrt(np.mean(xs[int(i * hop):int((i + 1) * hop)] ** 2)) + 1e-6) if int((i + 1) * hop) <= len(xs) else -99
                       for i in range(n)])
        loud = lv > np.percentile(lv, 95) - 10
        loud = loud | np.roll(loud, -1) | np.roll(loud, -2)          # the mouth may lead the sound by two frames
        active[loud] = 1.0
        active[:] = np.convolve(np.pad(active, 1, mode="edge"), [0.25, 0.5, 0.25], "valid")
        print("forced closures on frames", [int(i) for i in np.nonzero(force >= 1)[0]], "closed driver frame", jc, flush=True)
    for i in range(f_a, min(f_b, n)):
        j = min(max(i + off, 0), len(D) - 1)
        ca, Ma = LP.crop_face(A[i], P5s[i])
        body = LP.Face(ca)
        dex = DEX[j] if force[i] == 0 else DEX[j] * (1 - force[i]) + closed_ex * force[i]
        if mode == "replace":      # v1: the driver's lip keypoints replace the acted take's
            ex = body.ex.copy()
            ex[:, LIP_IDX, :] = body.ex[:, LIP_IDX, :] * (1 - gain) + dex[:, LIP_IDX, :] * gain
            kp = (body.sc * (body.mp @ body.R.T + ex) + body.tr).astype(np.float32)
        else:                      # v3 (default): the lip retargeter sets the opening to the driver's; driver lip shape added on top
            mc = np.array(la[i]["mouth"], np.float32)
            want = float(np.clip((dratio[j] - dmin) * rgain, 0, 0.9)) * (1 - force[i]) * active[i]
            # the retargeter under-closes an open acted mouth: overstate its current opening by --rnow (1.8) when the
            # target is shut, fading to 1 as the target opens (tested on I4: 1.0 leaves it ajar, 2.5 thins the lips)
            ratio_now = float(la[i]["gap"] / (np.linalg.norm(mc[0] - mc[1]) + 1e-6))
            ratio_now *= 1 + (float(opt.get("rnow", 1.8)) - 1) * (1 - min(want / 0.3, 1.0))
            kp0 = body.kp + LP.lip_offsets(body.kp, ratio_now, want).reshape(1, -1, 3)
            d = np.zeros_like(body.ex)
            d[:, LIP_IDX, :] = (dex - closed_ex)[:, LIP_IDX, :] * shape * active[i]
            kp = (kp0 + body.sc * (d @ body.R.T)).astype(np.float32)
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

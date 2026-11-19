#!/usr/bin/env python3
"""Lip-sync v4 checks (REVISION_V4 §1.2): placement from the take's own audio, and the face strip the director actually sees.

    $PY tools/review/lipsync_v4.py audiolag TAKE.mp4 --t0 T
        If the take carries a soundtrack (Seedance generate_audio:true with reference audio), find where in the song the
        take's frame 0 sits by cross-correlating its 1-3 kHz vocal envelope (1 ms steps) with the vocal stem over +-1.5 s,
        on the whole take and on each half (drift). Prints place_frame0_at, shift_f (24 fps, vs T) and drift_ms.
        Writes work/review/lipsync_v4/<name>_audiolag.json.

    $PY tools/review/lipsync_v4.py strip TAKE.mp4 --t0 T [--shift N] [--pick x,y] [--name N] [--every 2]
        The FACE STRIP: the lower face (nose to below the chin, both cheeks and the jaw line) of every 2nd frame from the first
        sung word to the last, zoomed (at least 2x the 960x540 cut), each cell labelled with frame number and the word sounding
        then (red = bilabial onset within 1 f: lips must be shut; green = vowel centre: must be open). Cell 0 = the take's frame
        0, the on-model reference. Also measures JAW: chin-to-nose distance (FaceMesh 152-1 / inter-ocular) against the lip gap;
        a mouth that opens without the jaw (the v3 failure) gives jaw_r < 0.3 and jaw_range ~0.
        Writes work/review/lipsync_v4/<name>_face.jpg and <name>_face.json.
        Judge on the strip (or have a fresh agent judge it): (1) mouth inside the face outline, (2) jaw/chin drops with open
        vowels, (3) teeth do not flicker on/off between neighbouring cells, (4) no soft or smeared patch around the mouth, (5) the
        face still matches cell 0 / the character sheet (design/characters/CANON.md §00). Timing alone is not a pass.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import lipsync as LS  # noqa: E402

FPS = 24.0
STEM = os.path.join(ROOT, "work/stems/vocals.wav")
TIMING = os.path.join(ROOT, "analysis/timing.json")
OUT = os.path.join(ROOT, "work/review/lipsync_v4")
FONT = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
LFONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BILAB = set("妈没蹦变百白把拔每毛不爸怕跑朋本帮被别比边步")


def opts(a):
    o, pos, i = {}, [], 0
    while i < len(a):
        if a[i].startswith("--"):
            o[a[i][2:]] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    return pos, o


def band_env(x, sr, rate=1000):
    import numpy as np
    from scipy.signal import butter, sosfiltfilt
    y = sosfiltfilt(butter(4, [1000, 3000], btype="band", fs=sr, output="sos"), x)
    hop = sr // rate
    n = len(y) // hop
    e = np.sqrt(np.mean(y[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    e = 20 * np.log10(e + 1e-6)
    e = e - np.convolve(e, np.ones(200) / 200, mode="same")   # remove slow level (200 ms)
    return (e - e.mean()) / (e.std() + 1e-9)


def read_audio(path, start=None, dur=None, sr=16000):
    import numpy as np
    cmd = [LS.FFMPEG, "-v", "error"] + (["-ss", f"{start:.3f}"] if start is not None else []) + \
          (["-t", f"{dur:.3f}"] if dur is not None else []) + ["-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)


def audiolag(take, t0, name):
    import numpy as np
    sr, M = 16000, 1.5
    a = read_audio(take)
    if len(a) < sr // 2 or float(np.sqrt(np.mean(a ** 2))) < 1e-4:
        return dict(name=name, has_audio=False)
    s0 = max(0.0, t0 - M)
    s = read_audio(STEM, s0, len(a) / sr + 2 * M)
    if os.environ.get("LS4_RAW", "1") == "1":
        from scipy.signal import correlate
        cc = correlate(s, a, mode="valid", method="fft")
        k = int(np.argmax(np.abs(cc)))
        nrm = float(np.abs(cc[k]) / np.sqrt(np.sum(a ** 2) * np.sum(s[k:k + len(a)] ** 2) + 1e-12))
        L = int(round((s0 + k / sr - t0) * 1000))
        return dict(name=name, take=os.path.relpath(take, ROOT), t0=t0, has_audio=True, audio_lag_ms=L, r=round(nrm, 2),
                    place_audio_frame0_at=round(t0 + L / 1000, 4), passthrough=bool(nrm >= 0.3),
                    note="where the take's SOUNDTRACK sits in the song (raw waveform); says nothing about the mouth")
    ea, es = band_env(a, sr), band_env(s, sr)
    off0 = int(round((t0 - s0) * 1000))       # stem index of song time t0

    def best(seg0, seg1):
        x = ea[seg0:seg1]
        cs = []
        for L in range(-int(M * 1000), int(M * 1000) + 1, 1):
            i = off0 + seg0 + L
            if i < 0 or i + len(x) > len(es):
                cs.append(-1); continue
            cs.append(float(np.dot(x, es[i:i + len(x)]) / len(x)))
        cs = np.array(cs); k = int(np.argmax(cs))
        lags = np.arange(-int(M * 1000), int(M * 1000) + 1)
        far = cs[np.abs(lags - lags[k]) > 120]
        return int(lags[k]), float(cs[k]), float(cs[k] - (far.max() if len(far) else 0))
    n = len(ea)
    L, r, margin = best(0, n)
    L1, r1, _ = best(0, n // 2)
    L2, r2, _ = best(n // 2, n)
    res = dict(name=name, take=os.path.relpath(take, ROOT), t0=t0, has_audio=True, audio_lag_ms=L, r=round(r, 2),
               margin=round(margin, 2), half_lags_ms=[L1, L2], half_r=[round(r1, 2), round(r2, 2)], drift_ms=abs(L1 - L2),
               place_frame0_at=round(t0 + L / 1000, 4), shift_f=round(L / 1000 * FPS, 2))
    res["trust"] = bool(r >= 0.5 and margin >= 0.1)
    return res


def words():
    t = json.load(open(TIMING))
    out = []
    for ln in t["lines"]:
        for w in ln.get("words", []):
            out.append((w["start"], w["end"], w.get("w") or w.get("text") or "", w.get("confidence")))
    return out


def is_bilabial(w):
    wl = w.lower().strip(",.?!'")
    return (w[:1] in BILAB) or (wl[:1] in ("m", "b", "p") and wl.isascii())


def strip(take, t0, shift, name, pick=None, every=2):
    import cv2
    import mediapipe as mp
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    frames, fps = LS.read_frames(take)
    n = len(frames)
    place = t0 + shift / FPS
    H, W = frames[0].shape[:2]
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=4 if pick else 1, refine_landmarks=True,
                                         min_detection_confidence=0.2, min_tracking_confidence=0.2)
    lm = []
    for f in frames:
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            lm.append(None); continue
        faces = r.multi_face_landmarks
        if pick:
            faces = sorted(faces, key=lambda F: (F.landmark[1].x * W - pick[0]) ** 2 + (F.landmark[1].y * H - pick[1]) ** 2)
            pick = [faces[0].landmark[1].x * W, faces[0].landmark[1].y * H]
        lm.append(np.array([[p.x * W, p.y * H] for p in faces[0].landmark]))
    ok = [x for x in lm if x is not None]
    if len(ok) < 0.5 * n:
        return dict(name=name, error=f"face found on {len(ok)}/{n} frames")
    iod = np.array([np.linalg.norm(x[33] - x[263]) if x is not None else np.nan for x in lm])
    gap = np.array([np.linalg.norm(x[13] - x[14]) if x is not None else np.nan for x in lm]) / iod
    jaw = np.array([np.linalg.norm(x[152] - x[1]) if x is not None else np.nan for x in lm]) / iod
    good = ~np.isnan(gap)
    jr = float(np.corrcoef(gap[good], jaw[good])[0, 1]) if good.sum() > 5 else float("nan")
    W_ = [w for w in words() if place - 0.05 <= w[0] <= place + n / FPS]
    if not W_:
        return dict(name=name, error="no sung words in this take at this placement")
    f_a = max(0, int((W_[0][0] - place) * FPS) - 3)
    f_b = min(n - 1, int((W_[-1][1] - place) * FPS) + 3)
    miod = float(np.nanmedian(iod))
    cw, ch = 2.3 * miod, 1.45 * miod                         # crop size in take pixels: cheeks, nose tip to below chin
    scale_cut = 540 / H                                       # take pixel -> cut pixel
    z = max(2.0 * scale_cut * cw, 200) / cw                   # >= 2x the cut's pixels, at least 200 px wide
    z = min(z, 230 / cw) if z * cw > 230 else z
    cwz, chz = int(cw * z), int(ch * z)
    fc, fl = ImageFont.truetype(FONT, 13), ImageFont.truetype(LFONT, 12)

    def text(d, xy, s, fill):
        x, y = xy
        for chh in s:
            f = fl if ord(chh) < 0x2000 else fc
            d.text((x, y), chh, font=f, fill=fill)
            x += d.textlength(chh, font=f)

    def cell(k):
        x = lm[k] if lm[k] is not None else next((lm[j] for j in range(k, -1, -1) if lm[j] is not None), ok[0])
        cx, cy = x[1][0], x[1][1] - 0.35 * miod                # top of the crop just above the nose tip
        x0, y0 = int(cx - cw / 2), int(cy)
        im = cv2.cvtColor(frames[k], cv2.COLOR_BGR2RGB)
        pad = int(max(cw, ch))
        im = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT)
        c = im[y0 + pad:y0 + pad + int(ch), x0 + pad:x0 + pad + int(cw)]
        c = cv2.resize(c, (cwz, chz), interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(c)

    def word_at(k):
        t = place + k / FPS
        for s, e, w, conf in W_:
            if s - 0.5 / FPS <= t < e:
                tag = "B" if is_bilabial(w) and abs(t - s) <= 1.0 / FPS else ("V" if abs(t - (s + min(0.12, (e - s) / 2))) <= 1.0 / FPS else "")
                return w, tag
        return "", ""
    ks = [0] + list(range(f_a, f_b + 1, every))
    cols = max(6, min(12, int(1800 // (cwz + 4))))
    rows = (len(ks) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cwz + 4), rows * (chz + 22) + 30), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    text(d, (6, 6), f"{name}  frame0 at song {place:.3f}s (t0 {t0} shift {shift:+g} f)  every {every} f  jaw_r {jr:.2f}  "
                   f"cell 0 = frame 0 (reference)", (230, 230, 230))
    for i, k in enumerate(ks):
        r_, c_ = divmod(i, cols)
        X, Y = c_ * (cwz + 4), 30 + r_ * (chz + 22)
        sheet.paste(cell(k), (X, Y))
        w, tag = word_at(k) if i else ("REF f0", "")
        col = {"B": (230, 60, 60), "V": (60, 200, 90)}.get(tag, (200, 200, 200))
        if tag:
            d.rectangle([X, Y, X + cwz - 1, Y + chz - 1], outline=col, width=3)
        g = gap[k] if not np.isnan(gap[k]) else 0
        d.rectangle([X, Y + chz + 2, X + int(min(1, g / 0.6) * (cwz - 1)), Y + chz + 6], fill=(240, 200, 60))
        text(d, (X + 2, Y + chz + 6), f"f{k} {w}", col)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{name}_face.jpg")
    sheet.save(p, quality=88)
    res = dict(name=name, take=os.path.relpath(take, ROOT), place_frame0_at=round(place, 4), face_found_pct=round(100 * len(ok) / n, 1),
               iod_px=round(miod, 1), face_px_in_cut=round(miod * 2.6 * scale_cut), jaw_r=round(jr, 2),
               jaw_range=round(float(np.nanpercentile(jaw, 95) - np.nanpercentile(jaw, 5)), 3),
               gap_range=round(float(np.nanpercentile(gap, 95) - np.nanpercentile(gap, 5)), 3), strip=os.path.relpath(p, ROOT),
               frames=[f_a, f_b], gap=[None if np.isnan(v) else round(float(v), 4) for v in gap],
               jaw=[None if np.isnan(v) else round(float(v), 4) for v in jaw])
    json.dump(res, open(os.path.join(OUT, f"{name}_face.json"), "w"), indent=1)
    return res


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    pos, o = opts(sys.argv[2:])
    take = os.path.abspath(pos[0]); t0 = float(o["t0"])
    name = o.get("name") or os.path.splitext(os.path.basename(take))[0]
    if cmd == "audiolag":
        r = audiolag(take, t0, name)
        os.makedirs(OUT, exist_ok=True)
        json.dump(r, open(os.path.join(OUT, f"{name}_audiolag.json"), "w"), indent=1)
        print(json.dumps(r))
    elif cmd == "strip":
        try:
            import mediapipe  # noqa: F401
        except ImportError:
            if os.path.exists(LS.MP_PY) and os.environ.get("LIPSYNC_REEXEC") != "1":
                sys.exit(subprocess.run([LS.MP_PY, os.path.abspath(__file__)] + sys.argv[1:],
                                        env=dict(os.environ, LIPSYNC_REEXEC="1")).returncode)
            raise SystemExit("mediapipe not available (set MP_PY)")
        pick = [float(v) for v in o["pick"].split(",")] if o.get("pick") else None
        r = strip(take, t0, float(o.get("shift", 0)), name, pick, int(o.get("every", 2)))
        print(json.dumps({k: v for k, v in r.items() if k not in ("gap", "jaw")}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

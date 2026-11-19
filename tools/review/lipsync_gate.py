#!/usr/bin/env python3
"""Lip-sync QA gate (REVISION_V3 section 2.6): a singing face ships only if it passes this.

    $PY tools/review/lipsync_gate.py TAKE.mp4 --t0 T [--shift N] [--name SHOT_takeN] [--out DIR]
                                     [--eye "pass|fail: what you saw"] [--check] [--log] [--box x,y,w,h] [--pick x,y]

TAKE   the generated take.  --t0 T = song time (s) that the take's frame 0 was generated for
       (= the start of the audio window you sent the model).
--shift N   the retime actually used, in 24 fps frames: the take is placed N frames LATER than t0 (negative = earlier),
            i.e. clip frame 0 sits at song time T + N/24. Omit it and the gate picks the shift itself.
--eye       your verdict after LOOKING at the strip. Without it the result can only be AUTO-PASS (needs eye) or FAIL.
--pick x,y  two faces in frame: measure the one whose nose is nearest to pixel x,y in frame 0.
--check     also write <name>_check.mp4: the take at the chosen placement with the song under it (watch it once).
--log       append the result line to docs/logs/LOG_v3_lipsync.md

What it measures
1. Envelope lag (tools/review/lipsync.py): FaceMesh inner-lip gap against the 1-3 kHz vocal envelope -> lag_vs_synced, r, sharp.
2. Viseme lag: from analysis/timing.json it takes every word in the window. Bilabial closures (m/b/p; 妈 没 蹦 变 百 ...)
   must show a CLOSED mouth just before the word's onset (or at the word's end for a final m/p); every word's vowel must
   show an OPEN mouth (lip gap sampled at the exact times). The score is scanned over placements of -12..+12 frames; the best one is the viseme lag. This does
   not depend on loudness, so it works on legato lines where the envelope is flat.
3. The shift used = --shift, else the viseme lag when it is trusted (>= 3 bilabials and a clear peak), else the envelope
   lag when it is trusted (r >= 0.4 and sharp >= 0.35). If both are trusted they must agree within 1 frame, or the take
   is AMBIGUOUS. If neither is trusted the take is AMBIGUOUS: try shifts by hand with --shift and judge the strip.
4. At that placement: closed = share of bilabials whose mouth is closed, open = share of vowels whose mouth is open (lip gap >= 0.3 of the take's range, or >= 0.12 after rising from a shut mouth),
   drift = spread of the per-bilabial timing error in frames (a re-sung take drifts: one shift cannot fix it).
5. The word strip <name>_strip.jpg: one cell per word at the chosen placement. Red cells are bilabial closures (three
   consecutive frames ending on the onset frame: the mouth must be shut in at least one of the first two); grey cells are
   the vowel frame of each word (the mouth must be open); blue cells are phrase starts (first word after a silence): four
   frames at -3, -1, +1, +3 around the onset, the mouth must start moving between the second and third (this is the check
   that works on sparse lines such as "Yes" or "You're able", where the envelope has too little to hold on to).

With --shift given and no trustworthy lag measure (sparse line), the numbers can only say AUTO-PASS: the strip decides.
PASS needs all of: no phrase start later than +2 f or earlier than -6 f; face tracked on >= 90 % of frames; articulation >= 0.04; residual lag within +-1 frame (envelope, if
trustworthy, and viseme); closed >= 0.75; open >= 0.8; drift <= 1.5 frames; and --eye pass.
Exit code: 0 PASS or AUTO-PASS, 2 FAIL, 3 AMBIGUOUS / unreadable.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import lipsync as LS  # noqa: E402

FPS = 24.0
STEM = os.path.join(ROOT, "work/stems/vocals.wav")
TIMING = os.path.join(ROOT, "analysis/timing.json")
LOG = os.path.join(ROOT, "docs/logs/LOG_v3_lipsync.md")
CJK_FONT = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
LATIN_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Raw envelope lag of takes whose audio is known to be aligned (p-video-avatar passes the stem through, offset 0.0 ms):
# -42, -83 (first bake-off), -42, -125, -125, -83, -125, -83 (v3 bake-off). Mean -90 ms, spread +-45 ms = +-1.1 frame.
# So the envelope alone cannot certify +-1 frame; its tolerance below is 1.5 f and the strip decides.
BIAS_MS = -90
BILABIAL_CJK = set("妈没蹦变百白把拔每毛不爸怕跑朋本帮被别比边步")
SILENT_B = {"climb", "thumb", "lamb", "comb", "bomb", "dumb"}


def parse():
    a = sys.argv[1:]
    o, pos, i = {}, [], 0
    while i < len(a):
        if a[i].startswith("--"):
            k = a[i][2:]
            if k in ("check", "log", "json"):
                o[k] = True; i += 1
            else:
                o[k] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    if not pos or "t0" not in o:
        raise SystemExit(__doc__)
    return pos[0], o


def bilabial_events(w):
    """-> list of ('init'|'final'|'mid') for one timing word."""
    s = w["w"].lower()
    if re.search(r"[一-鿿]", s):
        return ["init"] if s[0] in BILABIAL_CJK else []
    s = re.sub(r"[^a-z']", "", s)
    if not s:
        return []
    ev = []
    if s[0] in "mbp" and not s.startswith("ph"):
        ev.append("init")
    core = re.sub(r"(e|es|s|ed|'s|'m)$", "", s) if len(s) > 2 else s
    if s.endswith("'m"):
        ev.append("final")
    elif s not in SILENT_B and len(core) > 1 and core[-1] in "mbp" and not (len(core) == 1):
        ev.append("final")
    mid = core[1:-1] if len(core) > 2 else ""
    if re.search(r"[mbp]", mid.replace("ph", "")) and s not in ("remember",):
        ev.append("mid")
    if s == "remember":
        ev += ["mid"]
    return ev


def _sounding(tm, tv):
    """True if the vocal stem at tm is within 9 dB of its level at the vowel point tv."""
    import numpy as np
    def lvl(t):
        raw = subprocess.run([LS.FFMPEG, "-v", "error", "-ss", f"{max(0, t - 0.05):.3f}", "-t", "0.1", "-i", STEM, "-ac", "1", "-ar", "16000",
                              "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32)
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) if len(x) else -120
    return lvl(tm) > lvl(tv) - 9


def events(t_a, t_b):
    """Words whose onset lies in [t_a, t_b] -> closures and vowels (song times)."""
    T = json.load(open(TIMING))
    out = []
    for l in T["lines"]:
        if l.get("echo"):
            continue
        for w in l["words"]:
            if not (t_a <= w["start"] <= t_b) or w.get("confidence") == "low":     # low-confidence times are not judged
                continue
            st, en = w["start"], max(w["end"], w["start"] + 0.06)
            for kind in bilabial_events(w):
                if kind == "init":      # lips shut during the frames just before the release (= the measured onset)
                    out.append(dict(kind="B", word=w["w"], t=st - 0.030, lo=st - 0.085, hi=st + 0.005, tag="init"))
                elif kind == "final":
                    out.append(dict(kind="B", word=w["w"] + "|", t=en + 0.02, lo=en - 0.03, hi=en + 0.09, tag="final"))
                else:
                    out.append(dict(kind="B", word="-" + w["w"] + "-", t=(st + en) / 2, lo=st + 0.04, hi=en - 0.02, tag="mid"))
            tv = st + min(0.5 * (en - st), 0.14)
            out.append(dict(kind="V", word=w["w"], t=tv, lo=tv - 0.02, hi=tv + 0.045, tag="vowel"))
            if en - st >= 0.5 and _sounding(st + 0.5 * (en - st), tv):   # a held note still sounding at its middle
                tm = st + 0.5 * (en - st)
                out.append(dict(kind="V", word=w["w"] + "~", t=tm, lo=tm - 0.06, hi=tm + 0.06, tag="hold"))
    words = sorted((w["start"], max(w["end"], w["start"] + 0.06), w["w"], w.get("confidence")) for l in T["lines"] if not l.get("echo") for w in l["words"])
    for i, (st, en, ww, cf_) in enumerate(words):
        if cf_ != "low" and t_a <= st <= t_b and (i == 0 or (st - words[i - 1][1] >= 0.15 and words[i - 1][3] != "low")):
            out.append(dict(kind="S", word=">" + ww, t=st, lo=st - 0.1, hi=st + 0.1, tag="start"))
    out.sort(key=lambda e: e["t"])
    return out


def norm_gap(op):
    import numpy as np
    v = np.array(op, float)
    idx = np.arange(len(v)); good = ~np.isnan(v)
    if good.sum() > 2:
        v = np.interp(idx, idx[good], v[good])
    lo, hi = np.percentile(v, 5), np.percentile(v, 95)
    return np.clip((v - lo) / (hi - lo + 1e-9), 0, 1), lo, hi


def fidx(t, place, n):
    return int(round((t - place) * FPS))


def score_at(g, ev, place):
    """closed share, open share, combined score at a placement (song time of clip frame 0)."""
    import numpy as np
    n = len(g)
    c, o = [], []
    for e in ev:
        a, b = int(np.floor((e["lo"] - place) * FPS)), int(np.ceil((e["hi"] - place) * FPS))
        a, b = max(a, 0), min(b, n - 1)
        if b < a or b < 0 or a > n - 1:
            continue
        seg = g[a:b + 1]
        if e["kind"] == "S" or (e["t"] - place) * FPS > n - 1:
            continue
        if e["kind"] == "B":
            c.append(1.0 - float(seg.min()))
        else:
            v = float(seg.max())
            # a small, rounded vowel (you, to, 悟) still counts if the mouth clearly opened INTO it from a shut mouth
            if v < 0.30 and v >= 0.12 and v - float(g[max(a - 6, 0):a + 1].min()) >= 0.10:
                v = 0.30
            o.append(v)
    cs = float(np.mean(c)) if c else float("nan")
    os_ = float(np.mean(o)) if o else float("nan")
    return c, o, (np.nanmean([cs, os_]) if (c or o) else float("nan"))


def score_point(g, ev, place):
    """Sharp version for the lag scan: the lip gap sampled exactly at each closure / vowel time (no tolerance window)."""
    import numpy as np
    n = len(g); c, o = [], []
    for e in ev:
        if e["tag"] == "mid":
            continue
        x = (e["t"] - place) * FPS
        if x < 0 or x > n - 1:
            continue
        v = float(np.interp(x, np.arange(n), g))
        if e["kind"] == "B":
            c.append(1.0 - v)
        else:
            # the vowel is open AND the mouth opened into it (gap now minus gap 2.5 frames before the vowel point)
            before = float(np.interp(max(x - 2.5, 0), np.arange(n), g))
            o.append(0.5 * v + 0.5 * min(max(0.5 + (v - before), 0.0), 1.0))
    if not c and not o:
        return float("nan")
    return float(np.nanmean([np.mean(c) if c else np.nan, np.mean(o) if o else np.nan]))


def main():
    clip, o = parse()
    try:
        import mediapipe  # noqa: F401
    except ImportError:
        if os.path.exists(LS.MP_PY) and os.environ.get("LIPSYNC_REEXEC") != "1":
            sys.exit(subprocess.run([LS.MP_PY, os.path.abspath(__file__)] + sys.argv[1:],
                                    env=dict(os.environ, LIPSYNC_REEXEC="1")).returncode)
        raise SystemExit("mediapipe not available (set MP_PY)")
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    t0 = float(o["t0"])
    name = o.get("name") or os.path.splitext(os.path.basename(clip))[0]
    outdir = o.get("out") or os.path.join(ROOT, "work/review/lipsync_gate")
    os.makedirs(outdir, exist_ok=True)
    frames, fps = LS.read_frames(clip)
    n = len(frames)
    res = dict(name=name, clip=os.path.relpath(os.path.abspath(clip), ROOT), t0=t0, frames=n, fps=round(fps, 3))
    if abs(fps - FPS) > 0.01:
        res["warning"] = f"clip is {fps:.3f} fps, not 24: conform it first (ffmpeg -vf fps=24)"

    # --- mouth series + landmarks for the crops
    import mediapipe as mp
    pick = [float(v) for v in o["pick"].split(",")] if o.get("pick") else None
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=4 if pick else 1, refine_landmarks=True,
                                         min_detection_confidence=0.2, min_tracking_confidence=0.2)
    op, boxes, ok = [], [], 0
    for f in frames:
        h, w = f.shape[:2]
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            op.append(np.nan); boxes.append(None); continue
        ok += 1
        faces = r.multi_face_landmarks
        if pick:
            faces = sorted(faces, key=lambda F: (F.landmark[1].x * w - pick[0]) ** 2 + (F.landmark[1].y * h - pick[1]) ** 2)
            pick = [faces[0].landmark[1].x * w, faces[0].landmark[1].y * h]
        L = faces[0].landmark
        P = lambda i: np.array([L[i].x * w, L[i].y * h])  # noqa: E731
        iod = np.linalg.norm(P(33) - P(263)) + 1e-6
        op.append(np.linalg.norm(P(13) - P(14)) / iod)
        c = (P(61) + P(291)) / 2
        boxes.append((c[0], c[1], iod))
    res["face_found_pct"] = round(100 * ok / max(1, n), 1)
    if o.get("box"):
        x, y, bw, bh = (int(v) for v in o["box"].split(","))
        m, _ = LS.mouth_dark(frames, (x, y, bw, bh))
        op = list(m); boxes = [(x + bw / 2, y + bh / 2, bw * 0.9)] * n
        res["method"] = "dark-area box"
    elif ok < 0.9 * n:
        res.update(verdict="FAIL", reason=f"face tracked on only {res['face_found_pct']} % of frames: the mouth cannot be "
                   "measured, so by rule 2.6 it cannot ship as a singing face. Re-frame closer / more frontal, or play the "
                   "line off the listener, the book or the hands.")
        return finish(res, o, outdir, 3)
    op = np.array(op, float)
    art = float(np.nanpercentile(op, 95) - np.nanpercentile(op, 5))
    res["articulation"] = round(art, 3)
    g, lo, hi = norm_gap(op)

    # --- 1. envelope lag
    e = LS.envelope(STEM, t0, n, fps)
    lag, r, sharp, lags, rs = LS.xcorr(LS.hp_z(op, fps), LS.hp_z(e, fps), fps, 0.6)
    env_ms = lag * 1000 - BIAS_MS             # picture late by this much
    env_ok = bool(r >= 0.4 and sharp >= 0.35)       # re-checked below: needs >= 5 words in the take
    res.update(env_lag_ms=round(env_ms), r=round(float(r), 2), sharp=round(float(sharp), 2), env_trust=env_ok)

    # --- 2. viseme lag scan (placement = t0 + s/24: positive s = play the take later)
    ev = events(t0 - 0.02, t0 + n / fps - 0.08)
    nb = sum(1 for x in ev if x["kind"] == "B")
    res["n_bilabials"], res["n_words"] = nb, sum(1 for x in ev if x["kind"] == "V" and x["tag"] == "vowel")
    if res["n_words"] < 5:
        env_ok = False; res["env_trust"] = False
    R = int(o.get("scan", 12))          # --scan N: search +-N frames (v4: 18 for Seedance, whose lag reaches +-700 ms)
    scan = {s: score_point(g, ev, t0 + s / FPS) for s in range(-R, R + 1)}
    top = max(scan.values())
    plateau = [s for s in scan if scan[s] >= top - 0.015]
    best = min(plateau, key=lambda s: abs(s - float(np.mean(plateau))))      # centre of the plateau
    vis_shift = best
    res["viseme_shift_f"] = vis_shift
    res["viseme_score_best"] = round(float(scan[best]), 2)
    srt = sorted(scan.values(), reverse=True)
    res["viseme_margin"] = round(float(scan[best] - np.median(list(scan.values()))), 2)
    # envelope says the picture is late by env_ms -> play the take earlier by that much
    env_shift = -int(round(env_ms / 1000 * FPS))
    res["env_shift_f"] = env_shift

    # --- 3. choose the shift. The viseme scan is only trusted with >= 3 bilabials and a clear peak.
    vis_ok = bool(nb >= 3 and res["viseme_margin"] >= 0.15)
    res["viseme_trust"] = vis_ok
    if "shift" in o:
        shift, why = int(o["shift"]), "given"
    elif env_ok and vis_ok:
        shift = vis_shift if abs(env_shift - vis_shift) <= 1 else env_shift
        why = "viseme+envelope agree" if abs(env_shift - vis_shift) <= 1 else "envelope (viseme disagrees)"
    elif vis_ok:
        shift, why = vis_shift, "viseme (envelope weak)"
    elif env_ok:
        shift, why = env_shift, "envelope (too few bilabials for viseme)"
    else:
        shift, why = env_shift, "none trusted"
    res.update(shift_f=shift, shift_from=why, place_frame0_at=round(t0 + shift / FPS, 3))
    place = t0 + shift / FPS

    # --- 4. residuals and shares at the chosen placement
    c, ov, sc = score_at(g, ev, place)
    closed = float(np.mean([x >= 0.70 for x in c])) if c else float("nan")
    opened = float(np.mean([x >= 0.30 for x in ov])) if ov else float("nan")
    res.update(closed=round(closed, 2) if c else None, open=round(opened, 2) if ov else None,
               viseme_score=round(float(sc), 2))
    res["resid_env_f"] = round(env_ms / 1000 * FPS + shift, 1) if env_ok else None      # >0: picture still late
    res["resid_viseme_f"] = shift - vis_shift
    # per-bilabial timing error: where is the nearest closure (local min of g below 0.3) around the nominal frame
    errs = []
    for x in ev:
        if x["kind"] != "B" or x["tag"] == "mid":
            continue
        f0 = fidx(x["t"], place, n)
        best_k, best_v = None, 9
        for k in range(-3, 4):
            j = f0 + k
            if 0 <= j < n and g[j] < 0.30 and (g[j] < best_v - 0.02 or (abs(g[j] - best_v) <= 0.02 and abs(k) < abs(best_k))):
                best_k, best_v = k, g[j]
        x["err_f"] = best_k
        if best_k is not None:
            errs.append(best_k)
    starts = []
    for x in ev:
        if x["kind"] != "S":
            continue
        f0 = (x["t"] - place) * FPS
        a, b = int(np.floor(f0)) - 6, int(np.ceil(f0)) + 6
        if a < 0 or b >= n:
            continue
        rest = float(np.median(g[max(a - 3, 0):a + 3]))
        mv = [j for j in range(a + 2, b) if abs(g[j] - rest) > 0.2 and abs(g[j + 1] - rest) > 0.2]
        x["err_f"] = round(mv[0] - f0, 1) if mv else None
        starts.append(x["err_f"])
    res["phrase_start_err_f"] = starts
    res["bilabial_err_f"] = [x.get("err_f") for x in ev if x["kind"] == "B" and x["tag"] != "mid"]
    res["gap"] = [round(float(v), 2) for v in g]
    res["drift_f"] = round(float(np.mean(np.abs(np.array(errs) - np.median(errs)))), 1) if len(errs) >= 2 else 0.0
    res["viseme_scan"] = {str(k): round(float(v), 2) for k, v in scan.items()}

    # --- 5. strip
    strip = os.path.join(outdir, f"{name}_strip.jpg")
    make_strip(strip, frames, boxes, g, ev, place, n, res, Image, ImageDraw, ImageFont, cv2, np)
    res["strip"] = os.path.relpath(strip, ROOT)

    # --- verdict
    fails, amb = [], []
    if art < 0.04:
        fails.append(f"mouth barely moves (articulation {art:.3f})")
    if env_ok and abs(res["resid_env_f"]) > 1.5:
        (fails if why == "given" else amb).append(f"envelope lag {res['resid_env_f']:+.1f} f at this placement")
    if vis_ok and abs(res["resid_viseme_f"]) > 1:
        (fails if why == "given" else amb).append(f"viseme scan wants {-res['resid_viseme_f']:+d} f from this placement")
    if not env_ok and not vis_ok and why != "given":
        amb.append("neither the envelope nor the viseme scan finds a clear lag: place by the strip (try --shift) or reject")
    if not env_ok and abs(shift) > 6 and why != "given":
        amb.append(f"a {shift:+d} f shift on an untrusted envelope: likely a chance match, check the strip hard or reject")
    if c and closed < 0.75:
        fails.append(f"bilabials closed on only {closed:.0%}")
    if ov and opened < 0.8:
        fails.append(f"vowels open on only {opened:.0%}")
    # mouths move before the sound (breath, shutting for an m): up to 6 f early is natural; late by more than 2 f is not
    bad = [e_ for e_ in starts if e_ is not None and (e_ > 2.0 or e_ < -6.0)]
    if bad:
        fails.append(f"a phrase starts {bad[0]:+.0f} f off its word onset (allowed -6..+2)")
    if res["n_words"] < 5 and why != "given":
        amb.append("fewer than 5 words: the lag cannot be found from this take alone; place it by construction (--shift) and judge the strip")
    if res["drift_f"] > 1.5:
        fails.append(f"timing drifts inside the take (sd {res['drift_f']} f): one shift cannot fix it")
    eye = o.get("eye", "")
    res["eye"] = eye
    if fails:
        res["verdict"], code = "FAIL", 2
    elif amb:
        res["verdict"], code = "AMBIGUOUS", 3
    elif eye.lower().startswith("pass"):
        res["verdict"], code = "PASS", 0
    elif eye.lower().startswith("fail"):
        res["verdict"], code = "FAIL", 2; fails.append("by eye: " + eye)
    else:
        res["verdict"], code = "AUTO-PASS (look at the strip, then re-run with --eye)", 0
    if eye.lower().startswith("fail") and "by eye: " + eye not in fails:
        res["verdict"], code = "FAIL", 2; fails.append("by eye: " + eye)
    res["reason"] = "; ".join(fails + amb)

    if o.get("check"):
        chk = os.path.join(outdir, f"{name}_check.mp4")
        song = os.path.join(ROOT, json.load(open(TIMING))["meta"]["file"])
        if not os.path.exists(song):
            song = STEM
        subprocess.run([LS.FFMPEG, "-v", "error", "-y", "-i", clip, "-ss", f"{place:.3f}", "-t", f"{n / fps:.3f}", "-i", song,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "24",
                        "-c:a", "aac", "-shortest", chk], check=True)
        res["check"] = os.path.relpath(chk, ROOT)
    return finish(res, o, outdir, code)


def make_strip(out, frames, boxes, g, ev, place, n, res, Image, ImageDraw, ImageFont, cv2, np):
    CW, CH, PAD, LAB = 132, 100, 4, 38
    def fonts(size):
        try:
            return ImageFont.truetype(LATIN_FONT, size), ImageFont.truetype(CJK_FONT, size)
        except OSError:
            f = ImageFont.load_default(); return f, f
    font, small = fonts(16), fonts(12)

    class D:   # draws mixed Latin / CJK runs
        def __init__(self, dr): self.dr = dr
        def rectangle(self, *a, **k): self.dr.rectangle(*a, **k)
        def text(self, xy, s, fill, font):
            x, y = xy
            for run in re.findall(r"[\u2e80-\u9fff\uff00-\uffef]+|[^\u2e80-\u9fff\uff00-\uffef]+", s):
                f = font[1] if re.match(r"[\u2e80-\u9fff\uff00-\uffef]", run) else font[0]
                self.dr.text((x, y), run, fill=fill, font=f); x += self.dr.textlength(run, font=f)

    def crop(j):
        j = min(max(j, 0), n - 1)
        b = boxes[j] or next((x for x in boxes[j:] + boxes[:j][::-1] if x), None)
        f = frames[j]
        if b is None:
            return Image.new("RGB", (CW, CH), (40, 40, 40))
        cx, cy, iod = b
        hw = iod * 0.62; hh = hw * CH / CW
        x0, y0, x1, y1 = int(cx - hw), int(cy - hh * 0.9), int(cx + hw), int(cy + hh * 1.1)
        H, W = f.shape[:2]
        pad = cv2.copyMakeBorder(f, 200, 200, 200, 200, cv2.BORDER_REPLICATE)
        c = pad[y0 + 200:y1 + 200, x0 + 200:x1 + 200]
        c = cv2.resize(c, (CW, CH), interpolation=cv2.INTER_AREA if c.shape[1] > CW else cv2.INTER_CUBIC)
        return Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB))

    cells = []
    for e in ev:
        f0 = int(round((e["t"] - place) * 24.0))
        if f0 < -1 or f0 > n:
            continue
        if e["kind"] == "B":
            js = [f0 - 1, f0, f0 + 1]
        elif e["kind"] == "S":
            js = [f0 - 3, f0 - 1, f0 + 1, f0 + 3]
        else:
            js = [f0]
        cells.append((e, js))
    per_row_w = 1900
    rows, cur, wsum = [], [], 0
    for e, js in cells:
        wc = len(js) * CW + PAD * 2 + 6
        if wsum + wc > per_row_w and cur:
            rows.append(cur); cur, wsum = [], 0
        cur.append((e, js)); wsum += wc
    if cur:
        rows.append(cur)
    HEAD = 50
    img = Image.new("RGB", (per_row_w + 20, HEAD + len(rows) * (CH + LAB + 14) + 8), (250, 248, 242))
    d = D(ImageDraw.Draw(img))
    d.text((10, 4), f"{res['name']}   frame 0 at song {res['place_frame0_at']} s (shift {res['shift_f']:+d} f, {res['shift_from']})   "
           f"env lag {res['env_lag_ms']:+d} ms r {res['r']} sharp {res['sharp']}   viseme shift {res['viseme_shift_f']:+d} f",
           fill=(0, 0, 0), font=font)
    d.text((10, 28), "RED = bilabial m/b/p: 3 frames ending at the onset; the lips must be SHUT in one of the first two.   "
           "GREY = the word's vowel frame: the mouth must be OPEN.   number = clip frame, bar = measured lip gap (0..1)",
           fill=(90, 90, 90), font=small)
    y = HEAD
    for row in rows:
        x = 10
        for e, js in row:
            red = e["kind"] == "B"; blue = e["kind"] == "S"
            wc = len(js) * CW
            d.rectangle([x - 3, y - 3, x + wc + 2, y + CH + LAB + 4], outline=(200, 30, 30) if red else (40, 80, 200) if blue else (170, 170, 170),
                        width=3 if (red or blue) else 1)
            for k, j in enumerate(js):
                img.paste(crop(j), (x + k * CW, y))
                jj = min(max(j, 0), n - 1)
                gv = float(g[jj])
                d.rectangle([x + k * CW + 2, y + CH - 6, x + k * CW + 2 + int(gv * (CW - 4)), y + CH - 2],
                            fill=(30, 140, 60) if gv >= 0.3 else (200, 30, 30))
                d.text((x + k * CW + 3, y + 2), str(j), fill=(255, 255, 0), font=small)
            lab = e["word"] + ("  [" + {"init": "closed before", "final": "closed after", "mid": "closed inside"}[e["tag"]] + "]" if red else
                               "  [phrase start: -3 -1 +1 +3 f]" if blue else "")
            d.text((x + 2, y + CH + 1), lab, fill=(170, 0, 0) if red else (30, 60, 170) if blue else (0, 0, 0), font=font)
            d.text((x + 2, y + CH + 22), f"{e['t']:.2f}s" + (f"  err {e['err_f']:+.0f}f" if (red or blue) and e.get("err_f") is not None else
                                                              ("  no closure" if red and e["tag"] != "mid" else "")),
                   fill=(110, 110, 110), font=small)
            x += wc + PAD * 2 + 6
        y += CH + LAB + 14
    img.save(out, quality=88)


def finish(res, o, outdir, code):
    jp = os.path.join(outdir, f"{res['name']}_gate.json")
    json.dump(res, open(jp, "w"), ensure_ascii=False, indent=1)
    if o.get("json"):
        print(json.dumps(res, ensure_ascii=False))
    else:
        for k, v in res.items():
            print(f"{k:20s} {v}")
    if o.get("log"):
        new = not os.path.exists(LOG)
        with open(LOG, "a") as f:
            if new:
                f.write("# LOG v3 lip-sync (gate results; tools/review/lipsync_gate.py)\n\n"
                        "| take | t0 | shift f | frame 0 at | env lag ms | r | sharp | viseme shift | closed | open | drift f | verdict | eye / reason | strip |\n"
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
            g = res.get
            f.write(f"| {g('clip')} | {g('t0')} | {g('shift_f')} | {g('place_frame0_at')} | {g('env_lag_ms')} | {g('r')} | {g('sharp')} | "
                    f"{g('viseme_shift_f')} | {g('closed')} | {g('open')} | {g('drift_f')} | **{g('verdict')}** | "
                    f"{(g('eye') or '') + (' / ' + g('reason') if g('reason') else '')} | {g('strip')} |\n")
    sys.exit(code)


if __name__ == "__main__":
    main()

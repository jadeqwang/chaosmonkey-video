#!/usr/bin/env python3
"""RETIRED in v4 (REVISION_V4 §1.2: no transferred mouths). Use tools/gen/lipsync_v4.py. Kept as the record.
Singing takes, the v3 way (docs/LIPSYNC_V3.md): acted take + lip driver + local lip transfer + gate.

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    $PY tools/gen/lipsync_take.py act   SHOT KEYFRAME.jpg "acting prompt with timed beats" --t0 T --dur D [--takes 2] [--res 720p]
    $PY tools/gen/lipsync_take.py drive SHOT WHO --t0 T --dur D          # WHO = lj | mama | dau | jade
    $PY tools/gen/gen.py wait <the job ids both printed>
    $PY tools/gen/lipsync_take.py lips  SHOT N --t0 T [--act K | --clip ACTED.mp4] [--pick x,y] [--mask jaw|mouth] [--eye "pass: ..."]
    $PY tools/gen/lipsync_take.py conform SHOT CLIP.mp4 "song:src,song:src,..."     # an existing acted take with a time map

conform  if the acted take is placed in the comp through a piecewise time map (speed changes), bake the map first:
         writes media/gen/ls_<SHOT>_act1_conf.mp4, 24 fps, frame k = song time song_first + k/24 (nearest source frame).
         Then `lips SHOT N --t0 <song_first> --clip media/gen/ls_<SHOT>_act1_conf.mp4`, and in the comp use the result
         1:1 (map [[song_first, 0], [song_last, song_last - song_first]]). The lips must be made AFTER any retime.
drive    --t0 may be earlier than the take's T (pre-roll for the driver); `lips` lines the two up from the spec's t0.

T    song time (s) of the take's frame 0 (the cut's shot start, or up to 0.5 s before the first word). D whole seconds, 3-8.
act    Kling v4 from your keyframe: the PERFORMANCE (eyes, head, brows, hands, breathing). No audio goes to it.
drive  pruna/p-video-avatar on the canon frontal singing frame of WHO with the vocal stem window [T, T+D]: the MOUTH only.
lips   tools/sync/lp_lips.py: lips of the driver onto acted take K (default 1), bilabial closures forced from
       analysis/timing.json -> media/gen/v3/lipsync/<SHOT>_take<N>.mp4, then the gate at shift 0 (--check, --log).
       Look at the strip it names and re-run with --eye to record PASS.
Specs: media/gen/specs/ls_<SHOT>_act<k>.json, ls_<SHOT>_drive.json. Outputs: media/gen/ls_<SHOT>_*.mp4.
"""
import glob, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import gen
PY = sys.executable
STEM = "work/stems/vocals.wav"
DRIVER = {w: f"media/kf/v3/lipsync_test/{w}_sing_1920.jpg" for w in ("lj", "mama", "dau", "jade")}
WHO = {"lj": "The little girl", "dau": "The little girl", "mama": "The woman", "jade": "The woman"}
GUARD = (" Same painting throughout: fine ink line and light colour wash on paper, the same faces and hair, the same framing. "
         "The camera does not move. No text. Wide 16:9 landscape frame.")


def opts(a):
    o, pos, i = {}, [], 0
    while i < len(a):
        if a[i].startswith("--"):
            o[a[i][2:]] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    return pos, o


def spec(tag, model, inp, t0, notes):
    p = os.path.join(ROOT, f"media/gen/specs/{tag}.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"model": model, "tag": tag, "notes": notes, "t0": t0, "input": inp}, open(p, "w"), ensure_ascii=False, indent=1)
    return p


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, (pos, o) = sys.argv[1], opts(sys.argv[2:])
    shot = pos[0]; t0 = float(o.get("t0", 0))
    if cmd == "act":
        kf, prompt = pos[1], pos[2]; dur = int(o["dur"])
        small = os.path.join(ROOT, "media/gen/refs", f"ls_{shot}_1920.jpg")
        gen.ref_image(os.path.join(ROOT, kf), small, max_side=1920)
        p = "Animate the first frame exactly. The singer sings softly, mouth moving with the words. " + prompt + GUARD
        for k in range(1, int(o.get("takes", 2)) + 1):
            sp = spec(f"ls_{shot}_act{k}", "klingai/kling-v4",
                      {"prompt": p, "first_frame": "file:" + os.path.relpath(small, ROOT), "duration": dur, "aspect_ratio": "16:9",
                       "resolution": o.get("res", "720p")}, t0, f"lip-sync v3 acted take; keyframe {kf}; t0={t0}")
            print(gen.submit(sp))
    elif cmd == "drive":
        who = pos[1]; dur = float(o["dur"])
        aud = os.path.join(ROOT, f"media/gen/v3/lipsync/_audio/{shot}.mp3")
        gen.audio_ref(os.path.join(ROOT, STEM), t0, dur, aud)
        sp = spec(f"ls_{shot}_drive", "pruna/p-video-avatar",
                  {"image": "file:" + DRIVER[who], "audio": "file:" + os.path.relpath(aud, ROOT), "voice": "Kore (Female)",
                   "voice_script": "", "voice_language": "English (US)", "voice_prompt": "Sing the following.", "resolution": "720p",
                   "video_prompt": f"{WHO[who]} sings. Her head stays still. The camera does not move.",
                   "negative_prompt": "wide grin, bared teeth, camera move, zoom, reframing, captions, subtitles, text, background change",
                   "strength_negative_prompt": 1.0, "disable_safety_filter": True, "disable_prompt_upsampling": True},
                  t0, f"lip-sync v3 lip driver ({who}); vocal stem {t0}+{dur}s")
        print(gen.submit(sp))
    elif cmd == "conform":
        import cv2
        clip, mp_ = pos[1], sorted(tuple(float(v) for v in x.split(":")) for x in pos[2].split(","))
        cap = cv2.VideoCapture(clip); fps = cap.get(5) or 24.0; W, H = int(cap.get(3)), int(cap.get(4))
        fr = []
        while True:
            ok, f = cap.read()
            if not ok: break
            fr.append(f)
        import numpy as np
        xs, ys = [m[0] for m in mp_], [m[1] for m in mp_]
        nout = int(round((xs[-1] - xs[0]) * 24))
        out = os.path.join(ROOT, f"media/gen/ls_{shot}_act1_conf.mp4")
        pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                                 "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for k in range(nout):
            src = float(np.interp(xs[0] + k / 24.0, xs, ys))
            pipe.stdin.write(fr[min(max(int(round(src * fps)), 0), len(fr) - 1)].tobytes())
        pipe.stdin.close(); pipe.wait()
        print(out, nout, "frames; frame 0 = song", xs[0])
    elif cmd == "lips":
        n = pos[1]; k = o.get("act", "1")
        act = [o["clip"]] if o.get("clip") else sorted(glob.glob(os.path.join(ROOT, f"media/gen/ls_{shot}_act{k}_*.mp4")))
        drv = sorted(glob.glob(os.path.join(ROOT, f"media/gen/ls_{shot}_drive_*.mp4")))
        if not act or not drv:
            raise SystemExit(f"missing take: act {act} drive {drv} (gen.py wait / collect first)")
        os.makedirs(os.path.join(ROOT, "media/gen/v3/lipsync"), exist_ok=True)
        out = os.path.join(ROOT, f"media/gen/v3/lipsync/{shot}_take{n}.mp4")
        pick = ["--pick", o["pick"]] if o.get("pick") else []
        dt0 = json.load(open(os.path.join(ROOT, f"media/gen/specs/ls_{shot}_drive.json")))["t0"]
        off = int(round((t0 - dt0) * 24)) - int(o.get("delay", 1))     # --delay N: the driver mouth N frames later
        extra = sum((["--" + k_, o[k_]] for k_ in ("mask", "rgain", "shape", "gain", "rnow") if o.get(k_)), [])
        subprocess.run([PY, os.path.join(ROOT, "tools/sync/lp_lips.py"), act[-1], drv[-1], out, "--t0", str(t0), "--offset", str(off)]
                       + pick + extra, check=True)
        open(out[:-4] + ".txt", "w").write(f"acted {os.path.relpath(act[-1], ROOT)}\ndriver {os.path.relpath(drv[-1], ROOT)}\nt0 {t0}\n"
                                           f"pick {o.get('pick')}\ntools/sync/lp_lips.py --t0 {t0} --offset {off} {' '.join(extra)}\n")
        g = [PY, os.path.join(ROOT, "tools/review/lipsync_gate.py"), out, "--t0", str(t0), "--shift", "0", "--name", f"{shot}_take{n}",
             "--check"] + pick + (["--eye", o["eye"], "--log"] if o.get("eye") else [])
        sys.exit(subprocess.run(g).returncode)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

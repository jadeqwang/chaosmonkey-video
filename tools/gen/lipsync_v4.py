#!/usr/bin/env python3
"""Singing takes, the v4 way (docs/LIPSYNC_V4.md). Two video models, nothing pasted (REVISION_V4 §1.2):
  pass 1 ACT   Kling v4 from the shot keyframe performs the scene (no audio; a CALM clause: no bounces / fast turns);
  pass 2 SING  pruna/p-video-animate re-renders the whole character from the keyframe with the acted take's motion and the song
               window's audio, which drives the lips; the audio returns bit-exact, so clip frame 0 = song t0, shift 0, speed 1.

    PY=/home/jade/Documents/halys-video/.venv/bin/python; export TMPDIR=$PWD/work/tmp
    $PY tools/gen/lipsync_v4.py act  SHOT KEYFRAME.jpg --who "the woman with glasses" --partner "the little girl in her lap" \
                                     --act "timed beats ..." [--takes 2] [--first T --out T] [--dry 1]
    $PY tools/gen/lipsync_v4.py wait SHOT                          # choose acted take K on its sheet
    $PY tools/gen/lipsync_v4.py anim SHOT K [--seeds 2] [--rap 1] [--prompt "..."]
    $PY tools/gen/lipsync_v4.py wait SHOT
    $PY tools/gen/lipsync_v4.py measure SHOT [--pick x,y]          # gate at shift 0, face strip, sheet -> work/review/lipsync_v4/<SHOT>_takes.tsv
    $PY tools/gen/lipsync_v4.py eye SHOT ls4w_SHOT_aKsN "pass: ..."   # after LOOKING at the strip; appends to the LIPSYNC log
    $PY tools/gen/lipsync_v4.py seedance SHOT KEYFRAME.jpg --who .. --partner .. --lang .. --act .. [--takes 6]   # fallback only

t0 = min(first sung word - 0.5 s, shot in). Specs media/gen/specs/ls4w_<SHOT>_*.json (written before submit), job ids in
media/gen/specs/ls4w_<SHOT>_jobs.txt, takes media/gen/ls4w_<SHOT>_*.mp4. The v3 act/drive/lips method (lipsync_take.py) is retired.
"""
import glob, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import gen
PY = sys.executable
STEM = "work/stems/vocals.wav"
REV = os.path.join(ROOT, "tools/review")
OUTD = os.path.join(ROOT, "work/review/lipsync_v4")
PAD = 1.0
GUARD = (" The picture stays the same hand-painted Chinese ink-and-colour painting on paper in every frame: fine ink line, pale colour"
         " wash, paper grain; faces keep exactly their drawn features, big dark eyes with highlights, rosy cheeks. The camera does not"
         " move. No text, no captions.")


def opts(a):
    o, pos, i = {}, [], 0
    while i < len(a):
        if a[i].startswith("--"):
            o[a[i][2:]] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    return pos, o


def shot(sid):
    s = json.load(open(os.path.join(ROOT, "docs/shots.json")))["shots"]
    s = s if isinstance(s, list) else list(s.values())
    return next(x for x in s if x["id"] == sid)


def run_json(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    ls = [l for l in r.stdout.splitlines() if l.startswith("{")]
    return json.loads(ls[-1]) if ls else {"error": (r.stderr or r.stdout)[-300:]}


def seedance(sid, kf, o):
    sh = shot(sid)
    first = float(o.get("first", sh["lyrics"][0]["start"] if sh.get("lyrics") else sh["in"]))
    out_t = float(o.get("out", sh["out"]))
    st, du = first - 0.5, out_t + 0.3 - (first - 0.5)
    aud = f"media/gen/v4/lipsync/_audio/{sid}_{st:.3f}_{du:.3f}_pad.mp3"
    os.makedirs(os.path.join(ROOT, os.path.dirname(aud)), exist_ok=True)
    subprocess.run([gen.FFMPEG, "-v", "error", "-y", "-ss", f"{st:.3f}", "-t", f"{du:.3f}", "-i", os.path.join(ROOT, STEM), "-af",
                    f"adelay={int(PAD * 1000)}:all=1,apad=whole_dur={2 * PAD + du}", "-ac", "2", "-ar", "44100", "-c:a", "libmp3lame",
                    "-b:a", "192k", os.path.join(ROOT, aud)], check=True)
    t0 = st - PAD
    img = os.path.join("media/gen/refs", f"ls4w_{sid}_1920.jpg")
    gen.ref_image(os.path.join(ROOT, kf), os.path.join(ROOT, img), max_side=1920)
    who = o["who"]
    p = (f"Animate the first frame exactly. The first second is silent: {who} listens, lips closed. Then {who} sings the song of audio 1"
         f" herself, lip-synced to it exactly: her lips, jaw and cheeks move with every syllable at the moment it is heard, the jaw"
         f" dropping on open vowels and the lips closing on m, b and p; silent and at rest where the audio is silent. {o['lang']}."
         f" While singing she acts: {o['act']} Her eyes stay open and on {o['partner']}." + GUARD)
    dur = int(-(-(du + 2 * PAD) // 1))
    ids = []
    for k in range(int(o.get("from", 1)), int(o.get("from", 1)) + int(o.get("takes", 6))):
        tag = f"ls4w_{sid}_{k}"
        sp = os.path.join(ROOT, "media/gen/specs", tag + ".json")
        json.dump({"model": "bytedance/seedance-2.5", "tag": tag, "t0": t0, "shot_in": sh["in"], "shot_out": sh["out"],
                   "notes": f"lip-sync v4 take; keyframe {kf}; audio {aud}; t0={t0}",
                   "input": {"prompt": p, "image": "file:" + img, "reference_audios": ["file:" + aud], "duration": dur,
                             "resolution": o.get("res", "720p"), "aspect_ratio": "16:9", "generate_audio": True, "watermark": False}},
                  open(sp, "w"), ensure_ascii=False, indent=1)
        ids.append(gen.submit(sp, dry_run="dry" in o))
    open(os.path.join(ROOT, "media/gen/specs", f"ls4w_{sid}_jobs.txt"), "a").write("\n".join(i for i in ids if i) + "\n")
    print("submitted", len(ids), "takes; t0", round(t0, 4), "duration", dur, "s")


CALM = (" Her movements are smooth and moderate: no jumping, no bouncing, no fast turns of the head; her face stays clearly"
        " visible and toward the camera the whole time, nothing passes in front of it.")


def window(sid, o):
    sh = shot(sid)
    first = float(o.get("first", sh["lyrics"][0]["start"] if sh.get("lyrics") else sh["in"]))
    out_t = float(o.get("out", sh["out"]))
    t0 = min(first - 0.5, sh["in"])
    return sh, t0, max(3, int(-(-(out_t + 0.3 - t0) // 1)))


def act(sid, kf, o):
    """Pass 1: the PERFORMANCE. Kling v4 from the keyframe, no audio. Frame 0 = song time t0."""
    sh, t0, dur = window(sid, o)
    img = os.path.join("media/gen/refs", f"ls4w_{sid}_1920.jpg")
    gen.ref_image(os.path.join(ROOT, kf), os.path.join(ROOT, img), max_side=1920)
    p = (f"Animate the first frame exactly. {o['who'][0].upper() + o['who'][1:]} sings softly, mouth moving with the words. {o['act']}"
         f" Her eyes stay open and on {o['partner']}." + CALM + GUARD)
    ids = []
    for k in range(int(o.get("from", 1)), int(o.get("from", 1)) + int(o.get("takes", 2))):
        tag = f"ls4w_{sid}_act{k}"
        sp = os.path.join(ROOT, "media/gen/specs", tag + ".json")
        json.dump({"model": "klingai/kling-v4", "tag": tag, "t0": t0, "shot_in": sh["in"], "shot_out": sh["out"], "keyframe": kf,
                   "notes": f"lip-sync v4 pass 1 (acting); keyframe {kf}; t0={t0}",
                   "input": {"prompt": p, "first_frame": "file:" + img, "duration": dur, "aspect_ratio": "16:9",
                             "resolution": o.get("res", "720p")}}, open(sp, "w"), ensure_ascii=False, indent=1)
        ids.append(gen.submit(sp, dry_run="dry" in o))
    open(os.path.join(ROOT, "media/gen/specs", f"ls4w_{sid}_jobs.txt"), "a").write("\n".join(i for i in ids if i) + "\n")
    print("acted takes submitted; t0", round(t0, 4), "duration", dur, "s. Pick one on its sheet, then: lipsync_v4.py anim", sid, "K")


RAP = ("Animate the little girl with the motion of the video. She raps the audio fast in Mandarin Chinese: her lips and jaw articulate"
       " every syllable crisply and clearly, opening visibly on each vowel and closing on b and m, like a confident child rapper. Keep the"
       " painting style and her face exactly as in the image.")


def anim(sid, k, o):
    """Pass 2: the SINGING. pruna/p-video-animate re-renders the whole character from the keyframe with the acted take's motion and
    the song window's audio (it drives the lips from the audio; output audio = input, bit-aligned, so frame 0 = song time t0)."""
    j = next((j for j in gen.read_manifest()["jobs"].values() if j["tag"] == f"ls4w_{sid}_act{k}" and j.get("files")), None)
    if not j:
        raise SystemExit(f"acted take ls4w_{sid}_act{k} not collected yet")
    spec = json.load(open(os.path.join(ROOT, j["spec_file"])))
    t0 = float(spec["t0"])
    src = os.path.join(ROOT, f"media/gen/v4/lipsync/_audio/{sid}_act{k}_src.mp4")
    os.makedirs(os.path.dirname(src), exist_ok=True)
    subprocess.run([gen.FFMPEG, "-v", "error", "-y", "-i", os.path.join(ROOT, j["files"][0]), "-ss", f"{t0:.3f}", "-i", os.path.join(ROOT, STEM),
                    "-map", "0:v", "-map", "1:a", "-shortest", "-vf", "fps=24,scale=854:480", "-c:v", "libx264", "-crf", "30", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "160k", src], check=True)
    img = os.path.join("media/gen/refs", f"ls4w_{sid}_1280.jpg")
    gen.ref_image(os.path.join(ROOT, spec["keyframe"]), os.path.join(ROOT, img), max_side=1280, quality=85)
    ids = []
    for s_ in range(1, int(o.get("seeds", 2)) + 1):
        tag = f"ls4w_{sid}_a{k}s{s_}"
        sp = os.path.join(ROOT, "media/gen/specs", tag + ".json")
        json.dump({"model": "pruna/p-video-animate", "tag": tag, "t0": t0, "shot_in": spec["shot_in"], "shot_out": spec["shot_out"],
                   "notes": f"lip-sync v4 pass 2 (singing) on act{k}; t0={t0}",
                   "input": {"video": "file:" + os.path.relpath(src, ROOT), "image": "file:" + img, "resolution": o.get("res", "720p"),
                             "save_audio": True, "ignore_audio": False, "target_fps": "24", "turbo": False, "disable_safety_checker": False,
                             "seed": 1000 + s_, "instruction_prompt": o.get("prompt", RAP if o.get("rap") else "Animate the singer with the motion of the video, and make"
                             " her lips sing the audio exactly. Keep the painting style and her face exactly as in the image.")}},
                  open(sp, "w"), ensure_ascii=False, indent=1)
        ids.append(gen.submit(sp, dry_run="dry" in o))
    open(os.path.join(ROOT, "media/gen/specs", f"ls4w_{sid}_jobs.txt"), "a").write("\n".join(i for i in ids if i) + "\n")
    print("singing passes submitted; frame 0 = song", round(t0, 4))


def takes(sid):
    man = gen.read_manifest()["jobs"]
    for jid, j in sorted(man.items(), key=lambda kv: kv[1]["tag"]):
        if j["tag"].startswith(f"ls4w_{sid}_") and j.get("state") == "done" and j.get("files") and "act" not in j["tag"]:
            yield j


def measure(sid, o):
    pick = ["--pick", o["pick"]] if o.get("pick") else []
    rows = []
    for j in takes(sid):
        name = j["tag"]; take = os.path.join(ROOT, j["files"][0])
        spec = json.load(open(os.path.join(ROOT, j["spec_file"])))
        t0 = float(spec["t0"])
        run_json([PY, os.path.join(REV, "lipsync_v4.py"), "strip", take, "--t0", str(t0), "--name", name] + pick)
        if j["model"] == "klingai/kling-v4":
            continue                      # acted takes are pass 1: judged on their sheet, not measured
        if j["model"] == "pruna/p-video-animate":
            lg = {"shift_f": 0, "confidence": "by construction (audio bit-aligned)", "lag_ms": 0}
        else:
            lg = run_json([PY, os.path.join(REV, "ls4_lag.py"), name, "--t0", str(t0)])
        s = lg.get("shift_f", 0)
        subprocess.run([PY, os.path.join(REV, "lipsync_gate.py"), take, "--t0", str(t0), "--shift", str(s), "--name", name, "--out",
                        os.path.join(OUTD, "gate"), "--scan", "18"] + pick, capture_output=True)
        gr = json.load(open(os.path.join(OUTD, "gate", f"{name}_gate.json")))
        fs = run_json([PY, os.path.join(REV, "lipsync_v4.py"), "strip", take, "--t0", str(t0), "--shift", str(s), "--name", name] + pick)
        sheet = os.path.join(OUTD, "sheets", name + ".jpg")
        os.makedirs(os.path.dirname(sheet), exist_ok=True)
        subprocess.run([gen.FFMPEG, "-v", "error", "-y", "-i", take, "-vf", "fps=3,scale=320:-2,tile=6x3", "-frames:v", "1", sheet])
        place = t0 + s / 24.0
        n = gr.get("frames", 0)
        covers = place <= spec.get("shot_in", place) + 1e-3 and place + n / 24.0 >= spec.get("shot_out", 0) - 1e-3
        rows.append(dict(take=name, file=j["files"][0], place_frame0_at=round(place, 4), lag_ms=lg.get("lag_ms"), lag_conf=lg.get("confidence"),
                         covers_shot=covers, closed=gr.get("closed"), open=gr.get("open"), drift_f=gr.get("drift_f"),
                         face_px=fs.get("face_px_in_cut"), jaw_r=fs.get("jaw_r"), gate=gr.get("verdict", "")[:9],
                         strip=fs.get("strip"), sheet=os.path.relpath(sheet, ROOT)))
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
    if rows:
        p = os.path.join(OUTD, f"{sid}_takes.tsv")
        open(p, "w").write("\t".join(rows[0]) + "\n" + "\n".join("\t".join(str(v) for v in r.values()) for r in rows) + "\n")
        print("table", os.path.relpath(p, ROOT))


def eye(sid, n, verdict):
    p = os.path.join(OUTD, f"{sid}_takes.tsv")
    rows = [l.split("\t") for l in open(p).read().splitlines()]
    hdr, body = rows[0], rows[1:]
    r = next(b for b in body if b[0] in (f"ls4w_{sid}_{n}", n))
    rec = dict(zip(hdr, r)); rec["eye"] = verdict
    pk = os.path.join(OUTD, f"{sid}_pick.json")
    allp = json.load(open(pk)) if os.path.exists(pk) else []
    allp.append(rec)
    json.dump(allp, open(pk, "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "docs/logs/LOG_v4_lipsync.md"), "a") as f:
        f.write(f"\n| {rec['take']} | {rec['file']} | frame0 at {rec['place_frame0_at']} | covers {rec['covers_shot']} | "
                f"closed {rec['closed']} open {rec['open']} drift {rec['drift_f']} | {verdict} | {rec['strip']} |")
    print("recorded", pk)


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]; pos, o = opts(sys.argv[2:])
    if cmd == "act":
        act(pos[0], pos[1], o)
    elif cmd == "anim":
        anim(pos[0], pos[1], o)
    elif cmd == "seedance":
        seedance(pos[0], pos[1], o)
    elif cmd == "wait":
        ids = open(os.path.join(ROOT, "media/gen/specs", f"ls4w_{pos[0]}_jobs.txt")).read().split()
        gen.wait(ids, timeout=3600)
    elif cmd == "measure":
        measure(pos[0], o)
    elif cmd == "eye":
        eye(pos[0], pos[1], pos[2])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

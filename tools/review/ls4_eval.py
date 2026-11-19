#!/usr/bin/env python3
"""Evaluate every finished v4 lip-sync take: audio placement, gate at that placement, face strip. One row per take.

    $PY tools/review/ls4_eval.py [TAG_SUBSTRING ...]      -> work/review/lipsync_v4/ls4_table.tsv (+ per-take json/strips)

Placement rule (LIPSYNC_V4): if the take carries the song (audiolag trust), frame 0 goes at audiolag's place_frame0_at
(rounded to the frame); otherwise the gate chooses the shift. The gate (tools/review/lipsync_gate.py) then measures at that
placement; the face strip is drawn at the same placement. Gate verdicts here are numbers only: the strip decides.
"""
import glob, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable
OUT = os.path.join(ROOT, "work/review/lipsync_v4")
GATE_OUT = os.path.join(OUT, "gate")
PICK = {"C3": "560,180"}   # Mama's nose, 720p frame 0 (two faces in frame)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith("{")]
    return json.loads(lines[-1]) if lines else {"error": (r.stderr or r.stdout)[-300:]}


def main():
    subs = sys.argv[1:]
    man = json.load(open(os.path.join(ROOT, "media/gen/manifest.json")))["jobs"]
    rows = []
    os.makedirs(GATE_OUT, exist_ok=True)
    for jid, j in sorted(man.items()):
        if not j["tag"].startswith("ls4_") or j.get("state") != "done" or not j.get("files"):
            continue
        if subs and not any(s in j["tag"] for s in subs):
            continue
        take = os.path.join(ROOT, j["files"][0])
        spec = json.load(open(os.path.join(ROOT, j["spec_file"])))
        t0 = float(spec["t0"]); line = j["tag"].split("_")[1]; name = j["tag"]
        # conform to 24 fps if needed
        src = take
        al = run([PY, os.path.join(HERE, "lipsync_v4.py"), "audiolag", src, "--t0", str(t0), "--name", name])
        # Seedance passes the reference audio through at offset 0 whatever its mouth does: the face decides (ls4_lag.py)
        run([PY, os.path.join(HERE, "lipsync_v4.py"), "strip", src, "--t0", str(t0), "--name", name] + (["--pick", PICK[line]] if line in PICK else []))
        lg = run([PY, os.path.join(HERE, "ls4_lag.py"), name, "--t0", str(t0)]) if j["model"] != "pruna/p-video-animate" else \
            {"shift_f": 0, "confidence": "construction"}
        shift = lg.get("shift_f")
        if os.environ.get("LS4_SHIFT", "").startswith(name + "="):
            shift = int(os.environ["LS4_SHIFT"].split("=")[1])
        pick = ["--pick", PICK[line]] if line in PICK else []
        g = [PY, os.path.join(HERE, "lipsync_gate.py"), src, "--t0", str(t0), "--name", name, "--out", GATE_OUT, "--scan", "18"] + pick + \
            (["--shift", str(shift)] if shift is not None else [])
        subprocess.run(g, capture_output=True, text=True)
        gp = os.path.join(GATE_OUT, f"{name}_gate.json")
        gr = json.load(open(gp)) if os.path.exists(gp) else {}
        sh = shift if shift is not None else gr.get("shift_f", 0)
        fs = run([PY, os.path.join(HERE, "lipsync_v4.py"), "strip", src, "--t0", str(t0), "--shift", str(sh), "--name", name] + pick)
        rows.append(dict(tag=name, model=j["model"], line=line, t0=t0, lag_conf=lg.get("confidence"), coarse_r=lg.get("coarse_r"), has_audio=al.get("has_audio"), audio_lag_ms=al.get("audio_lag_ms"),
                         audio_r=al.get("r"), audio_drift_ms=al.get("drift_ms"), audio_trust=al.get("trust"), shift_f=sh,
                         gate_shift_from=gr.get("shift_from"), env_lag_ms=gr.get("env_lag_ms"), env_r=gr.get("r"), viseme_shift=gr.get("viseme_shift_f"),
                         closed=gr.get("closed"), open=gr.get("open"), drift_f=gr.get("drift_f"), face=gr.get("face_found_pct"),
                         verdict=gr.get("verdict"), reason=(gr.get("reason") or "")[:120], jaw_r=fs.get("jaw_r"), jaw_range=fs.get("jaw_range"),
                         gap_range=fs.get("gap_range"), face_px=fs.get("face_px_in_cut"), strip=fs.get("strip") or fs.get("error")))
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
    p = os.path.join(OUT, "ls4_table.tsv")
    old = {}
    if os.path.exists(p):
        hdr, *body = open(p).read().splitlines()
        for b in body:
            old[b.split("\t")[0]] = b
    if rows:
        keys = list(rows[0].keys())
        for r in rows:
            old[r["tag"]] = "\t".join(str(r[k]) for k in keys)
        open(p, "w").write("\t".join(keys) + "\n" + "\n".join(old[k] for k in sorted(old)) + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Splice split shots: media/comp/<part>.mp4 ... -> media/comp/spliced/<ID>.mp4, and point docs/picks.json at them.

Rule: parts are concatenated in order. If the total exceeds the shot's frame count the END of the FIRST part is trimmed;
if it falls short the last frame is held (reported). Missing parts: the shot is skipped (reported).
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLICES = {
    "C5": ["C5a", "C5b"], "D2": ["D2", "D2d"], "F3": ["F3a", "F3b"], "F4": ["F4a", "F4b"],
    "F6": ["F6a", "F6b"], "I3": ["I3a", "I3b"], "K2": ["K2a", "K2b"],
}

def nframes(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return int(out.strip().split(",")[0])

def main():
    shots = {s["id"]: s for s in json.load(open(ROOT / "docs/shots.json"))["shots"]}
    comp = ROOT / "media/comp"; out_dir = comp / "spliced"; out_dir.mkdir(exist_ok=True)
    picks_p = ROOT / "docs/picks.json"
    picks = json.load(open(picks_p)) if picks_p.exists() else {}
    for sid, parts in SPLICES.items():
        need = shots[sid]["frames"]
        paths = [comp / f"{p}.mp4" for p in parts]
        miss = [p.name for p in paths if not p.exists()]
        if miss:
            print(f"{sid}: skipped, missing {miss}"); continue
        counts = [nframes(p) for p in paths]
        total = sum(counts)
        take = counts[:]
        if total > need:
            take[0] = max(1, counts[0] - (total - need))
        filt, labels = [], []
        for i, n in enumerate(take):
            filt.append(f"[{i}:v]trim=end_frame={n},setpts=N/(24*TB),scale=960:540,setsar=1[v{i}]")
            labels.append(f"[v{i}]")
        pad = need - sum(take)
        cat = "".join(labels) + f"concat=n={len(take)}:v=1:a=0,setpts=N/(24*TB)[c]"
        tail = f";[c]tpad=stop_mode=clone:stop={max(pad,0)+3}[o]"  # +3 guard frames; -frames:v trims to need
        dst = out_dir / f"{sid}.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for p in paths: cmd += ["-i", str(p)]
        cmd += ["-filter_complex", ";".join(filt) + ";" + cat + tail, "-map", "[o]", "-frames:v", str(need), "-r", "24",
                "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(dst)]
        subprocess.run(cmd, check=True)
        got = nframes(dst)
        picks[sid] = {"src": str(dst.relative_to(ROOT)), "in": 0.0, "rate": 1.0}
        print(f"{sid}: parts {counts} -> take {take} pad {max(pad,0)} = {got}/{need}" + ("  HELD" if pad > 0 else ""))
    json.dump(picks, open(picks_p, "w"), indent=1)

if __name__ == "__main__":
    sys.exit(main())

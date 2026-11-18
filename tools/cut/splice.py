#!/usr/bin/env python3
"""Splice split shots: media/comp/<part>.mp4 ... -> media/comp/spliced/<ID>.mp4, and point docs/picks.json at them.

Rule: parts are concatenated in order. If the total exceeds the shot's frame count the END of the FIRST part is trimmed;
if it falls short the last frame is held (reported). Missing parts: the shot is skipped (reported).

v3 table (preview_v3; sources: docs/logs/LOG_v3_{attic,bedcar,book,stage}.md, summary in docs/QA_PREVIEW_V3.md):
  C5 = C5a + C5b            57 + 58                      cut on song frame 1311
  D2 = D2 + D2d             65 (of 80: tail trimmed) + 15, cut on 1531
  F3 = F3a + F3b            29 + 12                      cut on 2694
  F4 = F4a + F4b            38 + 45                      cut on 2744
  F6 = F6a + F6b            50 (of 63: tail trimmed) + 33, cut on 2882 (120.083; BED+CAR round 2)
  I2 = pages/I2_full        66   BOOK's page comp; media/comp/I2.mp4 is still the v2 hand-shadow shot and is NOT used
  I3 = I3a + I3b            40 + 57                      cut on 4431
  K2 = K2a + K2b            38 + 40                      cut on 5091
  L3 = L2b + L3             26 + 34   the shots.json slot "L3" (5660-5720) holds ATTIC's L2b (5660-5685, the 1988 half of
                            the blanket match cut, which is ON 235.833 = frame 5660) and then ATTIC's L3.mp4 (5686-5719).
                            The slot "L2" (5597-5660) is BED+CAR's L2.mp4 alone (63 f, last frame 5659).
K1 is BED+CAR's K1.mp4 alone (it renders BOOK's shots/K1page.py for 4973-5053; pages/K1_full.mp4 is the same frames).
EXPECT pins the frames taken from each part; a part that changes length stops the build instead of moving a cut.
"""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLICES = {
    "C5": ["C5a", "C5b"], "D2": ["D2", "D2d"], "F3": ["F3a", "F3b"], "F4": ["F4a", "F4b"],
    "F6": ["F6a", "F6b"], "I2": ["pages/I2_full"], "I3": ["I3a", "I3b"], "K2": ["K2a", "K2b"],
    "L3": ["L2b", "L3"],
}
EXPECT = {"C5": [57, 58], "D2": [65, 15], "F3": [29, 12], "F4": [38, 45], "F6": [50, 33], "I2": [66],
          "I3": [40, 57], "K2": [38, 40], "L3": [26, 34]}

def nframes(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return int(out.strip().split(",")[0])

def main():
    shots = {s["id"]: s for s in json.load(open(ROOT / "docs/shots.json"))["shots"]}
    comp = ROOT / "media/comp"; out_dir = comp / "spliced"; out_dir.mkdir(exist_ok=True)
    picks_p = ROOT / "docs/picks.json"
    picks = json.load(open(picks_p)) if picks_p.exists() else {}
    report, bad = {}, []
    for sid, parts in SPLICES.items():
        need = shots[sid]["frames"]
        paths = [comp / f"{p}.mp4" for p in parts]
        miss = [p.name for p in paths if not p.exists()]
        if miss:
            print(f"{sid}: skipped, missing {miss}"); bad.append(sid); continue
        counts = [nframes(p) for p in paths]
        total = sum(counts)
        take = counts[:]
        if total > need:
            take[0] = max(1, counts[0] - (total - need))
        pad = need - sum(take)
        if take != EXPECT.get(sid, take) or pad > 0:
            print(f"{sid}: parts {counts} -> take {take} pad {max(pad,0)}: NOT the v3 table {EXPECT.get(sid)}"); bad.append(sid)
        filt, labels = [], []
        for i, n in enumerate(take):
            filt.append(f"[{i}:v]trim=end_frame={n},setpts=N/(24*TB),scale=960:540,setsar=1[v{i}]")
            labels.append(f"[v{i}]")
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
        f0 = shots[sid]["in_frame"]; cuts = [f0 + sum(take[:i]) for i in range(1, len(take))]
        report[sid] = {"parts": parts, "have": counts, "take": take, "pad": max(pad, 0), "frames": got, "cuts": cuts,
                       "mtimes": [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime)) for p in paths]}
        print(f"{sid}: parts {counts} -> take {take} pad {max(pad,0)} = {got}/{need}  cut frames {cuts}" + ("  HELD" if pad > 0 else ""))
        if got != need: bad.append(sid)
    json.dump(picks, open(picks_p, "w"), indent=1)
    (ROOT / "work/cut").mkdir(parents=True, exist_ok=True)
    json.dump(report, open(ROOT / "work/cut/splice_report.json", "w"), indent=1)
    if bad:
        print("SPLICE PROBLEMS:", sorted(set(bad))); return 1

if __name__ == "__main__":
    sys.exit(main())

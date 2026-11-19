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

v4 table (preview_v4; sources: docs/logs/LOG_v4_*.md DONE/CHECKPOINT blocks; REVISION_V4 §12). Output media/comp/spliced_v4/,
picks docs/picks_v4.json (v3's docs/picks.json and media/comp/spliced/ are left as they were), report
work/cut/splice_report_v4.json. Differences from v3:
  F4 = F4                   83   SWARM's single comp (s0-82 of F4F5F6a.mp4); no F4a/F4b. F5 = F5.mp4 (43) unspliced.
  F6 = F6a + F6b            50 + 33, cut on 2882: F6a = swarm s126-175; F6b is now the MIRROR shot (BED+CAR)
  G5 + G6 = G5.mp4          78 f over both slots (song frames 3515-3592; REVISION_V4 §12): the G5 slot takes frames 0-67, the
                            G6 slot frames 68-77 of the same file (a pick with an in-point: no re-encode, no shots.json edit).
                            If G5.mp4 is not 78 f, v3's arrangement stays (G5 68 f + G6 blank) and the report says so.
  B2's internal cut (lap -> over the shoulder) moved to 24.6 s (frame 591): not a splice, a lyric PART.
  Unchanged: C5 D2 F3 I2 I3 K2 L3 (same parts, same counts; D2 still takes the first 65 of 80).
"""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'v4'
SPLICES = {
    "C5": ["C5a", "C5b"], "D2": ["D2", "D2d"], "F3": ["F3a", "F3b"],
    "F6": ["F6a", "F6b"], "I2": ["pages/I2_full"], "I3": ["I3a", "I3b"], "K2": ["K2a", "K2b"],
    "L3": ["L2b", "L3"],
}
EXPECT = {"C5": [57, 58], "D2": [65, 15], "F3": [29, 12], "F6": [50, 33], "I2": [66],
          "I3": [40, 57], "K2": [38, 40], "L3": [26, 34]}
# one source over two slots: slot -> (file, first frame used). G5's file is 78 f; G5 slot = 0..67, G6 slot = 68..77.
SPAN = {"G5": ("G5", 0), "G6": ("G5", 68)}
SPAN_NEED = {"G5": 78}               # the file must have exactly this many frames, otherwise the v3 arrangement stays
OUT_DIR = "media/comp/spliced_v4"
PICKS = "docs/picks_v4.json"
REPORT = "work/cut/splice_report_v4.json"

def nframes(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return int(out.strip().split(",")[0])

def main():
    shots = {s["id"]: s for s in json.load(open(ROOT / "docs/shots.json"))["shots"]}
    comp = ROOT / "media/comp"; out_dir = ROOT / OUT_DIR; out_dir.mkdir(exist_ok=True)
    picks_p = ROOT / PICKS
    picks = {}                                      # rebuilt from the table every run (no stale entries)
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
            print(f"{sid}: parts {counts} -> take {take} pad {max(pad,0)}: NOT the {VERSION} table {EXPECT.get(sid)}"); bad.append(sid)
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
    for sid, (src, first) in SPAN.items():
        p = comp / f"{src}.mp4"
        n = nframes(p) if p.exists() else 0
        need = SPAN_NEED.get(src)
        if need is not None and n != need:
            print(f"{sid}: {src}.mp4 has {n} f, not {need}: v3 arrangement kept for this slot  ** MARKER: G5/G6 NOT v4 **")
            report[sid] = {"span": src, "have": n, "kept_v3": True}
            continue
        f0 = shots[sid]["in_frame"]
        picks[sid] = {"src": str(p.relative_to(ROOT)), "in": first / 24.0, "rate": 1.0,
                      "label": src}
        report[sid] = {"span": src, "have": n, "first": first, "frames": shots[sid]["frames"],
                       "song_frames": [f0, f0 + shots[sid]["frames"] - 1],
                       "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))}
        print(f"{sid}: {src}.mp4 frames {first}-{first + shots[sid]['frames'] - 1} (of {n}) on song frames "
              f"{f0}-{f0 + shots[sid]['frames'] - 1}")
    json.dump(picks, open(picks_p, "w"), indent=1)
    (ROOT / "work/cut").mkdir(parents=True, exist_ok=True)
    json.dump(report, open(ROOT / REPORT, "w"), indent=1)
    if bad:
        print("SPLICE PROBLEMS:", sorted(set(bad))); return 1

if __name__ == "__main__":
    sys.exit(main())

"""Side-by-side bake-off grid per shot: every model's clip tiled 3 across at 640x360, labelled, in sync
(24 fps, short clips hold their last frame), played twice, H.264 -> work/review/bakeoff/<SHOT>_grid.mp4

usage: .venv/bin/python tools/review/bakeoff_grid.py [SHOT ...]
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bakeoff_sheets import ROOT, NAMES, clips  # noqa: E402

OUT = os.path.join(ROOT, "work/review/bakeoff")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TW, TH, COLS = 640, 360, 3


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
                       capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def grid(shot):
    cl = clips(shot)
    items = list(cl.items())
    longest = max(dur(p) for _, p in items)
    n = len(items)
    rows = (n + COLS - 1) // COLS
    inputs, f = [], []
    for i, (m, p) in enumerate(items):
        inputs += ["-i", p]
        label = NAMES[m].replace(":", r"\:")
        f.append(f"[{i}:v]fps=24,scale={TW}:{TH}:force_original_aspect_ratio=decrease,"
                 f"pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,"
                 f"tpad=stop_mode=clone:stop_duration={longest:.3f},trim=duration={longest:.3f},setpts=PTS-STARTPTS,"
                 f"drawtext=fontfile={FONT}:text='{label}':x=8:y=8:fontsize=22:fontcolor=0xFFE678:box=1:boxcolor=black@0.7:boxborderw=6,"
                 f"drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=w-tw-8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=4"
                 f"[v{i}]")
    # fill empty cells
    k = n
    while k < rows * COLS:
        f.append(f"color=c=black:s={TW}x{TH}:r=24:d={longest:.3f}[v{k}]")
        k += 1
    layout = "|".join(f"{(j % COLS) * TW}_{(j // COLS) * TH}" for j in range(rows * COLS))
    f.append("".join(f"[v{j}]" for j in range(rows * COLS)) + f"xstack=inputs={rows * COLS}:layout={layout}[g]")
    f.append("[g]split[a][b];[a][b]concat=n=2:v=1:a=0,format=yuv420p[out]")
    out = os.path.join(OUT, f"{shot}_grid.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f), "-map", "[out]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high", "-movflags", "+faststart", "-an", out]
    subprocess.run(cmd, check=True)
    print(out, f"{n} clips, {longest:.2f}s x2")


if __name__ == "__main__":
    for s in sys.argv[1:] or ["A1", "C2", "C7", "C9", "F1"]:
        grid(s)

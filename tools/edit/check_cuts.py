#!/usr/bin/env python3
"""Check docs/shots.json against analysis/timing.json. Exit 1 on any failure.

Fails if: a cut is more than one frame from its anchor (the anchor is re-resolved from timing.json, so a stale or
hand-edited shots.json is caught), in_frame is not the anchor's frame (ceil(t*24)), shots overlap or leave gaps, the
first shot does not start at frame 0, the last does not end at the total, or the totals are off.
Warns (no failure) on: shots under 8 frames, anchors that are section boundaries or have nothing to cut on within a
frame (soft), typed times > 1 frame from their anchor (see docs/shots_report.md).
Prints the cut list with durations and the shots-per-section pacing.

    .venv/bin/python tools/edit/check_cuts.py [--shots docs/shots.json] [--quiet]
"""
import argparse
import sys
from collections import OrderedDict

from common import (FPS, ONE_FRAME, SHOTS, AnchorError, frame_of, load_json, load_timing, nearest_points,
                    resolve_anchor, sync_points, tc)

MIN_FRAMES = 8


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--shots', default=str(SHOTS))
    ap.add_argument('--quiet', action='store_true', help='only failures and warnings')
    args = ap.parse_args()
    data = load_json(args.shots)
    shots, meta = data['shots'], data['meta']
    timing = load_timing()
    pts = sync_points(timing)
    total = meta['total_frames']
    fails, warns = [], []

    # totals: the audio length and the frame count must agree with the timing map's file
    dur = timing['source']['duration']
    if abs(dur - meta['end_t']) > 1e-6:
        fails.append(('ALL', f'end_t {meta["end_t"]} != audio duration {dur}'))
    if total != int(dur * FPS + 1e-6):
        fails.append(('ALL', f'total_frames {total} != whole frames in {dur} s ({int(dur * FPS + 1e-6)})'))

    ids = set()
    for i, s in enumerate(shots):
        sid = s['id']
        if sid in ids:
            fails.append((sid, 'duplicate id'))
        ids.add(sid)
        # anchor: re-resolve and compare
        try:
            a = resolve_anchor(s['anchor'], timing)
        except AnchorError as e:
            fails.append((sid, f'anchor does not resolve: {e}'))
            continue
        if abs(a['t'] - s['in']) > 1e-3:
            fails.append((sid, f'in {s["in"]:.3f} but anchor {a["label"]} now resolves to {a["t"]:.3f} (rebuild shots.json)'))
        cut_t = s['in_frame'] / FPS
        off = cut_t - a['t']
        if abs(off) > ONE_FRAME + 1e-9:
            fails.append((sid, f'cut frame {s["in_frame"]} ({cut_t:.3f} s) is {off * 1000:+.0f} ms from {a["label"]} '
                               f'{a["t"]:.3f} (> 1 frame)'))
        elif s['in_frame'] != frame_of(a['t']):
            fails.append((sid, f'in_frame {s["in_frame"]} != ceil(anchor*24) = {frame_of(a["t"])}'))
        # contiguity
        if i == 0 and s['in_frame'] != 0:
            fails.append((sid, f'first shot starts at frame {s["in_frame"]}, not 0'))
        if i > 0 and s['in_frame'] != shots[i - 1]['out_frame']:
            kind = 'overlap' if s['in_frame'] < shots[i - 1]['out_frame'] else 'gap'
            fails.append((sid, f'{kind}: starts at {s["in_frame"]}, previous shot ends at {shots[i - 1]["out_frame"]}'))
        n = s['out_frame'] - s['in_frame']
        if n <= 0:
            fails.append((sid, f'non-positive length {n}'))
        elif n < MIN_FRAMES:
            warns.append((sid, f'only {n} frames (< {MIN_FRAMES})'))
        if s.get('frames') is not None and s['frames'] != n:
            fails.append((sid, f'frames field {s["frames"]} != out-in {n}'))
        if a.get('soft', '').startswith('section'):
            warns.append((sid, f'anchor is a {a["soft"]}'))
        if not nearest_points(a['t'], pts, ONE_FRAME):
            warns.append((sid, f'nothing (beat/word/event) within a frame of {a["t"]:.3f}'))
        if s.get('typed_in') is not None and abs(s['typed_in'] - a['t']) > ONE_FRAME + 1e-9:
            warns.append((sid, f'typed {s["typed_in"]:.2f} is {(s["typed_in"] - a["t"]) * 1000:+.0f} ms from its anchor '
                               f'(cut follows the anchor)'))
    if shots and shots[-1]['out_frame'] != total:
        fails.append((shots[-1]['id'], f'last shot ends at {shots[-1]["out_frame"]}, total is {total}'))
    if sum(s['out_frame'] - s['in_frame'] for s in shots) != total:
        fails.append(('ALL', 'shot lengths do not sum to the total'))
    # letterbox flag: true exactly for shots before the opening frame
    lbf = meta['letterbox_until']['frame']
    for s in shots:
        if s['letterbox'] != (s['in_frame'] < lbf):
            fails.append((s['id'], f'letterbox flag {s["letterbox"]} wrong for in_frame {s["in_frame"]} (opens at {lbf})'))
    if not any(s['in_frame'] == lbf for s in shots):
        warns.append(('ALL', f'the letterbox opens at frame {lbf}, which is not a cut'))

    if not args.quiet:
        print(f'{"id":5s} {"in":>8s} {"tc":>12s} {"frame":>6s} {"frames":>6s} {"secs":>6s}  anchor')
        for s in shots:
            n = s['out_frame'] - s['in_frame']
            print(f'{s["id"]:5s} {s["in"]:8.3f} {tc(s["in_frame"]):>12s} {s["in_frame"]:6d} {n:6d} {n / FPS:6.2f}  '
                  f'{s["anchor"]["label"]}{"  [LB]" if s["letterbox"] else ""}')
        print()
        sec = OrderedDict()
        for s in shots:
            sec.setdefault(s['section'], []).append(s)
        print(f'{"sec":4s} {"shots":>5s} {"secs":>7s} {"avg s":>6s} {"min f":>6s} {"max f":>6s}  title')
        for k, ss in sec.items():
            fr = [x['out_frame'] - x['in_frame'] for x in ss]
            print(f'{k:4s} {len(ss):5d} {sum(fr) / FPS:7.2f} {sum(fr) / len(fr) / FPS:6.2f} {min(fr):6d} {max(fr):6d}  '
                  f'{ss[0]["section_title"]}')
        allf = [s['out_frame'] - s['in_frame'] for s in shots]
        print(f'ALL  {len(shots):5d} {sum(allf) / FPS:7.2f} {sum(allf) / len(allf) / FPS:6.2f} {min(allf):6d} '
              f'{max(allf):6d}  total {sum(allf)} frames')
        print()
    for sid, m in warns:
        print(f'WARN {sid:5s} {m}')
    if fails:
        print()
        print(f'{"FAIL":5s} {"shot":5s} reason')
        for sid, m in fails:
            print(f'FAIL  {sid:5s} {m}')
        print(f'\n{len(fails)} failure(s)')
        sys.exit(1)
    print(f'OK: {len(shots)} shots, {total} frames, every cut within one frame of its anchor ({len(warns)} warnings)')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Labelled contact sheets of a cut made by assemble.py.

  shots: first / middle / last frame of every shot, labelled with id, frame and timecode
  every: one frame every 0.5 s (--step), labelled with time and shot id

    .venv/bin/python tools/edit/contact.py --name animatic_v0              # both sheets of the full cut
    .venv/bin/python tools/edit/contact.py --name animatic_v0 --range C1:C5
    .venv/bin/python tools/edit/contact.py --video some.mp4 --start-frame 0 --sheet every

Frames are decoded by index (not by seeking) and converted as BT.709 limited range, so what you see is what a player
shows. Output: work/edit/<name>/contact_shots_pN.jpg, contact_every_pN.jpg (pages of --rows rows).
"""
import argparse
import bisect
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

from common import FPS, ROOT, SHOTS, load_json, select_range, tc
from typeset import font

TW, TH = 320, 180       # thumbnail size
GAP, LAB = 6, 24


def decode_frames(path, wanted, tw=TW, th=TH):
    """{local frame index: PIL thumbnail} for the wanted indices, decoding sequentially."""
    from av.video.reformatter import VideoReformatter
    ref = VideoReformatter()
    out, wanted = {}, set(wanted)
    with av.open(str(path)) as c:
        s = c.streams.video[0]
        s.thread_type = 'AUTO'
        for i, fr in enumerate(c.decode(s)):
            if i in wanted:
                rgb = ref.reformat(fr, width=tw, height=th, format='rgb24', src_colorspace='ITU709',
                                   src_color_range='MPEG', dst_color_range='JPEG', interpolation='AREA')
                out[i] = Image.fromarray(rgb.to_ndarray(), 'RGB')
            if len(out) == len(wanted):
                break
    return out


def sheet(cells, cols, rows_per_page, out_base, title):
    """cells: [(thumb or None, label, group_break)]; writes pages, returns paths."""
    f = font('Mono', 15)
    ft = font('OpenSans', 22, 600)
    paths = []
    per_page = cols * rows_per_page
    for p0 in range(0, len(cells), per_page):
        page = cells[p0:p0 + per_page]
        nrows = (len(page) + cols - 1) // cols
        W = cols * (TW + GAP) + GAP
        H = 44 + nrows * (TH + LAB + GAP) + GAP
        img = Image.new('RGB', (W, H), (18, 18, 18))
        d = ImageDraw.Draw(img)
        d.text((GAP, 30), f'{title}   page {p0 // per_page + 1}', font=ft, fill=(230, 230, 230), anchor='ls')
        for j, (th, lab, hl) in enumerate(page):
            x = GAP + (j % cols) * (TW + GAP)
            y = 44 + (j // cols) * (TH + LAB + GAP)
            if th is not None:
                img.paste(th, (x, y))
            else:
                d.rectangle([x, y, x + TW, y + TH], outline=(200, 60, 60))
            d.text((x + 2, y + TH + 17), lab, font=f, fill=(255, 220, 120) if hl else (200, 200, 200), anchor='ls')
        pth = Path(f'{out_base}_p{p0 // per_page + 1}.jpg')
        img.save(pth, quality=88)
        paths.append(pth)
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', help='work/edit/<name>/chaosmonkey_<name>.mp4')
    ap.add_argument('--range', help='the --range the file was built with (A1:C4)')
    ap.add_argument('--video', help='explicit file instead of --name')
    ap.add_argument('--start-frame', type=int, help='global frame of the file\'s first frame (with --video)')
    ap.add_argument('--sheet', choices=['shots', 'every', 'both'], default='both')
    ap.add_argument('--step', type=float, default=0.5, help='seconds between frames on the "every" sheet')
    ap.add_argument('--rows', type=int, default=12, help='rows per page')
    ap.add_argument('--out', help='output folder (default: next to the video)')
    args = ap.parse_args()

    shots = load_json(SHOTS)['shots']
    sel = select_range(shots, args.range) if args.range else shots
    if args.video:
        video = Path(args.video)
        start = args.start_frame if args.start_frame is not None else sel[0]['in_frame']
    else:
        root = ROOT / 'work' / 'edit' / args.name
        video = root / (f'chaosmonkey_{args.name}.mp4' if not args.range else
                        f'chaosmonkey_{args.name}_{sel[0]["id"]}-{sel[-1]["id"]}.mp4')
        start = sel[0]['in_frame']
    outdir = Path(args.out) if args.out else video.parent
    end = sel[-1]['out_frame']
    starts = [s['in_frame'] for s in shots]

    def shot_at(g):
        return shots[bisect.bisect_right(starts, g) - 1]

    want = {}
    if args.sheet in ('shots', 'both'):
        for s in sel:
            a, b = s['in_frame'], s['out_frame'] - 1
            for g in (a, (a + b) // 2, b):
                want[g - start] = None
    if args.sheet in ('every', 'both'):
        k = 0
        while True:
            g = int(round(k * args.step * FPS))
            if g >= end:
                break
            if g >= start:
                want[g - start] = None
            k += 1
    thumbs = decode_frames(video, want.keys())

    made = []
    if args.sheet in ('shots', 'both'):
        cells = []
        for s in sel:
            a, b = s['in_frame'], s['out_frame'] - 1
            for j, g in enumerate((a, (a + b) // 2, b)):
                lab = f'{s["id"]} {"FML"[j]} f{g} {tc(g)[3:]}'
                cells.append((thumbs.get(g - start), lab, j == 0))
        made += sheet(cells, 9, args.rows, outdir / 'contact_shots',
                      f'{video.name}: first / middle / last frame of each shot (F/M/L), f = global frame')
    if args.sheet in ('every', 'both'):
        cells = []
        k = 0
        while True:
            g = int(round(k * args.step * FPS))
            if g >= end:
                break
            if g >= start:
                s = shot_at(g)
                cells.append((thumbs.get(g - start), f'{g / FPS:6.2f}s {s["id"]} f{g}', g == s['in_frame']))
            k += 1
        made += sheet(cells, 9, args.rows, outdir / 'contact_every',
                      f'{video.name}: one frame every {args.step:g} s (highlighted = first frame of a shot)')
    missing = [g for g in want if g not in thumbs]
    for p in made:
        print(p.relative_to(ROOT) if str(p).startswith(str(ROOT)) else p)
    if missing:
        print(f'WARNING: {len(missing)} wanted frames not in the file (first: {sorted(missing)[:5]})')


if __name__ == '__main__':
    main()

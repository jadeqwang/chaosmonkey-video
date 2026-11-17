#!/usr/bin/env python3
"""The title card (T1) as a frame sequence, and the G4 date card as an RGBA PNG.

Type system after holdfire's end card (docs/HARVEST.md section 8): Archivo 800 at 125 % width, tracked 0.14, 150 px for
the title on baseline 590; a 2 px gold rule 840 px wide at 652; Open Sans credits; small print at 22 px; everything
centred on x 960 inside the 864 px safe width; nothing under 22 design px; a soft dark 'shade' halo under all text.
Text comes from docs/credits.json. The title lands on the first frame with a settle (scale 1.06 -> 1 over 3 frames),
then everything holds, no fade, to the last frame. No studio marks, no director's name.

    .venv/bin/python tools/edit/title_card.py t1   [--size 1920x1080] [--out work/edit/title/T1]
    .venv/bin/python tools/edit/title_card.py date [--out design/cards/g4_date_card.png]
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

from common import ROOT, SHOTS, load_json
from typeset import BOOK_GOLD, CREAM, DIM, GOLD, GOLD_PALE, Layer, measure

CREDITS = ROOT / 'docs' / 'credits.json'
VARIANT = 'corona'              # the chosen card (docs/FINISH.md); 'corona' adds a faint G4 corona above the title

TITLE = dict(face='Archivo', weight=800, width=125, track=0.14, size=150, color=CREAM)
STY = {
    'line': dict(face='OpenSans', weight=600, size=32, color=CREAM),
    'dim': dict(face='OpenSans', weight=500, size=25, color=DIM),
    'name': dict(face='OpenSans', weight=600, size=34, color=GOLD_PALE),
    'small': dict(face='OpenSans', weight=500, size=22, color=BOOK_GOLD, alpha=0.9),
    # an italic book title inside small print: Cormorant runs small, so 28 px sits with Open Sans 22 (holdfire's 32/25)
    'small_italic': dict(face='CormorantI', weight=600, size=28, color=BOOK_GOLD, alpha=0.9),
    'support': dict(face='OpenSans', weight=500, size=28, color=BOOK_GOLD),
}
SETTLE = [1.06, 1.04, 1.02]     # frames 0, 1, 2; frame 3 on is 1.0
STAGGER = 1                     # credit group g is fully up by frame g + 1 (all in by frame 5), then held

# vertical layout, design px (baselines). The title sits a little above centre; the credits run beneath it.
Y_TITLE = 440                   # cap height ~108 px: the title spans ~332-440 (its centre ~386, centre of frame 540)
Y_RULE = 484
Y_MUSIC = 534
Y_MADE = 588
Y_MADE_MODELS = 628
Y_LEAD = 680
Y_ROW = 722                     # video row, then picture row, then support rows
SMALL_LEAD = 28
CORONA = dict(src='work/sky/shots/G4/f0060.png', scale=0.30, cy=176, opacity=0.30)


def support_rows(names, k):
    """The support list on one row if it fits at >= 26 px in 864, else split into balanced rows (by width)."""
    st = STY['support']
    sep = '  ·  '
    one = sep.join(names)
    if 864 / measure(one, st) * st['size'] >= 26 or len(names) < 3:
        return [one]
    best = None
    for i in range(1, len(names)):
        a, b = sep.join(names[:i]), sep.join(names[i:])
        w = max(measure(a, st), measure(b, st))
        if best is None or w < best[0]:
            best = (w, [a, b])
    return best[1]


def corona_layer(w, h):
    """A very faint, small, exact corona (tools/sky G4 render) for the top of the card: sky floor removed, radially
    feathered, screen-added over black."""
    im = np.asarray(Image.open(ROOT / CORONA['src']).convert('RGB'), np.float32) / 255.0
    floor = np.percentile(im.reshape(-1, 3), 20, axis=0)
    im = np.clip((im - floor) / (1 - floor), 0, 1)
    H, W = im.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - W / 2, yy - H / 2) / (H / 2)
    im *= np.clip((1.0 - r) / 0.35, 0, 1)[..., None] ** 1.5          # feather to nothing by half the frame height
    k = w / 1920.0
    sc = CORONA['scale'] * k
    small = Image.fromarray((im * 255 + 0.5).astype(np.uint8)).resize((max(1, int(W * sc)), max(1, int(H * sc))),
                                                                     Image.LANCZOS)
    out = np.zeros((h, w, 3), np.float32)
    sw, sh = small.size
    x0, y0 = int(960 * k - sw / 2), int(CORONA['cy'] * k - sh / 2)
    sa = np.asarray(small, np.float32) / 255.0
    ys0, xs0 = max(0, -y0), max(0, -x0)
    ys1, xs1 = min(sh, h - y0), min(sw, w - x0)
    out[y0 + ys0:y0 + ys1, x0 + xs0:x0 + xs1] = sa[ys0:ys1, xs0:xs1]
    return out * CORONA['opacity']


def card_layer(cr, w, h, title_scale=1.0, frame=99):
    """One frame of the card. The title is re-set at title_scale about its own centre (crisp, not resampled);
    credit groups arrive by `frame` (STAGGER)."""
    k = w / 1920.0
    L = Layer(w, h)
    up = lambda g: float(np.clip((frame + 1 - g * STAGGER) / 1.0, 0, 1))   # group g: 0 before frame g, 1 from it
    t = dict(TITLE, size=TITLE['size'] * title_scale)
    cy = Y_TITLE - 54
    L.text([(cr['title'], t)], cy + (Y_TITLE - cy) * title_scale, k=k, safe=864 * title_scale, shade=0.55, glow=10)
    L.rule(Y_RULE, 840, 2, GOLD, 0.96 * up(0), k=k)
    a = up(1)
    if a:
        L.text([(cr['music'], STY['line'])], Y_MUSIC, k=k, alpha=a)
    a = up(2)
    mb = cr.get('made_by')
    if a and mb:
        L.text([(mb['line'], STY['line'])], Y_MADE, k=k, alpha=a)
        L.text([(mb['models'], STY['name'])], Y_MADE_MODELS, k=k, alpha=a)
    a = up(3)
    c = cr['cast']
    y = Y_ROW
    sep = '  ·  '
    if a:
        L.text([(c['lead'], STY['dim'])], Y_LEAD, k=k, alpha=a)
        for row in (c['video'], c['picture']):
            L.text([(sep.join(row), STY['name'])], y, k=k, alpha=a)
            y += 40
        y -= 4
        for row in support_rows(c['support'], k):
            L.text([(row, STY['support'])], y, k=k, alpha=a)
            y += 34
    else:
        y += 2 * 40 - 4 + 34 * len(support_rows(c['support'], k))
    a = up(4)
    y = max(y + 30, 1080 - 24 - SMALL_LEAD * (len(cr.get('small', [])) - 1) - 60)
    for row in cr.get('small', []):
        if a:
            L.text([(txt, STY[st]) for txt, st in row], y, k=k, alpha=a)
        y += SMALL_LEAD
    if y - SMALL_LEAD > 1080 - 24:
        raise ValueError('small print runs off the frame')
    return L


def card_frame(cr, w, h, i, corona=None):
    sc = SETTLE[i] if i < len(SETTLE) else 1.0
    rgb = card_layer(cr, w, h, sc, frame=i).rgb
    if corona is not None:
        rgb = 1 - (1 - rgb) * (1 - corona)                        # screen: the type stays on top, the ring stays faint
    return Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB')


def render_t1(args):
    cr = load_json(CREDITS)
    shots = {s['id']: s for s in load_json(SHOTS)['shots']}
    n = args.frames or shots['T1']['frames']
    w, h = (int(x) for x in args.size.split('x'))
    corona = corona_layer(w, h) if args.variant == 'corona' else None
    out = ROOT / args.out
    tmp = out.with_name(out.name + '.partial')
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    held = None
    last = max(len(SETTLE), 4 * STAGGER + 1)     # from this frame on, every frame is identical (a hold, not a fade)
    for i in range(n):
        if i >= last and held is not None:
            img = held
        else:
            img = card_frame(cr, w, h, i, corona)
            if i >= last:
                held = img
        img.save(tmp / f'f_{i:05d}.png', compress_level=3)
    (tmp / 'meta.json').write_text(json.dumps({'shot': 'T1', 'frames': n, 'size': [w, h], 'settle': SETTLE,
                                               'variant': args.variant, 'credits': cr}, indent=1, ensure_ascii=False))
    shutil.rmtree(out, ignore_errors=True)
    os.replace(tmp, out)
    print(f'T1: {n} frames {w}x{h} ({args.variant}) -> {out.relative_to(ROOT)}')


def render_stills(args):
    """The held card of both variants as PNGs (full size and a 480 px phone-width copy) for comparison."""
    cr = load_json(CREDITS)
    w, h = (int(x) for x in args.size.split('x'))
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    for v in ('plain', 'corona'):
        img = card_frame(cr, w, h, 99, corona_layer(w, h) if v == 'corona' else None)
        img.save(out / f'T1_{v}.png')
        img.resize((480, int(480 * h / w)), Image.LANCZOS).save(out / f'T1_{v}_480.png')
        print(f'-> {(out / f"T1_{v}.png").relative_to(ROOT)}')


def render_date(args):
    w, h = 1920, 1080
    L = Layer(w, h)
    st = dict(face='Archivo', weight=500, width=112, track=0.32, size=34, color=CREAM)
    # lower third, centred; a soft shade so it holds over the corona
    L.text([(args.text, st)], 880, shade=0.55)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(L.rgba8(), 'RGBA').save(out)
    print(f'date card -> {out.relative_to(ROOT)}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('t1')
    a.add_argument('--size', default='1920x1080')
    a.add_argument('--out', default='work/edit/title/T1')
    a.add_argument('--frames', type=int, default=0, help='default: T1 length from docs/shots.json')
    a.add_argument('--variant', choices=['plain', 'corona'], default=VARIANT)
    c = sub.add_parser('stills')
    c.add_argument('--size', default='1920x1080')
    c.add_argument('--out', default='work/edit/title/compare')
    b = sub.add_parser('date')
    b.add_argument('--text', default='28 MAY 585 BC')
    b.add_argument('--out', default='design/cards/g4_date_card.png')
    args = ap.parse_args()
    {'t1': render_t1, 'date': render_date, 'stills': render_stills}[args.cmd](args)


if __name__ == '__main__':
    main()

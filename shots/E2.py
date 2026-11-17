"""E2 'he never once forgot a spell' (89.417-93.000, 86 frames). Team MOUNTAIN.

The page: the troop of faceless brush-dab monkeys swarming the slope (C_troop_plate keyed onto the book paper);
beside them, in the bare upper right, the storybook's printed text column, razor sharp (匯文明朝體, typeset, never
generated): ch.2's own lines about learning the spells (西遊記 第二回, proofed in design/text/categories.txt),
three vertical columns. One thing moves: a few dabs hop, on twos (canon dab elements C_dab_*).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from shots._mountain import *

T0, T1 = 2146 / 24, 2232 / 24
COLUMNS = ['這猴王也是他一竅通時百竅通', '當時習了口訣自修自煉', '將七十二般變化都學成了']
# (dab element, frame x, frame foot y, first hop time, period)
HOPPERS = [(5, 1330, 895, 89.55, 1.15), (12, 1180, 640, 89.9, 1.3), (21, 470, 470, 90.3, 1.05)]


def typeset(W, H, s):
    """The printed column as an ink layer: crisp glyph edges (no bleed), woodblock-black ink."""
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    px = int(round(40 * s))
    font = ImageFont.truetype(str(ROOT / PRINT_FONT), px)
    x = 1740 * s
    for col in COLUMNS:
        y = 120 * s
        for ch in col:
            d.text((x, y + px * 0.5), ch, font=font, fill=255, anchor='mm')
            y += px * 1.12
        x -= px * 1.6
    a = np.asarray(im, np.float32) / 255.0
    return ink_T(a * 1.15)


def setup(ctx):
    global P, PLATE, TEXT, DABS
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    PLATE = key_paper(load_image('design/plates/C_elements/C_troop_plate.png', size=(ctx.W, ctx.H)), lo=0.04)
    TEXT = typeset(ctx.W, ctx.H, s)
    DABS = []
    for k, x, y, t_on, per in HOPPERS:
        T = element(f'design/plates/C_elements/dabs/C_dab_{k:02d}.png', 84 * s)
        DABS.append((T, x * s, y * s, t_on, per))
    # fix round 2 (QA: hops invisible at 540p): bigger dabs, higher hops, each dab takes every third beat in turn and
    # leaves the ground ON the frame containing its beat
    global HOPS
    bs = [on_frame(b) for b in ctx.timing.beats_in(T0, T1)]
    HOPS = [[b for j, b in enumerate(bs) if j % 3 == i and b >= DABS[i][3] - 0.5] for i in range(len(DABS))]


def render(t, ctx):
    f = P.frame(t)
    f *= PLATE
    f *= TEXT
    for i, (T, x, y, t_on, per) in enumerate(DABS):
        h = 0.0
        past = [b for b in HOPS[i] if b <= t + 1e-9]
        if past:
            n = int(round((t - past[-1]) * 24))            # frames since take-off, drawn on twos after the first
            n = n if n < 1 else n - (n % 2) + 1
            u = (0.5 + n) / 9.0                            # a hop lasts 9 frames
            if u < 1:
                h = 64 * ctx.s * 4 * u * (1 - u) + 10 * ctx.s
        lay_at(f, T, x - T.shape[1] / 2, y - T.shape[0] - h)
    return f

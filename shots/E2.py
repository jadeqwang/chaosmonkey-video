"""E2 'he never once forgot a spell' (89.417-93.000, 86 frames). BOOK team, v3.

v3: THE TROOP IS ALIVE. The painting the director likes (C_troop_plate on the book paper) was given to a video model
as the first frame (minimax/h3 2K, take 1: media/gen/bk3_E2_h3_t1_*.mp4; prompt in media/gen/specs/bk3_E2_h3_t1.json):
pairs groom, two swing in the pines, some walk the slope, each doing its own thing; rocks and pines locked (drift 0).
The clip is keyed back onto OUR paper (Clip.prepare, 1080 store), played from 0.3 s at speed 1; a slow push (1.0 ->
1.10) toward the troop. The printed column stays razor sharp; the static inscription 切切记了口诀 sits beside it.
(v2 text below.)

The page: the troop of faceless brush-dab monkeys swarming the slope (C_troop_plate keyed onto the book paper);
beside them, in the bare upper right, the storybook's printed text column, razor sharp (匯文明朝體, typeset, never
generated): ch.2's own lines about learning the spells (西遊記 第二回, proofed in design/text/categories.txt),
three vertical columns. One thing moves: a few dabs hop, on twos (canon dab elements C_dab_*).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from shots._mountain import *
from tools.ink.video import Clip, Retime
from tools.ink.inscription import inscription

CLIP_SRC = 'media/gen/bk3_E2_h3_t1_158c37e912.mp4'

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
    global P, CLIP, RT, TEXT, INS
    P = Paper(ctx.W, ctx.H, 'new', seed=BOOK_PAPER_SEED, breathe=1.0)
    CLIP = Clip.prepare(CLIP_SRC, ground='light', height=1080, stabilise=False, smooth=0.4, lo=0.04, hi=0.14)
    RT = Retime(t0=T0, src0=0.3, duration=CLIP.duration)
    for w in RT.check(ctx.t0, ctx.t1):
        print('retime:', w)
    TEXT = typeset(ctx.W, ctx.H, ctx.s)
    INS = inscription(ctx, 'E2', box=(1480, 120, 80, 640), paper=P)


def render(t, ctx):
    f = P.frame(t)
    lay_ink(f, CLIP.layer(t, RT, scale=ctx.H / CLIP.h), 0, 0)
    f *= TEXT
    INS.draw(f)
    z = 1.0 + 0.10 * ramp(t, T0, T1, 'sine')
    tx, ty = 800 * ctx.s, 600 * ctx.s
    return view(f, tx + (ctx.W / 2 - tx) / z, ty + (ctx.H / 2 - ty) / z, z, ctx.W, ctx.H)

"""K5 (224.18-228.767) 'it wasn't there on any line'.

The last page of the register (p8 of the team's ledger = the plate's p4 layout): ruled columns of entries, the final
(leftmost) column bare. The torch rests on the bare column; the filled columns fall away into the dark to the right,
the book's outer edge and the dark beyond it on the left. Hold. Nothing moves, not even on the hit at 225.254.
Lyric (if on) small in the lower right, away from the bare column.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.ink import *
from _heaven import *

T0, T1 = 224.16666666666666, 228.75
# fix2 (lead's re-frame): a ledger page, not a close-up. Scale 1.20 page px -> 1080p px: the bare last column (p8
# x 208-414, between the outer frame rule and the first column rule) sits a little left of centre in the middle of the
# torch pool, from the page's top frame rule down; written columns to its right fall off to dark, the page margin and
# the book's edge on its left. Window in p8 page px: see PAGE_RECT.
SC = 1.20                         # page px -> 1080p px
BARE_X = 311                      # centre of the bare column, spread px (p8 is the LEFT page)
FX = 860                          # where the bare column sits in the frame (1080p px)
Y0 = 260                          # page y at the frame's top edge (the top frame rule is at ~350)
POOL = (860, 600, 560)            # torch centre (1080p px) and radius


GAIN = float(os.environ.get('K5_GAIN', '1.42'))
PAGE_RECT = (BARE_X - FX / SC, Y0, BARE_X - FX / SC + 1920 / SC, Y0 + 1080 / SC)


def setup(ctx):
    global F, WORDS
    ensure_ledger()
    W, H = ctx.W, ctx.H
    s = SC * ctx.s
    x0 = BARE_X - FX / SC
    sp = load_image(LEDGER + 'spread_7_8.png')
    night = blur(Paper(W, H, 'aged', seed=88).rgb, 9 * ctx.s) * 0.30                  # what lies beyond the book's edge: the bedspread
    page = fit(sp, W, H, s, x0, Y0)
    a = fit(np.ones(sp.shape[:2] + (1,), np.float32), W, H, s, x0, Y0)
    a = a[..., None] if a.ndim == 2 else a
    # the book's outer edge: a thin shadow under the edge, the leaf slightly lifted
    edge_x = (0 - x0) * s
    xx = np.arange(W, dtype=np.float32)[None, :, None]
    shade = 1 - 0.55 * np.exp(-np.maximum(edge_x - xx, 0) / (14 * ctx.s)) * (xx < edge_x)
    base = page * a + night * (1 - a) * shade
    L = light_field(W, H, (POOL[0] * ctx.s, POOL[1] * ctx.s), POOL[2] * ctx.s, ambient=0.07, gain=GAIN, tilt=88,
                    stretch=1.30, seed=11)
    F = lit(base, L)
    WORDS = line_words(ctx, 'it wasn', 224.2)


def render(t, ctx):
    f = F.copy()
    lyric(f, ctx, sung_words(WORDS, t, tail=1.0), y=0.955, x=0.63, px=28)
    return f

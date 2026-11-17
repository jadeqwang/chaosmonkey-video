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
SC = 0.38                         # page px -> 1080p px (K3 was 0.445: a step back, the whole column in frame)
BARE_X = 317                      # centre of the bare column (p8 col 8: x 220-415), spread px (p8 is the LEFT page)
FX = 830                          # where it sits in the frame (1080p px)
Y0 = 314


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
    L = light_field(W, H, ((FX + 10) * ctx.s, 560 * ctx.s), 400 * ctx.s, ambient=0.06, gain=1.36, tilt=88, stretch=1.45,
                    seed=11)
    F = lit(base, L)
    WORDS = line_words(ctx, 'it wasn', 224.2)


def render(t, ctx):
    f = F.copy()
    lyric(f, ctx, sung_words(WORDS, t, tail=1.0), y=0.955, x=0.63, px=28)
    return f

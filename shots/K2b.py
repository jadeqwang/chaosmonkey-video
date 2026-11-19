"""K2b 'He opened the Book of Life and Death' (212.125-213.792, 40 frames). BOOK v4 (LEDGER sub-team).

v4 (REVISION_V4 §5 K2): the ledger is turned a quarter-turn on the desk (columns vertical on screen) and the monkey (costume
B) draws ONE stroke straight down a column toward the viewer; the camera plunges from the whole spread to the ledger and the
shot ends mid-stroke, matching K3's stroke (same screen column x~0.70, same direction, same speed). See work/book4/LEDGER/NOTES.md.
First-frame framing (whole spread, LAP_ots_push_end) is unchanged from v3 (WORLD's K1->K2b contract).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots._book4_k2b import LedgerShot

T0, T1 = 5091 / 24, 5131 / 24
CLIP = os.environ.get('K2B_CLIP', 'media/gen/bk4_K2b_h3_t2_adbdd75890.mp4')       # the pick (take 2)
CLIP_START = float(os.environ.get('K2B_START', '0'))
FOCUS = (2015, 1312)
Z1 = 3.4
TIP = (2128, 1300)


# out frame -> clip frame: the clip's own pace through the plunge, then the stroke itself run ~4.8x (one fast breath),
# smeared by temporal blur; the shot's last frame lands mid-stroke (head ~65% down the column)
KEYS = [(0, 0), (31, 29), (39.5, 72)]


def setup(ctx):
    global PS
    PS = LedgerShot(ctx, T0, T1, CLIP or None, CLIP_START, FOCUS, Z1, TIP, clip_keys=KEYS)


def render(t, ctx):
    return PS.render(t, ctx)

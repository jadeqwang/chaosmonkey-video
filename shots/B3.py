"""B3 'a stone looked over the sea' (26.125-29.292, 76 frames). Team MOUNTAIN.

FLAT PAGE-SPACE move (the room team maps this onto the book in perspective): the whole double-page spread in
frame as flat paper, B_master painted across it (花果山 in the lower-left corner, the stone a speck on top, sea and
sky bare paper) and a narrow column on the right page. No ch.1 stone wording exists in design/text/, so per the
director the column is faint ruled lines (界行) with no characters. Then the film's signature push in toward the
mountain until the page edges have left frame; only once we are inside does the mist band (bare paper) begin to
drift. Outside the pages: flat faded-indigo cloth (to be replaced by the room team's book).
"""
import numpy as np

from shots._mountain import *

T0, T1 = 627 / 24, 703 / 24
SW, SH = 4585, 2420                       # the spread (two pages, A_open_book proportions)
MX, MY = 260, 230                         # canvas margin around the spread
CW, CH = SW + 2 * MX, SH + 2 * MY
PS = SH / 1920.0                          # B_master scale onto the spread
START = (MX + SW / 2, MY + SH / 2, 1920 / (SW + 330))
END = (MX + 1060, MY + 1500, 1920 / 2350)
T_PUSH0, T_PUSH1 = 26.32, T1 + 0.25       # the push is still moving on the cut
CLOTH = np.array([0.33, 0.36, 0.43], np.float32)


def setup(ctx):
    global PAGE, BARE, MIST, CAM, T_IN
    paper = Paper(SW, SH, 'new', seed=BOOK_PAPER_SEED)
    T = key_paper(load_image(B + 'B_master.png'), lo=0.03)
    T = cv2.resize(T, (int(round(T.shape[1] * PS)), SH), interpolation=cv2.INTER_AREA)
    page = paper.rgb.copy()
    lay_ink(page, T, 0, 0)
    # the ruled column on the right page: five printed rules, a woodblock's broken line, pale
    rules = np.ones((SH, SW, 3), np.float32)
    x1, y0, y1, n, pitch = SW - 300, 300, 1720, 5, 52
    br = fbm(SH, 8, 9.0, 3, 'rule', octaves=3)
    for k in range(n + 1):
        x = x1 - k * pitch
        a = 0.16 * (0.75 + 0.5 * smoothstep(0.3, 0.6, br[y0:y1, k % 8]))
        rules[y0:y1, x:x + 3] *= (1 - a)[:, None, None] * np.ones((1, 3, 3), np.float32) + 0
    for y in (y0, y1):
        rules[y:y + 3, x1 - n * pitch:x1 + 3] *= 0.86
    page *= blur(rules, 0.7)
    PAGE = np.empty((CH, CW, 3), np.float32)
    PAGE[:] = CLOTH * (0.92 + 0.08 * fbm(CH, CW, 60.0, 2, 'cloth')[..., None])
    PAGE[MY:MY + SH, MX:MX + SW] = page
    BARE = PAGE.copy()
    BARE[MY:MY + SH, MX:MX + SW] = paper.rgb
    # the mist band, as painted across the mountain's waist (bare paper): drifts only once we are inside
    m = np.zeros((CH, CW), np.float32)
    band_ = mist_band(SW + 1200, 460, 110, 350, seed=5, softness=0.5, wisp=0.75)
    MIST = (band_, MX - 600, MY + int(1000 * PS) - 110)
    CAM = Camera.push_in(T_PUSH0, T_PUSH1, START, END, 'in')
    # when have the page edges left the frame? (left edge and bottom edge)
    T_IN = T1
    for t in np.arange(T0, T1, 1 / 48):
        cx, cy, z = CAM.at(t)[:3]
        if cx - 960 / z > MX and cy + 540 / z < MY + SH:
            T_IN = float(t)
            break


def render(t, ctx):
    cx, cy, z = CAM.at(t)[:3]
    f = view(PAGE, cx, cy, z, ctx.W, ctx.H)
    bm, mx, my = MIST
    drift = -26.0 * max(0.0, t - T_IN) - 9.0 * max(0.0, t - T_IN) ** 2      # eases from still into a slow drift
    a = np.zeros((CH, CW), np.float32)
    x0 = int(round(mx + drift))
    a0, a1 = max(0, x0), min(CW, x0 + bm.shape[1])
    a[my:my + bm.shape[0], a0:a1] = bm[:, a0 - x0:a1 - x0]
    a[:MY], a[MY + SH:], a[:, :MX], a[:, MX + SW:] = 0, 0, 0, 0
    am = view(a, cx, cy, z, ctx.W, ctx.H)
    bv = view(BARE, cx, cy, z, ctx.W, ctx.H)
    f += (bv - f) * np.clip(am, 0, 1)[..., None] * 0.8
    return f

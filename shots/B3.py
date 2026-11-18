"""B3 'a stone looked over the sea' (26.125-29.292, 76 frames). BOOK team, v3 (REVISION_V3 §2.1, §13).

STEPPING INTO THE PAINTING. Frame 0 is the flat spread exactly as the attic's over-shoulder push ends
(v3_LAP_ots_push_end: spread u 0.031..0.969, v 0.105..0.895; see LOG_v3_book.md) with the inscription on the right
page. Then the camera crosses the page surface and the picture opens into depth: every element of the flat picture
lives on its own plane (far ridges over the sea, the summit, a band of mist, the near cliff, two foreground pines),
registered at frame 0 so the page is FLAT there; as the push goes in they separate with true parallax, the pines
slide past the lens, the ridges hang back, the mist (bare paper) flows between summit and cliff.
Page art for the room team: `python shots/B3.py` -> media/comp/pages/B3_page.png (the flat spread, unlit).
"""
import numpy as np

from shots._mountain import *
from tools.ink.inscription import inscription

T0, T1 = 627 / 24, 703 / 24
SW, SH = 3072, 2048                        # the spread, at the layout's 1.5:1
C0 = (SW / 2.0, SH / 2.0)
Z0 = 1920.0 / (0.938 * SW)                 # frame 0: u 0.031..0.969 of the spread across the frame
END = (790.0, 800.0, 1.36)
T_PUSH0 = T0 + 0.12
MS = SW / 3392.0                           # B_master scale onto the spread
MY = 150                                   # B_master's top edge on the spread
import os
T_CLIP = float(os.environ.get('B3_TCLIP', 27.75))      # B3_TCLIP=99 renders the layered move alone
CLIP_SRC = 'media/gen/bk3_alive_B3_h3_t3_e231888b05.mp4'     # take 3: travels up through the mist to the stone
R0, R1 = 4.2, 2.4                            # clip frames per film frame at the join and at the cut
PX = 60.0 / Z0                             # inscription size on the page so it is 60 px at frame 0


def layers():
    """[(name, ink layer, depth, (x, y) canvas pos)] registered on the flat page."""
    def master(name):
        T = key_paper(load_image(B + name), lo=0.03)
        return cv2.resize(T, (SW, int(round(T.shape[0] * MS))), interpolation=cv2.INTER_AREA)
    out = []
    for i, (x, y, w, g, d) in {2: (1250, 1040, 1700, 0.55, 7.0), 1: (1900, 1150, 1300, 0.45, 5.0)}.items():
        T = key_paper(load_image(f'design/plates/C_elements/ridges/C_ridge_{i:02d}.png'), lo=0.02, gain=g)
        T = cv2.resize(T, (w, int(T.shape[0] * w / T.shape[1])), interpolation=cv2.INTER_AREA)
        out.append((f'ridge{i}', T, d, (x, y)))
    out.append(('summit', master('B_master_L_summit.png'), 2.4, (0, MY)))
    out.append(('near', master('B_master_L_near.png'), 1.0, (0, MY)))
    out.append(('pine_a', element('design/plates/C_elements/pines/C_pine_02.png', 520), 0.5, (150, 1260)))
    out.append(('pine_b', element('design/plates/C_elements/pines/C_pine_04.png', 330, flip=True), 0.62, (1235, 1455)))
    out.append(('pine_c', element('design/plates/C_elements/pines/C_pine_03.png', 430), 0.42, (560, 1560)))
    return out


def gutter():
    T = np.ones((SH, 80, 3), np.float32)
    x = np.abs(np.arange(80, dtype=np.float32) - 40) / 40
    T *= (1 - 0.07 * np.exp(-(x / 0.35) ** 2))[None, :, None]
    return T


def page_art(paper, ins):
    f = paper.rgb.copy()
    for name, T, d, (x, y) in layers():
        lay_ink(f, T, x, y)
    lay_ink(f, gutter(), SW // 2 - 40, 0)
    ins.draw(f)
    return f


def aligned(d, pos):
    """Scale and position that register a depth-d layer with the flat page at the START camera."""
    dz0 = 1.0 - 1.0 / Z0
    s = Z0 * (d - dz0) / d
    return s, (C0[0] + s * (pos[0] - C0[0]), C0[1] + s * (pos[1] - C0[1]))


MX = MY = 0                                 # v2 compatibility (shots/_rooms88.spread('hgs') reads PAGE/BARE/MX/MY/SW/SH)
PAGE = BARE = None


def setup(ctx):
    global SC, CAM, PAGE, BARE
    if ctx is None:                         # v2 callers: only the flat page and its bare paper
        paper = Paper(SW, SH, 'new', seed=BOOK_PAPER_SEED)
        PAGE = page_art(paper, inscription((SW, SH), 'B3', (2560, 300, 330, 1100), px=PX, paper=paper))
        BARE = paper.rgb.copy()
        return
    paper = Paper(SW, SH, 'new', seed=BOOK_PAPER_SEED)
    SC = Scene(SW, SH, paper=paper)
    ins = inscription((SW, SH), 'B3', (2560, 300, 330, 1100), px=PX, paper=paper)
    for name, T, d, pos in layers():
        s, p = aligned(d, pos)
        SC.add(T, depth=d, pos=p, scale=s, name=name, occlude=(name in ('near', 'summit')))
        if name == 'summit':                                    # mist lies between the summit and the near cliff
            SC.mist(985, 1275, depth=1.6, drift=-34, opacity=lambda t: 0.25 + 0.65 * ramp(t, T_PUSH0, T_PUSH0 + 1.6, 'sine'),
                    seed=5, softness=0.7, wisp=0.75)
    SC.mist(1500, 1760, depth=0.8, drift=-52, opacity=lambda t: 0.75 * ramp(t, T_PUSH0 + 0.2, T_PUSH0 + 1.4, 'sine'),
            seed=9, softness=0.75, wisp=0.8)          # a second veil between the cliff foot and the foreground pines
    SC.add(gutter(), depth=1.0, pos=(SW // 2 - 40, 0), opacity=lambda t: 1 - ramp(t, T_PUSH0, T_PUSH0 + 1.0, 'sine'))
    SC.add(ins.T, depth=1.0)
    SC.add(place_rgba(ins), depth=1.0, kind='rgba')
    # §13 alive pass: from T_CLIP the travel INSIDE the painting is a minimax/h3 dolly animated from our own frame at
    # T_CLIP (work/book3/gen/B3_mid.jpg = this shot's still at 27.75): real depth, mist flowing, the far ridges hanging
    # back. Played at CLIP_RATE, tone-matched to our frame, crossed in over 5 frames.
    global CLIPF, GAIN
    from tools.ink.video import decode
    CLIPF = [(np.clip(im, 0, 1) * 255).astype(np.uint8) for _, im in decode(CLIP_SRC, height=1080)]
    CAM = Camera([(T0, C0[0], C0[1], Z0), (T_PUSH0, C0[0], C0[1], Z0), (T1 + 0.3, END[0], END[1], END[2], 'inout')])
    ours = SC.render(T_CLIP, CAM, ctx.size)
    f0 = cv2.resize(CLIPF[0].astype(np.float32) / 255, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA)
    # one colour gain for the whole frame (bare-paper tone to bare-paper tone): a low-frequency match left a halo
    GAIN = (np.percentile(ours.reshape(-1, 3), 80, axis=0) / np.maximum(np.percentile(f0.reshape(-1, 3), 80, axis=0), 1e-3)).astype(np.float32)


def place_rgba(ins):
    out = np.zeros((SH, SW, 4), np.float32)
    s = ins.seal
    x, y = ins.seal_pos
    out[y:y + s.shape[0], x:x + s.shape[1]] = s
    return out


def render(t, ctx):
    f = SC.render(t, CAM, ctx.size) if t < T_CLIP + 4 / 24.0 else None
    if t >= T_CLIP - 1e-9:
        u = (t - T_CLIP) * 24.0                              # the clip starts at the push's own speed and settles
        n = (T1 - T_CLIP) * 24.0
        q = min(len(CLIPF) - 1.001, R0 * u - (R0 - R1) / (2 * n) * u * u)
        i0 = int(q)
        g = (CLIPF[i0].astype(np.float32) * (1 - (q - i0)) + CLIPF[i0 + 1].astype(np.float32) * (q - i0)) / 255
        g = cv2.resize(g, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA) * GAIN
        k = ramp(t, T_CLIP - 1 / 24.0, T_CLIP + 4 / 24.0, 'linear')
        f = g if f is None else f + (g - f) * k
    return np.clip(f, 0, 1)


if __name__ == '__main__':
    import os
    os.makedirs('media/comp/pages', exist_ok=True)
    paper = Paper(SW, SH, 'new', seed=BOOK_PAPER_SEED)
    save_image('media/comp/pages/B3_page.png', page_art(paper, inscription((SW, SH), 'B3', (2560, 300, 330, 1100),
                                                                            px=PX, paper=paper)))
    print('wrote media/comp/pages/B3_page.png')

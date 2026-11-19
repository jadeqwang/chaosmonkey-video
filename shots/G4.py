"""G4 song frames 3390-3514 (125 f). ATTIC v4. Sings on camera: Mama ('Then 听话, or you'll get one to wear / Do what mama says, no more ...').
Keyframe media/kf/v4/G4.jpg (v4_G4, set-checked, fallen books lower right). The take was made at a tight crop (box 360,130,1180,664 of the
3072 keyframe) and is pasted back into the full keyframe (work/attic4/g/paste.py -> media/comp/attic4/G/G4_s1_full.mp4); clip frame 0 =
song 139.75, shift 0. Camera: opens on the G3 strip framing, the paper margins draw back to full frame over the first 10 frames while the
camera widens to the books, holds wide, then pushes in toward Mama's face. Own margin function (opens)."""
from shots._attic4 import *

T0, T1 = 3390 / 24, 3515 / 24
PLACE = 139.75
OPEN_F = 10


def g_margins(t, W, H):
    """narrow strip (shared schedule's 25 % at 141.25) -> open over OPEN_F frames, grey drain fades with it"""
    from tools.ink.core import ease
    from shots._margins import margin_state
    u = min(1.0, max(0.0, (t - T0) / (OPEN_F / 24.0)))
    st = dict(margin_state(T0 - 1e-3, W, H))                  # G3's last state (25 %)
    w0 = (st['rect'][2] - st['rect'][0]) / W
    w = w0 + (1.06 - w0) * ease(u, 'inout')
    p = max(0.0, (1.04 - w) / (1.04 - 0.22))
    half = w * W / 2.0
    tb = (-0.03 + 0.075 * p) * H
    return {'rect': (W / 2.0 - half, tb, W / 2.0 + half, H - tb), 'desat': 0.4 * float(min(1.0, p ** 0.7 * 1.08)), 'progress': p, 'open': p <= 0.0}


S = AtticShot([Seg4(T0, T1, 'G4', key='G4', tmap=[[T0, T0 - PLACE], [T1, T1 - PLACE]], floor=0.66, keep=[(600, 330, 420, 330), (780, 600, 300, 300)],
                    cam=[(T0, 700, 400, 1.6), (T0 + 0.55, 960, 540, 1.0), (T0 + 1.8, 960, 540, 1.0), (T1, 640, 330, 1.9)])],
               margins=True, margin_state=g_margins)


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
# swap

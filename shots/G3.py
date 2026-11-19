"""G3 134.375-141.250 (165 f). ATTIC v4. 'It isn't fair, it isn't fair / I don't want it in his hair': she does NOT sing on camera.
Top-down (v4_G3): her hand lies flat over the banded monkey on the page to protect him, pats, her head (bottom edge) shaking no.
Keyframe media/kf/v4/G3.jpg (blank page); Kling v4 take t2 (5.04 s) slowed to 0.73x over the shot (picks.json key G3).
Page art (pilgrim with the gold band) + the hand's shadow cast on the page as in v3. Margins: v3's narrow strip (shared schedule 28 -> 25 %)."""
from shots._attic4 import *

T0, T1 = 3225 / 24, 3390 / 24


def g_margins(t, W, H):
    from shots._margins import margin_state
    st = dict(margin_state(t, W, H)); st['desat'] *= 0.4
    return st


S = AtticShot([Seg4(T0, T1, 'G3', key='G3', tmap=[[T0, 0.0], [T1, 5.04]], floor=0.62, keep=[(800, 480, 520, 380)],
                    page=dict(kind='shift:0.03,-0.2:pilgrim', roi=(430, 70, 1120, 720), quad=[[452, 148], [1517, 92], [1527, 688], [548, 772]],
                              plate=True, clean=False, shadow=dict(d=(-46, 32), soft=10, aniso=0.7, strength=1.0, grow=1.02)),
                    cam=[(T0, 730, 450, 1.12), (T1, 730, 440, 1.2)])], margins=True, margin_state=g_margins)


HAND = [(595, 440), (630, 368), (690, 370), (772, 442), (790, 520), (762, 600), (792, 700), (782, 1080), (598, 1080), (610, 700), (640, 590), (598, 480)]


def setup(ctx):
    """PageArt's paper mask treats every bright pixel of the keyframe as paper, which lets the art print over the child's hand.
    After the segment is set up, the keyframe used for the paper mask only (PageArt reads seg.KF) gets the hand and forearm
    darkened, so the hand counts as 'not paper' (no art on it) and casts the shadow."""
    import cv2
    import numpy as np
    S.setup(ctx)
    for sg in S.segs:
        H, W = sg.KF.shape[:2]
        m = np.zeros((H, W), np.float32)
        cv2.fillPoly(m, [np.round(np.array(HAND) * (W / 1920.0)).astype(np.int32)], 1.0)
        m = cv2.GaussianBlur(cv2.dilate(m, np.ones((int(18 * W / 1920) | 1,) * 2, np.uint8)), (0, 0), 2.0 * W / 1920)
        sg.KF = (sg.KF * (1 - 0.8 * m[..., None])).astype(sg.KF.dtype)


def render(t, ctx):
    return S.render(t)

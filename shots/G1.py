"""G1 song frames 2915-3058 (144 f). ATTIC v4. Sings on camera: little Jade ('Why does he wear a band of gold? / Is it heavy? Is it cold?').
Keyframe media/kf/v4/G1.jpg (v4_G1, set-checked); take = Kling-free two-pass: Seedance act (at4ls_G1_4, crop) -> p-video-animate sing
(ls4w_G1_asrc4s1) pasted back into the full keyframe at the crop box (work/attic4/g/paste.py -> media/comp/attic4/G/G1_full.mp4).
Clip frame 0 = song 118.59, shift 0, speed 1. Margins: v3 behaviour (shared schedule, grey drain x0.4), closes into BOOK's G2."""
from shots._attic4 import *

T0, T1 = 2915 / 24, 3059 / 24
PLACE = 118.59


def g_margins(t, W, H):
    from shots._margins import margin_state
    st = dict(margin_state(t, W, H)); st['desat'] *= 0.4
    return st


S = AtticShot([Seg4(T0, T1, 'G1', key='G1', tmap=[[T0, T0 - PLACE], [T1, T1 - PLACE]], floor=0.64, keep=[(1030, 500, 320, 320)],
                    cam=[(T0, 960, 540, 1.0), (T1, 990, 520, 1.08)])], margins=True, margin_state=g_margins)


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)
# swap

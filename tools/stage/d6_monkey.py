"""STAGE -> WORLD hand-over: the costume-B monkey for D6 (somersaults in from the right on his cloud, lands in 亮相).
Source: Kling v4 multi-keyframe take s4_d6_k4b (keyed store work/ink_clips/s4_d6_k4b), retimed to D6 (73.500-76.417):
he enters from the right, somersaults over the cloud, the cloud thins away, crouches and rises into the one-leg look-out
亮相 on element frame 37 (= song 75.042, the kick 75.025) and holds alive to the end.
    from tools.stage.d6_monkey import monkey_layer, FOOT
    T = monkey_layer(t, W, H)            # HxWx3 transmittance (1 = nothing), full frame, the 1920x1080 element at WxH
    lay_ink(frame, place_small(T, ...))  # or tools.ink.transform(T, scale=..., tx=..., ty=...) then frame *= T
FOOT = the standing foot of the 亮相 in element px (1920x1080) for putting him on the middle peak.
Ready-made: media/el/stage_v4/D6_monkey_B_T.mp4 (+ _png/ sequence), multiply-ready (white = transparent), and
media/el/stage_v4/D6_monkey_B.json (per-frame source time and ink box). Re-render at 1080 for free (it is 1080 native)."""
import json
import numpy as np
from tools.ink import resize
from tools.ink.video import Clip
from tools.stage.stage import KeyRetime

TAG = 's4_d6_k4b'
T0, N, LAND_F = 73.5, 70, 37
SRC0, SRC_LAND, SRC_END = 0.3, 3.833, 5.9
_CL = None


def _clip():
    global _CL
    if _CL is None:
        _CL = Clip(f'work/ink_clips/{TAG}')
    return _CL


def retime():
    cl = _clip()
    return KeyRetime([(T0, SRC0), ((1764 + LAND_F) / 24, SRC_LAND), (T0 + N / 24, SRC_END)], duration=cl.duration)


def monkey_layer(t, W=1920, H=1080):
    cl = _clip()
    T = np.clip(cl.at(retime().src(t)), 0, 1)
    if (T.shape[1], T.shape[0]) != (W, H):
        T = resize(T, W, H)
    return T.astype(np.float32)


def _foot():
    m = json.load(open('media/el/stage_v4/D6_monkey_B.json'))
    b = m['frames'][-1]['ink_box']
    return (b[0] + b[2]) / 2, b[3]


try:
    FOOT = _foot()
except Exception:                      # noqa: BLE001
    FOOT = None

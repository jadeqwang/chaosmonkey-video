"""Stage team v4 helpers (costume B). Everything of stage3 plus the v4 D1/D2 hand-over: D1 holds the 亮相 longer
(the wind-up into the first bow starts at D2_PRE = frame 1451 instead of 1445) and D2 is the multi-keyframe take."""
from tools.stage.stage3 import *            # noqa: F401,F403
from tools.stage.stage3 import KeyRetime, on_frame
import os, json

D2_TAKE = os.environ.get('STAGE_D2_TAKE', 's4_d2_k4a')
D2_PRE = 1451 / 24                          # D1's frame where the bows' wind-up starts
D2_BOWS = [61.321, 62.205, 63.090, 63.980]  # as v3: east, south, west, north nadirs on every 2nd grid beat from "bowed"
# the take's four bows at their lowest (clip s), and where it leaves the 亮相; measured per take (work/stage/v4/d2_nadirs.json)
_N = json.load(open('work/stage/v4/d2_nadirs.json')) if os.path.exists('work/stage/v4/d2_nadirs.json') else {}
D2_NADIR = _N.get(D2_TAKE, {}).get('nadir', [30 / 24, 56 / 24, 84 / 24, 112 / 24])
D2_LEAVE = _N.get(D2_TAKE, {}).get('leave', 4 / 24)


def d2_retime(duration):
    """Song time -> D2 clip time, shared by D1 (its last frames are the wind-up) and D2: each bow's lowest point lands
    on its beat and is held 2 frames (the stamp)."""
    keys = [(D2_PRE, D2_LEAVE)]
    for b, n in zip(D2_BOWS, D2_NADIR):
        keys += [(on_frame(b), n), (on_frame(b) + 2 / 24, n)]
    keys.append((on_frame(D2_BOWS[-1]) + 1.2, min(duration - 0.05, D2_NADIR[-1] + 0.45)))
    return KeyRetime(keys, duration=duration)

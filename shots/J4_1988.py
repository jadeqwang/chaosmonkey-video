"""J4, the 1988 half (song frames 4719-4815, 97 f) -> media/comp/J4_1988.mp4 for BED+CAR's split comp (they take the
centre 480 columns at 540p). ATTIC v4 (set J4L = LAP_front, keyframe media/kf/v4/J4L.jpg, Seedance 2.5 sing take). LAP_front in red neon: Mama and little Jade look out and sing 'No cradle, no song',
swaying; on the echo hit (198.74 -> 198.833) little Jade throws both arms up, Mama leans back from the small hands.
Kling v4 on media/kf/v3/J4.jpg, real time (no lip transfer: the faces are small in the split; mouths move with the take)."""
from shots._attic4 import *

T0, T1 = 4719 / 24, 4816 / 24


def lift(f, t, shot, sg):
    """Balance against the flashlight-white 2026 half of the split: lift the mids, and glaze the room cinnabar so the
    half reads as 'red' at a glance (BED+CAR: the 1988 half was much darker than theirs)."""
    f = 1 - (1 - f) ** 1.55
    l = f.mean(axis=2, keepdims=True)
    red = np.array([1.0, 0.36, 0.30], F32)
    a = np.clip(0.55 - l, 0, 0.55) * 0.75 * np.clip((l - 0.16) / 0.16, 0.25, 1)                 # the darks take the neon; faces and paper keep their colour
    return np.clip(f * (1 - a) + (l * 1.9 * red + 0.05 * red) * a, 0, 0.97).astype(F32)

P = pick4('J4L')
TM = [[T0, 0.0], [T1, T1 - T0]] if not P else P['tmap']
S = AtticShot([Seg4(T0, T1, 'J4L', key='J4L', tmap=TM, floor=0.92, keep=[(480, 120, 960, 900)],
                    cam=[(T0, 960, 540, 1.0), (T1, 960, 540, 1.0)])], post=lift)


def setup(ctx):
    S.setup(ctx)


def render(t, ctx):
    return S.render(t)

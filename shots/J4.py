"""J4  196.625-200.667  "No cradle, no song (no song)" (stage team).

Four heads in a row on bare paper, after Muqi's Six Persimmons: Mama (1988), little Jade, Jade, the daughter, cut from
the canon expression sheets (tools/stage/heads.py) and keyed as ink of four strengths, darkest to palest, left to
right; evenly spaced with a little irregularity. They sing by puppet-style HARD mouth swaps on the measured word
onsets (no morphing). On the strongest hit (perc 198.613) all four snap to the same tilt: a 亮相, mouths frozen for
8 frames. The echo "(no song)" (198.74) is a faint re-pressed 倉 over the fourth face. Nothing else: heads and paper.
"""
import numpy as np

from tools.ink import *
from tools.ink.core import INK_K
from tools.stage.stage import seals, lyrics_on, LATIN, PAPER_SEED, hold_index

T0, T1 = 196.625, 200.666667
HEADS = [  # name, mouths available, ink strength, (cx, cy) centre, height, own tilt
    ('mama', ('shut', 'open'), 1.30, (352, 500), 430, -2.5),
    ('lj', ('shut', 'open', 'o'), 0.86, (764, 518), 412, 2.0),
    ('jade', ('shut', 'open'), 0.56, (1168, 494), 450, -1.0),
    ('dau', ('shut', 'open', 'o'), 0.34, (1574, 524), 384, 3.0),
]
T_LIANG = 198.613          # strongest hit in the shot (perc 1.0): the 亮相
T_ECHO = 198.74            # "(no song)"
FREEZE = 8 / 24
COMMON_TILT = -8.0
# mouth score on the word onsets (AUDIO_MAP lines 59-60): No 196.615 · cradle 196.83 · no 197.81 · song 198.12 ·
# (no 198.74 · song 199.38) · end 199.475
SCORE = [(0.0, 'shut'), (196.615, 'o'), (196.83, 'open'), (197.02, 'shut'), (197.81, 'o'), (198.12, 'open'),
         (198.74, 'o'), (199.02, 'open'), (199.38, 'open'), (199.48, 'shut')]


def _ink(T, strength):
    k = float(np.mean(INK_K))
    lum = T.mean(axis=2)
    d = -np.log(np.clip(lum, 1e-3, 1)) / k
    return ink_T((d * strength).astype(np.float32))


def setup(ctx):
    global P, LAY, SEAL, INS, TIMES
    s = ctx.s
    P = Paper(ctx.W, ctx.H, 'aged', seed=PAPER_SEED + 1)
    LAY = {}
    for name, mouths, k, (cx, cy), h, tilt in HEADS:
        for m in mouths:
            T = _ink(np.load(f'work/stage/heads/{name}_{m}.npy'), k)
            T = resize(T, int(T.shape[1] * h * s / T.shape[0]), int(h * s))
            ph, pw = int(T.shape[0] * 0.12), int(T.shape[1] * 0.15)
            T = np.pad(T, ((ph, ph), (pw, pw), (0, 0)), constant_values=1.0)
            for key, ang in (('own', tilt), ('liang', COMMON_TILT)):
                # rotate about the chin (the neck pin of a puppet head)
                L = transform(T, angle=ang, center=(T.shape[1] / 2, T.shape[0] * 0.80), out_size=(T.shape[1], T.shape[0]))
                LAY[(name, m, key)] = L
    SEAL = seals(s)
    TIMES = [a for a, _ in SCORE]
    INS = Inscription('No cradle, no song', LATIN, region=(int(760 * s), int(860 * s), int(400 * s), int(52 * s)),
                      size=ctx.size, vertical=False, words=ctx.timing.words('No cradle, no song'), mode='word',
                      paper=P, seed=9, density=0.8)


def mouth_at(t):
    if T_LIANG <= t < T_LIANG + FREEZE:
        t = T_LIANG                                    # the 亮相 holds the mouths too
    return SCORE[hold_index(t, TIMES)][1]


def render(t, ctx):
    s = ctx.s
    f = P.frame(t)
    m = mouth_at(t)
    key = 'liang' if t >= T_LIANG else 'own'
    jolt = -5 * s if 0 <= t - T_LIANG < 2 / 24 else 0
    for name, mouths, k, (cx, cy), h, tilt in HEADS:
        mm = m if m in mouths else ('open' if m == 'o' else 'shut')
        L = LAY[(name, mm, key)]
        lay_ink(f, L, int(cx * s - L.shape[1] / 2), int(cy * s - L.shape[0] / 2 + jolt))
    x4, y4 = HEADS[3][3]
    echoes(f, SEAL['cang_small'], t, [(T_ECHO, ((x4 + 40) * s, (y4 - 30) * s))], first=0.42, seed=12)
    if lyrics_on(ctx):
        INS.draw(f, t)
    return f

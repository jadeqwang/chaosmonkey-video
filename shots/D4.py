"""D4 '一通百通' (67.917-69.292, 33 frames). BOOK team, v3 (REVISION_V3 §3.2).

(a) 67.917: ONE carved character, 通 (千字文 line 117 右通廣內), fills the frame. A breath of mist (bare paper; the same
    water sleeve as Mama's breath in C5) drifts in from the right and touches it; on '通' (68.09) it lights: gold runs
    into the cut.
(b) cut wide on '百' (68.53) to the cliff face (shots/_tong.py: the mid cliff, 千字文 1-160). The light does not spread:
    it JUMPS. From 通 a fine gold thread shoots to every carved character that shares 辶 with it (道 遐 邇 過 隨 連 造 退
    逸 逐 達 途 遵), wherever it is; on the second '通' (68.77) each of those passes it on through its OTHER component
    (道 -> 首 ..., IDS data). D5 continues from this frame.
"""
import numpy as np

from shots._mountain import *
from shots import _tong

T0, T1 = 1630 / 24, 1663 / 24
T_TONG, T_BAI, T_TONG2 = (on_frame(x) for x in (68.09, 68.53, 68.77))
TIMES = [68.53, 69.50, 70.146, 70.594, 71.029, 71.471, 71.925, 72.356]      # generation start times (D4 + D5)
STAGGER = [0.68, 0.50, 0.36, 0.3, 0.3, 0.3]      # each generation's jumps dealt one after another: every jump is seen
T_BASE, T_SPAN = 68.0, 5.0
Z_WIDE = 0.66
THREAD_GENS = 3


def build_wide(ctx):
    """Shared by D4(b) and D5: the carved mid cliff, the chain and its schedule."""
    C, cells, paper = _tong.build_mid()
    chars = [c for c in qianziwen(160) if c in cells]
    gens = _tong.chain(chars, per_jump=2, pos=cells)
    t_lit, edges = _tong.schedule(gens, TIMES, STAGGER)
    t_lit['通'] = T_BASE
    rest = [c for c in chars if c not in t_lit]
    for c in rest:                                              # never reached by a true jump: lit with the gong
        t_lit[c] = 72.805
    _tong.set_lit(C, cells, t_lit, T_BASE, T_SPAN, C.size)
    C.prepare(fill=0.4)
    n = sum(len(g) for g in gens[:THREAD_GENS])
    E = [(cells[s][0], cells[s][1], cells[d][0], cells[d][1], t, g) for s, d, t, g in edges[:n]]
    return dict(C=C, cells=cells, paper=paper, edges=E, gens=gens, n_rest=len(rest))


def wide_frame(S, t, cx, cy, z, ctx, t_end=None):
    C = S['C']
    g = _tong.progress(t, T_BASE, T_SPAN)
    f = view(None, cx, cy, z, ctx.W, ctx.H,
             render=lambda box: C.render((312, 24, 0.8), fill=0.4, gold=g, ambient=0.86, warmth=0.6, box=box))
    zz = z * ctx.W / 1920.0
    _tong.threads(f, t, S['edges'], lambda x, y: ((x - cx) * zz + ctx.W / 2, (y - cy) * zz + ctx.H / 2), ctx.s,
                  t_end=t_end)
    return f


def start_cam(S):
    """Wide enough that most of the first jumps land in frame: between 通 and the middle of its 辶 family."""
    x, y = S['cells']['通']
    tg = [S['cells'][d] for _, d, _ in S['gens'][0]]
    mx, my = sum(p[0] for p in tg) / len(tg), sum(p[1] for p in tg) / len(tg)
    C = S['C']
    cx, cy = 0.4 * x + 0.6 * mx, 0.4 * y + 0.6 * my
    hw, hh = 960 / Z_WIDE, 540 / Z_WIDE
    return min(max(cx, hw - 200), C.W - hw + 700), min(max(cy, hh - 150), C.H - hh)


def setup(ctx):
    global CC, S, SLEEVE, PC, XX, YY
    raw = load_image(B + 'B_cliff_run.png')
    patch = cv2.resize(raw[330:870, 6820:7780], (1920, 1080), interpolation=cv2.INTER_CUBIC)
    PC = Paper(1920, 1080, 'new', seed=BOOK_PAPER_SEED, scale=2.0)
    rock_c = onto_paper(patch, PC, ground=np.percentile(raw.reshape(-1, 3), 97, axis=0))
    CC = Cliff(rock_c, '通', SEAL_FONT, size=820, region=(550, 120, 820, 840), seed=9, weather=0.04, chips=0.0,
               jitter=0.0, weight=0.016, paint=0.35, depth=0.45, streaks=0.2, grime=0.3)
    CC.prepare(fill=0.55, gold=True)
    L = 4200
    band_ = mist_band(L, 1080, 250, 760, seed=11, softness=0.5, wisp=0.5)
    xs = np.arange(L, dtype=np.float32)[None, :]
    SLEEVE = (band_ * smoothstep(0, 620, xs) * smoothstep(L, L - 1500, xs)).astype(np.float32)
    YY, XX = np.mgrid[0:1080, 0:1920].astype(np.float32)
    S = build_wide(ctx)
    print('D4 chain: generations', [len(g) for g in S['gens']], 'unreached', S['n_rest'])


def render(t, ctx):
    if t < T_BAI - 1e-9:
        g = ramp(t, T_TONG, T_TONG + 0.36, 'out') if t >= T_TONG - 1e-9 else None
        f = CC.render((325, 22, 1.0), fill=0.55, ambient=0.84, warmth=0.8, gold=g, gold_stagger=0.0)
        # the breath: its head reaches the character just before '通' and rolls on across it
        u = ramp(t, T0 - 0.25, T_BAI + 0.1, 'linear')
        off = 1920 - u * 2600
        wave = 30 * np.sin((XX - off) / 860 * 2 * np.pi - t * 2.2) + 70 * np.exp(-((XX - off) / 480) ** 2)
        a = cv2.remap(SLEEVE, (XX - off).astype(np.float32), (YY + wave).astype(np.float32), cv2.INTER_LINEAR,
                      borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        f += (PC.rgb - f) * (np.clip(a, 0, 1) * 0.86)[..., None]
        return f if f.shape[1] == ctx.W else cv2.resize(f, (ctx.W, ctx.H), interpolation=cv2.INTER_AREA)
    cx, cy = start_cam(S)
    return wide_frame(S, t, cx, cy, Z_WIDE, ctx)

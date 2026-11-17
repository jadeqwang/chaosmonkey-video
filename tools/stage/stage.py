"""Stage team helpers (D1, D2, D6, D7, D8, J3, J4): canon monkey singles as ink layers, the corner mountain,
seals, and the shared numbers of the stage register. Shot scripts are authored in 1920x1080 px; every helper takes
`s` (ctx.s = W/1920) so the scripts also render at 1080p without changes.
"""
import os
import numpy as np

from tools.ink import (load_image, key_paper, resize, lay_ink, transform, place, seal, blur, ink_T, density_of)

SINGLES = 'design/characters/monkey/singles/'
SEAL_FONT = 'refs/fonts/chongxi-seal/崇羲篆体.otf'
KAI_FONT = 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'
LATIN = 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
LATIN_IT = 'refs/fonts/eb-garamond/EBGaramond-Italic[wght].ttf'
CACHE = 'work/stage/figs'
PAPER_SEED = 58          # one sheet for the whole stage (D1-D8): same fibres across the cuts


def _crop_to_ink(T, thr=0.06, pad=12):
    d = 1 - T.mean(axis=2)
    ys, xs = np.where(d > thr)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
    y1, x1 = min(T.shape[0], y1 + pad), min(T.shape[1], x1 + pad)
    return T[y0:y1, x0:x1]


def fig(name, lo=0.035):
    """A canon single (e.g. '01_liangxiang') keyed off its paper and cropped to the ink: transmittance HxWx3."""
    os.makedirs(CACHE, exist_ok=True)
    p = f'{CACHE}/{name}_{lo:.3f}.npy'
    if os.path.exists(p):
        return np.load(p)
    T = key_paper(load_image(SINGLES + name + '.jpg'), lo=lo)
    T = _crop_to_ink(T).astype(np.float32)
    np.save(p, T)
    return T


def sized(T, height, flip=False):
    """Scale a layer to `height` px (aspect kept); optional mirror."""
    if flip:
        T = T[:, ::-1].copy()
    h = max(2, int(round(height)))
    w = max(2, int(round(T.shape[1] * h / T.shape[0])))
    return resize(T, w, h)


def lay_at(frame, T, cx, base, dx=0, dy=0):
    """Lay an ink layer with its bottom centre at (cx, base)."""
    h, w = T.shape[:2]
    lay_ink(frame, T, int(round(cx - w / 2 + dx)), int(round(base - h + dy)))


def grey_ink(T, strength=1.0):
    """Monochrome ink of a given strength from a keyed layer (density scaled)."""
    d = density_of(T)
    d = d.mean(axis=2) if d.ndim == 3 else d
    return ink_T(d * strength)


def mountain(W, H, s, x=40, base=1060, height=430, remove_stone=True):
    """The small corner mountain (B_master, Ma Yuan one corner) keyed as ink, with the burst stone painted out
    (the monkey has come out of it). Returns (T_full_frame)."""
    p = f'{CACHE}/mountain.npy'
    if os.path.exists(p):
        T = np.load(p)
    else:
        img = load_image('design/plates/B_huaguoshan/B_master.png')
        T = key_paper(img, lo=0.03)
        # plate px: marks bbox x 0.08-0.38, y 0.42-0.96 of 3392x1920; stone ≈ (707, 625), ~90 px wide
        Hh, Ww = T.shape[:2]
        x0, x1, y0, y1 = int(0.04 * Ww), int(0.42 * Ww), int(0.36 * Hh), int(0.985 * Hh)
        if remove_stone:
            yy, xx = np.mgrid[0:Hh, 0:Ww]
            r = np.hypot(xx - 707, (yy - 610) * 1.15)
            k = np.clip((r - 52) / 16, 0, 1)[..., None]           # 1 outside the stone, 0 on it
            T = 1 - (1 - T) * k
        T = T[y0:y1, x0:x1].astype(np.float32)
        os.makedirs(CACHE, exist_ok=True)
        np.save(p, T)
    T = sized(T, height * s)
    out = np.ones((H, W, 3), np.float32)
    lay_ink(out, T, int(x * s), int(base * s - T.shape[0]))
    return out


SEALS = {}


def seals(s=1.0):
    """倉 (big gong) and 才 (cymbal) as 白文 impressions in seal script (仓 is not in Chong Xi; 倉 is its form)."""
    key = round(s, 3)
    if key not in SEALS:
        SEALS[key] = dict(
            cang=seal('倉', SEAL_FONT, int(150 * s), 'bai', wear=0.32, seed=7),
            cang_small=seal('倉', SEAL_FONT, int(104 * s), 'bai', wear=0.32, seed=7),
            cai=seal('才', SEAL_FONT, int(84 * s), 'bai', wear=0.3, seed=11),
            tai=seal('台', SEAL_FONT, int(84 * s), 'bai', wear=0.3, seed=13),
        )
    return SEALS[key]


def hold_index(t, cues):
    """Index of the last cue <= t (-1 before the first): hard re-posing, no in-betweens."""
    k = -1
    for i, c in enumerate(cues):
        if t >= c - 1e-6:
            k = i
    return k


def settle(t, t_hit, amp, dur=0.25, late=2 / 24):
    """A small lag-and-settle offset that starts `late` after a hit (eyes/plumes catching up a beat late)."""
    u = t - t_hit - late
    if u < 0 or u > dur:
        return 0.0
    return amp * np.exp(-u * 14) * np.cos(u * 40)


def lyrics_on(ctx):
    """The one switch for on-screen lyrics (ctx.opts['lyrics'] when the runner provides opts; env STAGE_LYRICS=0)."""
    o = getattr(ctx, 'opts', None) or {}
    return bool(o.get('lyrics', os.environ.get('STAGE_LYRICS', '1') != '0'))


# ---------------------------------------------------------------------------------------------------- D1 / D2 shared
T_GONG = 58.673                          # hook 1 crash: the stone bursts


def d1_layout(s=1.0):
    """Where the newborn stands in D1 and keeps standing in D2 (authoring px, multiply by s)."""
    return dict(cx=830, base=1012, h=820, seal=(1235, 520))


_SPL = {}


def d1_splash(W, H, s):
    """The one throw of splashed ink: thrown from the upper right across the whole sheet, landing on the gong and
    gathering into the 亮相 (canon single 01). Built once per size."""
    key = (W, H)
    if key in _SPL:
        return _SPL[key]
    from tools.ink import Paper, splash
    L = d1_layout(s)
    P = Paper(W, H, 'new', seed=PAPER_SEED)
    Tf = sized(fig('01_liangxiang'), L['h'] * s)
    # carbon-ink density from the lightest channel (exact Beer-Lambert inverse), so ink_T(dfig) * COL == Tf:
    # the splash gathers the grey figure and COL (cinnabar, ochre, gold) is laid as it settles
    from tools.ink.core import INK_K
    kk = np.asarray(INK_K, np.float32)
    dfig = (-np.log(np.clip(Tf.max(axis=2), 1e-3, 1)) / float(kk.mean())).astype(np.float32)
    COL = np.clip(Tf / np.maximum(ink_T(dfig), 1e-3), 0, 1).astype(np.float32)
    mask = (blur(dfig, 2.0 * s) > 0.10).astype(np.float32)
    h, w = mask.shape
    pos = (int(L['cx'] * s - w / 2), int(L['base'] * s - h))
    sp = splash((int(980 * s), int(470 * s)), size=int(520 * s), direction=150, seed=31, into=mask, into_pos=pos,
                paper=P, figure_density=dfig, resolve=0.42, fly=0.10, remain=0.30, fingers=18, droplets=160)
    _SPL[key] = (sp, Tf, pos, COL)
    return _SPL[key]


_RES = {}


def d1_residue(W, H, s):
    """What the throw leaves on the sheet besides the figure: the pale dried stain and spatter (ink layer, full frame)."""
    key = (W, H)
    if key not in _RES:
        sp = d1_splash(W, H, s)[0]
        d = sp.Ds * sp.remain * sp._bleed_gate(30.0)
        out = np.ones((H, W, 3), np.float32)
        lay_ink(out, ink_T(d.astype(np.float32)), int(sp.pos[0]), int(sp.pos[1]))
        _RES[key] = out
    return _RES[key]


# ---------------------------------------------------------------------------------------------------- retiming
class KeyRetime:
    """Song time -> source time from keys [(t_song, src_t), ...], linear between keys, held before the first and
    after the last. Equal src on two keys = a hold (亮相). twos=[(ta, tb)]: inside, a new source pose only every
    second SONG frame (quantised on the song's own 24 fps grid, so the twos are the cut's twos).
    hard=[t, ...]: no in-between across these song times (the key there is a jump: a re-pose/cut)."""

    def __init__(self, keys, twos=(), duration=None, fps=24):
        self.keys = sorted(keys)
        self.twos, self.duration, self.fps = list(twos), duration, fps

    def src(self, t):
        for ta, tb in self.twos:
            if ta <= t < tb:
                fr = round(t * self.fps)
                t = (fr - (fr % 2)) / self.fps
        ks = self.keys
        if t <= ks[0][0]:
            s = ks[0][1]
        elif t >= ks[-1][0]:
            s = ks[-1][1]
        else:
            for (a, sa), (b, sb) in zip(ks, ks[1:]):
                if a <= t < b:
                    s = sa + (sb - sa) * (t - a) / max(b - a, 1e-9)
                    break
        if self.duration:
            s = min(max(s, 0.0), self.duration - 0.5 / self.fps)
        return s


def clip_bbox(clip, i, thr=0.12):
    """Ink bbox (x0, y0, x1, y1) of keyed frame i of a prepared Clip, in clip px."""
    d = clip.density(i)
    ys, xs = np.where(d > thr)
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None


def heaven(W, H):
    """D_heaven_mid keyed as ink, cropped to its densest 16:9 window (x 832-4684, y 704-2870; ~74 % marks) and sized
    to the frame: the blue-green heaven as the stage for J3."""
    p = f'{CACHE}/heaven_{W}x{H}.npy'
    if os.path.exists(p):
        return np.load(p)
    img = load_image('design/plates/D_heaven/D_heaven_mid.png')
    T = key_paper(img, lo=0.03)[704:2870, 832:4684]
    T = resize(T, W, H).astype(np.float32)
    os.makedirs(CACHE, exist_ok=True)
    np.save(p, T)
    return T

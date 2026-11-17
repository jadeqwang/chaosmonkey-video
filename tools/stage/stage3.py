"""Stage team v3 helpers (yellow monkey): keyed clip layers, the medium switch with a held pose, inscriptions.
Everything else (seals, KeyRetime, clip_bbox, on_frame...) still comes from tools/stage/stage.py."""
import numpy as np

from tools.ink import resize, lay_ink
from tools.ink.core import hit_frame, on_frame
from tools.ink.medium import Mediums, medium_at
from tools.ink.video import Clip
from tools.stage.stage import KeyRetime, clip_bbox, seals, PAPER_SEED, LATIN, LATIN_IT, lyrics_on   # noqa: F401

CLIPS = 'work/ink_clips/'


def clip(tag):
    return Clip(CLIPS + tag)


def layer(cl, src, sc):
    """The keyed clip frame at source time `src`, scaled by sc (clip px -> frame px)."""
    a = cl.at(src)
    return np.clip(resize(a, int(round(cl.w * sc)), int(round(cl.h * sc))), 0, 1)


def hold_t(t, switches, hold=4):
    """Song time to use for the POSE while a medium switch is held: the switch's own first frame, so the same
    pose is shown in the other medium (REVISION_V3 §2.4). switches: [(t, medium), ...]."""
    f = hit_frame(t)
    for tc, _ in switches:
        f0 = hit_frame(tc)
        if f0 <= f < f0 + hold:
            return on_frame(tc)
    return t


def switched(med, frame, t, switches, paper, hold=4):
    """Last step of render(): the medium switch on the listed hits."""
    return med.switch(frame, t, switches, paper=paper, hold=hold)


def palm_T(W, H):
    """The Buddha's-palm plate (five finger pillars in a cloud sea) keyed as ink, sized to the frame."""
    import os
    from tools.ink import load_image, key_paper
    p = f'work/stage/figs/palm_{W}x{H}.npy'
    if os.path.exists(p):
        return np.load(p)
    T = key_paper(load_image('design/plates/D6_palm/D6_palm.jpg'), lo=0.02)
    T = resize(T, W, H).astype(np.float32)
    os.makedirs('work/stage/figs', exist_ok=True)
    np.save(p, T)
    return T


class Palm:
    """The D6 plate with depth. Either the video-model plate clip (store work/ink_clips/s3_d6pl, with its measured
    camera travel in meta 'travel': [(src_t, dx_px_at_clip_width)]) or, in code, the still cut into three depths
    (far: middle finger; mid: ring + index; near: little finger, thumb and the cloud sea) that slide past each other
    as the camera travels left, with paper-coloured mist drifting between the far and the near layers."""
    TRAVEL = 70.0                                   # near-layer shift over the shot, authoring px

    def __init__(self, ctx, clip_store='work/ink_clips/s3_d6pl'):
        import os, json
        from tools.ink import fbm, blur, density_of, ink_T
        self.ctx = ctx
        W, H, s = ctx.W, ctx.H, ctx.s
        self.clip = None
        if os.path.exists(clip_store + '/meta.json') and os.path.exists(clip_store + '/travel.json'):
            self.clip = Clip(clip_store)
            self.travel = json.load(open(clip_store + '/travel.json'))     # {'src': [...], 'dx': [...]} clip px
            return
        T = palm_T(W, H)
        xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]

        def band(a, b, soft=0.012):
            return np.clip((xx - a) / soft, 0, 1) * np.clip((b - xx) / soft, 0, 1)
        above = np.clip((0.86 - yy) / 0.05, 0, 1)                   # the cloud sea at the bottom is all 'near'
        far = band(0.222, 0.318) * above
        mid = (band(0.138, 0.228) + band(0.312, 0.408)) * above * (1 - far)
        near = np.clip(1 - far - mid, 0, 1)
        self.layers = [(1 - (1 - T) * m[..., None]).astype(np.float32) for m in (far, mid, near)]
        self.par = (0.25, 0.55, 1.0)
        self.mist = fbm(H, W * 2, 260 * s, 11, 'palm_mist', octaves=3).astype(np.float32)
        self.mist_y = (np.clip((yy - 0.42) / 0.30, 0, 1) * np.clip((0.90 - yy) / 0.08, 0, 1)).astype(np.float32)

    def lay(self, f, t, t0, t1):
        """Multiply the plate into frame f at song time t. Returns the near layer's x shift in frame px (what the
        monkey, who stands in the near layer, must ride)."""
        import cv2
        from tools.ink import lay_ink
        W, H, s = self.ctx.W, self.ctx.H, self.ctx.s
        u = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
        if self.clip is not None:
            src = 0.35 + u * (min(self.clip.duration, 5.0) - 0.6)
            a = self.clip.at(src, blend=True)
            f *= np.clip(resize(a, W, H), 0, 1)
            dx = float(np.interp(src, self.travel['src'], self.travel['dx'])) * W / self.clip.w
            return dx
        tr = self.TRAVEL * s * (u - 0.5)
        for k, (L, p) in enumerate(zip(self.layers, self.par)):
            M = np.float32([[1, 0, tr * p], [0, 1, 0]])
            Lw = cv2.warpAffine(L, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(1, 1, 1))
            if k < 2:                                    # mist (bare paper) drifting across the far layers
                off = int((u * 0.22 + 0.1 * k) * W)
                m = self.mist[:, off:off + W]
                veil = np.clip((m - 0.42) / 0.25, 0, 1) * self.mist_y * (0.75 if k == 0 else 0.5)
                Lw = 1 - (1 - Lw) * (1 - veil[..., None])
            f *= Lw
        return tr


class RingStain:
    """What the staff has written so far, and it STAYS: the running maximum of the clip's own grey dry-brush marks
    (飞白 rings and sweeps the model painted and then lets fade), with the figure itself (yellow wash, dense black)
    masked out frame by frame. Built once (ctx.cache) at half the store size; .lay(frame, src, sc, pos)."""

    def __init__(self, cl, f0, f1, step=2, keep=0.55):
        import cv2
        self.f0, self.step, self.keep, self.fps = f0, step, keep, cl.fps
        h, w = cl.h // 2, cl.w // 2
        cum = np.zeros((h, w), np.float32)
        self.maps = []
        k = max(3, int(w * 0.022)) | 1
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        for i in range(f0, min(f1, cl.n - 1) + 1, step):
            T = cv2.resize(np.clip(cl.frame(i), 0, 1), (w, h), interpolation=cv2.INTER_AREA)
            grey = 1 - T.max(axis=2)                              # carbon ink only (yellow wash has a bright R)
            sat = T.max(axis=2) - T.min(axis=2)
            body = cv2.dilate(((sat > 0.22) | (grey > 0.62)).astype(np.uint8), ker)
            d = np.where(body > 0, 0, np.clip(grey, 0, 0.6))
            cum = np.maximum(cum, cv2.GaussianBlur(d.astype(np.float32), (0, 0), 2.0))
            self.maps.append((cum * 255).astype(np.uint8))

    def density(self, src):
        i = int((src * self.fps - self.f0) / self.step)
        if i < 0:
            return None
        return self.maps[min(i, len(self.maps) - 1)].astype(np.float32) / 255 * self.keep

    def lay(self, f, src, sc, pos, cl):
        from tools.ink import ink_T
        d = self.density(src)
        if d is None:
            return
        w, h = int(round(cl.w * sc)), int(round(cl.h * sc))
        lay_ink(f, ink_T(resize(d, w, h)), int(pos[0]), int(pos[1]))


# ------------------------------------------------------------------------------------------------ D1 tail / D2
D2_TAKE = 's3_d2_kling4ff'
D2_PRE = 1445 / 24                       # D1's frame where the bows' wind-up starts (after the second switch)
D2_BOWS = [61.321, 62.205, 63.090, 63.980]          # every 2nd grid beat from "bowed": east, south, west, north
D2_NADIR = [46 / 24, 64 / 24, 79 / 24, 108 / 24]    # the take's four bows at their lowest (clip s)


def d2_retime(duration):
    """Song time -> D2 clip time, shared by D1 (its last 21 frames are the wind-up) and D2: each bow's lowest
    point lands on its beat and is held 2 frames (the stamp); the take is natively on twos."""
    keys = [(D2_PRE, 0.0)]
    for b, n in zip(D2_BOWS, D2_NADIR):
        keys += [(on_frame(b), n), (on_frame(b) + 2 / 24, n)]
    keys.append((on_frame(D2_BOWS[-1]) + 1.2, min(duration - 0.05, D2_NADIR[-1] + 0.45)))
    return KeyRetime(keys, duration=duration)

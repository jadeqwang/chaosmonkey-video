"""Chroma key (#00B140) -> RGBA with despill. key(rgb uint8 HxWx3) -> rgba."""
import numpy as np
from scipy import ndimage as ndi

def key(rgb, lo=28.0, hi=70.0, bg=None, mode='dist'):
    f = rgb.astype(np.float32)
    if bg is None:
        b = np.concatenate([rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)])
        bg = np.median(b, axis=0).astype(np.float32)
    bg = np.asarray(bg, np.float32)
    # chroma distance: green dominance over max(r,b)
    g_dom = f[..., 1] - np.maximum(f[..., 0], f[..., 2])
    bg_dom = bg[1] - max(bg[0], bg[2])
    d = np.linalg.norm(f - bg, axis=-1)
    a = np.clip((d - lo) / (hi - lo), 0, 1)
    if mode == 'sat':   # hue-based: also removes darker green ground shadows
        sat = g_dom / np.maximum(f[..., 1], 1)
        a = np.clip((0.55 - sat) / 0.35, 0, 1)
    # pixels with strong green dominance are background-ish
    a = np.minimum(a, np.clip(1 - (g_dom - 10) / (bg_dom - 40), 0, 1) ** 0.7 * 1.0 + 0.0) if False else a
    # despill: clamp green to max(r,b) where it exceeds
    out = f.copy()
    lim = np.maximum(f[..., 0], f[..., 2]) * 1.0 + 8
    spill = f[..., 1] > lim
    out[..., 1] = np.where(spill, lim, f[..., 1])
    # edge pixels: mix toward foreground by un-premultiplying against bg
    m = (a > 0) & (a < 1)
    aa = np.maximum(a, 1e-3)[..., None]
    un = (f - (1 - aa) * bg) / aa
    out = np.where(m[..., None], np.clip(un, 0, 255), out)
    out[..., 1] = np.where(m, np.minimum(out[..., 1], np.maximum(out[..., 0], out[..., 2]) + 8), out[..., 1])
    return np.dstack([np.clip(out, 0, 255).astype(np.uint8), (a * 255).astype(np.uint8)])

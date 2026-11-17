"""Small DSP + loudness kit for the Chaos Monkey sound layer (copied from halys-video tools/audio/sfx/dsp.py, itself ported from
holdfire tools/audio/sfx.py): filters, fades, pan, synthetic reverb, BS.1770-4 K-weighting, momentary/integrated loudness, true peak."""
import io
import os
import subprocess

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, resample_poly, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SR = 48000


def N(t):
    return int(round(t * SR))


def tt(d):
    return np.arange(N(d)) / SR


def db2a(db):
    return 10.0 ** (np.asarray(db, dtype=np.float64) / 20.0)


def a2db(a):
    return 20.0 * np.log10(np.maximum(np.asarray(a, dtype=np.float64), 1e-12))


def _sos(kind, f, order):
    return butter(order, f, kind, fs=SR, output="sos")


def lp(y, f, order=4):
    return sosfilt(_sos("low", f, order), y, axis=-1)


def hp(y, f, order=4):
    return sosfilt(_sos("high", f, order), y, axis=-1)


def bp(y, lo, hi, order=4):
    return sosfilt(_sos("band", [lo, hi], order), y, axis=-1)


def peq(y, f0, gain_db, q=1.0):
    """RBJ peaking EQ (a presence dip keeps the layer out of the voice's 1-5 kHz)."""
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w), 1 - al / A])
    return lfilter(b / a[0], a / a[0], y, axis=-1)


def ramp(t, a, b):
    return np.clip((np.asarray(t, dtype=np.float64) - a) / (b - a), 0.0, 1.0)


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def fades(y, a=0.0, r=0.0):
    """Raised-cosine fade in/out (seconds) on the last axis."""
    y = np.array(y, dtype=np.float64, copy=True)
    n = y.shape[-1]
    if a > 0:
        k = min(n, max(2, N(a)))
        y[..., :k] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(k) / k)
    if r > 0:
        k = min(n, max(2, N(r)))
        y[..., n - k:] *= 0.5 + 0.5 * np.cos(np.pi * (np.arange(k) + 1) / k)
    return y


def stereo(y):
    return y if y.ndim == 2 else np.stack([y, y])


def mono(y):
    return y.mean(0) if y.ndim == 2 else y


def pan(y, p):
    """Constant-power pan (p in [-1, 1], scalar or per-sample); mono in -> (2, n); stereo in -> width-preserving balance."""
    th = (np.asarray(p, dtype=np.float64) + 1) * np.pi / 4
    if y.ndim == 2:
        return np.stack([y[0] * np.cos(th), y[1] * np.sin(th)]) * np.sqrt(2)
    return np.stack([y * np.cos(th), y * np.sin(th)]) * np.sqrt(2)


def narrow(y, width):
    """Stereo width 0 (mono) .. 1 (as is)."""
    y = stereo(y)
    m, s = (y[0] + y[1]) / 2, (y[0] - y[1]) / 2 * width
    return np.stack([m + s, m - s])


def add_at(dst, y, i):
    y = stereo(y)
    a, b = max(0, i), min(dst.shape[1], i + y.shape[1])
    if b > a:
        dst[:, a:b] += y[:, a - i:b - i]


def white(n, rng):
    return rng.standard_normal(n)


def pink(n, rng):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / np.sqrt(np.maximum(f, 20.0))
    y = np.fft.irfft(X, n)
    return y / (np.sqrt(np.mean(y ** 2)) + 1e-12)


def brown(n, rng):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / np.maximum(f, 15.0)
    y = np.fft.irfft(X, n)
    return y / (np.sqrt(np.mean(y ** 2)) + 1e-12)


def ir(dur, rt60, lp_hz=8000, hp_hz=150, seed=0, predelay=0.0):
    """Synthetic stereo reverb impulse response (decaying filtered noise), unit energy per channel."""
    rng = np.random.default_rng(seed)
    n = N(dur)
    t = np.arange(n) / SR
    env = 10 ** (-3 * t / rt60) * (1 - np.exp(-t / 0.004))
    ch = [hp(lp(rng.standard_normal(n) * env, lp_hz, 2), hp_hz, 2) for _ in range(2)]
    pd = np.zeros(N(predelay))
    out = np.stack([np.concatenate([pd, c]) for c in ch])
    return out / np.sqrt(np.sum(out ** 2) / 2)


def reverb(y, impulse, wet_db=-12.0, dry=1.0):
    y = stereo(y)
    w = np.stack([fftconvolve(y[0], impulse[0]), fftconvolve(y[1], impulse[1])])
    out = db2a(wet_db) * w
    out[:, :y.shape[1]] += dry * y
    return out


def peak_db(y):
    return float(a2db(np.max(np.abs(y))))


def norm(y, peak=1.0):
    return y * (peak / (np.max(np.abs(y)) + 1e-12))


# ------------------------------------------------------------------------------------------------ loudness (BS.1770-4)
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def kpow(y):
    """K-weighted power summed over channels (1-D, per sample)."""
    y = stereo(y)
    k = lfilter(*_K2, lfilter(*_K1, y, axis=-1), axis=-1)
    return np.sum(k * k, axis=0)


class Momentary:
    """Loudness in a window (default 400 ms, centred) of a power array whose sample 0 sits at time t0."""

    def __init__(self, p, t0=0.0):
        self.cs = np.concatenate([[0.0], np.cumsum(p, dtype=np.float64)])
        self.t0, self.n = t0, len(p)

    def __call__(self, times, win=0.4):
        c = np.round((np.asarray(times) - self.t0) * SR).astype(np.int64)
        h = N(win) // 2
        a, b = np.clip(c - h, 0, self.n), np.clip(c + h, 0, self.n)
        e = (self.cs[b] - self.cs[a]) / (2 * h)
        return -0.691 + 10 * np.log10(e + 1e-20)


def integrated_lufs(y):
    p = kpow(y)
    blk, hop = N(0.4), N(0.1)
    cs = np.concatenate([[0.0], np.cumsum(p, dtype=np.float64)])
    st = np.arange(0, len(p) - blk + 1, hop)
    z = (cs[st + blk] - cs[st]) / blk
    lk = -0.691 + 10 * np.log10(z + 1e-20)
    g = z[lk > -70]
    if g.size == 0:
        return -200.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = z[(lk > -70) & (lk > rel)]
    return float(-0.691 + 10 * np.log10(g2.mean()))


def true_peak_db(y, chunk_s=10.0):
    y = stereo(y)
    n, c, pad = y.shape[1], N(chunk_s), 256
    m = 0.0
    for a in range(0, n, c):
        s0, s1 = max(0, a - pad), min(n, a + c + pad)
        up = resample_poly(y[:, s0:s1], 4, 1, axis=-1)
        lo, hi = (a - s0) * 4, (min(n, a + c) - s0) * 4
        m = max(m, float(np.max(np.abs(up[:, lo:hi]))))
    return float(a2db(m))


def ebur128(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    out = {}
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("I:"):
            out["integrated_lufs"] = float(s.split()[1])
        elif s.startswith("Peak:"):
            out["true_peak_dbtp"] = float(s.split()[1])
        elif s.startswith("LRA:"):
            out["lra_lu"] = float(s.split()[1])
    return out


# ------------------------------------------------------------------------------------------------ I/O
def load(path):
    """Any audio file -> float64 (2, n) at 48 kHz (ffmpeg decode for mp3)."""
    if path.endswith(".wav"):
        y, sr = sf.read(path, always_2d=True, dtype="float64")
        y = y.T
        if sr != SR:
            y = resample_poly(y, SR, sr, axis=-1)
    else:
        wav = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-ac", "2", "-ar", str(SR),
                              "-c:a", "pcm_f32le", "-f", "wav", "pipe:1"], check=True, capture_output=True).stdout
        y, _ = sf.read(io.BytesIO(wav), always_2d=True, dtype="float64")
        y = y.T
    return stereo(y) if y.shape[0] == 2 else np.stack([y[0], y[0]])


def limit(y, crest_db=10.0, look=0.004):
    """Peak limiter for a bed on the layer (never the song): peaks held to crest_db over the bed's own RMS, 4 ms look-ahead
    (max filter), gain smoothed over 8 ms. A clash 30 dB over the bed would otherwise set the bed's level by its peak cap."""
    from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d
    y = stereo(y)
    ceil = np.sqrt(np.mean(y ** 2)) * db2a(crest_db)
    env = maximum_filter1d(np.max(np.abs(y), 0), 2 * N(look) + 1)
    g = np.minimum(1.0, ceil / (env + 1e-12))
    g = uniform_filter1d(minimum_filter1d(g, 2 * N(look) + 1), N(0.008))
    return y * g

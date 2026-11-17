"""Envelopes for the Chaos Monkey track -> work/audio/env.npz  (5 ms frames: frame k = k * 0.005 s) and
work/audio/loudness.npz (10 Hz momentary / short-term loudness, BS.1770 K-weighting).

Per source (mix, vocals, vocals_demucs, instrumental, drums, bass, other):
  onset_<src>   librosa spectral-flux onset strength (128 mel, lag 1), hop 240 @ 48 kHz
  rms_<src>     RMS in dBFS, 10 ms window
Band energies of the mix (dB): low 20-150, mid 150-2500, high 2500-16000, air 6000-16000, sub 20-60.
Loudness: momentary (400 ms) and short-term (3 s) LUFS at 10 Hz; integrated LUFS (gated, pyloudnorm).

    .venv/bin/python tools/audio/features.py
"""
import os, numpy as np, soundfile as sf, librosa, scipy.signal as ss, pyloudnorm

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W = os.path.join(ROOT, 'work')
SR, HOP = 48000, 240
SRC = dict(mix='audio/song.wav', vocals='stems/vocals.wav', vocals_demucs='stems/vocals_demucs.wav', lead='stems/lead.wav', backing='stems/backing.wav',
           instrumental='stems/instrumental.wav', drums='stems/drums.wav', bass='stems/bass.wav', other='stems/other.wav')


def db(x): return 20 * np.log10(x + 1e-10)


def rms_env(y, win):
    return np.sqrt(np.maximum(np.convolve(y.astype(np.float64) ** 2, np.ones(win) / win, mode='same'), 0))[::HOP]


out = {}
for k, p in SRC.items():
    y, sr = sf.read(os.path.join(W, p), dtype='float32'); assert sr == SR
    m = y.mean(1)
    out['onset_' + k] = librosa.onset.onset_strength(y=m, sr=SR, hop_length=HOP, lag=1, max_size=1, n_mels=128)
    out['rms_' + k] = db(rms_env(m, 480))
    if k == 'mix':
        for nm, (lo, hi) in dict(sub=(20, 60), low=(20, 150), mid=(150, 2500), high=(2500, 16000), air=(6000, 16000)).items():
            sos = ss.butter(4, [lo, hi], btype='band', fs=SR, output='sos')
            out['band_' + nm] = db(rms_env(ss.sosfilt(sos, m.astype(np.float64)), 480))
        mixst = y.astype(np.float64)
        # band-limited spectral flux (log-magnitude rise) of the mix -> work/audio/bandflux.npz (low = kick/boom/sub)
        S = np.abs(librosa.stft(m, n_fft=4096, hop_length=HOP)); f = librosa.fft_frequencies(sr=SR, n_fft=4096)
        def flux(lo, hi):
            X = np.log1p(100 * S[(f >= lo) & (f < hi)]); return np.r_[0, np.maximum(np.diff(X, axis=1), 0).sum(0)]
        np.savez(os.path.join(W, 'audio/bandflux.npz'), T=np.arange(S.shape[1]) * HOP / SR,
                 low=flux(20, 120), mid=flux(120, 1000), high=flux(2000, 12000))
    print(k, len(out['onset_' + k]))
n = min(len(v) for v in out.values())
out = {k: v[:n] for k, v in out.items()}
out['T'] = np.arange(n) * HOP / SR
np.savez(os.path.join(W, 'audio/env.npz'), **out)

# ---- loudness (BS.1770 K-weighting: high shelf + high pass, 48 kHz coefficients)
b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
kw = ss.lfilter(b2, a2, ss.lfilter(b1, a1, mixst, axis=0), axis=0)
p = (kw ** 2).sum(1)                                            # channel-summed power (L, R weights 1)
cs = np.r_[0, np.cumsum(p)]
t10 = np.arange(0, len(p) / SR, 0.1)


def lufs(win):
    a = np.clip(((t10 - win / 2) * SR).astype(int), 0, len(p)); b = np.clip(((t10 + win / 2) * SR).astype(int), 0, len(p))
    return -0.691 + 10 * np.log10((cs[b] - cs[a]) / np.maximum(b - a, 1) + 1e-12)


mom, st = lufs(0.4), lufs(3.0)
integ = pyloudnorm.Meter(SR).integrated_loudness(mixst)
np.savez(os.path.join(W, 'audio/loudness.npz'), t=t10, momentary=mom, short_term=st, integrated=integ)
print(f'integrated {integ:.1f} LUFS; momentary max {mom.max():.1f} LUFS')

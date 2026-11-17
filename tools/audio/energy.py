"""Energy / stereo width / brightness -> work/audio/energy.npz (fine, 10 ms hop, 50 ms window) and the 0.5 s table.
  rms_<src> dB          RMS (mono sum) of mix and stems
  width                 side/mid energy ratio S/M in dB (mix): -inf = mono; plus lr_corr (L/R correlation, 1 = mono)
  centroid, rolloff85   spectral centroid / 85 % rolloff (Hz) of the mix (and of the instrumental)
  hf_db                 energy above 4 kHz minus total (dB): drops when a low-pass filter closes
"""
import os, numpy as np, soundfile as sf, librosa
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = os.path.join(ROOT, 'work')
SR = 48000; HOP = 480; WIN = 2400
SRC = dict(mix='audio/song.wav', vocals='stems/vocals.wav', instrumental='stems/instrumental.wav', drums='stems/drums.wav',
           bass='stems/bass.wav', other='stems/other.wav', lead='stems/lead.wav', backing='stems/backing.wav')
def frames(x, hop, win):
    n = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None] + hop * np.arange(n)[:, None]; return x[idx]
def db(p): return 10 * np.log10(p + 1e-12)
out = {}
for k, p in SRC.items():
    y, _ = sf.read(os.path.join(W, p), dtype='float32')
    for hop, win, tag in ((HOP, WIN, ''), (24000, 24000, '_h')):
        m = y.mean(1); F = frames(m, hop, win); out['rms_' + k + tag] = db((F.astype(np.float64) ** 2).mean(1))
        if k in ('mix', 'instrumental'):
            Mi = frames((y[:, 0] + y[:, 1]) / 2, hop, win).astype(np.float64); Si = frames((y[:, 0] - y[:, 1]) / 2, hop, win).astype(np.float64)
            out[k + '_width' + tag] = db((Si ** 2).mean(1)) - db((Mi ** 2).mean(1))
            L = frames(y[:, 0], hop, win).astype(np.float64); R = frames(y[:, 1], hop, win).astype(np.float64)
            out[k + '_lrcorr' + tag] = (L * R).sum(1) / np.sqrt((L ** 2).sum(1) * (R ** 2).sum(1) + 1e-12)
            S = np.abs(librosa.stft(m, n_fft=4096, hop_length=hop, center=False)) ** 2; f = librosa.fft_frequencies(sr=SR, n_fft=4096)
            tot = S.sum(0) + 1e-12
            out[k + '_centroid' + tag] = (f[:, None] * S).sum(0) / tot
            c = np.cumsum(S, 0) / tot; out[k + '_rolloff85' + tag] = f[np.argmax(c >= 0.85, axis=0)]
            out[k + '_hf_db' + tag] = db(S[f >= 4000].sum(0)) - db(tot)
n = min(len(v) for k, v in out.items() if not k.endswith('_h')); nh = min(len(v) for k, v in out.items() if k.endswith('_h'))
o = {k: (v[:nh] if k.endswith('_h') else v[:n]) for k, v in out.items()}
o['T'] = (np.arange(n) * HOP + WIN / 2) / SR; o['T_h'] = np.arange(nh) * 0.5
np.savez(os.path.join(W, 'audio/energy.npz'), **o); print('ok', n, nh)

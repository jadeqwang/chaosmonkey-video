"""Singer ID (mom vs child) for the new vocal stem.
Train: frames of the spliced-take stems (chaosmonkey-song/spliced/stems; different render, same Suno voices) where only
one of mom/child is active (other < -45 dBFS, self > -35 dBFS). Features: 20 MFCC (+ median F0 from pyin is reported
separately). Classifier: LDA (numpy, two classes). Apply: per 20 ms frame on work/stems/vocals.wav; outputs
work/audio/singer.npz {T, p_child, active, f0}. Cross-validated on held-out halves of the training song.
"""
import os, numpy as np, soundfile as sf, librosa
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SD = '/home/jade/Documents/chaosmonkey-song/spliced/stems/'
SR = 16000; HOP = 320
def load(p):
    y, sr = sf.read(p); y = y.mean(1) if y.ndim > 1 else y
    return librosa.resample(y, orig_sr=sr, target_sr=SR, res_type='soxr_hq')
def feats(y):
    M = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, n_fft=1024, hop_length=HOP, n_mels=64, fmax=8000)
    r = librosa.feature.rms(y=y, frame_length=1024, hop_length=HOP)[0]
    return M.T, 20 * np.log10(r + 1e-9)
mom, kid = load(SD + 'mom vocal.wav'), load(SD + 'child vocal.wav')
Fm, Rm = feats(mom); Fk, Rk = feats(kid); n = min(len(Fm), len(Fk))
selm = (Rm[:n] > -35) & (Rk[:n] < -45); selk = (Rk[:n] > -35) & (Rm[:n] < -45)
X = np.r_[Fm[:n][selm], Fk[:n][selk]]; Y = np.r_[np.zeros(selm.sum()), np.ones(selk.sum())]
tt = np.r_[np.where(selm)[0], np.where(selk)[0]] * HOP / SR
print('train frames mom', selm.sum(), 'child', selk.sum())
def lda(X, Y):
    mu0, mu1 = X[Y == 0].mean(0), X[Y == 1].mean(0)
    Sw = np.cov(X[Y == 0].T) + np.cov(X[Y == 1].T) + 1e-3 * np.eye(X.shape[1])
    w = np.linalg.solve(Sw, mu1 - mu0); c = w @ (mu0 + mu1) / 2
    s = X @ w - c; sd = s.std(); return w, c, sd
# CV: train on first half of the song, test on second, and vice versa
for a, b in ((tt < 118, tt >= 118), (tt >= 118, tt < 118)):
    w, c, sd = lda(X[a], Y[a]); pr = (X[b] @ w - c) > 0
    print('cv frame acc', round((pr == Y[b]).mean(), 3), ' (mom acc', round((~pr[Y[b] == 0]).mean(), 3), 'child acc', round(pr[Y[b] == 1].mean(), 3), ')')
w, c, sd = lda(X, Y)
v = load(os.path.join(ROOT, 'work/stems/vocals.wav')); Fv, Rv = feats(v)
s = Fv @ w - c; p = 1 / (1 + np.exp(-2 * s / sd))
f0, vf, _ = librosa.pyin(v, fmin=110, fmax=900, sr=SR, hop_length=HOP, frame_length=2048)
n = min(len(p), len(f0))
np.savez(os.path.join(ROOT, 'work/audio/singer.npz'), T=np.arange(n) * HOP / SR, p_child=p[:n], rms=Rv[:n], f0=np.where(vf[:n], f0[:n], np.nan))
# reference F0 of the training stems
for nm, y, sel in (('mom', mom, selm), ('child', kid, selk)):
    f, vv, _ = librosa.pyin(y[:SR * 120], fmin=110, fmax=900, sr=SR, hop_length=HOP, frame_length=2048)
    m = min(len(f), len(sel)); ok = vv[:m] & sel[:m]
    print(nm, 'median F0 (first 120 s, solo frames)', librosa.hz_to_note(np.nanmedian(f[:m][ok])), round(np.nanmedian(f[:m][ok])))

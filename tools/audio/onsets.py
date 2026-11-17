"""Percussive onsets + descriptors -> work/audio/onsets.json
Onsets: peaks of spectral-flux onset strength on the drums stem (5 ms hop) AND on the 'other' stem (gongs/crashes and
suona often land in 'other'), merged within 25 ms. Each onset time is refined to the sample-level attack on the drums
(or other) stem: first 1 ms frame exceeding the preceding 30 ms floor by 12 dB, searched within -30..+15 ms.
Descriptors (drums stem unless noted), dB energies in 40 ms after the onset minus 40 ms before, per band:
  sub 20-60, low 60-150, lmid 150-500, mid 500-2000, hi 2000-6000, air 6000-16000
  hf_decay: time for 4-16 kHz envelope to fall 20 dB below its post-onset peak (cap 1.5 s) (long = cymbal/crash/gong)
  lo_decay: same for 40-400 Hz
  other_* : same bands for the 'other' stem; mix_flux: mix onset strength / 99.5 pct (0-1) = strength
"""
import json, os, numpy as np, soundfile as sf, librosa, scipy.signal as ss
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = os.path.join(ROOT, 'work')
SR = 48000; HOP = 240
def ld(p): y, _ = sf.read(os.path.join(W, p), dtype='float64'); return y.mean(1)
D, O, M = ld('stems/drums.wav'), ld('stems/other.wav'), ld('audio/song.wav')
B = dict(sub=(20, 60), low=(60, 150), lmid=(150, 500), mid=(500, 2000), hi=(2000, 6000), air=(6000, 16000), hf=(4000, 16000), lo=(40, 400))
def benv(x, lo, hi, w=240):
    sos = ss.butter(4, [lo, hi], btype='band', fs=SR, output='sos'); z = ss.sosfilt(sos, x) ** 2
    return 10 * np.log10(np.convolve(z, np.ones(w) / w, 'same')[::HOP // 2] + 1e-12)   # 2.5 ms grid
ED = {k: benv(D, *v) for k, v in B.items()}; EO = {k: benv(O, *v) for k, v in B.items() if k not in ('hf', 'lo')}
EOh = benv(O, 4000, 16000)
def onset_env(x): return librosa.onset.onset_strength(y=x.astype(np.float32), sr=SR, hop_length=HOP, lag=1, max_size=3, n_mels=128)
od, oo, om = onset_env(D), onset_env(O), onset_env(M)
def peaks(o, rel):
    thr = np.convolve(o, np.ones(41) / 41, 'same') + rel * np.percentile(o, 99)
    p, _ = ss.find_peaks(o, height=thr, distance=8)        # >= 40 ms apart
    return p
pd_, po = peaks(od, 0.06), peaks(oo, 0.12)
cand = sorted([(p * HOP / SR, 'd') for p in pd_] + [(p * HOP / SR, 'o') for p in po])
merged = []
for t, s in cand:
    if merged and t - merged[-1][0] < 0.025: merged[-1] = (merged[-1][0], merged[-1][1] + s); continue
    merged.append((t, s))
ref = np.percentile(om, 99.5); refd = np.percentile(od, 99.5)
def attack(x, t):
    a = int((t - 0.06) * SR); seg = np.abs(x[a:int((t + 0.03) * SR)])
    nf = len(seg) // 48; pk = seg[:nf * 48].reshape(nf, 48).max(1)
    for i in range(30, nf):
        fl = np.median(pk[i - 30:i]) + 1e-9
        if pk[i] > fl * 4 and i * 48 / SR >= 0.03: return round((a + i * 48 + int(np.argmax(seg[i * 48:(i + 1) * 48] > fl * 4))) / SR, 4)
    return round(t, 4)
def decay(e, j, cap=1.5):
    k = j + int(0.06 / 0.0025); pk = e[j:k].max(); pj = j + int(np.argmax(e[j:k]))
    end = min(len(e), pj + int(cap / 0.0025)); below = np.where(e[pj:end] < pk - 20)[0]
    return round((below[0] if len(below) else end - pj) * 0.0025, 3)
out = []
for t, s in merged:
    x = D if 'd' in s else O
    ta = attack(x, t); j = int(ta / 0.0025)
    pre = slice(max(0, j - 16), j); post = slice(j, j + 16)
    rec = dict(t=ta, src=s, strength=round(float(min(1, om[max(0, int(t * SR / HOP) - 6):int(t * SR / HOP) + 6].max() / ref)), 3),
               dstr=round(float(min(1, od[max(0, int(t * SR / HOP) - 4):int(t * SR / HOP) + 4].max() / refd)), 3))
    for k in ('sub', 'low', 'lmid', 'mid', 'hi', 'air'):
        rec['d_' + k] = round(float(ED[k][post].max()), 1); rec['dr_' + k] = round(float(ED[k][post].max() - np.median(ED[k][pre])), 1)
        rec['o_' + k] = round(float(EO[k][post].max()), 1)
    rec['hf_decay'] = decay(ED['hf'], j); rec['lo_decay'] = decay(ED['lo'], j); rec['o_hf_decay'] = decay(EOh, j)
    out.append(rec)
json.dump(out, open(os.path.join(W, 'audio/onsets.json'), 'w'))
print(len(out), 'onsets')

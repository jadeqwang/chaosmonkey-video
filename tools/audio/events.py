"""Beat grid + classified hits + transitions -> work/audio/events.json
Beats: beat_this (mix; instrumental agrees on 98% of beats within 30 ms) refined: each beat is moved to the nearest
  drums-stem onset (dstr >= 0.3) within +-35 ms if there is one ('snapped'), else kept at a local robust linear fit of
  neighbouring beats (removes beat_this's 20 ms frame quantisation). Downbeats: beat_this downbeats mapped to refined beats.
Hits (from onsets.json, drums+other stems): class heuristics (all class guesses are 'low'/'medium' confidence):
  gong_crash  long 4-16 kHz tail (>= 0.4 s) AND the drums-stem 6-16 kHz level jumps >= 10 dB above its median over the
              preceding 1 s, AND its 6-16 kHz peak is >= 6 dB above every onset in the preceding 0.6 s (accented, not part of a hat/ride
              pattern); jump threshold 10 dB (dominant; hi-hat/ride
              patterns are not counted) and dstr/strength >= 0.5
  low_drum    isolated (no other onset within 0.6 s) low tonal hit (low band > -26 dB, short HF)
  kick        low (60-150 Hz) >= mid band + 3 dB and > -26 dB
  snare       150-2000 Hz body > -24 dB and 2-6 kHz > -42 dB, short tail
  clapper     bright, bodiless click: 2-6 kHz > 150-500 Hz - 3 dB, 150-500 Hz < -38 dB, 60-150 Hz < -40 dB, tail < 80 ms
  perc        anything else
Chops: full-band holes in the mix (5 ms RMS falls >= 18 dB below the median of the preceding 150 ms, lasting 15-150 ms),
  clustered (gap <= 0.6 s) into stutter clusters. Silences: mix < -50 dBFS or < local - 30 dB for > 150 ms (also listed: > 30 ms).
Accelerandos: runs of >= 5 consecutive drum onsets (dstr >= 0.15) with IOI <= 0.5 s whose IOI decreases (Spearman <= -0.6)
  and last IOI <= 0.75 x first IOI.
Suona phrases (low confidence): 'other' stem, pyin F0 300-1400 Hz, voiced-prob > 0.6 and 1-4 kHz band > -40 dB,
  sustained notes; phrases = voiced runs >= 0.5 s, gaps < 0.2 s merged.
Risers: 4-16 kHz band of the instrumental rising >= 9 dB over 1-6 s (linear fit r >= 0.85).
Sub drops: bass stem 20-60 Hz rises >= 18 dB to > -30 dB and holds >= 0.3 s.
Width / filter: instrumental L/R correlation and >4 kHz share; transitions = steepest change of the 0.25 s-smoothed curve.
"""
import json, os, numpy as np, soundfile as sf, scipy.signal as ss, librosa
from scipy.stats import spearmanr
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = os.path.join(ROOT, 'work')
SR = 48000
O = json.load(open(os.path.join(W, 'audio/onsets.json')))
BT = json.load(open(os.path.join(W, 'audio/beat_this.json')))
E = np.load(os.path.join(W, 'audio/energy.npz')); T = E['T']
DUR = 11439360 / SR
OD = np.array([o['t'] for o in O if o['dstr'] >= 0.3 and 'd' in o['src']])
# ---------------- beats
b = np.array(BT['beats']); fit = b.copy()
for i in range(len(b)):
    lo, hi = max(0, i - 6), min(len(b), i + 7); k = np.arange(lo, hi)
    p = np.polyfit(k, b[lo:hi], 1); r = b[lo:hi] - np.polyval(p, k)
    good = np.abs(r) < 0.03
    if good.sum() >= 4: p = np.polyfit(k[good], b[lo:hi][good], 1)
    fit[i] = np.polyval(p, i)
beats = []
for i, t in enumerate(fit):
    j = np.argmin(np.abs(OD - t)) if len(OD) else None
    if j is not None and abs(OD[j] - t) <= 0.035: beats.append(dict(t=round(float(OD[j]), 3), src='onset', raw=round(b[i], 3)))
    else: beats.append(dict(t=round(float(t), 3), src='fit', raw=round(b[i], 3)))
bt = np.array([x['t'] for x in beats])
down = sorted(set(int(np.argmin(np.abs(b - d))) for d in BT['downbeats']))
# ---------------- hits
def cls(o, iso):
    if (o['hf_decay'] >= 0.4 or o['o_hf_decay'] >= 0.9) and max(o['dstr'], o['strength']) >= 0.5 and o['d_air'] > -45 and air_jump(o['t']) >= 10 and dominance(o['t']) >= 6: return 'gong_crash'
    if iso and o['d_low'] > -26 and o['hf_decay'] < 0.15: return 'low_drum'
    if o['d_low'] > -26 and o['d_low'] >= o['d_mid'] + 3: return 'kick'
    if o['d_hi'] >= o['d_lmid'] - 3 and o['d_lmid'] < -38 and o['d_low'] < -40 and o['hf_decay'] < 0.08: return 'clapper'
    if max(o['d_lmid'], o['d_mid']) > -24 and o['d_hi'] > -42 and o['hf_decay'] < 0.3: return 'snare'
    return 'perc'
yd_, _ = sf.read(os.path.join(W, 'stems/drums.wav')); yd_ = yd_.mean(1)
_sos = ss.butter(4, [6000, 16000], btype='band', fs=SR, output='sos'); AIR = ss.sosfilt(_sos, yd_) ** 2
AIR = 10 * np.log10(np.convolve(AIR, np.ones(480) / 480, 'same')[::240] + 1e-12)   # 5 ms
def air_jump(t):
    j = int(t / 0.005); pre = np.median(AIR[max(0, j - 200):max(1, j - 4)]); return float(AIR[j:j + 20].max() - pre)
def air_pk(t): j = int(t / 0.005); return float(AIR[j:j + 20].max())
def dominance(t):
    # loudness of the 6-16 kHz peak vs every onset in the preceding 0.6 s (their windows truncated before t)
    j = int(t / 0.005); me = float(AIR[j:j + 20].max()); oth = []
    for u in ts:
        if t - 0.6 <= u < t - 0.01:
            a_, b_ = int(u / 0.005), min(int(u / 0.005) + 20, j - 1)
            if b_ > a_: oth.append(float(AIR[a_:b_].max()))
    return me - (max(oth) if oth else -120)
ts = np.array([o['t'] for o in O]); hits = []
TSH = np.array([o['t'] for o in O if o['dstr'] >= 0.15 or o['strength'] >= 0.4])
for o in O:
    if o['dstr'] < 0.15 and o['strength'] < 0.4: continue
    nb = np.abs(TSH - o['t']); iso = np.sum((nb > 0.001) & (nb < 0.6)) == 0
    c = cls(o, iso)
    hits.append(dict(t=o['t'], cls=c, air_jump_db=round(air_jump(o['t']), 1), strength=round(max(o['dstr'], o['strength']) if c in ('gong_crash', 'low_drum') else o['dstr'], 2),
                     confidence='medium' if c in ('gong_crash', 'low_drum', 'kick') else 'low'))
# ---------------- accelerandos (on drum onsets, incl. weak ones): IOIs non-increasing (each <= 1.1 x previous),
# >= 3 strict decreases (< 0.9 x previous), first/last IOI >= 1.6, run >= 5 onsets and >= 0.6 s
DO = [o for o in O if o['dstr'] >= 0.1 and 'd' in o['src']]
acc = []; t_ = np.array([o['t'] for o in DO]); i = 0
while i < len(t_) - 5:
    j = i + 1; dec = 0
    while j + 1 < len(t_):
        a_, b_ = t_[j] - t_[j - 1], t_[j + 1] - t_[j]
        if b_ > 1.1 * a_ or b_ < 0.025: break
        if b_ < 0.9 * a_: dec += 1
        j += 1
    ioi = np.diff(t_[i:j + 1])
    if j - i + 1 >= 5 and dec >= 3 and ioi[0] / ioi[-1] >= 1.6 and t_[j] - t_[i] >= 0.6 and ioi[0] <= 0.6:
        acc.append(dict(start=round(t_[i], 3), peak=round(t_[j], 3), n=j - i + 1, first_ioi=round(ioi[0], 3), last_ioi=round(ioi[-1], 3),
                        clicks=[round(x, 3) for x in t_[i:j + 1]],
                        classes=[next((h['cls'] for h in hits if abs(h['t'] - x) < 1e-6), 'perc') for x in t_[i:j + 1]]))
        i = j
    else: i += 1
# ---------------- chops & silences
y, _ = sf.read(os.path.join(W, 'audio/song.wav')); m = y.mean(1); h = 240
n = len(m) // h; r = 10 * np.log10((m[:n * h].reshape(n, h) ** 2).mean(1) + 1e-12); tt = np.arange(n) * h / SR
pre = np.array([np.median(r[max(0, k - 30):k]) if k else r[0] for k in range(n)])
q = r < pre - 18; chops = []; k = 0
while k < n:
    if q[k]:
        j = k
        while j < n and r[j] < pre[k] - 15: j += 1
        d = (j - k) * h / SR
        if 0.015 <= d <= 0.15 and pre[k] > -40: chops.append(dict(start=round(tt[k], 3), end=round(tt[j], 3), depth_db=round(float(pre[k] - r[k:j].min()), 1)))
        k = max(j, k + 1)
    else: k += 1
clusters = []
for c in chops:
    if clusters and c['start'] - clusters[-1]['end'] <= 0.6: clusters[-1]['end'] = c['end']; clusters[-1]['n'] += 1; clusters[-1]['times'].append(c['start'])
    else: clusters.append(dict(start=c['start'], end=c['end'], n=1, times=[c['start']]))
loc = np.array([np.median(r[max(0, k - 200):k + 200]) for k in range(0, n, 20)]).repeat(20)[:n]
qs = (r < -50) | (r < loc - 30); sil = []; k = 0
while k < n:
    if qs[k]:
        j = k
        while j < n and qs[j]: j += 1
        if (j - k) * h / SR >= 0.03: sil.append(dict(start=round(tt[k], 3), end=round(tt[j], 3), dur=round((j - k) * h / SR, 3), max_db=round(float(r[k:j].max()), 1)))
        k = j
    else: k += 1
# ---------------- suona phrases (low confidence): harmonic part (HPSS) of the 'other' stem, 700-5000 Hz band energy,
# 50 ms smoothing; phrase = runs above (global 60th percentile) lasting >= 0.4 s, gaps < 0.12 s merged.
yo, _ = sf.read(os.path.join(W, 'stems/other.wav')); mo = librosa.resample(yo.mean(1), orig_sr=SR, target_sr=16000)
Sx = librosa.stft(mo, n_fft=1024, hop_length=160); H, P = librosa.decompose.hpss(Sx, margin=2.0)
fq = librosa.fft_frequencies(sr=16000, n_fft=1024); hb_ = (np.abs(H[(fq >= 700) & (fq <= 5000)]) ** 2).sum(0)
he = 10 * np.log10(np.convolve(hb_, np.ones(5) / 5, 'same') + 1e-12); thr = np.percentile(he, 60)
v = he > thr; seg = []; k = 0
while k < len(v):
    if v[k]:
        j = k
        while j < len(v) and (v[j] or v[j:j + 12].any()): j += 1
        if (j - k) * 0.01 >= 0.4: seg.append(dict(start=round(k * 0.01, 2), end=round(j * 0.01, 2), level_db=round(float(np.median(he[k:j]) - thr), 1)))
        k = j
    else: k += 1
# ---------------- risers
yi, _ = sf.read(os.path.join(W, 'stems/instrumental.wav')); mi = yi.mean(1)
sos = ss.butter(4, [4000, 16000], btype='band', fs=SR, output='sos'); hb = ss.sosfilt(sos, mi) ** 2
hb = 10 * np.log10(np.convolve(hb, np.ones(4800) / 4800, 'same')[::4800] + 1e-12)   # 0.1 s
risers = []; k = 0
while k < len(hb) - 10:
    best = None
    for L in range(10, 61):
        if k + L >= len(hb): break
        x = np.arange(L); yy = hb[k:k + L]; p = np.polyfit(x, yy, 1); rr = np.corrcoef(x, yy)[0, 1]
        if rr >= 0.85 and p[0] * L >= 9: best = (L, p[0] * 10, rr)
    if best: risers.append(dict(start=round(k * 0.1, 2), end=round((k + best[0]) * 0.1, 2), slope_db_per_s=round(best[1], 1), r=round(best[2], 2))); k += best[0]
    else: k += 2
# ---------------- sub drops
yb, _ = sf.read(os.path.join(W, 'stems/bass.wav')); mb = yb.mean(1)
sos = ss.butter(4, [20, 60], btype='band', fs=SR, output='sos'); sb = ss.sosfilt(sos, mb) ** 2
sb = 10 * np.log10(np.convolve(sb, np.ones(960) / 960, 'same')[::240] + 1e-12)
subs = []; k = 20
while k < len(sb) - 60:
    if sb[k] - np.median(sb[k - 20:k - 2]) >= 18 and sb[k:k + 10].max() > -30 and np.median(sb[k:k + 60]) > -40:
        subs.append(dict(t=round(k * 240 / SR, 3), peak_db=round(float(sb[k:k + 20].max()), 1))); k += 100
    else: k += 1
# ---------------- width/filter transitions in verse 3 (search windows from inspection: 120-124 close, 133-138 open)
def sm(x, nn): return np.convolve(x, np.ones(nn) / nn, 'same')
lc = sm(E['instrumental_lrcorr'], 25); hf = sm(E['instrumental_hf_db'], 25)
def steepest(x, a, b_, sign):
    mk = (T >= a) & (T <= b_); d = np.gradient(x) * sign; j = np.where(mk)[0][np.argmax(d[mk])]; return round(float(T[j]), 3)
trans = dict(width_close=steepest(lc, 121.0, 122.6, +1), width_open=steepest(lc, 135.0, 136.6, -1),
             filter_close=steepest(hf, 121.0, 122.6, -1), filter_open=steepest(hf, 135.0, 136.6, +1))
json.dump(dict(beats=beats, downbeat_idx=down, hits=hits, accelerandos=acc, chops=chops, chop_clusters=clusters, silences=sil,
               suona=seg, risers=risers, sub_drops=subs, transitions=trans), open(os.path.join(W, 'audio/events.json'), 'w'), indent=0)
print('beats', len(beats), 'snapped', sum(x['src'] == 'onset' for x in beats), 'down', len(down))
print('hits', {c: sum(h['cls'] == c for h in hits) for c in set(h['cls'] for h in hits)})
print('accelerandos', [(a['start'], a['peak'], a['n'], a['first_ioi'], a['last_ioi']) for a in acc])
print('chops', len(chops), 'clusters', [(c['start'], c['n']) for c in clusters])
print('silences', [(s['start'], s['dur']) for s in sil if s['dur'] > 0.15])
print('suona', [(s['start'], s['end']) for s in seg])
print('risers', risers); print('subs', subs); print('trans', trans)

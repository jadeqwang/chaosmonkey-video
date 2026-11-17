"""Numerical checks + analysis/click_check.wav.
Click track: song at -3 dB + 15 ms 1.5 kHz click on every beat (2.5 kHz, louder, on downbeats) + a 40 ms band-noise
'tick' (4-10 kHz burst, panned hard right) on every hit classed gong_crash.
Checks -> analysis/verification.json:
  words_vs_vocal_onsets  word start minus nearest vocal-stem spectral-flux onset peak (|d| <= 80 ms), by confidence
  words_vs_whisper       English word starts vs faster-whisper word starts (same word text, |d| <= 0.5 s)
  words_rf_vs_demucs     word start on BS-RoFormer vs htdemucs vocal stems (two independent separations)
  beats_vs_drum_onsets   refined beat minus nearest drums-stem onset (dstr >= 0.3)
  beats_vs_beat_this_raw refined minus raw beat_this (20 ms frames)
  crash_vs_mix_attack    gong_crash time minus steepest 5 ms mix-RMS rise within +-40 ms
"""
import json, os, re, numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = os.path.join(ROOT, 'work')
TJ = json.load(open(os.path.join(ROOT, 'analysis/timing.json'))); SR = 48000
def st(d):
    d = np.array([x for x in d if x is not None]);
    if not len(d): return None
    a = np.abs(d); return dict(n=int(len(d)), median_ms=round(float(np.median(d)) * 1000, 1), median_abs_ms=round(float(np.median(a)) * 1000, 1),
                               p90_abs_ms=round(float(np.percentile(a, 90)) * 1000, 1), max_abs_ms=round(float(a.max()) * 1000, 1),
                               frac_within_42ms=round(float(np.mean(a <= 0.042)), 3))
out = {}
words = [w for l in TJ['lines'] for w in l['words']]
out['words_vs_vocal_onsets'] = {c: st([w['onset_resid'] for w in words if w['confidence'] == c]) for c in ('high', 'medium', 'low')}
out['words_vs_vocal_onsets']['note'] = 'sign: + = onset peak after the word start. Unmatched (no onset peak within 80 ms) words excluded: ' + \
    str(sum(w['onset_resid'] is None for w in words)) + f' of {len(words)}'
sh = [w['energy_shift'] for w in words if 'energy_shift' in w]
out['energy_onset_refinement'] = dict(n_words_moved=len(sh), median_shift_ms=round(float(np.median(sh)) * 1000, 1), max_shift_ms=round(float(min(sh)) * 1000, 1), note='MMS word starts lag the vocal-energy rise after a gap by ~50-130 ms (nasal/voiced consonants); such words were moved to the rise (cap 130 ms).')
WH = json.load(open(os.path.join(W, 'asr/whisper.json')))['en']; ww = [w for s in WH for w in s['words']]
norm = lambda s: re.sub(r"[^a-z']", '', s.lower())
d = []
for w in words:
    if not re.match(r'[A-Za-z]', w['w']): continue
    c = [x for x in ww if norm(x['w']) == norm(w['w']) and abs(x['start'] - w['start']) <= 0.5]
    if c: d.append(min((x['start'] - w['start'] for x in c), key=abs))
out['words_vs_whisper'] = st(d); out['words_vs_whisper']['note'] = 'whisper - ours; whisper word times are coarse (often early), an independent sanity check only'
WD = json.load(open(os.path.join(W, 'audio/words.json')))
out['words_rf_vs_demucs'] = st([w['start'] - w['dm_start'] for l in WD for w in l['words']])
O = json.load(open(os.path.join(W, 'audio/onsets.json'))); OD = np.array([o['t'] for o in O if o['dstr'] >= 0.3 and 'd' in o['src']])
bs = [b for b in TJ['beats'] if b['confidence'] != 'low']
out['beats_vs_drum_onsets'] = st([OD[np.argmin(np.abs(OD - b['t']))] - b['t'] for b in bs if np.min(np.abs(OD - b['t'])) <= 0.1])
out['beats_vs_drum_onsets']['snapped_fraction'] = round(float(np.mean([b['src'] == 'onset' for b in bs])), 3)
EVB = json.load(open(os.path.join(W, 'audio/events.json')))['beats']
out['beats_vs_beat_this_raw'] = st([b['t'] - b['raw'] for b in EVB])
y, _ = sf.read(os.path.join(W, 'audio/song.wav')); m = y.mean(1); h = 240
n = len(m) // h; r = 10 * np.log10((m[:n * h].reshape(n, h) ** 2).mean(1) + 1e-12); tt = np.arange(n) * h / SR
dr = np.r_[0, np.diff(r)]
cr = [x for x in TJ['hits'] if x['cls'] == 'gong_crash' and x['strength'] >= 0.8]
res = []
for x in cr:
    k = (tt >= x['t'] - 0.04) & (tt <= x['t'] + 0.04); j = np.where(k)[0][np.argmax(dr[k])]; res.append(tt[j] - x['t'])
out['crash_vs_mix_attack'] = st(res)
sp = []
for s in TJ['sync_points']:
    k = (tt >= s['t'] - 0.06) & (tt <= s['t'] + 0.06)
    if s['kind'] in ('gong_crash', 'hit', 'low_drum', 'perc') and k.any(): j = np.where(k)[0][np.argmax(dr[k])]; sp.append(dict(name=s['name'], t=s['t'], mix_attack=round(float(tt[j]), 3), resid_ms=round(float(tt[j] - s['t']) * 1000, 1)))
out['sync_hits_vs_mix_attack'] = sp
json.dump(out, open(os.path.join(ROOT, 'analysis/verification.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k != 'sync_hits_vs_mix_attack'}, indent=1, ensure_ascii=False))
for s in sp: print(s)
# ---------------- click track
song, _ = sf.read(os.path.join(ROOT, 'inputs/Chaos Monkey - reformatted for duet.wav')); outw = song * 0.7
def blip(f, dur, amp):
    t = np.arange(int(dur * SR)) / SR; return amp * np.sin(2 * np.pi * f * t) * np.exp(-t / (dur / 4))
cb, cd = blip(1500, 0.015, 0.35), blip(2500, 0.02, 0.5)
rng = np.random.default_rng(0); nz = rng.standard_normal(int(0.04 * SR))
import scipy.signal as ss
nz = ss.sosfilt(ss.butter(4, [4000, 10000], btype='band', fs=SR, output='sos'), nz); nz = 0.5 * nz / np.abs(nz).max() * np.exp(-np.arange(len(nz)) / (0.01 * SR))
DB = {d['t'] for d in TJ['downbeats']}
for b in TJ['beats']:
    c = cd if b['t'] in DB else cb; i = int(b['t'] * SR); outw[i:i + len(c)] += c[:len(outw) - i, None]
for x in TJ['hits']:
    if x['cls'] == 'gong_crash' and x['strength'] >= 0.5:
        i = int(x['t'] * SR); seg = nz[:len(outw) - i]; outw[i:i + len(seg), 1] += seg
outw /= max(1.0, np.abs(outw).max() / 0.99)
sf.write(os.path.join(ROOT, 'analysis/click_check.wav'), outw, SR, subtype='PCM_16')
print('click track written')

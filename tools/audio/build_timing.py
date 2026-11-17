"""Assemble analysis/timing.json from work/audio/{events,words,energy,singer,onsets}.json/npz.
Sections are hand-set from measured events (each boundary cites the event it sits on). Word overrides (OVR) are
measured vocal-stem onset peaks / local re-alignments used where MMS failed (reasons given)."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import sung
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = os.path.join(ROOT, 'work')
DUR = 238.320
EVT = json.load(open(os.path.join(W, 'audio/events.json'))); WD = json.load(open(os.path.join(W, 'audio/words.json')))
O = json.load(open(os.path.join(W, 'audio/onsets.json'))); EN = np.load(os.path.join(W, 'audio/energy.npz'))
SG = np.load(os.path.join(W, 'audio/singer.npz')); EV = np.load(os.path.join(W, 'audio/env.npz'))
L = sung.build()
r3 = lambda x: None if x is None else round(float(x), 3)
# ---------------------------------------------------------------- sections
SEC = [
 ('intro', 0.000, 15.515, 'Solo guqin (0-2.0), low hand-drum pulse from 2.03, bright clapper 16ths from ~12.6 tightening to a 32nd roll 15.07-15.28; wordless vocal hum (D4) 13.3-15.3; 75 ms full-band hole 15.440-15.515.'),
 ('verse1', 15.515, 41.014, 'Band + bass enter after the hole; child "妈妈..." from 15.81, Mom from 23.06; steady 16th percussion (no audible slow-to-fast clapper accelerando); drums drop out 37.885-40.995 under "soaking up light" (the [Pause]).'),
 ('prechorus', 41.014, 58.673, 'Drums back on the 41.014 downbeat; "It split apart" with a 3-hole stutter chop 43.80-44.13 and drum break 44.15-44.50; "Monkey!" 45.275; drums thin to a 16th-note roll 57.04-57.81, then a drum break under the "Born fully formed" pickup (57.79).'),
 ('hook1', 58.673, 85.236, 'The stone bursts: crash + kick on the 58.673 downbeat into breakbeat; octave duet; vocals end 73.5; 72.0-85.2 instrumental post-hook (suona-like lead in the other stem, drum breaks 71.9-72.8 and 75.5-76.4).'),
 ('verse2_memory', 85.236, 107.975, 'Fill 85.46-86.12 (IOI 219->44 ms) into a bass/band hole 85.99-87.0, band back with crash 86.998; Mom/child verse; band drops away 100.9-107.9 for "The master leaned in close" with isolated hits; audible whispered "ps ps ps" 103.20-103.60 over hits at 103.207/103.416/103.648.'),
 ('rap', 107.975, 122.005, 'Crash + full breakbeat on 107.975 (rap pickup from 107.04); fast Mandarin rap, Mom joins (octave double) from 112.76; inline echoes "七十二变" (110.38) and "谁是真身" (119.54).'),
 ('verse3_band', 122.005, 148.550, 'Headband verse: instrumental narrows (L/R corr ~0.95, width close 121.905) and low-passes (>4 kHz share -35..-55 dB, filter close 122.545) with sparse hits; reopens: filter 135.685, width 136.025, full band back on the 135.878 downbeat; drums drop out 146.455 under "no more, no less".'),
 ('yes', 148.550, 149.285, 'Child "Yes" (148.72-149.27), off the beat over the drum-less tail.'),
 ('silence', 149.285, 149.720, 'Only near-silence in the song: mix < -50 dBFS 149.285-149.525 (0.24 s), then a crash/sub hit at 149.720. Not a full bar (bar = 1.73 s).'),
 ('bridge', 149.720, 177.408, 'Full band with drums and a sustained suona-like line from 149.72 (NOT drum-less); child sings alone 162.63-176.1; no clearly audible vocoder (not measurable).'),
 ('build', 177.408, 189.805, 'Drums and bass drop out (177.645); sparse low tonal drum hits 179.094, 180.758, 184.121, 187.460 (+187.781, 188.097, 188.313); Mom/child dialogue ("Wouldn\'t you? You\'re able" ends 189.9 over the drop).'),
 ('drop2', 189.805, 202.898, 'Arrives as a 4-hit stuttered crash 189.805/189.867/189.922/189.972 (drums back), then kick + bass on the 190.860 downbeat (grid beat 190.885); octave duet with chopped echoes; stutter chop 200.675-201.080 inside "一通百通".'),
 ('outro', 202.898, 228.767, 'Mom "Do you want to know..." over the beat; bass cuts 211.515 (downbeat); the beat cuts out mid-bar at 218.715 (one beat after the 218.332 downbeat); child lines over pads with two isolated wooden/low hits 221.805, 225.254.'),
 ('end', 228.767, DUR, 'Percussion pattern returns (16ths) 228.767-235.833 with the last vocal note ("line") to 230.76; sub drone in 232.29; last hit 235.833; drone/hum cuts 237.84; faint -43 dBFS tail; file hard-cuts at 238.320 (no digital silence).'),
]
bt = np.array([b['t'] for b in EVT['beats']]); DI = EVT['downbeat_idx']; DT = bt[DI]
NOPULSE = [(146.455, 149.720), (177.645, 189.790), (218.715, 228.767), (235.9, DUR), (0.0, 2.0)]
def bpm_in(a, b):
    k = (bt >= a) & (bt < b); x = bt[k]
    if len(x) < 4: return None, None
    i = np.arange(len(x)); p = np.polyfit(i, x, 1); ioi = np.diff(x)
    return round(60 / p[0], 1), round(60 / np.median(ioi), 1)
sections = []
for name, a, b, d in SEC:
    nb = int(np.sum((DT >= a - 0.02) & (DT < b - 0.02)))
    bp, bm = bpm_in(a, b)
    sections.append(dict(name=name, start=r3(a), end=r3(b), dur=r3(b - a), bars=nb, bpm=bp, bpm_median_ioi=bm, description=d))
# ---------------------------------------------------------------- words / lines
OVR = {  # (line, word): (start, confidence, reason)
 (11, 0): (57.790, 'medium', 'MMS failed in the dense octave duet; vocal-stem onset peak'), (11, 1): (58.130, 'medium', 'onset peak (greedy CTC hears f at 58.18)'),
 (11, 2): (58.450, 'medium', 'onset peak; F0 leap to the held note'), (12, 0): (59.595, 'medium', 'onset peak after the 59.4 dip'),
 (12, 1): (60.015, 'medium', 'onset peak'), (12, 2): (60.460, 'medium', 'onset peak, held to 60.9'),
 (13, 0): (61.070, 'medium', 'onset peak (greedy e at 61.12)'), (13, 1): (61.330, 'medium', 'onset peak (greedy b at 61.28)'), (13, 2): (61.700, 'medium', 'greedy f at 61.70'),
 (14, 0): (64.435, 'medium', 'onset peak'), (14, 1): (64.775, 'medium', 'strong onset peak'), (14, 2): (65.320, 'medium', 'strong onset peak'),
 (14, 3): (65.765, 'low', 'onset; backing-stem decode hears l at 65.70'), (14, 4): (67.065, 'medium', 'onset; greedy l/n at 67.02'), (14, 5): (67.440, 'medium', 'greedy s at 67.44'),
 (57, 0): (195.650, 'low', 'solo voice on the lead stem 195.6-196.5 between "warmed" and "No cradle"'),
 (58, 0): (196.615, 'medium', 'onset; greedy n at 196.62'), (58, 1): (196.830, 'medium', 'onset'), (58, 2): (197.810, 'low', 'onset, local re-alignment 197.78'), (58, 3): (198.120, 'medium', 'greedy s at 198.12'),
 (59, 0): (198.740, 'low', 'local re-alignment (window 189.4-203.4)'), (59, 1): (199.380, 'low', 'local re-alignment; lead-stem activity'),
 (60, 0): (200.735, 'low', 'strong vocal onset just before the 200.675-201.08 chop'), (60, 1): (201.090, 'low', 'strong onset right after the chop'),
 (60, 2): (201.620, 'low', 'onset (re-alignment 201.58)'), (60, 3): (201.965, 'low', 'onset (re-alignment 201.94)'),
 (61, 0): (202.460, 'low', 're-alignment; onsets 202.40/202.505'), (61, 1): (202.795, 'low', 'onset'),
}
TT = EV['T']; RV = EV['rms_vocals']; ONV = EV['onset_vocals']
import scipy.signal as ss
pk, _ = ss.find_peaks(ONV, height=np.percentile(ONV, 80), distance=6); PT = TT[pk]
lines = []
for l, wd in zip(L, WD):
    ws = [dict(**w) for w in wd['words']]
    for i, w in enumerate(ws):
        if (l['id'], i) in OVR:
            s, c, why = OVR[(l['id'], i)]; w['start'] = s; w['confidence'] = c; w['override'] = why
    for i, w in enumerate(ws):   # energy-onset refinement (word preceded by a dip >= 12 dB in the 200 ms before it)
        a0 = w['start'] - 0.20; k = (TT >= a0) & (TT <= w['start'] + 0.04); idx = np.where(k)[0]
        if len(idx) < 10: continue
        lev = RV[np.searchsorted(TT, w['start'] + 0.03)]; jm = idx[np.argmin(RV[idx[:-8]])] if len(idx) > 8 else idx[0]
        if lev - RV[jm] >= 12 and TT[jm] < w['start']:
            thr = RV[jm] + 0.5 * (lev - RV[jm]); after = np.where((TT > TT[jm]) & (TT <= w['start'] + 0.04) & (RV >= thr))[0]
            if len(after):
                eo = float(TT[after[0]]) - 0.005   # 10 ms RMS window centred on the frame
                prev_ok = i == 0 or eo >= ws[i - 1]['start'] + 0.10
                if 0.02 <= w['start'] - eo <= 0.13 and prev_ok and 'override' not in w:
                    w['energy_shift'] = round(eo - w['start'], 3); w['start'] = round(eo, 3)
    for i, w in enumerate(ws):
        nxt = ws[i + 1]['start'] if i + 1 < len(ws) else None
        if nxt is not None and (w['end'] > nxt or 'override' in w): w['end'] = max(w['start'] + 0.08, min(w['end'], nxt - 0.01) if w['end'] > w['start'] + 0.08 and w['end'] <= nxt else nxt - 0.01)
        if w['end'] <= w['start']: w['end'] = w['start'] + 0.1
        j = np.argmin(np.abs(PT - w['start'])); rr = PT[j] - w['start']; w['onset_resid'] = r3(rr) if abs(rr) <= 0.08 else None
    s = ws[0]['start']; e = ws[-1]['end']
    later = [WD[j]['words'][0]['start'] for j in range(l['id'] + 1, len(L)) if not L[j]['echo']]
    lim = min(min(later) if later else e + 2, e + 2.0)
    m = (TT >= s) & (TT <= max(e, s + 0.05)); peak = RV[m].max()
    j = np.searchsorted(TT, e)
    while j < len(TT) and TT[j] < lim and RV[j] > peak - 20: j += 1
    end = max(e, float(TT[min(j, len(TT) - 1)])); ws[-1]['end'] = r3(max(ws[-1]['end'], min(end, ws[-1]['start'] + 3.0)))
    ms = (SG['T'] >= s) & (SG['T'] < end) & (SG['rms'] > -38); pc = float(np.mean(SG['p_child'][ms])) if ms.sum() >= 5 else None
    singer = l['singer']; note = None
    if l['singer'] == 'child' and pc is not None and pc < 0.35: note = f'timbre classifier says mom-like (p_child {pc:.2f}); sheet says child'
    if l['singer'] == 'mom' and pc is not None and pc > 0.65: note = f'timbre classifier says child-like (p_child {pc:.2f}); sheet says mom'
    if l['id'] == 44: note = 'whispered/spoken; classifier unreliable on 13 frames (p_child 0.18)'
    confs = [w['confidence'] for w in ws]
    lc = 'low' if confs.count('low') > len(confs) / 2 else ('high' if confs.count('high') >= len(confs) * 0.6 else 'medium')
    lines.append(dict(id=l['id'], section=l['section'], start=r3(s), end=r3(end), singer=singer, singer_p_child=None if pc is None else round(pc, 2),
                      singer_note=note, language=l['lang'], text=l['text'], echo=l['echo'], confidence=lc,
                      words=[dict(w=w['w'], start=r3(w['start']), end=r3(w['end']), confidence=w['confidence'], score=w['score'],
                                  onset_resid=w['onset_resid'], **({'override': w['override']} if 'override' in w else {}), **({'energy_shift': w['energy_shift']} if 'energy_shift' in w else {})) for w in ws]))
# ---------------------------------------------------------------- beats
def in_np(t): return any(a <= t < b for a, b in NOPULSE)
bar = 0; beats = []; downs = set(DI); bib = 0
for i, b in enumerate(EVT['beats']):
    if i in downs: bar += 1; bib = 1
    else: bib += 1
    beats.append(dict(t=b['t'], bar=bar, beat=bib, src=b['src'], confidence='low' if in_np(b['t']) else ('high' if b['src'] == 'onset' else 'medium')))
downbeats = [dict(t=beats[i]['t'], bar=beats[i]['bar'], confidence=beats[i]['confidence']) for i in DI]
# ---------------------------------------------------------------- hits
hits = [dict(t=r3(h['t']), cls=h['cls'], strength=h['strength'], confidence=h['confidence']) for h in EVT['hits']]
ISO = (179.094, 180.758, 184.121, 187.460, 221.805, 225.254)   # each follows >= 1.3 s of drum silence (drum_dropouts)
for h in hits:
    if any(abs(h['t'] - x) < 0.01 for x in ISO): h['cls'] = 'low_drum'; h['confidence'] = 'medium'; h['note'] = 'isolated hit after >= 1.3 s drum silence; low tonal body (wooden/low drum)'
# fast rolls (>= 4 onsets with IOI <= 75 ms, any drum onset dstr >= 0.1)
DO = sorted([o['t'] for o in O if o['dstr'] >= 0.1 and 'd' in o['src']]); rolls = []; i = 0
while i < len(DO) - 3:
    j = i
    while j + 1 < len(DO) and DO[j + 1] - DO[j] <= 0.075 and DO[j + 1] - DO[j] >= 0.025: j += 1
    if j - i + 1 >= 4: rolls.append(dict(start=r3(DO[i]), end=r3(DO[j]), n=j - i + 1, clicks=[r3(x) for x in DO[i:j + 1]], iois_ms=[round((DO[k + 1] - DO[k]) * 1000) for k in range(i, j)])); i = j + 1
    else: i += 1
acc = [dict(**a, kind='fill (IOIs shrink)', confidence='low') for a in EVT['accelerandos']]
specials = dict(
  accelerating_runs=acc, fast_rolls=rolls,
  chops=[dict(**c, cls='breakbeat_chop', confidence='medium') for c in EVT['chops']],
  chop_clusters=EVT['chop_clusters'],
  silences=[dict(**s, confidence='high') for s in EVT['silences']],
  suona_phrases=[dict(**s, confidence='low') for s in EVT['suona'] if s['start'] > 14],
  risers=[dict(**r, confidence='low') for r in EVT['risers']],
  sub_drops=[dict(t=149.72, note='crash + sub boom (sub band -17 dB)', confidence='medium'), dict(t=232.29, note='sub drone enters (bass stem 20-60 Hz)', confidence='medium')],
  drum_dropouts=[], band_reentries=[])
E = EN; T = E['T']
q = E['rms_drums'] < -55; k = 0
while k < len(q):
    if q[k]:
        j = k
        while j < len(q) and q[j]: j += 1
        if T[j - 1] - T[k] >= 0.25 and T[k] > 2: specials['drum_dropouts'].append(dict(start=r3(T[k]), end=r3(T[j - 1])))
        k = j
    else: k += 1
# ---------------------------------------------------------------- energy (0.5 s)
Th = E['T_h']; energy = dict(t=[r3(x) for x in Th], hop_s=0.5,
  rms_db={k: [round(float(v), 1) for v in E[f'rms_{k}_h']] for k in ('mix', 'vocals', 'instrumental', 'drums', 'bass', 'other', 'lead', 'backing')},
  width_side_minus_mid_db=dict(mix=[round(float(v), 1) for v in E['mix_width_h']], instrumental=[round(float(v), 1) for v in E['instrumental_width_h']]),
  lr_correlation=dict(mix=[round(float(v), 3) for v in E['mix_lrcorr_h']], instrumental=[round(float(v), 3) for v in E['instrumental_lrcorr_h']]),
  centroid_hz=dict(mix=[round(float(v)) for v in E['mix_centroid_h']], instrumental=[round(float(v)) for v in E['instrumental_centroid_h']]),
  rolloff85_hz=dict(mix=[round(float(v)) for v in E['mix_rolloff85_h']], instrumental=[round(float(v)) for v in E['instrumental_rolloff85_h']]),
  hf_share_db=dict(mix=[round(float(v), 1) for v in E['mix_hf_db_h']], instrumental=[round(float(v), 1) for v in E['instrumental_hf_db_h']]),
  note='rms = mono-sum RMS dBFS over each 0.5 s; width = side/mid energy ratio (dB, -inf = mono); lr_correlation 1 = mono; hf_share = energy above 4 kHz minus total (dB). Fine (10 ms) curves: work/audio/energy.npz.',
  transitions=dict(**EVT['transitions'], note='steepest change of 0.25 s-smoothed instrumental L/R correlation (width) and >4 kHz share (filter). The narrowing is partial: instrumental L/R corr ~0.90-0.98 vs 0.5-0.7 elsewhere; never digital mono.'))
# ---------------------------------------------------------------- sync points
def W_(lid, wi=0): return next(l for l in lines if l['id'] == lid)['words'][wi]
SP = [
 ('First clapper (roll 0.165-0.381)', 0.165, 'clapper', 'low'),
 ('Low hand-drum pulse enters', 2.031, 'perc', 'medium'),
 ('Clapper 16ths begin (intro)', 12.597, 'clapper', 'low'),
 ('Intro roll peak (32nds) before the hole', 15.279, 'clapper', 'low'),
 ('Full-band hole -> band + bass enter (verse 1)', 15.515, 'edit', 'high'),
 ('"妈妈" first word', W_(0)['start'], 'vocal', 'high'),
 ('Mom enters "On 花果山"', W_(2)['start'], 'vocal', 'medium'),
 ('Drums drop out (verse-1 pause)', 37.885, 'dropout', 'high'),
 ('Drums back, pre-chorus downbeat', 41.014, 'hit', 'high'),
 ('"It split apart" stutter chops', 43.805, 'chop', 'medium'),
 ('"Monkey!"', W_(7)['start'], 'vocal', 'high'),
 ('Pre-hook roll start (16ths)', 57.035, 'perc', 'medium'),
 ('"Born" pickup (hook 1)', 57.790, 'vocal', 'medium'),
 ('Hook 1 crash: the stone bursts', 58.673, 'gong_crash', 'high'),
 ('"He bowed four ways"', W_(13, 1)['start'], 'vocal', 'medium'),
 ('Post-hook drum break', 71.925, 'dropout', 'medium'),
 ('Verse-2 fill start (IOI shrinks 219->44 ms)', 85.458, 'perc', 'medium'),
 ('Verse-2 crash / band back', 86.998, 'gong_crash', 'high'),
 ('"ps ps ps" (whispered, audible)', W_(22)['start'], 'vocal', 'medium'),
 ('Rap pickup "石"', W_(24)['start'], 'vocal', 'high'),
 ('Rap crash / breakbeat in', 107.975, 'gong_crash', 'high'),
 ('Mom joins the rap "千"', W_(28)['start'], 'vocal', 'medium'),
 ('Cut to mono (width closes)', EVT['transitions']['width_close'], 'transition', 'medium'),
 ('Filter closes', EVT['transitions']['filter_close'], 'transition', 'medium'),
 ('(听话) 1', W_(37)['start'], 'vocal', 'medium'),
 ('(听话) 2', W_(39)['start'], 'vocal', 'medium'),
 ('Filter reopens', EVT['transitions']['filter_open'], 'transition', 'medium'),
 ('Full band back (downbeat) / width reopens', 135.878, 'hit', 'high'),
 ('Drums drop out before "Yes"', 146.455, 'dropout', 'high'),
 ('"Yes"', W_(44)['start'], 'vocal', 'medium'),
 ('Near-silence start', 149.285, 'silence', 'high'),
 ('Near-silence end', 149.525, 'silence', 'high'),
 ('Bridge entry: crash + sub, full band', 149.720, 'gong_crash', 'high'),
 ('Bridge vocal "Tool"', W_(45)['start'], 'vocal', 'high'),
 ('Build: drums + bass out', 177.645, 'dropout', 'high'),
 ('Build low drum hits', 179.094, 'low_drum', 'medium'),
 ('Drop 2: stuttered crash (4 hits, 189.805-189.972)', 189.805, 'gong_crash', 'high'),
 ('Drop 2 downbeat: kick + bass in', 190.860, 'hit', 'high'),
 ('Echo (formed) 1', W_(54)['start'], 'vocal', 'low'),
 ('Echo (formed) 2', W_(55)['start'], 'vocal', 'low'),
 ('Echo (warmed)', W_(57)['start'], 'vocal', 'low'),
 ('Echo (no song)', W_(59)['start'], 'vocal', 'low'),
 ('Drop-2 stutter chop', 200.675, 'chop', 'high'),
 ('Echo (百通)', W_(61)['start'], 'vocal', 'low'),
 ('Outro vocal "Do you want"', W_(62)['start'], 'vocal', 'medium'),
 ('Bass cuts (outro)', 211.515, 'dropout', 'high'),
 ('Beat cuts out mid-bar', 218.715, 'dropout', 'high'),
 ('Single wooden/low hit 1', 221.805, 'low_drum', 'medium'),
 ('Single wooden/low hit 2', 225.254, 'low_drum', 'medium'),
 ('Percussion returns (end)', 228.767, 'hit', 'high'),
 ('Sub drone in', 232.290, 'sub', 'medium'),
 ('Last percussive hit', 235.833, 'hit', 'high'),
 ('Hum/drone cuts off', 237.840, 'edit', 'high'),
 ('True end of audio (hard cut)', DUR, 'end', 'high'),
]
sync = [dict(name=n, t=r3(t), frame24=int(np.ceil(t * 24 - 1e-9)), kind=k, confidence=c) for n, t, k, c in SP]
ver = json.load(open(os.path.join(ROOT, 'analysis/verification.json'))) if os.path.exists(os.path.join(ROOT, 'analysis/verification.json')) else None
out = dict(meta=dict(file='inputs/Chaos Monkey - reformatted for duet.wav', sample_rate=48000, channels=2, samples=11439360, duration=DUR,
                     frame_rule='frame24 = ceil(t*24): first 24 fps frame starting at or after the event',
                     stems='work/stems/ (separated from this file: BS-RoFormer vocals, htdemucs_ft drums/bass/other, mel-band-roformer karaoke lead/backing). The supplied spliced stems are a different render (44.1 kHz, 236.40 s, offset drifting 0 -> +2 s) and were not used for timing.',
                     tempo_note='Measured ~136-140 BPM (not 150). Beats: beat_this + snap to drum onsets; cut to beats[], not to a constant tempo.'),
           sections=sections, lines=lines, beats=beats, downbeats=downbeats, hits=hits, hit_events=specials, energy=energy,
           sync_points=sync, verification=ver)
os.makedirs(os.path.join(ROOT, 'analysis'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'analysis/timing.json'), 'w'), ensure_ascii=False, indent=1)
for s in sections: print(f"{s['name']:14s} {s['start']:8.3f} {s['end']:8.3f} bars {s['bars']:3d} bpm {s['bpm']} / {s['bpm_median_ioi']}")
print('rolls', [(r['start'], r['n'], r['iois_ms']) for r in rolls])
print('flags', [(l['id'], l['singer_note']) for l in lines if l['singer_note']])

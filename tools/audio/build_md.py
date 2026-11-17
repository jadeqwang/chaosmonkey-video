"""docs/AUDIO_MAP.md from analysis/timing.json + analysis/verification.json."""
import json, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TJ = json.load(open(os.path.join(ROOT, 'analysis/timing.json'))); V = TJ['verification']
def mmss(t): return f"{int(t // 60)}:{t % 60:05.2f}"
def fr(t): return int(np.ceil(t * 24 - 1e-9))
bt = np.array([b['t'] for b in TJ['beats']]); B = TJ['beats']
def barbeat(t):
    i = int(np.searchsorted(bt, t + 1e-6) - 1)
    if i < 0: return '-'
    b = B[i]; return f"{b['bar']}.{b['beat']} ({(t - b['t']) * 1000:+.0f} ms)"
L = []; A = L.append
A('# Chaos Monkey: audio map\n')
A('Timing reference for the edit. All times are seconds from the first sample of `inputs/Chaos Monkey - reformatted for duet.wav` '
  '(48 kHz stereo, 11 439 360 samples, **238.320 s**). Frame = ceil(t x 24): the first 24 fps frame that starts at or after the event. '
  'Machine-readable: [`analysis/timing.json`](../analysis/timing.json). Plots: [`analysis/plots/`](../analysis/plots/) '
  '(`00_overview.png` + one zoomed spectrogram per section). Spot-check audio: [`analysis/click_check.wav`](../analysis/click_check.wav) '
  '(click on every beat, higher click on downbeats, noise tick in the right channel on every crash). Checks: '
  '[`analysis/verification.json`](../analysis/verification.json). Rebuild: [`tools/audio/README.md`](../tools/audio/README.md).\n')
A('Confidence marks used below: no mark = solid (about +-25 ms), `~` = medium (about +-50 ms), `?` = low (+-100 ms or more, or an inference).\n')
A('## Stems: the supplied spliced stems do NOT match this file\n')
A('`chaosmonkey-song/spliced/stems/*.wav` are 44.1 kHz, **236.40 s** long and belong to the *spliced duet* render, not to the '
  '*reformatted for duet* file (a separate Suno render of the splice). Envelope cross-correlation of their sum against this file in 10 s windows '
  'gives low correlation (0.28-0.83) and an offset that drifts steadily from ~0 s at 10-30 s to +0.95 s at 140 s and ~+2 s at 220 s '
  '(`tools/audio/check_stems.py`). So the stems were re-separated from this file (`work/stems/`, sample-aligned, same length): BS-RoFormer vocals '
  '(timing authority), htdemucs_ft drums/bass/other (+ a second vocal stem), and a mel-band-roformer karaoke lead/backing split. There is no '
  'model that separates mom from child here: both voices sit around D4 (median F0 295 vs 285 Hz in the take stems), so **singer per line is '
  'from the lyric sheet, checked with a timbre classifier** (LDA on MFCCs trained on the spliced take stems; 81-87 % per-frame accuracy on held-out '
  'data, `p_child` per line in timing.json). In the octave duets the karaoke model puts everything in "backing", so echoes could not be '
  'isolated on their own stem; they were aligned inline in sung order.\n')
A('## The numbers to cut on\n')
A('| # | Sync point | Time | s | Frame | Bar.beat | Conf. |'); A('|---|---|---|---|---|---|---|')
for i, s in enumerate(sorted(TJ['sync_points'], key=lambda x: x['t'])):
    A(f"| {i + 1} | {s['name']} | {mmss(s['t'])} | {s['t']:.3f} | {s['frame24']} | {barbeat(s['t'])} | {s['confidence']} |")
A('')
A('## What differs from the lyric sheet / stage directions\n')
diffs = [
 '**Tempo is ~135-140 BPM, not 150.** Measured per section below; it creeps up from ~135.5 (intro to hook 1) to ~137 (verse 2, rap), ~138.5 (verse 3, bridge) and ~139-140 (drop 2, outro), then ~135.7 in the end tag. A constant grid would drift by about a beat over the song: cut to `beats[]`.',
 '**No long "slow, then accelerate" clapper runs.** The percussion sits on a steady 16th grid (~108-110 ms) almost everywhere. What exists: a 5-click clapper roll at the very start (0.165-0.381, IOIs 55/52/44/65 ms); clapper 16ths from 12.6 s tightening to 32nds 15.07-15.28 before the hole at 15.44; short fills whose IOIs shrink into section changes (85.46-86.12: 219->44 ms; 134.57-135.89: 427->45 ms; 122.84-124.15; 130.17-131.09; 200.33-201.51; 72.36-73.35); and the 4-hit stuttered crash into drop 2 (189.805-189.972). All listed with every click time in timing.json `hit_events.accelerating_runs` / `fast_rolls`.',
 '**Intro is not drum-less**: solo guqin for only 2 s, then a low hand-drum pulse from 2.03 and clappers; a wordless vocal hum (D4) 13.3-15.3 precedes "妈妈" (15.81).',
 '**"(ps ps ps)" IS audible**: a whispered "pss pss pss" 103.20-103.60 (Whisper also hears it), over hits at 103.207 / 103.416 / 103.648.',
 '**The "bar of silence" is 0.24 s**, not a bar: the only near-silence in the song is 149.285-149.525 (< -50 dBFS); a crash + sub hit follows at 149.720. Before it the drums drop out 146.455-149.72 under "no more, no less" and "Yes" (148.72).',
 '**"Uh" is gone and "Yes" is short**: "Yes" 148.72-149.27, quiet, right after "less" (147.91); no audible sigh.',
 '**The bridge is NOT drum-less**: the full band (drums, bass, sustained suona-like line) comes back at 149.720 and plays a 13 s instrumental before the child sings (162.63); drums continue under the whole bridge vocal. A vocoder halo is not measurably present. The drum-less, sparse section is the **build** (177.645-189.8), with single low drum hits on bar lines.',
 '**Drop 2 arrives early as a stutter**: a 4-hit stuttered crash at 189.805 (half a bar before the downbeat), kick + bass on 190.860. There is no separate crash on the downbeat.',
 '**Headband verse narrows but never becomes mono**: instrumental L/R correlation rises to ~0.90-0.98 (0.5-0.7 elsewhere) and the >4 kHz share drops 30-40 dB. Width closes 121.905 / filter closes 122.545; filter reopens 135.685, width 136.025, full band back on the 135.878 downbeat. The narrowing covers "Why does he wear..." to "It isn\'t fair" only; "I don\'t want it in his hair" onward is wide again.',
 '**"(听话)" echoes are sung (child, Mandarin) at 130.18 and 133.69**; "Then 听话" at 141.45.',
 '**Echo placement**: "(born fully formed)" is a full repeat 59.60-60.9; "(七十二变)" is sung inline right after the line (110.38); "(谁是真身)" 119.54 overlaps the run into "问了也白问" (low confidence); drop-2 echoes "(formed)" x2 191.51 / 192.37, "(warmed)" 195.65, "(no song)" 198.74, "(百通)" 202.46 all low confidence (continuous octave vocal, no separable echo stem). Whisper hears drop 2\'s tail as "song by song by song".',
 '**Singer check**: the last two outro lines ("I turned each page, I looked for mine", "it wasn\'t there on any line") are sheet = child, but the timbre classifier rates them mom-like (p_child 0.22 / 0.29, the same range as Mom\'s lines). Listen before casting these two lines. All other lines match the sheet.',
 '**The beat cuts out mid-bar at 218.715** (one beat after the 218.332 downbeat), after "I turned each page"; the bass had already cut on the 211.515 downbeat. Two isolated wooden/low hits follow at 221.805 and 225.254.',
 '**The ending is not "a single clapper then the hum cuts off"**: after the last lyric a percussion pattern returns 228.767-235.833 (16ths, crash at 228.767) with a sub drone from 232.29; the last hit is 235.833; the drone ("hum") cuts at **237.840** (20 dB fall within ~30 ms); a faint -43 dBFS tail remains and the file hard-cuts at **238.320** with no digital silence (the last sample is non-zero). Final silence: none.',
]
for d in diffs: A(f'- {d}')
A('')
A('## Sections\n')
A('| # | Section | Start | End | Start s | End s | Frames | Bars | BPM | What the music does |'); A('|---|---|---|---|---|---|---|---|---|---|')
for i, s in enumerate(TJ['sections']):
    A(f"| {i + 1} | **{s['name']}** | {mmss(s['start'])} | {mmss(s['end'])} | {s['start']:.3f} | {s['end']:.3f} | {fr(s['start'])}-{fr(s['end'])} | {s['bars']} | {s['bpm'] if s['bpm'] else '-'} | {s['description']} |")
A('\nBPM = 60 / slope of a linear fit of beat time vs index inside the section (median-IOI value in timing.json agrees within 1 BPM). '
  'Bars = downbeats inside the section. The build (no drums) reads ~143 BPM from the tracker: treat as low confidence.\n')
A('## Tempo and grid\n')
A('Beats: beat_this (CPJKU, GPU) on the mix (98 % of beats within 30 ms of a separate run on the instrumental), each moved to the drums-stem '
  f"onset within +-35 ms where there is one ({V['beats_vs_drum_onsets']['snapped_fraction'] * 100:.0f} % of beats in pulsed regions), otherwise "
  'a local linear fit. Beats are `confidence: low` where there is no pulse: 0-2.0 (guqin), 146.455-149.72 (drums out), 177.645-189.79 (build), '
  '218.715-228.767 (outro, no beat), 235.9-end. The intro bar numbering is the tracker\'s and may be phase-shifted; from 15.5 on the downbeats '
  'line up with the section hits (41.014, 58.673, 86.998, 107.975, 135.878, 149.720, 190.885, 228.767 are all downbeats).\n')
A('## Lyrics: line by line\n')
A('Word time = onset. Mandarin is per character. Singer is the lyric-sheet assignment; `!` marks a classifier disagreement (see above). '
  'Echoes are in parentheses.\n')
A('| # | Section | Start | End | Frame | Singer | Line, word onsets |'); A('|---|---|---|---|---|---|---|')
for l in TJ['lines']:
    ws = ' · '.join(f"{w['w']}{'' if w['confidence'] == 'high' else ('~' if w['confidence'] == 'medium' else '?')} {w['start']:.2f}" for w in l['words'])
    sg = l['singer'] + ('!' if l['singer_note'] and l['id'] != 44 else '')
    txt = f"*{l['text']}*" if l['echo'] else l['text']
    A(f"| {l['id'] + 1} | {l['section']} | {l['start']:.2f} | {l['end']:.2f} | {fr(l['start'])} | {sg} | {txt}<br>{ws} |")
A('')
he = TJ['hit_events']
A('## Hits\n')
cr = [h for h in TJ['hits'] if h['cls'] == 'gong_crash']
A(f"**Gong/cymbal crashes** ({len(cr)}; accented high-band jumps, see events.py for the rule): " + ', '.join(f"{h['t']:.3f}" for h in cr) + '. '
  'High-band sample checks of the key ones: hook 58.670, rap 107.965, bridge 149.710, drop 2 189.805 (0-10 ms from the listed times).\n')
A('**"He bowed four ways": no four distinct crashes.** The bar has normal breakbeat hits (61.07-64.4) and no accented crash: the only crash in hook 1 is 58.673. '
  'Candidate cut points for four bows are the four strongest drum hits on beats in 61.0-64.4 (see 04_hook1.png); treat them as a choice, not a sync.\n')
low = [h for h in TJ['hits'] if h['cls'] == 'low_drum']
A('**Isolated low/wooden drum hits** (each after >= 1.3 s of drum silence; low tonal body, short high end; build hits sit on bar lines): ' + ', '.join(f"{h['t']:.3f}" for h in low) + '. Spectral peaks: 179.094 ~130 Hz, 180.758 ~73 Hz, 184.121 ~116 Hz; 221.805/225.254 ~45 Hz thump + a 440/233 Hz tone.\n')
A('**Accelerating fills** (IOIs shrink; every click listed in timing.json):\n')
for a in he['accelerating_runs']: A(f"- {a['start']:.3f} -> {a['peak']:.3f}: {a['n']} hits, IOI {a['first_ioi'] * 1000:.0f} -> {a['last_ioi'] * 1000:.0f} ms: " + ', '.join(f'{c:.3f}' for c in a['clicks']))
A('\n**Fast rolls** (>= 4 hits <= 75 ms apart):\n')
for r in he['fast_rolls']: A(f"- {r['start']:.3f}-{r['end']:.3f}: " + ', '.join(f'{c:.3f}' for c in r['clicks']) + f"  (IOI {r['iois_ms']} ms)")
A('\n**Clapper 16ths in the intro** (bright, bodiless clicks, every ~107 ms): 12.597 to 15.279, then 32nds 15.073, 15.130, 15.184, 15.279; full list `hits[]` class `clapper`.\n')
A('**Breakbeat chops / stutter edits** (full-band holes 15-150 ms, >= 18 dB): ' + ', '.join(f"{c['start']:.3f}-{c['end']:.3f}" for c in he['chops']) + '.\n')
A('**Silences** (mix < -50 dBFS or 30 dB under local): ' + ', '.join(f"{s['start']:.3f}-{s['end']:.3f} ({s['dur'] * 1000:.0f} ms)" for s in he['silences']) + '. Only 149.285-149.525 is a musical silence (> 150 ms) after the intro.\n')
A('**Drum drop-outs** (drums stem < -55 dB, >= 0.25 s): ' + ', '.join(f"{d['start']:.2f}-{d['end']:.2f}" for d in he['drum_dropouts']) + '.\n')
A('**Suona phrases** (low confidence: sustained harmonic energy 0.7-5 kHz in the "other" stem; guqin/pipa sustain can also trigger): ' + ', '.join(f"{s['start']:.2f}-{s['end']:.2f}" for s in he['suona_phrases'] if s['end'] - s['start'] >= 0.8) + ' (phrases >= 0.8 s; all in timing.json).\n')
A('**Risers** (low confidence; instrumental 4-16 kHz rising >= 9 dB): ' + ', '.join(f"{r['start']:.1f}-{r['end']:.1f}" for r in he['risers']) + '. None is a clear classic riser; the clearest swells are 37.9-43.9 (back into the pre-chorus) and 147.4-153.0 (into the bridge).\n')
A('**Sub**: crash + sub boom 149.720; sub drone enters 232.29 and cuts 237.840.\n')
tr = TJ['energy']['transitions']
A(f"**Width / filter (headband verse)**: width closes {tr['width_close']:.3f}, filter closes {tr['filter_close']:.3f}, filter opens {tr['filter_open']:.3f}, width opens {tr['width_open']:.3f}. Per-0.5 s values in `energy`; 10 ms curves in work/audio/energy.npz.\n")
A('## Verification\n')
w = V['words_vs_vocal_onsets']
A(f"- Word starts vs nearest vocal-stem onset peak (+-80 ms): high-confidence words median {w['high']['median_ms']} ms, median |d| {w['high']['median_abs_ms']} ms, "
  f"90th pct {w['high']['p90_abs_ms']} ms, {w['high']['frac_within_42ms'] * 100:.0f} % within one frame (42 ms); medium {w['medium']['median_abs_ms']} / {w['medium']['p90_abs_ms']} ms; low {w['low']['median_abs_ms']} / {w['low']['p90_abs_ms']} ms.")
e = V['energy_onset_refinement']
A(f"- MMS starts lag the vocal-energy rise after a gap (nasals, voiced consonants): {e['n_words_moved']} words were moved to the rise (median {e['median_shift_ms']} ms, cap 130 ms).")
d = V['words_rf_vs_demucs']; A(f"- Same alignment on two independent vocal separations (BS-RoFormer vs htdemucs): median |d| {d['median_abs_ms']} ms, 90th pct {d['p90_abs_ms']} ms, {d['frac_within_42ms'] * 100:.0f} % within 42 ms.")
x = V['words_vs_whisper']; A(f"- Whisper word starts (independent ASR) run {-x['median_ms']:.0f} ms earlier than ours on average (median |d| {x['median_abs_ms']} ms): Whisper's singing timestamps are early; the vocal-stem envelope supports our times.")
b = V['beats_vs_drum_onsets']; A(f"- Beats vs drum onsets: {b['frac_within_42ms'] * 100:.0f} % within 42 ms (max {b['max_abs_ms']} ms). Refined vs raw beat_this: median |d| {V['beats_vs_beat_this_raw']['median_abs_ms']} ms.")
c = V['crash_vs_mix_attack']; A(f"- Crashes vs steepest mix-level rise +-40 ms: median {c['median_ms']} ms, 90th pct |d| {c['p90_abs_ms']} ms.")
A('')
A('## Low-confidence areas\n')
for t in ['Hook 1 "Born fully formed (born fully formed) He bowed": MMS could not read the dense octave duet; times are vocal-onset peaks (medium).',
          'Hook 1 "no lullaby" (65.77?) and the rap tail "身外身法 谁是真身 (谁是真身) 问了也白问" (118.0-121.5): low alignment scores.',
          'All drop-2 echoes and "No cradle, no song / 一通百通" (196.6-202.8): low; the vocal is continuous and the 200.675-201.08 chop sits inside "一通".',
          'Singer of outro lines 67-68 (classifier vs sheet).',
          'Hit classes (clapper/snare/kick/perc) are heuristic; crash and low-drum classes are more reliable. Suona phrases and risers are low confidence.',
          'Beat grid in the drum-less build (177.6-189.8) and the intro bar phase.']: A(f'- {t}')
open(os.path.join(ROOT, 'docs/AUDIO_MAP.md'), 'w').write('\n'.join(L) + '\n'); print('written', len(L), 'lines')

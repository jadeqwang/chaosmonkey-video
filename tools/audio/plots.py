"""analysis/plots/: 00_overview.png (waveform + sections + stem energies + width + brightness) and one zoomed
spectrogram per section (NN_<name>.png, ~1800 px wide) with beats, downbeats, classified hits and lyric words."""
import json, os, warnings, numpy as np, soundfile as sf, librosa, matplotlib
warnings.filterwarnings('ignore'); matplotlib.use('Agg'); import matplotlib.font_manager as fm, matplotlib.pyplot as plt
fm.fontManager.addfont('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Droid Sans Fallback']
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = os.path.join(ROOT, 'work')
OUT = os.path.join(ROOT, 'analysis/plots'); os.makedirs(OUT, exist_ok=True)
TJ = json.load(open(os.path.join(ROOT, 'analysis/timing.json'))); E = np.load(os.path.join(W, 'audio/energy.npz')); T = E['T']
y, SR = sf.read(os.path.join(W, 'audio/song.wav')); m = y.mean(1); DUR = len(m) / SR
SC = plt.cm.tab20(np.linspace(0, 1, 20))
HC = dict(gong_crash='#d62728', low_drum='#8c564b', kick='#1f77b4', snare='#2ca02c', clapper='#ff7f0e', perc='#999999')
SINGC = dict(mom='#7b3294', child='#008837', both='#c51b7d')
def sm(x, n): return np.convolve(x, np.ones(n) / n, 'same')
# ------------- overview
fig, ax = plt.subplots(5, 1, figsize=(30, 15), sharex=True, gridspec_kw=dict(height_ratios=[1.3, 1.6, 1, 1, 0.5]))
step = 480; env = np.abs(m[:len(m) // step * step]).reshape(-1, step).max(1); te = np.arange(len(env)) * step / SR
ax[0].fill_between(te, -env, env, color='0.3', lw=0); ax[0].set_ylabel('waveform')
for i, s in enumerate(TJ['sections']):
    for a in ax: a.axvspan(s['start'], s['end'], color=SC[i % 20], alpha=0.18, lw=0)
    ax[0].text((s['start'] + s['end']) / 2, 0.95, f"{s['name']}\n{s['start']:.2f}", ha='center', va='top', fontsize=10, weight='bold')
for k, c in (('mix', 'k'), ('vocals', '#c51b7d'), ('drums', '#1f77b4'), ('bass', '#8c564b'), ('other', '#ff7f0e')):
    ax[1].plot(T, sm(E['rms_' + k], 50), label=k, color=c, lw=1)
ax[1].set_ylim(-70, -5); ax[1].set_ylabel('RMS dBFS (0.5 s smooth)'); ax[1].legend(loc='lower left', ncol=5)
ax[2].plot(T, sm(E['instrumental_lrcorr'], 25), color='#1f77b4', label='instrumental L/R corr (1 = mono)')
ax[2].plot(T, sm(E['mix_lrcorr'], 25), color='0.5', lw=.7, label='mix L/R corr'); ax[2].set_ylim(0, 1.02); ax[2].legend(loc='lower left')
tr = TJ['energy']['transitions']
for k in ('width_close', 'width_open'): ax[2].axvline(tr[k], color='r', ls='--'); ax[2].text(tr[k], 0.05, f" {k} {tr[k]:.2f}", color='r', fontsize=9)
ax[3].plot(T, sm(E['instrumental_hf_db'], 25), color='#9467bd', label='instrumental >4 kHz share dB (filter)'); ax[3].legend(loc='lower left')
for k in ('filter_close', 'filter_open'): ax[3].axvline(tr[k], color='r', ls='--'); ax[3].text(tr[k], -60, f" {k} {tr[k]:.2f}", color='r', fontsize=9)
for l in TJ['lines']:
    ax[4].plot([l['start'], l['end']], [0.5, 0.5] if l['singer'] != 'both' else [0.2, 0.2], color=SINGC[l['singer']], lw=6, solid_capstyle='butt')
ax[4].set_yticks([]); ax[4].set_ylabel('lines\n(mom/child/both)')
for sp in TJ['sync_points']:
    if sp['kind'] in ('gong_crash', 'silence', 'edit', 'transition', 'dropout'): ax[0].axvline(sp['t'], color='r', lw=.6, alpha=.6)
ax[4].set_xticks(np.arange(0, DUR, 5)); ax[4].set_xlim(0, DUR); ax[4].set_xlabel('seconds')
for a in ax: a.grid(alpha=.25)
plt.suptitle('Chaos Monkey (reformatted for duet) - overview. Red lines: crashes, silences, edits, drop-outs, width/filter transitions', fontsize=14)
plt.tight_layout(); plt.savefig(os.path.join(OUT, '00_overview.png'), dpi=60); plt.close()
# ------------- per section
BT = TJ['beats']; DB = {d['t'] for d in TJ['downbeats']}
for i, s in enumerate(TJ['sections']):
    a, b = max(0, s['start'] - 0.5), min(DUR, s['end'] + 0.5)
    if b - a < 4: c = (a + b) / 2; a, b = max(0, c - 3), min(DUR, c + 3)
    seg = m[int(a * SR):int(b * SR)]
    S = librosa.amplitude_to_db(np.abs(librosa.stft(seg, n_fft=2048, hop_length=240)), ref=np.max)
    fig, ax = plt.subplots(4, 1, figsize=(30, 14), sharex=True, gridspec_kw=dict(height_ratios=[3.2, 1.0, 1.1, 1.6]))
    ax[0].imshow(S, origin='lower', aspect='auto', extent=[a, b, 0, SR / 2], cmap='magma', vmin=-80)
    ax[0].set_yscale('symlog', linthresh=500); ax[0].set_ylim(30, 20000); ax[0].set_ylabel('mix spectrogram Hz')
    for x in BT:
        if a <= x['t'] <= b:
            ax[0].axvline(x['t'], color='w' if x['t'] in DB else 'c', lw=1.6 if x['t'] in DB else .5, alpha=.8 if x['confidence'] != 'low' else .35)
            if x['t'] in DB: ax[0].text(x['t'], 16000, f"{x['bar']}", color='w', fontsize=9)
    k = (T >= a) & (T <= b)
    for kk, c in (('vocals', '#c51b7d'), ('drums', '#1f77b4'), ('bass', '#8c564b'), ('other', '#ff7f0e')): ax[1].plot(T[k], E['rms_' + kk][k], color=c, lw=.8, label=kk)
    ax[1].set_ylim(-70, -5); ax[1].legend(loc='lower left', ncol=4, fontsize=8); ax[1].set_ylabel('stem RMS dB')
    for h in TJ['hits']:
        if a <= h['t'] <= b: ax[2].vlines(h['t'], 0, h['strength'], color=HC[h['cls']], lw=1.5)
    for c, col in HC.items(): ax[2].plot([], [], color=col, label=c)
    he = TJ['hit_events']
    for x in he['silences']:
        if x['end'] >= a and x['start'] <= b: ax[2].axvspan(x['start'], x['end'], color='k', alpha=.3)
    for x in he['chops']:
        if a <= x['start'] <= b: ax[2].axvspan(x['start'], x['end'], color='r', alpha=.4)
    for x in he['suona_phrases']:
        if x['end'] >= a and x['start'] <= b: ax[2].plot([x['start'], x['end']], [1.05, 1.05], color='#e377c2', lw=4)
    ax[2].set_ylim(0, 1.12); ax[2].legend(loc='upper left', ncol=6, fontsize=8); ax[2].set_ylabel('hits (strength)\nred=chop black=silence\npink bar=suona?')
    lv = 0
    for l in TJ['lines']:
        if l['end'] < a or l['start'] > b: continue
        col = SINGC[l['singer']]
        for w in l['words']:
            if a <= w['start'] <= b:
                ax[3].axvline(w['start'], color=col, lw=.6, alpha=.6)
                ax[3].text(w['start'], 0.15 + 0.4 * (lv % 2), w['w'] + ('' if w['confidence'] == 'high' else ('~' if w['confidence'] == 'medium' else '?')),
                           fontsize=11, color=col, rotation=60, alpha=1 if not l['echo'] else .7, style='italic' if l['echo'] else 'normal')
        lv += 1
    for kk, c in SINGC.items(): ax[3].plot([], [], color=c, lw=4, label=kk)
    ax[3].legend(loc='upper right', fontsize=9); ax[3].set_yticks([]); ax[3].set_ylim(0, 1.1); ax[3].set_ylabel('words (~ medium, ? low)')
    ax[3].set_xlim(a, b); step = 0.25 if b - a < 15 else 0.5
    ax[3].set_xticks(np.arange(np.ceil(a / step) * step, b, step)); ax[3].tick_params(axis='x', labelsize=8, rotation=90)
    for x in ax: x.axvline(s['start'], color='lime', lw=2); x.axvline(s['end'], color='lime', lw=2)
    for x in ax[1:]: x.grid(alpha=.3)
    fig.suptitle(f"{i + 1:02d} {s['name']}  {s['start']:.3f}-{s['end']:.3f} s  ({s['bars']} bars, {s['bpm']} BPM)  - {s['description'][:150]}", fontsize=12)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, f"{i + 1:02d}_{s['name']}.png"), dpi=60); plt.close()
    print(s['name'])

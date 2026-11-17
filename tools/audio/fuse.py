"""Word/line timing -> work/audio/words.json
1. Per section, ONE sequential MMS_FA pass over a window around the section's lines (window from the global pass in
   align_rf.json, +-0.5 s, clipped to neighbouring sections), with the parenthetical echoes INLINE in sung order
   (Suno sings the echoes after the phrase; the karaoke lead/backing split does not isolate them). Run on the BS-RoFormer
   vocal stem ('rf', the timing authority) and on the htdemucs vocal stem ('dm', second opinion).
2. Word confidence: high = rf score >= 0.35 and |rf-dm| start <= 40 ms; medium = score >= 0.1 and |rf-dm| <= 100 ms;
   low otherwise. Echo words are capped at medium.
3. Line end: last word end extended while the vocal-stem RMS stays within 20 dB of the line's peak (held notes),
   up to the next line start / +2 s.
4. Residuals vs the vocal stem: nearest spectral-flux onset peak of the vocal stem within +-80 ms of each word start.
Overrides (from inspection) in OVR below, each with its reason.
"""
import json, os, sys, numpy as np, scipy.signal as ss
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sung, align
ROOT = align.ROOT; W = os.path.join(ROOT, 'work')
L = sung.build(); G = json.load(open(os.path.join(W, 'asr/align_rf.json')))
def gspan(l):
    k = str(l['id']) if not l['echo'] else f"{l['id']}_vocals"
    return G[k][0]['start'], G[k][-1]['end']
secs = []
for l in L:
    if not secs or secs[-1][0] != l['section']: secs.append((l['section'], []))
    secs[-1][1].append(l)
Y = {k: align.load16(os.path.join(W, f'stems/{p}.wav')) for k, p in (('rf', 'vocals'), ('dm', 'vocals_demucs'))}
res = {}
for si, (name, ls) in enumerate(secs):
    a = min(gspan(l)[0] for l in ls if not l['echo']) - 0.5; b = max(gspan(l)[1] for l in ls) + 0.8
    if si > 0: a = max(a, max(gspan(l)[1] for l in secs[si - 1][1] if not l['echo']) - 0.05)
    if si + 1 < len(secs): b = min(b, min(gspan(l)[0] for l in secs[si + 1][1] if not l['echo']) + 0.05)
    a = round(a, 2); b = round(b, 2)
    toks = [u for l in ls for u in l['align']]
    for k, y in Y.items():
        E = align.emissions(y[int(a * 16000):int(b * 16000)], win=b - a + 1, hop=b - a + 1)
        out = align.fa(E, toks, t0=a); i = 0
        for l in ls:
            for wi, w in enumerate(l['words']):
                res.setdefault((l['id'], wi), {})[k] = out[i]; i += 1
    print(name, a, b, flush=True)
# vocal onset envelope + rms (5 ms)
EV = np.load(os.path.join(W, 'audio/env.npz')); TT = EV['T']; ON = EV['onset_vocals']; RV = EV['rms_vocals']
pk, _ = ss.find_peaks(ON, height=np.percentile(ON, 80), distance=6); PT = TT[pk]
words = []
for l in L:
    ws = []
    for wi, w in enumerate(l['words']):
        r, d = res[(l['id'], wi)]['rf'], res[(l['id'], wi)]['dm']
        dd = abs(r['start'] - d['start'])
        conf = 'high' if r['score'] >= 0.35 and dd <= 0.04 else ('medium' if r['score'] >= 0.1 and dd <= 0.1 else 'low')
        if l['echo'] and conf == 'high': conf = 'medium'
        j = np.argmin(np.abs(PT - r['start'])); resid = PT[j] - r['start']
        ws.append(dict(w=w, start=r['start'], end=r['end'], score=r['score'], dm_start=d['start'], confidence=conf,
                       onset_resid=round(float(resid), 3) if abs(resid) <= 0.08 else None))
    words.append(dict(id=l['id'], words=ws))
# line ends from RMS
for k, l in enumerate(L):
    ws = words[k]['words']; s, e = ws[0]['start'], ws[-1]['end']
    nxt = min([words[j]['words'][0]['start'] for j in range(k + 1, len(L)) if not L[j]['echo']] + [e + 2.0])
    lim = min(nxt, e + 2.0)
    m = (TT >= s) & (TT <= e); peak = RV[m].max() if m.any() else -30
    j = np.searchsorted(TT, e)
    while j < len(TT) and TT[j] < lim and RV[j] > peak - 20: j += 1
    words[k]['end_rms'] = round(float(max(e, TT[min(j, len(TT) - 1)])), 3)
json.dump(words, open(os.path.join(W, 'audio/words.json'), 'w'), ensure_ascii=False, indent=0)
for l, wl in zip(L, words):
    print(f"{l['id']:2d} {wl['words'][0]['start']:7.2f}-{wl['end_rms']:7.2f} " + ' '.join(f"{w['w']}@{w['start']:.2f}{'' if w['confidence']=='high' else ('~' if w['confidence']=='medium' else '?')}" for w in wl['words']))

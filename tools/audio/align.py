"""Forced alignment of the known lyric (sung.py) with torchaudio MMS_FA (wav2vec2, 1100+ languages, romanized chars,
20 ms frames). Mandarin characters are aligned via toneless pinyin.
Pass 1 (global): ONE Viterbi pass over the whole song for all non-echo lines on the given vocal stem
  (emissions computed in 30 s windows, 10 s overlap, centres stitched).
Pass 2 (echo): each parenthetical echo aligned locally inside the gap/window around its neighbours, on both the
  karaoke 'backing' stem and the full vocal stem; window = [prev line word-before-last start, next line 2nd word end].
    python tools/audio/align.py work/stems/vocals.wav tag  -> work/asr/align_<tag>.json
"""
import json, os, sys
import numpy as np, soundfile as sf, librosa, torch, torchaudio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import sung
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=False).cuda().eval(); DIC = bundle.get_dict(star=None)

def load16(p):
    y, sr = sf.read(p); y = y.mean(1) if y.ndim > 1 else y
    return librosa.resample(y, orig_sr=sr, target_sr=16000, res_type='soxr_hq').astype(np.float32)

def emissions(y16, win=30.0, hop=20.0):
    dur = len(y16) / 16000; outs = []; a = 0.0; FR = 0.02
    nF = int(np.ceil(dur / FR)) + 2; E = None
    while True:
        b = min(dur, a + win); seg = y16[int(a * 16000):int(b * 16000)]
        x = torch.from_numpy(seg / (np.abs(seg).max() + 1e-9) * 0.7)[None].float().cuda()
        with torch.inference_mode(): em, _ = model(x)
        em = torch.log_softmax(em, -1)[0].cpu().numpy()
        if E is None: E = np.zeros((nF, em.shape[1]), np.float32)
        f0 = int(round(a / FR)); n = min(len(em), nF - f0)
        kf = 0 if a == 0 else int((win - hop) / 2 / FR); kt = n if b >= dur else n - int((win - hop) / 2 / FR)
        E[f0 + kf:f0 + kt] = em[kf:kt]
        if b >= dur - 0.05: E = E[:f0 + n]; break
        a += hop
    return E

def fa(E, units, t0=0.0):
    toks = [DIC[c] for u in units for c in u if c in DIC]
    em = torch.from_numpy(E)[None]
    ali, sc = torchaudio.functional.forced_align(em, torch.tensor([toks], dtype=torch.int32), blank=0)
    spans = torchaudio.functional.merge_tokens(ali[0], sc[0].exp())
    out = []; k = 0
    for u in units:
        m = len([c for c in u if c in DIC]); sp = spans[k:k + m]; k += m
        out.append(dict(start=round(t0 + sp[0].start * 0.02, 3), end=round(t0 + sp[-1].end * 0.02, 3),
                        score=round(float(np.mean([s.score for s in sp])), 3),
                        chars=[[round(t0 + s.start * 0.02, 3), round(t0 + s.end * 0.02, 3)] for s in sp]))
    return out

if __name__ == '__main__':
    voc, tag = sys.argv[1], sys.argv[2]
    L = sung.build(); y16 = load16(voc); E = emissions(y16)
    main = [l for l in L if not l['echo']]
    units = [u for l in main for u in l['align']]
    res = fa(E, units); k = 0; out = {}
    for l in main:
        out[l['id']] = [dict(w=w, **res[k + i]) for i, w in enumerate(l['words'])]; k += len(l['words'])
    # echoes
    yb = load16(os.path.join(ROOT, 'work/stems/backing.wav')); EB = emissions(yb)
    for l in L:
        if not l['echo']: continue
        MI = [l2['id'] for l2 in main]; prev = max(i for i in MI if i < l['id']); nxt = min([i for i in MI if i > l['id']], default=None)
        a = out[prev][max(0, len(out[prev]) - 2)]['start']
        b = out[nxt][min(1, len(out[nxt]) - 1)]['end'] if nxt is not None else a + 4
        b = max(b, a + 1.5)
        # several echoes may share the window (drop2 '(formed) (formed)'): align them together
        group = [g for g in L if g['echo'] and max(i for i in MI if i < g['id']) == prev]
        if l['id'] != group[0]['id']: continue
        gu = [u for g in group for u in g['align']]
        for nm, EE in (('backing', EB), ('vocals', E)):
            fa_ = fa(EE[int(a / 0.02):int(b / 0.02)], gu, t0=round(int(a / 0.02) * 0.02, 3)); k = 0
            for g in group:
                out.setdefault(f"{g['id']}_{nm}", [dict(w=w, **fa_[k + i]) for i, w in enumerate(g['words'])]); k += len(g['words'])
    os.makedirs(os.path.join(ROOT, 'work/asr'), exist_ok=True)
    json.dump({str(k): v for k, v in out.items()}, open(os.path.join(ROOT, f'work/asr/align_{tag}.json'), 'w'), indent=0, ensure_ascii=False)
    for l in L:
        for key in ([l['id']] if not l['echo'] else [f"{l['id']}_backing", f"{l['id']}_vocals"]):
            ws = out[key]
            print(f"{str(key):11s} {ws[0]['start']:7.2f}-{ws[-1]['end']:7.2f} " + ' '.join(f"{w['w']}@{w['start']:.2f}({w['score']:.2f})" for w in ws))

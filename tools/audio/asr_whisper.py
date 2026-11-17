"""faster-whisper large-v3 (halys model cache) on a vocal stem, word timestamps; passes: en, zh (no prompt).
Used only as an independent cross-check of the forced alignment (never as timing authority).
    python tools/audio/asr_whisper.py work/stems/vocals.wav   -> work/asr/whisper.json"""
import json, os, sys
import torch  # noqa
from faster_whisper import WhisperModel
import numpy as np, soundfile as sf, librosa
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
model = WhisperModel('large-v3', device='cuda', compute_type='float16', download_root='/home/jade/Documents/halys-video/work/models/whisper')
y, sr = sf.read(sys.argv[1]); y = y.mean(1) if y.ndim > 1 else y
y16 = librosa.resample(y, orig_sr=sr, target_sr=16000, res_type='soxr_hq').astype(np.float32)
res = {}
for lang in ('en', 'zh'):
    segs, info = model.transcribe(y16, language=lang, word_timestamps=True, beam_size=5, vad_filter=False,
                                  condition_on_previous_text=False, temperature=0.0)
    out = []
    for s in segs:
        out.append(dict(start=s.start, end=s.end, text=s.text.strip(),
                        words=[dict(w=w.word.strip(), start=round(w.start, 3), end=round(w.end, 3), p=round(w.probability, 3)) for w in s.words]))
        print(f'{lang} {s.start:7.2f}-{s.end:7.2f} {s.text.strip()}', flush=True)
    res[lang] = out
os.makedirs(os.path.join(ROOT, 'work/asr'), exist_ok=True)
json.dump(res, open(os.path.join(ROOT, 'work/asr/whisper.json'), 'w'), indent=1, ensure_ascii=False)

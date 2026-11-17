"""Neural beat/downbeat tracking with beat_this (CPJKU, ISMIR 2024; checkpoint 'final0', GPU, no DBN) on the song.
Used for the intro segment of the grid and as an independent cross-check of the onset-anchored grid.
    .venv/bin/python tools/audio/beat_this_run.py   -> work/audio/beat_this.json {beats, downbeats}"""
import json, os
from beat_this.inference import File2Beats
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
b, d = File2Beats(checkpoint_path='final0', device='cuda', dbn=False)(os.path.join(ROOT, 'work/audio/song.wav'))
json.dump(dict(beats=[float(x) for x in b], downbeats=[float(x) for x in d]), open(os.path.join(ROOT, 'work/audio/beat_this.json'), 'w'))
print(len(b), 'beats', len(d), 'downbeats')
b2, d2 = File2Beats(checkpoint_path='final0', device='cuda', dbn=False)(os.path.join(ROOT, 'work/stems/instrumental.wav'))
json.dump(dict(beats=[float(x) for x in b2], downbeats=[float(x) for x in d2]), open(os.path.join(ROOT, 'work/audio/beat_this_inst.json'), 'w'))
print(len(b2), 'beats (instrumental)', len(d2), 'downbeats')

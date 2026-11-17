# tools/audio: rebuilding the timing map

Builds `analysis/timing.json`, `analysis/verification.json`, `analysis/click_check.wav`, `analysis/plots/*.png` and `docs/AUDIO_MAP.md`
from `inputs/Chaos Monkey - reformatted for duet.wav` (never modified). Method and tools adapted from halys-video/tools/audio.
Uses halys-video's venv (no new installs): `P=/home/jade/Documents/halys-video/.venv/bin/python`. Models: BS-RoFormer checkpoint and
Whisper cache from halys-video/work/models, the mel-band-roformer karaoke checkpoint from moongazing (hard-linked into work/models),
MMS_FA and beat_this from ~/.cache/torch/hub. GPU used by steps 2-6.

| Step | Command | Writes |
|---|---|---|
| 1 | `$P tools/audio/check_stems.py` | prints: supplied spliced stems vs this file (they do not align; drift 0 -> +2 s) |
| 2 | `$P tools/audio/stems.py` | `work/audio/song.wav`, `work/stems/{vocals,instrumental,drums,bass,other,vocals_demucs,lead,backing}.wav` |
| 3 | `$P tools/audio/features.py` | `work/audio/env.npz` (5 ms onset/RMS envelopes), `bandflux.npz`, `loudness.npz` |
| 4 | `$P tools/audio/energy.py` | `work/audio/energy.npz` (RMS per stem, width, L/R corr, centroid, rolloff, >4 kHz share; 10 ms and 0.5 s) |
| 5 | `$P tools/audio/beat_this_run.py` | `work/audio/beat_this.json`, `beat_this_inst.json` |
| 6 | `$P tools/audio/asr_whisper.py work/stems/vocals.wav` | `work/asr/whisper.json` (cross-check only) |
| 7 | `$P tools/audio/align.py work/stems/vocals.wav rf` (also `vocals_demucs dm`, `lead lead`) | `work/asr/align_<tag>.json` (global MMS_FA pass, pinyin for Mandarin) |
| 8 | `$P tools/audio/singer.py` | `work/audio/singer.npz` (mom/child timbre classifier, F0) |
| 9 | `$P tools/audio/fuse.py` | `work/audio/words.json` (per-section sequential re-alignment with echoes inline, rf + dm stems) |
| 10 | `$P tools/audio/onsets.py` | `work/audio/onsets.json` (drums/other onsets + band descriptors) |
| 11 | `$P tools/audio/events.py` | `work/audio/events.json` (beat grid, hit classes, fills, chops, silences, suona, risers, width/filter transitions) |
| 12 | `$P tools/audio/build_timing.py` | `analysis/timing.json` (sections, word overrides, energy refinement, sync points) |
| 13 | `$P tools/audio/verify.py` then step 12 again | `analysis/verification.json`, `analysis/click_check.wav` |
| 14 | `$P tools/audio/plots.py` | `analysis/plots/00_overview.png`, `NN_<section>.png` |
| 15 | `$P tools/audio/build_md.py` | `docs/AUDIO_MAP.md` |

Diagnostics: `greedy.py STEM a b` (free CTC character decode with times), `local_align.py STEM a b "tokens"` (sequential re-alignment
of a window). Hand decisions live in `build_timing.py` (`SEC` section boundaries with the event each sits on, `OVR` word overrides
with reasons, `ISO` isolated hits) and `sung.py` (lyric text, singer per sheet, pinyin).

# Cut tools

Run from any directory with `/home/jade/Documents/halys-video/.venv/bin/python` (PyYAML, Pillow, PyAV required). Uses `/usr/bin/ffmpeg` and `/usr/bin/ffprobe` and the repository's LXGW WenKai font.

```bash
PY=/home/jade/Documents/halys-video/.venv/bin/python
$PY tools/cut/build.py
$PY tools/cut/assemble.py --name animatic_v0 --profile animatic
$PY tools/cut/contact.py --name animatic_v0
$PY tools/cut/assemble.py --name sequence_test --profile preview --range A1:C6
$PY tools/cut/assemble.py --name selected --profile preview --only A1,B2 --clean
$PY tools/cut/assemble.py --name final --profile master --audio '/path/to/song.wav'
```

`build.py` validates times and ids before writing `docs/shots.json` and `docs/SHOTLIST.md`. Shot boundaries use Python `round(t*24)`; out frames are exclusive. The JSON object contains `fps`, `end`, `sequences`, and `shots`. Lyrics retain their original song-clock timestamps. `nearest_beat_in.offset_ms` is the snapped cut minus the nearest beat (positive means cut follows beat).

Assembly selects picks from `docs/picks.json` (`{"A1": {"src": "path.mp4", "in": 0, "rate": 1}}`), then comps, JPG/PNG keyframes, then slates. Pick paths are repository-relative or absolute. Speed 2 means twice as fast. Videos are fitted with a centre crop; stills push in 4%. Source audio is discarded. Short videos freeze at their last frame and display SHORT for animatic/preview; master reports all short shots before rendering. An in-point past all source frames is an error in every profile.

Burn-ins are drawn with Pillow using the repository font on RGB frames streamed from FFmpeg and piped back to FFmpeg for encoding. Text and timecodes never enter FFmpeg filter expressions.

Animatic: 960×540 CRF 20, shot id, song timecode and timed lyrics. Preview: 960×540 CRF 18, small shot id (`--clean` removes it). Master: 1920×1080 CRF 14. All use 24 fps CFR, yuv420p, BT.709 tags and AAC 320k. The song is sliced at frame-snapped shot boundaries; final audio is padded or trimmed to the video length (the full song's rounded frame boundary differs from its end by less than one frame).

`--range` includes both endpoint ids in shot-list order. `--only` filters that range (or the full list); disjoint selections concatenate the corresponding song intervals. No shot is retimed to close selection gaps.

Renders are cached in `work/cut/NAME/ID_HASH/shot.mp4` using source mtime/size, shot metadata, render parameters, font mtime and renderer code. Delete that directory to force rebuilding. The final MP4 is in `media/cut/NAME.mp4`. Assembly counts decoded frames per render and verifies final decoded frame count, A/V durations, fps, pixel format and colour tags. `work/cut/NAME/manifest.json` records selected shots and output offsets for contact extraction. Reassemble before generating contacts after a shot-list change.

`contact.py` decodes the finished MP4 and creates `work/cut/NAME/contact_SEQ.jpg` for each included sequence, with one row per shot and first/middle/last frames. Labels show both song and cut timecodes. Sheets are 2220 pixels wide.

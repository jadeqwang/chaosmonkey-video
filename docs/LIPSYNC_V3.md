# Lip-sync v3 (DRAFT, bake-off still running; updated as results land)

State 14:58: the gate tool is ready to use; the method is not chosen yet. Room teams: shoot keyframes and non-singing acting
first. For a singing shot make the start frame now as below; the take recipe follows here within the hour.

## Start frame for a singing take (already safe to make)
- gpt-image-2, v3 refs as in CANON §00 "Lip-sync start frame". Chest-up or closer, the singer's face at least a third of the
  frame height, three-quarter front or front (never profile), mouth and chin unobstructed, lips relaxed and just parted, no
  teeth. A face under about 150 px high at 720p cannot be measured and so cannot ship as a singing face.
- Save a 1920 px copy for the relay (`gen.py ref-image SRC OUT --max=1920`).

## The gate (every singing take must go through it)
```
PY=/home/jade/Documents/halys-video/.venv/bin/python
$PY tools/review/lipsync_gate.py TAKE.mp4 --t0 <song time of the take's frame 0> --name SHOT_takeN --check
#   -> work/review/lipsync_gate/SHOT_takeN_strip.jpg, _gate.json, _check.mp4 (take + song at the chosen placement)
# look at the strip (red cells: lips shut; grey cells: mouth open), watch _check.mp4 once, then record it:
$PY tools/review/lipsync_gate.py TAKE.mp4 --t0 T --shift <shift_f it printed> --name SHOT_takeN --eye "pass: ..." --log
```
`--t0` is the start of the audio window sent to the model. `shift_f` is the retime in frames (positive = play the take
later); in the comp place clip frame 0 at `place_frame0_at`. PASS needs the numbers AND `--eye pass`.

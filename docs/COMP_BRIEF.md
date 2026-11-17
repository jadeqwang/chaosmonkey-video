# Shot production brief (sequence teams)

For every agent that builds finished shots. Lead: Claude (Fable 5.2). Goal of this pass: a COMPLETE 540p cut of the whole
song by morning. A good shot delivered beats a perfect shot missing; but every shot must hold the look.

## Read first
1. `docs/TREATMENT.md` (the vision; the table "Glitch, in the tradition's own terms"; "Opera and wushu, where they live").
2. `docs/shots.yaml` + `docs/SHOTLIST.md` + `docs/shots.json`: your shots, exact frame counts, lyrics per shot.
3. `docs/AUDIO_MAP.md` and `analysis/timing.json`: cut and animate to MEASURED words, beats, hits and chops (about 137 BPM,
   drifting). Never to a constant BPM.
4. `tools/ink/README.md` (+ `tools/ink/examples/`, `tools/ink/NOTES.md`): the compositor. You write `shots/<ID>.py` against it.
5. `design/plates/PLATES.md` (plates, layers, registration, coverage), `design/characters/CANON.md`, `refs/fonts/FONTS.md`,
   `design/text/` (proofed texts: use these files for every Chinese character on screen; never let a model draw writing).
6. `docs/VIDEO_BAKEOFF.md` (which video model for which job, prompts, what to do to each model's output; may still be
   in progress: read what is there), `docs/PIPELINE_RECON.md` §3 (gen.py / cf.py calls, relay rules).
7. The brainstorm (`inputs/…brainstorm.md`): "Whitespace and camera", "The carved mountain" rules, "The third voice" rules.
8. `docs/research/OPERA_WUSHU.md` for anything on the stage register (亮相, 四击头, 锣鼓经 syllables: use only 仓 才 台).

## Deliverable per shot
- `shots/<ID>.py` (the tools.ink shot script; times on the song clock so `--t0/--t1` come from `docs/shots.json`).
- `media/comp/<ID>.mp4`: 960x540, 24 fps CFR, EXACTLY the shot's frame count (`docs/shots.json`), no audio. Render with
  `python -m tools.ink.run shots/<ID>.py --t0 IN --t1 OUT --size 960x540 --out media/comp/<ID>.mp4`
  (PY=/home/jade/Documents/halys-video/.venv/bin/python; run from the repo root). The script must also render at
  1920x1080 without changes (resolution-independent layout), for the later master.
- A row in `media/comp/LOG_<team>.md`: shot, status (done / weak / placeholder), sources used, QA numbers, what is weak.
- A review sheet per shot: `work/review/comp/<ID>.jpg` (8 frames incl. first and last). LOOK at it and fix what is wrong.

## Rules of the picture
- One world: paper, ink, stone, light. Nothing digital-looking: no glow blooms, no lens effects, no motion-graphics easing
  that feels like software, no pure black or white. Quiet shots: ONE thing moves. Camera: push in (entering the story),
  travel right to left (time), pull back (scale; only in D5 and J2-J5). Otherwise the camera holds.
- Whitespace is the subject: meet the shot's `ink` budget (`python -m tools.ink.qa coverage … --budget N`), and the squint
  test. Mist, water, sky are bare paper.
- All shots inside the book share ONE paper (Paper 'new' in 1988 light, 'aged' in 2026). Continuity across a cut matters:
  check the last frame of the previous shot and the first of the next (see neighbours' sheets in `work/review/comp/`).
- Loud sections (hook, bridge opening, drop 2): the paper is a stage. Hits get 亮相 freezes, seal strikes (仓 on the big
  crashes, 才/台 on lighter ones), rubbing flips and block mis-registration on the measured chops. Sparingly: two or three
  devices per shot, each locked to a measured event, never random.
- Lyrics on screen: sung words only, set as an inscription in the blank (English: EB Garamond; Chinese: LXGW WenKai, or
  崇羲篆體 where it is carved/sealed), appearing with the measured word onsets, small, with at most one red seal. Keep
  inside the centred 4:5 area. The lead may strip or restyle text globally later: make it one switch
  (`ctx.opts.get("lyrics", True)`).
- The carved mountain: 千字文 lines 1-160 only (fully covered by 崇羲篆體), vertical columns right to left, cinnabar in
  the cuts; light is raking sun, moon, neon or flashlight, warm, never blue-white, never pulsing. Gold happens only at the
  birth (C6/D-hook), the band (G2) and the halo (H5).
- No-AI test: every frame must be fully explained by the mother-daughter story or the myth.
- Monkey: canon is `design/characters/monkey/` (two plumes, cinnabar face patch, dark splashed-ink body, banded staff).

## Generation
- Spend is capped per team (see your task message) and logged by the tools; check `python tools/gen/spend.py`.
- The relay starts 2 jobs a minute for the whole project and is busy: submit early, in one batch, and build the comp
  while you wait (`gen.py wait … --timeout=3000` in the background). Every generated clip is keyed onto OUR paper with
  `Clip.prepare`/`key_paper` (never shown raw), usually played on twos, with a freeze on the hit.
- If a generation fails twice or is late, ship the shot with the procedural fallback (tools.ink strokes, splash,
  puppet-style hard re-posing of canon stills) and mark it "weak" in your log. Do not block the cut.
- Keep prompts and rejects beside the files. Do not commit (the lead commits). Do not edit other teams' shots.

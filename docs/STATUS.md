# Status checkpoint (resume from here)

Lead: Claude (Fable 5.2). Jade asleep; decisions: spend cap $600; stop at a complete 540p cut for review;
sound-design layer allowed (ElevenLabs etc.); checkpoint hourly; usage window resets 03:40 (resume then if paused).

Read first: `docs/TREATMENT.md`, then the brainstorm in `inputs/`.

## Checkpoint 1 — 2026-11-16 late evening
Done: treatment written and committed; branch `claude/video-production`.
Running (background agents, each writes its own file):
- pipeline recon -> `docs/PIPELINE_RECON.md` (+ copies halys tools into `tools/gen|review|edit`)
- timing map -> `analysis/timing.json`, `docs/AUDIO_MAP.md`, `analysis/plots/`
- reference paintings -> `refs/paintings/` + MANIFEST.md
- fonts and proofed texts -> `refs/fonts/FONTS.md`, `design/text/`
- opera/wushu bible -> `docs/research/OPERA_WUSHU.md`
Next: shot list to measured timing (`docs/SHOTLIST.md`, `docs/shots.json`); model bake-offs; 3D rooms
(Blender not installed; Three.js exists at merge-me-back-to-main/engine); character sheets; slate animatic;
bulk generation; comp; sound layer; 540p preview; morning report `docs/MORNING.md`.
If an agent's output file is missing on resume, relaunch that agent (briefs are reproducible from this list).

## Checkpoint 2 — 2026-11-16 23:54
Done: recon manual (`docs/PIPELINE_RECON.md`), tools copied (`tools/gen|review|edit`), CF ids in `work/`, cap $600 set in
`tools/gen/spend.py`; fonts + proofed texts (`refs/fonts/FONTS.md`, `design/text/`; seal font = 崇羲篆體, 千字文 lines 1-160
fully covered); opera bible (`docs/research/OPERA_WUSHU.md`); timing map (`analysis/timing.json`, `docs/AUDIO_MAP.md`;
supplied stems did not match, agent re-separated into `work/stems/`); shot list v1 (`docs/shots.yaml`, 63 shots).
Running: painting library; ink compositor (`tools/ink/`, notes in `tools/ink/NOTES.md`); image look bake-off
(`docs/LOOK_BAKEOFF.md`, $25); codex cut tooling (`work/codex/job_cut.md` -> `tools/cut/`, log `work/codex/log.txt`);
Three.js room blockouts (`layout/`, `media/layout/`); sound layer (`docs/SOUND.md`, $20).
Next (lead): review look bake-off -> lock rendering hand + models; design lock (character sheets, monkey design,
storybook spreads); video bake-off (ink mist, ink figure/staff, character acting, lip-sync on Seedance 2.5 with automatic
lag measurement); then sequence teams A-L produce shots -> `media/comp/<ID>.mp4`; assemble preview; `docs/MORNING.md`.
Spend: $0 at time of writing (look bake-off in progress).

## Checkpoint 3 — 2026-11-17 00:32
Done since last: ink compositor (`tools/ink/`, README + NOTES; cliff carving needs a real rock plate and tuning);
sound layer v1 (`docs/SOUND.md`, `media/sound/mix_v1*.wav`, ending variants A/B/C; agent recommends A = hard cut);
I1 cut moved to the kick at 177.193.
Running: image look bake-off (outputs in `media/look/L1..L10`; early read: ink-wash "painting of night" rooms work,
Mama renders too old); painting library; codex cut tooling; Three.js blockouts.
Next: lock rendering hand + models from `docs/LOOK_BAKEOFF.md`; design lock; video bake-off; sequence teams.
Spend: TOTAL $10.50 of $600 cap  (118 billed items; list-price estimates)

## Checkpoint 4 — 2026-11-17 00:44
LOCKED after image bake-off (`docs/LOOK_BAKEOFF.md`): rendering hand (a) = people in fine line + wash on xuan, rooms as
ink-wash paintings of night (refs `media/look/L5/nbp_a_v2.jpg`, `L6/nbp_a_v2.jpg`); monkey canon = `media/look/L3/sd5_v2.jpg`;
models: Nano Banana Pro (rooms, people), Qwen/NBP/Seedream (plates), GPT Image 2 (脸谱 grid, puppets). Neon sign is built in code.
Done: cut tooling works (`tools/cut/`; `media/cut/animatic_v0.mp4` = slate animatic, 65 shots, 5720 frames).
Note: codex headless needs `< /dev/null` or it hangs.
Running: character + monkey canon (`design/characters/CANON.md`, $25); video bake-off (`docs/VIDEO_BAKEOFF.md`, $70);
plates + elements (`design/plates/PLATES.md`, $45); painting library; Three.js blockouts (`layout/NOTES.md`).
Next: when canon + video bake-off + blockouts land -> sequence teams produce shots into `media/comp/<ID>.mp4`
(stage/book shots can start as soon as plates groups B/D/F are checkpointed) -> assemble preview_v1 -> `docs/MORNING.md`.
Spend: TOTAL $10.57 of $600 cap  (119 billed items; list-price estimates)

## Checkpoint 5 — 2026-11-17 01:18
Done: room blockouts (`layout/`, `media/layout/`, 39 setups, sidecars with page/pane quads; `docs/LAYOUT.md`);
painting library (422 images, `refs/paintings/MANIFEST.md`); character + monkey canon
(`design/characters/CANON.md`, `_overview.jpg`; drift: Jade's jacket trim in medium shots, Mama's small hand gestures);
G4 is now shadow-only (18 lip-sync shots); keyframe brief (`docs/KEYFRAME_BRIEF.md`).
Running: attic keyframes (`media/kf/LOG_attic88.md`, $18); bedroom+car keyframes (`media/kf/LOG_bed26*.md`, $16);
video bake-off (`docs/VIDEO_BAKEOFF.md`); plates (`design/plates/PLATES.md`).
Next: on video bake-off verdict -> animate room keyframes + lip-sync; book/stage sequence teams build comps in tools/ink
from plates; assemble preview_v1; morning report.
Spend: TOTAL $79.08 of $600 cap  (287 billed items; list-price estimates)

## Checkpoint 6 — 2026-11-17 01:36
Production started. Brief for all shot teams: `docs/COMP_BRIEF.md`. Each team logs to `media/comp/LOG_<team>.md`,
writes `shots/<ID>.py`, renders `media/comp/<ID>.mp4` (960x540, exact frames).
Teams running (relaunch from the shot lists here if a log stops growing):
- MOUNTAIN: B3 B4 B5 C1 C4 C5b C6 D4 D5 E2 E4 G2 H5 H6 G6 (+ `shots/_margins.py` margin schedule for the G shots) ($20)
- STAGE: D1 D2 D6 D7 D8 J3 J4 (monkey; Kling v4 first+last between canon poses) ($60)
- FACES: H1-H4 (脸谱 bridge), F2 F4b F5 F6a (shadow puppets in car panes) ($10)
- HEAVEN & LEDGER: I3b J2 J5 K2b K3 K4 K5 + page art for I2/J1 ($10)
- Keyframes: attic (`media/kf/LOG_attic88.md`), bedroom+car; video bake-off (`docs/VIDEO_BAKEOFF.md`, partial: Kling v4,
  Seedance 2.0, HappyHorse keep the ink figure; h3 i2v needs ratio "adaptive"); plates (B, D, F done; E, A, C, G in progress).
Not yet assigned: ROOMS team (animate room keyframes, lip-sync 18 shots, map pages onto the book, hand shadows, neon sign in
code, margins on G shots, splice a/b parts): starts when keyframes + bake-off lip-sync verdict land.
Then: assemble preview_v1 (`tools/cut/assemble.py --profile preview --audio media/sound/mix_v1.wav`), QA pass, `docs/MORNING.md`.
Spend: TOTAL $94.29 of $600 cap  (362 billed items; list-price estimates)

## Checkpoint 7 — 2026-11-17 01:52
All 65 shots are now assigned. New teams: ROOMS-88 (attic: A1-A4 B1 B2 C2 C3 C5a D2d D3 D9 E1 E3 E5 E6 F3b G1 G3 G4 G5 L3;
log `media/comp/LOG_rooms88.md`, $55) and ROOMS-26 (F1 F3a F4a F6b I1 I2 I3a I4 J1 K1 K2a L1 L2; `LOG_rooms26.md`, $55).
Method for rooms: Kling v4 motion from keyframes (first+last), Seedance 2.5 lip-sync with `tools/review/lipsync.py` auto-lag,
comp layers in tools.ink (page art on book via sidecar quads, neon sign in code, hand shadows, margins).
Done: plates (all groups, `design/plates/PLATES.md`); bedroom + car keyframes (`media/kf/_sheets/`).
Split shots to splice at assembly (lead): C5 = C5a+C5b @54.6; D2 = D2 + D2d (last ~0.6 s); F3 = F3a+F3b (last 12 f);
F4 = F4a+F4b @~114.3; F6 = F6a+F6b @~120.6; I3 = I3a+I3b @~184.6; K2 = K2a+K2b @~212.1 (exact frames in team logs).
Still running: attic keyframes; video bake-off (V1b/V4/V6 tails); teams MOUNTAIN, STAGE, FACES, HEAVEN.
Next (lead): splice script; assemble preview_v1 with `media/sound/mix_v1.wav`; QA sheets; `docs/MORNING.md`.
Spend: TOTAL $123.20 of $600 cap  (451 billed items; list-price estimates)

## Checkpoint 8 — 2026-11-17 02:15
Done: teams MOUNTAIN (15 shots), STAGE (7), FACES (8, H3 fixed to stay on the album), HEAVEN & LEDGER (7): all in
`media/comp/`, scripts in `shots/`, logs `media/comp/LOG_*.md`, sheets `work/review/comp/`. Video bake-off final.
Interim cut: `media/cut/preview_v0.mp4` (finished shots + keyframes for rooms; sound mix v1; 5720 frames verified);
contact sheets `work/cut/preview_v0/contact_<SEQ>.jpg`. Keyframe animatic: `media/cut/animatic_v1.mp4`.
Splice tool: `tools/cut/splice.py` (writes `media/comp/spliced/`, updates `docs/picks.json`); 7 split shots wait on room parts.
Running: ROOMS-88 and ROOMS-26 (no logs written yet at this time; they are generating Kling/Seedance clips).
Next: when rooms land -> splice.py -> assemble preview_v1 -> lead QA pass on contact sheets (continuity, lyric text
consistency, brightness of rooms) -> fixes -> `docs/MORNING.md`.
Spend: TOTAL $172.24 of $600 cap  (506 billed items; list-price estimates)

## Checkpoint 9 — 2026-11-17 02:33
Running: ROOMS-88 and ROOMS-26, both progressing (71 clips now in `media/comp/` incl. parts; newest: F3a, G4, F4a, C5a,
F3b, I2, G3, G1). Relay queue is empty (144 done, 15 error, 8 rejected overall). Nothing stalled.
Next: on room hand-backs -> `tools/cut/splice.py` -> `assemble.py --name preview_v1 --profile preview --audio
media/sound/mix_v1.wav` -> contact sheets -> lead QA -> `docs/MORNING.md`.
Spend: TOTAL $172.24 of $600 cap  (506 billed items; list-price estimates)

## Checkpoint 10 — 2026-11-17 02:43
**FIRST COMPLETE CUT EXISTS: `media/cut/preview_v1.mp4`** (960x540, all 65 shots, no slates, sound mix v1, 5720 frames
verified). Contact sheets: `work/cut/preview_v1/contact_<SEQ>.jpg`. All six shot teams delivered; logs in `docs/logs/`.
Lead change: narrowest margin strip widened 15% -> 22% (`shots/_margins.py`) so the face in G5 is whole; G4, G5 re-rendered.
Running: QA review (read-only) -> `docs/QA_PREVIEW_V1.md`; polish round 1 (I4 repaint in the painted hand, G2 margin
legibility, B3 surround, L2 thumb press, J2 back on paper) -> `docs/logs/LOG_polish1.md`.
Known weak (lead's read of the contact sheets): lip-sync shots drift toward a soft 3D look and score r 0.16-0.54;
rooms brighter than their night budgets; lyric inscriptions tiny and inconsistent; 脸谱 faces graphic rather than brushy.
Next: apply QA's top fixes -> re-assemble as preview_v2 -> `docs/MORNING.md` -> stop for Jade's review.
Spend: TOTAL $172.24 of $600 cap  (506 billed items; list-price estimates)

## Checkpoint 11 — 2026-11-17 03:02
Done: polish round 1 (`docs/logs/LOG_polish1.md`: I4 repainted in the painted hand, G2 margins legible, B3 surround,
L2 repaint + thumb press, J2 on paper); QA review of preview_v1 (`docs/QA_PREVIEW_V1.md`: 15 ranked fixes, measured
sync table, lip-sync table); lead fixed `tools/cut/splice.py` (it duplicated a frame: all 7 splices were 1-2 frames
late; now frame-exact, verified).
Running fix round 2 from the QA list: BOOK/STAGE fixer (`docs/logs/LOG_fix2_book.md`: late seal/flip/crack/page
triggers, D2 bows + legible seal glyphs, 脸谱 painted surface, J3/J2 light, K5 blank column) and ROOMS fixer
(`docs/logs/LOG_fix2_rooms.md`: ending L2->L3 black + neon off, E3, unmarked crashes, centred faces, lip-sync shifts,
I1 white-in, G4 ring, F6b reflection).
Next: global lyric pass (QA item 4: one consistent lyric layer; per-shot lyric text off) -> splice -> preview_v2 ->
`docs/MORNING.md` -> stop for Jade.
Spend: TOTAL $174.90 of $600 cap  (514 billed items; list-price estimates)

## Checkpoint 12 — 2026-11-17 03:32
Done: fix round 2 BOOK/STAGE (`docs/logs/LOG_fix2_book.md`): hit triggers fixed at the source in tools/ink (all
measured at 0 frames), D2 bows distinct, seal syllables in 館閣楷 白文, 脸谱 painted surface, J3/J2 light, K5 reframed
(scale 1.20; framing in the log and in `shots/K5.py`).
Running: fix round 2 ROOMS (`docs/logs/LOG_fix2_rooms.md`).
Next: global lyric pass (ctx has no `opts`; teams used three different switches incl. env INK_LYRICS: unify, turn
per-shot lyric text off, keep art inscriptions 一通百通 in D4/D5/J5, add one consistent lyric layer at assembly) ->
`tools/cut/splice.py` -> preview_v2 -> `docs/MORNING.md`.
Spend: TOTAL $174.90 of $600 cap  (514 billed items; list-price estimates)

## Checkpoint 13 — 2026-11-17 03:44 (after the 03:40 window reset)
No interruption occurred; nothing died. Done: fix round 2 ROOMS (`docs/logs/LOG_fix2_rooms.md`: ending L2->L3 rebuilt
(black from f5660, window up f5670-5672, neon off f5709), E3, crash events in E1/F1, G1 margins on f2926, centred faces
reframed, I4 ghost, lip-sync 1-frame shifts, I1 torch-on, G4 band, F6b reflection).
Running: global lyric pass + preview_v2 (one agent): unify the lyric switch (`ctx.opts`, default off), re-render every
shot with per-shot lyric text off (old comps kept in `media/comp/_v1/`), new `tools/cut/lyrics.py` layer at assembly
(`assemble.py --lyrics on|off`), then `preview_v2` and `preview_v2_clean`, re-measured sync, `docs/QA_PREVIEW_V2.md`.
If that agent dies: its brief is reproducible from this paragraph and QA item 4 in `docs/QA_PREVIEW_V1.md`.
Next (lead): review preview_v2 sheets -> `docs/MORNING.md` -> stop for Jade's review.
Spend: TOTAL $174.90 of $600 cap  (514 billed items; list-price estimates)

## Checkpoint 14 — 2026-11-17 04:16 — STOPPED FOR JADE'S REVIEW
Complete 540p cut delivered: `previews/chaosmonkey_preview_v2_540p.mp4` (lyrics) and `..._nolyrics.mp4`
(= `media/cut/preview_v2.mp4`, `preview_v2_clean.mp4`; 5720 frames, verified). Morning report: `docs/MORNING.md`.
Current QA: `docs/QA_PREVIEW_V2.md`. No agents or jobs are running; the hourly checkpoint job is cancelled.
Nothing further is to be generated or rendered until Jade has reviewed (her stop point). No 1080p render was made.
Spend: $174.90 of $600.

## Checkpoint 15 — 2026-11-17 13:30 — Jade's first feedback; sheets redrawn; handoff written
Jade watched preview_v2: "a pretty good start". Feedback so far: girls less cute than references; little Jade and Jade
must have no bangs over the forehead (curtained to the sides); "deadpan unsmiling" makes them lifeless. Done since:
notes page `review/preview_v2_notes.html` (built by `tools/review/notes_page.py`); v2 sheets for little Jade and Jade
(`design/characters/*/…_v2.jpg`, crops `refs/*_v2.jpg`, not yet approved); `design/characters/CANON.md` section 0;
`docs/HANDOFF.md` (what her notes will look like, acting direction per shot, which shots need new keyframes).
No shots regenerated. Uncommitted. Spend: $176.20 of $600. Next: wait for her pasted notes; start from `docs/HANDOFF.md`.

## Checkpoint 16 — 2026-11-17 evening — preview_v3 reshoot running
Jade's notes on preview_v2 are in; brief: `docs/REVISION_V3.md`; team roster, scopes, logs and resume procedure:
`docs/TEAMS_V3.md`. Likeness pass done with Jade (v3 canon accepted). Done: characters, 3D blocking, sound mix v2.
Running: research, book, faces, stage, lip-sync, attic, bedroom+car. Cap raised to $1,500 on Jade's word.
Spend: TOTAL $229.14 of $1500 cap  (647 billed items; list-price estimates)

## Checkpoint 17 — 2026-11-17 late evening — before an expected interruption
Committed 0578318 (docs, briefs, tools, scripts; local only). Research DONE (`refs/paintings/MANIFEST_V3.md`; changes in
REVISION_V3 §15). `/tmp` was 98% full: chaosmonkey-song scratch cleared with Jade's OK; teams told to use `work/tmp/`.
Running: BOOK, FACES, STAGE, LIPSYNC, ATTIC, BED+CAR (logs `docs/logs/LOG_v3_*.md`, each with a CHECKPOINT block).
To resume after an interruption: `docs/TEAMS_V3.md` ("how to resume"), then relaunch any team whose log has no DONE line.
Then the lead's remaining work: splice, lyric layer (rap English, REVISION_V3 §7), extend L3 to 241.920, assemble
preview_v3 with `media/sound/mix_v2.wav`, QA, notes page, report. Open with Jade: her parents' recheck of
`design/text/lyrics_zh_v3.txt` (I2 line is the lead's proposal); mix v2 not yet listened to.

## Checkpoint 18 — 2026-11-18 00:50 — preview_v3 DELIVERED FOR JADE'S REVIEW
`previews/chaosmonkey_preview_v3_540p.mp4` (+ `_nolyrics`), 5806 frames, 4:01.9, mix v2 with ending B. Every shot re-made.
QA and ranked remaining problems: `docs/QA_PREVIEW_V3.md`. Notes page: `review/preview_v3_notes.html`. Rebuild:
`work/cut/build_v3.sh`. All teams DONE (logs `docs/logs/LOG_v3_*.md`); no agents or jobs running. Not watched in motion or
listened to by anyone. Uncommitted since 0578318. Open with Jade: monkey costume A/B; inscription text (parents' recheck,
I2 line); banquet name slips. TOTAL $361.81 of $1500 cap  (878 billed items; list-price estimates)

## Checkpoint 19 — 2026-11-18 — handoff written
`docs/HANDOFF.md` rewritten for the next session (state, Jade's standing direction, open decisions, weak points, how to
work her notes, standing rules). Nothing else changed since checkpoint 18. Still waiting on Jade's review of preview_v3.

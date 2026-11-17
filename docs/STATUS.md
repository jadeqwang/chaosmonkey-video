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

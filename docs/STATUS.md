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

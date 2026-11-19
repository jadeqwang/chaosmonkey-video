# Chaos Monkey: handoff to the next session

Written 2026-11-19 by Claude (Fable 5.2), lead of the preview_v2, v3 and v4 passes. It replaces the handoff of
18 Nov (in git at `fabcc64`; its v3 detail is superseded by the files named below).

**You are receiving Jade's timestamped notes on preview_v4 together with this file.** Her one-line verdict on the
cut was "massive improvement". Your job is the next pass (preview_v5, 540p) against those notes.

## 1. Where things stand

- **preview_v4 is delivered and she has watched it.** `previews/chaosmonkey_preview_v4_540p.mp4` (+ `_nolyrics`):
  960x540, 24 fps, 5806 frames, 4:01.9, audio `media/sound/mix_v3b.wav`.
- Her review pages (she may paste their "Copy everything" output, or may only send timestamped notes):
  - `review/preview_v4_notes.html`: 11 questions and a proofread table for 33 new Chinese lines.
  - `review/sing_v4/index.html`: all 16 singing shots with sound, a sync-offset slider and verdict buttons.
  - `review/f1_ab/index.html`: four takes of the F1 rap line, same controls.
- Nothing is running: no agents, relay jobs, cron jobs or tmux/Codex jobs. All team logs end in DONE.
- Spend: **$838.42 of the $1,500 cap** (`tools/gen/spend.py`); v4 cost $476.61. About $660 is left: enough for one
  more pass of this size, not two. No 1080p master exists; do not make one until she asks.
- Git: branch `claude/video-production`, last commit `fabcc64` (pushed). **184 paths are uncommitted**, the whole v4
  pass. I offered a commit twice; she has not answered. Ask once, early; commit only on her word.

## 2. Read in this order

1. This file.
2. `docs/REVISION_V4.md`: the v4 brief. §1 the five global rules, §3 hero-shot concepts, §5 shot table, §10 her
   preview_v3 notes verbatim, §12 decisions made during the pass.
3. `docs/QA_PREVIEW_V4.md`: what is in the cut, splice table, calligraphy placement, §5 the 22 ranked problems.
4. `docs/LIPSYNC_V4.md` and `work/review/sing_v4/audit.md`: the lip-sync recipe and where it fails.
5. `docs/TEAMS_V4.md`: roster, checkpoint rule, image-generation route. `docs/SETS_V4.md`: the 3D rooms.
6. As needed: `docs/STATUS.md` checkpoints 20 to 23, team logs `docs/logs/LOG_v4_*.md`, `docs/SOUND.md` "v3"/"v3b",
   `design/characters/CANON.md`, `docs/REVISION_V3.md` (story arc §1, acting direction, still in force).

## 3. How to work her notes

1. **Map each timestamp to a shot** with `docs/shots.json` (frame = seconds x 24; slots that are two shots are in the
   splice table, QA_PREVIEW_V4 §3). Sort each note to a kind: lip-sync, acting retake, keyframe/blocking, comp (timing,
   grade, text), calligraphy text, cut, sound.
2. **Write `docs/REVISION_V5.md` before spending anything**, with her notes verbatim in it (as §10 of REVISION_V4).
   Decisions you take during the pass go in a last section as you take them.
3. Cross-check her notes against QA_PREVIEW_V4 §5. Where she did not mention a known problem, do not assume she
   accepts it; list those and ask in one batch at the end, not one at a time.
4. Comp, text and cut notes are free (edit `shots/<ID>.py`, `design/text/*`, re-render). Acting notes cost a keyframe
   (Codex), a Kling take, and the animate pass if the shot sings.
5. Teams: copy `docs/TEAMS_V4.md` to `TEAMS_V5.md`. Opus team leads, Sonnet for mechanical work. She asked me to
   "delegate generously to smaller models" to protect the Fable limit. Agent IDs from this session will not resume in
   yours; relaunch from the logs.
6. Rebuild: `work/cut/build_v4.sh` (splice, both cuts, verification, notes page); copy to `build_v5.sh`.
   Singing page: `tools/review/sing_page_v4.py --refresh <ID>`.

## 4. What she has decided (do not reopen)

- Vision is right; the work is execution. Bar: "the most impressive thing that anyone on Twitter has seen". Not limited
  to 2D. "Not worry about token costs", within the cap.
- **Rooms and bodies are built in 3D first** (`layout/`, three.js), cameras placed, keyframes checked against the
  render (`tools/review/set_check.py`). L2 is the reference bedroom blocking.
- **All lip-sync is done by video models.** No mouth transplant, no compositing of mouths.
- **Chinese lyrics in calligraphy on every sung line**; one export, no separate subtitled version. Typeset only
  (Ma Shan Zheng), never drawn by a model.
- Costume B for the monkey (key-fret, leopard trim, red scarf). Little Jade's hair as in E6: two little ponytails,
  half up, no fringe.
- "Yes" (G5) one beat late: approved by ear. E3's sword-hand cast: approved. The mirror shot is reused as the last
  rap line (F6b). Ending B. Inscription text and font are right.
- Medium switches must read as intentional. The album leaf stays.

## 5. Waiting on her (check whether her notes answer these)

| Item | State |
|---|---|
| Singing-shot verdicts and offsets | Audit: FAIL C3, G1, K2a; SUSPECT G4, I4, J4. I held all retakes for her verdicts. |
| F1 take | `F1_new_a` is in the cut (`media/comp/F1.mp4`); alternates `F1_b`, `F1_ar9`, `F1_alt`. None fully passes. |
| F3b retake | The permission check refused it. **Do not run it without her yes.** Prompt: `work/attic4/notes/EF.md`. |
| Chinese proofread | 33 new lines, `review/lyrics_zh_v4_proof.md`. My doubts: C2 猴子/石猴, G5 好/嗯, H3, D3, K1b 幽冥界, G2c 听话, "Wouldn't you? You're able." |
| Mix | `mix_v3.wav` approved by ear. `mix_v3b.wav` (nine faint cues re-timed) is in the cut; she has now heard it but has not said. |
| Commit | See §1. |
| Two older points | 小龙女 is from 神雕侠侣, not 射雕英雄传 (she accepted the cast anyway). "Fight the gods and win" couplet in I2 was quoted from memory; check it against the 100-chapter text before any master. |

## 6. Known problems in preview_v4, most serious first

Full list with frames: QA_PREVIEW_V4 §5.

1. **Lip-sync is the weakest area.** See §7.
2. **G1, G4:** faces are about 80 px; the recipe needs about 240. They need closer framing, not more seeds.
3. **J4:** little Jade's arms go up about 0.9 s before the gong.
4. **E3:** second line is a held pose in a wider angle with her mouth closed while the line is sung.
5. **D6 into D7:** hard cut from night blue to bare paper.
6. **F3b:** poor hair-puff match cut.
7. **B3, J2:** the dolly into the page and the "suddenly 3D" moment are better than v3 and still below the bar.
8. **K1:** page calligraphy is fixed to the screen over a panning page; the line's last 1.4 s has no Chinese.

## 7. Lessons from this pass

- **Frame strips do not judge lip-sync or hands.** I passed F1 on strips; she found a still mouth through six syllables
  and fingers changing shape frame to frame within one viewing. Nobody but her watches in motion, and the test browser
  here cannot play H.264. Say so plainly in every report, and give her anything that sings on a page with sound and an
  offset slider (copy `review/f1_ab/index.html`), never as a bare mp4.
- **Lip-sync recipe:** Kling v4 acts silently, then `pruna/p-video-animate` re-renders the character to the vocal stem
  (`tools/gen/lipsync_v4.py`). Known behaviour of the animate model:
  - Cold start: the mouth stays still at the head of the clip. Fix: splice a sung run-up before the line and discard
    those frames. Applied to F1 only; I4 and K2a likely need it.
  - It drops large gestures and redraws hands. Keep the arm clear of hair and face; keep gestures small in sung shots.
  - Face size: about 240 px at 720p, 350 for the rap.
  - Lip-sync audio must come from the edited song (`work/stems/vocals_v4.wav`, timing `analysis/timing_v4.json`).
  - Seedance re-performs the song with a random lag; `runwayml/aleph-2` fails with a billing error.
- **Painted keyframes joined by Kling multi-keyframe flights beat pure 3D** for the painted world. WORLD's two 3D rounds
  of D4 to D6 failed the bar; the keyframe flight (`tools/dflight/`, `tools/swarm4/`) made the two best shots in the cut.
  3D is for rooms, bodies and camera placement.
- **Send work back.** H6 took three rounds and D4 to D6 three; the accepted versions were the third.
- **Interruptions:** a usage limit and a spend limit each killed every running team. All resumed from their logs
  because of the checkpoint rule. Keep it: every agent writes plan, prompts, job IDs and picks to files as it goes.
- **Shared files:** WORLD overwrote one of BOOK's page plates. Give each team its own output names.

## 8. Pipeline facts

- Python: `/home/jade/Documents/halys-video/.venv/bin/python`. `export TMPDIR=$PWD/work/tmp` (`/tmp` is a 16 GB RAM disk).
- Generation: `tools/gen/cf.py`, `gen.py`, `vgen.py`, `spend.py`; ledger `docs/spend_ledger.jsonl`.
- **Images go through Codex first** (her paid plan): `codex exec -s workspace-write --skip-git-repo-check "<prompt> ...
  save to <abs path>" < /dev/null` under `flock /tmp/chaosmonkey-codex.lock`; prompt before any `-i` images; no
  sandbox-bypass flags. Cloudflare gpt-image-2 only where Codex cannot do the job. Video models stay on Cloudflare.
- gpt-image-2 holds the faces. Pass only v3/v4 character material as reference; older images bring the fringe back.
- Comps: one script per shot in `shots/`, output `media/comp/<ID>.mp4`, 960x540, 24 fps, exact frame count, no audio.
  Backups: `media/comp/_v3/`, `shots/_v3/`, `media/comp/_world_r2/`, candidates in `media/comp/_cand/`.
- Calligraphy: inscriptions `tools/ink/inscription.py`; room overlay `tools/cut/roomcal.py` with
  `design/text/roomcal_v4.tsv`; text `design/text/lyrics_zh_v4.txt`. English layer `tools/cut/lyrics.py`.
- Cut: `tools/cut/splice.py`, `assemble.py`, `work/cut/verify_v4.py`. G5 is one 78-frame shot over song frames
  3515 to 3593 (the "Yes" attack is frame 3583).
- Headless page checks: playwright-core at `/home/jade/Documents/1-music-shipped/moongazing/render/node_modules/`,
  Chrome at `/opt/google/chrome/chrome`.

## 9. Standing rules

- Spend cap $1,500. 540p until she asks for the master.
- Her name, email, photos and project details stay out of requests to outside services. Never send
  `design/characters/_src/jade_face_photo.jpg` or any real photo anywhere without asking her first.
- Commit only when she asks; never push without being asked.
- A job the permission check refuses is hers to approve. No agent, and not the lead, re-submits it.
- Never deploy, modify or delete the Cloudflare Worker `rare-earth-v3-relay` or its KV namespaces; never print
  Cloudflare secrets.
- All Chinese on screen is typeset from `design/text/`.
- Subagents checkpoint to local files. Temp files in `work/tmp/`.

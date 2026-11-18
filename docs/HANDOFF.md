# Chaos Monkey: handoff to the next session

Written 2026-11-18 by Claude (Fable 5.2), lead of the preview_v2 and preview_v3 passes. It replaces the handoff of
17 Nov (in git at `ca11e64`; its acting direction was carried into `docs/REVISION_V3.md` and still holds).

## Where things stand

- **preview_v3 is delivered and waiting for Jade's review.** She has not yet said anything about it.
  - `previews/chaosmonkey_preview_v3_540p.mp4` (lyrics on) and `..._540p_nolyrics.mp4`: 960x540, 24 fps, 5806 frames,
    4:01.9, sound `media/sound/mix_v2.wav` with ending B.
  - Her notes page: `review/preview_v3_notes.html`. She will paste its "Copy everything" output into the session.
- All 65 shots were re-made against her preview_v2 notes. The cut is verified by measurement (frame counts, sync, no
  slates, no duplicated frames). **Nobody has watched it in motion or listened to the mix**: every check was on frames,
  contact sheets and numbers. Do not tell her otherwise.
- No agents, relay jobs, cron jobs or tmux Codex jobs are running. All team logs end in DONE.
- Spend: **$361.81 of the $1,500 cap** (`tools/gen/spend.py`, ledger `docs/spend_ledger.jsonl`).
- Git: branch `claude/video-production`, last commit `0578318` (local only, never pushed). Everything since is
  uncommitted, about 150 changed or new paths, including every v3 shot script. I offered a commit; she has not answered.
- No 1080p master exists. Do not make one until she asks.

## Read in this order

1. This file.
2. `docs/REVISION_V3.md`: the governing brief. §1 story arc, §2 changed rules, §3 concepts, §5 shot table, §7 rap
   English, §10 her preview_v2 notes verbatim, §13 stepping into the painting, §14 blocking decisions, §15 research.
3. `docs/QA_PREVIEW_V3.md`: what is in the cut, the splice table, and the ranked list of remaining problems.
4. `docs/STATUS.md` checkpoints 16 to 18 for history; `docs/TEAMS_V3.md` for team scopes and the checkpoint rule.
5. As needed: `design/characters/CANON.md` §00 (v3 canon), `docs/LAYOUT_V3.md` (3D blocking), `docs/LIPSYNC_V3.md`
   (lip-sync recipe), `docs/SOUND.md` "v2", team logs `docs/logs/LOG_v3_*.md`.

## What Jade wants (standing direction)

- **Story arc, kept subtle.** Little Jade is mischievous and "a full click smarter than both her parents". Mama's
  parenting is do-what-you're-told, as a light response to a child who climbs and falls. Jade's parenting encourages
  independence: fight the gods and win, ask for a seat at the table.
- **Acting must be alive.** Each shot gets a want and an action in timed beats, never a mood. Never write deadpan,
  unsmiling, neutral. Stillness is reserved for "Yes", the bare column at the end, and the two light switches.
- **Both storytimes: child on the parent's lap, book in front of them.** Inconsistent scenes are blocked in three.js first.
- **Inside the book:** "stepping into a Chinese landscape painting that feels 3d once you're in it", with brushstrokes
  that come to life.
- **Inscriptions:** where the novel has the line, use the novel's words. All Chinese on screen is typeset, never drawn
  by a model.
- **Title:** "Chaos Monkey" / 混沌猴 / "Jade Wang" (English name only, no Chinese name).
- **Likeness:** hair on little Jade and Jade is curtained to the sides, no fringe over the forehead. Accepted heads:
  LJ-1/LJ-2, D-1/D-2, M-1/M-2, J-1/J-3 (`work/sheets_v3/`, `review/likeness_v3.html`). Jacket lettering (RARE EARTH on
  the back, 1420 MHz in the circle) is added in code, REVISION_V3 §12.
- **Working style:** do a likeness pass with her before re-animating anything with a changed face. Mechanical work may
  go to Codex through tmux or to smaller models. Teams checkpoint to files. "Don't worry about budget" for reshoots,
  within the cap.

## Decisions waiting on her

| Question | State | My recommendation |
|---|---|---|
| Monkey costume | A (all yellow, `design/characters/monkey/v3/monkey_v3_model_sheet.jpg`) is in the shots; B is `monkey_v3b_ALT_fret_leopard_redscarf.jpg` | B. About $12, six stage clips to re-make. |
| Inscription text | `design/text/lyrics_zh_v3.txt`, her own proofread; her parents will recheck | Wait for their changes, then re-render the affected book pages (comp only, no generation). |
| "You'd fight the gods and win" (I2) | In the cut: 强者为尊该让我 / 英雄只此敢争先, my proposal from chapter 7, **quoted from memory and not yet checked against the 100-chapter text** | Check the characters against a source before anything final. Fallback: 敢战天兵 / 战必胜. |
| Banquet name slips (I3b) | 佛老 菩萨 罗汉 [bare] 观音 圣帝 玄灵, chosen by the BOOK team | Hers to confirm. She also asked whether a banquet seat reads as a seat at the table of power; the staging answer is in REVISION_V3 §15. |
| Medium switch and swarm | Paper-cut, rubbing and shadow-puppet switches replace the glitch; the agent swarm is a ruled album leaf with name slips, not car windows | Ask whether both read as intended. |
| Sound | mix v2: layer louder, ending B, two early abacus clicks removed (`mix_v2_prev.wav` kept) | Needs her ears. |
| Commit | Offered | Commit only on her word; never push. |

## Known weak points, most important first

Full list with frame numbers in `docs/QA_PREVIEW_V3.md`.

1. **F2 (car window) colour:** blue-violet cabin between two warm amber shots; the puppet screen is the brightest
   thing in the sequence.
2. **Neon sign:** now one red 酒家 blade sign everywhere, but in the close attic shots it reads as facing the window
   instead of as a perpendicular wedge.
3. **Lip-sync is unjudged in motion.** F1 failed the numeric gate and I accepted it on the frame strip. G4 passes on
   the threshold after three takes. J4 (split screen) and F4a (mirror) are not synced at all.
4. **H5 ("made of the telling"):** the child's shadow is a pale blob. BOOK moved it off the writing; I had it put
   back; it is still weak.
5. **G2:** the painted margin page is brighter than the room shots around it.
6. **Carry-overs:** long near-still ledger shots (K3 to K5); no push into I3b; B2's push has no breathing under it;
   D9's climb has a jump.
7. **Sound:** the 1988 blanket cue plays over a quilt that is already tucked. Cues were timed to the first build, so
   re-time any that moved (`docs/sound_cues.json`, `tools/audio/sfx/build_v2.py`).
8. Lyric residue burned into B4, H3, C1, D6 plates.

## How to work her notes

1. Sort every note to a shot and a kind: likeness, acting retake, comp (timing, grade, text), cut, sound. Write the
   list into a new `docs/REVISION_V4.md` before spending; quote her notes verbatim in it, as §10 of REVISION_V3 does.
2. Likeness changes first, with her, before any re-animation.
3. Comp-only notes are free: edit `shots/<ID>.py` and re-render. Acting notes mean a new keyframe, a new Kling take,
   then lip-sync if the shot sings.
4. If you launch teams, reuse `docs/TEAMS_V3.md`: one log per team with a CHECKPOINT block rewritten at least every
   20 minutes, prompts and specs in files, relay jobs collectable by ID, a DONE line at the end. Two kinds of
   interruption killed teams in this pass (an auth drop and usage limits); every one resumed cleanly from its log.
5. Rebuild: `work/cut/build_v3.sh` (about 4 minutes; splice, both cuts, contact sheets, verification, notes page).
   For a new cut copy it to `build_v4.sh` and change the names.

## Pipeline facts worth knowing

- Python: `/home/jade/Documents/halys-video/.venv/bin/python`. Generation: `tools/gen/cf.py`, `gen.py`, `spend.py`.
- **gpt-image-2 holds the faces; nano-banana-pro does not.** Keyframes go through gpt-image-2. Any v1 or v2 image of
  little Jade or Jade in the references brings the fringe back: pass only v3 material.
- Acted takes: Kling v4. Comps: `tools/ink`, one script per shot in `shots/`, output `media/comp/<ID>.mp4` at the
  exact frame count in `docs/shots.json`.
- Lip-sync (`docs/LIPSYNC_V3.md`): Kling take, then `pruna/p-video-avatar` to drive, then `tools/sync/lp_lips.py`
  (LivePortrait ONNX) to transfer only the mouth, then `tools/review/lipsync_gate.py`. Wrapper
  `tools/gen/lipsync_take.py`. The face must be about 150 px or more at 720p. Adults: `--rgain 0.55 --shape 0.2
  --mask mouth --delay 2`. With two faces in frame, crop to the singer first, or the mouth lands on the other person
  (it did, on Mama, in E3 and G1).
- Helpers: `tools/ink/inscription.py` (`inscription(ctx, key, box=..., paper=P)`, font Ma Shan Zheng, reads
  `design/text/lyrics_zh_v3.txt`); `tools/ink/medium.py` (`Mediums`, `pick_chops`).
- Splices are defined in `tools/cut/splice.py`; the table and the reasons are in QA_PREVIEW_V3 §2. `media/comp/I2.mp4`
  is the old v2 shot and is not used (the slot is `pages/I2_full`). `media/comp/F1.mp4` is the face-synced version;
  `F1_body.mp4` is the fallback.
- v2 backups: `media/comp/_v2/`, `shots/_v2/`.
- Opera faces: checked against sources by a separate agent (`docs/logs/LOG_v3_faces_verify.md`); three were wrong and
  nine were repainted; 木吒 was removed; the monkey's face sits in cell 16 beside the bare cell. Opera photographs are
  reference only, never model inputs.
- `/tmp` is a 16 GB RAM disk and filled once. Teams use `work/tmp/` (shared, emptied between runs). It is at 42% now.

## Standing rules

- Spend cap $1,500. 540p passes until Jade asks for the master.
- Her name, email, photos and project details stay out of requests to outside services unless she asks. Never send
  `design/characters/_src/jade_face_photo.jpg` or any real photo to any service without asking her first.
- Commit only when she asks; never push without being asked.
- Never deploy, modify or delete the Cloudflare Worker `rare-earth-v3-relay` or its KV namespaces; never print
  Cloudflare secrets.
- Codex runs headless with `< /dev/null` under `flock /tmp/chaosmonkey-codex.lock`, never with sandbox-bypass flags.
- All Chinese on screen is typeset from `design/text/`, never drawn by a model.

# preview_v3 teams: roster and how to resume (lead's checkpoint file)

Written 2026-11-17 by Claude (Fable 5.2), lead. If the session is interrupted, a new lead reads `docs/REVISION_V3.md`
(the brief), this file, then each team's log, and relaunches any team whose log has no "DONE" line, giving it: the
reading list in REVISION_V3, its scope below, and "resume from your log's CHECKPOINT block; do not redo finished work".

## Checkpoint rule for every team
- Log file below, appended as you go. At the top keep a block `## CHECKPOINT <time>` rewritten at least every 20
  minutes and after every finished shot/sheet: done / in progress / next / relay job IDs still pending (with the spec
  path and where the output will land) / decisions made and why / open questions for the lead.
- Everything lives in files: prompts beside images, specs in `media/gen/specs/`, picks and rejects noted in the log.
  Nothing that matters may exist only in an agent's memory. Submit relay jobs so they can be collected later by ID.
- Subagents and Codex jobs you start get the same rule and their own section in your log.
- When finished write `## DONE <time>` plus the final report into the log as well as sending it to the lead.

## Teams
| Team | Scope | Log | Ceiling | State at 2026-11-17 evening |
|---|---|---|---|---|
| CHARACTERS | v3 canon from the heads Jade accepted | `design/characters/CANON.md` §00 | $40 | DONE ($5.35). Proofs seen and approved by Jade. |
| LAYOUT | Three.js blocking: lap setups both rooms, car with two seats, perpendicular neon, D9 fall, hand-shadow light, endings | `docs/LAYOUT_V3.md`, `layout/NOTES.md` | $0 | DONE |
| SOUND | mix v2 (layer louder, ending B, new cues) | `docs/SOUND.md` "v2" | $15 | DONE: `media/sound/mix_v2.wav`. Needs a listen; cues need re-timing to final picture. |
| RESEARCH | traditional references, 7 topics | `refs/paintings/MANIFEST_V3.md` | $0 | running |
| BOOK | B3 B4 B5 C1 C4 C5b C6 D4 D5 E2 E4 G2 H5 H6 J2 J5 K3 K4 K5; page art I2, I3b, K1, K2b; `tools/ink/inscription.py`; medium-switch helper; REVISION_V3 §3.1, §3.2, §13 | `docs/logs/LOG_v3_book.md` | $200 | running |
| FACES | H1-H4; 脸谱 archetype audit and mapping table | `docs/logs/LOG_v3_faces.md` | $30 | running |
| STAGE | yellow monkey v3; D1 D2 D6 D7 D8 J3; swarm F2 F4b F5 F6a (§3.3) | `docs/logs/LOG_v3_stage.md` | $150 | running |
| LIPSYNC | method bake-off, `tools/review/lipsync_gate.py`, `docs/LIPSYNC_V3.md`, then passing takes for room teams | `docs/logs/LOG_v3_lipsync.md` | $120 | running |
| ATTIC | A1-A4 B1 B2 C2 C3 C5a D2d D3 D9 E1 E3 E5 E6 F3b G1 G3 G4 G5, 1988 half of J4, L2b, L3 | `docs/logs/LOG_v3_attic.md` | $280 | running |
| BED+CAR | F1 F3a F4a F6b; I1 I3a I4 (morph) J1, 2026 half of J4 + the J4 split comp, K1 K2a L1 L2 | `docs/logs/LOG_v3_bedcar.md` | $220 | running |
| CUT (lead) | splice, lyric layer with Jade's rap English, L3 extended to 241.920, assemble preview_v3 with mix_v2, QA, notes page | `docs/STATUS.md` | $0 | waits on teams |

## Decisions by Jade so far (all in REVISION_V3)
Faces accepted: LJ-1/LJ-2, D-1/D-2, M-1/M-2, J-1/J-3 (`work/sheets_v3/`, `review/likeness_v3.html`); proofs and overview
approved, with jacket lettering to add in code (§12). Title: "Chaos Monkey" / 混沌猴 / "Jade Wang" (English only).
Inscriptions: her proofread file `design/text/lyrics_zh_v3.txt` (parents will recheck; I2 line is the lead's proposal,
pending). Feel inside the book: stepping into a painting with depth, living brushstrokes (§13). Spend cap $1,500.
Mechanical work may go to Codex via tmux or smaller models.

## To finish the cut (lead)
`tools/cut/splice.py` -> `tools/cut/assemble.py --name preview_v3 --profile preview --audio media/sound/mix_v2.wav
--lyrics on|off` -> copies to `previews/chaosmonkey_preview_v3_540p[_nolyrics].mp4` -> `tools/review/notes_page.py
--name preview_v3` -> `docs/QA_PREVIEW_V3.md` -> report to Jade. Nothing is committed; commit only when she asks.

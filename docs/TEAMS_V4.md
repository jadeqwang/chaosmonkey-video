# preview_v4 teams: roster and how to resume (lead's checkpoint file)

Written 2026-11-18 by Claude (Fable 5.2), lead. Brief: `docs/REVISION_V4.md` (overrides V3 where they differ).
Checkpoint rule, unchanged from `docs/TEAMS_V3.md`: each team keeps `docs/logs/LOG_v4_<team>.md` with a
`## CHECKPOINT <time>` block rewritten at least every 20 minutes and after every finished shot (done / in progress /
next / pending relay job IDs with spec path and output path / decisions and why / questions for the lead); everything
that matters lives in files; `## DONE <time>` plus the final report at the end. To resume after an interruption:
relaunch any team whose log has no DONE line with "read REVISION_V4, your scope below, resume from your CHECKPOINT".

Team leads run on Opus and hand mechanical work (batch generation, sheets, checks, renders) to Sonnet/Haiku subagents.

## Phase 1 (launched together)
| Team | Scope | Log | Ceiling |
|---|---|---|---|
| SETS | REVISION_V4 §1.1, §4: complete 3D rooms (attic88, bed26 rebuilt to L2, car26), jointed bodies, per-shot cameras and guide renders, painted master plate per set, `docs/SETS_V4.md`, the keyframe-vs-render checker | `LOG_v4_sets.md` | $40 |
| LIPSYNC | §1.2, §6: bake-off, `docs/LIPSYNC_V4.md`, one recipe + wrapper | `LOG_v4_lipsync.md` | $90 |
| WORLD | §2, §3.1: 3D painted-world toolkit; B3 B4 B5, D4 D5 D6, J1-page J2 J5, entry for K2b | `LOG_v4_world.md` | $230 |
| SWARM | §3.2: F4 F5 F6a (176 frames, one shot); F2 shapeshift window | `LOG_v4_swarm.md` | $180 |
| BOOK | §3.3 H5 H6, §3.4 C5b wind (and the flow handed to ATTIC's C5a), §3.5 K5; E4, G2 (听话), K2b/K3 stroke match, K4 no hand, I4-page static text; other pages only where the inscription changes | `LOG_v4_book.md` | $130 |
| STAGE | costume B on D1 D2 D7 D8 J3 and the puppets; v3 weak points | `LOG_v4_stage.md` | $80 |
| SOUND | §7: G5 "Yes" one beat late, mix_v3, cue re-timing at the end | `LOG_v4_sound.md` | $10 |

## Phase 2 (after SETS delivers guides and LIPSYNC delivers the recipe)
| Team | Scope | Log | Ceiling |
|---|---|---|---|
| ATTIC | all 1988 room shots per §5 (B1 B2 C2 C3 C5a D2d D3 D9 E1 E3 G1 G3 G4 G5, J4 left, L2b L3; A-shots and E5/E6 only if checks force it) | `LOG_v4_attic.md` | $170 |
| BED+CAR | F1 F3a F6b; I1 I3a I4 (no morph) J1, J4 right + split, K1 K2a, L1 L2 | `LOG_v4_bedcar.md` | $140 |

## Phase 3
| CUT | room calligraphy (light on dark) + lyric layer without the Chinese row, `design/text/lyrics_zh_v4.txt`, splice table v4, assemble `preview_v4` with `mix_v3.wav`, QA on dense strips, notes page, `docs/QA_PREVIEW_V4.md` | `LOG_v4_cut.md` | $0 |

Reserve: about $70 under the $1,500 cap. State of each team: see its log.

## Checkpoint rule, tightened 2026-11-18 20:25 (Jade, after a usage-limit stop killed all six running teams)
Everything to local files, always: CHECKPOINT block rewritten after every finished item or every 15 minutes; every
subagent has its own notes file named in the team log, writes its plan before starting and appends each result, pick
and job ID as it happens; prompts, specs and picks are written before jobs are submitted; partial results go into the
deliverable doc as they come. A new agent reading only the files must be able to continue. All six teams were resumed
from their transcripts at 20:22 and sent this rule.

## Image generation route (Jade, 2026-11-18 late evening)
"when you have the choice to call gpt-image thru codex (thru tmux) vs thru Cloudflare, preferentially do it thru tmux
because that draws against a plan I'm already paying for." So: gpt-image calls go through Codex's built-in image_gen
(how: `docs/PIPELINE_RECON.md` §8 and `docs/LOOK_BAKEOFF.md` line 284; headless `codex exec -s workspace-write
--skip-git-repo-check "<prompt> ... save to <abs path>" < /dev/null` under `flock /tmp/chaosmonkey-codex.lock`, never
sandbox-bypass flags; output about 1672x941). Use Cloudflare gpt-image-2 only where Codex cannot do the job (a larger
size is truly needed, a reference-image input it cannot take, a refusal after rewording, or the single-job lock would
stall a team). Log which route each image used. Video models stay on Cloudflare.

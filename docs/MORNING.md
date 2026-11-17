# Chaos Monkey: morning report

2026-11-17, about 04:20. Written by Claude (Fable 5.2), lead, for Jade.

## Where it stands

There is a complete 540p cut of the whole song, as agreed, and I have stopped there. No full-size render was made.

- **Watch this:** `previews/chaosmonkey_preview_v2_540p.mp4` (lyrics on) or `previews/chaosmonkey_preview_v2_540p_nolyrics.mp4`.
  Both are 960x540, 24 fps, 5,720 frames, with the sound mix. All 65 shots are filled; there are no slates.
- **Contact sheets:** `work/cut/preview_v2/contact_<A–L>.jpg` (first, middle and last frame of every shot).
- **Spend:** $174.90 of the $600 cap (list-price estimates from the ledger).
- **Branch:** `claude/video-production`, committed locally, not pushed. Media files are not in git.

Nobody has watched the cut in motion or listened to the mix. Every check was done on extracted frames and by
measurement. Treat motion quality, lip-sync feel and the sound layer as unreviewed until you have played it.

## What the film is

The treatment is `docs/TREATMENT.md`. Its one idea: the blank page of Chinese painting and the bare stage of Peking
opera are the same place. The quiet sections follow your brainstorm (one corner, bare paper, one thing moving). When
the percussion hits, the storybook's paper becomes a stage, and every glitch move is done through a traditional twin.

| Glitch move | What is on screen |
|---|---|
| Freeze on the hit | 亮相: the monkey snaps into a held pose with a 倉 seal slammed beside him |
| RGB split | Woodblock mis-registration |
| Invert | The frame flips to its rubbing, white on black |
| Echo | The same seal pressed again, fainter |
| Sample chop | Shadow-puppet joints re-posed in hard cuts, in the car windows during the rap |

Changes from the brainstorm that you should know about:

- **People are painted in the storybook's hand** (fine line and wash), not cel anime, so a room and a page can share a frame.
- **The categories are opera faces.** The bridge opens with 13 seconds of full band before the child sings, so painted
  faces stamp onto an album leaf one per beat; one cell stays bare and the child stands under it.
- **The hook's 12 instrumental seconds are the monkey's staff form** on bare paper; the staff's dry-brush ring stays on the page.
- **The ending is two switches.** The track has no single final clapper. The flashlight goes off on the last hit
  (3:55.8) and the 1988 neon goes off when the hum cuts (3:57.8).
- **The carved mountain is in small seal script**, because no free bronze or Stone-Drum font exists. The text is the
  real 千字文, lines 1–160.
- **The narrowest strip in the band verse is 22% of the frame width**, not 15%, so little Jade's face is whole on "Yes".

## What I think is strongest

1. The staff flower (D7, 1:16): the ring of dry brush that stays on the paper, the seal landing on the pose.
2. The carved cliff under raking sun and moon (B4, 0:29).
3. The birth (D1, 0:58): a real ink throw that resolves into the monkey on the gong.
4. The hand-shadow monkey thrown across the page on "Monkey!" (C2, 0:45), the thumbnail frame.
5. The ledger ending (K3–K5, 3:33–3:48): one stroke on "breath", then the bare column held with nothing moving.

## What is weak (my ranking)

1. **Lip-sync.** Seedance 2.5 softens the painted faces toward a 3D-render look, and sync is loose. Three shots (K1,
   G3, F4) don't show a readable mouth and play as off-screen voice. This is the biggest gap to a finished film.
2. **The opera faces** in the bridge still look digital at the wide framings, though the close ones now have a painted surface.
3. **Mama's age.** She reads 35–40 in several attic shots, not 30. You should also check her likeness.
4. **Takes that need regenerating:** the daughter's hands pray where they should chop the rap beat (F1) and her hair goes
   ginger; Mama reads as "shh" where she should blow on the page (C5); the ledger pages turn with no hand (K4).
5. **Rooms are brighter than their night budgets**, even after grading.
6. **Three holds drag:** the band page (G2, 6.9 s), the monkey troop (E2), the page turns (K4).
7. **Smaller:** the pull-back to the bed warps the room flat (L1); the cliff jumps in paper tone into the summit shot (B4→B5).

The full lists are `docs/QA_PREVIEW_V2.md` (current) and `docs/QA_PREVIEW_V1.md` (the first review, with measured sync).

## Decisions for you

1. **Is the direction right?** The opera stage, traditional-twin glitch, and painted people are the three big calls.
2. **Lip-sync:** keep singing faces (and I look for a better method, or roto the mouths), or cut more lines to
   hands, pages and shadows so fewer faces have to sing.
3. **Lyrics on screen:** the current layer is a consistent lower-third line, ink on paper and cream on night, with
   English under the rap. Over the carved cliffs (B4, C6, D5, H5) the line sits on carving; keep it there or drop it for those four.
4. **The ending's sound:** three mixes exist in `media/sound/` (`mix_v1_endA/B/C.wav`). A is the song's own hard cut and
   is what the preview uses. B gives the last note a 3-second natural tail. C is a hard cut plus 3 seconds of faint room tone.
5. **The opening's neon.** After a late change by the room team the attic is darker and the window stays mostly red.
   Say if you want the stronger red-to-blue cycle back.
6. **Mama's face and the working English for the rap** both need your eye.
7. **Go-ahead for the 1080p master** once the notes are in. Every shot script renders at 1920x1080 unchanged, but
   generated clips were made at 720p or 1080p and some will be soft.

## How it was made

| Stage | Result | Where |
|---|---|---|
| Timing map | Measured words, beats and hits; about 137 BPM, drifting. The supplied stems did not match the file and were re-separated | `docs/AUDIO_MAP.md`, `analysis/timing.json` |
| Research | Opera and wushu bible; 422 reference artworks saved locally; proofed texts and fonts | `docs/research/`, `refs/paintings/MANIFEST.md`, `refs/fonts/FONTS.md` |
| Bake-offs | Image and video models compared on ink material | `docs/LOOK_BAKEOFF.md`, `docs/VIDEO_BAKEOFF.md` |
| Design | Character and monkey canon, about 200 plates, three rooms blocked in Three.js | `design/`, `layout/` |
| Compositor | Paper, ink, seals, rubbings, mis-registration, carved text, margins, shadows | `tools/ink/` |
| Shots | 65 shots by six teams, then two fix rounds from a measured QA review | `shots/`, `docs/logs/` |
| Sound | 47 cues under the song; the song itself is untouched | `docs/SOUND.md` |

Model verdicts for this look:

- **MiniMax h3** is the best landscape model, as you suspected; the earlier "failed 5 of 5" was a settings error.
- **Kling v4** is best for room acting and for moving between two poses.
- **Seedance 2.0** gives the most real ink throw and dry-brush rings.
- **Nano Banana Pro** painted the rooms and people; GPT Image 2 the opera-face grid.

Spend by model: Seedance 2.5 $52, Nano Banana Pro $32, Kling v4 $26, Seedance 2.0 $20, GPT Image 2 $11, Veo 3.1 $10,
others $24.

## To resume

`docs/STATUS.md` has the checkpoints. To rebuild the cut:
`tools/cut/splice.py`, then `tools/cut/assemble.py --name NAME --profile preview --audio media/sound/mix_v1.wav --lyrics on|off`.
Python is `/home/jade/Documents/halys-video/.venv/bin/python`. Codex headless needs `< /dev/null` or it hangs.

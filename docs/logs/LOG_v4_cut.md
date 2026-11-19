# LOG v4 CUT (preview_v4 preparation)

Team: CUT (Opus 5.5). Brief: docs/REVISION_V4.md §1.3, §12; docs/TEAMS_V4.md Phase 3. Spend ceiling $0.
Assignment 1 = PREPARATION + trial build only (ATTIC, WORLD round 2, BOOK H6 still working). Stop and report after.

## CHECKPOINT 2026-11-18 (start)
- done: nothing yet; reading the brief, v3 cut tools, team logs.
- in progress: reading.
- next: lyrics_zh_v4.txt + proof table; roomcal renderer; placement table; lyric layer; splice v4; build_v4.sh; trial.
- decisions: none yet.

## CHECKPOINT 2026-11-18 22:25
- done: read brief/logs/tools. design/text/lyrics_zh_v4.txt (v3 + 33 new keys incl. 8 rap [sung] keys and G2c; all glyphs
  in Ma Shan Zheng). tools/cut/roomcal.py (renderer + --proof + --check). design/text/roomcal_v4.tsv (rows, default regions;
  NOT yet measured). lyrics.py: timing_v4, rap English-only (no Chinese row), v4 PARTS (B2 cut 591, F4/F5 swarm, F6a+F6b,
  G6 slot = G5b). splice.py v4 table -> media/comp/spliced_v4/, docs/picks_v4.json, work/cut/splice_report_v4.json
  (ran OK: all EXPECT match; G5 78 f spans G5+G6 slots by in-point). assemble.py: --picks, --calligraphy, labels.
  Backups of v3 cut tools: work/cut/bak_v4/.
- in progress: measuring regions (subagent), proof table md, lyric overrides v4, build_v4.sh / verify_v4.py.
- decisions: PX 26 at 540p (52 at 1080p), seal 白文 0.7 px (朱文 reads as an empty frame at 18 px); text opacity 0.92 x brush;
  album/page shots without inscription (H3, H4, K1 page part) get the same hand in INK (ground=paper), screen-fixed;
  room part of a line whose page inscription follows reuses that inscription's text (B2a<-B3 col1, C5a<-C5, I3a<-I3,
  K2a<-K2, L1<-K5). G5/G6: picks_v4 G6 = G5.mp4 from frame 68 (no shots.json edit). v3 picks.json untouched.
- subagent MEASURE (Sonnet, running): regions for every roomcal row; notes work/cut/roomcal_measure/NOTES.md, proposal
  work/cut/roomcal_measure/proposed.tsv (I review and apply to design/text/roomcal_v4.tsv).

## CUES FOR SOUND (v4 picture vs REVISION_V3 §11 / docs/sound_cues.json; collected from the v4 team logs, 2026-11-18 22:40)
Song clock (s), song frame = floor(t x 24). "moved" = the action is no longer where the v2/v3 cue sits; "new" = a new action
that has no cue yet; "gone" = the cue's action no longer exists. Source log in brackets. PROV = the shot is still being
re-made (ATTIC open items, WORLD round 2, BOOK H6): re-check before the final mix.
| Shot | Cue / action | v3 time | v4 time | Kind | Source |
|---|---|---|---|---|---|
| B1 | Mama turns to the child | 21.3 | ~21.0 | moved (-0.3) | ATTIC notes B.md |
| B2 | over-the-shoulder warp / page push starts | 24.5 | 24.6 (cut lap -> OTS on frame 591) | moved (+0.1) | ATTIC |
| B3 | true 3D dolly: page surface gives way, pines/rocks pass the lens (whoosh/air) | - | 26.125-29.29 (whole shot) | new | WORLD DONE (PROV r2) |
| C2 | hands up (shadow monkey) | ~45.3 | ~45.7 | moved (+0.4) | ATTIC |
| C5a->C5b | the wind: breath leaves Mama's lips 53.22; flow exits C5a right ~54.6; enters C5b at the left edge, front at x=0 54.505, first stroke 54.71; ribbons over the egg to ~56.4 (f42 dissolve) | 53.22 (hair lift) | 53.22 / 54.5-56.4 | new (wind on the page) | BOOK "C5b flow contract" |
| D1 | figure complete in colour | - | 59.55; wind-up into D2 from frame 1451 (60.46) | moved | STAGE DONE |
| D2 | four 抱拳 bow nadirs E S W N | v3 bows | 61.321, 62.205, 63.090, 63.980 (north under D2d) | moved/confirmed | STAGE DONE |
| D2d | the bow bottom in the attic echo | - | ~63.98-64.0 | confirmed | ATTIC CD |
| D4-D6 | flight: 通 lights 67.99; generation jumps 68.53 69.50 70.146 70.594 71.029 71.471 71.925 72.356; gong 72.805; 亮相 rays on landing 75.025 | v3 D5 jumps | as listed | moved/new (PROV r2) | shots/_dflight.py, _dflight2.py |
| D7 | one-hand thrust 亮相 | - | 78.808 | confirmed | STAGE |
| D9 | climb 83.24, topple 83.80, land 84.12, catch 84.35 | 83.244 / 83.798 / 84.127 / 84.351 | within ~1 f | confirmed | ATTIC CD |
| E1 | nose tap on "you" (if it reads; the pick shows no clear tap) | ~88.47 | not seen | gone? (PROV) | ATTIC EF |
| E3 | wuxia sword-hand cast on "a spell I'd remember well" (PROV: the cast is not yet in the comp) | - | ~96.2-99.6 | new | REVISION_V4 §5 E3, ATTIC EF |
| E4 | finger crooks (beckon) | v3 | ~100.4, 100.8, 101.3 (clip f11/22/33); sleeve lean from 100.9; tail flicks on its own | moved | BOOK |
| F2 | 72 transformations: hard re-poses on the beats (sparrow, cormorant, fish, water snake, bustard -> temple) | - | 108.84-111.04 (beats; see shots/F2.py) | new | SWARM F2 |
| F3a | daughter's puff | 112.146 | 112.125-112.208 (pursed f26-28) | confirmed | BED+CAR |
| F3b | little Jade's puff, hairs drift right | 112.372 | blow window sped ~3x, F3b 112.25-112.75 | confirmed (faint) | ATTIC EF |
| F4 | spawn: hairs stream in, generations plucking/blowing (puffs) | - | 112.75-114.3 | new | SWARM |
| F4 | beat-wave lantern flares (= the old abacus clicks) | 113.688 114.135 114.567 115.002 115.445 115.882 | 113.250 113.688 114.133 114.567 115.000 115.446 115.883 | +1 new (113.250) | SWARM DONE |
| F5 | sectors go dark / 讫 seals | 116.320 116.736 117.200 117.628 | 116.321 116.737 117.200 117.629 | confirmed | SWARM |
| F5->F6a | hair gale streams back (spiral) | - | ~117.77-118.0 (hair streak), twin ink puff 117.958-118.292 | new | SWARM |
| F6a | 真 seals pressed | 119.12, 119.812 | 119.162 (left), 119.812 (right) | moved (+0.04) | SWARM |
| F6b | the hair catch + laugh | ~120.1-121.4 | - | GONE: F6b is now the mirror shot (she raps at the mirror; Jade's eyes crinkle ~120.75) | BED+CAR, REVISION_V4 §12 |
| G2 | 听话 inks in (cinnabar) | - | 130.175, 133.690 | new | BOOK |
| G4 | Mama picks up / taps a fallen book, lifted finger (PROV: ATTIC re-take) | - | ~141.2-143 | new (PROV) | REVISION_V4 §5 G4 |
| G5 | thinking beat, then the nod; "Yes" moved | Yes 148.72 | eyes away 148.6-149.1, nod ~149.15-149.3, Yes attack 149.306; G5 runs to 149.708 (G6's blank 10 f gone) | moved | SOUND, REVISION_V4 §12 |
| H5 | carved strokes lift off the cliffs, stream and assemble into the girl | - | 169.25-172.75 | new | BOOK |
| H6 | gale takes her hair; strand works loose; monkey grows along it; somersaults out (PROV: round 3 running) | v3 hair | 172.75-177.21 | new (PROV) | BOOK |
| J1 | fingertip press | 189.620 | dip at ~189.50-189.55; character lights from 189.62 | moved (-0.1) | BED+CAR |
| J2 | pop into depth (flat page -> 3D) | v3 jump | 190.885; beats in flight 191.315 191.739 192.172 192.602 | new (PROV r2) | shots/_jworld.py |
| J4 | arms up on the gong | 198.74 | 2026 half ~198.7-198.8 (on); 1988 half ~197.8-197.96 (0.9 s EARLY, ATTIC not fixed) | moved (PROV) | BED+CAR, ATTIC |
| J5 | range collapses back into strokes on the flat page | - | 200.667-203.7 | new (PROV r2) | WORLD |
| K2b | brush stroke run (match to K3) | v3 | ~213.4-213.8 (clip f31-39) | moved | BOOK |
| K3 | wet strike on "crossed out"; bloom on "single breath" | 213.805 | 213.805; ~216.2 | confirmed/new | BOOK |
| K4 | page turns in the draught, no hand: leaf lands 218.22 ('page'); leaf 2 lifts, hangs, falls back 219.4-220.3; goes over and lands 220.92 ('looked'); leaf 3 lands 221.805 (hit); last leaf stirs 222.75-223.95 | v3 hand turns | as listed | new | BOOK, shots/K4.py |
| K5 | the wet line un-writes: cells retreat ~224.67 / 225.37 / 226.07, cell 1 gone on the 225.254 hit, bare ~226.6 | - | as listed | new | BOOK |
| L2b | blanket tuck | 235.88-236.28 | hands start ~235.88, tuck 236.276 | confirmed | ATTIC OPEN |

## CHECKPOINT 2026-11-18 22:50 (coordinator facts received)
- G5.mp4 = 78 f (3515-3592), no G6 comp: handled in picks_v4 (G6 slot = G5.mp4 from frame 68); shots.json untouched.
- sync_b2.sh = v3 path: NOT run (build_v4.sh only prints the B2-last vs B3-f0 diff). B2 must be re-rendered by ATTIC on
  WORLD's round-2 B3 frame 0 before the final assembly (ATTIC's log says how).
- tools.ink.run cache does not key on picks.json (touch the shot script after a pick-only change) - not my tool, noted.
- lip-strip/gate tools label words from old timing.json (only G5's Yes differs).
- Still changing, rows provisional: E3 (second half becomes a cut inside the shot), J4 (both halves), F1 (retake), H6,
  B3 B4 B5 D4 D5 D6 J2 J5 (WORLD r2).
- ATTIC sides (960x540): B1 left x0-190; B2 right top x750-960 y0-300; C3 left x0-190; D3 none free; E1 right x>650;
  E3 right upper; G1 right x700-960 y0-300; G4 right while wide; G5 left; J4 left. BED+CAR: left for I1 I3a I4 K1 K2a F1
  L1 (upper-left wall); right/middle F6b. -> forwarded to the MEASURE subagent.

## CHECKPOINT 2026-11-18 23:00
- done: TRIAL BUILD 1 (work/cut/build_v4.sh preview_v4_trial; log work/cut/build_v4_trial.log): pipeline runs end to end.
  verify (work/cut/preview_v4_trial/verify.txt): 5806 f both cuts, 960x540 24/1 CFR yuv420p, A/V 241.9167/241.9160 s,
  65 shots + END 86 f each on its in_frame, no slate, audio vs mix_v3 r 0.9999 at 0.0 ms, moved-Yes window r 0.9998,
  no duplicated frame at any of 72 boundaries, G6 slot = G5.mp4 frame 68 (diff 1.79 vs 3.83/1.94 for 67/69).
  B2 last vs B3 f0 2.38/255. Contacts work/cut/preview_v4_trial/contact_*.jpg. Calligraphy at placeholder regions.
  CUES FOR SOUND written (section above). review/lyrics_zh_v4_proof.md written (33 rows).
- seen on contacts: G1 end / G3 / G4 start are paper strips -> G3 rows ground=paper in the margin; G1/G4 windows trimmed
  to picture (told MEASURE). English lyric overrides from v3 are stale on new pictures (G4/G5 "Yes" on her chest, F4 f0
  over the monkey, F6a over the 真 seal): re-set after the calligraphy regions are final.
- next: apply MEASURE proposal, re-proof, English overrides v4 + --check, trial build 2.

## CHECKPOINT 2026-11-18 23:25
- done: MEASURE delivered (work/cut/roomcal_measure/NOTES.md, proposed.tsv, proof_final/); applied to
  design/text/roomcal_v4.tsv (placeholder kept in work/cut/bak_v4/roomcal_v4_placeholder.tsv) with my changes: K1a f1=4950
  (bright page fills the left after ~4955); H4 split in two rows (A: empty cell right of the girl 3983-4010; B: felt right
  of the album from 4016) because the measured L spot covered the child's face mask at 3983; status prov for B2a D3 E3 F1
  J3 J4. roomcal setting cache keyed on region too. G3 rows ground=paper (bare margin, right).
- English overrides v4 (tools/cut/lyrics.py OVERRIDES): F4, F5, F6a (no leaf: one row along the bottom, under the 真 seal),
  E4 (off the monkey's tail), G4 (+delay 14 until the strip opens; G4:43 right after the push), G5/G5b right (was on her
  chest), I1 (right of the lower-left calligraphy). roomcal --check: 0 collisions.
- QA helper work/cut/qa_v4_lyrsheet.py (one tile per English lyric segment from a built cut).
- in progress: trial build 2.

## CHECKPOINT 2026-11-18 23:50 — PREPARATION DONE, waiting for the lead's go for the final assembly
- TRIAL BUILD 3 (work/cut/build_v4_trial3.log): media/cut/preview_v4_trial.mp4 + _clean.mp4 (NOT in previews/).
  verify ALL OK: 5806 f each, 960x540 24/1 CFR yuv420p, A/V 241.9167/241.9160 s, 65 shots + END 86 f on their in_frames,
  no slate, audio r 0.9999 at 0.0 ms vs mix_v3 (moved-Yes window r 0.9998), no duplicated frame at 72 boundaries, G6 slot =
  G5.mp4 frame 68. B2 last vs B3 f0 2.83/255 (B3 changed since 18:57; ATTIC to re-render B2 on WORLD r2's B3).
  Contacts work/cut/preview_v4_trial/contact_*.jpg; English-lyric tiles lyr_0..5.jpg; calligraphy proofs
  work/cut/preview_v4_trial/roomcal_proof/. roomcal --check: 0 collisions.
- added row B3 line 3 (prov): B3's inscription flies out by ~f637 in WORLD's dolly; its column 2 set in ink top-left 640-699.
- next (on the lead's message): wait for ATTIC E3/J4, BED+CAR F1/J4, BOOK H6, WORLD r2; re-measure the prov rows on the
  final comps (MEASURE's method), re-check English overrides on every changed picture (qa_v4_lyrsheet.py), full build
  preview_v4, dense-strip QA, notes page, docs/QA_PREVIEW_V4.md.

## CHECKPOINT 2026-11-19 00:0x — FINAL ASSEMBLY GO (coordinator)
Facts: D4 D5 D6 NEW = lead's painted flight DFLIGHT_t3 (33+101+70; own inscriptions 一通百通 f0-32, 一窍通时/百窍通+seal
33-133 upper right; night blue; hard cut into pale D7 accepted). WORLD r2: B3, J2 changed (B4 B5 J5 r1). B2 left as is
(report 2.83/255). E3 final: E3a 72 f + E3b 94 f, internal cut at song frame 2304; calligraphy right upper x770-960.
J4 final (1988 arms early). F1 new take (re-measure). H6 BOOK round 3 (recheck). F3b unchanged.
Decisions: page/album ink rows at 30 px (inscription size), room rows 26; B3 ink overlay kept; K1 page screen-fixed ink
kept (weak point); D3: I check right side on 9+ frames full size, else low-left dark floor.
Do: re-measure prov rows, recheck English on changed pictures, build preview_v4 (mix_v3; if mix_v3b.wav exists with
SOUND DONE: tell the lead, do not switch), copies to previews/, verify, contacts, notes page review/preview_v4_notes.html
(links sing_v4, f1_ab, proof; proof table section with OK/correction; 10 questions with stills; v4 shot descriptions),
docs/QA_PREVIEW_V4.md, STATUS.md line (checkpoint 23, spend from tools/gen/spend.py).
- subagent NOTES (Sonnet, running): review/preview_v4_notes.html via tools/review/notes_page.py; notes work/cut/notes_v4/NOTES.md
- 00:3x done: page/album ink rows at 30 px (PX_PAGE_540); E3 split into units E3a (2232-2303) / E3b (2304-) in lyrics PARTS and
  the table; re-measured prov rows on the final comps: B2a E3a E3b F1 J4 clean (proof strips); J3 halo .3 (pale paper-cut
  flash 4645-49 = 5 faint frames); D3 RIGHT checked by me at full size on 10 frames 1546-1627: ~30 px clear of the window
  lettering, no face -> kept; H3 re-placed by a per-frame bare-paper measurement: x750-825 bare in all three face holds,
  window 3903-3965 (the pull-back has no bare strip); K1b ends 5019 (officials walk into every free spot after); B3 region
  enlarged for 30 px. All rows final now except B3 (WORLD-dependent).
- next: build preview_v4, then English recheck on changed pictures (D4-D6, B3, J2, E3, F1, H6) and rebuild changed shots.
- 01:1x first preview_v4 build done with mix_v3 (verify ALL OK). LEAD CHANGED AUDIO: build with media/sound/mix_v3b.wav (SOUND task 2
  DONE: song bit-identical to mix_v3, cues re-timed to the v4 picture, not heard by anyone). build_v4.sh now MIX=mix_v3b default,
  verify_v4 default mix_v3b. Rebuilding (renders cached; only the mux changes). Notes page + QA must say: Yes approved by ear in
  mix_v3; v3b differs only in the effects layer (28 cue rows, SOUND.md), unheard; question "Sound layer re-timed (v3b)"; nine new
  cues measure faint under the rap and drop 2.
- NOTES subagent done: tools/review/notes_page.py v4 mode (+ --cut), work/cut/notes_v4/descriptions_v4.json; I add the sound question.

## DONE 2026-11-19 (final assembly)
- preview_v4 built with mix_v3b (build log work/cut/build_v4b.log): verify ALL OK (work/cut/preview_v4/verify.txt): 5806 f both,
  CFR, 65 shots + END on in_frames, no slate, audio r 0.9999 / Yes window 0.9998 vs mix_v3b (residual vs v3b -35.4 dB, vs v3
  -23.4 dB), no duplicated frame at 72 boundaries, G6 slot = G5.mp4 f68. B2->B3 2.83/255 (left, lead).
- copies previews/chaosmonkey_preview_v4_540p.mp4 / _nolyrics.mp4 (cmp identical). Contacts work/cut/preview_v4/contact_*.jpg,
  lyric tiles lyr_0..5.jpg.
- notes page review/preview_v4_notes.html (NOTES subagent's v4 mode of tools/review/notes_page.py + my edits: swarm question text
  corrected (the lantern figure IS drawn), question 10 = sound v3b, 11 = what next).
- docs/QA_PREVIEW_V4.md, STATUS.md checkpoint 23. Spend total $838.42 (CUT $0).

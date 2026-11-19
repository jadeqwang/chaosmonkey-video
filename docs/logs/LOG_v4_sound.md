# LOG v4 SOUND (G5 "Yes" one beat late; mix_v3)

## YES ONSET
**New "Yes" onset 149.152 s (frame24 3580); word ends 149.702 (frame 3593); old 148.72-149.27 (frame 3570).**
Shift = exactly one beat of the local grid = 0.432 s = 20736 samples (beats 148.865 -> 149.297, 138.9 BPM; drums are out,
grid is the linear fit between measured beats 146.274 and 149.720). Loudest point of the vowel: old 148.905 -> new 149.337
(frame 3585, i.e. in G6 as shots.json stands: G5 ends 149.292). The word is the last thing before the bridge crash 149.720:
its final "s" runs under the bridge's rising swell (149.59-149.70).

## CHECKPOINT 2026-11-18 start
- done: read REVISION_V4 §7, TEAMS_V4, SOUND.md, AUDIO_MAP; stems located: work/stems/ (local BS-RoFormer vocals/instrumental,
  htdemucs_ft, mel-band-roformer karaoke; made by tools/audio/stems.py, no outside service). Supplied Suno stems
  (chaosmonkey-song/spliced/stems) belong to a different render (AUDIO_MAP), not usable for a sample-exact rebuild.
- in progress: precise measurement of the word, beat grid 146.27-149.72, collision check vs 149.285 silence / 149.720 crash.
- next: edit window build, ghost checks, mix_v3, timing_v4, review excerpts.
- spend: $0 (all local).

## CHECKPOINT 2026-11-18 edit done, verifying
- done: `tools/audio/yes_shift_v4.py` -> `inputs/Chaos Monkey - reformatted for duet - v4 yes late.wav` (PCM_16 like the original;
  original untouched, sha256 14433b34...). Method: song - w*V + shift(w*V), V = BS-RoFormer vocal stem (complementary to the
  instrumental stem to -172 dB), w = 1 over 148.69-149.40, raised-cosine ramps 148.62-148.69 / 149.40-149.50, shift exactly
  20736 samples. Also `work/stems/vocals_v4.wav` (vocal stem with the word moved, for the builder's vocal rules).
- verify (`tools/audio/yes_verify_v4.py` -> work/sound_v4/verify.json): 0 changed samples outside 148.62-149.932; ghost at the
  old place below the backing floor in every band; shape-similarity test shows nothing at lag 0 (test can see -40 dB ghosts);
  no HF transients beyond the original's own.
- attack (-6 dB of peak, 10 ms): old 148.874 (beat 3 148.865 +9 ms) -> new 149.306 (beat 4 149.297 +9 ms).
- next: timing_v4.json, mix_v3 via builder (reuse layer_v2), excerpts, loudness.

## CHECKPOINT 2026-11-18 task 1 delivered
- done: timing_v4.json; builder parametrised (build_layer: CM_SONG / CM_VOCALS / CM_TIMING env, defaults unchanged;
  build_v2: CM_CUES, `--tag`, `--reuse-layer`; non-v2 tags never touch the SOUND.md v2 block); mix_v3.wav built (reuse
  layer_v2); review excerpts + plots in work/review/sound_v4/; SOUND.md "v3 mix" section with the numbers and how to add cues.
- task 2 (cue re-timing / new cues K4 pages, F4-F6 swarm spawn + gale, J2 pop into depth, C5 wind): NOT started, waiting for
  the lead's list. How: SOUND.md "Adding / re-timing cues for mix_v3".
- questions for the lead: (1) shots.json G5 ends 149.292, so the moved word starts 3 frames before the G5->G6 cut and its
  vowel and "s" (149.21-149.72) play over G6 (blank paper, 10 frames). The brief's G5 exception presumably covers extending G5
  over G6; picture decision. (2) The edited song WAV (45 MB) sits beside the tracked original in inputs/, untracked.
- spend: $0.

## DONE 2026-11-18 (task 1). Task 2 pending the lead's list.

## CHECKPOINT 2026-11-18 task 2 started
- Director approved the moved "Yes" by ear ("sounds good"): edited song + mix_v3 stand.
- Task 2 brief (lead): cue list docs/logs/LOG_v4_cut.md "CUES FOR SOUND" (35 rows) + updates: D4-D6 painted flight (LOG_v4_swarm
  "# D-FLIGHT": ember on 通 68.09, arcs 70.594/71.029/71.471/71.925/72.356, landing bloom 75.025); E3 second line held pose (no
  cast whoosh; small cloth move ~96.0 at most); F1 new take (no change); F6b mirror shot (hair-catch removed); J4 gong stays; H6 new
  (strand tumbles, monkey grows ~174.3-175.6, somersault out left ~176.3; LOG_v4_book round 3).
- Output: media/sound/mix_v3b.wav via build_v2.py (edited song + re-timed layer); keep mix_v3.wav and layer_v2; layer level as v2.
  Sources only media/sound/sfx or local synthesis; $0; no outside service.
- in progress: reading the cue list.

## CHECKPOINT 2026-11-18 task 2 plan (cue sheet docs/sound_cues_v3.json, copy of v2 + edits; build --tag v3b)
Decisions per row (anchors checked against analysis/timing_v4.json beats/hits/words):
- re-time: breath (C5) start 52.55 -> 53.10 (breath leaves the lips 53.22), sleeve_wind 54.60-57.20 -> 54.50-56.70 (flow enters
  C5b 54.505, ribbons to 56.4); abacus_f4b -> lantern flares on 113.247 113.688 114.133 114.567 115.000 115.446 115.883 (+3);
  hair_air (H6) -> gale/strand; ledger_pages (K4) -> leaf lands 218.22 / lift 219.40 / falls back 220.30 / lands 220.92;
  fingertip_j1 189.62 -> 189.52 (the dip); room_yes / neon_hum_yes end anchor -> t:149.285 (silence anchor gone in timing_v4).
- new: B3 dolly air (26.145-29.29, PROV), D4 ember on 通 68.09, D5 frontier arcs x5, E3 cloth move ~96.0 (small), F2 re-poses
  (108.84 109.30 109.74 110.175 110.38 110.80), F4 spawn puffs + air (112.75-114.3), F5->F6a gale 117.70-118.40 + ink puff
  117.958, F6a 真 seals 119.157 / 119.812, G2 听话 inks in 130.175 / 133.69, H5 strokes stream (169.25-172.75), H6 growth
  strokes + somersault out 176.3, J2 pop into depth 190.885, K2b/K3 stroke run 213.40 -> wet strike 213.807, K4 draught bed +
  last-leaf stir 222.75-223.95, K5 un-writing x3 (224.67 225.37 226.07).
- unchanged on purpose: seal_d1 (59.126; D1 colour completes 59.559 but the echo 'born' starts 59.60, the vocal rule would bury a
  seal there), land_d6 75.025 = the landing (bloom is light, feet carry it), D7/D9/F3/F5/L2 confirmed, J4 gong in seal_echoes
  198.74 kept, F1 none. Gone: none of the v2 cues is a hair catch in F6b (nothing to remove: streetlight 120.687 only).
- skipped (no action sound / PROV): B1 turn, C2 hands, E1 nose tap, E4 beckon, G4 book (PROV, under 'Then 听话'), J5 collapse
  (PROV; flips_j5 already on its start).
- new sources (synth, local, $0): gale, ember, arc, depth_pop, draught, dolly_air, brush_rev.

## CHECKPOINT 2026-11-18 task 2 built and verified
- done: 7 synth sources (sounds.py: gale ember arc depth_pop draught dolly_air brush_rev; $0, local); docs/sound_cues_v3.json via
  tools/audio/sfx/cues_v3.py (76 cues, 28 changes); mix_v3b built (build_v2.py --tag v3b, 26 s; log work/sound/build_v3b.log);
  checks tools/audio/sfx/verify_v3b.py -> work/sound/verify_v3b.json; SOUND.md section "v3b mix" with the table.
- measured: song under layer bit-identical (mix_v3b - layer_v3b rounded to 16 bit = edited song, 0 mismatches 0-229.90 s; ending B
  as approved after); mix_v3 -15.84 LUFS / -1.37 dBTP -> mix_v3b -15.83 / -1.37 (ebur128 -15.8 / LRA 7.5 / -1.4 both), 0 clipped;
  layer -30.36 -> -30.51 LUFS, median 17.2 dB under the song (v2 17.3); unchanged cues -126 dB vs v2 (3 drift <= 1 dB in peak:
  margin_notches, c5_hair_lift, c5_scrunch).
- "weak" by the v2 audibility model: abacus_f4b, cloth_e3, flips_f2, spawn_air_f4, spawn_puffs_f4, strokes_h5, grow_h6, pop_j2, draught_k4.

### Cues changed in v3b
| shot | cue | old time (s) | new time (s) | what | peak dBFS | under song (400 ms, median) | band margin med / p10 | audible (model) |
|---|---|---|---|---|---|---|---|---|
| C5 | breath | 52.55-54.45 | 53.10-54.55 | Mama's breath now leaves her lips at 53.22 (C5a); the breath rises 0.18 s so it is there on 53.22 and runs into the wind | -18.1 | 15.4 | 9.8 / 3.6 | yes |
| C5 | sleeve_wind | 54.60-57.20 | 54.50-56.70 | the wind flow enters C5b at the left edge 54.505 and its ribbons cross the egg to ~56.4 (BOOK flow contract) | -17.5 | 14.2 | 12.0 / 8.4 | yes |
| F4 | abacus_f4b | 114.567 115.002 115.445 115.882 | 113.247 113.688 114.133 + the same four | F4 lantern flares on the beat wave (= the old abacus clicks), three earlier beats added | -22.0 | 34.2 | 20.4 / 11.1 | weak |
| H6 | hair_air | 172.90-177.10 (hair_air) | 172.76-174.40 (gale) | H6 round 3: the gale takes the girl's hair and a strand works loose in the first 36 f (172.76-174.25); the growth and the somersault get their own cues | -16.0 | 16.4 | 12.9 / 5.8 | yes |
| K4 | ledger_pages | 218.75 219.80 220.23 | 218.22 219.40 220.30 220.92 | K4 no hand: a leaf lands 218.22 ('page'); leaf 2 lifts 219.40, hangs and falls back 220.30; goes over and lands 220.92 ('looked') | -18.0 | 27.8 | 6.6 / -13.6 | yes |
| J1 | fingertip_j1 | 189.62 | 189.52 | J1: the fingertip dips at ~189.50-189.55; the character lights from 189.62 | -27.0 | 26.3 | 8.1 / -6.1 | yes |
| K3 | brush_strike | 216.060 | 216.165 | K3: the bloom on 'single breath' is at ~216.2: nearest hit 216.165 | -21.5 | 17.0 | 2.0 / -7.8 | yes |
| G5 | room_yes | 149.285 (silence anchor) | 149.285 (t:) | same end; the 'Yes' now starts 149.152, the bed is 40 dB under it | -19.3 | 10.7 | 7.5 / -5.3 | yes |
| G5 | neon_hum_yes | 149.285 (silence anchor) | 149.285 (t:) | same end; the 'Yes' now starts 149.152, the bed is 40 dB under it | -23.6 | 15.1 | -1.0 / -29.4 | yes |
| B3 | dolly_b3 | - | 26.145-29.29 | B3 3D dolly: page air + pines passing the lens | -15.0 | 15.4 | 12.7 / 5.8 | yes |
| D4 | ember_d4 | - | 68.09 | D4 ember on 通 | -10.7 | 15.4 | 8.8 / -5.6 | yes |
| D5 | arcs_d5 | - | 70.594 71.029 71.471 71.925 72.356 | D5 frontier light arcs on the beats | -19.9 | 15.0 | 6.7 / -2.5 | yes |
| E3 | cloth_e3 | - | 96.00 | E3 small cloth move (no cast whoosh) | -24.3 | 23.7 | 17.1 / 9.4 | weak |
| F2 | flips_f2 | - | 108.84 109.30 109.74 110.175 110.38 110.80 | F2 shadow-puppet re-poses | -13.9 | 23.6 | 15.2 / 8.1 | weak |
| F4 | spawn_air_f4 | - | 112.76-114.30 | F4 spawn: hairs stream in (air) | -20.9 | 19.1 | 14.4 / 8.2 | weak |
| F4 | spawn_puffs_f4 | - | 112.85 113.03 113.47 113.90 | F4 spawn: plucking/blowing puffs | -20.3 | 28.4 | 14.9 / 8.0 | weak |
| F5 | gale_f5 | - | 117.70-118.40 | F5->F6a hair gale streams back | -20.0 | 18.6 | 9.4 / -3.2 | yes |
| F6a | inkpuff_f6a | - | 117.958 118.125 | F6a twin ink puff | -17.4 | 13.7 | 10.0 / 5.3 | yes |
| F6a | seals_f6a | - | 119.157 119.812 | F6a 真 seals (left, right) | -18.7 | 24.3 | 20.1 / 4.4 | yes |
| G2 | ink_g2 | - | 130.175 133.690 | G2 听话 inks in | -22.7 | 12.6 | 4.9 / -0.2 | yes |
| H5 | strokes_h5 | - | 169.25-172.75 | H5 strokes lift off and stream | -16.5 | 20.5 | 14.7 / 9.1 | weak |
| H6 | grow_h6 | - | 174.400 174.824 175.160 175.595 | H6 monkey grows from the strand (3 strokes + scarf) | -18.9 | 16.4 | 12.7 / 6.4 | weak |
| H6 | somersault_h6 | - | 176.334 | H6 somersault out left | -17.8 | 17.9 | 10.1 / -0.1 | yes |
| J2 | pop_j2 | - | 190.885 | J2 pop into depth | -15.8 | 16.6 | 14.8 / 7.8 | weak |
| K2b-K3 | strike_k3 | - | 213.40 213.807 | K2b stroke run + K3 wet strike | -18.9 | 13.0 | 9.8 / -1.6 | yes |
| K4 | draught_k4 | - | 217.20-224.18 | K4 draught (page-turning air) | -26.0 | 25.7 | 18.9 / 6.1 | weak |
| K4 | stir_k4 | - | 222.75 223.35 223.95 | K4 last leaf stirs | -18.0 | 16.3 | 8.2 / -15.1 | yes |
| K5 | unwrite_k5 | - | 224.67 225.37 226.07 | K5 the line un-writes | -26.1 | 14.5 | 6.1 / -12.2 | yes |
## DONE (task 2) 2026-11-18. mix_v3b delivered; the lead decides when the cut switches from mix_v3 to mix_v3b.

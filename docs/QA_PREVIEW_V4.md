# QA: preview_v4 (fourth complete 540p cut; Chinese calligraphy in every room)

CUT pass, 2026-11-18/19 (Claude, Opus 5.5). Preparation and three trial builds, then the final build. CUT spend $0: nothing
was generated. Nothing committed. **Nobody has watched this cut, or any shot in it, in motion.** Every statement below
rests on decoded frames, contact sheets, measured numbers, or the teams' logs, and says which.

## 1. What is in the cut

| File | What |
|---|---|
| `media/cut/preview_v4.mp4` = `previews/chaosmonkey_preview_v4_540p.mp4` | English lyric layer on, calligraphy on |
| `media/cut/preview_v4_clean.mp4` = `previews/chaosmonkey_preview_v4_540p_nolyrics.mp4` | English lyric layer off, **calligraphy on** (it is part of the picture: one export, no separate rednote version) |
| `work/cut/preview_v4/contact_A..L.jpg` | first / middle / last frame of every shot (and the END tail) |
| `work/cut/preview_v4/lyr_0..5.jpg` | one frame per English lyric segment (72), from the built cut (`work/cut/qa_v4_lyrsheet.py`) |
| `work/cut/preview_v4/roomcal_proof/` | every calligraphy row on 3 frames of its window (first full-opacity, middle, last) |
| `review/preview_v4_notes.html` | the director's notes page (11 questions, proofread table of the new Chinese lines) |
| `review/lyrics_zh_v4_proof.md` | the 33 new Chinese lines for Jade's proofread |
| `work/cut/build_v4.sh` | the whole build in one command (`MIX=mix_v3` to build on the approved-by-ear mix instead) |
| `work/cut/preview_v4/verify.txt`, `sources.txt`, `scan.json` | verification; every source with mtime; boundary/frozen-frame scan |

Both cuts: 960x540, 24 fps CFR, yuv420p BT.709, AAC 320k, the small shot id top left (the G6 slot is labelled G5).

**Audio: `media/sound/mix_v3b.wav`** (lead's decision, 19 Nov). The director approved the moved "Yes" in `mix_v3.wav` **by
ear**. `mix_v3b` has the bit-identical song under it (same moved "Yes"), the same loudness and true peak (-15.83 LUFS,
-1.37 dBTP), and differs from mix_v3 only in the effects layer: 28 cue rows re-timed or added for the v4 picture (listed in
`docs/SOUND.md` "v3b mix"). **Nobody has heard mix_v3b.** By SOUND's model (not ears), nine of the new cues sit faint under
the loudest song: the rap and drop 2. The notes page asks her (question 10).

## 2. Verified by number (`work/cut/verify_v4.py`, run by the build)

- **5806 frames** in each cut = 241.920 s x 24. Video 241.9167 s, audio 241.9160 s. Every packet the same duration (CFR).
- **Per shot:** all 65 shots have exactly their `docs/shots.json` frame count and start on their `in_frame`; none short;
  plus `END` 86 f (5720-5805). No slate in any slot.
- **Audio:** correlation with mix_v3b 0.9999 at 0.0 ms; in the moved-"Yes" window (148.5-150.0 s) 0.9998. Cross-check
  that the cut carries v3b and not v3: residual energy of the cut's audio against v3b -35.4 dB, against v3 -23.4 dB.
- **No duplicated frame at any of 72 boundaries** (shot cuts, splices, the G5/G6 span), clean cut.
- **G5 over two slots:** frame 3583 of the cut matches G5.mp4 frame 68 (mean abs diff 1.83/255, against 3.86 for frame
  67 and 1.98 for 69: frame 68, as planned; the shot is near-still there).
- **Calligraphy vs English lyric layer:** `tools/cut/roomcal.py --check` over every frame: 0 box collisions.
- **B2 -> B3 landing:** B2's last frame vs WORLD's round-2 B3 frame 0: 2.83/255 (B2 was warped onto an earlier B3;
  v3's landings were 2.2-2.5; left as is on the lead's decision).
- Frozen runs (>= 6 identical frames, inside shots): A1 31-130 (title hold), C1 holds, C4 1191-1253, G2 3215-3224, the
  H1-H3 album holds (3697-3960, by design of the faces sequence), H5 4042-4056, J5 tail 4879-4888, K5 5383-5391.
  Listed in `scan.json`; none at a boundary.

## 3. Splice table v4 (`tools/cut/splice.py`; `docs/picks_v4.json`, `media/comp/spliced_v4/`)

v3's `docs/picks.json` and `media/comp/spliced/` are untouched. `docs/shots.json` is **not** edited.

| Slot (frames) | Built from | Cut on song frame | Source |
|---|---|---|---|
| C5 (115) | C5a 57 + C5b 58 | 1311 | unchanged |
| D2 (80) | D2 first 65 of 80 + D2d 15 | 1531 | unchanged; D2's north bow (63.98) is under D2d |
| F3 (41) | F3a 29 + F3b 12 | 2694 | unchanged |
| F4 (83) | **F4.mp4 alone** (SWARM's one shot, s0-82) | - | LOG_v4_swarm DONE |
| F5 (43) | F5.mp4 (s83-125) | - | SWARM |
| F6 (83) | F6a 50 (s126-175) + **F6b 33 = the mirror shot** | 2882 | SWARM, BED+CAR, REVISION_V4 §12 |
| **G5 (68) + G6 (10)** | **G5.mp4 (78 f) frames 0-67, then 68-77** (a pick with an in-point) | (3583: continuous) | REVISION_V4 §12; G6's blank frames are gone |
| I2 (66) | pages/I2_full | - | unchanged |
| I3 (97) | I3a 40 + I3b 57 | 4431 | unchanged |
| K2 (78) | K2a 38 + K2b 40 | 5091 | unchanged |
| L3 (60) | L2b 26 + L3 34 | 5686 | unchanged |
| END (86) | black tail | 5720 | as v3 |

Cuts inside single comps (for the lyric layer's schedule, `tools/cut/lyrics.py` PARTS): B2 lap -> over the shoulder at 591
(24.6 s, v3 588); **E3a -> E3b at 2304** (ATTIC's two-cut E3); I4 -> its page view at 4545; K1 room -> page at 4973.
`EXPECT` still stops the build if a part changes length.

## 4. Chinese calligraphy (REVISION_V4 §1.3) and the English lyric layer

**Text:** `design/text/lyrics_zh_v4.txt` = Jade's proofread v3 file unchanged + 33 new keys (`# NEW v4, for Jade's
proofread`): the room lines, H3/H4/J3/J4/K1 lines, "Wouldn't you? You're able." (I4), the 8 rap lines as the sung words, and
BOOK's G2c (听话). Proof table: `review/lyrics_zh_v4_proof.md` and the notes page. A line that starts in a room and goes on
to a page whose inscription carries it reuses that inscription's text (B2 <- B3 col 1, C5a <- C5, I3a <- I3, K2a <- K2,
L1 <- K5). Everything else on the pages is the existing static inscriptions (not touched).

**Renderer:** `tools/cut/roomcal.py`, applied at assembly (a proofreading change is a re-render). Same typeset hand as the
inscriptions (Ma Shan Zheng, dry brush), columns top to bottom, right to left, one small 白文 seal 悟空. Rooms: light on dark
(warm paper-white, 0.92 x brush density, soft edge), **26 px at 540p** (52 at 1080p) in every room row, halo 0.2-0.3 only on
busy backgrounds (F2, F4, F6b, J3, J4). Album/page shots without an inscription (H3, H4, the K1 page part, G3's paper
margin, B3's tail): ink, **30 px** = the inscriptions' size (lead's decision). 6-frame fade in on the line's first word,
6-frame fade out after its last; at a cut inside a line it switches with the picture.

**Placement:** `design/text/roomcal_v4.tsv`, 42 rows, every sung line without an on-screen inscription. Sides from the teams'
logs; regions measured (Sonnet MEASURE agent, `work/cut/roomcal_measure/NOTES.md`: luma mean/p90 over every 8th frame of
each window, visual check) and re-measured by me on the final comps for B2a, D3 (10 frames at full size: ~30 px clear of
the window lettering, no face), E3a, E3b, F1, J3, J4, H3 (per-frame bare-paper measurement), K1b. All rows are final except
B3 (depends on WORLD). Compromises, all known:
- F2: the only dark strip is a 52 px pillar; the block touches the amber window edge. F4/F6b: busy sky / no free band (halo).
- J3: the paper-cut flash 4645-4649 is pale: 5 frames where the light text is faint.
- H3: placed in the one strip bare in all three face holds (x750-825); leaves at 3966 (0.6 s before the line ends) because
  the pull-back has no bare strip. H4: two places (empty cell right of the girl, then the felt beside the album), 6-frame gap.
- K1a ends at 4950 (the bright page fills the left); **K1b: screen-fixed ink over a panning page** (weak point, lead's
  decision), ends at 5019 because the officials walk into every free spot: the line's last 1.4 s has no Chinese.
- B3: WORLD's dolly carries the inscription out of frame by ~637; its column 2 is set in ink top-left from 640 (provisional).

**English lyric layer** (`tools/cut/lyrics.py`): timed from `analysis/timing_v4.json` (the moved "Yes"). The rap is English
only, full size (the sans-serif Chinese row is gone). Placements re-set for the v4 pictures: F4, F5, F6a (no leaf: along the
bottom, under the 真 seal), E4 (off the monkey's tail), G4 (held 14 f until the strip opens; right after the push),
G5 and the G6 slot (right; v3's spot was her chest), I1 (right of the calligraphy). Checked on one frame per segment
(`lyr_*.jpg`, 72 tiles) for the final cut: D5/D6's tail sits cream on the night flight, legible; no line on a face except
**E3a** (the English sits over the child's shoulder and jacket, lower centre-left: minor) and **I1** (over the girl's arm).

## 5. Known problems, ranked

Frame numbers are song frames = cut frames. Owner in brackets. Sources: every team's DONE/"still weak" list, the singing
audit `work/review/sing_v4/audit.md` (machine measurement, nobody watched), my frame checks.

**Lip-sync (audit flags, `review/sing_v4/index.html` has every singing shot with a sync slider)**
1. **C3 FAIL** [ATTIC]: Mama's mouth shut for 19 f while words are sung (f57-75), frozen 12 f (f25-36).
2. **G1 FAIL** [ATTIC]: first mouth movement 9 f late, frozen 13 f (f55-67) (face only 77 px: noisy measurement).
3. **K2a FAIL** [BED+CAR]: mouth moves on 50 % of the words; frozen 15 f (f3-17). Logged as best of 4, face ~200 px.
4. **SUSPECT G4** (shut 8 f, f69-76; 87 px face), **I4** (67 % of words, frozen f0-9), **J4** (mother shut 8 f).
5. **F1** [BED+CAR]: new take (ls4w_F1_ahold1s1, index finger to her chest, hand on the strap); the audit's OK is on the
   numbers, the lead's read is "improved but not passing". A/B page `review/f1_ab/index.html`.
6. E3 not measurable (face in view on 44 % of the sung frames); E3b's face is frontal with a closed mouth while "a spell
   I'd remember well" is sung (by design of the lead's E3 decision).

**Picture**
7. **J4: the 1988 half's arms go up ~0.9 s early** (197.8 vs the gong 198.74); the 2026 half is on time. A join was not
   possible without a pop [ATTIC; question 6].
8. **E3b is a held pose**: no visible flourish, the pushing palm edge-on, a jump in scale at the 2304 cut [ATTIC; q5].
9. **D6 -> D7 hard colour cut**: night blue into bare pale paper at 1834 (accepted for this cut) [lead]. D-flight: the
   carving is legible only for the first ~30 frames; dot-grid glow s27-54; the monkey is small [SWARM/D-FLIGHT; q2].
10. **H6** (round 3): from my lyric tiles at 4184 the strand's curl passes the end of the inscription's first column
    (一根毫毛); the growth is sped up 3-5x; seam with H5 a near-match [BOOK; q3].
11. **F3b**: faint 12-frame puff (~3x speed); the retake submit was refused by the permission check and not re-tried [ATTIC; q7].
12. **K1 page part**: screen-fixed ink over a moving page; no Chinese 5019-5053 (section 4). BOOK's page has a stretched
    band at its right edge; hard cut room -> over-the-shoulder as v3 [BED+CAR/BOOK].
13. **B3**: inscription leaves frame by ~637 (provisional ink overlay of column 2); WORLD round 2's reviewer: second half
    "still a centred peak growing", white matte halos on pines [WORLD]. B4/B5/J5 are round 1. J2's deepening boils, hitch
    f9-10 [WORLD].
14. **C5b**: the wind's motion is the video model's invention, lines cross the egg rather than parting round it; C5a has no
    flow tail at the cut (1311) [BOOK/ATTIC; q4].
15. **Swarm F4-F6a**: crowd reads as texture at 540p; spawn smears were a reason other candidates lost; the twin arrives
    in ~2 frames from an ink puff [SWARM; q1].
16. **E1**: no nose tap / cross-eyed giggle, the girl's eyes shut; **B1**: acting weak (no tug), two half-winks [ATTIC].
17. **G2**: 听话 placement judged on sheets only; the far end of the band shows as a gold arc behind his hand from clip f56
    [BOOK; q8]. **G3** nearly static.
18. **K2b -> K3**: only the stroke matches (oblique painting into a flat page); K3 near-still after f16; K4 lands ~1 f
    early on the hit [BOOK].
19. **J1**: the press is a 1 px dip at ~189.50 (0.1 s before the cue; SOUND re-timed to 189.52); the lit character hides
    under the fingertip; the hand dissolves as a smear f10-13 [BED+CAR].
20. **L2b** not matched to BED+CAR's L2 (v3's match cut is looser) [ATTIC].
21. Stage: D7's ring a soft grey halo; D8's monkey small; J3's yellow mustard under the red light [STAGE].
22. Sound: mix_v3b unheard; nine cues measure faint under the rap and drop 2 [SOUND; q10].

## 6. What nobody has done

- **Nobody has watched preview_v4, or any of its shots, in motion.** Nobody has listened to mix_v3b.
- Lip-sync: only the audit's numbers and the teams' strips; no playback.
- Sound-cue sync on the picture: SOUND re-timed to the teams' logged times; I did not spot-check cues on frames this pass
  (v3's §6 table was not redone).
- The calligraphy was checked on 3 frames per row (MEASURE: every 8th frame for luma), not on every frame; brief motion
  between samples could cross it. The 1080p calligraphy (52 / 60 px) has not been rendered.
- No 1080p render of any v4 shot by CUT.
- The notes page was built and its layout rendered headless (no H.264 in that browser, so playback/seek on the page itself
  was not exercised).

## 7. Rebuild

`work/cut/build_v4.sh` (about 10 min cold; renders cached per source mtime/size and per calligraphy/lyric signature):
splice, calligraphy proof + collision check, both cuts (`MIX`, default mix_v3b), contact sheets, B2->B3 landing number,
verification, copies to `previews/`, notes page. `work/cut/build_v4.sh preview_v4_trial` builds a trial without copies.
After Jade's proofread: edit `design/text/lyrics_zh_v4.txt` (and, if a line gets longer, check `roomcal.py --proof`, which
reports any row that no longer fits its region), then re-run the build. Any change to the TSV or the text re-renders every
shot carrying calligraphy (about 40 of 65).

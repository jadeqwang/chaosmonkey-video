# QA: preview_v3 (third complete 540p cut, all rooms re-shot)

CUT pass, 2026-11-17/18. Two builds: the first complete cut (20:30), then the **final rebuild after the fix round**
(00:5x on the 18th), which this file describes. Spend $0: nothing was generated. Nothing committed.
Nothing here was watched in motion: every check is on frames, sheets and measurements.

## 1. What is in the cut

| File | What |
|---|---|
| `media/cut/preview_v3.mp4` = `previews/chaosmonkey_preview_v3_540p.mp4` | lyric layer on |
| `media/cut/preview_v3_clean.mp4` = `previews/chaosmonkey_preview_v3_540p_nolyrics.mp4` | lyric layer off |
| `work/cut/preview_v3/contact_A..L.jpg` | first / middle / last frame of every shot (and of the END tail) |
| `review/preview_v3_notes.html` | the director's notes page (v3 likeness sheets, the 7 open questions) |
| `work/cut/build_v3.sh` | the whole build in one command (about 4 minutes) |
| `work/cut/preview_v3/verify.txt`, `sources.txt` | verification output; every source file with its mtime |

Both cuts: 960x540, 24 fps CFR, yuv420p BT.709, audio `media/sound/mix_v2.wav` (ending B, rebuilt in the fix round,
section 3). Like preview_v2, both carry the small shot id top left (clear of the A1 title block, which is lower left).

**Verified** (`work/cut/verify_v3.py`, run by the build):
- **5806 frames** in each cut = 241.920 s x 24 (5806.08, rounded). Video 241.9167 s, audio 241.9160 s: the mix is
  trimmed by 3.3 ms (0.08 frame) to the last whole frame.
- Every packet has the same duration (CFR).
- **Per shot:** all 65 shots have exactly their `docs/shots.json` frame count and start on their `in_frame`; none is
  short; plus one `END` unit of 86 frames (5720-5805). Sum 5806.
- Audio against the new `mix_v2.wav`: correlation 0.9999 at 0.0 ms. In the changed window (113.5-114.7 s) the cut
  matches the new mix (0.9997) better than the previous one (0.9988).
- No slate (all 65 slots have a comp). No black frame except A1's first 4 frames (the sign has not lit) and from 5714
  on (after the neon). No duplicated frame at any shot boundary or splice (`work/cut/qa/scan.py`,
  `work/cut/qa/scan_final.txt`; the frozen runs it lists are holds inside shots, section 5 item 9).

**Ending (REVISION §9).** `docs/shots.json` is unchanged (L3 still ends at 5720 = 238.333). `assemble.py --tail black`
appends the hold to the end of the audio: the last frame of L3 (the dark room, mean level 2.9/255) sinks to true black
over 8 frames, then black to frame 5805. The manifest lists it as `END`.

## 2. Splice table used (`tools/cut/splice.py`, v3)

| Slot (frames) | Built from | Cut on song frame | Source of the rule |
|---|---|---|---|
| C5 (115) | `C5a` 57 + `C5b` 58 | 1311 | unchanged |
| D2 (80) | `D2` first 65 of 80 + `D2d` 15 | 1531 (63.792) | unchanged; the monkey's north bow (63.98) is under D2d as in v2 |
| F3 (41) | `F3a` 29 + `F3b` 12 | 2694 | LOG_v3_bedcar |
| F4 (83) | `F4a` 38 + `F4b` 45 | 2744 | LOG_v3_bedcar |
| F6 (83) | `F6a` first 50 of 63 + `F6b` 33 | **2882 (120.083)** | LOG_v3_bedcar round 2. Fix round: both 真 seals are now inside the first 50 |
| I2 (66) | `pages/I2_full` | none | BOOK's page comp. `media/comp/I2.mp4` is still the v2 hand-shadow shot and is not used |
| I3 (97) | `I3a` 40 + `I3b` 57 | 4431 | LOG_v3_bedcar |
| K2 (78) | `K2a` 38 + `K2b` 40 | 5091 | LOG_v3_bedcar |
| L3 (60) | `L2b` 26 + `L3` 34 | 5686 | LOG_v3_attic |
| END (86) | black tail | 5720 | REVISION §9 |

Not spliced: K1 is BED+CAR's `K1.mp4` alone (it renders BOOK's `shots/K1page.py` for 4973-5053; checked against
`pages/K1_full.mp4`: same frames). I1 and I4 are single comps (I4's last 10 frames are J1's view, by design; the
picture runs straight through the I4/J1 boundary).

**Choices where the brief was ambiguous:**
1. *"L2 = BED+CAR's L2 + ATTIC's L2b; L3 = ATTIC's L3.mp4."* `shots.json` has L2 = 5597-5660 (63 f) and L3 = 5660-5720
   (60 f), and BED+CAR's L2 is already 63 f ending on 5659. So the **L2 slot is `L2.mp4` alone and the L3 slot is
   `L2b` + `L3`**: the 1988 half of the match cut starts ON 235.833 (frame 5660) and every slot keeps its count.
2. *Extending the picture.* `shots.json` is not changed; the black is an appended unit.
3. `splice.py` has an `EXPECT` table: if a part changes length the build stops instead of silently moving a cut.

## 3. What I changed or re-ran myself

Cut-level:
- `tools/cut/splice.py`: v3 table, `EXPECT` guard, `work/cut/splice_report.json`.
- `tools/cut/assemble.py`: `--tail black`.
- `tools/cut/lyrics.py`: the rap's English replaced with the director's 8 lines (REVISION §7); `PARTS` for the v3
  internal cuts (B2 at 588, F6b at 2882, I2 as a page, I4's page view from 4545, K1's page from 4973; D3 is one unit
  again); every placement override re-set against the v3 pictures (section 4).
- `tools/review/notes_page.py`: v3 head sheets, the 7 questions, pictures inside a question, v3 shot descriptions
  under the video (REVISION §5), an END entry, stills refreshed when the cut is rebuilt.
- `tools/cut/README.md`; `work/cut/build_v3.sh`, `sync_b2.sh`, `verify_v3.py`; QA helpers in `work/cut/qa/`.

**Sound (fix round, on the lead's instruction).** The two abacus clicks at 113.688 and 114.135 fell over the mirror
shot (F4a), before the leaf appears on frame 2744. They are removed from `docs/sound_cues.json` (cue `abacus_f4b`
now has the four clicks 114.567-115.882) and the mix rebuilt with `tools/audio/sfx/build_v2.py`.
- Previous files kept: `media/sound/mix_v2_prev.wav`, `layer_v2_prev.wav`; the old cue sheet and QA numbers are in
  `work/cut/bak_v3/`.
- New mix: 241.920 s, 24-bit, ending B, **true peak -1.37 dBTP**, -15.84 LUFS (song -15.88), 0 clipped samples.
- **Song untouched:** mix minus layer is bit-identical before and after (max change 0.0).
- **Where it differs from the old mix:** only inside **113.590-116.272 s**; bit-identical everywhere else. That is
  wider than the two clicks' own windows (113.59-113.95, 114.10-114.40), so "only in that window" is not exactly
  true, and this is why: the builder sets levels by measurement on the summed layer. Inside the two click windows the
  click peaks are gone (layer peak -14 -> -20 dBFS) and what remains there (streetlight swoosh, car bed) is 0.7-1.4 dB
  louder, because the bus is no longer riding down for the clicks. The four remaining clicks changed by at most
  0.2 dB RMS (largest sample difference -39 dBFS). Not listened to.
- `docs/SOUND.md`: the auto block was rewritten by the builder; the hand-written cue list now names the removal.

Other teams' renders re-run in the first build, **without editing their scripts**, because their hand-over contracts
say to: B2 on B3's new first frame (`work/cut/sync_b2.sh`, part of every build; now **2.20/255** against B3 frame 0,
still up to date after ATTIC's own re-render of B2); and I1, K1, K2a on fresh stills of BOOK's first frames (landing
differences 8.5 / 7.7 / 6.1 -> 4.2 / 3.0 / 4.0 per 255; K1's streaked page edge gone). Old files: `work/cut/bak_v3/`.

## 4. Lyric layer against the inscriptions

Checked on one frame per lyric line per unit (`work/cut/qa/preview_v3_lyr_00..04.jpg`) and on the contact sheets,
again after the fix round for every re-rendered shot. No lyric line touches a painted inscription, its seal, a name
slip, or the A1 title block (A1 has no lyric; the title sits lower left, the new sign is in the far window).

Moved because of an inscription, seal column or name slip:
| Shot | Now |
|---|---|
| B2 (page part), B3 | centre-right bare page, under the inscription column |
| B5 | right, under the inscription (same spot as C1, which carries the line on) |
| B4 | right of the macro character, mist behind the line; the inscription is top right, clear |
| D2 | left of the monkey (the 才 seal column and the inscription are right) |
| **F4b, F5, F6a** | **fix round: in the bare band under the leaf.** The leaf's bottom rule measures y 0.817 (F4b, F5) and 0.806 (F6a). F4b: baseline y 0.965 at 90 %. F5 and F6a: y 0.985 at 80 %, so the English stays on one row and the Chinese row clears the rule. Nothing crosses a cell, slip, seal or figure any more |
| H5 | right, on the mist veil under the inscription |
| I2 | bare cloud lower centre, right of the couplet |
| I3b | lower left corner, below the inscription's seal (it was touching it) |
| K1 (page) | under the walkers |

Moved because the picture changed: B1, C3, D3, F1, F3a, F3b, G1 (both lines), H3, I3a, I4 (page part), J4, K1 (room).
Re-checked after the fix round and left as they were: C2 ("Monkey!" lower right, clear of the new monkey shadow),
C5a, D2d, F2 (door panel left, clear of the pane and the child), I4, J1.

Still not clean (cannot be fixed by placement):
- **B4**: the wide half is carved rock edge to edge; the line has a mist band and still sits on carving (as v2).
- **H3**: under the chins, on the rule between rows; it clips the tops of the next row's faces at the end.
- **C1**: during the two rubbing holds (5 frames each) the ink-coloured line is on black, unreadable for those frames.
- **D6**: the tail of the D5 line (6 frames) sits on the cloud line.

## 5. Problems, re-ranked after the fix round

Frame numbers are song frames = cut frames. Owner in brackets.

**Fixed since the first build**
| Was | Now |
|---|---|
| 1. F2 was the v2 shot | v3 shot: same child, dress and seat as F1/F3. See the read below for what is left |
| 2. Jump cut L2b -> L3 (awake / asleep) | continuous: same pose, the camera steps back |
| 3. Neon sign drawn three ways | one sign, one colour in every attic shot that shows the window (read below) |
| 4. L2 -> L2b not a match | now a match in framing and gesture |
| 5. F6a's second 真 seal cut off | both seals inside the 50 frames used: left on 2859, right on 2875 |
| 6. Two abacus clicks over the mirror | removed from the mix (section 3) |
| 7. J1's page was v2's grey cliff | J1's page is J2's blue-green peak |
| 13. Lyric across the swarm leaf | in the bare band under the leaf |
| 12. C2's shadow was two hands | a monkey's head in profile, joined to the two hands |

**My read of the cut points the lead named**
- **2612 (F1 -> F2) and 2665 (F2 -> F3).** Same child (brown braids, strawberry dress), same grey high-backed seat,
  the window on her left as in F3, and she is alive: pointing, laughing, kicking. Two things still set F2 apart.
  (a) Colour: F2's cabin is blue-violet (frame mean R,G,B 79,70,86 on 2612) between two warm brown-amber shots
  (84,66,56 before; 92,69,60 after). (b) The window: on 2612 it is a flat dusk blue with no road or streetlights,
  and by 2630 the whole pane is a bright cream screen, the brightest thing in the car sequence; F1 and F3 show a
  dark road with amber lamps through the same glass. It reads as the same car at night with the pane turned into a
  lit screen, which is the idea, but the cut in at 2612 is a visible temperature jump.
- **2882 (F6a -> F6b).** Clean. Both 真 seals are down (left 2859, right 2875), six frames of hold, then the cut to
  her catching the hair.
- **4581 (J1 -> J2).** The page carries: same peak, near enough the same framing, the pressed character glowing
  under her fingertip at the foot of the peak. Two small things: J2 is more saturated and its paper whiter than the
  torch-lit page in J1 (a step up in brightness at the cut), and in J2's first frames the lit character is at the very
  bottom edge of frame (about y 0.98), nearly cut off, so the eye may lose it for the first half second.
- **5660 (L2 -> L2b).** A real match now. Both: the mother kneels at frame left reaching to the upper right, both hands
  on the quilt at the child's chin, the child's head upper centre-right. Differences that remain: 1988 is tighter and
  seen from further behind (Mama's face is hidden; Jade's profile is visible), and the hands are already at the chin
  in both, so the 1988 "pull" is only a smoothing of the quilt (the blanket sound at 235.88-236.28 plays over that).
- **5686 (L2b -> L3).** Continuous. Same pose and gesture, the camera steps back and round to the side; the sign is the
  same; the room drops a little (frame mean 46 -> 37). The floor differs between the two setups (scattered books at
  the left in L2b, a bare mat in L3); I doubt anyone sees it in 26 frames.
- **Neon across the attic shots** (A1, A2, A3, A4, C5a, D2d, D9, L2b, L3 show the window; B2, D3 and the close
  two-shots do not). One sign and one colour: red glass, the two characters 酒家 pale pink-white, vertical, in the
  right-hand part of the window, in every one. What it is not, in the closer shots, is a steep wedge: in A2, A4, C5a
  and D9 the lettering reads as a sign facing the window, legible and fairly broad; only the wides (A1, L3) read as a
  narrow blade. Consistent, then, but if the brief's "steep wedge of red light" is meant literally, the close shots
  do not show it.

**Remaining, ranked**
1. **F2's colour and window against its neighbours** (2612-2664) [STAGE]: as above. A grade toward F1/F3's warm night
   and a hint of road through the glass before the pane lights would close it.
2. **G2's margins are brighter than its neighbours'** [BOOK vs ATTIC]. Left-margin paper: G1 last (236,227,212), G2
   (245,237,222), G3-G5 (236,227,212), G6 (233,224,210): a step of about 9 levels at 3059 and back at 3225. ATTIC's
   strips also drain 40 % to grey while BOOK's drain fully.
3. **J2 opens with the lit character at the frame edge**, and brighter/more saturated than J1's page [BOOK].
4. **The sign is not a wedge in the close attic shots** [ATTIC]: consistent, but see the read above.
5. **Tone steps at the page landings** [BED+CAR / BOOK]: I1 -> I2 (4325) 4.7, K2a -> K2b (5091) 3.4, K1's push -> page
   (4973) about 3 per 255: BOOK's torch vignette switches on at the cut.
6. **No push into I3b** [BED+CAR, logged]: 4431 is a straight cut from the daughter's face to the banquet page.
7. **B1: Mama is only a shoulder and hair** until the last second [ATTIC, logged].
8. **L2b's blanket cue** now plays over a tucked quilt being smoothed, not pulled [ATTIC / SOUND]: minor.
9. **Long holds** (frame identical to the previous one): K5 for nearly all of its 110 frames; K3 44 frames
   (5132-5175); A1 from frame 32 to 130 apart from the sign's stutters [BOOK, ATTIC].
10. **E2, I2**: a few smeared figures in the video-model takes [BOOK, logged].
11. Lyric residue: B4, H3, C1's rubbing holds, D6's 6-frame tail (section 4).
12. C6 -> D1 paper: (233,224,209) -> (237,228,213) at 1408, 4 levels [BOOK vs STAGE]. Not visible at speed.

Not problems: every splice is on its logged frame; B2 -> B3 (627, 2.5/255), C1 after B5, K2a -> K2b land cleanly; D1 ->
D2, F4b -> F5 and H3 -> H4 are continuous; no old shot is in any slot.

## 6. Sync spot-checks against REVISION §11 (measured on the final `preview_v3_clean.mp4`)

| Cue (s) | Frame | On screen | Verdict |
|---|---|---|---|
| A3 apron lifted 11.68-12.04 | 280-289 | over her head 284-288, clear by 288 | on |
| A3 apron on the hook 12.220 | 293 | arm at the hook 292-294 | on |
| A3 towel 12.400 | 297 | towel going up 296-298 | on |
| C5 hair lifts 53.220 | 1277 | hair starts to rise by 1278, streaming by 1282 | on (within 1 f at this size) |
| C5 scrunch 53.950 | 1294 | curled into Mama, eyes shut 1290-1294 | on |
| D9 on the stack 83.244 | 1997 | up on it 1997-1999 | on |
| D9 wobble 83.475 | 2003 | arms out, tilting 2003-2007 | on |
| D9 **stack topples 83.798** | 2011 | 2009 stack leaning, 2011 child in the air, Mama lunging, books going | on |
| D9 lands 84.127 | 2019 | on the mat 2019 | on |
| D9 catch 84.351 | 2024 | Mama's hands on her 2023-2025 | on |
| D9 settle 84.570 | 2029 | last book down by 2029 | on |
| F3 daughter's puff 112.146 | 2691 | mouth round 2688-2690, lips pursed blowing 2691-2693 | on, or up to 2 f early: check in motion |
| F3 little Jade's puff 112.372 | 2696 | cheeks 2696, hair flying 2697-2698 | on |
| F4b clicks 114.567, 115.002, 115.445, 115.882 | 2749.6, 2760.0, 2770.7, 2781.2 | all cells change pose on 2749, 2760, 2770, 2781 | on |
| F5 seals 116.320, 116.736, 117.200, 117.628 | 2791.7, 2801.7, 2812.8, 2823.1 | seal frames 2791, 2801, 2812, 2823 (others on the half beats) | on |
| F6a seals | 2859 / 2875 | left seal first seen 2859 (119.125), right 2875 (119.792) | both shown |
| J1 fingertip 189.620 | 4551 | finger travels 4548-4551, the picture change settles into the push from 4552 | on |
| L2 pull 235.33-235.78 | 5648-5659 | quilt moves 5648-5658, tucked 5658-5659 | on |
| **L2 match cut 235.833** | 5660 | first 1988 frame is 5660 | on, exact |
| **Neon off 237.840** | 5708.2 | last lit frame 5708 (mean 29.0), first unlit **5709** (16.4); room gone by 5716 | on (first frame after the cue) |
| Audio end 241.920 | 5806 | last frame 5805, black | on |

Not measured here: lip-sync (LIPSYNC's gate owns it; nobody has watched the takes in motion), sound levels by ear.

## 7. Not revised, or known weak from the team logs

**Not revised:** G6 (10 blank frames, "as v2"). K3, K5 pictures are v2 plus an inscription; K4 is v2 plus a hand.
(F2 and J1's page, unrevised in the first build, are now v3.)

**Lip-sync as logged:** PASS B1, C3, E1, E3, G1 (envelope weak, r 0.23), G5 (acted, placed by hand), I1, I3a, I4.
Borderline: G4 (vowels open exactly 0.80; two earlier takes failed). **F1 failed the gate's numbers** (envelope 8.8 f
early on a periodic rap) and ships on the lead's eye verdict of the strip. Mouths move unsynced: J4 (all four), F4a
(the daughter in the mirror). No singing face by design: B2, D3, F3, G3, K1, K2a. All verdicts are from strips and
stills, never playback. I4 was re-rendered in the fix round; I have not re-gated it.

**Weak, by team (their own lists, shortened; fix-round items removed where I could see the fix):**
- ATTIC: G4 (Mama cut by the strip, the books she glances at are out of frame); D9 (a jump in the climb, aftermath
  1.5x); B2's over-shoulder half is a still under the warp; J4's 1988 half is a red glaze; A3's softening smile is 4
  frames.
- BED+CAR: F1 as above; I1's push is 16 frames; F3a plays 1.5-1.9x and L2's pull 2.8x to hit their cues; the morph's
  attic background has bed-like shapes for 4 frames.
- BOOK: H5 (the shadow reads by head and ring more than outline); C5b's mist is whiter than the paper and stylised;
  D5 generation 3 is dense for half a second; J2's threads are brief; K4's hand is a still cut-out; I2's hawk; G2's
  band is a wash; I3b has a faint inpaint mark at the bare place; no medium switch in D5.
- STAGE: D1's 亮相 holds 1.1 s and the clip is 720p; D2's bows are palms-forward pushes, the south bow shallow; D6 reads
  as fingers at once and the monkey is about 150 px; D8's climb has two teleport-like frames; J3's yellow reads orange
  under the red light; swarm figures are small (smaller still now the leaf leaves a band); F5 is one per half beat.
- FACES: nothing open; 鲁智深's 戒疤 dots are below the leaf's resolution.
- Nobody rendered v3 shots at 1920x1080 except six BOOK spot-checks.

## 8. Rebuild

`work/cut/build_v3.sh`: B2 sync if B3 is newer, splice, both cuts, copies to `previews/`, contact sheets,
verification, notes page. Renders are cached per source mtime and size, so only changed shots re-render.
`work/cut/preview_v3/sources.txt` lists every file used with its mtime; a comp newer than that list means the cut is
stale. Fix-round files used (17 Nov): A1 20:44:13, A2 20:44:01, A3 20:43:15, A4 20:43:23, B2 20:43:41, C2 20:42:57,
C5a 20:43:48, D2d 20:43:50, D9 20:43:32, F2 20:48:58, F4b 20:36:11, F5 20:36:16, F6a 20:36:23, I4 20:40:12,
J1 20:39:48, L2b 20:49:22, L3 20:49:48; BOOK's polish: B3 19:56:14, B4 20:00:34, C5b 19:52:48, D4 19:56:47,
D5 19:59:22, J2 19:59:30, H5 20:03:15. `mix_v2.wav` rebuilt 18 Nov 00:3x.

Caveat for whoever re-runs it: `work/tmp/` is shared and other teams empty it; the build keeps nothing there between
steps.

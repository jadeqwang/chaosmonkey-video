# QA: preview_v1

Reviewer: QA agent, 2026-11-17. Cut reviewed: `media/cut/preview_v1.mp4` (960x540, 24 fps, 5720 frames, mix_v1). Spend $0.
I changed no project file outside `work/qa/` and this report.

How it was checked:
- **Every 6th frame watched.** All 40 sheets, labelled with shot and song time: `work/qa/sheets/sheet_00..39.jpg`.
- **Every cut.** 64 cuts plus the 7 splices, showing the 2 frames before and the 2 after: `work/qa/cuts/cuts_00..11.jpg`. Numbers for each cut are in `work/qa/cuts/cut_table.tsv`.
- **Per-frame measures.** Mean difference from the previous frame, frame-to-frame correlation (catches rubbing flips), red-pixel count (catches seals), brightness and saturation: `work/qa/frame_stats.npz`, per shot in `work/qa/shot_stats.txt`. Probes are in `work/qa/sync/probe*.txt`.
- **Lip-sync.** `tools/review/lipsync.py --maxlag 0.35` run on each lip-sync range cut from the final film: `work/qa/lipsync/` (plots, clips, mouth strips).
- **Ink coverage and squint.** Run with `tools.ink.qa`'s own `mark_mask` and `mass_report`: `work/qa/coverage.txt` and `.json`, plus the squint sheet `work/qa/squint/squint_all.png`.
- **Text.** Full-resolution crops are in `work/qa/text/`.
- **Audio alignment.** The cut's soundtrack sits 0 ms from the song in all six windows tested, so every offset below belongs to the picture.

Frame convention: the audio event's frame is ceil(t*24), as in AUDIO_MAP. Offsets are picture frame minus audio frame.
Large intermediates are in `work/qa/_cache/` (about 1.3 GB) and can be deleted.

---

## The 15 fixes, ranked by impact on a first-time viewer

| # | Shot / time | What is wrong | Evidence | Smallest fix | Kind |
|---|---|---|---|---|---|
| 1 | **L2 to L3**, 3:53.2-3:55.8 (f5597-5660) | The ending's first switch never happens. L2 is a frozen still: the frame difference is 0.00 on all 63 frames, and the thumb never moves. It cuts lit straight to the lit 1988 window, with no click-off and no black, so the timeline change does not happen "inside black". The film's last idea, rooms existing only while lit, is lost. | `work/qa/cuts/cuts_11.jpg` (last row); `shot_stats.txt` (L2 static 100 %); `sync/probe.txt` (L2 mad) | Animate the thumb press over f5650-5659. At f5660 switch to the existing `L2_off` frame, held black for about 8-12 frames. Let L3's window come in from black (reuse A1's stutter-on logic, not a lit first frame). | comp |
| 2 | **E3**, 1:33.0-1:39.9 (166 f) | A huge blurred beige rod (the keyframe's "Mama blur": shoulder plus stick) fills the left third for 7 s, beside the film's longest close-up. It reads as an unexplained object. | `sheets/sheet_15.jpg`, `sheet_16.jpg` | Grade or blur the left 35 % into the night wash, so only a dark soft shoulder silhouette remains. Or crop 15 % in from the right and re-centre. | comp (regen of the keyframe if the grade can't hide it) |
| 3 | **B3**, 0:26.1-0:29.3 | A slate-indigo cloth border frames the page for the whole shot, still showing at the left edge on the last frame (f702). The push from B2's warm lit spread lands on a flat page in a blue frame, so the signature "into the page" move breaks at its first use. | `cuts/cuts_00.jpg` (B2→B3), `cuts_01.jpg` (B3→B4) | Replace the indigo surround with B2's lit spread and lap, or start B3 at a zoom where the page edge is already out of frame. End with the edge out of frame, as the shot list asks. | comp |
| 4 | Lyrics, film-wide | **The lyric layer is inconsistent.** Lyrics show in room and stage shots but are missing from almost every book shot (B3-B5, C1, C2 "Monkey!", C4, C6, E2, E4, G2-G5, H5). They appear in at least 6 positions and sizes (top-left, top-right, lower-right, bottom-centre, chin, vertical in a pane). In the rap, consecutive shots flip between horizontal and vertical Chinese (F1 horizontal at the top, F2 vertical in the pane, F3 horizontal top-left, F4a horizontal at the bottom, F4b/F5/F6 vertical on the right). All punctuation and inner spaces are stripped: "孙悟空came" (B1), "Not yet that's just the start" (C3), "石头里蹦出来没有童年" (F1), "Tool or threat trick or kid" (H3). In H3 the line sits on top of a face (f3980). | `text/lyrics_combo.png`; sheets 02-03, 17-20, 27 | Use one global lyric layer at assembly: a single size, one position rule (lower third inside the 4:5 area; vertical only for the carved or sealed lines), and keep the source punctuation and spaces. Decide once whether book shots carry lyrics. | comp |
| 5 | **All 7 splices** (C5, D2, F3, F4, F6, I3, K2) | Each second part lands 1-2 frames late. Measured splice frames are +2, +2, +1, +1, +2, +1, +1 against the logged frames. A duplicated frame is inserted in the first part (a visible stutter mid-push in F3a at f2692), and the second part's last 1-2 frames are dropped. D2d's 4th bow and its 仓 land at f1538 against 63.980 (f1536): +2. | `cuts/cut_table.tsv` splice rows; `shot_stats.txt`; the duplicate-frame list in this report | In `tools/cut/splice.py`, drop the `fps=24` after `setpts` (use `setpts=N/24/TB`) or concat by frame index. Then re-splice and reassemble. | comp (tooling) |
| 6 | **H1-H4** 脸谱 album, 2:29.7-2:49.2 (18 s) | The faces read as flat vector clip-art: perfectly smooth fills, egg-shaped heads with cartoon ears, symmetric, no brush. Each stamp is preceded by a soft grey Gaussian blob (f3593, 3636, 3690, 3780, 3792-3804). The loudest section of the film looks the most digital. | sheets 24-27; `cuts/cuts_07.jpg` (G6→H1 blob) | Multiply the paper fibre through the gouache, add dry-brush edge breakup and slight misprint jitter to the colour fields, and replace the blur blob with a hard-edged ink-wash shadow or cut it. | comp (regen the 17 faked faces only if comp can't rough them up) |
| 7 | **Centred faces**: F1, G1, K2a, I4a | The rule allows only G5 and I4 as centred faces. F1 (daughter dead centre, 1.8 s), G1 (little Jade near centre, 6 s, just before G5), K2a (daughter frontal and centred, 1.6 s) and I4a all break it. In I4a Mama is a hard-cut, full-frame, centred red face, not a ghost over Jade. G5 and I4 lose their weight. | sheets 17-18, 20-21, 31, 35 | Reframe F1, G1 and K2a off-centre (shift and crop by about 15 %). In I4, overlay `I4_mama` on Jade's face at 70→0 % over 8 frames instead of cutting to it. | comp |
| 8 | Sync: seals, flips, crack, words, page turns | These run 2-6 frames late. C1 crack +3; rubbing flips +2/+2/+3; echo seals +2 (195.65, 198.74); H3 "kid" cut +2; G2 second margin step **+6**; K4 page landings **+3 / +4**; D2 bow 4 +2. | sync table below | The seal and flip code fires its first visible frame 2 frames after the trigger, so move every trigger 2 frames earlier. Move the G2 step to 133.690. Retime K4 turns 2 and 3 to *land* on 220.92 and 221.805. | comp |
| 9 | **E1 / F1 / G1 hits** | Three section hits have no picture event. The verse-2 crash (86.998) has none: the cut D9→E1 is 28 frames earlier, at 85.833. The rap crash (107.975) has none in F1. In G1 the margins start closing at 124.75 (f2994), 2.8 s after the narrowing at 121.905. | sync table; `sync/probe2.txt` (G1 strip widths) | E1: put a light sweep or neon flare on 86.998, or move the cut to f2088 if D9's clip has 28 more frames. F1: give one streetlight sweep a peak on 107.975. G1: start the margin closing at 121.905. | comp |
| 10 | **K5**, 3:44.2-3:48.8 | The payoff does not read. The torch pool covers two entries, and the bare column looks like page margin, not a missing entry. K5 is 80 levels darker than K4 under "the same torch". Coverage is 27 % against a budget of 3. | sheets 37-38; `paper_tone.txt` | Reframe onto the ruled empty column with its rule lines lit, a filled column beside it for contrast, and the rest in dark. Match the torch exposure to K4. | comp |
| 11 | **I1** white-in, and torch blooms | The white-in is not glare. There is 1 frame of page white (f4253), then a uniform grey dissolve over 6 frames (luma 235→157→102→65→41). It reads as a software cross-fade. The torch heads in I1, K1 and L1 carry round bloom halos ("no glow blooms"). | `cuts/cuts_08.jpg` (H6→I1); `sync/probe.txt` (I1 luma) | Hold full white 3-4 frames, then contract it into the torch pool, a radial reveal from the bulb with no global fade. Clamp the bulb halos to a hard-edged pool. | comp |
| 12 | **G4**, 2:22.5-2:23.3 | The finger-and-thumb ring shadow floats above the head silhouette as a horizontal ellipse, exactly an angel's halo, 2 s before it settles. That pre-empts H5's halo, the one sanctioned halo. The head shadow's tuft reads as a horn or an elf ear. | `sheets/sheet_23.jpg` (f3426-3432) | Bring the ring in already touching the head, as a band seen edge-on rather than an ellipse above it. Round off the tuft. | comp |
| 13 | **D2** four bows | The four re-poses are near-identical crouches, so nobody reads "bowed four ways". The 才 seals render as "キ"-like glyphs at 540p and can read as katakana. | `text/glyph_combo.png`; sheet 10 | Use four clearly different compass bows (body turned E/S/W/N, a deeper bow), and set 才 larger or in a less katakana-like seal form. | comp (regen of bow poses if canon has none) |
| 14 | **J3** red pages, **J2** heaven | J3's "1988 light" is a flat cinnabar tint over the whole frame, including the paper whites, so it reads as a colour filter, not neon on paper. J2 is meant to be the fullest frame of the film (budget 75), but most of it is dark with a moon-like bloom halo around the one lit peak (59 % mean). | sheets 31-32; `coverage.txt` | J3: apply red as light *multiplied* on the paper, keeping highlight structure, with a lower strength. J2: lift the ambient light so the neighbouring blue-green peaks read, and hard-edge the pool. | comp |
| 15 | **F6b** reflection, 2:00.6-2:01.4 | The code-made reflection reads as a large pale ghost face in the side window, not the daughter waving. | `sheets/sheet_20.jpg` (f2898-2910) | Scale the reflection to her size, move it to the same pane height, add the waving hand, and cut its opacity to about 30 %. | comp |

Just below the line: the D8 ink-bleed (f1968) leaves a white figure with a black outline that reads like a line drawing. The L1 homography pull-back (f5514-5540) warps the room like a 2D picture-in-picture. The B4 moon pass turns the paper cement-grey, and the jump B4→B5 is 57 levels.

---

## 2. Cuts and continuity

**Flash frames and 1-frame glitches.** No unintended flash frame at any of the 64 cuts. The only isolated 1-frame spikes in the film are J1's designed flashes (f4556-4561) and one in H2 (f3892, a face landing).

H1's first frame (f3593) is a one-frame grey blur blob on bare paper after G6. It is the intended stamp shadow, but it reads as a smudge.

**Splices.** All 7 are 1-2 frames late (fix 5):

| Splice | Logged frame | Actual cut frame | Δ |
|---|---|---|---|
| C5a\|C5b | 1311 | 1313 | +2 |
| D2\|D2d | 1531 | 1533 | +2 |
| F3a\|F3b | 2694 | 2695 | +1 (plus a duplicated frame at 2692, mid-push) |
| F4a\|F4b | 2744 | 2745 | +1 |
| F6a\|F6b | 2895 | 2897 | +2 |
| I3a\|I3b | 4431 | 4432 | +1 |
| K2a\|K2b | 5091 | 5092 | +1 |

Internal cuts D3a\|D3b (1568) and I4 (4500, 4523) are on their logged frames.

**Paper tone between book and stage shots.** Measured as the median RGB of the brightest 20 % of pixels (`work/qa/paper_tone.txt`):

| Jump | Size | Cause |
|---|---|---|
| B4 last → B5 first | 57 | Moon-grey cliff to cream summit; visible |
| H4 → H5 | 25 | Album board to cliff |
| H5 → H6 | 21 | Cliff to paper |
| J3 → J4 | 15 | |
| K2b → K3 | 47 | Same torch, different exposure; visible |
| K3 → K4 | 34 | Same torch, different exposure; visible |
| K4 → K5 | 80 | Same torch, different exposure; visible |

All others are ≤ 9.

**Other look jumps:**
- **B2→B3**: warm lit spread to a flat page in an indigo frame (fix 3).
- **D1→D2**: the sd20 monkey changes into the canon figure (known).
- **C1 vs C4**: two different egg drawings. C1 is a large pale oval on ground; C4 is a small textured ball. C1's crack is gone in C4. The story allows it ("Not yet"), but it reads as two objects.

**Timeline changes (1988↔2026) and whether they happen inside white or black:**

| Cut | Frame | Inside white/black? | Note |
|---|---|---|---|
| E6→F1 | 2569 | no, hard cut dark→dusk | Shot list asks for a hard cut on the pickup; acceptable |
| F3a→F3b→F4a | 2695 / 2706 | no | Intended match cut on the blow; face positions match (0.61 vs 0.625 of width) |
| F6b→G1 | 2915 | no, hard cut | Brainstorm rule broken; shot list silent |
| H6→I1 | 4253 | **yes, but via a grey dissolve** | Fix 11 |
| I3b→I4a (Mama) →I4b→I4a (Jade) | 4488 | no | Should be a ghost over Jade, not a cut (fix 7) |
| J1 / J3 alternations | — | stage register, cut on hits | Fine |
| L2→L3 | 5660 | **no: lit to lit** | Fix 1 |

**Centred faces.** Intended: G5 (✓, in the strip) and I4 Jade (✓). Also centred:
- F1 daughter
- G1 little Jade
- K2a daughter
- I4a Mama, full frame

C1's stone and D7's monkey are also dead centre (objects, not faces; minor).

**Other continuity:**
- **Little Jade's hair** is a long ponytail in A3, B1, D9 and E3, short in B2/E1. Known keyframe drift.
- **Mama** reads late 30s in C3, I4a and E6, and wears an off-model dark sweater in F3b (headless torso holding the book).
- **The daughter's hair** goes ginger-orange under the car grade (F1-F6); canon is light chestnut.
- **Jade** wears glasses throughout (canon); the jacket holds.
- **The monkey** holds two plumes and the cinnabar peach patch in D1-D8 and J3, with the tiger kilt and banded staff. The plumes are very thin, curved lines and read a little like insect antennae at 540p. The G2 pilgrim monkey has no plumes or patch (acceptable for the pilgrim).

---

## 3. Sync, measured

The picture's frame is the first frame where the change is visible. "Late" means > 1 frame after the audio frame; "early" means > 2 frames before it.

| Event | Audio t | Audio f | Picture f | Δ | Verdict |
|---|---|---|---|---|---|
| Neon comes on | 0.165 | 4 | 4 | 0 | ok |
| Cut on the hole / band in | 15.515 | 373 | 372 | −1 | ok |
| Crack appears (C1) | 43.635 | 1048 | 1051 | **+3** | LATE |
| Rubbing flip 1 | 43.805 | 1052 | 1054 | **+2** | LATE |
| Rubbing flip 2 | 44.040 | 1057 | 1059 | **+2** | LATE (held 4 f) |
| Rubbing flip 3 | 44.385 | 1066 | 1069 | **+3** | LATE |
| "Monkey!" hand shadow | 45.275 | 1087 | 1087 | 0 | ok |
| Ink throw lands | 58.673 | 1409 | 1409 | 0 | ok (throw in flight on 1408) |
| Bow 1 + 才 | 61.321 | 1472 | 1472 | 0 | ok |
| Bow 2 + 才 | 62.205 | 1493 | 1494 | +1 | ok |
| Bow 3 + 才 | 63.090 | 1515 | 1516 | +1 | ok |
| Bow 4 + 仓 (D2d) | 63.980 | 1536 | 1538 | **+2** | LATE (splice) |
| 一 (cut to 通) | 67.910 | 1630 | 1630 | 0 | ok |
| 百 (cut wider) | 68.530 | 1645 | 1645 | 0 | ok |
| Verse-2 crash | 86.998 | 2088 | — | **none** | MISSING (cut is at 2060, −28) |
| Rap pickup cut | 107.040 | 2569 | 2569 | 0 | ok |
| Rap crash | 107.975 | 2592 | — | **none** | MISSING |
| Margins begin (G1) | 121.905 | 2926 | 2994 | **+68** | LATE |
| Margin step 1 (听话) | 130.175 | 3125 | 3127 | **+2** | LATE |
| Margin step 2 (听话) | 133.690 | 3209 | 3215 | **+6** | LATE |
| Margin step 3 (G4) | 141.450 | 3395 | 3395 | 0 | ok |
| "Yes", mouth opens | 148.720 | 3570 | 3569 | −1 | ok |
| Bare paper starts | 149.285 | 3583 | 3583 | 0 | ok (G6 3583-3592) |
| Bridge crash | 149.720 | 3594 | 3594 | 0 | ok (1 blur frame at 3593) |
| "Tool" | 162.630 | 3904 | 3903 | −1 | ok |
| "threat" | 163.480 | 3924 | 3924 | 0 | ok |
| "trick" | 164.360 | 3945 | 3946 | +1 | ok |
| "kid" | 165.240 | 3966 | 3968 | **+2** | LATE |
| Flashlight white-in | 177.193 | 4253 | 4253 | 0 | ok (but a grey dissolve) |
| Drop-2 crash 1-4 | 189.805/.867/.922/.972 | 4556/4557/4559/4560 | 4556/4557 (rubbing)/4559/4560-61 | 0 | ok |
| Drop-2 downbeat cut | 190.860 | 4581 | 4581 | 0 | ok |
| Seal on downbeat kick | 190.885 | 4582 | 4582 | 0 | ok |
| Echo (formed) 1 | 191.510 | 4597 | 4597 | 0 | ok |
| Echo (formed) 2 | 192.370 | 4617 | — | ? | Not detectable: too faint during the pull-back. Verify by eye |
| Echo (warmed) | 195.650 | 4696 | 4698 | **+2** | LATE |
| Echo (no song) | 198.740 | 4770 | 4772 | **+2** | LATE (亮相 tilt 4768) |
| J5 seal | 202.030 | 4849 | 4850 | +1 | ok |
| Echo (百通) re-press | 202.460 | 4860 | — | ? | Not detectable (decay 0.35) |
| Strike-out on "breath" | 216.520 | 5197 | drawn 5192-5198 | +1 at completion | ok |
| Page turn 1 lands ("page") | 218.220 | 5238 | 5238 | 0 | ok |
| Page turn 2 lands ("looked") | 220.920 | 5303 | 5306 | **+3** | LATE |
| Page lands on wooden hit | 221.805 | 5324 | 5328 | **+4** | LATE |
| Nothing moves | 225.254 | 5407 | frame difference 0.00 | — | ok (K5 fully static) |
| Flashlight off | 235.833 | 5660 | — | **none** | MISSING (lit cut) |
| Neon off | 237.840 | 5709 | 5710 | +1 | ok |

---

## 4. Lip-sync

There are 17 `sync: lip` shots in shots.yaml/json, not 18: G4 became shadow-only.

How to read the columns:
- **lag**: the tool's `lag_vs_synced` in ms; positive means the picture is late.
- **r ≥ 0.4 with sharp ≥ 0.35** counts as usable.
- **Box** means FaceMesh found no face and a mouth box was used, so r means little.

| Shot | Frames | Method | lag ms | r | sharp | By eye |
|---|---|---|---|---|---|---|
| B1 | 372-534 | FaceMesh | +102 | 0.30 | 0.29 | Plausible sung vowels with blinks. The mouth is closed on the first 妈 (f380) and opens at f383: about 3 f late. No chewing |
| B2 | 535-626 | box | +185 | 0.21 | 0.14 | Wide shot; Mama's mouth moves but is small |
| C3 | 1108-1190 | box | +18 | 0.29 | 0.27 | Mama sings with a smile; reads fine |
| D3b | 1568-1629 | box | −273 | 0.23 | 0.26 | Faces tiny; reads as general mouthing |
| E1 | 2060-2145 | box | +227 | 0.24 | 0.20 | Mouth small; nose tap lands on "you" (88.47) ✓ |
| E3 | 2232-2397 | FaceMesh | +102 | 0.37 | 0.45 | Good mouth shapes; about 2-3 f late. No shrug |
| F1 | 2569-2611 | box | +18 | 0.48 | 0.57 | OK; hands pressed in prayer rather than chopping |
| F3a | 2665-2694 | box | +310 | 0.19 | 0.27 | 30 frames, mostly an "o" for the blow; acceptable |
| F4a | 2706-2744 | FaceMesh | −232 | 0.26 | 0.16 | Mouths in the mirror barely move (articulation 0.03): holds |
| G1 | 2915-3058 | FaceMesh | +102 | 0.33 | 0.32 | Plausible; about 2-3 f late |
| G3 | 3225-3389 | box | +60 | 0.17 | 0.17 | Face cropped at the top of the strip, looking down; mouth barely readable |
| G5 | 3515-3582 | FaceMesh | −23 | 0.39 | 0.45 | "Yes" opens at f3569 (−1): good. Mouth stays parted to the cut |
| I1 | 4253-4324 | box | −23 | 0.57 | 0.59 | Face about 120 px; fine |
| I3a | 4391-4431 | FaceMesh | +18 | 0.60 | 0.73 | Good |
| I4 (Jade) | 4523-4554 | FaceMesh | +352? | 0.73 | 0.57 | Ambiguous: the second peak is −208 at r 0.69, the window is only 32 f and +352 is at the search limit. By eye the mouth opens on "You're" |
| K1 | 4889-5052 | box | −190 | 0.12 | 0.13 | Profile with a tiny mouth: does not follow the words. Wide shot |
| K2a | 5053-5091 | FaceMesh | +18 | 0.46 | 0.48 | Good |

The three FaceMesh-readable attic close-ups (B1, E3, G1) all measure +102 ms, a consistent 2-3 frame late placement. Moving those clips 2 frames earlier is a comp-only retime.

---

## 5. Whitespace

Coverage uses the paper ground for book, stage and blank shots and the night ground for rooms, sampled every 0.5 s. Full table: `work/qa/coverage.txt`.

**Where the number is not meaningful (judge by eye):**
- **Full-bleed rock**: B4, C6, D4, D5, H5.
- **Torch pools**: I2, I3b, J1, J2, J5, K2b, K3, K4, K5. The pool reads as marks.
- **H4**: the dark board reads as marks.
- **Car shots**: the painted interiors dominate.

**Real over-budget cases:**

| Shot | Budget | Mean | Note |
|---|---|---|---|
| A2 | 15 | 38 | |
| A4 | 20 | 50 | |
| B2 | 20 | 52 | |
| B3 | 15 | 43 | The indigo border |
| B5 | 15 | 26 | |
| C2 | 20 | 43 | |
| E1, E3, E5, E6 | 20 | 38-56 | |
| G1 | 20 | 51 | |
| K5 | 3 | 27 | By eye too: the lit pool holds two columns of text |

All room shots are 15-40 points over their budgets; this is known from the keyframe logs.

**Real under-budget cases (the loud sections are not full):**

| Shot | Budget | Mean | Note |
|---|---|---|---|
| D1 | 60 | 25 | By eye about 45 % at the splash peak |
| D2 | 45 | 27 | |
| D6 | 35 | 11 | |
| D7 | 40 | 11 | |
| D8 | 30 | 4 | |
| H1 | 50 | 24 | |
| H2 | 65 | 31 | |

The stage register is cleaner than the plan. That reads well; only D1 needs to feel fuller.

**Squint test (32 px).** These do NOT read as one mass in one corner or one pool:
- A2 (diagonal red wedge plus quilt)
- A4
- B2
- B4 (an even field of red glyphs)
- C3
- C6
- D4
- E2 (diagonal band across the frame)
- E3 (stick plus face: two masses)
- E5
- F2-F6 (whole car interiors)
- H2 and H4 (an even grid, by design)
- J3 (whole frame red)
- J4 (a row)
- K4 (whole spread)

These pass:
- A1/L3 (96 % in one quadrant)
- B5
- C1, C4
- D6, D7, D8
- E4
- G3-G6
- H6
- I1, I2, I3b
- J5
- K3, K5
- L2

Sheet: `work/qa/squint/squint_all.png`.

---

## 6. Text

| Where | What is on screen | Correct? |
|---|---|---|
| Cliff B4, C6, D5, H5 | 崇羲篆體 cut from `qianziwen.txt` (scripts read the proofed file; verified in `shots/_mountain.py`, `B4.py`, `D4.py`) | Source correct. Seal forms are not verifiable by eye at 540p. In B4 every character is equally cinnabar-bright, so the raking sun does not visibly light characters in passing |
| D4 | 通 (line 117 右通廣內), then a 5x5 block around it | Source correct. The large 通 has a glossy bevel and extruded look that reads as digital embossing |
| D5, J5 | 一通百通 inscription in LXGW WenKai plus a 悟空 seal | ✓ |
| E2 | 這猴王也是他一竅通時百竅通 / 當時習了口訣自修自煉 / 將七十二般變化都學成了 | ✓ against `categories.txt` and ch.2. It is a prose excerpt in traditional script while the lyrics are simplified. Acceptable as a book prop |
| K3/K4 ledger | Entry 魂字一千三百五十號 孫悟空 / 天產石猴 該壽三百四十二歲 善終 | ✓. Neighbouring filler entries reuse ch.3's 似人相 不入人名 / 似蠃蟲 不居國界 / 似飛禽 不受鳳凰轄 as if they belonged to other monkeys. 蠃 is the ch.58 variant, so not an error. Readers of Chinese will see Wukong's own description assigned to monkeys 1348/1349/1351 |
| Seals | 倉 (D1, D2, D6-D8, J3, J4), 才 (D2), plain blank 白文 squares (H3), 悟空 (D5, J2, J5) | Syllables are within 仓/倉 才 台. 才 renders as "キ" at 540p (fix 13). 悟空 is an inscription seal, not a percussion syllable: fine |
| Neon sign | Mirror-reversed CHIN. IND. SPEC. REST. + 酒家 | Invented; no real name ✓ |
| Lyrics | See fix 4 | Inconsistent placement and orientation; punctuation stripped; "孙悟空came" has no space; F1's two clauses run together; H3 text overlaps a face. The EB Garamond lines are about 11-13 px cap height at 540p: legible, at the limit |
| Model-invented text | I3a wall: faint cursive wash marks at the left (room team noted). Car: blank dashboard display shapes (F4a, F6a). No legible gibberish found on book covers, windows or dashboards | Paint out the I3a marks if they read on a full-size watch |

---

## 7. No-AI test and guardrails

- **No AI imagery.** No frame needs AI to make sense. There are no screens with faces, no circuitry and no glowing blue minds. The dashboard displays are blank and dark under the grade.
- **Riskiest reading: H3's clown face (F14).** Its white patch is a wide rectangle across the eyes (f3948-3990), and at 540p it reads as a censor or redaction bar over a face in a "categories" grid. That is the one image that invites a surveillance or redaction reading. Narrow it to the traditional small 豆腐块 on the nose.
- **K3 strike-out.** Its 8 drawing frames have a straight-cut front and briefly read as a black redaction bar (f5196). Same family; give the stroke a bristle-tapered head.
- **Monkey design.** It does not echo Havoc in Heaven, the 1986 series, Black Myth or Dragon Ball. It is a black splashed-ink body, a peach cinnabar patch, two long plumes and a tiger kilt. The heart-shaped red face is closest to opera make-up, as intended.
- **No real brand, logo or restaurant name seen.** The jacket's RARE EARTH and 1420 MHz are left blank, as canon says.

---

## 8. Overall watch

**Pacing against the song.**
- The quiet register is the film's strength: A1, B5, C4, E4, G6 and H6 all hold their nerve.
- The loud sections do hit harder: D1, D7, H1, J1 and J3. But the hook's back half (D6-D8) is visually the emptiest stretch of the film while the suona plays at full band. The coverage of 4-11 % is beautiful but low-energy.
- The bridge (H1-H2, 13 s instrumental) is the busiest-looking and least hand-made section (fix 6).
- **Holds that drag:** G2, 6.9 s of a nearly static figure (frame difference 0.14) with no lyric; E2, 3.6 s static; K4, 7 s of near-identical spreads.
- **Too fast to read:** J1's four flashes are fine as impact. The C1 flips read. D2's bows don't read (fix 13).
- **The ending does not land as written.** Without the click-off (fix 1) the last 4 s are a lit flashlight still, then the window. The neon-off itself is clean (+1 frame) and the final black is right.

**Five strongest shots:**
1. **A1 / L3**: the window. One lit opening, exact sync on the clapper roll and the hum-off.
2. **C2**: the hand shadow lands on "Monkey!" to the frame; the red page with the giant shadow is the thumbnail.
3. **D7**: the staff flower. Dry-brush rings stay on the paper; the best stage shot.
4. **F2**: the shadow-puppet monkey in the amber pane, head-swapped on the beats. Truly a traditional twin.
5. **E4**: the Master's sleeve and a tiny monkey, about 1 % ink.

**Five weakest shots:**
1. **L2**: frozen, no click (fix 1).
2. **E3**: the stick (fix 2).
3. **B3**: the indigo frame (fix 3).
4. **H1/H2**: vector faces (fix 6).
5. **K5**: the blank column does not read (fix 10).

---

## Per-shot notes

| Shot | Notes |
|---|---|
| A1 | Strong. Neon on at f4 exactly; the breath to blue reads. |
| A2 | Drift is a flat 2D pan; the floorboard light lines are barely visible; the "storybook on a pillow" doesn't read at 540p; the child is asleep (fine, she sits up in A3). Over budget. |
| A3 | Good door light. Little Jade's hair is long. |
| A4 | Good hands; bright close-up. Duplicate frame at f338 (on twos). |
| B1 | Good face. Lip about 3 f late; last 0.5 s holds. Lyric top-left, "孙悟空came". |
| B2 | Brightest attic frame (luma up to 117); push into the spread works but lands on B3's mismatched page. |
| B3 | Indigo border (fix 3). The mist band is a straight white streak. The right-page "text column" is faint rules only. |
| B4 | Cliff travel reads; the sun and moon passes are weak (every glyph is equally red); the moon pass goes cement-grey. 21 mean frame difference per frame: constant-speed scroll, check for judder at full size. |
| B5 | Good: holds on the drum dropout, only the mist moves. The mist band edge is straight. |
| C1 | Crack +3 f; flips +2/+2/+3 (sync table). Stone dead centre. |
| C2 | Best sync point in the film. |
| C3 | Good; Mama reads mid-30s. Lyric loses its comma. |
| C4 | Clean (3.9 % ink). The egg is a different drawing from C1's. |
| C5 | C5a: Mama holds a finger at her lips ("shh") more than blowing; the egg is invisible on the open book. C5b: the egg fades rather than being wiped by a sleeve. Splice +2. |
| C6 | Gold run up the columns reads; the cliff is very dense (texture); the egg cracks read. |
| D1 | Good impact on 58.673; the monkey appears with the patch and plumes; the rubbing flip on the echo is subtle. Grey blob at f1408. |
| D2 | Bows unreadable; 才 looks like キ; bow 4 +2 (splice). |
| D3 | D3a gold beams good; D3b wide, faces tiny, lip unmeasurable. |
| D4 | 通 bevel reads digital; the 百 cut is exact. |
| D5 | Pull-back and inscription good; the gold columns read as dotted LED-like dashes at 540p. |
| D6 | Monkey tiny (by design); landing freeze OK; grey blob before the seal (f1800). |
| D7 | Strong. |
| D8 | Perch and seal good; the bleed-back leaves an outline ghost (f1968). |
| D9 | Good pose copy; Mama laughing. |
| E1 | Nose tap on "you" ✓; nothing marks the 86.998 crash. |
| E2 | Static 3.6 s; the troop is realistic macaques rather than dabs; the hops are invisible at 540p. |
| E3 | Stick (fix 2); no shrug; lip +102 ms. |
| E4 | Strong whitespace; the lean is subtle; no lyric. |
| E5 | Good whisper image; hand at her own mouth. |
| E6 | Good; eyes go wide at the end. Little Jade's hair differs from E5's. |
| F1 | Centred face; hands in prayer, not chopping; ginger hair; no event on the 107.975 crash. |
| F2 | Strong. The painted static amber streak on the glass stays still under the moving lamps. |
| F3 | Duplicate frame at f2692 mid-push; match cut OK; F3b Mama headless in a dark sweater. |
| F4 | Mirror mouths barely move; F4b busy; the amber shaft is a straight diagonal band. |
| F5 | Copies go dark per beat ✓; the amber reads as a dome light. |
| F6 | F6a good mirrored puppets; F6b ghost reflection (fix 15). |
| G1 | Near-centred face 6 s; margins start 2.8 s late; very bright, flat face. |
| G2 | Static 6.9 s; margin step 2 +6 f; margins are paper-on-paper, read only by edge lines; no lyric. |
| G3 | Strip OK; face cropped at the eyes by the top margin; lip not readable; no lyric visible. |
| G4 | Halo-like ring (fix 12); step at 141.45 ✓. |
| G5 | Good "Yes" (−1 f). The strip cuts the outer eye corners. |
| G6 | ✓ 10 frames bare paper on the silence. |
| H1 | Faces land on beats ✓; vector look and blur blobs (fix 6). |
| H2 | Grid fills; two cells stay empty until about f3900 (the last face lands at the cut). |
| H3 | Cuts on Tool/threat ✓, trick +1, kid +2; the clown patch reads as a censor bar; the lyric overlaps a face. |
| H4 | Pull-out to the album leaf works; inscription OK. |
| H5 | The child shadow is a soft grey blob and the glyphs under it stay red: no "child-shaped blank in lit writing". The gold ring reads. No lyric. |
| H6 | Strong. |
| I1 | Grey dissolve (fix 11); torch bloom; the crayon monkey is invisible at 540p. |
| I2 | Hands and shadows read; the hands glow white in the pool. |
| I3 | I3a lip good (r 0.60); I3b banquet reads as a lit stage set, with a soft elliptical vignette. |
| I4 | Mama is a hard cut, not a ghost (fix 7); I4b shadow climb on the hits OK; Jade's face smooth, near photoreal. |
| J1 | Four flashes on the crashes ✓. |
| J2 | Dim; bloom halo; echo 2 not visible. |
| J3 | Red tint reads as a filter (fix 14); seal +2. |
| J4 | Four faces read (graphite-like); seal +2; the daughter is very faint. |
| J5 | Pull-back and inscription good; rubbing flip at f4817 ✓ (chop 200.675 → f4817). |
| K1 | Good warmth; lip unmeasurable (profile). |
| K2 | K2a centred face; K2b king and scribe good; ledger crisp. |
| K3 | Entry legible and correct; the strike reads as a redaction bar for its first frames. |
| K4 | No hands; turns 2/3 land +3/+4; 7 s of similar spreads. |
| K5 | Fix 10. |
| L1 | The pull-back warps the room like a flat image; torch bloom. |
| L2 | Fix 1. |
| L3 | Clean hum-off (+1). |

### Duplicate frames found inside moving shots (not on purpose)

| Shot | Frame | Context |
|---|---|---|
| F3 | 2692 | Splice |
| F4 | 2758 | |
| J4 | 4778 | |
| K2b | 5105 | Push |
| L1 | 5517 | Pull-back |
| H1 | 3695, 3701, 3723 | During camera moves |

D7, D8 and I2 are on twos by design.

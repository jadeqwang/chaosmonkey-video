# Keyframes: attic88 (1988 attic)

Painter: keyframe agent, 2026-11-17. Model nbp (google/nano-banana-pro) 2K 16:9 throughout; returns of 1376x768 are
Lanczos-upscaled to 2752x1536 (noted in each alt `.txt`). Prompts beside every image (`alt/*.txt`; pick prompt as `<SHOT>.txt`).
Costs: `media/kf/_costs_attic88.tsv` ($0.134 per nbp call, list estimate).
Coverage = `tools/review/coverage.py` on the inverted frame (night as ground, so "ink" = lit area). For calibration the
layout `_lit.png` renders score 6-18 % and the L5 look anchor 42 %: nbp's paintings run 25-35 points brighter than the
budgets even after "deep night" edits. Recorded per shot; not chased further (it would need a grade, which is a comp decision).

## Room lock (set in A1-A3, kept in every prompt: `scratchpad p/room.txt` text is pasted into each prompt)
- Window: small square wooden window, four dusty panes (2x2), plain sill, low on the right gable wall; red glow, no letters.
- Floor: wide old dark-brown pine boards, thin amber light lines between them.
- Mats: pale ochre woven straw mats with dark wood edging (nbp paints them as thin tatami; kept).
- Blankets: little Jade = faded indigo cotton quilt with tiny white flowers; Mama = plain white pillow + folded olive-grey blanket.
- Book: plain red cloth cover, no title. Open pages painted blank.
- Props: grey portable TV with rabbit ears on a wooden crate (left), stack of schoolbooks (right), a bare bulb from the ridge.

## Checkpoint 1 (A1-A4)

| shot | pick | attempts | cost | coverage (budget) | defects left |
|---|---|---|---|---|---|
| A1 | `alt/A1_v3dark` (edit of v2) | 2 gens + 1 darkening edit | $0.40 | 12.7 % (10) | Rafters still readable more than "barely there"; v1 had sign shapes in the glass (rejected). |
| A1_off | edit of A1 + code dim of the panes (42 %, desaturated, soft mask) and x0.75 overall | 1 | $0.13 | n/a | Quilt loses its colour vs A1 (it is night-grey); geometry matches A1 by eye. |
| L3 | = A1 (copy) | 0 | $0 | 12.7 % (5) | Same frame as A1 by design. |
| A2 | `alt/A2_v3dark` (edit of v1) | 2 gens + 1 edit | $0.40 | 45.6 % (15) | Too bright vs budget; mats are thick tatami platforms (guide's slab thickness). Book moved onto the pillow by edit. |
| A3 | `alt/A3_v3dark` (edit of v1) | 2 gens + 1 edit | $0.40 | 39.6 % (15) | Little Jade's hair hangs to mid-back (edit did not shorten it); the window shows at the right edge; v2 had a roof skylight (rejected). Mama in the door reads ~35. |
| A4 | `alt/A4_v2fix` (edit of v1) | 1 gen + 1 edit | $0.27 | 58.1 % (20) | Camera is higher/closer than the guide; a sliver of red window remains top right (that wall should be the left gable); forearms pink rather than red. |

End frames so far: `A3_end` (edit of A3: Mama out of the doorway, about one step rather than two; room unchanged),
`A4_end` (2nd try: v1 barely moved; v2 lifts the book clear of the pillow, tilted upright).

## Checkpoint 2 (B1, B2, C2, C3)

Lesson: close-ups come back lit like daytime unless the prompt carries an explicit night-lighting paragraph
(`night.txt`: "the attic is unlit, only red neon from the right ... no daylight"). Added to every prompt from B2 on.

| shot | pick | attempts | cost | coverage (budget) | defects left |
|---|---|---|---|---|---|
| B1 (lip, LJ) | `alt/B1_v3fix` (night edit of v1) | 2 gens + 1 edit | $0.40 | 55.9 % (20) | Little Jade's hair hangs past her shoulders in a long ponytail (edit asked shoulder length, ignored); Mama at left is soft but not truly out of focus, sleeves down. Mouth closed, eyes left to Mama: OK for lip-sync. |
| B2 (lip, Mama) | `alt/B2_v2` | 2 gens | $0.27 | 60.6 % (20) | Brightest frame of the set (walls lit pink-brown); Mama's eyes read toward camera/right rather than clearly on little Jade; long sleeves. Mats/quilt/blanket/pillow on model. |
| B2_end | edit of B2 | 1 | $0.13 | | Book open wider, Mama's eyes lowered to it. Good. |
| C2 | `alt/C2_v3fix` (2 edits of v1) | 1 gen + 2 edits | $0.40 | 53.2 % (20) | v1/v2 painted a little monkey face on the child's hands (the word "monkey" does it); v3 = bare hands (flat-hand snout + two raised fingers as ears), which reads less like a monkey head; the silhouette must come from the comp shadow layer anyway. Book is a held spread, the gutter matches the guide only roughly. |
| C3 (lip, Mama) | `alt/C3_v3fix` (2 edits of v1) | 1 gen + 2 edits | $0.40 | 49.0 % (20) | v1 Mama read 40+ and was mid-song with open mouth; v2 fixed age and mouth; v3 restored the chest band. Mama still reads ~35. The one-finger gesture holds. |

## Checkpoint 3 (C5a, C5b, D3a, D3b)

| shot | pick | attempts | cost | coverage (budget) | defects left |
|---|---|---|---|---|---|
| C5a (= C5.jpg) | `alt/C5a_v1` | 1 | $0.13 | 62.4 % (15) | Not a true contre-jour silhouette: the face is lit from the front. Her raised hand is near (not over) her mouth; breath mist and dust motes present; window matches A1. |
| C5a_end | edit of C5a | 1 | $0.13 | | Change is subtle: lips less pursed, mist thinner; may read as almost identical to the start. |
| C5b | `alt/C5b_v1` | 1 | $0.13 | 90.7 % (15; page = ground here) | The book is held up toward camera rather than lying on the lap; spread is clean and blank, hands on the outer edges. |
| D3a (= D3.jpg) | `alt/D3a_v3clean` (edit of v1 + code patch) | 1 gen + 1 edit + code | $0.27 | 41.6 % (30) | v1 had two people asleep on the mats (removed by edit). Both nbp passes drew the gold beams across the page; I patched the page in code (beam columns below the page's top edge replaced with paper from 300 px to the right, feathered), so the beams now rise from the page edge. Beams are hair-thin and gold, page clean. |
| D3b (lip, both) | `alt/D3b_v3fix` (2 edits of v1) | 1 gen + 2 edits | $0.40 | 53.7 % (30) | v1 had loose papers instead of the book and little Jade's mouth was a round "o"; fixed. Faces are small (wide shot), so lip-sync there is low resolution. Mama looks at the camera more than at her daughter. |

End frames: `B2_end` ok; `C3_end` (hands lowered into her lap, Mama's fingertip on them; the jacket's chest band drifts to a sash);
`C5a_end` (subtle).

## Checkpoint 4 (D9, E1, E3, E5)

| shot | pick | attempts | cost | coverage (budget) | defects left |
|---|---|---|---|---|---|
| D9 | `alt/D9_v1` | 1 | $0.13 | 47.1 % (20) | Window is on the back wall rather than at the right edge as in the guide; pose (one leg up, hand shading eyes) and laughing Mama both hold. |
| E1 (lip, Mama) | `alt/E1_v1` | 1 | $0.13 | 57.2 % (20) | Bright; Mama's eyes on the child, mouth closed smile; finger just short of the nose. |
| E1_end | edit of E1 | 1 | $0.13 | | Fingertip on the nose; nothing else moved. Good. |
| E3 (lip, LJ) | `alt/E3_v1` | 1 | $0.13 | 65.8 % (20) | No shrug / palms; the "Mama blur" at left reads as a blurred shoulder plus an odd wooden stick shape. Face, mouth and gaze (left, to Mama) are fine for lip-sync. |
| E5 | `alt/E5_v1` | 1 | $0.13 | 58.3 % (20) | Mama's cupped hand is at her own mouth beside the child's face rather than at the ear; both faces on model; no text. |

## Checkpoint 5 (E6, F3b, G1, G3)

| shot | pick | attempts | cost | coverage (budget) | defects left |
|---|---|---|---|---|---|
| E6 | `alt/E6_v2notext` (edit of v1) | 1 gen + 1 edit | $0.27 | 59.7 % (20) | **v1 wrote "JOURNAL OF HIDDEN STORIES" on the book cover** (missed at preview size; the first E6_end inherited it); edit blanked the cover. Mama reads ~35-40 here; the book on her lap is closed. |
| E6_end | `alt/E6_end_v2` (from the clean E6) | 2 | $0.27 | | Eyes wide, nothing else moved. Good. |
| F3b | `alt/F3b_v2` | 2 gens | $0.27 | 54.0 % (20) | v1 was a wide shot (child small, centre-right). v2 is close and blowing with hairs flying left; but "Mama" at left wears a dark sweater (off-model) with her lower face visible, not a soft blur. |
| G1 (lip, LJ) | `alt/G1_v1` | 1 | $0.13 | 53.1 % (20) | Two fingertips on the forehead, eyes up, mouth closed; colour muted but still warm skin. |
| G1_end | `alt/G1_end_v3` | 3 edits | $0.40 | | v1 swapped the room for a plain grey wall; v2 barely moved the hand; v3 = hand at chest height rising, room kept. The pair is "touching" (start) vs "rising" (end): the animator may want them in the other order. |
| G3 (lip, LJ) | `alt/G3_v2` | 2 gens | $0.27 | 59.1 % (15) | v1 had no centre column. v2 has the kneeling child above, hand flat on the left page, but Mama is in a dark grey top (off-model) with half her face in; little Jade looks down at the page (eyes not on Mama) and her head is ~20 % of frame height (under the 25 % lip-sync rule). |
| G3_end | `alt/G3_end_v2` | 2 edits | $0.27 | | Hand hovers above the page. |

## Checkpoint 6 (G4, G5) and close

| shot | pick | attempts | cost | coverage (budget) | defects left |
|---|---|---|---|---|---|
| G4 | `alt/G4_v1` | 1 | $0.13 | 55.3 % (12) | Little Jade peeks over the book (head and shoulders) rather than lying on her tummy; the ring hand is in front of the right page, not between window and head (the shadow is comp anyway). Not centre-column; the strip will crop it hard. |
| G5 (lip, LJ) | `alt/G5_v2fix` (edit of v1) | 1 gen + 1 edit | $0.27 | 48.4 % (12) | v1 looked off-lens right; edit moved the gaze left and greyed it. Background shows the attic + window, not plain. |

## Summary
- Spend: 58 nbp calls, $7.77 (list estimate), of the $18 limit. Ledger `media/kf/_costs_attic88.tsv`; project total after this set $123.20 of $600 (all agents).
- 33 frames: 23 setups + `A1_off` + 9 end frames (+ `C5.jpg` = C5a, `D3.jpg` = D3a, `L3.jpg` = A1).
- Contact sheet: `media/kf/_sheets/attic88.jpg`.
- Set-wide defects: (1) every frame is 25-45 points brighter than its ink budget by the night-ground measure (nbp will not paint
  night this dark on a close-up; a grade in comp is the fix); (2) little Jade's hair runs long (a long half-ponytail past the
  shoulders) in A3, B1 and most close-ups; (3) Mama reads 35-40 in C3, E6, G3 and wears off-model dark clothes in F3b/G3;
  (4) the window wanders: right wall at the right edge (A1, A3, C3, G1) vs back wall (B2, D9, E6) depending on camera, which
  is mostly true to the guides but not in D9/E1.
- Lip-sync frames: mouths closed or barely parted in all; weakest are D3b (faces small, wide), G3 (looking down, head ~20 %).

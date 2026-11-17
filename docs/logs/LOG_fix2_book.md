# LOG: FIX ROUND 2, BOOK + STAGE shots

QA: `docs/QA_PREVIEW_V1.md`. Rule applied: a hit's first visible frame = floor(t*24), at full strength (overshoot may
follow, never precede). Offsets below = picture frame - floor(t*24), measured on the rendered mp4 with
`work/fix2_book/measure.py` (frame difference + red-pixel delta per frame). The "before" numbers come from the pre-fix mp4s in
`work/fix2_book/backup/comp/`. Note that QA counted with ceil, so its "+2" is +1 under floor plus whatever was late beyond that.
Render: `work/fix2_book/do.sh ID [F0 F1]` (--fresh, 960x540, sheet, frame count). Backups of every touched script are in
`work/fix2_book/backup/`. Spend $0.

## Root cause and shared fixes (item 1)
- Every trigger compared `t >= t_event`. A frame is rendered at N/24, so the frame containing the event (N = floor) never fired.
  The fix is to snap to the frame start: `tools/ink/core.py` gets `hit_frame(t)` and `on_frame(t)`.
- `tools/ink/seal.py strike()` now counts in frames: k = hit_frame(t) - hit_frame(t_hit). The default is `lead=0`, so the
  2-frame grey "stone shadow" before each seal is gone (QA's blobs at D1 f1408, D6 f1800, J2). `shake_offset` is snapped.
  `seal()` gains `stretch=` (default unchanged).
- Snapped as well: `rubbing.flip_on`, `woodblock.beat_key` and the `misregister` hold, `Camera` shakes, and `tools/stage/stage.py hold_index`.
- `shots/_margins.py`: the step knots sit on on_frame(听话), and a step shows 75 % of its travel on that frame.
- **Affects room shots on their next render:** D2d's 仓 and bow land 1 frame earlier, and D2d's seal is in the new face. The G3/G4 margin steps land 1 frame earlier (141.45 -> f3394).

## Per shot
| shot | change | sync before -> after |
|---|---|---|
| C1 | Crack visible from the frame containing 43.635 (34 % of its run on the first frame, eased out); flips snapped | crack +4 (first faint frame f1051) -> 0 (f1047); flips +1/+1/+1 -> 0/0/0 |
| G2 | Margin steps and band snap on on_frame; 75 % on the first frame | 130.175 +1 -> 0; 133.690 +1 -> 0 (QA's +6 was on the pre-polish cut) |
| D1 | The gong (58.673) falls inside D1's first frame f1408, so that frame is the impact (splat + throw streak + 倉 at full); the in-flight frame and grey blob are gone | +1 -> 0; set 59.126 on twos; rubbing flip 59.595 +1 -> 0 |
| D2 | [13] Three distinct bows from canon singles. East: 04 profile right, pitched 13°. South: 03 frontal, 1.25x bigger, folded (0.8 squash), lower/toward us. West: 04 mirrored, pitched -15°, displaced 230 px left. Each lands on its frame thrown 18 % past its mark and settles in 3 frames. 才 in the new seal face | bows +1/+1/0 -> 0/0/0 (f1471/1492/1514) |
| D4 | 通 carving weathered (weather 0.22, chips 0.08, depth 0.7, streaks 0.25, grime 0.5): pitted chisel, less glossy bevel; 百 cut + pools snapped, pools 75 % lit on their frame | 百 +1 -> 0 |
| D5 | Roll flips snapped. **Bug:** timing lists 71.692 twice (perc + fast_roll), which cancelled the first flip. Now deduped | 71.692 none -> 0; 71.76/71.87/71.925 each 0; gong mis-reg on f1747 |
| D6 / D7 / D8 | Hit times on_frame; seals in the new face | D6 75.025 +1 -> 0; D7 78.808 +1 -> 0; D8 80.806 +1 -> 0 |
| D8 | Bleed-back rewritten: the whole figure's density sinks into the paper at once (blur grows, fibre break-up). No line-drawing rim (QA f1968) | - |
| J3 | [14] Red page = neon light from the window (upper right) with strong falloff to dark warm ink, paper tooth raked by it, hot pinkish core near the source, blue-greens faintly there. White page = a torch pool (r 1080, ambient 0.075) with falloff, not flat white. Cuts/seal/echo on_frame; echo paste 0.45 -> 0.62 | page cuts +1 -> 0 (x3); 倉 195.181 +1 -> 0; echo 195.65 +1 -> 0 |
| J4 | 亮相, echo and mouth swaps on_frame; echo paste 0.42 -> 0.62 | mouths +1 -> 0; tilt 198.613 +1 -> 0; echo 198.74 +1 -> 0 |
| E2 | Dabs 58 -> 84 px; hops 64 px high, each dab on every third beat, leaving the ground on the beat frame (on twos after) | - |
| E4 | Lean -1.4° / 22 px -> -3.0° / 40 px | - |
| B3 | End framing pushed in (END x 1060 -> 1220, width 2350 -> 2250): the page edge is out of frame from about f690; mist band bent (`wavy_band`) | - |
| B4 | Moon pass warm, not cool: the night tint is warm, ambient drop 0.13 -> 0.07, warmth kept 0.35. Last-frame paper tone 182/178/168 -> 198/189/169 (B5 starts at 237): the jump went from 57 to about 40 levels. Partly fixed | - |
| B5 | Mist band bent, lumpy edges (`wavy_band` in `_mountain.py`) | - |
| seals | [13] Every 锣鼓经 syllable seal (`stage.seals()`: D1 D2 D2d D6 D7 D8 J3 J4) is 白文 in 館閣楷, thickened, natural proportions. 倉 才 台 read as characters at 540p. In 崇羲 small seal, 才 read as キ and 台 not at all. 悟空 name seals stay in seal script | - |


## FACES (H1-H6), fix round 2 sub-fork

Files: `shots/faces_lib.py`, `shots/H1.py`, `H2.py`, `H3.py`, `H5.py` (H4 and H6 are untouched; H4 was re-rendered for the new faces).
faces_lib is used only by H1-H4. The F2/F4b/F5/F6a puppets use `puppet_lib`, not faces_lib, so they are unchanged.
All five re-rendered with `work/fix2_book/do.sh` (--fresh), exact counts: H1 158, H2 152, H3 80, H4 79, H5 84. Sheets refreshed.

| shot | what changed | sync (floor rule; picture frame minus floor(t*24)), before -> after |
|---|---|---|
| H1-H4 (faces_lib) | **No pre-stamp blob.** The 2-frame "stone shadow" ellipse is gone. Landing timing now uses frame indices (`hit_frame`): frame N-1 is bare leaf; frame N (the frame containing the beat) is the face at 108 %, then 97.5 % and 100.8 %, and at rest from N+3. The stamp now carries the ground and 72 % of the colour field on frame N, so the hit frame reads as a face, not a pale disc. The field completes over 2 frames and the black lines draw on over frames 2-6.5. The pressed-paper dent shadow after the landing is kept (it follows the hit and never comes before it). | see rows below |
| H1-H4 (faces_lib) | **Painted surface**, baked into each face's precompute. The cache key now depends on faces_lib.py, so code edits rebuild it. The surface has: two-scale mottle on pigment density, as a power on the colour; pigment pooled at the rim of every colour field (Sobel edge band); granulation from a real Paper height; paper fibre (high-pass of a Paper sheet) multiplied through the colour. Dark ink fields are protected from grain blow-up. Black lines get dry-brush break-up from bristle streaks stretched along x (thin lines and stroke edges break first) and a `tools.ink.wash` bleed halo (feathered, 0.55 strength). The line block is printed 1-3.5 px out of register with the colour (per face, deterministic). Line ink is warm black modulated by the fibre. Checked at a 100 % crop of a 1080p still (F04, F14): reads as gouache on paper with a mottled field and darker rims. | |
| H3 / H4 (faces_lib) | **F14 clown**: the wide pale rectangle across both eyes (the "censor bar") is painted back to skin, including its thin outline rule. A small 豆腐块 now sits between the eyes, down the bridge of the nose. Eye and nose lines are kept. | |
| H1 | Cuts at `on_frame(beat)` instead of `beat - 1/48`. With that rule a cut landed on floor or ceil depending on where in the frame the beat fell. | landings, before: +1, +1, 0, +1, 0, 0, +1, 0, +1, 0 (the frames before also had the blob); widening cuts 154.061-155.810: +1 x5; flips 151.675 / 155.147: +1 / +1; mis-reg 154.714 / 155.810: +1. **After: all 0.** The beat-1 face lands on H1's frame 0 (f3593, crash 149.720). |
| H2 | Cuts snapped the same way. Mis-registration (`mis_at`) and the dent snapped. | pairs 156.668 / 157.537: +1 / +1 -> 0 / 0; mis-reg 159.277 / 159.711 / 160.583: +1 each -> 0; flip 160.143: +1 -> 0; last face 161.886: +1 -> 0. Roll 158.255-158.420: 0 (small faces, change at +0 is small but present). |
| H3 | Noun cuts, child and category seals on `on_frame(word)`. | Tool 162.630: f3903 = H3's frame 0, seal on it (0). threat +1 -> 0, trick +1 -> 0, **kid +1 -> 0** (QA's +2 was in ceil terms on the old cut). |
| H5 | Child shadow edge blur 5 -> 2.5 px, so it reads as a crisper shape. Inside the lit shadow the frame is replaced by its own luma in a warm unlit-stone tone: the cinnabar in the cuts no longer reads red there, making a child-shaped blank in the lit writing. | no hits in H5 (light band only) |

Weak / skipped:
- At the full-leaf framings (H2 end, H4) the faces are about 60-90 px tall at 540p. The surface is subtle there; it reads at the close framings in H1, H3 and early H4.
- The faked 3-stage builds (17 faces) still show the old ~2-frame inpainting smear in the colour stage on F11/F13-like faces. It is now hidden more, because the lines draw on 3 frames earlier.
- H5's shadow is still a flat warm grey silhouette (a cast shadow). The gold ring still crosses carved characters.
- The lyric overlap in H3 is untouched (lyric pass).
- H6: nothing found wrong; not touched.
- Spend $0.

## HEAVEN sub-fork (J2 J5 K3 K4 K5; I3b K2b untouched)

Offsets = picture frame - floor(t*24), measured with `work/fix2_book/measure.py` (before = `backup/comp/*.mp4`).

| shot | what changed | sync before -> after |
|---|---|---|
| J2 | Relit as the fullest frame: from frame ~16 the page stays lit to the edges (warm ambient 0.62, the blue-green neighbours read), and a HARD-edged torch pool on 花果山 (local `pool_field`: flat plateau, 7 % uneven edge, no bloom) adds +0.42; radius in frame eased 760 -> 400 px (1080p) during the pull-back; centre raised to mid (1880, 700) so the peak sits inside. Polish-1's first 20 frames unchanged. Echo decay 0.55 -> 0.80; the two pale heads under the echoes dropped (a red smudge at speed). No pre-strike shadow (shared strike fix). | seal 190.885: +1 -> +0 (shadow frame removed); echo 191.51: +1 -> +0; echo 192.37: invisible (red +53 px) -> +0 (red +2522 px) |
| J5 | Rubbing flip snapped to the frame containing the chop (frames 4816-4819); echo decay 0.35 -> 0.70 | flip 200.675: +1 -> +0; seal 202.03: +1 -> +0; echo 202.46: invisible -> +0 (red +689 px) |
| K3 | Strike completes ON floor(216.52*24) = f5196 (T_END = on_frame); bristle-tapered head: each bristle column arrives at its own moment and the edges lag the centre, so the front is a ragged point, not a straight bar. Torch gain 1.38 -> 1.55 (paper tone 220 -> 244; K2b last 251, K4 first 244) | completion: 94 % on f5196 -> 100 % on f5196 (+1 -> +0) |
| K4 | Turn landings snapped (`leaf_state`: tl = on_frame(tl)) | 218.22: +1 -> +0 (f5237); 220.92: +1 -> +0 (f5302); 221.805: +1 -> +0 (f5323). QA's +3/+4 were on the cut's ceil convention + an older render |
| K5 | Reframed close: scale 2.10 (page px -> 1080p px), bare column (p8 x 220-415) at frame x 360-770 with the thick outer frame rule on its left and the column rule on its right, the 1391 note column (飛禽 不受) and number column (千三百) falling into dark to the right. Torch centre (640, 540) 1080p px, radius 660, stretch 1.30 vertical, ambient 0.07, gain 1.30. Paper tone 151 -> 249 (K4 last 245). Still static. | - |

**K5 framing for L1** (page space of `work/heaven/ledger/E_ledger_p8.png`, 2200x3300): the 1920x1080 frame shows
x 50.3-964.6, y 880.0-1394.3 (scale 2.10 frame px per page px; frame = (page - (50.33, 880)) * 2.1). Torch pool centre
frame (640, 540) = page (355.1, 1137.1), radius 660 frame px = 314 page px (stretched 1.30 vertically).

Skipped / weak: I3b's soft elliptical vignette is the shared torch field (same as K2b-K5); changing it in one shot would
break the torch's continuity, left as is. K4 still has no hands (regeneration-level). K5 coverage stays far over the 3 %
budget by design (two written columns frame the emptiness).

## Skipped (regeneration-level or beyond 15 min)
- B4: glyphs are equally red, so the sun does not light characters in passing (Cliff render change).
- C1/C4: two different egg drawings.
- C5b: the egg fades rather than being wiped by a sleeve.
- C6: dense cliff text.
- D5: gold far columns read as LED dashes.
- H5: the gold ring crosses carved characters.
- K4: no hands.
- I3b: vignette (shared torch field).
- E2: the troop plate is realistic macaques.
- J2: at the end of the pull-back the hard-edged pool reads as a flat pale disc, a little moon-like. It could use a softer far edge.

## K5 re-frame (lead's request, after the round)
The 2.10 close-up read as giant characters. K5 is now reframed at **scale 1.20** (p8 page px -> 1080p px).
- **Framing:** the frame shows `E_ledger_p8.png` / `spread_7_8.png` (p8 is the left page) x -405.7 to 1194.3, y 260 to 1160. Frame = (page - (-405.67, 260)) x 1.2. Negative x is beyond the book's edge, the dark bedspread.
- **Bare column:** page x 208-414 sits at frame x 735-985, a little left of centre. Its two rules run full height from the top frame rule (page y about 350).
- **Torch:** centre at frame (860, 600) = page (311, 760). Radius 560 frame px = 467 page px, stretched 1.30 vertically. Ambient 0.07, gain 1.42.
- **What reads:** about four written columns show to the right, falling into the dark. The outer frame rule, the page margin and the book's edge are on the left.
- **Exposure and stillness:** paper tone is 247/228/185, against K4's last frame at 245/227/187. The picture is static; only the lyric changes.

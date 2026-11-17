# Keyframes: bed26 (2026 bedroom)

Painter: keyframe agent (bed26 + car26), 2026-11-17. Model: google/nano-banana-pro, 16:9 2K, $0.134/call (list estimate).
Guides: `media/layout/bed26/<SHOT>_line.png` as image 1 ("ONLY for geometry"); refs `design/characters/refs/jade_upper.jpg`,
`jade_heads.jpg`, `daughter_A_turnaround.jpg` / `daughter_B_poses_mouths.jpg` (downscaled to 2048), `mama_heads.jpg` + `mama_B_expressions.jpg`.
Style ref (where a slot was free): wall crop of my own L1 v1. Costs: `media/kf/_costs_bed26_car26.tsv` (both sets).
Pages are painted bare: the crayon monkey in I1's margin and all page art are left to comp. No shadows painted (I2, I4b).

Night coverage: `tools/review/coverage.py` has no night-ground mode, so I measured the share of pixels > 28/255 from the median
of the darkest 40% (same threshold as coverage.py). Most frames are **20-50 points over the ink budget**: nbp lights the walls and
clothes with violet fill, and the darker prompt wording only partly helped. L1 and L2_off are on budget.

| shot | pick | attempts | cost | night cov / ink | defects left |
|---|---|---|---|---|---|
| I1 (lip, Jade) | `alt/I1_v4` (edit of v2) | 3 + 1 edit | $0.54 | 47 / 20 | The flashlight light lands on her jacket chest more than in a pool on the pages (the pages are lit, but not the brightest thing). Eyes only half slid toward the daughter. v3 rejected: lost likeness, NASA-style patches on the jacket |
| I1_end | `alt/I1_end_v1` (edit of I1) | 1 | $0.13 | 46 | Good: the daughter's finger on the near page margin. Returned at 1K, Lanczos x2 |
| I2 | `alt/I2_v4` (edit of v3) | 3 + 1 edit | $0.54 | 57 / 25 | Hands are pinch/"OK" shapes, not a clear monkey head (v2 painted monkey faces on the hands: rejected). Pages clean, no shadows |
| I4a (lip, Jade, centred) | `alt/I4a_v2` (also `I4.jpg`) | 2 | $0.27 | 73 / 20 | Eyes 0.45/mouth 0.74 of the frame height (guide 0.45/0.76). Underlight subtle. Close-ups are inherently over the ink budget |
| I4_mama | `alt/I4_mama_v3` (edit of I4a) | 3 | $0.40 | 50 | Eyes, nose and mouth line up with I4a to within a few px (checked by overlay at 700 px). She reads late 30s rather than 30 (v1/v2 read 40+); perm and round glasses OK; half-smile asymmetric |
| I4b | `alt/I4b_v1` | 1 | $0.13 | 60 / 20 | Clean. The daughter's hand points rather than making a puppet; fine for the shadow comp |
| J1 | `alt/J1_v2` | 2 | $0.27 | 72 / 40 | Bottom of frame: an orange flashlight with a white/orange cuff that reads ambiguously (sleeve or torch). v1 rejected: a giant hand and the daughter's head |
| K1 (lip, Jade) | `alt/K1_v3` (edit of v2) | 2 + 1 edit | $0.40 | 47 / 15 | Pool again partly on her jacket; the page-corner lift is weak. v1 rejected: unpainted paper over the top right |
| K1_end | `alt/K1_end_v2` (edit of K1) | 2 | $0.27 | 48 | Head turned to the daughter in profile, page turned. The figure and book drifted a little (Jade a few % left, book brighter) compared with K1: check as a last frame |
| L1 | `alt/L1_v2` (edit of v1) | 1 + 1 edit | $0.27 | 22 / 15 | Small figures; the second pool on the floor was removed in v2. Jacket trim mostly clean |
| L2 | `alt/L2_v1` | 2 | $0.27 | 49 / 12 | A long dark bar (the guide's arm/book-edge block) runs across the frame and reads as an object. Thumb on the switch, orange body, pool on the page. v2 rejected: a ghost face painted in the sleeve |
| L2_off | `alt/L2_off_v1d` | 1 edit | $0.13 | 0.1 | Model edit of L2 (light off), then multiplied by 0.28 to reach near black |

Bed26 total: 26 paid calls, about $3.49.

Checkpoints: after I1/I2/L1 (batch 1); after I4a/I4b/J1/K1/L2 (batch 2); after retries (batch 3); final.

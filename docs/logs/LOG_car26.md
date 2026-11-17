# Keyframes: car26 (2026 car, dusk)

Painter: keyframe agent (bed26 + car26), 2026-11-17. Model: google/nano-banana-pro 16:9 2K. Costs: `media/kf/_costs_bed26_car26.tsv`.
**Glass:** before generating, I rebuilt each `_line.png` with everything seen through a pane blanked to flat grey (a pixel is blanked
when the depth render puts it beyond the pane plane from the sidecar; the mirror is kept). Script: the scratchpad's `kf26/prep.py`.
Every pick has plain dusk-violet glass with nothing in it: no trees, road, lamps or reflections. F6b's reflection is left to comp.
Amber, one direction per shot, from the sidecar's `pane_backlight.light_travel_dir_px` of the shot's main pane (all on the
`right`/`median` lamp side):
F1 from frame left falling down-right (rear_right 0.73,0.69); F2 from the top of the pane straight down (0.05,1.0); F3a from
the upper left (0.45,0.9); F4a from above, down-right (windscreen 0.37,0.93); F4b from the upper left (0.47,0.88); F5 from above
(rear_window 0.27,0.96); F6a from the upper left (0.44,0.9); F6b from frame right travelling left-down (-0.78,0.62).

| shot | pick | attempts | cost | night cov / ink | defects left |
|---|---|---|---|---|---|
| F1 (lip, daughter) | `alt/F1_v4` = edit of a crop of v3 | 3 + 1 edit | $0.54 | 54 / 30 | No attempt matched the guide's close low camera, so v3 was cropped to make her face larger, then edited for the hands. The hands are upright and flat but held close together (reads half-chop, half-clap). The amber reads from the right/back, not frame left. 1K return, Lanczos |
| F2 | `alt/F2_v1` cropped (`F2_v1c`) | 2 | $0.27 | 70 / 40 | v1 had a painted paper margin: cropped 2% and resized. She faces the camera more than the pane. A second empty car seat sits behind her. The amber is a vertical streak on the glass (comp can replace it). v2 rejected: two ghost adult faces |
| F3a (lip, daughter) | `alt/F3a_v1` (also `F3.jpg`) | 1 | $0.13 | 51 / 30 | Face at about 0.53/0.38, not the 0.6/0.38 of F3b: shift in comp for the match cut. Mouth closed, palm under the chin, hand at the hair. 1K, Lanczos |
| F4a (lip, both) | `alt/F4a_v2` (also `F4.jpg`) | 2 | $0.27 | 69 / 50 | Both faces in the mirror with mouths visible (Jade's barely parted, the daughter's a small "o"). Mirror centred rather than centre-right. A blank dashboard display shape at bottom centre. Dots on Jade's collar. v1 rejected: stray hands under the mirror |
| F4b | `alt/F4b_v2` cropped (`F4b_v2c`) | 2 | $0.27 | 52 / 50 | Paper margin cropped (about 9% lost: the frame is tighter than the guide). Camera higher than the guide's low letterbox view. The daughter sits behind the passenger seat. v1 rejected: Jade standing |
| F5 | `alt/F5_v1` | 1 | $0.13 | 57 / 30 | The amber reads as a dome light in the roof. She sits in a plain seat (no car-seat shell visible). The rear window and side panes are large and clean. 1K, Lanczos |
| F6a | `alt/F6a_v1` (also `F6.jpg`) | 1 | $0.13 | 43 / 30 | Clean windscreen stage, Jade from behind. **A blank dashboard screen rectangle is visible**: paint it out in comp or re-roll |
| F6b | `alt/F6b_v2` | 2 | $0.27 | 42 / 30 | On model, deadpan wave, the side window large and plain. v1 rejected: off-model (older face) |

Car26 total: 16 paid calls, about $2.15. Both sets: 42 calls, **$5.64** (no failed calls).

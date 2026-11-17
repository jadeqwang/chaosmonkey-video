# LOG_faces: sequence team FACES (H1-H4 脸谱 bridge; F2, F4b, F5, F6a shadow puppets in the car panes)

Budget $10. **Spent $0** (everything is compositing from existing plates and canon sheets). Render: `PY -m tools.ink.run shots/<ID>.py --t0 <in_frame/24> --t1 <out_frame/24> --size 960x540 --fresh`
(pass `--fresh` after editing `shots/faces_lib.py`: the frame-cache key does not cover imported shot helpers).
Shared code: `shots/faces_lib.py` (album leaf + mount, face precompute, stamp/build, woodblock split, child figure).

| shot | status | frames | sources | QA (coverage, budget) | weak |
|---|---|---|---|---|---|
| H1 | done | 158 (149.708-156.292) | F_lianpu leaf rgba, faces F01 F02 F21 F06 F04 F23 F16 F08 F09 F11 (all six 3-stage builds) | mean 20 %, max 37 % (50) | see below |
| H2 | done | 152 (156.292-162.625) | leaf + 23 faces | mean 31 %, max 38 % (65) | |
| H3 | done (rebuilt per lead) | 80 (162.625-165.958) | the completed leaf + 23 faces (H2 plan), 白文 category seals, child (pale ink), EB Garamond line | close framings, paper-dominated | |
| H4 | done | 79 (165.958-169.250) | leaf + 23 faces + child + EB Garamond inscription | qa 45/69 % (the dark board is read as ground); leaf-only 30 % (40) | |
| F2 | done | 53 (108.833-111.042) | media/kf/F2.jpg, puppet rig (parts colour sheet) + swap heads | night qa 76 % (the plate alone is 70 %, KF log) | weak-ish: see below |
| F4b | done | 45 (114.333-116.208) | media/kf/F4b.jpg, rig, 8-pose run cycle band | plate-dominated | band on windscreen, not rear window |
| F5 | done | 43 (116.208-118.000) | media/kf/F5.jpg, rig | night qa 62 % (plate 57 %) | rear-window copies are small (the glass is 150 px tall) |
| F6a | done | 63 (118.000-120.625) | media/kf/F6a.jpg, rig | night qa 44 % (plate 43 %) | |

## Bridge: beats and events used (analysis/timing.json)

- Beats 149.72-169.22 (bridge, ~138.7 BPM): 149.720 150.162 150.588 151.024 151.463 151.894 152.325 152.762 153.195
  153.628 154.061 154.496 154.930 155.364 155.810 | 156.235 156.668 157.104 157.537 157.972 158.420 158.850 159.277
  159.711 160.143 160.583 161.025 161.447 161.886 162.315 | 162.746 ...
- **No breakbeat chops are measured inside 149.72-169.25** (the nearest is 149.295-149.390, in the silence). Rubbing
  flips and mis-registration are therefore locked to the strongest measured hits instead (listed per shot).
- H1: one face stamped per beat on 149.720 ... 153.628 (10 faces), hard cut ON each beat (cut 1/48 s before the beat
  so the overshoot frame is the first frame of the new framing), close (face 0.60-0.94 of frame height), anchors
  alternating left/right, high/low. Widening cuts on 154.061 154.496 154.930 155.364 155.810 (zoom 1.3 -> 0.68).
  Rubbing flips (2 frames): 151.675 (kick 1.0), 155.147 (perc 1.0). Woodblock mis-registration (colour block vs
  black-line block print apart, 0.16 s): 151.241, 152.978, 154.714, 155.810. Shake: 10 px on the crash 149.720, 4 px
  on the other landings.
- H2: pairs on 156.668 157.104 157.537 157.972; four on the fast roll 158.255 158.310 158.365 158.420; the last face
  (F14, beside the bare cell) alone on 161.886 with a shake, then the camera holds still to the cut (half bar).
  Cuts 157.104 157.537 157.972 158.191 158.850 160.143 (zoom 0.95 -> 0.555). Mis-registration on snares 159.277
  159.711 160.583; rubbing flip 160.143 (kick 1.0).
- H3 (rebuilt): stays ON the completed album. Hard cuts on the word onsets Tool 162.630, threat 163.480, trick
  164.360, kid 165.240 (cut 1/48 s before) to close framings of existing faces F04 blue (cell 10), F02 black (cell 3),
  F21 white (cell 13), F14 clown (cell 14), anchors alternating left/right; on each cut a plain 白文 cinnabar square is
  struck beside the face (tucked under its jaw, inside its own cell; slam + dent, 4 px shake). The kid framing also
  holds the bare cell, with the child (pale ink, from behind) standing at its foot. 165.54-165.958: ease-out widen
  (zoom 1.70 -> 1.55) to exactly H4's first framing. Lyric bloomed word by word, lower right, behind the switch.
  The four seals stay on the leaf and are visible in H4's pull-out. Cuts checked side by side: H2 last (full leaf) ->
  H3 first (close on F04) is a hard cut on Tool; H3 last = H4 first, pixel-identical framing.
- H4: pull-out 165.958 -> 168.30 (inout, log zoom 1.55 -> 0.405, the bare cell on a straight path), hold to 169.25.
  Inscription in the leaf's upper-left margin, written word by word on the onsets (the 165.94 ... did 168.76).

## How a face lands (faces_lib)

2 frames of a tightening stone shadow, then the PALE GROUND is stamped (scale 1.10 -> 0.965 -> 1.012 -> 1.0 over
frames 0-2, pressed-paper dent shadow decaying 0.12 s), the COLOUR FIELD is laid in one slanted bristle-streaked sweep
(frames 2-5), the BLACK LINES are drawn in three wipes, brows -> eyes/nose -> mouth/chin, each from the centre line
outward (frames 5-9.5). H2 runs the strokes at 0.6x duration, H3 at 0.8x. Real 3-stage builds for F01 F04 F08 F09
F11 F16; the other 17 are faked in code: ground = shared white with the cap kept, colour = the final face with thin
dark lines (not broad black fields) inpainted away. Paper fibres show through the gouache a little.
Mis-registration is done per face (colour block and line block offset in opposite directions), not with
`woodblock.misregister`, which cannot reprint white gouache (lighter than the paper) and erased the grounds.

## Notes for others

- F21 (water-white) in `design/plates/F_lianpu/faces/` was never normalised: its mask is the whole square sheet and
  its head is 0.78x the shared head, 8 px high. faces_lib fixes it at load (scale 1/0.78, F01 silhouette); the
  plate department may want to fix the file.
- `tools/ink/text.Inscription`: a unit whose glyph box starts left of x=0 (region x = 0, Latin 't' side bearing)
  is dropped entirely. Inset the region by a few px (H4 does).
- Continuity: H1 opens on 1 frame of the gathering stamp shadow on bare leaf paper, then the crash; H2 ends on the
  full leaf (grid nearly frame-filling), H3 cuts in close on the same leaf and hands H4 its first framing; H4 ends
  on the whole leaf on its darker board, child small in the bare cell, the line in the upper-left margin
  ("did" is still being written at the cut; it completes at 169.34 in H5's time).

## Rap shadow screen (F2 F4b F5 F6a)

**Splice ranges for the room team:** F4b = frames 2744-2788 (t 114.3333-116.2083, 45 frames; F4a = 2706-2743,
112.750-114.333, 38 frames: the split is the onset of 每一个都是我, 114.32). F6a = frames 2832-2894 (t 118.000-120.625,
63 frames; F6b = 2895-2914, 120.625-121.458, 20 frames: the split is the frame after the 120.6 wave cue).

- Rig (`shots/puppet_lib.py`): 10 parts cut from `puppet_parts_colour.jpg` by thresholding (parts lie apart on plain
  paper; no SAM/BiRefNet needed), pinned at the rivet holes found on the sheet (hole search, coordinates in the
  file); both legs use the same thigh/shin pieces (toes forward), plumes swept back. Leather = colour sheet divided by
  its paper, lifted (^0.55) for translucency, openwork and rivet holes open. Swap heads from the coloured row of
  `puppet_heads_swap.jpg`, scaled 0.64 to the rig's rivet. Poses: stand guard strike shade crouch leap salute + an
  8-pose run cycle; `tools.ink.puppet.Puppet` with hard re-posing only.
- Panes: **the sidecar quads do not match the painted keyframes** (crop/camera drift), so quads were measured on
  media/kf/<SHOT>.jpg (cover-fit to 16:9) and are in each shot file; a glass mask (violet or amber-lit, smooth,
  grown to the painted frame lines but never over dark paint) keeps heads, headrests, hair and the mirror in front.
  The room image is a parameter (`room_plate`: kf if present, else `_lit.png`); if the plate is repainted, re-measure
  the quads.
- Light: each puppet exists only inside a streetlight sweep (hot spot crossing the pane along the keyframe's light
  direction; up/down in 1 frame); lit = lamp amber x hide transmittance, unlit = the plate's dusk glass.
- F2 cues: 108.840, 109.300, 109.740, 110.175, 110.380, 110.800 (line onset, beats, echo 七 and 变): heads monkey -> pine
  -> bird -> fish -> cat -> monkey, poses stand guard leap crouch strike shade; one sweep per state, ~1 frame of dusk
  between.
- F4b: side copies (left rear, left front, right front) on out-of-phase sweeps, re-posed on beats 114.567 115.002
  115.445 115.882; the 走马灯 band (8 runners, 16 rpm, far side faint and reversed) runs across the windscreen under one
  long lamp, each runner stepping one run pose per beat.
- F5: four copies (right side, rear window x2, left side) go dark on beats 116.320 116.736 117.200 117.628; empty dusk
  glass to 118.000.
- F6a: two identical puppets mirror-posed either side of the windscreen centre, re-posed together on 118.000 118.500
  118.938 119.374 119.812 120.249, one shared lamp per pose.
- Lyrics (switch `ctx.opts['lyrics']`): pale LXGW WenKai columns on the night picture, word onsets from timing.json,
  inside the 4:5 area. The echo lines (七十二变)/(谁是真身) are not set (timing.words() maps them to the main line).

## Weak / open

- The faked builds for non-build faces are good at speed but the colour stage of F13/F11-like faces shows brief
  inpainting smears for ~2 frames.
- F2: the painted amber streak on the keyframe glass stays static under the moving lamps. The bird pose (leap) reads
  sideways. Swap heads are a little smaller than the rig's own head.
- F4b: the brief's rear-window band became a windscreen band (see above); a thin violet strip remains above the
  mirror. The left-front pane is mostly hidden by the seat, as painted.
- Car qa coverage is dominated by the dense painted plates (KF log: F2 70 %, F5 57 %, F6a 43 %), not the puppets.
- H4 coverage by `qa` reads high because the board around the leaf is darker than the leaf; leaf-only is 30 %.

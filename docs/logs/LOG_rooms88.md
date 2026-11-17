# LOG team ROOMS-88 (the 1988 attic)

Shared code: `shots/_rooms88.py` (RoomShot: clip/still source registered to its keyframe by ORB + similarity fit and
colour-matched; page tracking per frame and page-art mapping in perspective; the neon sign; dust; hand/head/ring
shadows; paper fibre; compositor camera; lyric inscriptions behind `ctx.opts['lyrics']`), `shots/_attic_grade.py`
(ONE grade for every attic shot: crush outside the neon pool to warm ink wash, faces protected with soft weights),
margins from team MOUNTAIN's `shots/_margins.py` (G1, G3, G4, G5).
Generation: `shots/_r88_gen.py` (all specs, prompts in `media/comp/rooms88/prompts/`, audio windows with the other
singer muted in `media/comp/rooms88/audio/`). Picks + retime: `shots/_r88_pick.py` -> `media/comp/rooms88/clips.json`
(lip-sync numbers cached in `media/comp/rooms88/lipsync.json`). Render+sheet+QA: `work/r88/do.sh ID BUDGET`.
Sheets: `work/review/comp/<ID>.jpg`. Coverage = `tools.ink.qa coverage --ground night` (the keyframes are painted
25-45 points over their budgets; the grade pulls them down but not to budget: see each row).

## The sign
`Sign` in `_rooms88.py`: mirror-reversed `CHIN. IND. SPEC. REST.` (Nimbus Sans Narrow centre-line tubes) under 酒家
(LXGW WenKai outline tubes), in a thin border tube, cinnabar breathing to cold pale blue and back (period 9 s on the
song clock, phase 0, so it is one continuous object across cuts), behind the painted glass (glass = bright AND red
pixels of the keyframe's window, so mullions, frames and people in front hide it), soft core + small halo. The room's
red pool and the glass cool with it. Placed in the PAINTED window of every keyframe where one shows (the sidecars
put the window in frame only in A1/C5a/L3, the paintings show it in most shots). No window: A2, B1, C2, G1, G3.

## Checkpoint 1 (A1, L3, A2, C2, B2, B1, G5)
## Checkpoint 2 (C3, D3, D2d, E1, E3, E5, E6, A3, A4, C5a, D9, F3b, G1, G3, G4)

| Shot | Deliver (song frames) | Status | Source | Lip-sync (take, r, lag vs synced -> clip frame 0 at) | Coverage (budget) | Weak / notes |
|---|---|---|---|---|---|---|
| A1 | A1.mp4 0-130 (131) | done | code: A1 / A1_off blended by the tube level; stutter-on on the measured clappers 0.165-0.381, dip at the 0.605 silence, relit 0.775 | - | 5.5 % (10) | - |
| A2 | A2.mp4 131-232 (102) | done | code: A2 keyframe, drift left (compositor), floorboard light lines come up, dust in the beam | - | 37 % (15) | over budget: the painted red pool is large; drift is a flat 2D pan (no parallax) |
| A3 | A3.mp4 233-301 (69) | done | Kling v4 A3 -> A3_end, on twos | - | 27 % (15) | little Jade's hair too long (keyframe) |
| A4 | A4.mp4 302-371 (70) | done | Kling v4 A4 -> A4_end, on twos | - | 51 % (20) | bright close-up (hands + pillow fill the frame) |
| B1 | B1.mp4 372-534 (163) | done | Seedance 2.5 t1 | t1 r 0.46 (t2 0.24), +560 ms -> 14.750 | 28 % (20) | the last 0.5 s holds the take's last frame |
| B2 | B2.mp4 535-626 (92) | done | Seedance 2.5 t1; spread = B3's page-space build (imported from shots/B3.py), tracked per frame | t1 r 0.51 (t2 0.50), +560 ms -> 21.730 (mouth box: no FaceMesh face in the wide shot) | 52 % (20) | push from 25.05 lands on the spread (zoom 2.6, 720p clip upscaled: soft at 1080p) so the cut into B3 continues it |
| C2 | C2.mp4 1084-1107 (24) | done | keyframe still (the Kling take painted its own flat hand shadow and lost the raised fingers: rejected), 4 % push; monkey-head shadow from handshadow_silhouette.jpg pops ON 45.275, settles, trembles; red neon on the page | - | 42 % (20) | still, not a clip (only the shadow moves) |
| C3 | C3.mp4 1108-1190 (83) | done | Seedance 2.5 t2 (C3 -> C3_end) | t2 r 0.40 (t1 0.36), +18 ms -> 45.647 (mouth box 415,215,60,45) | 34 % (20) | 'Monkey!' muted from Mama's audio window |
| C5a | C5a.mp4 1254-1310 (57; MOUNTAIN's C5b starts 1311) | done | Kling v4 C5a -> C5a_end, on twos; dust motes; egg page (B_egg) on the open book | - | 50 % (15) | not a true contre-jour (keyframe); the egg reads faintly at 540p |
| D2d | D2d.mp4 1531-1545 (15) = last 15 f of D2 | done | two keyframes painted for it (edits of D9: `media/kf/D2d_stand.jpg`, `media/kf/D2d.jpg`, $0.27): stand -> hard re-pose into the bow on 63.980 + STAGE's 倉 (`tools.stage.stage.seals`, cang_small) strike + their 2-frame jolt | - | 35 % (45) | the bow is shallow (a small girl's bow), faces camera rather than a compass direction |
| D3 | D3.mp4 1546-1629 (84): D3a 1546-1567, D3b 1568-1629 | done | D3a: keyframe, painted beams inpainted out and redrawn as gold lines flying up from the page in 0.2 s (only gold/self-lit moment), birth page (B_stone_crack, right half); D3b: Seedance 2.5 t2 | D3b t2 r 0.35 (t1 0.24), -982 ms -> 64.982 | 39 % (30) | weak lip-sync: faces small (wide, per lead); head drift 47 px |
| D9 | D9.mp4 1980-2059 (80) | done | Kling v4 (wobble + laugh), on twos; compositor pull-back 1.25 -> 1.0; birth page on the book | - | 36 % (20) | window on the back wall (keyframe) |
| E1 | E1.mp4 2060-2145 (86) | done | Seedance 2.5 t1 (forced) | t1 r 0.32, +852 ms -> 84.493. t2 scored 0.41 but FaceMesh found the face in 53 % of frames and its -1148 ms would put the nose tap (clip 3.6 s) after the shot; t1's tap lands at ~88.4 (word 'you' 88.5) | 43 % (20) | weak-ish score |
| E3 | E3.mp4 2232-2397 (166) | done | Seedance 2.5 t2 | t2 r 0.50 (t1 0.22), +518 ms -> 91.972 | 56 % (20) | no shrug in the take; Mama's 'blur' is a shoulder + stick shape (keyframe) |
| E5 | E5.mp4 2477-2502 (26) | done | Kling v4 from clip 0.4 s, on twos | - | 44 % (20) | hand at her own mouth (keyframe; reads as a whisper) |
| E6 | E6.mp4 2503-2568 (66) | done | Kling v4 E6 -> E6_end, on twos; eyes go wide on the last frames (pickup 107.04) | - | 38 % (20) | - |
| F3b | F3b.mp4 2694-2705 (12) = last 12 f of F3 | done | Kling v4 from clip 0.55 s (the hairs fly), on ones | - | 35 % (30) | Mama's dark clothes kept dim |
| G1 | G1.mp4 2915-3058 (144) | done | Seedance 2.5 t1 (G1_end -> G1, forced: the gesture), margins | t1 r 0.35 (t2 0.36), -815 ms -> 121.773 | 50 % (20) | weak score |
| G3 | G3.mp4 3225-3389 (165) | weak | Seedance 2.5 t2 (forced: t1 painted two upside-down faces on the blank pages), margins; pilgrim page; flat-hand shadow (procedural) sharpens and settles over the gold band | t2 r 0.23 (t1 0.29), +393 ms -> 133.477 (no FaceMesh face: she looks down) | 16 % (15) | WEAK lip-sync (face down, mouth small); the shadow is procedural and drifts a little with the page track |
| G4 | G4.mp4 3390-3514 (125) | done | keyframe still (the Kling take's hands doubled after 3 s), compositor push; head shadow + finger-and-thumb ring shadow (enlarged, a band) lowering from 142.0 onto its brow on 'wear' (143.65); on the clean right page so it reads in the 15 % strip | - | 12 % (12) | still: only the shadows move |
| G5 | G5.mp4 3515-3582 (68) | weak | Seedance 2.5 t1, audio window silent until 'Yes'; face centred in the strip | t1 r 0.26 measured with --maxlag 0.6 (at 1.2 s the correlation locked on noise: +1018 ms, checked on the frames: the mouth opens at clip 2.3-2.9 s vs 'Yes' at 2.76 s), -357 ms -> 146.315 | 8 % (12) | WEAK score (one word, articulation 0.07); the 15 % strip cuts the outer eye corners |
| L3 | L3.mp4 5660-5719 (60) | done | code: A1 humming (faint mains hum), hard off at 237.840 to A1_off, sunk to black | - | 6 % (5) | - |

Splices for the lead: C5a.mp4 = song frames 1254-1310 (MOUNTAIN C5b.mp4 from 1311). D2d.mp4 = frames 1531-1545 (replace
the last 15 frames of STAGE's D2.mp4, which holds from 63.817). F3b.mp4 = frames 2694-2705 (the last 12 of F3).
D3.mp4 is one file (both parts ours).

Spend (list estimates, tags r88_*): 18 Seedance 2.5 takes $23.58, 9 Kling v4 clips $4.85 (C2, G4 unused), 2 nbp
keyframe edits $0.27. Total $28.70 of $55.

QA: every file is 960x540 24 fps with the exact frame count (checked with ffprobe). G3 and C2 also rendered at 1920x1080
without changes. Lessons: Seedance outputs are reframed 1-2 % against their first frame (registered by ORB); Seedance
lags here ran +0.5 s (B1/B2/E3, checked on the frames); a near-silent window (G5) needs `--maxlag 0.6`.

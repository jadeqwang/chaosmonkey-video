# LOG v4 STAGE team (costume B monkey): D1 D2 D7 D8 J3 + D6 monkey element for WORLD + costume-B pose set

Brief: `docs/REVISION_V4.md` §1, §5 D/J, §8; `docs/TEAMS_V4.md` (ceiling $80). Scratch: `work/stage/v4/`.
Tags: images `stg4_*`, video `s4_*` (`tools/gen/spend.py --tags`). v3 backups: `media/comp/_v3/`, `shots/_v3/`.

## CHECKPOINT 1 (start)
- done: read briefs, v3 log, scripts. B sheet is a single model sheet (4 views + face) -> pose sheets needed.
- plan: (1) costume-B pose sheets with gpt-image-2 at 3840x2160, 4 figures per sheet, B sheet + v3 pose singles as
  refs -> `design/characters/monkey/v4/`; cut singles. (2) keyframes on one blank sheet (as make_frames_v3).
  (3) video: Kling v4 multi-keyframe (first + middle_frames + last) for D2 (four real bows) and D8 (climb through
  intermediate poses, no teleport); Seedance 2.0 first+last 1080p for D1; Kling v4 / h3 2K for D7 J3 D6-element.
- pending relay jobs: none.

## READY: monkey B poses (2026-11-18)
Costume B (key-fret jacket, leopard trim, red scarf, yellow knot cap, ringed gold eyes, gold-banded staff), gpt-image-2
3840x2160 from the B sheet only (`design/characters/monkey/v3/monkey_v3b_ALT_fret_leopard_redscarf.jpg`), 4 figures
per sheet. Sheets `design/characters/monkey/v4/monkey_v4b_poses_{A_liang,B_bows,C_staff,D_climb,E_tumble,F_cloud_swarm}.jpg`
(prompt in the .txt beside each). Singles, one figure each on its own paper (key with `key_paper(img, lo=0.025)`):
`design/characters/monkey/v4/singles/01..24_*.jpg` (+ README.txt). Overview: `work/stage/v4/tmp/singles_overview.jpg`.
- 01 亮相 look-out on one leg | 02 合十 hands (NOT the martial salute; do not use) | 03 thrust lunge | 04 newborn crouch
- 05/07 deep bow, profile facing screen LEFT (mirror for right) | 06 bow to viewer | 08 bow seen from behind (抱拳 hands)
- 09 staff flower | 10 overhead spin | 11 overhead strike | 12 low sweep
- 13-16 climbing the planted staff (plant, low, high, perched hand at brow); staff lengths differ slightly per figure
- 17 launch | 18 tucked somersault | 19 layout somersault | 20 landing crouch
- 21 riding the 筋斗云 cloud, hand at brow | 22 somersault over the cloud | 23 plucking a hair, about to blow (swarm)
  | 24 seated cross-legged, palm open (swarm original)
Checked by eye on the sheets: costume parts present on every figure, same face, five-fingered hands at sheet size.
The hand is a little cleaner/more illustrative than the B sheet's wet wash (same design). Spend: 7 images, ~$1.40.

## CHECKPOINT 2
- done: pose set (above). Keyframes `tools/stage/make_frames_v4.py` -> `media/gen/stage/v4/frames/` (overview
  `work/stage/v4/tmp/frames_overview.jpg`): one scale per shot; D8's staff made one length across the climb keyframes
  (`restaff`: only bare-staff rows resized). v3 comps/scripts backed up to `media/comp/_v3/`, `shots/_v3/`,
  `tools/stage/_v3/stage3.py`.
- relay batch 1 (19 takes, ~$27 est), specs `media/gen/specs/s4_*.json` written by `tools/stage/submit_v4.py`,
  prompts `media/gen/stage/v4/prompts/<shot>.txt`. Collect: `PY tools/gen/gen.py collect` then
  `PY tools/stage/takes4.py` (copies to `media/gen/stage/v4/clips/`, 16-frame sheets in `work/stage/v4/takes/`).
  d1: sd20a/b/c (1080p f+l) + h3 2K | d2: k4a/b/c (multi-keyframe 亮相 -> E S W N, 5/6/7 s) | d6 element: k4a/b/c
  (cloud ride -> somersault -> 亮相) | d7: sd20a/b + k4a | d8: k4a/b/c (thrust -> plant -> low -> high -> perched) |
  j3: k4a/b + sd20a.
- side job: subagent checking the F2 transformation list against ch. 6 text (REVISION_V4 §5 F2 "STAGE: verify").
- next: sheets + zoom strips, blind ranking subagent, key picks (`prep4`), rewrite shot scripts, render, sheets.

## F2 list checked against ch. 6 (for SWARM, who owns F2; REVISION_V4 §5 F2 "STAGE: verify")
Source: zh.wikisource 西遊記/第006回 (read through a summarising fetch: wording approximate, order reliable).
Wukong -> Erlang's answer: 麻雀 -> 鷂鷹 (sparrow-hawk) | 大鶿老 (cormorant) -> 大海鶴 | 魚 -> 魚鷹 | 水蛇 -> 灰鶴 |
花鴇 (bustard) -> Erlang takes his own form, shoots it with a pellet (the form is too lowly to approach) |
土地廟, the tail stood up BEHIND it as the flagpole (旗竿立在後面) -> Erlang sees through it. Then Wukong takes Erlang's
own form (變作二郎爺爺的模樣) and goes into Erlang's temple at 灌江口.
Verdict: the brief's list, order and the flagpole-behind-the-temple detail are right. Unlisted: Erlang's counter-forms
and the last form (Wukong as Erlang). Typeset 鴇/鸨 and 鶿/鹚 to match the rest of the on-screen text if any label appears.

## CHECKPOINT 3
- batch 1 collected (19 clips, `media/gen/stage/v4/clips/`), sheets + zoom strips `work/stage/v4/takes/`, blind copies
  `work/stage/v4/blind/` (key `work/stage/v4/tmp/blind_key.json`), keyed stores `work/ink_clips/s4_*`.
  Teleport check `tools/stage/jumps4.py`; consecutive strips `tools/stage/strip4.py` / `strip4b.py`.
- blind ranking (fresh subagent, letters only): d1 h3 > sd20a > sd20c > sd20b | d2 k4a > k4b (face mush f82) > k4c
  (shallow, north bow missing) | d6 k4b > k4c > k4a (both limb smears) | d7 k4a > sd20a (ghost staff) > sd20b (red
  ribbon trails) | d8 k4a > k4c (leg smear) > k4b (staff bends) | j3 k4a > k4b (mush f38, loose scarf) > sd20a (no sweep).
- my checks: d7 k4a f77->f78 is a snap re-pose with a brush-smear fan (reads as a strike, keep); j3 k4a f31-46 smooth;
  d8 k4a f16->f17 staff swing down is abrupt -> the comp starts D8 at the plant (f17), climb f17-100 continuous;
  d2 k4a hands smear f10-13 in the transition out of 亮相; d6 k4b face smear on landing f86-90.
- round 2 queued: salute pose sheet G (`monkey_v4b_poses_G_salute.jpg`, singles 25-28) -> D2 with 9 keyframes
  (亮相, salute+bow per direction) k4d/k4e (8 s), k4f (9 s); D6 with 5 keyframes (cloud, tuck, layout, crouch, 亮相)
  k4d/k4e (6 s). Spend so far ~$29 + round 2 $8.7.

## CHECKPOINT 4
- rendered on costume B (960x540, exact frames, sheets `work/review/comp_v4/<ID>.jpg`): D1 (h3, 58 f), D7 (k4a, 69 f),
  D8 (k4a, 77 f), J3 (k4a, 91 f). D1/D2 hand-over moved to `tools/stage/stage4.py` (D2_PRE = frame 1451; D2 nadirs per
  take in `work/stage/v4/d2_nadirs.json`, `tools/stage/d2nadir4.py`). D1 currently uses s4_d2_k4a for its last 15 frames.
- D7: clip laid at 1.04 so the overhead-spin staff leaves the frame instead of hitting the model's frame edge; 亮相 =
  the one-hand thrust f88 held (the take's f90-95 re-pose smears, never shown); ring stain softened (keep .30, blur 12)
  and skipped in medium-switch frames (it cut as red blobs). J3: figure lit warm-white under the neon (yellow, not
  orange), switches shown under a mostly neutral light, stain skipped in switches; 亮相 = clean thrust f97-99.
- waiting: round 2 (D2 k4d/e/f, D6 k4d/e) still queued on the relay.

## D6 element handed to WORLD (also written into LOG_v4_world.md)
`tools/stage/d6_monkey.py` (`monkey_layer(t, W, H)`, `FOOT`), pre-render `media/el/stage_v4/D6_monkey_B_T.mp4` (+png,
json; `tools/stage/d6_element.py s4_d6_k4b 3.833 5.9`). Take s4_d6_k4b; round 2 (k4d, k4e: 5 keyframes) ranked below
it blind (k4e unusable: smears, cloud reappears; k4d: spread-eagle not a tuck, cloud returns).

## CHECKPOINT 5
- round 2 blind (fresh subagent): D2 k4a > k4d > k4e > k4f (9-keyframe takes made the front/back bows SHALLOWER; k4d
  shows 合十 hands in the opening turn) -> D2 stays on s4_d2_k4a. D6 k4b > k4d > k4e -> k4b.
- D2 rendered on k4a (80 f): east 61.321, south 62.205, west 63.090, north 63.980 nadirs, all four deep (sheet).

## DONE (2026-11-18)
All five stage shots re-made on costume B, 960x540, 24 fps, exact frame counts, no audio, `media/comp/<ID>.mp4`
(v3 in `media/comp/_v3/`, `shots/_v3/`). Sheets `work/review/comp_v4/<ID>.jpg` (16 f), `<ID>_dense.jpg` (every 2nd
frame), `<ID>_zoom.jpg` (figure crops). 1080p = re-render (`PY tools/stage/render4.py <ID> --size 1920x1080`; sources
are 1080p Kling / 2K h3; 1080 stills rendered OK for all five).

| shot | takes (blind rank) | pick | fixed vs v3 | still weak |
|---|---|---|---|---|
| D1 58 f | h3 2K > sd20a > sd20c > sd20b | s4_d1_h3 | 2K source (was 720p); blot -> black silhouette in pose -> ink figure -> colour, complete by 59.55; wind-up into D2 from f1451 (was 1445): pose held ~1.4 s, in full colour ~0.85 s | hold still shorter than ideal (D2's first bow is pinned at 61.321); throw flight not seen (gong is frame 1408, as v3); hands soft for 2 frames in the wind-up (f1454-57) |
| D2 80 f | k4a > k4d > k4e > k4f > k4b (face mush) > k4c (shallow) | s4_d2_k4a | multi-keyframe: four real 抱拳 bows (fist under palm at the chest), all deep, E S W N, nadirs on 61.321/62.205/63.090/63.980 | rise into the west bow shows flat palms for a moment; north bow (63.98) lies past the cut's first 65 frames (D2d copies it) |
| D7 69 f | k4a > sd20a (ghost staff) > sd20b (ribbon trails) | s4_d7_k4a | big black dry-brush fans, overhead spin, one-hand thrust 亮相 on 78.808; staff leaves frame instead of hitting the model's frame edge | lasting ring reads as a soft grey halo, not crisp 飞白; strike f47-50 is a smear-frame snap |
| D8 77 f | k4a > k4c (leg smear) > k4b (staff bends) | s4_d8_k4a | every climb phase is a keyframe; one staff length; no twos; starts with the staff planted (abrupt swing-up never shown): no teleport frames (motion metric max step 1-2 px/frame outside the switch) | the monkey is small on the tall staff; staging begins planted (v3 began on the lunge) |
| J3 91 f | k4a > k4b (mush f38, loose scarf) > sd20a (no sweep) | s4_j3_k4a | figure lit warm-white under the neon: yellow, not orange; paper-cut switch readable (neutral light), stain kept out of switches | yellow under red now mustard rather than bright gamboge; 亮相 held ~35 frames near-still; stone-rubbing switch is dark by nature |
| D6 element | k4b > k4d > k4e (r2); k4b > k4c > k4a (r1) | s4_d6_k4b | handed to WORLD (see above) | 2-3 smear frames at the landing |

Not checked: nothing watched at speed; seams D1->D2 (shared clip), D7->D8, J2->J3->J4 not compared frame to frame;
lyric layer not overlaid. Spend: $37.58 (8 images $1.63, 24 video clips $35.95), ceiling $80. No relay jobs pending.
Shared code touched: `tools/stage/stage3.py` RingStain.density reads an optional `soft` (default 5.0, unchanged
behaviour for v3 scripts). New: `tools/stage/{imgen4,cut4,make_frames_v4,submit_v4,takes4,prep4,jumps4,strip4,
strip4b,d2nadir4,render4,stage4,d6_element,d6_monkey}.py`.

# LOG v3 STAGE team (monkey, opera stage, swarm): D1 D2 D6 D7 D8 J3 + F2 F4b F5 F6a

## DONE round 2 20:38
From `docs/QA_PREVIEW_V3.md` (items 1, 5, 13). All re-rendered at 960x540, exact frames, sheets in
`work/review/comp_v3/`, each looked at (sheets and single frames; nothing watched at speed).
- **F6a** (63 frames delivered; the cut uses the first 50): cues 118.5, 118.938, 119.374, 119.812. Left 真 seal on
  119.12 (frame 2858), right 真 seal + both salute on 119.812 (frame 2875). Frames 2876-2894 are a still hold. The
  lunge pose was dropped. Round-1 script: `work/stage/v3/F6a_round1.py`.
- **Lyric band**: the 3x3 leaf (F4b, F5) now ends at y = 872/1080 (outer rule 881), figures 184 px (was 205); F6a's
  leaf ends at 860/1080. Below that is bare lit paper. The lyric layer's y for these three still has to be moved
  into the band by the lead (`tools/cut/lyrics.py`); I did not touch that file or re-check the overlay.
  Round-1 lib: `work/stage/v3/swarm_lib_round1.py`.
- **F2** (53 frames): now on BED+CAR's v3 keyframe `media/kf/v3/F2.jpg` (the STILL: she does not move). Pane quad
  measured on the painting (`V3_QUAD`/`V3_POLY` in `shots/F2.py`; the sidecar quad does not match). Jointed puppet,
  capped head without plumes, heads monkey -> pine -> bird -> fish -> cat -> monkey on the v2 cues, amber lamp sweeps;
  her pointing hand stays in front of the glass. The acted plate `media/kf/v3/F2_plate.mp4` (+ `F2_pane.json`) had
  not been written when I finished: when it exists, `PY tools/stage/render3.py F2` picks it up; that clip path has
  never been run. Weak: the puppet is the dark leather rig, not yellow; the staff floats off the hand in the first
  pose; two lamp sweeps leave the puppet pale; in the last pose the arm covers the head.
- **F2 round 3 (20:49)**: re-rendered on the car team's acted plate `media/kf/v3/F2_plate.mp4` with
  `F2_pane.json` (53 frames, sheet looked at; not watched at speed). Her hand and forearm are composited back over
  the screen from `F2_fg_matte.mp4`. The screen mask is now the whole glass `poly` grown 5 px and the screen quad was
  enlarged to contain it (top edge lifted 60-109 px, right/bottom pushed out): no blue slivers on the sheet. First
  pose: staff planted upright in the hand; last pose: the BACK hand shades the eyes, head uncovered (`POSE3`).
  Puppet lowered and shrunk to 74 % of the screen height. Left: the leaping (bird) pose's raised hand still touches
  the top of the glass; two lamp sweeps leave the puppet pale (as v2); the puppet is the dark leather rig.
- No relay jobs, no spend in round 2.

---
## DONE 15:11
Final state: D1 D2 D6 D7 D8 J3 F4b F5 F6a rendered for preview_v3 (960x540, exact frame counts, sheets in
`work/review/comp_v3/`). **F2 is not revised** (waits on the car team's `media/kf/v3/F2.jpg`; then
`PY tools/stage/render3.py F2`). No relay jobs pending. Restore the dark monkey / v2 swarm: copy
`media/comp/_v2/<ID>.mp4` and `shots/_v2/<ID>.py` back. Per-shot table, picks, weak points, what was not checked and
spend: sections 4-6 below. Open questions for the lead: leaf intercut vs car panes for the swarm; costume (a) vs the
alternate (b) sheet; F5 one per half beat; D2's tail vs D2d.

---
Brief: `docs/REVISION_V3.md` §2.4, §3.3, §3.4, §3.5. Scratch: `work/stage/v3/`. v2 backups (restore = file copy):
`media/comp/_v2/<ID>.mp4`, `shots/_v2/<ID>.py`, `shots/_v2/puppet_lib.py`, `tools/stage/_v2/`.
NOTE (machine): /tmp (tmpfs 16 G) is 99 % full from other sessions; scratch kept in `work/stage/v3/`.

## 1. Monkey v3 (yellow)  [14:20-14:40]
- Three model-sheet tries (`design/characters/monkey/v3/_tests/`): nbp+ref (clean costume illustration, reads as a doll),
  sd5 no ref (flat yellow, a new face), **sd5 + old model sheet + L3 as refs = pick**: wet 藤黄 wash with pooled edges
  over quick ink line, dark swirl marks, the SAME face as the v2 monkey (cinnabar peach field, gold eyes), black fur at
  the head and wrists, dark ochre flap skirt, black boots, yellow pompom cap, knotted yellow scarf. No plumes (the
  opera 猴帽 has pompoms, not 翎子): the scarf ends take over the plumes' job (trailing arcs).
- Pose sheets by passing the OLD pose sheets as pose/layout reference + the v3 model sheet as design reference
  (sd5): poses and spacing carried over one to one, so every v2 first/last frame has a v3 twin.
- Files: see CANON "5c. Monkey v3 (yellow)".
- Opera photos: none used anywhere (the researcher's topic-1 folder was still empty; the design was written from
  the costume's known parts). Only our own sheets were passed to models.

## 2. D6 plate: the Buddha's palm  [14:30-14:40]
- Traditional reference (researcher, topic 2): 絵本西遊記 1806, "悟空自驚在佛掌中" (the five finger pillars in cloud),
  `refs/paintings/v3/02_buddha_palm_wuxingshan/ehon_saiyuki_1806_wukong_in_buddhas_palm_five_finger_pillars.jpg`
  (public domain print; passed to the image model as composition reference).
- v1 prompt (whole hand lying palm-up + fingers as pillars): both models drew extra fingers (rejects in
  `design/plates/D6_palm/_tests/palm_*_v1.jpg`). v2 = the print's own composition: ONLY the five fingers standing out of
  a cloud sea, nails and knuckle creases, cloud band along the whole bottom. Pick: sd5 (`design/plates/D6_palm/D6_palm.jpg`).

## 3. Swarm layout decision  [14:40-14:55]
Options sheet: `work/review/comp_v3/_swarm_options.jpg` (A car panes as cells / B ruled album leaf full frame / C leaf
across the windscreen), each panel 960x540. Judged at a third of that size (1400 px sheet):
- A: reads as "puppets on car windows joined by a red line". The panes sit in one row, so the threads collapse into one
  horizontal line; no grid; five irregular cells; name slips are 10 px.
- C: the leaf is 480x160 px at 540p: cells 53 px high, nothing readable.
- **B (pick)**: grid, labels, hub and spokes are read before any single figure is: the orchestrator diagram. A
  traditional eye gets a ruled album leaf of 皮影 figures with 榜题. The car is kept by LIGHT: dusk paper with amber
  streetlight pools passing behind it (the leaf is the window become an album), and by the cut (F4a mirror before,
  F6b after). It also does not depend on the re-blocked car plates.

## 4. Video takes (batch 1: 13 clips, all returned; plate batch: 2 clips)  [14:45-15:15]
Frames: `tools/stage/make_frames_v3.py` -> `media/gen/stage/v3/frames/`; specs `media/gen/specs/s3_*.json` (written by
`tools/stage/submit_v3.py`); prompts `media/gen/stage/v3/prompts/`; clips `media/gen/stage/v3/clips/`; 15-frame sheets
`work/stage/v3/takes/<tag>.jpg`; keyed stores `work/ink_clips/<tag>` (`tools/stage/prep3.py`, `key lo=0.03`).

| shot | takes | pick | why |
|---|---|---|---|
| D1 | `s3_d1_sd20` (1080p), `s3_d1_sd20b` (720p) | **sd20b** | b: splash -> ink-LINE monkey -> the yellow floods through him (what §3.4 asks). a: the splash gathers into a solid black monkey that then recolours |
| D2 | `s3_d2_kling4` (first+last), `s3_d2_kling4ff` (first frame only), `s3_d2_sd20` | **kling4ff** | the only smooth take with all four bows in order (east, south, west, north). kling4 first+last gives south, west, north only; sd20 has four but steps on threes with long holds (the roughness the director disliked) |
| D6 | `s3_d6_kling4`, `s3_d6_sd20` | **kling4** | two clean tucked somersaults right to left, touch-down between them, lands and rises into 亮相. sd20: one somersault then walks |
| D7 | `s3_d7_sd20`, `s3_d7_kling4` | **sd20** | full dry-brush rings round him (舞花 reads); kling gives short arcs |
| D8 | `s3_d8_kling4`, `s3_d8_sd20` | **kling4** | plants, climbs, perches, hand to brow late (lands on the snare). sd20 equal but 720p |
| J3 | `s3_j3_kling4`, `s3_j3_sd20` | **kling4** | bigger wet sweeps, leap, lunge. sd20 has a back view and scarf growing long |
| D6 plate | `s3_d6pl_h3` (2K), `s3_d6pl_kling4` | **h3** | slow real travel (thumb moves 105 px at 1920) and paper-coloured mist rising between the fingers, plate otherwise locked. kling: tan dust fog and too much travel |

## 5. Shots
| shot | status | on screen | weak |
|---|---|---|---|
| D1 | done, 58 f | Throw lands ON the gong (frame 1408) as a black splat, bleeds, gathers into the ink-line monkey in 亮相 (58.96); from 59.126 the gamboge floods through him, whole by 59.98. 倉 on the gong. Inscription 五官俱备 / 四肢皆全 (key D1). Medium switches: paper-cut on "born" 59.595, rubbing on "fully" 60.02 (4 held frames, same pose). From f1445 he lowers the leg and turns: the wind-up of D2's clip | the 亮相 holds only ~1.1 s before he moves; first frame is already the splat (no flight) because the gong is in frame 1408; clip is 720p (soft at 1080 master) |
| D2 | done, 80 f | One continuous performed movement: east bow 61.321, south 62.205, west 63.090, north (his back) 63.980, each nadir on its beat, held 2 frames; 才 才 才 仓 pressed in a column under D1's 倉. Inscription key D2 | the model's bows are palms-forward pushes rather than cupped fists; the south bow is shallower than the others; scarf ends grow long on the north bow |
| D6 | done, 70 f | The whole composition in frame: five pillars in a cloud sea at the left (h3-animated plate: slow travel, mist between them), fine rays behind; the monkey somersaults in from the right twice, lands 亮相 at their foot on the kick 75.025 with a small 倉; on that hit, 4 held frames of red paper-cut in which the pillars are plainly a hand | fingers read as fingers at once, before the "pillars" reading; monkey is small (~150 px at 540p); parallax between fingers is slight (the travel is real, the depth separation modest) |
| D7 | done, 69 f | Staff flower: the model's own dry-brush rings, and what they write stays as a pale lasting ring; lunge and thrust land 亮相 on the snare 78.808 + 倉. Switches: shadow puppet on the kick 77.919, paper-cut on 78.808 | the lasting stain is soft/blocky where the model's ring broke into dashes |
| D8 | done, 77 f | Plants the staff, climbs, perches, hand to brow on the snare 80.806 + 倉 + rubbing switch; from 81.45 figure and seal sink into the paper; ends near bare | the climb is quick (two frames of teleport-like motion mid-climb) |
| J3 | done, 91 f | Staff form over the blue-green heaven under the 1988 red neon; one cut to the 2026 torch-lit page on 194.963 with the last sweep crossing it; thrust 亮相 195.181 + 倉, echo re-press 195.65. Paper reserved under his silhouette so the yellow reads. Switches: paper-cut 193.459, rubbing 194.103 | in the red light the yellow reads orange; switches are tinted by the room light; no inscription (no blank on this page) |
| F4b | done, 45 f | Ruled 3x3 leaf: eight shadow-puppet copies, one job each with a typeset slip (读 写 算 运 战 扫 望 磨), the original (我) seated in the centre, hand raised, a cinnabar thread to each; all cells step a pose on each beat | figures are ~95 px at 540p: jobs read by prop + slip, not by acting; threads end at the copy's body, crossing some props; the car is present only as light |
| F5 | done, 43 f | Same leaf: clockwise, one copy per half beat presses a red 讫 in its cell, becomes a hair and flies home along its reeling thread; ends on eight sealed empty cells and the one monkey | one per HALF beat, not per beat; hair is 3 frames, easy to miss |
| F6a | done, 63 f | Two cells, two identical monkeys mirror-posed, each holding a thread to the other's chest, both slips 真; seal 真 left on 119.12, right on 120.249 | threads cross in an X that reads a little like a diagram error on the pointing poses |
| F2 | NOT revised | `media/comp/F2.mp4` is still the v2 comp (old car, v2 plate). Script is ready for the v3 plate | blocked on `media/kf/v3/F2.jpg` (BED+CAR) |

Not checked: no playback at speed was watched (sheets and single frames only); no 1080p render of the v3 scripts was
made; `tools.ink.qa coverage` was not run; neighbours' cuts (C6->D1, D2->D2d/D3, D5->D6, D8->D9, J2->J3->J4, F4a->F4b,
F6a->F6b) were not compared frame to frame. Sound cue times (§11) not cross-checked.

## 6. Spend
About $18 list-price estimate of the $150 ceiling (`spend.py --tags`, tags `s3_*`, `stg3_*`: $17.10 over 23 tags; a
few image calls may be tagged outside that pattern): 13 figure clips $15.28, 2 plate clips $1.83, ~11 images ~$1.1.

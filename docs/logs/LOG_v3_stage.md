# LOG v3 STAGE team (monkey, opera stage, swarm): D1 D2 D6 D7 D8 J3 + F2 F4b F5 F6a

## CHECKPOINT 14:57
**Done (rendered 960x540, exact frames, sheet in `work/review/comp_v3/`, looked at):**
- Monkey v3 (yellow): `design/characters/monkey/v3/` (model sheet, pose sheets A/B/C, 20 singles, proof), CANON section
  "Monkey v3 (yellow)" appended. Storybook miniature reference = `monkey/v3/monkey_v3_model_sheet.jpg`.
- D1 (take `s3_d1_sd20b`: throw -> ink-line monkey -> yellow floods in; rubbing + paper-cut switches on the echo).
- D6 (Buddha's palm: plate `design/plates/D6_palm/D6_palm.jpg`, monkey `s3_d6_kling4`, paper-cut switch on the landing
  shows the hand). Depth is the in-code 3-layer parallax + mist for now.
- D7 (take `s3_d7_sd20`; the model's own brush rings kept as a lasting stain; shadow + paper-cut switches).
- F4b, F5, F6a: swarm on the ruled album leaf (`shots/swarm_lib.py`).
- F2: script now takes the car team's v3 plate + v3 pane quad when `media/kf/v3/F2.jpg` or `F2_plate.mp4` exists;
  until then it renders as v2.

**In progress:** D2 (four bows; takes `s3_d2_kling4ff` [E,S,W,N, smooth 24 fps, 1080p] vs `s3_d2_sd20` [E,S,W,N but
steps on twos/threes]; keying `s3_d2_kling4ff` now), then D8 (`s3_d8_kling4`), J3 (`s3_j3_kling4`).

**Next:** D1's last 10 frames start the D2 clip (so the first bow can land on 61.321); swap D6's plate for the
video-model depth plate if it is good; polish swarm (F6a seal placement); final log + report.

**Relay jobs:** all 13 figure clips are back (`media/gen/stage/v3/clips/s3_*.mp4`, sheets `work/stage/v3/takes/`).
Pending: `chaosmonkey/s3_d6pl_h3-fe23e651da` (spec `media/gen/specs/s3_d6pl_h3.json`) and
`chaosmonkey/s3_d6pl_kling4-a44ed461a3` (spec `media/gen/specs/s3_d6pl_kling4.json`): the palm plate animated with
parallax + mist. Collect with `PY tools/gen/gen.py wait <ids>` then `PY tools/stage/takes3.py` (copies to
`media/gen/stage/v3/clips/`). To use one: key it to `work/ink_clips/s3_d6pl` (no stabilise) and write
`work/ink_clips/s3_d6pl/travel.json` ({"src": [...], "dx": [...]}, the near layer's shift); `stage3.Palm` then uses it.

**Decisions:**
- Yellow monkey: sd5 with the old model sheet as ref (keeps our face and hand); no plumes (pompom cap), scarf ends trail.
- Swarm layout = B, a full-frame ruled album leaf intercut with the car, lit like the car glass (options sheet
  `work/review/comp_v3/_swarm_options.jpg`; reasons in §3 below). The new v3 pane quads are used for F2 (pane shot).
  For F4b/F5/F6a the panes are too small at 540p to read grid + labels + threads (§3), and no painted v3 car plates exist yet.
- D1 take b (ink line first, then the wash) over take a (`s3_d1_sd20`, 1080p: the splash gathers into a BLACK monkey
  that then turns yellow); a is kept as the alternate (`STAGE_D1_TAKE=s3_d1_sd20`, needs its SRC times measured).
- No chops are measured inside any stage shot (`timing.hits('chop')` is empty there): medium switches sit on the
  strongest measured drum hits / echo words, listed in each script's SWITCH.

**Open questions for the lead:** (1) OK that F4b/F5/F6a leave the car (leaf intercut)? `swarm_lib.Leaf` can be laid
into a pane quad if you want a car version once painted v3 car plates exist. (2) F2 needs the BED+CAR plate.
(3) F5: eight copies in 1.8 s go home one per HALF beat (not one per beat).

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

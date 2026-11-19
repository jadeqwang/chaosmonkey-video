# LOG v4 SWARM team (F4+F5+F6a one shot, F2 shapeshift window)

Team lead: Claude (Opus 5.5). Brief: REVISION_V4 §3.2, §5 F. Ceiling $180. Spend tag prefix `sw4_`.
Project total at start: $361.81. Scratch: `work/swarm/`. Assets: `media/swarm4/`. Engine: `tools/swarm4/`.
v3 backups: `media/comp/_v3/{F2,F4b,F5,F6a}.mp4`, `shots/_v3/{F2,F4b,F5,F6a,swarm_lib}.py`.

## Timing (song clock, from analysis/timing.json; s = frame within the 176-frame shot, song frame = 2706 + s)
Beats: 112.814 (s1.5) 113.247 (s12.0) 113.688 (s22.5) 114.135 (s33.2) 114.567 (s43.6) 115.002 (s54.0)
115.445 (s64.7) 115.882 (s75.2) 116.320 (s85.7) 116.736 (s95.7) 117.200 (s106.8) 117.628 (s117.1) 118.068 (s127.6)
118.500 (s138.0) 118.938 (s148.5) 119.374 (s159.0) 119.812 (s169.5); shot ends 120.083 (s176).
Lines: 千百个我 同时在这里 112.76-114.32 (s0-37.4); 每一个都是我 每一个都算 114.32-116.125 (s37.4-80.7);
说完这句话 各自消散 116.2-118.0 (s82.8-126); 身外身法 谁是真身 118.0-119.73 (s126-167.5) (+ echo 119.54-120.2).
Sound cues (REVISION_V3 §11): abacus 113.688 114.135 114.567 115.002 115.445 115.882; seals 116.320 116.736 117.200
117.628; F6a 真 seals (v3) 119.12 and 119.812.
F3 hands over hairs blown toward frame right (little Jade's palm at right): the swarm shot receives them entering from
frame left/lower left.

## Plan (lead's concept §3.2, made concrete)
- One three.js scene (`tools/swarm4/`), rendered headless per frame, deterministic, any resolution.
- Explicit spawn tree: 1 -> 8 -> 64 -> 512 -> 2048 leaves (2633 monkeys). Leaf positions are chosen by projecting the
  亮相 silhouette from the apex camera onto the terrain (anamorphic: only from the apex do the lanterns draw him);
  the hierarchy is a recursive spatial clustering of those points, each parent standing on the highest ground of its
  cluster. Each of the 8 branches is one department/job (读 写 算 运 战 扫 望 磨).
- Waves down the tree: on each beat the root acts, then each generation 2 frames later, with a light bead running
  down every cinnabar thread from parent to child.
- Monkeys: costume-B sprites (gpt-image-2 sheets, cut out) with 2 beat poses per job; hero monkeys near camera are
  video-model takes (Kling v4) as RGBA billboard sequences.
- Terrain: procedural 青绿 night range with ink/gold shader + painted projection plates (phase 2); mist planes with
  h3-animated mist textures.
- Candidates: at least 3 full renders differing in camera blocking / look / enlivening (pure 3D, 3D + v2v model).

## CHECKPOINT 1 (start)
- done: read brief, timings, v3 F shots; backups made.
- in progress (launched 3 subagents): ENGINE (spec work/swarm/ENGINE_SPEC.md -> tools/swarm4/), ASSETS (sonnet:
  concepts media/swarm4/concept/, sprites media/swarm4/sprites/, hero Kling takes media/swarm4/clips/), F2 (sonnet:
  shots/F2.py -> media/comp/F2.mp4). Each appends its own `## <NAME> (agent)` section below.
- finding: runwayml/aleph-2 (v2v, $0.336/s) takes a data-URI source video plus up to 5 timed guidance images: the
  candidate "enliven" path = 3D render as source + painted keyframes (gpt-image-2 over render frames) as guidance.
  To test once the engine renders.
- pending relay jobs: see agents' sections.
- deliverable split: the cut table splits F4 = F4a + F4b today; v4 delivers media/comp/F4.mp4 (83, whole slot),
  F5.mp4 (43), F6a.mp4 (50) and F4F5F6a.mp4 (176). CUT must change SPLICES: F4 -> ["F4"], F6 stays F6a + F6b (50+33).

## ASSETS (agent)
- Concepts (gpt-image-2 2048x1152, ref = costume-B sheet, $0.2 each) in media/swarm4/concept/. t1: c1 strong (big monkey blowing, small spawn plucking, red threads link them; looks like a painted film frame). c2_t1 weak: monkeys giant in the foreground, not hundreds. c3 strong: lantern-dotted giant liangxiang figure over night range, reads instantly (but the figure is drawn almost as a solid painted figure, lanterns only outline it; real build will be points). c4 ok: hair gale + red threads good, monkey small and calm, palm open. c5_t1 weak: lanterns on poles, thread held in hands, ledges flat.
- t2 retakes: c2_t2 much better (hundreds of small monkeys, jobs readable, bridges/scaffolds, red threads fan up to one point at top centre). c5_t2 better (empty dark range, two lit ledges, thread between raised hands; mirror pose slightly stiff, but identical).

## F2 (agent)
Output `media/comp/F2.mp4` (53 frames, 960x540, 24 fps, no audio; song frames 2612-2664). Script `shots/F2.py` (v3 structure kept; v3 copy `shots/_v3/F2.py`, v3 render `media/comp/_v3/F2.mp4`). Render: `PY -m tools.ink.run shots/F2.py --t0 108.8333 --t1 111.02 --size 960x540 --out media/comp/F2.mp4`. Review: `work/review/comp_v4/F2.jpg` (16 frames), `work/review/comp_v4/F2_forms.jpg` (each form at pane size).

**Plate**: no v4 F2 guide/plate and no "READY: car26" line in `LOG_v4_sets.md` at the time of writing -> v3 acted plate `media/kf/v3/F2_plate.mp4`, pane `F2_pane.json`, hand matte `F2_fg_matte.mp4` kept. The lyric INS line is unchanged.

**Chapter source** (verified): 西游记 第六回 on Chinese Wikisource, https://zh.wikisource.org/zh-hans/西遊記/第006回 . Order and quotes: 摇身一变，变作个麻雀儿，飞在树梢头钉住 / 变作一只大鹚老，冲天而去 / 变作一个鱼儿，淬入水内 / 变作一条水蛇，游近岸，钻入草中 / 变做一只花鸨，木木樗樗的，立在蓼汀之上 / (the temple) 只有尾巴不好收拾，竖在后面，变做一根旗竿。真君赶到崖下，不见打倒的鸨鸟，只有一间小庙。…见旗竿立在后面，笑道：“是这猢狲了”. (The bustard is skipped: 4 animals + temple used.)

**Forms and cues** (frame = song frame 2612 + n; t = 108.8333 + n/24; hard cuts, each form starts with its own lamp sweep):
| cue t | file frame n | form |
|---|---|---|
| 108.84 | 1 (frame 0 is the road only) | the jointed monkey (v3 pose), lamp fades in over ~6 frames |
| 109.30 | 12 | 麻雀 sparrow on a twig |
| 109.74 | 22 | 大鹚老 cormorant in flight |
| 110.175 | 33 | 鱼 fish over water lines |
| 110.38 | 38 | 水蛇 water snake |
| 110.80 | 48, held to the end | 土地庙 temple, tail as flagpole behind it |
Forms: gpt-image-2, white ground, style refs puppet_parts_colour.jpg + puppet_heads_swap.jpg, `work/f2/forms/*.png` (tags `sw4_F2_sparrow|cormorant|fish|snake|temple`, one take each, 5 calls). Every animal carries the ringed red heart-shaped face mask with gold eye and the monkey's capped headband stripe; the temple has a monkey-face plaque and the furry, gold-ringed tail as the flagpole. Cut by transmittance (like the rig's parts), composited through Pane + `sweep` (radius_k 1.25, deeper sodium amber `AMBER` instead of cream).

**Colour fix**: the plate is graded by a per-channel 9-point percentile match of its cabin (outside the glass) to F1+F3a (`_cabin_lut`); shadow p10 RGB now ~(44,40,38) vs F3a (46,37,40), v3 was (43,42,47). Before and between sweeps the glass shows a dark night highway (`road_local`: warm horizon, two parallax layers of streetlights, far red tail lights) darkened and blended into the glass; sweep 1 rises out of it.

**Spend**: 5 x gpt-image-2 ~ $1.06.

**Still weak**: only 1 frame of pure road before the lamp (the cue is at frame 1; the lamp ramps up instead); streetlights read as glowing dots more than poles; the cormorant looks goose-like and its face mask is small; her pointing hand overlaps the cormorant's beak and the fish's head (matte keeps the hand in front; nothing is hidden); forms are single flat pieces (not jointed, hard cut only); the sweep gap frames show the form as a dark ghost on the road. Not watched at speed; only sheet frames checked.

## CHECKPOINT 2 (lead)
- F2: delivered by the F2 agent (see `## F2 (agent)`); lead looked at work/review/comp_v4/F2.jpg and F2_forms.jpg:
  accepted for now (sparrow, cormorant, fish, water snake, temple with fang doors / round-window eyes / tail flag
  behind; warm cabin, road in the glass). Weak: cormorant reads goose-like; forms are single pieces.
- Concepts c1..c5 looked at (work/swarm/concepts_sheet.jpg): c1, c2_t2, c3, c4, c5_t2 set the look (teal-indigo night,
  green mineral pillars, gold lanterns, red threads). c3's giant lantern 亮相 figure is the reveal to build.
- Plan for candidates: A = pure 3D engine render; B = runwayml/aleph-2 v2v of A guided by painted keyframes
  (gpt-image-2 over A's frames); C = Kling v4 multi-keyframe (first + 3 middle + last) from the same painted keyframes,
  retimed piecewise to the beats; composite typeset seals/slips back where they register.
- pending relay: chaosmonkey/sw4_kmk_concept_t1-69e4307323 (Kling v4 8 s 1080p, the 5 concept frames as keyframes;
  spec media/gen/specs/sw4_kmk_concept_t1.json; collect with gen.py collect) = test of C's method.
- Sprites: 6 gpt-image-2 sheets (media/swarm4/raw/s1-s6.jpg) on flat #00B140; background stayed flat, style held; no white-paper fallback needed. tools/swarm4/cut.py (+key.py: border-median key, despill, un-premultiply edges) -> 23 RGBA sprites + sprites.json (anchor = bbox bottom centre, so broom/staff/table tips can pull the anchor off the feet: sweep_*, spar_B, carry_*). Contact sheet media/swarm4/sprites/contact.jpg: all on-model (costume, mask, cap, scarf; no text). Weak spots: seated_q34 palm points to frame left while face looks right (hand is on his far side, reads as mirrored); sweep/watch poses are frontal rather than facing right; pluck hairs are tiny. liangxiang_big.png + liangxiang_silhouette.png (946x2048, clean filled mask) from a dedicated 1152x2048 gpt-image-2 figure (media/swarm4/raw/lx_big.jpg); the smaller liangxiang_side/q34 sprites are also there.
- Hero stills h1-h3 on green (raw/h?_still.jpg; ground-colour differs slightly per still, so keyer samples border median). Kling v4 1080p 5s jobs sw4_h{1,2,3}_t{1,2} queued ($1.175 each); relay queue says ~25 min.

## CHECKPOINT 3 (lead)
- Kling multi-keyframe test collected: media/gen/sw4_kmk_concept_t1_69e4307323.mp4 (193 f, 1080p), sheets
  work/swarm/kmk/t1_sheet.jpg, t1_trans.jpg. Verdict: the method works (one continuous flight: ledge -> fall back ->
  aerial -> lantern figure -> gale -> two monkeys); weak where keyframes disagree in geography (figure -> gale is a
  dissolve). Next: keyframes with one geography.
- Sprites delivered by ASSETS (media/swarm4/sprites/contact.jpg): on-model, all 8 jobs x 2 poses + spawn poses + 亮相.
- Launched KFLIGHT agent (sonnet): consistent keyframes K0..K6 + 3 Kling 12 s takes -> work/swarm/K/ (candidate C).
- Comp plan for any video-model candidate: retime piecewise to the beats; beat waves added in comp as a radial lantern
  flare from the root's screen point outward (down the tree); seals 讫 / 真 and name slips typeset and tracked.

## KFLIGHT (agent)
Goal: one-geography 7-keyframe set + Kling v4 flight (first K0, middle K1..K5, last K6). Keys: `media/swarm4/K/K0..K6.jpg` (2048x1152, gpt-image-2, takes `sw4_K{n}_t{1,2}.jpg` + `.txt` prompts, prompts also `work/swarm/K/K*.prompt`), sheet `work/swarm/K/keys.jpg`. Each key got the costume-B ref + previous key(s) as refs. Picks: K0 t1 (t2 had an elongated arm), K1 t2 (rows of generations clearly read as a tree; t1 monkeys tiny), K2 t2 (pine/ledge/pillar stayed where K1 had them; t1 moved the pine), K3 t1 (bolder figure, twin pillars + pavilion spur kept), K4 t1 (clear spiral gale), K5 t1 (dense gale into palm), K6 t1 (same camera as K5).
Kling specs: `media/gen/specs/sw4_K_kling_t{1,2,3}.json` (12 s, 1080p, ~$2.82 each). Job ids: see below.
Jobs: chaosmonkey/sw4_K_kling_t1-69cd5b08bc, t2-f54280c505, t3-5f703175b6 (queued).

## ENGINE (agent)
- Built `tools/swarm4/` (README there): headless three.js r170 on the RTX 3090 (`--use-angle=gl` works on this machine; `--use-gl=egl` falls back to SwiftShader; `--gl swiftshader` kept as a flag). Deterministic from (cand JSON, s).
- Speed: init ~5 s (terrain 1280² warped mesh, tree, atlas); 960x540 beauty ~50 ms/frame (176 frames in ~15 s incl. PNG transfer), guide+depth ~57 ms/frame, 1920x1080 ~285 ms/frame, `--mb 4` ~0.6 s/frame.
- Delivered: `work/swarm/cand_A.json`; full render `work/swarm/render/A/f0000-0175.png` (+ `cams.json`); guide pass `work/swarm/render/A_guide/{guide,depth}_*.png`; `media/comp/F4F5F6a_A.mp4` (176 f, no audio); sheets `work/review/comp_v4/swarm_A.jpg`, `swarm_A_guide.jpg`; tree `work/swarm/tree_A.json` (2633 nodes).
- Uses the asset agent's `media/swarm4/sprites/` (sprites.json + liangxiang_silhouette.png, mapped by `assets.pose_map`); clips are scheduled per hero in `assets.clips` (tested with a dummy clip, none real yet); projectors (painted plates by frame or camera) implemented and tested with one of our own renders.
- Lead's mid-job notes applied: steeper apex (≈70°), figure 0.72 of frame height, 62 % of the leaves on the outline (interior lanterns at 0.55), taller pillar field with spires, pine blotches on tops, `--pass guide`, gen-1/2 lookouts pulled toward the root and placed below it (terraces under the ledge), camera higher at s25.
- Weak/open: rock forms are still procedural (rounded "pill" columns, corrugated terracing on some slopes); the ledge close-ups are plain and the root lantern reads as a glow, not a lantern; gen-1 landings at s18-24 are small at distance; the gale is sparse in the dark dive (s100-120); threads read weakly except at s56-62. Painted plates via `projectors` are the intended fix for the rock look.

## CHECKPOINT 4 (lead)
- ENGINE done (see `## ENGINE (agent)`): candidate A rendered, media/comp/F4F5F6a_A.mp4, sheet
  work/review/comp_v4/swarm_A.jpg. Lead verdict: structure/timing right, figure reads at s82, look is CG (pill rocks,
  black end background). A stays as the pure-3D candidate and as layout/motion source.
- Launched HYBRID B agent (sonnet): gpt-image-2 paints A's frames s12/30/58/82/105/128/152 keeping layout -> Kling v4
  12 s multi-keyframe (B-kling) and runwayml/aleph-2 v2v of A guided by the painted keys (B-aleph). work/swarm/B/.
- Running: ASSETS (hero Kling takes), KFLIGHT (candidate C, work/swarm/K/).
- Hero takes (Kling v4 1080p 5 s, 121 f @24, first frame = green still; queue wait ~35 min): all six kept the camera locked and background flat except h3 (Kling added a dark ground shadow; removed by the hue key mode='sat'). Picks: h1_t2 (stronger, more readable hair plume, hairs visible on palm before the blow; t1 plume thinner), h2_t2 (clear look-up to frame right at the end; t1 dropped a visible dark hair bead into the palm but never really looked up; t2's arriving speck is a tiny white dot), h3_t2 (deeper crouch, big scarf flare, ends plucking with hairs visible between fingers; t1 ends with vague hands). Keyed with tools/swarm4/clipkey.py -> media/swarm4/clips/{h1,h2,h3}/f0000..0120.png + clip.json (shared crop per clip, anchor_px = feet in crop). Strip over dark checked: no green fringe, shadow gone. Raw videos + 15-frame sheets: media/swarm4/raw/vid/.
- Caveats: h1 hair plume is dark ink and thin: nearly invisible on a dark ground (composite over lit mist, or draw hairs in the engine); figures fill 70-90 % of frame height, not 60 % (scale at use); h3 first frames are airborne so the crop reaches the top.
- Spend by this job (sw4_c*, s*, lx_big, h*): about $10.5 (sheets/concepts/stills $0.2 each x 16 = 3.2; 6 videos x 1.175 = 7.05). Other agents also use the sw4_ prefix.

## HYBRID B (agent)
Work dir `work/swarm/B/` (hires renders `hires/`, keys `keys/`, prompts `prompts/`). Keys sheet `work/swarm/B/keys.jpg`; all 14 takes `keys_all.jpg`; 50 % overlays on the guide `ov_sheet.jpg` (order: s12 t1,t2, s30 t1,t2, s58 ..., s152).
- Keys: gpt-image-2 2048x1152, refs = A beauty (hires), A guide (hires), concept look (c1_t1 / c2_t2 / c3_t1 / c5_t2), costume v3b_ALT. Tags `sw4_B_00xx_t{1,2}`, 14 calls ~$3.3.
- Picks by overlay fidelity, then beauty: s12 t2 (t1 gave a doubled monkey offset from the guide), s30 t2 (pillars equal; t2 more monkeys), s58 t1, s82 t1 (figure outline aligns with the guide mask; t2 figure is shifted right with a different pose; lanterns stay separate points in both), s105 t1, s128 t2 (same plateau as s152 t2: geography continuity), s152 t2 (t1 shows a ghost double offset from the guide).
- Jobs: Kling `chaosmonkey/sw4_B_kling_t1-9eeca8f43c`, `sw4_B_kling_t2-573ccce38d` (12 s 1080p, first s12, middle s30 s58 s82 s105 s128, last s152; specs `media/gen/specs/sw4_B_kling_t{1,2}.json`). Aleph `chaosmonkey/sw4_B_aleph_t1-7bbfab0a7b`, `sw4_B_aleph_t2-f8726077ad` (video = media/comp/F4F5F6a_A.mp4 data URI, job body 13.7 MB < 24 MB; keyframes s12 s58 s82 s105 s152 at s/24 s, 1280x720). Pending.
RESULTS: takes `media/gen/sw4_K_kling_t{1,2,3}_{69cd5b08bc,f54280c505,5f703175b6}.mp4` (1920x1080, 24 fps, 289 frames). Sheets in `work/swarm/K/`: `sheet16_t*.jpg`, `strip_t*.jpg` (6 transitions per take, stride 2 up to 24 cols, stride 3-5 for longer ones), `keys.jpg`, frame matching `idx.json`/`idx.py`.
Keyframe frame index (best pixel match; err ~3-9/255, i.e. keyframes are hit almost exactly) K0..K6: t1 8,51,79,188,224,260,284; t2 1,51,95,159,233,263,284; t3 0,43,99,164,231,260,287.
Ranking: t2 > t1 > t3. All three are one continuous camera move (fall back off ledge, rise, apex, descend to ledge), no dissolves between keys; geography (pine, ledge, notched pillar) holds. t2: cleanest, lantern figure legible ~159-200 and fades out, gale pours into palm 250-263, no artifacts. t1: good but a blurry golden smear lower right ~f96 and figure is dimmer/shorter-held (173-192). t3: crispest figure (154-173) but a stray yellow limb/object enters top right ~f269-272 and the gale is weaker. Weak in all: the lantern figure is thinner and dimmer than in K3, and the K3 apex is only held ~20-40 frames.
Spend: 14 gpt-image-2 ~ $3.03, 3 Kling ~ $8.46, total ~ $11.5.

## CHECKPOINT 5 (lead)
- ASSETS done (sprites, clips h1-h3, concepts). KFLIGHT done: best take media/gen/sw4_K_kling_t2_f54280c505.mp4
  (lead looked at work/swarm/K/sheet16_t2.jpg: continuous flight, on-model, strong; weak: the giant figure is a
  translucent outline in the sky rather than lanterns on the terraces; no beat motion; threads faint).
- Submitted F6a extension from t2's last frame: chaosmonkey/sw4_C_ext_t1-ec7985869b, sw4_C_ext_t2-7ecb120fad
  (specs media/gen/specs/sw4_C_ext_t*.json; first frame work/swarm/C/t2_last.jpg).
- Launched VCOMP agent (sonnet): tools/swarm4/vcomp.py (retime map, beat-wave lantern flare, regions dark on seal
  beats with 讫 flashes, tracked 真 seals and name slips) -> candidate C = media/comp/F4F5F6a_C.mp4.
- Running: HYBRID B.

### KFLIGHT round 2
New keys (media/swarm4/K/): K3b (t2: bigger lantern-point figure ~80% frame height; t1 smaller), K1b (t1: eight landed + third generation mid-air landing, glowing threads), K4b (second prompt round `K4b2`, t1: first round copied K4's zoomed view and lost the figure; K4b2 keeps K3b framing, outer parts dark, core lit, vortex of hairs). Compare sheets work/swarm/K/k3b_cmp.jpg k1b_cmp.jpg k4b_cmp.jpg k4b2_cmp.jpg.
Specs: media/gen/specs/sw4_K_kling_r2t{1,2}.json (K0,K1b,K1,K2,K3b,K4b,K5,K6). Jobs: chaosmonkey/sw4_K_kling_r2t1-cc27e6c157, r2t2-6356e9ec5e.
- RESULTS. Kling: `media/gen/sw4_B_kling_t1_9eeca8f43c.mp4`, `sw4_B_kling_t2_573ccce38d.mp4` (1920x1080, 289 f @24 = 12 s). Sheets `work/swarm/B/k{1,2}_sheet.jpg` (16 frames), `k{1,2}_apex.jpg`, `k{1,2}_spawn.jpg`; frames `work/swarm/B/k{1,2}/f%04d.png` (480x270, 1-based).
- Keyframe reached (0-based frame of closest match, then L1 distance): t1 s12 f0, s30 f44, s58 f71, s82 f148, s105 f211, s128 f260, s152 f274 (the last key is reached ~15 f before the end, then held). t2 s12 f1, s30 f47, s58 f73, s82 f156, s105 f203, s128 f255, s152 f284. A-time equivalent is far from linear: Kling spends f0-70 on the spawn/fall (A s0-58), then holds the lantern figure f130-200 (A has it only s75-86).
- ALEPH: all 3 submissions (t1, t2, then a resubmit of t1 `sw4_B_aleph_t1-f937a92f8c`) failed with `7005: Unified billing service unavailable` (relay/Cloudflare unified billing, not a body-size issue: body 13.7 MB). Skipped; probably not billed.
- Spend: 14 gpt-image-2 ~$3.34 + 2 Kling $5.64 = ~$9.0.

## CHECKPOINT 6 (lead)
- HYBRID B done: Kling t2 media/gen/sw4_B_kling_t2_573ccce38d.mp4 = candidate B source (painted over A's layout;
  lantern figure made of points on the ground: the best figure so far; the s58->s82 stretch is a fast smeared zoom).
  Aleph failed 3x with `7005: Unified billing service unavailable` (unbilled); specs kept for a retry.
- Submitted B's F6a extension: chaosmonkey/sw4_B_ext_t1-10a8e78e9f, sw4_B_ext_t2-ef7ae00554 (first frame
  work/swarm/B/t2_last.jpg).
- KFLIGHT round 2 running (K1b three generations + K3b lantern-point figure in C's geography; 2 Kling takes).
- VCOMP running (candidate C comp).
- Spend so far (sum of sw4_ tags incl. pending): $47.66 of $180.

## CHECKPOINT 7 (lead, resumed after usage-limit stop)
- News from coordinator: SETS done (car26 v4 guides media/layout/car26/v4_F2*; v3 F2 plate passed the set check:
  F2 plate stays). STAGE done (costume-B singles design/characters/monkey/v4/singles/; chapter 6 list verified,
  鸨/鹚 simplified forms; F2 shows no typeset names, nothing to change).
- Collected: C ext t1/t2 (media/gen/sw4_C_ext_t{1,2}_*.mp4), KFLIGHT round 2 Kling r2t1/r2t2
  (media/gen/sw4_K_kling_r2t{1,2}_*.mp4). B ext t1/t2 still running (sw4_B_ext_t*-10a8e78e9f / -ef7ae00554).
- VCOMP agent was stopped by the usage limit mid-job: tools/swarm4/vcomp.py exists, configs work/swarm/C/comp_C*.json,
  test images in work/swarm/C/, no final comp yet, no VCOMP log section. KFLIGHT round-2 agent likewise stopped after
  the Kling takes (ranking not written).
- next: lead judges r2 takes vs t2; relaunch a Sonnet VCOMP to finish candidate C (and B); 3 candidates, ranked by a
  fresh agent; deliver.

## CHECKPOINT 8 (lead)
- done: F2 (media/comp/F2.mp4, shots/F2.py; accepted on sheet). Candidate A (pure 3D, media/comp/F4F5F6a_A.mp4).
  Sources for B, C, D collected. Lead picks: KFLIGHT round 2 take 1 (media/gen/sw4_K_kling_r2t1_cc27e6c157.mp4)
  = C's source (three generations read as rows on the terraces, lantern figure, gale into palm; sheet
  work/swarm/K/r2_sheet_t1.jpg); r2t2 weaker (blurred gen-1 landing). F6a extension = C ext t2
  (media/gen/sw4_C_ext_t2_7ecb120fad.mp4; t1's red glow between the palms reads as fire). r2t1's last frame matches
  the ext's first (work/swarm/C/last_cmp.jpg).
- in progress: VCOMP agent (resumed; notes file work/swarm/C/VCOMP_NOTES.md) composites B, C, D:
  B = sw4_B_kling_t2 + B ext; C = K r2t1 + C ext t2; D = K r1 t2 + C ext t2; outputs media/comp/F4F5F6a_{B,C,D}.mp4,
  sheets work/review/comp_v4/swarm_{B,C,D}.jpg.
- pending relay: chaosmonkey/sw4_B_ext_t1-10a8e78e9f, sw4_B_ext_t2-ef7ae00554 (specs media/gen/specs/sw4_B_ext_t*.json,
  output media/gen/sw4_B_ext_t*_<id>.mp4 on collect).
- next: fresh-eyed ranking agent on the 16-frame sheets vs the director's words (notes file
  work/swarm/RANK_NOTES.md); then the pick split into media/comp/F4.mp4 (s0-82), F5.mp4 (s83-125), F6a.mp4 (s126-175)
  and media/comp/F4F5F6a.mp4; shots/F4F5F6a.py wrapper so 1080p is a re-render; SOUND times.
- Subagent notes files: F2 -> log `## F2 (agent)`; ASSETS/ENGINE/KFLIGHT/HYBRID B -> their log sections (all done);
  VCOMP -> work/swarm/C/VCOMP_NOTES.md.

## CHECKPOINT 9 (lead)
- VCOMP active (notes work/swarm/C/VCOMP_NOTES.md, "Lead notes (update 4)" = my fixes from the C/D sheets: whip
  through r2t1 blur, bigger slips and 真 seals, D figure hold s72-88, crisp 讫 flashes). C and D first renders exist
  (media/comp/F4F5F6a_{C,D}.mp4); fixes being applied.
- B ext t1/t2 stuck "running" 97 min; resubmitted chaosmonkey/sw4_B_ext_t3-106bf31cfd (spec media/gen/specs/sw4_B_ext_t3.json).
- Coordinator: F6b is now the mirror shot; our ending hands no hair to F6b.
- next: when VCOMP reports, ranking agent (notes work/swarm/RANK_NOTES.md), then split + deliver.
- Director rule (image route): further gpt-image work goes through Codex (docs/TEAMS_V4.md "Image generation route",
  flock /tmp/chaosmonkey-codex.lock, no sandbox bypass); Cloudflare gpt-image-2 only where Codex cannot. All SWARM
  images so far (concepts, sprites, hero stills, F2 forms, K/B keyframes: ~50 calls) went via Cloudflare gpt-image-2,
  before this rule. No image generation is planned in the remaining work (VCOMP is comp-only); video stays on Cloudflare.

## VCOMP (agent)
Tool `tools/swarm4/vcomp.py <config.json> [--w 960 --h 540] [--stage base] [--no-encode]`; notes + recipes in `work/swarm/C/VCOMP_NOTES.md`; configs `work/swarm/C/comp_{C,D}.json` generated by `parts_{C,D}.py` (+ `gen_cfg2.py`, shared overlay defaults in `gen_cfg.py`).
Stages: retime (PCHIP monotone map on a virtual source axis; DIS flow at 480x270 interpolates fractional frames, fb-consistency falls back to blend) -> overlays (all authored in 960x540 units, tracking/blob detection on a 960x540 copy, so `--w 1920 --h 1080` is a pure re-render from the 1080p sources) -> mp4 + sheet + strips.
Outputs: `media/comp/F4F5F6a_{C,D}.mp4` (176 f, 24 fps, 960x540, no audio), `work/review/comp_v4/swarm_{C,D}.jpg` (+ `_strip_a.jpg` s0-48, `_strip_b.jpg` s70-130, every 2nd frame). B: pending (ext jobs), recipe `parts_B.py`.
Extension pick: ext t2 (t1 grows glowing red orbs between the palms). Speed: 1x freezes, 2x gives arc + palms opening: used 2x (ext idx 0..94 over s130-175; sources joined at virtual v=288, A last frame == ext frame 0, mean abs diff ~3-4/255, no visible seam).
Maps (output s : source frame, A then ext on virtual axis, ext = 288 + idx):
- C (KFLIGHT r2t1, keys K0 1, K1b 51, K1 54, K2 104, K3b 207, K4b 222, K5 268, K6 285): 0:1 14:25 28:48 33:55 36:75 56:116 62:152 72:185 88:210 104:222 120:268 128:285 130:288 152:334 175:382. s36-56 and s56-62 are whips through the model's blurry morph / fog dive (speed up to ~6 src f per out f).
- D (round-1 t2): 0:1 28:51 55:95 72:156 86:190 96:206 102:233 120:263 128:284 130:288 152:334 175:382 (figure fades in s66-76, fully lit s76-86, goes dark by sector).
Overlay events (s = frame in the shot, t = 112.75 + s/24), identical in C and D:
- Beat wave (lantern flare ring from the root, 8 frames, gain 1.6 + bloom): beats s12.0 22.5 33.2 43.6 54.0 64.7 75.2 = t 113.250 113.688 114.133 114.567 115.000 115.446 115.883 (ring runs s..s+8).
- Dark sectors (4 angular sectors around the root, outer edge inward over 6 frames, lanterns to 15 %, +10 % dim; released s122-128): s85.7 (up-right, t116.321), s95.7 (lower-left, t116.737), s106.8 (up-left, t117.200), s117.1 (lower-right, t117.629). 讫 flashes (12-15 px typeset 白文 seal, 4 frames each, at lantern blobs the front just passed, max 9 per frame): C frames s87-92 (~40), s99-102 (~23), s119-123 (~14); D s87-92, s99-102, s113, s119-123.
- 真 seals (46 px on the lit rock, 3-frame press from 115 % / 0 opacity, LK-tracked): left pressed s153.9 (frames 154-156, t119.162), right s169.5 (frames 170-172, t119.812).
- Name slips (tall paper strip, ~30x56 px, glyph 22 px, 6-frame fades, tracked): C 读 s37-55, 写 s38-56, 磨 s37-55, 运 s38-56; D 读/写 s42-60, 磨/运 s46-62. Chosen where the monkey is clearly reading (scroll), writing at a desk, at a millstone/pot with peaches, carrying baskets on a pole.
Weak: model morph blur in C at s30-38 (partly whipped) and the fog dive; D figure is only fully lit for ~10 frames; 讫 seals are 12-px blocks (glyph barely legible by design); 真 白文 seals read as red blocks with a faint glyph; ring flare also lights paper scrolls/monkey costume edges; B not built yet (no readable jobs in its take, so no slips there).

## CHECKPOINT 10 (lead)
- VCOMP done for C and D (media/comp/F4F5F6a_{C,D}.mp4, sheets work/review/comp_v4/swarm_{C,D}.jpg; maps and overlay
  event times in `## VCOMP (agent)` and work/swarm/C/VCOMP_NOTES.md). C at 1080p rendered unencoded in
  work/swarm/C/frames_1920x1080 (re-render proven). B waits on its ext (waiters log work/swarm/C/waitB*.log; finish
  with `PY work/swarm/C/parts_B.py <ext.mp4>` then `PY tools/swarm4/vcomp.py work/swarm/C/comp_B.json`).
- Lead view of C (frames 90/93/175 at full size, work/swarm/C/lead_zoom.jpg): 讫 flashes read as small red seal
  squares on the figure (acceptable at distance); 真 seals sit together on the lit rock between the monkeys.
- In progress: ranking agent (sonnet, fresh, not told the lead's favourite), notes work/swarm/RANK_NOTES.md,
  sheets work/swarm/rank/.

## CHECKPOINT 11 (lead)
- Ranking (fresh Sonnet agent, not told the lead's favourite; work/swarm/RANK_NOTES.md, sheets work/swarm/rank/):
  D 8 > C 7 > A 3 overall. D: cleanest camera, generations visible, giant lantern figure, legible hair gale, mirror
  pair. C: spawn smears s14-18, blur s34, dark dead frame ~s110. A: CG look, "would not clear the bar". B not built
  (ext stuck). Lead agrees: **pick D**.
- In progress (VCOMP, resumed): D fixes (no empty beat s60-70; twin appears from an ink puff + last hair instead of
  a ghosted morph; legible 真 seals 60 px one beside each monkey; thread contrast), then deliver
  media/comp/F4F5F6a.mp4 + F4.mp4 (83) F5.mp4 (43) F6a.mp4 (50), shots/F4F5F6a.py, sheet
  work/review/comp_v4/F4F5F6a.jpg.

### VCOMP final: D is the delivered swarm shot (agent)
Delivered: `media/comp/F4F5F6a.mp4` (= `F4F5F6a_D.mp4`, 176 f), `F4.mp4` (s0-82, 83 f), `F5.mp4` (s83-125, 43 f), `F6a.mp4` (s126-175, 50 f); all 960x540, 24 fps, no audio (ffprobe checked). Wrapper `shots/F4F5F6a.py` (`--master` adds the 1920x1080 re-render). Sheet `work/review/comp_v4/F4F5F6a.jpg` + `F4F5F6a_strip_a.jpg` (s0-48) / `_strip_b.jpg` (s70-130). Config `work/swarm/C/comp_D.json` (from `parts_D.py`).
Final D map (s : round-1 t2 frame; ext = 288+n): 0:1 28:51 55:95 59:120 62:146 66:158 86:195 92:203 96:210 102:233 120:262 123:266 125:268 127:277 129:285 130:288 152:334 175:382. Whip s55-62 (terraces -> wide range), figure formed by s66, held lit to s86; twin morph (src 268-277) raced into ~2 frames (s125-127).
Event times (t = 112.75 + s/24):
- Beat-wave flares: s12.0 22.5 33.2 43.6 54.0 64.7 75.2 (t 113.250 113.688 114.133 114.567 115.000 115.446 115.883), each ring runs 8 frames.
- Sector darkening (6 frames, lanterns to 15 %): s85.7 t116.321, s95.7 t116.737, s106.8 t117.200, s117.1 t117.629 (protected around the monkeys, released s122-128).
- 讫 flashes (11-13 px, 4 frames each, only where the sector is dark): s87-92 (about 36 seals), s101-102 (12), s119 (3), s122 (5).
- Hair streak into the twin spot: s120.5-125 (thin dark curve from upper right); twin ink puff: s125-133 at ref (420,290) (dense s125-128, thinning to nothing by s133, t 117.958-118.292); no semi-transparent double body is visible (checked s121-132 on a 12-frame sheet; the twin shows through speckled ink at s126-129 while the puff thins).
- 真 seals (60 px 白文, SEALF font, on the lit rock, press 3 frames from 115 %/0 opacity with a warm glow ~7 frames): left pressed s153.9 (frames 154-156, t119.162), right s169.5 (frames 170-172, t119.812). 白文 tested against 朱文 on a zoom crop: 白文 with wear 0.05 is the legible one.
- Name slips (tall strips ~30x56 px, 22 px glyph, 6-frame fades): 读 s42-58, 写 s42-58, 磨 s46-59, 运 s46-59.
- Thin red threads: +50 % gain on thin red pixels s38-90 (no artefacts seen on the sheets).
B: ext jobs never landed in time; waiters stopped, B not built (recipe `work/swarm/C/parts_B.py`).

## DONE (lead)
Delivered (960x540, 24 fps, no audio, counts checked with ffprobe):
- media/comp/F4F5F6a.mp4 (176 f, candidate D) and its split media/comp/F4.mp4 (s0-82, 83 f), F5.mp4 (s83-125, 43 f),
  F6a.mp4 (s126-175, 50 f). CUT: change SPLICES so F4 = ["F4"] (no F4a/F4b); F6 stays F6a + F6b (50 + 33).
  Wrapper shots/F4F5F6a.py (runs tools/swarm4/vcomp.py work/swarm/C/comp_D.json; --master = 1920x1080 from the
  1080p sources). Sheet work/review/comp_v4/F4F5F6a.jpg + strips.
- media/comp/F2.mp4 (53 f), shots/F2.py.
Method of D: painted keyframes in one geography (gpt-image-2, media/swarm4/K/) -> Kling v4 multi-keyframe 12 s 1080p
(media/gen/sw4_K_kling_t2_f54280c505.mp4) + Kling extension from its last frame for F6a
(media/gen/sw4_C_ext_t2_7ecb120fad.mp4) -> vcomp: piecewise retime to the beats, lantern beat waves, sectors dark on the
seal beats with typeset 讫 flashes, ink puff for the twin, tracked typeset 真 seals and name slips.
Other candidates kept: A (pure 3D engine, media/comp/F4F5F6a_A.mp4, tools/swarm4/), C (media/comp/F4F5F6a_C.mp4).
B not built (extension jobs stuck: chaosmonkey/sw4_B_ext_t1-10a8e78e9f, t2-ef7ae00554, t3-106bf31cfd).
SOUND times (song clock): beat-wave lantern flares 113.250 113.688 114.133 114.567 115.000 115.446 115.883 (= the
v3 abacus cues, unchanged); sectors go dark / 讫 seals 116.321 116.737 117.200 117.629 (= v3 seal cues); twin ink
puff 117.958-118.292 (s125-133, hair streak from 117.77); 真 seals pressed 119.162 (left) and 119.812 (right; v3
had 119.12 / 119.812).
Spend: $48.84 (sum of sw4_ tags, list-price estimates, incl. the stuck B ext jobs) of $180.

# D-FLIGHT (new assignment from the coordinator: D4 -> D5 -> D6 as one painted Kling flight, budget $60)
Brief: coordinator message (in work/dflight/BRIEF.md), REVISION_V4 §3.1. Do NOT overwrite media/comp/D4/D5/D6.mp4;
deliver media/comp/_cand/DFLIGHT_<name>.mp4 (204 f) + split D4 (33) D5 (101) D6 (70), sheets
work/review/comp_v4/DFLIGHT_<name>.jpg + frontier strip. Images via Codex first (docs/TEAMS_V4.md); video via relay.
Spend tag prefix `sw4_df_`.
## D-FLIGHT timing (s = frame in the 204-frame shot, song frame 1630 + s, t = 67.917 + s/24)
Words: 一 67.91 (s0) 通 68.09 (s4.2) 百 68.53 (s14.7) 通 68.77 (s20.5); D5 from s33 (69.292): One 69.29 whisper 69.61
(s40.3) and 70.555 the 70.75 hundred 70.97 (s73.3) come 71.39 along 71.71 (s91); drum break 71.925 (s96.2);
D6 from s134 (73.5); landing kick 75.025 (s170.6); shot ends 76.417 (s204).
Beats (s): 0.6 11.2 21.8 32.3 42.9 53.5 64.2 74.7 85.3 96.2 106.5 117.3 128.1 138.5 149.2 159.9 170.6 181.3 192.1 202.9.
## D-FLIGHT plan
- 7 painted keyframes in one geography, each made with the previous as reference (Codex image route):
  KD0 macro carved face, mist touches the (blank-panel) centre; KD1 cliff with lit carvings + gold threads; KD2 thread
  arcs across a gorge to the next peak; KD3 high: lit country / frontier / dark country at dusk; KD4 whole range alight;
  KD5 above the cloud sea: five lit pillars = the Buddha's hand (4 tall + 1 short thumb apart); KD6 same, the monkey
  landed in 亮相 on the middle peak with a burst of light. Legible characters only typeset: the macro panel is painted
  blank and typeset columns are planar-tracked onto it in comp until < 14 px per glyph.
- Kling v4 1080p 12 s multi-keyframe, 3+ takes (2 keyframe sets / prompt variants) -> comp: retime to the beats,
  typeset carving + ember + component jumps + threads layer, frontier layer if needed, inscription 一窍通时/百窍通 +
  seal as in the current comp, landing flash on 75.025.
- Blind ranking vs WORLD r2 (media/comp/D4+D5+D6).
## D-FLIGHT CHECKPOINT 1
- done: brief read, timing above. in progress: keyframe agent (notes work/dflight/KEYS_NOTES.md). pending relay: none.
## D-FLIGHT CHECKPOINT 2
- in progress: KEYS agent (sonnet; notes work/dflight/KEYS_NOTES.md; picks -> work/dflight/keys/KD0..KD6.jpg; stops
  before video), COMP agent (sonnet; notes work/dflight/COMP_NOTES.md; tools/dflight/dcomp.py tested on a stand-in).
- next: lead reviews keys sheet -> Kling v4 12 s 1080p takes (specs media/gen/specs/sw4_df_*.json written before
  submit) -> comps -> blind ranking vs WORLD r2.
## D-FLIGHT CHECKPOINT 3
- COMP tool done on a stand-in: tools/dflight/dcomp.py (+ standin.py), notes/README work/dflight/COMP_NOTES.md.
  Typeset incised carving panel tracked by homography, ember on 通 at s4, IDS-chain jumps with snapping gold threads
  (s15-51), inscription as WORLD's comps (一通百通 s0-32; 一窍通时/百窍通 + 悟空 seal s33-133; none in D6), landing
  bloom s170, optional frontier grade layer, cut_to_D7 check. Needs the real flight to tune (panel corners per key).
- KEYS agent still painting.
## D-FLIGHT CHECKPOINT 4
- KEYS done (all 14 images via Codex, $0 Cloudflare; picks work/dflight/keys/KD0..KD6.jpg, sheet
  work/dflight/keys_sheet.jpg, notes work/dflight/KEYS_NOTES.md). Lead: accepted; KD5 reads as the Buddha's palm
  (4 fingers + angled thumb), dusk dark with gold burning; KD1's panel glow is a dot grid (to be covered by the
  typeset layer).
- Submitted Kling v4 1080p (prompts work/dflight/kling/t*_prompt.txt, specs media/gen/specs/sw4_df_kling_t*.json):
  t1 12 s crane = chaosmonkey/sw4_df_kling_t1-9db39d17a6; t2 12 s drone = sw4_df_kling_t2-f6c7c85c50;
  t3 10 s crane = sw4_df_kling_t3-2e6dc95885. Outputs land as media/gen/sw4_df_kling_t*_<id>.mp4 on collect.
- next: sheets + keyframe indices per take, comps with tools/dflight/dcomp.py, blind ranking vs WORLD r2.
## D-FLIGHT CHECKPOINT 5
- Kling takes collected: media/gen/sw4_df_kling_t1_9db39d17a6.mp4, t2_f6c7c85c50.mp4, t3_2e6dc95885.mp4; sheets
  work/dflight/kling/sheet_t*.jpg. Lead: all three are continuous flights panel -> gorge arc -> frontier -> range
  alight -> through cloud (brief whiteout) -> five-pillar hand -> monkey lands on the middle finger. t1/t2 keep the
  panel blank early (good for the typeset layer); t3 draws its own glow constellation on the panel.
- In progress: COMP agent (resumed) builds candidates t1, t2, t3 -> media/comp/_cand/DFLIGHT_t*.mp4 (+ splits,
  sheets, strips, cut_to_D7). Retime targets: KD0 s0, KD1 s33, KD2 ~s55, KD3 ~s75, KD4 ~s105, cloud ~s124-134,
  KD5 ~s142, touch-down s170 (75.025), hold to s203.
- next: blind ranking (fresh agent, in motion if possible) vs WORLD r2 (media/comp/D4+D5+D6).
- Spend so far on D-FLIGHT: Kling 2.82 + 2.82 + 2.35 = $7.99; images $0 (Codex).
## D-FLIGHT CHECKPOINT 6
- Comps done: media/comp/_cand/DFLIGHT_t{1,2,3}.mp4 + _D4/_D5/_D6 splits; sheets work/review/comp_v4/DFLIGHT_t*.jpg,
  dense strips DFLIGHT_t*_dense.jpg; configs work/dflight/dcomp_t*.json; maps and event times in
  work/dflight/COMP_NOTES.md. Lead looked at DFLIGHT_t1.jpg: strong (typeset incised panel, ember, arcs, range alight,
  hand of five pillars, landing).
- Open: last frame is dark-blue night vs D7's pale paper (hard colour cut; lead's decision, maybe intended as the medium
  switch); carving legible only s0-~30; D5 inscription stays over the whiteout to s133.
- In progress: blind ranking (sonnet) of P/Q/R/S = t1/t2/t3/WORLD r2 (key work/dflight/_blind_key.json, notes
  work/dflight/blind/RANK_NOTES.md).
## D-FLIGHT CHECKPOINT 7
- Blind ranking (key work/dflight/_blind_key.json: P=WORLD r2, Q=t2, R=t1, S=t3): S(t3) 9 > Q(t2) 8 > R(t1) 7 >
  P(WORLD r2) 3. t3: warmest gold against the darkest dusk, clearest thumb, best landing flash. Fixes requested (COMP
  agent, t3 only): race the cloud fill s124-130, frontier wave on beats s60-110 if it reads, live hold s170-203
  (push-in + light pulse down the pillars).
## D-FLIGHT DONE
- Pick (blind): t3 = media/comp/_cand/DFLIGHT_t3.mp4 (+ _D4 33 f, _D5 101 f, _D6 70 f), sheet
  work/review/comp_v4/DFLIGHT_t3.jpg, dense strip DFLIGHT_t3_dense.jpg. Alternates t2, t1 beside it. media/comp/D4/D5/D6
  untouched. Re-render: `PY tools/dflight/dcomp.py work/dflight/dcomp_t3.json [--w 1920 --h 1080]`.
- Event times (song clock): ember on 通 68.09 (s4); 辶-family jumps s15-20 (68.54-68.75), 自/又 chains s20-28;
  frontier arcs on beats 70.594 71.029 71.471 71.925 72.356 (s64.2-106.5); cloud whiteout s125-126 (73.13-73.17);
  clearing s130-134 (73.33-73.5 = D5/D6 cut); landing bloom + pulse down the pillars 75.025 (s170); push-in s170-203.
- Weak: hard colour cut night-blue -> D7's pale paper; legible carving only s0-~30; model's dot-grid panel glow s27-54;
  frontier layer marginal (a few extra arcs/streaks, e.g. s81, s95); before the whiteout the dark range, not the
  pillars, is in frame; monkey is small (model's KD6 scale); never watched at speed by anyone.
- Spend: Kling 3 takes $7.99; images 14 via Codex ($0 Cloudflare). Total D-FLIGHT $7.99 of $60.

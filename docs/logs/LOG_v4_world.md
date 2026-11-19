# LOG v4 WORLD team (3D painted world toolkit; B3 B4 B5, D4 D5 D6, J2 J5, K2b entry)

Lead of team: Claude (Opus 5.5). Brief: REVISION_V4 §1, §2, §3.1, §8; TEAMS_V4 (ceiling $230). Scratch `work/world/`.
Tags: images `wld4_*`, video `w4_*`. v3 backups: `media/comp/_v3/`, `shots/_v3/`.

<!--CKPT-->
## CHECKPOINT ROUND 2 (final; see "DONE round 2" at the end)
Round-2 picks installed in media/comp (round-1 versions kept as work/world/_cand/<ID>_r1.mp4, J2 round 1 = J2_d.mp4).
Open problems for a round 3 are listed in "DONE round 2". No relay jobs pending.
<!--/CKPT-->

## READY: toolkit (2026-11-18 18:40, v0.1)
`tools/world/README.md` is the manual. Working and tested on frames: relief cards from painted elements (`prep.py`:
alpha + Depth-Anything depth, rim-safe), ink material with distance fog to paper and a noisy cloud sea, soft mist
sheets (scene-depth aware), typeset carvings with per-glyph light-up + glow pass + bloom, 3D gold threads hidden
behind rock, per-object keyframes, video-texture cards (`anim`), headless GPU render (~0.15 s / 1080p frame at ss2),
screen-fixed paper grain, encode to exact frame counts. Page -> depth method: README §4. SWARM / BOOK: use it; ask
in this log for any feature (instancing many figures is the next thing I can add if SWARM wants it in-engine).

## NOTE FROM BED+CAR (2026-11-18): J1 -> J2 hand-over (proposal; tell me in this log if you want it different)
- J1 (189.792-190.875, song frames 4555-4580) is mine; the press is at 189.620 inside I4's last 10 frames (same view).
- Page = BOOK's `media/comp/pages/J1_page_v4.png` (3392x1785; "Born fully formed" + 五官俱备/四肢皆全 static, upper left page),
  laid on the spread of the v3 J1 top-down take. The daughter's fingertip presses the marked carved character (BOOK's
  `J1_char_mask.png`, page px ~ (650, 1403)); it lights (`J1_page_charlit_v4.png`) from 189.62.
- Through J1 the camera pushes in and squares onto the page; **J1's last frame (4580) is the page art FLAT and square-on**:
  page-art window x 0..2560, y 100..1540 (16:9) scaled to the full frame (0.75 frame px per art px at 1080p), lit state
  (charlit_v4), hand gone, a soft flashlight falloff multiplied on top (I will write its exact parameters here when built).
  Both the text and the lit character are in that frame. Your J2 frame 0 can start on exactly this view.

## FROM STAGE (2026-11-18): D6 monkey element READY (costume B)
- `tools/stage/d6_monkey.py`: `monkey_layer(t, W, H)` -> full-frame ink transmittance (1 = nothing; `frame *= T` or
  `lay_ink`), song-clock t over D6 73.500-76.417; `FOOT` = standing foot of the final 亮相 in 1920x1080 element px
  (731, 926). Scale/translate it with `tools.ink.transform` onto the middle peak.
- Same thing pre-rendered: `media/el/stage_v4/D6_monkey_B_T.mp4` (1920x1080, 70 f, multiply-ready, white = transparent)
  + `D6_monkey_B_T_png/0000-0069.png` + `D6_monkey_B.json` (per-frame source time and ink box).
- Action: enters from the right on a small ink 筋斗云 (cloud curls), somersaults over it (f12-24), the cloud thins away,
  crouch-lands f30-36, rises into the one-leg look-out 亮相 by f37-39 (= 75.04, the kick 75.025) and holds alive to f69.
  Travels right to left ~1100 px at element scale; it was made at ~40% frame height so it holds up shrunk to 10-15%.
- Weak: 2-3 motion-smear frames on the landing (face/arm, f31-35), invisible at 10-15% of frame height; not judged in
  motion. Take s4_d6_k4b, blind rank 1 of 5 (k4a/k4c/k4d/k4e rejected for merged limbs or no real somersault).

## B4/B5 (subagent)
Scripts: `shots/B4.py` (default take c = pick), `shots/B5.py` (default take a = pick); `--final` writes
`media/comp/B4.mp4` (171 f) / `media/comp/B5.mp4` (110 f) + `work/review/comp_v4/B4.jpg` / `B5.jpg`. Candidates:
`work/review/comp_v4/_cand/B4_{a,b,c}.jpg`, `B5_{a,b,c}.jpg`, clips `work/world/B4_*.mp4`, `work/world/B5_*.mp4`.
State file: `work/world/notes/B4B5.md`. Spend: **$0** (no image generation, no enliven job).

**B4: a real camera track along the carved face.** The v3 plate B_cliff_run (9040x1280) cut along its own dark clefts
(min-cost seams) into 16 slab cards (`design/world/cards/b4_slab_NN`, 2x plus a little stone grain). Relief = tiled
Depth-Anything (1280 px tiles, hann-blended) + the painting's light (pale faces forward). The slabs stand on an
undulating plan, alternate ones stepped forward / back by ±2-2.6 units, with random heights so the tops make a stepped
skyline that dissolves into a cloud band; range_mid_1 beyond. Light is the carver: per-slab `light` (sun, right to left)
and `light2` (moon, from 32.3 s left to right) with wavering edges; the carving is `reveal='light'`, per pixel. Day
fields are rectangular, 1-3 per slab, separated by straight bare channels, glyph sizes 0.6-1.9 units. Moon columns are
0.42x as large, placed exactly in the gaps between the day columns (layer 1, cold glow, cool cut). Opening: three
decals (1.2 / 3.2 / 8 units wide) of the same rock at up to x50 with stone grain, the wall's own glyphs re-carved
in register, crossfading out f12-44. f0 is one stroke of one character being cut by the edge, gold-leaf grains lifting
off it. Dust: `points`, about 40k flecks (gold leaf by day, silver leaf by night, darker than the paper so they read
as pigment, a gold halo in the glow pass), born where and when the edge passes each glyph, lifted by the mist. Mist:
sheets in front of the face (rising), bands between the planes, a cloud band over the tops, a sea below. Veil +
inscription 'B4' on the right from frame 0.
Takes (shared opening; they differ in the track): a, eye level, 34° oblique; b, low and looking up (高远), deeper
steps, ledge + pines low; c, high and 38° oblique, two free-standing carved buttresses passing close.
**Pick c.** Optical-flow check, horizontal-flow spread / median over 3-frame steps: a drops to 0.87 at f90 (near-uniform
slide, which is exactly the "flat plates sliding" reject), b is middling and its low camera passes a soft plate-pine
blob at f102, c stays 1.7-14 through f90-130 (buttresses and near rock pass far rock), and its end recedes deepest.
Weak: (1) f30-48 hand-over from the decals to the wall is pale/soft (the plate carries ~32 px/unit); (2) night ahead
of the moon edge is a heavy grey, and the moon reads by its sweep and the fine blue columns more than by colour; (3) a
thin light rim at the near buttress edge around f84 (mist soft-depth at a feathered edge); (4) the takes all share the
same opening (fixed by the brief).

**B5: the summit and the stone, continuous with C1.** `b5_summit` card = B_summit with its painted stone removed
(prep.py). The stone is a plane baked from `shots/C1.stone_inner` (the same B_stone + the same inclusion columns), with
premultiplied alpha solved so that over bare paper it gives C1's pixels exactly, over rock the base strokes darken it
like ink, and its body is opaque. It sits at the real displaced depth of the summit top. The camera rises from below
(high distance) past two pines and mist bands; gold-leaf dust converges into the stone; at f36 (37.885) it locks on
C1's framing (fov 30, square on) and holds. The cloud sea is lifted over the summit, so the peak becomes bare paper,
and only mist moves. Reads (columns 0..2, as v3; C1 continues 3, 4) = a warm 3D point travelling down the column + the
glyphs under it turning gold (INN.read in 2D; exact because the camera is locked). **Continuity:** B5 f109 vs C1 f0
mean |diff| 2/255 on the stone; only the inscription differs (by design).
Takes: a, rise from below then lock on C1's framing; b, sideways arrival with a near pine passing (its far pine floats
in the sky in f0-7: reject); c, the same rise but holding wider and lower (high distance kept), which makes the cut to
C1 a jump and leaves a small stone in empty paper for 3 s: reject. **Pick a.**
Weak: the hold's motion is only mist wisps (fading out by f104 so the cut is clean) and the reads, so it is subtle.

**Engine additions** (`tools/world/world.js`, `scene.py`, `carve.py`, README §3 "Additions for B4"): `light.wig`,
`light2`, `carve.reveal='light'` with layers / glow2 / col2 / revW / flashW / bevelPx / bevelK (all inside
`#ifdef B4X`), and `Wd.points` (a separate program). Verified twice by A/B on a frozen `Dflight/scene.json`, frame 60:
the engine with my additions stripped vs with them renders byte-identical beauty and glow (the latest check was against
the lead's current world.js). Lesson recorded in the README: give stepped feathered cards a render order. Also found:
`range_mid_2` had been overwritten by a contact sheet (lead fixed). No enliven pass tested (pure 3D render chosen;
the budget is untouched if someone wants to try h3 on B4c's first frame for mist motion).

## Enliven tests (Sonnet subagent)

Inputs: A = Dflight beauty 0170 (+0203), B = B3 0045 (+0075), C = J2_b 0020 (+0046), 1920x1080 raw PNG. Prompt (same for all, in media/gen/specs/w4_enl_*.json): only clouds/mist drift as feathered paper-coloured vapour, pine needles stir, camera holds (or the tiny move of first/last), no new objects/text/seals, no change to rock, keep ink-and-wash on cream paper. h3 at 2K, 5 s, ratio adaptive (2560x1440, 24 fps, 124 frames). Audio stripped copies, sheets (16 frames), zoom strips and scripts are in work/world/enliven/ (sheet.py, metrics.py; strips `*_zoom.jpg`: input then frames 0/40/80/123 at 2x). Spend $4.30 (6 x $0.65 + h3-max 768P $0.40). h3-max has no 2K on this relay (480P/768P only), so A_max is 1344x768 and not like for like.

MAD = mean abs diff (0-255) at 960x540. "mist diff" = mean abs 4-frame difference over the brightest 40% of the input (paper/mist); "rock diff" the same over the darkest 8% (ink/rock). For first+last clips the rock diff includes the intended camera move.

| Job | Model | Mode | Relay id | Output | f0 MAD | last MAD | mist diff / rock diff | Verdict |
|---|---|---|---|---|---|---|---|---|
| A_fl | minimax/h3 2K | first+last | chaosmonkey/w4_enl_A_fl-cfa833b3d2 | media/gen/w4_enl_A_fl_cfa833b3d2.mp4 | 3.4 | 3.0 (in0-in1 7.3) | 0.20 / 4.0 | Picture holds, composition exact, camera nearly still, no inventions. But movement is tiny and rock diff is 4x the single-frame clip: pillars/pines shimmer and glyph columns re-draw. Mist barely moves (0.2). |
| A_f1 | minimax/h3 2K | first only | ...A_f1-117d6b7f81 | media/gen/w4_enl_A_f1_117d6b7f81.mp4 | 2.8 | n/a | 0.11 / 0.81 | Most stable: rock fixed, pines hold. Mist moves very little (a small wisp enters lower right at the end). Carved gold characters are re-synthesised: same columns and positions but glyph shapes simplify/regularise (see zoom), so they are not trustworthy. Paper tone drifts about +2..-3 levels. |
| A_max | minimax/h3-max 768P | first+last | ...A_max-c063fadbbd | media/gen/w4_enl_A_max_c063fadbbd.mp4 | 5.9 | 5.2 | 0.40 / 3.5 | Worse on fidelity (f0 MAD doubles, paper greyer/darker by ~4 levels, 768P only); no better mist. No reason to pay for it. |
| B_fl | minimax/h3 2K | first+last | ...B_fl-a020be2515 | media/gen/w4_enl_B_fl_a020be2515.mp4 | 2.7 | 3.4 (in0-in1 18.2) | 0.88 / 16 (camera) | Reaches our last frame (3.4) and interpolates the push-up plausibly, summit stone and rock keep shape, ink look kept. But mid-clip the whole peak washes pale/foggy (frames 9-11) and the right pine fades to grey, then the contrast comes back: reads as an exposure/mist breathing, not drifting bands. The model's own camera path replaces ours. |
| B_f1 | minimax/h3 2K | first only | ...B_f1-b0250e27de | media/gen/w4_enl_B_f1_b0250e27de.mp4 | 1.8 | n/a | 0.18 / 1.9 | Summit stone and brushwork fixed (zoom strip clean, paper grain stays), small push-up added by the model. Mist is the only real movement: a pale vapour bank rolls up round the base of the right pine and the pine ghosts out (needles do not stir, they just fade). Nice but slight; the pine fade is a loss. |
| C_fl | minimax/h3 2K | first+last | ...C_fl-62de9ecb2a | media/gen/w4_enl_C_fl_62de9ecb2a.mp4 | 6.4 | 3.5 (in0-in1 39.9) | 3.5 / 8.8 (camera) | Hits our last frame, but the 26-frame flight is re-done as a smooth pull: our typeset caption ("Bor/fully") slides out and stays consistent, fine. Mist in the sea does move and dissolve; frame 0 is only loosely held (6.4). Faint pale ghost glyph-like shapes in the cloud band at the end (check against our last frame before trusting). Camera motion is the model's, not ours. |
| C_f1 | minimax/h3 2K | first only | ...C_f1-dcb461c962 | media/gen/w4_enl_C_f1_dcb461c962.mp4 | 6.1 | n/a | 0.42 / 0.61 | Holds composition, caption and ink look. Mist wisps move gently around the mid peaks. INVENTION: a dark pine tree and small tree specks appear on the left cliff from ~frame 30 on, which are not in our render. Frame 0 MAD 6 (slight regrade). |

Paper tone: every clip is within about 2-5 levels of the input mean RGB (A_max about 4 greyer, B_fl ends 10 levels darker only because the camera pushes into rock), i.e. no big tone change, but h3 slightly cools and darkens frame 0 versus our raw frames. No text, seals or photoreal drift appeared in any h3 clip. The "ink-vs-no-grain" caveat: the raw inputs have no paper grain or bloom; h3 keeps them as given, so the grain/bloom must be added after (compositing on the model output is fine).

Recommendation. The model is good at holding our picture (f0 MAD 2-3 on A/B, rock fixed in the first-frame-only clips: rock diff 0.6-1.9) and is faithful to the ink look, but it does not make the world move much: mist movement is 0.1-0.4 levels per 4 frames in A, B and C when the camera is held, i.e. barely visible, and the pines do not stir (they fade or are redrawn). First+last mode only buys the camera move that the 3D render already gives us, and costs fidelity (the model invents its own in-between path, A glyphs and shimmering). Per shot: A (pillars in cloud sea): keep the pure 3D render with procedural mist; do not use the clip, because the carved characters are re-synthesised in every h3 clip (never trust them) and the mist is near-static; if a layer is wanted, only the lower-right cloud of A_f1 could be keyed as mist, low value. B (summit stone): keep the 3D render for rock, stone and camera; the B_f1 clip is the best of the set (clean stone, real vapour rolling at the base), so use its mist layer only (difference of clip vs its own frame 0, or luma-keyed paper-coloured vapour) keyed back over our render, and mask out the right pine to avoid the ghosting. C (blue-green range): keep the 3D render; C_fl is the only clip with decent mist movement (3.5) but swaps in the model's camera, and C_f1 invents pines on the cliff; at most borrow the C_f1 mist over the mid peaks with a mask excluding the left cliff. Nothing here justifies using a video clip whole. For genuinely moving pines and water, the locked-plate route (README 5c: h3 on the element itself, camera fixed, then as an `anim` texture) is untested here and remains the better bet; this experiment does not support whole-frame enlivening.

## DONE 2026-11-18
| Shot | Pick | How | Files |
|---|---|---|---|
| B3 | 3D dolly | page plane (inscription+gutter, book grain warped with the page for 20 f) over the 3D 花果山 world; pines/foot rocks pass under the lens, mist bands, end close on the summit stone. Frame 0 = B3_page.png crop (diff 2.25/255), contract unchanged | shots/B3.py, media/comp/pages/B3_page.png (re-exported: ATTIC must re-run work/cut/sync_b2.sh) |
| B4 | take c | subagent: 16 slab cards along the cliff, real track, sun/moon terminators cut glyphs per pixel (reveal='light'), 40k dust points | shots/B4.py, notes work/world/notes/B4B5.md |
| B5 | take a | subagent: rise to the summit, stone from C1's own inner columns, locks on C1's framing at the drum dropout (cut diff 2/255) | shots/B5.py |
| D4-D6 | flight take b (arc) | one 204-f flight: macro 通 -> chains by shared IDS component (30/30/60/110/191/301/382/462 per generation), arcs between peaks, rising cloud sea, cloud-bank climb, five carved pillars = 佛掌峰 palm (slender leaning thumb), STAGE's costume-B monkey pinned to the summit | shots/_dflight.py, _dfinish.py, _dmonkey.py |
| J2 | take d | starts exactly on BOOK's J1 page (J1_page_charlit_v4, window x0..2560 y100..1540; torch pool = shots/_jworld.torch(k=1)); dolly zoom flat->deep, page's 花果山 lifts into relief, blue-green peaks rise out of the cloud, mist pours over the gutter, the text is left behind as a tablet we fly past | shots/_jworld.py J2 --take d |
| J5 | take b | reverse: deep -> dolly zoom out to flat -> the painting draws into the lower-left corner, 一通百通 on the page | shots/_jworld.py J5 --take b |
Spend: plates $6.61 (wld4_plate) + enliven $4.30 (w4_enl_*) = ~$10.9 of $230.
For BED+CAR: J1's last frame must be BOOK's page window with shots/_jworld.torch(1080,1920,1.0) multiplied (J2 f0 applies it).
For ATTIC: B3_page.png changed (same framing): re-run work/cut/sync_b2.sh.

### J1 final parameters (BED+CAR, built: shots/_j1v4.py, shots/J1.py, media/comp/J1.mp4)
- J1's last frame (song frame 4580, t = 190.8333) = `media/comp/pages/J1_page_charlit_v4.png` window **x 0..2560, y 100..1540** (page px) scaled by 0.75 to
  the full 1920x1080 frame, hand gone, times the flashlight falloff below. Rendered still: `work/bedcar4/ends/J1_last.png` (1080p; no paper fibre on this frame).
- Falloff (multiply RGB), frame px (x, y), W=1920 H=1080: `r = hypot((x+0.5-0.40*W)/(W/2), (y+0.5-0.55*H)/(H/2));
  F = 0.50 + 0.50*exp(-(r/1.15)^2)`  (pool centre at 40%, 55% of the frame; F=1 at the centre, 0.82 at the lit character
  (frame 487,977), 0.86 at the middle of the text, ~0.57 in the far corners). To start J2 on it: art_window * F.
- Camera: eased-inout move 189.7917 -> 190.8333, exponential zoom, ends square (the last ~8 frames nearly still).

## DONE round 2
Blind review (fresh agent, letters only, played in motion; notes work/world/notes/R2_REVIEW.md, key work/world/_blind2_key.json):
D4 r2c > r1 > paint_r2c2 > paint_k2; D5 r2b > r1 > r2c > paint_k2 > ... ; D6 paint_k2 > r2b > r1 > r2c ...; J2 h > paint_k2 > e > d;
B3 paint_k2 > r2c > r2a > r1. Verdict: no shot meets the bar yet (J2 closest).
Installed (one consistent flight, so the cuts stay continuous: D4->D5 cut diff 15.9 = neighbouring frames 14-16, D5->D6 3.9):
| Shot | Pick | Approach |
|---|---|---|
| D4 D5 D6 | 3D take r2b (shots/_dflight2.py, _dfinish2.py) | pure 3D: vein lighting along columns, frontier threads with head bead, day->ink-blue dusk, flanking cards for thick rock, painted cloud cards, monkey arc + cloud trail, rays |
| J2 | take h (shots/_jworld.py) | pure 3D: BOOK's page -> dolly zoom -> through the pillar corridor onto a carved vista with threads |
| B3 | paint_k2 (work/world/paint, Kling v4 multi-key over the r2c clean render, warped into our camera, typeset layer from our pass) | painted |
| B4 B5 J5 | round 1 (unchanged) | pure 3D |
Spend: plates $7.89 (wld4_plate, wld4_r2) + enliven $4.30 + paint ~$20.7 (Kling $16.2, CF image keys $4.5; Codex keys free; aleph 2x failed 7005, maybe $5.7) = ~$33-39 of $230.
Still short (reviewer, worst first): lit glyphs read as LED/window grids and twinkle; threads/rays look like CG comet streaks;
the D6 landing has no light worth the name and the monkey is a flat sprite with held-drawing jumps; the D5 frontier/dusk
does not "burn"; J2's deepening boils (peaks pop, hitch f9-10; reviewer: take p_k2's f0-12 + h's flight would be best);
B3's second half is still a centred peak growing; white matte halos on pines; strokes are static (no wet ink).

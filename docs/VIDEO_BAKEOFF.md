# Video bake-off (ink on paper)

2026-11-17. Budget $70 for this task. **Status: COMPLETE.** Spent **$60.73** of the $70 (list-price estimates from `tools/gen/spend.py`, tags `vb_*` and
`vbake_*`; 87 billed items, errors and cancelled jobs not billed). Nothing committed.

Clips: `media/vbake/<test>/<model>_<variant>.mp4`, each with a `.txt` (model, job id, exact input, prompt). Per-clip
10-frame sheets: `media/vbake/_sheets/<test>/<model>_<variant>.jpg`. Synced labelled grids (all models of a test, 4 across):
`work/review/bakeoff/vbake_<test>_grid.mp4`. Metrics: `work/review/bakeoff/vbake_<test>.json`. Lip-sync plots and numbers:
`work/review/lipsync/`.

## Tools written for this

- `tools/gen/vbake.py`: every prompt (verbatim) and the per-model input mapping (16 image-to-video models + 2
  talking-head models). `vbake.py spec TEST --models a,b [--variant v]` writes relay specs; `vbake.py file` copies
  finished clips into `media/vbake/`.
- `tools/gen/vbake_frames.py`: derived frames in `media/vbake/_frames/` (blank paper = the L3 sd5 sheet with the monkey
  erased; single poses from the L3 nbp pose sheet re-centred on that sheet's own paper). Singing close-ups
  `face_child.jpg` / `face_mom.jpg` were made with nano-banana-pro from the L5 / L6 stills (prompts beside them, $0.27).
- `tools/review/vbake_review.py intake|grid|compare TEST`: first-frame match, camera drift (ORB), flow, temporal std on
  the upper two thirds of the first frame's ink (V1: the rock above the mist) and on bare paper, ink-coverage drift,
  invented marks and colour, frame repeats; 10-frame sheets; synced grids.
- `tools/review/lipsync.py CLIP --audio work/stems/vocals.wav --t0 T`: automatic lag and sync score (see Lip-sync).

## Catalog and MiniMax

Catalog refreshed 2026-11-17 (`tools/gen/catalog.py`, cards @ 39a00b0): no new video model since 2026-11-13. MiniMax's live
video models are exactly `h3`, `h3-max`, `h3-lite`, `h3-highspeed`, `hailuo-2.3`, `hailuo-2.3-fast`; probes of
`hailuo-3`, `h3.1`, `h3.5`, `h3-pro`, `h4` return "model not found". All six were run on V1 and V2.

**Why h3 "failed 5 of 5" in HV**: with a first frame, h3-family models reject any `ratio` other than `"adaptive"`
(`7003 … image-to-video requires adaptive ratio`; the relay only stores "7003: User Input Error", a direct call shows the
reason). gen.py's DEFAULTS put `ratio: 16:9`. With `ratio: "adaptive"` all four h3 variants work, including first + last
frame. h3 cannot mix a first frame with `reference_audios` ("frame and reference inputs cannot be mixed").

Model keys and settings: kling4 = klingai/kling-v4 (720p) · hh11 = alibaba/hh1.1-i2v (1080P) · veo31 = google/veo-3.1
(1080p, 6 s, generate_audio false) · sd20 = bytedance/seedance-2.0 (720p, camera_fixed) · sd25 = bytedance/seedance-2.5
(720p) · h3 = minimax/h3 (2K; 768P for first+last and V6) · h3max / h3lite / h3hs = minimax/h3-max / -lite / -highspeed
(768P) · hailuo23 / hailuo23f = minimax/hailuo-2.3 / -fast (6 s 768P, prompt_optimizer off) · pixv6 = pixverse/v6 (720p)
· vidu3 = vidu/q3-pro (720p) · wan27 = alibaba/wan-2.7-i2v (720P, 30 fps) · k3omni = klingai/kling-v3-omni (sound off) ·
pavatar = pruna/p-video-avatar (720p) · fabric = veed/fabric-1.0 (720p).

Not testable on this relay: **lightricks/ltx-2-5-fast** (`image_uri` must be an HTTPS URL), **veed/fabric-1.0** (2047
"Invalid User Credentials" on 2 of 2 tries, likely the same URL requirement; not billed). **kling-v3-omni** treats
`image_input` as a loose reference, not a first frame (redraws a different picture: ff corr -0.04 / 0.42): dropped.

## V1 Landscape wakes (mist at the foot of the one-corner peak)

First frame `media/look/L1/qwen_v2.jpg`. Prompt v1 = the brainstorm's motion prompt adapted; v2 (leaders) describes the mist
as a soft feathered substance "the same cream colour as the paper", because v1's "the mist is the bare paper itself" made
two models draw an object (a paper strip, a silk sash). Rock std = median temporal std (0-255) of the rock above the mist
band; < 2 is locked like a still. Usable s = seconds a compositor can use as is.

| Model | $ / clip | Rock std | ff corr | Usable s | Verdict |
|---|---|---|---|---|---|
| **h3** (2K) | 0.65 | 1.7 | 0.997 | 5.2 | **Best.** Frame 0 exact at 2560x1440, rock and boulder locked, brush texture intact to the last frame, soft cream mist rises over the foot from 2 s. No birds, sun or colour. Mist is a touch white-grey rather than paper; key it as light |
| h3lite (768P) | 0.20 | 1.6 | 0.993 | 5.2 | Same behaviour for a third of the price; a thin mist band; paper slightly warmer. **Best value** |
| h3hs (768P) | 0.30 | 1.9 | 0.992 | 5.2 | Same; mist band a little blue |
| h3max (768P) | 0.40 | 6.6 | 0.991 | 5.2 | Same idea, mist denser and climbs higher over the rock (hence std) |
| kling4 v2 | 0.79 | 2.2 | 0.997 | 5.0 | Rock locked; soft foot mist, but invents a faint horizon line |
| kling4 v1 | 0.79 | 1.1 | 0.997 | 0 | Rock locked but the "mist" is a hard-edged tan **paper strip** sliding across: v1 wording taken literally |
| sd25 v1 | 1.16 | 0.9 | 0.884 | 3 | Locked, soft foot mist, but regrades frame 0, and the rock's hairline texture smears into worm-like ripples by 4 s; v2 came back **21:9** (1470x630) with grey streaks |
| sd20 v1 / v2 | 0.75 | 1.7 | 0.975 | 0 | Locked, but the mist is a thin grey streak on the horizon (v1) or it invents small distant islands (v2); paper grain boils (std 1.2-1.5) |
| hailuo23 v1 / v2 | 0.28 | 7.2 | 0.988 | 1 | A grey-blue fog wall swallows the rock and the rock dissolves into speckle; v2 tilts down. Last second (clearing mist) is pretty |
| hailuo23f | 0.19 | 2.7 | 0.988 | 0 | Grey fog bank plus painted water |
| veo31 v1 / v2 | 1.20 | 37-41 | 0.995 | 1.5 | Tilts / pans down unasked and invents more peaks and pines below the frame |
| hh11 | 0.90 | 13.6 | 0.999 | 0 | A floating brown silk sash, not mist |
| vidu3 | 0.63 | 14.0 | 0.998 | 0 | Jump-cut to a reframed picture at 0.5 s |
| pixv6 | 0.30 | 41.8 | 0.998 | 0 | Pulls back, invents mountains and pines |
| wan27 | 0.50 | 10.8 | 0.991 | 0 | Photographic billowing cumulus |
| k3omni | 0.57 | — | -0.04 | 0 | Ignores the first frame (redraws a different rock) |

Winning prompt (v1, as sent to h3):
```
Animate the first frame exactly. Locked-off camera. The painting does not move: the rocky peak, the round boulder on its
summit and every brushstroke stay exactly as painted. Only a long thin band of mist drifts slowly to the left across the
foot of the peak, veiling the lowest rocks as it passes and uncovering them again behind it. The mist is the bare unpainted
cream paper itself, not grey fog or smoke. Nothing new appears. No zoom, no pan, no change of light. No birds, no sun, no
water, no waves, no colour change.
```
(For non-MiniMax models use v2, in `tools/gen/vbake.py`.)

## V1b Heaven (青绿 clouds flowing, slow pull-back)

First frame `media/look/L4/sd5_v1.jpg`, prompt `V1b/v1` in vbake.py. Leaders only.

| Model | $ / clip | ff corr | Usable s | Verdict |
|---|---|---|---|---|
| **h3** (2K) | 0.65 | 0.998 | 5.2 | **Best.** Smooth slow pull-back (to 0.88), bare-paper clouds visibly drift in the valleys, peaks keep their azurite/malachite strokes, nothing invented. 2560x1440 |
| hailuo23 | 0.28 | 0.996 | 5.9 | Good second: pull-back to 0.89, clouds move, mountains hold; slightly softer |
| sd20 | 0.75 | 0.927 | 5.0 | Nearly static (cloud shimmer only, pull-back ignored); safe as a "breathing" plate |
| sd25 | 1.16 | 0.476 | 0 | Recomposes frame 0 |
| kling4 | 0.79 | 0.998 | 2.5 | Pulls back until the painting becomes a **sheet with a margin on a table** |
| veo31 | 1.20 | 0.995 | 3 | Pulls back and **invents calligraphy columns and red seals** in the corners, plus foreground pines |

Rule kept from the brainstorm: do the pull-back in code (multiplane `Camera.pull_back`), ask the model only for the
clouds. h3 is the only one that did both cleanly.

## V2 Ink figure in motion (the important one)

First frame `media/look/L3/sd5_v2.jpg` (alt `codex_v2.jpg`). Prompts a (staff flower + freeze), b (cartwheel pass right to
left + land), c (four bows) verbatim in vbake.py. All 16 models ran a; the 4 leaders plus MiniMax h3 ran b and c.

| Model | $ / clip | a staff flower | b tumbling pass | c four bows | Verdict |
|---|---|---|---|---|---|
| **kling4** | 0.79 | Big wet dry-brush arcs, stays on one leg, freezes in pose by 3.9 s | Cartwheel + back flip, lands crouched (leaves a small ink smear under him) | Plants staff, four clear turns and bows incl. back view | **Best all-round ink performer.** Figure stays ink wash; plumes and face patch hold; paper stays clean (std 0.45-0.75 except b). Codex alt frame: equally good, keeps the wetter Liang Kai wash |
| **sd20** | 0.75 | The most "staff is a brush": dry-brush rings like 飞白, ends in pose | Real cartwheel right to left, lands in pose (frame 0 already shifted right) | Turns and crouch-bows, reads as four directions | **Co-best.** Animates with an alternating big/small frame step (reads like twos), paper grain slightly alive |
| hh11 | 0.90 | Dry-brush ring, pushes in 1.5x, staff grows a spear head | Spectacular swirl tumble but paper turns brown, camera pushes in, adds a tail | Decent turns and bows | Strongest single moments, least control (camera, props, paper colour) |
| veo31 | 1.20 | Crisp spin with motion blur, but the staff vanishes from the final pose | Cartwheel, then shrinks; **invents teal shoes** and a ground splash | Turns, adds a tail, ends standing frontal | Fine motion, invents details |
| vidu3 | 0.63 | Clean ring spin, small, keeps the look | – | – | Good a; V1 / V2d show jump cuts and solid-black silhouettes |
| **h3** (2K) + plume guard | 0.65 | Dry-brush staff swipe and ring, ends in pose, plumes stay ink strokes | Cartwheel + aerial flip right to left, lands low on the left in pose | – (not run) | **Co-best**, at 2560x1440 for $0.65: frame 0 exact, clean paper (std 0.8-0.9). **Without** the guard (first run) the plumes become photoreal barred pheasant feathers |
| h3max / h3hs / h3lite | 0.40 / 0.30 / 0.20 | Same feather drift (max), ribbon plumes (hs), modest spin (lite) | – | – | Cheap, obedient, low energy |
| hailuo23 | 0.28 | Snaps at 0.6 s into a **flat black cel silhouette with a white mask** | – | – | Fails the look |
| hailuo23f | 0.19 | Stiff, snaps into a standing pose | – | – | Fails |
| pixv6 | 0.30 | Wild splashed-ink spin, spatters everywhere, adds a tail, zooms 1.5x, dirty paper | – | – | Not keyable; a source of splash texture at most |
| wan27 | 0.50 | Decent spin, grows a third plume, 30 fps | – | – | Second tier |
| sd25 | 1.16 | Recomposes to a close-up | – | – | Not for figure plates |
| k3omni | 0.57 | Ignores the frame (different costume, real feathers) | – | – | Drop |

**V2d Kling first + last frame between two poses** (`_frames/pose2.jpg` overhead swing -> `pose3.jpg` lunge thrust):

| Model | $ | Verdict |
|---|---|---|
| **kling4** | 0.79 | **Best.** One continuous arc with a dry-brush trail, lands exactly on the last pose at 3.9 s, holds 1 s |
| sd20 | 0.75 | Spin ring, lands at 2.2 s, then holds 3 s (wasted) |
| h3 (768P, ratio adaptive) | 0.40 | Works, but most of the move happens between two frames around 2 s (a cut, not a move) |
| vidu3 | 0.63 | Figure turns into a solid black silhouette mid-move, then back |

Winning prompt (a, as sent to kling4 and sd20):
```
Animate the first frame exactly. The splashed-ink Peking-opera monkey drops his shading hand, whips the long staff out
from behind his back and spins it in a fast staff flower in front of his body, the staff wheeling in blurred circles from
hand to hand, then on the last beat snaps it to a dead stop tucked under his arm and freezes in a sharp heroic pose, chin
up, perfectly still. Trained wushu precision: crisp, weighty, committed. He stays a painting of wet black ink washes and a
few quick brushstrokes, with his two long pheasant plumes and the small red patch around his eyes; the cream paper around
him stays bare. Locked-off camera. No ground, no shadow, no background, nothing new appears.
```
For MiniMax add: "His two plumes stay two thin black brush strokes, never real feathers; no colour except the small red
face patch." (`V2/h3_aplume.mp4`, `h3_bplume.mp4`: the guard fixes it completely).

## V3 Ink throw (blank paper -> the monkey)

First frame `_frames/blank_sd5.jpg` (the L3 sd5 sheet with the monkey erased), last frame `media/look/L3/sd5_v2.jpg`.
"fl" prompt = "starts exactly on @image_1 and ends exactly on @image_2 …"; "ff" prompt = describes the splash forming the
figure without naming the frames. **Note:** vbake.py passed the last frame to every V3 spec, so kling4_ff and sd20_ff are
also first+last (with the alternative wording); only pixv6_ff is truly first-frame-only (pixverse has no last frame).

| Model | $ | Settles by | Verdict |
|---|---|---|---|
| **sd20 fl** | 0.75 | 3.3 s | **Best.** Splash enters from the left, blooms grey into the paper like real wet ink on xuan, condenses into the figure; paper clean after |
| **sd25 fl** | 1.16 | 2.2 s | Very close: big thrown arc with flying droplets, most violent and painterly; paper texture moves during the splash |
| **h3 fl** (768P) | 0.40 | 2.3 s | A splash lands mid-sheet, droplets, resolves to the figure; cleanest paper of all (std 0.49); cheapest. Smaller gesture |
| sd20 ff | 0.75 | 2.2 s | Streak from the left + bloom, good |
| kling4 fl / ff | 0.79 | 2.2 s | Glossy black liquid tube, reads as CG fluid, not ink on paper |
| vidu3 fl | 0.63 | 3.9 s | Covers the whole sheet in solid black, then a silhouette |
| pixv6 ff (no last frame) | 0.30 | – | A splash cloud that becomes a different, coarser monkey with a tail; paper stays dirty |

Compared with the procedural splash (`tools/ink`): sd20 / sd25 / h3 are better at the wet bleed and droplet scatter; the
procedural one wins on timing control. Use a model throw for the birth shot, retimed so the figure lands on the gong
(58.673) with `Retime.freeze_at`.

## V4 Room acting

Attic `media/look/L5/nbp_a_v2.jpg` (prompt `V4/attic`), bedroom `media/look/L6/nbp_a_v2.jpg` (prompt `V4b/bed`).
Mistake on the first attic batch: both stills are named `nbp_a_v2.jpg` and `gen.ref_image` caches by basename, so the
first attic takes got the **bedroom** frame (kept as `V4b/<model>_atticprompt.mp4`; vbake.py now names refs by full path).
The attic was re-run on kling4 and sd20 (`V4/<model>_attic2.mp4`).

| Model | $ | Attic (mother page + glance, child looks up, neon flicker) | Bedroom (flashlight slides, child shifts chin) | Verdict |
|---|---|---|---|---|
| **kling4** | 0.79 | Neon dims the whole room off and back on (2.2-3.3 s), mother glances, faces stable, painting holds | Flashlight pool slides on the page, child shifts her chin on her arms; faces locked (std 0.7) | **Best.** Hand (a) look intact, no drift to anime or photo |
| sd20 | 0.75 | Neon flickers off and on twice, small page movement, child looks; look holds | The book and the pool morph, the pool slides off the book; paper/wash boils (std 10) | Good attic, weaker bedroom |
| veo31 | 1.20 | (only got the bedroom frame) invents a red zig-zag neon tube on the wall | Flashlight moves, child small moves; stable | Invents props |

## V5 Lip-sync

Frames: `_frames/face_child.jpg`, `_frames/face_mom.jpg` (nano-banana-pro, hand (a), chest-up, lips parted). Audio: the
BS-RoFormer vocal stem `work/stems/vocals.wav`, windows 15.31-20.31 (child "妈妈, will you tell me before I sleep",
first word 15.81) and 203.22-208.22 (Mom "Do you want to know how he never died", first word 203.72), i.e. 0.5 s pre-roll.

| Model | $ | Line | lag vs synced (ms) | r | sharp | Head drift / roll | Look and identity | Verdict |
|---|---|---|---|---|---|---|---|---|
| **sd25** take 1 | 1.16 | child | +18 | 0.36 | 0.35 | 8 px / 2.5° | Holds the painting and face, red neon side light kept | weak score, plausible sung vowels |
| sd25 take 2 | 1.16 | child | +143 | 0.38 | 0.41 | 16 px / 0.9° | Same | weak, needs -143 ms retime |
| **sd25** take 1 | 1.16 | Mom | -273 | 0.45 | 0.45 | 13 px / 1.0° | Holds; regrades frame 0 (ff 0.78), glasses hold, a blink | usable after +273 ms retime |
| **sd25** take 2 | 1.16 | Mom | -190 | 0.52 | 0.53 | 10 px / 2.2° | Same | **usable**, best take |
| pavatar | 0.13 | child | +18 | 0.51 | 0.52 | 21 px / **16.6°** | **Repaints the room into ink-wash blotches**, head tilts | sync exact (audio passed through, r 1.0 vs stem), look fails |
| pavatar | 0.13 | Mom | -23 | 0.46 | 0.49 | **55 px / 16.9°** | Background dissolves into a cloud, then into a paper-and-ink room; eyes close, smiles | same |
| fabric | – | both | – | – | – | – | 2047 "Invalid User Credentials" twice (not billed) | untestable on the relay |
| h3 | – | both | – | – | – | – | 7003 "frame and reference inputs cannot be mixed"; reference image + audio also 7003 | MiniMax has no audio-driven i2v here |

Mouth shapes (sd25): clear O / ah / closed shapes and a held open vowel, not chewing; one expressive blink per take.
The pavatar "ink painting" behaviour came from the `video_prompt` ("The picture stays an ink-and-wash painting"): it took
that as an instruction to repaint. Next try (not run): pavatar with a neutral `video_prompt` ("She sings, head still")
— its sync is exact and it is 9x cheaper than sd25, but the 17° head roll was also seen in MG.

**Measured lag spread for sd25: -273 to +143 ms (416 ms) across four takes** — the lag is random per take, as every earlier
project found, so every take must be measured and retimed (below).

## V6 Shadow puppet and hand shadow (kling4, sd20, plus h3)

| Model | $ | Puppet (`L9/gpt2_puppet_v1.jpg`) | Hand shadow (`L9/nbp_hand_v1.jpg`) |
|---|---|---|---|
| **kling4** | 0.79 | Moves in two blocks (move, hold, move): staff arm lifts, body steps; pieces stay flat and rigid | **Best:** the shadow's jaw opens and shuts 4-5 times with the fingers, head tilts; book and light steady |
| h3 (768P) | 0.40 | Continuous small motion, no snap | Talks too (5 bursts with holds), smaller jaw; cheapest |
| sd20 | 0.75 | One hop forward with blur, jittery cadence, screen grain boils (std 18) | Jaw barely opens; regrades frame 0 |

None gives the true shadow-play snap; the treatment's "re-posed in hard cuts, no in-betweens" is better done with
`tools/ink/puppet.py` from cut-out parts. Use kling4 for the hand shadow "talking".

## Recommended model per job

| Job | Model | Settings | Why | Backup |
|---|---|---|---|---|
| Landscape mist / water on a plate | **minimax/h3** | 2K, 5 s, `ratio: "adaptive"`, prompt V1 v1 | Frame 0 exact at 2560x1440, rock locked (std 1.7), real soft mist, brush texture intact, no inventions | h3-lite 768P ($0.20, same behaviour) for drafts; kling4 720p/1080p with prompt v2 |
| Heaven clouds (青绿) | **minimax/h3** | 2K, 5 s | Clean pull-back + drifting paper clouds, nothing invented | hailuo-2.3 ($0.28) |
| Ink figure action (staff, tumbling, bows) | **klingai/kling-v4** and **minimax/h3** (2K + plume guard) | kling 1080p for keeps (720p tested); h3 2K `ratio adaptive`; 5 s; first frame mid-pose | Committed, weighty moves, ink holds, plumes and patch hold, paper clean; h3 gives 2K for $0.65 | **seedance-2.0** (best dry-brush staff rings); veo31 / hh11 for single spectacular takes |
| Figure between two poses | **kling-v4 first + last** | 5 s; prompt "starts exactly on @image_1 … ends exactly on @image_2" | Lands exactly on the last pose by ~3.9 s | sd20 last_frame_image (arrives early) |
| Ink throw / birth splash | **seedance-2.0 first + last** | 720p, 5 s | Wet bleed into paper, settles into the exact figure | seedance-2.5 (more violent), h3 768P first+last (cleanest paper, $0.40) |
| Room acting | **klingai/kling-v4** | 720p-1080p, 5 s | Faces locked, painted hand holds, neon flicker as asked | seedance-2.0 for the attic |
| Lip-sync | **seedance-2.5 + reference_audios** | 720p, 5 s, 0.5 s pre-roll, `generate_audio:false`, then `tools/review/lipsync.py` retime | Only model that holds the painted face and sings plausibly | pruna/p-video-avatar with a neutral video_prompt (exact sync, unstable head) |
| Puppets / hand shadow | **kling-v4** (hand shadow) / code (`tools/ink/puppet.py`) for the jointed puppet | 5 s | Kling makes the shadow talk; no model snaps like a real 皮影 | h3 768P |

## MiniMax verdict

Jade's hint holds **for landscape painting**: h3 is the best model in the test for mist and clouds on a painted plate
(exact first frame at 2K, locked brushwork, mist that reads as paper-coloured vapour, no invention), and the cheap h3-lite /
h3-highspeed behave the same at 768P. h3 also does first + last frame (with `ratio: "adaptive"`). On the **figure** it holds
the frame exactly and moves with real commitment (staff ring, cartwheel + flip), but left alone it turns the two ink plumes
into photoreal barred pheasant feathers (h3, h3-max); one guard sentence fixes that, after which h3 is co-best with
kling-v4 for figure action, at 2K and $0.65 a clip. hailuo-2.3 is good on heaven clouds but fails the figure (flat black cel silhouette) and
fogs the plate grey; hailuo-2.3-fast fails both. MiniMax has no audio input with a first frame on this relay. HV's
"MiniMax 0/5" was only the `ratio` default in gen.py.

## Failure patterns

- **"Mist is the paper" taken as an object**: kling4 drew a tan paper strip, hh11 a silk sash. Describe mist as a feathered
  substance the colour of the paper (prompt v2) for non-MiniMax models.
- **Unasked camera moves**: veo31 tilts/pans and invents more landscape below the frame; pixv6 pulls back; hh11 pushes in on
  big moves; vidu3 jump-cuts to a reframed image at ~0.5 s.
- **Inventions**: veo31 calligraphy + seals on 青绿, teal shoes, a tail; hh11 spear head, tail; pixv6 / veo31 tails; wan27 a
  third plume; h3 photoreal pheasant feathers; kling4 a painting margin on pull-back.
- **Style collapse**: hailuo-2.3 flat cel silhouette; vidu3 solid black silhouette mid-move; kling4 CG glossy fluid in the
  throw; sd25 smears hairline rock texture into worm ripples after ~3 s.
- **Frame 0 not held**: sd25 (recomposes, regrades, once returned 21:9 1470x630 despite 16:9), k3omni (ignores it).
- **Paper**: sd20 and hh11 make the paper grain/tone live (std 1.2-1.5; hh11 browns the sheet on big moves); pixv6 dirties it.
- **Audio tracks**: kling4, hh11, wan27 and all h3 return a (silent or AAC) audio stream; strip it.
- **Inputs that need a public HTTPS URL** (ltx `image_uri`; probably fabric): untestable through the relay.
- **Ref-name collision** in `gen.ref_image` (same basename in two folders): fixed in vbake.py; watch for it in other tools.

## Lip-sync procedure (with the automatic lag tool)

1. First frame: chest-up, face about a third of the height, lips parted, painted hand (a) (nano-banana-pro from the room
   still is fine). Never name the shot size in the video prompt.
2. Audio: `gen.py audio-ref work/stems/vocals.wav <first_word - 0.5> 5.0 OUT.mp3` (or `vbake.py`'s `audio=` tuple).
3. Seedance 2.5, 720p, 5 s, `reference_audios: [OUT]`, `generate_audio:false`, prompt V5 (in vbake.py). Make 2 takes.
4. Measure every take:
   `$PY tools/review/lipsync.py TAKE.mp4 --audio work/stems/vocals.wav --t0 <window start> --plot work/review/lipsync/X.png`
   It tracks the inner-lip gap with MediaPipe FaceMesh (it re-runs itself in the orbital-sunrise py3.12 venv that has
   mediapipe 0.10.14; painted faces are found 100 % of the time), correlates it with the 1-3 kHz vocal-band envelope over
   ±1.2 s, and prints `lag_ms`, `lag_vs_synced_ms` (corrected for the -60 ms mouth lead measured on takes whose audio is
   known to be in sync), `r_best`, `sharp`, a second-peak check, head drift/roll and a suggested placement
   ("place clip frame 0 at song time T").
5. Keep takes with r ≥ 0.4 and sharp ≥ 0.35; on two equal takes prefer the smaller head roll. Place with
   `Retime(t0=T - lag_vs_synced/1000, src0=0)`. If Jade's ear disagrees, the tool's second peak is the first alternative.
6. Validation of the tool: on p-video-avatar takes (audio returned bit-identical to the stem, so true lag is 0) it measures
   -42 and -83 ms (= the physiological mouth lead); shifting the window by +200 / -300 ms moves the estimate by +167 /
   -333 ms (within one frame). Broadband loudness was rejected: on legato singing it barely dips (r 0.33).

## What the compositor must do per model (`tools/ink/video.py`)

| Model | Prep |
|---|---|
| h3 / h3-lite | Strip audio. Frame 0 is the still: use the clip as the plate itself (no stabilise needed, drift 0.1 px). Mist is lighter than the paper: if it must go onto our sheet, take `max(0, clip - still)` luminance as an erase/mist matte rather than `key_paper`. h3 output is 5.17 s; cut at 5.0 |
| kling4 | Strip audio. `Clip.prepare(ground='light')` keys cleanly (paper std 0.4-0.8). Drop the first ~0.4 s (repeated frames at the start); first+last holds land ~1 s early: freeze/hold into the hit with `Retime.freeze_at` rather than playing the dead tail |
| sd20 | Grade-match frame 0 (ff 0.975). Raise `lo` / use `smooth=0.5` to kill the living paper grain. Its alternating frame steps suit `on_twos` |
| sd25 | Check the output size (21:9 happens); regrade; only for lip-sync and the throw |
| hh11 | Stabilise + undo the push-in (zoom 0.65-1.28), de-tint the browned paper (prepare's per-frame ground division), matte out the invented spear head / tail |
| veo31 | Stabilise (drift 110-300 px); desaturate everything but cinnabar (teal shoes); never use for plates |
| vidu3 | Drop everything before the jump cut (~0.6 s) |
| All figure clips | Play the action on twos, `freeze_at` the 亮相 on the gong, matte with SAM 2.1 if the key catches stray smears; run `tools/review/vbake_review.py intake` to confirm paper std < 1 after prep |

## Recommended settings

- **Duration**: ask for 5 s (h3 returns 5.17 s, Veo only 4/6/8 s, Hailuo 6/10 s). Most figure moves resolve by 3-4 s; the
  rest is a hold that the compositor replaces with `freeze_at`. Never stretch past the end.
- **Resolution**: h3 at 2K is the best price per pixel ($0.13/s for 2560x1440); kling-v4 1080p ($0.235/s) for keeps,
  720p ($0.157/s) for tries; seedance-2.0 720p is enough for keyed figures (stores are 720p in `tools/ink`), 1080p for plates.
- **First frame**: always the staged still; for figures pick a still already mid-action. Start every prompt with
  "Animate the first frame exactly." and end with the guards.
- **Last frame**: use it whenever the end pose matters (kling-v4 best, seedance-2.0 lands early, h3 works with ratio adaptive,
  h3-max rejects it). For the ink throw, the last frame is what makes the splash resolve into *our* monkey.
- **h3 family**: `ratio: "adaptive"` with any image; no reference audio with a first frame.

## The best clips

1. `media/vbake/V1/h3_v1.mp4` — mist at the foot of the one-corner peak, 2K, rock locked.
2. `media/vbake/V1b/h3_v1.mp4` — heaven clouds with a clean pull-back, 2K.
3. `media/vbake/V2/kling4_a.mp4` — staff flower with wet dry-brush arcs, freeze (also `V2/kling4_c.mp4`, four bows).
4. `media/vbake/V2/h3_bplume.mp4` — tumbling pass right to left, lands in pose, 2K (and `h3_aplume.mp4`).
5. `media/vbake/V3/sd20_fl.mp4` — ink throw blooming into the monkey (also `V3/sd25_fl.mp4`, `V3/h3_fl.mp4`).
6. `media/vbake/V5m/sd25_sing2.mp4` — Mom sings "Do you want to know how he never died"; r 0.52, retime +190 ms.

Also worth keeping: `V2d/kling4_fl.mp4` (pose to pose), `V4/kling4_attic2.mp4` and `V4b/kling4_bed.mp4` (room acting),
`V6b/kling4_hand.mp4` (talking hand shadow), `V2/sd20_a.mp4` (dry-brush rings).

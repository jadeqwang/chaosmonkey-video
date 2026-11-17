# LOG: ROOMS-26 (car F1 F3a F4a F6b; bedroom I1 I2 I3a I4 J1 K1 K2a L1 L2)

Python `/home/jade/Documents/halys-video/.venv/bin/python`, run from the repo root. Shared code: `shots/_rooms26.py`
(clip plates + retime from `media/gen/rooms26/picks.json`, page-art mapping, paper fibre, line/wash flattening, ECC
tracking, lyrics switch `ctx.opts['lyrics']` / env `INK_LYRICS=0`), `shots/_bed_grade.py` (one white pool, dark violet
outside, faces kept by soft bounce lift), `shots/_car_grade.py` (dusk violet, faces kept; the amber sweeps are the
clips' own, `amber_sweep()` is there but was not needed). Generation: `media/gen/rooms26/` (`mkspecs.py` = every
prompt, `picks.json` = chosen take + song time of its frame 0, `lipsync_c.jsonl` / `wordsync.jsonl` = sync measures,
`paint_kf.sh` = keyframe prompts). Review sheets: `work/review/comp/<ID>.jpg`. All 13 files re-rendered `--fresh`,
960x540, exact frame counts; a 1920x1080 still of every script renders.

**Note for anyone editing `shots/_rooms26.py` / `_bed_grade.py` / `_car_grade.py`:** the runner's frame cache key does
not cover helper files in `shots/`: re-render with `--fresh`.

**Lip-sync measuring.** `tools/review/lipsync.py` unconstrained put 5 of 6 first takes at -0.7..-1.15 s; by eye (mouth
strips `work/rooms26/mouths.jpg`) those are spurious peaks (backing vocals / continuous rap in the window): F1 opens 3
frames before 石, I4 opens on "Wouldn't". Reported r = lipsync.py with `--maxlag 0.35`; lags applied as the tool
suggests (frame 0 at T - lag_vs_synced). Wide shots (I1, K1, F4a) fall back to the dark-box measure (face too small for
FaceMesh): their r means little; a word-gated check (`wordsync.py`) is given beside them.

**Keyframe vs clip:** sd25 reframes frame 0 (I1's book ~40 px higher than in `I1.jpg`), Kling drifts: page/pane quads
were measured on the CLIP frames, not on the keyframes or the sidecars (the sidecar quads were off for I1, K1, J1, L1, L2;
right for I2/I4b).

## Deliverables

| shot | frames | status | sources | QA (night cov / ink budget) & sync | weak / notes |
|---|---|---|---|---|---|
| F1 | 43 (2569-2612) | done (weak sync) | sd25 t1 `r26_F1_8fddbd590a`, t0 106.605 | 50 / 30; r 0.32 sharp 0.41, lag -65 ms | Hands pressed together (keyframe: half-chop/half-clap), not chopping. Two amber passes from the clip |
| F3a | 29 (2665-2694) | done (weak sync) | sd25 t2 `r26_F3a_t2_d5cc0c8a34`, t0 110.522 | 43 / 30; r 0.29, lag +18 ms | Compositor push 1.0 -> 1.35 (ease in) puts her face on F3b's first-frame position (0.63/0.48 vs F3b 0.625/0.48, checked side by side). Mouth makes the "o"; the blow itself (112.2) falls in F3b. Push to 1.35 on a 720p source is soft on the last frames |
| F4a | 38 (2706-2743) | done (weak sync) | sd25 t2 `r26_F4a_t2_2c28eb35fe`, t0 112.158 | 49 / 50; r 0.25 (dark-box, two small faces) | Both mouths move; the daughter's is tiny. Blank dashboard display shape (keyframe defect) left, dark under the grade |
| F6b | 20 (2895-2914) | done | Kling `r26_F6b_f0e32a1a2e` first 0.5 s at 0.6x (the model pans after that), ECC-stabilised, 5 % push | 39 / 30 | Reflection made in code (keyed upper body, mirrored about x 1000, dimmed, cooled, offset, inside the measured pane): same frame = same instant. Faint by design |
| I1 | 72 (4253-4325) | done (weak sync) | sd25 t1 `r26_I1_0068530c94` (first+last I1 -> I1_end), t0 176.71; page = worn left page + `B_master` + `A_crayon_monkey_rgba` | 22 / 20; dark-box r 0.16, word-gated r 0.25 | Face ~120 px: sync not measurable with confidence. The mountain sits on the visible band of the page, half under her knee; the crayon monkey (~60 px at 1080p) is right under her fingertip at the end. First 7 frames come out of the page's white (glare) |
| I2 | 66 (4325-4391) | done | Kling `r26_I2_75ef5f7c54` on twos; `media/comp/pages/I2_page.png`; `handshadow_silhouette.jpg` x2 | 51 / 25 (qa reads the lit pool as marks) | Jade's shadow on the right page from frame 0; the daughter's (smaller, facing it) pops up on "fight" 180.71; both re-posed (lean/tilt) on the beats 180.758 .. 182.466. Shadows sit above the hands (designed placement, not physically cast from them). Page art kept off hands by a warm/saturation key + closed holes: a few edge pixels of art may touch a knuckle |
| I3a | 40 (4391-4430) | done | **new keyframe** `media/kf/I3a.jpg` (nbp, `alt/I3a_v1`, refs daughter_heads + twins_left3); sd25 t1 `r26_I3a_7e9745c98b`, t0 182.39 | 51 / 25; **r 0.52 sharp 0.64**, lag +60 ms | Face off-centre right, looking left to Jade; no eyebrow lift. Faint scribble-like wash marks on the wall at left (from the clip), barely visible |
| I4 | 67 (4488-4555) | done | sd25 t1 `r26_I4_0c73641138`, t0 186.49; `I4_mama.jpg`; `I4b.jpg` still + `D_banquet.png`; silhouette | 42 / 20; r 0.37 sharp 0.32 (FaceMesh), word-gated r 0.41 | Cut on the MEASURED hits: I4a 187.000-187.500 (Mama ghost 70 % frames 0-7, 35 % frame 8, gone frame 9: "Wouldn't" under her), I4b 187.500-188.417 (shadow re-posed on 187.46/.781/.097/.313 floor -> leg -> seat edge -> sits; ends on the drum dropout), I4a 188.417-end ("You're able."). The brief's "last ~1.4 s" could not hold with hits at 187.46-188.31. I4b is the still (the Kling take was not used: a moving hand would not match the shadow). Shadow is the canon head silhouette; reads as a monkey head but small at 540p. Face flattened + paper fibre per lead note |
| J1 | 26 (4555-4581) | done | Kling `r26_J1_bd845757bc` on twos; `J1_page.png` / `J1_page_charlit.png` | 70 / 40 (lit page) | 草 placed under the fingertip by shifting the page on its leaf; lights over 5 frames after the last crash (HEAVEN's warm raking-light variant). Flashes one frame each on 4556/4557/4559/4560: flat page framed on 草 / Rubbing / misregister / page. The character is small in the room view (~27 px at 1080p); it reads in the flashes. Hand mask is a static polygon (the hand barely moves in 1 s) |
| K1 | 164 (4889-5053) | done (weak sync) | sd25 t1 `r26_K1_d6327b8779` (first+last K1 -> K1_end), t0 203.22; `I2_page.png` then `E_king_desk.png` | 26 / 15; word-gated r 0.35 at 0 ms, lipsync.py r 0.13 (dark-box) | Page art switches heaven -> underworld when the turning leaf passes upright (clip frame 158); page art is hard-foreshortened (grazing view of the painted book) |
| K2a | 38 (5053-5090) | done | **new keyframe** `media/kf/K2a.jpg` (nbp, `alt/K2a_v1`); sd25 t1 `r26_K2a_f0246a262d`, t0 209.855 | 68 / 20; **r 0.54 sharp 0.54**, lag +185 ms | Eyes on the page (leads into K2b's push). The cover's red pulled down to brown; 2 % push in. t2 (alt keyframe `K2a_alt.jpg`, eyes to lens) scored r 0.63 but sharp 0.47 |
| L1 | 107 (5490-5597) | done | team HEAVEN's K5 setup (read-only) for frame 0; ledger p8 (`work/heaven/ledger/spread_7_8.png`); Kling `r26_L1_d004183ee8` | 17 / 15 | Frame 0 = K5's last frame (mean abs diff 0.56/255 at 540p). Pull-back 228.80-232.70: the page flies from K5's frontal framing onto the book on the blanket, the whole room carried by the same homography (it tilts out from under the camera; the surround stays dark until mid-move). Covers the scribble "text" painted on that page. Lyric "…line" continues K5's |
| L2 | 63 (5597-5660) | done | `L2.jpg` still; ledger p8 multiplied on the page | 32 / 12 | One thing moves: the thumb tip presses toward the switch over the last 6 frames (local warp; subtle at 540p). Ends lit. The keyframe's long dark bar (defect) is left; its thumb sits beside, not on, the switch. Kling take not used (it rotates the torch and slides the pool off the column) |

Coverage: the car and close-up frames stay 10-45 points over their night budgets even after the grade (faces must read);
lit-page shots (I2, J1) are read by `qa coverage` as marks inside the pool, as HEAVEN noted for theirs.

## Spend

24 paid items: 22 relay jobs ($19.79: sd25 16 takes, Kling 6) + 4 nano-banana-pro keyframe paints ($0.54) =
**$20.33** of the $55 limit. Unused paid takes: Kling I4b, Kling L2 (stills used instead), second takes everywhere.

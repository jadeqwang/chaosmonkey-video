# Plates catalogue (background painter / plate department)

Started 2026-11-17. Every plate is a flat scan of a painting on cream xuan paper (or a code-built page), no frame, seal,
signature or writing. Prompts sit beside each file as `<name>.txt` (model, size, refs, full prompt). Rejected candidates are
in each group's `_rejects/`, generation sources in `src/`. Costs: `design/plates/_costs.tsv`. Style-reference crops (public
domain paintings, cropped clear of inscriptions and seals): `design/plates/_refs/`.

Coverage = `tools/review/coverage.py` measure (share of pixels > 28/255 from the plate's own paper, at 1024 px). For layers
and full-bleed rock it is relative to the plate's own ground. Key every paper plate with `key_paper(load_image(...))`;
full-bleed rock plates (B_cliff_run) go straight into `Cliff(rock, ...)` as RGB.

Spend for this pass: **$21.02** list-price estimate over 73 paid calls (gpt-image-2 33 = $13.73, nano-banana-pro 27 = $6.37,
qwen 11 = $0.77, seedream 2 = $0.15; gpt-image-2 priced conservatively by area), ledger `design/plates/_costs.tsv`.
Code-built (free): ledger pages, album leaf, worn book, far heaven, cliff stitch, face normalisation and builds, all cut-outs.

Status: **B done** · **D done** · **F done** · **E done** · **A done** · **C done** · **G done**

---

## B. Spread 1: 花果山 (`B_huaguoshan/`)

| id | file | px | shots | cov % | layers / notes |
|---|---|---|---|---|---|
| B-master | `B_master.png` | 3392x1920 | B3, D5 (end of pull-back), J2 | 16.4 | Ma Yuan one corner, qwen. Mountain lower-left (marks bbox x 0.08-0.38, y 0.42-0.96); **the stone is a speck at ≈ (707, 625), ~90 px wide**: push-in target. Sea and sky bare paper (a faint pale-grey wash at the waterline only). |
| B-master-L | `B_master_L_summit.png`, `B_master_L_near.png` | 3392x1920 each | B3, D5 | 3.5 / 13.8 | Same plate split at y = 0.56 H with a 0.1 H feathered crossfade (registered: just add both). Summit + stone + upper pines = far plane; lower cliff + waterfall + waterline = near plane. Put the mist band over y ≈ 1000-1150. |
| B-master-alt | `B_master_alt.png` | 3072x1728 | spare | 17.1 | Same prompt, slightly larger stone (≈ 45 px at 1400 view), mountain a little tighter in the corner. |
| B-cliff-run | `B_cliff_run.png` (cream) / `B_cliff_run_silk.png` (as painted, brown silk) | **9040x1280** (7:1) | B4, C6, D4, H5 | 28.6 (vs its own ground) | **Full bleed**, gpt-image-2, three 3840x1280 panels outpainted leftwards and stitched on min-cost seams at x = 3535 and 5899 (invisible at 100 %). Broad flat vertical planes between dark axe-cut fissures; no characters. **Camera:** right-to-left travel at full height: `Camera.travel(t0, t1, x_from=7900, x_to=1140, cy=640, zoom=0.84)` (frame = 2276x1280 of canvas, ≈ 4 frames of travel); closer travel at zoom 1.5 (1280x720 window) is still 1:1 sharp. Panels get narrower toward the left (older/younger rock reads as variation). Widest unbroken pale planes (measured, full height): x ≈ 1950-2220, 3270-3580, 4660-4940, 6180-6560, 7100-7420, 8020-8280; carved columns may also cross the thin cracks on any plane. |
| B-cliff-mid | `B_cliff_mid.png` | 3072x1728 | B4 (wide passes), C6, D5 (start of pull-back) | 32.2 | qwen. The cliff wall from mid-distance: six tall flat faces (for columns as texture, `size` ≈ 30-40 px), three bamboo ladders, two lashed scaffolds, pines. Cliff fills left 2/3, right third and sky bare paper. No figures painted: lay `carvers/` on the ladders (a carver ≈ 60-90 px tall here). |
| B-carvers | `carvers/B_carver_01..08_nbp.png`, `B_carver_09..16_qwen.png` | 330-640 px crops | B4 | elements | Separate cut-outs on their own paper. 01-08 nbp: 4-5 stroke jianbi dabs (round hats; some hold a chisel, three with a ladder piece). 09-16 qwen: finer wash figures with mallet + chisel, six on ladders, one kneeling on a plank. Scale so a carver is ≈ one stroke of a carved character. Swap variants on each pass. |
| B-summit | `B_summit.png` | 1920x3392 (9:16) | B5, C6 end | 45.2 whole / 21.4 in the end framing (budget 15: frame a little higher, rows ≈ 450-1530, for ≈ 15) | Fan Kuan high distance (qwen): peak rises from the bottom, the smooth stone on top at ≈ (970, 1040), ~170 px wide, upper third bare paper. **Camera:** tilt up from `(960, 2850, zoom 1.0)` to `(960, 1150, zoom 1.0)`, end framing = rows ≈ 610-1690: stone in the upper third of frame, sky above it. Mist band at y ≈ 1900. |
| B-stone | `B_stone.png` | 5504x3072 | C1, B5 insert | 6.3 | nbp. The stone close: one wet ring stroke, pale wash darker below, paper bare on top; summit is a band of a few strokes and moss dots. Smooth, unmarked. |
| B-stone-crack | `B_stone_crack.png` + `B_stone_crack_mask.png` | 5504x3072 | C1 at 43.635 | 5.9 | nbp edit of B-stone: pixel-registered, the only change is one hairline crack top to base forking at the foot. The mask (white = crack ink) lets the comp run the crack down over a few frames (reveal along y). |
| B-egg | `B_egg.png` | 5504x3072 | C4, C5 | 4.0 | nbp. The stone egg alone: one pale ring, wash, three dry dots, a soft bleed halo; left of centre, low (centroid 0.34, 0.64). The paper is fibrous (visible kozo fibres); `key_paper` drops most of them, raise `lo` if any remain. |

Weak / notes: the cliff run's ink is cooler (blue-grey) after removing the silk tone; if the comp wants warmth, use the
silk version and key it. The summit is a different hand (finer, qwen) from the stone close-up (nbp, wet and abbreviated);
they meet across a cut, not a dissolve. The far ridge for the master's third plane is in group C (`C_elements/ridges/C_ridge_*`).

---

## D. Heaven, blue-green (`D_heaven/`)

| id | file | px | shots | cov % | notes |
|---|---|---|---|---|---|
| D-mid | `D_heaven_mid.png` | 5504x3072 | J2, J3, I2 (page under the shadows) | 41 whole; **74 in the densest 16:9 window 70 % of the width** (x 832-4684, y 704-2870); 94 in a half-width window | nbp 4K, Wang Ximeng crop as style ref. Azurite/malachite peaks over ochre, crowded centre, all four edges sink into bare-paper cloud (cloud is paper, never painted). 花果山 = the tall peak left of centre, stone at **(1880, 452)**. Fold line painted out in code where bare. |
| D-close | `D_heaven_close.png` | 5504x3072 | J2 start (one lit peak among neighbours) | 52 (81 in a 60 % window) | nbp edit of the mid crop (input `src/heaven_close_in.png`): same peaks, finer cun, pines. **Registered**: ECC affine, cc 0.998; occupies mid rect (786, 242)-(3381, 1678), i.e. 2.12 close px per mid px. Stone at (2320, 450). |
| D-far | `D_heaven_far.png` | 5504x3072 | J5 end ("a few strokes in the lower-left corner", 5 %) | 4.9 | Code: the mid keyed and shrunk x0.34 into the lower-left of a bare sheet at (192, 1936, 1871x1044). Stone at (831, 2090). |
| D-reg | `D_heaven_registration.json` | | J2-J5 | | **How the three scales register:** one coordinate chain close -> mid (affine from `corners_in_mid_px`) -> far (`p * 0.34 + (192, 1936)`). Pull back on the close until its zoom equals 2.12x the mid's, cross to the mid at the same stone position, continue to 0.34x and cross to the far. All three share peak positions exactly (the far is the mid itself), so the crossings are invisible; do them inside a rubbing flip or a chop if you want them hidden twice. |
| D-banquet | `D_banquet.png` | 3072x2048 | I3, I4 | 21.2 | gpt-image-2. One lacquered table, **8 chairs, 7 blank name slips**; the empty chair is the **front-centre one, pulled out toward us, no slip** (it stands clear of the table: bbox 1345,1351-1787,1985, ready for the daughter's hand-shadow to climb onto in I4). Peach bough from the upper left. Seen from slightly above, from the servants' side. Paper is yellowish (#e8d8b1): key it. Slips are blank (no writing). |
| D-banquet-el | `banquet_elements/`: `D_table.png` (table alone, same 7 slips + peaches, 3072x2048), `D_chairs_sheet.png`, `D_chair_back/front/side_facing_left/side_facing_right.png`, `D_empty_chair_from_plate.png` (cut from the plate), `D_peach_bough.png` (cut from the plate) | | I3, I4 | elements | Table and chairs generated by gpt-image-2 with the banquet plate as reference (same hand). The model drew both profiles facing right; `side_facing_left` is a mirror. |

Weak: the banquet is in a clean fine-line court-painting hand, cooler and more "illustrated" than the ink plates; it
works as the heaven page (青绿 register) but is the least brushy plate in the set. The heaven range is nbp's tidier
version of Wang Ximeng (fewer layers than the real scroll).

---

## F. 脸谱 album (`F_lianpu/`)

| id | file | px | shots | notes |
|---|---|---|---|---|
| F-leaf | `F_album_leaf_empty.png` (full bleed) / `F_album_leaf_empty_rgba.png` (sheet with worn round corners and a soft deckle, 120 px transparent pad) | 3600x2400 (+pad) | H1, H2, H3, H4 | **Built in code** on `Paper('aged')`: faint hand-ruled 6x4 grid inside a thin double rule, foxing and tide lines, all cells bare. Cell rects, row-major, in `F_album_grid.json` (cell 510x475 px from (270, 230)); the bare cell is row 3, col 4 (index 15) as in the bake-off. Fit a face so its 1120 px face box is ≈ 0.8 of the cell height (scale ≈ 0.34). |
| F-faces v3 | `v3/faces/<ID>.png` + `<ID>_mask.png`; index `F_faces_v3.json` (id, file, mask, face box, take); cell map `shots/faces_lib.ALBUM` | 1400x1400 each | H1-H4 | **v3 (current): every face is the conventional 脸谱 of a named character**, checked against sources (`docs/logs/LOG_v3_faces_verify.md`; first pass `LOG_v3_faces.md`). gpt-image-2 1536 high via `v3/gen_faces.py` (prompts `v3/faces_v3.json`; F01 as outline ref; CC0 Qing album crops as pattern refs for 包拯, 二郎神, 时迁, 孙悟空), candidates in `v3/_cand/` (all takes kept, picks in `v3/picks.json`), **normalised in code** by `v3/normalise.py` (face cap-to-chin 1120 px, centred). Previous normalised set in `v3/faces/_v3a/`. The face build stages and wear are made in code (`faces_lib._paint_surface`). |
| F-faces v1/v2 | `faces/F01..F23.png` (+ masks, `F_faces.json`), `builds/` | 1400x1400 | (none now) | The v2 "original design" faces, superseded by v3 (audit in `LOG_v3_faces.md` §3). F01 is still the head-outline reference for generation. |

The v3 leaf (row-major 6 x 4; cell 15 bare, the child stands there):

| cell | id | character | 谱式, colour | meaning in the tradition |
|---|---|---|---|---|
| 0 | ZHANGFEI | 张飞 | 黑十字门 (蝴蝶脸), laughing | black: rough, blunt, upright |
| 1 | BAOZHENG | 包拯 | 黑整脸, white crescent | black: upright, impartial |
| 2 | DIANWEI | 典韦 | 黄花三块瓦, halberds in the brows | yellow: fierce, ruthless |
| 3 | CAOCAO | 曹操 (**threat**) | 水白整脸, pink 印堂 | white: treacherous |
| 4 | XUYANZHAO | 徐延昭 | 紫六分脸 | purple: steadfast, loyal |
| 5 | HUANGGAI | 黄盖 | 红六分脸 (老脸) | red: loyal old general |
| 6 | CHENGYAOJIN | 程咬金 | 绿碎脸 | green: rash, impetuous |
| 7 | JIANGWEI | 姜维 | 红三块瓦, taiji on the forehead | red: loyal; taiji: resourceful |
| 8 | DOUERDUN | 窦尔敦 | 蓝花三块瓦, double hooks on the brows | blue: staunch, unbending |
| 9 | GAODENG | 高登 | 油白三块瓦 | oil-white: overbearing |
| 10 | GUANYU | 关羽 (**tool**) | 红整脸, one mole (破脸) | red: loyal and brave |
| 11 | ZHENGEN | 郑恩 | 黑歪脸, 雌雄眼 | crooked face |
| 12 | LUZHISHEN | 鲁智深 | 白僧脸, red 圆光, 螳螂眉 | the monk's face |
| 13 | TANGQIN | 汤勤 (**trick**) | 文丑, square 豆腐块 | the clown: scheming |
| 14 | KID | 娃娃生 / 哪吒 (**kid**) | 俊扮 (unpainted), red dot at 印堂 | a child has no pattern |
| 16 | MONKEY | 孙悟空 | 象形脸, 倒栽桃: red inverted peach, gold eyes, cloud curl | the monkey's own face, beside the child's cell |
| 17 | LIUJIN | 刘瑾 | 红太监脸, 舍利珠, white lower lip | eunuch; the red is satire |
| 18 | ZHOUCANG | 周仓 | 花元宝脸, 淡青 forehead | the ingot face |
| 19 | ERLANG | 二郎神 | 金三块瓦, third eye | gold: gods |
| 20 | JINQIANBAO | 金钱豹 | gold 神怪脸, leopard head, coins | gold: spirits |
| 21 | ZHONGKUI | 钟馗 | 花元宝脸, red forehead, bat | the demon-queller |
| 22 | XIAHOUDUN | 夏侯惇 | 蓝三块瓦, red dot under his left eye | blue: fierce |
| 23 | SHIQIAN | 时迁 | 武丑, kite-shaped 筝形 patch | the martial clown, the thief |

No face carries writing (the monkey's 卍/佛 variants and 项羽's 寿 avoided). Silver is not used (no silver face is
attested by two sources; 木吒 dropped). Weak: all faces share one head outline (the grid needs it); fine line work is
below 540p at the full-leaf framing; 鲁智深 lacks the small 戒疤 dots.

---

## E. The underworld and the ledger (`E_underworld/`)

| id | file | px | shots | cov % | notes |
|---|---|---|---|---|---|
| E-king | `E_king_desk.png` | 4800x3584 (4:3) | K2 | 17.8 | The storybook's painting: a king of the underworld seated frontally behind a draped desk, a scribe in green at left with a brush, an inkstone, a folding screen in pale lines, **the register lying open on the desk with blank ruled pages**. Fine line + pale wash, one touch of cinnabar on the desk cloth; bare paper all round. Seedream-5-pro (Ten Kings crop as style ref) re-scanned to 4K by an nbp edit (faithful; slightly pinker paper). Alt at native size: `E_king_desk_alt_2304.png`. **Register on the desk (approx ±10 px, for mapping or the push target):** book outline TL (2258,1840) TR (2910,1818) BR (3010,2090) BL (2340,2110); ruled area of the right page (2610,1850)(2895,1825)(2970,2055)(2690,2065); left page (2295,1860)(2580,1848)(2650,2070)(2365,2075). |
| E-ledger pages | `ledger/E_ledger_p1..p4.png` | 2200x3300 each | K3, K4, K5 | 24-25 (whole page) | **Built in code** (`ledger/build_ledger.py`, rebuildable): `Paper('aged')`, 乌丝栏 hand-ruled frame (thick outer + thin inner rule) and 9 ruled columns, entries typeset in **館閣楷 GuanGe Kai** (FONTS.md's ledger kai for the official clerk-hand feel; pass the LXGW WenKai path as argv[1] for the softer alternative), through `ink.wash` so the ink bleeds into the fibres; ink fades where the paper is worn. Right to left. Each entry = a column `魂字…號 + name`, then (for double entries) an indented note column. |
| E-entry | page 1, columns 5-6 (from the right), box (611, 440)-(1002, 2756) | | K3 | | **The novel's entry, verbatim from `design/text/categories.txt` (ch. 3):** 魂字一千三百五十號 / 孫悟空 / 天產石猴 / 該壽三百四十二歲 / 善終. Page 1 opens with the heading column 猴屬之類 (the novel's words). |
| E-filler | everything else on p1-p4 | | K4 | | **INVENTED FILLER, 20 entries (魂字一千三百四十八號 … 一千三百六十八號 except 1350):** name always 猴屬; notes use only the ch. 3 phrases 似人相 不入人名 / 似臝蟲 不居國界 / 似走獸 不伏麒麟管 / 似飛禽 不受鳳凰轄, plus an invented age 該壽N歲 and sometimes 善終. Listed per column (with an `invented` flag) in `ledger/E_ledger.json`. |
| E-last | `ledger/E_ledger_p4.png` | 2200x3300 | K5 | ≈ 0 in the bare column | Page 4: five entries, then **the final (leftmost) column ruled but bare** (column 8, x ≈ 220-416). Frame K5 on that column for the 3 % budget. |
| E-strike | `ledger/E_ledger_strike_density.png` (16-bit, normalised; peak density 0.95), `ledger/E_ledger_strike_arrival.png` (16-bit, 0..1 progress along the stroke, 1 outside), preview `ledger/E_ledger_p1_struck.png` | 2200x3300 (page-1 coords) | K3 at "single breath" | | One wet vertical-diagonal stroke (`ink.stroke`, width 92, wet start, dries toward the end) from above the 魂 down-left across both entry columns. Animate: `D * smoothstep(0, 0.04, p - A)`, i.e. `InkAnim(D, A)`; lay with `ink_T`. Points in `E_ledger.json`. |
| E-persp | `ledger/E_ledger_p1..p4_rgba.png` (page with deckle alpha, 160 px pad), `ledger/E_ledger_spread_p1p2.png`, `_p3p4.png` (open spreads, right page first, gutter shading), `ledger/E_ledger_spread_p1p2_persp.png` (example warp, RGBA 3600x2200, corners in the json) | | K2-K4 | | Perspective-ready: warp the RGBA page or spread with `cv2.getPerspectiveTransform` onto the desk quad above or any camera quad. |

Weak: the king's face is a stock official type (fine for a storybook); the filler ages are invented numbers.
Whole-page coverage (24-25 %) is above K4's 10 %: frame K4 so the turning page is part of a wider, darker shot, or
let the camera sit on two or three columns.

---

## A. The storybook as an object (`A_book/`)

| id | file | px | shots | notes |
|---|---|---|---|---|
| A-cover-new | `A_cover_new.png` | 2304x2592 (8:9, closed book, edge to edge, no perspective) | A2, A4 | gpt-image-2. Half-bound: faded-indigo cloth spine (left ≈ 13 %), cream paper boards with a small ink-and-colour 花果山 (stone on the summit) in the lower half above an unpainted sea. **Title area blank: the upper half, x ≈ 0.16-0.97, y ≈ 0.04-0.52.** Crisp corners (1988). |
| A-cover-worn | `A_cover_worn.png` | 2304x2592 | I1, L1 | gpt-image-2 edit of the new cover: same layout, rounded rubbed corners, faded frayed spine, foxing, a pale water stain at the lower edge, yellowed paper. Not pixel-registered to the new one (re-drawn), same layout. |
| A-open-new | `A_open_new.png` | 5504x3072 | B2, B3 (start of the push), C2, A2 | nbp, **painted in the film's hand** (fine line + pale wash), seen straight down: a clean rectangle, blank pages, grey-wash gutter shadow, stacked page edges as fine lines, indigo cloth margin. Geometry in `A_open_book.json`: book bbox (234, 314)-(5266, 2865), gutter x = 2797, right page [2857, 314, 5040, 2729], left page [455, 314, 2738, 2733]. Map spreads into those boxes (the page tops curve slightly down to the gutter; follow with a mild bend near x = gutter ± 150). |
| A-open-worn | `A_open_worn.png`, `A_open_worn_crayon.png` | 5504x3072 | I1, I2, I3, K1, L1, L2 | **Built in code, pixel-registered to A-open-new** (swap or dissolve between 1988 and 2026 without a jump): pages re-toned with `Paper('aged', gutter=…)` (foxing, tide lines, faded gutter, worn corners), cloth faded, outer corners rounded. `_crayon` adds the crayon monkey in the left page's bottom outer margin at [569, 2069, 553, 580] (x, y, w, h). |
| A-crayon | `A_crayon_monkey.png` (on cream), `A_crayon_monkey_rgba.png` | 1260x1320 | I1 | Little Jade's wax-crayon monkey (orange/brown, blue dot eyes, curly tail, one arm waving). Keyed from a generated photo of a drawing. Lay with multiply (`_rgba` alpha = wax density). |

The rejected gpt-image-2 open book (`_rejects/open_new_gpt2_a`) is cleaner and photographic; the nbp worn edit
(`_rejects/open_worn_nbp_a`) went to "treasure map" (torn edges, heavy stains) and came back at 1376x768.

---

## C. Elements on bare paper (`C_elements/`)

| id | file | px | shots | cov % | notes |
|---|---|---|---|---|---|
| C-pines | `pines/C_pine_01..05.png` | 600-910 x 1130-1750 | B3-B5, D5, E2 | elements | qwen (same hand as B-master): tall twisted, cliff-hanger, long-armed, young straight, split old pine. Roots end in dry strokes, no ground. |
| C-waterfall | `C_waterfall.png` | 3072x5504 (9:16) | B3, B4, D5 | 0.8 | One thin broken thread of falling water, a dark notch of rock at the top, spray dots at the foot. Animate the thread only (video model) or slide a noise mask down it. |
| C-waves | `C_waves.png` (as painted, very pale) / `C_waves_strong.png` (density x3.2 in code) | 6336x2688 (21:9) | B3, D8, level-distance sea | 0.0 / 0.1 | Ma Yuan water-album lines, sparse, lower band only. Use `_strong` with `key_paper` (the original is under the default `lo`). |
| C-ridges | `ridges/C_ridge_01..04.png` | 3392 x ≈300 each | B-master far plane, D5, J5 | elements | qwen, Xia Gui: long low ridges in one pale wash, top edge crisp, bottom dissolving. 01 = lowest/palest on the sheet … 04 = topmost/darkest; re-tone with `gain` for depth. Full sheet in `src/ridges_qwen.png`. |
| C-mist-edges | `mist/C_mist_01..06.png` | 1500-2270 wide | everywhere a rock foot meets a mist band | elements | Pale wash shapes whose lower part feathers into bare paper (wet blooms). Lay under a rock layer's foot, or use `1 - T` as an erase mask for `Scene.mist`. |
| C-troop | `C_troop_plate.png` | 5504x3072 | E2 | 25.5 (budget 25) | nbp with the canon troop dabs as ref: a rocky slope from lower left, two pines, ≈ 100 faceless monkeys in clusters thinning at the edges; upper half and right side bare (room for the printed text column). |
| C-dabs | `dabs/C_dab_01..42.png` | 230-700 px crops | E2, F4/F5 (clones as ink), D5 | elements | 40 poses (sitting, climbing, running, hanging, grooming pair, peach-carriers, asleep …) cut apart in code. **Weak:** nbp painted small wash macaques rather than true 6-stroke dabs; at troop scale they read as dabs. Truer few-stroke dabs: the canon sheet `design/characters/monkey/monkey_storybook_figures.jpg` (≈ 20). |
| C-sleeve | `C_master_sleeve.png` + `elements_E4/C_sleeve_hand_whisper.png`, `C_tiny_monkey_bowing.png` | 3840x2160 | E4 | 0.5 (pale fine line) | **Composited in code from canon art** (the generated version was a Creation-of-Adam pointing hand with a realistic macaque: `_rejects/sleeve_nbp`). The Master's pale sleeve and hand enter from the upper right and lean down; the tiny canon storybook monkey bows toward the fingertip (fingertip at 2722, 1193). The Master is never whole. Elements separate so the lean can be animated (rotate the sleeve about its upper-right corner a degree or two). |
| C-pilgrim | `C_pilgrim_band.png` | 5504x3072 | G2 | 3.1 | nbp from the canon pilgrim figure: crouching grey-robed monkey clutching his head, **one thin gold band the only colour**, lower left, everything else bare (the margins close in on it). Fold line at the centre painted out where bare. For "the gold pulls tight" key the band by hue (r - b) and tighten it with a slight scale toward the head centre. |

## G. Extras (`G_extras/`)

| id | file | px | shots | notes |
|---|---|---|---|---|
| G-rubbing | `G_rubbing_texture.png` | 1265x675 | C1, D1, D5, J1 (rubbing flips) | Look reference for a blank 拓片 sheet: pad-dabbed matte black, pinholes, creases, no characters. nbp returned only 1K; production should use `Paper('rubbing')` / `rubbing.py` and match its pad mottling to this. |
| G-halo | `G_halo_ring.png` (on cream) / `G_halo_ring_rgba.png` (matted) | 3688x3688 | H5 | One loose open brush ring in shell gold, wet and heavy where the brush pressed, breaking into 飞白 streaks, a few flicked specks. `_rgba` keeps only warm gold (paper fibres removed): lay with `over()`, it is opaque pigment, never multiplied. Float it behind her head, not touching. |
| G-hair | (none) | | H6 | Drawn by the compositor (`ink.hairline`), as asked. |

---

## Model notes from this pass

- nano-banana-pro returned **1K (1376x768 / 1200x896 / 1584x672) on about a third of 4K calls**, at the full 4K price,
  more often with an image input and on long (>150 s) calls. Check sizes; re-roll or rescan (an nbp "reproduce this
  painting as a high-resolution scan" edit worked well on E_king_desk).
- nano-banana-pro still paints an album fold down the centre of 16:9 sheets (heaven, waves, pilgrim, carvers): painted out
  in code where the column is bare paper.
- qwen-image-3.0-pro maximum is 6.55 MP (3392x1920); seedream-5-pro 4.19 MP with sides divisible by 16 (2720x1520 /
  2304x1728); gpt-image-2 up to 3840 on a side, 3:1 max (3840x1280 was used for the cliff), ≈ $0.59 at that size.
- gpt-image-2 outpainting re-paints the "kept" third, so long runs are stitched on min-cost seams, not on the overlap.

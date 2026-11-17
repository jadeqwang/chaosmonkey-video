# LOG: HEAVEN & LEDGER (I3b J2 J5 K2b K3 K4 K5 + page art I2/J1)

Python: `/home/jade/Documents/halys-video/.venv/bin/python`, run from the repo root. Shared helpers: `shots/_heaven.py`
(torch light field, image fit, lyric switch: `ctx.opts['lyrics']` or env `INK_LYRICS=0`; env `HL_NOLIGHT=1` renders
the page without the torch, for coverage QA). Extra ledger pages for the page turns: `shots/_heaven_ledger_pages.py`
-> `work/heaven/ledger/` (8 pages: p1, p2 pixel-identical to the plate's; p3-p6 filler entries in the plate's
wording; p7, p8 = the plate's p3/p4 layouts and papers with the numbering continued, p8's final column bare).

**QA note (all torch shots):** `qa coverage` takes the dark border as the ground, so it counts the whole lit pool as
marks (K3 reads 38 % lit). Numbers below give both: lit (as the tool reads it) and the page alone (`HL_NOLIGHT=1`).

| shot | frames | status | sources | QA | weak |
|---|---|---|---|---|---|
| K3 | 81 (5131-5212) ok | done | plate `E_ledger_spread_p1p2.png` (p1 right, p2 left), `tools.ink.stroke` (own path, see notes) | coverage lit 38.5 %, page alone 43 % vs budget 15: over. The ledger close is dense text by design; under the torch only the pool (about a quarter of the frame) reads. | Over the ink budget (framing kept so the whole entry is legible). Stroke's advancing front is a straight cut for the 8 drawing frames. |
| K5 | 110 (5380-5490) ok | done | `work/heaven/ledger/spread_7_8.png` (p8 = plate p4 layout, final column bare) | lit 27 % (tool reads the pool) vs budget 3; the page alone cannot be measured (the dark beyond the book's edge reads as marks). By eye: one lit strip, the bare column, two entries, the rest dark. | The bare column is narrow (74 px at 1080p) because the whole column height is in frame; the left 37 % is the dark beyond the book's edge. |
| K4 | 168 (5212-5380) ok | done (no hands) | `work/heaven/ledger/spread_*.png`, p1 with the K3 strike re-drawn at page resolution | lit 64 % (tool reads the pool); not meaningful | Hands not attempted: the canon hand poses are tiny parts of full-body colour sheets (about 200 px, with sleeves); I judged a cut-out would read as a sticker at the page corner. The pages turn by an unseen hand. Three turns, not four (4 spreads). The leaf is 3 rigid panels, so the curl is faceted at 1080p if you step frames. |
| K2b | 40 (5091-5131) ok | done | plate `E_king_desk.png` keyed onto aged paper; ledger p2 / p1 (upper halves) laid into the painted register's inner frames in perspective | lit 80-90 % (tool reads the pool); the plate alone is ~21 % of its sheet | The ledger text is crisper than the painting's line; the painted rules inside the register were erased and replaced by ours. |
| J2 | 47 (4581-4628) ok | done (heads faint) | `D_heaven_close.png` carved with `Cliff` (千字文 lines 1-60, 崇羲篆體, size 64 close px, cinnabar fill) -> `D_heaven_mid.png` on the registration chain; seal 悟空 (崇羲篆體 zhu); heads from `mama_B_expressions.jpg`, `lj_C_expressions_mouths.jpg` | lit, tool not meaningful | The carving only reads in the first ~20 frames (it is small seal on a busy blue-green face). The two heads are faint and fall in the dark outside the pool: read as "a face under the seal" on a still, as a smudge at speed. Drop them (`HEADS = []`) if the lead finds them cluttered. |
| J5 | 73 (4816-4889) ok | done | `D_heaven_mid.png` keyed, laid into a bare aged sheet at the far plate's rect (192, 1936) x0.34 (= `D_heaven_far` geometry); 一通百通 in LXGW WenKai; seal 悟空 | page alone (HL_NOLIGHT) at the end: 7.5 % vs budget 20: ok. Lit reads 70-85 % (tool takes the vignette as ground). | While the camera is still close (201.1-201.4) the first characters sit over the range's right side before it shrinks away from them. |
| I3b | 57 (4431-4488) ok | done | `D_banquet.png` keyed onto aged paper | plate ~21 % of its sheet (PLATES.md); lit reading not meaningful | The banquet plate's clean court hand is the least brushy plate (PLATES.md); under the torch it reads as a lit stage set. Chair legs touch the frame's bottom edge. |

## Notes per shot

**K3.** Frame = spread at 0.445 page px per 1080p px, spread px (155, 385) at frame (0, 0); the entry columns (p1 cols
5-6) sit right of centre, x 1290-1460 at 1080p. Torch held still on the entry (pool r 470, stretched 1.55 vertically),
ambient 0.075. The strike: ONE `stroke` drawn top to bottom over 8 frames, the last on the onset of "breath" (216.52):
down the number-and-name column (魂字一千三百五十號 孫悟空) and out in a hook (勾, as in ch.3 "一概勾之") across the foot
of the note column (該壽三百四十二歲 善終); wet darkening dries back, then a small capillary halo creeps for ~0.7 s.
My path differs from the plate's `E_ledger_strike_*` diagonal (that one missed 孫悟空). Lyric small, bottom, in the dark
left half. Nothing else moves.

**K5.** Static frame (built once in setup): the left page (p8) at 0.38, its bare column (page x 220-415) at frame
x 790-865 (1080p), the book's outer edge at x 710 with a soft contact shadow, beyond it the dark bedspread (blurred
aged paper x 0.3). Torch on the bare column, ambient 0.06. Nothing moves on 225.254. Lyric "it wasn't there on any"
(word onsets; "line" falls after the cut) small, lower right, in the dark, away from the bare column.
NOTE FOR L1 (pull back out of the ledger): my last page is `work/heaven/ledger/E_ledger_p8.png` (the plate's p4
layout and paper, numbering continued to 1391); the plate's `E_ledger_p4.png` differs only in the entry numbers/ages.

**K4.** Spread at 0.29, centred. Turn = 6 frames on twos (3 drawings at 36, 93, 150 deg), leaf front = the left page
just read, back = the next right page, under it the next left page; panels shaded 0.62-1.0 by tilt; soft shadow
blurred with height. Landings: "page" 218.22, "looked" 220.92, wooden hit 221.805 (frame 5324 is the first landed
frame). Spreads: (p1 struck | p2) -> (p3 | p4) -> (p5 | p6) -> (p7 | p8, last). Holds 2.4 s on the last spread.

**K2b.** Starts at 212.1 (frame 5091; the script renders any t, so the splice point can move). Push in a Scene on the
composited plate: (2470, 1730, zoom 0.72) -> (2633, 1955, 1.06) on a sine ease that ends 0.25 s after the cut, so it
is still drifting very slowly into K3. Painted register inner frames (plate px): left TL (2297,1863) TR (2579,1849)
BR (2662,2050) BL (2366,2074); right TL (2610,1850) TR (2891,1847) BR (2969,2054) BL (2676,2045). Torch anchored on
the page at (2600, 1900) r 1150 plate px, so the pool widens with the push. The bass cut (211.515) is before 212.1:
nothing in K2b marks it.

**J2.** Scene on the mid plate (keyed, on aged paper); the carved close plate laid over it at its registered rect
(786, 242), scale 1/2.121, opacity 1 above zoom 1.55, 0 below 1.05 (both under 1:1 there, so the handover is
invisible). Camera (mid px): (1878, 640, zoom 2.05) -> (2300, 1100, 0.55) on a sine ease ending 0.12 s after the
cut; 花果山's stone stays upper centre. Torch anchored on 花果山 (mid 1880, 820, r 560), ambient 0.16: at the end it
is one lit peak among dark neighbours. Seal 悟空 pressed on the downbeat kick 190.885 (full), echoes at 191.51 and
192.37 (decay 0.55), frame-fixed in the sky: (1440, 250), (1650, 470), (330, 200) at 1080p. Heads 230 px, pale ink,
10 frames from each echo. No chop falls inside J2 (nearest 189.505, 200.675): no mis-registration in this shot.

**J5.** Scene on a bare aged sheet the size of the far plate, the keyed mid plate as a layer at (192, 1936) x0.34.
Camera (far px): J2's last framing (974, 2310, zoom 1.62) -> whole sheet (2752, 1536, 0.3516), inout, settling at
202.70; then still. Rubbing flip 4 frames from the stutter chop 200.675 (frames 4817-4820). Torch: from 花果山 (r 420)
opening to the page (r 1250, centre) with the pull-back. Inscription: 一通百通 vertical, region x 1210-1380 (1080p),
each character blooms on its onset (200.735, 201.09, 201.62, 201.965); seal on 202.03, faint re-press (decay 0.35)
at 202.46, 108 px to the left. Inscription and seals sit under the lyric switch.

**I3b.** Starts at 184.6 (frame 4431); the script renders any t, so the splice can move. Plate at 0.56 (1080p px per
plate px), plate px (-178, 70) at frame (0, 0). Torch r 520 drifts (inout over the whole shot) from the table (plate
1480, 1060) to the empty chair (1585, 1600). Lyric small at the top, centre-right.
**EMPTY CHAIR (for I4):** plate px bbox (1345, 1351)-(1787, 1985), seat centre (1590, 1640) in `D_banquet.png`
(3072x2048). In I3b's frame (1920x1080): bbox (853, 717)-(1100, 1072), seat centre (990, 879); at 960x540 halve.
Mapping: frame = (plate - (-178, 70)) * 0.56.

## Splits
I3b = frames 4431-4488 (57; I3a is 4391-4430, 40 frames). K2b = frames 5091-5131 (40; K2a is 5053-5090, 38 frames).
All seven files verified: 960x540, 24 fps, exact frame counts.

## Page art (for the room team)

Built by `shots/_heaven_pages.py` -> `media/comp/pages/` (+ `pages.json`). Both are flat double pages at the open
book's spread aspect (1.9:1, gutter at the centre with a soft fold shadow), on 2026 aged paper, UNLIT (light them in
the room comp).
- `I2_page.png` 5504x2897: the heaven spread (D_heaven_mid keyed, rows 87-2984). 花果山's stone at (1880, 365).
- `J1_page.png` 3392x1785: the 花果山 spread (B_master, rows 67-1852), 千字文 lines 1-80 cut into the mountain's faces
  (崇羲篆體 44 px, raking light from the upper left, cinnabar in the cuts), all on the LEFT page.
  **Marked character: 草**, box (627, 1384)-(671, 1428) px, centre **(649, 1406)** px = (0.191, 0.788) of the spread
  (left page). `J1_char_mask.png` = its cut (0..1, same size as the page) for your own light;
  `J1_page_charlit.png` = the same page with only that character lit (low raking light, warm, fuller cinnabar).

## Spend
$0.00 generated (no model calls: everything is plates + code). `tools/gen/spend.py` total unchanged by this team.

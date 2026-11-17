# LOG: FIX ROUND 2, ROOM shots (QA_PREVIEW_V1 items 1, 2, 7, 9, 11, 12, 15 + lip-sync)

Render, sheet and frame count: `work/fix2r/do.sh ID --fresh` (frames from docs/shots.json) and `work/fix2r/do2.sh ID --fresh`
(split parts: the script's own T0/T1). Frame strips: `work/fix2r/strip.py`. Pre-fix copies of every edited script and
helper: `work/fix2r/*_before.py`, `work/fix2r/clips_before.json`. Every file below is 960x540, 24 fps, with the exact
frame count (ffprobe). A 1920x1080 still renders for L3, I1, G1, E3, F1, G4 and E1. Spend: **$0** (comp only).

Helpers touched: `_rooms88.py` (RoomShot `sign_on` and `margin_state` hooks; spread kind `egg_close`), `_bed_grade.py`
(`find_lens`, `dehalo`). `_margins.py` was not touched.

| QA # | Shot | Status | What changed | Numbers |
|---|---|---|---|---|
| 1 | L3 (5660-5719) | done | Rewritten. f5660-5669 night black (A1's pre-sign black as one flat tone with paper fibre, no #000, no window ghost). f5670-5672 the 1988 window comes up as the eye adjusts; the sign is held at cinnabar; the attic is at 0.55 of A1's level outside a soft window mask. f5709 (237.840): neon off hard, the bare glass a faint grey on f5709-5710, then night black to f5719. L2 unchanged: polish-1's thumb press already ends lit on f5659 | mean luma: 2.0 (black), 4.7/7.8/10.7 (adjust), 10.7 (hum), 2.5 (grey glass), 2.0 |
| 2 | E3 | done | Mama's beige shoulder and stick painted out with the attic's own dark wash: row tones sampled from the room beside it, one warm hue, falling darker to the left edge, paper fibre on top. The static mask is `media/comp/rooms88/E3_blob_mask.png`, the blob's footprint over all 166 frames. It now reads as a dark soft shoulder; Jade is right of centre. No repaint | - |
| 9 | E1 | done | 86.998 (f2088): the neon flares for 3 frames (sign x1.9 / 1.54 / 1.27 plus a spill into the room) and the camera cuts in on the same frame (x1.16, window kept in frame), then pushes slowly. Mama's hand cannot be retimed to the hit: the take is lip-synced and she sings from 86.3 | - |
| 9 + 7 | F1 | done (hands: not) | The clip's own amber passes are taken out (each frame scaled by the darkest plates' low-frequency light over its own). ONE sweep slams in on 107.975 (f2592): visible on f2592, full by f2595, then it crosses left to right and is gone by ~f2604. Reframed x1.30: her face is on the right third and the window on the left carries the sweep. The hands still press in prayer, not chopping (take) | lip: r 0.52, sharp 0.67, lag_vs_synced +60 ms |
| 9 + 7 | G1 | done | Margins: the shared schedule starts at 1.04 W with a slow ease, so its sheets stayed off-frame until f2994. G1 reads it through `margin_g1`: the sheets enter on f2926 (8-9 px a side at 540p) and creep in; from ~125.6 s it is exactly `margin_state`, so the cut into G2 is unchanged (last frame 154/153 px, as before). Reframe x1.15 -> 1.21: face on the left third; past the plate's right edge, the room's dark tone with a soft fall | paper px a side at 540p: f2925 0, f2926 8, f2955 28, f3058 154 |
| 7 | K2a | done | Comp reframe x1.40 -> 1.43: face on the left third, the book's top edge running right. The book's corner still ends just inside the right edge | lip: r 0.50, sharp 0.55, lag -23 ms |
| 7 | I4 | done | Polish-1 still read as a full-frame Mama. Now Mama is a ghost: her face (an ellipse registered on Jade's) at 70 % for frames 0-7 and 35 % on frame 8, gone on frame 9; her hair and red ground only at 30 % of that. Jade's own dark lines read through from frame 0 (a darken min) | - |
| 6 / 11 | I1 | done | No dissolve. Frame 0 (the kick 177.193) is H6's bare paper, the same sheet (Paper 'new', BOOK_PAPER_SEED). From frame 1 it is a torch pool: a hard-edged ellipse (4 px edge, slightly uneven rim, a core falloff on the paper) with the dim room outside. The room is darker on f1 and present on f2. The edges close in over f1-f10 at x2.5 on the lit page, then pull back to the I1 framing over f10-f26. The paper becomes the page in 2 frames, and the hard pool hands over to the room's own pool. Torch glow removed (`dehalo`: the radial floor of the light around the lens is subtracted; the lens is a flat pale painted disc) | - |
| 11 | K1, L1 | done | `dehalo` on the torch head (K1 tracked in a box; L1 on the room plate before its warp). L2's torch points away and has no halo: not changed. I1's straight light-shaft from the torch (in the take) remains, fainter | - |
| L1/K5 | L1 | done | Matched to the book fixer's final K5. L1 now reads SC/BARE_X/FX/Y0/POOL from `shots/K5.py`, so it follows K5 if K5 moves again. QK5 = p8 corners mapped by (page - (BARE_X - FX/SC, Y0)) x SC; the torch on the flying page is K5's (page (311, 760), r 467 page px, 1.30). Frame 0 = K5's last frame | mean abs diff K5 last vs L1 f0: 0.76/255 |
| 12 | G4 | done | No halo. The ring is absent until 0.75 s before 'wear'. It comes in already touching the crown and drops onto the brow, landing on the frame containing 'wear' (f3447). It is a nearly edge-on band of the head's width: only the front arc is drawn (it crosses the forehead), and the far arc is hidden behind the head. It tightens 3.5 % on the next beat (144.111, f3458). The head's tuft is now a round bun | - |
| 15 | F6b | done | Reflection mixed into the glass at 25 % (no max-lighten), blurred 2.2 px, dusk-violet like the pane, mirrored and offset into the pane beside her. Her hand and the reflection's hand wave on the same frames | - |
| 9 | C5a | partly | The egg page is mapped close (`egg_close`: the egg large on the left page, its wash deepened). The egg now shows on the open book under her fingers. Her hand at her lips ("shh") is the take: not fixable in comp | - |
| lead | D2d, G3, G4 | done | Re-rendered --fresh for the new triggers and seal face. D2d's re-pose and jolt now use `on_frame(63.980)`: the bow lands on f1535, the frame containing the beat | D2d frame diff f1535 6.6 (bow) |

## Lip-sync (`tools/review/lipsync.py --maxlag 0.35`, on the comp files, vocals stem)

| Shot | before (QA) | 2-frame shift | **kept: 1-frame shift** |
|---|---|---|---|
| B1 | +102 ms, r 0.30 | -107 ms, r 0.49 | **-65 ms, r 0.49, sharp 0.46** |
| E3 | +102 ms, r 0.37 | -107 ms, r 0.53 | **-65 ms, r 0.54, sharp 0.60** |
| G1 | +102 ms, r 0.33 | -65 ms, r 0.36 | **-23 ms, r 0.35, sharp 0.40** |

The 2-frame shift overshot: the correlation peak jumped by 5 frames. One frame lands all three within -3..-1 frames,
and r rises. clips.json keeps the old value as `t_clip0_fix1`.

Faces that do not follow the words:
- **D3b**: pushed in (x1.25 -> 1.32 on both faces) and retimed +0.25 s. The mouth box on Mama now reads -273 -> -23 ms, r 0.56, sharp 0.70.
- **K1**: pushed in (x1.22 -> 1.30). The mouth is still a 3/4 profile about 30 px wide and does not measure (box r 0.28, weak). Let it play as voice.
- **G3**: left as is. Her face looks down under the top margin and the mouth is not visible.
- **F4a**: left as is. The mirror mouths barely move (articulation 0.03).

G3, F4a and K1 can play as off-screen voice.

## Not done (regeneration-level or out of scope)
- F1: the hands chop. The take has hands in prayer, so this needs a new take.
- E1: the hand's first movement on 86.998. It cannot move without breaking the lip-sync, so the hit is marked by the cut-in and the flare instead.
- C5a: "shh" vs blowing (the take).
- A2: missing props, floorboard lines and the flat pan.
- The neon sign's legibility (mirror text at 540p).
- I1: the straight light-shaft in the take.
- The splice tooling (QA 5), the lyric layer and the book or stage items belong to other agents.

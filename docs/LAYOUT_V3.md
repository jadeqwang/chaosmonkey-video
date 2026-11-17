# Layout v3: re-blocking after the director's review (2026-11-17)

Nothing from v1 is overwritten. The new setups live beside the old ones with a `v3_` prefix:
`media/layout/<set>/v3_<SETUP>_{line,flat,depth,label,lit}.png` + `v3_<SETUP>.json`. `_line.png` is the layout
reference for the image model, `_lit.png` the mood check, `_label.png` names everything, the JSON carries the quads,
faces, hands, lights and (new) the sign, hooks, push and hand-shadow data. How to re-render: `layout/README.md` (v3 section).

Contact sheets (`media/layout/_sheets/`):

| sheet | what |
|---|---|
| `v3_attic88.jpg`, `v3_bed26.jpg`, `v3_car26.jpg` | every v3 setup of the set, label mode |
| `v3_neon_options.jpg` | the blade sign: five placements x (A1 wide, the window zoomed, lit, plan from above, view from the mat) |
| `v3_lap_parallel.jpg` | the eight LAP setups, attic beside bedroom, flat + lit |
| `v3_hand_shadows.jpg` | hand-shadow setups: label, line guide, lit |
| `v3_J4_split.jpg` (+ `v3_J4_split_{line,flat,lit}.png`, 1920x1080) | J4 preview: left half attic `v3_LAP_front`, right half bedroom `v3_LAP_front` (centre 960 px of each) |

Tell the model, beyond every guide (unchanged from v1): the people are the on-model characters, not mannequins; hands
are real hands (the guide's are mitts); keep the camera, positions and sizes. Heights are true: Mama 160, little Jade
108, Jade 165, the daughter 102 cm. **New: from A3b on, Mama wears no apron in any attic shot**; the apron and a towel
hang on the hook rail by the stair door.

## What changed, in one screen

1. **Neon sign** is a vertical blade on brackets, perpendicular to the facade, lettering on both faces. From inside it
   is a narrow wedge of red. Its lettering is read from the side, so it is **not mirror-reversed** any more (the A1
   line in `shots.yaml` still says mirror-reversed).
2. **Hooks**: a rail of four hooks on the door gable, right of the stair door as seen from the room. A3 is two setups.
3. **Lap storytime** replaces every side-by-side two-shot in both rooms: eight setups, identical lens / distance /
   framing in the attic and the bedroom.
4. **D9** is the fall: three poses in one wide camera.
5. **Car**: two forward-facing child seats on the back bench; the daughter in the rear-right one, the rear-left one empty.
6. **Hand shadows** are cast by the real light (attic: the part of the blade the page can see through the window;
   bedroom: the flashlight), with hand position, light position and shadow polygon in the sidecar.
7. **Endings**: L2 / L2b are the blanket, matched; A1 / L3 keep the wide.

The storytime place in the attic moved: Mama sits on the lower half of little Jade's mat (pelvis at x 2.6, z -1.5),
turned 18 degrees away from the window, so the neon comes over her left shoulder onto the page. The pillow end of the
mats is outside the beam: little Jade lies awake in the dark (A1, A2), story happens in the light.

## A. The neon blade (attic88)

Model (`layout/sets/attic88/layout.js`, `SIGN_V3`): a blade 0.70 m deep x 2.6 m tall x 0.12 m thick, on two bracket
arms, standing 0.18 to 0.88 m out from the wall, its top 0.25 m above the window head, running down a storey. Top to
bottom on each face: 酒, 家 (0.5 m blocks, at window height), then CHIN. / IND. / SPEC. / REST. stacked. The sidecar key
`sign` gives both faces and the six lettering blocks as quads (px + world, TL TR BR BL as read), which face the camera
sees, and the effective light point.

One fact decides the placement: through a 0.8 m window from 5 m back you only see what hangs almost straight out
from the glass. A blade beside the window, clear of the glass, cannot be seen from the door end at all.

| option | where | in A1 / L3 | its light |
|---|---|---|---|
| **A (recommended, built into every v3 setup)** | in front of the far third of the window (z -1.0) | a narrow wedge right of the centre mullion: the lettering strip is about 48 px wide by 300 px tall in a 265 px window | lands on the lower half of the mats and the boards in front of them; the lap, the page and the D9 stack are in it |
| B | in front of the near (mats') third | a sliver at the right jamb, half hidden | covers the mats completely |
| C | beside the window, far side, clear of the glass | the widest, clearest wedge (left pane) | misses the mats: falls on the open floor toward the door |
| D | beside the window, mats' side, clear of the glass | not visible; only the reveal glows | covers the mats |
| E | as A, 0.6 m further out | narrower wedge, further right | lower and weaker |

Recommendation: **A**. It is the only placement that both shows in the A1 / L3 wide and lights the storytime. C looks
best in the wide but leaves the mats dark, so every storytime shot would lose its motivated light. If the wedge in A1
reads too thin, the fix is the camera, not the sign: D9's camera (lower, closer, more oblique, `v3_D9_a`) shows 酒家
nearly twice as wide.

| setup | lens | camera intent | tell the model beyond the guide | serves |
|---|---|---|---|---|
| `v3_A1` | 32 | Wide from the door end; window lower right (0.8/0.74); little Jade awake under her blanket, a dark shape | Only the window carries light. In it, a tall narrow wedge of cinnabar neon (the blade seen edge-on-ish), lettering foreshortened, readable only as strokes; dusty glass; red on the window reveal and a faint rake across the foot of the mats | A1 |
| `v3_L3`, `v3_L3_off` | 32 | Identical camera; Mama and little Jade asleep under blankets; apron and towel on the hooks | Neon on, then off at 237.840 (`_off` is the end state) | L3 |
| `v3_A2` | 28 | Low across the floorboards as v1 A2 | Little Jade lies awake on her back, eyes open to the rafters; the pillow end is dark, red only on the lower blanket | A2 |
| `v3_neonopt_{A..E}`, `_plan`, `_mat` | 32 / 35 / 28 | Comparison only | not for generation | sheet |

## B. The apron hook (attic88, A3)

| setup | lens | camera intent | tell the model beyond the guide | serves |
|---|---|---|---|---|
| `v3_A3a` | 24 | From behind and over little Jade (propped on her hands, head turned to the door, back of her head lower centre) across the dark attic: the stair door a tall warm slot, Mama in it; the empty hook rail on the wall right of the door | Mama wipes her hands on her apron; tungsten from the stairwell the only warm source; the hooks are small: four pegs on a board | A3 (first beat) |
| `v3_A3b` | 40 | Closer, from inside the room: Mama at the rail, right hand on the hook, the open door a warm slot at frame left | She has taken the apron off and is hanging it by its neck loop; a towel already on the next hook; she glances back over her shoulder toward the mats. No apron on her from here on | A3 (second beat) |

Hook positions (px and world) are in `hooks` in every attic v3 sidecar; hook 1 = apron, hook 2 = towel.

## C. Lap storytime: the same eight setups in both rooms

Pose (`layout/engine/lap.js`): the mother sits with her legs out in a loose V; the child sits between them, back
against her chest, 7 cm to her right so the mother's face clears the child's head; the book rests on the child's
thighs, tipped 36 degrees toward them. In the attic Mama holds both lower corners from underneath. In the bedroom
Jade sits on the rug with her back against the side of the bed, her right hand under the book, the flashlight in her
left hand held out left of the book (0.36 m from the gutter), which puts the light on the same side and at about the
same angle as the neon. Cameras are defined in the mother's frame, so lens, distance and angle are identical.

| setup | lens | camera intent | attic `v3_...` serves | bedroom `v3_...` serves |
|---|---|---|---|---|
| `LAP_front` | 40 | Front two-shot from 1.95 m, slightly above eye level; child's face lower centre (0.47/0.45), mother's above and right (0.53/0.29); book along the bottom | B2, C3, D3b, E6; B1 / E1 as the wider option; J4 left half | I1, K1; J4 right half |
| `LAP_34` | 32 | Three-quarter from the light side, 40 degrees round, 1.55 m | B2, C3, E1 (Mama's finger comes round to the nose) | I1, K1 |
| `LAP_ots` | 35 | Over the mother's left shoulder, past the child's head, down onto the spread; the mother's head soft at frame right. Camera rolled 25 degrees toward the page. Page quads in the sidecar | B3 (start of the push), D3a | I1, K2 (start of the push) |
| `LAP_ots_push_end` | 35 | Square on to the spread, 0.39 m from the gutter: the spread exactly fills the frame (quads at the frame edges) | B3 (end), C5b | K2 (end); I1 reversed (out of the white page) |
| `LAP_child_cu` | 85 | Child's face centred (0.5/0.46), mother's chin and shoulder above | G5 "Yes", B1, E3, G1 | I3 (the eyebrow), K2 first 1.5 s |
| `LAP_mother_cu` | 85 | Mother's face (0.5/0.36), top of the child's head at the bottom | Mama's lines in B2, C3, E1, G4 | I4a |
| `LAP_profile` | 35 | Profile two-shot from the mother's right, 1.35 m; she leans over the child's shoulder to the page | C5 (she blows; the window and the blade behind them, contre-jour) | K1; parallel to C5 |
| `LAP_hands` | 50 | Top-down onto the spread from 1.05 m; both pairs of hands at the bottom of the pages; the child's hair fringes the bottom edge | base for C2, G3, G4 | base for I2, I4b, J1 |

Beyond the guide, attic: red neon from frame right and slightly behind (it rims Mama's left cheek and shoulder); the
open page is the brightest thing and throws a soft red bounce up into both faces; no apron. Bedroom: one small
flashlight from frame right; the page bounce is white; jacket orange and strawberry pink the only saturated colours.
Do not copy the mitts: the mother's hands cup the lower corners of the book, the child's rest on the bottom of the pages.

Extra lap setups:

| setup | lens | camera intent | tell the model beyond the guide | serves |
|---|---|---|---|---|
| `attic88/v3_F3b` | 50 | Little Jade in the lap, face at 0.6/0.38, seen from 13 degrees above, to match the car | Blows across her flat palm; hairs fly toward frame left | F3 match cut |
| `_sheets/v3_J4_split_*` | 40 | Left half attic `v3_LAP_front`, right half bedroom `v3_LAP_front`, each the centre 960 px | Red half, white half; the two pairs in the same pose | J4 |

The push (B3, K2): `push` in `v3_LAP_ots_push_end.json` has the start and end camera. The line from start to end swings
18 degrees onto the page's normal and rolls level as it moves in. The real end position is in front of the child's
face, so the last third is best done as a 2D warp of the painted page using the quads; the guide hides both heads.

Not staged as its own setup: E5 (the whisper). In the lap Mama's mouth is already by the child's ear; use
`LAP_child_cu` with Mama leaning in at frame right. v1 L1 (the daughter asleep against Jade's arm, book on the
blanket) no longer follows from the lap blocking and needs a decision before it is repainted.

## D. D9: the fall (attic88)

One camera: 28 mm, wide and low from the middle of the attic, the window behind the action.

| setup | pose | tell the model beyond the guide |
|---|---|---|
| `v3_D9_a` | Little Jade on a wobbly stack of nine textbooks (0.34 m) on the boards off the foot of her mat: one leg up, hand shading her eyes; Mama on the mat behind with the book, laughing | The child is silhouetted against the window and the neon blade; opera 亮相 pose copied from the page; the stack visibly crooked |
| `v3_D9_b` | The stack shoots out toward camera; she tips backward, arms up; Mama already on her knees, both arms out | Mid-air, books sliding; Mama's face toward the child |
| `v3_D9_c` | Mama kneeling has her under the arms, little Jade leaning back into her, legs out; books scattered toward camera | Both laughing; no apron |

## E. The car (car26)

Rear bench: two forward-facing child seats, outboard left and right (`cabin(shot)` in `build.js`). Jade drives, front
left. The daughter is rear right, behind the empty front passenger seat. `seating` in each sidecar gives the px of
her seat, the empty seat and both front headrests.

| setup | lens | camera intent | tell the model beyond the guide | serves |
|---|---|---|---|---|
| `v3_F1` | 28 | High between the two front headrests, looking back and a little down over the seatbacks: headrests frame both edges, the daughter left of centre (0.32/0.47), the empty child seat right of centre | Deadpan rap, hands chopping; she looks up at the lens; the second car seat is plainly empty, harness hanging open; rear window and dusk road behind | F1 |
| `v3_F2` | 24 | As v1 F2: toward her right rear window, the pane a shadow screen, the daughter in profile at frame right | unchanged | F2 |
| `v3_F3a` | 40 | Tighter, past the front passenger headrest (a dark soft shape down the left edge); face at 0.6/0.38 | Plucks at her hair, blows across her open palm; the shell of her car seat round her head | F3 |
| `v3_F4a` | 26 | Looking up at the rear-view mirror; true reflection | In the glass: Jade's face large at the left end, the daughter small and deeper at the right end in her car seat, the back bench between them | F4 (first half) |
| `v3_F4b` | 18 | Wide from the tailgate: backs of the two child seats, Jade beyond | Every pane a lit screen | F4 (second half) |
| `v3_F5` | 18 | Reverse wide from above the dashboard: Jade large at frame right, the daughter small on the back bench at left, the empty seat between | Panes go dark one per beat | F5 |
| `v3_F6a` | 24 | From the middle of the back bench, between the two child seats: the windscreen as stage | unchanged | F6 (first half) |
| `v3_F6b` | 24 | From the gap between the front seats, driver side: the daughter waves, her reflection waves in her side window; passenger headrest at the left edge | True reflection in the guide | F6 (end) |

## F. Hand shadows from the real light

All on the `LAP_hands` camera. `hand_shadow` in the sidecar lists, per caster: `hand_px` / `hand_world`, the point of
the page under the hand, `height_above_page_m`, `shadow_polygon_px` and `_page_uv` (plus `holes_*` for the monkey's eye,
ear and mouth), `offset_on_page_m`, light elevation, magnification, soft-edge width; `light_world` / `light_px` is the
light. The monkey is the traced `design/characters/monkey/handshadow_silhouette.jpg` as a cut-out card
(`layout/assets/monkey_silhouette.json`).

| setup | casters | hand above page | shadow offset | size | edge |
|---|---|---|---|---|---|
| `attic88/v3_C2` | monkey card (little Jade's two hands), 14 cm tall, over the left page | 4.0 cm | 5.7 cm toward frame right | x1.04 | soft: 4 cm along the throw, 1.3 cm across |
| `attic88/v3_G3` | little Jade's flat left hand over the left page | 2.4 cm | 2.4 cm | x1.02 | soft: 2 cm |
| `attic88/v3_G4` | little Jade's head, folded forward over the left page; Mama's ring hand between window and head | head 9 cm; ring 19 cm | 14 cm; 34 cm | x1.1; x1.27 | head 10 cm; ring 21 cm |
| `bed26/v3_I2` | two monkey cards: the daughter's (10 cm) over the left page, Jade's (13 cm) over the right | 3.9 / 4.3 cm | 3.2 / 7.5 cm | x1.20 / x1.23 | hard: 4 to 5 mm |
| `bed26/v3_I4b` | the daughter's hand over the left page | 8 cm | 10.7 cm | x1.46 | 9 mm |
| `bed26/v3_J1` | the daughter's fingertip on the page | touching | 0 at the fingertip | | hard |

What is physically plausible:

- **The shadow is never under the hand.** It sits on the side away from the light, offset = height / tan(elevation).
  In the attic the neon reaches the page at about 35 degrees, so offset is about 1.4 x height; with the flashlight at 30 to
  50 degrees it is 0.8 to 1.7 x height. Hand and shadow only touch where the hand touches the page (J1). A shadow that
  "connects" means a hand 2 to 4 cm up, not 10.
- **The hands must be parallel to the page.** An upright hand profile in raking light smears to about three times its
  width. The cards are held flat over the page, wrists toward the reader.
- **Attic: same size, soft.** The blade is 1.8 m away, so the shadow is the size of the hands (14 cm monkey on a 27 cm
  page: "big" is half the page height, not more). The visible blade is a tall source, so the edge softens by about
  the hand's height along the throw: at 4 cm the eye and mouth gaps are still open, by 8 cm they have closed.
- **Bedroom: larger, hard.** The flashlight is 0.3 to 0.45 m away: x1.2 at 4 cm, x1.45 at 8 cm; the nearer hand
  throws the bigger monkey. For two "identical" monkeys the daughter's hands go nearer the light or higher.
- **G4 does not work as real light.** A 4 cm ring held 19 cm above the page has a 21 cm soft edge: no shadow at all.
  To read, the ring must come within 3 to 4 cm of the page beside the child's head-shadow, or the ring shadow is a
  compositor's drawing placed on the head-shadow's brow using `shadow_centre_px`. The head-shadow itself (9 cm up) is a
  soft 20 cm blob on the right page, usable.

## G. Endings

| setup | lens | camera intent | tell the model beyond the guide | serves |
|---|---|---|---|---|
| `bed26/v3_L2` | 40 | From the foot of the bed, 2.4 m, 32 degrees above: the daughter asleep, head away from us at upper right; Jade kneels at frame left and draws the blanket up | Replaces the flashlight insert; her hands on the turned edge of the blanket (`blanket.edge_centre_px`), moving toward the child's chin; dark room, blue from the blind | L2 |
| `attic88/v3_L2b` | 40 | The same camera relative to the sleeper: little Jade asleep on her mat, Mama kneeling at frame left with the blanket edge | Red neon; no apron; cuts to or from `v3_L2` on the pull | L2 (attic half) |
| `attic88/v3_L3`, `v3_L3_off` | 32 | The A1 wide | see A | L3 |

## Physically awkward, flagged

- **A1 wedge is thin** (see A). Lettering in the wide is strokes, not words; 酒家 reads in D9, LAP_profile and from the mat.
- **Car, low front cameras are impossible.** From anywhere on the centreline forward of the seatbacks and below
  about 1.3 m, the front passenger seatback hides the child sitting behind it. F1, F3a and F5 therefore sit just
  under the headliner and look 14 to 17 degrees down. `v3_F3b` was given the same down-angle so the match cut holds.
- **Mirror (F4a)**: the reflection is exact. With the mirror tilted to hold the child seat, Jade's face fills the
  left fifth of the glass and the daughter's head is a little under half that size at the far right, with the
  back bench between them. They are not equal in scale; if both faces must sing legibly, the mirror shot wants to be tighter on the right end or a split.
- **LAP_front light**: with the page catching the neon, the faces are side- and back-lit; frontal light on the faces
  comes only from the page bounce. That is the look in the lit previews, not an error.
- **LAP_profile, bedroom**: the camera stands where the nightstand is (hidden in the guide).
- **G4**: as above. Also in the top-down the child's head covers most of the left page.
- **LAP_hands**: the child's hair covers the bottom centre of frame (about a fifth of the height in G3).

# SETS_V4: the set bible for preview_v4 (attic88, bed26, car26)

Written 2026-11-18 by the SETS team (Claude Opus) for REVISION_V4 §1.1 / §4. One source of truth per room: the numbers
below are copied from the code (`layout/sets/<set>/v4.js`, `layout/sets/attic88/layout.js`, `layout/sets/car26/layout.js`);
if this file and the code disagree, the code wins and this file is stale. Units metres, y up, floor y = 0.

## How to use this (room teams: ATTIC, BED+CAR)

For every keyframe give gpt-image-2, in this order:
1. the shot's guide `media/layout/<set>/v4_<SHOT>_line.png` (structure; "keep the camera, every object's position and size");
2. the set's painted master plate `media/kf/v4/_sets/<set>_master.png` (look, palette, what every object looks like);
3. the character sheets / accepted v3 heads as before (never v1/v2 images of little Jade or Jade; never a real photo);
4. optionally `v4_<SHOT>_lit.png` for where the light comes from.
Then run the set check (below) on the keyframe before any video is made, and on the last frame of every video take.

Tell the model, beyond the guide (all sets): the people are the on-model characters, not mannequins; the mannequin's
ball joints, five-finger hands and hair caps are placeholders: real hands (five fingers, no webbing), real hair per
canon (little Jade: two small ponytails half up, the rest down, curtained to the sides, NO fringe; Jade: long, parted
slightly off-centre, NO fringe; Mama: jaw-length 1980s perm; the daughter: warm brown braids). **Every arm leaves its
own shoulder**: the guide shows shoulder, upper arm, elbow, forearm, hand as one chain; keep that chain, do not let an
arm enter from a frame edge that is not where that body is. Heights are true: Mama 160, little Jade 108, Jade 165, the
daughter 102. Glasses on Mama and Jade (the guide's rings). Nothing in the room may be added, removed or moved; if an
object is in the label render it must be in the picture at that place; if it is not in the label render it must not be
in the picture.

Renders per setup (1920x1080): `_line` (give to the model), `_flat`, `_depth`, `_label` (names), `_lit` (mood), and the
sidecar `v4_<SHOT>.json`: camera (matrices, lens), `objects` (every labelled thing the camera sees: frame fraction, screen
bbox, centroid, world box), `heads`, `hands`, `joints` (shoulder, elbow, wrist, hand, hip, knee, ankle per figure, px +
visible), `contacts` (B1: little Jade's hand on Mama's forearm, distance in cm), `book` quads, `panes`, `lights`, `sign`,
`hooks`, `flashlight`, `warnings` (joint limits, reach, blocked faces). Contact sheets: `media/layout/_sheets/v4_<set>.jpg`
(label), `v4_<set>_line.jpg`, set views `v4_<set>_bible.jpg`, J4 preview `v4_J4_split.jpg` (+ `_line/_lit.png`).

Re-render: `node layout/render.mjs --set <set> --prefix v4_` then `sh layout/sheets_v4.sh [label|line|lit]`;
camera table: `python3 layout/camera_table_v4.py`. Bodies: `layout/engine/body.js` (jointed mannequin built on the
v1/v3 pose solver, joint-limit report). v1 and v3 files were not touched by any v4 render.

## Decisions (where the v3 images and the v3 model disagreed)

| # | what | the evidence | decision |
|---|---|---|---|
| 1 | Attic mats' direction | Every preview_v3 frame (A1, A2, B1, L2b, L3) shows little Jade's mat running toward the window with her pillow under it; the v3 3D model had both mats along z with the pillows at the back eaves. | **Mats along x, pillows at the window gable.** L3/L2b are the director's approved attic sleeping place. |
| 2 | Textbooks | The v3 model had two piles (7 books by the pillows, a separate 9-book D9 stack at the mat foot); frames show one pile, beside the pillow by the window (A1, A2) or at frame right of the lap (B2, D3). Under the low slope by the pillows the roof is 1.27 m: a child standing on a 0.34 m stack there would put her head through it. | **One stack of 9**, at (2.92, -0.30): beside little Jade's pillow, in front of the window's near jamb, where the roof is 2.78 m. D9 happens there, silhouetted against the window. |
| 3 | Fallen books | v3 G1, L2b, L3 put the fallen books at lower LEFT; D9 v3 sends them toward camera; nothing agrees with anything. | **Fallen state fixed in `FALLEN4`**: the nine books fanned from the stack 0-1 m toward the D9 camera (into the room, toward the door end). They lie there in D9 c and every later attic shot (E1 ... L3). From the L2b camera they are at frame right, not left; v3 L2b/L3 are wrong on this. |
| 4 | Attic storytime place | Moves with the mats: Mama on the foot half of little Jade's mat at (1.62, -0.92), yaw -18 (facing into the room, window on her left). Neon still comes over her left shoulder, frame right in LAP_front. | as stated |
| 5 | A3a window | v3 A3a shows the window on the side wall while the camera looks at the door gable; the window is in the opposite gable. | **Window not in A3a** (behind the camera); its red light falls on her back and the near boards. |
| 6 | Bedroom | L2 is canon (director). L1 (pillows and bunny at frame left behind them) and K1 (nightstand frame left) agree with a lap place on the rug against the bed's window side; I1 (nightstand frame right), K1 (bunny frame right), K2a (bunny on the bed at left beyond the nightstand) disagree. | **Room rebuilt to L2**; storytime on the rug against the bed's left rail, facing -x. From the LAP cameras: headboard, pillow and bunny frame left, nightstand far left, door light far right, flashlight frame right. I1/K1/K2a/I3a/I4/J1 v3 frames fail the set check on these points. |
| 7 | L2 camera | Solved from the v3 L2 frame: the bed's vanishing point (above frame, right) gives a camera yawed ~20 deg left of the bed axis and pitched ~37 deg down; the headboard's width (390 px for 1.06 m) gives ~2.9 m to it. | **Camera at (0.68, 2.10, 0.76)**, above the right side of the bed's foot, looking down-left. The guide overlays the v3 frame within about 30-50 px (headboard, bunny, Jade's head; the v3 pillow is drawn larger than ours). The attic L2b camera is the same camera in the sleeper's frame. |
| 8 | Bedroom bed | v3 model had a toddler bed against the right wall; L2 shows a twin bed with a wooden headboard standing free on the back wall with floor on both sides. | twin, 1.0 x 2.0 m, mattress top 0.50, headboard top 0.86 (just above the pillow, as in L2) |
| 9 | B1 | v3 B1: Mama's back at frame right and an arm entering from the bottom edge with no visible shoulder. | **Over Mama's left shoulder, close**: her shoulder, upper arm and elbow in the right foreground, the forearm running forward-left to little Jade, who kneels in front of her left knee facing her (and us) with her right hand on it (contact 3.5 cm in the sidecar). |
| 10 | Car | v3 car model and frames mostly agree (two child seats, she rear right). v3 F1 frames do not show the empty seat. | Cabin unchanged; v4 F1 keeps the empty seat right of centre and replaces the arms with the brief's rap body language. |

## 1. attic88: the attic above the restaurant, Netherlands, 1988, night

Views: `media/layout/_sheets/v4_attic88_bible.jpg` (plan before / after D9, the window gable, the door gable, the back
slope), single files `media/layout/attic88/v4_{PLAN,PLAN_fallen,ELEV_window,ELEV_door,ELEV_back}_label.png`. Plan is
drawn north (-z) up, the window gable at the right (+x).

Shell: 7.0 m (x, door gable at x -3.5, window gable at x +3.5) by 5.6 m (z, eaves at +-2.8); knee walls 0.9 m, ridge
3.0 m along x; rafters every 0.6 m, purlins at mid-slope, ridge beam, collar ties every second pair at 2.25 m; floorboards
along x, the cracks over the kitchen (x -2.4..2.9, z -0.45..1.7) glow warm from below.

| object | where (centre, m) | size / notes |
|---|---|---|
| window | x 3.5, z -0.8, sill 0.45 | 0.8 x 0.8, 2 x 2 dusty panes, the one opening; it looks onto the street |
| neon blade sign | outside, plane z -1.0, 0.18-0.88 m out from the wall, y -1.1..1.5 | red, 酒 家 at window height then CHIN. IND. SPEC. REST.; seen from inside as a narrow red wedge in the right half of the window; lettering not mirror-reversed |
| stair door | x -3.5, z 0, 0.76 x 1.9 | opens outward over the stairwell; warm tungsten stairwell beyond |
| hook rail | x -3.5, y 1.42, z -0.64..-1.06 (4 hooks) | right of the door as seen from the room; apron on hook 2 and towel on hook 3 from A3b on (empty in A1, A2, A3a) |
| little Jade's mat | x 1.10..2.85, z -1.35..-0.55 | 0.8 x 1.75, along x; pillow at x 2.65 (under the window) |
| Mama's mat | x 0.95..2.90, z -2.30..-1.40 | 0.9 x 1.95, beside it under the low slope (roof 1.3-2.0 m there), pillow at x 2.7 |
| quilts | on the mats | little Jade's: navy cotton, small flower print. Mama's: beige, folded at the foot of her mat unless she sleeps |
| textbook stack | (2.92, -0.30) | 9 school textbooks, 0.34 m, crooked. Stacked before D9 (A1 ... D9 a) |
| textbooks fallen | from the stack 0-1 m toward the room (direction -0.87, +0.49) | D9 c and every later shot; book positions in `FALLEN4` (attic88/v4.js) |
| small TV on a crate | (0.28, -2.2), yawed 22 | CRT, off, rabbit-ear antenna; under the back slope beyond the mat feet |
| storage boxes | back-left corner (-2.75..-2.2, -2.4) and one at (-1.0, 2.35) | cardboard |
| rice sacks | (-2.85..-2.35, 1.55..2.35) | three |
| paper piano keys | (0.85, 0.30) | two taped A4 sheets |
| bare bulb | (0.4, 2.2, 0) | off, always |
| storybook | in hands, or closed on the boards at (2.30, -0.40) beside her pillow when nobody holds it | red cloth, 21 x 28 cm |

Light: the neon is the only strong source (red, from the window, from frame right in every LAP setup); the stair door
when open (A3: tungsten slot); warm lines up through the floor cracks; a faint blue night ambient. The pillow end is
below the window sill and darker than the storytime place. In L3_off the neon is off.

Tell the model (attic): "a 1988 Dutch attic above a Chinese-Indonesian restaurant: bare roof boards and rafters, plank
floor with warm light in the cracks, thin cotton sleeping mats on the floor, one small window filled with red neon from a
blade sign outside. No furniture except what the guide shows; no lamp, no bed frame, no rug, no posters."

## 2. bed26: the daughter's bedroom, Austin, 2026, night (rebuilt to L2)

Views: `media/layout/_sheets/v4_bed26_bible.jpg`, files `media/layout/bed26/v4_{PLAN,ELEV_back,ELEV_left,ELEV_right}_label.png`.
Plan north (-z, the bed head) up.

Shell: 4.4 m (x -2.8 left wall .. +1.6 right wall) by 3.6 m (z -1.8 back wall .. +1.8 front wall), 2.6 m high,
blue-grey walls, wooden floor.

| object | where (centre, m) | size / notes |
|---|---|---|
| bed | x -0.2..0.8, z -1.78..0.24 | twin, wooden frame and legs, mattress top 0.50, head against the back wall, floor on both sides |
| headboard | back wall, x -0.23..0.83 | wood, top 0.86 m (a little above the pillow) |
| footboard | z 0.26 | low, wood, 0.56 m |
| pillow | (0.30, 0.57, -1.48) | one, white-lilac |
| bunny | (0.64, 0.6, -1.32) | beige plush, ears up, sitting on the mattress on the FAR (right, door-side) side of the pillow |
| quilt | on the bed | pale lavender-white; turned down when nobody is in bed, pulled up in L2 |
| nightstand | (-0.53, -1.58) | wood, 0.44 x 0.58 x 0.4, at the head on the window (left) side; a cup and a night-light (off) on it |
| window + blind | back wall, x -1.8..-0.8, sill 0.95, top 2.0 | above and LEFT of the headboard; white slatted blind, nearly closed, dusk-blue night between the slats |
| door | right wall (x 1.6), z 0.55..1.4, 2.03 high | open into the room; warm hallway light: the warm source at frame right in L2 and at the far right in the LAP views |
| rug | x -2.05..-0.22, z -1.25..0.65 | fluffy, mauve, left of the bed; storytime and Jade's knees in L2 are on it |
| bookshelf | front wall, left corner (-2.05, 1.65) | behind the L2 camera; visible only in reverse angles |
| flashlight | in Jade's left hand during storytime, held out left of the book; lying on the rug, on, in L1 | small LED, orange body |

Storytime place: Jade on the rug, back against the bed's left rail at (-0.44, -0.42), facing -x (toward the left wall);
the daughter in her lap; flashlight at frame right. From the LAP cameras: pillow, bunny and headboard behind them at
frame left, the nightstand at the far left, the bed's foot and the open door at the right.

Tell the model (bedroom): "a small child's bedroom at night, 2026: twin bed with a plain wooden headboard against the
back wall, a white slatted blind on the window above and left of the headboard, a wooden nightstand at the head of the
bed on the window side with a cup on it, a plush bunny on the far side of the pillow, a fluffy rug on the floor by the
bed, the door open on the right with warm light from the hall. Blue-violet night, the only other light the flashlight."

## 3. car26: compact SUV at dusk on the highway

Views: `media/layout/_sheets/v4_car26_bible.jpg` (plan with the roof off; side section). Cabin unchanged from v3
(`layout/sets/car26/layout.js` CAR): left-hand drive, Jade driving front left; the back bench carries TWO forward-facing
child seats: the daughter in the rear RIGHT one (behind the empty front passenger seat), the rear-left one EMPTY,
harness open. Rear-view mirror at (0, 1.33, -0.43) angled at her seat. Streetlights pass on the right shoulder and the
median (sodium amber), violet dusk sky; positions per shot from `lampsAt(t)`.

Tell the model (car): "the back seat of a compact SUV at dusk: two child car seats side by side on the back bench, she
sits in the right one, the left one is empty; the front headrests in the foreground where the guide has them; amber
streetlights passing outside, violet sky."

## 4. Per-shot cameras (generated from the sidecars by `layout/camera_table_v4.py`)

LAP_* setups are the v3 vocabulary (engine/lap.js): identical lens / distance / angle in the mother's body frame in both rooms (LAP_front 40 mm 1.95 m, LAP_34 32 mm 1.55 m at 40 deg, LAP_ots 35 mm, LAP_child_cu 85 mm 1.15 m, LAP_mother_cu 85 mm 1.35 m, LAP_profile 35 mm, LAP_hands 50 mm top-down). Which LAP setup a shot uses is in its header in the label render. Warnings that remain are listed; a "reach" warning means that hand stops a few cm short of the named target (no contact is implied there).

#### attic88

| setup | serves | lens | camera position (m) | looks at (m) | fixed objects in frame (largest first) | warnings |
|---|---|---|---|---|---|---|
| `v4_A1` | A1 | 32 | -1.70, 1.38, 0.95 | -0.17, 1.05, -0.29 | small TV (off) on a crate, sleeping mat (little Jade), sleeping mat (Mama), window, quilt (little Jade's, navy floral), quilt (Mama's, beige), stack of textbooks, neon blade sign (perpendicular to the wall), pillow (Mama) |  |
| `v4_A2` | A2 | 28 | 1.75, 0.40, 0.15 | 2.78, 0.26, -1.56 | quilt (little Jade's, navy floral), sleeping mat (little Jade), window, pillow (little Jade), stack of textbooks, neon blade sign (perpendicular to the wall), pillow (Mama), sleeping mat (Mama), storybook (closed) |  |
| `v4_A3a` | A3 | 24 | 3.20, 0.86, -0.98 | 1.21, 0.67, -0.87 | quilt (Mama's, beige), small TV (off) on a crate, storage boxes, sleeping mat (Mama), quilt (little Jade's, navy floral), stair door, rice sacks, stairwell (lit), paper piano keys (printout) |  |
| `v4_A3b` | A3 | 40 | -2.05, 1.30, -1.65 | -3.59, 1.41, -0.38 | stair door, towel (on the hook), apron (on the hook), hook rail, stairwell (lit), hooks |  |
| `v4_A4` | A4 | 35 | 0.95, 0.82, -1.25 | 2.76, 0.32, -0.57 | quilt (little Jade's, navy floral), window, storybook (closed), pillow (little Jade), sleeping mat (Mama), stack of textbooks, neon blade sign (perpendicular to the wall), sleeping mat (little Jade), neon lettering block: 家 | joint limit: Mama armR: cannot reach its target (reach 1.04); the hand stops short |
| `v4_B1` | B1 | 32 | 2.12, 1.13, -1.58 | 1.54, 0.18, 0.08 | sleeping mat (little Jade), light through floorboard cracks, storage boxes, quilt (little Jade's, navy floral), paper piano keys (printout), rice sacks |  |
| `v4_B2` | B2, J4 (left half: use v4_J4L) | 40 | 1.14, 1.01, 1.19 | 1.54, 0.60, -0.72 | quilt (little Jade's, navy floral), quilt (Mama's, beige), sleeping mat (little Jade), pillow (little Jade), sleeping mat (Mama), storybook (open), pillow (Mama), small TV (off) on a crate |  |
| `v4_B2_ots` | B2 (over the shoulder, start of the push) | 35 | 1.91, 1.14, -0.72 | 0.91, -0.54, -0.27 | storybook left page, storybook right page, storybook (open), light through floorboard cracks, sleeping mat (little Jade) |  |
| `v4_C2` | C2 | 50 | 1.49, 1.40, -0.53 | 1.49, -0.60, -0.50 | storybook right page, storybook left page, sleeping mat (little Jade), hand-shadow monkey (cut-out card = the two hands), storybook (open), light through floorboard cracks, quilt (little Jade's, navy floral) | joint limit: little Jade armR: cannot reach its target (reach 1.1); the hand stops short |
| `v4_C3` | C3 | 32 | 2.07, 0.96, 0.64 | 1.34, 0.52, -1.17 | sleeping mat (Mama), small TV (off) on a crate, quilt (little Jade's, navy floral), sleeping mat (little Jade), storybook (open), storybook right page, storage boxes, storybook left page | joint limit: little Jade armL: cannot reach its target (reach 1.07); the hand stops short |
| `v4_C5a` | C5a | 35 | 0.18, 0.72, -1.04 | 2.03, 0.50, -0.33 | window, quilt (little Jade's, navy floral), neon blade sign (perpendicular to the wall), stack of textbooks, storybook left page, sleeping mat (little Jade), pillow (little Jade), storybook right page, light through floorboard cracks |  |
| `v4_D2d` | D2d | 32 | 1.87, 1.09, 2.16 | 1.87, 0.82, 0.18 | sleeping mat (little Jade), window, stack of textbooks, small TV (off) on a crate, quilt (little Jade's, navy floral), sleeping mat (Mama), pillow (little Jade), storybook (open), quilt (Mama's, beige) |  |
| `v4_D3` | D3 | 32 | -0.58, 0.98, 0.05 | 1.34, 0.67, -0.43 | sleeping mat (little Jade), sleeping mat (Mama), window, quilt (Mama's, beige), stack of textbooks, pillow (Mama), neon blade sign (perpendicular to the wall), storybook (open), light through floorboard cracks |  |
| `v4_D9a` | D9 | 28 | 0.25, 0.95, 1.25 | 1.88, 0.85, 0.10 | sleeping mat (little Jade), window, stack of textbooks, quilt (little Jade's, navy floral), sleeping mat (Mama), pillow (little Jade), pillow (Mama), quilt (Mama's, beige), neon blade sign (perpendicular to the wall) |  |
| `v4_D9b` | D9 | 28 | 0.25, 0.95, 1.25 | 1.88, 0.85, 0.10 | sleeping mat (little Jade), sleeping mat (Mama), quilt (little Jade's, navy floral), stack of textbooks (toppling), window, pillow (Mama), storybook right page, neon lettering block: 家, quilt (Mama's, beige) | joint limit: Mama armL: cannot reach its target (reach 1.11); the hand stops short |
| `v4_D9c` | D9 | 28 | 0.25, 0.95, 1.25 | 1.88, 0.85, 0.10 | sleeping mat (little Jade), textbooks (fallen, scattered), window, sleeping mat (Mama), quilt (little Jade's, navy floral), neon blade sign (perpendicular to the wall), neon lettering block: 家, neon lettering block: 酒, pillow (Mama) |  |
| `v4_E1` | E1 | 40 | 1.11, 1.02, 1.14 | 1.52, 0.61, -0.78 | quilt (little Jade's, navy floral), quilt (Mama's, beige), sleeping mat (Mama), storybook (open), pillow (Mama), small TV (off) on a crate, pillow (little Jade), sleeping mat (little Jade) | joint limit: Mama wristR: bent 89 deg (max 85) |
| `v4_E3` | E3 | 40 | 1.09, 1.02, 1.15 | 1.50, 0.61, -0.77 | quilt (little Jade's, navy floral), quilt (Mama's, beige), small TV (off) on a crate, storybook (open), sleeping mat (Mama), pillow (Mama), pillow (little Jade), sleeping mat (little Jade) |  |
| `v4_E5` | E5 | 85 | 1.22, 0.73, 0.44 | 1.64, 0.61, -1.52 |  |  |
| `v4_E6` | E6 (keep the v3 take unless the set check fails) | 40 | 1.09, 1.02, 1.14 | 1.50, 0.62, -0.78 | quilt (little Jade's, navy floral), quilt (Mama's, beige), sleeping mat (Mama), small TV (off) on a crate, storybook (open), pillow (Mama), pillow (little Jade), sleeping mat (little Jade) |  |
| `v4_F3b` | F3 (last 12 frames) | 50 | 1.31, 0.90, 0.27 | 1.50, 0.35, -1.64 | quilt (Mama's, beige), sleeping mat (Mama), quilt (little Jade's, navy floral) |  |
| `v4_G1` | G1 | 40 | 1.19, 1.00, 1.17 | 1.60, 0.59, -0.75 | quilt (little Jade's, navy floral), quilt (Mama's, beige), pillow (little Jade), sleeping mat (Mama), sleeping mat (little Jade), storybook (open), pillow (Mama), small TV (off) on a crate |  |
| `v4_G3` | G3 | 50 | 1.49, 1.40, -0.53 | 1.49, -0.60, -0.50 | storybook right page, storybook left page, sleeping mat (little Jade), storybook (open), light through floorboard cracks, quilt (little Jade's, navy floral) |  |
| `v4_G4` | G4 | 32 | 0.08, 1.27, 0.81 | 1.63, 0.61, -0.27 | textbooks (fallen, scattered), sleeping mat (little Jade), window, sleeping mat (Mama), quilt (Mama's, beige), quilt (little Jade's, navy floral), pillow (little Jade), neon blade sign (perpendicular to the wall), storybook (open) |  |
| `v4_G5` | G5 | 85 | 1.30, 0.71, 0.45 | 1.72, 0.59, -1.50 |  |  |
| `v4_J4L` | J4 (left half) | 40 | 1.14, 1.01, 1.19 | 1.54, 0.60, -0.72 | quilt (little Jade's, navy floral), quilt (Mama's, beige), sleeping mat (little Jade), pillow (little Jade), sleeping mat (Mama), storybook (open), pillow (Mama), small TV (off) on a crate |  |
| `v4_L2b` | L2 (attic half) | 40 | 0.47, 1.64, -0.57 | 2.35, 0.24, -1.25 | sleeping mat (Mama), quilt (little Jade's, navy floral), sleeping mat (little Jade), textbooks (fallen, scattered), window, pillow (little Jade), pillow (Mama), storybook (closed), quilt (Mama's, beige) |  |
| `v4_L3` | L3 | 32 | -1.70, 1.38, 0.95 | -0.17, 1.05, -0.29 | small TV (off) on a crate, sleeping mat (little Jade), quilt (Mama's, beige), quilt (little Jade's, navy floral), textbooks (fallen, scattered), window, sleeping mat (Mama), neon blade sign (perpendicular to the wall), pillow (little Jade) |  |
| `v4_L3_off` | L3 | 32 | -1.70, 1.38, 0.95 | -0.17, 1.05, -0.29 | small TV (off) on a crate, sleeping mat (little Jade), quilt (Mama's, beige), quilt (little Jade's, navy floral), textbooks (fallen, scattered), window, sleeping mat (Mama), neon blade sign (perpendicular to the wall), pillow (little Jade) |  |

#### bed26

| setup | serves | lens | camera position (m) | looks at (m) | fixed objects in frame (largest first) | warnings |
|---|---|---|---|---|---|---|
| `v4_I1` | I1 | 40 | -2.54, 0.97, -0.29 | -0.59, 0.56, -0.49 | quilt (on the bed), bed (wooden frame), nightstand, rug (fluffy), door (open), hallway (lit), headboard (wood), mattress, pillow |  |
| `v4_I3a` | I3a | 85 | -1.77, 0.69, -0.34 | 0.22, 0.56, -0.54 | quilt (on the bed) |  |
| `v4_I4` | I4 (no morph) | 85 | -1.98, 0.86, -0.35 | -0.00, 0.62, -0.56 | quilt (on the bed) |  |
| `v4_J1` | J1 | 50 | -0.84, 1.35, -0.42 | -0.88, -0.65, -0.42 | rug (fluffy), storybook right page, storybook left page, storybook (open), flashlight (on) |  |
| `v4_J4R` | J4 (right half) | 40 | -2.60, 0.97, -0.23 | -0.66, 0.56, -0.43 | quilt (on the bed), bed (wooden frame), rug (fluffy), nightstand, door (open), hallway (lit), headboard (wood), mattress, pillow |  |
| `v4_K1` | K1 (room part) | 40 | -2.63, 0.93, -0.24 | -0.68, 0.52, -0.44 | quilt (on the bed), rug (fluffy), bed (wooden frame), nightstand, door (open), hallway (lit), headboard (wood), mattress, storybook (open) |  |
| `v4_K1_ots` | K1 (page part, start of the push), K2b entry | 35 | -0.55, 1.12, -0.08 | -1.25, -0.58, -0.88 | rug (fluffy), storybook left page, storybook right page, storybook (open), flashlight (on) |  |
| `v4_K2a` | K2a | 35 | -1.75, 1.38, 0.26 | -0.53, 0.12, -0.69 | rug (fluffy), quilt (on the bed), nightstand, bed (wooden frame), storybook left page, storybook right page, mattress, storybook (open), flashlight (on) |  |
| `v4_L1` | L1 | 35 | -2.77, 0.88, -0.10 | -0.82, 0.55, -0.38 | rug (fluffy), door (open), nightstand, bed (wooden frame), quilt (on the bed), hallway (lit), headboard (wood), mattress, pillow | joint limit: Jade armL: forearm passes through the torso |
| `v4_L2` | L2 | 40 | 0.68, 2.10, 0.76 | 0.00, 0.70, -1.12 | blanket (being pulled up), headboard (wood), mattress, rug (fluffy), pillow, nightstand, window, bunny (stuffed toy), night-light (off) |  |

#### car26

| setup | serves | lens | camera position (m) | looks at (m) | fixed objects in frame (largest first) | warnings |
|---|---|---|---|---|---|---|
| `v4_F1` | F1 | 28 | 0.00, 1.40, -0.20 | 0.21, 1.18, 1.78 | headliner (roof), passenger seat, driver's seat, EMPTY child car seat (rear left), rear bench, child car seat (hers, rear right), tailgate, median barrier, guard rail |  |
| `v4_F2` | F2 | 24 | 0.06, 1.16, 0.44 | 1.49, 1.15, 1.84 | child car seat (hers, rear right), B pillar, door panels, headliner (roof), roof rail, streetlight poles, guard rail, tailgate, C pillar |  |
| `v4_F3a` | F3 | 40 | -0.05, 1.34, 0.10 | 0.98, 1.11, 1.80 | passenger seat, child car seat (hers, rear right), headliner (roof), rear bench, C pillar, tailgate, roof rail, guard rail |  |
| `v4_F4a` | F4 (first half) | 26 | -0.08, 1.21, -0.20 | 0.47, 2.02, -1.94 | rear-view mirror glass, rear-view mirror, streetlight poles |  |
| `v4_F6b` | F6 (end) | 24 | -0.12, 1.30, 0.30 | 1.36, 1.22, 1.64 | passenger seat, headliner (roof), child car seat (hers, rear right), glass: rear_right, rear bench, roof rail, door panels, tailgate, B pillar |  |

## 5. Master plates (`media/kf/v4/_sets/`)

Painted by gpt-image-2 (`tools/gen/sets_master_v4.py`, prompt + inputs in each `.txt`) from the empty-room guide
(`media/layout/<set>/v4_MASTER*_line.png` for structure, `_lit.png` for light) plus two clean frames of accepted v3 shots
for style only (`media/kf/v4/_sets/refs/v3_*.png`, extracted from `media/comp/`; no real photo, no v1/v2 image). Pass the
plate to every keyframe of that set as the look reference, together with the shot's own guide; the guide decides
placement, the plate decides what things look like.

| plate | view | use for |
|---|---|---|
| `attic88_master.jpg` | empty attic toward the window, books stacked (`v4_MASTER_window`) | every attic shot before D9 c |
| `attic88_master_fallen.jpg` | the same after D9 (books fallen) | D9 c and every later attic shot |
| `attic88_master_door.jpg` | toward the stair door: door ajar, hook rail with apron and towel | A3, and any shot that sees the door end |
| `bed26_master.jpg` | the storytime side (from where LAP_front stands) | I1, I3a, I4, J1, J4R, K1, K2a, L1 |
| `bed26_master_L2.jpg` | the L2 camera, empty bed | L2 (and as the bedroom's look reference) |
| `car26_master.jpg` | from between the front seats toward the two (empty) child seats | F1, F2, F3a, F4a, F6b |

Checked by looking (each plate beside its guide): object placement follows the guides closely in all six. Known
deviations, tell the model to follow the shot guide on these: the plates leave the neon lettering as glow without
characters (as asked: 酒家 is composited from typeset text, never drawn); the attic plates drop the paper piano
printout and `attic88_master_fallen` adds a stray book in the foreground; `car26_master` redraws the cabin a little wider
than the crude v3 cabin geometry (seat shapes are the plate's, positions the guide's). Spend: 6 plates, about $1.43.

## 6. The set check (`tools/review/set_check.py`)

Run it on every keyframe before any video is made, and on the last frame of every take:

```sh
PY=/home/jade/Documents/halys-video/.venv/bin/python; export TMPDIR=$PWD/work/tmp
$PY tools/review/set_check.py --set attic88 --shot G4 --image media/kf/v4/G4_take1.jpg        # or --video X.mp4 --at first|last|<sec>
$PY tools/review/set_check.py --print-prompt                                                  # the vision-pass instructions
# a Sonnet/Haiku subagent opens the sheet (.jpg), answers with the JSON the prompt asks for -> <sheet>.verdict.json
$PY tools/review/set_check.py --merge work/review/set_check/G4_take1.json work/review/set_check/G4_take1.verdict.json   # PASS / FAIL + reasons
```

The sheet: candidate | candidate with the guide's lines in yellow / label render | candidate with every fixed object's
expected box (numbered); then one tile per object (candidate crop beside the label-render crop). The JSON carries the
expected boxes and two numeric hints per object (edge support, best-match shift); they only flag, the verdict is the
vision pass's. A frame FAILS when any key object (window, blade sign, door, hooks, mats, pillows, textbooks, TV,
headboard, bed, bunny, nightstand, blind, rug, door, child seats, mirror, flashlight, the book) is missing or moved, when
something sizeable is invented, or when the people do not stand where the mannequins stand. Reject and regenerate
failing keyframes; for a failing last frame of a take, re-take. Batch runs: give a smaller model a tab-separated list
like `work/tmp/sets/v3_check_list.tsv` and the instructions in the log (`docs/logs/LOG_v4_sets.md`, "v3 check").

### The v3 frames against the v4 sets

Run 2026-11-18 by a Sonnet subagent over 59 frames of 39 v3 room shots (first / last / chosen frames), every sheet
opened and judged; sheets, numeric JSON and verdicts in `work/review/set_check/v3/`, table in `SUMMARY.md` there.
Caveat: the agent named only the objects it found wrong; the rest were recorded as present by default. The lead looked
at a sample (B2, I1, L2) and agrees with those verdicts.

**FAIL (must be re-made to the v4 set; reason):**
- attic: A1 (Mama's mat and pillow absent), A3 first beat (TV on the wrong side), A4 (window and stack on the wrong
  side, TV invented at left), B1 (also re-blocked for the arm), B2 (a textbook stack where the pillows are; pillows absent),
  C3 (pillow invented at frame left), C5a (window on the wrong side, stack absent), D2d (TV absent), D3 (no window, no
  blade at all), D9 start and end (TV invented at right), E1 (TV moved), E3 and E6 (Mama's pillow / quilt on the wrong
  side), F3b (TV invented behind Mama), G1 (fallen books lower left), J4 left (window invented on the right, stack where
  the pillows are), L2b (fallen books on the wrong side, storybook absent, TV invented), L3 (TV and fallen books absent).
- bedroom: I1 (bed and nightstand on the wrong side, no door light, no bunny), K1 (no door light, bunny moved, lamp
  invented), K2a (flashlight on the wrong side), L1 (no door light, nightstand on the wrong side).
**PASS:** A2, A3 second beat, C2, E5, G3, G4, G5 (the last three are narrow strips on paper: little room to judge),
I3a, I4, J1, L2, and all car shots F1, F2, F3a, F4a, F6b.

Patterns: in the attic the window / TV / stack are mirrored in about half the shots, and the quilt and Mama's pillow
swap sides between the lap shots; in the bedroom the nightstand and the door light are the usual failures. E6 is on the
FAIL list (Mama's pillow and the TV): the brief keeps E6 for hair and acting, so ATTIC should decide whether a set fix
(comp the background) is enough there.

# Layout: camera per room shot (v1, 2026-11-17)

Guides: `media/layout/<set>/<SHOT>_line.png` is what the image model gets as the layout reference (geometry only,
"do not copy the plain shading"); `_lit.png` is the mood check for us, `_label.png` names everything, `<SHOT>.json`
has page/pane corners, face and hand positions and light directions for the compositor. How to re-render:
`layout/README.md`. Contact sheets: `media/layout/_sheets/{attic88,bed26,car26}.jpg`.

Always tell the model, beyond the guide: the people are the on-model characters (fine-line 白描 faces with light
wash), not mannequins; hands are real hands (the guide's hands are mitts); keep the camera, the positions and the
sizes. Mannequin heights are true (Mama 160, little Jade 108, Jade 165, daughter 102 cm).

## attic88 (1988, night; neon through the one window frame-right of the "front" view, warm lines between floorboards)

| shot | lens | camera intent | tell the model beyond the guide |
|---|---|---|---|
| A1 | 32 | Wide from the door end of the attic; the window a small lit opening lower right (0.8/0.74), everything else night (Ma Lin) | Only the window carries light: red neon, mirror-reversed CHIN. IND. SPEC. REST. / 酒家 seen through dusty glass; rafters and mats barely there in the dark; little Jade asleep is a dark shape |
| A2 | 28 | Low across the floorboards (0.42 m), drifting left ~1 m: piano printout corner, mats, child asleep under a blanket, book on Mama's pillow, textbooks, TV | Thin warm lines between the boards, red neon spill on the floor, dust in the beam; TV is off |
| A3 | 24 | From behind little Jade (lower right, back to us) across the dark attic to the stair door, open wide: a tall warm slot with Mama small in it | Mama drying her hands on her apron; tungsten light from the stairwell is the only warm source; neon red on little Jade's back |
| A4 | 50 | From the pillow side, low: Mama's two hands lifting the closed storybook off her pillow | Her hands are wet and red from the kitchen; the red cloth cover catches a sheen of neon; face out of frame |
| B1 | 55 | Little Jade three-quarter, face in the 4:5 centre; Mama a soft shoulder at the left edge | Deadpan, lit red from the window side; Mama out of focus |
| B2 | 32 | From the foot of the mats: Mama (centre-left) sings, the open book across her knees tipped toward little Jade (right) | The open spread glows: the brightest thing in the room (paper catching neon); no crib anywhere |
| C2 | 58 | THUMBNAIL. Mama's eyeline (her head hidden) onto the upright spread; little Jade's two hands enter from frame left, the window side | The hands make a monkey head in profile; its red shadow is big, thrown across the left page toward the gutter (see `hand_shadow` polygons; light travels left->right/down); 花果山 small under it; leave room for the title |
| C3 | 40 | Close two-shot, both faces in the 4:5 centre: Mama presses little Jade's raised hands down with one finger | Mama amused (she sings); little Jade's hands half-lowered |
| C5a | 50 | Pure profile, contre-jour: Mama in the left third leans to the page and blows; the window and neon behind her | Dust motes swirling in the red beam; her breath visible as a faint mist toward the page |
| C5b | 50 | Straight down onto the spread from above Mama's head; Mama's hands on the outer edges | Page quads for the push into the painting; the egg and mist are on the page |
| D3a | 50 | The right page low in frame, its top edge 60% down, dark floor/attic beyond | Two thin gold beams shoot up from the page's top edge out of frame (the only gold) |
| D3b | 30 | High from the foot of the mats: floorboards, two mats, no crib; Mama and little Jade side by side cross-legged singing, the book open on the mat between them | Both faces singing in octaves; one pool of neon |
| D9 | 28 | Wide end of the pull-back: little Jade (right) standing on her mat on one leg, hand shading her eyes (Sun Wukong's look-out pose); Mama (centre-left) laughing | Opera 亮相 pose copied from the page; neon red |
| E1 | 40 | Close two-shot, one pool of neon: Mama (left) taps little Jade's nose | Fingertip on the nose exactly on "you"; Mama sings |
| E3 | 70 | Little Jade close from the window side, face at 0.6; Mama a warm blur at frame left | Small shrug, palms up; Mama's face out of focus (faces soft, characters sharp) |
| E5 | 60 | Extreme close: Mama's mouth and cupped hand at little Jade's ear, little Jade's face right | No subtitle, no visible secret; Mama's eyes amused |
| E6 | 40 | Two-shot: little Jade faces front, eyes slid sideways to Mama; Mama leans back chuckling, hand by her mouth | On the pickup, little Jade's eyes go wide |
| F3b | 50 | Match cut: little Jade's face at 0.6/0.38 (same as F3a), palm open under her lips | She blows across the palm; hairs fly toward frame left |
| G1 | 60 | Little Jade's face slightly right of centre, her fingertip on her forehead | The margins will close from left and right: keep face and hand inside the centre third; colour draining to grey + gold |
| G3 | 45 | Vertical stack in the centre column: little Jade (kneeling) above, her flat hand over the left page, its shadow below | The hand's shadow covers the painted gold band on the monkey's head |
| G4 | 45 | Over the spread from above Mama (head hidden): little Jade on her tummy at the window-side page edge, her head-shadow across the left page; Mama's finger-and-thumb ring between window and head | PHYSICS: a 4 cm ring throws a shadow ~1/4 of the head-shadow; it can't encircle it. Paint the ring shadow sitting on the brow of the head-shadow like the band (or the compositor scales it); strip is ~15% wide at its narrowest, so everything in the centre column |
| G5 | 85 | First centred face: little Jade dead centre, holding Mama's look (Mama just off-lens left) | Nothing moves; deadpan; grey with neon |
| L3 | 32 | Identical to A1 | Neon on, then off at 237.840 (render the off state by switching `light.neon: 'off'`) |

## bed26 (2026, dark bedroom; one small flashlight)

| shot | lens | camera intent | tell the model beyond the guide |
|---|---|---|---|
| I1 | 35 | Front-left two-shot: Jade on the floor against the low bed, book on her knees, flashlight in her right hand; the daughter on her tummy on the bed by her left shoulder | Out of white glare into the dark room; flashlight white is the only light; book corners soft and worn; a crayon monkey in the page margin; jacket orange and strawberry pink the only saturated colours |
| I2 | 40 | Jade's eyeline into the spread (head hidden): her right hand's monkey shadow on the right page, the daughter's identical one on the left | The painting is blue-green heaven (青绿); the two shadows are big and identical; flashlight pool on the page |
| I4a | 85 | Second centred face: Jade dead centre, lit from below by the page | Certain, nothing moves; Mama's sceptical 1988 face ghosts over for the first 8 frames (composite) |
| I4b | 40 | Same eyeline as I2: the daughter's small hand in the beam | Its shadow climbs onto the bare chair at the painted banquet table (一桌二椅) |
| J1 | 50 | Close on the left page from above-left: the daughter's fingertip on a carved character | The character lights under her finger; four hard flashes follow in the composite |
| K1 | 35 | Two-shot: Jade lifts a page corner toward the last chapter, flashlight in her right hand; the daughter cross-legged beside her, nodding | Softer; the pool of flashlight on the page |
| L1 | 24 | High and wide from the door corner: bed frame-right, Jade on the floor against it, the daughter asleep against her arm, the book open on the blanket, the flashlight lying on the blanket, still on | End of the pull-back; the only light is the pool on the book |
| L2 | 50 | Close behind Jade's hand: flashlight foreground, thumb on the switch, the white pool on the page beyond | The pool sits on the blank column; on the click, black |

## car26 (2026, dusk, highway; streetlights sweep; panes become shadow-puppet screens)

| shot | lens | camera intent | tell the model beyond the guide |
|---|---|---|---|
| F1 | 28 | From between the front seats looking back: the daughter in her forward-facing car seat, face in the 4:5 centre, hands chopping | Deadpan rap; amber streetlight sweeping across her from the side window; dusk violet outside |
| F2 | 24 | From between the front seats toward her right rear window: the pane fills frame left, the daughter right | The pane is a shadow screen: a jointed leather shadow-puppet monkey, back-lit amber by the passing streetlight (pane quad `rear_right` in the sidecar) |
| F3a | 38 | Same place as F1, tighter: face at 0.6/0.38 (matches F3b) | Plucks at her hair, blows across her open palm; hairs fly toward frame left |
| F4a | 26 | Looking up at the rear-view mirror against the windscreen; camera position found by search so both reflections sit in the glass | In the mirror: Jade's eyes (left) and the daughter behind (right), both singing. The reflection is rendered true in the guide; then puppet copies on every pane |
| F4b | 18 | Wide from the back of the cabin: windscreen, side windows, mirror; Jade and the daughter from behind | Every pane carries its own shadow-puppet copy lit by its own streetlight; a 走马灯 ring of running monkeys |
| F5 | 18 | Reverse wide from above the front seats: rear window and rear side windows, the daughter left | Copies go dark one per beat with their lights, until the glass is empty dusk |
| F6a | 24 | From the rear centre seat: the windscreen is the stage between Jade (left) and the passenger headrest (right) | Two identical puppet monkeys face each other across the windscreen's centre line, mirror-posed |
| F6b | 24 | From between the front seats: the daughter waving (right), her reflection waving in her dark side window (left) | The reflection is rendered true in the guide; same instant, same gesture |

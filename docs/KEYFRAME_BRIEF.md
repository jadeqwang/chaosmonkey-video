# Keyframe brief (room shots)

For every agent painting keyframes of the attic (1988), the bedroom and the car (2026). Lead: Claude (Fable 5.2).

## Read first
- `docs/TREATMENT.md` (vision, "Look"), `docs/shots.yaml` (your shots: description, ink budget, lip-sync flag),
  `docs/SHOTLIST.md` (frames, lyrics per shot).
- `docs/LAYOUT.md`, `layout/README.md`, and your set's guides in `media/layout/<set>/<SHOT>_{line,flat,label,lit}.png`
  with sidecars `<SHOT>.json` (book-page quads, pane quads, head and hand positions).
- `design/characters/CANON.md` (which reference crops to pass per character, the verbal descriptions, the guard
  sentences, known drift). Overview: `design/characters/_overview.jpg`.
- `docs/LOOK_BAKEOFF.md` (recipes, failure patterns) and `docs/PIPELINE_RECON.md` §3, §5 (calls; the blockout method:
  pass the `_line.png` guide as image 1, "use image 1 ONLY for geometry").
- Look anchors: `media/look/L5/nbp_a_v2.jpg` (attic), `media/look/L6/nbp_a_v2.jpg` (bedroom). Do NOT pass these as
  references for close-ups: a room frame used as a reference copies its contents. Describe the room in words.

## The look (locked)
An ink-and-light-colour painting on cream xuan paper, one hand for everything. People: fine brush-line faces and hands,
light wash, flat even tones, no cel shading, no photoreal skin. Rooms are paintings of night: dark ink washes with paper
fibre showing, ONE pool of coloured light, everything else falling to dark wash. Full-bleed painting to the frame edge:
no paper margin, no border, no vignette, no signature, no seal, no writing anywhere.
- 1988 attic: cinnabar-red neon from a low window on the right gable wall (the only strong colour), thin warm tungsten
  lines between the floorboards, old-wood browns. The neon SIGN is added in code: paint the window as dusty glass with
  a red glow outside and no lettering.
- 2026 bedroom: dusk-violet darks, one small white flashlight pool. 2026 car: blue-hour dusk, amber streetlight sweeps.
  Strawberry pink and the jacket's orange are the only saturated colours in 2026.
- The storybook's open pages: paint them as BLANK cream paper (bare), lit by the room's light. The page art is mapped on
  in the compositor from the sidecar quads, so pages must be clean, unobstructed where the shot allows, and match the
  guide's quad. Where hands or shadows cross the page, that is fine: they are separated in comp.
- Hand shadows (C2, G3, G4, I2): do not paint the shadow. Paint the hands and the lit page; the shadow is a comp layer.
- Composition: follow the guide exactly (camera, positions, sizes). Subject in one corner or along one side. Only G5 and
  I4 are dead-centre faces. Lip-sync close-ups: mouth closed or barely parted, neutral; face fully visible; nothing
  crossing the mouth; head at least 25% of frame height; eyes on the person they sing to.
- Mama is about 30 (use CANON's guard sentence every time). Little Jade's hair is jet black. Jade's jacket: orange band
  on chest and sleeves only (no orange collar or cuffs); pale-blue dot on the chest.

## Method
Model: `google/nano-banana-pro` at 2K, 16:9 (max 3 reference images: guide + one canon crop per character; if three
characters/props are needed, composite two canon crops into one reference image). Fall back to Seedream 5 Pro or GPT
Image 2 if a shot fights you. Save `media/kf/<SHOT>.jpg` (the pick, 2752x1536 or the model's 2K size), the prompt as
`media/kf/<SHOT>.txt`, alternates as `media/kf/alt/<SHOT>_vN.jpg`. For shots with two setups (a/b) save both
`<SHOT>a.jpg`, `<SHOT>b.jpg` and ALSO copy the one that opens the shot to `<SHOT>.jpg` (the animatic reads that name).
Where a shot will be animated with first+last frames, add `<SHOT>_end.jpg` painted from the same guide with the end pose
(e.g. hand lowered, head turned): edit the pick rather than regenerate, so the room does not change.

Check every image by looking at it (downscale to at most 1400 px to view): matches the guide; right characters on model;
five fingers; no text, seals, margins; reads at 32 px wide as one light pool; night coverage within about 10 points of
the shot's ink budget (`tools/review/coverage.py`, night ground). Up to 3 attempts per shot, then keep the best and log
the defect. Consistency across the set matters more than any single frame: same floor, same window, same mats, same
blanket colours, same book. After the first 3 picks, reuse one of your own picks (cropped to a detail without people)
as a style reference where a slot is free.

Write a log `media/kf/LOG_<set>.md`: per shot the pick, attempts, cost, defects left. Build a contact sheet
`media/kf/_sheets/<set>.jpg`. Budget is in your task message; check `tools/gen/spend.py`. Do not commit.

# Layout department notes (checkpoints)

## 2026-11-17 checkpoint 0
- Read TREATMENT, shots.yaml, brainstorm (Characters, Art direction, Section by section), PIPELINE_RECON s5,
  moongazing guanghan3d + blockouts harness (playwright-core + swiftshader Chrome, importmap three, data-URL PNGs).
- Plan: layout/engine (core, mannequin, book, renderer), layout/sets/<set>/{layout.js,build.js,shots.js},
  layout/render.mjs CLI, sheets via ImageMagick montage. $0, no generation.
- Attic orientation: ridge along x; door gable at x=-3.5 (left when looking -z), window gable at x=+3.5 (right);
  mats heads at -z under the low slope; main "front" camera looks -z from +z (foot of the mats).
- Neon sign hung 1.2 m outside the window gable, parallel to it, so light enters near-horizontal and reaches the mats.

## checkpoint 1 (attic88 first full pass)
- Engine done: engine/{core,mannequin,book,stage,aim,render,main}.js; render.mjs CLI; review.sh / sheet.sh helpers.
- Cameras: `orbit` around named points (face-relative az) + `aim` (screen placement) solved at build time; `headAt` to
  slide a figure so its head lands on a point; `ray:<point>:<d>` targets put hands on the neon ray (shadow lands on point).
- Lessons: POV inserts need the reader's head hidden (hideParts) and el >= 60 or the torso fills frame; close-ups
  must check `blocked_by` (sidecar warnings); 5-year-old arm reach is ~0.43 m -> she kneels/lies next to the book.
- Neon effective point raised to y 1.5 (sign 1.2 m outside, window 0.8x0.8) so the light reaches faces and rakes the
  page at ~22 deg; hand shadows land on the page only when hands are within ~0.1-0.2 m of it.
- G4 physics: the finger-ring's shadow is ~1/4 the size of the head-shadow (ring 4 cm vs head 19 cm, both near the
  page); it cannot encircle it. Staged so it lands on the head-shadow's brow; flagged for the compositor.

## checkpoint 2 (bed26 first pass)
- bed26 built: room 3.4 x 3.2 x 2.6, toddler bed on the right wall (mattress top 0.33), window + blind on the back wall,
  bookshelf left, nightstand. Flashlight = prop + spot (17 deg) placed by `flashlight {aimAt, from|at}`; hands grip
  it via 'flash:grip'; 'ray:' targets in this set point at the flashlight lens.
- POV inserts (I2, I4b, J1) use Jade's hidden head, el ~64.

## checkpoint 3 (all three sets rendered; docs)
- car26 built: SUV cabin with named panes, rear-view mirror angled at the child seat, streetlights from lampsAt(t).
  True reflections (F4a rear-view mirror, F6b side window) rendered by reflecting the world root and compositing
  through the glass pixels; F4a camera found by grid search so both faces land in the mirror.
- Renders: attic88 23 shots, bed26 8, car26 8, five modes each + sidecars; sheets in media/layout/_sheets/.
- Docs: layout/README.md (how-to + sidecar schema), docs/LAYOUT.md (one line per shot).
- Open: hands are mitts (shape only); G4 ring/head-shadow scale (physics); G4 hides Mama's head (lip-sync face
  off-screen in that framing); POV inserts show the reader's body edge; lit preview is a mood check only.

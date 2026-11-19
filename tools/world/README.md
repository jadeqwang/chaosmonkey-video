# tools/world: the painted world as a real 3D scene (REVISION_V4 §2)

WORLD team toolkit, v0.1 (2026-11-18). Painted elements in our hand -> alpha + depth -> displaced relief cards in a
three.js scene with an ink-on-paper material -> camera flights rendered headless on the GPU -> paper grain + glow ->
`media/comp/<ID>.mp4`. Characters, threads, inscriptions and seals are typeset objects in the scene, so they stay crisp
and fixed to the rock while the camera flies. Questions / requests: `docs/logs/LOG_v4_world.md`.

## 1. Pipeline in five commands

```sh
PY=/home/jade/Documents/halys-video/.venv/bin/python; export TMPDIR=$PWD/work/tmp
$PY tools/world/plates.py list                               # painted element jobs (gpt-image-2), add your own to JOBS
$PY tools/world/plates.py run pillar_slender --n 2          # -> design/world/plates/pillar_slender_{1,2}.png (+ .txt prompt)
$PY tools/world/prep.py design/world/plates/pillar_slender_1.png --out design/world/cards --name pillar_slender
#   -> design/world/cards/pillar_slender_{rgba,depth}.png + .json   (alpha = ink key + filled body; depth = Depth-Anything-V2-L)
$PY shots/MYSHOT.py                                          # your script: builds a World, renders, finishes, encodes
node tools/world/render.mjs --scene work/world/MYSHOT/scene.json --frames 0,40,80   # (what World.render() calls)
```

Rendering is fast: ~0.15 s per 1080p frame at 2x supersampling on the RTX 3090 (Chrome + ANGLE/Vulkan, headless).
`--swiftshader` forces the CPU path (30x slower). 1080p is the authoring size; `World.encode()` writes 960x540; a
1080p master is the same render with `w=1920, h=1080` passed to encode.

## 2. Painted elements: how to paint them so they lift well

One element per sheet, isolated on bare paper, nothing else painted, its foot fading into blank paper (a sea of cloud
hides every base: no ground plane needed). `tools/world/plates.py` has the prompt blocks (`HAND`, `ISO`, `FOOT`, `QL`
for blue-green) and the refs (the film's own 花果山 plate for the hand + public-domain Huangshan paintings for rock
language: `refs/paintings/v4/huangshan/MANIFEST.md`). Never ask the model for text: all Chinese is typeset.
`prep.py` options: `--solid 0` for wet/mist-like elements (alpha = ink only), `--crop x,y,w,h` to cut one element out of
a composed plate, `--nodepth` for flat things. Check: the rgba over a checkerboard and the depth side by side
(`work/world/_test/hgs_check.jpg` shows the expected look).

Existing cards: `design/world/cards/` (Huangshan pillars, near pines/ledges, far ranges, 花果山 parts, 青绿 peaks).

## 3. Building a scene in Python (`tools/world/scene.py`)

```python
import sys; sys.path.insert(0, '.')
from tools.world.scene import World, smooth_path, dolly_zoom, paper_grain, encode, sheet
Wd = World('H5', frames=84)                        # scratch: work/world/H5/
Wd.fog(density=0.012, start=20)                    # distance fades to paper (far = paler, as painters do)
Wd.sea(y=0, soft=2.5, amp=3, scale=0.04)           # everything below y +- noise dissolves into bare paper (cloud sea)
pk = Wd.card('pillar_slender', pos=[0, -6, -60], height=40, relief=8)    # bottom-centre anchor; width from aspect
Wd.card('pine_near', pos=[-4, -2, -9], height=6, relief=1.0)
Wd.mist([0, 4, -40], [150, 60], pitch=-90, opacity=0.8, scale=0.05, speed=[0.4, 0.1])    # horizontal vapour sheet
Wd.mist([0, 10, -70], [200, 25], band=True, opacity=0.7)                                  # vertical band of mist
P = smooth_path([(0, [0, 6, 10]), (83, [3, 9, -30])], 84)                                # camera positions
Wd.camera = [dict(p=list(p), t=[p[0], p[1], p[2] - 40], fov=40) for p in P]              # one dict per frame
Wd.render(ss=2)                                    # -> work/world/H5/frames/{beauty,glow}/NNNN.png
G = paper_grain(1920, 1080)                        # screen-fixed paper (tools.ink Paper 'new', seed 1988)
encode((Wd.finish_frame(f, grain=G, bloom=1.0) for f in range(84)), 'media/comp/H5.mp4', 84)
```

Units are free (think metres); fov is vertical degrees. Camera dict: `p`, `t` (look-at), `fov`, optional `up`, `roll`
(deg), `near`, `far`, `ortho` (vertical extent: a true orthographic frame).

### Objects
| call | what | main options |
|---|---|---|
| `card(name, pos, height/width, relief, yaw, pitch)` | relief card from `design/world/cards/<name>` (or `tex=` any RGBA png) | `bend` (sides recede, more roundness), `ink` (0 = paper .. 1), `lum`, `tint`, `fogk`/`seak` (0 = immune to fog / cloud sea), `opacity`, `edge` (noisy wet-edge erosion), `anchor` ('bottom'/'center'), `billboard` (turns to face the camera around y), `visible=[f0,f1]`, `uvRect`, `carve`, `light`, `anim`, `keys` |
| `plane(tex, pos, size)` | flat textured plane in the opaque pass (a page, a tablet, a typeset inscription on rock) | same as card |
| `overlay(tex, pos, size)` | flat plane drawn after the opaque pass, not depth tested (things in front of everything) | same |
| `mist(pos, size, yaw, pitch)` | paper-coloured vapour sheet, soft against geometry (scene depth), drifting fbm | `opacity`, `scale` (cells/unit), `speed`, `thresh` (0.3 dense .. 0.6 wisps), `edge`, `soft`, `wash` (pale grey in thin parts), `band`, `nearFade`, `billboard`, `keys` |
| `thread(pts, f0)` | gold thread drawn from pts[0] to pts[-1] from frame f0, screen-width ribbon, hidden behind rock | `fdraw`, `fhold`, `ffade`, `rest` (level after the fade), `width` (px at 1080p), `col`, `glow` |

`keys=[[frame, {pos, yaw, pitch, roll, scale, opacity, relief, ink, lum, fogk, seak, light}], ...]` animates any
object (linear between keys, held at the ends). `anim={'pattern': 'dir/%04d.png', 'n': 120, 'start': 0, 'rate': 1,
'loop': 'pingpong'|'loop'|'hold'}` plays a frame sequence as the card's texture: this is how a video-model clip of a
locked plate (pines moving, waterfall, mist) becomes a living texture on 3D geometry (keep the alpha in the frames, or
reuse the card's alpha: see §5).

`truePos=[x,y,z]` on a card: fog and cloud sea are computed where the card really is even while keys move/scale it
(used to squash a world flat onto a page and release it: shots/_jworld.py `flat_keys`).

`Wd.card_point(o, u, v)` = world position of texture point (u, v) on card o, displaced exactly as the shader does
(use it to pin threads, figures, cameras to a spot on the rock). `Wd.card_normal(o)`.

### Carved characters (`tools/world/carve.py`)
```python
from tools.world.carve import Carving, qianziwen
CV = Carving('design/world/cards/pillar_scripture_rgba.png', size=4096)
gl = CV.field((0.30, 0.25, 0.70, 0.85), qianziwen(), px=70)      # columns right->left; only on solid pale rock
CV.save('work/world/D5/carve_pillar')
o = Wd.card('pillar_scripture', [0, -5, -50], height=40, relief=6, carve=CV.spec(lit=[(g['id'], 12 + i, 1.0) for i, g in enumerate(gl)]))
```
Incised look (darkened + bevel), each glyph lights at its frame (rise 4 f, flare, ember flicker, steady glow) in
`glow` (default gold). The glow pass is bloomed by `finish_frame(bloom=...)`. Font: the v3 carved-cliff seal script.
`CV.spec(..., reveal=True)`: a glyph does not exist before its frame (carved by the light): it appears with a flash that
settles to `base`; `col` tints the cut (e.g. cinnabar `(1.0, 0.55, 0.45)`), `glow_fog` (0..1) how much fog dims the glow.

### Raking light (B4)
`light={'v': [edge_u, softness, dir, strength], 'col': [r, g, b]}` + keys `light` to move the terminator across a card.

Additions for B4 (all optional; a card that uses none of them compiles the exact old shader. The card-shader code is
behind `#ifdef B4X`, set only when a card has `light.wig`, `light2` or `carve.reveal == 'light'`. Checked byte-identical
on the D flight, frame 60, beauty and glow):
- `light.wig = [amp_u, cells_per_v]`: the terminator is a wavering edge, not a ruled line.
- `light2 = {'v': [...], 'col': [...], 'wig': [...]}` + keys `light2`: a second terminator (the moon), same maths.
- `carve=CV.spec(lit=[(id, 0, gain, layer)], reveal='light', glow2=, col2=, revW=, flashW=, bevelPx=, bevelK=)`: a glyph's
  strokes exist only where its light's terminator has passed, per pixel, so one stroke is cut as the edge crosses it.
  The fresh cut flashes over `flashW` (u) behind the edge and keeps `base`. Layer 0 is cut by `light`, layer 1 by
  `light2` (its own glow / cut tint). `bevelPx` / `bevelK` widen the chisel wall for macro views (blur the cov too).
- `Wd.points(parts, **kw)`: dust / flecks. `parts` = Nx10 `[x, y, z, f0, vx, vy, vz, life_s, size_units, seed]`,
  ballistic plus `acc` and `sway`, hidden behind rock (scene depth), fogged, irregular soft flecks (not sparkles). kw:
  `col` (beauty), `glowCol` / `glow` (glow pass, bloomed), `opacity`, `minPx` / `maxPx` (px at 1080p), `fadeIn` (s),
  `fadeOut` (fraction of life), `grow`, `fogk`, `keys` (opacity), `order`. To make a particle arrive at a target at the
  end of its life: `v = (target - p0) / life - acc * life / 2` (B5's dust gathering into the stone).
- Render order matters for stepped walls of feathered cards: recessed slabs need a lower `order` than the slabs in front
  of them. Otherwise a recessed slab drawn later fails the depth test behind the front slab's half-transparent edge and
  a paper-coloured seam shows.

### Additions for round 2 (R2_3D; all default-off, Dflight_b frame 60/150 beauty+glow byte-identical)
- Passes `typeset` / `typeset_a` (`Wd.render(passes=['beauty','glow','typeset','typeset_a'])`): only the typeset objects
  (carved glyphs: cut + lit colour; threads; points; cards with `typeset=True`) premultiplied on black, everything else
  black but still occluding (rock) and veiling (mist); `typeset_a` is the alpha. Composite: `bg*(1-A) + TS`.
- Card keys `tint`. Threads: `headW` (the drawing head swells to (1+headW) x width: a bead), `headG` (extra glow at the
  head), `distFade=[d0, d1]` (alpha ramps in from view distance d0 to d1).

## 4. Page -> depth (B3, J2, K2b): the method
The page is a plane in the 3D scene; the painting on it is the 3D world itself, seen from the page camera through a
very long lens (fov ~1-2 deg from far away = near-orthographic: the world looks flat, exactly like the page). Text
and seals on the page are a transparent `plane` at the page distance. On the cue the camera dolly-zooms
(`dolly_zoom(target, direction, frame_h, d0, d1, n, u)`): it travels toward the page while the lens widens, so the
plane of the page keeps its size in frame and everything else acquires depth in place: near peaks swell, far ones
recede, mist separates, and the page text stays where it was written and is left behind in space. The page art you
hand to the room team is `Wd.render()` of frame 0 composited with the book paper (so the warp into the page and the
first frame of the 3D shot are the same picture).

## 5. Enliven (video models)
Order of preference, chosen per shot by looking (log the evidence in your team log):
(a) pure 3D render + procedural mist; (b) the 3D render's first (+ last) frame to minimax/h3 2K (`ratio: adaptive`) or
Seedance 2.0 for ink dynamics; (c) locked-plate clips (h3 on the element itself, camera fixed) used as `anim` textures
on the cards, so the camera stays ours and the pines/water/mist move for real. Typeset characters are never trusted to
a video model: render them in the 3D pass and composite them back.

## 6. Files
```
tools/world/world.js     three.js page: cards (displaced, ink material, fog, cloud sea, carve, light), mist, threads, passes
tools/world/render.mjs   headless GPU renderer (CLI)        tools/world/index.html   page
tools/world/scene.py     World builder, camera helpers, finish (grain + bloom), encode, 16-frame sheet
tools/world/prep.py      painted element -> rgba + depth (+ json)
tools/world/carve.py     typeset carvings in a card's UV space
tools/world/plates.py    painted element jobs (gpt-image-2)
design/world/plates/     generated sheets (+ .txt prompts)  design/world/cards/  prepared cards
```

## 7. Worked examples (v4 shots) and recipes for the other teams
- `shots/_dflight.py` + `shots/_dfinish.py` (D4-D6): one long flight cut into shots; carvings lit generation by
  generation through true shared components; gold threads; a cloud bank to climb through; the cloud sea rising per
  frame (`seaY` on the camera dicts: also `fogDensity`, `fogStart`, `paper`); a 2D element (STAGE's monkey clip) pinned
  to a point of the 3D world by projection (`shots/_dmonkey.py project()`).
- `shots/B3.py` (page -> world, room hand-over contract): the page plane carries the inscription + gutter; the
  world behind it is composed so that the page camera sees the page picture; the book paper grain is warped with the
  page for the first frames, then hands over to the screen grain; `write_page()` exports the page art for the room team.
- `shots/_jworld.py` (J2 / J5): page -> depth by a pure dolly zoom (take b: an orthographic-looking page becomes a
  deep world in 8 frames; nothing jumps) or by squashing the world onto the page and releasing it (take a,
  `flat_keys` + `truePos`); J5 runs it backwards and draws the painting in to a corner.
- K2b (BOOK): use the B3 recipe with the bedroom contract (page art `media/comp/pages/K2b_page.png`, framing as B3's):
  build the underworld page's elements as cards behind a page plane carrying the ledger text, compose them from the
  page camera, push through the page plane; dotted ghost-line figures = cards with `ink` < 1 and a dotted texture.
- Gotchas: never put backticks inside the GLSL strings in world.js; a mist's `scale` is its noise scale; near planes
  that scale with distance clip close mist (keep `near` <= 1.5); give glyph lit frames >= 0 unless they are lit
  before the shot starts (negative = already lit).

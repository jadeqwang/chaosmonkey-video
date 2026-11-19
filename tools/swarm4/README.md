# tools/swarm4: the SWARM v4 shot (F4+F5+F6a, 176 frames, s = 0..175, song t = 112.75 + s/24)

Headless three.js (r170) in Chrome through playwright-core, on the RTX 3090 (`--use-angle=gl`). Deterministic: every frame
is a pure function of (candidate JSON, s). No generation calls.

```sh
export TMPDIR=$PWD/work/tmp; PY=/home/jade/Documents/halys-video/.venv/bin/python
node tools/swarm4/render.mjs --cand work/swarm/cand_A.json --out work/swarm/render/A        # 960x540, all 176 frames -> f0000.png..
node tools/swarm4/render.mjs --cand ... --out ... --w 1920 --h 1080                          # 1080p (px sizes scale with height)
node tools/swarm4/render.mjs --cand ... --out ... --frames 0-40 | --frames 0,40,80
node tools/swarm4/render.mjs --cand ... --out ... --pass guide      # guide_####.png (flat greys + ink line + sprites + lanterns + threads, no fog) + depth_####.png
node tools/swarm4/render.mjs --cand ... --out ... --pass depth|ids  # depth (log, near = white) / ids (terrain grey, monkeys by branch)
node tools/swarm4/render.mjs --cand ... --out ... --mb 4            # cheap motion blur: 4 sub-frames over `motion_blur_shutter` (0.5 frame)
node tools/swarm4/render.mjs --cand ... --out ... --cams            # also <out>/cams.json: per-frame camera (matrices, fov) for plates / compositing
node tools/swarm4/render.mjs --cand ... --gl swiftshader            # CPU fallback (slow)
$PY tools/swarm4/encode.py work/swarm/render/A media/comp/F4F5F6a_A.mp4       # 24 fps, no audio, H.264 yuv420p
$PY tools/swarm4/sheet.py  work/swarm/render/A work/review/comp_v4/swarm_A.jpg  # 16 evenly spaced frames, labelled s + song time
$PY tools/swarm4/sheet.py  work/swarm/render/A_guide out.jpg --prefix guide_ [--frames 0,40,80]
```

Each render also writes `work/swarm/tree_<cand>.json`: every node (id, parent, gen, job, branch, position, depart, land,
blow, seal, beat switch frames), the ledge, the second monkey's spot and the apex camera matrices.

## Candidate JSON (`work/swarm/cand_A.json`); defaults in `engine/config.js`, `engine/terrain.js`, `engine/swarm.js` (SWARM_DEFAULTS)

| key | what |
|---|---|
| `camera.keys[]` | `{s, pos, target, fov, roll, path, ease}`; `path` (how the segment INTO this key moves): `smooth` (Catmull-Rom), `linear`, `log` (log-distance about the target, for the big rise/dive), `orbit` (around `center`, log radius), `hold`; `ease`: linear in out inout in3 out3 inout5. `{"apex": true}` = the apex camera. `camera.smooth_frames` (gaussian over +-n frames), `camera.min_clear` (m above ground) |
| points | `[x,y,z]` or `{ref, off}` with ref `ledge`, `root`, `second`, `apex`, `apex_target`, `node:<id>`, `mid:a,b`, `nearest` (+ `gen`, `to`, `rank`, `below` m), or `{orbit: {around, az, el, dist}}` |
| `camera.apex` | `{pos, target, fov}`: the projection camera for the silhouette (and the s75 frame) |
| `silhouette` | `image` (alpha, or white-on-black / black-on-white), `height` (fraction of frame), `center` or `anchor_uv` (mask uv placed on the ledge), `invert` |
| `tree` | `counts` [1,8,64,512,2048], `jobs`, `other_job_frac`, `seed`, `edge_frac` (leaves on the outline), `min_sep`, `parent_pull/below/min_dist/search` per gen |
| `spawn` | root hair (`from` camera-relative at s0, `land`), `root_appear`, `blow` per gen [12.0, 22.5, 33.2, 43.6], `flight`, `stagger`, `pluck_lead`, `blow_hold`, `arc` |
| `work` | `beats` (pose switch + bead per beat), `offsets` per gen [0,2,4,6,8], `until` |
| `seal` | `beats` [85.7, 95.7, 106.8, 117.1], `branches` per beat, `hop` (frames per generation), `jitter`, `vortex` (frames per beat), `hairs_per_monkey`, `hair_trail` |
| `second` | `land`, `dist`, `az`, `seal_left` 153.9, `seal_right` 169.5;  `root.sit`, `root.height` |
| `range_light`, `outline` | `[[s, v], ...]` the range darkening / faint outline mode |
| `look` | palette (azurite, malachite, ochre, ink, gold, sky, moon), `ink_weight`, `gold_strength`, `cun`, `green`, haze, valley mist |
| `mist` | `on`, `layers[]` `{y, size, density, scale, speed, soft, fade, thr}`, `video` (mp4 -> cached PNG frames used as density) |
| `pines`, `terrain` | counts/sizes; terrain seed, massif, columns, spires, peak, ledge |
| `post` | `bloom`, `bloom_radius`, `bloom_threshold`, `exposure`, `paper_grain`, `vignette`, `ink_bleed`, `saturation`, `paper_tint` |
| `swarm` | `monkeys.height` per gen, `lantern` (radius, min_px, intensity, flare, pulse, interior, light_radius, hero_*), `threads` (width, min_px, opacity per gen, bow), `beads`, `hairs`, `puffs`, `seals`, `slips` (window, n, min_px), `vortex` |
| `assets` | `sprites` (sprites.json), `pose_map` (engine pose -> sprite name), `faces_left`, `ref_px` (standing height in sprite px), `clips_dir`, `clips[]` `{who: root/second, clip, from, to, start, speed, loop, min_px}` |
| `projectors[]` | painted plates: `{image, frame: s}` (the shot camera at s) or `{image, camera: {pos, target, fov}}`, `amount`; blended by facing + projector depth visibility; up to 4 |
| `text` | `font`, `seal_font`, `seal_done` (讫), `seal_true` (真) |

Engine poses: `stand point pluck blow sit land seal` and `<job>_0/1` for read write reckon carry spar sweep watch grind.
Swapping assets is a JSON change (`assets.*`); anything missing falls back to drawn placeholders.
Clip folders: `<clips_dir>/<name>/clip.json` `{fps, frames, anchor: [x, y] px, pattern: "%04d.png", first: 1}` + RGBA PNGs.

## Files
`render.mjs serve.mjs index.html` CLI, static server (repo root), page. `engine/main.js` page API; `terrain.js` heightfield,
mesh, raycast; `look.js` terrain/sky/normal-depth materials; `glsl.js` noise + haze; `tree.js` silhouette leaves, balanced
k-means hierarchy, timing; `swarm.js` everything that moves; `sprites.js text.js clips.js` assets; `mist.js pines.js post.js camera.js`.

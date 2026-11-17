# Video bake-off (ink on paper)

2026-11-17. Budget $70 for this task. **Status: IN PROGRESS** (this file is checkpointed as results arrive).

Clips: `media/vbake/<test>/<model>_<variant>.mp4`, each with a `.txt` (model, job, exact input, prompt). Per-clip
10-frame sheets: `media/vbake/_sheets/<test>/`. Comparison sheets: `media/vbake/_sheets/<test>_cmp.jpg`. Synced grids:
`work/review/bakeoff/vbake_<test>_grid.mp4`. Metrics: `work/review/bakeoff/vbake_<test>.json`.

Tools written for this:
- `tools/gen/vbake.py`: every prompt (verbatim) and the per-model input mapping (16 image-to-video models + 2
  talking-head models). `vbake.py spec TEST --models ..` writes relay specs; `vbake.py file` files the results.
- `tools/gen/vbake_frames.py`: the derived first/last frames in `media/vbake/_frames/` (blank paper from the L3
  monkey sheet; single poses from the L3 pose sheet re-centred on that sheet's own paper).
- `tools/review/vbake_review.py`: intake (first-frame match, camera drift, flow, temporal std on ink and on paper,
  ink-coverage drift, invented marks and colour, frame repeats), 10-frame sheets, comparison sheets, synced grids.
- `tools/review/lipsync.py`: automatic lag and sync score for singing takes (see "Lip-sync procedure").

Catalog refreshed 2026-11-17 (`tools/gen/catalog.py`, cards @ 39a00b0): no new video models since 2026-11-13. MiniMax's
live video models are exactly `h3`, `h3-max`, `h3-lite`, `h3-highspeed`, `hailuo-2.3`, `hailuo-2.3-fast`; probes of
`hailuo-3`, `h3.1`, `h3.5`, `h3-pro`, `h4` all return "model not found". All six were run.

Model keys: kling4 = klingai/kling-v4 (720p), hh11 = alibaba/hh1.1-i2v (1080P), veo31 = google/veo-3.1 (1080p, 6 s, no
audio), sd20 = bytedance/seedance-2.0 (720p), sd25 = bytedance/seedance-2.5 (720p), h3 = minimax/h3 (2K; 768P in V2d/V3/V5),
h3max / h3lite / h3hs = minimax/h3-max / -lite / -highspeed (768P), hailuo23 / hailuo23f = minimax/hailuo-2.3 / -fast
(6 s 768P, prompt_optimizer off), pixv6 = pixverse/v6 (720p), ltx = lightricks/ltx-2-5-fast (1280x720), vidu3 = vidu/q3-pro
(720p), wan27 = alibaba/wan-2.7-i2v (720P), k3omni = klingai/kling-v3-omni (sound off), fabric = veed/fabric-1.0 (720p),
pavatar = pruna/p-video-avatar (720p).

## Submitted so far

- V1 and V2a on all 16 image-to-video models; V2d (first+last pose) on kling4, vidu3, sd20, h3, ltx; V3 first+last on
  kling4, vidu3, sd20, sd25, h3, ltx; V5 on sd25 (2 takes per line), fabric, pavatar, h3 (reference audio).
- First frames for V5 made with nano-banana-pro from the L5/L6 stills (`media/vbake/_frames/face_child.jpg`,
  `face_mom.jpg`, prompts beside them; $0.27).

## Checkpoint notes (raw, 01:35; superseded by the tables below once complete)

- V1 (mist, prompt v1): sd25 best so far (rock locked, std 0.9; soft white mist at the foot; but re-grades frame 0,
  ff_corr 0.88). sd20 locked but its "mist" is a thin grey streak on the horizon. kling4 locked but draws a literal
  hard-edged tan paper strip sliding across ("mist is the paper" taken as an object); hh11 a floating silk sash; veo31
  tilts down and invents more peaks; hailuo23 a grey-blue fog wall that swallows the rock, then clears to a nice foot
  mist; hailuo23f grey fog plus painted water; pixv6 pulls back and invents mountains and pines; vidu3 jump-cuts to a
  zoomed frame at 0.5 s; wan27 photographic billowing cloud. LTX needs an HTTPS image URL (7003): not testable here.
  MiniMax h3 family first failed 7003: **image-to-video requires `ratio: "adaptive"`** (fixed in vbake.py; resubmitted).
- V2a (staff flower): kling4, sd20, hh11, veo31, vidu3 all keep the ink figure and give a real spin; kling4, sd20
  and hh11 leave dry-brush rings ("the staff is a brush") for free. sd25 recomposes to a close-up. hailuo23 turns him
  into a flat black cel silhouette with a white mask; hailuo23f is stiff; pixv6 is wild splashed ink but adds a tail,
  zooms 1.5x and dirties the paper; wan27 OK but grows a third plume (30 fps).

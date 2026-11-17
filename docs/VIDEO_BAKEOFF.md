# Video bake-off (ink on paper)

2026-11-17. Budget $70 for this task. **Status: IN PROGRESS** — V1, V2 (a, b, c), V2d, V3 first+last, V5 measured;
V1b, V4, V6, V3 first-frame-only still arriving. This file is checkpointed as results land.

Clips: `media/vbake/<test>/<model>_<variant>.mp4`, each with a `.txt` (model, job id, exact input, prompt). Per-clip
10-frame sheets: `media/vbake/_sheets/<test>/<model>_<variant>.jpg`. Synced labelled grids (all models of a test, 4 across):
`work/review/bakeoff/vbake_<test>_grid.mp4`. Metrics: `work/review/bakeoff/vbake_<test>.json`. Lip-sync plots and numbers:
`work/review/lipsync/`.

## Tools written for this

- `tools/gen/vbake.py`: every prompt (verbatim) and the per-model input mapping (16 image-to-video models + 2
  talking-head models). `vbake.py spec TEST --models a,b [--variant v]` writes relay specs; `vbake.py file` copies
  finished clips into `media/vbake/`.
- `tools/gen/vbake_frames.py`: derived frames in `media/vbake/_frames/` (blank paper = the L3 sd5 sheet with the monkey
  erased; single poses from the L3 nbp pose sheet re-centred on that sheet's own paper). Singing close-ups
  `face_child.jpg` / `face_mom.jpg` were made with nano-banana-pro from the L5 / L6 stills (prompts beside them, $0.27).
- `tools/review/vbake_review.py intake|grid|compare TEST`: first-frame match, camera drift (ORB), flow, temporal std on
  the upper two thirds of the first frame's ink (V1: the rock above the mist) and on bare paper, ink-coverage drift,
  invented marks and colour, frame repeats; 10-frame sheets; synced grids.
- `tools/review/lipsync.py CLIP --audio work/stems/vocals.wav --t0 T`: automatic lag and sync score (see Lip-sync).

## Catalog and MiniMax

Catalog refreshed 2026-11-17 (`tools/gen/catalog.py`, cards @ 39a00b0): no new video model since 2026-11-13. MiniMax's live
video models are exactly `h3`, `h3-max`, `h3-lite`, `h3-highspeed`, `hailuo-2.3`, `hailuo-2.3-fast`; probes of
`hailuo-3`, `h3.1`, `h3.5`, `h3-pro`, `h4` return "model not found". All six were run on V1 and V2.

**Why h3 "failed 5 of 5" in HV**: with a first frame, h3-family models reject any `ratio` other than `"adaptive"`
(`7003 … image-to-video requires adaptive ratio`; the relay only stores "7003: User Input Error", a direct call shows the
reason). gen.py's DEFAULTS put `ratio: 16:9`. With `ratio: "adaptive"` all four h3 variants work, including first + last
frame. h3 cannot mix a first frame with `reference_audios` ("frame and reference inputs cannot be mixed").

Model keys and settings: kling4 = klingai/kling-v4 (720p) · hh11 = alibaba/hh1.1-i2v (1080P) · veo31 = google/veo-3.1
(1080p, 6 s, generate_audio false) · sd20 = bytedance/seedance-2.0 (720p, camera_fixed) · sd25 = bytedance/seedance-2.5
(720p) · h3 = minimax/h3 (2K; 768P for first+last and V6) · h3max / h3lite / h3hs = minimax/h3-max / -lite / -highspeed
(768P) · hailuo23 / hailuo23f = minimax/hailuo-2.3 / -fast (6 s 768P, prompt_optimizer off) · pixv6 = pixverse/v6 (720p)
· vidu3 = vidu/q3-pro (720p) · wan27 = alibaba/wan-2.7-i2v (720P, 30 fps) · k3omni = klingai/kling-v3-omni (sound off) ·
pavatar = pruna/p-video-avatar (720p) · fabric = veed/fabric-1.0 (720p).

Not testable on this relay: **lightricks/ltx-2-5-fast** (`image_uri` must be an HTTPS URL), **veed/fabric-1.0** (2047
"Invalid User Credentials" on 2 of 2 tries, likely the same URL requirement; not billed). **kling-v3-omni** treats
`image_input` as a loose reference, not a first frame (redraws a different picture: ff corr -0.04 / 0.42): dropped.

## V1 Landscape wakes (mist at the foot of the one-corner peak)

First frame `media/look/L1/qwen_v2.jpg`. Prompt v1 = the brainstorm's motion prompt adapted; v2 (leaders) describes the mist
as a soft feathered substance "the same cream colour as the paper", because v1's "the mist is the bare paper itself" made
two models draw an object (a paper strip, a silk sash). Rock std = median temporal std (0-255) of the rock above the mist
band; < 2 is locked like a still. Usable s = seconds a compositor can use as is.

| Model | $ / clip | Rock std | ff corr | Usable s | Verdict |
|---|---|---|---|---|---|
| **h3** (2K) | 0.65 | 1.7 | 0.997 | 5.2 | **Best.** Frame 0 exact at 2560x1440, rock and boulder locked, brush texture intact to the last frame, soft cream mist rises over the foot from 2 s. No birds, sun or colour. Mist is a touch white-grey rather than paper; key it as light |
| h3lite (768P) | 0.20 | 1.6 | 0.993 | 5.2 | Same behaviour for a third of the price; a thin mist band; paper slightly warmer. **Best value** |
| h3hs (768P) | 0.30 | 1.9 | 0.992 | 5.2 | Same; mist band a little blue |
| h3max (768P) | 0.40 | 6.6 | 0.991 | 5.2 | Same idea, mist denser and climbs higher over the rock (hence std) |
| kling4 v2 | 0.79 | 2.2 | 0.997 | 5.0 | Rock locked; soft foot mist, but invents a faint horizon line |
| kling4 v1 | 0.79 | 1.1 | 0.997 | 0 | Rock locked but the "mist" is a hard-edged tan **paper strip** sliding across: v1 wording taken literally |
| sd25 v1 | 1.16 | 0.9 | 0.884 | 3 | Locked, soft foot mist, but regrades frame 0, and the rock's hairline texture smears into worm-like ripples by 4 s; v2 came back **21:9** (1470x630) with grey streaks |
| sd20 v1 / v2 | 0.75 | 1.7 | 0.975 | 0 | Locked, but the mist is a thin grey streak on the horizon (v1) or it invents small distant islands (v2); paper grain boils (std 1.2-1.5) |
| hailuo23 v1 / v2 | 0.28 | 7.2 | 0.988 | 1 | A grey-blue fog wall swallows the rock and the rock dissolves into speckle; v2 tilts down. Last second (clearing mist) is pretty |
| hailuo23f | 0.19 | 2.7 | 0.988 | 0 | Grey fog bank plus painted water |
| veo31 v1 / v2 | 1.20 | 37-41 | 0.995 | 1.5 | Tilts / pans down unasked and invents more peaks and pines below the frame |
| hh11 | 0.90 | 13.6 | 0.999 | 0 | A floating brown silk sash, not mist |
| vidu3 | 0.63 | 14.0 | 0.998 | 0 | Jump-cut to a reframed picture at 0.5 s |
| pixv6 | 0.30 | 41.8 | 0.998 | 0 | Pulls back, invents mountains and pines |
| wan27 | 0.50 | 10.8 | 0.991 | 0 | Photographic billowing cumulus |
| k3omni | 0.57 | — | -0.04 | 0 | Ignores the first frame (redraws a different rock) |

Winning prompt (v1, as sent to h3):
```
Animate the first frame exactly. Locked-off camera. The painting does not move: the rocky peak, the round boulder on its
summit and every brushstroke stay exactly as painted. Only a long thin band of mist drifts slowly to the left across the
foot of the peak, veiling the lowest rocks as it passes and uncovering them again behind it. The mist is the bare unpainted
cream paper itself, not grey fog or smoke. Nothing new appears. No zoom, no pan, no change of light. No birds, no sun, no
water, no waves, no colour change.
```
(For non-MiniMax models use v2, in `tools/gen/vbake.py`.)

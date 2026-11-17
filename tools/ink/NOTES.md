# tools/ink build notes (checkpoint log)

Owner: compositing-engine agent. Python: `/home/jade/Documents/halys-video/.venv/bin/python`. Run from repo root.

## Layout
- `core.py` images/noise/ink primitives. `paper.py` Paper + key_paper. `camera.py` Scene/Camera multiplane.
  `ink.py` wash/stroke/splash/bloom/dissolve/hairline. `timing.py` Timing loader + stub. `run.py` shot runner.
- Demos: `tools/ink/demos/dNN_*.py` (each is a shot script), outputs in `work/ink_demo/` and `work/ink_demo/stills/`.
- README fragments while building: `tools/ink/_readme/*.md` (merged into README.md at the end).

## Gotchas found
- OpenCV thread pool deadlocks after fork: run.py keeps the parent single-threaded (cv2.setNumThreads(0)) and workers
  never re-enable threads. Do not call cv2.setNumThreads(>0) in a shot script. No torch/CUDA inside render(); do GPU
  work in setup() through ctx.cache() so workers only see numpy.
- Editing any tools/ink/*.py invalidates every shot's frame cache (key = engine source + shot file).

## Status: all 14 features built (2026-11-17)
| # | Feature | Module | Demo |
|---|---|---|---|
| 1 | Paper + keying | paper.py | d01_paper |
| 2 | Multiplane camera | camera.py (kinds ink, rgba, frame, erase, mist) | d02_camera |
| 3 | Ink dynamics | ink.py, stock.py (stand-in art) | d03_ink |
| 4 | Seal | seal.py | d04_seal |
| 5 | Rubbing | rubbing.py | d05_rubbing |
| 6 | Mis-registration, paper-cut, torn | woodblock.py (not print.py) | d06_print |
| 7 | Carved cliff | cliff.py | d07_cliff |
| 8 | Margins | margins.py | d08_margins |
| 9 | Inscription, subtitles | text.py | d09_text |
| 10 | Light | light.py | d10_light |
| 11 | Shadow screen, lantern | puppet.py | d11_puppet |
| 12 | Video ingestion, retime, roto | video.py, roto.py | d12_make_src, d12_video, d12_roto |
| 13 | QA | qa.py | stills/d13_* |
| 14 | Runner | run.py, shot.py | examples/ex1..ex3 |

timing.py reads the real analysis/timing.json (`cls` hits; hit_events spans folded in). `Timing.stub()` = synthetic map.
README.md is merged; `_readme/` fragments are deleted.

## Not done / next
- Nothing has been tried on real generated plates or clips (none existed): key thresholds and roto need tuning then.
- `Scene` kind='erase' was added after d12_video was written and is untested in a demo.
- BiRefNet matte path untested (venv lacks timm, kornia). SAM 2.1 works.
- Demo clips for d04-d12 were rendered before the last core edits; re-render to refresh (results should not change).
- Fork demos d04, d05, d06, d08, d11 use stub timing; examples use the real map.

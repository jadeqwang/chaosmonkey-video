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

## Status
| # | Feature | State |
|---|---|---|
| 1 | Paper + keying | done (paper.py); demo pending |
| 2 | Multiplane camera | done (camera.py, demo d02) |
| 3 | Ink dynamics | done first pass (ink.py); demo pending |
| 14 | Runner | done (run.py): mp4/ProRes/PNG/still/audio, resumable |
| 4,5,6 | seal, rubbing, print | delegated (fork A) |
| 7,9 | cliff, inscription text | delegated (fork B) |
| 12 | video ingestion + roto | delegated (fork C) |
| 8,10,11 | margins, light, puppets | delegated (fork D) |
| 13 | QA | next (lead of this build) |

# tools/edit: shot list → cut

Python: `.venv/bin/python`. Run from the project root. Outputs go to `work/edit/` (git-ignored).

## Commands, in order

```sh
# 1. shot list: edit docs/shots_src.yaml (one `cut:` line per shot), then rebuild docs/shots.json + docs/shots_report.md
.venv/bin/python tools/edit/build_shots.py
# 2. check: exits 1 on any cut > 1 frame from its anchor, gap/overlap, wrong totals; prints cut list + pacing
.venv/bin/python tools/edit/check_cuts.py
# 3. cards: T1 title frames (work/edit/title/T1, from docs/credits.json) and the G4 date card (design/cards/)
.venv/bin/python tools/edit/title_card.py t1
.venv/bin/python tools/edit/title_card.py date
# 4. assemble (profiles: animatic 960x540 burn-in no grain; preview 960x540 grain; master 1920x1080 CRF 14 AAC 320k)
.venv/bin/python tools/edit/assemble.py --name animatic_v0 --profile animatic
.venv/bin/python tools/edit/assemble.py --name preview_v1  --profile preview --burn-in
.venv/bin/python tools/edit/assemble.py --name master_v1   --profile master --audio work/sound/mix.wav
#    part of the film: --range C1:D4 (renders and joins those, with their audio); --only C3,G4 (renders, no join)
# 5. contact sheets (first/middle/last of every shot; one frame every 0.5 s)
.venv/bin/python tools/edit/contact.py --name animatic_v0 [--range C1:D4]
```

Useful assemble options: `--size WxH`, `--crf`, `--preset`, `--burn-in/--no-burn-in`, `--grain 0.035`,
`--grain-mode dynamic|static` (default: dynamic for preview and master, a new field every frame; static = one
field per shot, which reads as a dirty lens), `--no-phase-grade`, `--letterbox-open N` (bars ease open over N frames from the hit;
default 0 = hard cut), `--audio`, `--abr`, `--jobs`, `--force`.

What assemble guarantees: each shot is exactly `out_frame - in_frame` frames at 24 fps CFR (checked per shot); shots
are cached in `work/edit/<name>/shots/<id>.mp4` + `<id>.json` and re-rendered only when the shot record, its pick,
its source files (size/mtime), the options, or the edit code change; the join is a stream copy (x264 `stitchable`),
then checked: decoded frame count, every timestamp step exactly 1/24 s, video length, audio vs video within one frame,
tags `bt709/tv/bt709/bt709`, yuv420p. Outputs are written as `.partial` and renamed only when they pass. The song is
muxed untouched (AAC); the audio is 121.840 s and the picture 2924 frames = 121.833 s. Exit codes: 0 ok, 2 verify
failed, 3 the cut was built but some pick could not fill its shot (listed; those shots are slated in red).

## Cut source (`docs/shots_src.yaml`)

`cut: "<typed s> @ <anchor>"`. The cut time comes from the anchor, resolved in `analysis/timing.json`; the typed
number is checked against it and disagreements go to `docs/shots_report.md`. Anchors: `start`, `bar N`, `beat T`,
`word LINE WORD[#k]`, `event KIND T`, `key "NAME"`, `section "NAME"`. Frame = ceil(t·24) (the timing map's rule).
A shot ends where the next begins; the last ends at frame 2924.

## `docs/picks.json`

```jsonc
{
  // built by tools/grade/build.py from docs/grade.json (see "Grade" below); hand-written lift/gamma/gain still work
  "phase_grades": { "<phase>": {"lut": "work/grade/luts/phase_<phase>.cube", "grain_scale": 1, "grain_size": 1,
                                "lift": 0 | [r,g,b], "gamma": 1 | [r,g,b], "gain": 1 | [r,g,b], "sat": 1},
                    "print": {"lut": "...", "halation": {...}, "grain": {...}} },  // "print": the whole film
  "picks": {
    "<shot id>": {
      // the picture: one of these kinds, or no "kind" for a slate (overlays still apply)
      "kind": "still",  "src": "media/....jpg",
          "crop": [x, y, w, h],                      // optional, 0..1 of the source; the view is then cover-fitted
          "move": {"from": {"zoom": 1.0, "x": 0.5, "y": 0.5}, "to": {"zoom": 1.15, "x": 0.45, "y": 0.4},
                   "ease": "inout" | "linear"},     // x, y = centre of view in 0..1 of the source; zoom 1 = cover fit
      "kind": "video",  "src": "media/gen/....mp4",
          "in": 1.25,          // source seconds shown on the shot's first frame
          "rate": 1.0,         // source seconds per film second (0.5 = half speed, 2 = double)
          "interp": "hold" | "blend",   // slow motion: repeat source frames (hold) or cross-blend neighbours
          "crop": [x, y, w, h], "flip": false,
          // fails loudly (slate "TOO SHORT") if in + (frames-1)*rate/24 is past the source's end: never freezes or loops
      "kind": "frames", "dir": "work/sky/G4", "pattern": "*.png", "start": 0, "crop": [...], "flip": false,
          // a pre-rendered sequence, one file per film frame; RGBA is composited over black

      "overlay": [                                   // applied in order, after the grade unless "pre_grade": true
        {"src": "design/cards/g4_date_card.png", "blend": "over" | "screen" | "add", "opacity": 1.0},
        {"dir": "work/sky/D1_crescents", "pattern": "*.png", "start": 0, "blend": "screen", "pre_grade": true}
      ],
      "grade": {"lift": ..., "gamma": ..., "gain": ..., "sat": ..., "lut": "x.cube", "blur": 0.6,
                "to": {...a grade dict...}, "ease": "inout", "span": [0, 1],
                "mattes": [{"dir": "work/grade/mattes/C6", "pattern": "m*.png", "lut": "x.cube"}],
                "window": {"center": [0.5, 0.44], "radius": [0.2, 0.24], "soft": 0.7, "outside": -0.45},
                "print": true, "halation": {...} | false} | false,  // per-shot, after the phase grade; false = no grading at all
      "phase_grade": true,      // false skips the phase placeholder for this shot
      "grain": null | false | 0.02,   // null = the run's --grain; false = none; number = this strength
      "seed": 1234              // grain seed (default crc32 of the shot id)
    }
  }
}
```

Keys starting with `_` are comments. Slates (no pick, or a failed pick) are not graded and get no grain. Per-frame
order: source → pre-grade overlays → phase grade → shot grade → halation → print LUT → overlays → grain → letterbox (black bars, 2.39:1,
on every frame before the 40.98 hit) → burn-in (bottom-left, inside the picture area).

## Files

| file | what |
|---|---|
| `common.py` | paths, frame rule, anchor parse/resolve, timecode |
| `build_shots.py` | `docs/shots_src.yaml` → `docs/shots.json`, `docs/shots_report.md` |
| `check_cuts.py` | the cut checker |
| `assemble.py` | per-shot render + join + verify |
| `contact.py` | contact sheets |
| `title_card.py`, `typeset.py` | T1 title frames and the G4 date card; type after holdfire's end card (fonts in `design/fonts/`, OFL) |

## Grade

The look is set in `docs/grade.json` and nowhere else; `tools/grade/build.py` turns it into 3D LUTs
(`work/grade/luts/*.cube`, 33³, rebuildable, readable by Resolve), writes `docs/picks.json` → `phase_grades` and the
per-shot fragment `docs/picks_grade.json`; then `merge_picks.py` lays the fragment over the picks. Parameters
(exposure, temp/tint, black, gamma, PCHIP tone curve, split toning, sat and sat-vs-luma, hue qualifiers with
shift / sat / "keep warmth") are documented in `tools/grade/look.py`; the look itself in `docs/GRADE.md`.

What assemble does with it (all optional; a picks file without these keys renders exactly as before):

- **grade dict** (phase or shot): `blur` (Gaussian sigma in px at 1920 wide, for over-sharp renders), then the
  simple `lift/gamma/gain/sat`, then `lut` (trilinear). `to` (another grade dict) makes it time-varying: the two
  results are blended by the eased shot position (`ease` inout|linear, over `span` [u0, u1] of the shot). A shot
  with trims carries its own LUT (trim then phase look baked together) and `"phase_grade": false`.
  `mattes`: a secondary, that LUT applied inside per-frame grey mattes (SAM 2.1, `tools/grade/matte.py`: C6's
  tunics, the totality faces). `window`: a soft elliptical dodge, the outside `outside` stops darker (the kings).
- **print** (`phase_grades.print`): after the phase and shot grades on every graded shot (not slates, not
  `grade: false`, not with `--no-phase-grade`; a shot can opt out with `grade.print: false`). First `halation`
  (`threshold` on max(R,G,B), `radius` px at 1920, `strength`, `tint`: light above the threshold bleeds back as a
  soft red-orange glow; a shot can override or switch it off with `grade.halation`), then the print `lut`.
- **grain model** (`phase_grades.print.grain`, used whenever present, also with `--no-phase-grade`): luma-weighted
  film grain at the run's strength (`--grain`, the profile's 0.035) × the shot's `grain` × the phase's
  `grain_scale`. Fine grain (`fine` sigma px) in the highlights, coarse (`coarse`) in the shadows, both × the phase's
  `grain_size`; `chroma` is the relative strength of a 3-channel colour grain (`chroma_size`); `curve`
  [[luma, mult], ...] shapes the amplitude. Without a model the old flat field is used. `--grain-mode` applies (dynamic by default: living grain).

Cache: LUT files enter each shot's key by size + mtime; `build.py` rewrites a LUT only when its content changes.

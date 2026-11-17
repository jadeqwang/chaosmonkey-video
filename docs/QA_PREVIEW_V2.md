# QA: preview_v2 (lyric pass, second complete cut)

Lyric pass, 2026-11-17. Spend $0: nothing was generated.

**The two cuts:**
- `media/cut/preview_v2.mp4`: the film's lyric layer on.
- `media/cut/preview_v2_clean.mp4`: the same picture with no lyrics.

Both are 960x540, 24 fps CFR, **5720 frames**, with `media/sound/mix_v1.wav`. Video and audio are both 238.333 s (238.3333 against 238.3330), so A/V is within a frame. Contact sheets are in `work/cut/preview_v2*/contact_*.jpg`.

**Review material in `work/qa/v2/`:**
- `sheets/preview_v2_every12_00..13.jpg`: every 12th frame, labelled.
- `sheets/preview_v2_lyrics_00..11.jpg`: one full-size frame per lyric segment.
- `sync/`: per-frame stats, event windows and the alignment check.

Before-and-after diffs of the re-render are in `work/lyricpass/diff/<ID>.jpg`, with the table in `work/lyricpass/compare.tsv`.

## 1. What was done

**Part 1: per-shot lyrics off, one switch.**
- `tools/ink/run.py` now builds a real `ctx.opts` dict (new module `tools/ink/opts.py`). It is filled from env `INK_LYRICS` (**default off**) and from `--opt key=value` (repeatable).
- `opts` is part of the frame-cache key.
- Every variant of the switch now resolves to `tools.ink.opts.lyrics_on(ctx)`:
  - `_rooms26`, `_rooms88`, `_heaven` and `puppet_lib`;
  - `tools/stage/stage.py` (it read `STAGE_LYRICS`);
  - the direct `getattr(ctx,'opts',{})` reads in D5, H3 and H4.
- **Art separated from the switch.** D5's 一通百通 + 悟空 inscription, and J5's 一通百通 inscription with its 悟空 echo seals, were behind the lyric switch. They now always draw.
- Seals (倉 才 台), the ledger, the cliff text and E2's book text were never behind the switch.
- **Frame cache.** `run.py`'s cache key now also hashes the shared helpers (`shots/_*.py`, `shots/*_lib.py`, `tools/stage/*.py`). Section 2 explains why.
- **Re-render.** All 72 files were re-rendered `--fresh` with lyrics off: 58 shots plus the 14 parts of the 7 spliced shots, each on its v1 frame range.
  - Every count is exact. The old comps are in `media/comp/_v1/` (spliced ones in `_v1/spliced/`), and the v1 PNG caches are hard-linked in `work/ink_v1/`.
  - One worker hung on H2's last frame. It was resumed from the cache (same key).
- **Splice.** `tools/cut/splice.py` gives every spliced shot its exact count: C5 115, D2 80 (65 + 15), F3 41, F4 83, F6 83, I3 97, K2 78.

**Assembly bug found and fixed.** `assemble.py` decoded every source through a raw pipe with FFmpeg's default `cfr` timing, which duplicated and dropped frames wherever the source timestamps jittered.
- This affected the spliced files most: D2's room part showed up 2 frames late in the cut, although `spliced/D2.mp4` itself was exact.
- The fix is `-fps_mode passthrough` on the decode.
- `work/qa/v2/sync/align.py` compared every frame of preview_v2_clean with its source: **0 misaligned frames out of 5720**.
- The QA v1 "+1/+2 splice" offsets and several of its "duplicate frames inside moving shots" (F3 2692, K2b 5105, L1 5517) were this bug.

**Part 2: one lyric layer.** It is in `tools/cut/lyrics.py`, wired into `assemble.py` as `--lyrics on|off` (default on for preview and master, off for animatic). Section 4 has the settings.

## 2. Did the re-render change anything except lyric text?

Every frame of every shot was compared losslessly: the v1 PNG cache against the new PNG cache, with a pixel threshold of 6/255.
- **Identical picture, only lyric text gone:** B1, C5a, D2, D3, E1, E3, F1-F6 (except F3b), G1, H3, H4, I1-I4, J2, J3, J4, K1-K5, L1.
- **Bit-identical (no lyric was drawn):** A3, A4, B3-B5, C1, C2, C4, C5b, C6, D2d, D4-D9, E2, E4, F6b, G2-G6, H1, H2, H5, H6, J1, **J5, D5 (art kept)**, L2, L3.

**Changed beyond the lyrics: 8 files.** All 8 v1 comps had been encoded from frame caches made *before* their team's own later helper edits. The runner's cache key ignored `shots/_*.py`, so `--fresh` was the only way to pick those edits up. The new pictures are what the current scripts render. Nothing from the fix rounds was lost: every fix-round shot is identical apart from lyrics.

| File | What differs | Cause (helper edited after the v1 cache) |
|---|---|---|
| A1, A2 | The attic is darker and the window glass stays red where v1 had pale blue. In A2 the red pool is dimmer | `_attic_grade.py` (02:19: floor and percentiles) and `_rooms88.Sign` (checkpoint 9: glass cools at 0.45, not 0.75; red-glass detection) |
| B2, C3, E5, E6 | Only the window glass: red-pink, not pale blue | `_rooms88.Sign`, as above |
| F3b | The same framing (scale 1.00, shift ≤ 1 px), but slightly different clip frames (hair strands) and grade. The match cut still lines up | RoomShot / clip timing changed after the 02:29 cache |
| D1 | The 倉 seal's face is drawn differently | `tools/stage/stage.seals()` (fix 2: 館閣楷 白文) |

**Look at A1/A2:** the opening is now darker and the sign stays red through the blue phase. It is what the code says, but it is a visible change to the film's first shot.

## 3. Changes since v1, by QA item

Item numbers are those of `docs/QA_PREVIEW_V1.md`. Sources: `docs/logs/LOG_polish1.md` (P1), `LOG_fix2_book.md` (F2B), `LOG_fix2_rooms.md` (F2R), and this pass.

| # | Item | Status | Where / note |
|---|---|---|---|
| 1 | L2→L3 click-off | **fixed** | P1 (L2 thumb press) + F2R (L3). Measured: black from f5660 (luma 80→2.0), window up f5670-5672 (3.4/6.7/9.3), neon off f5709 |
| 2 | E3 stick | **fixed** | F2R: painted out to a dark shoulder |
| 3 | B3 indigo frame | **fixed** | P1 (attic + red book rim) + F2B (edge out of frame from ~f690) |
| 4 | Lyrics | **fixed** | This pass: one layer, sections 4-5 |
| 5 | Splices late | **fixed** | splice.py (frame-exact) + **the assemble.py retiming fix above**. All 7 splice frames now on their logged frames |
| 6 | 脸谱 faces vector-like, pre-stamp blobs | **partly** | F2B faces: blobs gone, painted surface added. It reads at the close framings; at the full leaf (H2 end, H4) the faces are 60-90 px and still look smooth |
| 7 | Centred faces | **partly** | F1, G1 and K2a reframed off-centre and I4 is a 70→0 % ghost (F2R). F1's hands still press in prayer (the take) |
| 8 | Sync 2-6 f late | **fixed** | F2B/F2R floor-frame rule + the assembly fix. Table in section 6 |
| 9 | E1/F1/G1 hits | **fixed** | E1 flare + cut-in on f2088; F1 sweep visible f2592 (full by f2595); G1 margins enter f2925-2926 |
| 10 | K5 payoff | **fixed (lead to judge)** | F2B re-frame at scale 1.20: bare column lit, exposure matched to K4. Lyric moved off the column (lower left in the dark) |
| 11 | I1 white-in, torch blooms | **partly** | F2R: no dissolve, hard pool, `dehalo` on K1/L1. I1's straight light-shaft from the take remains |
| 12 | G4 halo | **fixed** | F2R: edge-on band landing on 'wear', bun |
| 13 | D2 bows, 才 as キ | **fixed** | F2B: three distinct compass bows + 館閣楷 白文 seals. Bow 4 (D2d, little Jade) is shallow by design |
| 14 | J3 red filter, J2 dim | **partly** | F2B: J3 neon multiplied, J2 relit. At the end of J2's pull-back its hard pool reads as a flat moon-like disc |
| 15 | F6b ghost reflection | **fixed** | F2R: 25 %, mirrored, waving on the same frames |
| — | D8 outline ghost | fixed | F2B: sinks into the paper |
| — | B4 moon pass, B4→B5 jump | partly | F2B: warm moon; the jump is about 40 levels, down from 57 |
| — | L1 2D warp | open | — |
| — | QA dup frames F3 2692, K2b 5105, L1 5517 | fixed | They came from assembly; the frame-difference series is now continuous. J4 4778 and H1 3701 are designed holds |

## 4. The lyric layer: settings

Everything is a named constant at the top of `tools/cut/lyrics.py`.
- **Lines.** All `analysis/timing.json` lines are shown with their own spelling, punctuation and spacing: **55 of 68**.
  - Hidden: the 10 parenthetical echoes (including 百通), "(ps ps ps)", and the two 一通百通 lines (art in picture).
  - "Monkey!" and "Yes" are shown.
- **Rap** (107.04-121.47): the Chinese line, with the brainstorm's working English beneath it at `RAP_EN_SCALE` 0.80.
- **Type.**
  - Latin: EB Garamond (variable, weight 500), 60 px at 1080p. That gives an x-height of 24 px (12 px at 540p) and a cap height of 39 px.
  - Child lines: EB Garamond Italic.
  - CJK: LXGW WenKai, sized so the ideograph ink height is 1.18× the Latin cap height (about 27 px at 540p). It is raised so its ink centre sits on the Latin cap centre.
  - A space between two CJK characters is 0.45 em.
  - Fonts mix run by run in one line ("妈妈, will you…", "how 孙悟空 came…", "Then 听话, or…").
  - Glyph coverage was checked with fontTools: no missing glyph (no tofu).
- **Layout.** The baseline of the last row sits at 0.86 H. A line wraps into balanced rows when it is wider than min(62 % of W, the centred 4:5 area less 3 % a side), which is 406 px at 540p.
  - Up to 4 rows are allowed in narrow overrides.
  - A break after a comma is preferred within 6 %.
  - Shrinking stops at 0.8.
- **Voices.** Mom and both: upright. Child: italic Latin; CJK keeps the same weight. No names, no colours.
- **Timing.**
  - Each word appears on the frame containing its onset, at 70 % and then 100 % (2 frames).
  - A line clears 6 frames after its end time, or when the next line actually shows, whichever is first.
  - At a room ↔ book/stage cut, including the cuts inside spliced shots (`PARTS`), the line clears. It re-appears in the new world on its next word onset, if one is left.
  - A line that would show for fewer than 4 frames before a cut starts at the cut instead. This avoids 1-frame flashes, at E6→F1, K1→K2a and C2→C3.
- **Colour.**
  - Paper ground: ink (0.20, 0.175, 0.15) at 85 %, multiplied, with an 8 % grain and slightly rough edges (edge noise 0.30 at a 1.6 px cell, 2× supersampled). No stroke, no shadow.
  - Night ground: cream (0.935, 0.905, 0.835) at 92 %, over a feathered dark wash multiplied behind the line. The wash reaches 0.55 em past the letters with a 0.45 em feather, at 0.10-0.35 strength from the 90th-percentile luma under the line.
  - The ground is decided per frame from the mean luma under the text box, with hysteresis: paper ≥ 0.50, night ≤ 0.38, in between keep the previous ground; hysteresis is reset at a room ↔ page change.
  - A ground must hold 8 frames to switch, so flashes and rubbing flips never switch it, and the text holds steady through flips and mis-registration.
  - In the final cut every ground switch falls on a cut or splice: B2 is night throughout; C5, D2, D3, K2 and I3 switch at their part cuts.
- **Mist** (an override key): bare paper laid behind the line on full-bleed carved rock: B4, B5, C6, D5, H4, H5.
- **Clean cut.** The layer is composited in `assemble.py` after the shot is laid and before the burn-ins, so `--lyrics off` gives a clean cut. Each shot's decision is stored as `lyrics.json` in its render-cache directory.

## 5. Placement overrides

There are 52 entries in `OVERRIDES` (including two per-line entries for G2). Every lyric frame of preview_v2 was checked on `work/qa/v2/sheets/preview_v2_lyrics_*`; none sits on a face, a hand, the monkey, a seal, the struck entry or the bare ledger column.

| Unit | Placement | Why |
|---|---|---|
| B1, E3 | x 0.27 | Over the dark left, off the child |
| B2 | lower left, y 0.93 | Off the book in Mama's hands; stays dark through the push |
| B3 | x 0.72 | Bare page right of the mountain |
| B4, B5 | centred + mist 0.55 / 0.45 | Full-bleed cliff / rides B5's mist band |
| C1 | right, y 0.78 | Off the egg and its crack |
| C2 | x 0.82 | Off the hand and its shadow |
| C3, C5a, E6 | lower right | Off the two hands / Mama / the child |
| C5b, C6 (+mist), D1 | x 0.68 / 0.72 / 0.76 | Beside the egg / off the splash and monkey |
| D2 | right x 0.83 | Off the bowing monkey, right of the seals |
| D2d, D3b | lower left | Off Mama, the child and the book |
| D5, D6 | x 0.82 (+mist in D5) | Off the mountain; under the 悟空 seal and 一通百通 column |
| E1 | lower right, y 0.93 | Off the nose tap |
| E2 | lower right, narrow | Bare paper under the book text, off the troop |
| F1, F2 | lower left (dark seats / door) | Off the child's hands and the puppet pane |
| F3a | lower right (seat back) | Off the blowing hand |
| F3b | mid-left, y 0.60 (12 f) | Mama's dark sweater: the only spot off book, palm and face |
| F5, F6a, F6b | x 0.62 / 0.56 / 0.30 | Empty seat / console / under the reflection |
| G1 | x 0.70 | Dark wall right of the face |
| G2-G5 | **right margin**, ink, left-aligned (G2 line 36 at x 0.828 in 4 rows; line 38 at x 0.735; G3 0.665; G4/G5 0.635) | The strip is too narrow, and the lower centre is inside the strip, so the line goes on the bare-paper side margin |
| H3 | y 0.90 | Under the chins |
| H4 | y 0.965, 0.9×, mist | Under the album's bottom row |
| H5 | x 0.635 in 3 rows, mist | The rock gap between carved columns |
| H6 | lower right, 0.8× | The emptiest frame; away from the hair-line |
| I1 | lower left, delay 12 f | After the white-in; off the lit book |
| I2 | lower right, narrow | Off the hands and page |
| I3a / I3b | lower right / lower left | Off her face / off the banquet table |
| I4 | y 0.95, night | Centred face: below the chin, on the dark collar |
| J1 | lower left | Off the pointing hand |
| J3 | x 0.80 | Off the monkey's stance |
| K1, K2a | lower left / lower right | Off the book, lap and reading face |
| K3 | lower left in the dark | Not over the struck entry |
| K4 | right dark strip, 0.9× | Off the turning pages |
| K5, L1 | lower left in the dark, night | Nothing over or under the bare column; L1 continues K5's line from the same frame |

**Lines that could not be placed well:**
- **Over carving.** B4, C6's first frames, the start of D5 and H5 are full-bleed carved cliff, so the line sits over carving with a mist band. The alternative is to drop lyrics on those four.
- **H4.** Mid pull-back (f3990-4015) the line touches the bottom row of faces.
- **F3b.** 12 frames out of the lower third.
- **G2 line 36.** 4 rows in a 154 px margin.
- **H6.** Small by request: x-height about 9.6 px.
- **J3's last 7 frames.** On the white page, cream on a light picture (too short to switch ground).
- **The 4:5 safe area.** About 25 corner and margin placements sit outside it. A vertical cut would need its own placement table.

## 6. Sync: before and after

"Before" is the QA v1 row (Δ against ceil(t·24)). "After" is the first visible frame, measured on preview_v2_clean (`work/qa/v2/sync/windows.txt`), with Δ against ceil and against floor (the frame containing the event, the fix rounds' rule).

| Event | t | ceil f | Before Δ | After f | After Δ ceil / floor |
|---|---|---|---|---|---|
| Crack (C1) | 43.635 | 1048 | +3 | 1047 | −1 / 0 |
| Flip 1 / 2 / 3 | 43.805 / 44.040 / 44.385 | 1052 / 1057 / 1066 | +2 / +2 / +3 | 1051 / 1056 / 1065 | −1 / 0 each |
| Bow 1 / 2 / 3 | 61.321 / 62.205 / 63.090 | 1472 / 1493 / 1515 | 0 / +1 / +1 | 1471 / 1492 / 1514 | −1 / 0 each |
| Bow 4 + 倉 (D2d) | 63.980 | 1536 | +2 | 1535 | −1 / 0 (room cut exact at 1531) |
| Verse-2 crash (E1) | 86.998 | 2088 | none | 2088 (flare + cut-in) | 0 / +1 |
| Rap crash (F1) | 107.975 | 2592 | none | 2592 sweep (full 2595) | 0 / +1 |
| Margins begin (G1) | 121.905 | 2926 | +68 | 2925-2926 | 0 / 0 |
| Margin step 1 / 2 | 130.175 / 133.690 | 3125 / 3209 | +2 / +6 | 3124 / 3208 | −1 / 0 each |
| Margin step 3 (G4) | 141.450 | 3395 | 0 | 3394 | −1 / 0 |
| Tool / threat / trick / kid | 162.63 … 165.24 | 3904 / 3924 / 3945 / 3966 | −1 / 0 / +1 / +2 | 3903 / 3923 / 3944 / 3965 | −1 / 0 each |
| Echo formed 1 / 2 | 191.51 / 192.37 | 4597 / 4617 | 0 / not seen | 4596 / 4616 (red +542 / +467 px) | −1 / 0 |
| Echo warmed / no song | 195.65 / 198.74 | 4696 / 4770 | +2 / +2 | 4695 / 4769 | −1 / 0 |
| J5 seal / echo 百通 | 202.03 / 202.46 | 4849 / 4860 | +1 / not seen | 4848 / 4859 (red +72 px) | −1 / 0 |
| K4 page lands 1 / 2 / 3 | 218.22 / 220.92 / 221.805 | 5238 / 5303 / 5324 | 0 / +3 / +4 | 5237 / 5302 / 5323 | −1 / 0 each |
| Flashlight off / L3 black | 235.833 | 5660 | none | 5660 black (luma 2.0) | 0 / +1 |
| Window up | — | 5670-5672 | — | 5670 / 5671 / 5672 (luma 3.4 / 6.7 / 9.3) | as logged |
| Neon off | 237.840 | 5709 | +1 | 5709 | 0 / +1 |

**Splice frames:**

| Splice | Logged | v1 measured | v2 measured |
|---|---|---|---|
| C5a\|C5b | 1311 | 1313 | **1311** |
| D2\|D2d | 1531 | 1533 | **1531** |
| F3a\|F3b | 2694 | 2695 (+ dup at 2692) | **2694**, no dup |
| F4a\|F4b | 2744 | 2745 | **2744** |
| F6a\|F6b | 2895 | 2897 | **2895** |
| I3a\|I3b | 4431 | 4432 | **4431** |
| K2a\|K2b | 5091 | 5092 | **5091** |

No row is still late. Every event now lands on the frame containing it; against QA's ceil rule that is 0 or −1, within tolerance.

## 7. Remaining open issues, ranked

1. **The opening changed look.** A1/A2 (and the window glass in B2, C3, E5, E6) now render with the attic grade and sign code the rooms team wrote after their v1 caches: darker, with red glass where v1 had blue. The lead should approve it or roll the helper back (section 2).
2. **H1-H4 faces** still read smooth and digital at full-leaf framings, and the 17 faked builds show a 2-frame colour smear (QA 6, partly).
3. **The carved cliffs and the lyric.** B4, C6, D5 and H5 have no bare area, so the line sits on carving behind a mist band. Decide: keep it, or no lyric on those four.
4. **Take-level problems** (need regeneration): F1's hands pray instead of chopping, and the daughter's hair is ginger; C5a shows "shh" not a blow; C5b's egg fades rather than being wiped; K4 has no hands; D2d's bow is shallow.
5. **Vertical cut.** About 25 lyric placements fall outside the 4:5 safe area. A vertical cut needs its own placement table.
6. **L1** pull-back warps the room like a flat picture (open). **I1** keeps the take's straight light shaft. **J2**'s end pool reads moon-like.
7. **B4→B5 paper jump** is about 40 levels. B4's glyphs are all equally red, so the sun pass is weak. **C1 and C4** are different egg drawings.
8. **Holds that drag:** G2 (6.9 s), E2 (3.6 s, realistic macaques), K4 (7 s of near-identical spreads). The loud D6-D8 stretch is under its ink budget.

## 8. Files changed in this pass (for the lead's commit)

- **New:** `tools/ink/opts.py`, `tools/cut/lyrics.py`, `docs/QA_PREVIEW_V2.md`.
- **Edited:**
  - `tools/ink/run.py`: `ctx.opts`, `--opt`, cache key covers opts and the shared helpers.
  - `tools/ink/README.md`.
  - `tools/cut/assemble.py`: `--lyrics`, the lyric pass, `-fps_mode passthrough`.
  - `tools/cut/README.md`.
  - `tools/stage/stage.py`.
  - `shots/_rooms26.py`, `_rooms88.py`, `_heaven.py`, `puppet_lib.py`.
  - `shots/D5.py`, `J5.py` (art always on), `H3.py`, `H4.py`.
- **Re-rendered:** all of `media/comp/*.mp4` and `media/comp/spliced/*`. The v1 copies are in `media/comp/_v1/`.
- `docs/picks.json` was rewritten by splice.py with the same content.
- **Work files:**
  - `work/lyricpass/` (render script, logs, compare).
  - `work/ink_v1/` (hard links to the v1 caches, about 6 GB of links; it can be deleted after review).
  - `work/qa/v2/`.

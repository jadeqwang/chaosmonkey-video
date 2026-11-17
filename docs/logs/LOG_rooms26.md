# LOG: ROOMS-26 (car F1 F3a F4a F6b; bedroom I1 I2 I3a I4 J1 K1 K2a L1 L2)

Python `/home/jade/Documents/halys-video/.venv/bin/python`, run from the repo root. Shared code: `shots/_rooms26.py`
(clip plates, page-art mapping, paper fibre, ECC tracking, lyrics switch `ctx.opts['lyrics']` / env `INK_LYRICS=0`),
`shots/_bed_grade.py` (one white pool, dark violet outside, faces kept by bounce), `shots/_car_grade.py` (dusk violet,
one amber sweep). Generation: `media/gen/rooms26/` (`mkspecs.py` = every prompt, `picks.json` = chosen take + song time
of its frame 0, `lipsync_c.jsonl` / `wordsync.jsonl` = sync measures, `paint_kf.sh` = keyframe prompts).

**Lip-sync measuring note.** `tools/review/lipsync.py` unconstrained put 5 of 6 first takes at -0.7..-1.15 s; by eye
(mouth strips, `work/rooms26/mouths.jpg`) those are spurious peaks (backing vocals / continuous rap in the window):
F1 opens 3 frames before 石 (in sync), I4 opens on "Wouldn't". Numbers reported are lipsync.py with `--maxlag 0.35`
plus a word-gated check (`media/gen/rooms26/wordsync.py`: mouth vs measured word spans). Wide shots (I1, K1, F4a) use
the dark-box fallback (face too small for FaceMesh): their r is not meaningful.

**Keyframe vs clip:** sd25 reframes frame 0 (I1's book ~40 px higher than in `I1.jpg`): page quads are measured on the
CLIP frames, not the keyframe or the sidecar.

| shot | frames | status | sources | QA / sync | weak |
|---|---|---|---|---|---|
| I4 | 67 (4488-4555) | done | sd25 take 1 `r26_I4_0c73641138` (t0 186.49); `I4_mama.jpg` ghost; `I4b.jpg` still + `D_banquet.png` on the spread; `handshadow_silhouette.jpg` | lipsync.py r 0.37 sharp 0.32; word-gated r 0.41 (+83 ms) -> no retime | Structure follows the MEASURED hits: I4a 187.000-187.500 (Mama ghost 70 % frames 0-7, 35 % frame 8, gone frame 9), I4b 187.500-188.417 (shadow re-posed on 187.46 / .781 / .097 / .313, ends on the drum dropout), I4a 188.417-end ("You're able."). The brief's "last ~1.4 s" could not hold with hits at 187.46-188.31. Hand-shadow is the canon head silhouette (reads as a monkey head, small at 540p). I4b is the still (no Kling clip used: the hand would not match the shadow) |
| I1 | 72 (4253-4325) | done (weak sync) | sd25 take 1 `r26_I1_0068530c94` (first+last I1 -> I1_end, t0 176.71); page = worn left page + `B_master` + `A_crayon_monkey_rgba` | dark-box r 0.16 (face small), word-gated r 0.25 | Sync not measurable with confidence (face ~120 px); the mountain sits on the visible band of the page, half under her knee; the crayon monkey is small (~45 px at 1080p) right under the fingertip at the end. First 7 frames come out of the page's white (glare) |
| K1 | 164 (4889-5053) | done (weak sync) | sd25 take 1 `r26_K1_d6327b8779` (first+last K1 -> K1_end, t0 203.22); `media/comp/pages/I2_page.png` before the turn, `E_king_desk.png` after (switch at clip frame 158) | word-gated r 0.35 at 0 ms; lipsync.py r 0.13 (dark-box) | Page art is foreshortened hard (the painted book is seen at a grazing angle); the turning leaf carries the heaven art until it passes upright |

Spend so far: 18 relay jobs ($16.09) + 4 keyframe paints ($0.54) + 4 lip takes I3a/K2a ($3.70) = **$20.33**.

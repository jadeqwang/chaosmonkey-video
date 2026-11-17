# LOG v3 LIPSYNC

## CHECKPOINT 14:58
**Done**
- Read the brief, recon, bake-off and QA docs. Live catalog probed (free): there is NO Kling lip-sync/avatar endpoint, NO
  OmniHuman, Hedra, sync.so, Wan-S2V or any video-to-video lip-sync model on this relay (23 names probed, all "model not
  found"). `omni12` in `tools/gen/bakeoff.py` is `google/gemini-omni-1.2-flash`, not OmniHuman.
  Audio-taking models that exist: `bytedance/seedance-2.5` (reference_audios), `bytedance/seedance-2.0-mini`
  (reference_audio, described as background music), `pruna/p-video-avatar`, `veed/fabric-1.0`, `google/gemini-omni-1.2-flash`.
- Start frames (gpt-image-2, v3 refs, $0.90): `media/kf/v3/lipsync_test/{lj_sing,mama_sing,dau_sing,jade_sing}.jpg` (+ `.txt`
  prompts, `_1920.jpg` copies). Generator: `tools/gen/ls3_frames.py`.
- Spec builder with every prompt and audio window: `tools/gen/ls3_bake.py` (lines a = little Jade 15.31+7 s, b = Mama
  45.67+4 s, c = daughter rap 106.54+4 s; `f0` variants start 40 ms before the first word).
- Gate written and tested: `tools/review/lipsync_gate.py` (envelope lag + viseme scan on bilabials/vowels from timing.json +
  word strip + PASS/FAIL). Batch measure: `tools/review/ls3_measure.py` -> `work/review/lipsync_gate/` (strips, 12-frame
  sheets, `ls3_table.tsv`, `_check.mp4` with the song under the take).

**In progress**: batch 1 on the relay (28 jobs). Pending, spec `media/gen/specs/<tag>.json`, output `media/gen/<tag>_<hex>.mp4`:
ls3_a_kling_1-315c490bfb, ls3_b_sd25pre_1-83fd33272b, ls3_b_sd25f0_1-e043a7e3b7, ls3_c_sd25pre_1-e938b097da,
ls3_c_sd25f0_1-711d3c2ca8, ls3_a_sd25pre_1-c598df150e, ls3_a_sd25f0_1-73d1b9aa2a, ls3_a_sd25short_1-85d76db4c1,
ls3_b_sd20mini_1-a630cff44e, ls3_b_pavD_1-e70102357b, ls3_c_pavD_1-014516cd9a, ls3_b_sd25pre_2-3f436d6db0,
ls3_b_sd25f0_2-30b32880c7, ls3_c_sd25pre_2-4a1a271cb8, ls3_c_sd25f0_2-f3b85acc3a, ls3_a_sd25pre_2-a85a49d7f4,
ls3_a_sd25f0_2-644d638117, ls3_a_sd25short_2-6252b9dcd3 (all prefixed `chaosmonkey/`; collect with `gen.py collect`).

**Bake-off so far** (full numbers: `work/review/lipsync_gate/ls3_table.tsv`)
| take | sync | look | acting |
|---|---|---|---|
| pavN (p-video-avatar, neutral prompt) a/b/c | audio passed through bit-aligned (offset 0.0 ms). Gate: b env -65 ms r 0.66; c r 0.54, bilabials land +-3 f around the true time on the rap; a r 0.36, 2 of 7 bilabials not closed | holds the painting this time (ff 0.99; softer, slightly 3D) | sings like a pop singer to camera: eyes close, head sways 18-32 deg; eyeline to the child is lost |
| pavA (acted prompt) b | r 0.65 | holds | overacts: full-teeth grin, head rolls 40 deg, 7 blinks in 4 s. Reject |
| kling (no audio, acting only) b/c | n/a | best: exact hand | b: good acted beats (head shake, eyes down to the child, brows, smile). c: fist chops, frown, blink. These are the acting reference |
| omni (gemini-omni-1.2-flash image+audio) b | 7003 User Input Error | | |
| fabric b | 2047 Invalid User Credentials (third time across two bake-offs) | | not usable on this relay |

**Decisions so far and why**
- The gate does not trust one number. Envelope lag is only believed with r >= 0.4 and sharp >= 0.35; the viseme scan only with
  >= 3 bilabials and a clear peak. On takes whose audio is known to be aligned the envelope still scatters -65..+18 ms, so
  +-1 frame cannot be certified by the envelope alone: the strip decides.
- p-video-avatar with an acted prompt is out (overacting). Neutral prompt is the sync reference.

**Next**: measure Seedance takes (pre-roll vs frame 0 vs 4 s); two-stage tests (Kling acted take -> Seedance 2.5 with
reference_videos + reference_audios; local LivePortrait lip transfer from the avatar take onto the Kling take); write the recipe.

**Open questions for the lead**: none yet.

## Notes
- Spend tag prefix `ls3_`. Ceiling $120.

## Gate results (appended by `lipsync_gate.py --log`)

| take | t0 | shift f | frame 0 at | env lag ms | r | sharp | viseme shift | closed | open | drift f | verdict | eye / reason | strip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

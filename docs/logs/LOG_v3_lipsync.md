# LOG v3 LIPSYNC

## DONE 19:35
(Resumed after the usage-limit stop; the earlier DONE block is replaced by this one.)

**Final report (also sent to the lead)**
- **Method for all three singer types: act, drive, transfer.** Kling v4 acted take (no audio) + `pruna/p-video-avatar` lip
  driver on a canon frontal frame with the exact stem window (audio passes through at offset 0.0 ms) + local LivePortrait
  lip transfer `tools/sync/lp_lips.py` (opening ratio from the driver, bilabial closures forced from timing.json, mouth at
  rest where the lead is silent) + gate at shift 0. Wrapper `tools/gen/lipsync_take.py act|drive|conform|lips`.
  Recipe, bake-off table, shot table, failure signs: `docs/LIPSYNC_V3.md`.
- **Gate** `tools/review/lipsync_gate.py`: envelope lag, viseme scan, phrase starts, word strip; PASS only with `--eye`.
- **Pass rates**: two-stage 3 of 3 test lines (child 7 s, Mama, rap). Seedance 2.5 + reference audio about 5 of 27 (child
  1/12, Mama 0/6, rap 2/6, Jade 2/3 on numbers only); lag random -493..+673 ms; audio from frame 0 does not help; 4 s
  windows help a little. p-video-avatar as the picture: sync fine, acting wrong (eyes shut, head sway, singer to camera),
  with all three prompts (neutral, acted, default; all measured). Not on the relay: Kling lip-sync, OmniHuman, Hedra,
  sync.so, any v2v lip-sync; fabric 2047; omni rejects audio; Seedance reference video needs a public URL.
- **Shots**: PASS I4 (`I4_take3.mp4`), I3a (`I3a_take2.mp4`), and by ATTIC with this recipe B1c, C3, E1; G5 passes as an
  acted take placed by hand. E3 and G1 are AUTO-PASS awaiting ATTIC's eye verdict. G4 take 1 FAIL (vowels 0.73). B1 in its
  first framing FAIL (face tracking 80 %), replaced by B1c. Unsynced / off-face: F1, I1 (wide, faces 115 / 90 px), K1, K2a,
  and B2, D3, F4a, J4 unless re-framed.
- **BED+CAR hand-off done**: `work/bedcar/picks.json` lips now point at `I3a_take2.mp4` (t0 182.9583) and `I4_take3.mp4`
  (t0 187.600, no +3 f offset any more); `work/bedcar/do.sh I3a 182.95833333333334 184.625` and `do.sh I4` re-run;
  `media/comp/I3a.mp4` re-gated PASS; the previous I4 comp is kept as `media/comp/I4_lips_take1.mp4`. The I4 comp itself
  cannot be gated as a whole (the morph frames at its head are not trackable); the take is gated. Note I4_take3 is baked
  through their EARLIER time map (187.6:0.5 ... 189.4:2.83), not the linear one now in picks.json: if they prefer the
  linear timing, re-run `lipsync_take.py conform` + `lips` with the settings in `I4_take3.txt` (5 minutes).
- **What the transfer does to the acted face**: everything outside the lower face is the acted take, pixel for pixel
  (eyes, brows, blinks, head, hands). Inside the patch: (1) the mouth is the avatar's, so at default strength it opens
  wider and shows more teeth than the sheets and than the acted Kling mouth. BED+CAR's note on I4 was right; the gentle
  setting (`--rgain 0.55 --shape 0.2 --mask mouth --delay 2`) fixes it and still passes (`sheets/I4_take2_vs_3.jpg`).
  (2) the redrawn lips are a little softer than Kling's ink line on big 1080p faces. (3) chin and jaw travel is only what
  the acted take had. (4) the acted take's own smile on a sung word is flattened toward the driver's mouth shape.
- **Spend**: $32.92 of $120 (45 relay jobs about $32.0, start frames $0.90; 4 errored jobs not billed).
- **Caveats**: I judged strips and contact sheets, not moving video: someone should watch the `_check.mp4` files in
  `work/review/lipsync_gate/` once. The envelope number alone cannot certify +-1 frame (its scatter on known-aligned takes
  is +-1.1 f) and lines under 5 words have no trustworthy lag measure: there the strip and the by-construction placement
  carry the verdict. The avatar's mouth leads the sound by about 3 frames, hence `--delay` (default 1, 2 on I4 / I3a).
  timing.json has wrong times on low-confidence words ("I'd" 183.93 is sung from 183.67): the gate skips them.
  LivePortrait runs on CPU here (about 2-4 s per frame).
- No relay jobs of mine are pending. Nothing committed. Caches: `work/lipsync/cache/`; LivePortrait weights
  `~/.cache/liveportrait_onnx` (323 MB); nothing of mine in /tmp.

## Notes
- Spend tag prefix `ls3_`. Ceiling $120.

## Gate results (appended by `lipsync_gate.py --log`)

| take | t0 | shift f | frame 0 at | env lag ms | r | sharp | viseme shift | closed | open | drift f | verdict | eye / reason | strip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| media/gen/v3/lipsync/test/a_lp_3.mp4 | 15.31 | 0 | 15.31 | 7 | 0.37 | 0.35 | 0 | 1.0 | 0.82 | 0.3 | **PASS** | pass: all 7 bilabials shut on the onset (妈 妈 me before sleep| came| be); 妈 tell I how 悟 came open; ee vowels (me, sleep) small as they should be | work/review/lipsync_gate/a_lp_3_strip.jpg |
| media/gen/v3/lipsync/test/c_lp_3.mp4 | 106.54 | 0 | 106.54 | 7 | 0.52 | 0.45 | 1 | 1.0 | 0.95 | 0.7 | **PASS** | pass: 蹦 没 变 shut on the onset frame, every vowel cell open except 童 and 二 (fast, small) | work/review/lipsync_gate/c_lp_3_strip.jpg |
| media/gen/v3/lipsync/test/b_lp_3.mp4 | 45.67 | 0 | 45.67 | -35 | 0.69 | 0.73 | 2 | None | 0.86 | 0.0 | **PASS** | pass: Not/yet/start wide open on the stressed vowels, just/the small; 'that's' nearly shut on the th (weak but not wrong); no bilabials in this line | work/review/lipsync_gate/b_lp_3_strip.jpg |
| media/comp/G5.mp4 | 146.458 | 0 | 146.458 | 48 | 0.27 | 0.25 | 3 | None | 1.0 | 0.0 | **PASS** | pass: one word; mouth shut through Mama's off-camera 'no less', opens on Yes (148.72-148.86 open, closing 149.0), blink after; acted Kling take conformed by hand, no transfer | work/review/lipsync_gate/G5_comp_strip.jpg |
| media/gen/v3/lipsync/I4_take1.mp4 | 187.6 | 0 | 187.6 | -118 | 0.75 | 0.77 | -8 | None | 0.5 | 0.0 | **FAIL** | fail: mouth opens wide for 'able' 5 f before the sound (driver leads); superseded by take2 (driver delayed 2 f) / vowels open on only 50%; by eye: fail: mouth opens wide for 'able' 5 f before the sound (driver leads); superseded by take2 (driver delayed 2 f) | work/review/lipsync_gate/I4_take1_strip.jpg |
| media/gen/v3/lipsync/I4_take2.mp4 | 187.6 | 0 | 187.6 | -35 | 0.8 | 0.87 | -9 | None | 1.0 | 0.0 | **PASS** | pass, borderline: shut and at rest until f23, opens on 'You're' at f24-25 (onset f25.7) but small and already closing by f29; 'able' opens f34 (3 f before the sound) and is wide on the vowel; the b of able falls after the cut | work/review/lipsync_gate/I4_take2_strip.jpg |
| media/gen/v3/lipsync/C3_take1.mp4 | 46.167 | 0 | 46.167 | 48 | 0.47 | 0.51 | 1 | None | 1.0 | 0.0 | **PASS** | pass: no bilabials in the line; mouth open on every vowel (Not/yet/that's/just/the/start), she laughs through it; env lag +48 ms | work/review/lipsync_gate/C3_take1_strip.jpg |
| media/gen/v3/lipsync/E1_take1.mp4 | 85.833 | 0 | 85.833 | 7 | 0.52 | 0.51 | 3 | 1.0 | 0.83 | 0.0 | **PASS** | pass: lips shut before monkey / memory / -memory-, open on had, just, like, you; the held 'you~' closes a little early; env lag +7 ms | work/review/lipsync_gate/E1_take1_strip.jpg |
| media/gen/v3/lipsync/I3a_take1.mp4 | 182.9583 | 0 | 182.958 | -35 | 0.63 | 0.6 | 12 | None | 1.0 | 0.0 | **FAIL** | fail: made before the mask fix; mouth timing judged against a wrong word time (I'd, low confidence in timing.json); superseded by take2 / by eye: fail: made before the mask fix; mouth timing judged against a wrong word time (I'd, low confidence in timing.json); superseded by take2 | work/review/lipsync_gate/I3a_take1_strip.jpg |
| media/gen/v3/lipsync/I3a_take2.mp4 | 182.9583 | 0 | 182.958 | 7 | 0.62 | 0.58 | 12 | None | 1.0 | 0.0 | **PASS** | pass: open on You/think, wide from f15 for I'd (stem energy from f17) through ask, shut by f32 after the k; 'for' at f38 small with the head tipped back (weak); mouth already open on frame 0, 3 f before 'You' sounds | work/review/lipsync_gate/I3a_take2_strip.jpg |
| media/gen/v3/lipsync/B1c_take1.mp4 | 15.5 | 0 | 15.5 | 48 | 0.3 | 0.3 | 1 | 1.0 | 0.88 | 0.6 | **PASS** | pass: lips shut before both 妈, me, before, be; open on will/tell/sleep/how/came; small on 'you' and 'I' | work/review/lipsync_gate/B1c_take1_strip.jpg |
| media/gen/v3/lipsync/I4_take3.mp4 | 187.6 | 0 | 187.6 | -35 | 0.75 | 0.73 | -8 | None | 1.0 | 0.0 | **PASS** | pass: gentler setting (rgain 0.55, shape 0.2, delay 2, mouth mask): at rest until f23, opens small on You're (f25), nearly shut f28-31, opens on able from f34 to a moderate opening with only the upper teeth edge; closer to her sheet than take2 | work/review/lipsync_gate/I4_take3_strip.jpg |
| media/comp/I3a.mp4 | 182.95833 | 0 | 182.958 | 7 | 0.6 | 0.59 | 12 | None | 1.0 | 0.0 | **PASS** | pass: the comp carries I3a_take2 1:1 (same frames as the gated take); numbers unchanged at 960x540 | work/review/lipsync_gate/I3a_comp_strip.jpg |
| media/gen/v3/lipsync/E3_take2.mp4 | 93.0 | 0 | 93.0 | 48 | 0.45 | 0.51 | 0 | 1.0 | 0.83 | 0.0 | **PASS** | pass (measured on the 2x child crop; comp uses E3_take2_full.mp4 = crop pasted back): shut after Names, before but, inside spell/remember; open on Names, faces, I, lose, few, spell, I'd, remember; 'well' is in profile as she turns up to Mama, mouth open. take1 REJECTED: transfer landed on Mama | work/review/lipsync_gate/E3_take2_strip.jpg |
| media/gen/v3/lipsync/G1_take2.mp4 | 121.458 | 0 | 121.458 | -35 | 0.23 | 0.23 | 2 | 1.0 | 1.0 | 0.0 | **PASS** | pass (measured on the 2x child crop; comp uses G1_take2_full.mp4): shut before band, open on wear, band, heavy; 'gold' and 'cold' are sung in profile as she turns up to Mama (open); envelope weak r 0.23. take1 REJECTED: transfer landed on Mama | work/review/lipsync_gate/G1_take2_strip.jpg |
| media/gen/v3/lipsync/I1_take1.mp4 | 177.2083 | 0 | 177.208 | 548 | 0.65 | 0.64 | 1 | 1.0 | 1.0 | 0.0 | **PASS** | pass (BED+CAR, strip only, not watched in motion): shut before baby f2-4, open f7, shut inside ba-by f11, shut before Monkey's f22-24, open f27; twin f46 is the acted squeeze grin with teeth | work/review/lipsync_gate/I1_take1_strip.jpg |
| media/gen/v3/lipsync/F1_take2.mp4 | 107.0417 | 0 | 107.042 | -368 | 0.65 | 0.64 | 10 | 1.0 | 1.0 | 0.0 | **FAIL** | fail: numbers. Strip at shift 0 has both bilabials shut on time and every vowel open, but the envelope puts the take 8.8 f early and the gate also auto-passes +9 f: ambiguous on this periodic rap with 2 bilabials; not shifted, not shipped as the main F1 / envelope lag -8.8 f at this placement; by eye: fail: numbers. Strip at shift 0 has both bilabials shut on time and every vowel open, but the envelope puts the take 8.8 f early and the gate also auto-passes +9 f: ambiguous on this periodic rap with 2 bilabials; not shifted, not shipped as the main F1 | work/review/lipsync_gate/F1_take2_strip.jpg |
| media/gen/v3/lipsync/G4_take3.mp4 | 141.25 | 0 | 141.25 | 7 | 0.4 | 0.38 | 1 | 1.0 | 0.8 | 0.5 | **PASS** | pass, borderline: shut before mama / -mama- / more; open on 听 话 or you'll get wear mama no more; small on the unstressed 'to', 'Do', 'what' (vowels open exactly 0.80). take1/take2 (act2) FAIL at 0.73 | work/review/lipsync_gate/G4_take3_strip.jpg |

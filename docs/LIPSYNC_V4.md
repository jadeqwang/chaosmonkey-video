# Lip-sync v4: one recipe (a video model sings and acts; nothing is pasted)

State: **READY, recipe changed from the provisional one** (see "Change for room teams"). Two-pass passes 8 of 20 takes by eye (adult and child
lines about 1 in 2; fast rap 1 in 5 with the rap prompt) and every test line has a passing take. Log: `docs/logs/LOG_v4_lipsync.md`. Spend $43.78 of $90 (ls4_ tags, list-price estimates, includes a $1.72 probe that probably was not billed).

## Change for room teams (ATTIC, BED+CAR), read first
The provisional READY said "Seedance 2.5 image + reference audio, 6 takes, place by measured lag". The bake-off since shows that
Seedance re-performs the song at its own tempo (skips words, sings into silence, drifts inside a take), so it passes only about
1 take in 6 and its lag cannot be certified by numbers. **Use the two-pass recipe below instead.** Seedance takes you already made
are not wasted: judge them on the face strip; a take that passes the strip may ship.

## 1. The recipe: Kling acts, p-video-animate sings (both video models; whole face re-rendered from the audio)
1. **ACT** (pass 1): Kling v4 from the shot's keyframe, the full acting prompt, a CALM clause (no jumps, no bounces, no fast head
   turns, face visible), no audio. 2 takes; pick the acting on the sheet. Its frame 0 = song time t0 (0.5 s before the first sung
   word, or the shot's in).
2. **SING** (pass 2): `pruna/p-video-animate` with `video` = the acted take with the vocal stem window muxed in (from t0), `image` =
   the keyframe. It re-renders the whole character (face, jaw, cheeks, head, body) from the keyframe, following the acted take's motion,
   and drives the lips from the audio. The audio comes back bit-identical, so **clip frame 0 = song t0, shift 0, speed 1**. 2 seeds.
3. **JUDGE** on the 2x face strip (`work/review/lipsync_v4/<take>_face.jpg`) and the sheet; record with `eye`.

```
PY=/home/jade/Documents/halys-video/.venv/bin/python; export TMPDIR=$PWD/work/tmp
$PY tools/gen/lipsync_v4.py act  C3 media/kf/v4/C3.jpg --who "the woman with glasses" --partner "the little girl in her lap" \
    --act "0-0.5 s: she breathes in, smiling, looking down at the girl's raised hands. 0.5-1.4 s: she sings 'not yet', shaking her head once ..." --takes 2
$PY tools/gen/lipsync_v4.py wait C3            # then look at work/review/lipsync_v4/sheets/ (or make one) and choose acted take K
$PY tools/gen/lipsync_v4.py anim C3 K --seeds 2
$PY tools/gen/lipsync_v4.py wait C3
$PY tools/gen/lipsync_v4.py measure C3 [--pick x,y]       # gate at shift 0 + face strip + sheet per take; table <SHOT>_takes.tsv
$PY tools/gen/lipsync_v4.py eye C3 ls4w_C3_a1s2 "pass: opens on Not f2, narrows on that's, chin drops on start, eyes on the child"
```
Cost per line (4 s): Kling 720p 2 x $0.63 + animate 2 x $0.12 = **about $1.50**; 7 s: about $2.60.

## 2. Conditions
- Face at least about 240 px high in the 960x540 cut (tested 240-400 px). Front to three-quarter. Two faces: `--pick x,y`.
- The keyframe: the singer's mouth relaxed, lips together or just parted, no teeth; nothing in front of mouth or chin.
- Acting prompt: timed beats, eyes on the partner, "sings softly"; never describe mouth shapes; add no bounce / jump / fast turn
  (the CALM clause is in the wrapper): **animate smears the face on fast body moves** (B1 v3 take, frames 92-112, a double bounce).
- Length: tested 4 s and 7 s (B1). Animate input must stay under the request limit: the wrapper sends the acted take at 480p crf 30.
- Fast Mandarin rap: give concrete rap body language (two-finger count chopping on stressed syllables, nod on the downbeat, point at
  the listener on line ends); name the language in the acting text. Result: section 4.

## 3. Measuring tools (new)
- `tools/review/lipsync_v4.py strip TAKE --t0 T [--shift N] [--pick x,y]`: lower face every 2nd frame through the sung words, at
  least 2x the cut's pixels, labelled with the word sounding; red = bilabial, green = vowel; cell 0 = frame 0 (on-model reference);
  jaw_r = how much the chin moves with the mouth. What to judge: mouth inside the face, jaw drops on open vowels, teeth stable, no
  soft patch, same face as cell 0. Calibration: the v3 transfer that Jade rejected, `work/review/lipsync_v4/v3_C3_take1_face.jpg`.
- `tools/review/lipsync_v4.py audiolag`: where a take's soundtrack sits in the song (Seedance: always offset 0, says nothing about
  its mouth; animate/avatar: offset 0, bit-aligned).
- `tools/review/ls4_lag.py`: lag from the face (phrase structure + visemes). Works on avatar/animate takes; NOT reliable on Seedance.
- `tools/review/lipsync_gate.py` gains `--scan N`. `tools/review/ls4_eval.py`: batch runner.

## 4. Bake-off table (pass = fresh-eye strip verdict PASS; numbers in `work/review/lipsync_v4/ls4_table.tsv`)
Lines: B1 little Jade (en + 妈妈), C3 Mama (en), F1 daughter Mandarin rap, I4 adult Jade (en). Judgements:
`work/review/lipsync_v4/judge_batch1.md`, `judge_batch2.md`, `judge_anim.md`.

| Method | B1 child | C3 Mama | F1 rap | I4 Jade | All | $ / take | Notes |
|---|---|---|---|---|---|---|---|
| **Kling act (calm) + p-video-animate (two-pass)** | **2/3** (+1 borderline) | **3/4** (+1 borderline) | 0/4 (3 borderline, 1 fail) | **2/4** (+2 borderline) | **7/15** (47 %), 1 fail | 0.75 (4 s) | timing locked at shift 0 (bit-aligned audio); every non-rap line got a PASS from 2 acted takes x 2 seeds |
| same + rap instruction prompt (`--rap 1`), F1 only | | | **1/5** soft PASS (+2 borderline, 2 fail) | | | 0.12 per seed | distinct shapes on the first phrase; all seeds smear at f81 (after the shot) |
| same, on v3 acted takes (not calm) | 0/1 (face smears in the bounce) | 1/1 eye + 3 of 4 more seeds pass the numbers | | | | 0.12-0.2 per seed | C3 seeds: env lag +7..+48 ms, r 0.59-0.64 |
| Seedance 2.5 image + audio, 4 s, 0.5 s pre-roll | 1/3 (borderline) | 1/3 (+1 borderline) | 0/3 | 1/3 | 3/12 | 0.92 | random lag -0.7..+1.1 s, placed by eye |
| Seedance 2.5, shot window + 1 s silence pads | 0/2 | 0/2 | 1/3 (marginal) | 0/3 | 1/10 | 1.2-1.6 | sings into the silence, skips words, drifts |
| same, full mix instead of vocal stem | 0/1 | 0/1 | | | 0/2 | 1.4-1.6 | not better |
| same, 7 s line | 0/1 | | | | 0/1 | 2.3 | breaks after "sleep" |
| p-video-avatar as picture, holding prompt, shot keyframe / tight crop | 0/2 | 0/2 | 0/1 | 0/1 | 0/6 | 0.10 | sync by construction; reframes, off-model, eyes shut, sways |
| Seedance reference_videos (Kling URL or ByteDance URL) + audio | 7003 | 7003 x2 | | | n/a | | provider refuses video+audio edit (URL is not the cause) |
| gemini-omni-1.2-flash image + audio | | 7003 | | | n/a | | audio input still not enabled |
| v3 transfer (act + driver + lp_lips) | retired | | | | | | rejected by Jade; strip shows why |

Not tested: Kling motion-control (needs a public image URL; a URL route exists via provider output URLs, not needed now);
veed/fabric (v3: 2047 credentials). Catalog refresh 18 Nov: no other model takes audio with a first frame.

## 5. Best take per test line (place clip frame 0 at the song time given, speed 1)
| Line | Best take | frame 0 at | Verdict | Strip |
|---|---|---|---|---|
| B1 little Jade | `media/gen/ls4_B1_animK1_1_2b2c45f02e.mp4` (7 s) | 15.31 | PASS (fresh judge): in time, shut on me/before, round on 孙悟空, rests between phrases; small vowels | work/review/lipsync_v4/ls4_B1_animK1_1_face.jpg |
| C3 Mama | `media/gen/ls4_C3_animK1_1_5a6818dee4.mp4` | 45.67 | PASS (judge); also `ls4_C3_anim_C3_1` (my eye) at 46.167 | work/review/lipsync_v4/ls4_C3_animK1_1_face.jpg |
| F1 rap | `media/gen/ls4_F1_animR2_3_91f78fe1e7.mp4` (use frames 12-55 = the shot) | 106.54 | soft PASS (judge and my eye): O / open / shut-for-蹦 shapes through 石头里蹦出来, 没 closed then open, 童 round, 年 open; smear at f81 is after the shot | work/review/lipsync_v4/ls4_F1_animR2_3_face.jpg |
| I4 Jade | `media/gen/ls4_I4_animK2_2_cff52ed492.mp4` | 186.49 | PASS (judge): clearest shapes, teeth stable, rests in silences; she looks near the lens more than down | work/review/lipsync_v4/ls4_I4_animK2_2_face.jpg |
Per-take verdicts: `work/review/lipsync_v4/judge_anim.md` (animate), `judge_batch1.md`, `judge_batch2.md` (Seedance, avatar).

## 6. Per line type: what to do
| Line type | Recipe | Expected | If it fails |
|---|---|---|---|
| Adult, English, face >= 240 px (Mama, Jade) | two-pass | about 1 PASS per 2 acted takes x 2 seeds ($1.50 per 4 s) | 2 more seeds ($0.25), then a new acted take |
| Child, English/Chinese, calm acting (B1, I3a, G5) | two-pass with the CALM clause | same; 7 s lines work | bounces, jumps, fast turns smear the face: keep big moves out of sung words |
| Fast Mandarin rap (F1) | two-pass from a TIGHT framing (face ~350 px), rap body language in the acting prompt, `anim --rap 1`, **5+ seeds** per acted take | about 1 soft PASS in 5 seeds ($0.12 each); without --rap 0/4 | articulation is the weak point; if no seed passes, the lead re-stages the fastest phrase off-face |
| Face under ~200 px, profile, mouth covered | no recipe | | play the line off-face (listener, hands, book) |
| Seedance single pass | fallback only: 6 takes, judge on raw strips | about 1 in 6 | |

## 7. "Is it technically difficult to act and sing at the same time?"
Yes, with the models we can reach, and we measured why. The only model that takes a first frame and the song together and also acts
(Seedance 2.5) treats the audio as something to re-perform: it sings at its own tempo, skips words, starts during silence, so most
takes are out of sync somewhere (about 1 in 6 passes). The models that are locked to the audio (p-video-avatar) cannot act: they
sing to camera, sway, close their eyes, and redraw the painting. The v3 answer (paste a mouth onto the acted take) looked wrong because
the jaw and cheeks did not move with it. The v4 answer splits the work between two video models instead of between a model and us:
Kling performs the scene; p-video-animate redraws the whole character, face, jaw and all, from the keyframe, following Kling's motion
and singing to the audio, which it keeps bit-exact. Acting and singing end up in one rendered face.

## 8. What failed and why (short)
- v3 mouth transfer: retired (pasted mouth, jaw does not move): calibration strip `work/review/lipsync_v4/v3_C3_take1_face.jpg`.
- Seedance + reference audio: random lag AND drift inside a take; its output soundtrack is our audio at offset 0, so it cannot be used to
  place the picture; 1 s silence pads made it worse (it sings into them); full mix no better; 7 s lines break.
- Lag from numbers: on these short sung lines the envelope and viseme scans are flat and multimodal (an avatar take with true lag 0
  scores best at -11 f); only locked-audio methods can be placed without an eye check.
- p-video-avatar as the picture: 0/6 even from the shot keyframe with a holding prompt.
- Seedance video+audio edit (two-pass): provider refuses (7003) with a Kling URL and with a ByteDance URL alike. URLs: relay results
  carry the provider's public output URL (about 30 days), so a reference-video URL never needs a bucket.
- gemini-omni image+audio: 7003, audio not enabled. Not tested: Kling motion-control, fabric.
- p-video-animate fails only on fast body motion (face smears) and occasionally under-articulates.

## 9. What was verified, and how
- Every verdict above comes from the 2x face strip (every 2nd frame) and a 12-18-frame sheet, judged by fresh Sonnet agents
  (`judge_batch1.md`, `judge_batch2.md`, `judge_anim.md`, `judge_rap.md`, notes beside them). I re-checked these by eye: B1_sd_2,
  C3_sd_3, C3_anim_C3_1, B1_anim_B1_1 (smear found), F1_animK2_2 (downgraded to BORDERLINE), F1_animR2_3, plus the acted-take sheets.
- Nobody has watched a take in motion with sound. Strips sample every 2nd frame, so one-frame pops can be missed. Before shipping,
  watch the `_check.mp4` (gate `--check`) of each pick once.
- `lipsync_v4.py act` is dry-run tested; `anim` / `measure` / `eye` mirror the bake-off code (ls4_bake.py / ls4_eval.py) but have
  not yet run end-to-end on an `ls4w_` take. The first room team to use them should report any error to LIPSYNC.
- Animate output is 1408x768 (scale to 960x540); its colour is close to the acted take's but compare at the cut.

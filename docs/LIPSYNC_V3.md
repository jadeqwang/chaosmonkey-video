# Lip-sync v3: recipe and gate

Final (19:45). The two-stage method passed the gate, numbers and eye, on all three test lines (3 of 3; Seedance 2.5: about 5 of 27).

**Rule (REVISION_V3 §2.6):** a singing face ships only if `tools/review/lipsync_gate.py` says PASS: lag within ±1 frame,
bilabials (m/b/p, 妈 没 蹦 变 百…) shut, stressed vowels open on the word strip, looked at by a person/agent and recorded.

## The method: act, drive, transfer (all singer types)

The performance and the mouth are made separately, then joined locally.

1. **ACT** — Kling v4 from your room keyframe, with your full acting prompt (timed beats, eyes, body action, blink,
   breath). No audio goes to it. This take IS the performance: head, eyes, brows, hands, the painting.
2. **DRIVE** — `pruna/p-video-avatar` on a canon frontal singing frame of the same character, fed the exact vocal-stem
   window. It returns the audio untouched (offset 0.0 ms measured), so its mouth is in time by construction. Only its lip
   movement is used; its picture is thrown away.
3. **TRANSFER** — `tools/sync/lp_lips.py` (LivePortrait, local, free, about 2 s per frame on CPU): sets the acted take's
   lip opening to the driver's frame for frame (whatever its own mouth was doing), adds the driver's lip shape, forces a
   full closure before every bilabial onset in `analysis/timing.json`, puts the mouth at rest wherever the lead is not
   singing (the driver also mouths backing echoes), redraws only the lower face and feathers it back. Eyes, glasses, hair, hands, background and
   every pixel outside the lower face stay the acted take's.
4. **GATE** at shift 0.

```
PY=/home/jade/Documents/halys-video/.venv/bin/python; export TMPDIR=$PWD/work/tmp
# T = song time of the take's frame 0 (the shot's start in the cut), D = whole seconds 3..8, WHO = lj | mama | dau | jade
$PY tools/gen/lipsync_take.py act   B1 media/kf/v3/B1_pick.jpg "At the start she looks up to the right at her mother ... (timed beats)" --t0 15.31 --dur 4 --takes 2
$PY tools/gen/lipsync_take.py drive B1 lj --t0 15.31 --dur 4
$PY tools/gen/gen.py wait <job ids printed above> --timeout=3000
$PY tools/gen/lipsync_take.py lips  B1 1 --t0 15.31 [--act 2] [--pick x,y]      # -> media/gen/v3/lipsync/B1_take1.mp4 + gate
#   look at work/review/lipsync_gate/B1_take1_strip.jpg and watch B1_take1_check.mp4 (take + song), then record:
$PY tools/gen/lipsync_take.py lips  B1 1 --t0 15.31 --eye "pass: 妈 shut f10/f18, vowels open"   # re-renders; or call the gate directly:
$PY tools/review/lipsync_gate.py media/gen/v3/lipsync/B1_take1.mp4 --t0 15.31 --shift 0 --name B1_take1 --eye "pass: ..." --log
```
In the comp place clip frame 0 at song time T (shift 0), speed 1. No retime, no lag picking.

`lips` options: `--delay N` (default 1) plays the driver's mouth N frames later: the avatar opens about 3 frames before the
sound, 1-2 is natural. If a blue phrase-start cell shows the mouth already wide open at -3, re-run with `--delay 2`
(I4 and I3a needed 2). `--mask mouth` redraws a smaller patch: use it on big faces at 1080p, where the redrawn lower face
is visibly softer than Kling's line. `--rgain 1.3` opens wider, `--pick x,y` chooses the singer in a two-shot.

**You already have an acted Kling take, or you retime it with a time map?** The lips must go on AFTER the retime. Bake the
map, then transfer onto the baked clip and use the result 1:1:
```
$PY tools/gen/lipsync_take.py conform I4 media/gen/v3bc_I4_t2_xxxx.mp4 "187.6:0.5,188.2:1.5,188.67:2.1,189.4:2.83"   # song:src pairs
$PY tools/gen/lipsync_take.py drive   I4 jade --t0 186.6 --dur 4            # driver may start earlier (1 s pre-roll is good)
$PY tools/gen/lipsync_take.py lips    I4 1 --t0 187.6 --clip media/gen/ls_I4_act1_conf.mp4
```

Cost per 4 s take: Kling 720p $0.63 + driver $0.10. Choose the acted take first (contact sheet, as for any acted shot),
then transfer onto the one you like; a second driver is not needed.

### Conditions (what the keyframe and the acted take must give)
- The singer's face at least about 150 px high at 720p (a fifth of the frame height), front to three-quarter (within
  about 35° of frontal). **Profile, a face seen from above/behind, or a face under 120 px cannot be transferred or
  measured: play those lines off the listener, the book or the hands.**
- Mouth and chin never covered (hand, hair, book edge, the other person's head) during sung words.
- Two faces in frame: pass `--pick x,y` = the singer's nose position in frame 0 (720p pixels). The other face is untouched.
- In the acting prompt write "sings softly"; do not describe mouth shapes. Do not ask for laughing or a wide grin on a sung
  word (the transfer keeps the jaw the acted take has).
- Start frame mouth: relaxed, lips just parted or closed, no teeth.
- One singer per take ("both" lines: not tested; shoot them as two singles or play one singer off-face).
- Lines whose words have `confidence: low` in timing.json (e.g. "I'd" in I3a) are not judged by the gate and not muted by
  the transfer; say so in `--eye`.
- Short takes are fine (I3a 40 frames, I4 43 frames passed); the transfer has no length limit, the test maximum was 7 s.

### What it does to acting
Nothing is lost: the acted take is the picture. Measured on the tests the Kling takes carry the beats asked for (head
shake, eyeline to the child, brows, blink, fist chops) and the transfer changes the lower face only. What it cannot add
is jaw/chin travel that the acted take did not have, so on big held vowels the mouth opens but the chin moves little.

## Which listed shots pass (REVISION_V3 §6), state 19:45
| Shot | State |
|---|---|
| I4 Jade "You're able" | **PASS** `media/gen/v3/lipsync/I4_take3.mp4` (1080p, 43 f, frame 0 = 187.600, 1:1; in `work/bedcar/picks.json`, comp re-rendered). Gentle setting, see below. take1 / take2 are rejects |
| I3a daughter "You think I'd ask" | **PASS** `I3a_take2.mp4` (40 f, frame 0 = 182.9583, 1:1; in picks.json, comp re-rendered and re-gated). "for" is weak (head tipped back) |
| B1 little Jade (ATTIC, closer frame `B1c`) | **PASS** `B1c_take1.mp4`. The first framing `B1_take1` FAILED: face tracked on 80 % of frames |
| C3 Mama, E1 Mama | **PASS** (`C3_take1.mp4`, `E1_take1.mp4`, ATTIC) |
| G5 little Jade "Yes" | **PASS** without transfer: the acted Kling take placed by hand (`media/comp/G5.mp4`) |
| E3, G1 | numbers AUTO-PASS, eye verdict still to be recorded by ATTIC |
| G4 Mama | take 1 **FAIL** (vowels open 0.73): ATTIC to re-run (`--rgain 1.3`) or play off-face |
| F1 (face 115 px), I1 (90 px) | **ship unsynced / off-face**: wides whose acted mouths move but are not synced and cannot be measured. Keep the cut on hands, body and the listener; if the mouth reads, tighten or cut away |
| K1 (mouth hidden in the curls), K2a (page) | no singing mouth on screen |
| B2 first half, D3, F4a, J4 | not requested; under the 150 px limit as framed in the last cut: treat as unsynced wides unless re-framed |

**Teeth and wide mouths (I4).** At default strength the transfer follows the avatar driver, which sings with a big open
mouth and shows both rows of teeth; on Jade's close-up this was off-model against her sheet and against the acted take
(`media/comp/I4_acted.mp4`). `--rgain 0.55 --shape 0.2 --mask mouth --delay 2` (I4_take3) gives a moderate opening with only
the edge of the upper teeth and still passes the gate. Comparison: `work/review/lipsync_gate/sheets/I4_take2_vs_3.jpg`
(top = default, bottom = gentle). **Use the gentle setting on adult close-ups; default on children and on fast rap**, where a
small mouth stops reading.

## Alternative: Seedance 2.5 with reference audio (single pass)
Use only if the transfer conditions fail but the face is still readable, or as a second opinion on a hero close-up.
`$PY tools/gen/ls3_bake.py` shows the exact spec (`image` + `reference_audios` [window starting 0.5 s before the first
word] + `generate_audio:false`, 720p, **4 s windows only**). Lag is random per take (measured -482 to +643 ms; starting
the audio at frame 0 does not help; a 7 s line never passed; one take came back portrait). Make 3 takes, gate each without
`--shift`, keep a take only if the gate finds the lag itself and the strip agrees, place frame 0 at `place_frame0_at`.
Measured pass rate: about 1 take in 5 (table below), so budget 5 takes per line: roughly $4.60 per passing 4 s.

## The gate
```
$PY tools/review/lipsync_gate.py TAKE.mp4 --t0 T [--shift N] [--pick x,y] --name SHOT_takeN --check [--eye "pass|fail: ..."] [--log]
```
- Outputs in `work/review/lipsync_gate/`: `<name>_strip.jpg`, `<name>_gate.json`, `<name>_check.mp4`.
- It measures (1) envelope lag: FaceMesh lip gap against the 1-3 kHz vocal envelope (trusted only at r ≥ 0.4, sharp ≥ 0.35);
  (2) viseme lag: lips shut before each bilabial onset and open on each vowel, scanned over ±12 frames (trusted only with
  ≥ 3 bilabials and a clear peak); (3) at the placement used: share of bilabials shut, share of vowels open, drift.
- **Strip:** red cells = a bilabial, three frames ending on the onset frame: the lips must be shut in one of the first two.
  Grey cells = the vowel frame of each word (`word~` = middle of a held note): the mouth must be open. The bar under each
  cell is the measured lip gap. Judge it yourself; the numbers only pre-sort.
- PASS = face tracked ≥ 90 %, articulation ≥ 0.04, residual lag ≤ 1 frame (viseme) / 1.5 frames (envelope, whose own
  scatter on known-aligned takes is ±1.1 f), shut ≥ 0.75, open ≥ 0.8, drift ≤ 1.5 f, AND `--eye pass`.
  AUTO-PASS = numbers fine, nobody has looked yet. AMBIGUOUS = no trustworthy lag: reject or prove it on the strip.
- `--log` appends the row to `docs/logs/LOG_v3_lipsync.md`.

## Failure signs
- Strip: a red cell with an open mouth in all three frames (closure missing or late); grey cells shut on long vowels.
- `drift_f` > 1.5 or bilabial errors of mixed sign: the take re-sang the line at its own tempo; no shift fixes it.
- Gate picks a shift beyond ±6 frames with a weak envelope: a chance match, reject.
- Transfer: a soft or swimming patch around the mouth (face too small or too turned), teeth flicker, a mouth that stays ajar
  on m/b/p (the acted take's jaw was wide open: re-shoot the acted take with a calmer mouth), a visible seam under the nose
  when the head turns fast.
- Avatar driver used as picture: closed eyes, swaying head, singer-to-camera. Never ship the driver itself.
- Seedance: output not 1280x720; first frame regraded (ff about 0.88: grade-match at the cut).

## Bake-off table
Lines: a = little Jade "妈妈, will you tell me before I sleep / how 孙悟空 came to be?" (15.31+7 s; 7 bilabials), b = Mama "Not
yet, that's just the start" (45.67+4 s; none), c = daughter rap "石头里蹦出来 没有童年 …" (106.54+4 s; 3). lag = picture late
(ms, bias-corrected); gate = numbers only unless "eye" is noted. All numbers: `work/review/lipsync_gate/ls3_table.tsv`,
strips and 12-frame sheets beside it, takes `media/gen/ls3_*.mp4` and `media/gen/v3/lipsync/test/`.

| Method | Line | $ | lag ms | r | bilabials shut / vowels open | Look (first-frame corr) | Acting | Gate |
|---|---|---|---|---|---|---|---|---|
| **Two-stage: Kling act + avatar driver + `lp_lips`** | a | 1.28 | +7 (shift 0) | 0.37 | 1.0 / 0.82, errors 0 -1 0 0 0 +1 0 | Kling's picture (0.99), lower face redrawn | all of the Kling take: look up, blink, lean, breath | **PASS** (eye) |
| same | b | 0.73 | -35 (shift 0) | 0.69 | no bilabials / 0.86 | same | head shake, eyes to the child, brows, smile | **PASS** (eye) |
| same | c | 0.73 | +7 (shift 0) | 0.52 | 1.0 / 0.95 | same | fist chops, frown, blink | **PASS** (eye) |
| Seedance 2.5 + reference_audios, 0.5 s pre-roll | a (7 s) | 1.62 | +340, +590 | 0.35, 0.36 | no single shift fits | regraded (0.90) | fair | 0 of 2 |
| same, audio from frame 0 | a (6 s) | 1.39 | +590, +257 | 0.25, 0.25 | | 0.90 | fair | 0 of 2 |
| same, 4 s window, first half | a | 0.92 | +132 to +673 | 0.19-0.41 | one take 1.0 / 0.91 at +1 f; others open 0.64 or drift | one take came back 834x1112 portrait | fair | 1 of 5 |
| same, 4 s window, second half | a | 0.92 | -243 to +90 | 0.21-0.41 | open 0.57-0.71, drift 2-2.5 f | one regraded hard (0.66) | fair | 0 of 3 |
| same, pre-roll | Jade "Wouldn't you? You're able." | 0.92 | +340, -77, +340 | 0.36, 0.51, 0.33 | 2 takes 1.0 / 0.8 at -4 f and +2 f | 0.85 | mouth small (articulation 0.08-0.10) | 2 of 3 on numbers, not eye-checked |
| same, pre-roll | b | 0.92 | -398, +143, -410, -493 | 0.44, 0.42, 0.60, 0.44 | open 0.50, 0.83, 0.56, 0.44; held "start" shut | 0.88 (one 0.65) | fair, one blink | 0 of 4 by eye |
| same, frame 0 | b | 0.92 | +102, +102 | 0.38, 0.52 | open 0.75, 0.62 | 0.88 | | 0 of 2 |
| same, pre-roll | c | 0.92 | -482, -23, +507, +673 | 0.27, 0.56, 0.34, 0.40 | take 2: 1.0 / 1.0 at +2 f; takes 3, 4 shut 0.33, 0.0 | 0.66-0.85 | good: chops, frown | 1 of 4 (eye) |
| same, frame 0 | c | 0.92 | +18, +643 | 0.53, 0.28 | 0.75 / 0.90; 0.67 / 0.85 | 0.85, 0.78 | | 1 of 2 |
| Seedance 2.0-mini + reference_audio | b | 0.36 | -107 | 0.44 | open 0.86 | 0.96 | mouth too wide, re-sung | not judged further |
| p-video-avatar, neutral prompt (shipped as picture) | a / b / c | 0.18 / 0.10 / 0.10 | audio bit-aligned | 0.36 / 0.66 / 0.54 | a 0.62 shut; c closures +-3 f | holds the painting (0.99) | singer-to-camera: eyes shut, head sways 18-32 deg | a FAIL, b ok, c drift: driver only |
| p-video-avatar, acted prompt | a / b / c | same | aligned | 0.43 / 0.65 / 0.63 | a 0.62 shut | 0.99 | overacts: teeth grin, 40 deg rolls | reject |
| p-video-avatar, default prompt | b / c | 0.10 | aligned | 0.68 / 0.44 | c 0.67 shut | 0.99 | as neutral, 35 deg rolls | reject |
| Kling v4 alone (no audio) | a / b / c | 1.10 / 0.63 / 0.63 | n/a | | | 0.99 | the best acting of all | stage 1 only |
| Seedance 2.5 reference_videos (Kling take) + audio | b, c | | | | | | | 7003: reference video must be a public URL |
| gemini-omni-1.2-flash image + audio | b | | | | | | | 7003: audio input not enabled |
| veed/fabric-1.0 | b | | | | | | | 2047 Invalid User Credentials |

Not in the catalog (probed by name, all "model not found"): Kling lip-sync / avatar, OmniHuman, Hedra, sync.so, Wan-S2V,
HappyHorse S2V, PixVerse lipsync, LatentSync, HeyGen, Tavus, Creatify.

Seedance 2.5 lag is random per take (-493 to +673 ms in 27 takes); "audio starts at frame 0" does not reduce it and
shorter windows only help a little. **Seedance pass rate: about 5 of 27 (child 1 of 12, Mama 0 of 6, rap 2 of 6, Jade 2 of 3
unverified). Two-stage: 3 of 3.**

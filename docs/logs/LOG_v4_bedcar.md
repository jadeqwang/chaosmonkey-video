# LOG v4 BED+CAR (2026 bedroom and car), preview_v4

Team lead: Claude (Opus 5.5). Brief: REVISION_V4 §1, §5 F/I/J/K/L, §8, §12; TEAMS_V4 (ceiling $140). Scratch `work/bedcar4/`.
Keyframes `media/kf/v4/bedcar/<KEY>_t<k>.jpg` (+ .txt prompt/refs; generator `work/bedcar4/kfgen4.py`, jobs `kfjobs4.py`).
Tighter cameras = same SETS camera with a longer lens (a crop of the renders + transformed sidecar): `work/bedcar4/crop_guide.py`
-> `media/layout/<set>/bc/v4bc_<ID>*` (use `set_check.py --sidecar` on them). Spend tags: `v4bc_*`, singing takes `ls4w_<SHOT>_<k>`.
v3 backups: `media/comp/_v3/<ID>.mp4`, `shots/_v3/<ID>.py` (+ `_bedcar3.py`, `_j1v3.py`, `F1_body.mp4`).

<!--CKPT-->
## CHECKPOINT 6 — NEW ASSIGNMENT: F1 re-make (director watched F1 with sound, 2026-11-18 late)
Her words on media/comp/F1.mp4 (ls4w_F1_ar9): "has reasonable acting though the lip sync timing is off (but hard to tell b/c I'm
opening it in the default video player). the gesture is fine, but the hands came out incoherent (the position of her fingers from
frame to frame is either 2 fingers out, or 1 finger out, or closed fist, in a confused AI glitch kind of way)".
Keep: acting + gesture pattern (points at herself / chest, shoulders, grin, wide on 童年). Fix: (1) hands hold ONE stable shape per
hand all shot (find which pass changes the fingers: Kling act or animate); (2) lip timing verified (placement arithmetic of the comp,
stem window = acted clip window), retake with 5+ rap-prompt animate seeds on the best new acted take, pick on EVERY-FRAME 2x face
strip vs syllable onsets (closed into 蹦 没, open on 来 年), every-frame hand strip (any finger-count change = reject).
Deliver: new media/comp/F1.mp4 (keep media/comp/F1_ar9.mp4, F1_alt.mp4), strips in work/review/comp_v4/, review/f1_ab/F1_new_sound.mp4,
F1_new_sound_x4.mp4 (muxed like the existing files there), F1_new_sound_half.mp4 (half speed, pitch-preserved audio); F1_new_a/_b
if two are close. Images via Codex first. If the permission check refuses a subagent's submission: do NOT resubmit myself; stop and
tell the lead.
ADDITION (coordinator, director on the offset page): "the mouth is still for a long time before the audio starts (true for both and
all the options given)". The rap starts ON frame 0 (石 107.04 ... 年 108.34-108.645) but the mouth is a closed smile for ~20 frames.
The "soft PASS" strip verdicts on F1 were a FAILED judgement. NEW ACCEPTANCE TEST: on an every-frame face strip the mouth must
visibly open and close for each of the ten syllables, starting within 2 frames of 107.04. Causes to test: (a) placement (done: correct,
see below); (b) cold start -> give the animate model a 1.5-2 s sung run-up (pre-roll audio = 一声耳语 学会七十二变 from the stem spliced
in front of the real line; acted Kling clip with the same run-up, already performing); use only frames from 107.0417; (c) tighter face;
(d) Seedance only if it articulates from the first syllable. Keep one hand shape per hand.
Findings so far:
- TIMING ARITHMETIC (checked, correct): ar9's own audio cross-correlates with vocals_v4.wav at song 106.800 (= its spec t0 = the
  pick's map); the animate source (acted take + stem) also starts at 106.800; comp frames 0/10/20/42 match take frames 6/16/26/48
  exactly (expected round(f + 5.8)); review/f1_ab/F1_sound.mp4 audio starts at song 107.0416 (mix_v3), 1.791 s. So no window error:
  the "timing off" is the take's articulation (animate under-articulates the middle of the line: closed smile through 头里蹦出来).
- FINGER CHANGES: every-frame strips work/review/comp_v4/F1_act_t2_hands_every.jpg and F1_ar9_hands_every.jpg (comp frames 0-42).
  The Kling ACT pass already changes the hand shape frame to frame (flat hand -> V -> two fingers up -> point -> flat), because my
  act prompt asked for chops + points + a raised hand; the ANIMATE pass then re-draws the hand differently again (fist vs one finger vs
  two fingers in consecutive frames). Both passes contribute; the act pass sets the shape changes, animate adds flicker.
- Fix plan: new keyframe with ONE held shape (variant A: loose fist, index finger out, pointing at her chest; variant B: flat blade),
  left hand holding the harness strap the whole shot; act prompt with only forearm/shoulder moves, shape stated as unchanging;
  2 acted takes per variant; 5+ rap-prompt animate seeds on the best; every-frame face + hand strips.
- Review page (coordinator): review/f1_ab/index.html; add new takes FIRST in its TAKES array with an honest note; mux like F1_sound.mp4; x4/half files no longer needed.
- Codex route WORKS with reference images (prompt must come before the -i list: `codex exec ... "PROMPT" -i a -i b`, else -i eats
  it). F1p_point_codex.png (Codex, 1672x940: index finger out pointing at her chest, left hand on the strap; face held) PICKED;
  F1p_blade_codex.png (Codex) read as a flat hand on the chest, not a chop: dropped. Background identical to F1c_t4 (set check PASS, hands/face clean: work/bedcar4/notes/F1CHK.md).
- Submitted acted takes F1hold t1 t2 t3 (vspecs4.py S['F1hold'], vt0 106.8, HOLD clause: one shape per hand) — jobs.tsv.
- RUN-UP: audio media/gen/v4/lipsync/_audio/F1_runup_105.13.wav = stem 108.80-110.62 (一声耳语 学会七十二变) + stem 106.95-110.13;
  clip t >= 1.82 <-> song 106.95 + (t - 1.82); virtual frame0 = 105.13 (picks map [[105.13,0],[135.13,30]]; only frames >= 107.0417
  used = clip >= 1.9117 s = frame 45.9). anim4.py got `--audio WAV`. Acted takes F1run t1 t2 t3 submitted (vspecs4 S['F1run'], rapping
  from frame 0, point on 年 at clip 3.15-3.55). Plan: 6+ rap-prompt animate seeds with --audio on the best F1run take (+ a few on F1hold
  with the same run-up audio as a cheap extra), every-frame strips 107.0417-108.833, acceptance = all 10 syllables open/close from <=2 f
  after 107.04, one hand shape throughout.
- F1hold t1-3 collected (hands mostly hold the index point; t1 every-2nd-frame strip work/review/comp_v4/F1hold_t1_hands.jpg).
- F1run t2 t3 collected (t1 still rendering). Animate with run-up submitted by me: work/bedcar4/anim_batch7.sh/.log (arun2s1-3,
  arun3s1-3, ahold1s1-2; rap prompt; --audio run-up).
- Subagent F1FIX (Sonnet, running): collect, mapping check, every-frame face + hand strips, strict acceptance, pick, comp, review
  mux + TAKES line -> work/bedcar4/notes/F1FIX.md. It must not submit jobs (writes WANT lines instead).
- F1FIX DONE (work/bedcar4/notes/F1FIX.md): mapping verified (all 11 takes' audio at song 106.950 from clip 1.82 s). The run-up
  WORKS: the mouth now articulates from comp frame 0 (石 open f0) in every take. No take passes BOTH strict tests. Current media/comp/F1.mp4
  = ls4w_F1_ahold1s1 (hands: index point held in every readable frame, left on the strap; face: syllables move from f0, closed into 蹦,
  open on 出/来/童/年; FAILS: 没 is a round o with no closure, closed-smile frames on 头/出, mild ghosting f26-27, hand hidden by hair
  f10-11). media/comp/F1_b.mp4 = ls4w_F1_arun2s1 (best mouth incl. closure into 没; fails hands: arm to the hair, blur, shape changes).
  Review: review/f1_ab/F1_new_a_sound.mp4, F1_new_b_sound.mp4 + two TAKES lines (first) in index.html. F1_ar9.mp4, F1_alt.mp4 kept.
- More seeds on F1hold t1 submitted by me: work/bedcar4/anim_batch9.sh/.log (ahold1s3..s7).
- Keyframes via Codex first (work/codex/bc_F1p_{point,blade}.prompt, runner bc_F1p_run.sh, logs bc_F1p_*.log) -> media/kf/v4/bedcar/F1p_*_codex.png.

## CHECKPOINT 5 (20:25) — read this block first to resume
**Subagents and their notes files** (each writes plan first, appends as it goes):
- SING (Sonnet, running): animate on every acted take + measure + face/hand strips -> `work/bedcar4/notes/SING.md`,
  strips `work/review/lipsync_v4/bc4/`. Does NOT pick.
- set-check batches 1-3 (done): `work/review/set_check/v4bc/SUMMARY_1.md`, `_2.md`, `_3.md` (+ verdict JSONs, zoom/).
- PREP (Sonnet, done; L1 t3/t4 still to sheet: work/tmp/bc4_prep_x/mk.py + strips.py): 16-frame sheets, hand/face strips, last-frame set checks of K1 ots F3a F6b J1 L1 takes + L1_b_t1 keyframe -> `work/bedcar4/notes/PREP.md`, sheets `work/review/comp_v4/takes/`.
- CHK4 (Sonnet, done): set check of the mirror keyframes F6m_t1/t2 -> `work/bedcar4/notes/CHK4.md`.
- COMP_A (Sonnet, done): F3a + K1 comps -> `work/bedcar4/notes/COMP_A.md`.
- COMP_J1 (Sonnet, done): shots/_j1v4.py + J1 comp (press, page art J1_page_v4, flat end frame for WORLD) -> `work/bedcar4/notes/COMP_J1.md`.
- JUDGE (Sonnet, done; verdicts in JUDGE.md): blind strip verdicts I4 F1 I3a K2a J4R -> `work/bedcar4/notes/JUDGE.md`. F6b animate (anim_batch3.log) and I1 (acted t3 t4 pending) later.
- COMP_B (Sonnet, done): I4 (+J1 tail), I3a, F1 + F1_alt, K2a (+push into K2b), J4 split -> `work/bedcar4/notes/COMP_B.md`.
- SING (Sonnet, done): tables + strips for I4 F1 I3a K2a J4R F6b (work/bedcar4/notes/SING.md). F1_ar10 errored on the relay.
- REVIEW2 (Sonnet, done): L1 t3/t4 sheets + last-frame set check; blind judge of F6b mirror animate takes -> `work/bedcar4/notes/REVIEW2.md`.
- COMP_C (Sonnet, done): L1 + F6b mirror comps -> `work/bedcar4/notes/COMP_C.md`.
- COMP_I1 (Sonnet, done): collect/measure/strips/blind judge of I1 animate a3 a4 a3b a4b, pick, comp I1 -> `work/bedcar4/notes/COMP_I1.md`.
- FINAL_J4F6 (Sonnet, running): J4R re-act animate a5 a5b a6 a6b (anim_batch6.log) judge vs a2b + re-render J4; F6b seeds 3103-3105 judge vs am2r + re-render F6b -> `work/bedcar4/notes/FINAL_J4F6.md`.
- planned: COMP agents per `work/bedcar4/COMP_BRIEF.md`
  -> `work/bedcar4/notes/COMP_<group>.md`.

**SCOPE CHANGE (coordinator, 20:3x, from the director): F6b becomes the MIRROR shot.** 33 frames, song frames 2882-2914
(120.083-121.458), line 问了也白问 个个都真. Staging = v3 F4a framing (v4 guide car26/v4_F4a), tightened toward the daughter's end
if the guide allows: Jade's eyes large at one end of the glass, the daughter deeper in the reflection rapping the last line AT the
mirror (F1's counting hand, chin-lead), point at her mother on the last word; Jade's eyes crinkle on 个个都真 and flick up to meet
hers; dusk road + lamps outside. Her mouth via the two-pass lip-sync route (or small enough not to be the subject: say so). No hair.
The hair-catch F6b work (F6b_r_t1 keyframe, takes v4bc_F6b_t1/t2) is dropped. v3 F6b kept in media/comp/_v3/F6b.mp4.
Splice unchanged: F6 = F6a (50) + F6b (33), F6b = song frames 2882-2914.
Progress: keyframes media/kf/v4/bedcar/F6m_t1/t2.jpg (guide bc/v4bc_F6m = v4_F4a x1.17, both faces in the glass; my eye prefers t2:
her face larger, two-finger hand at the mirror; her face is ~55 px high at 540p: small, so the mouth is not the subject);
set check CHK4: F6m_t1 PASS, F6m_t2 PASS (work/bedcar4/notes/CHK4.md) -> pick F6m_t2. Submitted F6mact t1 t2 (jobs.tsv; ids chaosmonkey/v4bc_F6mact_t1-6545eed602, _t2-654d593459). Acted take spec written: vspecs4.py S['F6mact'] (vt0 119.9, 1:1 to the
song, point on 真 121.3, Jade's eyes flick up and crinkle at 120.9) -> then two-pass animate (mute the echo before 120.09).

**LIP-SYNC RECIPE (final, docs/LIPSYNC_V4.md, read 21:0x):** Kling acts from the keyframe (timed, calm, no audio) -> pruna/p-video-animate
re-renders the whole character from the keyframe on the acted take + stem window (frame 0 = song t0, shift 0, speed 1), 2 seeds; rap:
LIPSYNC's rap instruction prompt + 5 seeds; judge on the 2x face strip; output 1408x768 -> scale to 960x540. Conditions: face >= ~240 px
in the cut (~350 for rap), front to 3/4, mouth relaxed in the keyframe. Seedance takes may ship only if the strip clearly passes.
My implementation = the same thing: work/bedcar4/anim4.py (tags ls4w_<SHOT>_a<k>; `--rap 1` uses lipsync_v4.RAP; `--seed`), on my
acted takes `<SHOT>act` (vspecs4.py, timed 1:1 to the song from vt0, CALM clause). Seeds requested from SING: 2 per acted take,
F1 rap x10 (5 per acted take), F6b mirror 2 + 2 rap. Animate output gets the set check and hand check too.
F6b mirror: her face ~55 px at 540p: under the condition -> her mouth is small in frame (not the subject); animate still drives it.

**IMAGE ROUTE (director, 21:0x):** gpt-image via Codex (docs/TEAMS_V4.md "Image generation route") wherever it can do the job;
Cloudflare gpt-image-2 only where Codex cannot (size, refs, refusal, lock stall). Every keyframe made so far (40 images, kf_r1..r8
logs) went through Cloudflare gpt-image-2 (before this rule). Any further keyframe: test Codex once with the guide + plate + sheets
first, log the route per image. Video stays on Cloudflare. Subagents told when they generate images (none of mine do).
Picks for non-singing takes: work/bedcar4/picks4.json (F3a t2, K1 t1 src 0.3-2.6, ots t1 for I1 + K1 pushes, J1 t1 press src 3.05).

**Done**
- spend so far (ledger, my tags v4bc_* and ls4w_<my shots>_*, list-price estimates): $83.6 (gpt-image-2 $18.2, Kling v4 $36.7 incl.
  the 6 lost jobs, Seedance $22.2, animate $6.6) of $140.
- I1 DONE: pick ls4w_I1_a4b (acted t4 + animate seed 2002, frame0 176.9); blind judge PASS (eyes on the child, opens/closes between
  words, jaw moves, no smear; squeeze/wriggle weak); my eye on the strip: natural small mouth, but the face is rendered softer/more
  modelled than the keyframe and the girl's eyes go doll-like. media/comp/I1.mp4 72 f (4-frame fade from paper; ots push lands on
  I2 frame 0 with mean diff 4.5/255). Set check of part A: visually matches (bunny, bed, nightstand, door light) but the verdict
  was not merged (numeric flags only). Darkest LEFT.
- COMPS DONE (COMP_C): media/comp/L1.mp4 107 f (push 1.0->1.03; set check PASS; darkest LEFT, plainest = upper-left wall above the
  bed x110-420 y0-130 @960, or wall between Jade's head and the door x580-740 y0-150); media/comp/F6b.mp4 33 f (song frames
  2882-2914; mirror; push 1.0->1.04 toward the girl; set check PASS; darkest RIGHT/middle). F6b defect: finger smears f4-8, f20
  (animate) -> 3 more rap seeds submitted (anim_batch5.log: ls4w_F6b_am2r3103..3105).
- picks: L1 = t4 (src 0.3-4.76, speed 1; exhale visible; no book glance in either take; last-frame set check PASS);
  F6b mirror = ls4w_F6b_am2r (frame0 119.9; blind judge PASS rank 1/4; no clear point on 真, no clear eye flick-up).
- I1 animate submitted by me (work/bedcar4/anim_batch4.sh/.log: ls4w_I1_a3 a4 a3b a4b on acted t3/t4, frame0 176.9).
- J4Ract2 t1 t2 running; L1 t3 t4 ready (REVIEW2 sheets them).
- COMPS DONE (COMP_B, notes work/bedcar4/notes/COMP_B.md): I4 67 f (Seedance-free two-pass take 187.0-189.375 + j1_frame tail;
  set check PASS; darkest LEFT 46 vs 101), I3a 40 f (PASS; darkest LEFT), F1 43 f + F1_alt 43 f (PASS; darkest LEFT = headrest),
  K2a 38 f (room to 211.70 then PagePush into K2b, last 1080p still == K2b_f0 (diff 0.0); set check FAIL only for the bunny on the
  bed (bible object just inside the top edge of this view: override as CHECKPOINT 3); darkest LEFT), J4 97 f (split; exposure matched).
- J4 2026 half (J4R a2b): the girl leaves the lap and turns to her mother; a hand rests on her head; book flattens -> does not mirror
  the 1988 half. Re-act submitted: J4Ract2 t1 t2 (girl stays in the lap facing out, arms up on 2.45 s = 198.75). ATTIC told (their log).
- SINGING PICKS (picks4.json; judge verdicts work/bedcar4/notes/JUDGE.md; my eye on the I4 and F1 strips):
  I4 = ls4w_I4_a1 (two-pass, frame0 186.5) PASS, looks down at the child; I3a = ls4w_I3a_a2b (frame0 182.6) PASS;
  K2a = ls4w_K2a_a1 (210.2) BORDERLINE best of 4 (b closure on Book; face ~200 px, under the condition); J4R = ls4w_J4R_a2b (196.3)
  PASS, arms up 198.80-199.0; F1 = ls4w_F1_ar9 (rap prompt, 106.8) soft PASS: real rap hands (points at herself / chest) but mid-line
  under-articulated, 蹦/没 not closed; F1_alt = Seedance ls4w_F1_3 (placed 106.275 by eye) PASS on the mouth (closed 没, open 童) but
  the V hand is frozen beside the face the whole line. Shipping F1 = ar9 (the director's arm note), F1_alt rendered for her to compare.
  Strips: work/review/lipsync_v4/bc4/<take>_{face,sheet,hands}.jpg.
- COMP DONE: media/comp/J1.mp4 (26 f; render --t0 4555/24 --t1 190.875), shots/_j1v4.py (j1_frame valid from 189.375 for I4's last
  10 frames). Press: nail drops ~1 px at src 2.93-2.97 = song 189.6 (inside 189.54-189.67; cue 189.62). Page art J1_page_v4 scaled
  0.5 about the marked character (char under the fingertip, text kept on the page), lights from 189.62; push + perspective-squaring to
  the flat window x0..2560 y100..1540 (exact last frame, falloff formula in LOG_v4_world.md + work/bedcar4/notes/COMP_J1.md,
  work/bedcar4/ends/J1_last.png). Looked at the sheet: reads well (finger on the peak, text legible from f15). Weak: press is a 1 px
  dip (not a visible bend), lit character hidden under the fingertip, hand dissolves as a soft smear f10-13, faint double gutter.
- Relay: I1act t1 t2, L1 t1 t2, F6b t2, J1 t2 stuck "running" 6500 s (lost?) -> resubmitted I1act t3 t4, L1 t3 t4 (jobs.tsv).
  F6b t2 / J1 t2 not needed any more. The stuck four may still bill (~$4.7).
- COMPS DONE: media/comp/F3a.mp4 (29 f; t2; puff pursed f26-28 = 112.125-112.208, palm to frame right; last-frame set check PASS;
  weak: hair not visible, re-pose jump f13-15) and media/comp/K1.mp4 (164 f; room f0-51 K1 t1 src 0.3-2.25 (lead retimed to drop the
  smeared lean-in), ots push f52-83 with OtsPush4 q0 [[274,461],[1013,184],[1231,593],[500,932]], BOOK's K1page f84-163; room set
  check PASS; darkest side = LEFT (nightstand/wall column x 0-350, y 400-900) -> calligraphy side for CUT; weak: hard cut room->ots
  as v3, painted spine ~20 px off the art crease, BOOK's page has a stretched band at its right edge). Notes work/bedcar4/notes/COMP_A.md.
- keyframes + set check + lead overrides: table in CHECKPOINT 3 below (picks: I1d_t1, I3a_t2, I4c_t6, F1c_t4, K1_t2, ots_t3,
  K2a_r_t1, J1_t1, J4R_r_t1, F6b_r_t1, L1_b_t1 (L1_b not yet set-checked: bunny ~6 % left, black flashlight, book bottom centre)).
- collected takes (media/gen/v4bc_<SHOT>_t<k>_<id>.mp4): F1act t1 t2, F1ref t1, F3a t1 t2, F6b t1, I3aact t1 t2, I4act t1 t2,
  J1 t1, J4Ract t1 t2, K1 t1 t2, K2aact t1 t2, ots t1. Seedance: ls4w_I4_1..6, ls4w_F1_1..6 (measured: tables
  work/review/lipsync_v4/{I4,F1}_takes.tsv, all gate FAIL, lags -958..+458 ms = the re-perform problem), ls4w_I3a_1..6 (v3 kf, data only).
- F3a: t2 blows to frame RIGHT (palm held out right), no hairs visible; candidate pick t2 (time map: puff onset -> 112.146).
- hand-over stills: work/bedcar4/ends/{K2b_f0,K1page_f0,I2page_f0}.png. J1->J2 proposal in LOG_v4_world.md.
- comp framework shots/_bedcar4.py (picks work/bedcar4/picks4.json, not yet written); comp brief work/bedcar4/COMP_BRIEF.md.

**In progress / pending relay jobs** (ids in work/bedcar4/jobs.tsv = shot, take, id, spec media/gen/specs/v4bc_<SHOT>_t<k>.json;
output media/gen/v4bc_<SHOT>_t<k>_<id>.mp4): I1act t1 t2, F6b t2, J1 t2, L1 t1 t2 (running). Animate jobs: SING agent, ids in
media/gen/specs/ls4w_<SHOT>_jobs.txt (tags ls4w_<SHOT>_a<k>, specs media/gen/specs/ls4w_<SHOT>_a<k>.json).

**Next**
1. L1_b_t1 set check (Sonnet) + last-frame checks of every picked take.
2. JUDGE singing takes blind (director's words), then my picks -> picks4.json.
3. Non-singing picks on 16-frame sheets (K1, ots, F3a, F6b, J1, L1) -> picks4.json.
4. COMP agents: F1 F3a F6b | I1 I3a I4+J1 | K1 K2a L1 | J4 split (needs ATTIC J4L).
5. Report.

**Decisions**: Seedance for I1/I3a/K2a/J4R refused by the permission classifier, not retried; two-pass route for all singing.
Override rule for the strict set check: CHECKPOINT 3. Flashlight: black everywhere (bible says orange; every shot already black).
<!--/CKPT-->

## History: CHECKPOINT 3 (picks table)

## CHECKPOINT 3
- keyframe picks (set check verdicts in work/review/set_check/v4bc/SUMMARY_1..3.md):
  | shot | keyframe | strict check | lead decision |
  |---|---|---|---|
  | I1 | media/kf/v4/bedcar/I1d_t1.jpg (guide bc/v4bc_I1d, x1.92 of v4_I1) | FAIL: pillow higher, bunny ~10 % right; "invented" cup (it is the bible's cup on the nightstand) and headboard just inside the left edge | ACCEPT with override: every object on its own side (headboard/pillow/bunny left, bunny on the far side of the pillow, door light right); framing ~5 % wider than the crop |
  | I3a | I3a_t2.jpg | PASS | pick |
  | I4 | I4c_t6.jpg (bc/v4bc_I4c, x1.19 of v4_I4) | PASS | pick; left 35 % dark for the calligraphy |
  | F1 | F1c_t4.jpg (bc/v4bc_F1c, x2.34 of v4_F1) | PASS | pick (two fingers out, the other hand on the strap; empty seat edge at right) |
  | K1 | K1_t2.jpg | PASS | pick |
  | ots (I1, K1 pushes) | ots_t3.jpg | PASS | pick |
  | K2a | K2a_r_t1.jpg | FAIL: bunny, pillow, blinds, cup drawn just inside the top edge (the guide has them just above frame) | ACCEPT with override (all on their own side; framing a little wider at the top) |
  | J1 | J1_t1.jpg | FAIL: flashlight 8 % inside the left edge (guide: at the edge) | ACCEPT with override (prop on the correct side; the shot pushes into the page) |
  | J4R | J4R_r_t1.jpg | FAIL small: window/blind at the top-left corner (the room's window, just outside the guide frame) | ACCEPT with override |
  | F6b | F6b_r_t1.jpg | FAIL small: "invented" spark = the drifting hair (intended) | pick (t2 PASS but no hair, weaker) |
  | L1 | re-making (L1_b: black flashlight, the bible says orange but every other shot is black; bunny place) | L1_r_t2 FAIL marginal (bunny 5-8 % left) | pending |
  Override rule I used: FAIL for a key object on the wrong side, missing, or a new piece of furniture; ACCEPT (logged) when every key
  object is on its own side and the only findings are <=10 % shifts or bible objects just inside a frame edge.
- LIPSYNC CP4 (read 20:xx): Seedance re-performs the audio (not frame-locked; lag not certifiable); **pruna/p-video-animate on an acted
  Kling take muxed with the stem is in sync at shift 0**. So every singing shot now has an acted Kling take TIMED 1:1 TO THE SONG
  (`<SHOT>act`, frame 0 = song vt0) for the two-pass route (`work/bedcar4/anim4.py`, tags ls4w_<SHOT>_a<k>), plus Seedance takes
  where already made (I4 x6, F1 x6; I3a x6 from the failed v3 keyframe = data only).
- Seedance submissions for I1, I3a (new kf), K2a, J4R were refused by the session's permission classifier; not retried. Those
  four go two-pass only.
- F3a: t1, t2 collected; t2 blows clearly toward frame RIGHT (palm out to the right); no hairs visible at this size.
- pending relay jobs (work/bedcar4/jobs.tsv): K1 t1 t2, ots t1, F1ref t1, I4act t1 t2, F1act t1 t2, I1act/I3aact/K2aact/J4Ract t1 t2,
  F6b t1 t2, J1 t1 t2. Keyframes L1_b t1 t2 (work/bedcar4/kf_r7.log).
- comp framework: shots/_bedcar4.py (picks work/bedcar4/picks4.json; lips mechanism off).
## CHECKPOINT 4 (resumed 20:21 after the usage-limit stop)
- the Seedance submissions for I1/I3a(new)/K2a/J4R were NOT "about to happen": they were refused by the session's permission
  classifier (twice) and I am not retrying them; those shots go two-pass (acted Kling 1:1 to the song -> p-video-animate), which
  is also LIPSYNC CP4's finding (Seedance re-performs the audio; animate is in sync at shift 0).
- collected: F1act t1 t2, F1ref, F3a t1 t2, F6b t1, I3aact t1 t2, I4act t1 t2, J1 t1, J4Ract t1 t2, K1 t1 t2, K2aact t1 t2, ots t1.
  Still running: I1act t1 t2, F6b t2, J1 t2, L1 t1 t2 (L1 from L1_b_t1.jpg, black flashlight).
- hand-over stills re-rendered: work/bedcar4/ends/{K2b_f0 (BOOK changed K2b), K1page_f0 (unchanged), I2page_f0 (unchanged)}.png.
- next: Sonnet agent SING: animate on every acted take + measure + strips; then a blind Sonnet judge; Sonnet comp agents per
  work/bedcar4/COMP_BRIEF.md once picks are in.

## DONE 2026-11-18 ~22:30 — final state (BED+CAR v4)
All comps 960x540, 24 fps, no audio, exact frame counts; scripts shots/<ID>.py on shots/_bedcar4.py (picks work/bedcar4/picks4.json),
1080p = re-render with --size 1920x1080. v3 files in media/comp/_v3/, shots/_v3/.

| shot | frames | status | pick | lip-sync (strip) | set check | calligraphy side |
|---|---|---|---|---|---|---|
| F1 | 43 | done | ls4w_F1_ar9 (Kling act + animate, rap prompt) | soft PASS: rap hands (points at herself/chest), grin, wide on 童年; mid-line under-articulated, 蹦/没 not closed. Strip work/review/lipsync_v4/bc4/ls4w_F1_ar9_face.jpg. Alt media/comp/F1_alt.mp4 = Seedance ls4w_F1_3: better mouth (closed 没) but frozen V hand | PASS (last) | LEFT (headrest) |
| F3a | 29 | done | v4bc_F3a_t2 (Kling) | no singing face | PASS (last) | — |
| F6b | 33 (song f 2882-2914) | done: NOW THE MIRROR SHOT | ls4w_F6b_am2r3104 (act + animate, rap prompt) | PASS-ish at small size (~55 px face, mouth not the subject): steady two-finger hand, natural mouth; no point on 真; Jade's eyes crinkle ~120.75 | PASS (last; flags only) | RIGHT/middle darkest |
| I1 | 72 | done | ls4w_I1_a4b (act + animate) + ots push into I2 | PASS: eyes on the child, opens/closes between words; face a little softer/modelled than the keyframe; squeeze weak. Strip ls4w_I1_a4b_face.jpg | visual match, not merged | LEFT |
| I3a | 40 | done | ls4w_I3a_a2b | PASS: hesitant look down, head tips back, eyes up | PASS | LEFT |
| I4 | 67 | done, no morph | ls4w_I4_a1 + J1 view tail (189.375-) | PASS: looks DOWN at the child, small natural openings, opens on You're able | PASS | LEFT (designed dark 35 %) |
| J1 | 26 | done | v4bc_J1_t1 + J1_page_v4 (BOOK) | — | take last frame FAIL (flashlight 8 % inside edge; override) | — |
| J4 | 97 | done (split; my half) | ls4w_J4R_a6b (re-act: girl stays in the lap facing out) | mouths in faces, arms up ~198.7; small faces | flags only | — |
| K1 | 164 | done | v4bc_K1_t1 (whisper, mouth in curls) + ots push + BOOK K1page | no singing mouth | PASS | LEFT |
| K2a | 38 | done | ls4w_K2a_a1 + PagePush into K2b | BORDERLINE (best of 4): b closure on Book, small "He opened"; face ~200 px | FAIL (bunny just inside the top edge; override) | LEFT |
| L1 | 107 | done | v4bc_L1_t4 | — | PASS | LEFT (upper-left wall) |
| L2 | 63 | kept v3 (reference) | v3 | — | PASS first+last | — |
F4a: not re-made (F2 belongs to SWARM; the mirror moved to F6b by the lead's scope change).

Splices: F3 = F3a 29 + F3b 12 (cut 2694); F6 = F6a 50 + F6b 33 (cut 2882); I3 = I3a 40 + I3b; K2 = K2a 38 + K2b (cut 5091); L2's
last frame 5659, ATTIC L2b from 5660. J4: ATTIC must re-render their half with arms on 198.74 (theirs go up at 197.75-197.9 now);
then re-run shots/J4.py (command in LOG_v4_attic.md note).
Cue times for SOUND (REVISION_V3 §11): F3a puff 112.146 kept (pursed puff f26-28). J1 press: the fingertip dip is at song ~189.50-189.55
(about 0.1 s BEFORE the 189.62 cue; the lit character fades in from 189.62). J4 2026 arms up ~198.7 (gong 198.833). F6b: the hair-catch
and laugh are gone; now the girl raps 问了也白问 个个都真 at the mirror (no catch sound). L2 unchanged.

## DONE (F1 re-make) 2026-11-18 late
- Cause of the finger changes: BOTH passes. The Kling act pass already switched hand shapes frame to frame (my old act prompt asked
  for chops + points + a raised hand); the animate pass then re-drew the hand differently again (fist / one finger / two fingers).
  Strips: work/review/comp_v4/F1_act_t2_hands_every.jpg, F1_ar9_hands_every.jpg.
- Timing check: placement arithmetic was CORRECT (take audio = stem at 106.800 = map; comp frames = take frames +5.8; review mux at
  107.0417). The real fault was a COLD START: the animate model did not articulate the first ~20 frames. Fixed with a sung run-up
  (stem 108.80-110.62 spliced before the line; virtual frame0 105.13): every candidate now moves the mouth from comp frame 0.
- Hands: new keyframe via Codex (F1p_point_codex.png: loose fist, index finger out at her chest; left hand on the strap; set check
  PASS) + act prompts with a HOLD clause; acted takes F1hold t1-3, F1run t1-3; 16 run-up animate seeds (rap prompt).
- Pick: media/comp/F1.mp4 = ls4w_F1_ahold1s1 (one index-finger shape held, never across the face; mouth moves on every syllable
  from f0, closes into 蹦). STILL FAILS the strict test on: no lip closure into 没 (round o), closed-smile frames on 头/出, mild
  ghosting f26-27, hand hidden by hair f10-11. Alternative media/comp/F1_b.mp4 = ls4w_F1_arun2s1 (best mouth incl. 没 closure, but
  the hand waves to her hair and blurs: fails hands). Kept: F1_ar9.mp4, F1_alt.mp4.
- Review: review/f1_ab/F1_new_a_sound.mp4 (F1), F1_new_b_sound.mp4 (F1_b), two TAKES lines added first in index.html.
- Spend now about $93 of $140 (ledger estimate, my tags).

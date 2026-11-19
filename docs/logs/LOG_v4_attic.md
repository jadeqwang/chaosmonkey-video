# LOG v4 ATTIC (1988 room shots), preview_v4

Team lead: Claude (Opus 5.5). Brief: REVISION_V4 §1, §5, §8, §12; TEAMS_V4 (ceiling $170). Spend tags `at4_*` (keyframes
`at4_kf_<KEY>`, acted takes `at4_<KEY>_k4_t<k>`, singing takes `at4ls_<SHOT>_<k>`). Project total at start: $506.30.
Scratch `work/attic4/`. v3 backups: media/comp/_v3/ (A1..L3, J4_1988), shots/_v3/ (+ _attic3, _attic_grade, _margins, _rooms88).

<!--CKPT-->
## CHECKPOINT 2026-11-18 20:25 (resume after usage limit)
- All 5 group agents stopped by the Sonnet usage limit (resets ~22:20 CST). State is in work/attic4/notes/<GROUP>.md:
  OPEN: all keyframes picked + set-check PASS; takes queued A3a A4 L2b (x2), A1 L3 (x1), at4ls_J4L_1..3.
  B: B1 / B2 / B2_ots keyframes + crops; C2 edited (v3 hair read as one ponytail; a third hand removed); takes at4ls_B1_1..6,
     at4ls_B2_1..4, at4_B2_ots t1-2, at4_C2 t1-2.
  CD: keyframes C3 C5a D2d D3 D9_0/a/b/c; takes at4ls_C3_1..6, at4ls_D3_1..4, at4_D9 t1-2, at4_C5a t1-2, at4_D2d t1-4 (ids work/attic4/cd_ids.txt).
  EF: E1 E3 F3b keyframes (set check PASS); E6 route A (BiRefNet matte + empty plate) works so far; takes at4ls_E1_1..5,
      at4ls_E3_1..5, at4_F3b t1-2.
  G: G1 G3 G4 G5 keyframes PASS; takes at4ls_G1/G4/G5 _1..6, at4_G3 t1-2. G group at its $42 ceiling.
- Spend at4 total $131.65 of $170 (all generation for the first pass is submitted; re-takes will need the lead's approval).
- Lead's look at all picked keyframes (work/attic4/look/kf_all.jpg): set placement consistent across shots (TV left, window right,
  stack before D9 / fallen books lower right after), little Jade's hair = E6 in every keyframe, Mama on model.
- Fixed: ls4.py `wait` read the wrong jobs file (now at4ls_<SHOT>_jobs.txt).
- done 20:30: collected every relay job (73 done, 2 errored/refunded: at4ls_B1_3, at4ls_B2_1; ids work/attic4/all_ids.txt).
- Director's file-first rule added to work/attic4/BRIEF_COMMON.md (end); group notes files: work/attic4/notes/{OPEN,B,CD,EF,G}.md.
- RECIPE CHANGE (coordinator, 20:40): LIPSYNC is DONE; final recipe = Kling v4 acts (calm, no audio, 2 takes) -> pruna/p-video-animate
  re-renders the whole character singing to the stem window (frame 0 = song t0, shift 0, speed 1, 2 seeds, 1408x768 -> 960x540) ->
  judge on the 2x face strip. Measured: two-pass 7/15 (child 2/3, Mama 3/4, Jade 2/4); Seedance+audio 3/12 at 4 s, 1/13 longer.
  Our Seedance takes (B1 B2 C3 D3 E1 E3 G1 G4 G5 J4L) may ship only if their strip clearly passes; otherwise two-pass (existing
  well-acted takes may be the motion source). Set check + hand check also on animate output. G5 with vocals_v4.wav.
  ATTIC wrapper for it: work/attic4/ls4v2.py (= tools/gen/lipsync_v4.py + --stem, anim --mute, anim --src TAG --kf, J4L/G5 aliases,
  eye -> work/attic4/notes/lipsync_picks.md); dry-run tested (act G5, anim G5 from at4ls_G5_1). Written into BRIEF_COMMON.md.
  Spend per group at 20:40: OPEN 17.33, B 21.69, CD 28.85, EF 24.93, G 38.84 = 131.65. Ceilings revised: OPEN 23, B 30, CD 38, EF 32, G 47 (=170).
- 20:45 limit lifted: all ATTIC relay jobs collected (none pending); all 5 group agents resumed by message with the recipe change
  and the file-first rule (agent ids in this session; resume otherwise by relaunching from the notes files).
- IMAGE ROUTE (director): gpt-image through Codex first (docs/TEAMS_V4.md "Image generation route"); Cloudflare gpt-image-2 only
  where Codex cannot. Wrapper work/attic4/kfcodex.py (same scene JSON as kf4.py). Lead testing on G5 (log work/attic4/codex_test.log)
  before switching groups; written into BRIEF_COMMON.md.
  TEST 20:42: Codex OK (G5 from the same scene JSON + 7 reference images, 127 s, 1672x941, media/kf/v4/alt/G5_cxtest.png vs
  media/kf/v4/G5.jpg: work/attic4/look/codex_vs_cf_G5.jpg). Face and E6 hair held (centre part, two ponytails, no fringe, dot on her
  left chest); a little smoother / less paper grain, and it framed tighter than the guide (set check still decides). Use: Codex for
  new stills and edits; Cloudflare only for sources of tight singing crops (needs > 1672 px) or if Codex fails the set check twice.
  (Fix made: the prompt must come before the -i flags.) Route so far: EVERY keyframe made before 21:00 = Cloudflare gpt-image-2 (kf4.py).
- OPEN reported (21:00, work/attic4/notes/OPEN.md): comps A1 (still + code sign + title; Kling take rejected: neon faded) 131 f,
  A3 (A3a t2 + v3 A3b) 69 f, A4 t1 70 f, L2b t2 26 f, L3 t1 + off 34 f, J4_1988 (Seedance t1, borderline, arms up ~197.8 = 0.9 s
  EARLY vs 198.74) 97 f; all keyframes Cloudflare. Lead looked at the comp sheets (work/attic4/look/open_comps.jpg): fine except J4
  (arms early; very bright/pink, not neon red: BED+CAR balances the split). Sent back: J4L two-pass with arms on 198.74, last-frame
  set checks of every pick, A4 hand strip. OPEN ceiling 23 -> 26 (to be covered by B underspend).
- B reported (21:10, work/attic4/notes/B.md, $21.7): B1 = Seedance at4ls_B1_4 (frame0 at 13.518, face_px 261, gate auto-pass),
  163 f, arm chain continuous in every hand-strip frame, last-frame set check PASS; B2 = Seedance at4ls_B2_4 (lap, frame0 21.893) +
  Kling ots t1 + warp landing on WORLD's NEW B3 frame 0 (media/comp/B3.mp4 of 18:57, diff 2.38/255; re-extract if WORLD re-renders
  B3), 92 f; C2 re-made (v3 hair was one ponytail; a third hand removed) Kling t2, 24 f. Lead read the B1 strip
  (work/review/lipsync_v4/at4ls_B1_4_face.jpg): closes on me f91, before f97, be f187; opens wide on how, round on 空; BUT two
  one-eye half-winks (f61-63, f93-95) and the acting is weak (no clear tug, no bounce). Verdict: borderline PASS, ship for now;
  acting re-take only if budget remains (bounces smear under animate anyway). B group underspends: $3 of it moved to OPEN for J4L.
  Moved: B1 Mama's turn ~21.0 (target 21.3); B2 warp start 24.6 (v3 24.5); C2 hands up ~45.7 (v3 ~45.3).
- CD reported (21:35, work/attic4/notes/CD.md, $29.45): comps C3 83 f (animate on Seedance take 2's acting, ls4w_C3_asrc2s1),
  C5a 57 f (Kling first+last t1; breath to screen right, does not exit), D2d 15 f (t3), D3 84 f (animate ls4w_D3_asrc1s1, face 197 px,
  gate open 0.57: borderline), D9 80 f (ONE Kling take D9_0 -> mids D9a, D9b -> last D9c: no jump in the climb; cues within ~1 f of
  §11 on sheets: climb 83.24, topple 83.80, land 84.12, catch 84.35). Lead on the sheets (work/attic4/look/cd_comps.jpg): D9 good;
  C5a good; C3 REJECTED (crop so tight the acting is gone: forehead cut, child from behind, hands out of frame) -> wider crop +
  two-pass; C5a: add faint ink ribbons exiting right in BOOK's band (decision: yes); D2d re-check; D3 waits for the blind judge.
- EF reported (21:45, work/attic4/notes/EF.md, $26.5): E6 route A DONE (BiRefNet matte local + empty-room plate edit, Cloudflare;
  set check PASS f0/f65; v3 acting/hair untouched) 66 f; F3b Kling t1, 12 f (blow window sped ~3x, hairs drift right, faint);
  E1 animate ls4w_E1_asrc1s1 borderline (nose tap + cross-eyed giggle missing); E3 animate ls4w_E3_asrc1s1 borderline AND the
  wuxia cast was lost (animate turned the sword-hand into open palms). Lead on E6 sheet: clean, but the v3 zoom (1.3-1.42) was dropped:
  restore it. Sent back: E3 new calm cast act + animate with a gesture-keeping prompt; E1 one new act with the tap; E6 zoom; last-frame
  set checks on animate outputs. EF ceiling 32 -> 34. Ceilings now OPEN 26, B 21.7 (done), CD 38, EF 34, G 47 = 166.7.
- OPEN follow-ups DONE (22:05, ~$19.2 by OPEN's own sum): last-frame set checks PASS for A3a A4 L2b L3 (+ L3_off still);
  A4 hand strip PASS. J4L two-pass tried: Kling acts hit the arms cue (~198.7-198.8, up by 199.1) but BOTH animate seeds DROPPED the
  arms-up (animate re-renders from the arms-down keyframe and does not follow a big limb move), gate FAIL -> J4_1988 stays the
  Seedance take 1 comp with arms up ~197.8 (0.9 s early vs 198.74). FINDING for the lead/LIPSYNC: p-video-animate loses large
  gestures that leave the keyframe silhouette (J4 arms up; E3 sword-hand became open palms). OPEN group closed.
- G reported (22:10, work/attic4/notes/G.md, ~$40.1): all 18 Seedance takes unusable (G5 mouths Mama's words; G1/G4 drift);
  G1 animate ls4w_G1_asrc4s1 borderline-pass (small amplitude) 144 f; G3 Kling t2 (hand flat, no webbing, five fingers; last frame
  PASS) 165 f; G4 animate ls4w_G4_asrc1s1 borderline (Mama's eyes closed last 3 s, face drifts out of the crop) 125 f, margins open
  over 10 f then the camera widens to the books and pushes in; G5 animate ls4w_G5_asrc5s1 (vocals_v4, muted Mama) lips PASS (opens
  ~149.3) but the thinking beat is weak (no nod) 78 f. Sent back: finish G5 Kling acts (strong thinking prompt) + anim; one new G4
  act (eyes open, look to the books, head steady) + anim; G1 last-frame set check.
- CD deltas (22:35, ~$31): C3 RE-MADE: crop C3_crop2 (x384 y0 w2458 h1382), Kling act2 + animate ls4w_C3_a2s2 (face 238 px,
  frame0 45.665), lips borderline-pass, last frame PASS; lead looked at the sheet: the finger pressing the hands down and the child's
  sneak-up now read -> ACCEPTED. Calligraphy C3 LEFT. D2d: fixed keyframe + t3 last frame PASS; bow bottom retimed to ~63.98-64.0.
  D3: no free calligraphy side. C5a code ribbons: lead REJECTED (mechanical white streaks over the child's face) -> reverted; C5a
  ships without a flow tail; the crossing is BOOK's C5b entry (lead may ask BOOK for a tail from their solver).
- EF round 2 (22:55, ~$33): E3 new Kling act1 HAS a readable sword-hand + pushing palm, but animate (2 seeds, gesture-keeping
  prompt) loses it again; comp still the old animate (open palms) = cast NOT delivered. Lead: one more test, animate with the IMAGE =
  the act1 frame at the cast peak (media/kf/v4/E3_castref.jpg), EF ceiling 35. E1 new act not better (kept asrc1s1). E6 v3 zoom
  restored (66 f). Last-frame checks E1/E3 consistent by eye.
- EF FINAL (23:05, ~$33): E3 cast-image animate test result pending/see EF.md; E3 ships the old animate (open palms) unless the
  test kept the sword-hand. G round 2 (23:10, ~$43.4): G5 Kling act1 + animate a1s2 -> LEAD PICKS a1s2 (strip read by me: eyes down
  and away f35-57, slow blink f59-63, back to Mama, mouth opens f65-69 = on the v4 Yes 149.152-149.306); NOTE the lip strip/gate tools
  label words from the OLD analysis/timing.json ("Yes" 148.72), so G5 gate numbers are invalid; verdict by eye. G4 keeps
  ls4w_G4_asrc1s1 (lowered lids = looking down at the child; accepted). G1 last frame PASS.
- 23:30 all five groups finished. E3 round 3 (animate with the cast frame as image): still open palms -> E3 ships lips + shrug,
  CAST NOT DELIVERED (lead decision needed; the only sword-hand is the unsynced Kling act media/gen/ls4w_E3_act1_2a06e46d1b.mp4).
  ATTIC spend by tags (at4* + ls4w_ of my shots): $147.73 of $170. Project total $816.27.
  All 22 comps verified 960x540 at their frame counts (G5 78). Trap found by G: tools.ink.run's frame cache does NOT key on
  media/comp/attic4/picks.json; after changing only a pick, delete the comp (or touch the script) before re-rendering.
  Blind judge (Sonnet) running: lip A/B on 9 shots (packet work/attic4/judge/pairs.md, key KEY_do_not_give_to_judge.json) + all comp
  sheets -> work/attic4/judge/VERDICTS.md.
- BLIND JUDGE done (23:40, work/attic4/judge/VERDICTS.md; key work/attic4/judge/KEY_do_not_give_to_judge.json). Lip A/B: agrees with
  our picks on B1 C3 E1 J4L (D3 tie, B2 alt does not cover the shot -> keep); prefers the OTHER take on G4 (asrc1s2) and G1
  (asrc1s1) -> swapping; G5: judge preferred asrc5s1 but its own reading puts that mouth opening 9 f late for the v4 Yes -> lead keeps
  a1s2 (its comp got SHIP, "visibly thinks"). No smear, no mouth outside a face, no fringe anywhere. Comps: SHIP A4 C5a E6 G5 L3 B1;
  RE-DO F3b (dark scribble hairs, frozen "o", no fingers) and E3 (no sword-hand); notes D2d (bow ambiguous), E1 (girl's eyes shut,
  fixed smile), G3 (frozen), D9 books pop f32-37, J4 arm ownership f58-96, B2 hand ghost in the dissolve f79.
  Actions: G swaps G4/G1 (no spend); EF re-takes F3b (2 Kling, +$2); CD smooths the D9 retime (no spend).
- next: collect those deltas, write DONE + final report., two-pass where needed, comps; lead judges picks + blind judge.
- (old) collect every finished relay job now (lead), relaunch/continue the groups when the limit resets, then judge picks.
## CHECKPOINT 2026-11-18 (setup done, groups launched)
- done: read REVISION_V4/V3, TEAMS_V4, SETS_V4 + log + v3 set-check SUMMARY, LIPSYNC_V4 + log, LOG_v3_attic, CANON §00,
  HANDOFF, BOOK/WORLD hand-over notes. Backed up v3 comps/scripts. Built the team tooling:
  `work/attic4/kf4.py` (gpt-image-2 keyframes: v4 guide line + master plate + v3 sheets + E6 hair ref, scene JSON per key),
  `work/attic4/vid4.py` (Kling v4 acted takes, per-key job tables), `work/attic4/ls4.py` (LIPSYNC's tools/gen/lipsync_v4.py with
  ATTIC tags at4ls_, --stem (G5: vocals_v4.wav), --lead pre-roll, --mute, J4L/G5 aliases; pick records in work/attic4/notes/),
  `work/attic4/strips.py` (16-frame sheets, 2x zoom strips, last frame), `shots/_attic4.py` (Seg4 = v4 keyframes + picks
  media/comp/attic4/picks.json). Hair ref `work/attic4/refs/lj_hair_E6.jpg` (three crops of v3 E6: keyframe + take frames).
  Common brief `work/attic4/BRIEF_COMMON.md`, group direction `work/attic4/GROUPS.md`.
- in progress: 5 Sonnet group agents (notes work/attic4/notes/<GROUP>.md): OPEN (A1 A3a A4 L2b L3 J4L, $24), B (B1 B2 C2, $30),
  CD (C3 C5a D2d D3 D9, $38), EF (E1 E3 E6-bg F3b, $32), G (G1 G3 G4 G5, $42). Reserve $4.
- decisions:
  1. Singing shots: keyframe from the full v4 guide (set check), then a 16:9 crop of it so the singer's face meets LIPSYNC's
     ~240 px condition; the crop goes to Seedance; the comp shows the crop. A crop of a passing frame is consistent by
     construction; the take's last frame is checked by pasting it back into the full keyframe.
  2. G margins: G1 as v3 (closes at the end into G2), G3 keeps the strip, G4 OPENS to full frame over ~10 frames (books in frame,
     face size for the recipe, dark side for 听话 calligraphy), G5 full frame. For the lead: this changes BOOK's band device
     after G3.
  3. G5 = 78 f (3515-3592) per REVISION_V4 §12; docs/shots.json still says G5 68 f + G6 10 f (lead to update; I do not edit it).
  4. C2 passes the set check: kept unless the top-of-head hair reads wrong (group B checks).
  5. A3b passes: only A3a is re-made.
  6. E6: background replacement on the kept take first, re-shoot only if the matte cannot be clean.
- group agents (resume: relaunch a group with "read work/attic4/BRIEF_COMMON.md, your GROUPS.md section, resume from work/attic4/notes/<GROUP>.md CHECKPOINT").
- pending relay jobs: see each group's notes.
- questions for the lead: (G5 frame count above; G margins above.)
<!--/CKPT-->

## NOTE FROM BED+CAR (J4 split, 2026-11-18 ~21:40)
- Split comp exists: shots/J4.py -> media/comp/J4.mp4 (left = your media/comp/J4_1988.mp4 x 240..720, right = mine; exposure
  auto-matched each render). Re-render after you replace J4_1988.mp4: `$PY -m tools.ink.run shots/J4.py --t0 196.625 --t1
  200.6666666667 --size 960x540 --out media/comp/J4.mp4 --jobs 10 --fresh` (I will also re-run it before I finish).
- Your current file: the girl's arms are fully up at 197.96 (0.9 s early). Mine go up 198.75, fully up ~198.9.
- I am re-taking my half so that both of mine stay facing out with the girl IN THE LAP, centred, arms straight up on the gong and held
  to the end: matching yours (girl centred in Mama's lap) is the point of the split.

## DONE 2026-11-19 00:05
All 22 ATTIC comps exist at 960x540, 24 fps, with exact frame counts and no audio. Notes for each group are in
work/attic4/notes/{OPEN,B,CD,EF,G}.md. The blind judge's verdicts are in work/attic4/judge/VERDICTS.md. No relay jobs are pending and
nothing is committed. Spend: $147.73 of the $170 ceiling, list-price estimate across the at4* and ls4w_<my shots> tags. Project
total is $819.79.

| Shot | Frames | Pick (motion source) | Lips | Set check | State |
|---|---|---|---|---|---|
| A1 | 131 | still kf + typeset sign + title (Kling take rejected: the neon faded) | - | kf PASS | ship |
| A3 | 69 | A3a Kling t2 + v3 A3b | - | kf + last PASS | ship (Mama small in the door) |
| A4 | 70 | Kling t1 | - | kf + last PASS, hands OK | ship |
| B1 | 163 | Seedance at4ls_B1_4 @13.518 | borderline-pass (judge prefers it) | kf + last PASS, arm chain OK | ship; acting weak (no tug or bounce), 2 half-winks |
| B2 | 92 | Seedance at4ls_B2_4 @21.893 + Kling ots t1 + warp onto WORLD's new B3 f0 | pass | kf FAIL on 1 corner pillow outside the crop; ots PASS | ship; hand ghost in the f79 dissolve |
| C2 | 24 | Kling t2 (hair fixed to two ponytails) | - | PASS | ship |
| C3 | 83 | Kling act2 + animate ls4w_C3_a2s2 @45.665 | borderline-pass | kf + last PASS | ship |
| C5a | 57 | Kling first+last t1 | - | kf PASS | ship; no flow tail at the cut |
| D2d | 15 | Kling t3 | - | kf + last PASS | ship-with-note (the bow reads ambiguous) |
| D3 | 84 | animate ls4w_D3_asrc1s1 @62.935 | borderline (face 197 px) | kf PASS | ship-with-note |
| D9 | 80 | one Kling take D9_0>D9a>D9b>D9c, retime smoothed | - | last PASS | ship (cues within ~1 f) |
| E1 | 86 | animate ls4w_E1_asrc1s1 @84.345 | borderline | kf PASS | ship-with-note (no nose tap or giggle; the girl's eyes are shut) |
| E3 | 166 | animate ls4w_E3_asrc1s1 @91.49 | borderline | kf PASS | NOT the director's cast (open palms); the lead decides |
| E6 | 66 | v3 take, background replaced (BiRefNet + plate), v3 zoom | - (v3) | PASS | ship |
| F3b | 12 | Kling t1 at ~3x | - | kf + last PASS | RE-DO per the judge; the re-take submit was denied by the permission check |
| G1 | 144 | animate ls4w_G1_asrc1s1 @118.59, pasted into the kf | borderline-pass | last PASS | ship |
| G3 | 165 | Kling t2 | - | kf + last PASS, hand clean | ship (nearly static) |
| G4 | 125 | animate ls4w_G4_asrc1s2 (pasted), margins open, push in | judge's preferred take | last PASS | ship |
| G5 | 78 | Kling act1 + animate ls4w_G5_a1s2 @146.458, vocals_v4, Mama muted | pass by eye (Yes opens f65-69) | last PASS | ship |
| J4_1988 | 97 | Seedance at4ls_J4L_1 @195.28 | borderline | kf + last PASS | arms up ~197.8 = 0.9 s EARLY |
| L2b | 26 | Kling first+last t2 | - | kf + last PASS | ship (not matched to BED+CAR's L2) |
| L3 | 34 | Kling t1 + L3_off (neon off on f5710) | - | PASS | ship |

<!--CKPT-->
## CHECKPOINT 2026-11-19 00:20 (lead's decisions on the three open items)
1. E3 (do FIRST): cut inside the shot. E3a = line 1 ("Names and faces, I lose a few") from the shipped animate take ls4w_E3_asrc1s1;
   E3b = line 2 ("but a spell I'd remember well") as a NEW ANGLE where her mouth is not readable while she casts: wider
   three-quarter from the light side (v4 LAP_34-type guide; use v4_C3 if no LAP_34 id) or slightly from behind her shoulder, whole
   upper body + both arms in frame; sword-hand drawn back past her ear, other palm pushing out, wrist flourish, chin up, hold a beat,
   then she turns her head up to check if Mama is impressed; Mama laughing above. Face small/turned (log the face height). Kling
   only, >= 3 takes, set check, EVERY-FRAME hand strip (two fingers together the whole time). Cut on the breath between the lines
   (analysis/timing_v4.json). E3 total stays 166 f. Keyframe via Codex first.
2. J4 1988: keep the Seedance take to the end of the sung "song" (timing_v4), then join to the Kling act ls4w_J4L_act1 that hits
   the arms cue, at the closest matching frame (blink/head dip, <= 2-3 f dissolve); every-frame strip of the join; if it pops, keep
   the current take and say so. When final, re-run shots/J4.py (BED+CAR's split).
3. F3b: do NOT re-submit or route around the refusal; it is the director's decision; current F3b stays.
Any further permission refusal: stop and report.
- in progress: E3b agent (Sonnet), notes work/attic4/notes/E3b.md. Cut at 96.000 (frame 2304; breath 95.905-96.18): E3a 72 f, E3b 94 f.
- J4 join: NOT POSSIBLE as specified (lead checked, no spend). timing_v4: "song" is sung 198.12-199.475 (held) and the echo
  "(no song)" 198.74-199.48, so the singing does not end before the cue 198.74-198.833. Worse, the Seedance take already has the arms
  UP from ~197.8, while the Kling act (media/gen/ls4w_J4L_act1_c6824bdebc.mp4, sheet work/attic4/look/J4_act1_sheet.jpg) has them
  DOWN until clip f64 (= song 198.78, up by f72 = 199.1). Any join without an arms pop must be before 197.8, i.e. during "no"
  (197.81), leaving "no song" + the echo (~1.7 s) on Kling's unsynced mouths (big open grins). So: current J4_1988 kept (arms ~0.9 s
  early); lead decides between early arms and re-staging (e.g. a new act + animate from a keyframe with the arms already up, or
  the arms-up moment framed so the faces are not the subject). shots/J4.py not re-run (my half unchanged).
- E3b round 1 (00:55): Codex keyframe media/kf/v4/E3b.jpg (v4_C3 angle, set check PASS, face ~105 px, mouth closed), Kling t1-t3,
  pick t3 put into shots/E3.py (cut at 2304; E3a 72 f + E3b 94 f; media/comp/E3.mp4 166 f). LEAD REJECTS the hand: in the
  every-frame strip (work/review/comp_v4/E3b_hands_every.jpg) the two fingers are together only to ~f91, then spread into a V
  (peace sign) to the end. Round 2 sent: Codex keyframe with the cast already formed (fingers pressed together), small-motion
  Kling x3 (E3b2), every-frame check; else keep and report.
- E3b round 2 DONE (01:40): Codex edit keyframe media/kf/v4/E3b2.jpg (cast already formed; set check PASS); Kling E3b2 t1 (arm
  swings away), t3 (white sword streak) rejected; PICK t2: lead checked the every-frame comp strip work/review/comp_v4/E3b_hands_every.jpg
  (f72-165): the index+middle stay together as one blade in every frame (slight tip separation in a few cells, never a V); mouth
  closed; she looks up to Mama ~f80+ of the take, Mama laughs. Weak: the cast is a held pose (no visible flourish, the pushing palm is
  edge-on), her face (~105 px) is frontal with a closed mouth while "a spell I'd remember well" is sung, and the cut is a jump in
  scale from the tight E3a crop to the wide three-quarter. media/comp/E3.mp4 166 f (E3a 72 + E3b 94, cut 2304). Backups:
  work/attic4/E3_onecut_backup.py (shipped single take), work/attic4/E3_twocut_t3_backup.py (round 1).
<!--/CKPT-->
## DONE 2 (01:45): E3 two-cut delivered; J4 join not possible (see above), current J4_1988 kept; F3b unchanged pending the director.
<!--/CKPT-->

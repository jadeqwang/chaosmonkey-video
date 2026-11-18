# LOG v3 ATTIC team (1988 attic): A1-A4 B1 B2 C2 C3 C5a D2d D3 D9 E1 E3 E5 E6 F3b G1 G3 G4 G5, J4 (1988 half), L2b, L3

## DONE 19:59
ATTIC v3: all 23 shots + the J4 half are rendered at 960x540, 24 fps, exact frame counts (ffprobe), each with a 12-frame sheet in `work/review/comp_v3/<ID>.jpg` that I looked at. Spend $56.19 of $280 (keyframes ~$10, Kling ~$36, lip acts/drivers ~$10). Nothing committed. v2 files are in `media/comp/_v2/`, `shots/_v2/`.

**Per shot (performance now on screen)**
- A1: the blade sign stutters on as a narrow wedge (酒家, not mirrored); she lies awake, a small shape; title block lower left from 0.7 s (Chaos Monkey / 混沌猴 / Jade Wang / seal 猴).
- A2: awake on her back: blinks at the rafters, sighs, toes wriggle, hugs the book, glances for the stairs.
- A3: she pushes up as Mama wipes her hands in the stair door; apron off over her head, on the hook 12.22, towel 12.40, she turns. RARE EARTH typeset on the child's back, tracked.
- A4: she offers the book beaming, pink hands take it, she claps.
- B1 (sings: little Jade, PASS): over Mama's shoulder; hand on Mama's forearm, tug on "tell me", bounce on 孙悟空, watches; Mama turns in and takes her hand.
- B2 (no singing face): scooped giggling into the lap, book opened; over the shoulder, push, the page lands and opens into B3's own first frame (last frame vs B3 f0: 2.5/255).
- C2: both hands shoot up and hover, fingers waggling; shadow cast from the real hand mask, joined.
- C3 (sings: Mama, PASS): laughs the line, one finger lowers the hands, child sneaks them up, grins up.
- C5a: Mama puffs past her ear, hair lifts 53.22, she scrunches and laughs 53.95.
- D2d: very deep bow, ponytail flipping, lands 63.98.
- D3 (no singing face): Mama's three mock-solemn head shakes, child copies looking up, both crack.
- D9: 0.35 s of the pose, climbs the stack (83.24), wobble, stack goes 83.80, Mama lunges, catch 84.35, relief, hand over her mouth hiding the laugh.
- E1 (sings: Mama, PASS): finger circles, taps her nose on "you", she scrunches and giggles.
- E3 (sings: little Jade, PASS): big palms-up shrug on "lose a few", taps her temple on "remember", turns up to Mama.
- E5: holds still, eyes slide to the whisper, shoulders creep up.
- E6: the sideways look, Mama hides a laugh, eyes wide on the rap pickup.
- F3b: puffs the hairs off her palm 112.37, laughs.
- G1 (sings: little Jade, PASS, envelope weak): fingertips on her forehead, worried, looks up to Mama and waits.
- G3 (not singing): hand flat over the banded monkey, pats, shadow touching the hand.
- G4 (sings: Mama, PASS borderline): finger wag, light and teasing, glance down toward the books; the child bites her lip, eyes to the finger, to the books, away.
- G5 (one word, PASS): lip held, eyes down, up and away, up to Mama, holds, a small "Yes" on 148.72, slow blink.
- J4 1988 half (`media/comp/J4_1988.mp4`, mouths acted, not synced): both sing out; arms up 198.74-198.83. Lifted and glazed red to balance (80 vs 89 mean); I re-ran `work/bedcar/do.sh J4`.
- L2b (`L2b.mp4`, frames 5660-5685): Mama draws the quilt to her chin (236.28), bends closer.
- L3 (`L3.mp4`, frames 5686-5719, 34 f): both asleep, books scattered, neon off on f5709.

**Gate results** (all at shift 0, logged in LOG_v3_lipsync): B1 `B1c_take1` shut 1.0 / open 0.88; C3 `C3_take1` no bilabials / open 1.0; E1 `E1_take1` 1.0 / 0.83; E3 `E3_take2` 1.0 / 0.83; G1 `G1_take2` 1.0 / 1.0 but envelope r 0.23; G4 `G4_take3` 1.0 / 0.80 (exactly on the threshold; two earlier takes failed at 0.73); G5 measured on the comp, one word.

**Things you should know**
- E3 and G1: the first transfers put the singing mouth on MAMA (FaceMesh does not see the small child face beside hers, so `--pick` fell to her). Rejected; redone on a 2x crop of the child pasted back (`work/attic3/childcrop.sh`). The gate was measured on the crop, not the full frame. BED+CAR's two-shots may have the same trap.
- B1's first version (side-by-side two-shot) failed the gate (face tracked 80 %); re-shot closer. Mama is only a shoulder until the last second.
- G5 is an acted Kling mouth conformed by hand to the word, not a transfer.
- L2/L2b splice: cut ON 235.833; BED+CAR's L2 ends on frame 5659, my L2b starts on 5660.
- B2 depends on `media/comp/attic3/B3_frame0.png`: re-extract and re-render B2 if BOOK re-renders B3.
- G shots use the shared margin rect/timing but only 40 % of the drain to grey (full drain turned her cheeks blue-grey). Not agreed with BOOK: their G2/G6 drain fully.

**Weak, ranked**
1. G4: lip gate on the threshold; Mama's face is partly cut by the strip in the second half; her glance reads "down-left", the toppled books themselves are not in the strip.
2. D9: a jump inside the climb (run to the stack cut out); aftermath plays about 1.5x.
3. C2: the shadow is of her two hooked hands, not a monkey silhouette; thrown away from the PAINTED window (opposite side from the sidecar light).
4. Continuity: mat/quilt arrangement differs between close and wide setups; the stack still stands in A1, toppled later; C5a's sign is hidden behind Mama's head; A4 and the close two-shots have no window/sign; D3's window is barely in view.
5. B2 part 2 is a still under the warp (no breathing in the over-shoulder); page art on the lap book elsewhere is bare paper (C5a) or seen from behind.
6. J4 half: mouths not synced; red is a glaze rather than deep neon.
7. Not checked: 1920x1080 renders of any shot; ink-coverage budgets; A3's softening smile has 4 frames.


## DONE round 2 20:50
Re-rendered (960x540, exact frames, each looked at): A1 A2 A3 A4 B2 C2 C5a D2d D9 L2b (26 f) L3 (34 f). Spend now $59.49 of $280.
1. **One sign.** `Blade` (`shots/_attic3.py`) is now a single narrow wedge on the painted window in every shot where the
   window is in view: 酒 over 家, constant cinnabar tubes (no blue breathing), wedge about 0.2 of the window width from the
   door end (A1, A3a), about 0.3 from the mats (A2, A4, C5a, D2d, D9, L2b, L3, B2's over-shoulder plate, C2's corner).
   It is placed per shot by `wedge=(u0, u1)` on the painted window, NOT projected from the sidecar: the paintings do not
   put the window where the guides do, and in C5a the true projection is hidden behind Mama's head, so I chose the
   visible, consistent wedge. D3, G-shots, E-shots, B1, J4: window out of frame (D3's is outside the crop).
2. **L2b** is a new shot: keyframe `media/kf/v3/L2m.jpg` painted from BED+CAR's `L2_end.jpg` for camera and placement only;
   Kling take 1. Mama from behind lower left, child's head upper centre-right, hands at the chin on frame 5660, tuck
   236.276, then one hand rests and she looks. Side by side with L2's last frame the screen positions match.
3. **L3** is continuous: keyframe `media/kf/v3/L2w.jpg` (the L2b picture extended outward), Kling take 1, sat in at x1.6
   easing to x1.5: Mama still kneeling, hand on the quilt, wedge on; neon off on f5709 (computed from the lit frame), cold
   glass two frames, then night. `shots/L3.py` no longer uses the A1 wide (`media/kf/v3/L3.jpg`, `L3_off.jpg` unused).
4. **C2**: the shadow is the monkey head in profile from `layout/assets/monkey_silhouette.json`, standing on the wrists
   of the real hands in each frame, facing the egg on the right page.
**Not done:** (5) B2 over-shoulder breathing and the D9 climb jump.
**Still weak / to know:** the scattered books are NOT in L3's frame (they lie further left than the x1.5 crop) though they
are in L2b; in L2b only 家 reads clearly in the wedge; C2's monkey rises above the hands (up-left) rather than strictly on
the side away from the painted window, because the true throw falls under her sleeves and cannot be read; the monkey is
already on the page from frame 3 as the hands arrive; A3b's window is cut by the frame edge so its wedge is half seen.

## CHECKPOINT 20:50 (final, round 2) nothing pending
- No relay jobs, no background processes. `work/attic3/tmp` emptied.

## Shot plan (v3)
| Shot | Setup / keyframes | Motion |
|---|---|---|
| A1 | `A1`, `A1_off` (wide, v3_A1) | code: sign stutter-on as v2, blade sign, title block |
| A2 | `A2` (v3_A2) | Kling: blinks at the rafters, fingers fidget on the quilt; drift in comp |
| A3 | `A3a` (door), `A3b` -> `A3b_end` (hooks) | Kling; apron off 11.68-12.04, on hook 12.220, towel 12.400 |
| A4 | `A4` | Kling: Mama's pink hands take the book she holds up |
| B1 | `B1` (side by side, hand on forearm) | lip little Jade; tug on "tell me", bounce on 孙悟空 |
| B2 | `B2a` -> `LAPF` (scoop into lap), `B2b` (over shoulder) | Kling first+last; push + 2D warp onto B3 frame 0 |
| C2 | `HANDS` -> `C2_end` | Kling first+last; monkey shadow from the hand mask |
| C3 | `C3` | lip Mama; finger lowers the hands, she sneaks them up |
| C5a | `C5a` (profile) | Kling; blow 53.220, scrunch 53.950 |
| D2d | `D2d` | Kling: the bow |
| D3 | `D3` (edit of LAPF, window in view) | Kling: three slow head shakes on the three "no" |
| D9 | `D9_0`, `D9_a`, `D9_b`, `D9_c` | Kling first/middle/last; retimed piecewise to the §11 cues |
| E1 | `E1` | lip Mama; nose tap on "you" 88.47 |
| E3 | `E3` | lip little Jade; shrug on "lose a few", temple on "remember well" |
| E5/E6 | `E5` (child cu), `E6` | Kling |
| F3b | `F3b` | Kling; puff 112.372 |
| G1 | `G1` | lip little Jade; margins |
| G3 | `HANDS` -> `G3_end` | Kling; hand flat over the monkey, shadow from the hand mask; margins |
| G4 | `G4` | lip Mama; the child listens; margins |
| G5 | `G5` (-> `G5_end`) | Kling/lip: up and away, back, hold, "Yes" 148.72, blink; margins |
| J4 | `J4` (edit of LAPF) | sing; arms up on the gong |
| L2b | `L2b` -> `L2b_end` | Kling first+last |
| L3 | `L3`, `L3_off` (edits of A1) | code |

## NOTES FOR OTHER TEAMS
- **BED+CAR: `media/comp/J4_1988.mp4` EXISTS now** (97 f, 960x540; arms start up 198.74, fully up 198.833, held). Run your `do.sh J4`.
  `media/comp/L2b.mp4` (26 f, song frames 5660-5685) starts with Mama's hands at the waist, tucked at the chin on 236.276.
- **BED+CAR, J4:** my half will be `media/comp/J4_1988.mp4`, 960x540, 97 frames (song frames of J4), full LAP_front frame
  (you take the centre 480 px columns, x 240..720, as `v3_J4_split`); red neon. Start pose: both look out, child's hands on
  the top edge of the book; both sing "No cradle, no song"; **both children throw their arms up on the echo hit 198.833**
  (arms start up at 198.74, fully up by 198.833, held to the cut). If you prefer another time, write it in your log.
  The keyframe will be `media/kf/v3/J4.jpg` (for matching your pose).
- **BED+CAR, L2 -> L2b:** the match cut is ON 235.833 (song frame 5660 is my first frame). My first frame = `media/kf/v3/L2b.jpg`
  (guide `attic88/v3_L2b`): Mama kneeling frame left, both hands on the turned quilt edge at the child's WAIST, starting to
  draw it up (hands move from 235.88, tucked at the chin 236.276). So your last frame should have Jade's hands already at
  the chin (tucked 235.780). If you would rather cut mid-pull (hands at the chest in both), say so here and I will re-time.

## LIPSYNC REQUESTS
(none yet: keyframes first)

## Per-shot log

| Shot | Status | Keyframes | Takes (pick) | Performance on screen | Weak |
|---|---|---|---|---|---|
| A1 | done | A1, A1_off | code | sign stutters on as a wedge reading 酒家; she lies awake; title lower left from 0.7 s | wedge lettering pale blue-white (v2 breathing colour) |
| A2 | done | A2 | k4 t1 (t2 similar) | blinks at the rafters, sighs, toes wriggle under the quilt, glances for the stairs | Kling softens the line a little |
| A3 | done | A3a, A3b, A3b_end | A3a t1; A3b t1 | pushes up, Mama wipes her hands in the door; apron off over her head, on the hook 12.22, towel 12.40, turns | the softening smile has only 4 frames |
| A4 | done | A4 | k4 t1 | she offers the book beaming, pink hands take it, she claps and squeezes her eyes shut with joy | no sign in the window |
| B2 | done | B2a, LAPF, B2b | B2a t1; push = code | scooped in giggling, feet kicking; they open the book; over the shoulder and in, onto B3 | part 2 is a still under the warp (no breathing) |
| C2 | done | HANDS, C2_end | t1 (t2 rejected: grew a face) | both hands shoot up and hover, fingers waggling; shadow joined under them | shadow reads as hands, not a monkey |
| C5a | done | C5a | t1 | Mama puffs past her ear, hair lifts 53.22, she scrunches and laughs 53.95 | sign hidden behind Mama's head |
| D2d | done | D2d | t1 | a very deep bow, ponytail flipping over, lands 63.98 | 15 frames |
| D3 | done | D3 | t1 | Mama mock-solemn head shakes, child copies looking up at her, both crack | grade a little dark |
| E5 | done | E5 | t1 | holds still, eyes slide to the whisper, shoulders creep up, smile | - |
| E6 | done | E6 | t1 | the sideways look, Mama hides a laugh in her hand, eyes go wide on the pickup | - |
| F3b | done | F3b | t1 | puffs the hairs off her palm 112.37, laughs | - |
| G3 | done | HANDS, G3_end | t1 | hand goes flat over the banded monkey, pats, head shakes at the frame edge | head shake small in the strip |
| L2b | done | L2b, L2b_end | t1 | Mama draws the quilt to her chin (236.28), bends closer | - |
| L3 | done | L3, L3_off | code | both asleep, books scattered, neon off on f5709 | - |
| D9 | done | D9_0, D9_a, D9_b, D9_c(v2) | D9a t3; D9b t4 (t1/t2 used the unaligned D9_c: the catch jumped framing; t3 has no hidden laugh) | 0.35 s of the pose, scrambles onto the stack (on it 83.24), pose, wobble 83.48, stack goes 83.80, Mama lunges, catch 84.35, relief, hand over her mouth hiding the laugh | a jump inside the climb (the run to the stack is cut out); the aftermath plays 1.5x |
| G5 | done (acted mouth, not transferred) | G5c (crop of alt/G5s_v2) | at3_G5c t1 (t2 turns to profile); `ls_G5` acted takes pending as an alternative | lip held, eyes down; up and away; up to Mama, holds; a small open 'Yes' on 148.72; slow blink 149.2 | mouth timing set by hand on the strip (opens f=148.72); gate not run yet |
| J4 (1988 half) | done | J4 | t2 | both sing out, sway; her arms fly up 198.74-198.83, Mama leans back grinning | mouths acted, not synced (small in the split) |
| C3 | done, sings (Mama), gate PASS | C3 | ls_C3 act2 + transfer (act1: no sneak-up) | Mama laughs the line, one finger lowers the raised hands, the child sneaks them up again and looks up at her | toothy mouth on 'start'; Mama's eyes often lowered |
| E1 | done, sings (Mama), gate PASS | E1 | ls_E1 act1 + transfer | Mama's finger circles, taps her nose on 'you'; she scrunches and giggles | comp a little dark; toppled books at the frame edge |
| B1 | done, sings (little Jade), gate PASS | B1c (v2); first try B1 two-shot | ls_B1c act1 + transfer (two-shot ls_B1: gate FAIL, tracked 80 %; kept as media/comp/attic3/B1_twoshot.mp4) | over Mama's shoulder: hand on her forearm, pats, tugs on 'tell me', pleads head tilted, bounces on 孙悟空, watches; Mama's profile turns in and her hand closes on the small hand; she beams | Mama is only a shoulder until the last second; small mouth on 'you' and 'I' |
| E3 | done, sings (little Jade), gate PASS | E3 | ls_E3 act1 + transfer on the child crop (take2_full); take1 rejected (mouth landed on Mama) | counts on her fingers, big shrug with palms up on 'lose a few', sits up, taps her temple on 'remember', turns up to Mama on 'well'; Mama smiles down | 'well' is sung in profile |
| J4 (1988 half) | re-rendered lifted | J4 | t2 | as above; now as bright as the 2026 half, room glazed cinnabar | red is a glaze, not a deep neon |
| B2 | re-rendered | - | - | the warp lands by 25.1, then the flat page opens into B3's own first frame (mountain steps forward) over 8 frames; last frame vs B3 f0 mean abs diff 2.5/255 | uses media/comp/attic3/B3_frame0.png: re-extract if B3 is re-rendered |
| G1 | done, sings (little Jade), gate PASS (envelope weak) | G1 | ls_G1 act1 + transfer on the child crop (take2_full); take1 rejected (mouth on Mama) | fingertips on her forehead, worried, looks up to Mama, waits | gold/cold sung in profile |
| G4 | done, sings (Mama), gate PASS borderline (open 0.80) | G4c | ls_G4 act1 + transfer rgain 1.4 (take3); act2 takes failed at 0.73 | teasing finger wag, glance down-left; child lip bite, eyes to finger, books, away | Mama partly cut by the strip late; books not in frame |

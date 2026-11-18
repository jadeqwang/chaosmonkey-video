# LOG v3 BED+CAR team (2026 bedroom and car), preview_v3

Shots: car F1, F3a, F4a, F6b; bedroom I1, I3a, I4 (+ morph), J1, J4 (2026 half + the split comp), K1, K2a, L1, L2.
Scratch: `work/bedcar/`. Keyframes + prompts: `media/kf/v3/` (generator `work/bedcar/kfgen.py`). v2 backups:
`media/comp/_v2/<ID>.mp4`, `shots/_v2/<ID>.py` (+ `_rooms26.py`, `_bed_grade.py`, `_car_grade.py`). Sheets:
`work/review/comp_v3/<ID>.jpg`. Spend tags: `v3bc_*`.

## DONE round 3 (from QA_PREVIEW_V3)
- **F2 plate for STAGE: READY.** `media/kf/v3/F2.jpg` (keyframe, gpt-image-2, prompt beside it) and
  `media/kf/v3/F2_plate.mp4` (1920x1080, 24 fps, 53 frames = song frames 2612-2664; Kling v4 take t2
  `media/gen/v3bc_F2_t2_1cf2b1ccc6.mp4`, source frames 5-57, raw, no grade). The daughter sits at frame right in her
  rear-right car seat (same child, seat and dusk as F1/F3a), three-quarter profile, watching a large BLANK dusk-blue side
  pane at frame left: she points, bounces, kicks, points higher, glances once toward the front, laughs; amber streetlight on
  the sill and the seat. The glass stays blank and the door does not move in the take.
  - The painted pane does not match the layout's `rear_right` quad, so I wrote `media/kf/v3/F2_pane.json` (quad TL TR BR BL
    = (184,0) (1089,109) (1005,633) (80,775), + `poly`), which `shots/F2.py` already reads. I test-rendered one still of
    STAGE's script (to a scratch file, their comp untouched): it picks up the plate and the screen lands on the glass.
  - **STAGE, two things the still showed:** (1) her pointing hand and forearm are in front of the pane in every frame and
    the screen currently paints over them: use `media/kf/v3/F2_fg_matte.mp4` (same 53 frames, white = hand/arm over the
    glass) to keep the hand on top; (2) thin slivers of blue glass stay visible along the top and right edges of the screen
    (the glass top runs out of frame; the right edge is curved): grow the pane a few px or use the `poly`.
  - Rejected: t1 (a faint pink smudge appears on the glass at her fingertip).
- **J1 and the last 10 frames of I4:** the page is now J2's own painting. `shots/_j1v3.py` renders BOOK's J2 scene just
  before its downbeat (no seal, no threads; `shots/J2.py` imported, not edited) and lays it on the page with 過, the
  character J2's threads start from, just above the pressed fingertip; 過 lights pale gold on the press (189.620); the camera
  closes to x3 with 過 low and right of centre, as in J2's first frame. Checked side by side: J1's last frame and J2's
  first show the same blue-green peak and summit stone at nearly the same size and place; the lit character is where
  J2's threads leave from. If BOOK changes J2's START camera or carving, `work/bedcar/do.sh J1` and `do.sh I4` follow it
  (the art is cached on `shots/J2.py`). v2's grey carved page is no longer used.
- **L2:** unchanged (ATTIC re-shoots L2b to it; nothing asked in their log).
- **Spend:** $34.5 of $220 (F2 keyframe $0.26, two 3 s Kling takes $1.41). No relay jobs pending.

## DONE round 2 (lead's three fixes), 20:00 machine clock
- **F6b:** `media/comp/F6b.mp4` is now the 33-frame take, song frames 2882-2914 (starts 120.083). **New splice: F6a must end at
  song frame 2882** (13 frames shorter). The old 20-frame file is `media/comp/F6b_20f.mp4`; `F6b_long.mp4` is identical to the new F6b.
- **I3a, I4:** re-rendered on LIPSYNC's gated `I3a_take2.mp4` / `I4_take3.mp4` (both PASS in LOG_v3_lipsync), 1:1 from their t0;
  sheets looked at: I3a's mouth works through "You think I'd ask" while she tips her head back; I4's mouth is at rest until
  "You're", moderate opening on "able", close to her sheet. `I4_lips.mp4` = I4.mp4; `I4_acted.mp4` is the untransferred mouth.
- **I1: PASS.** The sung words now play on a close lap two-shot (x1.5 on the same take: Jade's face about 135 px high at 540p),
  widening to the full lap framing 178.80-179.20 as she squeezes on "twin"; push into the I2 page unchanged. Lips: transfer on
  a native 1280x720 crop of the take (x420 y60), gentle setting (`--rgain 0.55 --shape 0.2 --mask mouth --delay 2 --pick 640,270`)
  -> `media/gen/v3/lipsync/I1_take1.mp4`, pasted back into the take (`picks.json` I1.lips.paste; `shots/_bedcar3.py` Take).
  Gate at shift 0: viseme +1 f (trusted, 3 bilabials), shut 1.0, open 1.0, verdict PASS with my eye note (strip only, not watched
  in motion); logged in LOG_v3_lipsync. "twin" is sung through the acted squeeze grin (teeth).
- **F1: the transfer did NOT pass, so F1.mp4 plays the rap on her body.** Transfer on a 1280x720 crop (x60 y30, face 190 px),
  default strength, two takes (`F1_take1`, `F1_take2` = delay 2, rgain 1.3). At shift 0 both bilabials (蹦, 没) are shut on
  time and vowels are open (0.9 / 1.0), but the envelope reads the take 8.8 frames early (r 0.65) -> FAIL; the gate
  auto-passes the same take at +9 frames. I read that as ambiguity (periodic rap, only 2 bilabials, and the acted take's own
  jaw is small in the first half and wide in the second), not a real lag, and did not shift it. Logged as FAIL.
  - `media/comp/F1.mp4` (delivered): her face is above the frame; chopping hands at the top edge, kicking feet, harness, her
    seat, the edge of the empty second seat at frame right. Rule-compliant, but clearly the weaker picture: the hands are
    half out of frame and there is no performance face.
  - `media/comp/F1_face.mp4` (alternative, same 43 frames): tighter on her with the face in frame (about 127 px at 540p), the
    edge of the empty seat at right, hands chopping apart, grin, with the transferred lips. This is the shot I would use
    if LIPSYNC or the lead accepts the strip (`work/review/lipsync_gate/F1_take2_strip.jpg`, `F1_take2_check.mp4`).
    Swap = copy the file; or `F1_FACE=1 work/bedcar/do.sh F1`.
- **Spend:** $32.85 of $220 (two p-video-avatar drivers added: `ls_F1_drive-5b00d8996c`, `ls_I1_drive-81fd35fde6`). No relay jobs pending.

## DONE 16:15 (machine clock) — final report
All 13 shots delivered: `media/comp/<ID>.mp4` 960x540, 24 fps, exact frame counts (F1 43, F3a 29, F4a 38, F6b 20, I1 72,
I3a 40, I4 67, J1 26, J4 97, K1 164, K2a 38, L1 107, L2 63), scripts `shots/<ID>.py` on `shots/_bedcar3.py` (+ `_j1v3.py`),
sheets `work/review/comp_v3/<ID>.jpg`, every sheet looked at. v2 in `media/comp/_v2/`, `shots/_v2/`. Extras:
`media/comp/F6b_long.mp4` (33 f from 120.083), `media/comp/I4_acted.mp4` (I4 with the acted Kling mouth, no lip transfer),
`media/comp/I4_lips.mp4` (= I4.mp4). Per-shot table: "Shots (v3)" below.
- **Sings on camera, gated:** I4 (Jade, "You're able"): LIPSYNC's transfer `media/gen/v3/lipsync/I4_take1.mp4`; gate FAIL at
  shift 0 (envelope lag -118 ms, vowels open 67 %), AUTO-PASS at shift +3 frames (shut 1.0, open 1.0), so I4.mp4 places it
  at 187.725. On the sheet the mouth is shut to 188.63, opens on "You're" 188.71, closes 188.9-189.0, opens on "able" 189.08.
  Eye check done on stills and the strip only (not watched in motion); `--eye` / `--log` left to LIPSYNC.
- **Sings on camera, NOT gated yet:** I3a (daughter): LIPSYNC's driver has landed (`media/gen/ls_I3a_drive_41e0f2274b.mp4`)
  but `media/gen/v3/lipsync/I3a_take1.mp4` did not exist when I stopped. I3a.mp4 shows the acted Kling mouth. When the file
  exists: `work/bedcar/do.sh I3a 182.95833333333334 184.625`, then gate it; if it needs a shift, set `lips.t0` in `work/bedcar/picks.json`.
- **Mouths that move but are not synced and cannot be gated (faces under the size limit):** F1 (rap, 115 px), I1 (Jade, 90 px),
  J4 (both pairs), F4a (the daughter in the mirror). K1 is a whisper with Jade's mouth hidden; K2a plays on the page.
- **L2 splice:** my last frame is song frame 5659 (hands at the chin, tucked on 235.780); ATTIC's L2b starts on 5660 = 235.833.
- **Morph:** Kling v4 first+last from `I4_mama.jpg` to `I4_jade.jpg` (same framing): one face throughout, no double exposure;
  Mama holds 4 frames, then 10 frames of flow (hair lengthens, glasses reshape, blouse becomes the jacket, red turns white).
- **Weak, ranked:** (1) F6b at 20 frames: catch / open / laugh is rushed, use `F6b_long` if F6a can give 13 frames; (2) I3a
  lips pending; (3) F1 and I1 unsynced mouths in wides; (4) I4: the transferred mouth shows more teeth than her sheet and
  opens wide on "able" (compare `I4_acted.mp4`); (5) I1's push into the I2 page is only 16 frames; (6) J4: ATTIC's half is
  much darker than mine; (7) J1's lit character is ~20 px at 540p; (8) K1: BOOK's page comp has a streaked right edge in
  its first ~40 frames (told BOOK); (9) the morph's attic background has bed-like shapes; (10) no over-shoulder push into I3b.
- **Spend:** $32.6 of $220 (22 gpt-image-2 keyframes $5.5; 27 Kling v4 1080p takes $27.1). No relay jobs pending.

## NOTES FOR OTHER TEAMS (contracts; newest first)
- **ATTIC, J4:** agreed: arms up from 198.74, fully up by 198.833, held to the cut. My half uses `media/kf/v3/J4_2026.jpg`
  (both look out, child's hands on the top edge of the book). I take x 240..720 of your `media/comp/J4_1988.mp4`.
- **ATTIC, L2 -> L2b:** agreed: my last frame (song frame 5659) has Jade's hands at the child's chin, quilt tucked
  (`media/kf/v3/L2_end.jpg`); pull 235.33-235.78. Your first frame (5660) = hands at the waist starting to pull.
- **STAGE, F2 (round 3): plate READY**, see `## DONE round 3`: `media/kf/v3/F2.jpg`, `F2_plate.mp4`, `F2_pane.json`, `F2_fg_matte.mp4`.
- **STAGE, F2 (earlier):** the daughter and the car are set by `media/kf/v3/F1.jpg` / `F3a.jpg` (grey high-backed seat, brown curls,
  strawberry dress); crop without her for style: `media/kf/v3/style/car_right.jpg`.
- **BOOK, K1 page comp:** `shots/K1page.py` starts at camera (2050, 1150, z 0.82): the view runs ~150 art px past the right
  edge of the 3072 px page, so the first ~40 frames have a streaked (replicated) right border (see `work/review/comp_v3/K1.jpg`
  f89, f104). My K1.mp4 renders your module unchanged, so a fix on your side needs only `work/bedcar/do.sh K1` (and
  `$PY -m tools.ink.run shots/K1page.py --still 207.2083333 --size 1920x1080 --out work/bedcar/ends/K1page_f0.png` first).
- **BOOK, hand-overs:** my pushes land exactly on your frame 0 of I2 (`pages/I2_full.mp4`), K1 (`K1page`), K2b (`K2b.mp4`),
  using stills of your first frames in `work/bedcar/ends/`. If you change a first frame, re-render that still the same way and
  re-run my shot (I1, K1, K2a). I did not make a push into I3b (I3a keeps its 40 frames for the look up).
- **BOOK:** my over-shoulder plate is `media/kf/v3/ots.jpg` (blank spread); I warp your flat page art onto its spread quad
  and finish on your frame 0 (spread fills frame as `bed26/v3_LAP_ots_push_end.json`).

## LIPSYNC REQUESTS
Start frames are 3072x1728 gpt-image-2 (1920 copies in `media/kf/v3/_1920/`). Kling acted takes of the same frames are being
made by me as the acting reference / fallback (`media/gen/v3bc_<SHOT>_t<k>_*.mp4`); please keep the beats below.
| shot | keyframe | line | song window | acting to keep |
|---|---|---|---|---|
| I4 (Jade) | `media/kf/v3/I4_jade.jpg` (face ~55% of frame height, front, lips just parted) | "You're able." (only these two words are on her face; "Wouldn't you?" is under the morph) | words 188.67-189.93; on screen 187.60-189.375; suggest audio 188.17+3 s | holds the child's eyes, small sure smile, leans in at ~188.2, tiny nod on "able"; likeness is the priority: no softening of the face |
| I3a (daughter) | `media/kf/v3/I3a.jpg` (face ~45% of frame height, front) | "You think I'd ask" (then I3b takes over at 184.625) | words 182.95-184.39; shot 182.958-184.625; suggest audio 182.45+3 s | eyes on the page for "You think", tips head back to look up at her mother on "I'd ask" (end pose `I3a_end.jpg`), hesitant, really asking |
| F1 (daughter) | `media/kf/v3/F1.jpg` | 石头里蹦出来 没有童年 | 107.04-108.645 | wide shot (two car seats must show): her face is ~115 px high at 720p, under the 150 px gate limit. Will play as an acted rap (hands, chin, feet) unless you can pass it; tell me if you want a tighter start frame |
| I1 (Jade) | `media/kf/v3/I1.jpg` | "(Mischievous) baby, Monkey's twin" | 177.37-179.43 | wide lap two-shot, face ~90 px at 720p: not gateable. Plays on the squeeze and the child's wriggle |
**LIPSYNC, final maps , please conform with THESE (the I4 map changed after your first conform):**
- I4: act = `media/gen/v3bc_I4_t2_4b1a803f59.mp4`, map `187.6:0.55,189.4:2.35` (speed 1), `--t0 187.6`. Jade is on screen
  187.600-189.375 only (the morph is before, the J1 finger after). Output expected at `media/gen/v3/lipsync/I4_take1.mp4`.
- I3a: act = `media/gen/v3bc_I3a_t1_f941599ca5.mp4`, map `182.9583:0.3,183.9:1.25,184.625:2.3`, `--t0 182.9583`.
  Output expected at `media/gen/v3/lipsync/I3a_take1.mp4`.
My comps pick these files up automatically when they exist (`work/bedcar/picks.json` key `lips`; `shots/_bedcar3.py` Take plays
them 1:1 from t0). If you write them elsewhere, edit the `lips.clip` path in picks.json and re-run `work/bedcar/do.sh I4` /
`work/bedcar/do.sh I3a 182.95833333333334 184.625`. Until then the comps show the acted Kling mouths (not gated).
**I4 result:** your `I4_take1.mp4` (16:08) gates FAIL at shift 0 and AUTO-PASS at shift +3 f; my comp places it at 187.725 (`picks.json` I4.lips.t0). Please confirm or log the eye verdict.
K1, K2a, J4, F4a: not requested (K1 is a whisper with the mouth hidden; K2a is the page; J4/F4a faces are small).

## Shots (v3)
| shot | frames | status | take (Kling v4 1080p) | what is on screen | weak |
|---|---|---|---|---|---|
| F1 | 43 | done | F1 t1 (t2 rejected: palms together) | back seat, two child seats, hers at frame left, the other empty; she raps at the front seat: hands chop APART, chin leads, feet up, grin; brown hair | mouth is acted, not synced (face 115 px at 720p: under the gate limit) |
| F3a | 29 | done | F3a t1, first+last | squints at the pinched hair, lays it on her palm, breath, PUFF starting on 112.146, hair in the air at the cut | 1.5-1.9x speed to fit 1.2 s |
| F4a | 38 | done | F4a t1 (0.1-1.7 s) | mirror: Jade's eyes find her and smile; the daughter small at the far end pointing at the mirror; empty seat between | one blink at f13; the daughter's mouth is tiny (plays as voice) |
| F6b | 33 (round 2; song frames 2882-2914) | done | F6b t2, first+last | a curled hair (code) flies in to her fist; she opens the hand: empty; laughs up toward the mirror | 20 frames is tight: the open-hand beat is 5 frames. `F6b_long.mp4` (from 120.083) reads properly if F6a can give 13 frames. The hair's arrival is a drawn squiggle |
| I1 | 72 | done | I1 t2, first+last; ots t1 | out of the white page; Jade reads like a dare, the daughter looks up at her; squeeze on "twin"; wriggle and laugh; from 179.542 over the shoulder and into the I2 page, landing on BOOK's `pages/I2_full.mp4` frame 0 | Jade's mouth acted, not synced (face 90 px); the push into the page is 16 frames |
| I3a | 40 | done (lips pending) | I3a t1, first+last | HESITANT: eyes down on the page, a blink, then tips her head back to look up at her mother on "I'd ask", brows up, really asking | lip transfer pending; no ots push into I3b (kept all 40 frames for the look) |
| I4 | 67 | done (lips transferred, placed +3 f) | morph t1 (first+last Mama->Jade), I4 t2, J1 t1 | Mama 1988 (4 frames) flows into Jade over 0.6 s as ONE face (hair lengthens, glasses reshape, red turns white); Jade holds her daughter's eyes, leans in, "You're able", small nod; 189.375 cut to the page: the fingertip hovers and presses on 189.620 | transferred mouth shows more teeth than her sheet; the morph's attic background has bed-like shapes for 4 frames; the 1980s attic and bedroom cross-melt behind her |
| J1 | 26 | done | J1 t1, first+last | fingertip pressed on the carved character, which is lit; camera closes on it | the character is ~20 px at 540p; page art is v2's carved page (`pages/J1_page*.png`), no 3.2 threads here (they start in BOOK's J2) |
| J4 | 97 | done (with ATTIC's `J4_1988.mp4`) | J4 t2 | split: 1988 red left / 2026 white right, strip of paper between; my pair sings out at us, the daughter throws both arms up on 198.833, Jade grins | mouths acted, not synced (small faces); the attic half is much darker than mine |
| K1 | 164 | done | K1 t1; ots t1; BOOK `shots/K1page.py` | whisper: Jade's mouth in the curls, the daughter's eyes slide to her and she nods before the question ends, grin; over the shoulder into the K1 page; then BOOK's page comp (rope from the sleeper to the gate) | BOOK's page comp shows a streaked right edge in its first ~40 frames (their camera starts past the art's edge at x 2050, z 0.82): told BOOK |
| K2a | 38 | done | ots t1 | over the shoulder: the daughter leans over the Ten Kings page, hand on it; push into the page landing on `K2b.mp4` frame 0 | her face is not seen (line plays on the page) |
| L1 | 107 | done | L1 t1 | asleep in Jade's lap, mouth open, arm flung over Jade's arm; Jade glances at the closed book, breathes out, lays her cheek on the curls; locked frame, 3 % push | quiet by design |
| L2 | 63 | done | L2 t1, first+last | Jade kneels, smooths the fold, pulls the quilt up 235.33-235.78, tucked at the chin on the last frame | the pull is 2.8x speed to hit the cue |

Splice frames: I3a ends at song frame 4431 (I3b); F3a ends at 2694 (F3b); F4a ends at 2744 (F4b); K2a ends at 5091 (K2b);
**L2's last frame is song frame 5659; ATTIC's L2b starts on 5660 (235.833)**: mine ends tucked at the chin, theirs starts at the waist.
Jacket lettering (REVISION §12): in my shots the back is seen only in L2, where her hair covers the area under the circle,
and the sleeve patch is not in any frame; nothing to typeset. The chest dot stays blank.

## Working log
- start: read REVISION_V3, LAYOUT_V3, CANON 00, HANDOFF Acting, briefs, bake-off, predecessors' logs. v2 comps/scripts backed up.

## LEAD 2026-11-17 evening: F1 decision
`media/comp/F1.mp4` is now the FACE version (was `F1_face.mp4`); the no-face fallback is kept as `media/comp/F1_body.mp4`.
Reason: on `work/review/lipsync_gate/F1_take2_strip.jpg` both bilabials (蹦, 没) are shut on time and every vowel frame is
open; the transfer is placed by construction (driver audio offset 0); the envelope lag is not trustworthy on a 9-syllable
periodic rap. Accepted by the lead's eye on the strip; to be confirmed in motion by Jade.

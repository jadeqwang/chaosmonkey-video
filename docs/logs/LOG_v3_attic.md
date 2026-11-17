# LOG v3 ATTIC team (1988 attic): A1-A4 B1 B2 C2 C3 C5a D2d D3 D9 E1 E3 E5 E6 F3b G1 G3 G4 G5, J4 (1988 half), L2b, L3

## CHECKPOINT 2026-11-17 (1) reading done, keyframe wave 1 running
- **Done:** read REVISION_V3, LAYOUT_V3, CANON §00, HANDOFF Acting, briefs, bake-off, predecessors' logs and `shots/_rooms88.py`.
  Plan per shot is in "Shot plan" below. Keyframe generator written: `work/attic3/kf.py` (every prompt in it; each image
  gets its `.txt` beside it). Word onsets for my lines: `work/attic3/words.txt`. Scratch: `work/attic3/` (/tmp is full).
- **In progress:** wave 1 keyframes (gpt-image-2 high, sync calls, no relay): `media/kf/v3/alt/{A1,A2,D9_a,LAPF}_v1.jpg`.
  They set the room; picks get copied to `media/kf/v3/<KEY>.jpg` with `kf.py --pick KEY vN`.
- **Next:** look at wave 1, write `work/attic3/roomref.json` (people-free crops as room refs for the wides), run wave 2
  (`kf.py A3a A3b A4 B1 B2b HANDS C3 C5a E1 E3 E5 E6 F3b G1 G4 G5 L2b`), then the edits (end frames: `A1_off L3 L3_off
  B2a D3 J4 A3b_end C2_end G3_end D9_0 D9_b D9_c D2d L2b_end G5_end`), then Kling v4 takes (specs
  `media/gen/specs/at3_<shot>_<model>_t<k>.json`, outputs `media/gen/at3_*.mp4`), then comps on a v3 wrapper of `_rooms88.py`.
- **Pending relay jobs:** none yet.
- **Decisions:** (1) the blade sign is drawn entirely in code (keyframes paint dusty red glass, no sign); (2) singing/acting
  two-shots use the CANON proof framing (close front two-shot, book seen from behind so no page art is needed), not the wider
  LAP_front, so faces are big enough for acting and the lip gate; LAP_front only for D3, J4, B2a; (3) lap two-shots that share
  a camera are EDITS of one base frame (`LAPF`) so the room cannot change; D9's poses are edits of `D9_a`; (4) hand shadows
  (C2, G3) are computed from the real hand mask of each frame shifted by the sidecar offset, so shadow and hand always join;
  (5) L2b occupies song frames 5660.. (after the 235.833 cut), the L3 wide follows it; proposed split below.
- **Open questions for the lead:** shots.json has L2 = 233.208-235.833 and L3 = 235.833-238.333, so "L2b after the match cut
  at 235.833" lies inside L3's frames. I will deliver `L2b.mp4` = frames 5660-5685 (26 f, blanket from 235.88, tucked 236.276,
  hold) and `L3.mp4` = 5686-5719 (34 f, neon off on f5709), plus a joined 60-frame `L3_full.mp4`. Say if you want another split.

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

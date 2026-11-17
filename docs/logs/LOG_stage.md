# Stage team log (D1, D2 first three bows, D6, D7, D8, J3, J4)

Budget $60 hard. Tools: `tools/stage/` (frames, batch submit). Frames for first+last generation: `media/gen/stage/frames/`
(canon singles keyed and laid on one blank sheet), prompts `media/gen/stage/prompts/`.

## Generation
| batch | clips | est | status |
|---|---|---|---|
| 1 | D1, D6, D7, D8, J3 x (kling-v4 1080p FL, seedance-2.0 1080p FL), 5 s | $15.13 | all 10 back in ~11 min |

Picks (sheets `media/gen/stage/sheets/`): D6 **kling4** (clean R->L tumbling pass, crouch landing, rises into 亮相; sd20
hops around the sheet); D7 **sd20** (full dry-brush rings round him, real 舞花; kling gives arcs, fewer rings); D8 **kling4**
(staff planted, jumps up it, perches; sd20's staff appears under him); J3 **kling4** (overhead spin, sweeps, leap, one
big final dry-brush sweep into the thrust = the cross-cut stroke). D1: neither clip used (see D1 row): kling's throw is
smoke in water; sd20's throw is real wet ink but its flight takes 1.2 s and the splat is a fifth of the sheet, while D1
starts 6 ms before the gong. -> Final D1 is a HYBRID (lead's note: sd20 has the realest bleed): sd20's own wet
throw is frame 1408, its splat + gathering is placed on the gong and played 3x on twos, inside a procedural splash
(same impact point) that floods the sheet and dries to the stain that D2 keeps. `STAGE_D1=procedural` gives the pure
procedural version.

Staff tracking: `track_point(mode='staff')` locks onto his legs in every one of these clips (thin legs + plumes), so
the persistent 飞白 strokes are keypointed from the figure (`ring_path`, `sweep_to_tip` in tools/stage/stage.py):
the ring rides his chest, the final J3 sweep lands exactly on the staff tip of the thrust frame.

## Shots
| shot | status | sources | QA | weak |
|---|---|---|---|---|
| D2 | done | canon singles 01 (hold) -> 02/03/04 hard re-poses on beats 61.321, 62.205, 63.090 (every 2nd grid beat from "bowed"); three 才 in a column under D1's 倉, one inking (decay .72); D1's stain kept; 2-frame jolt + small shake per bow | 80 f OK; cov 26 / 27; last 0.6 s (63.817-64.417) static (max px diff 6 = codec) | room team: their 4th bow + 仓 at beat 63.980; the 才 seals' paste reads thin |
| J4 | done | heads cut from canon sheets (`tools/stage/heads.py`; Jade/Mama mouths transplanted from the same sheet), monochrome ink x 1.30/.86/.56/.34; hard mouth swaps on No 196.615, cradle 196.83, no 197.81, song 198.12, (no) 198.74, (song) 199.38, end 199.48; 亮相 = common -8° tilt on perc 198.613, mouths frozen 8 f; faint re-pressed 倉 (paste .42) on the daughter at 198.74; aged paper | 97 f OK; cov 35 / 36 (budget 40) | 'aged' paper is heavy/brown with tide lines; Mama's closed mouth reads a little wry |
| D1 | done | HYBRID: sd20 FL clip (blank -> 01) throw on f1408, impact on gong 58.673 (f1409), gathering 3x on twos, set on beat 59.126; procedural splash flood + stain under it; 倉 strike + shake on the gong; "Born fully formed" + italic echo (59.595/60.02/60.46); rubbing flip 2 f at 59.595 | 58 f OK; cov 21/25 (qa low on splash, by eye ~45 %) | the sd20 figure and D2's canon figure differ slightly at the cut |
| D6 | done | kling4 FL clip (14 -> 01), 2.6x on twos + layer drift R->L (~1000 px), small against the corner mountain (B_master, stone painted out); lands 亮相 on kick 75.025 (clip f100), freeze 8 f, misregister 2 f, small 倉; clip tail 1x | 70 f OK; cov 10/11 (35) | figure is small (~290 px at 1080); no plume/staff trails here |
| D7 | done | sd20 FL clip (09 -> 12): flower 76.417-77.919 on twos; HARD re-pose (jump inside the clip) on kick 77.919; thrust lands 亮相 on snare 78.808 + 倉; persistent 飞白 = two keypointed rings (ensō) + model's own fading rings | 69 f OK; cov 10/13 (40) | rings are keypointed (not tracked) so they read a little too regular; plume arcs NOT drawn as lasting lines |
| D8 | done | kling4 FL clip (12 -> 08): plant, leap up the staff, perch; 1.8x on twos; freeze on snare 80.806 + 倉; bloom.dissolve 81.45-82.45 to bare paper (seal sinks to a ghost) | 77 f OK; cov 3/5 (30) | dissolve leaves a brief outline rim mid-way (reads as ink drying back, may look like a line drawing) |
| J3 | done | kling4 FL clip (11 -> 12) at 1.12 scale over D_heaven_mid (80 % window), slow pull-back 1.10->1.00; pages cut red(neon, new paper)/white(flashlight, aged paper) on 193.459, 194.103, 194.963 (no chops measured in J3: strongest drum hits); 3 keypointed staff strokes, the last sweep 194.70-195.181 crosses the 194.963 cut; 倉 on 195.181, faint re-press on "(warmed)" 195.65; lyric at the bottom | 91 f OK; page coverage unlit 64-72 % (budget 70); lit frames read 80-89 because qa takes the lamp falloff as marks | red page is a strong flat cinnabar; overhead spin ring is clipped by the top edge |

## Notes for other teams
- Room team (D2 4th bow): my D2 holds the 3rd bow cleanly from 63.817; the 4th bow beat is **63.980** (仓 there).
- D8 ends on nearly bare 'new' paper (seed 58) for the attic cut; J3 ends on the aged page, J4 is on 'aged' paper (seed 59).
- Lyrics switch: env `STAGE_LYRICS=0` (or ctx.opts['lyrics'] if the runner grows opts; ctx has no `opts` today).
- Render: `PY tools/stage/render.py <ID>` (exact frame counts from shots.json, --fresh, writes the review sheet).
  All seven scripts render a 1920x1080 still unchanged (checked).

## Spend
Batch 1 only: $15.13 (5 x kling-v4 1080p 5 s $1.175 + 5 x seedance-2.0 1080p 5 s $1.85). No retakes needed.

# LOG v4 SETS (team lead: Claude Opus, launched 2026-11-18)

Scope: REVISION_V4 §1.1, §4. Ceiling $40.

## CHECKPOINT 0 (start)
- done: read REVISION_V4, TEAMS_V4, LAYOUT_V3, layout/README+NOTES, HANDOFF.
- in progress: reading engine code + v3 set files, contact sheets.
- next: plan set rebuild.
- spend: $0.

## CHECKPOINT 1 (plan + first decisions, after reading code and contact sheets)
- done: read engine (core, mannequin, stage, lap, render, main, book, props), attic88 / bed26 / car26 layout+build+shots_v3; viewed preview_v3 contact A B D F G I K L and the v3 label sheets.
- plan:
  1. engine/body.js: v4 jointed mannequin built on the existing pose solver (buildFigure gives P); new geometry from P:
     shoulder girdle (clavicles + deltoids), joint balls, five-finger hands, no fringe; joint-limit + reach report.
     stage() gets an optional builder. v1/v3 outputs untouched.
  2. attic88: v4 props (one textbook stack with states stack/topple/fallen, fixed fallen positions), mats re-oriented.
  3. bed26: new room4 rebuilt to L2. 4. car26: v3 cabin + complete object list.
  5. shots_v4.js per set (ids v4_<SHOT>), sidecar gets `objects` (label -> visible px, bbox, centroid), joints px.
  6. ortho plan/elevation cameras for the bible. 7. master plates (gpt-image-2). 8. tools/review/set_check.py.
- DECISION attic mats: every v3 generated frame (A1, A2, L2b, L3, B1) shows little Jade's mat running ALONG x with the
  pillow at the window gable; the v3 3D model had the mats along z (pillows at the back eaves). The images agree with
  each other and the director approved L3/L2b, so v4 turns the mats: pillows under the window, feet toward the door.
- DECISION one textbook stack (v3 model had two: 7 books by the pillow corner and the D9 stack of 9 at the mat foot).
  At the pillow corner the roof is 1.27 m high, a child on a 0.34 m stack would put her head through it; so the one
  stack stands where D9 needs it: beside the pillow end on the +z side, in front of the window's near jamb.
- DECISION bedroom: L2 is canon. L1 (pillows at left, bunny left), K1 (nightstand left) agree with a lap place on the rug
  against the bed's window-side; I1 (nightstand right), K1 (bunny far right) disagree and lose.
- spend: $0.

## CHECKPOINT 2 (guides rendered for all three sets; bible written)
- done: engine/body.js (jointed mannequin + joint-limit report), stage() builder option, main.js v4 sidecar (objects,
  joints, contacts, ortho views), attic88/v4.js + shots_v4.js (28 setups + 5 bible views), bed26/v4.js (room rebuilt to
  L2) + shots_v4.js (10 setups + 4 views), car26/shots_v4.js (5 setups + 2 views). Renders: media/layout/<set>/v4_*,
  sheets media/layout/_sheets/v4_*.jpg, docs/SETS_V4.md (sections 1-4 final, 5-6 pending).
- verified by looking: label sheets of all three sets; B1 line render (arm chain readable); L2 and L2b line renders overlaid
  on the v3 frames (headboard, bunny, nightstand, Jade's head within ~30-50 px; mats/window match in L2b).
- remaining warnings (accepted, listed in the bible): small reach shortfalls C2/C3/A4/D9b (1-14 %), L1 Jade's left forearm
  grazes her torso, E1 wrist 89 deg.
- next: master plates (gpt-image-2), set_check.py, run it on v3 frames.

READY: attic88  (guides media/layout/attic88/v4_*, sheet media/layout/_sheets/v4_attic88.jpg, bible docs/SETS_V4.md §1, §4)
READY: bed26    (guides media/layout/bed26/v4_*, sheet media/layout/_sheets/v4_bed26.jpg, bible docs/SETS_V4.md §2, §4)
READY: car26    (guides media/layout/car26/v4_*, sheet media/layout/_sheets/v4_car26.jpg, bible docs/SETS_V4.md §3, §4)
(master plates and the checker follow; the room teams can start writing prompts from the guides now)

## CHECKPOINT 3
- done: master-plate views (v4_MASTER_* in each set, empty rooms); tools/gen/sets_master_v4.py; first plates
  attic88_master, attic88_master_door, bed26_master (looked at: placement matches the guides; neon left illegible).
  tools/review/set_check.py written and tried on v3 L2 and I1 (sheet + numeric hints work).
- in progress: plates bed26_master_L2, car26_master (background run, log work/tmp/sets/master_run1.log);
  a Sonnet subagent runs set_check over the v3 room shots (list work/tmp/sets/v3_check_list.tsv) -> work/review/set_check/v3/SUMMARY.md
- spend so far: about $0.72 (3 x gpt-image-2), 2 more pending.

## v3 check (how it was run; reuse for keyframes)
A Sonnet subagent, given work/tmp/sets/v3_check_list.tsv (shot / set / v4 id / video / frames), ran for each frame
`set_check.py --set S --shot ID --video V --at T --out work/review/set_check/v3/ID_T.jpg`, opened the sheet, answered with
the --print-prompt JSON into ID_T.verdict.json, ran `--merge`, and wrote work/review/set_check/v3/SUMMARY.md.
Result: 18 of 39 rows FAIL (list in docs/SETS_V4.md §6). Caveat: the agent named only wrong objects, the rest default to
present. Lead spot-checked B2, I1, L2 sheets: agrees.

## DONE 2026-11-18
- Deliverables: layout/engine/body.js; layout/sets/{attic88,bed26}/v4.js; layout/sets/{attic88,bed26,car26}/shots_v4.js;
  renders media/layout/<set>/v4_*; sheets media/layout/_sheets/v4_*; plates media/kf/v4/_sets/*.jpg;
  tools/review/set_check.py; tools/gen/sets_master_v4.py; layout/sheets_v4.sh, layout/camera_table_v4.py; docs/SETS_V4.md.
- Spend this team: 6 x gpt-image-2 = about $1.43 (project total $506.30 by spend.py).

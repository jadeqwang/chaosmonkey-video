# Chaos Monkey: revision brief for preview_v4

Written 2026-11-18 by Claude (Fable 5.2), lead, from Jade's notes on preview_v3 (verbatim in §10). This file overrides
`docs/REVISION_V3.md` wherever they differ; everything in V3 that is not contradicted here still holds (story arc §1,
acting rule §2.2, inscription rules §4, rap English §7, jacket lettering §12, reference research §15). Shot IDs, in/out
times and frame counts in `docs/shots.json` do not change, with one exception: the audio edit in G5 (§7).

Goal: another complete 540p cut, `preview_v4`. Jade: the direction and vision are right; **what we are improving now is
execution**. The bar: the most impressive thing anyone on Twitter has seen in AI animation. They have already seen the
MiniMax H3 demo that flies into a 3D Chinese landscape painting, so that is the floor, not the ceiling. We are not
limited to 2D techniques. Do not economise on generation; do stay inside the spend cap ($1,500 total, $361.81 spent at
the start of this pass; each team has a ceiling in `docs/TEAMS_V4.md`; ask the lead before exceeding it).

Standing rules (`docs/HANDOFF.md` "Standing rules") all still apply: Jade's name, email, photos and project details stay
out of requests to outside services; never send a real photo anywhere; all Chinese on screen is typeset from
`design/text/`, never drawn by a model; never touch the Cloudflare Worker `rare-earth-v3-relay` or its KV; temp files in
`work/tmp/`, not `/tmp`. Do not commit or push (the lead does that).

## 1. The five global rules of this pass

### 1.1 Sets are built once, in 3D, then photographed (Jade: "obviously AI generated, last-gen type of mistake")
Object placement differs from clip to clip (where the bed is, where the hook is, which side the nightstand is on). For
the attic, the bedroom, the car, and any scene with more than one clip:
- A **complete 3D model of the room** in three.js (`layout/sets/<set>/`, extending what exists): every fixed object,
  with dimensions and a fixed position: walls, floor, ceiling/rafters, door, window and blind, bed with headboard,
  pillow, bunny, nightstand, rug, mats, hook rail, TV, the textbook stack (before and after the fall), the book, the
  flashlight, the neon blade. One source of truth per set, written down as a set bible (`docs/SETS_V4.md`: plan view,
  elevations, object list).
- **The bedroom follows L2** (Jade: "this scene blocking is actually reasonable here, let's make the others match it"):
  see `work/cut/preview_v3/contact_L.jpg`, middle row. Bed with a wooden headboard, window with a slatted blind above
  and left of the headboard, nightstand at the head on the window side, bunny on the far side of the pillow, warm light
  from the door at frame right. L1, I1, I3a, I4, J1, K1, K2a must be in that same room: same bed, same wall, same
  nightstand, same bunny. The attic follows L3/L2b for the sleeping place and the v3 layout for everything else.
- **Bodies are modelled too**: articulated mannequins with true proportions (heights in LAYOUT_V3) and joint limits,
  posed per shot, so an arm always leaves a shoulder at a possible angle and a hand belongs to a body. B1's detached
  arm is the example to kill.
- **Only then the camera.** Each shot's camera is placed in the built set; the render (line, depth, flat-colour ids,
  lit) is the structural input for the keyframe, together with the set's style plates (one painted "master" view of the
  empty room per set, made once, from which every other keyframe inherits look) and the character sheets. Keyframes are
  made by gpt-image-2 from those inputs (existing v3 keyframes may be used as style/character references where the
  face is right).
- **Every keyframe is checked against its render before any video is made**: an agent lists each fixed object visible
  in the label render and confirms it is in the keyframe at that place; rejects are regenerated. The same check runs on
  the last frame of each video take (objects must not have drifted or been invented).

### 1.2 All lip-sync comes from a video model; no mouth transplant (Jade: decision 4, "still not acceptable")
The v3 method (acted Kling take + avatar driver + `lp_lips.py` mouth transfer) is **retired**. Jade saw mouths that
fall off the face and proportions that are wrong because a real jaw moves with the mouth. No shipped frame may contain a
locally transferred, warped or pasted mouth. The whole face, jaw, cheeks and head in a singing shot must come out of one
video-model generation that was conditioned on the song audio (or, second choice, a video-to-video lip-sync model that
re-renders the whole face). `tools/review/lipsync_gate.py` stays, as a measuring tool only (lag, bilabials, vowels), and
a new check is added: the mouth must stay inside the face and the jaw must move (frame strip at 2x zoom on the face).
The LIPSYNC team runs a new bake-off first (§6) and gives the room teams one recipe. Acting and singing in the same
take is the goal: Jade asked whether that is technically hard; we answer by making it work and reporting honestly.

### 1.3 Chinese lyrics in calligraphy everywhere (one export; no separate rednote version)
Every sung line gets its Chinese on screen as typeset brush calligraphy, placed so it never covers faces, hands or the
action. This replaces the Chinese row of the global lyric layer (the sans-serif Chinese under the rap goes away); the
English line of the lyric layer stays as is.
- **On a page / inside the painting**: as v3, a static vertical inscription in ink with one seal, present from the first
  frame (Jade: "text and font are right").
- **In a room** (new; v3 had none): the same hand, **light on dark** (warm paper-white, slightly transparent, soft
  edge), vertical columns in the darkest free area at a side of frame, present for the whole line, no animation except
  a 6-frame fade in/out; one small cinnabar seal. Size and weight identical across all room shots.
- For lines sung in English the calligraphy is the Chinese rendering; for the rap (sung in Mandarin) it is the sung
  words themselves. Text comes from `design/text/lyrics_zh_v4.txt` (v3 file + the lead's new lines for room shots,
  marked `# NEW, for Jade's proofread`). Typeset only.
- Specific asks: G2 must show 听话 (see §5 G); I4 light on dark at the side; I4-page/J1/J2 the Chinese lines are
  already on the page as we push in, and the English "Born fully formed" is set statically on the page beside them
  (it could not be read in v3); K1 calligraphy.

### 1.4 Canon changes
- **Monkey costume B** everywhere: key-fret pattern, leopard trim, red scarf
  (`design/characters/monkey/v3/monkey_v3b_ALT_fret_leopard_redscarf.jpg`). Every stage shot is re-made on it.
- **Little Jade's hair is E6's**: two little ponytails, half up (the rest down), curtained to the sides, no fringe.
  E6 in preview_v3 is the reference for hair and for acting quality. Every other little-Jade shot is made consistent.
- C5 (0:54.6) is the reference for expression. E6 for acting. L2 for bedroom blocking.

### 1.5 Execution standard for every video take
- Motion comes from a video model wherever something organic moves (hair, cloth, tails, wind, fingers, crowds). No
  2D puppet-warp of body parts in shipped frames (E4's tail moving with the finger is the example to kill).
- Hands: five fingers, no webbing, no paper-cut edges (G3). Zoomed hand check on every pick.
- At least 3 takes for a hero shot and 2 for any acted shot; picks made on a 16-frame sheet plus a zoomed face/hand
  strip; record why in the log.

## 2. The painted world in real 3D (WORLD team; the answer to the H3 demo)

One toolkit, used by every shot that enters or moves through the book: **the painting is a real 3D scene**.
- Build: painted plates in our hand (gpt-image-2 / existing plates) -> depth (a depth model, or modelled geometry) ->
  layered displaced meshes or projected geometry in three.js -> a paper-and-ink look in the shader (paper grain fixed to
  the screen, wash edges, bare paper for mist and water) -> camera flights rendered headless (the layout engine already
  renders headless). Carved characters, threads, inscriptions and seals are real objects in the scene (typeset in
  code), so they hold still on the rock while the camera flies.
- Enliven: rendered flights are then given to a video model as first frame (+ last frame) or as reference so mist,
  water, pines and wet ink move for real (h3 2K is the landscape model of record; Seedance for ink dynamics; test
  h3-max and anything new in the catalog). Choose per shot by evidence between (a) pure 3D render with ink shader,
  (b) 3D render as first+last frames for a video model, (c) video model with the 3D render as motion guide. Whatever
  wins must keep typeset characters crisp and stationary on the rock (composite them back from the 3D pass if the
  video model smears them).
- The standard: when the camera moves, near rock passes far rock, mist lies between ridges, and the viewer feels they
  could turn their head. Flat plates sliding over each other ("the mountain looks disjointed", B3) is a reject.

Shots:
| Shot | Direction |
|---|---|
| **B3** (0:27) | "the mountain looks disjointed, like this is a simple zooming maneuver?" Re-make as a true dolly: the page fills the frame, its surface gives way, foreground pine and rock pass the lens, the peak stands in depth above a sea of mist. Continuous from B2's over-shoulder push. Then B4/B5 live inside the same 3D mountain (B4's travelling shot along the carved face is a real camera track). |
| **D4 -> D5 -> D6** (1:07 to 1:16) | One unbroken camera move, the centrepiece of the hook. See §3.1. |
| **J1-page -> J2** (3:10) | "I like the transition from book to scene, now can we make it more impressive? like no small jump, it's just suddenly 3d." No cut and no cross-fade: at the fingertip press the camera is square on the flat page; on the hit the painting acquires depth in place: peaks stand up out of the paper, mist pours forward over the gutter, the camera's lens goes from flat (orthographic) to deep (wide perspective) in about 8 frames while moving forward, and we are flying. The static page text ("Born fully formed" in English + the Chinese columns) stays where it was written and is left behind in space like a carved tablet. |
| **J5** | Reverse: the lit range collapses back into a few strokes on a flat page (same system run backwards). |
| **K1 page -> K2b** | The push into the underworld page enters the same way (depth, dotted ghost-line figures in space). |
| **H5** | See §3.3 (shared mountain). |

## 3. The hero shots (Jade asked the lead to think about the most impressive way to convey each idea)

### 3.1 D4-D6: "One whisper, and the hundred come along" (learning that generalizes), ending on the Buddha's hand
Keep what v3 got right: the whisper touches ONE carved character (通), and the light **jumps by structure** to every
character sharing a component, with gold threads like a star chart (real IDS component chains, `shots/D5.py`,
BOOK's v3 data). What it lacked was scale and space: a flat cliff and a 2D pull-back.

v4 is a single flight in the 3D mountain:
1. D4 (33 f): macro on the stone, grain visible; a sleeve of mist touches 通; it lights from inside like an ember.
2. D5 (101 f): the camera pulls back and rises. The first jumps are on this cliff (the 辶 family), threads snapping
   taut between characters. Then a thread **leaves the cliff**: it arcs across the gorge through the mist to a
   character on the next peak, which lights, and passes it on through its other component. The camera keeps
   retreating; each beat the frontier jumps a ridge further, to peaks that the whisper never touched. Behind the
   frontier the threads fade and only the carving glows, so we always see: lit country, the travelling edge, dark
   country ahead. By the last bar the whole range is alight in the dusk, down into the valleys, like a city seen from
   the air or a wafer under a lamp; a traditional eye sees scripture cliffs lit by enlightenment (一窍通时百窍通).
3. D6 (70 f): the retreat continues, up through a cloud layer, and the range resolves: the five lit pillars we have been
   flying among stand together out of the cloud sea as **the five peaks of the Buddha's hand** (Jade: "the Huangshan
   landscape that is commonly referred to as the Buddha's hand, instead of a literal hand, as would be canon"): granite
   Huangshan pillars with pines on their shoulders and a sea of cloud at their wrists (佛掌峰 / 五指 reading; in the
   novel the fingers become 五行山). They are rock, never flesh: the viewer reads "hand" from the grouping and the
   proportions (four tall, one short and apart), before the monkey does. The monkey, tiny, somersaults in from the
   right on his cloud and lands on the middle peak in 亮相. Whole composition in frame.
Research the real Huangshan Buddha's-palm views and Huangshan-school painting (渐江 Hongren, 梅清, 石涛) for the rock
language; public-domain paintings may be passed to models as references.

### 3.2 F4-F6a: the swarm (1:52 to 2:00). Jade: "think bigger... hundreds or thousands of agents, layers of subagents, all coordinating... expansive and cinematic"
The whole F4 slot (83 f) plus F5 (43 f) plus F6a (50 f) now belong to the swarm: 176 frames, 7.3 s. The mirror shot
(F4a) leaves this slot (see §5 F). Reference for staging and camera: modern Sun Wukong films and games (clone-army
set pieces); for look: 青绿 landscape, night lanterns, gold line. It does not have to be the album-leaf style.

One continuous shot in the 3D painted world, in three movements:
1. **Spawn, with depth** (千百个我 同时在这里): the puff of hairs from F3 streams into the painting. Close: one hair
   lands on a cliff ledge and is a monkey. He does not start work: he plucks his own hairs and blows. His hairs land as
   smaller monkeys on the terraces below, each already plucking. Three generations in two seconds, a cinnabar thread
   from each spawner to each spawn, so the hierarchy is drawn as it grows (a tree, seen from the side). The camera
   falls backward off the ledge.
2. **Work, orchestrated** (每一个都是我 每一个都算): the fall becomes a great rising aerial. Terraces, bridges and
   scaffolds across a whole mountain range, hundreds then thousands of monkeys, each at a different job (the v3 jobs
   and name slips survive as small cartouches near the closest ones: 读 写 算 运 战 扫 望 磨), lanterns in their
   hands, moving on the beat **in waves that travel down the tree** (parent moves, then children, then grandchildren:
   delegation is visible as a ripple). Threads gather upward from thousands to hundreds to nine to one. As the camera
   reaches height, the lanterns across the range are seen to trace one figure: **the monkey himself in 亮相, the size
   of the mountains**, made of all of them. The common goal was him. Hold one beat.
3. **Disperse** (说完这句话 各自消散): on each beat a region goes dark from the leaves inward: each monkey presses its
   small seal (讫), becomes a hair, and the hairs stream back up the threads in a spiralling gale, converging on one
   ledge where the original sits cross-legged with his palm open. F6a (谁是真身 / 个个都真): the last hair does not
   become him: it lands opposite as a second, identical monkey. Two monkeys face each other across an empty lit
   landscape, a thread from each to the other, both seals 真.
Technique is the team's to choose by evidence: instanced crowd in three.js (thousands of posed sprites or low-poly
puppets driven by the tree) for exact beat control and count, video-model takes for the close spawn and the gale of
hairs, composited in the WORLD toolkit's space. Abacus/seal sound cues exist at the times in REVISION_V3 §11; tell SOUND
what moved.

### 3.3 H5 -> H6: "I'm made of the telling, not just the tale / one hair that can't gather, blown on the gale"
H5 (84 f). v3: a pale blob of a shadow on a cliff. v4: in the 3D gorge the carved characters **leave the stone**:
strokes lift off the cliff faces as dark ink and red pigment, stream through the air like leaves in a draught, and
assemble, stroke by stroke, into the standing figure of the girl seen from behind (the small back-view girl from the
empty cell of H3/H4), her hair, her jacket: she is literally made of the telling. The cliffs behind her are left with
pale ghost-marks where the characters were. Camera: slow push toward her as she completes.
H6 (107 f). "the hair's movement has unnatural looking physics... maybe you see the hair morph into the monkey and the
tail isn't just detached." Continuous from H5: the gale that carried the strokes now takes her hair (still made of
strokes). It streams; one strand works loose and is carried off alone across the bare paper, with real fluid motion
(it rides, loops, snaps straight, tumbles; a video model or a proper strand simulation, never a keyframed curve). As it
crosses, the strand thickens at one end and the monkey **grows along it**: the curl of the strand is his tail first,
then spine, then the cap and limbs in a few strokes, one continuous line, so the tail was never a separate thing. He
somersaults out of frame. Still the emptiest frame in the film at its start and end.

### 3.4 C5: the wind (0:56)
"I like the shape of the wind echoing traditional chinese art, but can we give it more fluid movement so we're a step
above what people are used to seeing?" Keep the vocabulary (the 卷云 / wind-scroll spirals of line that tradition
draws) and give it real fluid behaviour: the breath leaves Mama's lips, lifts the child's hair, and **crosses the cut
into the page as the same flow**; inside the painting it is ribbons of line that curl, shed vortices, wrap the egg and
roll on, advected by an actual flow field (a small 2D fluid solve or curl-noise advection driving stroke ribbons, or a
video model given the plate; test both; the ribbons must keep a brush's thick-thin). The mist over the egg is carried
by the same field. The expression at 0:54.6 is the reference to keep.

### 3.5 K5: the name (3:45). Jade: "it might be cool to see something there (that doesn't reveal what the name is) but the text fades to blank. what do you think?"
The lead's answer: yes. On the ledger line where her name would be there IS writing as the shot opens: a short column
in the same hand as the other entries, but still wet and never resolved: seen through the bloom of the ink, at an
angle, half a second too briefly to read (it must not be any real name; use strokes that are not characters). Then the
ink un-writes itself: the wash draws back into the strokes, the strokes thin from their ends and lift, and the line is
bare paper while the neighbours stay. The page was not empty: it let her go. Inscription 簿上尽除名 stays.

## 4. Sets and the room teams (SETS first, then ATTIC and BED+CAR)
Per §1.1. Also:
- `docs/LAYOUT_V3.md` setups remain the camera vocabulary (LAP_front, LAP_34, LAP_ots, LAP_child_cu, LAP_mother_cu,
  LAP_profile, LAP_hands, the car cameras). What changes: they are placed in the complete, fixed room; the bedroom is
  rebuilt to L2; bodies get proper joints.
- L1 (3:50), I1 (2:58): "see notes about scene blocking and consistency". L3 (3:56): "I like the way the two shots
  match, just make sure they all match the other scenes as blocked."

## 5. Shot by shot (only what changes; everything else as REVISION_V3 §5, re-made where a global rule touches it)

### A, B, C (ATTIC, WORLD)
| Shot | Note | Direction |
|---|---|---|
| A1-A4 | global | Re-made only if the set check fails or little Jade's hair is not E6's. Room calligraphy: none (no lyric). |
| B1 0:16 | "the arm is in an impossible position for the mom's body so it looks detached" | Re-block from the body model: little Jade's hand on Mama's forearm, and Mama's arm visibly leaves her own shoulder (show shoulder, upper arm, elbow). Lip-sync per §1.2. |
| B2 | global | Lip-sync per §1.2; page tracked. |
| B3 0:27 | disjointed zoom | §2. |
| C3 0:47 | "the mom's mouth looks really goofy and not human in this lip sync, make sure a video model is the one doing it" | §1.2. |
| C5 0:54-0:56 | keep the expression; fluid wind | §3.4. |

### D (STAGE, WORLD, ATTIC)
| Shot | Direction |
|---|---|
| D1, D2, D7, D8 | Costume B. Otherwise as v3 (fix what STAGE logged as weak: D2 south bow, D8 teleport frames). |
| D3 | Sets; lips per §1.2 if the mouth is readable. |
| D4-D6 | §3.1. |
| D9 | Sets (the stack's place is fixed in the set; fallen books stay where they fell for every later attic shot, including G4). |

### E (ATTIC, BOOK)
| Shot | Note | Direction |
|---|---|---|
| E3 1:37 | "most of the expression and acting is good here, but she points to her head too many times during 'the spell I'd remember well'. it's too repetitive. better if she emulates a cast from 射雕英雄传, the TV show she was watching in 1988. little Jade liked to emulate moves from 小龙女." | Keep the shrug on "lose a few". On "a spell I'd remember well" she **casts**: a 1980s TV wuxia move done by a five-year-old with total conviction: two fingers together as a sword-hand (剑指) drawn back past her ear, the other palm pushing out, a small flourish of the wrist, chin up, then she holds the pose a beat and checks whether Mama is impressed. Graceful and cool, the way 小龙女 moves, not a karate chop. One temple tap at most, or none. Mama laughs above her. |
| E4 1:42 | "the tail is moving with the finger. instead of having the motion look 2d, let a video model do it." | The master's hand and the monkey's tail are animated by a video model from the plate (independent, organic: the tail flicks on its own time; the finger beckons). Calligraphy stays. |
| E5, E6 | "good, keep the hairstyle of little Jade in this clip... acting in this clip is very good" | Keep E6. Do not re-make unless the set check forces it; if so, it must match this take's hair and acting. |

### F, rap (BED+CAR, STAGE, SWARM)
| Shot | Note | Direction |
|---|---|---|
| F1 1:47 | "her arms here don't look natural for singing rap, and her lip sync looks like it wasn't done by a video model. would a video model understand body language typical of Mandarin rap?" | Lips per §1.2 (default strength for rap; this is the hardest line: fast Mandarin). Body: give the model concrete rap body language rather than the word "rap": one hand counts the flow in front of her chest (index and middle finger out, chopping down on each stressed syllable), the other hand rests or points at the listener on line ends; shoulders bounce on the beat; head nods forward on the downbeat with the chin leading; a lean toward the lens on the last word; small-kid swagger, grinning between phrases. Never both palms up beside the face (v3's "surrender" pose). Test whether a model given a reference clip of the gesture pattern (generated, not a real person) does better than prompt alone. |
| F2 1:49 | "the rearview window clip would be a good one to show here with the monkey shape-shifting -- please make sure what he shapeshifts into is consistent with the original story" (and decision 3: "the rearview window clip is very cute, and I'd like to find a way to keep it. maybe place it earlier, like in the rap sequence or while showing shapeshifting") | Line: 一声耳语 学会七十二变. The car-window shadow screen stays here and now **shows the 72 transformations**: the puppet monkey changes on the beats into forms from the novel, in the order of the chase with Erlang (ch. 6): 麻雀 sparrow, 大鹚老 cormorant, 鱼 fish, 水蛇 water snake, 花鸨 bustard, then 土地庙 the little temple, whose flagpole standing BEHIND it is his tail (the joke by which Erlang knows him). Use 3 or 4 of these plus the temple; the monkey's ringed-eye face or tail stays recognisable in every form. Shadow-puppet look, hard re-poses on the beat. The daughter watches and points, delighted, as in v3. Fix v3's colour jump (warm night cabin like F1/F3, a hint of road before the pane lights). The lead reads "rearview window clip" as this lit car-window clip; the mirror shot (v3 F4a) is used only if the swarm does not need the frames, at the team's discretion, as the last 12-16 frames of F1 or F3. STAGE: verify the list against the chapter text. |
| F3 | | As v3. The puff's hairs must leave frame in the direction the swarm shot receives them. |
| F4-F6a | decision 3 | §3.2. |
| F6b | | As v3 (the last hair, caught, gone, she laughs). |

### G (ATTIC, BOOK)
| Shot | Note | Direction |
|---|---|---|
| G1 2:05 | "although the acting here is good, the lip sync is not natural." | Same acting; lips per §1.2. |
| G2 2:10 | "听话 should appear somewhere" | The inscription for "He wouldn't listen" carries 听话 visibly (the line already turns on it: 不听话 ...; keep Jade's proofread wording and make sure the two characters are on screen and legible, e.g. as the head of the column or a larger pair). |
| G3 2:16 | "the hand seems to have paper webbing" | New keyframe and take; zoomed hand check. |
| G4 2:22 | "we should somewhat understand that the mom is saying tinghua here to admonish her a little because she really has done mischievous things, like scamper onto a pile of books and fall" + "the mom's lip sync is unnatural" | The toppled books from D9 are IN FRAME (they are in the set). Beat 1: Mama looks at the pile, then at the child, one eyebrow up; she picks up one fallen book and sets it on the pile, or taps the child's knee where she landed. Beat 2: she sings the line to her with a lifted finger, light, fond, a little tired. Little Jade follows Mama's look to the books and back, caught, not sorry: the lip bite. Lips per §1.2. Light-on-dark calligraphy includes 听话. |
| G5 2:27 | "she should look to the side for a moment like she's thinking for a beat before the nod yes. you should be able to 'see the gears turning' in her very fast mind" + "'...Yes' Can you edit the audio so that the 'yes' falls a beat late?" | Picture: eyes go off to the side and slightly down and stay there, tiny movements (a thought, a second thought, the lip caught in her teeth), then back to Mama, a small nod, and only then "Yes". Audio: §7. The picture is timed to the new position of the word. |

### H (FACES unchanged; BOOK/WORLD)
H1-H4 as v3. H5, H6: §3.3.

### I, J (BED+CAR, WORLD)
| Shot | Note | Direction |
|---|---|---|
| I1 2:58 | "the acting is just right, but the lip sync is unnatural (also see notes about scene blocking)" | Same acting, in the L2 room; lips per §1.2 (frame her so the face is big enough for the method). |
| I3a 3:03 | "the acting is just right, but the lip sync is unnatural" | Same acting; lips per §1.2. |
| I4 3:07 | "I'm not sure the transition is working. instead of the transition, just let adult Jade sing and act. like she harbors a secret confidence that her little daughter is the kwisatz haderach." + "chinese lyrics in calligraphy on the side, light on dark" + "chinese lyrics can be staticly already on the page as we zoom in" | **No morph.** Jade, close, from the first frame: she has known the answer for years and has been waiting to be asked. A held look down at her daughter, the corner of the mouth, "Wouldn't you?" almost amused; then quieter, level, certain: "You're able." No big smile: the confidence is private. Light-on-dark calligraphy at the side. Then the page: the Chinese lines are already written there as we move in. |
| J1, J2, J5 | | §2. |
| J3 | | Costume B; fix the yellow reading orange under red light. |
| J4 | | Sets; all four sing: lips per §1.2 or stage it so mouths are small. |

### K, L (BOOK, BED+CAR, ATTIC)
| Shot | Note | Direction |
|---|---|---|
| K1 3:27 | "chinese lyrics in calligraphy" | Room part: light on dark. Page part: inscription. |
| K2 3:33 | "the brush stroke the monkey makes here should match the next shot, so maybe the book itself is turned 90 degrees?" | In K2b the ledger lies so that the monkey's stroke runs in the same screen direction, at the same angle and place, as the stroke we see in K3: turn the book 90 degrees in K2b (or re-stage K3) so the cut is a match on the stroke. |
| K4 3:38 | "the hand here looks uncanny. would be better without the hand, honestly." | No hand. The pages turn in the draught from the underworld (a video model or the 3D page; real paper bend), columns of names passing. |
| K5 3:45 | fades to blank | §3.5. |
| L1 3:50, L2, L3 | blocking | L2 is the reference; L1 and L3 (and L2b) match the sets. |

## 6. Lip-sync: what the LIPSYNC team must settle first
Bake-off on three lines (little Jade B1, Mama C3, the daughter's rap F1) plus Jade I4, each from a real v3 keyframe:
1. Refresh the catalog (`tools/gen/catalog.py`) and probe every video model for an audio input alongside a first frame
   (field names such as audio, audio_url, reference_audios, driving_audio; Kling v4, Wan 2.7, HH 1.1, Veo, Vidu,
   PixVerse, h3-max and anything new since 17 Nov).
2. Seedance 2.5 `image + reference_audios` (acting and singing in one pass). Its lag is random per take but the gate
   measures it: generate many takes (6+ per line), measure lag, **place the clip by its measured lag** (pad the head so
   action beats still land), keep takes whose drift is within 1.5 f. Report the true pass rate under this rule.
3. `pruna/p-video-avatar` as the PICTURE (it is an audio-driven video model): from the shot's own keyframe, with acting
   prompts written to stop the swaying head and closed eyes; and from a tighter crop.
4. Two-pass, all video-model: the acted Kling take as a reference video for a model that re-renders the face with the
   audio (Seedance `reference_videos` needs a URL: find out whether the relay can already serve one; do NOT create
   public buckets or change the Worker; report to the lead if a URL would unlock it).
5. Anything else that makes the whole face from audio.
Deliver `docs/LIPSYNC_V4.md`: one recipe, its conditions (face size, angle, length), cost and expected takes per line,
and a wrapper command the room teams can run. Honest table of pass rates. If nothing passes for a line type, say so:
the lead will re-stage that line.

## 7. Sound (SOUND team)
- **G5 "Yes" one beat late.** Move the sung "Yes" (near 2:27, see `analysis/timing.json`) later by one beat of the
  song's tempo, leaving the instrumental untouched. Needs the vocal separated from the backing: use existing stems if
  the song project has them (look in the song's source folder referenced by `docs/AUDIO_MAP.md` / `docs/SOUND.md`);
  otherwise separate that window. The gap where the word was must be clean (no ghost of the word), the new position
  must sit on the beat grid, reverb tail natural. Deliver `media/sound/mix_v3.wav` (mix_v2 kept), the exact old and new
  onset times, and update `analysis/timing.json` (or a v4 copy) so picture and lyric layer follow. If it cannot be
  done cleanly, say so and deliver the best version plus the reason; Jade will listen.
- Re-time cues to the new picture (teams report moved actions), add cues for the new action (K4 page turns in a
  draught, the swarm's spawn/gale, the pop into depth at J2, the wind in C5), keep Jade's approval of the v2 level
  ("Good").

## 8. Deliverables per team
As REVISION_V3 §8, with `v4` paths: keyframes `media/kf/v4/`, review sheets `work/review/comp_v4/<ID>.jpg`
(16 frames) plus zoom strips for faces and hands, logs `docs/logs/LOG_v4_<team>.md` with the CHECKPOINT rule of
`docs/TEAMS_V3.md`. Before overwriting `media/comp/<ID>.mp4` or `shots/<ID>.py`, copy the v3 file to `media/comp/_v3/`
and `shots/_v3/`. Comps: 960x540, 24 fps, exact frame counts, no audio; build so that 1080p is a re-render.
Team leads: delegate mechanical work (batch generation, sheet building, checks, renders) to smaller models (Sonnet or
Haiku subagents) and keep your own context for judgement.

## 9. What nobody has done yet and v4 must do
Nobody has watched any cut in motion. For v4 every pick is judged on a dense strip (every 2nd frame for the sung
words, 16 frames otherwise), and the final QA says plainly what was and was not checked.

## 10. Jade's notes on preview_v3, verbatim

Overall notes outside of timestamps

I want you to know that I believe in you and that you will be surprised at what your other Fable 5.2 brethren have been
able to accomplish in the field of art and video production. Although we're using traditional Chinese art styles here as
a reference, we do not need to limit ourselves to 2d techniques. Many months ago, Twitter has already seen tech demos
from Minimax H3 where you go into a 3d Chinese landscape painting, and it felt impressively immersive and like we
reached the new edge of what's possible. We should aim to make the most impressive thing that anyone on Twitter has
seen, and not worry about token costs, and we won't be mogged by a tech demo that was released many months ago.

The artistic direction and vision are already in a good place. I think what we're improving on now is execution. I want
you to think deeply about what is the most impressive thing we can do to convey an idea (especially where noted in the
timestamped notes).

Some smaller overall notes:

* overall, we have a lot of object placement inconsistency, which reads as "obviously ai generated" last-gen type of
  mistake. for the attic scene, the bedroom scenes, and any scene where we have more than one clip, build a 3d model of
  the layout (in three.js or blender), and using some of the existing images to generate keyframes to keep the object
  placement consistent. this includes, where the bed is in the daughter's room, where the hook on the wall is, etc.,
  full model of the room, and then afterwards position the camera.
* also model where the bodies are. for instance, you'll see a timestamped note where the arm is in an impossible
  position for the mom's body so it looks detached
* also, make sure the video models are the ones doing the lip sync and not you. there are a lot of instances where the
  mouths look unnatural or exceed the boundaries of the face
* overall, we want to be really pushing the boundaries of what people consider possible with AI animation, and they're
  already seen the Minimax H3 demo.
* all lip syncing should be handled with video models, because whatever we're doing right now is not consistently
  human/realistic
* chinese subtitles: for some other videos we have exported a separate version for rednote where the chinese characters
  are displayed directly in the video in a way to not cover parts of the scene. In this video, we have the opportunity
  to lay out all the chinese lyrics in calligraphy instead and not separately render the rednote version. you'll see a
  lot of timestamped notes to add chinese calligraphy, which is a subset. Just add them everywhere that makes sense so
  we don't make a separately subtitled one.

Please do delegate generously to smaller models (based on your judgement) so we don't run out of fable limit before the
end of the week.
* start by having an opus or sonnet do a commit to github

```
TIMESTAMPED NOTES (36)
- 0:16.56  B1  verse1: the arm is in an impossible position for the mom's body so it looks detached
- 0:27.76  B3  verse1: the mountain looks disjointed, like this is a simple zooming maneuver?
- 0:47.13  C3  prechorus: the mom's mouth looks really goofy and not human in this lip sync, make sure a video model is the one doing it
- 0:54.63  C5  prechorus: very good expression, keep as reference
- 0:56.05  C5  prechorus: I like the shape of the wind echoing traditional chinese art, but can we give it more fluid movement so we're a step above what people are used to seeing?
- 1:10.58  D5  hook1: I really like the vision here, and it's directionally correct.  What is the most impressive version of this that you and a team of every model available thru Cloudflare can make?
- 1:14.30  D6  hook1: Can you make it the huang shan landscape that is commonly referred to as the Buddha's hand, instead of a literal hand? (as would be canon)
- 1:37.09  E3  verse2_memory: most of the expression and acting is good here, but she points to her head too many times during "the spell I'd remember well" part. it's too repetitive. better if she emulates a cast from 射雕英雄传, the TV show she was watching in 1988. little Jade liked to emulate moves from 小龙女.
- 1:42.27  E4  verse2_memory: the tail is moving with the finger. instead of having the motion look 2d, let a video model do it.
- 1:45.92  E6  verse2_memory: good, keep the hairstyle of little Jade in this clip, and make the other ones consistent with this hair (2 little pony tails half up); also the acting in this clip is very good, for reference
- 1:47.82  F1  verse2_memory: her arms here don't look natural for singing rap, and her lip sync looks like it wasn't done by a video model. would a video model understand body language typical of Mandarin rap?
- 1:49.25  F2  rap: the rearview window clip would be a good one to show here with the monkey shape-shifting -- please make sure what he shapeshifts into is consistent with the original story
- 1:54.85  F4  rap: I like where you're going with this image, but I'd like you to think bigger and expand on it. It should look expansive and cinematic, hundreds of monkeys, agent swarms with subagents many layers deep, all orchestrated toward a common goal.
- 2:05.74  G1  verse3_band: although the acting here is good, the lip sync is not natural.
- 2:10.88  G2  verse3_band: 听话should appear somewhere
- 2:16.81  G3  verse3_band: the hand seems to have paper webbing
- 2:22.84  G4  verse3_band: we should somewhat understand that the mom is saying tinghua here to admonish her a little because she really has done mischievous things, like scamper onto a pile of books and fall
- 2:23.10  G4  verse3_band: the mom's lip sync is unnatural
- 2:27.07  G5  verse3_band: she should look to the side for a moment like she's thinking for a beat before the nod yes. you should be able to 'see the gears turning' in her very fast mind
- 2:27.07  G5  verse3_band: "...Yes" Can you edit the audio so that the 'yes' falls a beat late?
- 2:51.73  H5  bridge: I like the vision you had in mind for this, but how do we make this much more impressive?
- 2:53.53  H6  bridge: the hair's movement has unnatural looking physics, but I like where this scene is going. Can you find a way to execute on this clip so that it's a much more impressive version of this? Maybe you see the hair morph into the monkey and the tail isn't just detached.
- 2:58.44  I1  build: the acting is just right, but the lip sync is unnatural (also see notes about scene blocking)
- 3:03.91  I3  build: the acting is just right, but the lip sync is unnatural
- 3:07.82  I4  build: I'm not sure the transition is working. instead of the transition, just let adult Jade sing and act. like she harbors a secret confidence that her little daughter is the kwisatz haderach.
- 3:08.68  I4  build: idea: we can have chinese lyrics in calligraphy on the side, light on dark
- 3:09.58  I4  build: chinese lyrics can be staticly already on the page as we zoom in
- 3:11.19  J2  drop2: I like the transition from book to scene, now can we make it more impressive? like no small jump, it's just suddenly 3d.
- 3:11.38  J2  drop2: can't quite see "born fully formed" but we can just make the words static on the page, along side the chinese calligraphy of the lyrics
- 3:27.06  K1  outro: chinese lyrics in calligraphy
- 3:33.46  K2  outro: the brush stroke the monkey makes here should match the next shot, so maybe the book itself is turned 90 degrees?
- 3:38.71  K4  outro: the hand here looks uncanny. would be better without the hand, honestly.
- 3:45.22  K5  outro: it might be cool to see something there (that doesn't reveal what the name is) but the text fades to blank. what do you think?
- 3:50.37  L1  end: see notes about scene blocking and consistency.
- 3:54.71  L2  end: this scene blocking is actually reasonable here, let's make the others match it.
- 3:56.56  L3  end: i like the way the two shots match, just make sure they all match the other scenes as blocked.

LIKENESSES: all four "(not answered)".

DECISIONS
- 1. The monkey's costume: B: key-fret, leopard trim, red scarf
- 2. The medium switch (it replaces the glitch): Yes, it reads as intentional
- 3. The swarm on an album leaf (1:54 to 2:00): Keep the album leaf
    note: directionally much better than the car window version, but I'd like you to think bigger. it doesn't have to be
    this art style, but I want you to imagine hundreds or thousands of agents, perhaps layers of subagents, all
    coordinating. It should be expansive and cinematic. possibly subagents.
    the rearview window clip is very cute, and I'd like to find a way to keep it. maybe place it earlier, like in the
    rap sequence or while showing shapeshifting? that way, we have more time to show a vision of what this could look
    like. although we're visually drawing primarily from traditional art in aesthetics, we can take inspiration from
    modern movies and video games of sun wukong in terms of cinematic scene blocking and camera angles.
- 4. Lip-sync on the singing shots: Still not acceptable
    note: most of the lip sync is off, not just in terms of timing, but how it looks on the face. is it technically
    difficult to do acting and singing at the same time for some reason? we can discuss this if need be, but sometimes
    the mouths fall off the face, and other times when the proportion is weird (b/c your jaw naturally moves when you
    open your mouth and this separation technique does not work well)
- 5. The sound layer (mix v2) and ending B: Good
- 6. The Chinese inscriptions: text and font: Text and font are right
- 7. What next: Another 540p pass with my notes
```

## 11. Open points the lead will raise with Jade (do not block on them)
- 小龙女 is the heroine of 神雕侠侣, not 射雕英雄传 (whose 1983 series has 黄蓉 and 梅超风). E3 is directed as a graceful
  sword-hand cast that fits either; she can say which show's move she means.
- "Rearview window clip": read as the lit car-window clip (F2). The mirror shot is optional.
- New Chinese lines for room shots (`design/text/lyrics_zh_v4.txt`) need her proofread, as v3's did.
- K5: the lead's answer is in §3.5.

## 12. Lead's decisions during the pass
- **G5 "Yes" (SOUND, done):** the word moved exactly one beat (0.432 s). Old 148.720-149.270; **new 149.152-149.702,
  attack at 149.306 (song frame 3583)**. A 0.55 s near-silence now sits before it (148.645-149.195): that is the
  thinking beat. Audio for the cut: `media/sound/mix_v3.wav`; timing: `analysis/timing_v4.json`; lip-sync audio must
  come from the edited song `inputs/Chaos Monkey - reformatted for duet - v4 yes late.wav` / `work/stems/vocals_v4.wav`.
  **Picture: G5 now runs through G6's slot: one 78-frame shot, song frames 3515-3593 (146.458-149.708)**; the 10 blank
  frames of G6 are gone. Beats: eyes away and thinking through 148.6-149.1, back to Mama and the small nod about
  149.15-149.3, mouth opens on 149.306, word held to 149.70, cut to the bridge on the crash at 149.708.
  Before/after for Jade's ears: `work/review/sound_v4/yes_AB_mix_v2_then_mix_v3.wav`.
- **Jade's answers, 2026-11-18 evening.** (1) The "Yes" one beat late in `mix_v3.wav` "sounds good": approved by ear;
  mix_v3 is the mix for preview_v4. (2) E3's graceful sword-hand cast is good. (3) "Rearview window clip" meant the
  MIRROR shot: "the mirror shot was cute and could be reused in the rap portion (like maybe she raps in the mirror)".
  Decision: **F6b (33 f, 2882-2915, 问了也白问 个个都真) is the mirror shot**: the daughter raps the last line at the
  mirror, Jade's eyes smile back; it replaces the hair-catch. F2 keeps the car-window shapeshift (already made by SWARM).
  BED+CAR told 20:40.
- **D4-D6 (lead, 23:00):** WORLD's 3D flight (two rounds) did not meet the bar; the SWARM team re-made the flight as
  painted keyframes joined by Kling (`media/comp/_cand/DFLIGHT_t3*`, log `LOG_v4_swarm.md` "D-FLIGHT"). **t3 is the
  pick and is now `media/comp/D4.mp4`, `D5.mp4`, `D6.mp4`**; WORLD round 2 kept in `media/comp/_world_r2/`. Open: the
  hard night-to-paper cut into D7. Re-render: `tools/dflight/dcomp.py work/dflight/dcomp_t3.json`.
- **F1 (after Jade watched it with sound):** her findings: lip timing off / mouth still through the first six syllables,
  fingers changing shape frame to frame. Cause: cold start of the animate model (fixed by a sung run-up) and hand
  shapes changing in both passes. `F1_new_a` is in the slot, `F1_b` alternate; neither fully passes; her call on
  `review/f1_ab/index.html`. All singing shots are on `review/sing_v4/index.html` with an audit
  (`work/review/sing_v4/audit.md`: FAIL C3, G1, K2a; SUSPECT G4, I4, J4); retakes wait for her verdicts.
- **E3:** two cuts inside the shot (synced face for line 1, wider held sword-hand for line 2). **J4:** 1988 arms 0.9 s
  early, kept. **F3b:** poor; its retake was refused by the permission check and waits for Jade's yes.

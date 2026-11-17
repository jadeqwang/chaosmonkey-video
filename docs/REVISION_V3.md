# Chaos Monkey: revision brief for preview_v3

Written 2026-11-17 by Claude (Fable 5.2), lead, from Jade's notes on preview_v2 (her full notes are at the end of this
file, verbatim). This file overrides `docs/TREATMENT.md`, `docs/shots.yaml`, `docs/HANDOFF.md`, `docs/COMP_BRIEF.md` and
`docs/KEYFRAME_BRIEF.md` wherever they differ. Shot IDs, in/out times and frame counts in `docs/shots.json` do NOT
change (the song is the same), except that the last shot is extended for the longer ending (section 9).

Goal: another complete 540p cut (`preview_v3`), every room shot re-shot with new blocking and real acting. Jade: "all
the acting should be better, more alive, not lifeless / expressionless, reshoot all of it with new prompts if you need
to, don't worry about budget." Spend cap is now $1,500 (`tools/gen/spend.py`); each team has its own ceiling.

Inputs that exist now or are being made (check before you start; if a file is missing, wait or ask the lead):
- Faces accepted by Jade: `design/characters/CANON.md` section "00. v3 canon" and the `*_v3.jpg` sheets. Never pass a
  v1/v2 face sheet, keyframe or frame of the old cut as a reference.
- 3D blocking: `docs/LAYOUT_V3.md`, guides `media/layout/<set>/v3_*`.
- New traditional references: `refs/paintings/MANIFEST_V3.md`, `refs/paintings/v3/`.
- Chinese inscription text: `design/text/lyrics_zh_v3.txt` (lead's draft; typeset from this file only).

## 1. The story under the story (new, from Jade)

Jade as a child is naturally mischievous and a full click smarter than both her parents. She once hid that she
understood a whole language (Shanghainese) so her parents could not surprise her. Mama's parenting is
do-what-you're-told: warm, funny, tired, and its reflex answer to a child who climbs things and falls is "听话, do what
mama says". Jade's own parenting, 38 years later, is a reaction against that: she encourages independence, tells her
daughter to fight the gods and win, and to ask for the seat at the table.

The film shows this as two matched beats, never stated:

| | 1988 | 2026 |
|---|---|---|
| The child takes a risk | D9: little Jade climbs a stack of books to strike the monkey's pose, the stack goes, she falls | I3: the daughter doubts herself: "You think I'd ask for a seat at the table?" (hesitant, not scornful) |
| The mother answers | G4: "Then 听话, or you'll get one to wear / do what mama says": light, teasing, a finger lifted; said because of the fall | I4: "Wouldn't you? You're able.": certain, warm, leaning in |
| The child's reply | G5: "Yes", after a look up and away and back, a small lip bite: she has decided to keep what she thinks to herself | J1: the daughter presses her finger to the page and it lights |

Little Jade is never crushed and Mama is never harsh. The sadness is only visible to someone who sees both columns.

## 2. Rules that changed

1. **Kid in lap, book in front.** Both storytimes: the mother pulls the child into her lap, both face the same way, her
   arms around the child holding the open book in front of them both. The standard way into the book is over the
   shoulder onto the spread, then the camera pushes in until the page is the whole screen. Setups: `LAP_*` in
   `docs/LAYOUT_V3.md`, mirrored between attic and bedroom on purpose.
2. **Acting.** `docs/HANDOFF.md` "Acting" still holds as method (a want and an action, beats in time, eyes lead,
   children act with the whole body, listening is visible), but its shot table is replaced by section 5 here. Every
   video prompt must contain timed beats and at least: where the eyes go and when, one body action, a blink, breathing.
   A take with a frozen or blank face is a reject however good the picture is. Generate at least 2 takes of every
   acted shot and choose by watching a contact sheet of 12+ frames.
3. **Mama is 35, young and attractive, and wears no apron after A3** (she hangs it on a hook by the stair door).
4. **Glitch.** Jade: the visual glitch "reads as actual errors / carelessness rather than intentional". Dropped: block
   mis-registration (offset colour ghosts) and any 1-2 frame flicker. Kept: 亮相 freezes and seal strikes. New device
   for the breakbeat chops, **the medium switch**: on a chop the SAME pose and layout is shown, clean and full-frame,
   as a different traditional medium for a held 3 to 6 frames (never fewer than 3): ink painting -> red paper-cut
   (剪纸, flat cinnabar on paper) -> stone rubbing (拓片, white on black, with the rubbing's paper edge visible) ->
   leather shadow puppet (amber back-light) -> back to ink. Each medium is a finished, deliberate image with crisp
   edges and no offset doubles. At most two switches per bar; always on measured chops. It should look like a print
   shop showing off, not like a signal failing.
5. **Chinese calligraphy on the page.** Wherever a lyric is sung over a book/stage page, its Chinese rendering sits in
   the blank as a static vertical inscription (right-to-left columns, one small red seal), like a 题跋 beside a
   painting: part of the book, present from the first frame of the shot, not animated. Brush-kai or 行楷 font (not seal
   script, not a print face), typeset in code. The English lyric line of the global lyric layer stays (including over
   the carved cliffs). Rooms get no calligraphy.
6. **Lip-sync.** Fewer singing faces, each one QA'd. A singing face ships only if measured lag is within +/-1 frame
   after retiming AND a word-strip check by eye shows the mouth closing on the bilabials and opening on the stressed
   vowels. A softer, slightly 3D look on those shots is acceptable to Jade; wrong sync is not. If a line cannot pass,
   play it on the listener, the book or the hands. List in section 6.
7. **Sound.** The diegetic layer was "too quiet, I barely heard it": raise it clearly. Ending B (last note rings 3 s).

## 3. Ideas Jade asked the lead to think through

### 3.1 Sand that learned to think (B4, B5, C6, H5; the carved mountain)
The joke she is pointing at: we used light to carve runes into ultra-purified sand until the sand started to think. The
novel already says the stone "每受天真地秀，日精月华" (fed on sun essence and moon glow) until it grew a spirit. The
picture must read as that old tale to anyone, and as lithography and training to someone who knows.

- **Light is the carver.** No human carvers on ladders. In B4 the edge of the sunlight crossing the rock is the chisel:
  behind the moving terminator the columns of seal script are freshly cut, ahead of it the stone is blank. Day cuts in
  warm light; at "moonlight" a cold moon-edge crosses the other way and cuts the columns in between, finer. Two
  passes, two layers, interleaved.
- **Sand.** Every cut sheds a thread of bright dust. The dust does not fall: the mist carries it up the cliff as a
  glittering drift toward the summit. By B5 we see where it went: the summit stone is smooth, uncarved, and built of
  that dust, pure and faintly translucent like quartz or jade.
- **Scale.** B4 opens very close (one stroke of one character, chisel-fresh, grains visible), then the travelling
  shot widens until the columns are a texture, and the texture is laid out in rectangular fields of different
  densities separated by straight channels, the way cliff inscriptions and stele forests really are, and the way a
  chip looks from above. Do not add anything that is not stone, cut and light.
- **Soaking up light** (B5): hold on the smooth stone. Inside it, very faint, columns of characters lie like
  inclusions; one point of light after another travels down a column and goes out, as if being read. Slow, few, warm.
  The stone is the only uncarved thing on the mountain and the only thing that contains all of it.
- C6 (pre-hook) and H5 ("made of the telling") reuse this: in C6 the travelling points quicken and run together
  before the split; in H5 the child's shadow on the lit cliff has the same faint columns inside it.
- Inscription for B4/B5 from `lyrics_zh_v3.txt` (日精月华 line).

### 3.2 "One whisper, and the hundred come along" (D4, D5, J5; generalization)
The line is about learning that generalizes: the master whispers one thing and the monkey knows a hundred. The novel's
own phrase is 一窍通时百窍通. Show structure carrying the lesson, not light spreading to neighbours.

- D4: a breath of mist (the whisper; the same sleeve of mist as Mama's breath) touches ONE carved character, 通. It
  lights.
- D5 (the pull-back): the light does not spread outward like a stain. It jumps: every character on the cliff that
  shares a component with the lit one lights next, wherever it is (start with the 辶 of 通: 道 遠 邇 過 ... in the
  carved 千字文), a fine gold thread drawn between them for a few frames like the lines of an old star chart; then
  each newly lit character passes it on through its other component, and so on, on the beats, until a hundred that
  were never touched are lit and the threads have made a constellation across the mountain. Use real component data
  (IDS decomposition of the characters actually carved; choose the chains by hand if needed so every jump is true).
  By the end of the pull-back the whole mountain is lit and the threads fade; only the carving glows.
- J5 completes it: the lit range shrinks to a few strokes in the corner; the inscription 一通百通.
- To a reader of the old tale: enlightenment spreading through scripture. To a modern eye: one example, and the
  pattern fires everywhere it applies.

### 3.3 The agent swarm (F4b, F5, F6a; "千百个我 同时在这里")
A modern person must think "agent swarm" at once; a traditional eye must see 身外身法, the hairs that become monkeys.

- The plucked hairs (F3) land as small monkeys, and they do not copy him: **each takes a different job at once.** One
  reads a scroll, one writes with a brush, one clicks an abacus, one carries peaches, one spars with a staff, one
  sweeps, one keeps watch with a hand shading his eyes, one grinds ink, one stacks books.
- **Layout: a ruled album leaf of cells**, the same ruled grid as the 脸谱 album and the ledger. One worker per cell,
  each with a small vertical name-slip cartouche (榜题, typeset: 读 写 算 运 战 扫 望 磨 ...). The original monkey sits
  in the middle cell, cross-legged, one hand raised, and a hair-thin cinnabar thread runs from him to every cell.
  In the car, the cells are the panes of glass (windscreen, side windows, mirror): keep the shadow-puppet look and the
  hard re-posing on beats from v2, lit by passing streetlights.
- They work in parallel: on every beat ALL cells advance one pose at once (puppet-joint hard cuts).
- F5 "说完这句话 各自消散": one per beat, a worker finishes, presses a small red seal (讫) into its own cell, and
  becomes a hair that flies back along its thread to the centre. The glass empties.
- F6a "谁是真身 / 个个都真": two identical monkeys face each other; both hold a thread to the other.

### 3.4 The monkey in yellow (all stage shots; Jade: "can we try how that looks?")
Redesign the stage monkey as the Peking opera Sun Wukong she remembers: yellow costume with dark pattern, the yellow
cap with pompoms, the red-white-gold monkey face, scarf, banded staff; drawn in our ink-and-colour hand (藤黄 gamboge
wash over ink line, not metallic gold; gold leaf stays reserved for the birth light, the band and the halo). Use the
researcher's costume references. The birth (D1) still arrives as one throw of ink; the yellow floods in as he lands.
Keep the v2 comps of these shots in `media/comp/_v2/` so the dark-ink monkey can be restored if she prefers it.

### 3.5 Traditional episodes on the page
- **D6**: the top of the mountain was cut off; restage the tumbling pass as the somersault across the Buddha's palm
  (the five pillars at the edge of the sky that are fingers). Frame the whole thing; nothing cropped.
- **I2** ("you'd fight the gods and win"): replace the two hand shadows (hands looked deformed) with the page itself:
  the small monkey standing defiant, staff planted, against the host of heaven; then the host scattered. One or two
  beats. The daughter's and Jade's hands may sit at the page edges, natural, not shadow-making.
- **I3b** (the seat at the table): the table of the celestial gods as tradition paints it (Peach Banquet): the gods
  seated in rank, robes and halos in fine line, one seat bare. Still mostly bare paper; one corner.
- **K1/K2b** (the other side): over the shoulder onto the page: the monkey's road to the underworld as the
  tradition shows it, then the hall of the Ten Kings and the ledger.
Use `refs/paintings/MANIFEST_V3.md` for all four. Public-domain paintings may be passed to models as references;
opera stills never.

## 4. Chinese inscriptions
Text: `design/text/lyrics_zh_v3.txt` (draft by the lead for Jade to proofread; where the novel has the line, the novel's
wording is used). Font: a brush kai / 行楷 with full coverage of the text (the BOOK team chooses, downloads under a
free licence into `refs/fonts/`, records the licence in `refs/fonts/FONTS.md`, and makes one helper
`tools/ink/inscription.py` that every team uses: `inscription(ctx, key, box, ...)` -> vertical columns, right to
left, ink with dry-brush texture, one seal). Same size and weight relative to the page in every shot.

## 5. Shot by shot

Teams: ATTIC, BED+CAR, BOOK (mountain, heaven, ledger pages), STAGE (monkey, swarm), FACES (bridge), LIPSYNC, SOUND,
CUT (lead). "Lap" = the LAP setups. Lines in quotes are sung in the shot.

### A, intro (ATTIC)
| Shot | New direction |
|---|---|
| A1 | As v2, colour fine. The neon sign is a blade sign hung perpendicular to the wall outside the window, so from inside it is a steep wedge of red light, not a flat sign (use the placement the lead picks from `v3_neon_options.jpg`). **Song title** set small in one corner like a title slide: "Chaos Monkey" (EB Garamond), the Chinese title 混沌猴 (brush kai, typeset; decided by Jade 2026-11-17: 混沌 is both chaos engineering's 混沌工程 and the novel's first word, 混沌未分天地乱), her name "Jade Wang" smaller beneath (English only; do not use a Chinese name), and one red seal; on from about 0:00.7 to the end of A1. |
| A2 | The drift across the floor ends on little Jade lying on her back, wide AWAKE, waiting for her mama: blinking up at the ceiling, fingers fidgeting with the blanket edge, the storybook hugged on her chest. |
| A3 | She hears the stairs: head turns, she sits up. Mama comes up tired, wipes her hands on her apron, lifts it off over her head and hangs apron and towel on the hook by the door, then turns and softens when she sees the child awake. |
| A4 | Mama's pink-from-dishwater hands (no apron in frame) take the book the child holds up to her. |

### B, verse 1
| Shot | New direction |
|---|---|
| B1 (ATTIC, lip: little Jade) | "妈妈, will you tell me before I sleep / how 孙悟空 came to be?" Mama is sitting down beside her, not yet looking. Little Jade reaches out and puts her hand on Mama's forearm, a bid for attention, tugs once on "tell me", bounces on "孙悟空", then watches her face, hopeful and a little sly. Mama turns to her and smiles on the last word. |
| B2 (ATTIC, lip: Mama, first half only) | "On 花果山, where the cliffs run steep": Mama scoops her into her lap (LAP_front), opens the book in front of them both, and starts in a storyteller's voice. Cut to LAP_ots: over the shoulder onto the spread, the camera starts to push. The painted mountain on the page is rock-steady (v2: "the mountain appears to be dancing around the book": the page art must be tracked to the page quad or the book held still; no sliding). |
| B3 (BOOK) | "a stone looked over the sea": the push continues until the page is the whole screen (LAP_ots_push_end hands over to the flat page). Inscription. |
| B4 (BOOK) | "Sunlight by day and moonlight by night": 3.1. Travelling right to left across the characters (Jade liked the pan). Inscription. |
| B5 (BOOK) | "a thousand years of soaking up light": 3.1, the smooth stone. Vertical calligraphy of the line at the side. |

### C, pre-chorus
| Shot | New direction |
|---|---|
| C1 (BOOK) | "It split apart": the crack. Medium switch to rubbing on the chops (held, clean). Inscription: the stone split. |
| C2 (ATTIC) | "Monkey!": from her seat in Mama's lap both small hands shoot into the light; the monkey shadow lands on the page. Shadow physically joined to the hands (LAP_hands light model). |
| C3 (ATTIC, lip: Mama) | "Not yet, that's just the start": lap, close. Mama laughs through the line and lowers the small hands with one finger; little Jade sneaks them up an inch, is caught, grins up at her. |
| C4 (BOOK) | "A stone egg, round as a ball": as v2 plus static calligraphy in the corner. |
| C5 (ATTIC then BOOK) | "the wind blew once, and that was all": LAP_profile: child in her lap, Mama fills her cheeks and blows across the page past the child's ear; the child's hair lifts, she scrunches up and LAUGHS. Then the mist rolls over the egg. No finger near anyone's mouth. |
| C6 (BOOK) | 3.1: the points of light inside the stone run together; cracks. |

### D, hook
| Shot | New direction |
|---|---|
| D1 (STAGE) | Birth: ink throw lands as the monkey in 亮相; yellow floods in (3.4). Seal 仓. Medium switch on the echo. |
| D2 (STAGE) | "He bowed four ways": the four bows as one smooth performed movement from a video model (v2's hard cuts looked rough here), seals on the beats. D2d (ATTIC): little Jade, off Mama's lap, copies the last bow on her mat. |
| D3 (ATTIC) | "No cradle, no lullaby, no song": drop the unexplained yellow lines. Lap: Mama shakes her head slowly, one "no" each, mock-solemn; little Jade mirrors her half a beat late. Sung without a close singing mouth (wide enough that lips are not the subject), or one clean lip take of Mama if LIPSYNC can pass it. The window is in view: the sign is the perpendicular wedge. |
| D4, D5 (BOOK) | 3.2. |
| D6 (STAGE) | 3.5: the somersault on the Buddha's palm, whole composition in frame. |
| D7 (STAGE) | Staff flower as v2 (Jade's notes do not touch it), with the yellow monkey. |
| D8 (STAGE) | As v2 with the yellow monkey. |
| D9 (ATTIC) | The copy of the look-out pose is good but ran a beat too long: 1 second of it, then she climbs onto a stack of textbooks to do it higher, wobbles, and she and the whole stack go over. Mama lunges and catches her (alarm, then relief, then a laugh she tries to hide). Layout `D9_a/b/c`. This fall is what "do what mama says" answers later. |

### E, memory verse
| Shot | New direction |
|---|---|
| E1 (ATTIC, lip: Mama) | "The monkey had a memory just like you": back in her lap after the fall. Mama taps her nose on "you"; she goes cross-eyed and giggles. |
| E2 (BOOK) | "he never once forgot a spell": Jade likes this painting. Bring the troop to life with a video model: some groom each other, some jump, some eat; small, many, each doing its own thing. Shorten any dead hold. |
| E3 (ATTIC, lip: little Jade) | "Names and faces, I lose a few / but a spell I'd remember well": lap; a big shrug on "lose a few", taps her temple on "remember well", sure of herself; Mama smiling above her. |
| E4 (BOOK) | "The master leaned in close to his ear": fix the master's disjointed finger (redraw the hand); static calligraphy of the line at the side. |
| E5, E6 (ATTIC) | The whisper into her ear from behind/above (she is in the lap); she holds still, eyes slide sideways, shoulders up because it tickles; then twists round to give Mama the sideways look, one eyebrow; Mama hides a laugh. Eyes wide on the rap pickup. |

### F, rap (BED+CAR, STAGE)
| Shot | New direction |
|---|---|
| F1 (lip: daughter) | The back seat has two car seats; she is in one, off to one side of frame, the other is empty (layout). She performs for the front seat and knows she is good: hands chop the beat (apart, never palms together), chin leads, feet kick, a grin between phrases. Brown hair. Unmistakably the BACK seat. |
| F2 | Pane as shadow screen, as v2; she watches it, delighted, pointing. Alive, in the back seat. |
| F3 | No rapping face. She pinches a hair, squints at it, puffs it off her palm with full cheeks and watches it go; match cut to little Jade doing exactly the same (Jade: this little Jade "has the right amount of cuteness"). |
| F4 | F4a: the mirror: Jade's eyes smiling at her, the daughter behind, off to the side, singing at the mirror. F4b: 3.3. |
| F5 | 3.3 (seals, hairs fly home). |
| F6 | F6a: 3.3. F6b: v2's ending was unreadable ("not sure what she's reacting to"). New: the last hair drifts back to her; she catches it in her fist, opens her hand, it is gone; she looks up at the mirror and laughs. |

### G, the band (ATTIC, BOOK)
| Shot | New direction |
|---|---|
| G1 (lip: little Jade) | "Why does he wear a band of gold? / Is it heavy? Is it cold?": lap. A real worry: she touches her own forehead, looks from page to Mama and waits. Margins close as v2. |
| G2 (BOOK) | "He wouldn't listen ...": as v2, shorter-feeling (add life: he tugs at the band); Chinese calligraphy of the lines on the page in lieu of subtitles. |
| G3 | "It isn't fair ...": she does NOT sing on camera. Her hand goes flat over the monkey to protect him; the shadow is cast by that hand and touches it (light model). Head shaking, lower lip out, seen from above/behind, or the hand only. |
| G4 (lip: Mama) | "Then 听话, or you'll get one to wear / Do what mama says, no more, no less": no shadow play. Two-shot, lap: Mama sings it, light and teasing, a finger lifted, glancing at the toppled books; little Jade listens with a sceptical, mischievous face, a subtle lip bite, eyes going to the books, to Mama, away. |
| G5 (lip: little Jade, minimal) | "Yes": LAP_child_cu. She looks up and away for a moment, then back at Mama; holds; the smallest "Yes". Not defeated: deciding. Blink after. |
| G6 | As v2. |

### H, bridge (FACES, BOOK)
| Shot | New direction |
|---|---|
| H1, H2 | As v2 with the medium switch replacing mis-registration; painted surface on wide framings. |
| H3 | "Tool or threat, trick or kid": Jade asked whether the faces correspond to real archetypes. They must: each of the four is a true 脸谱 type whose traditional meaning answers its word, and the album as a whole follows the real colour code. FACES team: document the mapping in the log and fix any face that is not a real type. |
| H4 | As v2. |
| H5 (BOOK) | 3.1 addition (columns inside her shadow). |
| H6 (BOOK) | "one hair that can't gather, blown on the gale": the hair is curled; the wind is visible in it (it rides, loops, straightens); near the end of its crossing it begins to turn into a monkey (a few strokes) as it leaves the page. Still the emptiest frame. |

### I, build (BED+CAR, BOOK, STAGE)
| Shot | New direction |
|---|---|
| I1 (lip: Jade) | "Mischievous baby, Monkey's twin": Jade holds her in her arms, kid in lap, book in front of both (LAP_front, bedroom), flashlight propped or in hand. Read like a dare, a squeeze on "twin"; the daughter wriggles, pleased. |
| I2 | "you'd fight the gods and win": 3.5 (the page; no deformed hand shadows). |
| I3 (lip: daughter) | "You think I'd ask for a seat at the table?": I3a: LAP_child_cu: she is a little hesitant, looks at the page, then tips her head back to look up at her mother, really asking. I3b: the celestial table, one seat bare (3.5). |
| I4 (lip: Jade) | "Wouldn't you? You're able.": first a real MORPH made by a video model (first frame Mama's 1988 face, last frame Jade's, same framing; v2's double exposure looked like two faces superimposed), about 0.6 s, then Jade, built by animating her accepted likeness (not a redraw: v2's repaint "looks nothing like me"): a small smile on "Wouldn't you", leans in and holds her daughter's eyes on "You're able". |

### J, drop 2
| Shot | New direction |
|---|---|
| J1 | The daughter, encouraged, presses her fingertip to a carved character on the page as a child presses a lift button; it lights (and the 3.2 threads start from it). |
| J2, J3, J5 | As v2 with medium switches for the chops, the yellow monkey, the 3.2 threads in J2/J5. |
| J4 | Replace the four disjointed faces: a split screen of the two storytimes, 1988 left in red neon, 2026 right in flashlight white, each mother with her kid in her lap, same framing (LAP_front, `J4_split`), all four singing "No cradle, no song"; on the gong both pairs do the same small thing at once (both children throw their arms up). A thin strip of bare paper between the halves. |

### K, outro
| Shot | New direction |
|---|---|
| K1 (lip: Jade, or off-camera) | "Do you want to know how he never died, / what he did on the other side?": lap; Jade lowers her voice; the daughter is nodding before the question ends. Then over the shoulder onto the page: the monkey's road to the underworld (3.5). |
| K2 | K2a: the daughter says "He opened the Book of Life and Death" with relish, looking down at the page from the lap (lip only if it passes). K2b: the hall of the Ten Kings, pushed into from the over-shoulder view. |
| K3, K5 | As v2. Chinese inscription beside the ledger for the sung lines. |
| K4 | A small hand must be seen turning the pages. |

### L, end
| Shot | New direction |
|---|---|
| L1 | The daughter asleep in Jade's lap, mouth open, an arm flung over Jade's arm; Jade looks down at her and breathes out. Fix the warped pull-back (use the layout). |
| L2 | No flashlight shot ("overstated"). Jade pulls the blanket up over her sleeping daughter; on the last hit (235.833) match cut to 1988: Mama pulls the blanket up over sleeping little Jade, same framing, same gesture. |
| L3 | The attic window and its neon wedge; the hum cuts at 237.840 and the neon goes off; the last note rings out 3 s over black (ending B). |

## 6. Lip-sync shots (LIPSYNC team owns method and pass/fail)
On camera: B1 (little Jade), B2 first half (Mama), C3 (Mama), E1 (Mama), E3 (little Jade), G1 (little Jade), G4
(Mama), G5 (little Jade, one word), F1 (daughter), I1 (Jade), I3a (daughter), I4 (Jade). Optional if they pass: D3,
F4a, K1, K2a, J4. Not on camera any more: F3, G3.

## 7. Global lyric layer and the rap's English (CUT)
English under the rap, from Jade:
| Line | English |
|---|---|
| 石头里蹦出来 没有童年 | Burst out of a stone, no childhood |
| 一声耳语 学会七十二变 | One whisper, and learned the 72 transformations |
| 拔一把毫毛 吹一口气 | Pluck a handful of hairs, blow one breath |
| 千百个我 同时在这里 | Hundreds, thousands of me, all here at once |
| 每一个都是我 每一个都算 | Each one is me, each one counts |
| 说完这句话 各自消散 | When this sentence is finished, each one scatters |
| 身外身法 谁是真身 | Body outside the body: which is the real one? |
| 问了也白问 个个都真 | No use asking, every one is real |

## 8. Deliverables per team
As `docs/COMP_BRIEF.md`: `shots/<ID>.py`, `media/comp/<ID>.mp4` (960x540, 24 fps, exact frames, no audio), a review
sheet `work/review/comp_v3/<ID>.jpg` (12 frames), and a log `docs/logs/LOG_v3_<team>.md` (per shot: status, takes,
what is still weak). Before overwriting any `media/comp/<ID>.mp4` or `shots/<ID>.py`, copy the v2 file to
`media/comp/_v2/` and `shots/_v2/`. Keyframes go to `media/kf/v3/`. Do not commit; do not touch other teams' shots.
Standing rules in `docs/HANDOFF.md` ("Standing rules") all still apply, including: Jade's name, email, photos and
project details stay out of requests to outside services; never send `design/characters/_src/jade_face_photo.jpg`
anywhere; all Chinese on screen is typeset, never drawn by a model.

## 9. Sound and ending (SOUND, CUT)
Mix v2: the diegetic layer raised until it is clearly audible on laptop speakers without masking a lyric; ending B
(the last note rings about 3 s; audio length 241.920 s). New cues for the new action: apron and towel on the hook,
the book stack falling (D9), Mama's catch, blankets (L2), the daughter's hair-puff, abacus clicks and the small seals
in the swarm, page press (J1). The cut extends L3 with black to the end of the audio.

## 10. Jade's notes, verbatim

Overall: maybe use three.js or blender to block out some of the scenes that come out inconsistent. In both storytimes,
kid on mom's lap, book in front of them. All the acting should be better, more alive, not lifeless / expressionless;
reshoot all of it with new prompts if needed, don't worry about budget. Subtle story arc / contrast: see section 1.

```
- 0:00.71  A1  Should have song title somewhere on here, probably off to a corner, like a title slide
- 0:08.00  A2  she should be awake, waiting for her mama, so blinking up at the ceiling
- 0:10.37  A3  mama should hang her apron and towel up on a hook near the door before going to her kid, and in every scene after, she should not be wearing an apron.
- 0:16.15  B1  better acting direction across the entire video. she's really stiff, expressionless and lifeless here. maybe she reaches an arm out to touch her mom's arm? it's a bid for attention.
- 0:23.58  B2  slight lip sync issue
- 0:24.80  B2  the mountain appears to be dancing around the book
- 0:24.80  B2  ideal blocking: mom pulls the daughter into her lap, book in front of both, over the shoulder shot so you can see the book, then the camera zooms into the book and it becomes the whole screen
- 0:31.15  B4  I like the panning across the characters. AI as arcane magic: we used light to carve runes into ultra-purified sand so fine that the sand started to think. Make that idea come to life by sense of scale or other means; plausible deniability: someone who doesn't know computers sees the traditional tale, someone thinking about AI sees the metaphor. "a thousand years of soaking up light" and all the words of the language making their way into the stone has a lot of potential.
- 0:37.16  B5  chinese characters for the lyrics vertically on the side (static, not animated), like calligraphy accompanying a painting
- 0:44.86  C1  same: a painting inscription in chinese saying the stone split apart, in calligraphy
- 0:50.87  C4  static chinese calligraphy in the corner, the lyrics
- 0:53.17  C5  kid in her lap, she makes the blowing motion, and the kid laughs in reaction
- 0:59.81  D1  Sun Wukong in his traditional yellow outfit, like in peking opera; can we try how that looks?
- 1:01.45  D2  the animation could be smoother here, can we have a video model do it?
- 1:05.10  D3  not sure what the yellow lines are going on here
- 1:05.49  D3  the neon sign went perpendicular to the wall and would appear as a triangle from this view; block it in 3D
- 1:07.23  D3  lip sync issues
- 1:11.35  D5  "one whisper and the hundred come along" is about learning generalization: the master whispers one thing and the monkey knows a hundred things from that one lesson. think deeply about how to convey that in art
- 1:14.71  D6  the top of the mountain is cut off. render the monkey in one of the traditional stories, like how he flips around the buddha hand mountain; is there a traditional painting to reference?
- 1:24.19  D9  really good motion, but repeats a beat too long. in character for her to climb up on a stack of books after the motion and then she and the entire stack falls over, and her mother has to react
- 1:30.23  E2  I really like this painting. give it to a video model and make the monkeys come to life: grooming each other, jumping, eating
- 1:41.34  E4  Chinese calligraphy to show the lyrics on the side
- 1:42.20  E4  the master's finger is disjointed
- 1:47.85  F1  her car seat should be off to the side. two car seats in the back, she's in one, the other is empty. mock up the car in 3D
- 1:50.50  F2  she's really lifeless and expressionless here. more alive, and in the back seat not the front
- 1:51.79  F3  instead of rapping here, just show her doing the hair motion and blowing before we cut to little Jade
- 1:52.70  F3  this little Jade has the right amount of cuteness, for reference
- 1:53.67  F4  a good opportunity to illustrate an agent swarm in sun wukong's world, in a way that makes a modern person immediately think of agent swarms
- 2:01.45  F6  not sure what she's reacting to here, or what she's thinking. acting should be more natural
- 2:04.23  G1  lip sync issues
- 2:10.14  G2  Chinese calligraphy in lieu of later subtitles (for rednote)
- 2:17.46  G3  lip sync issues, or just not have her sing at all here. the hand shadow is disjointed from her actual hand; model the light
- 2:26.33  G4  not sure what the shadow is conveying; missed opportunity for her mama singing this lyric with her looking a little skeptical / mischievous / subtle lip bite leading up to the hesitant 'yes'
- 2:28.56  G5  hesitation in her eyes: she looks up or away for a moment and then back. mischievous child a full click smarter than both parents; consistent with hiding her understanding of Shanghainese from them
- 2:42.71  H3  do these correspond to what the types of archetypal characters are?
- 2:53.50  H6  show movement with this hair, like it's curled and you can see the wind expressed through it as it starts transforming into a monkey
- 2:58.43  I1  she should be holding her in her arms, kid in lap, book in front of both of them
- 3:01.86  I2  the hands look kinda deformed. show the monkey defiantly standing against the gods, one of the traditional stories where he fights the gods and wins
- 3:03.47  I3  her face should look a little hesitant, and her mother's response is to encourage her confidence; a direct contrast to her own mother's parenting
- 3:05.16  I3  what if it's the table of celestial gods in traditional Chinese lore?
- 3:09.01  I4  might as well just animate the reference image instead of this redrawn thing
- 3:17.49  J4  the 4 disjointed faces: split screen with two pairs of mother daughter at storytime, kid in mom's lap, to show a parallel
- 3:25.44  K1  over the shoulder shot onto the page, the monkey traveling to the underworld (traditional art, or peking opera stills)
- 3:54.58  L2  no flashlight shot, feels overstated. she pulls the blanket over the kid, cut to Jade's mom pulling the blanket over little Jade
Likeness I4 3:07.15: the two faces are superimposed instead of morphing; make a video model do a morph
Decisions: 1 direction mostly right, but the glitch reads as errors; find something else artistic. 2 keep singing faces, find a better method, QA sync. 3 keep the lyric over the cliffs, plus Chinese calligraphy on the page. 4 ending B. 5 neon colour fine; try the sign perpendicular. 6 rap English as section 7. 7 sound layer too quiet. 8 another 540p pass.
```

## 11. Sound cue times the picture must hit (mix v2, `media/sound/mix_v2.wav`, `docs/sound_cues.json`)
Picture teams: stage the action so it lands on these song-clock times (s). If a shot cannot, tell the lead the time you used.
- A3: apron lifted off 11.68-12.04 (peak 11.922); apron on the hook 12.220; towel draped 12.400.
- C5: Mama's blow lifts the child's hair 53.220; the child scrunches up 53.950.
- D9 (82.500-85.833): steps onto the book stack 83.244; wobble 83.475; stack starts to topple 83.798; child lands 84.127;
  Mama's catch 84.351; last books settle 84.570.
- F3: daughter's puff 112.146; little Jade's puff on the match cut 112.372.
- F4b abacus clicks (all cells advance a pose): 113.688, 114.135, 114.567, 115.002, 115.445, 115.882.
- F5 seals, one copy finishing per beat: 116.320, 116.736, 117.200, 117.628.
- J1: fingertip press 189.620 (crashes from 189.790).
- L2: 2026 blanket pulled up 235.33-235.78, tucked 235.780 (last hit 235.833 = the match cut); 1988 blanket from 235.88,
  tucked 236.276. Neon off 237.840. Audio ends 241.920 (ending B).

## 12. Additions from Jade, 2026-11-17 evening
- **Jacket lettering (Jade's and little Jade's white jacket):** "RARE EARTH" on the back under the large pale-blue
  circle, and "1420 MHz" inside the round ringed patch on the sleeve, were missing from the v3 sheets. They must be on
  screen wherever the back or the patch is readable. Lettering is never drawn by a model: paint the areas blank and
  set the text in code (tracked to the garment), as CANON says. Reference: `inputs/ref_merge_little_jade_fullbody.jpg`,
  `inputs/ref_moongazing_jade_singing_watercolor_first_frame.jpg`.
- **Inscriptions:** `design/text/lyrics_zh_v3.txt` was replaced by Jade's proofread version (comment lines start with
  `#`; several lines changed; H6 now has three columns). Her rule: where the novel has the line, use the novel's words.
  Her parents will recheck, so keep inscriptions data-driven: a text change must be a re-render, not a redesign.
- **I3b, the seat at the table:** a banquet seat and a seat of power are not the same thing in the novel. Stage the
  Peach Banquet so the table reads as rank: the Jade Emperor and the Queen Mother at the head, gods seated in strict
  order of precedence down both sides, a name slip at every place, the bare seat among them (not at the foot).

## 13. Stepping into the painting (Jade, 2026-11-17 evening)
Jade: "I kinda like the feeling of stepping into a Chinese landscape painting that feels 3d once you're in it, and
I've seen other AI artists do really impressive beautiful work where the brushstrokes come to life."
This is now the governing feel for every shot inside the book, and it relaxes the old "one thing moves" rule there:
- **Entering has depth.** When the camera pushes over the shoulder into the page (B2 -> B3, K1 -> K2b, I-shots), the
  flat page must open into space as we cross its surface: foreground rock and pine slide past, the middle cliff
  separates from the far peaks, mist lies between the layers, and the camera keeps travelling INSIDE the landscape
  (true parallax from layered plates or a depth-projected plate, or a video model given the plate as first frame and
  asked for a slow dolly through the painting). Once inside, the world is deep, in the logic of 三远 (high, deep and
  level distance); it is still ink on paper in every frame (paper grain, wash edges, bare paper for mist and water).
- **Brushstrokes are alive.** Strokes draw themselves on, wet ink blooms and settles, pine needles and grass are laid
  in as we pass, mist flows, water moves as bare paper with a few travelling lines, the troop moves (E2), the dust
  rises (B4). Prefer a video model animating our own plates (see `docs/VIDEO_BAKEOFF.md`: MiniMax h3 for landscape,
  Seedance 2.0 for ink dynamics) over procedural wobble; key the result back onto our paper.
- Leaving the book reverses it: depth collapses back to a flat page in a mother's hands.
- The whitespace rule stays: depth is made with fewer, better layers, not with more ink.

## 14. Blocking decisions from the 3D pass (`docs/LAYOUT_V3.md`)
- Neon: option A (the blade sign hangs in front of the far third of the window; a narrow wedge from the door end, and
  it lights the lower mats, the lap and the page). The lettering reads normally, NOT mirror-reversed.
- The attic storytime spot is the lower half of little Jade's mat, in the beam; she lies awake at the dark pillow end.
- Hand shadows are never directly under the hand: offset and softness per the sidecars; hands flat to the page.
- Car cameras sit just under the headliner looking down ~14 degrees (anything lower hides her behind the seatback);
  F3b in the attic matches that angle for the match cut.
- E5 (the whisper) uses `LAP_child_cu`. L1 must be re-blocked in the keyframe as: asleep in Jade's lap.
- The last third of the over-shoulder push is a 2D warp on the page quads into the BOOK team's flat page.

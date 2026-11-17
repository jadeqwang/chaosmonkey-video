# Chaos Monkey: handoff to the next session

Written 2026-11-17 by Claude (Fable 5.2), the lead of the first pass, for whichever session receives Jade's notes.

## Where things stand

- Jade has watched `previews/chaosmonkey_preview_v2_540p.mp4` (complete 540p cut, 65 shots, 3:58). Her verdict:
  **"overall I think this is a pretty good start."** The direction (opera stage, traditional-twin glitch, painted people)
  has not been rejected; her answer to it is question 1 on the notes page.
- She is writing notes in `review/preview_v2_notes.html` and will paste the result into the next session. Nothing has
  been regenerated since the preview except two characters' sheets (below).
- Spend: $176.20 of the $600 cap. No 1080p render exists; do not make one until she asks (notes page, question 8).
- Branch `claude/video-production`, last commit `3034547`. Everything since is uncommitted: commit only if Jade asks.

Read in this order: this file, `docs/MORNING.md` (what the film is, what is weak), `docs/TREATMENT.md`,
`docs/QA_PREVIEW_V2.md`, `design/characters/CANON.md` section 0, then `docs/STATUS.md` for history.

## What Jade has said so far (17 Nov)

1. **The little girls are less cute than their references.** My reading, not yet confirmed by her: I wrote cuteness out
   (see 3), gave little Jade a heavy fringe, the night grades grey the skin, and the lip-sync model ages faces.
2. **Hair: little Jade and adult Jade must not have bangs covering the forehead**; curtained to the sides, almost like
   layers. Sheets redrawn, see below.
3. **"All the deadpan unsmiling makes them look lifeless and have no action direction."** She asked for better, more
   natural acting direction. That is the section "Acting" below, and it overrides every "deadpan" in `docs/shots.yaml`,
   `design/characters/CANON.md`, `docs/KEYFRAME_BRIEF.md` and the brainstorm.
4. Earlier, from the sound note: she liked the diegetic sound layer of Hold Fire; whether this film's layer works is
   question 7 on the notes page.

## The notes she will send

One block of text from the page's "Copy everything" button, in three parts:

- **TIMESTAMPED NOTES**: `- 1:16.25  D7  hook1: text`. The time is the song clock, the ID is the shot
  (`docs/shots.json`; the script is `shots/<ID>.py`, the render `media/comp/<ID>.mp4`).
- **LIKENESSES**: per person, where it goes wrong (my sheet, the film frames, or both), ticked causes, her own words,
  notes on single frames (`B1 0:17.00: …`), and her verdict on the redrawn sheets ("Use these" / "Close; fix…" / "Not right").
- **DECISIONS**: eight questions (direction, lip-sync approach, lyrics over the carved cliffs, ending mix, opening neon,
  the rap's English, sound layer, what next).

How to work through them:

1. Sort every note to a shot and a kind: sheet/likeness, acting/retake, comp (timing, grade, text), cut (length, order),
   sound. Write the list where she can check it before spending.
2. If she did not approve the redrawn sheets, fix them first: nothing with little Jade or Jade should be regenerated
   against sheets she has not accepted.
3. Likeness and acting changes mean new keyframes (`media/kf/`), then new clips, then the comp re-render. Comp-only
   notes are cheap: edit `shots/<ID>.py` and re-render.
4. Rebuild and QA as in "To resume" in `docs/MORNING.md`. Rebuild the notes page for the new cut with
   `tools/review/notes_page.py --name preview_v3` (it expects `previews/chaosmonkey_<name>_540p[_nolyrics].mp4`).

## Redrawn sheets (little Jade and Jade)

New files, old ones left in place for comparison. Jade has not seen them yet; they are on the notes page under each
character with a three-way verdict.

| | New sheet | Crops for prompts |
|---|---|---|
| Little Jade | `design/characters/little_jade/lj_A_turnaround_v2.jpg`, `lj_B_poses_v2.jpg`, `lj_C_expressions_mouths_v2.jpg` | `design/characters/refs/lj_heads_v2.jpg`, `lj_full_v2.jpg` |
| Jade | `design/characters/jade/jade_A_turnaround_v2.jpg`, `jade_B_expressions_details_v2.jpg` | `design/characters/refs/jade_heads_v2.jpg`, `jade_upper_v2.jpg` |

What changed: open forehead with side-swept layers on both; little Jade also has larger glossy eyes with a highlight,
visible blush, and expression and pose sheets that are acted (rapt, asking, grinning, indignant, sceptical, sleepy)
where the old ones were ten versions of a flat face. Prompts are beside each file; the new prompt blocks are in
`CANON.md` section 0.

Things to know:

- **A v1 image in the references brings the fringe back.** It happened on the first attempt at the pose sheet. Pass no v1
  sheet, crop or keyframe of either character, and not the top row of the twins sheet.
- Every shot with little Jade or adult Jade carries the old hair, so every one needs a new keyframe: A3, B1, B2, C3, D3,
  D9, E1, E3, E5, E6, F3 (second half), F4, G1, G3, G5, I1, I4, K1, L1. C2, G4, I2, L2 are hands only.
- Little Jade's front view on the turnaround lies flatter than the others; use the three-quarter view and the expression
  heads for hair.
- Not redrawn: the daughter and Mama. The daughter's prompt block still says "deadpan, watchful, unimpressed" and her
  sheets were drawn to it, so she likely needs the same treatment (ask Jade, or read her likeness notes). Mama reads
  35 to 40 in several shots where she should be about 30.
- Adult Jade's first sheet was made from a photo of her that she supplied for that purpose. The redraw did not resend
  it (it edited the painted sheet). Do not send her photo to any service again without asking her.

## Acting

### What went wrong

I took one phrase from the brainstorm, the family's "resting oblivious face", and wrote it into every prompt as
"deadpan, watchful, unsmiling", and I listed "reads cute" as a fault to guard against. The models obeyed. A face told
only what not to do has nothing to do, so both girls stand and stare, and the adults got little more. It also
flattened the story: "Yes" at 2:28 is the moment a lively child goes quiet, and it cannot land if she has been quiet
all along.

### How to direct instead

- **Give each shot a want and an action, never a mood.** "She wants the story to start, so she tugs the blanket up and
  looks at the book, then at Mama" can be performed. "Deadpan" cannot.
- **Write it as beats in time**, matched to the measured words in `analysis/timing.json`: what she does before the line,
  on the stressed word, and after it. Video models follow "first… then… on the last word…" well.
- **Children act with the whole body.** Feet kick, hands fidget with a cuff, the head tilts, the weight shifts, they look
  at the thing and then check the adult's face. Ask for one of these in every shot with a child.
- **Eyes lead.** Say where she looks and when the look changes. Ask for blinks and breathing in any hold over a second.
- **Reactions matter as much as lines.** Whoever is not singing is listening, and listening is visible: leaning in,
  mouthing a word, a suppressed laugh.
- **Humour comes from understatement inside a lively child**, used once or twice (the sideways look at 1:46, the raised
  eyebrow at 3:03), not from a blank face throughout.
- **Smiles are allowed and wanted.** This is a bedtime story between people who love each other. Both rooms should feel
  warm before they feel anything else.
- **Never write** deadpan, unsmiling, flat, expressionless, neutral, unimpressed, "never cute". For lip-sync start
  frames, replace "mouth closed, neutral" with a relaxed, slightly open, about-to-speak face.
- **Stillness is saved for three places**: "Yes" (2:26 to 2:29), the bare column at the end (3:44 to 3:48), and the two
  switches. They work because nothing else is still.
- The one-thing-moves rule in the treatment is about the painted pages. In the rooms, people may move like people.

The pose sheet (`lj_B_poses_v2.jpg`) and the expression sheets are drawn to these and can be passed as references for
the matching shots.

### Shot by shot

Times are in-points. The words are the line sung in the shot.

**1988, the attic**

| Shot | Line | Play it as |
|---|---|---|
| A3 0:09 | (none) | She hears the stairs before the door opens: head turns, she scrambles up onto her knees, blanket in both fists. Mama comes up tired, drying her hands, and softens when she sees her still awake. |
| B1 0:15 | "妈妈, will you tell me before I sleep / how 孙悟空 came to be?" | She is bargaining for a story. Starts with the book hugged to her chest, holds it out on "tell me", bounces once on "孙悟空", then watches Mama's face for the yes. Hopeful, a little sly. |
| B2 0:22 | "On 花果山, where the cliffs run steep" | Mama settles, licks a finger, opens the book and slips into a storyteller's voice: eyebrows up, a hand rising to draw the cliff in the air. Little Jade wriggles in under her arm and cranes at the page. |
| C2 0:45 | "Monkey!" | She cannot wait: both hands shoot into the light, she half stands, grinning at her own shadow. |
| C3 0:46 | "Not yet, that's just the start" | Mama laughs through the line and lowers the small hands with one finger. Little Jade lets them be lowered, then sneaks them up again an inch; caught, she grins. |
| C5 0:52 | "the wind blew once, and that was all" | Mama fills her cheeks, glances sideways to make sure she is being watched, and blows across the page, lips rounded, eyes following the dust. It must not read as "shh": no finger near the mouth. |
| D3 1:04 | "No cradle, no lullaby, no song" | Mama shakes her head slowly, one "no" each, mock-solemn. Little Jade mirrors the head shake half a beat late, lips moving on "no song". |
| D9 1:22 | (none) | She has copied the page: one leg up, hand shading her eyes, wobbling, tongue between her teeth, very proud. She loses balance and hops. Mama claps once and laughs with her head back. |
| E1 1:25 | "The monkey had a memory just like you" | Mama leans in close and taps her nose on "you". Little Jade goes cross-eyed at the finger, scrunches her nose and giggles. |
| E3 1:33 | "Names and faces, I lose a few / but a spell I'd remember well" | Honest and unbothered: a big child's shrug with palms up on "lose a few", then she sits up straight and taps her own temple on "remember well", sure of herself. Behind her Mama smiles into the book. |
| E5 1:43 | "(ps ps ps)" | Mama cups a hand at her ear. Little Jade holds very still to hear, eyes sliding sideways and widening, then her shoulders come up because it tickles. |
| E6 1:44 | "a secret only he could hear" | She pulls back and gives Mama the sideways look: one eyebrow, a pressed smile, "is that true?". Mama hides a laugh behind her hand. On the rap pickup her eyes go wide. |
| G1 2:01 | "Why does he wear a band of gold…" | A real question that has started to worry her. Brows drawn, she touches her own forehead with two fingertips, looks from the page to Mama, and waits for the answer. |
| G3 2:14 | "It isn't fair, it isn't fair / I don't want it in his hair" | Indignant, close to tears. She puts her hand flat over the monkey to protect him, lower lip out, shaking her head on the second "fair", voice of a child arguing with the rules. |
| G4 2:21 | "Then 听话, or you'll get one to wear…" | Shadows only. Mama's ring of finger and thumb comes down slowly and teasing; the child's shadow shrinks, shoulders up, chin tucked. Mama means it as a joke. It lands as more. |
| G5 2:26 | "Yes" | The stillness. She was mid-protest: the breath she took to argue goes out, her eyes drop, come back up to Mama, and hold. A small swallow, then "Yes", barely moving her lips. Blink once, after. |

**2026, the car**

| Shot | Line | Play it as |
|---|---|---|
| F1 1:47 | "石头里蹦出来 没有童年" | She is performing for the front seat and knows she is good. Hands chop the beat like small karate cuts, apart, never palms together; chin leads; feet kick the car seat in time; a grin breaks through between phrases. |
| F3 1:51 | "拔一把毫毛 吹一口气" | She pinches one hair between finger and thumb, squints at it with total seriousness, then puffs it off her palm with her cheeks full and watches where it goes, delighted. Then 1988: little Jade doing exactly the same, same joy. |
| F4 1:52 | "千百个我 同时在这里…" | In the mirror Jade catches her daughter's eye and joins in, eyes smiling, head nodding the beat; the daughter points at the mirror and sings louder at her. |

**2026, the bedroom**

| Shot | Line | Play it as |
|---|---|---|
| I1 2:57 | "Mischievous baby, Monkey's twin, / you'd fight the gods and win" | Jade reads it like a dare, flashlight under her chin for a second, eyebrows up. The daughter, on her tummy with her feet in the air, pushes up on her elbows. |
| I2 3:00 | (hands) | Two hands race to make the monkey; the small one gets there second and bumps the big one on purpose. |
| I3 3:03 | "You think I'd ask for a seat at the table?" | Scornful and funny: she leans back, one eyebrow up, a puff of breath on "ask", then looks to see if it landed. This is where the understatement lives. |
| I4 3:07 | "Wouldn't you? You're able." | Jade answers gently and with full certainty. A small smile on "Wouldn't you", then she leans in and holds her daughter's eyes on "You're able". Warm, not grave. |
| J1 3:09 | (none) | The fingertip hovers, hesitates, then presses, the way a child presses a lift button. |
| K1 3:23 | "Do you want to know how he never died…" | Jade lowers her voice to a secret and turns the book toward her. The daughter is already nodding, fast, before the question ends, and shuffles closer on her knees. |
| K2 3:30 | "He opened the Book of Life and Death" | She has the big book in both arms, chin over the top of it, and says it with relish, eyes huge, pausing before "Death" for effect. |
| K4 3:37 | (page turns) | A small hand must be seen turning the pages: a lick of the finger, pages turned too many at a time, then one at a time. |
| L1 3:48 | (none) | Asleep the way children sleep: mouth open, one arm flung over Jade's arm, a foot off the bed. Jade looks down at her, then at the blank column, and breathes out. |
| L2 3:53 | (click) | Her thumb rests on the switch a moment longer than needed. |

Mama throughout: about 30, tired from the restaurant downstairs and glad to be upstairs. She performs the story with her
hands and voices; she is funny. Her sternness at 2:21 is half play, which is what makes it sad.

## Other open issues

Ranked in `docs/QA_PREVIEW_V2.md` and `docs/MORNING.md`. The largest that Jade's notes may not mention because she was
watching for story:

- Lip-sync softens painted faces toward a 3D look and sync is loose (Seedance 2.5). K1, G3 and F4 play as off-screen
  voice. Her choice of approach is question 2.
- The opera faces in the bridge look digital at wide framings.
- Takes already known to be wrong: F1 (praying hands, ginger hair), C5 (reads "shh"), K4 (no hand), D2d (shallow bow).
- Holds that drag: G2, E2, K4. L1's pull-back warps the room. B4 to B5 jumps in paper tone.

## Standing rules

- Spend cap $600 (`tools/gen/spend.py`). 540p passes until Jade asks for the master.
- Her name, email, photos and project details stay out of requests to outside services unless she asks.
- Commit only when she asks; never push without being asked. Never deploy, modify or delete the Cloudflare Worker
  `rare-earth-v3-relay` or its KV namespaces; never print Cloudflare secrets.
- Codex runs headless with `< /dev/null` under `flock /tmp/chaosmonkey-codex.lock`, never with sandbox-bypass flags.
- Python is `/home/jade/Documents/halys-video/.venv/bin/python`. Tool calls and model choices are in
  `docs/PIPELINE_RECON.md` and `docs/VIDEO_BAKEOFF.md`.
- All Chinese text on screen is typeset from `design/text/`, never drawn by a model.

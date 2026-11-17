# Chaos Monkey: director's treatment

Written 2026-11-16 by Claude (Fable 5.2), lead. This is the vision every agent works from. The brainstorm
(`inputs/Chaos Monkey — music video brainstorm.md`) stays the source for story, characters, the three
readings and the guardrails. Where this document differs from the brainstorm, this document wins; the
differences are listed at the end.

Jade's standing decisions for this pass (2026-11-16): spend cap $600; stop at a complete 540p cut for her
review; no full-size render before that.

## The one idea

**The blank page and the bare stage are the same place.**

Chinese painting leaves the paper bare (留白) and Peking opera leaves the stage bare (一桌二椅: one table,
two chairs, and everything else is the performer). Both make a world out of what is not there. The song is
opera percussion crashing into breakbeat, so the film is a storybook whose blank paper turns out to be a
stage: when the stone splits, the monkey that comes out of the ink is an opera performer, and the gongs that
have been waiting in the music finally have someone to land on.

So the film has two registers, and the music tells us which one we are in.

| Register | When | Rules |
|---|---|---|
| **Painting** (quiet) | Guqin, clappers, verses, bridge, outro | Brainstorm rules in full: ink budget, one corner, one thing moves per shot, mist is paper |
| **Stage** (loud) | Hook, rap, drop 2 | The paper becomes a stage. Opera grammar: 亮相 freezes, 四击头, staff, plumes, sleeves. Still only paper, ink, cinnabar, gold |

The rooms (attic 1988, car and bedroom 2026) are the audience. The tellers are always the ones holding
the light.

## Glitch, in the tradition's own terms

The brainstorm asked whether glitch belongs. It does, because every glitch technique already has an old
Chinese twin, and using the twin is what makes this a category nobody has seen. No digital artifact ever
appears; the picture breaks the way paper, print and theatre break.

| Glitch-hop move | Traditional twin | Where |
|---|---|---|
| Freeze / stutter on the hit | **亮相**: the performer snaps into a held pose on the last gong stroke | Every big crash in hook and drop 2 |
| RGB split | **Woodblock mis-registration**: the cinnabar, indigo and ink blocks print a few millimetres apart | Breakbeat chops |
| Invert | **Rubbing** (拓片): the same image white on black | Chops, alternating with the above |
| Echo / delay | **A seal pressed again without re-inking**, fainter each time | The chopped echoes in drop 2 |
| Sample chop / retrigger | **Shadow-puppet joints**: the same figure re-posed in hard cuts, no in-betweens | The rap |
| Loop | **走马灯** (trotting-horse lantern): a running figure repeating around a lit paper drum | Clones, 千百个我 |
| Slice / displacement | **Paper-cut** (剪纸) strips sliding out of register; a torn sheet re-pasted | Drop 2 peak, sparingly |
| Onscreen SFX text | **锣鼓经**: the opera's own syllables for its percussion (仓 才 台 …) stamped as red seals on the hits | Hook and drop 2 |
| Filter sweep / mono | Paper margins closing in | Headband verse |
| Dropout | Bare paper. Black | The bar of silence, the end |

## Opera and wushu, where they live

- **The birth is an entrance.** One throw of splashed ink (Liang Kai) lands as a figure in 亮相. "He bowed
  four ways" is a 四击头: four strikes, four bows, each stamped. The monkey moves like a 武生 doing a monkey
  role: tucked wrists, a hand shading the eyes, a staff flower.
- **The staff is a brush.** Wherever the staff sweeps it leaves a stroke: its spin is a ring of dry-brush
  (飞白), its thrust a single line. The suona melody is drawn by the staff tip. In drop 2 the staff form
  (猴棍) writes across the whole page, and the final stroke is the one that leaps from the 1988 page into
  the 2026 page.
- **Plumes and sleeves are mist and wind.** The two pheasant plumes (翎子) trace arcs that stay on the paper
  as lines. Mama's breath, the wind on the egg, is a water sleeve of mist.
- **The clones are shadow puppets.** In the car the windows are shadow screens: each passing streetlight
  throws a jointed monkey (and the daughter's own silhouette) on the glass, alive only while its light lasts.
  七十二变 is a puppet whose head is swapped on every beat. The hand shadows in both rooms are the same art,
  so the rap grows out of something the film has already taught.
- **The categories are painted faces.** "Tool or threat, trick or kid": four 脸谱 land in a row like stamps,
  each a type decided before the actor is born (red loyal, white treacherous, black upright, gold a god).
  "The categories arrived before I did": the row is one face of a whole album sheet of masks, old paper, one
  cell bare, and the child stands under the bare cell with no paint on her face. This replaces the poem's
  photocopied chart of faces with its true ancestor, and keeps the row that is one face short. The carved
  cliff then answers the next line ("made of the telling"): a child-shaped blank in lit writing.
- **The seat at the table is one of the two chairs.** The Peach Banquet is staged as opera: a painted table
  and chairs on bare paper. The bare seat is a chair. The daughter's shadow climbs onto it, which on the
  opera stage is how you climb a mountain.
- **Little Jade already does wushu.** She copied martial-arts poses from television in that attic. On the
  hook she mirrors the monkey's four bows on her mat; in drop 2 all four faces take the same 亮相 on the
  same gong.

## Look

One hand throughout: ink and light colour on cream xuan paper, fibres visible. People are drawn in the same
hand as the paintings (fine-line 白描 faces with light wash, like the teahouse reference), not cel anime, so
that a room and a page can share a frame without a seam. The rooms are paintings of night: dark washes with
one pool of light.

- **1988**: cinnabar neon cycling to cold blue, tungsten from the floorboards.
- **2026**: dusk violet, flashlight white; strawberry pink and jacket orange the only saturated colours.
- **The book**: 浅绛 for earth, 青绿 for heaven, bare paper for mist, water and sky.
- **The stage register**: ink black, paper, cinnabar, one gold.
- Gold happens three times only: the birth (light from the eyes), the band, the halo.

## Method

The picture is assembled in code from generated elements, so whitespace, timing and text are numbers.

1. **Plates and elements** from image models, each element alone on plain paper, cut out and laid on a paper
   canvas at the size the ink budget gives. Carved text and all readable Chinese is typeset from proofed
   sources, never generated.
2. **Motion** from video models, one moving thing per plate (mist, water, a figure), keyed back onto the
   paper. Bake-offs decide the model per task: ink landscape motion, ink figure motion (staff, tumbling),
   character acting and lip-sync, splashed-ink dynamics.
3. **Performance capture by rotoscope** for the stage register: generate (or source from our own generated
   footage) a performer doing staff and opera movement on a plain ground, then redraw it in code as brush
   marks so every frame is ink on our paper, not a filter over video.
4. **Rooms built once in 3D** (Blender or Three.js): attic, car interior, bedroom, and the storybook as an
   object. Renders give the video model first frames, so furniture, window and book stay put across shots.
5. **Final picture in the compositor**: multiplane camera moves on plates, seal strikes, mis-registration,
   rubbing flips, margins, lyrics set as inscriptions, all locked to `analysis/timing.json`.
6. **Review by measurement and by eye**: ink-coverage and squint tests per shot, contact sheets, a blind
   judge for bake-offs, a no-AI-test pass, a low-resolution animatic before bulk generation.

## Changes from the brainstorm

| Brainstorm | Here | Why |
|---|---|---|
| Glitch left to the builder, default none | Glitch throughout the loud sections, entirely through traditional twins | The music is glitch-hop; the twins keep the one-world rule |
| Opera only as an optional face patch | Opera stagecraft drives hook, rap and drop 2 | Jade's direction; the percussion is opera percussion |
| Characters in flat cel shading | Fine-line and wash, same hand as the paintings | Rooms and pages share frames; cel on xuan reads as a sticker |
| Categories carved on a cliff (天地神人鬼…) | A 脸谱 album sheet with one bare cell, then the cliff for "made of the telling" | Closer to the poem's face chart; faces are what she cannot read |
| Clones as reflections in car glass | Reflections that are shadow-puppet silhouettes, plus a 走马灯 loop | Ties the rap to the hand shadows |
| Sung words only on screen | Sung words, plus 锣鼓经 seal syllables on hits | They are the sound, written in the tradition's own notation |
| Banquet after Huizong's Literary Gathering | Same layout, reduced to table and chairs on bare paper | 一桌二椅 |

Kept exactly: the two timelines and voice handoff, the three readings and the no-AI test, the carved
mountain with real typeset text, raking light, the ink budget table, three camera moves, the ledger and the
blank column, the single click.

If an idea here does not survive contact with the footage, it is dropped and the brainstorm's quieter
version stands.

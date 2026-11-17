# Look bake-off (image models)

2026-11-16/17. Budget $25; spent **≈ $10.9** (list-price estimates, 100 paid calls; per-model split at the end).
Every output is in `media/look/<test>/<model>_<variant>.jpg` with its prompt and parameters in the `.txt` beside it; rejects
are kept. Contact sheets: `media/look/_sheets/L<n>.jpg`. Prompts: `media/look/_prompts/`. References: `media/look/_refs/`.

Tools written for this:
- `tools/gen/lookgen.py`: one prompt to one model, with the right input schema per model; `--parallel JOBS.tsv` runs 3 at a time.
  Costs land in `media/look/_costs.tsv` (list prices corrected for 2K output; cf.py under-counts qwen, krea and flux at 2K).
- `tools/review/coverage.py`: ink coverage. Paper colour = median of the brightest 40 % of pixels after a 2 px blur; a pixel is a
  mark if any channel is more than 28/255 away from it (measured at 1024 px). It also prints the marks' centroid and bbox and a
  paper-evenness number (luma spread of paper pixels over a 3x3 grid; higher = vignette or blotchy paper).
- `tools/review/look_sheets.sh N`: the labelled contact sheet.

Model keys: nbp = google/nano-banana-pro, sd5 = bytedance/seedream-5-pro, gpt2 = openai/gpt-image-2 (quality high),
qwen = alibaba/qwen-image-3.0-pro, flux2 = black-forest-labs/flux-2-max, krea3 = krea/krea-3, kling3 = klingai/kling-v3-image,
grok = xai/grok-imagine-image-quality, recraft / recraftpro = recraft/recraftv4-1 / -pro, codex = codex built-in image_gen (free).
The catalog has no MiniMax image model (only video, music, speech).

## Headline

| Use | First choice | Second | Notes |
|---|---|---|---|
| Earth plates (浅绛) | **qwen** | nbp, sd5 + style ref, codex | qwen has the finest real dry-brush; nbp the most "absorbent paper" |
| Elements (monkey, egg) | **nbp** | sd5 | nbp is the only one that really paints in a few strokes |
| Stage figure (splashed ink) | **sd5** | nbp, kling3, recraftpro | sd5 v2 nails the pose and Liang Kai wash |
| Pose sheet | **nbp** (with the L3 design as ref) | gpt2, sd5 | all three keep the design over 6 poses |
| Heaven (青绿) | **sd5** | nbp | |
| Rooms | **nbp**, rendering hand (a) | sd5, qwen | |
| Cliff for carving | nbp (crop the margin) | sd5 panel | weakest test; needs a round |
| 脸谱 album / row | **gpt2** | nbp | gpt2 obeys the 4x6 grid and the bare cell exactly |
| Shadow puppets | gpt2 (colour), nbp (silhouette, hand shadow) | | |
| Book object | gpt2 (neon), nbp / sd5 (flashlight) | | |

Dropped after round 1: flux2 (grey mottled paper, painted sea, invented calligraphy and a seal), krea3 and grok (soft digital
watercolour, timid), kling3 for plates (invents seals and waves; refs must be ≤ 2.5:1 aspect or it errors "Image aspect ratio is
invalid"), recraft standard (1344x768 only).

## L1 Storybook plate, earth (浅绛): 花果山, one corner

Target: marks 15-25 %, in the lower-left. Prompt v1 = the brainstorm's plate prompt adapted (below); v2 adds 马一角, 斧劈皴, the
boulder "pale grey ink with no colour, larger than a house", "no lines for waves"; v2style = v2 + Fan Kuan (public domain,
`refs/paintings/blocking/02_fan_kuan…`) as a style-only reference.

| Model | Variant | Cost | Coverage | Centroid | Verdict |
|---|---|---|---|---|---|
| qwen | v2 | $0.07 | 15.8 % | (0.18, 0.76) | **Best.** Finest dry-brush 皴, ochre/indigo 浅绛, clean corner, even paper |
| qwen | v1 | $0.07 | 14.0 % | (0.17, 0.78) | Same quality, peak cropped at the left edge |
| nbp | v1 | $0.13 | 9.3 % | (0.21, 0.78) | Most convincing ink on absorbent paper; boulder tinted blue; under budget |
| nbp | v2 | $0.13 | 12.9 % | | Boulder too big; faint border line |
| nbp | v2style | $0.13 | 19.3 % | | Denser, more Song; adds an album fold down the middle |
| sd5 | v2style | $0.08 | 16.6 % | (0.21, 0.76) | Style ref transformed it: crisp 斧劈, ochre and malachite touches |
| sd5 | v1 / v2 | $0.05 | 9.6 / 9.0 % | | Paints grey mist (breaks "mist is paper"); grey-pink paper |
| gpt2 | v1 / v2 | $0.19 | 9.0 / 12.2 % | | Obedient; slightly printed/illustration texture; yellow paper |
| codex | v1 | free | 4.7 % | (0.10, 0.82) | The most obedient corner and paper of all; too small; 1672x941 |
| recraftpro | v1 | $0.21 | 15.9 % | | Bold xieyi big-brush, not Song academy; white paper |
| recraft | v1 | $0.035 | 11.2 % | | Same, 1344x768 only |
| grok | v1 | $0.05 | 12.0 % | | Soft digital watercolour |
| kling3 | v1 | $0.03 | 16.0 % | | **Two red seals** and painted waves |
| krea3 | v1 | $0.06 | 10.1 % | | Coloured-pencil look |
| flux2 | v1 | $0.11 | 18.7 % | | Grey mottled paper (evenness 19), painted sea |

Best: `media/look/L1/qwen_v2.jpg`, `media/look/L1/nbp_v1.jpg`, `media/look/L1/sd5_v2style.jpg` (and `codex_v1.jpg` for restraint).

Winning recipe (qwen, `size 2048x1152`, `prompt_extend false`, negative prompt `media/look/_prompts/L1_neg.txt`):
```
Chinese ink painting on unsized cream xuan paper, Southern Song academy style, Ma Yuan one-corner composition (ma yi jiao),
ink and light colour (qianjiang). One steep rocky peak rises from the bottom-left corner and fills only the lower-left fifth
of the sheet, above an unpainted sea. On its very summit rests a single smooth round boulder, pale grey ink with no colour,
larger than a house. Axe-cut texture strokes (fupi cun) in dark ink, pale ink washes, faint touches of ochre on the rock and
pale indigo in the hollows, a few dark moss dots. The brush is wet and the ink bleeds slightly into the absorbent paper.
Everything else, the upper three-quarters and the whole right side of the sheet, is bare unpainted paper: the sea and sky
are the paper itself, with no lines for waves. No sky, no clouds, no distant mountains, no birds, no sun, no border, no
seal, no text, no signature. Flat, even scan of the painting; no frame, no shadow, no vignette.
```
Negative: `text, calligraphy, seal, stamp, signature, border, frame, vignette, clouds, sun, birds, distant mountains, waves,
photorealistic, 3d render, cinematic, dramatic lighting, digital art, fantasy`. For nbp, drop "larger than a house" (it
obeys too literally). For sd5, always add a Song painting as a style reference ("ONLY as a reference for brushwork, ink tones
and the texture of old paper; do not copy its composition").

## L2 Elements

| Model | Element | Cost | Coverage | Verdict |
|---|---|---|---|---|
| nbp | monkey | $0.13 | 3.5 % | **Best.** Genuine 减笔: wet strokes, a flicked tail, two eye dots |
| sd5 | monkey | $0.05 | 5.2 % | Soft Japanese sumi-e blob; good cut-out |
| qwen | monkey | $0.07 | 7.2 % | Too many strokes (fur rendered) |
| kling3 | monkey | $0.03 | 5.7 % | Strokes, but a smiling cartoon face |
| recraftpro | monkey | $0.21 | 9.4 % | Literal fat strokes, glyph-like grinning face; white paper |
| gpt2 | monkey | $0.19 | 1.4 % | Tiny grey smudge |
| nbp | egg | $0.13 | 0.5 % | **Best brush:** one ring stroke, pale wash, a few dots |
| qwen | egg | $0.07 | 2.5 % | Reads most as stone; outline is pencil-like |
| gpt2 / sd5 | egg | | 1.2 % | Pale, polite; sd5 has a halo stain |
| recraftpro | egg | $0.21 | 8.3 % | Radial paper stain around it: not cut-out friendly |

Best: `media/look/L2/nbp_monkey_v1.jpg`, `media/look/L2/nbp_egg_v1.jpg`, `media/look/L2/qwen_egg_v1.jpg`.
Recipe: the brainstorm's element prompt plus "abbreviated-brush (jianbi) manner of Liang Kai: wet strokes that bleed softly
into absorbent paper, one dry-brush flick for the tail, two dots for the eyes … about one tenth of its width … Flat even scan
of the painting, no shadow, no vignette" (`media/look/_prompts/L2m_v1.txt`, `L2e_v1.txt`). Elements come out small (0.5-4 %),
which is right for cut-outs: generate at 2K and scale up in the compositor.

## L3 Stage figure (Liang Kai splashed ink, 武生 monkey in 亮相)

| Model | Variant | Cost | Coverage | Verdict |
|---|---|---|---|---|
| sd5 | v2 | $0.05 | 7.1 % | **Best.** Leg raised, hand shading eyes (搭凉棚), staff behind, plumes; wet wash robe; original |
| nbp | v1 | $0.13 | 7.2 % | Clean, cap + plumes, peach patch; staff across rather than behind |
| kling3 | v2 | $0.03 | 11.6 % | Strongest splash and paper; reads as a heroic "Wukong" type (headband): watch originality |
| recraftpro | v1 | $0.21 | 13.0 % | Most like real 泼墨 brushwork; chimp face; leg not raised |
| recraftpro | v2 | $0.21 | 12.1 % | "Beaked mouth" taken literally (duck bill) |
| nbp | v2 | $0.13 | 5.7 % | Hairier, lighter; fine |
| sd5 | v1 | $0.05 | 7.0 % | Good; hand gesture is a wave, not shading |
| qwen | v1 | $0.07 | 9.2 % | **Gold circlet and 1986-TV-like face: originality flag** |
| flux2 | v1 | $0.11 | 15.3 % | **Fake calligraphy** in the corner; grubby paper |
| grok / gpt2 / krea3 | v1 | | 3.6-5.2 % | Small, timid or mottled digital texture |

Pose sheets (6 poses of a staff form, the nbp v1 figure as a design reference except recraftpro):

| Model | Cost | Verdict |
|---|---|---|
| nbp | $0.13 | **Best for animation:** design held in all 6, dry-brush staff trails ("the staff is a brush") |
| gpt2 | $0.20 | Equally consistent, cleaner silhouettes, slightly illustrative |
| sd5 | $0.08 | Biggest, clearest figures, but cute and smiling (drifts from deadpan ink) |
| recraftpro | $0.21 | Seven figures, inconsistent, skull-like faces |

Originality: none of the leaders resembles the 1961 film (no yellow tunic, no red-green face), Black Myth (no armour, no
realistic fur), Dragon Ball (no tail-and-gi child) or anime. Watch the red-around-the-eyes patch: it is generic opera
monkey make-up; keep it peach-shaped and small. qwen's gold circlet is the 1986 look: avoid qwen for the monkey.

Best: `media/look/L3/sd5_v2.jpg`, `media/look/L3/nbp_v1.jpg`, `media/look/L3/kling3_v2.jpg`; pose sheet
`media/look/L3/nbp_pose_v1.jpg` (and `gpt2_pose_v1.jpg`).

Winning recipe (sd5, `size 2560x1440`, no refs):
```
Chinese ink painting on unsized cream xuan paper in the manner of Liang Kai's "Immortal in Splashed Ink": the whole figure
is one or two broad wet washes of splashed ink with soft bleeding edges, plus a handful of quick abbreviated strokes (jianbi)
for the limbs, and the face drawn with a few fine lines. The figure: a newborn stone monkey as a Peking-opera martial
(wusheng) monkey performer, frozen in a liangxiang pose on one leg, the other knee raised high to the chest, the left hand
raised flat above the eyes to shade them as he peers into the distance, the right hand holding a long thin staff
horizontally behind the small of his back. Two very long pheasant-tail plumes rise from a small round cap and arc backwards
in two thin flowing strokes. A lean, wiry monkey face with a beaked mouth, and one small peach-shaped patch of cinnabar red
around the eyes: the only colour in the painting. Original design, drawn in the old idiom: not the 1961 Havoc in Heaven
animation, not the 1986 television make-up, no gold circlet, no armour, not Black Myth, not Dragon Ball, not anime. Full
figure, about a third of the sheet's height, centred, with bare unpainted paper all around. No ground line, no background,
no border, no seal, no text, no signature. Flat even scan of the painting, no shadow, no vignette.
```
(For recraftpro drop "beaked mouth".) Pose sheet prompt: `media/look/_prompts/L3_pose_r.txt` with `media/look/_refs/L3_design_nbp.jpg`.

## L4 Storybook plate, heaven (青绿)

| Model | Cost | Coverage | Verdict |
|---|---|---|---|
| sd5 | $0.05 | 57 % | **Best.** Azurite/malachite over ochre, cloud left as bare paper, tiny palace, clean paper |
| nbp | $0.13 | 55 % | Authentic silk seams and age; adds painted rivers; palace bigger |
| qwen | $0.07 | 60 % | Wallpaper of identical peaks |
| gpt2 | $0.19 | 46 % | Heavy ochre ground, painted cloud |

Coverage here is approximate (the paper estimate can catch pale cloud). All are under the 70 % target; ask for "peaks fill
three quarters of the sheet" next round. Best: `media/look/L4/sd5_v1.jpg`, `media/look/L4/nbp_v1.jpg`.
Recipe: `media/look/_prompts/L4_v1.txt`.

## L5 Room, 1988 attic, and the rendering hand

(a) = fine-line 白描 faces + light wash, a painting of night; (b) = gouache background + flat cel anime; (c) = in between
(brush outlines, flat watercolour fills on an ink-wash room). Refs: one composite `media/look/_refs/L5_cast.jpg` (Mama's face
cropped from the teahouse still, little Jade full body and face); kling3 needs `L5_cast_169.jpg`.

| Model | Hand | Cost | Verdict |
|---|---|---|---|
| nbp | a v2 | $0.13 | **Best.** Window lower right, one red pool, floor-light lines, deadpan child, jacket right, Mama ~30 |
| nbp | a v1 | $0.13 | Same quality; window right of centre |
| sd5 | a v2 | $0.12 | Very close second; the only one with **no letters in the neon**; Mama has a halo glow |
| sd5 | a v1 | $0.08 | Strong ink; good child |
| qwen | a v2 (text only) | $0.07 | Painterly, red hands from dishwater, good floor light; less "ink" |
| recraftpro | a v1 | $0.21 | Most real ink wash; faces cruder |
| gpt2 | a v1 | $0.21 | Muddy brown; Mama looks 60 |
| grok | a v1 | $0.06 | Pleasant illustration, pale |
| kling3 / krea3 / flux2 | a v1 | | Broken geometry / tiny / neon calligraphy + seal + border |
| nbp, sd5, qwen | c v1 | | Converges on (a) with heavier outlines; nothing gained |
| nbp, gpt2, sd5, kling3 | b v1 | | Works as anime stills, but the floor-light lines and paper vanish; nbp letterboxed |

Best: `media/look/L5/nbp_a_v2.jpg`, `media/look/L5/sd5_a_v2.jpg`, `media/look/L5/nbp_a_v1.jpg`. Recipe:
`media/look/_prompts/L5a_v2r.txt` (verbatim at the end of this file) with `L5_cast.jpg`.

### Recommendation: rendering hand (a)

1. It is the treatment's one-hand rule made visible: in (a) the attic and the 花果山 plate are the same paper, ink and wash, so
   the push from room into page needs no seam. (b) puts a glossy cel sticker on top of xuan paper.
2. The models are better at (a): nbp, sd5 and qwen all produced usable (a) frames on the first try with the deadpan child and
   the right jacket, and night reads as dark ink with one pool of red, which is exactly the ink budget's "Night 10-20 %".
3. (b) loses the details the brainstorm cares about (floor-light lines, dust, paper) and drifts to generic anime bedroom
   clutter (toys, teddies in L6 b).
4. Cost of (a): the faces are less "on model" than the anime canon, so likeness to Hold Fire/Moongazing Jade comes from the
   jacket, hair and glasses, not the anime face. Video models must keep the paper grain (check in the video bake-off). (c)
   is not a separate option: it collapses into (a).

## L6 Room, 2026 bedroom

Refs: `jade_wc.jpg` (watercolour Jade with glasses), `jade_sheet.jpg` (character sheet), `daughter_sheet.jpg`.

| Model | Hand | Cost | Verdict |
|---|---|---|---|
| nbp | a v2 | $0.13 | **Best.** Flashlight pool on the page, deadpan daughter in strawberries leaning in, jacket right |
| nbp | a v1 | $0.13 | Good, but the flashlight lights the bed, not the book |
| nbp | b v1 | $0.13 | Clean anime; cluttered bedroom, toys |
| sd5 | a v1 (one composite ref) | $0.08 | Very good painting of night; flashlight on the book; teddy-bear clutter; daughter less deadpan |
| sd5 | b v1 | — | Failed twice (504 upstream, with 3 refs and with 1); skipped |

Best: `media/look/L6/nbp_a_v2.jpg`, `media/look/L6/sd5_a_v1.jpg`. Recipe: `media/look/_prompts/L6a_v2.txt` with the three refs.

## L7 Rock for carving

| Model | Variant | Cost | Verdict |
|---|---|---|---|
| nbp | cliff v1 / v2 | $0.13 | Best 斧劈 brushwork and warm light, but **always paints a paper margin** (even when told not to): crop to the inner 85 % |
| sd5 | panel v1 | $0.05 | Best panel: a blank smooth slab inside 斧劈 edges, painting-like |
| qwen | cliff / panel | $0.07 | Fills the frame with true raking light, but reads as a photo of rock |
| sd5 | cliff v1 | $0.05 | Abstract streaks, not rock |
| nbp | panel v1 | $0.13 | Panel framed like a signboard |

Best: `media/look/L7/nbp_cliff_v2.jpg` (crop), `media/look/L7/sd5_panel_v1.jpg`, `media/look/L7/qwen_panel_v1.jpg`.
Needs another round (see end).

## L8 脸谱 album sheet

| Model | Variant | Cost | Verdict |
|---|---|---|---|
| gpt2 | album 3:2 | $0.19 | **Best.** Exactly 4x6, bare cell at row 3 col 4 as asked, all seven colours, aged paper, no text |
| nbp | album 3:2 | $0.13 | Most authentic album (foxing, gutter) but 4x8 grid |
| qwen | album 3:2 | $0.07 | 4x6 and bare cell right, but repetitive designs |
| gpt2 | row of 4 | $0.19 | **Best row:** bold red / white / black / gold, graphic, on bare paper |
| sd5 | row of 4 | $0.05 | More face than mask; good second |
| nbp | row of 4 | $0.13 | Album crease and faint circles behind |

Best: `media/look/L8/gpt2_album_v1.jpg`, `media/look/L8/gpt2_row_v1.jpg`, `media/look/L8/nbp_album_v1.jpg`.
Recipes: `media/look/_prompts/L8_v1.txt`, `L8_row.txt`. Check each mask design against real lianpu before use (models mix
conventions; the "white = treacherous" face must be the 粉白 type).

## L9 Shadow puppets and hand shadow

| Model | Variant | Cost | Verdict |
|---|---|---|---|
| gpt2 | puppet | $0.19 | **Best.** Translucent dyed hide, pierced openwork, rivets, rods |
| nbp | puppet | $0.13 | Good, but dark vignette around the screen |
| sd5 | puppet | $0.05 | Good, flatter |
| nbp | silhouette | $0.13 | **Best:** a convincing jointed monkey, pinhole openwork |
| sd5 | silhouette | $0.05 | Clean but a boy, not a monkey |
| nbp | hand shadow | $0.13 | **Best (frame-zero candidate):** red light, a readable monkey-head shadow over a landscape book |
| gpt2 | hand shadow | $0.19 | Shadow reads as a dog/bear |
| sd5 | hand shadow | $0.05 | Shadow reads as a heart |

Best: `media/look/L9/gpt2_puppet_v1.jpg`, `media/look/L9/nbp_sil_v1.jpg`, `media/look/L9/nbp_hand_v1.jpg`. All are
photographic, not painted: fine for the car-window shadows (light on glass), but the hand shadow for the thumbnail should be
re-run in hand (a) or composited from a real hand-shadow silhouette over our own plate.

## L10 The open storybook as an object

| Model | Variant | Cost | Verdict |
|---|---|---|---|
| gpt2 | neon | $0.19 | **Best.** Mountain lower-left, blank column, neon raking in from a window |
| sd5 | neon | $0.05 | Painted hand (a), red light as a wash; good |
| nbp | neon | $0.13 | Composition exact, but the "neon" is a red brush stroke painted across the book |
| gpt2 / nbp / sd5 | flashlight (worn book) | | All good; nbp brightest pool, sd5 most painting-like, gpt2 most object-like |

Best: `media/look/L10/gpt2_neon_v1.jpg`, `media/look/L10/sd5_neon_v1.jpg`, `media/look/L10/sd5_torch_v1.jpg`. These are
layout references only; the treatment builds the book in 3D.

## Known failure patterns, per model

- **nano-banana-pro**: paints paper margins, album folds and faint frames ("album leaf" instinct); writes letters into neon;
  takes size words literally ("larger than a house"); tints stones blue. Best brush realism and multi-ref likeness.
- **seedream-5-pro**: paints grey fog unless given a style reference; grey-pink paper; with 3 references it timed out
  (two 504 "Upstream service unavailable" after ~15 min; one composite ref works); 1.5-4 min per call. Best stage figure and 青绿.
- **gpt-image-2**: most literal obedience (grids, counts, bare cell) and the best design graphics; yellowish paper; ages
  Mama ~30 to ~60; $0.19-0.21 a call; ~70 s.
- **qwen-image-3.0-pro**: finest landscape texture and cheap; no reference input; gives the monkey a gold circlet (1986 look);
  repeats motifs on full frames; neon letters. Use `size WxH` (with an x) and `prompt_extend:false`.
- **recraft v4.1 (pro)**: bold xieyi, white paper, cartoon faces; std is 1344x768 only, `size` must be an aspect like "16:9".
- **kling-v3-image**: invents red seals and waves; reference image must not be wider than ~2.5:1.
- **flux-2-max**: grey mottled "aged" paper, invents calligraphy and seals.
- **grok-imagine-image-quality**: needs `response_format: b64_json` (zero-retention account); soft digital watercolour.
- **krea-3**: references must be URLs (not tested); pale, timid.
- **codex image_gen** (free): works headless with
  `codex exec -s workspace-write --skip-git-repo-check "<prompt> … save to <abs path>" < /dev/null`; without `< /dev/null`
  it hangs on "Reading additional input from stdin". 1672x941. Very obedient restraint (L1). It shares one lock with the
  other agents' codex jobs, so it is slow to get a turn. CODEX_L23_RESULT

## Needs another round

1. L7 cliff: a full-bleed painted cliff without a margin (try qwen with a Song style ref, or nbp at 4K and crop).
2. L4: push coverage to ~70 %; try sd5 with a Wang Ximeng detail as style ref once `refs/paintings` has one.
3. L9 hand shadow and L10 neon in hand (a).
4. Neon signs: every model writes glyphs; build the sign in code (mirror-reversed, invented name) and ask for "a plain red glow".
5. L3: run the sd5 v2 recipe as a pose sheet; pick one monkey design and lock it as the canon sheet.
6. Likeness check of Mama and little Jade by Jade.

## Spend by model (corrected list prices)

| Model | Calls | Spend |
|---|---|---|
| grok | 3 | $0.16 |
| recraftpro | 7 | $1.47 |
| gpt2 | 15 | $2.85 |
| recraft | 2 | $0.07 |
| qwen | 12 | $0.84 |
| nbp | 26 | $3.48 |
| krea3 | 3 | $0.18 |
| sd5 | 22 | $1.20 |
| kling3 | 6 | $0.16 |
| flux2 | 3 | $0.36 |
| **total** | 99 | **$10.78** |

Project ledger after this task (`tools/gen/spend.py`, includes any other agents' calls): TOTAL $10.57 of $600 cap  (119 billed items; list-price estimates). Failed calls (HTTP 4xx/504) are not billed; codex calls are free.

## Appendix: L5 (a) recipe, verbatim (nbp, 16:9 2K, ref `media/look/_refs/L5_cast.jpg`)

```
A Chinese painting of night, ink and light colour on cream xuan paper, in one hand: fine-line baimiao outlines for the faces and hands with light colour washes, and dark ink washes for the room, the paper grain showing through. A sloped-ceiling attic above a restaurant, 1988, seen from a low seated eye level. The ceiling slopes down to the right; in the lower right corner, at floor level, one small dusty window with red neon glowing outside (no readable letters), throwing one pool of red light across the mats. Bare wooden floorboards; between the boards, thin bright lines of warm amber light come up from the kitchen below. Floor mats and folded blankets. On the mats, left of centre, sits a mother about 30 years old, wavy shoulder-length black hair, thin glasses, an apron over a plain blouse with her sleeves pushed up, hands reddened from dishwater, an open picture book across her knees; beside her, her five-year-old daughter with straight black hair in a half ponytail and a deadpan, watchful, unsmiling face, wearing a cropped white jacket with an orange band across the chest and arms and a small pale-blue dot on the left chest. Faces drawn in delicate fine ink lines with a light flesh wash, as in a Song or Ming figure painting, not anime. Everything outside the red pool and the floor lines sinks into dark ink wash. The image is a painting on paper, not a photograph and not a digital render. No text, no signature, no seal, no border.

Reference image: the left part shows the mother's face (use the older woman, but make her about 30 years old); the middle and right show the daughter's hair, face and jacket. Use them for likeness only; repaint everything in the fine-line ink-and-wash painting style described.
```

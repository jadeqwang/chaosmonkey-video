# LOG v3 BOOK team (mountain, heaven, ledger pages), preview_v3
<!--CKPT-->
## CHECKPOINT 2026-11-17 20:01
final, after the polish round (see `## DONE` and `## POLISH ROUND` at the end). No relay jobs pending. All BOOK comps and
sheets (`work/review/comp_v3/`) are current. Render+sheet: `work/book3/do.sh ID [OUT] [--fresh]`, TMPDIR=work/tmp.
<!--/CKPT-->

## READY FOR OTHER TEAMS
- **Inscription helper is usable** (14:40): `tools/ink/inscription.py`. Usage is the 10 lines at the top of that file:
  `from tools.ink.inscription import inscription; INS = inscription(ctx, 'B5', box=(x, y, w, h), paper=P)` in setup(),
  `INS.draw(frame)` in render(). box = the blank, in 1920x1080 authoring px; columns top-right, right to left; one 悟空
  seal. 60 px characters at 1080p in every shot (do not pass px). Keys = first column of `design/text/lyrics_zh_v3.txt`.
  Font: Ma Shan Zheng (OFL), `refs/fonts/mashanzheng/`; licence in `refs/fonts/FONTS.md` ("v3 addition").
  Proof: `work/review/comp_v3/_inscription_proof.jpg`.
- **Medium switch helper is usable** (14:55): `tools/ink/medium.py`, documented in `tools/ink/README.md` §15.
  `MED = Mediums(ctx.W, ctx.H, seed)`; `frame = MED.switch(frame, t, pick_chops(ctx.timing, t0, t1), paper=P.rgb)` as
  the last step of render(). Paper-cut -> rubbing (paper edge) -> shadow puppet, held 4 frames, hard cuts, no doubles.
  Proof: `work/review/comp_v3/_medium_switch_proof.jpg`.
- NOTE (machine): /tmp (tmpfs, 16 G) is 99 % full from other sessions' scratch; keep scratch in `work/`.

## Working notes (BOOK v3)
- Scratch: `work/book3/`. v2 backups: `media/comp/_v2/`, `shots/_v2/`. Sheets: `work/review/comp_v3/<ID>.jpg`.
- Text file replaced by the director's proofread v2 (15:xx): parser already skips `#` and blank lines; Ma Shan Zheng
  covers every character of v2 (re-checked); proof sheet re-rendered. Inscriptions are data-driven (key -> file): a
  text edit needs only a re-render of the shot. Longest column is now 9 characters (B3): give boxes >= 660 px height.
- E4 done (v3 hand plate C_master_sleeve_v3_1.jpg, framing x1.45, inscription left).

## B3 FIRST-FRAME FRAMING (for the ATTIC team's over-shoulder push; fixed 2026-11-17, will not change)
- B3 frame 0 is the flat spread exactly as `media/layout/attic88/v3_LAP_ots_push_end.json` ends: the spread quad
  overfills the frame (quad x -64..1985, y -143..1223 px at 1920x1080).
- Flat page art for your warp: **`media/comp/pages/B3_page.png`**, 3072x2048 (1.5:1, the layout's spread aspect),
  both pages, gutter at x=1536, UNLIT book paper ('new', seed 1988). Map its four corners to the sidecar's `spread`
  quad (TL, TR, BR, BL).
- B3's first frame shows the spread-normalised rectangle **u 0.031..0.969, v 0.105..0.895** (u, v from the spread's
  top-left), i.e. page-art px x 96..2976, y 214..1834; scale 0.6665 frame px (1080p) per page-art px; nothing outside
  the paper is in frame. Picture: 花果山 lower left (left page), sea and sky bare, inscription upper right (right page).
- B3 frame 0 carries no neon cast any more (flat neutral book paper). If your last frame is red-lit, dissolve 6-8
  frames, or tell me the cast (RGB multiply) and I will put it on B3's first second.
- The same contract will hold for K2b (bedroom `LAP_ots_push_end`): page art `media/comp/pages/K2b_page.png`.
- E2 done: h3 take 1 (living troop) keyed to our paper, slow push, print column kept + inscription. C1 done (inclusions + reading points, rubbing held 5 f x2, inscription). B3 v3 multiplane written (see framing above).

## Per shot (v3), state at the time of writing
Sheets: `work/review/comp_v3/<ID>.jpg` (12 frames). All comps 960x540, 24 fps, exact frame counts (checked by do.sh).

| Shot | Status | On screen now | Sources / notes | Weak |
|---|---|---|---|---|
| B3 | done | Frame 0 = the flat spread (framing above); the push crosses the page and the picture separates into planes (far ridges, summit, mist band, near cliff, two foreground pines) with true parallax; mist flows; inscription on the right page leaves frame | `shots/B3.py` (Scene; layers registered at frame 0 by `aligned()`), B_master_L_* + C_ridge/C_pine | first 1.6 s is affine-layer parallax; from 27.75 the travel inside is a minimax/h3 dolly animated from our own frame (x3 speed, tone-matched): the speed dips for ~2 frames at the join |
| B4 | done | Macro: one stroke of one 千字文 character being cut by the edge of the sunlight (blank and shaded ahead of the edge, chisel-fresh behind); widens and travels R->L while the terminator runs ahead and columns stand in rectangular fields of different sizes separated by channels; cinnabar seeps into cuts well behind the edge; on "moonlight" night falls and a moon-edge crosses L->R cutting a finer column in every gap; gold (then silver) dust rises from every cut into the mist band; no carvers | `shots/B4.py`, engine `shots/_carve.py` (time-varying depth, `shade`, `Dust`); two rows of B_cliff_run (seam hidden in the mist band) | macro stone is plain; dust is fine at 540p; the pull to wide is fast (1.5 s) |
| B5 | done | (a) tilt up the peak, gold flecks climb the mist into the stone; (b) on the drum dropout cut to the smooth stone: faint columns inside it like inclusions, the last flecks sink in, three points of warm light read down a column one after another | `shots/B5.py`, `_carve.Inner` (also used by C1/C4/C5b/C6) | the cut at 37.885 is a hard cut inside the shot (v2 held on the wide) |
| C1 | done | The stone as B5 leaves it (two more reading points), crack on "It split apart", medium switch to RUBBING on chops 1 and 3 (5 frames each, paper edge), inscription | `shots/C1.py` | - |
| C4 | done | Egg, faint columns inside, one slow reading point, inscription top right | `shots/C4.py` | inclusions are barely visible at 540p (meant to be) |
| C5b | done | As v2 (mist sleeve over the egg) + inner columns + inscription | `shots/C5b.py` | mist still reads as a soft wipe |
| C6 | done | The reading points quicken, run down every column and run together into lines of gold; trembling, cracks, pressed to the crash. (v2's gold-up-the-cliff half is gone: one idea, one frame) | `shots/C6.py` | - |
| D4 | done | A breath of mist crosses ONE carved 通; it turns to gold on "通"; cut wide on "百": gold threads jump from 通 to the 11 carved characters sharing 辶, then each passes it on through its other component | `shots/D4.py`, `shots/_tong.py` | close-up carving is soft (2x plate) |
| D5 | done | Pull-back while generations light on the measured beats (11 / 26 / 66 / 154 / 118 / 16 true jumps; 104 lit by "hundred"), threads for the first three generations then they sink to a faint constellation and fade on the gong, where the 64 unreachable characters light too; whole cliff carved gold; inscription | `shots/D5.py`; plate `B_cliff_mid_v3_bare.jpg` (ladders painted out) | no medium switch (no measured chop in D5); the plate ends at its bottom edge |
| E2 | done | The troop alive (h3 take 1 keyed to our paper): grooming pairs, two swinging in the pines, walkers; print column + inscription; slow push | `shots/E2.py` | some figures smear for a few frames mid-slope |
| E4 | done | Redrawn natural hand (all joints joined), closer framing, lean on 100.9, inscription left | `shots/E4.py`, plate `elements_E4/C_master_sleeve_v3_1.jpg` | - |
| G2 | done | He tugs at the band (kling-v4 from our plate, on twos), jolts and margins as v2, both sung lines as inscriptions (the second arrives with its line) | `shots/G2.py` | band is keyed as gold wash, not opaque gold leaf |
| H5 | done | v2 + her shadow is smooth pale stone with the faint columns inside it and points of light reading down them; inscription | `shots/H5.py` (carving from `shots/_v2/B4.py`) | shadow is a flat grey shape; ring crosses characters |
| H6 | done | A curled hair rides the wind (bobs, one tumble, pulled straight by three gusts); over the last 2 s the canon storybook monkey (running, plumes, red face) comes up out of it from the tail root forward (the hair is his tail) and leaves the page; inscription (3 columns) | `shots/H6.py`; figure cropped from `design/characters/monkey/monkey_storybook_figures.jpg` | the hair itself is a clean procedural line |
| J2 | done | v2 + 37 pale-gold threads (3 generations of true jumps from 過) across the carved peak in the first second | `shots/J2.py` | carving itself barely reads on the blue-green peak, so the threads carry it |
| J5 | done | v2 pull-back; medium switch RUBBING (200.675) then SHADOW PUPPET (201.03), 4 frames each, shown clean (not torch-lit); inscription 一通百通 static on the page, revealed by the pull-back; faint re-press of the seal on (百通) | `shots/J5.py` | - |
| K3 | done | v2 + inscription 一笔勾之 (pale, on the dark left) | `shots/K3.py` | - |
| K4 | done | v2 + a small hand comes in, takes the page corner, carries it over, rests, withdraws (3 turns); inscription on the dark right | `shots/K4.py`, `H_v3_pages/hand/hand_1.png` | hand is a still cut-out (no finger motion) |
| K5 | done | v2 + inscription 簿上尽除名 (pale, on the dark beyond the book) | `shots/K5.py` | - |
| I3b | done | Peach Banquet before it begins: laid table on its terrace, screen, fans, peaches; immortals arriving in rank on clouds (emperor and Queen Mother first); typeset name slips at 6 places, the 4th place bare; monkey watching from his cloud; push to the bare place | `shots/I3b.py`, page `I3b_page.png` | faint inpaint mark where the 4th slip was |
| K2b | done | Hall of the Ten Kings: kings aside, judge and clerk, monkey on the desk with the brush over the ledger; push to the ledger; inscription | `shots/K2b.py`, page `K2b_page.png` | ledger pages blank in the painting (K3 is the close) |
| I2 (page) | done | Two beats: monkey defiant vs the host under banners (pagoda, fire-wheels, hawk and hound, thunder drum), in cloud; on "win" the host scattered; couplet inscription on the left page | `media/comp/pages/I2_full.mp4`, `I2_page.png`, `I2_page_b.png` | beat change is a hard cut |
| K1 (page) | done | Sleeper under the pine in solid ink; soul led on a rope by two fetchers in ghost-line toward the gate 幽冥界 (typeset); camera travels R->L | `media/comp/pages/K1_full.mp4` (frames 4973-5053), `K1_page.png` | ghost-line is pale under the torch |

### D4/D5 chain (true IDS jumps, cjkvi-ids; full list: `PYTHONPATH=. python shots/_tong.py`)
```
gen 1: 11 jumps (lit so far 12): 通>道(辶) 通>邇(辶) 通>過(辶) 通>隨(辶) 通>連(辶) 通>造(辶) 通>退(辶) 通>逸(辶) 通>達(辶) 通>途(辶) 通>遵(辶)
gen 2: 26 jumps (lit so far 38): 道>夏(自) 道>息(自) 邇>滿(巾) 邇>席(巾) 過>石(口) 過>郡(口) 隨>佐(左) 隨>服(月) 隨>朝(月) 隨>陰(阝) 隨>邙(阝) 連>轂(車) 連>輕(車) 造>回(口) 造>舍(口) 退>良(艮) ...
gen 3: 66 jumps (lit so far 104): 夏>慶(夂) 夏>終(夂) 息>感(心) 息>意(心) 滿>難(廿) 滿>漢(廿) 滿>浮(氵) 滿>滅(氵) 席>麗(广) 席>廉(广) 郡>隱(阝) 郡>阿(阝) 佐>優(亻) 佐>使(亻) 佐>功(工) 佐>涇(工) ...
gen 4: 154 jumps (lit so far 258): 慶>縻(广) 慶>磨(广) 慶>惠(心) 慶>思(心) 終>纓(幺) 終>約(幺) 終>納(糹) 感>鳴(口) 感>覆(口) 感>箴(咸) 意>莫(日) 意>昆(日) 意>端(立) 意>竟(立) 難>合(口) 難>右(口) ...
gen 5: 118 jumps (lit so far 376): 縻>京(小) 縻>楚(林) 磨>高(口) 磨>兄(口) 思>畫(田) 思>薑(田) 纓>好(女) 纓>姑(女) 約>寫(勹) 約>勿(勹) 鳴>馳(灬) 鳴>驚(灬) 鳴>鳳(鳥) 覆>履(复) 覆>微(彳) 箴>宮(口) ...
gen 6: 16 jumps (lit so far 392): 畫>肆(肀) 寫>兒(臼) 別>制(刂) 別>刻(刂) 別>刑(刂) 諸>詠(言) 諸>訓(言) 情>慎(忄) 情>惟(忄) 秦>奉(三) 吹>次(欠) 濟>分(刀) 弊>形(廾) 弊>升(廾) 弊>弁(廾) 弊>并(廾)
carved 456 unreached 64
```

### Alive pass (§13), added after the table above
minimax/h3 2K, 5 s, locked camera, first frame = our own page at the full-spread framing (page u 0.031..0.969,
v 0.105..0.895, 2560x1440; files `work/book3/gen/*_first.jpg`); specs `media/gen/specs/bk3_alive_*_h3_t1.json`.
All five takes accepted on a contact sheet + full-size frames: typeset writing, seals and figures hold.
- I3b: the procession glides in on its clouds, fans sway, the monkey scratches his head. K2b: the monkey walks along the
  desk and puts the brush to the ledger, the judge throws up his hands, the kings murmur. I2 (beat a): banners stream,
  fire-wheels spin, the monkey plants his staff (the hawk smears for about a second). K1: the fetchers walk the soul
  toward the gate, the sleeper breathes, mist curls at the gate.
- In the comps the clip replaces the still inside that framing (`PageShot(clip=...)`, tone-matched, feathered); camera
  and torch are ours. ROOM TEAMS: to have the page move in your over-shoulder shots, map the clip frames onto the same
  rectangle of the page quad (the `*_page.png` still is the fallback and matches clip frame 0).
- B3: `media/gen/bk3_alive_B3_h3_t1_d2fdbf4817.mp4` = a real dolly into the painting from B3's own frame at 27.75.

## Helpers (API)
- `tools/ink/inscription.py`: `inscription(ctx_or_(W,H), key=None, box=(x,y,w,h), paper=None, text=None, px=None,
  seal='悟空', seed=0, ground='paper'|'dark', colour=None)` -> `Inscribed` with `.draw(frame, opacity=1, dx=0, dy=0)`,
  `.T`, `.seal`, `.seal_pos`, `.bbox`, `.px`, `.columns`; `table()`, `columns_of(key, text)`. Data-driven from
  `design/text/lyrics_zh_v3.txt` (skips `#` and blank lines): a text edit = re-render.
- `tools/ink/medium.py`: `Mediums(W, H, seed)` with `.switch(frame, t, chops, paper=, mask=, hold=4, order=)`,
  `.papercut / .rubbing / .shadow(frame, paper, mask)`, `.render(name, ...)`; `pick_chops(timing, t0, t1,
  max_per_bar=2, min_gap=8)`; `medium_at(t, chops, hold)`. README §15.
- Shot-side libraries (BOOK only): `shots/_carve.py` (time-varying carving, `Dust`, `Inner`), `shots/_tong.py` (IDS
  chain, threads), `shots/_pages3.py` (traditional pages, `PageShot`).

## DONE 2026-11-17
Final report (also sent to the lead).
- **All BOOK shots have v3 comps** (960x540, 24 fps, exact frame counts verified with ffprobe; six spot-checked at
  1920x1080): B3 B4 B5 C1 C4 C5b C6 D4 D5 E2 E4 G2 H5 H6 J2 J5 K3 K4 K5 in `media/comp/`, plus I3b and K2b (mine), plus
  full-frame page comps `media/comp/pages/I2_full.mp4` (66 f, 4325-4391) and `K1_full.mp4` (80 f, 4973-5053), plus flat
  page art `media/comp/pages/{B3,I2,I2_page_b,I3b,K1,K2b}_page.png` (3072x2048, unlit) and `pages_v3.json`.
- v2 backups: `media/comp/_v2/`, `shots/_v2/` (H5 imports the v2 carved cliff from `shots/_v2/B4.py`).
- `shots/B3.py` keeps a v2 hook (`setup(None)` -> PAGE/BARE) because `shots/_rooms88.spread('hgs')` reads it; the
  spread is now 3072x2048 (was 4585x2420) and carries the inscription.
- Spend: $9.98 logged under tags `bk3_*` (ceiling $200).
- Weakest, in order: H5 (flat grey child shape); B4's macro stone surface (plain) and the 1.5 s pull from macro to
  wide; C5b (mist still a soft wipe); I2 (hawk smears ~1 s in the alive clip; beat change is a hard cut); K4 (hand is
  a still cut-out); D5 (plate ends at its bottom edge); G2 (band is a gold wash, not leaf).
- Not done: medium switch in D5 (no measured chop falls inside it); alive passes for B5(a) and C5b; the MANIFEST
  inscription-placement rule "top corner opposite the mass" is followed except where the frame is full-bleed rock
  (B4, B5a, D5, H5: inscription on a veil of mist at the right) and I3b/I2 (lower blank, the top is the procession).

## POLISH ROUND (lead's five points), done
1. **B3**: the halo was my low-frequency tone match between our frame and the clip: now one colour gain for the whole
   frame. Layers deepened (ridges at depth 7 and 5, summit 2.4, three foreground pines at 0.5 / 0.62 / 0.42, a second
   mist veil between cliff foot and pines); from 27.75 a NEW h3 dolly (take 3, animated from the new layered frame;
   first frame `work/book3/gen/B3_mid2.jpg`, rendered with env `B3_TCLIP=99`) travels up through the mist and ends
   close on the summit stone. Hand-over: the clip starts at the push's own speed and settles (4.2 -> 2.4 clip frames per
   film frame, blended); frame-difference dips 8.2 -> 6.0 -> 7.0 over the join (was 6 -> 0.5). Take 2 is a spare; take 1
   belongs to the old layers. `B3_page.png` re-exported (one more pine); the frame-0 framing contract is unchanged.
2. **D5 / D4 / J2 threads** (`shots/_tong.py threads`, `schedule(..., stagger)`): every jump is drawn source -> target
   over 3 frames with a bright bead at its head, on a darker ochre under-line; generation 1 is 3.4 px and held 0.8 s,
   generation 2 2.1 px, generation 3 1.3 px. The 11 jumps from 通 are dealt one at a time across 68.53-69.21 (D4, whose
   wide view is now zoom 0.66 so most of them land in frame); generation 2 from 69.50, 3 from 70.146, each staggered;
   a character lights when its thread arrives; all threads fade on the gong. J2 uses the same drawing in pale gold.
3. **H5**: the child stands in the uncarved gap between two inscription blocks, so the ring crosses no character; her
   shadow is translucent pale stone (the rock's fissures just showing through, a soft wet rim) with her OWN faint columns
   inside (`_carve.Inner`) and five points of light reading down them.
4. **C5b**: h3 take 2 animated from the shot's own first frame: a curling cloud-sleeve of mist rolls in over the egg and
   trails off (take 1 drew a silk ribbon: rejected). Our own page is kept wherever the clip agrees with frame 0.
5. **B4**: macro-to-wide pull 2.5 s (was 1.55), macro stone has grain, mottling and sparse quartz flecks.
Spend after this round: $12.58 (tags `bk3_*`).
Still weak: C5b's mist is whiter than bare paper and stylised (auspicious-cloud curls); D5 generation 3 is dense for
about half a second; J2's threads are brief; K4 hand static; I2 hawk smear.

## H5 change-back (lead, after the polish round), done
The child-shaped BLANK in lit writing is back: her cast shadow slants down-left from the raking light (LEAN 0.30 in
`shots/H5.py`), so the head and the ring sit in the uncarved gap between two inscription blocks (ring radius 110, no
character under it) while the body falls across the lit columns of the left block (the lower characters of two columns
are blanked). Inside it: the translucent smooth stone, her own faint columns, five reading points (kept).
84/84 frames, sheet `work/review/comp_v3/H5.jpg` rebuilt. Weak: the shadow is a slanted soft shape that reads as a
figure more by the head and ring than by its outline; the ring's lower arc passes over the shadow's neck (it floats
around the head, as in v2), not fully clear of her.

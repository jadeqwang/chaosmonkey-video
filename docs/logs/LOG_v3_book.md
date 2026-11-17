# LOG v3 BOOK team (mountain, heaven, ledger pages), preview_v3
<!--CKPT-->
## CHECKPOINT 2026-11-17 14:57
Resume rule: read this block, then the sections below. Scratch `work/book3/`; render+sheet `work/book3/do.sh ID`
(sheet -> `work/review/comp_v3/ID.jpg`, 1400 px copy `work/book3/_s_ID.jpg`). v2 backups in `media/comp/_v2`, `shots/_v2`.
- **Done (rendered, sheet looked at):** helpers (`tools/ink/inscription.py`, `tools/ink/medium.py`, README §15);
  E4 (redrawn hand); C1 (inclusions + reading points, rubbing switch x2, inscription); E2 (h3 living troop);
  B3 (multiplane push from the flat page; page art `media/comp/pages/B3_page.png`).
- **In progress:** B4 (`shots/B4.py` + engine `shots/_carve.py`: light-as-carver, macro -> fields, moon pass, dust;
  tuning cut shading/dust; render running). B5 (`shots/B5.py` written, not yet rendered).
- **Next, in order:** B5, D4/D5 (IDS jumps; data `refs/data/cjkvi-ids/ids.txt`; bare cliff plate
  `design/plates/B_huaguoshan/B_cliff_mid_v3_bare.jpg`), J2/J5 threads, C4/C5b/C6 (egg with inclusions via
  `_carve.Inner`), H5 (columns in the shadow), H6 (curled hair -> monkey), G2 (clip below), K3/K4/K5 (inscriptions,
  hand), page art I2 / I3b (rank staging, name slips, bare seat among them) / K1 / K2b (+ K2b_page.png), then §13
  "alive" passes if budget/time allow.
- **Relay jobs:** none pending. Collected: `media/gen/bk3_E2_h3_t1_158c37e912.mp4` (USED in E2), `bk3_E2_h3_t2_*`,
  `bk3_E2_kling4_t1_*` (spares), `bk3_G2_h3_t1_fafb4a5efb.mp4`, `bk3_G2_kling4_t1_0f0c8d5083.mp4` (G2 tugging at the
  band; not yet judged). Specs `media/gen/specs/bk3_*.json`. Image edits: `C_master_sleeve_v3_1.jpg` (USED),
  `_v3_2.jpg` (spare), `B_cliff_mid_v3_bare.jpg`.
- **Spend so far:** about $5.0 (5 video, 3 nano-banana-pro edits) of $200.
- **Decisions:** inscription font Ma Shan Zheng; 60 px at 1080p everywhere; on full-bleed rock shots (B4, B5a) the
  inscription sits on a static veil of mist at frame right. Spread art is 1.5:1 to match the layout quads. Night in B4
  kept warm (v2 note: cement-grey). Dust = gold-leaf flecks (洒金), silver under the moon. C1 switches: chops 1 and 3
  only (max two per bar), 5 frames each.
- **Open questions for the lead:** none blocking. I2/K1 full-frame comps will be written to `media/comp/pages/`
  (not over the BED team's `media/comp/I2.mp4` / `K1.mp4`).
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

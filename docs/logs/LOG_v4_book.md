# LOG v4 BOOK team (H5/H6, C5b, K5, E4, K2b/K3/K4, G2, I4/J1-page), preview_v4
<!--CKPT-->
## CHECKPOINT 2026-11-19 00:05 (final, after H6 round 3)
All BOOK v4 shots delivered. H6 round 3 DONE: media/comp/H6.mp4 = A3 (107 f): kling opening 36 f (hair in the gale,
strand works loose, cliffs dissolve) + kling-v4 multi-keyframe take t4 (5 Codex-painted keys: strand -> root swells ->
3 wet ink strokes make a crouched monkey ~0.3 H facing right, tail = remaining strand ending in the same curl, body
length; red scarf, then yellow) + kling exit out_t2 (somersault out left, tail drawn out after him, bare by f98) +
7 f breathing paper. Model layer shifted rigidly left (91 -> 298 px at 1080p, ramped) to keep clear of the
inscription. Blind ranking r3: A2 first, round-2 last (work/book4/H56/blind_r3/RANKING.md). Notes
work/book4/H56/H6R_NOTES.md, build work/book4/H56/final_h6r.py (SHIFT=1 ... A3). Round-2 kept as
media/comp/_cand/H6_r2final.mp4. No relay jobs pending, no subagents running. Spend $61.24 of $130 (round 3 $15.98;
all 9 H6R keys via Codex).
<!--/CKPT-->

## READY FOR OTHER TEAMS
- **J1 page text** (PAGES, 2026-11-18): `media/comp/pages/J1_page_v4.png` and `J1_page_charlit_v4.png` (3392x1785, identical
  registration to J1_page.png): Chinese 五官俱备 / 四肢皆全 (key D1, inscription.py, seal) and "Born fully formed" (EB Garamond
  Italic, ink) static on the blank sky of the left page, right of the summit. Boxes in page px: `media/comp/pages/J1_page_v4.json`.
  Text-only layers for 3D objects: `J1_page_v4_text_T.png` (multiply) and `J1_page_v4_text_alpha.png`. Whole right page is bare
  paper if the push crops this area. Script `shots/_book4_j1text.py`.
- K2b page art v4 (LEDGER): `media/comp/pages/K2b_page_v4.png` (3072x2048, unlit, same contract and inscription as K2b_page.png; the monkey is in costume B and the ledger is turned so its columns run vertically; ledger pages blank in the still, the writing lives in the clip composite `shots/_book4_k2b.py`). K2b_page.png untouched.

## C5b flow contract (for ATTIC's C5a)
The wind enters C5b at the LEFT edge, already moving at C5b frame 0 (song frame 1311, 54.625 s), travelling left ->
right and rising. In the shipped C5b (cand C) the first ink stroke enters at y ~0.43 H at f2-4 (54.71 s), angled up to
the right. In fallback A (measured): front crosses x=0 at 54.505 s (song frame 1308), ~1290 px/s at 1080p, band
y 0.38-0.64 H at f0 widening to 0.21-0.69 H by f12. So in C5a the breath leaves Mama's lips at 53.22 s and should exit
frame RIGHT, rising, by ~54.6 s.

## Per shot (v4), state
| Shot | State | What / how | Files | Weak (ranked) | $ |
|---|---|---|---|---|---|
| C5b | done | Cand C: h3 2K take 2 (first frame = our plate with lines entering left) used only as a 'what the wind did' layer (frame / frame0, gated to change, inscription box excluded), tilted 10 deg to rise L->R, dissolved to paper from f42, multiplied onto our own egg/paper; inscription ours. Cand A: real 2D stable-fluids solve, egg obstacle, ~35 advected brush ribbons + mist (shots/_book4_C5b_A.py, _book4_wind.py). B: raw h3 / seedance (seedance drew clip-art clouds). | media/comp/C5b.mp4, shots/C5b.py (env C5B_CLIP/ANGLE/FADE0), _cand/C5b_*.mp4, sheets comp_v4/C5b_*.jpg, work/book4/c5b_cmp.jpg | motion is what h3 invented, not a solve; 1080p is an upscale of the 2K clip; faint mist-edge wedges f23-42; lines cross the egg's face rather than parting round it. 3 more h3 takes were prepared but the permission check denied the subagent's submit: not run. | 2.80 |
| E4 | done | gpt-image-2 repaint to costume B (try c, monkey 1.3x v3), kling-v4 1080p take 3 of 3 (plus seedance, h3 tested) at native 24 fps clip f0-78; finger crooks ~f11/22/33, tail attached, one S + flick; sleeve lean from 100.9 s as a small rigid rotation; inscription ours | media/comp/E4.mp4, shots/E4.py, work/book4/E4/ | faint tail-tip trail f52-73; head turns to the finger (more than a tilt) from f44; finger crook becomes a reach | 5.56 |
| G2 | done | costume B plate in grey ink (margins drain colour; band only gold), kling-v4 t3 (hands under the band, lift, clutch); 听话 typeset cinnabar 1.6x in the left margin, inks in on each sung (听话) 130.175 / 133.690 and stays; margin luma 238 -> 228 (= G1 last / G3 first) by dividing out _margins SHEET_LIFT locally | media/comp/G2.mp4, shots/G2.py, comp_v4/G2.jpg, G2_tinghua.jpg | far end of the band shows as a gold arc behind his hand from clip f56; costume grey not yellow/red (by design); 听话 placement judged on sheets only | 4.17 (incl. J1) |
| J1 page | done | D1 columns 五官俱备 / 四肢皆全 + 'Born fully formed' (EB Garamond Italic) static on the left page's sky; layers for WORLD's 3D | media/comp/pages/J1_page_v4*.png/.json, shots/_book4_j1text.py | I4's line has no Chinese in lyrics_zh_v3 | - |
| K2b | done | ledger repainted turned 90 deg (gpt-image-2), monkey costume B, h3 t2 alive clip; entries typeset in perspective onto the pages (孫悟空 column under the brush); push to z 3.4 by f31; stroke run f31-39 at 4.8x | media/comp/K2b.mp4, shots/K2b.py, shots/_book4_k2b.py, pages/K2b_page_v4.png, comp_v4/K2b_K3_match.jpg | oblique painting -> flat K3 page (only the stroke matches); fast plunge; brush hand smear at the end | 1.30+1.06 img |
| K3 | done | opens mid-stroke continuing K2b's (x 673, ~20 px/f), bold wet strike on 'crossed out' (213.805), hook out by ~f14; on 'single breath' (~216.2) the ink darkens and blooms; torch breathes, dust in the beam | media/comp/K3.mp4, shots/K3.py | near-still after f16; wide solid bar | - |
| K4 | done | no hand: code page-turn mesh (travelling bend, flutter, normal lighting, typeset both faces, cast shadow): leaf 1 lands on 'page' 218.22, leaf 2 lifts, falls back, goes over on 'looked' 220.92, leaf 3 lands on the 221.805 hit; last leaf stirs. kling/seedance rejected (text wiped / book redrawn) | media/comp/K4.mp4, shots/K4.py, shots/_book4_pageturn.py | landing ~1 f early on the hit; uniform soft shadow | 1.93 |
| K5 | done | 3 wet cells from MMAH strokes of different characters (IoU-checked against MMAH, by eye no real character), wet core + fibre feathering + pale bloom with broken tide-line; per cell the tide-line retreats then strokes thin from the ends and lift (cells 0.5/1.2/1.9 s; cell 1 gone on the 225.254 hit), bare ~226.6 s; lamp breathes, last damp spot dries, slow drift | media/comp/K5.mp4, shots/K5.py, comp_v4/K5.jpg, K5_wet_strip.jpg | bloom very pale; cells read character-like (intended) | 0 |
| H5 | done | minimax/h3 2K first+last (v3 cliff frame -> painted girl-of-strokes key) take 2: carved red characters lift off as strokes, arc, spiral into a vortex, assemble into the girl; source on twos -> de-duplicated (72/124) + RAFT optical-flow interpolation to 84 f; invented right-edge glyphs patched f0-44; inscription ours | media/comp/H5.mp4, work/book4/H56/final_h5.py, interp.py, hi/H5_final.mp4, comp_v4/H5.jpg, H5_diff.png | mild 3-frame cadence f44-62; girl small at the end; strokes are character-like shapes, not literal glyph strokes (the procedural A has literal MMAH strokes but ranked low blind) | see total |
| H6 (round 2, superseded by round 3 A3, see checkpoint) | replaced | kling-v4 first+last opening (H5 last -> hair streaming; cliffs dissolve; one strand works loose, 42 f) + h3 2K first+last growth (strand frame -> k3b monkey whose tail is the strand: wet ink silhouette grows from the root, red scarf strokes, yellow floods last, 28 f) + kling-v4 somersault-out take 1 (30 f) + 7 f of our breathing paper; all speed-ups by frame selection, no blending | media/comp/H6.mp4, work/book4/H56/final_h6.py, hi/H6_final.mp4, comp_v4/H6.jpg, H6_growth.jpg, H5_H6_seam.jpg, FINAL_NOTES.md | strand far bigger than the monkey (reads as running along it, not his tail) ; speed-ups 1.2-3.6x; seam near-match only (girl slightly larger, red ribbons gone); monkey a full painted render, not 'a few strokes'; model paper vs our paper at the end crossfade | see total |
| H5/H6 alternatives | kept | procedural A (real MMAH strokes as PBD ribbons, shots/_book4_strokes.py; rounds 1+2), all video/hybrid candidates in media/comp/_cand/; blind ranking work/book4/H56/blind/review/RANKING.md | | | |
- 21:15 check (coordinator): media/comp/pages/J1_page_v4.png restored by WORLD by re-running shots/_book4_j1text.py:
  3392x1785, peak + egg on the left page, 'Born fully formed' + 五官俱备/四肢皆全 + seal right of the summit, right page
  bare: it is what PAGES made. OK.

## DONE 2026-11-18 22:10 (reopened 22:20 for H6 round 3)
Report sent to the lead (final message). Comps verified with ffprobe: H5 84, H6 107, C5b 58, E4 79, G2 166, K2b 40,
K3 81, K4 168, K5 110 frames, all 960x540, no audio. Spend $45.26 of $130.

## DONE 2026-11-19 00:05 (H6 round 3)
H6 = A3, 107 f verified. Weak: speed-ups by frame selection 3-5x (ink-only monkey ~0.4 s on screen); full coloured
render from ~f66; somersault smears f86-92; the strand root brushes the inscription at f38-42; H5's red ribbons
vanish inside H5's own last 3 frames (only a remnant is carried into H6 f0-7). Seen on sheets/strips only.

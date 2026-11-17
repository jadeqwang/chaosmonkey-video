# Look bake-off (image models)

Status: IN PROGRESS (checkpoint). Driver: `tools/gen/lookgen.py`; coverage: `tools/review/coverage.py`
(paper = median of the brightest 40 % of pixels after a 2 px blur; coverage = share of pixels more than 28/255 from it in any
channel, measured at 1024 px). Outputs: `media/look/<test>/<model>_<variant>.jpg` + `.txt`; costs `media/look/_costs.tsv`.

## L1 (round 1, all models) - notes
- nbp: real brush on absorbent paper, obedient corner, 9 % coverage; boulder painted blue (fix).
- qwen: finest qianjiang dry-brush texture, obedient corner, 14 %.
- gpt2: clean corner, a bit illustration-like, 9 %.
- recraft / recraftpro: bold xieyi big-brush, not Song academy; strong for splashed ink.
- kling3: invented two red seals and painted waves (disobeys); real-looking drips.
- flux2: grey mottled 'aged' paper, painted sea, uneven paper (19 pts).
- sd5: painted grey mist, peak centred, pink-grey paper.
- krea3, grok: soft, digital watercolour.

## L3 (round 1) - notes
- nbp, recraftpro, kling3, sd5 lead. qwen gave a gold circlet / 1986-TV-like face (flag). flux2 drew fake calligraphy.

## Checkpoint 2 (round 1-3 reviewed)
- L1 v2 ("boulder pale grey, larger than a house") made the boulder too big on nbp/gpt2; qwen_v2 and sd5_v2style
  (Fan Kuan as style ref) are clean. Style ref fixed sd5's grey-mist habit; on nbp it added an album fold line.
- codex image_gen (free) works headless (`codex exec -s workspace-write --skip-git-repo-check "..." < /dev/null`; without
  `< /dev/null` it hangs on "Reading additional input from stdin"). L1 codex_v1: the most obedient corner (4.7 %), 1672x941.
- L2 monkey: nbp is the only true few-stroke jianbi; sd5 soft sumi-e blob; recraftpro literal strokes but cartoon glyph face.
  Egg: nbp (one ring stroke + dots) best brush; qwen reads as stone but pencil-like outline.
- L3 v2: sd5_v2 best (pose, Liang Kai wash, original); kling3_v2 strongest splash; recraftpro_v2 beak too literal.
  Pose sheets: nbp_pose_v1 and gpt2_pose_v1 both hold the design across 6 poses; nbp adds dry-brush staff trails.
- L4: sd5_v1 closest to Wang Ximeng (clean paper cloud, tiny palace); nbp_v1 authentic silk seams but painted rivers.
- L5a: nbp_a_v2 best (window lower right, red pool, floor-light lines, deadpan child, fine-line faces); qwen_a_v2 and
  sd5_a_v1 close. Every model writes letters into the neon (composite the neon in code). (b) works on nbp/gpt2/sd5 but
  the floor-light lines get lost and it fights the paper.

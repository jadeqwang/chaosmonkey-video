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

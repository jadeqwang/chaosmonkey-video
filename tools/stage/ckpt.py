"""Rewrite the CHECKPOINT block at the top of docs/logs/LOG_v3_stage.md from work/stage/v3/ckpt.md.  PY tools/stage/ckpt.py"""
import re, time
p = 'docs/logs/LOG_v3_stage.md'
s = open(p).read()
body = open('work/stage/v3/ckpt.md').read().strip()
block = f"## CHECKPOINT {time.strftime('%H:%M')}\n{body}\n\n---\n"
s = re.sub(r'## CHECKPOINT .*?\n---\n', '', s, flags=re.S)
head, rest = s.split('\n', 1)
open(p, 'w').write(head + '\n\n' + block + rest.lstrip('\n'))

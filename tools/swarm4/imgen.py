"""Stage team v4: one gpt-image-2 (or other lookgen key) call. Writes OUT (.jpg) and OUT.txt beside it.
    PY tools/stage/imgen4.py OUT.jpg PROMPT.txt [--m=gpt2] [--ref=path ...] [--size=3840x2160] [--force]"""
import json, os, subprocess, sys, time
sys.path.insert(0, 'tools/gen')
import cf, lookgen
a = sys.argv[1:]
pos = [x for x in a if not x.startswith('--')]
out, pf = pos
key = ([x.split('=')[1] for x in a if x.startswith('--m=')] or ['gpt2'])[0]
refs = [x.split('=', 1)[1] for x in a if x.startswith('--ref=')]
size = ([x.split('=')[1] for x in a if x.startswith('--size=')] or ['3840x2160'])[0]
prompt = open(pf).read().strip()
inp, price = lookgen.build(key, prompt, refs, '', '16:9')
if key == 'gpt2':
    inp['size'] = size
model = lookgen.MODELS[key]
if os.path.exists(out) and '--force' not in a:
    print('exists', out); sys.exit(0)
os.makedirs(os.path.dirname(out), exist_ok=True)
t0 = time.time()
paths = cf.generate(model, inp, out, tag='sw4_' + os.path.basename(out)[:-4])
p = paths[0]
if p != out:
    subprocess.run(['convert', p, '-quality', '94', out], check=True); os.remove(p)
meta = {k: v for k, v in inp.items() if k not in ('prompt', 'images')}
open(out[:-4] + '.txt', 'w').write(f"model: {model}\nparams: {json.dumps(meta, ensure_ascii=False)[:600]}\nrefs: {refs}\n"
                                   f"secs: {time.time()-t0:.0f}\n\nPROMPT:\n{prompt}\n")
print('ok', out, f'{time.time()-t0:.0f}s')

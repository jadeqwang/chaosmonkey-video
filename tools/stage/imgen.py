"""Stage team v3: one image call. Writes OUT (.jpg) and OUT.txt (model, params, prompt) beside it.
    PY tools/stage/imgen.py OUT.jpg PROMPT.txt --m=sd5|nbp|gpt2 [--ref=path ...] [--aspect=16:9] [--size=4K]"""
import json, os, subprocess, sys, time
sys.path.insert(0, 'tools/gen')
import cf, lookgen
a = sys.argv[1:]
pos = [x for x in a if not x.startswith('--')]
out, pf = pos
key = [x.split('=')[1] for x in a if x.startswith('--m=')][0]
refs = [x.split('=', 1)[1] for x in a if x.startswith('--ref=')]
aspect = ([x.split('=')[1] for x in a if x.startswith('--aspect=')] or ['16:9'])[0]
size = ([x.split('=')[1] for x in a if x.startswith('--size=')] or ['2K'])[0]
prompt = open(pf).read().strip()
inp, price = lookgen.build(key, prompt, refs, '', aspect)
if key == 'nbp' and size == '4K':
    inp['image_size'] = '4K'
model = lookgen.MODELS[key]
if os.path.exists(out):
    print('exists', out); sys.exit(0)
os.makedirs(os.path.dirname(out), exist_ok=True)
t0 = time.time()
paths = cf.generate(model, inp, out, tag='stg3_' + os.path.basename(out)[:-4])
p = paths[0]
if p != out:
    subprocess.run(['convert', p, '-quality', '93', out], check=True); os.remove(p)
meta = {k: v for k, v in inp.items() if k != 'prompt'}
open(out[:-4] + '.txt', 'w').write(f"model: {model}\nparams: {json.dumps(meta, ensure_ascii=False)[:600]}\nrefs: {refs}\n"
                                   f"secs: {time.time()-t0:.0f}\n\nPROMPT:\n{prompt}\n")
print('ok', out, f'{time.time()-t0:.0f}s')

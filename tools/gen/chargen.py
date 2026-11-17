#!/usr/bin/env python3
"""Character-design driver: one prompt -> one model -> design/characters/<out>.jpg + .txt (prompt beside it).

    $PY tools/gen/chargen.py OUT_REL PROMPT_FILE --m=nbp [--ref=path ...] [--aspect=16:9] [--size=4K] [--dry-run]
    $PY tools/gen/chargen.py --parallel JOBS.tsv     # lines: OUT_REL MODEL PROMPT_FILE refs,comma,sep|- ASPECT SIZE ; 3 at once

OUT_REL is relative to design/characters/ (e.g. mama/mama_sheet_heads_nbp_v1.jpg).
Reuses lookgen.build() for the per-model input schema; adds nbp 4K and larger gpt2 sizes.
Costs append to design/characters/_costs.tsv.
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf  # noqa: E402
import lookgen  # noqa: E402

ROOT = cf.ROOT
BASE = os.path.join(ROOT, "design", "characters")
COSTS = os.path.join(BASE, "_costs.tsv")
GPT2_BIG = {"16:9": (3072, 1728), "3:2": (3072, 2048), "1:1": (2048, 2048), "4:3": (2816, 2112), "3:4": (2112, 2816),
            "2:3": (2048, 3072), "9:16": (1728, 3072)}


def run(out_rel, key, prompt_file, refs=(), aspect="16:9", size="2K", dry=False):
    prompt = open(prompt_file).read().strip()
    inp, price = lookgen.build(key, prompt, list(refs), "", aspect)
    if key == "nbp" and size == "4K":
        inp["image_size"] = "4K"; price = 0.24
    if key == "gpt2" and size == "4K":
        w, h = GPT2_BIG[aspect]; inp["size"] = f"{w}x{h}"; price = None
    model = lookgen.MODELS[key]
    if price is None:
        price = cf.estimate(model, inp)[0] or 0.25
    out = os.path.join(BASE, out_rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if dry:
        cf.generate(model, inp, out, tag="char", dry_run=True); print("price", price); return None
    if os.path.exists(out):
        print("exists, skip", out); return out
    t0 = time.time()
    try:
        paths = cf.generate(model, inp, out, tag="char_" + os.path.basename(out_rel)[:-4])
    except Exception as e:
        print(f"FAIL {out_rel}: {str(e)[:400]}", file=sys.stderr)
        with open(COSTS, "a") as fh:
            fh.write(f"{time.strftime('%H:%M:%S')}\t{out_rel}\t{key}\t0\tFAIL {str(e)[:120]}\n")
        return None
    p = paths[0]
    if p != out:
        subprocess.run(["convert", p, "-quality", "93", out], check=True); os.remove(p)
    meta = {k: v for k, v in inp.items() if k != "prompt"}
    with open(out[:-4] + ".txt", "w") as fh:
        fh.write(f"model: {model}\nparams: {json.dumps(meta, ensure_ascii=False)[:600]}\nrefs: {list(refs)}\n"
                 f"est_usd: {price}\nsecs: {time.time()-t0:.0f}\n\nPROMPT:\n{prompt}\n")
    with open(COSTS, "a") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')}\t{out_rel}\t{key}\t{price}\tok\n")
    print("ok", out, price)
    return out


def main(argv):
    if argv and argv[0] == "--parallel":
        jobs = [l.split() for l in open(argv[1]) if l.strip() and not l.startswith("#")]

        def go(j):
            refs = j[3].split(",") if len(j) > 3 and j[3] != "-" else []
            try:
                return run(j[0], j[1], j[2], refs, j[4] if len(j) > 4 else "16:9", j[5] if len(j) > 5 else "2K")
            except Exception as e:
                print(f"FAIL {j[0]}: {e}", file=sys.stderr)
        with ThreadPoolExecutor(3) as ex:
            list(ex.map(go, jobs))
        return
    pos = [a for a in argv if not a.startswith("--")]
    opt = {a.split("=", 1)[0][2:]: a.split("=", 1)[1] for a in argv if a.startswith("--") and "=" in a and not a.startswith("--ref=")}
    refs = [a.split("=", 1)[1] for a in argv if a.startswith("--ref=")]
    run(pos[0], opt.get("m", "nbp"), pos[1], refs, opt.get("aspect", "16:9"), opt.get("size", "2K"), "--dry-run" in argv)


if __name__ == "__main__":
    main(sys.argv[1:])

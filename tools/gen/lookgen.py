#!/usr/bin/env python3
"""Look bake-off driver: one prompt -> one model, saved as media/look/<test>/<key>_<variant>.jpg + .txt.

    $PY tools/gen/lookgen.py TEST KEY VARIANT PROMPT_FILE [--ref=path ...] [--neg=NEG_FILE] [--aspect=16:9] [--dry-run]
    $PY tools/gen/lookgen.py --parallel JOBS.tsv     # lines: TEST KEY VARIANT PROMPT_FILE [refs,comma,sep] ; <=3 at once

Model keys: nbp sd5 gpt2 qwen flux2 krea3 kling3 grok recraft recraftpro
Costs are appended to media/look/_costs.tsv with list prices corrected for 2K output (cf.py under-estimates some).
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf  # noqa: E402

ROOT = cf.ROOT
LOOK = os.path.join(ROOT, "media", "look")
COSTS = os.path.join(LOOK, "_costs.tsv")

MODELS = {
    "nbp": "google/nano-banana-pro", "sd5": "bytedance/seedream-5-pro", "gpt2": "openai/gpt-image-2",
    "qwen": "alibaba/qwen-image-3.0-pro", "flux2": "black-forest-labs/flux-2-max", "krea3": "krea/krea-3",
    "kling3": "klingai/kling-v3-image", "grok": "xai/grok-imagine-image-quality", "recraft": "recraft/recraftv4-1",
    "recraftpro": "recraft/recraftv4-1-pro",
}
DIMS = {"16:9": (2048, 1152), "1:1": (1536, 1536), "3:2": (1872, 1248), "4:3": (1792, 1344), "3:4": (1344, 1792),
        "2:3": (1248, 1872), "9:16": (1152, 2048)}
SD_DIMS = {"16:9": (2560, 1440), "1:1": (2048, 2048), "3:2": (2496, 1664), "4:3": (2304, 1728), "3:4": (1728, 2304),
           "2:3": (1664, 2496)}


def build(key, prompt, refs, neg, aspect):
    w, h = DIMS[aspect]
    f = ["file:" + r for r in refs]
    if key == "nbp":
        i = {"prompt": prompt, "aspect_ratio": aspect, "image_size": "2K", "output_format": "jpg"}
        if f: i["image_input"] = f[:3]
        return i, 0.134
    if key == "sd5":
        sw, sh = SD_DIMS[aspect]
        i = {"prompt": prompt, "size": f"{sw}x{sh}", "watermark": False}
        if f: i["image"] = f if len(f) > 1 else f[0]
        return i, 0.045 + 0.03 * len(f)
    if key == "gpt2":
        i = {"prompt": prompt, "size": f"{w}x{h}", "quality": "high", "output_format": "jpeg"}
        if f: i["images"] = f
        return i, None   # use cf estimate
    if key == "qwen":
        i = {"prompt": prompt, "size": f"{w}x{h}", "watermark": False, "prompt_extend": False}
        if neg: i["negative_prompt"] = neg
        return i, 0.07
    if key == "flux2":
        i = {"prompt": prompt, "width": w, "height": h, "output_format": "jpeg", "safety_tolerance": 2}
        if f: i["input_images"] = f
        mp = w * h / 1e6
        return i, round(0.07 + 0.03 * (mp - 1) + 0.03 * len(f) * 1.0, 3)
    if key == "krea3":
        i = {"prompt": prompt, "resolution": "2K", "aspect_ratio": aspect}
        if neg: i["negative_prompt"] = neg
        return i, 0.06
    if key == "kling3":
        i = {"prompt": prompt, "resolution": "2k", "aspect_ratio": aspect}
        if neg: i["negative_prompt"] = neg
        if f: i["image"] = f[0]
        return i, 0.027
    if key == "grok":
        i = {"prompt": prompt, "aspect_ratio": aspect, "resolution": "2k", "quality": "high", "response_format": "b64_json"}
        if f: i["images"] = [{"url": x, "type": "image_url"} for x in f]
        return i, 0.05 + 0.01 * len(f)
    if key in ("recraft", "recraftpro"):
        pass
        if key == "recraft":
            rw, rh = {"16:9": (1820, 1024), "1:1": (1024, 1024), "3:2": (1536, 1024), "4:3": (1365, 1024)}.get(aspect, (1820, 1024))
        i = {"prompt": prompt, "size": aspect}
        return i, 0.035 if key == "recraft" else 0.21
    raise SystemExit(f"unknown key {key}")


def run(test, key, variant, prompt_file, refs=(), neg_file=None, aspect="16:9", dry=False):
    prompt = open(prompt_file).read().strip()
    neg = open(neg_file).read().strip() if neg_file else ""
    inp, price = build(key, prompt, list(refs), neg, aspect)
    model = MODELS[key]
    if price is None:
        price = cf.estimate(model, inp)[0] or 0.2
    out = os.path.join(LOOK, test, f"{key}_{variant}.jpg")
    if dry:
        cf.generate(model, inp, out, tag=f"look_{test}", dry_run=True)
        print("corrected price", price)
        return None
    if os.path.exists(out):
        print("exists, skip", out); return out
    t0 = time.time()
    try:
        paths = cf.generate(model, inp, out, tag=f"look_{test}_{key}_{variant}")
    except Exception as e:
        print(f"FAIL {test} {key} {variant}: {str(e)[:400]}", file=sys.stderr)
        with open(COSTS, "a") as fh:
            fh.write(f"{time.strftime('%H:%M:%S')}\t{test}\t{key}\t{variant}\t0\tFAIL {str(e)[:120]}\n")
        return None
    p = paths[0]
    if not p.endswith(".jpg"):
        subprocess.run(["convert", p, "-quality", "93", out], check=True)
        os.remove(p); p = out
    meta = {k: (v if not (isinstance(v, str) and v.startswith("file:")) else v) for k, v in inp.items() if k != "prompt"}
    with open(out[:-4] + ".txt", "w") as fh:
        fh.write(f"model: {model}\nparams: {json.dumps(meta, ensure_ascii=False)}\nrefs: {list(refs)}\n"
                 f"est_usd: {price}\nsecs: {time.time()-t0:.0f}\n\nPROMPT:\n{prompt}\n")
        if neg: fh.write(f"\nNEGATIVE:\n{neg}\n")
    with open(COSTS, "a") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')}\t{test}\t{key}\t{variant}\t{price}\tok\n")
    return out


def main(argv):
    if argv and argv[0] == "--parallel":
        jobs = [l.split() for l in open(argv[1]) if l.strip() and not l.startswith("#")]
        def go(j):
            refs = j[4].split(",") if len(j) > 4 and j[4] != "-" else []
            neg = j[5] if len(j) > 5 and j[5] != "-" else None
            aspect = j[6] if len(j) > 6 else "16:9"
            try:
                return run(j[0], j[1], j[2], j[3], refs, neg, aspect)
            except Exception as e:
                print(f"FAIL {j[:3]}: {e}", file=sys.stderr)
                return None
        with ThreadPoolExecutor(3) as ex:
            for r in ex.map(go, jobs):
                print("done", r)
        return
    pos = [a for a in argv if not a.startswith("--")]
    refs = [a.split("=", 1)[1] for a in argv if a.startswith("--ref=")]
    neg = next((a.split("=", 1)[1] for a in argv if a.startswith("--neg=")), None)
    aspect = next((a.split("=", 1)[1] for a in argv if a.startswith("--aspect=")), "16:9")
    run(*pos[:4], refs=refs, neg_file=neg, aspect=aspect, dry="--dry-run" in argv)


if __name__ == "__main__":
    main(sys.argv[1:])

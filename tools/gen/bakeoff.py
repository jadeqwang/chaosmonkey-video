#!/usr/bin/env python3
"""Write one first-frame spec per candidate video model for a staged keyframe (the bake-off).

    PY tools/gen/bakeoff.py SHOT KEYFRAME.jpg "motion prompt" [--models veo31,kling4,...] [--dur 5] [--suffix t1]
    PY tools/gen/gen.py submit media/gen/specs/bk_<SHOT>_<model>_<suffix>.json [...]

Each model gets the same keyframe and the same prompt, at its best resolution up to 1080p, without audio.
Field names differ per model (docs/gen_catalog/<model>.json); they are mapped here once.
The specs are in gen.py's format, so submit / wait / collect work as usual and spend is logged.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPECS = os.path.join(ROOT, "media", "gen", "specs")

# key -> (model id, function(image_ref, prompt, dur) -> input dict)
MODELS = {
    "veo31": ("google/veo-3.1", lambda im, p, d: {
        "prompt": p, "image_input": im, "duration": "4s" if d <= 4 else ("6s" if d <= 6 else "8s"),
        "aspect_ratio": "16:9", "resolution": "1080p", "generate_audio": False}),
    "kling4": ("klingai/kling-v4", lambda im, p, d: {
        "prompt": p, "first_frame": im, "duration": d, "aspect_ratio": "16:9", "resolution": "1080p"}),
    "sd20": ("bytedance/seedance-2.0", lambda im, p, d: {
        "prompt": p, "image": im, "duration": d, "resolution": "1080p", "aspect_ratio": "16:9",
        "generate_audio": False, "watermark": False, "use_virtual_avatar": True}),
    "sd25": ("bytedance/seedance-2.5", lambda im, p, d: {
        "prompt": p, "image": im, "duration": d, "resolution": "720p",
        "generate_audio": False, "watermark": False, "use_virtual_avatar": True}),
    "hh11": ("alibaba/hh1.1-i2v", lambda im, p, d: {
        "prompt": p, "image": im, "duration": d, "resolution": "1080P", "watermark": False}),
    "wan27": ("alibaba/wan-2.7-i2v", lambda im, p, d: {
        "prompt": p, "image": im, "duration": d, "resolution": "1080P", "watermark": False}),
    "omni12": ("google/gemini-omni-1.2-flash", lambda im, p, d: {
        "text": p, "image": im, "aspect_ratio": "16:9", "resolution": "1080p"}),
    "gen45": ("runwayml/gen-4.5", lambda im, p, d: {
        "prompt": p, "image_input": im, "ratio": "1280:720", "duration": d}),
    "vidu3": ("vidu/q3-pro", lambda im, p, d: {
        "prompt": p, "start_image": im, "duration": d, "resolution": "1080p", "audio": False}),
    "h3": ("minimax/h3", lambda im, p, d: {
        "prompt": p, "image": im, "duration": max(d, 4), "resolution": "2K", "ratio": "16:9"}),
}


def main():
    a = sys.argv[1:]
    if len(a) < 3:
        raise SystemExit(__doc__)
    shot, kf, prompt = a[0], a[1], a[2]
    models, dur, suffix = list(MODELS), 5, "t1"
    i = 3
    while i < len(a):
        if a[i] == "--models":
            models = a[i + 1].split(","); i += 2
        elif a[i] == "--dur":
            dur = int(a[i + 1]); i += 2
        elif a[i] == "--suffix":
            suffix = a[i + 1]; i += 2
        else:
            raise SystemExit(f"unknown arg {a[i]}")
    if not os.path.exists(os.path.join(ROOT, kf)):
        raise SystemExit(f"no keyframe {kf}")
    os.makedirs(SPECS, exist_ok=True)
    for k in models:
        model, build = MODELS[k]
        tag = f"bk_{shot}_{k}_{suffix}"
        spec = {"model": model, "tag": tag, "notes": f"bake-off {shot}, keyframe {kf}",
                "input": build("file:" + kf, prompt, dur)}
        p = os.path.join(SPECS, tag + ".json")
        json.dump(spec, open(p, "w"), indent=1)
        print(os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()

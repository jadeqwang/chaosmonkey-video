#!/usr/bin/env python3
"""Video-model bake-off on ink-on-paper plates (docs/VIDEO_BAKEOFF.md). All prompts live here, verbatim.

    $PY tools/gen/vbake.py spec TEST [--models a,b,..] [--variant v1]   # -> media/gen/specs/vb_<TEST>_<model>_<variant>.json
    $PY tools/gen/vbake.py file                                         # copy collected clips -> media/vbake/<TEST>/<model>_<variant>.mp4 (+ .txt)
    $PY tools/gen/vbake.py list                                         # tests and models

Then `gen.py submit media/gen/specs/vb_*.json` and `gen.py wait ...` as usual (spend is logged and capped there).
Every model gets the same first frame and prompt; field names, durations and resolutions are mapped here once.
"""
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen  # noqa: E402

ROOT = gen.ROOT
SPECS = gen.SPECS
FR = "media/vbake/_frames"


def _h3(model, res, dmin=4):
    def b(first, prompt, dur, last=None, audio=None):
        inp = {"prompt": prompt, "image": first, "duration": max(dur, dmin), "resolution": res, "ratio": "adaptive"}   # i2v requires adaptive (7003 otherwise)
        if last:
            inp["last_frame_image"] = last
        if audio:
            inp["reference_audios"] = [audio]
        if model == "minimax/h3-max":
            inp["extra"] = {"prompt_expansion_mode": "disabled"}
        return inp
    return model, b


def _hailuo(model):
    return model, lambda first, prompt, dur, last=None, audio=None: {
        "prompt": prompt, "first_frame_image": first, "duration": 6, "resolution": "768P",
        "prompt_optimizer": False, "fast_pretreatment": False}


# key -> (model id, build(first, prompt, dur, last=None, audio=None) -> input).  'first'/'last' are "file:<path>" strings.
MODELS = {
    "kling4": ("klingai/kling-v4", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "first_frame": f, **({"last_frame": last} if last else {}), "duration": d,
        "aspect_ratio": "16:9", "resolution": "720p"}),
    "hh11": ("alibaba/hh1.1-i2v", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image": f, "duration": d, "resolution": "1080P", "watermark": False}),
    "veo31": ("google/veo-3.1", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image_input": f, "duration": "6s" if d <= 6 else "8s", "aspect_ratio": "16:9",
        "resolution": "1080p", "generate_audio": False}),
    "sd20": ("bytedance/seedance-2.0", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image": f, **({"last_frame_image": last} if last else {}), "duration": d, "resolution": "720p",
        "aspect_ratio": "16:9", "camera_fixed": True, "generate_audio": False}),
    "sd25": ("bytedance/seedance-2.5", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image": f, **({"last_frame_image": last} if last else {}),
        **({"reference_audios": [audio]} if audio else {}), "duration": d, "resolution": "720p",
        "aspect_ratio": "16:9", "camera_fixed": True, "generate_audio": False}),
    "h3": _h3("minimax/h3", "2K"),
    "h3max": _h3("minimax/h3-max", "768P", 5),
    "h3lite": _h3("minimax/h3-lite", "768P"),
    "h3hs": _h3("minimax/h3-highspeed", "768P"),
    "hailuo23": _hailuo("minimax/hailuo-2.3"),
    "hailuo23f": _hailuo("minimax/hailuo-2.3-fast"),
    "pixv6": ("pixverse/v6", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image_input": f, "duration": d, "aspect_ratio": "16:9", "quality": "720p", "generate_audio": False}),
    "ltx": ("lightricks/ltx-2-5-fast", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image_uri": f, **({"last_frame_uri": last} if last else {}), "duration": d,
        "resolution": "1280x720", "fps": 24, "generate_audio": False}),
    "vidu3": ("vidu/q3-pro", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "start_image": f, **({"end_image": last} if last else {}), "duration": d,
        "resolution": "720p", "audio": False, "aspect_ratio": "16:9"}),
    "wan27": ("alibaba/wan-2.7-i2v", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image": f, "duration": d, "resolution": "720P", "watermark": False}),
    "k3omni": ("klingai/kling-v3-omni", lambda f, p, d, last=None, audio=None: {
        "prompt": p, "image_input": f, "duration": d, "aspect_ratio": "16:9", "sound": "off"}),
    # talking-head models (V5): image + audio only
    "fabric": ("veed/fabric-1.0", lambda f, p, d, last=None, audio=None: {
        "image_url": f, "audio_url": audio, "resolution": "720p"}),
    "pavatar": ("pruna/p-video-avatar", lambda f, p, d, last=None, audio=None: {
        "image": f, "audio": audio, "voice": "Kore (Female)", "voice_script": "", "voice_language": "English (US)",
        "resolution": "720p", "video_prompt": p, "voice_prompt": "Sing the following.", "negative_prompt":
        "teeth, grin, smile, head tilt, camera move, zoom, captions, text, photorealistic, 3d render",
        "strength_negative_prompt": 1.0, "disable_safety_filter": True, "disable_prompt_upsampling": True}),
}
ALL_I2V = ["kling4", "hh11", "veo31", "sd20", "sd25", "h3", "h3max", "h3lite", "h3hs", "hailuo23", "hailuo23f",
           "pixv6", "ltx", "vidu3", "wan27", "k3omni"]

INK_TAIL = ("It stays a Chinese ink painting on cream xuan paper: brushstrokes, washes and paper grain do not change. "
            "Locked-off camera.")

# test -> dict(first, last, dur, audio, variants{name: prompt})
TESTS = {
    "V1": dict(first="media/look/L1/qwen_v2.jpg", dur=5, variants={
        "v1": "Animate the first frame exactly. Locked-off camera. The painting does not move: the rocky peak, the "
              "round boulder on its summit and every brushstroke stay exactly as painted. Only a long thin band of mist "
              "drifts slowly to the left across the foot of the peak, veiling the lowest rocks as it passes and "
              "uncovering them again behind it. The mist is the bare unpainted cream paper itself, not grey fog or "
              "smoke. Nothing new appears. No zoom, no pan, no change of light. No birds, no sun, no water, no waves, "
              "no colour change.",
        # v2: v1 made kling draw a literal tan paper strip and hh11 a silk sash ("mist is the paper" taken as an object)
        "v2": "Animate the first frame exactly. Locked-off camera; the painting itself does not move. Soft white mist, "
              "the same cream colour as the paper, rises from the sea at the foot of the peak and drifts slowly to the "
              "left, its edges feathered and dissolving like breath, so the lowest rocks fade into blank paper and "
              "then reappear. The rocky peak, the boulder and every brushstroke above the mist stay exactly as "
              "painted. Nothing new appears: no birds, no sun, no waves, no colour change, no zoom, no pan."}),
    "V1b": dict(first="media/look/L4/sd5_v1.jpg", dur=5, variants={
        "v1": "Animate the first frame exactly. A blue-and-green Chinese landscape painting on paper. The clouds "
              "between the peaks, which are bare unpainted paper, flow slowly to the right through the valleys, "
              "parting around the peaks and veiling the lower slopes as they pass. The camera pulls back very slowly "
              "and steadily, the whole painting growing slightly smaller in the frame. The mountains keep their "
              "painted brushstrokes and do not change shape. Nothing new appears. No birds, no sun, no people, no "
              "change of light."}),
    "V2": dict(first="media/look/L3/sd5_v2.jpg", dur=5, variants={
        "a": "Animate the first frame exactly. The splashed-ink Peking-opera monkey drops his shading hand, whips the "
             "long staff out from behind his back and spins it in a fast staff flower in front of his body, the staff "
             "wheeling in blurred circles from hand to hand, then on the last beat snaps it to a dead stop tucked "
             "under his arm and freezes in a sharp heroic pose, chin up, perfectly still. Trained wushu precision: "
             "crisp, weighty, committed. He stays a painting of wet black ink washes and a few quick brushstrokes, "
             "with his two long pheasant plumes and the small red patch around his eyes; the cream paper around him "
             "stays bare. Locked-off camera. No ground, no shadow, no background, nothing new appears.",
        "b": "Animate the first frame exactly. The splashed-ink Peking-opera monkey launches into a tumbling pass "
             "across the sheet from right to left: a cartwheel, then a twisting aerial somersault with the staff in "
             "one hand and his two long plumes whipping behind him, and he lands low on the left side of the sheet "
             "and freezes in a sharp pose on the last beat, staff level, perfectly still. Trained wushu acrobatics: "
             "crisp, weighty, committed. He stays a painting of wet black ink washes and a few quick brushstrokes, "
             "with the small red patch around his eyes; the cream paper around him stays bare. Locked-off camera. "
             "No ground, no shadow, no background, nothing new appears.",
        "c": "Animate the first frame exactly. The splashed-ink Peking-opera monkey sets his foot down, plants the "
             "staff upright and bows deeply from the waist to the four directions in turn: to us, then a sharp "
             "quarter turn to his left and a bow, a quarter turn away from us and a bow, a quarter turn to his right "
             "and a bow, each bow a quick stamped stop like a gong stroke, then he turns back to us and holds still. "
             "Peking-opera precision: crisp, weighty, formal. He stays a painting of wet black ink washes and a few "
             "quick brushstrokes, with his two long pheasant plumes and the small red patch around his eyes; the "
             "cream paper around him stays bare. Locked-off camera. No ground, no shadow, no background, nothing new "
             "appears.",
    }),
    "V2alt": dict(first="media/look/L3/codex_v2.jpg", dur=5, variants={}),   # filled from V2 prompts
    "V2d": dict(first=f"{FR}/pose2.jpg", last=f"{FR}/pose3.jpg", dur=5, variants={
        "fl": "The video starts exactly on @image_1 and ends exactly on @image_2. The ink-painted Peking-opera monkey "
              "whips the staff down from overhead in one fast spinning arc, steps through and drives forward into a "
              "deep lunge, thrusting the staff out to the left, and freezes on the last beat. Trained wushu "
              "precision: crisp, weighty, committed. He stays a painting of black ink washes and brushstrokes with "
              "the small red face patch and two long plumes; the cream paper around him stays bare. Locked-off "
              "camera. No ground, no shadow, no background."}),
    "V3": dict(first=f"{FR}/blank_sd5.jpg", last=f"{FR}/monkey_sd5.jpg", dur=5, variants={
        "fl": "The video starts exactly on @image_1 and ends exactly on @image_2. A single violent throw of black ink "
              "splashes across the bare cream paper from the left: a flying arc of wet ink and droplets lands and "
              "spreads, the wash bleeds into the absorbent paper, and the splash settles into the ink painting of the "
              "monkey in his pose, which then stays perfectly still for the last second. Locked-off camera, flat "
              "paper, nothing else appears.",
        "ff": "Animate the first frame exactly. A single violent throw of black ink splashes across the bare cream "
              "paper from the left: a flying arc of wet ink and droplets lands in the middle of the sheet, spreads and "
              "bleeds into the absorbent paper, and within a second the wet splash settles into the figure of a "
              "Peking-opera monkey standing on one leg, his hand raised to shade his eyes, a long staff behind him, "
              "two long thin plumes arcing from his cap, painted in wet black washes and a few quick brushstrokes, "
              "with one small red patch around his eyes. Then nothing moves. Locked-off camera, flat paper, no "
              "background, no shadow."}),
    "V4": dict(first="media/look/L5/nbp_a_v2.jpg", dur=5, variants={
        "attic": "Animate the first frame exactly. In the dark attic the mother turns one page of the picture book "
                 "on her knees and glances down at her daughter; the little girl looks up at her mother's face. "
                 "Outside the low window the red neon light flickers off for an instant and back on, and the red "
                 "pool of light on the floor flickers with it. Everything else stays still. The picture stays a "
                 "Chinese ink-and-wash painting on paper with fine-line faces, not a photograph and not anime. "
                 "Locked-off camera."}),
    "V4b": dict(first="media/look/L6/nbp_a_v2.jpg", dur=5, variants={
        "bed": "Animate the first frame exactly. In the dusk-violet bedroom the woman sitting on the floor slowly "
               "moves the flashlight a little across the open page, and the white pool of light slides with it. On "
               "the bed behind her, the little girl shifts her chin on her folded arms and keeps watching the book. "
               "Everything else stays still. The picture stays a Chinese ink-and-wash painting on paper with "
               "fine-line faces, not a photograph and not anime. Locked-off camera."}),
    "V5c": dict(first=f"{FR}/face_child.jpg", dur=5, audio=("work/stems/vocals.wav", 15.31, 5.0), variants={
        "sing": "Animate the first frame exactly. She sings the words of the reference audio with precise lip sync, "
                "softly, her head almost still, eyes calm. The picture stays an ink-and-wash painting on paper with "
                "fine-line features. Locked-off camera."}),
    "V5m": dict(first=f"{FR}/face_mom.jpg", dur=5, audio=("work/stems/vocals.wav", 203.22, 5.0), variants={
        "sing": "Animate the first frame exactly. She sings the words of the reference audio with precise lip sync, "
                "tenderly, her head almost still, eyes calm. The picture stays an ink-and-wash painting on paper with "
                "fine-line features. Locked-off camera."}),
    "V6": dict(first="media/look/L9/gpt2_puppet_v1.jpg", dur=5, variants={
        "puppet": "Animate the first frame exactly. A Chinese shadow play: the jointed leather monkey puppet is "
                  "worked on its rods behind the glowing screen in the stiff, snapping way of a real shadow play: "
                  "the staff arm jerks up in two sharp jointed moves, the head nods twice, the body hops forward "
                  "once and stops dead, each limb swinging from its rivet as a flat rigid piece that never bends. "
                  "The screen and the light stay still. Locked-off camera."}),
    "V6b": dict(first="media/look/L9/nbp_hand_v1.jpg", dur=5, variants={
        "hand": "Animate the first frame exactly. The two hands in the red light open and close their fingers so "
                "the monkey-head shadow on the open book opens and shuts its jaw as if it is talking, four quick "
                "times, the shadow's head tilting slightly as it speaks. The book and the light stay still. "
                "Locked-off camera."}),
}
TESTS["V2alt"]["variants"] = {"a": TESTS["V2"]["variants"]["a"]}


def spec(test, models, variants=None):
    T = TESTS[test]
    def ref(path):   # unique name per source (L5/nbp_a_v2 and L6/nbp_a_v2 collided in gen.ref_image's default name)
        out = os.path.join(gen.REFS, path.replace("/", "_").rsplit(".", 1)[0] + "_2048.jpg")
        return "file:" + os.path.relpath(gen.ref_image(os.path.join(ROOT, path), out), ROOT)
    first = ref(T["first"])
    last = ref(T["last"]) if T.get("last") else None
    audio = None
    if T.get("audio"):
        src, st, du = T["audio"]
        audio = "file:" + os.path.relpath(gen.audio_ref(os.path.join(ROOT, src), st, du,
                                                         os.path.join(ROOT, f"media/vbake/_frames/{test}_audio.mp3")), ROOT)
    out = []
    for v, prompt in T["variants"].items():
        if variants and v not in variants:
            continue
        for k in models:
            model, build = MODELS[k]
            tag = f"vb_{test}_{k}_{v}"
            inp = build(first, prompt, T["dur"], last=last, audio=audio)
            s = {"model": model, "tag": tag, "notes": f"video bake-off {test}/{v}; first {T['first']}"
                 + (f"; last {T['last']}" if last else "") + (f"; audio {T['audio']}" if audio else ""), "input": inp}
            p = os.path.join(SPECS, tag + ".json")
            os.makedirs(SPECS, exist_ok=True)
            json.dump(s, open(p, "w"), indent=1, ensure_ascii=False)
            out.append(os.path.relpath(p, ROOT))
    print("\n".join(out))
    return out


def file_clips():
    m = gen.read_manifest()
    n = 0
    for jid, j in m["jobs"].items():
        if not j["tag"].startswith("vb_") or j["state"] != "done" or not j.get("files"):
            continue
        _, test, model, var = j["tag"].split("_", 3)
        spec_file = j["spec_file"]
        if not os.path.exists(os.path.join(ROOT, spec_file)):
            # the first V4 attic takes got the L6 bedroom frame (ref-name collision): kept as V4b/<model>_atticprompt
            spec_file = spec_file[:-5] + ".wrongframe.json"
            test, var = "V4b", "atticprompt"
        dst = os.path.join(ROOT, "media", "vbake", test, f"{model}_{var}.mp4")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        src = os.path.join(ROOT, j["files"][0])
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        shutil.copy2(src, dst)
        sp = json.load(open(os.path.join(ROOT, spec_file)))
        inp = {k: (v if not (isinstance(v, str) and v.startswith(("file:", "data:"))) else v[:120])
               for k, v in sp["input"].items()}
        with open(dst[:-4] + ".txt", "w") as f:
            f.write(f"model {sp['model']}\njob {jid}\nsource {j['files'][0]}\nest ${j.get('est_usd')}\n"
                    f"notes {sp.get('notes','')}\ninput {json.dumps(inp, ensure_ascii=False)}\n\n"
                    f"{gen.cf.prompt_of(sp['input'])}\n")
        n += 1
        print(os.path.relpath(dst, ROOT))
    print(f"{n} filed")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "spec":
        models, variants = ALL_I2V, None
        if "--models" in a:
            models = a[a.index("--models") + 1].split(",")
        if "--variant" in a:
            variants = a[a.index("--variant") + 1].split(",")
        spec(a[1], models, variants)
    elif a[0] == "file":
        file_clips()
    elif a[0] == "list":
        for t, T in TESTS.items():
            print(t, T["first"], list(T["variants"]))
        print(" ".join(MODELS))

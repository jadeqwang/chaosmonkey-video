#!/usr/bin/env python3
"""Lip-sync bake-off v3: write relay specs for every audio-driven method on the three test lines.
    $PY tools/gen/ls3_bake.py LINE METHOD[,METHOD] [--n 2]     -> media/gen/specs/ls3_<LINE>_<METHOD>_<i>.json
LINE a (little Jade, en+zh), b (Mama, en), c (daughter, zh rap). Windows and prompts below are the record."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
ROOT = gen.ROOT
STEM = "work/stems/vocals.wav"
KF = "media/kf/v3/lipsync_test"
AUD = "media/gen/v3/lipsync/_audio"
GUARD = (" Same painting throughout: fine ink line and light colour wash on paper, the same face and hair, the same framing. "
         "The camera does not move. No text. Wide 16:9 landscape frame.")
LINES = {
 "a": dict(img=f"{KF}/lj_sing.jpg", who="the little girl", win=dict(pre=(15.31, 7), f0=(15.77, 6), short=(15.31, 4), short2=(18.70, 4)),
   act="A five-year-old bargaining for a bedtime story. At the start she looks up to the right at her mother and sings the first "
       "word with her eyebrows lifting. Around 1.5 s she leans in a little and tilts her head, blinks once, singing sweetly. Around "
       "3.5 s she takes a small breath, her shoulders rise, her eyes flick down and come back up. Then she sings the question, her "
       "eyes widening on the hero's name, and ends on a hopeful half-smile with her mouth closed."),
 "b": dict(img=f"{KF}/mama_sing.jpg", who="the woman", win=dict(pre=(45.67, 4), f0=(46.13, 4)),
   act="A mother telling a story she loves. At the start she shakes her head once, slowly, eyes down to the left on her child, "
       "singing 'not yet'. Around 1.5 s her eyebrows go up, she lifts her chin and her eyes brighten, she blinks once. On the last long "
       "word she leans forward a little, breathing in through the note, a smile growing at the corners."),
 "c": dict(img=f"{KF}/dau_sing.jpg", who="the little girl", win=dict(pre=(106.54, 4), f0=(107.0, 4)),
   act="A four-year-old rapping fast with total self-belief. She bobs her head on the beat and chops her raised hand down on each "
       "phrase, eyes straight at us; around 1.8 s she blinks, takes a quick breath and her shoulders bounce, then goes on, chin "
       "pushing forward, eyebrows working."),
 "d": dict(img=f"{KF}/jade_sing.jpg", who="the woman", win=dict(pre=(186.49, 4), f0=(186.95, 4)),
   act="A mother daring her child. She looks down to the right, eyebrows up, sings a short question, then holds, breathing, a blink, "
       "a small sure nod as she sings the answer, a warm certain smile at the end."),
}
SING = "{Who} sings the words of the reference audio with precise lip sync; the lips close fully on every m, b and p and open wide on the long vowels. "

def audio(line, var):
    st, du = LINES[line]["win"][var]
    out = f"{AUD}/{line}_{var}.mp3"
    if not os.path.exists(os.path.join(ROOT, out)):
        gen.audio_ref(os.path.join(ROOT, STEM), st, du, os.path.join(ROOT, out))
    return "file:" + out, st, du

def image(line):
    src = LINES[line]["img"]; out = src[:-4] + "_1920.jpg"
    if not os.path.exists(os.path.join(ROOT, out)):
        gen.ref_image(os.path.join(ROOT, src), os.path.join(ROOT, out), max_side=1920)
    return "file:" + out

def sd25(line, var, res="720p"):
    L = LINES[line]; a, st, du = audio(line, var)
    p = "Animate the first frame exactly. " + SING.format(Who=L["who"].capitalize()) + L["act"] + GUARD
    return "bytedance/seedance-2.5", {"prompt": p, "image": image(line), "reference_audios": [a], "duration": int(du),
            "resolution": res, "aspect_ratio": "16:9", "generate_audio": False, "watermark": False}, st

def sd25v2v(line, res="480p"):
    """Two-stage: the acted Kling take (no lip-sync) as reference video + the vocal window; Seedance re-renders it singing."""
    import glob
    L = LINES[line]; a, st, du = audio(line, "pre")
    v = os.path.join(ROOT, f"media/gen/v3/lipsync/_ref/{line}_kling_1.mp4")   # 720p crf 22 copy of the Kling take
    p = ("Edit the reference video. Keep its performance exactly: the same head moves, eyes, blinks, eyebrows, hands, timing, "
         "framing and the same ink-and-wash painting. Change only the mouth: " + SING.format(Who=L["who"]) + "No camera move. No text.")
    return "bytedance/seedance-2.5", {"prompt": p, "reference_videos": ["file:" + os.path.relpath(v, ROOT)], "reference_audios": [a],
            "duration": -1, "resolution": res, "aspect_ratio": "16:9", "generate_audio": False, "watermark": False}, st

def sd20mini(line, var="pre"):
    L = LINES[line]; a, st, du = audio(line, var)
    p = "Animate the first frame exactly. " + SING.format(Who=L["who"].capitalize()) + L["act"] + GUARD
    return "bytedance/seedance-2.0-mini", {"prompt": p, "image": image(line), "reference_audio": a, "duration": int(du),
            "resolution": "720p", "aspect_ratio": "16:9", "fps": 24, "camera_fixed": True, "use_virtual_avatar": False,
            "generate_audio": False, "watermark": False}, st

def pav(line, mode):
    L = LINES[line]; a, st, du = audio(line, "pre")
    vp = {"neutral": f"{L['who'].capitalize()} sings. Her head stays still. The camera does not move.",
          "acted": f"{L['who'].capitalize()} sings. " + L["act"] + " The camera does not move.",
          "default": "The person is singing."}[mode]
    return "pruna/p-video-avatar", {"image": image(line), "audio": a, "voice": "Kore (Female)", "voice_script": "", "voice_language": "English (US)",
            "voice_prompt": "Sing the following.", "resolution": "720p", "video_prompt": vp,
            "negative_prompt": "wide grin, bared teeth, camera move, zoom, reframing, captions, subtitles, text, background change",
            "strength_negative_prompt": 1.0, "disable_safety_filter": True, "disable_prompt_upsampling": mode != "default"}, st

def fabric(line, model="veed/fabric-1.0"):
    a, st, du = audio(line, "pre")
    return model, {"image_url": image(line), "audio_url": a, "resolution": "720p"}, st

def omni(line):
    L = LINES[line]; a, st, du = audio(line, "pre")
    p = (f"Animate this image into a {int(du)} second video in which {L['who']} sings exactly the attached audio, with precise lip sync to "
         "it; use the attached audio as the soundtrack unchanged. " + L["act"] + GUARD)
    return "google/gemini-omni-1.2-flash", {"text": p, "image": image(line), "audio": a, "aspect_ratio": "16:9", "resolution": "720p"}, st

def kling(line):
    L = LINES[line]; st, du = L["win"]["pre"]
    p = ("Animate the first frame exactly. " + f"{L['who'].capitalize()} sings softly. " + L["act"] + GUARD)
    return "klingai/kling-v4", {"prompt": p, "first_frame": image(line), "duration": int(du), "aspect_ratio": "16:9", "resolution": "720p"}, st

METHODS = {
 "sd25pre": lambda l: sd25(l, "pre"), "sd25f0": lambda l: sd25(l, "f0"), "sd25short": lambda l: sd25(l, "short"),
 "sd25short2": lambda l: sd25(l, "short2"), "sd25pre480": lambda l: sd25(l, "pre", "480p"),
 "sd20mini": sd20mini, "sd25v2v": sd25v2v, "sd25v2v720": lambda l: sd25v2v(l, "720p"), "pavN": lambda l: pav(l, "neutral"), "pavA": lambda l: pav(l, "acted"), "pavD": lambda l: pav(l, "default"),
 "fabric": fabric, "fabricfast": lambda l: fabric(l, "veed/fabric-1.0-fast"), "omni": omni, "kling": kling,
}

def write(tag, model, inp, t0, notes=""):
    os.makedirs(os.path.join(ROOT, "media/gen/specs"), exist_ok=True)
    p = os.path.join(ROOT, f"media/gen/specs/{tag}.json")
    json.dump({"model": model, "tag": tag, "notes": f"lipsync bake-off v3; t0={t0} {notes}", "t0": t0, "input": inp},
              open(p, "w"), ensure_ascii=False, indent=1)
    return p

if __name__ == "__main__":
    line, methods = sys.argv[1], sys.argv[2].split(",")
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 1
    for m in methods:
        model, inp, t0 = METHODS[m](line)
        for i in range(1, n + 1):
            print(write(f"ls3_{line}_{m}_{i}", model, inp, t0))

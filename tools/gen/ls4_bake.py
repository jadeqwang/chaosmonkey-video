#!/usr/bin/env python3
"""Lip-sync bake-off v4 (REVISION_V4 §6): every method in which a VIDEO MODEL makes the whole singing face from the audio.

    $PY tools/gen/ls4_bake.py LINE METHOD[,METHOD] [--n 3] [--submit]   -> media/gen/specs/ls4_<LINE>_<METHOD>_<i>.json
    $PY tools/gen/ls4_bake.py url MEDIA.mp4                              -> says whether a provider URL exists (never prints it)

LINE  B1 (little Jade, en + 妈妈/孙悟空), C3 (Mama, en), F1 (daughter, Mandarin rap), I4 (adult Jade, en).
Every spec carries "t0" = the song time of the audio window's first sample (= the take's frame 0 if the model kept the audio
where it was given). Windows and prompts below are the record.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
ROOT = gen.ROOT
STEM = "work/stems/vocals.wav"
LEAD = "work/stems/lead.wav"
MIX = "inputs/Chaos Monkey - reformatted for duet.wav"
AUD = "media/gen/v4/lipsync/_audio"
KF4 = "media/kf/v4/lipsync_test"
GUARD = (" The picture stays the same hand-painted Chinese ink-and-colour painting on paper in every frame: fine ink line, pale colour"
         " wash, paper grain; faces keep exactly their drawn features, big dark eyes with highlights, rosy cheeks. The camera does not"
         " move. No text, no captions.")

LINES = {
 "B1": dict(img="media/kf/v3/B1c.jpg", tight=f"{KF4}/B1_tight.jpg", who="the little girl", win=(15.31, 4), full=(15.31, 7),
   lang="She sings in English, with the Chinese word 妈妈 (mā ma) at the start",
   partner="her mother (seen from behind at the right edge)",
   act="A five-year-old bargaining for a bedtime story. She looks up to the right at her mother's face the whole time, eyes wide"
       " open. 0-0.5 s: she draws a breath, hand on her mother's forearm. 0.5-1.6 s: she sings 妈妈, eyebrows lifting, patting the"
       " forearm. 1.6-3.4 s: she leans in a little and tilts her head, pleading, still singing, one blink. 3.4-4 s: a small breath,"
       " her shoulders rise, a hopeful half-smile. Then she sings the question, her eyes widening on the hero's name 孙悟空, and ends on a"
       " hopeful half-smile with her mouth closed, still looking up at her mother."),
 "C3": dict(img="media/kf/v3/C3.jpg", tight=f"{KF4}/C3_tight.jpg", who="the woman with glasses", win=(45.67, 4),
   lang="She sings in English", partner="the little girl in her lap",
   act="A mother telling a story she loves, amused. 0-0.5 s: she breathes in, smiling, looking down at the girl's raised hands."
       " 0.5-1.4 s: she sings 'not yet', shaking her head once, slowly, and her one finger presses the two small hands down."
       " 1.4-2.6 s: eyebrows up, she glances at the girl's face and back to the page, still singing. 2.6-4 s: she holds the last"
       " long word, leaning in a little, a smile growing at the corners. The girl in her lap does not sing; her mouth stays closed."),
 "F1": dict(img=f"{KF4}/F1_tight.jpg", wide="media/kf/v3/F1.jpg", who="the little girl", win=(106.54, 4),
   lang="She raps fast in Mandarin Chinese (石头里蹦出来 没有童年, 一声耳语 学会七十二变), crisp syllables, about six syllables a second",
   partner="her mother in the front seat (towards the camera)",
   act="A four-year-old rapping with total self-belief. Her right hand counts the flow in front of her chest, index and middle"
       " finger out, chopping down on each stressed syllable; her other hand rests, then points at the camera at the end of the"
       " line. Her shoulders bounce on the beat and her head nods forward on each downbeat with the chin leading. Around 2 s a quick"
       " breath and a grin, then on into the next line, leaning toward the camera on the last word. Never both palms up beside the face."),
 "I4": dict(img="media/kf/v3/I4_jade.jpg", who="the woman with glasses", win=(186.49, 4),
   lang="She sings in English, softly",
   partner="her little daughter below the frame",
   act="A mother who has known the answer for years and has been waiting to be asked. 0-0.5 s: she looks down at her daughter,"
       " level, the corner of her mouth just lifting. 0.5-1.1 s: she sings 'Wouldn't you?', almost amused, eyebrows a little up."
       " 1.1-2.1 s: she holds the look, breathes, one slow blink. 2.1-3.4 s: quieter, certain, she sings 'You're able', a very"
       " small nod. 3.4-4 s: she holds, a private confidence; no big smile."),
}


def audio(line, src="stem", pad=0.0, win=None, tail=0.0):
    """The exact window of the song; pad = seconds of digital silence put BEFORE it (t0 moves back by pad), tail = after it."""
    st, du = win or LINES[line]["win"]
    s = {"stem": STEM, "lead": LEAD, "mix": MIX}[src]
    out = f"{AUD}/{line}_{src}_{st:.2f}_{du:g}" + (f"_pad{pad:g}" if pad else "") + (f"_tail{tail:g}" if tail else "") + ".mp3"
    if not os.path.exists(os.path.join(ROOT, out)):
        os.makedirs(os.path.join(ROOT, AUD), exist_ok=True)
        af = ["-af", f"adelay={int(pad*1000)}:all=1,apad=whole_dur={pad+du+tail}"] if (pad or tail) else []
        subprocess.run([gen.FFMPEG, "-v", "error", "-y", "-ss", f"{st:.3f}", "-t", f"{du:.3f}", "-i", os.path.join(ROOT, s)] + af +
                       ["-ac", "2", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", os.path.join(ROOT, out)], check=True)
    return "file:" + out, st - pad, du + pad + tail


def image(path):
    out = os.path.join("media/gen/refs", "ls4_" + os.path.basename(path)[:-4] + "_1920.jpg")
    if not os.path.exists(os.path.join(ROOT, out)):
        gen.ref_image(os.path.join(ROOT, path), os.path.join(ROOT, out), max_side=1920)
    return "file:" + out


def provider_url(media_path):
    """The provider's public output URL that the relay stored for a finished job (res:<job>.media[].url). Never printed."""
    m = gen.read_manifest()["jobs"]
    rel = os.path.relpath(os.path.join(ROOT, media_path), ROOT)
    for jid, j in m.items():
        if rel in (j.get("files") or []):
            rec = gen.kv_get("res:" + jid)
            urls = [f.get("url") for f in (rec or {}).get("media", []) if f.get("url")] or gen._urls((rec or {}).get("result"))
            return urls[0] if urls else None
    return None


def seedance(line, var):
    """Seedance 2.5, first frame + the song window as reference audio; acting and singing in one take."""
    L = LINES[line]
    o = dict(src="stem", pad=0.0, res="720p", img=L["img"], gen_audio=True, win=None, tail=0.0)
    o.update(var)
    a, t0, du = audio(line, o["src"], o["pad"], o["win"], o["tail"])
    who = L["who"]
    p = (f"Animate the first frame exactly. {who[0].upper() + who[1:]} sings the song of audio 1 herself, lip-synced to it exactly:"
         f" her lips, jaw and cheeks move with every syllable at the moment it is heard, the jaw dropping on open vowels and the lips"
         f" closing on m, b and p; silent where the audio is silent. {L['lang']}. While singing she acts: {L['act']} Her eyes stay"
         f" open and on {L['partner']}." + GUARD)
    inp = {"prompt": p, "image": image(o["img"]), "reference_audios": [a], "duration": max(4, int(-(-du // 1))), "resolution": o["res"],
           "aspect_ratio": "16:9", "generate_audio": o["gen_audio"], "watermark": False}
    return "bytedance/seedance-2.5", inp, t0


def seedance_v2v(line, var):
    """Two-pass: the acted Kling take (provider URL) as reference video + the song window; Seedance re-renders it singing."""
    L = LINES[line]
    o = dict(src="stem", res="480p", gen_audio=True)
    o.update(var)
    url = provider_url(o["video"])
    if not url:
        raise SystemExit(f"no provider URL for {o['video']}")
    a, t0, du = audio(line, o["src"], 0.0, (o["vt0"], o["vdur"]))
    p = (f"Edit video 1. Keep everything of video 1 exactly: the painting, the framing, the people, every head move, eye move, blink,"
         f" hand move and its timing. Change only the singer's face so that {L['who']} sings the song of audio 1, lip-synced to it"
         f" exactly: lips, jaw and cheeks move with every syllable as it is heard, the jaw dropping on open vowels and the lips closing"
         f" on m, b and p. {L['lang']}. No text.")
    inp = {"prompt": p, "reference_videos": [url], "reference_audios": [a], "duration": -1, "resolution": o["res"],
           "aspect_ratio": "16:9", "generate_audio": o["gen_audio"], "watermark": False}
    return "bytedance/seedance-2.5", inp, t0


def pavatar(line, var):
    """pruna/p-video-avatar as the PICTURE, from the shot's own keyframe, with a holding prompt."""
    L = LINES[line]
    o = dict(src="stem", img=L["img"], res="720p", pad=0.0)
    o.update(var)
    a, t0, du = audio(line, o["src"], o["pad"])
    vp = (f"{L['who'][0].upper() + L['who'][1:]} sings, looking at {L['partner']}, not at the camera. Her eyes stay open the whole"
          f" time, with ordinary blinks only. Her head stays almost still: no swaying, no rolling, no tilting from side to side. Small"
          f" natural movements only. Everything else in the picture stays exactly as it is. The camera does not move.")
    inp = {"image": image(o["img"]), "audio": a, "voice": "Kore (Female)", "voice_script": "", "voice_language": "English (US)",
           "voice_prompt": "Sing the following.", "resolution": o["res"], "video_prompt": vp,
           "negative_prompt": "closed eyes, eyes shut, looking at camera, head sway, head roll, head tilt, wide grin, bared teeth,"
                              " camera move, zoom, reframing, captions, subtitles, text, background change, repainting",
           "strength_negative_prompt": 1.5, "disable_safety_filter": True, "disable_prompt_upsampling": True}
    return "pruna/p-video-avatar", inp, t0


def animate(line, var):
    """pruna/p-video-animate: an acted Kling take with the song muxed in as the source; the keyframe as subject."""
    L = LINES[line]
    src = os.path.join(ROOT, var["video"]); vt0 = var["vt0"]
    out = os.path.join(ROOT, AUD, f"{line}_anim_src.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([gen.FFMPEG, "-v", "error", "-y", "-i", src, "-ss", f"{vt0:.3f}", "-i", os.path.join(ROOT, STEM), "-map", "0:v",
                    "-map", "1:a", "-shortest", "-vf", "fps=24,scale=854:480", "-c:v", "libx264", "-crf", "30", "-preset", "slow", "-c:a", "aac", "-b:a", "160k", out],
                   check=True)
    small = os.path.join(ROOT, "media/gen/refs", f"ls4_{line}_1280.jpg")
    gen.ref_image(os.path.join(ROOT, L["img"]), small, max_side=1280, quality=85)
    inp = {"video": "file:" + os.path.relpath(out, ROOT), "image": "file:" + os.path.relpath(small, ROOT), "resolution": "720p", "save_audio": True,
           "ignore_audio": False, "target_fps": "24", "turbo": False, "disable_safety_checker": False,
           "instruction_prompt": f"Animate {L['who']} with the motion of the video, and make her lips sing the audio exactly. Keep the painting style."}
    return "pruna/p-video-animate", inp, vt0


SHOTWIN = {"B1": (15.31, 3.6), "B1full": (15.31, 7.3), "C3": (45.67, 4.25), "F1": (106.54, 2.6), "I4": (186.49, 3.6)}
METHODS = {
 "sdp": lambda l: seedance(l, {"pad": 1.0, "tail": 1.0, "win": SHOTWIN[l]}),
 "sdpmix": lambda l: seedance(l, {"pad": 1.0, "tail": 1.0, "win": SHOTWIN[l], "src": "mix"}),
 "sdpfull": lambda l: seedance(l, {"pad": 1.0, "tail": 1.0, "win": SHOTWIN[l + "full"]}),
 "sd": lambda l: seedance(l, {}),
 "sdna": lambda l: seedance(l, {"gen_audio": False}),
 "sdpad": lambda l: seedance(l, {"pad": 1.0}),
 "sdmix": lambda l: seedance(l, {"src": "mix"}),
 "sd480": lambda l: seedance(l, {"res": "480p"}),
 "sdwide": lambda l: seedance(l, {"img": LINES[l].get("wide", LINES[l]["img"])}),
 "sdfull": lambda l: seedance(l, {"win": LINES[l].get("full")}),
 "pav": lambda l: pavatar(l, {}),
 "pavt": lambda l: pavatar(l, {"img": LINES[l].get("tight", LINES[l]["img"])}),
}
# acted v3 Kling takes (no audio) for the two-pass methods: video, song time of its frame 0, seconds to use
ACTED = {"B1": ("media/gen/ls_B1c_act1_9ce114e639.mp4", 15.5, 7), "C3": ("media/gen/ls_C3_act1_f77b3d12ea.mp4", 46.167, 4),
         "F1": ("media/gen/v3bc_F1_t1_21db80cfb6.mp4", None, 5), "I4": ("media/gen/v3bc_I4_t1_e55abf46b2.mp4", None, 4)}
for _l, (_v, _t, _d) in ACTED.items():
    if _t is not None:
        METHODS.setdefault(f"v2v_{_l}", (lambda v, t, d: (lambda l: seedance_v2v(l, {"video": v, "vt0": t, "vdur": d})))(_v, _t, _d))
        METHODS.setdefault(f"anim_{_l}", (lambda v, t: (lambda l: animate(l, {"video": v, "vt0": t})))(_v, _t))


def omni(line, var):
    L = LINES[line]
    a, t0, du = audio(line, "stem", 1.0, SHOTWIN[line], 1.0)
    p = (f"Animate this image into a {int(-(-du // 1))} second video in which {L['who']} sings exactly the attached audio, lip-synced to it,"
         f" and use the attached audio unchanged as the soundtrack. {L['lang']}. {L['act']}" + GUARD)
    return "google/gemini-omni-1.2-flash", {"text": p, "image": image(L["img"]), "audio": a, "aspect_ratio": "16:9", "resolution": "720p"}, t0


METHODS["omni"] = lambda l: omni(l, {})
METHODS["v2vsd_C3"] = lambda l: seedance_v2v(l, {"video": "media/gen/ls4_C3_sd_1_23879b1c18.mp4", "vt0": 45.67, "vdur": 4})


KWIN = {"B1": (15.31, 7), "C3": (45.67, 4), "F1": (106.54, 4), "I4": (186.49, 4)}
CALM = (" Her movements are smooth and moderate: no jumping, no bouncing, no fast turns of the head; her face stays clearly"
        " visible and toward the camera the whole time, nothing passes in front of it.")


def kling_act(line, var):
    """Stage 1 of the two-pass method: the acted performance, Kling v4 from the keyframe, no audio."""
    L = LINES[line]; st, du = KWIN[line]
    p = (f"Animate the first frame exactly. {L['who'][0].upper() + L['who'][1:]} sings softly, mouth moving with the words. {L['act']}"
         f" Her eyes stay open and on {L['partner']}." + CALM + GUARD)
    return "klingai/kling-v4", {"prompt": p, "first_frame": image(var.get("img", L["img"])), "duration": du, "aspect_ratio": "16:9",
                                "resolution": "720p"}, st


METHODS["kact"] = lambda l: kling_act(l, {})


def write(tag, model, inp, t0, notes=""):
    os.makedirs(os.path.join(ROOT, "media/gen/specs"), exist_ok=True)
    p = os.path.join(ROOT, f"media/gen/specs/{tag}.json")
    json.dump({"model": model, "tag": tag, "notes": f"lipsync bake-off v4; t0={t0} {notes}", "t0": t0, "input": inp},
              open(p, "w"), ensure_ascii=False, indent=1)
    return p


if __name__ == "__main__":
    if sys.argv[1] == "anim":     # anim LINE VIDEO VT0 TAGSUFFIX [--n 2] [--submit]
        line, video, vt0, suf = sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 1
        model, inp, t0 = animate(line, {"video": video, "vt0": vt0})
        if "--rap" in sys.argv:
            inp["instruction_prompt"] = ("Animate the little girl with the motion of the video. She raps the audio fast in Mandarin Chinese:"
                " her lips and jaw articulate every syllable crisply and clearly, opening visibly on each vowel and closing on b and m,"
                " like a confident child rapper. Keep the painting style and her face exactly as in the image.")
        import shutil
        s_ = os.path.join(ROOT, AUD, f"{line}_anim_src.mp4"); d_ = os.path.join(ROOT, AUD, f"{line}_anim_src_{suf}.mp4")
        shutil.copy(s_, d_); inp["video"] = "file:" + os.path.relpath(d_, ROOT)
        for i in range(1, n + 1):
            inp_i = dict(inp, seed=1000 + i)
            p = write(f"ls4_{line}_anim{suf}_{i}", model, inp_i, t0, f"source {video}")
            print(gen.submit(p) if "--submit" in sys.argv else p)
        sys.exit()
    if sys.argv[1] == "url":
        print("provider URL available" if provider_url(sys.argv[2]) else "no provider URL")
        sys.exit()
    line, methods = sys.argv[1], sys.argv[2].split(",")
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 1
    start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 1
    for m in methods:
        model, inp, t0 = METHODS[m](line)
        for i in range(start, start + n):
            p = write(f"ls4_{line}_{m}_{i}", model, inp, t0)
            print(gen.submit(p) if "--submit" in sys.argv else p)

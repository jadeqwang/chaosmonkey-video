#!/usr/bin/env python3
"""Generated foley sources for the Chaos Monkey sound layer: ElevenLabs Music v2 through the Cloudflare unified catalog
(tools/gen/cf.py logs every call to media/genlog.jsonl + docs/spend_ledger.jsonl and checks the cap).

docs/gen_catalog/INDEX.tsv (checked 2026-11-17) has no sound-effects / text-to-sound model: the only audio generators are
elevenlabs/music-v2 ($0.0025 per output second) and minimax/music-2.6 (per track), plus TTS/ASR. So, as on HALYS
(halys-video/tools/audio/sfx/gen_sources.py), music-v2 with force_instrumental and a "sound effects only" prefix.

Budget for this layer: $20 hard limit. Run with CHAOSMONKEY_CAP set to (project total before this layer + 20) so spend.check()
enforces it:   CHAOSMONKEY_CAP=26.49 $PY tools/audio/sfx/gen_sources.py [NAME ...] [--dry-run]

Writes media/sound/sfx/gen/<name>.mp3 and <name>.txt (model, prompt, length, date). Everything else in the layer is synthesised
in code (tools/audio/sfx/sounds.py). A take is only a raw source: build_layer.py cuts, filters and levels it.
"""
import datetime
import json
import os
import subprocess
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "media", "sound", "sfx", "gen")
PY = "/home/jade/Documents/halys-video/.venv/bin/python"
CF = os.path.join(ROOT, "tools", "gen", "cf.py")
MODEL = "elevenlabs/music-v2"
NO_MUSIC = ("Sound effects only, realistic close foley recording. No music, no melody, no musical instruments, no drums, "
            "no beat, no singing, no voices. ")

JOBS = {
    "stairs_wood": (10000, "A woman in soft slippers slowly climbing a steep narrow flight of old wooden attic stairs: each step a "
                    "soft footfall with a dry creak of the boards, about one step per second, coming closer. Quiet house at night."),
    "dishes_below": (10000, "Heard from the room above, through a wooden floor: someone washing up in a small kitchen downstairs, "
                     "porcelain bowls and plates clinking gently in a sink, a little water. Muffled, distant, calm night."),
    "pages_turn": (8000, "An old paper storybook: its pages turned slowly one at a time by hand, close up, the soft flap and slide "
                   "of each thin page, a pause between turns. Quiet room."),
    "book_lift": (6000, "A small cloth-bound book lifted from a cotton pillow and opened, close up: soft cloth rustle, the cover "
                  "creaking open, a page settling. Quiet room."),
    "blanket_rustle": (8000, "A small child sitting up on a straw floor mat under a cotton quilt, close up: fabric rustling, the "
                       "woven mat creaking softly, then still. Quiet room at night."),
    "brush_paper": (8000, "A soft wet Chinese calligraphy brush painting slow strokes on thin rice paper on a felt pad, very close "
                    "up: the gentle swish and drag of wet bristles on paper, one stroke at a time, pauses between. Quiet room."),
    "drybrush": (6000, "A nearly dry stiff ink brush dragged quickly across rough handmade paper, very close: short scratchy "
                 "papery swishes, fast, one after another. Quiet room."),
    "seal_stamp": (6000, "A heavy stone seal pressed hard down onto paper on a thick wooden desk, close up: a single dull firm "
                   "thump, a pause, then another, then another. Quiet room, dry."),
    "stone_crack": (6000, "A large boulder slowly cracking open: a deep dry grinding creak building to one sharp splitting crack "
                    "of stone, a few small grits falling. Outdoors, close, no explosion."),
    "chisel_stone": (10000, "Far away across a quiet mountain valley: a stone mason tapping a hammer on a chisel against a rock "
                     "cliff, slow steady small taps echoing faintly off the rocks. Distant, calm."),
    "car_cabin": (12000, "Inside a quiet modern car driving on a smooth highway at dusk: steady low tyre roar on the road, soft "
                  "wind on the windows, gentle cabin rumble. No music, no radio, no engine revving, no indicator."),
    "ink_splash": (5000, "A cup of thick liquid thrown hard onto a big sheet of paper on the floor, close up: one wet heavy "
                   "splash and splatter of droplets, then silence."),
    "paper_slide": (6000, "A large sheet of paper slid slowly across a smooth wooden table, close up: a soft dry hiss of paper on "
                    "wood, a pause, then slid again. Quiet room."),
    "flashlight_click": (5000, "A small plastic flashlight's push button switch clicked, very close: one crisp click, a pause of "
                         "two seconds, another click. Quiet bedroom at night."),
    "feet_boards": (6000, "Barefoot performer jumping and landing on a wooden theatre stage floor, close: a firm heavy landing "
                    "thump on the boards, a pause, another landing. Empty theatre, no voices."),
    # round 2 (2026-11-17): the first takes of stairs_wood, dishes_below, book_lift, chisel_stone and blanket_rustle came back as a
    # steady noise floor with no events (measured by inspect_sources.py); reworded with concrete counts, as HALYS did
    "stairs_r2": (10000, "Foley: footsteps going up old creaky wooden stairs inside a house. Step, creak, step, creak: six slow "
                  "heavy footsteps on hollow wooden treads, each with a squeaky creak of the old boards. Close microphone."),
    "dishes_r2": (10000, "Foley: ceramic rice bowls and porcelain plates being stacked and washed in a sink: clink, clink, "
                  "clatter of dishes, gentle tapping of porcelain, splash of water. Kitchen, natural recording."),
    "book_r2": (6000, "Foley: picking up a hardback book and opening it: a soft thump as it is lifted, the creak of the spine, "
                "the cover flapping open, pages fluttering. Close microphone."),
    "chisel_r2": (10000, "Foley: a stonemason carving a rock with a steel chisel and a small hammer: tink, tink, tink, sharp "
                  "metallic taps on stone, slow and regular, with small stone chips falling. Outdoors, natural recording."),
    "rustle_r2": (8000, "Foley: a child turning over under a thick cotton quilt on a straw tatami mat: loud fabric rustles and "
                  "swishes, the mat creaking, then quiet. Close microphone."),
}


def write_txt(name, ms, prompt, status):
    with open(os.path.join(OUT, f"{name}.txt"), "w") as f:
        f.write(f"source: generated, {MODEL} via Cloudflare unified catalog (tools/gen/cf.py), force_instrumental=true, "
                f"output mp3_48000_192\nlength_ms: {ms}\nest_cost_usd: {ms / 1000 * 0.0025:.4f}\n"
                f"date: {datetime.date.today().isoformat()}\nstatus: {status}\nprompt: {prompt}\n")


def run(name, dry):
    ms, desc = JOBS[name]
    prompt = NO_MUSIC + desc
    inp = {"prompt": prompt, "music_length_ms": ms, "force_instrumental": True, "output_format": "mp3_48000_192"}
    cmd = [PY, CF, MODEL, os.path.join(OUT, f"{name}.mp3"), json.dumps(inp), f"--tag=cm_sfx_{name}"]
    if dry:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(f"[{name}] rc={r.returncode} {r.stdout.strip()[-200:]} {r.stderr.strip()[-300:]}", flush=True)
    if not dry:
        write_txt(name, ms, prompt, "ok" if r.returncode == 0 else f"failed: {r.stderr.strip()[-200:]}")


def main(argv):
    dry = "--dry-run" in argv
    names = [a for a in argv if not a.startswith("--")]
    os.makedirs(OUT, exist_ok=True)
    todo = names or [n for n in JOBS if not os.path.exists(os.path.join(OUT, f"{n}.mp3"))]
    secs = sum(JOBS[n][0] for n in todo) / 1000
    print(f"{len(todo)} jobs, {secs:.0f} s, est ${secs * 0.0025:.3f}")
    th = [threading.Thread(target=run, args=(n, dry)) for n in todo]
    for i, t in enumerate(th):
        t.start()
        if i % 3 == 2:          # at most ~3 in flight at once
            th[i - 2].join(); th[i - 1].join(); t.join()
    for t in th:
        t.join()


if __name__ == "__main__":
    main(sys.argv[1:])

"""ROOMS-88 generation batch: Kling v4 motion + Seedance 2.5 lip-sync specs for the 1988 attic shots.

    $PY shots/_r88_gen.py            # write specs + prompts, dry-run every spec
    $PY shots/_r88_gen.py --submit   # queue them (priority order)

Specs -> media/gen/specs/r88_<shot>_<model>_t<k>.json ; prompts -> media/comp/rooms88/prompts/<tag>.txt
Audio windows -> media/comp/rooms88/audio/<shot>.wav (vocal stem window, the OTHER singer's lines muted).
"""
import json, os, subprocess, sys
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PY = sys.executable
OUT = 'media/comp/rooms88'
os.makedirs(f'{OUT}/prompts', exist_ok=True); os.makedirs(f'{OUT}/audio', exist_ok=True)
os.makedirs(f'{OUT}/refs', exist_ok=True); os.makedirs('media/gen/specs', exist_ok=True)

LOOK = ("The picture stays a Chinese ink-and-wash painting on cream paper with fine-line faces and light washes, "
        "not a photograph and not anime. The red light from the window stays steady. Locked-off camera.")
BLANK = " The open pages of the book stay blank and still."


def ref(name):
    """Keyframe -> unique-named 2048 px ref (gen.ref_image caches by basename)."""
    from PIL import Image
    out = f'{OUT}/refs/r88_{name}.jpg'
    if not os.path.exists(out):
        im = Image.open(f'media/kf/{name}.jpg').convert('RGB'); im.thumbnail((2048, 2048), Image.LANCZOS)
        im.save(out, 'JPEG', quality=92)
    return out


# ---- lyric lines (all shots) for muting the other singer
SH = json.load(open('docs/shots.json'))['shots']
LINES = {}
for s in SH:
    for l in s.get('lyrics', []):
        LINES[(l['start'], l['text'])] = l
LINES = sorted(LINES.values(), key=lambda l: l['start'])


def audio_window(shot, t0, dur, target, mute_before=None):
    """Vocal stem window [t0, t0+dur) as wav; lines sung only by the other singer are muted (20 ms fades)."""
    info = sf.info('work/stems/vocals.wav')
    sr = info.samplerate
    x, _ = sf.read('work/stems/vocals.wav', start=int(round(t0 * sr)), frames=int(round(dur * sr)), always_2d=True)
    g = np.ones(len(x))
    other = {'child': 'mom', 'mom': 'child'}.get(target)
    spans = [(l['start'] - 0.05, l['end'] + 0.08) for l in LINES if other and l['singer'] == other]
    if mute_before is not None:
        spans.append((t0 - 1, mute_before))
    tt = t0 + np.arange(len(x)) / sr
    fade = 0.02
    for a, b in spans:
        m = np.clip(np.minimum((tt - a) / fade, (b - tt) / fade), 0, 1)
        g = np.minimum(g, 1 - m)
    x = x * g[:, None]
    p = f'{OUT}/audio/{shot}.wav'
    sf.write(p, x, sr)
    return p


def sing(who, words, extra=''):
    if who == 'child':
        s = (f"Animate the first frame exactly. The little girl SINGS softly, a child singing to her mother, the words "
             f"\"{words}\", in precise lip sync with the reference audio: mouth shapes of singing, head still, "
             f"eyes on her mother.")
    elif who == 'mom':
        s = (f"Animate the first frame exactly. The mother SINGS softly, a mother singing a bedtime story to her little "
             f"daughter, the words \"{words}\", in precise lip sync with the reference audio: mouth shapes of singing, "
             f"head still, eyes on her daughter.")
    else:
        s = (f"Animate the first frame exactly. The mother and her little daughter sitting side by side both SING "
             f"softly together, the words \"{words}\", in precise lip sync with the reference audio: mouth shapes of "
             f"singing, heads still.")
    return f"{s} {extra} Nothing else moves. {LOOK} 16:9."


# ---- Kling v4 motion: shot -> (first, last, dur, prompt)
FL = "The video starts exactly on @image_1 and ends exactly on @image_2. "
KLING = {
    'A3': ('A3', 'A3_end', 3, FL + "In the dark attic the mother comes up out of the bright stairwell doorway and takes "
           "one step into the room, small in the frame, drying her hands on her apron. The little girl sitting on her mat "
           "in the foreground, her back to us, stays still. The warm light from the doorway stays steady. " + LOOK),
    'A4': ('A4', 'A4_end', 3, FL + "The mother's two hands lift the closed red cloth-covered storybook off the white pillow "
           "and tilt it upright; its cover catches a sheen of red light. One smooth, gentle movement, then the hands hold "
           "still. " + LOOK),
    'C2': ('C2', None, 3, "Animate the first frame exactly. The little girl's two small hands, raised in front of the "
           "open blank book, quickly settle into a hand-shadow shape: two fingers lift up like ears and the flat hand "
           "stretches forward like a snout, then they hold perfectly still. The book held open stays still." + BLANK
           + " " + LOOK),
    'C5a': ('C5a', 'C5a_end', 3, FL + "The mother, in profile, leans a little toward the open book and blows softly "
            "across the page; a faint breath of mist drifts toward the page and dust motes swirl slowly in the red light "
            "from the window behind her." + BLANK + " " + LOOK),
    'D9': ('D9', None, 4, "Animate the first frame exactly. The little girl balances on one leg on her mat in the "
           "Peking-opera look-out pose, one hand shading her eyes, wobbling a little and holding the pose proudly; her "
           "mother sitting on the floor laughs, her raised hand waving once. Nothing else moves." + BLANK + " " + LOOK),
    'E5': ('E5', None, 3, "Animate the first frame exactly. Behind her cupped hand the mother whispers a secret close to "
           "the little girl's ear, her lips moving slightly and her eyes amused; the little girl's eyes slide toward her "
           "mother. Nothing else moves. " + LOOK),
    'E6': ('E6', 'E6_end', 3, FL + "The mother leans back chuckling with her hand by her mouth, shoulders shaking "
           "slightly; the little girl beside her, facing front, keeps her eyes slid sideways toward her mother, and at "
           "the very end her eyes go wide. Nothing else moves. " + LOOK),
    'F3b': ('F3b', None, 3, "Animate the first frame exactly. The little girl blows across her open palm held under her "
            "lips; a few tiny hairs lift off the palm and fly away toward the left. The mother sitting in the dark at the "
            "left stays still. Nothing else moves. " + LOOK),
    'G4': ('G4', None, 6, "Animate the first frame exactly. The mother's hand, its finger and thumb making a small ring, "
           "slowly lowers a little toward the little girl's head; the little girl lying on her tummy beside the open "
           "book stays still and looks up. Nothing else moves." + BLANK + " " + LOOK),
}

# ---- Seedance 2.5 lip-sync: shot -> (audio t0, dur, singer, words, extra, takes=[(first, last)])
LIP = {
    'B1': (15.31, 7, 'child', "Mama, will you tell me before I sleep, how Sun Wukong came to be?",
           "Her face stays deadpan. The mother at the left edge stays still and soft.", [('B1', None), ('B1', None)]),
    'B2': (22.29, 4, 'mom', "On Hua Guo Shan, where the cliffs run steep",
           "The open book lies across her knees." + BLANK + " The little girl stays still.", [('B2', None), ('B2', 'B2_end')]),
    'C3': (45.665, 4, 'mom', "Not yet, that's just the start",
           "Amused, she gently presses the little girl's raised hands down with one finger.", [('C3', 'C3_end'), ('C3', 'C3_end')]),
    'D3b': (64.0, 4, 'both', "No cradle, no lullaby, no song", "The book lies open on the mat between them." + BLANK,
            [('D3b', None), ('D3b', None)]),
    'E1': (85.345, 5, 'mom', "The monkey had a memory just like you",
           "On the last word, 'you', she taps the little girl's nose with her fingertip.", [('E1', None), ('E1', 'E1_end')]),
    'E3': (92.49, 8, 'child', "Names and faces, I lose a few, but a spell I'd remember well",
           "Her face stays deadpan; on 'lose a few' she gives one small shrug.", [('E3', None), ('E3', None)]),
    'G1': (120.958, 7, 'child', "Why does he wear a band of gold? Is it heavy? Is it cold?",
           "She touches her own forehead with her fingertips and keeps them there.", [('G1_end', 'G1'), ('G1', None)]),
    'G3': (133.87, 8, 'child', "It isn't fair, it isn't fair, I don't want it in his hair",
           "She puts her small hand flat over the picture on the page and keeps it there.", [('G3_end', 'G3'), ('G3', None)]),
    'G5': (145.958, 4, 'child', "Yes",
           "For the first two seconds she holds perfectly still, holding her mother's look (her mother is just off to the "
           "left); only her eyes move slightly. Then she says the one soft word, 'Yes', barely parting her lips.",
           [('G5', None), ('G5', None)]),
}
MUTE_BEFORE = {'G5': 148.62, 'C3': 46.12}   # silence before the target's first word (Yes / after 'Monkey!')


def main():
    specs = []
    order = ['B1', 'B2', 'C2', 'G5', 'D3b', 'E5', 'E6', 'C3', 'G4', 'G1', 'G3', 'A3', 'A4', 'E1', 'E3', 'D9', 'C5a', 'F3b']
    for shot in order:
        if shot in KLING:
            a, b, d, p = KLING[shot]
            tag = f'r88_{shot}_kling4_t1'
            inp = {"prompt": p, "first_frame": 'file:' + ref(a), "duration": d, "aspect_ratio": "16:9", "resolution": "720p"}
            if b:
                inp["last_frame"] = 'file:' + ref(b)
            json.dump({"model": "klingai/kling-v4", "tag": tag, "notes": f"ROOMS-88 {shot}; first {a} last {b}", "input": inp},
                      open(f'media/gen/specs/{tag}.json', 'w'), indent=1, ensure_ascii=False)
            open(f'{OUT}/prompts/{tag}.txt', 'w').write(f'first {a} last {b} dur {d}\n\n{p}\n')
            specs.append(f'media/gen/specs/{tag}.json')
        if shot in LIP:
            t0, d, who, words, extra, takes = LIP[shot]
            wav = audio_window(shot, t0, d, who, MUTE_BEFORE.get(shot))
            for k, (a, b) in enumerate(takes, 1):
                tag = f'r88_{shot}_sd25_t{k}'
                p = sing(who, words, extra)
                if b:
                    p = p.replace("Animate the first frame exactly.", "The video starts exactly on the first frame and ends exactly on the last frame.")
                args = [PY, 'tools/gen/gen.py', 'spec', tag, 'bytedance/seedance-2.5', '--prompt', p, '--image', ref(a),
                        '--audio', f'{wav}@0+{d}', '--set', 'resolution="720p"', '--set', f'duration={d}',
                        '--set', 'camera_fixed=true', '--set', 'generate_audio=false',
                        '--notes', f'ROOMS-88 {shot} take {k}; audio vocals.wav {t0}+{d} (other singer muted); first {a} last {b}']
                if b:
                    args += ['--last-frame', ref(b)]
                subprocess.run(args, check=True, stdout=subprocess.DEVNULL)
                open(f'{OUT}/prompts/{tag}.txt', 'w').write(f'first {a} last {b} audio vocals.wav {t0}+{d}\n\n{p}\n')
                specs.append(f'media/gen/specs/{tag}.json')
    if '--only' in sys.argv:
        keep = sys.argv[sys.argv.index('--only') + 1].split(',')
        specs = [s for s in specs if any(f'r88_{k}_' in s for k in keep)]
    for s in specs:
        r = subprocess.run([PY, 'tools/gen/gen.py', 'submit', s] + ([] if '--submit' in sys.argv else ['--dry-run']),
                           capture_output=True, text=True)
        print(os.path.basename(s), (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else '')


if __name__ == '__main__':
    main()

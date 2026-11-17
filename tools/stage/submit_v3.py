"""Stage team v3 (yellow monkey): first+last-frame clips. Writes media/gen/specs/s3_<shot>_<take>.json and
media/gen/stage/v3/prompts/<shot>.txt.   PY tools/stage/submit_v3.py [--submit] [only ...]"""
import json, subprocess, sys, os
PY = sys.executable
LOOK = ("He stays a painting on paper: quick black ink line and a wet gamboge-yellow wash scattered with small dark "
        "swirl marks, his round yellow cap with its row of pompoms, the yellow scarf knotted at his throat, black sash, "
        "dark ochre flap skirt, black boots, the small red patch around his eyes, and the long dark staff with a gold band "
        "at each end. ")
GUARD = (LOOK + "The cream paper around him stays bare. Locked-off camera. No ground, no shadow, no background, no tail, "
         "no feathers, nothing new appears.")
FL = "The video starts exactly on @image_1 and ends exactly on @image_2. "
P = {
 'd1': (FL + "One violent throw of black ink is flung across the bare cream paper from the upper right: a single flying "
        "sheet of wet black ink and scattered droplets crosses the sheet and slaps down, bursts and bleeds into the "
        "absorbent paper, and in one breath the black splash gathers into the brush-drawn monkey in his pose; as he "
        "lands, a wet gamboge-yellow wash floods outward through his costume from the chest, blooming into the ink "
        "lines like yellow pigment dropped into wet paper, until the whole figure is yellow; then he holds perfectly "
        "still for the last two seconds. Real ink and watercolour on real xuan paper: matte, soaking, feathered edges, "
        "never glossy or liquid-looking. Locked-off camera, flat paper, nothing else appears."),
 'd2': ("The Peking-opera monkey sets his raised foot down, tucks the staff under one arm and performs four formal bows to "
        "the four directions as ONE continuous flowing movement, never stopping between them: fists cupped in salute, he "
        "bows deeply to his right (profile facing right), sweeps round a quarter turn and bows deeply straight toward us, "
        "sweeps round and bows deeply to his left (profile facing left), sweeps round and bows deeply away from us with "
        "his back to us. Four bows, evenly spaced, about one second each, each a deep fold from the waist with a small "
        "weighty dip at the bottom, his scarf ends swinging round after him. He stays on the same spot. Peking-opera "
        "precision: smooth, weighty, formal, a little proud. " + GUARD),
 'd6': (FL + "The Peking-opera monkey runs in and launches a string of somersaults across the sheet from right to left: "
        "three fast high tucked somersaults in the air, one after another, his body a spinning yellow ball, the staff in one "
        "hand and his scarf ends whipping round him, and he lands on the left side and snaps into his pose, one knee up, "
        "hand shading his eyes, perfectly still for the last second. Trained wushu acrobatics: crisp, weighty, "
        "committed. " + GUARD),
 'd7': (FL + "The Peking-opera monkey spins the long staff in a fast staff flower in front of his body, hand to hand, the "
        "staff wheeling in circles that leave dry-brush ink rings on the paper like a brush, his scarf ends swinging in "
        "wide arcs, then he drops into a deep lunge and drives the staff out level, and freezes on the last beat. "
        "Trained wushu precision: crisp, weighty, committed. " + GUARD),
 'd8': (FL + "The Peking-opera monkey stands the long staff upright and plants it, then scrambles up it hand over foot in "
        "two quick moves and perches crouched on the very top of the standing staff, one hand shading his eyes as he "
        "looks out far into the distance, and holds perfectly still for the last second, balanced. Agile, light, a "
        "little comic. " + GUARD),
 'j3': (FL + "The Peking-opera monkey explodes into a full staff form, bigger and wilder than before: the staff whirls "
        "overhead, sweeps low in a wide circle, he leaps and turns in the air, the staff tearing broad dry-brush ink arcs "
        "across the paper, his scarf ends lashing, and he lands in a deep lunge driving the staff out level and freezes "
        "on the last beat. Trained wushu power: fast, weighty, committed. " + GUARD),
}
R = 'file:media/gen/refs/s3_'
# take -> (model key, first, last or None, resolution, prompt prefix override)
TAKES = {
 'd1': [('sd20', 'blank', 'd1_last', '1080p'), ('sd20b', 'blank', 'd1_last', '720p')],
 'd2': [('kling4', 'd1_last', 'd2_last', '1080p'), ('kling4ff', 'd1_last', None, '1080p'), ('sd20', 'd1_last', 'd2_last', '720p')],
 'd6': [('kling4', 'd6_first', 'd6_last', '1080p'), ('sd20', 'd6_first', 'd6_last', '720p')],
 'd7': [('sd20', 'd7_first', 'd7_last', '1080p'), ('kling4', 'd7_first', 'd7_last', '1080p')],
 'd8': [('kling4', 'd8_first', 'd8_last', '1080p'), ('sd20', 'd8_first', 'd8_last', '720p')],
 'j3': [('kling4', 'j3_first', 'j3_last', '1080p'), ('sd20', 'j3_first', 'j3_last', '720p')],
}
os.makedirs('media/gen/stage/v3/prompts', exist_ok=True)
only = [a for a in sys.argv[1:] if not a.startswith('--')]
specs = []
for shot, takes in TAKES.items():
    open(f'media/gen/stage/v3/prompts/{shot}.txt', 'w').write(P[shot] + '\n\n' + json.dumps(takes) + '\n')
    for key, a, b, res in takes:
        tag = f's3_{shot}_{key}'
        if only and shot not in only and tag not in only:
            continue
        prompt = P[shot]
        if shot == 'd2':
            prompt = ((FL if b else 'Animate the first frame exactly. ') + prompt)
        if key.startswith('kling4'):
            inp = {"prompt": prompt, "first_frame": R + a + '.jpg', "duration": 5, "aspect_ratio": "16:9", "resolution": res}
            if b:
                inp["last_frame"] = R + b + '.jpg'
            spec = {"model": "klingai/kling-v4", "tag": tag, "notes": f"stage v3 {shot}", "input": inp}
        else:
            inp = {"prompt": prompt, "image": R + a + '.jpg', "resolution": res, "camera_fixed": True, "duration": 5}
            if b:
                inp["last_frame_image"] = R + b + '.jpg'
            spec = {"model": "bytedance/seedance-2.0", "tag": tag, "notes": f"stage v3 {shot}", "input": inp}
        json.dump(spec, open(f'media/gen/specs/{tag}.json', 'w'), indent=1, ensure_ascii=False)
        specs.append(f'media/gen/specs/{tag}.json')
for s in specs:
    args = [PY, 'tools/gen/gen.py', 'submit', s] + ([] if '--submit' in sys.argv else ['--dry-run'])
    r = subprocess.run(args, capture_output=True, text=True)
    print(s, (r.stdout + r.stderr).strip().splitlines()[-1])

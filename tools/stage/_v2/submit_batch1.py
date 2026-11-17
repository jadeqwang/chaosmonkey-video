"""Stage team batch 1: first+last-frame clips for D1, D6, D7, D8, J3 on Kling v4 and Seedance 2.0 (1080p, 5 s).
Writes media/gen/specs/stg_<shot>_<model>.json and media/gen/stage/prompts/<tag>.txt.  --submit to queue."""
import json, subprocess, sys, os
PY = sys.executable
GUARD = ("He stays a painting of wet black ink washes and a few quick brushstrokes, with the small red face patch, "
         "exactly two long plumes and the banded staff; the cream paper around him stays bare. Locked-off camera. "
         "No ground, no shadow, no background, nothing new appears.")
P = {
 'd1': ("The video starts exactly on @image_1 and ends exactly on @image_2. One violent throw of black ink is flung "
        "across the bare cream paper from the upper right: a single flying sheet of wet ink and scattered droplets "
        "crosses the sheet and slaps down, bursts and bleeds into the absorbent paper, and in one breath the splash "
        "gathers into the ink painting of the monkey in his pose, which then holds perfectly still for the last two "
        "seconds. Real ink on real xuan paper: matte, soaking, feathered edges, never glossy or liquid-looking. "
        "Locked-off camera, flat paper, nothing else appears."),
 'd6': ("The video starts exactly on @image_1 and ends exactly on @image_2. The splashed-ink Peking-opera monkey "
        "runs in and launches a tumbling pass across the sheet from right to left: two fast cartwheels and a twisting "
        "aerial somersault, the staff in one hand and his two plumes whipping behind him, and he lands on the left "
        "side and snaps into his pose, one knee up, hand shading his eyes, perfectly still for the last second. "
        "Trained wushu acrobatics: crisp, weighty, committed. " + GUARD),
 'd7': ("The video starts exactly on @image_1 and ends exactly on @image_2. The splashed-ink Peking-opera monkey "
        "spins the long staff in a fast staff flower in front of his body, hand to hand, the staff wheeling in circles "
        "that leave dry-brush rings on the paper like a brush, his two plumes swinging in wide arcs, then he drops "
        "into a deep lunge and drives the staff out level, and freezes on the last beat. Trained wushu precision: "
        "crisp, weighty, committed. " + GUARD),
 'd8': ("The video starts exactly on @image_1 and ends exactly on @image_2. The splashed-ink Peking-opera monkey "
        "stands the long staff upright and plants it, then scrambles up it hand over foot in two quick moves and "
        "perches crouched on the very top of the standing staff, one hand shading his eyes as he looks out far into "
        "the distance, and holds perfectly still for the last second, balanced. Agile, light, a little comic. " + GUARD),
 'j3': ("The video starts exactly on @image_1 and ends exactly on @image_2. The splashed-ink Peking-opera monkey "
        "explodes into a full staff form, bigger and wilder than before: the staff whirls overhead, sweeps low in a "
        "wide circle, he leaps and turns in the air, the staff tearing broad dry-brush arcs across the paper, his two "
        "plumes lashing, and he lands in a deep lunge driving the staff out level and freezes on the last beat. "
        "Trained wushu power: fast, weighty, committed. " + GUARD),
}
FRAMES = {'d1': ('blank', 'd1_last'), 'd6': ('d6_first', 'd6_last'), 'd7': ('d7_first', 'd7_last'),
          'd8': ('d8_first', 'd8_last'), 'j3': ('j3_first', 'j3_last')}
os.makedirs('media/gen/stage/prompts', exist_ok=True)
specs = []
for shot, prompt in P.items():
    a, b = FRAMES[shot]
    tag = f'stg_{shot}_kling4'
    spec = {"model": "klingai/kling-v4", "tag": tag,
            "notes": f"stage {shot}; first media/gen/stage/frames/{a}.jpg; last media/gen/stage/frames/{b}.jpg",
            "input": {"prompt": prompt, "first_frame": f"file:media/gen/refs/stg_{a}_2048.jpg",
                      "last_frame": f"file:media/gen/refs/stg_{b}_2048.jpg", "duration": 5,
                      "aspect_ratio": "16:9", "resolution": "1080p"}}
    json.dump(spec, open(f'media/gen/specs/{tag}.json', 'w'), indent=1, ensure_ascii=False)
    specs.append(f'media/gen/specs/{tag}.json')
    tag = f'stg_{shot}_sd20'
    subprocess.run([PY, 'tools/gen/gen.py', 'spec', tag, 'bytedance/seedance-2.0', '--prompt', prompt,
                    '--image', f'media/gen/stage/frames/{a}.jpg', '--last-frame', f'media/gen/stage/frames/{b}.jpg',
                    '--set', 'resolution="1080p"', '--set', 'camera_fixed=true', '--set', 'duration=5'], check=True,
                   stdout=subprocess.DEVNULL)
    specs.append(f'media/gen/specs/{tag}.json')
    open(f'media/gen/stage/prompts/{shot}.txt', 'w').write(f'first {a}.jpg  last {b}.jpg\n\n{prompt}\n')
for s in specs:
    args = [PY, 'tools/gen/gen.py', 'submit', s] + ([] if '--submit' in sys.argv else ['--dry-run'])
    r = subprocess.run(args, capture_output=True, text=True)
    print(s, (r.stdout + r.stderr).strip().splitlines()[-1])

"""Stage team v4 (costume B): video takes. Writes media/gen/specs/s4_<shot>_<take>.json and
media/gen/stage/v4/prompts/<shot>.txt.   PY tools/stage/submit_v4.py [--submit] [only ...]
Kling v4 takes use first_frame + middle_frames + last_frame (multi-keyframe): every pose is pinned."""
import json, subprocess, sys, os
PY = sys.executable
LOOK = ("He stays a painting on paper, exactly as in the keyframes: quick black ink line and transparent gamboge-yellow "
        "wash; yellow jacket and trousers with a black key-fret pattern, leopard-spot fur trim at the collar, cuffs and "
        "flap skirt, black sash, cinnabar-red scarf knotted at the throat, soft yellow cap with pompoms, black boots, the "
        "red heart-shaped field round his gold eyes, the long dark staff with a gold band at each end. His hands keep "
        "five fingers and his limbs stay attached and solid; he moves through every position in between, never jumping "
        "from one pose to the next. ")
GUARD = (LOOK + "The cream paper around him stays bare and still. Locked-off camera, no zoom, no pan. No ground, no "
         "shadow, no background, no tail, no feathers, no text, nothing new appears.")
P = {
 'd1': ("The video starts on the bare cream paper of @image_1 and ends exactly on @image_2. One violent throw of black "
        "ink is flung across the paper from the upper right: a single flying sheet of wet black ink and droplets crosses "
        "the sheet and slaps down, bursts and bleeds into the absorbent paper, and in one breath the splash gathers into "
        "the brush-drawn monkey in his pose; as he lands, gamboge-yellow wash, cinnabar red and the black key-fret "
        "pattern flood outward through his costume from the chest like pigment dropped into wet paper, until he is "
        "exactly the figure of @image_2; then he holds the pose for the last two seconds, alive: the scarf ends lift, "
        "he breathes, his eyes flick once. Real ink and watercolour on real xuan paper: matte, soaking, feathered "
        "edges, never glossy or liquid-looking. Locked-off camera, flat paper, nothing else appears."),
 'd2': ("A Peking-opera monkey performs four formal bows to the four directions as ONE continuous, smooth, weighty "
        "movement, staying on the same spot. @image_1: he holds his look-out pose on one leg. He sets the raised foot "
        "down, brings the staff under his left arm and joins his hands in the martial salute (the right hand a fist, "
        "the open left palm laid over it, held close to the chest, elbows out). @image_2: turned to face the right, he "
        "folds deeply from the hips, back straight, head down. He rises, steps round a quarter turn and @image_3: bows "
        "deeply straight toward us, the top of his cap showing. He rises, turns, and @image_4: bows deeply to the left "
        "in profile. He rises, turns his back to us and @image_5: bows deeply away from us. Rhythm: rise, turn, fold, "
        "with a small weighty settle at the bottom of each bow; the four bows evenly spaced. The joined hands stay at "
        "his chest the whole time: he never pushes his palms forward. His scarf ends swing round after each turn. " + GUARD),
 'd2r2': ("A Peking-opera monkey performs four formal bows to the four directions as ONE continuous, smooth, weighty "
        "movement on the same spot, the keyframes in order: @image_1 his look-out pose on one leg; he sets the foot down "
        "and turns to face the right, standing upright in the martial salute, @image_2 (the right hand a fist, the open "
        "left palm laid over it, close to the chest, elbows out, the staff under his left arm); he folds deeply from "
        "the hips, @image_3; rises upright as he pivots to face us, @image_4; bows deeply toward us, @image_5; rises as "
        "he pivots to face the left, @image_6; bows deeply to the left, @image_7; rises as he pivots to turn his back "
        "to us, @image_8; bows deeply away from us, @image_9. Every rise flows into the turn and every turn into the "
        "next fold, with a small weighty settle at the bottom of each bow. His hands stay joined in the salute at his "
        "chest from @image_2 to the end and the staff stays under his left arm. His scarf ends swing round after each "
        "turn. " + GUARD),
 'd6r2': ("The Peking-opera monkey arrives on his somersault cloud, keyframes in order: @image_1 he rides a small curling "
        "ink cloud in from the right, leaning into the speed; @image_2 he springs off it into a tucked somersault above "
        "it; the cloud thins away to nothing while @image_3 he opens out, stretched and upside down in the air, "
        "travelling left; @image_4 he drops to a low landing crouch, one hand touching down; @image_5 he springs up "
        "into his look-out pose on one leg, knee raised, hand flat above his eyes, staff behind his back, and holds "
        "it perfectly still for the last second. Trained wushu acrobatics: crisp, light, a weighty landing. " + GUARD),
 'd6': ("The Peking-opera monkey arrives on his somersault cloud. @image_1: he rides a small curling ink cloud in from "
        "the right, leaning into the speed, hand at his brow. He springs off it into a high tucked somersault, "
        "@image_2: upside down above the cloud, which curls round under him; he turns over once more in the air while "
        "the cloud breaks into a few curls of ink and thins away to nothing, and he drops onto one foot and snaps into "
        "@image_3: his look-out pose on one leg, knee raised, hand flat above his eyes, staff behind his back, and "
        "holds it perfectly still for the last second. Trained wushu acrobatics: crisp, light, weighty landing. " + GUARD),
 'd7': ("The Peking-opera monkey performs a staff flower. @image_1: the staff begins to spin in front of his body, hand "
        "to hand, faster and faster, wheeling in circles that leave dry-brush ink rings on the paper like a brush; "
        "@image_2: he lifts it into a flat spin above his head on one leg; then he drops into a deep lunge and drives "
        "the staff out level, @image_3, and freezes on the last beat. Trained wushu precision: crisp, weighty, "
        "committed, the staff a blur only at its fastest. " + GUARD),
 'd7sd': ("The video starts exactly on @image_1 and ends exactly on @image_2. The Peking-opera monkey spins the long "
        "staff in a fast staff flower in front of his body, hand to hand, the staff wheeling in circles that leave "
        "dry-brush ink rings on the paper like a brush, his scarf ends swinging in wide arcs, then he drops into a deep "
        "lunge and drives the staff out level, and freezes on the last beat. Trained wushu precision: crisp, weighty, "
        "committed. " + GUARD),
 'd8': ("The Peking-opera monkey climbs his own staff. @image_1: he holds a low lunge with the staff level. He swings the "
        "staff upright and plants its foot on the ground; @image_2: gripping it with both hands he puts one foot on it. "
        "He climbs it continuously, hand over hand, feet clasping the staff, the staff standing perfectly still and "
        "upright, held up only by him: @image_3 a third of the way up, @image_4 near the top, pulling himself onto it; "
        "@image_5: he crouches balanced on the very top end, one hand flat above his eyes, looking far out to the left, "
        "and holds perfectly still for the last second. Agile, light, a little comic, every movement continuous, the "
        "staff never changes length. " + GUARD),
 'j3': ("The Peking-opera monkey explodes into a full staff form, bigger and wilder than before. @image_1: he brings the "
        "staff down from overhead in a great strike; @image_2: drops into a low sweep, the staff skimming the ground; "
        "springs up and @image_3: whirls it flat over his head on one leg; and lands in a deep lunge driving the staff "
        "out level, @image_4, freezing on the last beat. The staff tears broad wet dry-brush ink arcs across the "
        "paper; his scarf ends lash. Trained wushu power: fast, weighty, committed. " + GUARD),
}
R = 'file:media/gen/refs/s4_'
# (take key, model, frames, resolution, duration, prompt key)
TAKES = {
 'd1': [('sd20a', 'sd20', ['blank', 'd1_last'], '1080p', 5, 'd1', 11), ('sd20b', 'sd20', ['blank', 'd1_last'], '1080p', 5, 'd1', 23),
        ('sd20c', 'sd20', ['blank', 'd1_last'], '1080p', 5, 'd1', 37), ('h3', 'h3', ['blank', 'd1_last'], '2K', 5, 'd1', None)],
 'd2': [('k4a', 'k4', ['d1_last', 'd2_e', 'd2_s', 'd2_w', 'd2_n'], '1080p', 5, 'd2', None),
        ('k4b', 'k4', ['d1_last', 'd2_e', 'd2_s', 'd2_w', 'd2_n'], '1080p', 6, 'd2', None),
        ('k4c', 'k4', ['d1_last', 'd2_e', 'd2_s', 'd2_w', 'd2_n'], '1080p', 7, 'd2', None)],
 'd6': [('k4a', 'k4', ['d6_first', 'd6_mid', 'd6_last'], '1080p', 5, 'd6', None),
        ('k4b', 'k4', ['d6_first', 'd6_mid', 'd6_last'], '1080p', 6, 'd6', None),
        ('k4c', 'k4', ['d6_first', 'd6_mid', 'd6_last'], '1080p', 5, 'd6', None)],
 'd2r2': [('k4d', 'k4', ['d1_last', 'd2_se', 'd2_e', 'd2_ss', 'd2_s', 'd2_sw', 'd2_w', 'd2_sn', 'd2_n'], '1080p', 8, 'd2r2', None),
          ('k4e', 'k4', ['d1_last', 'd2_se', 'd2_e', 'd2_ss', 'd2_s', 'd2_sw', 'd2_w', 'd2_sn', 'd2_n'], '1080p', 8, 'd2r2', None),
          ('k4f', 'k4', ['d1_last', 'd2_se', 'd2_e', 'd2_ss', 'd2_s', 'd2_sw', 'd2_w', 'd2_sn', 'd2_n'], '1080p', 9, 'd2r2', None)],
 'd6r2': [('k4d', 'k4', ['d6_first', 'd6_mid', 'd6_layout', 'd6_crouch', 'd6_last'], '1080p', 6, 'd6r2', None),
          ('k4e', 'k4', ['d6_first', 'd6_mid', 'd6_layout', 'd6_crouch', 'd6_last'], '1080p', 6, 'd6r2', None)],
 'd7': [('sd20a', 'sd20', ['d7_first', 'd7_last'], '1080p', 5, 'd7sd', 5), ('sd20b', 'sd20', ['d7_first', 'd7_last'], '1080p', 5, 'd7sd', 19),
        ('k4a', 'k4', ['d7_first', 'd7_mid', 'd7_last'], '1080p', 5, 'd7', None)],
 'd8': [('k4a', 'k4', ['d8_first', 'd8_plant', 'd8_low', 'd8_high', 'd8_last'], '1080p', 5, 'd8', None),
        ('k4b', 'k4', ['d8_first', 'd8_plant', 'd8_low', 'd8_high', 'd8_last'], '1080p', 6, 'd8', None),
        ('k4c', 'k4', ['d8_first', 'd8_plant', 'd8_low', 'd8_high', 'd8_last'], '1080p', 5, 'd8', None)],
 'j3': [('k4a', 'k4', ['j3_first', 'j3_sweep', 'j3_spin', 'j3_last'], '1080p', 5, 'j3', None),
        ('k4b', 'k4', ['j3_first', 'j3_sweep', 'j3_spin', 'j3_last'], '1080p', 6, 'j3', None),
        ('sd20a', 'sd20', ['j3_first', 'j3_last'], '1080p', 5, 'd7sd', 7)],
}
os.makedirs('media/gen/stage/v4/prompts', exist_ok=True)
only = [a for a in sys.argv[1:] if not a.startswith('--')]
specs = []
for shot, takes in TAKES.items():
    open(f'media/gen/stage/v4/prompts/{shot}.txt', 'w').write('\n\n'.join(P[k] for k in sorted({t[5] for t in takes})) + '\n\n' + json.dumps(takes) + '\n')
    for key, model, fr, res, dur, pk, seed in takes:
        tag = f's4_{shot[:2]}_{key}'
        if only and shot not in only and tag not in only:
            continue
        prompt = P[pk]
        if shot == 'j3' and model == 'sd20':
            prompt = prompt.replace('spins the long staff in a fast staff flower in front of his body, hand to hand',
                                    'explodes into a full staff form: the staff whirls overhead and sweeps low in wide circles, he leaps and turns')
        if model == 'k4':
            inp = {"prompt": prompt, "first_frame": R + fr[0] + '.jpg', "duration": dur, "aspect_ratio": "16:9", "resolution": res,
                   "last_frame": R + fr[-1] + '.jpg'}
            if len(fr) > 2:
                inp["middle_frames"] = [R + x + '.jpg' for x in fr[1:-1]]
            spec = {"model": "klingai/kling-v4", "tag": tag, "notes": f"stage v4 {shot}", "input": inp}
        elif model == 'sd20':
            inp = {"prompt": prompt, "image": R + fr[0] + '.jpg', "last_frame_image": R + fr[-1] + '.jpg', "resolution": res,
                   "camera_fixed": True, "duration": dur, "generate_audio": False, "seed": seed}
            spec = {"model": "bytedance/seedance-2.0", "tag": tag, "notes": f"stage v4 {shot}", "input": inp}
        else:
            inp = {"prompt": prompt.replace('@image_1', 'the first frame').replace('@image_2', 'the last frame'),
                   "image": R + fr[0] + '.jpg', "last_frame_image": R + fr[-1] + '.jpg', "resolution": res,
                   "ratio": "adaptive", "duration": dur}
            spec = {"model": "minimax/h3", "tag": tag, "notes": f"stage v4 {shot}", "input": inp}
        json.dump(spec, open(f'media/gen/specs/{tag}.json', 'w'), indent=1, ensure_ascii=False)
        specs.append(f'media/gen/specs/{tag}.json')
for s in specs:
    args = [PY, 'tools/gen/gen.py', 'submit', s] + ([] if '--submit' in sys.argv else ['--dry-run'])
    r = subprocess.run(args, capture_output=True, text=True)
    print(s, (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else '')

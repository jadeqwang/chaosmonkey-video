#!/usr/bin/env python3
"""SETS v4: painted master plates of the empty rooms (gpt-image-2), one look/placement reference per set.
$PY tools/gen/sets_master_v4.py [key ...]   ->  media/kf/v4/_sets/<key>.jpg + .txt (prompt + inputs)
Inputs per plate: the empty-room guide (media/layout/<set>/v4_MASTER*_line.png: structure), its lit preview (light), and
clean frames of accepted v3 shots (style only: media/kf/v4/_sets/refs/v3_*.png, extracted from media/comp/*.mp4).
No real photographs, no v1/v2 character images. The neon lettering is left illegible: Chinese is typeset later, never drawn."""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf
ROOT = cf.ROOT
OUT = "media/kf/v4/_sets"
STYLE = ("A hand-painted illustration in the exact style of images 3 and 4 (frames from the same film): soft gouache and coloured "
         "pencil on textured paper, visible paper grain, warm painterly light, gentle grain, no hard digital edges, not a photograph, not a 3D render. ")
RULES = ("Image 1 is a 3D layout line drawing of this exact room from this exact camera: keep the camera, the perspective, the horizon and "
         "EVERY object exactly where it is drawn, at the size and shape drawn; do not add, remove, move or resize any object; nothing that is "
         "not in image 1 may appear. Image 2 is the same view as a lighting preview: copy where the light comes from and where it falls. "
         "Images 3 and 4 are for style, palette and the look of the materials only; ignore their camera, their people and their objects' positions. "
         "The room is EMPTY: no people, no animals, no hands. No text, no letters, no signature, no watermark, no border. ")
J = lambda s, sh: f"media/layout/{s}/v4_{sh}"
JOBS = {
  "attic88_master": ("attic88", "MASTER_window", ["refs/v3_B2.png", "refs/v3_L2b.png"],
    "The attic above a Chinese-Indonesian restaurant in the Netherlands, 1988, at night. Bare dark roof boards and rafters, a plank floor with thin "
    "warm amber light glowing up through the cracks between the boards, two thin cotton sleeping mats on the floor side by side with their "
    "pillows toward the window, a navy cotton quilt with a small flower print on the nearer mat and a beige quilt folded at the foot of the "
    "other, a crooked stack of nine school textbooks beside the pillow end, a small old CRT television (switched off) on a wooden crate under "
    "the slope at the left, a closed red cloth storybook on the boards. The only strong light is the one small four-pane window in the gable: "
    "outside it hangs a vertical red neon blade sign, seen almost edge-on, so the window holds a narrow glowing cinnabar-red wedge; the "
    "sign's lettering is NOT legible: only soft red glowing shapes, no characters. Red light spills from the window across the floor and the "
    "lower half of the mats; the pillow end under the sill is darker. Deep brown-black shadows, a hint of cold blue night ambient. "),
  "attic88_master_fallen": ("attic88", "MASTER_fallen", ["refs/v3_B2.png", "refs/v3_L2b.png"], None),
  "attic88_master_door": ("attic88", "MASTER_door", ["refs/v3_A3.png", "refs/v3_B2.png"],
    "The same 1988 attic at night, looking the other way, toward the stair door gable: the plank floor with warm light in the cracks, the "
    "stair door standing a little ajar with a thin tall slot of warm tungsten light from the stairwell, a wooden rail with four hooks on the "
    "wall right of the door with a pale apron and a white towel hanging on two of them, cardboard boxes and rice sacks along the walls, bare "
    "rafters and roof boards, collar ties. Faint red neon light comes from behind the camera onto the near floor. "),
  "bed26_master": ("bed26", "MASTER_lap", ["refs/v3_L1.png", "refs/v3_L2.png"],
    "A small child's bedroom in Austin, 2026, at night. A twin bed with a plain wooden headboard against the back wall, a white pillow, a pale "
    "lavender-white quilt, a small beige plush bunny with long ears sitting on the far side of the pillow, a wooden nightstand at the head "
    "of the bed with a cup and a small night-light (off) on it, a fluffy mauve rug on the wooden floor beside the bed, a white door standing "
    "open on the right with warm amber light from the hallway falling into the room. Blue-violet night shadows; the walls a soft blue-grey. "),
  "bed26_master_L2": ("bed26", "MASTER", ["refs/v3_L2.png", "refs/v3_L1.png"],
    "The same small child's bedroom at night seen from above the foot of the bed: the twin bed with its wooden headboard on the back wall, the "
    "white slatted blind on the window above and left of the headboard with blue night light between the slats, the wooden nightstand with a "
    "cup at the head of the bed on the window side, the plush bunny on the far side of the pillow, the quilt, the fluffy rug on the left, "
    "warm hallway light from the open door at the right edge. Blue-violet night. "),
  "car26_master": ("car26", "MASTER", ["refs/v3_F1.png", "refs/v3_F3a.png"],
    "Inside a compact SUV at dusk on a highway in Texas, looking back from between the two front seats: the two front seatbacks and headrests "
    "dark in the foreground at the left and right edges, and on the back bench TWO forward-facing child car seats side by side, both EMPTY, "
    "the harness of each lying open; beyond them the rear window and side windows with a violet blue-hour sky and amber sodium streetlights "
    "passing along the road. Warm amber light from the streetlights rakes across the seats; the cabin is dark and soft. "),
}
def jpg(src, dst, w=1536):
    im = Image.open(os.path.join(ROOT, src)).convert("RGB"); im.thumbnail((w, w)); im.save(os.path.join(ROOT, dst), quality=90); return dst
def run(k):
    st, sh, refs, desc = JOBS[k]
    if desc is None: desc = JOBS["attic88_master"][3].replace("a crooked stack of nine school textbooks beside the pillow end", "nine school textbooks lying scattered on the boards where a stack beside the pillow end has toppled, fanned out toward us exactly as drawn")
    os.makedirs(os.path.join(ROOT, OUT, "_in"), exist_ok=True)
    ins = [jpg(J(st, sh) + "_line.png", f"{OUT}/_in/{k}_line.jpg"), jpg(J(st, sh) + "_lit.png", f"{OUT}/_in/{k}_lit.jpg")] + [jpg(f"{OUT}/{r}", f"{OUT}/_in/{k}_style{i}.jpg") for i, r in enumerate(refs)]
    prompt = STYLE + desc + RULES
    params = {"size": "2048x1152", "quality": "high", "output_format": "jpeg", "images": ["file:" + p for p in ins]}
    out = f"{OUT}/{k}.jpg"
    open(os.path.join(ROOT, out[:-4] + ".txt"), "w").write("model: openai/gpt-image-2\n" + json.dumps(params) + "\n\n" + prompt + "\n")
    try: return k, cf.generate("openai/gpt-image-2", dict(params, prompt=prompt), out, tag="sets_master_v4")
    except Exception as e: return k, f"ERR {e}"
if __name__ == "__main__":
    keys = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(3) as ex:
        for r in ex.map(run, keys): print(r)

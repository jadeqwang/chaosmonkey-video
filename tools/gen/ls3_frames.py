#!/usr/bin/env python3
"""Lip-sync bake-off start frames (v3 faces, gpt-image-2). $PY tools/gen/ls3_frames.py [key ...]
Writes media/kf/v3/lipsync_test/<key>.jpg + .txt (prompt)."""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cf
R = "file:design/characters/"
HAND = ("A Chinese painting, ink and light colour on cream xuan paper, in one hand: fine-line baimiao outlines for the face and "
        "hands with light colour washes, dark ink washes for the room, the paper grain showing through everywhere. Face drawn in "
        "delicate fine ink lines with a light flesh wash, as in a Song or Ming figure painting, not anime, not a photograph, not a "
        "digital render. No text, no signature, no seal, no border, no logos. ")
SKIN = ("LIGHT AND SKIN: the coloured light is a thin transparent glaze laid OVER a normally painted face. Under it the face keeps "
        "its own warm, rosy flesh wash and pink blush; the shadow side is warm umber, never grey. The eyes stay as large as on the "
        "face sheets, dark irises with a bright clear highlight in each. ")
MOUTH = ("Her mouth is relaxed and softly closed with the lips just barely parted in the middle, as if she has just drawn a breath and is "
         "about to sing the first word; a clearly drawn upper and lower lip; no teeth showing. The whole face is clearly visible and "
         "evenly readable, the mouth and chin unobstructed, nothing in front of the face. ")
END = " Use them for likeness only; repaint in this painting."
LJ = ("Little Jade, 1988, age 5: a small Chinese girl with a big round head and a short round face, very full soft cheeks with a wide warm "
      "pink blush, a tiny button nose, a tiny soft mouth, and LARGE round dark eyes set wide apart, each with thick dark upper lashes and a "
      "bright clear highlight; distinct, fairly strong, straight dark eyebrows. Glossy jet-black hair: a light fringe of a few soft parted "
      "strands with the forehead showing between them, long side locks in front of the ears, a small half-ponytail tied high at the back of "
      "the crown, the rest straight to just past her shoulders. A cropped white zip jacket with a stand collar, one straight horizontal "
      "orange band across the chest and around both upper arms, a small pale-blue dot on her left chest. ")
MAMA = ("Mama, 1988: a Chinese woman aged 35, young and attractive, smooth unlined warm skin; a soft oval face with a gently pointed chin, "
        "long almond dark eyes, clearly drawn dark straight-ish eyebrows that read behind her glasses, a straight nose, a full mouth; glossy "
        "jet-black hair in a soft late-1980s perm of loose springy curls, side-parted, ending at the jaw (never longer); thin round wire-rim "
        "glasses; a plain cream cotton collarless blouse with a small notched neckline. NO apron. No wrinkles, no lines from nose to mouth: "
        "35, not 45. ")
DAU = ("The daughter, 2026, age 4: a small girl of mixed Chinese and European descent with a big round head and a short round face, very "
       "full soft cheeks with a wide warm pink blush, a tiny button nose, a tiny soft mouth, LARGE round dark-brown eyes each with a bright "
       "clear highlight and soft lashes, soft light-brown eyebrows. Warm brown curly hair (brown, never black): centre-parted, a braid "
       "running along each side of her head from the temple to behind the ear, into two low curly pigtails tied with pink bands, loose curly "
       "wisps at the temples and forehead. A pink short-sleeved dress with small puffed sleeves, printed all over with red strawberries with "
       "green tops. ")
JADE = ("Jade, 2026: a Chinese woman who looks about 30; an oval face with a softly pointed chin, almond eyes with deep near-black irises, "
        "dark, fairly strong eyebrows (the eyebrow on the LEFT of the picture is straight; the one on the RIGHT runs straight and then lifts "
        "into a soft arch), a straight nose, full lips; thin dark rectangular half-rim glasses; long black hair with NO fringe: an open "
        "forehead, parted slightly off-centre, swept to both sides in long soft face-framing layers with a loose wave, past the shoulders. A "
        "cropped white racer jacket, stand collar with two snap tabs, worn open over a black mock-neck top; one orange band across the chest "
        "and around each upper arm; a small pale-blue dot on her left chest; no logos. ")
ATTIC = ("The attic above a restaurant, 1988, at night, soft and out of focus behind her: sloped wooden ceiling, dark ink wash, a pool of "
         "red neon glow from a window out of frame on the right, thin amber lines of light between floorboards. ")
BED = ("A child's bedroom, 2026, at dusk, soft behind her: the side of a low bed with a rumpled quilt, dusk-violet shadow; warm white "
       "light bounces up onto her face from an open book below the frame. ")
JOBS = {
 "lj_sing": (["refs/lj_heads_v3.jpg", "refs/lj_heads_v3_hand.jpg", "little_jade/lj_C_expressions_mouths_v3.jpg"],
   HAND + ATTIC + "Chest-up single of little Jade, eye level, slightly off-centre to the left, three-quarter front view turned a little to "
   "the right of frame, her face about a third of the frame height. She is tipping her head back a little and looking up and to the right, "
   "at her mother who is out of frame, hopeful and a little sly, bargaining for a story, eyebrows lifted. " + MOUTH + SKIN + LJ +
   "Reference images: image 1 is little Jade's accepted face sheet (her face and eye size); image 2 is little Jade in the painting hand "
   "(thin line, pale wash); image 3 is her expression sheet: use the 'bargaining, hopeful and sly' face (top row, second) with the closed "
   "hum mouth." + END),
 "mama_sing": (["refs/mama_heads_v3.jpg", "refs/mama_face_v3.jpg", "mama/mama_C_expressions_mouths_v3.jpg"],
   HAND + ATTIC + "Chest-up single of Mama, eye level, slightly off-centre to the right, three-quarter front view, her face about a third of "
   "the frame height. A storyteller's relish: eyebrows up, eyes bright, looking down and to the left at a child out of frame, the top edge "
   "of an open book just visible at the very bottom. " + MOUTH + SKIN + MAMA +
   "Reference images: image 1 is Mama's accepted face sheet; image 2 is Mama's face, large; image 3 is her expression sheet: use the "
   "'storyteller's relish' face (top row, first) with the closed hum mouth." + END),
 "dau_sing": (["refs/daughter_heads_v3.jpg", "refs/daughter_heads_v3_hand.jpg", "daughter/daughter_C_expressions_mouths_v3.jpg"],
   HAND + BED + "Chest-up single of the daughter, eye level, slightly off-centre, front view turned a little to the left, her face about a "
   "third of the frame height. She is about to rap with total self-belief: chin up, eyebrows set, eyes straight at us, one small hand "
   "raised beside her shoulder with the fingers spread, well clear of her face. " + MOUTH + SKIN + DAU +
   "Reference images: image 1 is the daughter's accepted face sheet (her face and eye size); image 2 is the daughter in the painting hand "
   "(thin line, pale wash); image 3 is her expression sheet: use the 'rapping with self-belief' face (top row, first) with the closed hum "
   "mouth." + END),
 "jade_sing": (["refs/jade_heads_v3.jpg", "refs/jade_face_v3.jpg", "jade/jade_C_expressions_mouths_v3.jpg"],
   HAND + BED + "Chest-up single of Jade, eye level, slightly off-centre to the left, three-quarter front view, her face about a third of the "
   "frame height. She looks down and to the right at her child out of frame, warm, a dare in her raised eyebrows. " + MOUTH + SKIN + JADE +
   "Reference images: image 1 is Jade's accepted face sheet; image 2 is Jade's face, large; image 3 is her expression sheet: use the "
   "'a dare, eyebrows up' face (top row, second) with the closed hum mouth." + END),
}
def run(k):
    refs, prompt = JOBS[k]
    out = f"media/kf/v3/lipsync_test/{k}.jpg"
    params = {"size": "3072x1728", "quality": "high", "output_format": "jpeg", "images": [R + r for r in refs]}
    open(out[:-4] + ".txt", "w").write("model: openai/gpt-image-2\n" + json.dumps(params) + "\n\n" + prompt + "\n")
    try:
        return k, cf.generate("openai/gpt-image-2", dict(params, prompt=prompt), out, tag="ls3_frame")
    except Exception as e:
        return k, f"ERR {e}"
if __name__ == "__main__":
    keys = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(run, keys): print(r)

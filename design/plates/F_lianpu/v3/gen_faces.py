"""FACES v3: generate named, real 脸谱 for the album (gpt-image-2). Usage: PY design/plates/F_lianpu/v3/gen_faces.py ID [ID ...] [--take=b]
Prompts are in faces_v3.json (id -> {name, pattern}); output _cand/<ID>_<take>.png + .txt"""
import json, sys, os, concurrent.futures as cf_
sys.path.insert(0, 'tools/gen')
import cf
D = 'design/plates/F_lianpu/v3'
SPEC = json.load(open(f'{D}/faces_v3.json'))
STYLE = ("One single Peking-opera painted face (lianpu) design, strictly frontal and symmetrical unless stated, hand-painted on a plain "
         "sheet of aged cream xuan album paper, in the manner of a leaf from a late-Qing court album of opera face patterns. "
         "Surface: opaque mineral pigments and gouache brushed on by hand: visible brush strokes that follow the forms, uneven "
         "pigment loading with lighter and darker passages inside every colour field, pigment pooled darker along the edges "
         "of the fields, small dry-brush gaps and rubbed spots where the paper shows through, hand-drawn ink outlines of "
         "varying thickness that wobble slightly; matte, a little worn with age. It must look painted with a brush, never "
         "printed: no vector-flat fills, no airbrush gradients, no gloss, no 3D shading, no photographic face. "
         "Only the face mask seen straight on, from a plain black hairline cap at the top down to the chin, with two small "
         "plain ears; no hat, no headdress, no beard, no neck, no costume. Eyes open, looking straight ahead. The face is "
         "centred and fills about two thirds of the sheet height; everything around it is bare paper. No text, no labels, "
         "no written characters anywhere, no seal, no signature, no border, no frame. Flat even scan, no shadow, no vignette. ")
REF = ("Use the reference image ONLY for the size and position of the head on the sheet, the black hairline cap, the ears and "
       "the paper; repaint the pattern, colours and brushwork entirely as described. ")

def one(fid, take):
    s = SPEC[fid]
    prompt = STYLE + REF + f"The design is the traditional Peking-opera face of {s['name']}. Pattern, exactly: {s['pattern']}"
    out = f'{D}/_cand/{fid}_{take}.png'
    inp = {"prompt": prompt, "size": "1536x1536", "quality": "high", "output_format": "png",
           "images": ["file:design/plates/F_lianpu/faces/F01.png"]}
    if s.get('ref'):                                    # public-domain Qing album crop (refs/lianpu_v3/SOURCES.txt)
        inp["images"].append("file:" + s['ref'])
        inp["prompt"] += (" The SECOND reference image is a detail of a Qing-dynasty album painting of this same character: "
                          "follow its face pattern (shapes of brows, eyes and marks), but ignore its hat, beard, costume and angle; "
                          "paint the face frontal, without hat or beard.")
    try:
        cf.generate("openai/gpt-image-2", inp, out, tag=f'lianpu_v3_{fid}_{take}')
        open(out[:-4] + '.txt', 'w').write("model: openai/gpt-image-2 1536 high, ref faces/F01.png (outline only)\n\nPROMPT:\n" + prompt + "\n")
        return fid, 'ok'
    except Exception as e:
        return fid, 'FAIL ' + str(e)[:300]

if __name__ == '__main__':
    take = 'a'
    ids = []
    for a in sys.argv[1:]:
        if a.startswith('--take='): take = a.split('=')[1]
        else: ids.append(a)
    with cf_.ThreadPoolExecutor(4) as ex:
        for r in ex.map(lambda i: one(i, take), ids):
            print(r, flush=True)

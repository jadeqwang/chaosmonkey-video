#!/usr/bin/env python3
"""Set check (SETS v4): does a keyframe / video frame keep the fixed set where the 3D layout put it?

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    $PY tools/review/set_check.py --set attic88 --shot G4 --image media/kf/v4/G4_a.jpg            # a keyframe
    $PY tools/review/set_check.py --set attic88 --shot G4 --video media/comp/G4.mp4 [--at first|last|<sec>]
    $PY tools/review/set_check.py ... --out work/review/set_check/G4.jpg        (default: work/review/set_check/<SHOT>_<stem>.jpg)
    $PY tools/review/set_check.py --print-prompt                                 # the vision-pass instructions

What it writes, next to the sheet:
  <out>.jpg   the sheet: candidate | candidate with the guide's lines over it (yellow) / label render | candidate with
              the expected object boxes; then one tile per fixed object: expected crop of the candidate beside the same
              crop of the label render. This sheet is what the vision pass reads.
  <out>.json  per-object table: expected box (px of the candidate), and the numeric hints: edge_support (fraction of the
              guide's edges inside the box that the candidate also has, 0..1) and best_shift_px (where that object's edge
              pattern matches best within +-12 % of the width). verdict fields are null until the vision pass fills them.
The numeric hints only flag; the verdict (present / moved / missing per object, plus invented extras) comes from the
vision pass: a Sonnet/Haiku subagent reads the sheet with --print-prompt's instructions and writes the verdict JSON,
then  `set_check.py --merge <out>.json <verdict.json>`  stores it and prints PASS / FAIL.
A shot FAILS if any object marked `key` is missing or moved, or anything big is invented. Figures are not judged here
(only their place: the people must stand where the guide has them).
"""
import argparse, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = os.environ.get("TMPDIR", os.path.join(ROOT, "work", "tmp"))
SKIP = {'floorboards', 'floor (wood)', 'sloped ceiling (roof boards)', 'rafters', 'purlin', 'collar ties', 'ridge beam', 'back wall', 'left wall', 'front wall',
        'ceiling', 'skirting', 'right gable wall', 'left gable wall', 'night outside', 'highway', 'tree line', 'night sky (dusk blue)', 'cabin floor', 'headliner (roof)',
        'door panels', 'roof rail', 'right wall (door)', 'door frame', 'lane markings', 'guard rail', 'median barrier', 'stair landing', 'stairs down', 'hallway (lit)', 'sign bracket', 'stairwell bulb'}
KEY = {'window', 'neon blade sign (perpendicular to the wall)', 'stair door', 'hook rail', 'sleeping mat (little Jade)', 'sleeping mat (Mama)', 'pillow (little Jade)', 'pillow (Mama)',
       'stack of textbooks', 'textbooks (fallen, scattered)', 'stack of textbooks (toppling)', 'small TV (off) on a crate', 'headboard (wood)', 'bed (wooden frame)', 'pillow',
       'bunny (stuffed toy)', 'nightstand', 'window blind (slats)', 'door (open)', 'rug (fluffy)', 'child car seat (hers, rear right)', 'EMPTY child car seat (rear left)',
       'passenger seat', "driver's seat", 'rear-view mirror', 'flashlight (on)', 'flashlight (off)', 'storybook (open)', 'storybook (closed)', 'apron (on the hook)', 'towel (on the hook)'}
PROMPT = """You are checking one frame of an animated film against the 3D layout of its set. Open the sheet image.
Top-left: the CANDIDATE frame. Top-right: the candidate with the layout's lines drawn over it in yellow. Middle-left: the
layout's LABEL render (grey 3D blockout, every object named). Middle-right: the candidate with the expected box of every
fixed object (numbered). Below: one tile per object: left half = the candidate cropped at the expected box, right half =
the same crop of the label render. People in the layout are grey mannequins; in the candidate they are painted characters.
For EACH numbered object decide:
  present  - the same object is in the candidate at about the expected place (its box overlaps the expected box by
             at least half, same rough size, same side of frame); style, colour and small shifts do not matter
  moved    - the object is in the candidate but clearly elsewhere (other side of frame, other wall, other side of the
             bed/mat, much bigger/smaller) - say where
  missing  - not in the candidate at all (or hidden where the layout shows it unobstructed)
  n/a      - the object is covered by a person in the candidate exactly where the layout also has a person, or it is
             too small to judge
Then list INVENTED objects: anything sizeable in the candidate that the layout does not have (a lamp, a second window,
a shelf, an extra pillow or stack, furniture on the wrong wall). Also say in one line whether the people stand where the
mannequins stand (same side of frame, same rough size).
Answer ONLY with JSON: {"objects": {"<n>": {"verdict": "present|moved|missing|n/a", "note": "..."}, ...},
 "invented": ["..."], "people_placement": "ok|wrong: ...", "camera": "same|similar|different: ..."}"""


def frame_of(video, at):
    os.makedirs(TMP, exist_ok=True); out = os.path.join(TMP, f"setcheck_{os.getpid()}.png")
    if at == "last": args = ["-sseof", "-0.08"]
    elif at == "first": args = ["-ss", "0"]
    else: args = ["-ss", str(at)]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args, "-i", video, "-frames:v", "1", out], check=True)
    return out


def edges(img):
    g = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY); g = cv2.GaussianBlur(g, (5, 5), 0)
    v = np.median(g); return cv2.Canny(g, int(max(10, 0.5 * v)), int(min(255, 1.3 * v + 20)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--set"); ap.add_argument("--shot"); ap.add_argument("--sidecar")
    ap.add_argument("--image"); ap.add_argument("--video"); ap.add_argument("--at", default="first"); ap.add_argument("--out")
    ap.add_argument("--print-prompt", action="store_true"); ap.add_argument("--merge", nargs=2, metavar=("CHECK_JSON", "VERDICT_JSON"))
    ap.add_argument("--max-tiles", type=int, default=12)
    a = ap.parse_args()
    if a.print_prompt: print(PROMPT); return
    if a.merge: return merge(*a.merge)
    sc_path = a.sidecar or os.path.join(ROOT, "media/layout", a.set, f"v4_{a.shot}.json")
    sc = json.load(open(sc_path)); base = sc_path[:-5]
    src = a.image or frame_of(a.video, a.at)
    cand = Image.open(src).convert("RGB"); W, H = cand.size; sx, sy = W / sc["w"], H / sc["h"]
    lab = Image.open(base + "_label.png").convert("RGB").resize((W, H), Image.LANCZOS)
    line = Image.open(base + "_line.png").convert("L").resize((W, H), Image.LANCZOS)
    stem = os.path.splitext(os.path.basename(a.image or a.video))[0] + ("" if a.image else f"_{a.at}")
    out = a.out or os.path.join(ROOT, "work/review/set_check", f"{sc['shot'][3:]}_{stem}.jpg"); os.makedirs(os.path.dirname(out), exist_ok=True)
    # objects to judge
    objs = []
    for o in sc.get("objects", []):
        if o.get("figure") or o["label"] in SKIP or o["frame_fraction"] < 0.0015: continue
        x0, y0, x1, y1 = o["bbox_px"]; objs.append({"label": o["label"], "key": o["label"] in KEY, "frame_fraction": o["frame_fraction"],
            "box": [int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy)]})
    people = [{"label": f"person: {w}", "box": None, "head_px": [int(h['px'][0] * sx), int(h['px'][1] * sy)]} for w, h in sc.get("heads", {}).items() if h.get("in_frame")]
    # numeric hints: edge support + best shift
    ec, el = edges(cand), (np.asarray(line) < 128).astype(np.uint8) * 255
    dt = cv2.distanceTransform(255 - ec, cv2.DIST_L2, 3); r = max(3, W * 0.012)
    for o in objs:
        x0, y0, x1, y1 = o["box"]; m = el[y0:y1, x0:x1] > 0; n = int(m.sum())
        o["edge_support"] = round(float((dt[y0:y1, x0:x1][m] <= r).mean()), 3) if n > 20 else None
        pad = int(W * 0.12); X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
        tpl = cv2.GaussianBlur(el[y0:y1, x0:x1].astype(np.float32), (0, 0), 2); reg = cv2.GaussianBlur(ec[Y0:Y1, X0:X1].astype(np.float32), (0, 0), 2)
        if n > 20 and tpl.shape[0] < reg.shape[0] and tpl.shape[1] < reg.shape[1] and tpl.std() > 0:
            res = cv2.matchTemplate(reg, tpl, cv2.TM_CCOEFF_NORMED); _, mv, _, ml = cv2.minMaxLoc(res)
            o["best_shift_px"] = [ml[0] + X0 - x0, ml[1] + Y0 - y0]; o["best_match"] = round(float(mv), 3)
        o["hint"] = ("low edge support" if (o["edge_support"] is not None and o["edge_support"] < 0.25) else "") + \
                    (" best match shifted" if o.get("best_shift_px") and np.hypot(*o["best_shift_px"]) > W * 0.06 and o.get("best_match", 0) > 0.25 else "")
        o.update(verdict=None, note=None)
    # sheet
    ov = cand.copy(); yl = Image.new("RGB", (W, H), (255, 225, 0)); msk = Image.fromarray(cv2.dilate(el, np.ones((2, 2), np.uint8)))
    ov.paste(yl, (0, 0), msk)
    bx = cand.copy(); d = ImageDraw.Draw(bx)
    try: F = ImageFont.truetype("DejaVuSans-Bold.ttf", max(12, W // 70)); Fs = ImageFont.truetype("DejaVuSans.ttf", max(11, W // 90))
    except Exception: F = Fs = ImageFont.load_default()
    pal = [(255, 80, 60), (60, 200, 255), (120, 255, 90), (255, 200, 40), (230, 90, 255), (255, 140, 0), (0, 255, 200), (255, 255, 255)]
    for i, o in enumerate(objs):
        c = pal[i % len(pal)]; d.rectangle(o["box"], outline=c, width=max(2, W // 400)); d.text((o["box"][0] + 4, o["box"][1] + 2), f"{i + 1} {o['label']}", fill=c, font=Fs, stroke_width=2, stroke_fill=(0, 0, 0))
    for p in people: d.ellipse([p["head_px"][0] - 8, p["head_px"][1] - 8, p["head_px"][0] + 8, p["head_px"][1] + 8], outline=(255, 0, 255), width=3); d.text((p["head_px"][0] + 10, p["head_px"][1] - 8), p["label"], fill=(255, 0, 255), font=Fs, stroke_width=2, stroke_fill=(0, 0, 0))
    tiles = []; TW = W // 2
    for i, o in enumerate(sorted(objs, key=lambda o: -o["frame_fraction"])[:a.max_tiles]):
        x0, y0, x1, y1 = o["box"]; mx, my = int((x1 - x0) * 0.25) + 8, int((y1 - y0) * 0.25) + 8
        bb = (max(0, x0 - mx), max(0, y0 - my), min(W, x1 + mx), min(H, y1 + my)); th = int(TW / 2 * (bb[3] - bb[1]) / max(1, bb[2] - bb[0])); th = max(60, min(th, TW // 3))
        t = Image.new("RGB", (TW, th + 22), (30, 30, 30)); t.paste(cand.crop(bb).resize((TW // 2 - 2, th)), (0, 22)); t.paste(lab.crop(bb).resize((TW // 2 - 2, th)), (TW // 2 + 2, 22))
        ImageDraw.Draw(t).text((4, 2), f"{objs.index(o) + 1} {o['label']}" + (" [key]" if o["key"] else "") + (f"   hint: {o['hint']}" if o['hint'] else ""), fill=(255, 255, 255), font=Fs); tiles.append(t)
    rows = [tiles[k:k + 2] for k in range(0, len(tiles), 2)]; rows = rows or [[Image.new('RGB', (TW, 10))]]; th_tot = sum(max(t.height for t in r) for r in rows)
    sheet = Image.new("RGB", (W * 2, H * 2 + 40 + th_tot), (20, 20, 20)); sd = ImageDraw.Draw(sheet)
    sd.text((8, 6), f"set check  {sc['shot']}  candidate: {os.path.relpath(src, ROOT) if src.startswith(ROOT) else src}   ({sc['set']})", fill=(255, 255, 255), font=F)
    for im, (px, py) in [(cand, (0, 40)), (ov, (W, 40)), (lab, (0, 40 + H)), (bx, (W, 40 + H))]: sheet.paste(im, (px, py))
    y = 40 + 2 * H
    for r in rows:
        for j, t in enumerate(r): sheet.paste(t, (j * W, y))
        y += max(t.height for t in r)
    if sheet.width > 2400: sheet = sheet.resize((2400, int(sheet.height * 2400 / sheet.width)), Image.LANCZOS)
    sheet.save(out, quality=88)
    rep = {"shot": sc["shot"], "set": sc["set"], "candidate": src, "sheet": out, "sidecar": sc_path, "size": [W, H], "objects": objs, "people": people, "verdict": None}
    json.dump(rep, open(out[:-4] + ".json", "w"), indent=1, ensure_ascii=False)
    flagged = [f"{i + 1} {o['label']} ({o['hint'].strip()})" for i, o in enumerate(objs) if o["hint"]]
    print(f"{out}\n  {len(objs)} objects ({sum(o['key'] for o in objs)} key); numeric flags: {', '.join(flagged) or 'none'}")


def merge(check, verdict):
    rep = json.load(open(check)); v = json.load(open(verdict)); bad = []
    for k, e in v.get("objects", {}).items():
        i = int(k) - 1
        if 0 <= i < len(rep["objects"]):
            o = rep["objects"][i]; o["verdict"], o["note"] = e.get("verdict"), e.get("note")
            if o["key"] and o["verdict"] in ("moved", "missing"): bad.append(f"{o['label']}: {o['verdict']} ({o['note']})")
    rep["invented"] = v.get("invented", []); rep["people_placement"] = v.get("people_placement"); rep["camera"] = v.get("camera")
    big_inv = [x for x in rep["invented"] if x]
    ok = not bad and not big_inv and not str(rep["people_placement"] or "ok").startswith("wrong")
    rep["verdict"] = "PASS" if ok else "FAIL"; rep["fail_reasons"] = bad + [f"invented: {x}" for x in big_inv] + ([f"people: {rep['people_placement']}"] if str(rep["people_placement"] or "").startswith("wrong") else [])
    json.dump(rep, open(check, "w"), indent=1, ensure_ascii=False)
    print(rep["verdict"], rep["shot"], "; ".join(rep["fail_reasons"]))


if __name__ == "__main__":
    main()

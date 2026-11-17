#!/usr/bin/env python3
"""Fill docs/picks.json with still picks for every shot that has a keyframe and no real pick yet (the animatic).

    .venv/bin/python tools/edit/animatic_picks.py

A shot gets media/kf/<ID>_pick_1080.jpg with a slow 4 % push-in, marked "_auto": "animatic". Shots rendered by
tools/sky (work/sky/shots/<ID>/f%04d.png, cut-in frame f0013) get a frames pick. Picks without "_auto" are
never touched, so real video picks survive re-runs. Shots sharing a frame fall back to their twin's keyframe.
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "docs", "picks.json")
TWIN = {"F8": "F6", "G14": "F5", "I1": "E1", "E6": "C2", "G2": "E4", "G3": "D2", "K1": "A1", "F7": "F2", "J11": "F8"}
SKY = ["C7", "D4", "G4", "G13", "H2"]
d = json.load(open(P)); picks = d["picks"]
shots = json.load(open(os.path.join(ROOT, "docs", "shots.json")))
shots = shots["shots"] if isinstance(shots, dict) else shots
n = 0
for s in shots:
    i = s["id"]; cur = picks.get(i, {})
    if cur.get("kind") and not cur.get("_auto"):
        continue
    new = None
    if i in SKY and os.path.isdir(os.path.join(ROOT, "work/sky/shots", i)):
        new = {"kind": "frames", "dir": f"work/sky/shots/{i}", "pattern": "f*.png", "start": 12, "phase_grade": False}
    else:
        for c in (i, TWIN.get(i)):
            f = f"media/kf/{c}_pick_1080.jpg"
            if c and os.path.exists(os.path.join(ROOT, f)):
                new = {"kind": "still", "src": f,
                       "move": {"from": {"zoom": 1.0, "x": 0.5, "y": 0.5}, "to": {"zoom": 1.04, "x": 0.5, "y": 0.5}, "ease": "linear"}}
                break
    if new:
        new["_auto"] = "animatic"
        for k in ("overlay",):
            if k in cur: new[k] = cur[k]
        picks[i] = new; n += 1
json.dump(d, open(P, "w"), indent=1)
print(n, "auto picks;", sum(1 for s in shots if not picks.get(s["id"], {}).get("kind")), "shots still slates")

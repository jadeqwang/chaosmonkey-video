#!/usr/bin/env python3
"""Merge the fragments docs/picks_<group>.json into docs/picks.json.

    .venv/bin/python tools/edit/merge_picks.py

Order: the older producers' fragments (alphabetical), then the round-4 producers' fragments (picks_r4_battle,
picks_r4_land, picks_r4_totality: they supersede the older takes of the shots they re-stage), then picks_retake.json,
picks_finish.json (the finishing editor's retimes and replacements), picks_comp.json (composites replace the plain
take), then picks_r4_finish.json (round-4 finishing: B1, re-takes, re-crops), then picks_r5.json and picks_r5_land.json
(fix round 5), then picks_r6.json and picks_r6_E1.json (round 6; both in docs/FIX_R5.md), then picks_grade.json, which is
different: it only lays per-shot keys ("grade", "phase_grade", "grain", "move", "crop") over whatever pick the
shot already has. A fragment's pick replaces an animatic still ("_auto") or an earlier fragment's pick and keeps
any overlay already on the shot. Picks set by hand in docs/picks.json (no "_auto", no "_from") are left alone.
"""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "docs", "picks.json")
R4 = ["picks_r4_battle.json", "picks_r4_land.json", "picks_r4_totality.json"]   # round 4: after the older producers
LAST = R4 + ["picks_retake.json", "picks_finish.json", "picks_comp.json", "picks_r4_finish.json",
              "picks_r5.json", "picks_r5_land.json",
              "picks_r6.json", "picks_r6_E1.json"]   # in this order (r5, r6: docs/FIX_R5.md)
OVERLAY_ONLY = "picks_grade.json"
d = json.load(open(P)); picks = d["picks"]
files = [f for f in sorted(glob.glob(os.path.join(ROOT, "docs", "picks_*.json")))
         if os.path.basename(f) not in LAST + [OVERLAY_ONLY]]
files += [os.path.join(ROOT, "docs", n) for n in LAST if os.path.exists(os.path.join(ROOT, "docs", n))]
for f in files:
    g = os.path.basename(f)[6:-5]; n = 0
    for k, v in (json.load(open(f)).get("picks") or {}).items():
        if k.startswith("_") or not v.get("kind"):
            continue
        cur = picks.get(k, {})
        if cur.get("kind") and not cur.get("_auto") and "_from" not in cur:
            print("kept hand pick", k); continue
        new = dict(v); new["_from"] = g
        if "overlay" in cur and "overlay" not in new:
            new["overlay"] = cur["overlay"]
        picks[k] = new; n += 1
    print(g, n, "picks")
f = os.path.join(ROOT, "docs", OVERLAY_ONLY)
if os.path.exists(f):
    n = 0
    for k, v in (json.load(open(f)).get("picks") or {}).items():
        if k in picks and not k.startswith("_"):
            for kk in ("grade", "phase_grade", "grain", "move", "crop"):
                if kk in v:
                    picks[k][kk] = v[kk]
            n += 1
    print("grade overlay on", n, "shots")
json.dump(d, open(P, "w"), indent=1)
print(sum(1 for v in picks.values() if v.get("kind") in ("video", "frames")), "moving picks in docs/picks.json")

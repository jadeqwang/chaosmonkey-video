#!/usr/bin/env python3
"""analysis/timing.json -> analysis/timing_v4.json for the edited song (G5 "Yes" one beat late; tools/audio/yes_shift_v4.py).
Only the word, its line, the 'yes'/'silence' sections, the near-silence/chop events and the sync points in 148.55-149.72 change;
beats, downbeats, hits and every other word are the same song and are copied. Every changed entry carries "v4": what changed."""
import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)  # noqa
E = json.load(open(P("work", "sound_v4", "edit.json")))
D = E["shift_s"]
NEW_SIL = (148.645, 149.195)          # edited song, mono 5 ms RMS < -50 dBFS (max -50.1): "less" tail -> moved word
ATTACK = {"old": 148.874, "new": 149.306}   # vocal stem, first 10 ms RMS within 6 dB of the word's peak

t = json.load(open(P("analysis", "timing.json")))
v4 = copy.deepcopy(t)
v4["meta"]["file"] = E["song_out"]
v4["meta"]["v4_edit"] = (f"Copy of analysis/timing.json for the v4 song: the child's 'Yes' moved +{D:.3f} s (one beat, {E['shift_samples']} samples) "
                         f"by tools/audio/yes_shift_v4.py; samples outside {E['changed_span_s'][0]:.3f}-{E['changed_span_s'][1]:.3f} s identical "
                         f"to the original. Word attack (-6 dB of peak): {ATTACK['old']} -> {ATTACK['new']} (beat 4 of bar 86, 149.297, +9 ms).")
for ln in v4["lines"]:
    if ln["text"] == "Yes":
        for w in ln["words"]:
            w["start"] = round(w["start"] + D, 3)
            w["end"] = round(w["end"] + D, 3)
            w["attack"] = ATTACK["new"]
            w["v4"] = f"moved +{D:.3f} s (was {w['start'] - D:.3f}-{w['end'] - D:.3f})"
        ln["start"], ln["end"] = round(ln["start"] + D, 3), round(ln["end"] + D, 3)
        ln["v4"] = f"moved +{D:.3f} s"
for s in v4["sections"]:
    if s["name"] == "yes":
        s["start"], s["end"] = round(148.72 + D, 3), 149.72
        s["dur"] = round(s["end"] - s["start"], 3)
        s["description"] = ("Child 'Yes' (149.152-149.702; attack 149.306 on beat 4), whispered, in the place of the old near-silence; its 's' "
                            "runs under the bridge's swell (from ~149.59) and the song's own cut of the word lands at 149.717, under the crash.")
        s["v4"] = "was 148.550-149.285"
    if s["name"] == "silence":
        s["start"], s["end"] = 148.55, round(148.72 + D, 3)
        s["dur"] = round(s["end"] - s["start"], 3)
        s["description"] = ("The pause before 'Yes': backing only (riser residue + room), mix < -50 dBFS 148.645-149.195 (0.55 s). "
                            "The old 0.24 s hole 149.285-149.525 is now filled by the word.")
        s["v4"] = "was 149.285-149.720 (the near-silence after the word); now the pause before it"
v4["sections"].sort(key=lambda s: s["start"])
he = v4["hit_events"]
he["silences"] = [x for x in he["silences"] if not (148.6 < x["start"] < 149.6)] + \
    [{"start": NEW_SIL[0], "end": NEW_SIL[1], "dur": round(NEW_SIL[1] - NEW_SIL[0], 3), "max_db": -50.1, "confidence": "high",
      "v4": "replaces 148.655-148.695 and 149.285-149.525 (the latter filled by the moved word)"}]
he["silences"].sort(key=lambda x: x["start"])
he["chops"] = [dict(x, v4_removed="149.295-149.390 hole is filled by the moved word in the v4 song") if abs(x["start"] - 149.295) < 0.01 else x
               for x in he["chops"]]
he["chops"] = [x for x in he["chops"] if "v4_removed" not in x]
he["chop_clusters"] = [x for x in he["chop_clusters"] if abs(x["start"] - 149.295) > 0.01]
for sp in v4["sync_points"]:
    if sp["name"] == '"Yes"':
        sp["t"] = round(sp["t"] + D, 3)
        sp["frame24"] = -(-int(round(sp["t"] * 1000)) * 24 // 1000)
        sp["attack"] = ATTACK["new"]
        sp["v4"] = f"moved +{D:.3f} s"
    elif sp["name"] == "Near-silence start":
        sp.update(t=NEW_SIL[0], frame24=-(-int(NEW_SIL[0] * 1000) * 24 // 1000), v4="the pause is now before the word (was 149.285)")
    elif sp["name"] == "Near-silence end":
        sp.update(t=NEW_SIL[1], frame24=-(-int(NEW_SIL[1] * 1000) * 24 // 1000), v4="the moved word starts here (was 149.525)")
v4["sync_points"].sort(key=lambda s: s["t"])
v4["energy"]["v4_note"] = "energy curves are those of the original song; they differ only in 148.62-149.93 (the moved word)."
json.dump(v4, open(P("analysis", "timing_v4.json"), "w"), indent=1, ensure_ascii=False)
print("ok")

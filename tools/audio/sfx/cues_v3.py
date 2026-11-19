#!/usr/bin/env python3
"""docs/sound_cues.json (v2, approved) -> docs/sound_cues_v3.json for mix_v3b (preview_v4 picture; edited song, 'Yes' +1 beat).
Every change is listed here with its reason; the cue table in docs/SOUND.md is generated from CHANGES. Run, then build:
  CM_SONG=... CM_VOCALS=work/stems/vocals_v4.wav CM_TIMING=analysis/timing_v4.json CM_CUES=docs/sound_cues_v3.json \
    $PY tools/audio/sfx/build_v2.py --tag v3b
"""
import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = lambda *a: os.path.join(ROOT, *a)  # noqa
V2 = {"band": 6, "floor": 3, "cap": -5, "eq": True, "duck": 9}
spec = json.load(open(P("docs", "sound_cues.json")))
spec["about"] = "v3 (mix_v3b): the v2 sheet re-timed to the preview_v4 picture + new-action cues; built by tools/audio/sfx/cues_v3.py from docs/sound_cues.json. " + spec["about"]
cues = {c["id"]: c for c in spec["cues"]}
order = [c["id"] for c in spec["cues"]]
CHANGES = []   # (shot, cue, old, new, what)


def moved(cid, old, new, what, **kv):
    cues[cid].update(kv)
    cues[cid]["v3"] = what
    CHANGES.append((cues[cid]["shot"], cid, old, new, what))


def add(c, what, when):
    c.setdefault("v2", dict(V2))
    c.setdefault("level", {"margin": 12, "cap": -16})
    c.setdefault("pan", 0.0)
    c["new"] = True
    c["picture_dependent"] = True
    c["v3"] = what
    cues[c["id"]] = c
    order.append(c["id"])
    CHANGES.append((c["shot"], c["id"], "-", when, what))


def ev(at, src_at=0.0, pre=0.03, dur=None, gain=0.0, pan=None, rate=None):
    e = {"at": at, "src_at": src_at, "pre": pre}
    if dur is not None:
        e["dur"] = dur
    if gain:
        e["gain"] = gain
    if pan is not None:
        e["pan"] = pan
    if rate:
        e["rate"] = rate
    return e


# ------------------------------------------------------------------ re-timed (existing cues)
moved("breath", "52.55-54.45", "53.10-54.55", "Mama's breath now leaves her lips at 53.22 (C5a); the breath rises 0.18 s so it is there on 53.22 and runs into the wind",
      start="t:53.10", end="t:54.55")
moved("sleeve_wind", "54.60-57.20", "54.50-56.70", "the wind flow enters C5b at the left edge 54.505 and its ribbons cross the egg to ~56.4 (BOOK flow contract)",
      start="t:54.50", end="t:56.70", fade_out=0.5)
c = cues["abacus_f4b"]
old_ev = c["events"]
c["events"] = [ev("beat:113.247", 2.40, 0.01, 0.14, pan=-0.3), ev("beat:113.688", 3.10, 0.01, 0.14, pan=0.3),
               ev("beat:114.133", 4.50, 0.01, 0.14, pan=-0.3)] + old_ev
c["intent"] = "F4 beat-wave: the lantern flares on every beat 113.247 .. 115.883 (SWARM: these replace the abacus clicks one for one, plus three earlier beats): a dry 2-3 click flick per flare, alternating sides."
moved("abacus_f4b", "114.567 115.002 115.445 115.882", "113.247 113.688 114.133 + the same four", "F4 lantern flares on the beat wave (= the old abacus clicks), three earlier beats added")
moved("hair_air", "172.90-177.10 (hair_air)", "172.76-174.40 (gale)", "H6 round 3: the gale takes the girl's hair and a strand works loose in the first 36 f (172.76-174.25); the growth and the somersault get their own cues",
      src="gale", start="t:172.76", end="t:174.40", fade_in=0.15, fade_out=0.4, proc={"lp": 2500})
cues["hair_air"]["intent"] = "H6: the gale takes her hair; one strand works loose and tumbles (gust R -> L), gone as the strand's root swells into ink."
moved("ledger_pages", "218.75 219.80 220.23", "218.22 219.40 220.30 220.92",
      "K4 no hand: a leaf lands 218.22 ('page'); leaf 2 lifts 219.40, hangs and falls back 220.30; goes over and lands 220.92 ('looked')",
      events=[ev("t:218.22", 1.185, 0.25, 0.35, gain=-3, pan=-0.2), ev("t:219.40", 1.54, 0.10, 0.30, gain=-9, pan=0.1),
              ev("t:220.30", 6.135, 0.10, 0.30, gain=-7, pan=0.1), ev("t:220.92", 2.07, 0.25, 0.40, pan=0.25)])
cues["ledger_pages"]["intent"] = "K4: the ledger's pages turn in a draught, no hand: land, lift, fall back, go over, land."
moved("fingertip_j1", "189.62", "189.52", "J1: the fingertip dips at ~189.50-189.55; the character lights from 189.62", events=[dict(cues["fingertip_j1"]["events"][0], at="t:189.52")])
moved("brush_strike", "216.060", "216.165", "K3: the bloom on 'single breath' is at ~216.2: nearest hit 216.165",
      events=[dict(cues["brush_strike"]["events"][0], at="hit:216.165")])
for cid in ("room_yes", "neon_hum_yes"):
    cues[cid]["end"] = "t:149.285"
    cues[cid]["v3"] = "end anchor silence:149.285 no longer exists in timing_v4 (the moved 'Yes' fills it): same time, raw"
    CHANGES.append(("G5", cid, "149.285 (silence anchor)", "149.285 (t:)", "same end; the 'Yes' now starts 149.152, the bed is 40 dB under it"))

# ------------------------------------------------------------------ new cues
add({"id": "dolly_b3", "shot": "B3", "kind": "bed", "src": "dolly_air", "start": "t:26.145", "end": "t:29.29", "fade_in": 0.3, "fade_out": 0.5,
     "proc": {"lp": 3000, "room": "valley"}, "duck": True, "v2": {**V2, "cap": -14},
     "intent": "B3 true 3D dolly into the page: air, and three soft passes as pines and rocks go by the lens (PROV: WORLD r2)."}, "B3 3D dolly: page air + pines passing the lens", "26.145-29.29")
add({"id": "ember_d4", "shot": "D4", "kind": "events", "src": "ember", "events": [ev("word:15:通", 0.0, 0.01, 0.8)],
     "proc": {"hp": 80, "lp": 9000, "room": "valley"}, "v2": {**V2, "cap": -10},
     "intent": "D-flight: 通 on the carved panel catches like an ember (68.09, the word 通)."}, "D4 ember on 通", "68.09")
add({"id": "arcs_d5", "shot": "D5", "kind": "events", "src": "arc",
     "events": [ev(f"beat:{t}", 0.5 * j + 0.22, 0.22, 0.12, gain=-2 * (j % 2), pan=(0.4 if j % 2 else -0.4)) for j, t in enumerate((70.594, 71.029, 71.471, 71.925, 72.356))],
     "proc": {"hp": 700, "lp": 11000, "room": "valley"}, "v2": {**V2, "cap": -8},
     "intent": "D-flight: the frontier's light arcs, one thin high whoosh per beat, peaking on the beat."}, "D5 frontier light arcs on the beats", "70.594 71.029 71.471 71.925 72.356")
add({"id": "cloth_e3", "shot": "E3", "kind": "events", "src": "cloth_swish", "events": [ev("t:96.00", 0.30, 0.20, 0.30, gain=-6)],
     "proc": {"hp": 200, "lp": 6000, "room": "attic"}, "v2": {**V2, "cap": -20},
     "intent": "E3: the held pose; only a small cloth move ~96.0, in the gap between 'few' and 'but'. (The wuxia cast whoosh is not needed.)"}, "E3 small cloth move (no cast whoosh)", "96.00")
add({"id": "flips_f2", "shot": "F2", "kind": "events", "src": "flip",
     "events": [ev(a, (0.25 * j) % 1.0, 0.01, 0.2, gain=-2 * (j % 2), pan=0.35) for j, a in enumerate(("t:108.84", "beat:109.30", "beat:109.74", "beat:110.175", "t:110.38", "t:110.80"))],
     "proc": {"hp": 400, "lp": 9000, "room": "car"}, "v2": {**V2, "cap": -8},
     "intent": "F2: the shadow puppet on her side window re-poses hard on each beat / syllable cluster (72 transformations): a leather-paper flick per re-pose."},
    "F2 shadow-puppet re-poses", "108.84 109.30 109.74 110.175 110.38 110.80")
add({"id": "spawn_air_f4", "shot": "F4", "kind": "bed", "src": "hair_air", "start": "t:112.76", "end": "t:114.30", "fade_in": 0.2, "fade_out": 0.4,
     "proc": {"lp": 2500, "room": "car"}, "duck": True, "v2": {**V2, "cap": -14},
     "intent": "F4 spawn: the hairs stream in on an air current."}, "F4 spawn: hairs stream in (air)", "112.76-114.30")
add({"id": "spawn_puffs_f4", "shot": "F4", "kind": "events", "src": "puff",
     "events": [ev("t:112.85", 0.02, 0.02, 0.3, gain=-2, pan=-0.4), ev("t:113.03", 0.02, 0.02, 0.3, gain=-6, pan=0.3, rate=1.15),
                ev("t:113.47", 0.02, 0.02, 0.3, gain=-5, pan=-0.2, rate=0.9), ev("t:113.90", 0.02, 0.02, 0.3, gain=-8, pan=0.4, rate=1.25)],
     "proc": {"hp": 300, "lp": 7000, "room": "car"}, "v2": {**V2, "cap": -8},
     "intent": "F4 spawn: generations pluck and blow: small puffs between the lantern flares, fainter as they multiply."}, "F4 spawn: plucking/blowing puffs", "112.85 113.03 113.47 113.90")
add({"id": "gale_f5", "shot": "F5", "kind": "bed", "src": "gale", "start": "t:117.70", "end": "t:118.40", "fade_in": 0.05, "fade_out": 0.3,
     "proc": {"lp": 3000, "room": "car"}, "duck": True, "v2": {**V2, "cap": -10},
     "intent": "F5 -> F6a: the hair gale streams back in a spiral (~117.77-118.0)."}, "F5->F6a hair gale streams back", "117.70-118.40")
add({"id": "inkpuff_f6a", "shot": "F6a", "kind": "events", "src": "puff",
     "events": [ev("t:117.958", 0.02, 0.02, 0.3, pan=-0.2, rate=0.8), ev("t:118.125", 0.02, 0.02, 0.3, gain=-4, pan=0.2, rate=0.8)],
     "proc": {"hp": 200, "lp": 5000, "room": "car"}, "v2": {**V2, "cap": -8},
     "intent": "F6a: the twin ink puff (117.958-118.292)."}, "F6a twin ink puff", "117.958 118.125")
add({"id": "seals_f6a", "shot": "F6a", "kind": "events", "src": "seal",
     "events": [ev("hit:119.157", 2.27, 0.03, 0.5, pan=-0.3), ev("beat:119.812", 2.27, 0.03, 0.5, gain=-2, pan=0.3)],
     "proc": copy.deepcopy(cues["seals_f5"]["proc"]), "v2": dict(cues["seals_f5"]["v2"]),
     "intent": "F6a: the two 真 seals pressed, left then right."}, "F6a 真 seals (left, right)", "119.157 119.812")
add({"id": "ink_g2", "shot": "G2", "kind": "events", "src": "brush_wet", "events": [ev("word:37:听", 0.0, 0.01, 0.45, gain=-2), ev("word:39:听", 0.0, 0.01, 0.45, gain=-4)],
     "proc": {"hp": 200, "lp": 7000, "room": "small"}, "v2": {**V2, "cap": -12},
     "intent": "G2: 听话 inks in, cinnabar, on each 听 (with the margin notch already there)."}, "G2 听话 inks in", "130.175 133.690")
add({"id": "strokes_h5", "shot": "H5", "kind": "bed", "src": "hair_air", "start": "t:169.25", "end": "t:172.75", "fade_in": 0.4, "fade_out": 0.5,
     "proc": {"lp": 2200, "room": "valley"}, "duck": True, "v2": {**V2, "cap": -16},
     "intent": "H5: carved strokes lift off the cliffs and stream across to assemble into the girl: one long breath of air, R -> L."}, "H5 strokes lift off and stream", "169.25-172.75")
add({"id": "grow_h6", "shot": "H6", "kind": "events", "src": "brush_wet",
     "events": [ev("beat:174.4", 0.0, 0.01, 0.45, pan=0.1), ev("beat:174.824", 0.0, 0.01, 0.45, gain=-2, pan=0.05),
                ev("hit:175.16", 0.0, 0.01, 0.45, gain=-3), ev("hit:175.595", 0.0, 0.01, 0.35, gain=-6, rate=1.2)],
     "proc": {"hp": 200, "lp": 7000, "room": "valley"}, "v2": {**V2, "cap": -10},
     "intent": "H6: the strand's root swells into wet ink and three strokes make the monkey (174.3-175.6), then the red scarf streak."}, "H6 monkey grows from the strand (3 strokes + scarf)", "174.400 174.824 175.160 175.595")
add({"id": "somersault_h6", "shot": "H6", "kind": "events", "src": "staff_whoosh", "events": [ev("hit:176.334", 0.27, 0.27, 0.2, pan=-0.6)],
     "proc": {"hp": 150, "lp": 5000, "room": "valley"}, "v2": {**V2, "cap": -12},
     "intent": "H6: he somersaults out to the left (~176.3), tail after him."}, "H6 somersault out left", "176.334")
add({"id": "pop_j2", "shot": "J2", "kind": "events", "src": "depth_pop", "events": [ev("hit:190.885", 0.0, 0.01, 0.9)],
     "proc": {"hp": 30, "lp": 9000, "room": "valley"}, "v2": {**V2, "cap": -6},
     "intent": "J2: the flat page pops into depth on the drop-2 downbeat (PROV: WORLD r2)."}, "J2 pop into depth", "190.885")
add({"id": "strike_k3", "shot": "K2b-K3", "kind": "events", "src": "brush_wet",
     "events": [ev("t:213.40", 0.0, 0.01, 0.4, gain=-4, pan=-0.1), ev("hit:213.807", 0.0, 0.01, 0.35, pan=0.05, rate=0.85)],
     "proc": {"hp": 150, "lp": 8000, "room": "small"}, "v2": {**V2, "cap": -10},
     "intent": "K2b -> K3: the brush stroke run (213.4-213.8) ends in the wet strike on 'crossed out' (213.807)."}, "K2b stroke run + K3 wet strike", "213.40 213.807")
add({"id": "draught_k4", "shot": "K4", "kind": "bed", "src": "draught", "start": "t:217.20", "end": "t:224.18", "fade_in": 1.0, "fade_out": 1.0,
     "proc": {"lp": 900, "room": "small"}, "duck": True, "v2": {**V2, "band": 10, "cap": -24},
     "intent": "K4: the draught that turns the pages, very low, under the beatless outro."}, "K4 draught (page-turning air)", "217.20-224.18")
add({"id": "stir_k4", "shot": "K4", "kind": "events", "src": "flip",
     "events": [ev("t:222.75", 0.0, 0.01, 0.15, gain=-6), ev("t:223.35", 0.5, 0.01, 0.15, gain=-9), ev("t:223.95", 0.25, 0.01, 0.15, gain=-12)],
     "proc": {"hp": 600, "lp": 8000, "room": "small"}, "v2": {**V2, "cap": -18},
     "intent": "K4: the last leaf stirs (222.75-223.95), three tiny flutters, fainter."}, "K4 last leaf stirs", "222.75 223.35 223.95")
add({"id": "unwrite_k5", "shot": "K5", "kind": "events", "src": "brush_rev",
     "events": [ev("t:224.67", 0.45, 0.45, 0.05, gain=-2), ev("t:225.37", 0.45, 0.45, 0.05, gain=-4), ev("t:226.07", 0.45, 0.45, 0.05, gain=-6)],
     "proc": {"hp": 200, "lp": 6000, "room": "small"}, "v2": {**V2, "cap": -10},
     "intent": "K5: the wet line un-writes, cell by cell (retreats 224.67 / 225.37 / 226.07): a reversed stroke ending on each retreat."}, "K5 the line un-writes", "224.67 225.37 226.07")

spec["cues"] = [cues[i] for i in order]
spec["v3_changes"] = [{"shot": s, "cue": c, "old": o, "new": n, "what": w} for s, c, o, n, w in CHANGES]
json.dump(spec, open(P("docs", "sound_cues_v3.json"), "w"), indent=1, ensure_ascii=False)
print(len(spec["cues"]), "cues;", len(CHANGES), "changes")

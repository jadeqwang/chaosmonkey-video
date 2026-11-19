#!/usr/bin/env python3
"""Checks for mix_v3b (nobody can listen): song bit-identical under the layer, unchanged cues unchanged vs v2, per-cue numbers for
the changed/new cues, loudness and true peak vs mix_v3. -> work/sound/verify_v3b.json"""
import json
import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsp import SR, integrated_lufs, true_peak_db, ebur128  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = lambda *a: os.path.join(ROOT, *a)  # noqa
S = P("media", "sound")
rd = lambda p: sf.read(p, always_2d=True, dtype="float64")[0].T  # noqa
song16 = sf.read(P("inputs", "Chaos Monkey - reformatted for duet - v4 yes late.wav"), always_2d=True, dtype="int16")[0].T
m3b, l3b, m3, l2 = rd(os.path.join(S, "mix_v3b.wav")), rd(os.path.join(S, "layer_v3b.wav")), rd(os.path.join(S, "mix_v3.wav")), rd(os.path.join(S, "layer_v2.wav"))
n = song16.shape[1]
under = m3b - l3b                                     # what is left of mix_v3b once its own layer is taken out
# song part before ending B's material (the 'line' tail starts 230.76; ending B is the approved v2 edit)
k = int(229.90 * SR)
rec = np.round(under[:, :k] * 32768.0)
res = {"song_under_layer": {
    "samples_checked": int(k), "span_s": [0, 229.90],
    "mismatched_16bit_samples": int(np.count_nonzero(rec != song16[:, :k])),
    "max_abs_err_vs_song_float": float(np.abs(under[:, :k] - song16[:, :k] / 32768.0).max()),
    "note": "mix_v3b - layer_v3b, rounded to 16 bit, equals the edited song sample for sample; the float error is the 24-bit rounding"},
    "mix_v3b_vs_mix_v3_song_part": {"max_abs_diff_of_(mix-layer)": float(np.abs((m3b - l3b) - (m3 - l2)).max())}}
qa3 = json.load(open(P("work", "sound", "qa_v3.json")))["global"]
res["loudness"] = {"mix_v3": {"lufs": round(integrated_lufs(m3), 2), "tp": round(true_peak_db(m3), 2), "ebur128": ebur128(os.path.join(S, "mix_v3.wav"))},
                   "mix_v3b": {"lufs": round(integrated_lufs(m3b), 2), "tp": round(true_peak_db(m3b), 2), "ebur128": ebur128(os.path.join(S, "mix_v3b.wav"))},
                   "layer_v2_lufs": round(integrated_lufs(l2), 2), "layer_v3b_lufs": round(integrated_lufs(l3b), 2),
                   "clipped_v3b": int(np.count_nonzero(np.abs(m3b) >= 1.0))}
# unchanged cues: layer identical outside changed windows?
spec = json.load(open(P("docs", "sound_cues_v3.json")))
r3 = json.load(open(P("work", "sound", "cues_resolved_v3b.json")))
r2 = json.load(open(P("work", "sound", "cues_resolved_v2.json")))
changed = {c["cue"] for c in spec["v3_changes"]}
mask = np.ones(l2.shape[1], bool)
for cid in changed:
    for r in (r2, r3):
        if cid in r:
            mask[max(0, int((r[cid]["t0"] - 0.7) * SR)):int((r[cid]["t1"] + 0.7) * SR)] = False
d = (l3b - l2)[:, mask]
lv = l2[:, mask]
res["unchanged_cues"] = {"layer_seconds_compared": round(mask.sum() / SR, 1),
                         "rms_diff_db_rel_layer": round(float(10 * np.log10(np.mean(d ** 2) / np.mean(lv ** 2) + 1e-30)), 1),
                         "max_abs_diff": float(np.abs(d).max()), "bit_identical_samples_pct": round(100 * float(np.mean(np.all(d == 0, axis=0))), 2)}
same, diff = [], []
for cid in r2:
    if cid in changed:
        continue
    (same if r2[cid] == r3.get(cid) else diff).append(cid)
res["unchanged_cues"]["resolved_times_and_peaks_equal"] = len(same)
res["unchanged_cues"]["resolved_differ"] = {c: [r2[c]["peak_dbfs"], r3[c]["peak_dbfs"]] for c in diff}
q = json.load(open(P("work", "sound", "qa_v3b.json")))["cues"]
res["changed_cues"] = {c: {kk: q[c][kk] for kk in ("times", "t0", "t1", "peak_dbfs", "song_med", "song_worst", "vocal_worst", "band", "rule")} for c in sorted(changed) if c in q}
json.dump(res, open(P("work", "sound", "verify_v3b.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k != "changed_cues"}, indent=1))
for c, v in res["changed_cues"].items():
    b = v["band"] or {}
    print(f"{c:16} t={v['times'][:6]} peak {v['peak_dbfs']} underSong med {v['song_med']} worst {v['song_worst']} vocal {v['vocal_worst']} band {b.get('median')}/{b.get('p10')}@{b.get('band_hz')} | {v['rule'][:70]}")

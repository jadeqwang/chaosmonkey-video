#!/usr/bin/env python3
"""preview_v4, G5: move the child's sung "Yes" one beat later, instrumental untouched.

    PY=/home/jade/Documents/halys-video/.venv/bin/python
    TMPDIR=$PWD/work/tmp $PY tools/audio/yes_shift_v4.py
      -> inputs/Chaos Monkey - reformatted for duet - v4 yes late.wav   (edited song, PCM_16 like the original; original untouched)
         work/stems/vocals_v4.wav                                       (vocal stem with the word moved, for the layer builder)
         work/sound_v4/edit.json                                        (exact numbers)

Method. The BS-RoFormer split in work/stems/ (tools/audio/stems.py, local) is complementary: song = vocals + instrumental to
-172 dB. So inside the edit window
        out = song - w*V + shift_D(w*V)
where V is the vocal stem, w a window that is 1 over the word and its reverb (148.69-149.40) with raised-cosine ramps in the
pre-word gap (148.62-148.69, vocal stem <= -58 dBFS) and after the song's own cut of the word (149.40-149.50, vocal stem
<= -95 dBFS), and D one beat of the local grid (beats 148.865 -> 149.297 = 0.432 s = 20736 samples, an integer: no
resampling or fractional delay). At the vacated place out == instrumental stem exactly; at the new place the word sits on
the original backing. The edit is additive with smooth windows, so it has no splice points and cannot click; outside
[148.62, 149.932] every sample is copied from the original file.
"""
import json
import os

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)  # noqa
SONG = P("inputs", "Chaos Monkey - reformatted for duet.wav")
OUT = P("inputs", "Chaos Monkey - reformatted for duet - v4 yes late.wav")
VOC = P("work", "stems", "vocals.wav")
VOC_OUT = P("work", "stems", "vocals_v4.wav")
SR = 48000
BEAT_A, BEAT_B = 148.865, 149.297          # analysis/timing.json beats, bar 86 beats 3 and 4 (linear fit; drums are out here)
D = int(round((BEAT_B - BEAT_A) * SR))     # 20736
R_IN = (148.620, 148.690)
R_OUT = (149.400, 149.500)


def window(n):
    w = np.zeros(n)
    a0, a1, b0, b1 = (int(round(x * SR)) for x in (*R_IN, *R_OUT))
    w[a0:a1] = np.sin(0.5 * np.pi * np.arange(a1 - a0) / (a1 - a0)) ** 2
    w[a1:b0] = 1.0
    w[b0:b1] = np.cos(0.5 * np.pi * np.arange(b1 - b0) / (b1 - b0)) ** 2
    return w, a0, b1


def main():
    s16, sr = sf.read(SONG, dtype="int16", always_2d=True)
    assert sr == SR
    info = sf.info(SONG)
    v, sr2 = sf.read(VOC, dtype="float64", always_2d=True)
    assert sr2 == SR and v.shape == s16.shape
    n = len(s16)
    w, i0, i1 = window(n)
    j1 = i1 + D
    seg = slice(i0, j1)
    wv = v[i0:j1] * w[i0:j1, None]                         # the word (zero after i1)
    moved = np.zeros_like(wv)
    moved[D:] = wv[: len(wv) - D]
    s = s16[seg].astype(np.float64) / 32768.0
    out = s - wv + moved
    q = np.clip(np.round(out * 32768.0), -32768, 32767).astype(np.int16)
    clipped = int(np.count_nonzero(np.abs(out * 32768.0) > 32767))
    y = s16.copy()
    y[seg] = q
    sf.write(OUT, y, SR, subtype=info.subtype, format="WAV")
    v2 = v.copy()
    v2[seg] = v[seg] - wv + moved
    sf.write(VOC_OUT, v2.astype(np.float32), SR, subtype="FLOAT")
    # exact numbers
    tm = json.load(open(P("analysis", "timing.json")))
    yes = [ln for ln in tm["lines"] if ln["text"] == "Yes"][0]["words"][0]
    rec = {"song_in": os.path.relpath(SONG, ROOT), "song_out": os.path.relpath(OUT, ROOT), "subtype": info.subtype,
           "shift_samples": D, "shift_s": D / SR, "beat_ref": [BEAT_A, BEAT_B],
           "window_s": {"ramp_in": R_IN, "ramp_out": R_OUT}, "changed_span_s": [i0 / SR, j1 / SR],
           "changed_span_samples": [int(i0), int(j1)], "clipped": clipped,
           "yes_old": {"start": yes["start"], "end": yes["end"]},
           "yes_new": {"start": round(yes["start"] + D / SR, 3), "end": round(yes["end"] + D / SR, 3)}}
    os.makedirs(P("work", "sound_v4"), exist_ok=True)
    json.dump(rec, open(P("work", "sound_v4", "edit.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()

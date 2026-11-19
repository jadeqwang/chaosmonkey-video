#!/usr/bin/env python3
"""Picture lag of a singing take from its own face, robust to the large random lag of Seedance (v4).

    $PY tools/review/ls4_lag.py NAME --t0 T          (needs work/review/lipsync_v4/NAME_face.json from lipsync_v4.py strip)

1. COARSE (phrase structure): the lip gap, smoothed over 5 frames, is cross-correlated with the vocal stem's voice activity
   (broadband level, 24 fps) over +-24 frames. Sung phrases and the silences between them (pre-roll, breaths) fix the lag
   to within a few frames even when the syllables are too fast for the envelope or viseme scan.
2. FINE (visemes): lipsync_gate.score_point over coarse +-3 frames (closures before m/b/p, vowels opening).
Prints shift_f = frames to play the take LATER (negative = earlier) so that frame 0 sits at T + shift_f/24, the peak heights,
and a confidence. Validated on p-video-avatar takes (audio bit-aligned, true shift 0 to -2 f for the mouth lead).
"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import lipsync_gate as G  # noqa: E402

FPS = 24.0


def vad(t_a, n):
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t_a):.3f}", "-t", f"{n / FPS + 0.1:.3f}", "-i", G.STEM, "-ac", "1",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if t_a < 0:
        x = np.concatenate([np.zeros(int(-t_a * sr), np.float32), x])
    hop = sr / FPS
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[int(i * hop):int((i + 1) * hop)] ** 2)) + 1e-9) if int((i + 1) * hop) <= len(x) else -120
                   for i in range(n)])
    return np.clip((db - (db.max() - 40)) / 40, 0, 1)


def lag(name, t0, R=24):
    fj = json.load(open(os.path.join(ROOT, "work/review/lipsync_v4", f"{name}_face.json")))
    gap = np.array([np.nan if v is None else v for v in fj["gap"]], float)
    n = len(gap)
    g, _, _ = G.norm_gap(gap)
    gs = np.convolve(g, np.ones(5) / 5, mode="same")
    pad = R + 2
    v = vad(t0 - pad / FPS, n + 2 * pad)
    vs = np.convolve(v, np.ones(5) / 5, mode="same")
    cs = {}
    for s in range(-R, R + 1):
        # frame k of the take shows song time t0 + (k + s)/24 ... placement shift s: frame 0 at t0 + s/24
        seg = vs[pad + s: pad + s + n]
        a, b = gs - gs.mean(), seg - seg.mean()
        cs[s] = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    c_best = max(cs, key=cs.get)
    others = [cs[s] for s in cs if abs(s - c_best) > 6]
    c_margin = cs[c_best] - (max(others) if others else 0)
    ev = G.events(t0 - 1.5, t0 + n / FPS + 1.0)
    fine = {s: G.score_point(g, ev, t0 + s / FPS) for s in range(c_best - 3, c_best + 4)}
    fine = {s: v_ for s, v_ in fine.items() if not np.isnan(v_)}
    f_best = max(fine, key=fine.get) if fine else c_best
    conf = "high" if cs[c_best] >= 0.5 and c_margin >= 0.15 else ("medium" if cs[c_best] >= 0.35 and c_margin >= 0.08 else "low")
    return dict(name=name, t0=t0, coarse_shift_f=c_best, coarse_r=round(cs[c_best], 2), coarse_margin=round(c_margin, 2),
                shift_f=int(f_best), fine_score=round(fine.get(f_best, float("nan")), 2), confidence=conf,
                place_frame0_at=round(t0 + f_best / FPS, 4), lag_ms=round(-f_best / FPS * 1000))


if __name__ == "__main__":
    name = sys.argv[1]; t0 = float(sys.argv[sys.argv.index("--t0") + 1])
    print(json.dumps(lag(name, t0)))

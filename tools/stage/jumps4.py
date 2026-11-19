"""Teleport check: per consecutive-frame motion (mean abs diff of the ink, 480 px wide) and the ink-centroid step.
Flags frames whose motion is > 2.5x the clip's running median (a pop / teleport / cut).  PY tools/stage/jumps4.py CLIP..."""
import sys, av, cv2, numpy as np
for p in sys.argv[1:]:
    with av.open(p) as c:
        fr = [cv2.resize(f.to_ndarray(format='gray'), (480, 270), interpolation=cv2.INTER_AREA).astype(np.float32) for f in c.decode(video=0)]
    bg = np.median(fr[0][:20])
    ink = [np.clip((bg - f) / 255, 0, 1) for f in fr]
    mot = np.array([np.abs(ink[i] - ink[i - 1]).mean() * 1000 for i in range(1, len(ink))])
    cen = []
    for d in ink:
        w = d.sum() + 1e-6; ys, xs = np.mgrid[:270, :480]
        cen.append(((d * xs).sum() / w, (d * ys).sum() / w))
    cen = np.array(cen); step = np.linalg.norm(np.diff(cen, axis=0), axis=1)
    med = np.array([np.median(mot[max(0, i - 6):i + 7]) for i in range(len(mot))])
    flags = [(i + 1, round(float(mot[i]), 1), round(float(step[i]), 1)) for i in range(len(mot)) if mot[i] > 2.5 * max(med[i], 0.3) and mot[i] > 1.0]
    print(p.split('/')[-1], 'n', len(fr), 'mot med %.2f max %.2f' % (np.median(mot), mot.max()), 'cen step max %.1f' % step.max(), 'flags', flags[:12])

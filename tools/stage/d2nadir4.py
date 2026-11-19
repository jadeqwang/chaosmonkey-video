"""Measure a D2 take: per frame the top of the figure (head/cap); the four bows are the four deepest dips (largest top
y) after he leaves the 亮相. Writes/updates work/stage/v4/d2_nadirs.json.  PY tools/stage/d2nadir4.py TAG..."""
import sys, json, os, av, cv2, numpy as np
from scipy.signal import find_peaks
J = 'work/stage/v4/d2_nadirs.json'
D = json.load(open(J)) if os.path.exists(J) else {}
for tag in sys.argv[1:]:
    with av.open(f'media/gen/stage/v4/clips/{tag}.mp4') as c:
        fr = [cv2.cvtColor(f.to_ndarray(format='rgb24'), cv2.COLOR_RGB2GRAY) for f in c.decode(video=0)]
    tops = []
    for g in fr:
        g = cv2.resize(g, (480, 270)).astype(np.float32); bg = np.median(g[:15])
        rows = np.where(((bg - g) > 40).sum(1) > 2)[0]
        tops.append(rows.min() if len(rows) else 0)
    tops = np.convolve(np.array(tops, float), np.ones(3) / 3, mode='same')
    pk, pr = find_peaks(tops, distance=12, prominence=4)
    best = sorted(sorted(pk, key=lambda i: -pr['prominences'][list(pk).index(i)])[:4])
    leave = int(np.argmax(np.abs(tops - tops[0]) > 3))
    D[tag] = dict(nadir=[i / 24 for i in best], nadir_frames=[int(i) for i in best], leave=max(leave - 2, 0) / 24,
                  tops=[int(x) for x in tops])
    print(tag, 'nadirs', [int(i) for i in best], 'all peaks', list(map(int, pk)), 'leave', leave)
json.dump(D, open(J, 'w'))

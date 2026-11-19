"""Cut figures from chroma-green sheets -> media/swarm4/sprites/*.png + sprites.json"""
import sys, json, os
sys.path.insert(0, 'tools/swarm4')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from key import key
SH = {
 's1': [('read','A'),('read','B'),('write','A'),('write','B')],
 's2': [('abacus','A'),('abacus','B'),('carry','A'),('carry','B')],
 's3': [('spar','A'),('spar','B'),('sweep','A'),('sweep','B')],
 's4': [('watch','A'),('watch','B'),('grind','A'),('grind','B')],
 's5': [('pluck',''),('blow',''),('land',''),('seal','')],
 's6': [('seated','front'),('seated','q34'),('liangxiang','side'),('liangxiang','q34')],
}
OV = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
out = 'media/swarm4/sprites'
meta = json.load(open(out + '/sprites.json')) if os.path.exists(out + '/sprites.json') else {}
for sh, names in SH.items():
    src = f'media/swarm4/raw/{sh}.jpg'
    rgba = key(np.array(Image.open(src).convert('RGB')))
    a = rgba[..., 3] > 60
    for it in (14, 8, 4, 2, 1):
        lab, n = ndi.label(ndi.binary_dilation(a, iterations=it))
        big = [i for i in range(1, n + 1) if ((lab == i) & a).sum() >= 8000]
        if len(big) == len(names): break
    # attach small fragments to nearest big component
    cent = {i: np.array(ndi.center_of_mass(lab == i)) for i in big}
    grp = {i: (lab == i) & a for i in big}
    for i in range(1, n + 1):
        if i in big: continue
        m = (lab == i) & a
        if m.sum() < 30: continue
        c = np.array(ndi.center_of_mass(m)); j = min(big, key=lambda k: np.linalg.norm(cent[k] - c)); grp[j] |= m
    comps = []
    for i in big:
        m = grp[i]; ys, xs = np.where(m); comps.append((xs.mean(), m, ys, xs))
    comps.sort(key=lambda c: c[0])
    if len(comps) != len(names): print('WARN', sh, len(comps), 'components'); 
    for (cx, m, ys, xs), (job, pose) in zip(comps, names):
        m2 = ndi.binary_dilation(m, iterations=3)  # keep soft edge pixels
        al = np.where(m2, rgba[..., 3], 0).astype(np.uint8)
        im = rgba.copy(); im[..., 3] = al
        x0, x1, y0, y1 = max(xs.min()-6,0), xs.max()+7, max(ys.min()-6,0), ys.max()+7
        crop = Image.fromarray(im[y0:y1, x0:x1], 'RGBA')
        name = f'{job}_{pose}'.strip('_')
        crop.save(f'{out}/{name}.png')
        w, h = crop.size
        bb = np.where(al[y0:y1, x0:x1] > 60)
        meta[name] = dict(file=f'{name}.png', w=w, h=h, anchor=[int((bb[1].min()+bb[1].max())/2), int(bb[0].max())], job=job, pose=pose or job, sheet=sh)
        print(name, w, h)
json.dump(meta, open(out + '/sprites.json', 'w'), indent=1)

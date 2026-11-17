"""Page-space art for two room shots (HEAVEN & LEDGER team). Run from the repo root:
    $PY shots/_heaven_pages.py
Writes media/comp/pages/:
  I2_page.png            the heaven spread (D_heaven_mid keyed) on the 2026 aged paper, flat double page, unlit
  J1_page.png            the 花果山 spread (B_master) with 千字文 columns cut into the mountain (tools.ink.cliff,
                         崇羲篆體, raking light from the upper left, cinnabar in the cuts), on aged paper, unlit
  J1_page_charlit.png    the same, the marked character lit (its cut walls bright, deep shadow, warm), nothing else
  J1_char_mask.png       0..1 mask of the marked character's cut (for the room team's own light)
  pages.json             sizes, gutter, page boxes, the marked character's box and centre, 花果山 / stone positions
Both spreads are the book's open-spread aspect (A_open_book.json: two ~2240x2420 pages + gutter -> 1.9:1).
"""
import json
import os
import sys

sys.path.insert(0, '/home/jade/Documents/chaosmonkey-video')
os.chdir('/home/jade/Documents/chaosmonkey-video')
import cv2
import numpy as np

from tools.ink import *
from tools.ink.cliff import Cliff

OUT = 'media/comp/pages/'
ASPECT = 1.9
SEALFONT = 'refs/fonts/chongxi-seal/崇羲篆体.otf'
os.makedirs(OUT, exist_ok=True)


def gutter(img, seed):
    H, W = img.shape[:2]
    xx = np.arange(W, dtype=np.float32)[None, :, None]
    c = W / 2
    shade = 1 - 0.22 * np.exp(-((xx - c) / (W * 0.012)) ** 2) - 0.07 * np.exp(-((xx - c) / (W * 0.05)) ** 2)
    return img * shade


def spread_from(T, seed):
    """Crop an ink layer to the spread aspect (centred vertically) and lay it on aged paper with a gutter."""
    H, W = T.shape[:2]
    h = int(round(W / ASPECT))
    y0 = (H - h) // 2
    T = T[y0:y0 + h]
    P = Paper(W, h, 'aged', seed=seed, gutter=W // 2)
    return gutter(P.rgb * T, seed).astype(np.float32), y0


meta = {}

# ---- I2: the heaven spread
Tm = key_paper(load_image('design/plates/D_heaven/D_heaven_mid.png'))
img, y0 = spread_from(Tm, 71)
save_image(OUT + 'I2_page.png', img)
reg = json.load(open('design/plates/D_heaven/D_heaven_registration.json'))
sx, sy = reg['huaguoshan_stone']['mid_px']
meta['I2_page'] = {'file': 'I2_page.png', 'size': [img.shape[1], img.shape[0]], 'gutter_x': img.shape[1] // 2,
                   'source': 'D_heaven_mid.png keyed, rows %d-%d' % (y0, y0 + img.shape[0]),
                   'huaguoshan_stone_px': [sx, sy - y0], 'lit': False}
print('I2', img.shape)

# ---- J1: the 花果山 spread, carved
plate = load_image('design/plates/B_huaguoshan/B_master.png')
cx0, cy0, cx1, cy1 = 300, 700, 1400, 1920                    # crop of the mountain the Cliff works on
rock = plate[cy0:cy1, cx0:cx1].copy()
lines = [l.strip() for l in open('design/text/qianziwen.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
text = ''.join(lines[:80])
REGION = (150, 440, 570, 1110)                               # the big pale face (plate x 450-870, y 1140-1810)
c = Cliff(rock, text, SEALFONT, size=44, region=REGION, weather=0.22, moss=0.1, presence='auto', seed=8)
LIGHT = (225, 12, 0.9)
base = c.render(light=LIGHT, fill=0.55)
# the marked character: the carved cell nearest the middle of the face
target = (360, 760)
best, bi = None, None
for i in range(len(c.cells)):
    _, qx, qy, _, _ = c.cells[i]
    d = np.hypot(qx - target[0], qy - target[1])
    if best is None or d < best:
        best, bi = d, i
bx0, by0, bw_, bh_ = [float(v) for v in c.char_box(bi)]
bx1, by1 = bx0 + bw_, by0 + bh_
ccx, ccy = (bx0 + bx1) / 2, (by0 + by1) / 2
lit = c.render(light=(225, 8, 1.6), fill=0.8, warmth=0.95, pool=(ccx, ccy, 70), ambient=0.5)
yy, xx = np.mgrid[0:rock.shape[0], 0:rock.shape[1]].astype(np.float32)
m = smoothstep(1.0, 0.55, np.hypot(xx - ccx, yy - ccy) / 52.0)
charlit = base * (1 - m[..., None]) + lit * m[..., None]
cut = getattr(c, 'cut', None)
cm = np.zeros(rock.shape[:2], np.float32)
if cut is not None and getattr(cut, 'shape', None) == rock.shape[:2]:
    box = np.zeros_like(cm)
    box[int(by0) - 2:int(by1) + 2, int(bx0) - 2:int(bx1) + 2] = 1
    cm = (np.asarray(cut, np.float32) > 0).astype(np.float32) * box
ch = c.cells[bi]
print('marked cell', ch)

outs = {}
for name, r in (('J1_page', base), ('J1_page_charlit', charlit)):
    full = plate.copy()
    full[cy0:cy1, cx0:cx1] = r
    T = key_paper(full)
    img, y0 = spread_from(T, 72)
    save_image(OUT + name + '.png', img)
    outs[name] = img
fm = np.zeros(plate.shape[:2], np.float32)
fm[cy0:cy1, cx0:cx1] = cm
fm = fm[y0:y0 + outs['J1_page'].shape[0]]
save_image(OUT + 'J1_char_mask.png', np.dstack([fm] * 3))
char = ch[0]
meta['J1_page'] = {'file': 'J1_page.png', 'lit_variant': 'J1_page_charlit.png', 'mask': 'J1_char_mask.png',
                   'size': [outs['J1_page'].shape[1], outs['J1_page'].shape[0]], 'gutter_x': outs['J1_page'].shape[1] // 2,
                   'source': 'B_master.png rows %d-%d, carved with tools.ink.cliff (千字文 lines 1-80, 崇羲篆體 44 px, '
                             'light az 225 el 12, cinnabar fill 0.55)' % (y0, y0 + outs['J1_page'].shape[0]),
                   'marked_char': str(char),
                   'marked_char_box_px': [bx0 + cx0, by0 + cy0 - y0, bx1 + cx0, by1 + cy0 - y0],
                   'marked_char_centre_px': [ccx + cx0, ccy + cy0 - y0],
                   'marked_char_centre_norm': [(ccx + cx0) / outs['J1_page'].shape[1],
                                               (ccy + cy0 - y0) / outs['J1_page'].shape[0]],
                   'page': 'left', 'lit': False}
json.dump(meta, open(OUT + 'pages.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(meta, ensure_ascii=False, indent=1))

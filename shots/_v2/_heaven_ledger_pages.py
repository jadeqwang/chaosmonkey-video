# HEAVEN & LEDGER team: copy of design/plates/E_underworld/ledger/build_ledger.py extended to 8 pages for K4's page turns.
# p1, p2 are pixel-identical to the plate's p1, p2; p3-p6 are filler pages; p7, p8 have the plate p3/p4 layouts and papers
# (seeds 42, 43; p8's final column bare) with the numbering continued. Writes work/heaven/ledger/. Run from repo root:
#   $PY shots/_heaven_ledger_pages.py
"""Ming-style register (生死簿) pages, built in code. Run from repo root with the HV venv."""
import sys, os, json, math
sys.path.insert(0, '/home/jade/Documents/chaosmonkey-video')
os.chdir('/home/jade/Documents/chaosmonkey-video')
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from tools.ink.paper import Paper, deckle_mask
from tools.ink.ink import wash, stroke
from tools.ink.core import ink_T, rough_mask, F32

FONT = 'refs/fonts/guangekai/館閣楷-Regular.ttf'
TAG = ''
OUT = 'work/heaven/ledger/'
os.makedirs(OUT, exist_ok=True)
W, H = 2200, 3300
TOP, BOT, SIDE = 400, 270, 220
NCOL = 8
BIG, SMALL = 148, 76
PITCH, SPITCH = 156, 82

def fnt(px): return ImageFont.truetype(FONT, px)
for ch in '魂字一千三百五十號孫悟空天產石猴該壽四十二歲善終屬之類似人相不入名走獸伏麒麟管飛禽受鳳凰轄臝蟲居國界六七八九零':
    f = fnt(100)
    assert f.getmask(ch).getbbox() is not None, ch

NUM = '〇一二三四五六七八九'
def cnum(n):
    """1350 -> 一千三百五十 (register style, no 零 dropped digits handled simply)."""
    s = ''; th, hu, te, on = n // 1000, n // 100 % 10, n // 10 % 10, n % 10
    if th: s += NUM[th] + '千'
    if hu: s += NUM[hu] + '百'
    elif th and (te or on): s += '零'
    if te: s += NUM[te] + '十'
    elif hu and on: s += '零'
    if on: s += NUM[on]
    return s
def age(n):
    s = ''; hu, te, on = n // 100, n // 10 % 10, n % 10
    if hu: s += NUM[hu] + '百'
    if te: s += ('' if (te == 1 and not hu) else NUM[te]) + '十'
    elif hu and on: s += '零'
    if on: s += NUM[on]
    return s
assert cnum(1350) == '一千三百五十' and age(342) == '三百四十二'

# descriptors taken verbatim from ch.3 (design/text/categories.txt): 似人相/不入人名, 似臝蟲/不居國界, 似走獸/不伏麒麟管, 似飛禽/不受鳳凰轄
DESC = [('似人相', '不入人名'), ('似臝蟲', '不居國界'), ('似走獸', '不伏麒麟管'), ('似飛禽', '不受鳳凰轄')]
rs = np.random.RandomState(1350)
REAL = 1350
NCOL = 9
def entry(n, kind='double'):
    """A register entry as one or two columns (right to left). double: [number+name], [indented note]."""
    if n == REAL:
        return [dict(t='main', num=f'魂字{cnum(n)}號', name='孫悟空', n=n, real=True),
                dict(t='note', parts=['天產石猴', '該壽三百四十二歲', '善終'], n=n, real=True)]
    if kind == 'single':
        return [dict(t='main', num=f'魂字{cnum(n)}號', name='猴屬', n=n)]
    a = int(rs.choice([47, 58, 63, 71, 81, 88, 93, 96, 104, 112, 120, 136, 150, 77, 69, 99]))
    d = DESC[n % 4]
    parts = [d[0], d[1], f'該壽{age(a)}歲'] + (['善終'] if rs.rand() < 0.6 else [])
    return [dict(t='main', num=f'魂字{cnum(n)}號', name='猴屬', n=n), dict(t='note', parts=parts, n=n)]
def page(spec, n0):
    cols, n = [], n0
    for k in spec:
        if k == 'head': cols.append(dict(t='head', text='猴屬之類'))
        elif k == 'bare': cols.append(None)
        else: cols += entry(n, 'single' if k == 's' else 'double'); n += 1
    assert len(cols) == NCOL, (spec, len(cols))
    return cols, n
p1, n = page(['head', 'd', 'd', 'd', 'd'], 1348)           # 1348, 1349, 1350 (real: columns 5-6), 1351
p2, n = page(['d', 's', 'd', 's', 'd', 's'], n)
f3, n = page(['d', 'd', 's', 'd', 'd'], n)
f4, n = page(['s', 'd', 's', 'd', 'd', 's'], n)
f5, n = page(['d', 's', 's', 'd', 'd', 's'], n)
f6, n = page(['s', 's', 'd', 'd', 's', 'd'], n)
p3, n = page(['s', 'd', 'd', 's', 's', 'd'], n)
p4, n = page(['d', 's', 'd', 's', 'd', 'bare'], n)
PAGES = [p1, p2, f3, f4, f5, f6, p3, p4]
SEEDS = [40, 41, 50, 51, 52, 53, 42, 43]
BIG, PITCH = 136, 146
NOTE, NPITCH = 120, 132

def col_x(i):   # centre x of column i counted from the right
    inner = W - 2 * SIDE
    cw = inner / NCOL
    return W - SIDE - cw * (i + 0.5), cw

def draw_text_mask(cols):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    boxes = {}
    def put(x, y, ch, px):
        d.text((x, y), ch, font=fnt(px), fill=255, anchor='mm')
    for i, c in enumerate(cols):
        if c is None: continue
        cx, cw = col_x(i)
        y = TOP + 40 + PITCH / 2
        y0 = y - PITCH / 2
        if c['t'] == 'head':
            y += PITCH * 1.0
            for ch in c['text']: put(cx, y, ch, BIG); y += PITCH
        elif c['t'] == 'main':
            for ch in c['num']: put(cx, y, ch, BIG); y += PITCH
            y += PITCH * 0.5
            for ch in c['name']: put(cx, y, ch, BIG); y += PITCH
        else:
            y += NPITCH * 2.2                     # notes are indented two characters
            for part in c['parts']:
                for ch in part: put(cx, y, ch, NOTE); y += NPITCH
                y += NPITCH * 0.45
        boxes[i] = (int(cx - cw / 2), int(y0), int(cx + cw / 2), int(y - PITCH / 2))
    return np.asarray(m, F32) / 255.0, boxes

def rule_mask(seed):
    """乌丝栏: outer thick + thin double frame, thin column rules; hand-ruled: slight width and tone wobble."""
    m = np.zeros((H, W), F32)
    r = np.random.RandomState(seed)
    def line(x0, y0, x1, y1, w):
        n = 40
        pts = []
        for k in range(n + 1):
            u = k / n
            pts.append((x0 + (x1 - x0) * u + r.randn() * 0.5, y0 + (y1 - y0) * u + r.randn() * 0.5))
        for (a, b), (c, e) in zip(pts[:-1], pts[1:]):
            cv2.line(m, (int(a * 4), int(b * 4)), (int(c * 4), int(e * 4)), float(0.75 + 0.25 * r.rand()),
                     max(1, int(w * 4 * (0.85 + 0.3 * r.rand()))), lineType=cv2.LINE_AA, shift=2)
    x0, y0, x1, y1 = SIDE - 30, TOP - 30, W - SIDE + 30, H - BOT + 30
    for (a, b, c, e) in [(x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)]: line(a, b, c, e, 8)
    g = 16
    for (a, b, c, e) in [(x0 + g, y0 + g, x1 - g, y0 + g), (x0 + g, y1 - g, x1 - g, y1 - g),
                         (x0 + g, y0 + g, x0 + g, y1 - g), (x1 - g, y0 + g, x1 - g, y1 - g)]: line(a, b, c, e, 2.0)
    inner = W - 2 * SIDE; cw = inner / NCOL
    for i in range(1, NCOL):
        x = SIDE + cw * i
        line(x, y0 + g, x, y1 - g, 1.7)
    return m

def render(p, cols, seed):
    paper = Paper(W, H, 'aged', seed=seed)
    tm, boxes = draw_text_mask(cols)
    Image.fromarray((np.clip(tm, 0, 1) * 255).astype(np.uint8)).save(OUT + f'textmask_s{seed}.png')   # K2b
    rm = rule_mask(seed)
    dt = wash(tm, paper.height, seed=seed, density=0.82, bleed=1.4, edge=0.25, granulate=0.25, pool=0.2, feather=0.35)
    dr = wash(rm, paper.height, seed=seed + 7, density=0.5, bleed=0.9, edge=0.15, granulate=0.4, pool=0.3, feather=0.2)
    T = ink_T(np.maximum(dt, dr * 0.95) + 0.25 * np.minimum(dt, dr))
    # time adds white: ink fades a little where the paper is worn
    T = 1 - (1 - T) * (1 - 0.55 * paper.wear)[..., None]
    img = paper.rgb * T
    return img, boxes, paper

def u8(a): return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))

meta = {'size': [W, H], 'font': FONT, 'columns_right_to_left': NCOL, 'pages': []}
imgs = []
for pi, cols in enumerate(PAGES):
    img, boxes, paper = render(pi, cols, seed=SEEDS[pi])
    name = f'E_ledger_p{pi + 1}{TAG}'
    u8(img).save(OUT + name + '.png')
    imgs.append(img)
    entries = []
    for i, c in enumerate(cols):
        if c is None: entries.append({'col': i, 'bare': True}); continue
        e = {'col': i, 'kind': c['t'], 'box': boxes.get(i)}
        if c['t'] == 'head': e['text'] = c['text']
        elif c['t'] == 'main': e['text'] = c['num'] + ' ' + c['name']; e['n'] = c['n']
        else: e['text'] = ' '.join(c['parts']); e['n'] = c['n']
        e['real'] = bool(c.get('real')); e['invented'] = c['t'] != 'head' and not c.get('real')
        entries.append(e)
    meta['pages'].append({'file': name + '.png', 'columns': entries})
    if pi == 0:
        bx = [boxes[i] for i, c in enumerate(cols) if c and c.get('real')]
        meta['real_entry_box'] = [min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx), max(b[3] for b in bx)]

def spread(right, left):
    g = 70
    sp = np.concatenate([left, np.ones((H, g, 3), F32) * right[:, :1].mean(), right], 1)
    xx = np.arange(sp.shape[1])[None, :, None].astype(F32); c = W + g / 2
    shade = 1 - 0.28 * np.exp(-((xx - c) / 70) ** 2) - 0.08 * np.exp(-((xx - c) / 260) ** 2)
    return sp * shade
for k in range(0, len(imgs), 2):
    u8(spread(imgs[k], imgs[k + 1])).save(OUT + f'spread_{k + 1}_{k + 2}.png')
json.dump(meta, open(OUT + 'ledger8.json', 'w'), ensure_ascii=False, indent=1)
print('ok')

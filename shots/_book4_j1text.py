"""BOOK v4: static text for the J1 page (media/comp/pages/J1_page_v4.png, J1_page_charlit_v4.png, J1_page_v4.json).
Chinese = inscription.py key D1 (五官俱备 / 四肢皆全, the same line as 'Born fully formed'), English = EB Garamond italic
(the lyric layer's Latin italic, tools/cut/lyrics.py). Run: PYTHONPATH=. python shots/_book4_j1text.py"""
import json, math
import numpy as np, cv2
from PIL import Image, ImageDraw
from tools.ink.core import load_image, save_image, lay_ink, ink_T, fbm, blur, F32
from tools.ink.cliff import load_font
from tools.ink.inscription import inscription

W, H = 3392, 1785
ZH_BOX = (1290, 150, 310, 760)          # blank sky right of the peak, left page (gutter at 1696, shadow from ~1650)
ZH_PX = 124                              # page px; 540p full-spread frame (scale 0.283) -> 35 px, a hair above the 30 px norm
EN_LINES = ['Born fully', 'formed']
EN_PX = 128
EN_RIGHT_EDGE = 1235                     # right-aligned against the Chinese columns, a column gap away
EN_TOP = 250
FONT = 'refs/fonts/eb-garamond/EBGaramond-Italic[wght].ttf'
INK = (0.20, 0.17, 0.15)

def english(seed=11):
    f = load_font(FONT, EN_PX)
    try: f.set_variation_by_axes([500])
    except Exception: pass
    r = np.random.RandomState(seed)
    D = np.zeros((H, W), F32); boxes = []
    for i, line in enumerate(EN_LINES):
        im = Image.new('L', (W, H), 0)
        dr = ImageDraw.Draw(im)
        l, t, rr, b = dr.textbbox((0, 0), line, font=f, anchor='ls')
        y = EN_TOP + EN_PX * (0.95 + 1.22 * i)
        x = EN_RIGHT_EDGE - (rr - l) - (0 if i == 0 else 0)
        dr.text((x, y), line, font=f, fill=255, anchor='ls')
        a = np.asarray(im, F32) / 255.0
        D = np.maximum(D, a)
        boxes.append([int(x + l - 6), int(y + t - 6), int(x + rr + 6), int(y + b + 14)])
    core = blur(D, 1.1)
    ph = fbm(H, W, 6.0, seed, 'enph', octaves=3)
    starve = np.clip((ph - 0.55) * 2.0, 0, 1) * 0.25
    d = 0.93 * np.clip(core * (1 - starve) + 0.25 * np.clip(D - blur(D, 2.0), 0, 1), 0, 1)
    d = np.maximum(d, 0.3 * blur(D, 2.2))
    return d.astype(F32), boxes

def build():
    zh = inscription((W, H), 'D1', ZH_BOX, px=ZH_PX, seed=5)
    d, en_boxes = english()
    T_en = ink_T(d, tint=INK)
    out = {}
    for name, src in (('J1_page_v4', 'J1_page'), ('J1_page_charlit_v4', 'J1_page_charlit')):
        f = load_image(f'media/comp/pages/{src}.png')
        f *= T_en
        zh.draw(f)
        save_image(f'media/comp/pages/{name}.png', f)
        out[name] = f
    cols = zh.columns
    x0, y0, bw, bh = zh.box
    sidecar = {
        'page_size_px': [W, H], 'registration': 'identical to J1_page.png (same crop, same 3392x1785 canvas); origin top-left',
        'base': 'J1_page_v4.png', 'charlit': 'J1_page_charlit_v4.png',
        'text_only_layers': 'J1_page_v4_text_T.png (RGB transmittance, multiply onto any paper) and J1_page_v4_text_alpha.png',
        'chinese': {'key': 'D1', 'columns': cols, 'lyric': 'Born fully formed (J1/J2, song 189.99-191.51)',
                    'char_px': zh.px, 'reading': 'top to bottom, columns right to left', 'ink_bbox_px_xyxy': [int(v) for v in zh.bbox],
                    'ink_only_bbox_px_xyxy': [int(x0), int(y0), int(x0 + bw), int(y0 + bh)],
                    'seal_bbox_px_xywh': [int(zh.seal_pos[0]), int(zh.seal_pos[1]), int(zh.seal.shape[1]), int(zh.seal.shape[0])]},
        'english': {'text': ' '.join(EN_LINES), 'lines': EN_LINES, 'font': FONT, 'font_px': EN_PX, 'colour_rgb': list(INK),
                    'line_bboxes_px_xyxy': en_boxes},
        'legibility': 'full spread (3392 px) shown at 960 px: Chinese chars %.0f px, English x-height ~%.0f px' % (zh.px * 960 / W, EN_PX * 0.4 * 960 / W),
        'placement': 'blank sky on the left page, right of the 花果山 peak, left of the gutter; nothing under the text but paper; the peak summit/egg is at ~(700, 560)',
        'alt_if_push_crops': 'the whole right page (x 1760-3340, y 120-1700) is bare paper',
        'proofread': 'Chinese = existing D1 line (no new characters). English = the lyric. '
                     "NOTE: 'Wouldn't you? You're able.' (I4/J1) has no Chinese line in lyrics_zh_v3.txt, so none is on this page.",
    }
    json.dump(sidecar, open('media/comp/pages/J1_page_v4.json', 'w'), ensure_ascii=False, indent=1)
    # text-only layers for the 3D team
    Tfull = np.ones((H, W, 3), F32) * T_en
    zh.draw(Tfull)                     # multiply layer
    save_image('media/comp/pages/J1_page_v4_text_T.png', Tfull)
    save_image('media/comp/pages/J1_page_v4_text_alpha.png', 1 - Tfull.min(-1))
    return sidecar

if __name__ == '__main__':
    print(json.dumps(build()['english']['line_bboxes_px_xyxy']))

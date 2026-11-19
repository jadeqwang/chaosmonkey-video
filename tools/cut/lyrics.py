"""The film's one lyric layer: data (what is shown, when) and renderer (how it is set), composited at assembly.

    from lyrics import LyricLayer
    layer = LyricLayer(all_shots, width, height)            # all_shots: docs/shots.json 'shots' (the whole film)
    plan = layer.plan(shot)                                  # what this shot shows, frame by frame (None: nothing)
    stats = layer.measure(plan, frame_rgb_u8, index)         # pass 1: luminance under the text box
    look = layer.decide(plan, stats, prev_state)             # ground: 'paper' (ink) or 'night' (cream + wash)
    painter = layer.painter(plan, look)                      # pass 2: painter(PIL image, index) -> PIL image

Text comes from analysis/timing.json `lines` (the lyric sheet's own spelling, punctuation and spacing) with word onsets.
Every parameter of the look is a named constant below so the layer can be restyled in one place; per-shot placement
overrides are in OVERRIDES. `assemble.py --lyrics on|off` switches the whole layer; the picture files never contain it.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FPS = 24
TIMING = ROOT / 'analysis/timing_v4.json'      # v4: the song with the 'Yes' one beat late (REVISION_V4 §12); v3 used timing.json

# ------------------------------------------------------------------------------------------------ what is shown
# Never shown: the parenthetical echoes, "(ps ps ps)" (never subtitled: a rule of the film), and the two 一通百通 lines
# (art inscriptions in the picture, D4/D5 and J5). Everything else in `lines` is shown, "Monkey!" and "Yes" included.
HIDE_PARENTHESES = True
HIDE_TEXTS = {'一通百通'}
# The rap (107.04-121.47): v3 set the Chinese line with the director's English beneath it. v4 (REVISION_V4 §1.3): the
# Chinese row is gone (the room calligraphy, tools/cut/roomcal.py, carries the sung words); only the English is set.
RAP_RANGE = (107.0, 121.47)
RAP_ENGLISH = {
    '石头里蹦出来 没有童年': 'Burst out of a stone, no childhood',
    '一声耳语 学会七十二变': 'One whisper, and learned the 72 transformations',
    '拔一把毫毛 吹一口气': 'Pluck a handful of hairs, blow one breath',
    '千百个我 同时在这里': 'Hundreds, thousands of me, all here at once',
    '每一个都是我 每一个都算': 'Each one is me, each one counts',
    '说完这句话 各自消散': 'When this sentence is finished, each one scatters',
    '身外身法 谁是真身': 'Body outside the body: which is the real one?',
    '问了也白问 个个都真': 'No use asking, every one is real',
}
# Voices: Mom upright, Child italic (Latin) / same weight (CJK). Lines sung by both are set upright. No names, no colours.
VOICE_ITALIC = {'child': True, 'mom': False, 'both': False}

# ------------------------------------------------------------------------------------------------ type
LATIN_FONT = ROOT / 'refs/fonts/eb-garamond/EBGaramond[wght].ttf'
LATIN_ITALIC_FONT = ROOT / 'refs/fonts/eb-garamond/EBGaramond-Italic[wght].ttf'
CJK_FONT = ROOT / 'refs/fonts/lxgw-wenkai/霞鹜文楷-Regular.ttf'
REF_H = 1080                 # all pixel sizes below are at 1080p and scale with the output height
LATIN_PX = 60                # EB Garamond 60 px at 1080p: x-height 24 px (12 px at 540p), cap height 39 px
LATIN_WEIGHT = 500           # variable-font weight axis (400 regular .. 800); a touch heavier for 540p
CJK_MATCH = 1.18             # CJK ideograph ink height = this x the Latin cap height (optical match)
CJK_SPACE_EM = 0.45          # a space between two CJK characters, in CJK em
RAP_EN_SCALE = 1.00          # the rap's English, relative to LATIN_PX (v3: 0.80 under the Chinese row; v4 it is the row)
RAP_CHINESE_ROW = False      # v4: no sans-serif Chinese row under/over the rap
LEADING = 1.28               # baseline-to-baseline distance, in the row's px
RAP_LEADING = 1.55           # from a rap line's last Chinese row to its English row, in the English row's px
BASELINE_Y = 0.86            # baseline of the LAST row, fraction of frame height (lower third)
WRAP_FRAC = 0.62             # wider than this fraction of the frame -> two balanced rows
SAFE_ASPECT = 4 / 5          # the centred 4:5 safe area (vertical crop) ...
SAFE_PAD = 0.03              # ... minus this fraction of its width on each side
MAX_ROWS = 4                 # rows allowed (narrow placements in margins/corners need three or four)
MIN_SCALE = 0.80             # if the rows still do not fit, shrink down to this, never below
COMMA_BONUS = 0.06           # a row break after a comma/question mark is preferred up to 6 % of extra width

# ------------------------------------------------------------------------------------------------ colour / ink
INK_RGB = (0.20, 0.175, 0.150)     # paper grounds: dark warm grey ink, multiplied
INK_OPACITY = 0.85
INK_GRAIN = 0.08                   # slight density variation inside the strokes (paper grounds)
CREAM_RGB = (0.935, 0.905, 0.835)  # night grounds: pale paper-cream
CREAM_OPACITY = 0.92
WASH_MIN, WASH_MAX = 0.10, 0.35    # night grounds: a feathered dark ink wash multiplied behind the line, only as strong as needed
WASH_GAIN = 0.75                   # wash = WASH_MIN + WASH_GAIN * (p90 luma under the line - WASH_FLOOR)
WASH_FLOOR = 0.10
WASH_PAD_EM = 0.55                 # wash reaches this far past the letters (in em), ...
WASH_FEATHER_EM = 0.45             # ... feathered with this Gaussian sigma (in em). No hard box, no glow.
ROUGH = 0.30                       # edge roughness (like tools.ink's inscription): strength of the edge noise
ROUGH_CELL_PX = 1.6                # noise cell at 1080p
SUPERSAMPLE = 2
# Ground per shot from the mean luminance under the text box (over the frames where text shows), with hysteresis
# against the previous shot's ground. The look switches hard, and only at cuts (one decision per shot).
PAPER_ON = 0.50                    # above this: paper (ink text)
NIGHT_ON = 0.38                    # below this: night (cream text + wash); in between: keep the previous ground
MIN_RUN = 8                        # a ground must hold this many frames to switch (flashes and flips never switch it)
MIST_RGB = (0.925, 0.900, 0.835)   # per-shot 'mist' (paper grounds over busy rock): bare paper laid behind the line

# ------------------------------------------------------------------------------------------------ timing
REVEAL = (0.70, 1.0)               # a word's opacity on its onset frame and the next (no fade longer than 2 frames)
CLEAR_AFTER = 6                    # frames after the line's end time (or when the next line starts, if sooner)
MIN_SEGMENT = 4                    # a line that would show for fewer frames before a cut starts at the cut instead
ROOM_WORLDS = {'attic88', 'car26', 'bed26'}     # room <-> book/stage (book, stage, blank): a line never crosses

# ------------------------------------------------------------------------------------------------ placement
# x: anchor (fraction of width), align: 'c' | 'l' | 'r', y: baseline of the last row, scale: size, maxw: max row width
# (fraction of width; default: the 4:5 safe area), ground: force 'paper' | 'night'.
DEFAULT = dict(x=0.5, align='c', y=BASELINE_Y, scale=1.0, maxw=None, ground=None)
# Units: shots spliced from parts (tools/cut/splice.py) or cut internally are scheduled, placed and lit per part.
# (id, first frame, world). A line never crosses a room <-> book/stage cut inside a shot either.
PARTS = {
    'B2': [('B2a', 535, 'attic88'), ('B2b', 591, 'attic88')],       # v4: lap two-shot to 24.6 s, then over the shoulder onto the page
    'C5': [('C5a', 1254, 'attic88'), ('C5b', 1311, 'book')],
    'D2': [('D2', 1466, 'stage'), ('D2d', 1531, 'attic88')],
    'F3': [('F3a', 2665, 'car26'), ('F3b', 2694, 'attic88')],
    'F4': [('F4', 2706, 'book')],                                   # v4: SWARM's one shot (painted world), F4 = s0-82
    'F5': [('F5', 2789, 'book')],                                   #     s83-125
    'F6': [('F6a', 2832, 'book'), ('F6b', 2882, 'car26')],          #     s126-175, then the mirror shot (REVISION_V4 §12)
    'G6': [('G5b', 3583, 'attic88')],
    'E3': [('E3a', 2232, 'attic88'), ('E3b', 2304, 'attic88')],    # v4: synced face, then the wide held sword-hand pose (ATTIC)                               # v4: G5 runs through G6's slot (one 78-f shot, §12)
    'I2': [('I2', 4325, 'book')],                                   # v3: BOOK's page comp fills the slot
    'K1': [('K1a', 4889, 'bed26'), ('K1b', 4973, 'book')],          # v3: BOOK's K1 page from 207.208
    'I4': [('I4', 4488, 'bed26'), ('I4b', 4545, 'bed26')],           # v3: from 189.375 the page and fingertip (J1's view)
    'I3': [('I3a', 4391, 'bed26'), ('I3b', 4431, 'book')],
    'K2': [('K2a', 5053, 'bed26'), ('K2b', 5091, 'book')],
}
# Per-unit placement overrides (unit id, or 'unit:line' with the timing.json line index for one line). Re-set for
# preview_v3 (every picture changed): checked on every lyric line of the cut (work/cut/qa/preview_v3_lyr_*.jpg), against
# the painted inscriptions, seals and name slips. Reasons: docs/QA_PREVIEW_V3.md. Keys: x, align, y, scale, maxw,
# ground ('paper'|'night'), mist (0..1 bare paper behind the line on busy paper grounds), delay (frames).
R, L = 'r', 'l'
OVERRIDES = {
    'B1':  dict(align=L, x=0.03, y=0.955, maxw=0.27),           # dark quilt lower left, off the child and her hands
    'B2a': dict(align=L, x=0.025, y=0.93, maxw=0.30),           # dark floor left of the lap
    'B2b': dict(x=0.72),                                        # over the shoulder: dark heads, then the bare page right (as B3)
    'B3':  dict(x=0.72),                                        # bare page right of the mountain, under the inscription
    'B4':  dict(x=0.70, mist=0.60),                             # right of the macro character; then carved rock: mist under the line
    'B5':  dict(x=0.86, y=0.78, maxw=0.22),                     # bare paper right, under the inscription (same place as C1)
    'C1':  dict(x=0.86, y=0.78, maxw=0.22),                     # off the egg and its crack, bare paper right
    'C2':  dict(x=0.82),                                        # off the hands and the shadow (dark floor right)
    'C3':  dict(align=L, x=0.025, y=0.93, maxw=0.22),           # dark quilt left, off Mama's arms and the hands
    'C5a': dict(align=R, x=0.975, y=0.90, maxw=0.36),           # dark floor right, off Mama and the book
    'C5b': dict(x=0.68),                                        # beside the egg, below the inscription
    'C6':  dict(x=0.72, mist=0.35),                             # beside the cracking egg
    'D1':  dict(x=0.76),                                        # off the splash and the monkey, below inscription and seal
    'D2':  dict(x=0.20, maxw=0.30),                             # left of the bowing monkey: the seal column and inscription are right
    'D2d': dict(align=L, x=0.025, maxw=0.28),                   # dark floor left; off Mama, child and the books
    'D3':  dict(align=L, x=0.025, maxw=0.24),                   # dark floor left, off the lap and the book
    'D5':  dict(x=0.82, maxw=0.30, mist=0.45),                  # off the cliff; below the inscription
    'D6':  dict(x=0.72, y=0.90, maxw=0.30),                       # 6 frames: between the pillars and the monkey's entrance
    'E1':  dict(align=R, x=0.975, y=0.93, maxw=0.30),           # dark quilt right, off the nose tap and the child
    'E2':  dict(align=R, x=0.975, maxw=0.21),                   # bare paper under the inscription, off the troop
    'E3':  dict(x=0.27),                                        # the dark left, off the child
    'E6':  dict(align=R, x=0.975, y=0.90, maxw=0.30),           # dark floor right, off Mama and the child
    'F1':  dict(align=R, x=0.975, y=0.90, maxw=0.29),           # the empty second seat, off the rapping child
    'F2':  dict(align=L, x=0.025, y=0.90, maxw=0.38),           # (v2 comp) door panel, off the child and the puppet pane
    'F3a': dict(align=L, x=0.025, y=0.90, maxw=0.30),           # dark door and seat edge left, off the palm and the dress
    'F3b': dict(align=L, x=0.03, y=0.93, maxw=0.30),            # 12 f: dark floor lower left, off the palm and the faces
    'F4':  dict(x=0.62, y=0.95),                                # v4 swarm: right of the spawning monkey (f0), calligraphy is top right
    'E4':  dict(align=L, x=0.04, y=0.93, maxw=0.30),           # v4: bare paper lower left, off the monkey and his tail
    'F5':  dict(y=0.97, scale=0.85, maxw=0.72),                 # v4 swarm: one row along the bottom (no leaf any more)
    'F6a': dict(y=0.975, scale=0.85, maxw=0.72),                # v4: one row under the 真 seal on the rock between the twins
    'F6b': dict(x=0.30, y=0.90),                                # dark door left, off the laughing child
    'G1':  dict(align=L, x=0.12, y=0.88, maxw=0.20),            # dark attic left; off faces and book
    'G1:35': dict(align=L, x=0.17, y=0.965, maxw=0.20),         # the margins have closed to x 0.15: dark floor inside the strip
    # G2-G5: the picture strip is narrow; the line sits in the bare-paper RIGHT margin, in ink
    'G2:36': dict(align=L, x=0.828, y=0.88, maxw=0.16, ground='paper'),
    'G2:38': dict(align=L, x=0.735, y=0.88, maxw=0.25, ground='paper'),
    'G2':  dict(align=L, x=0.745, y=0.88, maxw=0.23, ground='paper'),
    'G3':  dict(align=L, x=0.665, maxw=0.30, ground='paper'),
    'G4':  dict(align=L, x=0.03, y=0.95, maxw=0.40, delay=14),  # v4: G4 opens to full frame; dark floor lower left, off the fallen books
    'G4:43': dict(align=R, x=0.975, y=0.94, maxw=0.32),        # after the push in: dark pillow/floor right, off faces and the lifted finger
    'G5':  dict(align=R, x=0.975, y=0.94, maxw=0.30),          # v4 full-frame close-up: right, off her face (G6's slot = unit G5b)
    'G5b': dict(align=R, x=0.975, y=0.94, maxw=0.30),
    'H3':  dict(y=0.97, scale=0.9, mist=0.5),                   # under the big faces' chins, on the rule between the rows
    'H4':  dict(y=0.965, scale=0.9, mist=0.5),                  # under the album's bottom row (pull-back)
    'H5':  dict(align=R, x=0.975, y=0.90, maxw=0.20),           # the mist veil right, under the inscription, off the carving
    'H6':  dict(align=R, x=0.95, y=0.90, scale=0.8),            # the emptiest frame: small, lower right, under the inscription
    'I1':  dict(align=L, x=0.12, y=0.955, maxw=0.40, delay=12), # v4: after the white-in; right of the calligraphy (lower left)
    'I2':  dict(x=0.62, y=0.93, maxw=0.40),                     # bare cloud lower centre: right of the couplet, under the host
    'I3a': dict(align=L, x=0.02, y=0.82, maxw=0.20),             # the dark bedside left, off the child's face and the sleeves
    'I3b': dict(align=L, x=0.04, y=0.95, maxw=0.42, mist=0.4), # bare cloud lower left, under the inscription and its seal
    'I4':  dict(y=0.95, ground='night'),                        # centred face: below the chin, on the dark hair
    'I4b': dict(align=L, x=0.025, y=0.90, maxw=0.32),           # the page and fingertip (as J1)
    'J1':  dict(align=L, x=0.025, y=0.90, maxw=0.32),           # dark bedspread left, off the pointing hand
    'J3':  dict(x=0.80, maxw=0.30),                             # off the monkey's stance
    'J4':  dict(x=0.75, y=0.93),                                # the 2026 half's dark floor: off the paper strip between the halves
    'K1a': dict(align=L, x=0.02, y=0.955, maxw=0.24),            # dark floor left, off the book and the lap
    'K1b': dict(y=0.955),                                       # under the rope and the walkers
    'K2a': dict(align=R, x=0.975, maxw=0.28),                   # off the book, on the dark hair
    'K3':  dict(align=L, x=0.03, maxw=0.36),                    # the dark columns left, under the inscription, off the struck entry
    'K4':  dict(align=R, x=0.985, y=0.88, maxw=0.16, scale=0.9),  # the dark right of the spread, under the inscription
    'K5':  dict(align=L, x=0.025, maxw=0.21, ground='night'),   # lower left in the dark, under the inscription
    'L1':  dict(align=L, x=0.025, maxw=0.21, ground='night'),   # continues K5's line from K5's last frame
}


# ================================================================================================ helpers
def is_cjk(ch):
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF
            or 0x20000 <= o <= 0x2FFFF)


def frame_floor(t):
    """The frame containing time t (the onset rule used by the fix rounds)."""
    return int(math.floor(t * FPS + 1e-6))


def world_class(world):
    return 'room' if world in ROOM_WORLDS else 'page'


_FONTS = {}


def _font(path, px, weight=None):
    key = (str(path), int(px), weight)
    if key not in _FONTS:
        f = ImageFont.truetype(str(path), int(px), layout_engine=ImageFont.Layout.BASIC)
        if weight is not None:
            try:
                f.set_variation_by_axes([weight])
            except Exception:
                pass
        _FONTS[key] = f
    return _FONTS[key]


# ================================================================================================ data
class Line:
    def __init__(self, idx, rec):
        self.idx = idx
        self.text = rec['text']
        self.voice = rec.get('singer', 'mom')
        self.start, self.end = float(rec['start']), float(rec['end'])
        self.words = [(str(w.get('w', w.get('word', w.get('text', '')))), float(w['start'])) for w in rec.get('words', [])]
        self.english = RAP_ENGLISH.get(self.text) if RAP_RANGE[0] <= self.start < RAP_RANGE[1] else None
        self.tokens = self._tokens()                    # [(char_start, char_end, onset_frame)]
        self.first = self.tokens[0][2] if self.tokens else frame_floor(self.start)
        self.clear = frame_floor(self.end) + CLEAR_AFTER

    def _tokens(self):
        """Map each timed word onto the written text; a word takes the punctuation that follows it."""
        text, cur, out = self.text, 0, []
        for w, t in self.words:
            p = text.find(w, cur)
            if p < 0:
                p = text.lower().find(w.lower(), cur)
            if p < 0:
                raise ValueError(f'lyrics: word {w!r} not found in {text!r}')
            e = p + len(w)
            while e < len(text) and not text[e].isspace() and not text[e].isalnum() and not is_cjk(text[e]):
                e += 1
            if out:                                     # anything skipped belongs to the previous word
                out[-1] = (out[-1][0], p, out[-1][2]) if text[out[-1][1]:p].strip() else out[-1]
            out.append((p, e, frame_floor(t)))
            cur = e
        if out and out[-1][1] < len(text) and text[out[-1][1]:].strip():
            out[-1] = (out[-1][0], len(text), out[-1][2])
        return out

    @property
    def shown(self):
        if HIDE_PARENTHESES and self.text.strip().startswith('('):
            return False
        return self.text.strip() not in HIDE_TEXTS


def load_lines(path=TIMING):
    data = json.loads(Path(path).read_text())
    recs = data.get('lines') or data.get('lyrics') or []
    lines = [Line(i, r) for i, r in enumerate(recs)]
    shown = sorted([l for l in lines if l.shown], key=lambda l: l.first)
    for a, b in zip(shown, shown[1:]):                 # a line clears when the next one starts, if sooner
        a.clear = min(a.clear, b.first)
    return shown


# ================================================================================================ layout
class Setting:
    """A line laid out for one placement at one output size: per-token masks in a box, the box's frame position."""

    def __init__(self, line, place, W, H):
        self.line, self.place, self.W, self.H = line, place, W, H
        k = H / REF_H * place.get('scale', 1.0)
        italic = VOICE_ITALIC.get(line.voice, False)
        self.rows = []                                    # [(segments, px, width)]
        maxw = self._maxw()
        for shrink in np.linspace(1.0, MIN_SCALE, 9):
            px = LATIN_PX * k * shrink
            if line.english and not RAP_CHINESE_ROW:
                main, extra = self._rows(line.english, None, px * RAP_EN_SCALE, italic, maxw), []
            else:
                main = self._rows(line.text, list(range(len(line.tokens))), px, italic, maxw)
                extra = []
                if line.english:
                    extra = self._rows(line.english, None, px * RAP_EN_SCALE, italic, maxw)
            rows = main + extra
            if max(r[2] for r in rows) <= maxw or shrink == MIN_SCALE:
                break
        self.rows, self.px = rows, px
        self.n_main = len(main)
        self._render()

    def _maxw(self):
        p = self.place
        if p.get('maxw'):
            return p['maxw'] * self.W
        safe = min(self.W, SAFE_ASPECT * self.H) * (1 - 2 * SAFE_PAD)
        return min(WRAP_FRAC * self.W, safe)

    # -- segmentation into font runs, by token (so each token is drawn alone and revealed on its onset)
    def _segments(self, text, tok_of, px, italic, lo, hi):
        lat = _font(LATIN_ITALIC_FONT if italic else LATIN_FONT, round(px), LATIN_WEIGHT)
        cjk_px = self._cjk_px(px)
        cjk = _font(CJK_FONT, round(cjk_px))
        raise_ = self._cjk_raise(px, cjk_px)
        segs, x, i = [], 0.0, lo
        while i < hi:
            ch = text[i]
            if ch == ' ':
                prev_c = i > lo and is_cjk(text[i - 1])
                next_c = i + 1 < hi and is_cjk(text[i + 1])
                x += CJK_SPACE_EM * cjk_px if (prev_c and next_c) else lat.getlength(' ')
                i += 1
                continue
            c = is_cjk(ch)
            j = i
            while j < hi and text[j] != ' ' and is_cjk(text[j]) == c and tok_of(j) == tok_of(i):
                j += 1
            run = text[i:j]
            f = cjk if c else lat
            segs.append((x, run, f, -raise_ if c else 0.0, tok_of(i)))
            x += f.getlength(run)
            i = j
        return segs, x

    @staticmethod
    def _cjk_px(px):
        lat = _font(LATIN_FONT, 200, LATIN_WEIGHT)
        cap = lat.getbbox('H', anchor='ls')
        cjk = _font(CJK_FONT, 200).getbbox('国', anchor='ls')
        return px * CJK_MATCH * (cap[3] - cap[1]) / (cjk[3] - cjk[1])

    @staticmethod
    def _cjk_raise(px, cjk_px):
        """Shift CJK so its ink centre sits on the Latin cap-height centre."""
        lat = _font(LATIN_FONT, 200, LATIN_WEIGHT).getbbox('H', anchor='ls')
        cjk = _font(CJK_FONT, 200).getbbox('国', anchor='ls')
        lat_c = -(lat[1] + lat[3]) / 2 * px / 200
        cjk_c = -(cjk[1] + cjk[3]) / 2 * cjk_px / 200
        return lat_c - cjk_c

    def _rows(self, text, tokens, px, italic, maxw):
        if tokens is None:                                # untimed text (rap English): one token, index -1
            def tok_of(i):
                return -1
        else:
            spans = self.line.tokens

            def tok_of(i):
                for k, (a, b, f) in enumerate(spans):
                    if a <= i < b:
                        return k
                return max([k for k, (a, b, f) in enumerate(spans) if a <= i] or [0])
        segs, w = self._segments(text, tok_of, px, italic, 0, len(text))
        if w <= maxw:
            return [(segs, px, w)]
        spaces = [i for i, ch in enumerate(text) if ch == ' ']
        best = None
        for n in range(2, MAX_ROWS + 1):                   # balanced rows, broken at spaces; fewest rows that fit
            for cut in itertools.combinations(spaces, n - 1):
                bounds = [0] + [c + 1 for c in cut]
                ends = list(cut) + [len(text)]
                rows = [self._segments(text, tok_of, px, italic, a_, b_) for a_, b_ in zip(bounds, ends)]
                ws = [r[1] for r in rows]
                score = max(ws) / max(sum(ws) / n, 1)
                score -= COMMA_BONUS * sum(1 for c in cut if text[c - 1] in ',?!;:，')
                cand = (max(ws) > maxw, score, [(r[0], px, r[1]) for r in rows])
                if best is None or cand[:2] < best[:2]:
                    best = cand
            if best is not None and not best[0]:
                break
        return best[2] if best else [(segs, px, w)]

    # -- raster
    def _render(self):
        ss = SUPERSAMPLE
        p = self.place
        lead = [r[1] * (RAP_LEADING if i == self.n_main else LEADING) for i, r in enumerate(self.rows)]
        asc = self.rows[0][1] * 1.05
        desc = self.rows[-1][1] * 0.40
        heights = sum(lead[1:])
        width = max(r[2] for r in self.rows)
        pad = int(math.ceil(self.px * (WASH_PAD_EM + 3 * WASH_FEATHER_EM)))
        bw, bh = int(math.ceil(width)) + 2 * pad, int(math.ceil(asc + heights + desc)) + 2 * pad
        # frame position of the box
        base_last = p.get('y', BASELINE_Y) * self.H
        if p.get('align', 'c') == 'c':
            cx = p.get('x', 0.5) * self.W
            left = cx - width / 2
        elif p['align'] == 'l':
            left = p['x'] * self.W
        else:
            left = p['x'] * self.W - width
        top = base_last - heights - asc
        self.x0, self.y0 = int(round(left)) - pad, int(round(top)) - pad
        self.bw, self.bh = bw, bh
        n_tok = max(len(self.line.tokens), 1)
        layers = {}
        y = pad + asc
        for ri, (segs, px, w) in enumerate(self.rows):
            if ri:
                y += lead[ri]
            if p.get('align', 'c') == 'c':
                xr = pad + (width - w) / 2
            elif p['align'] == 'l':
                xr = pad
            else:
                xr = pad + width - w
            for (x, run, f, dy, tok) in segs:
                im = layers.get(tok)
                if im is None:
                    im = layers[tok] = Image.new('L', (bw * ss, bh * ss), 0)
                fs = _font(f.path, round(f.size * ss), LATIN_WEIGHT if 'Garamond' in str(f.path) else None)
                ImageDraw.Draw(im).text(((xr + x) * ss, (y + dy) * ss), run, font=fs, fill=255, anchor='ls')
        rough = self._noise(bw * ss, bh * ss, ROUGH_CELL_PX * self.H / REF_H * ss, 1)
        grain = self._noise(bw, bh, self.px * 0.35, 2)
        masks = {}
        for tok, im in layers.items():
            a = np.asarray(im, np.float32) / 255.0
            edge = 4 * a * (1 - a)
            a = np.clip(a + ROUGH * (rough - 0.5) * edge * 2.0, 0, 1)
            a = cv2.resize(a, (bw, bh), interpolation=cv2.INTER_AREA)
            masks[tok] = a
        self.masks = masks
        full = np.zeros((bh, bw), np.float32)
        for a in masks.values():
            full = np.maximum(full, a)
        self.full = full
        self.grain = 1 - INK_GRAIN * grain
        r = max(1, int(round(self.px * WASH_PAD_EM)))
        wash = cv2.dilate(full, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
        wash = cv2.GaussianBlur(wash, (0, 0), self.px * WASH_FEATHER_EM)
        self.wash = wash / max(float(wash.max()), 1e-6)
        ys, xs = np.nonzero(full > 0.05)
        self.ink_box = (self.x0 + int(xs.min()), self.y0 + int(ys.min()), self.x0 + int(xs.max()) + 1,
                        self.y0 + int(ys.max()) + 1) if len(xs) else (self.x0, self.y0, self.x0 + bw, self.y0 + bh)
        self.n_tok = n_tok

    def _noise(self, w, h, cell, key):
        seed = int(hashlib.md5(f'{self.line.idx}:{key}'.encode()).hexdigest()[:8], 16)
        r = np.random.default_rng(seed)
        gw, gh = max(2, int(w / max(cell, 0.5)) + 2), max(2, int(h / max(cell, 0.5)) + 2)
        g = r.random((gh, gw)).astype(np.float32)
        return cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC).clip(0, 1)

    def alpha(self, frame):
        """Mask at absolute frame `frame` (word-by-word reveal)."""
        a = np.zeros((self.bh, self.bw), np.float32)
        for tok, m in self.masks.items():
            if tok == -1:                                  # the rap English: with the first word
                on = self.line.first
            else:
                on = self.line.tokens[tok][2]
            k = frame - on
            if k < 0:
                continue
            v = REVEAL[min(k, len(REVEAL) - 1)]
            a = np.maximum(a, m * v)
        return a


# ================================================================================================ the layer
class LyricLayer:
    """Schedules the lines over the film's units (shots, and the parts of spliced/internally cut shots), sets them
    per placement, and paints them on laid frames."""

    def __init__(self, shots, W, H, overrides=None, timing=TIMING):
        self.shots = shots
        self.W, self.H = W, H
        self.lines = load_lines(timing)
        self.over = OVERRIDES if overrides is None else overrides
        self._settings = {}
        self.units = []                               # [{'id', 'shot', 'world', 'in_frame', 'out_frame'}]
        for sh in shots:
            parts = PARTS.get(sh['id'], [(sh['id'], sh['in_frame'], sh['world'])])
            for k, (uid, f0, world) in enumerate(parts):
                f1 = parts[k + 1][1] if k + 1 < len(parts) else sh['out_frame']
                self.units.append({'id': uid, 'shot': sh['id'], 'world': world, 'in_frame': f0, 'out_frame': f1})
        self._fix_clears()

    def place(self, uid, line=None):
        p = dict(DEFAULT)
        p.update(self.over.get(uid, {}))
        if line is not None:
            p.update(self.over.get(f'{uid}:{line.idx}', {}))
        return p

    def setting(self, line, uid):
        p = self.place(uid, line)
        key = (line.idx, json.dumps(p, sort_keys=True))
        if key not in self._settings:
            self._settings[key] = Setting(line, p, self.W, self.H)
        return self._settings[key]

    # ---- schedule
    def _unit_at(self, fr):
        for i, u in enumerate(self.units):
            if u['in_frame'] <= fr < u['out_frame']:
                return i
        return None

    def segments(self, line):
        """[(unit_index, f_from, f_to)] where the line shows (absolute frames), after the cut rules."""
        segs = []
        f, end = line.first, line.clear
        i = self._unit_at(f)
        while i is not None and f < end:
            u = self.units[i]
            f = max(f, u['in_frame'] + int(self.place(u['id']).get('delay', 0)))
            if f >= min(end, u['out_frame']):                  # held back past this unit (delay)
                if u['out_frame'] >= end:
                    break
                f, i = u['out_frame'], i + 1
                continue
            to = min(end, u['out_frame'])
            nxt = self.units[i + 1] if i + 1 < len(self.units) else None
            if nxt is not None and to == u['out_frame'] and end > to and (to - f) < MIN_SEGMENT:
                f, i = to, i + 1                              # too short before the cut: start at the cut
                continue
            segs.append((i, f, to))
            if nxt is None or to >= end:
                break
            if world_class(nxt['world']) != world_class(u['world']):
                later = [tk[2] for tk in line.tokens if tk[2] >= to]
                if not later or later[0] >= end:
                    break                                     # nothing left to sing in the new world
                f = later[0]                                  # re-appear on the next word in the new world
                i = self._unit_at(f)
                continue
            f, i = to, i + 1
        return segs

    def _fix_clears(self):
        """A line clears when the next line actually shows (after the cut rules), never later than its own end + 6."""
        starts = []
        for line in self.lines:
            segs = self.segments(line)
            starts.append(segs[0][1] if segs else line.first)
        for k, line in enumerate(self.lines[:-1]):
            own = frame_floor(line.end) + CLEAR_AFTER
            line.clear = min(own, max(line.clear, starts[k + 1]))

    def plan(self, shot):
        """Items for one shot: [(line, setting, f_from, f_to, unit)] in absolute frames; None if nothing shows."""
        items = []
        for line in self.lines:
            if line.clear <= shot['in_frame'] or line.first >= shot['out_frame'] + 48:
                continue
            for i, a, b in self.segments(line):
                u = self.units[i]
                if u['shot'] == shot['id']:
                    items.append((line, self.setting(line, u['id']), a, b, u))
        if not items:
            return None
        units = [u for u in self.units if u['shot'] == shot['id']]
        return {'shot': shot, 'items': items, 'units': units,
                'place': {u['id']: self.place(u['id']) for u in units}}

    def signature(self, plan, state_in):
        if plan is None:
            return None
        return hashlib.sha256(json.dumps({
            'items': [(l.idx, l.text, l.english, l.tokens, a, b, u['id'], s.place) for l, s, a, b, u in plan['items']],
            'place': plan['place'], 'state_in': state_in}, sort_keys=True).encode()).hexdigest()[:16]

    # ---- pass 1: measure
    def visible(self, plan, index):
        f = plan['shot']['in_frame'] + index
        return [(l, s, u) for l, s, a, b, u in plan['items'] if a <= f < b]

    def measure(self, plan, rgb, index):
        """rgb: HxWx3 uint8. Returns (mean luma, p90 luma) under the visible text's box, or None."""
        vis = self.visible(plan, index)
        if not vis:
            return None
        vals = []
        for l, s, u in vis:
            x0, y0, x1, y1 = s.ink_box
            pad = int(s.px * 0.3)
            x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(self.W, x1 + pad), min(self.H, y1 + pad)
            reg = rgb[y0:y1, x0:x1].astype(np.float32) / 255.0
            if reg.size:
                vals.append(reg @ np.float32([0.2126, 0.7152, 0.0722]))
        if not vals:
            return None
        y = np.concatenate([v.ravel() for v in vals])
        return float(y.mean()), float(np.percentile(y, 90))

    def decide(self, plan, stats, state_in):
        """Ground per frame from the luminance under the text, with hysteresis (PAPER_ON / NIGHT_ON); runs shorter than
        MIN_RUN frames (flashes, rubbing flips, mis-registration) are absorbed, so the look switches hard and only where
        the picture itself jumps (cuts). Hysteresis carries across units of the same world class only.
        Returns {'runs': [[f_from, f_to, ground, wash]], 'ground': state out, ...}."""
        f0 = plan['shot']['in_frame']
        raw = []                                         # (frame, ground, mean, p90)
        state = state_in
        prev_class = None
        for u in plan['units']:
            forced = plan['place'][u['id']].get('ground')
            cls = world_class(u['world'])
            if prev_class is not None and cls != prev_class:
                state = None
            prev_class = cls
            for f in range(u['in_frame'], u['out_frame']):
                st = stats[f - f0]
                if st is None:
                    continue
                m, p90 = st
                if forced:
                    g = forced
                elif m >= PAPER_ON:
                    g = 'paper'
                elif m <= NIGHT_ON:
                    g = 'night'
                else:
                    g = state or ('paper' if m >= (PAPER_ON + NIGHT_ON) / 2 else 'night')
                state = g
                raw.append([f, g, m, p90, u['id']])
        if not raw:
            return {'runs': [], 'ground': state_in}
        runs = []                                        # [f_from, f_to, ground, [p90...], [mean...], unit]
        for f, g, m, p90, uid in raw:
            if runs and runs[-1][2] == g and runs[-1][1] == f and runs[-1][5] == uid:
                runs[-1][1] = f + 1
                runs[-1][3].append(p90)
                runs[-1][4].append(m)
            else:
                runs.append([f, f + 1, g, [p90], [m], uid])
        changed = True
        while changed and len(runs) > 1:                 # absorb short runs into their longer neighbour (same unit)
            changed = False
            for k, r in enumerate(runs):
                if r[1] - r[0] >= MIN_RUN:
                    continue
                nb = [j for j in (k - 1, k + 1) if 0 <= j < len(runs) and runs[j][5] == r[5]]
                if not nb:
                    continue
                j = max(nb, key=lambda j: runs[j][1] - runs[j][0])
                a, b = sorted((k, j))
                merged = [runs[a][0], runs[b][1], runs[j][2], runs[a][3] + runs[b][3], runs[a][4] + runs[b][4], r[5]]
                runs[a:b + 1] = [merged]
                changed = True
                break
        out = []
        for a, b, g, p90s, ms, uid in runs:
            wash = float(np.clip(WASH_MIN + WASH_GAIN * (float(np.median(p90s)) - WASH_FLOOR), WASH_MIN, WASH_MAX))
            out.append([a, b, g, wash if g == 'night' else 0.0, round(float(np.median(ms)), 3)])
        return {'runs': out, 'ground': out[-1][2]}

    # ---- pass 2: paint
    def painter(self, plan, look):
        W, H = self.W, self.H
        ink = 1 - np.float32(INK_RGB)
        cream = np.float32(CREAM_RGB)
        mist_rgb = np.float32(MIST_RGB)
        runs = look['runs']

        def ground_at(f):
            for a, b, g, wash, m in runs:
                if a <= f < b:
                    return g, wash
            if runs:                                     # between runs (no text measured): nearest run
                r = min(runs, key=lambda r: min(abs(f - r[0]), abs(f - r[1])))
                return r[2], r[3]
            return 'night', WASH_MIN

        def paint(im, index):
            f = plan['shot']['in_frame'] + index
            vis = [(l, s) for l, s, a, b, u in plan['items'] if a <= f < b]
            if not vis:
                return im
            g, wash = ground_at(f)
            arr = np.asarray(im, np.float32) / 255.0
            arr = arr.copy()
            for l, s in vis:
                a = s.alpha(f)
                if not a.any():
                    continue
                x0, y0 = s.x0, s.y0
                fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + s.bw), min(H, y0 + s.bh)
                if fx1 <= fx0 or fy1 <= fy0:
                    continue
                sl = (slice(fy0 - y0, fy1 - y0), slice(fx0 - x0, fx1 - x0))
                reg = arr[fy0:fy1, fx0:fx1]
                a = a[sl]
                if g == 'paper':
                    mist = float(s.place.get('mist', 0.0))
                    if mist > 0:                          # bare paper (mist) behind the line, feathered
                        mk = (mist * s.wash[sl])[..., None]
                        reg[:] = reg + (mist_rgb - reg) * mk
                    k = (a * INK_OPACITY * s.grain[sl])[..., None]
                    reg *= 1 - k * ink
                else:
                    wk = wash * s.wash[sl][..., None]
                    reg *= 1 - wk
                    k = (a * CREAM_OPACITY)[..., None]
                    reg[:] = reg * (1 - k) + cream * k
            return Image.fromarray(np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8))

        return paint


def code_hash():
    return hashlib.sha256(Path(__file__).read_bytes() + TIMING.read_bytes()).hexdigest()[:16]

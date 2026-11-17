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
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FPS = 24
TIMING = ROOT / 'analysis/timing.json'

# ------------------------------------------------------------------------------------------------ what is shown
# Never shown: the parenthetical echoes, "(ps ps ps)" (never subtitled: a rule of the film), and the two 一通百通 lines
# (art inscriptions in the picture, D4/D5 and J5). Everything else in `lines` is shown, "Monkey!" and "Yes" included.
HIDE_PARENTHESES = True
HIDE_TEXTS = {'一通百通'}
# The rap (107.04-121.47): the Chinese line with the brainstorm's working English beneath it, smaller.
RAP_RANGE = (107.0, 121.47)
RAP_ENGLISH = {
    '石头里蹦出来 没有童年': 'Popped out of a stone, no childhood',
    '一声耳语 学会七十二变': 'One whisper, and I learned the seventy-two changes',
    '拔一把毫毛 吹一口气': 'Pluck a handful of hairs, blow one breath',
    '千百个我 同时在这里': 'Hundreds of me, here at the same time',
    '每一个都是我 每一个都算': 'Every one is me, every one counts',
    '说完这句话 各自消散': 'Say this line, and each one scatters',
    '身外身法 谁是真身': 'The body-beyond-the-body spell: which one is real?',
    '问了也白问 个个都真': 'No use asking: every one is real',
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
RAP_EN_SCALE = 0.80          # the working English under a rap line, relative to LATIN_PX
LEADING = 1.28               # baseline-to-baseline distance, in the row's px
RAP_LEADING = 1.55           # from a rap line's last Chinese row to its English row, in the English row's px
BASELINE_Y = 0.86            # baseline of the LAST row, fraction of frame height (lower third)
WRAP_FRAC = 0.62             # wider than this fraction of the frame -> two balanced rows
SAFE_ASPECT = 4 / 5          # the centred 4:5 safe area (vertical crop) ...
SAFE_PAD = 0.03              # ... minus this fraction of its width on each side
MIN_SCALE = 0.80             # if two rows still do not fit, shrink down to this, never below
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
NIGHT_ON = 0.38                    # below this: night (cream text + wash); in between: keep the previous shot's ground

# ------------------------------------------------------------------------------------------------ timing
REVEAL = (0.70, 1.0)               # a word's opacity on its onset frame and the next (no fade longer than 2 frames)
CLEAR_AFTER = 6                    # frames after the line's end time (or when the next line starts, if sooner)
MIN_SEGMENT = 4                    # a line that would show for fewer frames before a cut starts at the cut instead
ROOM_WORLDS = {'attic88', 'car26', 'bed26'}     # room <-> book/stage (book, stage, blank): a line never crosses

# ------------------------------------------------------------------------------------------------ placement
# x: anchor (fraction of width), align: 'c' | 'l' | 'r', y: baseline of the last row, scale: size, maxw: max row width
# (fraction of width; default: the 4:5 safe area), ground: force 'paper' | 'night'.
DEFAULT = dict(x=0.5, align='c', y=BASELINE_Y, scale=1.0, maxw=None, ground=None)
OVERRIDES = {
    # filled in by the lyric pass after checking every shot's sheet with lyrics on (docs/QA_PREVIEW_V2.md)
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
        best = None
        for i, ch in enumerate(text):                     # two balanced rows, broken at a space
            if ch != ' ':
                continue
            s1, w1 = self._segments(text, tok_of, px, italic, 0, i)
            s2, w2 = self._segments(text, tok_of, px, italic, i + 1, len(text))
            score = max(w1, w2) / max(w1 + w2, 1)
            if text[i - 1] in ',?!;:，':
                score -= COMMA_BONUS
            if best is None or score < best[0]:
                best = (score, [(s1, px, w1), (s2, px, w2)])
        return best[1] if best else [(segs, px, w)]

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
    def __init__(self, shots, W, H, overrides=None, timing=TIMING):
        self.shots = shots
        self.W, self.H = W, H
        self.lines = load_lines(timing)
        self.over = OVERRIDES if overrides is None else overrides
        self._settings = {}
        self._fix_clears()

    def place(self, sid):
        p = dict(DEFAULT)
        p.update(self.over.get(sid, {}))
        return p

    def setting(self, line, sid):
        p = self.place(sid)
        key = (line.idx, json.dumps(p, sort_keys=True))
        if key not in self._settings:
            self._settings[key] = Setting(line, p, self.W, self.H)
        return self._settings[key]

    # ---- schedule
    def segments(self, line):
        """[(shot_index, f_from, f_to)] where the line shows (absolute frames), after the cut rules."""
        segs = []
        f, end = line.first, line.clear
        idx = {s['id']: i for i, s in enumerate(self.shots)}
        order = self.shots
        # shot containing f
        def shot_at(fr):
            for i, s in enumerate(order):
                if s['in_frame'] <= fr < s['out_frame']:
                    return i
            return None
        i = shot_at(f)
        while i is not None and f < end:
            s = order[i]
            to = min(end, s['out_frame'])
            nxt = order[i + 1] if i + 1 < len(order) else None
            if nxt is not None and to == s['out_frame'] and end > to and (to - f) < MIN_SEGMENT:
                f, i = to, i + 1                              # too short before the cut: start at the cut
                continue
            segs.append((i, f, to))
            if nxt is None or to >= end:
                break
            if world_class(nxt['world']) != world_class(s['world']):
                later = [tk[2] for tk in line.tokens if tk[2] >= to]
                if not later or later[0] >= end:
                    break                                     # nothing left to sing in the new world
                f = later[0]                                  # re-appear on the next word in the new world
                i = shot_at(f)
                continue
            f, i = to, i + 1
        return segs

    def _fix_clears(self):
        """A line clears when the next line actually shows (after the cut rules), never later than its own end + 6."""
        if getattr(self, '_fixed', False):
            return
        self._fixed = True
        starts = []
        for line in self.lines:
            segs = self.segments(line)
            starts.append(segs[0][1] if segs else line.first)
        for k, line in enumerate(self.lines[:-1]):
            own = frame_floor(line.end) + CLEAR_AFTER
            line.clear = min(own, max(line.clear, starts[k + 1]))

    def plan(self, shot):
        """Items for one shot: [(line, setting, f_from, f_to)] in absolute frames; None if nothing shows."""
        items = []
        for line in self.lines:
            if line.clear <= shot['in_frame'] or line.first >= shot['out_frame'] + 48:
                continue
            for i, a, b in self.segments(line):
                if self.shots[i]['id'] == shot['id']:
                    items.append((line, self.setting(line, shot['id']), a, b))
        return {'shot': shot, 'items': items, 'place': self.place(shot['id'])} if items else None

    def signature(self, plan, state_in):
        if plan is None:
            return None
        return hashlib.sha256(json.dumps({
            'items': [(l.idx, l.text, l.english, l.tokens, a, b) for l, s, a, b in plan['items']],
            'place': plan['place'], 'state_in': state_in}, sort_keys=True).encode()).hexdigest()[:16]

    # ---- pass 1: measure
    def visible(self, plan, index):
        f = plan['shot']['in_frame'] + index
        return [(l, s) for l, s, a, b in plan['items'] if a <= f < b]

    def measure(self, plan, rgb, index):
        """rgb: HxWx3 uint8. Returns (mean luma, p90 luma) under the visible text's box, or None."""
        vis = self.visible(plan, index)
        if not vis:
            return None
        vals = []
        for l, s in vis:
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
        """One look per shot: ground with hysteresis against the previous shot; wash strength for night."""
        stats = [s for s in stats if s is not None]
        forced = plan['place'].get('ground')
        mean = float(np.median([s[0] for s in stats])) if stats else 0.0
        p90 = float(np.median([s[1] for s in stats])) if stats else 0.0
        if forced:
            ground = forced
        elif mean >= PAPER_ON:
            ground = 'paper'
        elif mean <= NIGHT_ON:
            ground = 'night'
        else:
            ground = state_in or ('paper' if mean >= (PAPER_ON + NIGHT_ON) / 2 else 'night')
        wash = float(np.clip(WASH_MIN + WASH_GAIN * (p90 - WASH_FLOOR), WASH_MIN, WASH_MAX))
        return {'ground': ground, 'wash': wash if ground == 'night' else 0.0, 'mean': mean, 'p90': p90}

    # ---- pass 2: paint
    def painter(self, plan, look):
        W, H = self.W, self.H
        ink = 1 - np.float32(INK_RGB)
        cream = np.float32(CREAM_RGB)

        def paint(im, index):
            f = plan['shot']['in_frame'] + index
            vis = [(l, s) for l, s, a, b in plan['items'] if a <= f < b]
            if not vis:
                return im
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
                if look['ground'] == 'paper':
                    k = (a * INK_OPACITY * s.grain[sl])[..., None]
                    reg *= 1 - k * ink
                else:
                    wk = look['wash'] * s.wash[sl][..., None]
                    reg *= 1 - wk
                    k = (a * CREAM_OPACITY)[..., None]
                    reg[:] = reg * (1 - k) + cream * k
            return Image.fromarray(np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8))

        return paint


def code_hash():
    return hashlib.sha256(Path(__file__).read_bytes() + TIMING.read_bytes()).hexdigest()[:16]

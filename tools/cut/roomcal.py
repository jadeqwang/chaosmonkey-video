"""Room calligraphy (REVISION_V4 §1.3): the Chinese of every sung line, laid at assembly as an overlay on the comps.

    from roomcal import RoomCal
    cal = RoomCal(all_shots, W, H)              # all_shots: docs/shots.json 'shots'; W x H: output size
    plan = cal.plan(shot)                       # rows that show in this shot (None: nothing)
    paint = cal.painter(plan)                   # paint(PIL image, index) -> PIL image (in place on the laid frame)

The same typeset brush hand as the page inscriptions (tools/ink/inscription.py: Ma Shan Zheng, dry-brush 飞白, columns
top to bottom, right to left, one small cinnabar seal 悟空 under the foot of the last column), but light on dark: warm
paper-white, slightly transparent, a soft edge, and a faint dark halo only where a row asks for it. Present for the whole
sung line; the only motion is a FADE-frame fade in (on the line's first word) and out (after its last); at a cut inside
the line it switches with the picture. Never drawn by a model.

Data: text from design/text/lyrics_zh_v4.txt (key -> columns), placement from design/text/roomcal_v4.tsv (one row per
unit and sung line: key, region, side). A proofreading change to the text is a re-render: nothing is baked into a comp.
Size: PX_540 at 960x540 for every room shot, scaled with the output height (1080p = 2 x); a text that no longer fits its
region is reported, never shrunk.

    python tools/cut/roomcal.py --proof          # every row on its unit's frames (first/middle/last of its window)
    python tools/cut/roomcal.py --check          # collisions: calligraphy vs the English lyric layer, per frame
"""
import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/cut'))
from tools.ink.inscription import Inscribed, table as zh_table, COL_PITCH, ROW_PITCH   # noqa: E402
from tools.ink.core import ink_T                                                       # noqa: E402
import lyrics as lyric_layer                                                            # noqa: E402

FPS = 24
TEXT_FILE = 'design/text/lyrics_zh_v4.txt'
TABLE_FILE = ROOT / 'design/text/roomcal_v4.tsv'
TIMING = lyric_layer.TIMING

# ------------------------------------------------------------------------------------------------ the look (one place)
PX_540 = 26                          # character size at 960x540 (1080p: 52) in every ROOM row (ground dark)
PX_PAGE_540 = 30                     # ground 'paper' rows (album/page shots in ink) = the page inscriptions' size (lead, 19 Nov)
SEAL_FRAC = 0.70                     # seal side / character size (the page inscriptions use 0.86)
SEAL_STYLE = 'bai'                   # 白文 (red block, bare characters): at 18 px a 朱文 seal reads as an empty red frame
PAPER_WHITE = (0.945, 0.910, 0.820)  # warm paper-white
OPACITY = 0.92                       # slightly transparent (x the brush density ~0.8-0.95)
SOFT_540 = 0.45                      # soft edge: Gaussian sigma in px at 540p
DRY = 0.35                           # 飞白 amount (inscriptions 0.5: a little less, light strokes starve visibly anyway)
HALO_SIGMA_540 = 4.0                 # the faint dark halo (only rows with halo > 0): sigma at 540p ...
HALO_GROW_540 = 2                    # ... grown this many px first
SEAL_OPACITY = 0.88
FADE = 6                             # frames
SEED = 4                             # one seed for the hand (per row it is mixed with the key)
INK_OPACITY_PAPER = 1.0              # ground 'paper' rows (album / page shots without an inscription): ink, multiplied


def _f(t):
    return lyric_layer.frame_floor(t)


def load_rows(path=TABLE_FILE):
    """Rows of the placement table (tab-separated; '#' lines are comments)."""
    rows = []
    with open(path, encoding='utf-8') as fh:
        lines = [l for l in fh if l.strip() and not l.startswith('#')]
    for r in csv.DictReader(lines, delimiter='\t'):
        r = {k.strip(): (v or '').strip() for k, v in r.items()}
        r['line'] = int(r['line'])
        for k in ('x', 'y', 'w', 'h'):
            r[k] = float(r[k])
        r['halo'] = float(r.get('halo') or 0)
        r['ground'] = r.get('ground') or 'dark'
        r['f0'] = int(r['f0']) if r.get('f0') else None
        r['f1'] = int(r['f1']) if r.get('f1') else None
        r['cols'] = [int(c) for c in r['cols'].split(',')] if r.get('cols') else None
        rows.append(r)
    return rows


def block_size(cols, px, seal=True):
    """(w, h) of a set of columns at character size px (the inscription's metrics)."""
    w = (len(cols) - 1) * COL_PITCH * px + px
    h = max(len(c) for c in cols) * ROW_PITCH * px + (px * SEAL_FRAC * 1.25 if seal else 0)
    return w, h


class _Arr:
    """A seal array that Inscribed accepts (it tests `if seal`, which an ndarray refuses)."""
    def __init__(self, a):
        self.a = a

    def __bool__(self):
        return True

    def __array__(self, dtype=None, copy=None):
        return self.a if dtype is None else self.a.astype(dtype)


class Setting:
    """One row laid out at one output size: a straight-alpha RGBA patch (text, halo, seal) and its frame position."""

    def __init__(self, row, cols, W, H):
        s = H / 540.0
        px = (PX_PAGE_540 if row['ground'] == 'paper' else PX_540) * s
        self.row, self.cols, self.W, self.H, self.px = row, cols, W, H, px
        bw, bh = block_size(cols, px)
        rx, ry, rw, rh = row['x'] * s, row['y'] * s, row['w'] * s, row['h'] * s
        self.fits = bw <= rw + 0.5 and bh <= rh + 0.5
        side = row['side'].upper()[:1]
        if side == 'L':
            bx = rx
        elif side == 'R':
            bx = rx + rw - bw
        else:
            bx = rx + (rw - bw) / 2
        by = ry
        seed = int(hashlib.md5(f"{SEED}:{row['key']}".encode()).hexdigest()[:6], 16)
        from tools.ink.seal import seal as _seal
        from tools.ink.inscription import SEAL_FONT
        sl = _seal('悟空', SEAL_FONT, size=int(round(px * SEAL_FRAC)), style=SEAL_STYLE, wear=0.15, seed=seed % 97)
        ins = Inscribed((W, H), cols, (bx, by, bw, bh), px, seal=_Arr(sl), seed=seed, ground='dark', dry=DRY,
                        seal_px=int(round(px * SEAL_FRAC)))
        self.ground = row['ground']
        D = np.clip(ins.D, 0, 1.2)
        x0, y0, w0, h0 = ins.box
        g = int(math.ceil(HALO_SIGMA_540 * s * 3 + HALO_GROW_540 * s)) + 2
        X0, Y0 = x0 - g, y0 - g
        Wp, Hp = w0 + 2 * g, h0 + 2 * g
        Dp = np.zeros((Hp, Wp), np.float32)
        Dp[g:g + h0, g:g + w0] = D
        if ins.seal is not None:                         # extend the patch to hold the seal
            sx, sy = ins.seal_pos
            sh, sw = ins.seal.shape[:2]
            ex0, ey0 = min(X0, sx - 2), min(Y0, sy - 2)
            ex1, ey1 = max(X0 + Wp, sx + sw + 2), max(Y0 + Hp, sy + sh + 2)
            big = np.zeros((ey1 - ey0, ex1 - ex0), np.float32)
            big[Y0 - ey0:Y0 - ey0 + Hp, X0 - ex0:X0 - ex0 + Wp] = Dp
            Dp, X0, Y0 = big, ex0, ey0
            Hp, Wp = Dp.shape
        self.x0, self.y0, self.pw, self.ph = int(X0), int(Y0), int(Wp), int(Hp)
        if self.ground == 'paper':
            self.T = ink_T(np.clip(Dp, 0, 1.2))               # ink, multiplied (as an inscription)
            self.text_a = None
        else:
            a = np.clip(Dp, 0, 1) * OPACITY
            a = cv2.GaussianBlur(a, (0, 0), SOFT_540 * s)      # the soft edge
            self.text_a = a.astype(np.float32)
            halo = float(row.get('halo') or 0)
            if halo > 0:
                k = max(1, int(round(HALO_GROW_540 * s)))
                m = cv2.dilate((Dp > 0.08).astype(np.float32), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1,) * 2))
                m = cv2.GaussianBlur(m, (0, 0), HALO_SIGMA_540 * s)
                self.halo_a = (halo * m / max(float(m.max()), 1e-6)).astype(np.float32)
            else:
                self.halo_a = None
        self.seal = None
        if ins.seal is not None:
            sx, sy = ins.seal_pos
            self.seal = (ins.seal.astype(np.float32), int(sx) - self.x0, int(sy) - self.y0)
        ys, xs = np.nonzero(Dp > 0.05)
        bb = [self.x0 + int(xs.min()), self.y0 + int(ys.min()), self.x0 + int(xs.max()) + 1, self.y0 + int(ys.max()) + 1]
        if self.seal is not None:
            sr, sx, sy = self.seal
            bb = [min(bb[0], self.x0 + sx), min(bb[1], self.y0 + sy), max(bb[2], self.x0 + sx + sr.shape[1]),
                  max(bb[3], self.y0 + sy + sr.shape[0])]
        self.bbox = tuple(bb)                                  # ink + seal, frame px

    def paint(self, arr, k):
        """arr: HxWx3 float32 0..1 (modified in place); k: opacity 0..1 (the fade)."""
        if k <= 0:
            return arr
        H, W = arr.shape[:2]
        x0, y0 = self.x0, self.y0
        fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + self.pw), min(H, y0 + self.ph)
        if fx1 <= fx0 or fy1 <= fy0:
            return arr
        sl = (slice(fy0 - y0, fy1 - y0), slice(fx0 - x0, fx1 - x0))
        reg = arr[fy0:fy1, fx0:fx1]
        if self.ground == 'paper':
            t = self.T[sl]
            reg *= 1.0 - (1.0 - t) * (k * INK_OPACITY_PAPER)
        else:
            if self.halo_a is not None:
                reg *= (1.0 - k * self.halo_a[sl])[..., None]
            a = (k * self.text_a[sl])[..., None]
            reg[:] = reg * (1 - a) + np.float32(PAPER_WHITE) * a
        if self.seal is not None:
            sr, sx, sy = self.seal
            h, w = sr.shape[:2]
            ax0, ay0 = x0 + sx, y0 + sy
            bx0, by0, bx1, by1 = max(0, ax0), max(0, ay0), min(W, ax0 + w), min(H, ay0 + h)
            if bx1 > bx0 and by1 > by0:
                s = sr[by0 - ay0:by1 - ay0, bx0 - ax0:bx1 - ax0]
                a = s[..., 3:4] * (k * SEAL_OPACITY)
                arr[by0:by1, bx0:bx1] = arr[by0:by1, bx0:bx1] * (1 - a) + s[..., :3] * a
        return arr


class RoomCal:
    def __init__(self, shots, W, H, timing=TIMING, rows=None, text=TEXT_FILE):
        self.W, self.H = W, H
        self.shots = shots
        self.text = zh_table(text)
        self.rows = load_rows() if rows is None else rows
        lines = {l.idx: l for l in lyric_layer.load_lines(timing)}
        allrecs = json.loads(Path(timing).read_text())['lines']
        self.units = {}
        for sh in shots:
            parts = lyric_layer.PARTS.get(sh['id'], [(sh['id'], sh['in_frame'], sh['world'])])
            for k, (uid, f0, world) in enumerate(parts):
                f1 = parts[k + 1][1] if k + 1 < len(parts) else sh['out_frame']
                self.units[uid] = {'id': uid, 'shot': sh['id'], 'in_frame': f0, 'out_frame': f1, 'world': world}
        self.items = []
        problems = []
        for r in self.rows:
            u = self.units.get(r['unit'])
            if u is None:
                problems.append(f"row {r['unit']}:{r['line']}: no such unit"); continue
            if r['key'] not in self.text:
                problems.append(f"row {r['unit']}:{r['line']}: key {r['key']} not in {text}"); continue
            rec = allrecs[r['line']]
            first = lines[r['line']].first if r['line'] in lines else _f(rec['start'])
            clear = _f(rec['end']) + FADE
            a, b = max(first, u['in_frame']), min(clear, u['out_frame'])
            if r['f0'] is not None:
                a = r['f0']
            if r['f1'] is not None:
                b = r['f1']
            cols = self.text[r['key']]['columns']
            if r['cols']:
                cols = [cols[i] for i in r['cols']]
            self.items.append(dict(row=r, unit=u, cols=cols, a=a, b=b))
        # a row clears when the next row in the same unit begins, if sooner (no two texts at once in one unit)
        by_unit = {}
        for it in self.items:
            by_unit.setdefault(it['unit']['id'], []).append(it)
        for its in by_unit.values():
            its.sort(key=lambda it: it['a'])
            for p, q in zip(its, its[1:]):
                if p['b'] > q['a']:
                    p['b'] = q['a']
        # fades: in and out everywhere, except where the same line carries straight on across a cut (then it switches
        # with the picture, like a held subtitle)
        for it in self.items:
            same = [o for o in self.items if o is not it and o['row']['line'] == it['row']['line']]
            it['fade_in'] = not any(o['b'] == it['a'] for o in same)
            it['fade_out'] = not any(o['a'] == it['b'] for o in same)
        self.problems = problems
        self._settings = {}

    def setting(self, it):
        r = it['row']
        key = (r['unit'], r['line'], r['key'], tuple(it['cols']), r['x'], r['y'], r['w'], r['h'], r['side'], r['ground'], r['halo'])
        if key not in self._settings:
            st = Setting(it['row'], it['cols'], self.W, self.H)
            if not st.fits:
                print(f"roomcal: {it['row']['unit']}:{it['row']['line']} {it['cols']} does not fit its region "
                      f"{it['row']['x'], it['row']['y'], it['row']['w'], it['row']['h']} (not shrunk)")
            self._settings[key] = st
        return self._settings[key]

    def opacity(self, it, f):
        if not (it['a'] <= f < it['b']):
            return 0.0
        k = 1.0
        if it['fade_in']:
            k = min(k, (f - it['a'] + 1) / FADE)
        if it['fade_out']:
            k = min(k, (it['b'] - f) / FADE)
        return max(0.0, min(1.0, k))

    def plan(self, shot):
        its = [it for it in self.items if it['unit']['shot'] == shot['id'] and it['b'] > it['a']]
        return {'shot': shot, 'items': its} if its else None

    def signature(self, plan):
        if plan is None:
            return None
        return hashlib.sha256(json.dumps([(it['row'], it['cols'], it['a'], it['b'], it['fade_in'], it['fade_out'])
                                          for it in plan['items']], sort_keys=True, default=str).encode()).hexdigest()[:16]

    def painter(self, plan):
        sets = [(it, self.setting(it)) for it in plan['items']]
        f0 = plan['shot']['in_frame']

        def paint(im, index):
            f = f0 + index
            vis = [(it, st, self.opacity(it, f)) for it, st in sets]
            vis = [v for v in vis if v[2] > 0]
            if not vis:
                return im
            arr = np.asarray(im, np.float32) / 255.0
            arr = arr.copy()
            for it, st, k in vis:
                st.paint(arr, k)
            return Image.fromarray(np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8))
        return paint

    def boxes_at(self, f):
        """[(unit:line, bbox)] of calligraphy visible on song frame f (for collision checks)."""
        out = []
        for it in self.items:
            if it['a'] <= f < it['b']:
                out.append((f"{it['row']['unit']}:{it['row']['line']}", self.setting(it).bbox))
        return out


def code_hash():
    h = hashlib.sha256(Path(__file__).read_bytes() + (ROOT / TEXT_FILE).read_bytes() + TABLE_FILE.read_bytes())
    for p in ('tools/ink/inscription.py', 'tools/ink/seal.py', 'tools/ink/core.py'):
        h.update((ROOT / p).read_bytes())
    return h.hexdigest()[:16]


# ------------------------------------------------------------------------------------------------ proof and checks
def _source_for(unit_shot, picks):
    if unit_shot in picks:
        p = Path(picks[unit_shot]['src'])
        return (p if p.is_absolute() else ROOT / p), float(picks[unit_shot].get('in', 0))
    return ROOT / f'media/comp/{unit_shot}.mp4', 0.0


def _frame(path, idx):
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap.read()
    cap.release()
    if not ok:
        return None
    return cv2.cvtColor(cv2.resize(fr, (960, 540), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)


def proof(out_dir, picks_path, only=None):
    shots = json.load(open(ROOT / 'docs/shots.json'))['shots']
    byid = {s['id']: s for s in shots}
    picks = json.load(open(picks_path)) if Path(picks_path).exists() else {}
    cal = RoomCal(shots, 960, 540)
    for p in cal.problems:
        print('PROBLEM', p)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tiles = []
    for it in cal.items:
        if only and it['row']['unit'] not in only:
            continue
        st = cal.setting(it)
        sh = byid[it['unit']['shot']]
        src, off = _source_for(sh['id'], picks)
        a, b = it['a'], it['b']
        fr_list = [a + min(FADE, max(0, b - a - 1)), (a + b) // 2, max(a, b - FADE - 1)]
        row = []
        for f in fr_list:
            idx = f - sh['in_frame'] + int(round(off * FPS))
            img = _frame(src, idx)
            if img is None:
                img = np.zeros((540, 960, 3), np.uint8)
            arr = img.astype(np.float32) / 255.0
            st.paint(arr, cal.opacity(it, f))
            im = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
            x0, y0, x1, y1 = st.bbox
            cv2.rectangle(im, (x0 - 1, y0 - 1), (x1, y1), (90, 200, 255), 1)
            r = it['row']
            cv2.rectangle(im, (int(r['x']), int(r['y'])), (int(r['x'] + r['w']), int(r['y'] + r['h'])), (255, 120, 60), 1)
            cv2.putText(im, f"{r['unit']} L{r['line']} {r['key']} f{f} {r.get('status','')}", (8, 530),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
            row.append(im)
        strip = np.hstack(row)
        name = f"{r['unit']}_L{r['line']:02d}" + (f"_f{r['f0']}" if r['f0'] is not None else '') + '.jpg'
        cv2.imwrite(str(out_dir / name), cv2.cvtColor(strip, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        tiles.append(name)
        print(f"{r['unit']}:{r['line']} {it['cols']} frames {a}-{b} fits={st.fits} bbox={st.bbox} -> {name}")
    return tiles


def check(lyrics_on=True):
    """Per frame: calligraphy boxes vs the English lyric layer's ink boxes (both at 960x540). Prints collisions."""
    shots = json.load(open(ROOT / 'docs/shots.json'))['shots']
    cal = RoomCal(shots, 960, 540)
    lay = lyric_layer.LyricLayer(shots, 960, 540)
    hits = {}
    end = shots[-1]['out_frame']
    for f in range(end):
        cb = cal.boxes_at(f)
        if not cb:
            continue
        u = lay._unit_at(f)
        for line in lay.lines:
            for i, a, b in lay.segments(line):
                if a <= f < b:
                    st = lay.setting(line, lay.units[i]['id'])
                    lx0, ly0, lx1, ly1 = st.ink_box
                    pad = 6
                    for name, (x0, y0, x1, y1) in cb:
                        if lx0 - pad < x1 and x0 < lx1 + pad and ly0 - pad < y1 and y0 < ly1 + pad:
                            hits.setdefault((name, lay.units[i]['id'], line.idx), []).append(f)
    for (name, uid, li), fs in sorted(hits.items()):
        print(f'COLLISION calligraphy {name} x lyric line {li} in {uid}: frames {fs[0]}-{fs[-1]} ({len(fs)})')
    print(f'{len(hits)} collisions')
    return hits


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--proof', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--only')
    ap.add_argument('--out', default=str(ROOT / 'work/cut/roomcal_proof'))
    ap.add_argument('--picks', default=str(ROOT / 'docs/picks_v4.json'))
    a = ap.parse_args()
    if a.proof:
        proof(a.out, a.picks, set(a.only.split(',')) if a.only else None)
    if a.check:
        check()

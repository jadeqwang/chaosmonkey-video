"""shots/_tong.py: 一窍通时百窍通 (REVISION_V3 §3.2): generalization on the carved cliff. Shared by D4, D5 (and J2/J5).

The light does not spread to neighbours. It JUMPS between carved characters that share a component, using the real
decomposition (IDS, cjkvi-ids `refs/data/cjkvi-ids/ids.txt`) of the 千字文 characters actually carved:
通 -> every character with 辶 -> each of those passes it on through its OTHER components -> ... Each jump is drawn
as a fine gold thread for a few frames, like the lines of an old star chart.
"""
import collections
import json
import re

import cv2
import numpy as np

from shots._mountain import *

IDC = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻')
# strokes and scraps that are not a component anyone would recognise
DENY = set('⺀𫝀龶𠂇一丿丶丨亅乚乙𠃌𠂊二八丷亠冂冖厶䒑儿コ十人入凵匚冫丆𠂉𠂆乛⺊卜丄丅𠄌㇀㇏①②③④⑤⑥⑦⑧⑨⑩')
THREAD = np.array([0.80, 0.56, 0.13], np.float32)


def ids_table():
    ids = {}
    for l in open(ROOT / 'refs/data/cjkvi-ids/ids.txt', encoding='utf-8'):
        if l.startswith('#') or '\t' not in l:
            continue
        p = l.rstrip('\n').split('\t')
        if len(p) >= 3:
            ids[p[1]] = re.sub(r'\[[^\]]*\]', '', p[2])
    return ids


def components(chars):
    """{char: set of recognisable components (two levels of IDS)} for the given characters."""
    ids = ids_table()

    def comps(ch, depth=0):
        out = set()
        for c in ids.get(ch, ch):
            if c in IDC or c == ch:
                continue
            if c not in DENY and ord(c) > 0x2E7F:
                out.add(c)
            if depth < 1 and c in ids and ids[c] != c:
                out |= comps(c, depth + 1)
        return out
    return {ch: comps(ch) for ch in chars}


def chain(chars, start='通', first='辶', per_jump=3, gens=9, seed=2, pos=None):
    """Generations of true jumps. Returns [[(src, dst, component), ...] per generation]. Generation 1 = every carved
    character sharing `first` with `start`; after that each newly lit character passes the light on through its
    other components to at most `per_jump` unlit characters per component (the farthest first when `pos` is given,
    so the threads cross the mountain); the last generations are unlimited."""
    C = components(chars)
    inv = collections.defaultdict(list)
    for ch in chars:
        for c in C[ch]:
            inv[c].append(ch)
    r = np.random.default_rng(seed)
    lit = {start: None}
    out = [[(start, d, first) for d in inv[first] if d != start]]
    for s, d, c in out[0]:
        lit[d] = c
    frontier = [d for _, d, _ in out[0]]
    for g in range(2, gens + 1):
        new, cap = [], (per_jump if g <= 5 else 99)
        for s in frontier:
            for c in sorted(C[s]):
                if c == lit[s] or len(inv[c]) < 2:
                    continue
                cand = [d for d in inv[c] if d not in lit]
                if pos is not None:
                    cand.sort(key=lambda d: -((pos[d][0] - pos[s][0]) ** 2 + (pos[d][1] - pos[s][1]) ** 2))
                    cand = cand[:cap * 2]
                r.shuffle(cand)
                for d in cand[:cap]:
                    lit[d] = c
                    new.append((s, d, c))
        if not new:
            break
        out.append(new)
        frontier = [d for _, d, _ in new]
    return out


def build_mid(seed=6, size=105):
    """The carved cliff at mid distance (the v3 plate with the ladders painted out), 千字文 1-160 in columns."""
    raw = load_image(B + 'B_cliff_mid_v3_bare.jpg')
    H, W = raw.shape[:2]
    paper = Paper(W, H, 'new', seed=BOOK_PAPER_SEED)
    T = key_paper(raw, lo=0.03)
    rock = paper.rgb * T
    d = (1 - T.min(axis=2) > 0.03).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (161, 161))
    sil = cv2.morphologyEx(d, cv2.MORPH_CLOSE, k)
    cs, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sil[:] = 0
    cv2.drawContours(sil, [max(cs, key=cv2.contourArea)], -1, 1, -1)
    sil = cv2.erode(sil, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (141, 141)))
    ys, xs = np.nonzero(sil)
    region = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min()), int(min(ys.max(), H - 40) - ys.min()))
    C = Cliff(rock, qianziwen(160), SEAL_FONT, size=size, region=region, seed=seed, weather=0.22, presence='plane',
              uncarved=(1 - sil).astype(np.float32), weight=0.02, paint=0.6, depth=1.2, col_gap=0.34)
    cells = {c[0]: (c[1], c[2]) for c in C.cells}
    return C, cells, paper


def set_lit(C, cells, t_lit, t_base, t_span, size):
    """Give the Cliff's gold a per-character arrival: character ch turns to gold at song time t_lit[ch].
    Then render with gold=progress(t) from `progress`."""
    A = np.full((C.H, C.W), 9.0, np.float32)
    h = int(size * 0.62)
    for ch, (cx, cy) in cells.items():
        if ch in t_lit:
            A[int(cy) - h:int(cy) + h, int(cx) - h:int(cx) + h] = (t_lit[ch] - t_base) / t_span
    C.gold_mask(0.5, 0.55, order='rtl')                         # builds the cache, then we replace the arrival
    C._gold_cache = (C._gold_cache[0], A)
    C._leaf_map()


def progress(t, t_base, t_span):
    return max(1e-4, ((on_frame(t) + 1 / 24.0) - t_base) / t_span / 1.04)


GEN_STYLE = [(3.4, 0.80, 0.42), (2.1, 0.50, 0.26), (1.3, 0.35, 0.14)]      # per generation: width px, hold s, resting alpha
UNDER = np.array([0.50, 0.32, 0.06], np.float32)                          # a darker ochre under the gold, for definition
BRIGHT = np.array([0.90, 0.62, 0.10], np.float32)


def threads(frame, t, edges, to_frame, s=1.0, t_end=None, hold=None, rest=None, colour=None, width=None):
    """edges: [(x0, y0, x1, y1, t_on[, generation])] in canvas px. A thread is DRAWN from source to target over 3
    frames, holds, then sinks to a fainter line that stays (the constellation) until t_end, where everything fades.
    First-generation threads are bold, later ones finer (GEN_STYLE); width/hold/rest override."""
    A = np.zeros(frame.shape[:2], np.float32)
    U = np.zeros(frame.shape[:2], np.float32)
    kf = 1.0 if t_end is None else float(1 - smoothstep(t_end, t_end + 0.5, t))
    if kf <= 0:
        return frame
    for e in edges:
        x0, y0, x1, y1, t_on = e[:5]
        gw, gh, gr = GEN_STYLE[min(int(e[5]) if len(e) > 5 else 2, 2)]
        gw, gh, gr = width or gw, hold or gh, rest if rest is not None else gr
        tf = on_frame(t_on)
        if t < tf - 1e-9:
            continue
        age = t - tf
        u = min(1.0, (age + 1 / 24.0) / 0.125)
        a = (1.0 if age < gh else gr + (1 - gr) * max(0.0, 1 - (age - gh) / 0.35)) * kf
        (fx0, fy0), (fx1, fy1) = to_frame(x0, y0), to_frame(x1, y1)
        ex, ey = fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u
        p0, p1 = (int(round(fx0 * 16)), int(round(fy0 * 16))), (int(round(ex * 16)), int(round(ey * 16)))
        w = max(1, int(round(gw * s)))
        cv2.line(U, p0, p1, float(a), w + max(1, int(round(1.6 * s))), cv2.LINE_AA, 4)
        cv2.line(A, p0, p1, float(a), w, cv2.LINE_AA, 4)
        if u < 1.0 or age < 0.2:                                   # the travelling head: a bright bead
            cv2.circle(A, p1, int(round((gw * 1.5 + 2) * s * 16)), float(min(1.0, a + 0.3)), -1, cv2.LINE_AA, 4)
        if u >= 1.0:
            cv2.circle(A, p1, int(round((4.5 + gw) * s * 16)), float(min(1.0, a + 0.2)), max(1, int(round(1.4 * s))), cv2.LINE_AA, 4)
    np.clip(A, 0, 1, out=A)
    np.clip(U, 0, 1, out=U)
    if colour is None:
        frame += (UNDER[None, None] - frame) * (U * 0.55)[..., None]
    frame += ((BRIGHT if colour is None else np.asarray(colour, np.float32))[None, None] - frame) * (A * 0.95)[..., None]
    return frame


def schedule(gens, times, stagger=None):
    """{ch: t_lit}, [(src, dst, t, generation)]. Generation g starts at times[g]; with stagger[g] seconds its jumps
    are dealt one after another across that span (so each is SEEN). A character lights as its thread arrives."""
    t_lit, edges = {}, []
    for g, lst in enumerate(gens):
        tg = times[min(g, len(times) - 1)]
        sp = (stagger[g] if stagger and g < len(stagger) else 0.0) if g < len(times) else 0.0
        for k, (s_, d, c) in enumerate(lst):
            tt = tg + sp * k / max(1, len(lst) - 1)
            t_lit[d] = tt + 0.11
            edges.append((s_, d, tt, g))
    return t_lit, edges


if __name__ == '__main__':
    chars = list(qianziwen(160))
    g = chain(chars)
    tot = 1
    for i, lst in enumerate(g, 1):
        tot += len(lst)
        print(i, len(lst), tot, ' '.join(f'{s}>{d}({c})' for s, d, c in lst[:14]))

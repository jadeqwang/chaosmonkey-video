"""Shared bits of the Chaos Monkey edit pipeline (copied from halys-video): paths, the frame rule, timing.json anchors, timecode, shots/picks loading.

Everything here is pure (no rendering) so build_shots / check_cuts / assemble / contact agree on one definition.
"""
import json
import math
import re
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIMING = ROOT / 'analysis' / 'timing.json'
SHOTS_SRC = ROOT / 'docs' / 'shots_src.yaml'
SHOTS = ROOT / 'docs' / 'shots.json'
PICKS = ROOT / 'docs' / 'picks.json'
SONG = ROOT / 'inputs' / 'Chaos Monkey - reformatted for duet.wav'
FONTS = ROOT / 'design' / 'fonts'
FPS = 24
ONE_FRAME = 1.0 / FPS


def frame_of(t):
    """The timing map's rule (analysis/timing.json conventions.frame24): ceil(t*24), the first 24 fps frame that starts
    at or after t. The 1e-6 guards against float noise turning an exact frame time (e.g. 1.0) into the next frame."""
    return int(math.ceil(t * FPS - 1e-6))


def tc(frame, fps=FPS):
    """HH:MM:SS:FF timecode of a frame index."""
    s, f = divmod(int(frame), fps)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f'{h:02d}:{m:02d}:{s:02d}:{f:02d}'


def load_json(p):
    with open(p) as fh:
        return json.load(fh)


def load_timing():
    return load_json(TIMING)


# ---------------------------------------------------------------------------------------------------------------------
# Anchors. A text spec (from shots_src.yaml) is parsed into a structured reference (stored in shots.json), and the
# structured reference is resolved against timing.json to a time. The checker re-resolves the structured reference, so
# a stale shots.json (timing.json re-analysed, or hand-edited) is caught.

class AnchorError(ValueError):
    pass


def parse_anchor(spec, timing):
    """Text spec -> structured anchor (without the resolved time; resolve_anchor adds it)."""
    tok = shlex.split(spec)
    if not tok:
        raise AnchorError('empty anchor')
    kind = tok[0]
    if kind == 'start' and len(tok) == 1:
        return {'type': 'start'}
    if kind == 'bar' and len(tok) == 2:
        return {'type': 'downbeat', 'bar': int(tok[1])}
    if kind == 'beat' and len(tok) == 2:
        # identify the beat by bar.beat (stable even if the grid is re-fitted by a few ms)
        t = float(tok[1])
        b = min(timing['beats'], key=lambda x: abs(x['t'] - t))
        if abs(b['t'] - t) > 0.1:
            raise AnchorError(f'no beat within 0.1 s of {t} (nearest {b["t"]})')
        return {'type': 'beat', 'bar': b['bar'], 'beat': b['beat']}
    if kind == 'word' and len(tok) == 3:
        w, _, k = tok[2].partition('#')
        return {'type': 'word', 'line': int(tok[1]), 'word': w, 'occurrence': int(k or 1)}
    if kind == 'event' and len(tok) == 3:
        t = float(tok[2])
        evs = [e for e in timing['events'] if e['kind'] == tok[1]]
        if not evs:
            raise AnchorError(f'no events of kind {tok[1]!r}')
        e = min(evs, key=lambda x: abs(x['t'] - t))
        if abs(e['t'] - t) > 0.25:
            raise AnchorError(f'no {tok[1]} within 0.25 s of {t} (nearest {e["t"]})')
        # index among events of that kind: survives small re-timings
        return {'type': 'event', 'kind': tok[1], 'index': evs.index(e)}
    if kind == 'key' and len(tok) == 2:
        hits = [k for k in timing['key_sync_points'] if tok[1].lower() in k['name'].lower()]
        if len(hits) != 1:
            raise AnchorError(f'key {tok[1]!r} matches {len(hits)} key_sync_points')
        return {'type': 'key', 'name': hits[0]['name']}
    if kind == 'section' and len(tok) == 2:
        hits = [s for s in timing['sections'] if tok[1].lower() in s['name'].lower()]
        if len(hits) != 1:
            raise AnchorError(f'section {tok[1]!r} matches {len(hits)} sections')
        return {'type': 'section', 'name': hits[0]['name']}
    raise AnchorError(f'cannot parse anchor {spec!r}')


def resolve_anchor(a, timing):
    """Structured anchor -> dict with the resolved 't' and a short human label (and confidence notes where known)."""
    a = {k: v for k, v in a.items() if k not in ('t', 'label', 'soft')}
    ty = a['type']
    soft = None
    if ty == 'start':
        t, label = 0.0, 'track start'
    elif ty == 'downbeat':
        d = [x for x in timing['downbeats'] if x['bar'] == a['bar']]
        if not d:
            raise AnchorError(f'no downbeat for bar {a["bar"]}')
        t, label = d[0]['t'], f'B{a["bar"]}'
        if d[0].get('zone') == 'interpolated':
            soft = 'interpolated grid'
    elif ty == 'beat':
        d = [x for x in timing['beats'] if x['bar'] == a['bar'] and x['beat'] == a['beat']]
        if not d:
            raise AnchorError(f'no beat {a["bar"]}.{a["beat"]}')
        t, label = d[0]['t'], f'b {a["bar"]}.{a["beat"]}'
        if d[0].get('zone') == 'interpolated':
            soft = 'interpolated beat'
    elif ty == 'word':
        lines = [l for l in timing['lyrics'] if l['line'] == a['line']]
        if not lines:
            raise AnchorError(f'no lyric line {a["line"]}')
        ws = [w for w in lines[0]['words'] if w['w'].strip('.,;:!?"').lower() == a['word'].lower()]
        k = a.get('occurrence', 1)
        if len(ws) < k:
            raise AnchorError(f'word {a["word"]!r} (#{k}) not in line {a["line"]}: {lines[0]["text"]!r}')
        w = ws[k - 1]
        t, label = w['start'], f'"{w["w"]}" (line {a["line"]})'
        if w.get('confidence') not in (None, 'solid', 'high'):
            soft = f'word confidence {w["confidence"]}'
    elif ty == 'event':
        evs = [e for e in timing['events'] if e['kind'] == a['kind']]
        if a['index'] >= len(evs):
            raise AnchorError(f'event {a["kind"]}[{a["index"]}] missing')
        t, label = evs[a['index']]['t'], f'{a["kind"]} {evs[a["index"]]["t"]:.3f}'
    elif ty == 'key':
        k = [x for x in timing['key_sync_points'] if x['name'] == a['name']]
        if not k:
            raise AnchorError(f'key {a["name"]!r} missing')
        t, label = k[0]['t'], a['name']
    elif ty == 'section':
        s = [x for x in timing['sections'] if x['name'] == a['name']]
        if not s:
            raise AnchorError(f'section {a["name"]!r} missing')
        t, label = s[0]['start'], f'section start "{a["name"]}"'
        soft = 'section boundary, not a beat/word/hit'
    else:
        raise AnchorError(f'unknown anchor type {ty!r}')
    a['t'] = round(float(t), 4)
    a['label'] = label
    if soft:
        a['soft'] = soft
    return a


def sync_points(timing):
    """Every beat, downbeat, word onset, chant word, event and key point: (t, label). Used to answer 'is there anything
    to cut on within a frame of this time?'. Section boundaries are deliberately not included."""
    pts = []
    for b in timing['beats']:
        pts.append((b['t'], f'b {b["bar"]}.{b["beat"]}' + (' (B)' if b['beat'] == 1 else '')))
    for l in timing['lyrics']:
        for w in l['words']:
            pts.append((w['start'], f'"{w["w"]}" L{l["line"]}'))
    for e in timing['events']:
        pts.append((e['t'], e['kind']))
    for k in timing['key_sync_points']:
        pts.append((k['t'], k['name']))
    return sorted(pts)


def nearest_points(t, pts, within):
    return [(pt, lab) for pt, lab in pts if abs(pt - t) <= within + 1e-9]


# ---------------------------------------------------------------------------------------------------------------------

def load_shots():
    d = load_json(SHOTS)
    return d


def select_range(shots, rng=None, only=None):
    """--range A1:C4 (inclusive, in film order) or --only C3,C8."""
    ids = [s['id'] for s in shots]
    if rng:
        a, _, b = rng.partition(':')
        b = b or a
        for x in (a, b):
            if x not in ids:
                raise SystemExit(f'unknown shot id {x!r}')
        i, j = ids.index(a), ids.index(b)
        if j < i:
            raise SystemExit(f'range {rng} runs backwards')
        return shots[i:j + 1]
    if only:
        want = [x.strip() for x in only.split(',') if x.strip()]
        for x in want:
            if x not in ids:
                raise SystemExit(f'unknown shot id {x!r}')
        return [s for s in shots if s['id'] in want]
    return list(shots)


def natural_key(s):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]

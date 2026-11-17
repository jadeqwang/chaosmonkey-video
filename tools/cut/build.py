#!/home/jade/Documents/halys-video/.venv/bin/python
"""Build the frame-snapped shot database and human-readable shot list."""
import json
import math
import re
import yaml
from common import ROOT, FPS, tc


def build():
    source = yaml.safe_load((ROOT / 'docs/shots.yaml').read_text())
    timing = json.loads((ROOT / 'analysis/timing.json').read_text())
    shots = source['shots']
    if not shots:
        raise ValueError('No shots')
    ids = set()
    previous = -1
    for shot in shots:
        if shot['id'] in ids:
            raise ValueError(f"Duplicate shot id: {shot['id']}")
        ids.add(shot['id'])
        t = float(shot['t'])
        if not math.isfinite(t) or t < 0 or t <= previous:
            raise ValueError(f"Unordered/invalid shot time: {shot['id']} at {t}")
        previous = t
    if not math.isfinite(source['end']) or source['end'] <= previous:
        raise ValueError('End must follow the last shot')
    beats = [float(b['t'] if isinstance(b, dict) else b) for b in timing['beats']]
    result = []
    for i, shot in enumerate(shots):
        start = round(shot['t'] * FPS)
        end = round((shots[i + 1]['t'] if i + 1 < len(shots) else source['end']) * FPS)
        if end <= start:
            raise ValueError(f"Zero-length shot after snapping: {shot['id']}")
        seq = re.match(r'[A-Za-z]+', shot['id']).group()
        if seq not in source['sequences']:
            raise ValueError(f'Unknown sequence: {seq}')
        beat = min(beats, key=lambda t: abs(t - start / FPS)) if beats else None
        result.append(dict(id=shot['id'], seq=seq, **{'in': start / FPS, 'out': end / FPS},
                           in_frame=start, out_frame=end, frames=end-start, dur=(end-start)/FPS,
                           world=shot['world'], ink=shot['ink'], sync=shot.get('sync'),
                           singer=shot.get('singer'), desc=shot['desc'],
                           lyrics=[{k: line.get(k) for k in ('text', 'singer', 'start', 'end')}
                                   for line in timing['lines'] if line['start'] < end/FPS and line['end'] > start/FPS],
                           nearest_beat_in=None if beat is None else {'t': beat, 'offset_ms': round((start/FPS-beat)*1000, 3)}))
    output = {'fps': FPS, 'end': round(source['end']*FPS)/FPS,
              'sequences': source['sequences'], 'shots': result}
    (ROOT / 'docs/shots.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    lines = ['# Shot list', '', '24 fps; in/out boundaries use round(t × 24). Beat offset = cut minus beat.', '']
    def cell(value):
        return str(value or '—').replace('|', '\\|').replace('\n', ' ')
    for seq, title in source['sequences'].items():
        lines += [f'## {seq}: {title}', '', '| ID | In m:ss.ff | Dur s | Frames | World | Sync | Ink % | Lyrics | Description |',
                  '| --- | --- | ---: | ---: | --- | --- | ---: | --- | --- |']
        for s in result:
            if s['seq'] == seq:
                values = [s['id'], tc(s['in_frame']), f"{s['dur']:.3f}", s['frames'], s['world'], s['sync'],
                          s['ink'], ' / '.join(l['text'] for l in s['lyrics']), s['desc']]
                lines.append('| ' + ' | '.join(cell(v) if v != 0 else '0' for v in values) + ' |')
        lines.append('')
    (ROOT / 'docs/SHOTLIST.md').write_text('\n'.join(lines))
    print(f"Built {len(result)} shots, {sum(s['frames'] for s in result)} frames; docs/shots.json and docs/SHOTLIST.md")


if __name__ == '__main__':
    build()

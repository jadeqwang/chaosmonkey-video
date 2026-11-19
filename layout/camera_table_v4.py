#!/usr/bin/env python3
"""Print the v4 per-shot camera table (markdown) from the sidecars media/layout/<set>/v4_<SHOT>.json."""
import json, glob, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXED_SKIP = {'floorboards', 'floor (wood)', 'sloped ceiling (roof boards)', 'rafters', 'purlin', 'knee wall', 'collar ties', 'ridge beam', 'back wall', 'left wall', 'front wall', 'right wall (door)', 'ceiling', 'skirting', 'right gable wall', 'left gable wall', 'night outside', 'highway', 'tree line'}
for st in sys.argv[1:] or ['attic88', 'bed26', 'car26']:
    print(f'\n#### {st}\n\n| setup | serves | lens | camera position (m) | looks at (m) | fixed objects in frame (largest first) | warnings |\n|---|---|---|---|---|---|---|')
    for f in sorted(glob.glob(f'{REPO}/media/layout/{st}/v4_*.json')):
        d = json.load(open(f)); sid = d['shot'][3:]
        if sid.startswith(('PLAN', 'ELEV')): continue
        c = d['camera']; objs = [o['label'] for o in d.get('objects', []) if not o.get('figure') and o['label'] not in FIXED_SKIP and o['frame_fraction'] > 0.0004][:9]
        w = '; '.join(d.get('warnings', [])) or ''
        lens = c.get('lens_mm'); pos = ', '.join(f'{v:.2f}' for v in c['position']); tgt = ', '.join(f'{v:.2f}' for v in c['target']) if c.get('target') else ''
        print(f"| `v4_{sid}` | {', '.join(d.get('serves', [])) or sid} | {lens} | {pos} | {tgt} | {', '.join(objs)} | {w} |")

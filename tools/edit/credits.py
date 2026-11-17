#!/usr/bin/env python3
"""Honest model credits for the T1 title card, derived from what is actually in the cut.

    .venv/bin/python tools/edit/credits.py          # rewrites the derived fields of docs/credits.json
    .venv/bin/python tools/edit/credits.py --check  # prints the walk, writes nothing

The walk (after holdfire's HF/tools/t2/credits.py, docs/HARVEST.md section 8):
  docs/picks.json, every shot -> its pick ->
    kind video  : the take file -> docs/takes/*.json -> that take's model (else the filename token, for bake-off takes)
    kind frames : a composite (docs/picks_comp.json `_plate`) -> the plate take, as above; plus SAM 2.1 when the
                  composite's mattes exist (work/comp/<ID>/matte_*.npy); a tools/sky render -> JPL DE441 + Skyfield
    kind still  : a keyframe in media/kf -> the image model (from the keyframe history files)
  every take used -> its keyframe -> the image model that made it (media/kf/<ID>_<token>_v*.jpg: `nbp` = Nano Banana Pro).
Only models whose output reaches the final picture or sound are credited. Bake-off takes, rejected takes, reference
sheets and tools used only as a check are not. The supporting audio/astronomy credits are a hand-kept list below, but
each is checked against a file that proves it is used; an entry whose evidence is missing is dropped (and reported).

It writes, in docs/credits.json: `cast` (the rows shown on the card) and `_walk` (shot -> model, for audit). The other
fields (title, music, made_by, small print) are kept as they are: the director owns their wording.
"""
import argparse
import glob
import json
import re
from collections import OrderedDict

from common import ROOT

PICKS = ROOT / 'docs' / 'picks.json'
COMP = ROOT / 'docs' / 'picks_comp.json'
CREDITS = ROOT / 'docs' / 'credits.json'

# public names (docs/BAKEOFF.md; docs/gen_catalog/<vendor>-<model>.json "name")
VIDEO = OrderedDict([            # display order on the card
    ('kling4', 'Kling v4'),          # klingai/kling-v4 (catalog name "Kling 4.0"; the bake-off calls it Kling v4)
    ('hh11', 'HappyHorse 1.1'),      # alibaba/hh1.1-i2v
    ('veo31', 'Veo 3.1'),            # google/veo-3.1
    ('sd25', 'Seedance 2.5'), ('sd20', 'Seedance 2.0'), ('vidu3', 'Vidu 3'), ('wan27', 'Wan 2.7'), ('gen45', 'Gen-4.5'),
])
MODEL_ALIASES = {'klingai/kling-v4': 'kling4', 'alibaba/hh1.1-i2v': 'hh11', 'google/veo-3.1': 'veo31'}
# keyframes made locally from another shot's keyframe (no paid call): media/kf/KEYFRAMES_homes.md, F7
DERIVED_KF = {'F7': 'F2'}
IMAGE_MODEL = {'google/nano-banana-pro': 'nbp', 'google/nano-banana-2.1': 'nbp2', 'openai/gpt-image-2.5-sunburst': 'gpt',
               'bytedance/seedream-5-pro': 'seedream', 'black-forest-labs/flux-2-max': 'flux'}
IMAGE = OrderedDict([('nbp', 'Nano Banana Pro'), ('gpt', 'GPT Image'), ('seedream', 'Seedream'), ('flux', 'FLUX')])

# supporting cast: (display, role, evidence glob or (file, regex)); role orders the rows
SUPPORT = [
    ('SAM 2.1', 'picture', None),                                    # added only if a composite in the cut has mattes
    ('RAFT', 'picture', ('docs/picks.json', r'r4_post/r4_C[26]_')),               # optical-flow retime in C2 (x1.25) and C6's slow peak (tools/edit/slowmo.py)
    ('ElevenLabs Music v2', 'sound', ('docs/SOUND.md', r'ElevenLabs')),          # foley sources in the layer
    ('BS-RoFormer', 'sound', ('docs/AUDIO_MAP.md', r'BS-RoFormer')),            # vocal stem: word times + the layer's vocal rule
    ('Demucs', 'sound', ('docs/AUDIO_MAP.md', r'htdemucs')),                    # drums stem: the drum hits the chant cuts sit on
    ('NeMo', 'sound', ('tools/audio/ctc.py', r'NeMo')),                         # conformer-CTC word alignment
    ('MMS', 'sound', ('docs/AUDIO_MAP.md', r'MMS')),                            # wav2vec2 MMS forced alignment
    ('JPL DE441', 'sky', ('tools/sky/ephem_build.py', r'de441')),               # the eclipse geometry
    ('Skyfield', 'sky', ('tools/sky/ephem_build.py', r'skyfield')),
]
NOT_CREDITED = {
    'Whisper large-v3': 'transcript and a check on the word times only (docs/AUDIO_MAP.md, Method)',
    'Veo 3.1 Fast, Seedance, Vidu, Wan, Gen-4.5': 'bake-off takes only; none is in the cut',
}


def load_takes():
    by_file = {}
    for f in sorted(glob.glob(str(ROOT / 'docs' / 'takes' / '*.json'))):
        d = json.load(open(f))
        for t in (d['takes'] if isinstance(d, dict) else d):
            if t.get('file'):
                by_file[t['file']] = t
            if t.get('tag'):                     # post files (media/gen/r4_post/) are found by the pick's _take
                by_file.setdefault('tag:' + t['tag'], t)
    return by_file


def token_of(path):
    m = re.search(r'bk_[A-Z]\d+_([a-z0-9]+)_', path)
    return m.group(1) if m else None


def video_model(src, takes, tag=None):
    t = takes.get(src)
    if t is None and token_of(src) is None and tag:   # only for files named neither in a take record nor bk_*
        t = takes.get('tag:' + tag)
    if t:
        m = t.get('model', '')
        key = MODEL_ALIASES.get(m, m)
        if key in VIDEO:
            return key, t
    key = token_of(src)
    if key in VIDEO:
        return key, t
    raise SystemExit(f'credits: no model for {src}')


def keyframe_model(kf, shot):
    """The image model behind a keyframe: the history files media/kf/<ID>_<token>_v*.jpg for that shot."""
    if not kf:
        return None
    name = kf.split('/')[-1]
    for tok in IMAGE:
        if f'_{tok}_' in name:
            return tok
    m = re.match(r'(.+?)_pick', name) or re.match(r'([A-Z]\d+)', name)
    stem = m.group(1) if m else shot              # C7_plate_pick_1080.jpg -> C7_plate_nbp_v*.jpg
    stem = DERIVED_KF.get(stem, stem)
    toks = {tok for tok in IMAGE if glob.glob(str(ROOT / 'media' / 'kf' / f'{stem}_{tok}_*'))}
    if len(toks) == 1:
        return toks.pop()
    m2 = re.match(r'([A-Z]\d+)_(r\d+)[a-z]?$', stem)
    if not toks and m2:
        # re-take keyframes (<ID>_r2_v<n>, <ID>_r4_v<n>) carry no model token in their file names; the spend ledger
        # names the model of every call, tagged kf_<ID>_<rN>* or kf_<rN>_<ID>*
        sid_, rn = m2.groups()
        pat = re.compile(rf'^kf_({sid_}_{rn}|{rn}_{sid_})(?![0-9])')
        models = set()
        for line in open(ROOT / 'docs' / 'spend_ledger.jsonl'):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if pat.match(d.get('tag') or ''):
                models.add(d.get('model', ''))
        toks = {tok for tok in IMAGE for mm in models if IMAGE_MODEL.get(mm) == tok}
        if len(toks) == 1 and len(models) == 1:
            return toks.pop()
    raise SystemExit(f'credits: keyframe {kf} ({shot}): image model not found ({toks or "no history files"})')


def evidence(ev):
    if ev is None:
        return True
    f, rx = ev
    p = ROOT / f
    return p.exists() and re.search(rx, p.read_text(errors='ignore'), re.I) is not None


def walk():
    picks = json.load(open(PICKS))['picks']
    comp = json.load(open(COMP))['picks'] if COMP.exists() else {}
    takes = load_takes()
    video, image, sam, sky, rows = set(), set(), False, False, OrderedDict()
    for sid in sorted(picks, key=lambda s: (s[0], int(re.sub(r'\D', '', s) or 0))):
        p = picks[sid]
        kind, src, note, tag = p.get('kind'), None, [], p.get('_take')
        if kind == 'video':
            src = p['src']
        elif kind == 'frames':
            d = p.get('dir', '')
            if d.startswith('work/comp/'):
                plate = p.get('_plate') or (comp.get(sid) or {}).get('_plate') or {}   # B1/D3 live in picks_r4_finish
                src, tag = plate.get('src'), plate.get('_take')
                if not src:
                    raise SystemExit(f'credits: composite {sid} names no plate in picks_comp.json')
                if glob.glob(str(ROOT / d / 'matte_*.npy')):
                    sam = True; note.append('SAM 2.1 mattes')
                note.append('composite')
            elif d.startswith('work/sky/'):
                sky = True; rows[sid] = 'tools/sky render (JPL DE441 + Skyfield)'; continue
            elif d.startswith('work/edit/title'):
                continue
        elif kind == 'still':
            s = p['src']
            if s.startswith('design/'):
                continue
            tok = keyframe_model(s, sid)
            image.add(tok); rows[sid] = f'still {s} -> {IMAGE[tok]}'; continue
        else:
            rows[sid] = 'slate (no picture)'; continue
        key, t = video_model(src, takes, tag)
        video.add(key)
        kf = (t or {}).get('keyframe') or f'media/kf/{sid}_pick_1080.jpg'
        tok = keyframe_model(kf, sid)
        image.add(tok)
        rows[sid] = f'{VIDEO[key]} ({src.split("/")[-1]}) from keyframe {kf.split("/")[-1]} -> {IMAGE[tok]}' + \
            (f'; {", ".join(n for n in note if n)}' if note else '')
    return video, image, sam, sky, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    video, image, sam, sky, rows = walk()
    vid = [VIDEO[k] for k in VIDEO if k in video]
    img = [IMAGE[k] for k in IMAGE if k in image]
    support, dropped = [], []
    for name, role, ev in SUPPORT:
        if name == 'SAM 2.1' and not sam:
            dropped.append(f'{name}: no composite in the cut uses mattes'); continue
        if role == 'sky' and not sky:
            dropped.append(f'{name}: no sky element in the cut'); continue
        if not evidence(ev):
            dropped.append(f'{name}: evidence missing ({ev})'); continue
        support.append((name, role))
    picture = img + [n for n, r in support if r == 'picture']
    sound_sky = [n for n, r in support if r in ('sound', 'sky')]
    cast = {
        '_doc': 'Derived by tools/edit/credits.py from docs/picks.json -> docs/takes/*.json -> models; do not edit by hand.',
        'lead': 'and a supporting cast of models:',
        'video': vid,            # row 1 (model-name style)
        'picture': picture,      # row 2: the image model, then compositing/finishing models
        'support': sound_sky,    # row(s) 3: audio and astronomy tools (smaller), split into balanced rows by title_card.py
    }
    for sid, r in rows.items():
        print(f'{sid:4s} {r}')
    print('\nvideo  :', ' · '.join(vid))
    print('picture:', ' · '.join(picture))
    print('support:', ' · '.join(sound_sky))
    for d in dropped:
        print('dropped:', d)
    if a.check:
        return
    cr = json.load(open(CREDITS), object_pairs_hook=OrderedDict)
    cr['cast'] = cast
    cr['_walk'] = rows
    cr['_not_credited'] = NOT_CREDITED
    cr.pop('generated_with', None)
    json.dump(cr, open(CREDITS, 'w'), indent=1, ensure_ascii=False)
    CREDITS.write_text(CREDITS.read_text() + '\n')
    print(f'\n-> {CREDITS.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

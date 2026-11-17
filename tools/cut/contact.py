#!/home/jade/Documents/halys-video/.venv/bin/python
"""Extract first/middle/last frames into one contact sheet per sequence."""
import argparse
import json
import av
from PIL import Image, ImageDraw
from common import ROOT, tc, font, safe_name


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--name', required=True, type=safe_name)
    args = p.parse_args()
    work = ROOT/'work/cut'/args.name
    manifest = json.loads((work/'manifest.json').read_text())
    targets = {}
    for s in manifest['shots']:
        for offset in (0, s['frames']//2, s['frames']-1):
            targets[s['cut_in_frame']+offset] = None
    with av.open(str(ROOT/'media/cut'/f'{args.name}.mp4')) as container:
        for i, frame in enumerate(container.decode(video=0)):
            if i in targets:
                targets[i] = frame.to_image().resize((720,405), Image.Resampling.LANCZOS)
    if any(im is None for im in targets.values()):
        raise RuntimeError('Missing contact frames in assembled video')
    seqs = list(dict.fromkeys(s['seq'] for s in manifest['shots']))
    for seq in seqs:
        shots = [s for s in manifest['shots'] if s['seq'] == seq]
        sheet = Image.new('RGB', (2220, 65+len(shots)*455), '#211f1c')
        d = ImageDraw.Draw(sheet)
        d.text((20,12), f'{args.name} · {seq} · first / middle / last', font=font(29), fill='white')
        for row, s in enumerate(shots):
            for col, offset in enumerate((0,s['frames']//2,s['frames']-1)):
                x, y = 20+col*735, 65+row*455
                sheet.paste(targets[s['cut_in_frame']+offset], (x,y))
                d.text((x,y+410), f"{s['id']} · song {tc(s['in_frame']+offset)} · cut {tc(s['cut_in_frame']+offset)}",
                       font=font(21), fill='#e1d7c5')
        path = work/f'contact_{seq}.jpg'
        sheet.save(path, quality=90)
        with Image.open(path) as check:
            check.verify()
        print(f'{path}: {len(shots)} shots, {sheet.width}×{sheet.height}')


if __name__ == '__main__':
    main()

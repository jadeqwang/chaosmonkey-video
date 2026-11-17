"""Prepare the picked generated clips (key onto our paper) into work/ink_clips/<name>/ at 1080p."""
import sys
sys.path.insert(0, '.')
from tools.ink.video import Clip
PICKS = {'stg_d1': 'media/gen/stage/clips/stg_d1_sd20.mp4', 'stg_d6': 'media/gen/stage/clips/stg_d6_kling4.mp4', 'stg_d7': 'media/gen/stage/clips/stg_d7_sd20.mp4',
         'stg_d8': 'media/gen/stage/clips/stg_d8_kling4.mp4', 'stg_j3': 'media/gen/stage/clips/stg_j3_kling4.mp4'}
for name in (sys.argv[1:] or PICKS):
    c = Clip.prepare(PICKS[name], out=f'work/ink_clips/{name}', ground='light', height=1080)
    print(name, c.n, c.w, c.h, c.meta.get('stab_lost'))

"""D6 hand-over element for WORLD: the costume-B monkey somersaulting in on his cloud and landing in 亮相, on BARE
paper, as a multiply-ready transmittance video (white = nothing; composite with frame *= T, i.e. tools.ink lay_ink),
70 frames = D6 (73.500-76.417), the landing (foot down, pose set) on the kick 75.025 = element frame 37.
    PY tools/stage/d6_element.py TAG SRC_LAND [SRC_END] -> media/el/stage_v4/D6_monkey_B_T.mp4 (1920x1080, 24 fps, 70 f)
       + D6_monkey_B_T_png/0000.png.. (16-bit-free 8-bit PNG) + D6_monkey_B.json (retime, foot point per frame)."""
import sys, os, json
sys.path.insert(0, '.')
import numpy as np, cv2
from tools.ink.video import Clip
from tools.stage.stage import KeyRetime
tag = sys.argv[1]; land = float(sys.argv[2]); end = float(sys.argv[3]) if len(sys.argv) > 3 else None
CL = Clip(f'work/ink_clips/{tag}')
T0, N, FL = 73.5, 70, 37
t_land = (1764 + FL) / 24
end = end or min(CL.duration - 0.05, land + 1.0)
RT = KeyRetime([(T0, 0.3), (t_land, land), (T0 + N / 24, end)], duration=CL.duration)
out = 'media/el/stage_v4/'; os.makedirs(out + 'D6_monkey_B_T_png', exist_ok=True)
import av
c = av.open(out + 'D6_monkey_B_T.mp4', 'w'); st = c.add_stream('libx264', rate=24)
st.width, st.height, st.pix_fmt = 1920, 1080, 'yuv444p'; st.options = {'crf': '10', 'preset': 'slow'}
meta = dict(take=tag, src_land=land, src_end=end, land_frame=FL, land_time=t_land, frames=[])
for i in range(N):
    t = (1764 + i) / 24 + 1e-6
    s = RT.src(t)
    T = np.clip(CL.at(s), 0, 1)
    if T.shape[1] != 1920:
        T = cv2.resize(T, (1920, 1080), interpolation=cv2.INTER_AREA)
    img = (T * 255 + 0.5).astype(np.uint8)
    cv2.imwrite(out + f'D6_monkey_B_T_png/{i:04d}.png', img[..., ::-1])
    d = 1 - T.min(axis=2); ys, xs = np.where(d > 0.15)
    box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
    meta['frames'].append(dict(i=i, song_t=round(t, 4), src=round(s, 4), ink_box=box))
    fr = av.VideoFrame.from_ndarray(img, format='rgb24')
    for p in st.encode(fr): c.mux(p)
for p in st.encode(): c.mux(p)
c.close()
json.dump(meta, open(out + 'D6_monkey_B.json', 'w'), indent=1)
print('ok', N, 'frames; landing box', meta['frames'][FL]['ink_box'])

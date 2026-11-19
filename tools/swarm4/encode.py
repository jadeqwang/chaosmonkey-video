"""Encode a swarm4 frame directory (f0000.png ...) to an mp4: 24 fps, no audio, yuv420p, H.264.
   python tools/swarm4/encode.py work/swarm/render/A media/comp/F4F5F6a_A.mp4 [--crf 14] [--expect 176]
"""
import argparse, glob, os, subprocess, sys
ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--crf', type=int, default=14); ap.add_argument('--expect', type=int, default=176)
a = ap.parse_args()
fr = sorted(glob.glob(os.path.join(a.src, 'f[0-9][0-9][0-9][0-9].png')))
if len(fr) != a.expect:
    print(f'warning: {len(fr)} frames in {a.src}, expected {a.expect}', file=sys.stderr)
names = [os.path.basename(f) for f in fr]
want = [f'f{i:04d}.png' for i in range(len(fr))]
if names != want: sys.exit('frames are not a contiguous f0000.. sequence')
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '24', '-i', os.path.join(a.src, 'f%04d.png'), '-an',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf), '-pix_fmt', 'yuv420p', '-r', '24', '-movflags', '+faststart', a.out], check=True)
print(a.out, len(fr), 'frames', f'{len(fr) / 24:.3f} s')

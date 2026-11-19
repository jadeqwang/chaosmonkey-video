#!/usr/bin/env python
"""standin.py: a 289-frame 1920x1080 stand-in for the Kling flight (tool test only).
Frames 0..~110: a clean rock plate (WORLD frame 0 with the 通 inpainted away) zoomed out about a known point (exp. zoom
2.4 -> 1.0, so panel corners are known exactly: see ZOOM / zoom_H), then cross-faded over WORLD's own 3D beauty frames
(work/world/Dflight_r2b/frames/beauty, 60..203). Writes work/dflight/standin/standin.mp4 (+ plate.png, truth.json)."""
import json, os, subprocess, sys
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
N, Z0, Z1, I_Z1, X0, X1 = 289, 2.4, 0.10, 125, 118, 170
CEN = (960.0, 540.0)
OUT = 'work/dflight/standin'


def zoom(i):
    return Z0 * (Z1 / Z0) ** min(i / I_Z1, 1.0)


def zoom_H(i, mode='plate'):
    """plate px (1920x1080) -> standin frame px at frame i (zoom about CEN)."""
    z = zoom(i)
    return np.array([[z, 0, CEN[0] * (1 - z)], [0, z, CEN[1] * (1 - z)], [0, 0, 1]], float)


def plate():
    p = f'{OUT}/plate.png'
    if os.path.exists(p):
        return cv2.imread(p)
    im = cv2.imread('work/world/Dflight_r2b/frames/beauty/0000.png')
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bg = cv2.GaussianBlur(cv2.medianBlur(g.astype(np.uint8), 101).astype(np.float32), (0, 0), 12)
    m = ((bg - g) > 4).astype(np.uint8) * 255
    m[:, :300] = 0; m[:, 1450:] = 0
    m = cv2.dilate(m, np.ones((31, 31), np.uint8))
    m = np.maximum(m, (cv2.dilate((g < 190).astype(np.uint8), np.ones((25, 25), np.uint8)) * 255) * (np.arange(1920)[None, :] > 300) * (np.arange(1920)[None, :] < 1450)).astype(np.uint8)
    out = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA).astype(np.float32)
    r = np.random.RandomState(5)
    tex = np.zeros((1080, 1920), np.float32)
    for sg, a in ((2, .015), (6, .02), (18, .025), (50, .03)):
        n = cv2.GaussianBlur(r.randn(1080, 1920).astype(np.float32), (0, 0), sg)
        tex += a * n / n.std()
    crk = np.zeros((1080, 1920), np.float32)
    for _ in range(28):
        pt = r.rand(2) * (1920, 1080); a = r.rand() * 6.28
        for _ in range(r.randint(40, 120)):
            a += r.randn() * .35; q = pt + 9 * np.array([np.cos(a), np.sin(a)])
            cv2.line(crk, tuple(map(int, pt)), tuple(map(int, q)), 1.0, 1, cv2.LINE_AA); pt = q
    crk = cv2.GaussianBlur(crk, (0, 0), 1.0)
    out = out * 0.93 * (1 + tex[..., None]) * (1 - 0.35 * np.clip(crk, 0, 1)[..., None])
    out = np.clip(out, 0, 255).astype(np.uint8)
    cv2.imwrite(p, out)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    P = plate()
    # larger canvas so zoom-out never shows the border: plate is used as is (z >= 1)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1920x1080', '-r', '24', '-i', '-',
           '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', f'{OUT}/standin.mp4']
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        H = zoom_H(i)
        A = cv2.warpAffine(P, H[:2], (1920, 1080), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        if i > X0:
            w = int(round(60 + (i - X0) * 143.0 / (N - 1 - X0)))
            Bf = cv2.imread('work/world/Dflight_r2b/frames/beauty/%04d.png' % min(w, 203)).astype(np.float32)
            u = np.clip((i - X0) / (X1 - X0), 0, 1); u = u * u * (3 - 2 * u)
            A = A * (1 - u) + Bf * u
        pr.stdin.write(np.clip(A, 0, 255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait()
    json.dump(dict(n=N, z0=Z0, i_z1=I_Z1, cen=CEN, x0=X0, x1=X1), open(f'{OUT}/truth.json', 'w'))
    print('wrote', OUT + '/standin.mp4')


MAP = [[0, 0], [20, 10], [60, 70], [134, 200], [170, 250], [203, 288]]


def write_cfg(path='work/dflight/dcomp_standin.json'):
    """dcomp config for the stand-in; panel corners at the key frames come from the TRUE zoom (so tracking can be checked)."""
    from scipy.interpolate import PchipInterpolator
    m = np.array(MAP, float)
    v = PchipInterpolator(m[:, 0], m[:, 1])
    unit = 180.0                       # plate px (1920) per panel unit (glyph size)
    rr = [-3.0, -2.5, 3.0, 2.5]
    plate = np.array([[CEN[0] + rr[0] * unit, CEN[1] + rr[1] * unit], [CEN[0] + rr[2] * unit, CEN[1] + rr[1] * unit],
                      [CEN[0] + rr[2] * unit, CEN[1] + rr[3] * unit], [CEN[0] + rr[0] * unit, CEN[1] + rr[3] * unit]])
    keys = []
    for s in (0, 25, 50, 75, 90):
        Hh = zoom_H(float(v(s)))
        q = cv2.perspectiveTransform(plate[None], Hh)[0] / 2.0        # -> 960x540 reference units
        keys.append(dict(s=s, corners=np.round(q, 2).tolist()))
    cfg = dict(name='standin', source=dict(file='work/dflight/standin/standin.mp4'), map=MAP,
               panel=dict(ref_rect=rr, keys=keys, cols=[-7, 7], rows=[-9, 9], g0=320, fade_px=[6.5, 11], glow_fade_px=[1.2, 3.0]),
               jumps=dict(ember_s=4.2, times=[14.7, 20.5, 21.8, 32.3, 42.9, 53.5, 64.2, 74.7, 85.3, 96.2, 106.5, 117.3, 128.1, 138.5, 149.2, 159.9],
                          stagger=[5, 6, 6, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]),
               frontier=dict(on=False),
               inscription=[dict(text='一通百通', s0=0, s1=32), dict(key='D5', s0=33, s1=133)],
               landing=dict(s=170.6, pt=[560, 380], radius=70, gain=0.95, decay_frames=10,
                            seal=dict(on=False, ch='倉', px=52, pt=[700, 150])),
               d7='media/comp/D7.mp4')
    json.dump(cfg, open(path, 'w'), indent=1, ensure_ascii=False)
    print('wrote', path)


def check():
    """tracking error vs truth (stand-in only): mean corner error (ref px) at s = 0,10,..,100 from the cached track json."""
    from scipy.interpolate import PchipInterpolator
    import glob
    m = np.array(MAP, float); v = PchipInterpolator(m[:, 0], m[:, 1])
    f = sorted(glob.glob('work/dflight/standin/track_*.json'), key=os.path.getmtime)[-1]
    Q = json.load(open(f))['quads']
    cfg = json.load(open('work/dflight/dcomp_standin.json')); rr = cfg['panel']['ref_rect']; unit = 180.0
    plate = np.array([[CEN[0] + rr[0] * unit, CEN[1] + rr[1] * unit], [CEN[0] + rr[2] * unit, CEN[1] + rr[1] * unit],
                      [CEN[0] + rr[2] * unit, CEN[1] + rr[3] * unit], [CEN[0] + rr[0] * unit, CEN[1] + rr[3] * unit]])
    for s in range(0, 104, 10):
        q = cv2.perspectiveTransform(plate[None], zoom_H(float(v(s))))[0] / 2.0
        print(s, 'corner err %.2f ref px' % np.abs(np.array(Q[s]) - q).max(), 'quad width %.0f' % np.linalg.norm(q[1] - q[0]))


if __name__ == '__main__':
    if '--check' in sys.argv:
        check()
    elif '--cfg' in sys.argv:
        write_cfg()
    else:
        main()

#!/usr/bin/env python3
"""Slow motion and speed ramps in post, from a real-speed 24 fps take (round-4 mechanics test).

    PY tools/edit/slowmo.py SRC.mp4 OUT.mp4 --in=S --out=S --slow=4 [--method=raft|mci|blend]
        constant slow motion: source [in, out] played at 1/slow speed (output is (out-in)*slow seconds).
    PY tools/edit/slowmo.py SRC.mp4 OUT.mp4 --ramp="S0:1, S1:1, S2:4, S3:4, S4:1, S5:1" [--method=raft]
        speed ramp: a list of source-time:slow-factor knots; the factor is linearly interpolated between knots
        and the output plays source S0..S_last. Example: real speed 0.6-1.2, into 4x slow by 1.5, hold to 2.1,
        back out to real speed by 2.4, real speed to 3.0:  --ramp="0.6:1,1.2:1,1.5:4,2.1:4,2.4:1,3.0:1"

Methods:
  raft   (default) torchvision RAFT-large optical flow (weights from download.pytorch.org, cached in
         ~/.cache/torch), bidirectional backward warping with forward-backward occlusion weighting; where the two
         warps disagree it takes the nearer frame's warp instead of cross-fading (--select=0 turns that off).
         --flowscale (default 0.75; 1.0 runs out of memory on the 24 GB card at 1080p). Needs the CUDA GPU (about 0.5 s per output frame at 1080p on the RTX 3090).
  mci    ffmpeg minterpolate (mi_mode=mci, aobmc, bidir, vsbmc), no GPU. Only constant --slow.
  blend  plain cross-fade between neighbouring frames (what assemble.py "interp": "blend" does), for reference.

Output: 24 fps, 1920x1080, H.264 CRF 14, no audio.
"""
import os
import subprocess
import sys

import cv2
import numpy as np

FPS = 24.0


def opts(argv):
    o, rest = {}, []
    for a in argv:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            o[k] = v
        else:
            rest.append(a)
    return o, rest


def read_frames(path):
    cap = cv2.VideoCapture(path)
    fr = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fr.append(f)
    return fr


def writer(out, w, h):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                             "-s", f"{w}x{h}", "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "14",
                             "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "24", out], stdin=subprocess.PIPE)


def source_times(o, n_src):
    """Source time (s) for each output frame."""
    last = (n_src - 1) / FPS
    if "ramp" in o:
        knots = [tuple(map(float, k.split(":"))) for k in o["ramp"].replace(" ", "").split(",")]
        t, out = knots[0][0], []
        while t <= min(knots[-1][0], last) + 1e-9:
            out.append(t)
            s = np.interp(t, [k[0] for k in knots], [k[1] for k in knots])
            t += 1.0 / FPS / s
        return out
    a, b, s = float(o.get("in", 0)), min(float(o.get("out", last)), last), float(o.get("slow", 4))
    k = int(round((b - a) * FPS * s))
    return [a + i / (FPS * s) for i in range(k + 1)]


# ------------------------------------------------------------------ RAFT interpolation
class Raft:
    def __init__(self, scale=0.5, select=True):
        self.scale, self.select = scale, select
        import torch
        from torchvision.models.optical_flow import Raft_Large_Weights, raft_large
        self.torch = torch
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = raft_large(weights=Raft_Large_Weights.DEFAULT, progress=False).to(self.dev).eval()
        self.cache = {}

    def _t(self, img):
        return self.torch.from_numpy(img[:, :, ::-1].copy()).permute(2, 0, 1).float()[None].to(self.dev) / 255.0

    def flows(self, i, f0, f1):
        """Flow 0->1 and 1->0 at full resolution (computed at half resolution), cached per pair."""
        if i in self.cache:
            return self.cache[i]
        torch = self.torch
        F = torch.nn.functional
        h, w = f0.shape[:2]
        hh, ww = (int(h * self.scale) + 7) // 8 * 8, (int(w * self.scale) + 7) // 8 * 8
        a = F.interpolate(self._t(f0), size=(hh, ww), mode="bilinear", align_corners=False) * 2 - 1
        b = F.interpolate(self._t(f1), size=(hh, ww), mode="bilinear", align_corners=False) * 2 - 1
        with torch.no_grad():
            fl = self.model(torch.cat([a, b]), torch.cat([b, a]), num_flow_updates=20)[-1]
        fl = F.interpolate(fl, size=(h, w), mode="bilinear", align_corners=False)
        fl[:, 0] *= w / ww
        fl[:, 1] *= h / hh
        self.cache = {i: (fl[0:1], fl[1:2])}
        return self.cache[i]

    def warp(self, img, flow):
        torch = self.torch
        _, _, h, w = img.shape
        yy, xx = torch.meshgrid(torch.arange(h, device=self.dev), torch.arange(w, device=self.dev), indexing="ij")
        gx = (xx[None] + flow[:, 0]) / (w - 1) * 2 - 1
        gy = (yy[None] + flow[:, 1]) / (h - 1) * 2 - 1
        return torch.nn.functional.grid_sample(img, torch.stack([gx, gy], -1), mode="bilinear",
                                               padding_mode="border", align_corners=True)

    def mid(self, i, f0, f1, t):
        torch = self.torch
        f01, f10 = self.flows(i, f0, f1)
        I0, I1 = self._t(f0), self._t(f1)
        # forward-backward consistency -> occlusion error at each frame's own pixels
        e0 = (f01 + self.warp(f10, f01)).norm(dim=1, keepdim=True)
        e1 = (f10 + self.warp(f01, f10)).norm(dim=1, keepdim=True)
        # flows from time t back to 0 and to 1 (linear-motion approximation, Super SloMo)
        ft0 = -(1 - t) * t * f01 + t * t * f10
        ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10
        w0 = (1 - t) / (1 + self.warp(e0, ft0))
        w1 = t / (1 + self.warp(e1, ft1))
        a, b = self.warp(I0, ft0), self.warp(I1, ft1)
        out = (w0 * a + w1 * b) / (w0 + w1 + 1e-6)
        if self.select:
            # where the two warps disagree (thin fast objects, occlusions) take the nearer frame's warp
            # instead of a cross-fade, so nothing is drawn twice
            d = (a - b).abs().max(dim=1, keepdim=True)[0]
            m = torch.nn.functional.max_pool2d((d > 0.08).float(), 9, 1, 4)
            m = torch.nn.functional.avg_pool2d(m, 9, 1, 4)
            near = a if t < 0.5 else b
            out = out * (1 - m) + near * m
        img = (out[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()[:, :, ::-1] * 255 + 0.5).astype(np.uint8)
        return np.ascontiguousarray(img)


def render(src, out, o):
    method = o.get("method", "raft")
    if method == "mci":
        if "ramp" in o:
            raise SystemExit("mci does constant slow motion only; use --method=raft for ramps")
        a, b, s = float(o.get("in", 0)), o.get("out"), float(o.get("slow", 4))
        trim = f"trim=start={a}" + (f":end={b}" if b else "") + ",setpts=PTS-STARTPTS,"
        vf = (trim + f"minterpolate=fps={FPS * s:g}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
              f"setpts={s:g}*PTS,fps=24")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", vf, "-an", "-c:v", "libx264",
                        "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", out], check=True)
        print(out)
        return
    fr = read_frames(src)
    times = source_times(o, len(fr))
    h, w = fr[0].shape[:2]
    p = writer(out, w, h)
    raft = Raft(float(o.get("flowscale", 0.75)), o.get("select", "1") != "0") if method == "raft" else None
    for t in times:
        x = t * FPS
        i = min(int(np.floor(x + 1e-6)), len(fr) - 1)
        a = x - i
        if a < 1e-3 or i >= len(fr) - 1:
            img = fr[i]
        elif method == "blend":
            img = cv2.addWeighted(fr[i], 1 - a, fr[i + 1], a, 0)
        else:
            img = raft.mid(i, fr[i], fr[i + 1], a)
        p.stdin.write(img.tobytes())
    p.stdin.close()
    p.wait()
    print(out, f"{len(times)} frames = {len(times) / FPS:.2f} s")


def main():
    o, a = opts(sys.argv[1:])
    if len(a) != 2:
        raise SystemExit(__doc__)
    os.makedirs(os.path.dirname(os.path.abspath(a[1])), exist_ok=True)
    render(a[0], a[1], o)


if __name__ == "__main__":
    main()

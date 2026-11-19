"""shots/_book4_pageturn.py: a leaf of a Chinese book as a deformable mesh (BOOK v4, K4; no hand).

The leaf hangs on the spine and turns left -> right. Its cross-section is an inextensible ribbon whose tangent angle
phi(a, v) (a = distance from the spine along the leaf, v = height across it) is
    phi = th + bend * g(s) + twist * (v - .5) * s^1.5 + ripple(s, v, t)        s = a / leaf width
so the outer edge can lead (bend > 0: the page lifts at its free edge and curls), a corner can lead (twist), and a
travelling ripple runs out to the free edge (flutter). Positions are integrated along a; phi is clamped to [0, pi]
(the leaf cannot go through the page below). The mesh is shaded per vertex from its normal (torch from above, a
little nearer the spine), textured on both faces with typeset page art (front = the old left page, back = the new
right page, mirrored), drawn painter-sorted at 2x supersampling, and casts a soft shadow on the pages below.
"""
import math

import cv2
import numpy as np
from tools.ink.core import blur

F32 = np.float32
SS = 2                       # supersampling of the leaf layer


def smooth(x, a=0.0, b=1.0):
    x = np.clip((x - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)


class Keys:
    """Piecewise smooth keyframes: list of (t, value); smoothstep between; held outside."""

    def __init__(self, pts):
        self.t = [p[0] for p in pts]
        self.v = [p[1] for p in pts]

    def __call__(self, t):
        ts, vs = self.t, self.v
        if t <= ts[0]:
            return vs[0]
        if t >= ts[-1]:
            return vs[-1]
        for i in range(len(ts) - 1):
            if ts[i] <= t < ts[i + 1]:
                u = (t - ts[i]) / (ts[i + 1] - ts[i])
                u = u * u * (3 - 2 * u) if len(ts) > 2 else u
                return vs[i] + (vs[i + 1] - vs[i]) * u


class Leaf:
    def __init__(self, front, back, spine_x, top, lw, lh, cam, light=(0.18, -0.30, 1.0), nu=44, nv=26):
        """front/back: float RGB textures of the leaf at its FLAT screen size x SS; front has the spine at its RIGHT
        edge (a left page), back has the spine at its LEFT edge (a right page). cam = (W, H, D, cx, cy)."""
        self.front, self.back = front, back
        self.spine, self.top, self.lw, self.lh, self.cam = spine_x, top, lw, lh, cam
        l = np.asarray(light, F32)
        self.l = l / np.linalg.norm(l)
        self.nu, self.nv = nu, nv
        self.th_, self.bend_, self.twist_, self.amp_, self.ph_ = 0, 0, 0, 0, 0

    def project(self, X, Y, Z):
        W, H, D, cx, cy = self.cam
        k = D / (D - Z)
        return cx + (X - cx) * k, cy + (Y - cy) * k

    def geometry(self, th, bend, twist, amp, phase, kw=1.6):
        nu, nv = self.nu, self.nv
        s = np.linspace(0, 1, nu + 1, dtype=F32)[None, :]
        v = np.linspace(0, 1, nv + 1, dtype=F32)[:, None]
        g = s ** 1.5
        phi = th + bend * g + twist * (v - 0.5) * s ** 1.5 + amp * np.sin(kw * 2 * math.pi * s - phase) * s * (0.6 + 0.8 * v)
        phi = np.clip(phi, 0.0, math.pi)
        da = self.lw / nu
        # integrate (trapezoid) along a
        cx_ = np.cumsum(np.cos(phi), 1) - 0.5 * (np.cos(phi) + np.cos(phi)[:, :1])
        sz_ = np.cumsum(np.sin(phi), 1) - 0.5 * (np.sin(phi) + np.sin(phi)[:, :1])
        X = self.spine - cx_ * da
        Z = sz_ * da
        Y = self.top + v * self.lh + 0 * X
        return X.astype(F32), Y.astype(F32), Z.astype(F32), phi

    def normals(self, X, Y, Z):
        P = np.stack([X, Y, Z], -1)
        Pa = np.gradient(P, axis=1)
        Pv = np.gradient(P, axis=0)
        n = np.cross(Pv, Pa)
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        return n.astype(F32)

    def shade(self, n, face):
        nn = n if face > 0 else -n
        d = np.clip((nn * self.l).sum(-1), 0, 1)
        # translucent paper: a sheet edge-on to the torch still glows a little; a sheet facing the torch is full
        return (0.30 + 0.80 * d ** 0.8).astype(F32)

    def draw(self, f, th, bend=0.0, twist=0.0, amp=0.0, phase=0.0, shadow=0.45):
        """Composite the leaf (and its cast shadow) onto the frame f (HxWx3, authoring px) in place."""
        H, W = f.shape[:2]
        X, Y, Z, phi = self.geometry(th, bend, twist, amp, phase)
        N = self.normals(X, Y, Z)
        nu, nv = self.nu, self.nv
        SX, SY = self.project(X, Y, Z)
        # ---- cast shadow on the page below: vertices moved along the torch ray to the page plane
        lx, ly, lz = self.l
        ZZ = np.maximum(Z, 0)
        shx, shy = X + ZZ * lx / lz * 1.6, Y + ZZ * ly / lz * 1.6
        pX, pY = self.project(shx, shy, 0 * Z)
        sh = np.zeros((H, W), F32)
        for i in range(nv):
            for j in range(nu):
                zq = float(ZZ[i:i + 2, j:j + 2].mean())
                if zq < 0.5:
                    continue
                q = np.array([[pX[i, j], pY[i, j]], [pX[i, j + 1], pY[i, j + 1]], [pX[i + 1, j + 1], pY[i + 1, j + 1]],
                              [pX[i + 1, j], pY[i + 1, j]]], F32)
                w = math.exp(-zq / (0.30 * self.lw))
                cv2.fillConvexPoly(sh, np.round(q * 8).astype(np.int32), float(w), shift=3)
        zm = float(ZZ.mean())
        sh = cv2.GaussianBlur(sh, (0, 0), 3.0 + 0.020 * zm + 0.010 * self.lw * 0.1)
        f *= (1 - shadow * np.clip(sh, 0, 1))[..., None]
        # ---- the leaf layer, supersampled
        LW, LH = W * SS, H * SS
        # only the bounding box of the mesh
        x0 = int(max(0, math.floor(SX.min() - 4))); x1 = int(min(W, math.ceil(SX.max() + 4)))
        y0 = int(max(0, math.floor(SY.min() - 4))); y1 = int(min(H, math.ceil(SY.max() + 4)))
        if x1 - x0 < 2 or y1 - y0 < 2:
            return f
        bw, bh = (x1 - x0) * SS, (y1 - y0) * SS
        layer = np.zeros((bh, bw, 3), F32)
        alpha = np.zeros((bh, bw), np.uint8)
        gx = (SX - x0) * SS
        gy = (SY - y0) * SS
        # per-face shading baked into the textures
        shF = self.shade(N, +1)          # (nv+1, nu+1)
        shB = self.shade(N, -1)
        th_, tw_ = self.front.shape[:2]
        texF = self.front * cv2.resize(shF, (tw_, th_), interpolation=cv2.INTER_LINEAR)[..., None]
        texB = self.back * cv2.resize(shB, (tw_, th_), interpolation=cv2.INTER_LINEAR)[..., None]
        # triangles
        tris = []
        for i in range(nv):
            for j in range(nu):
                zc = float(Z[i:i + 2, j:j + 2].mean())
                nz = float(N[i:i + 2, j:j + 2, 2].mean())
                tris.append((zc, i, j, nz))
        tris.sort(key=lambda t: t[0])
        for zc, i, j, nz in tris:
            front_face = nz > 0
            # screen quad
            qs = np.array([[gx[i, j], gy[i, j]], [gx[i, j + 1], gy[i, j + 1]], [gx[i + 1, j + 1], gy[i + 1, j + 1]],
                           [gx[i + 1, j], gy[i + 1, j]]], F32)
            # texture coords of the quad corners (u across the width = a/lw, v down)
            u0, u1 = j / nu, (j + 1) / nu
            v0, v1 = i / nv, (i + 1) / nv
            if front_face:                 # front: spine at the texture's right edge
                tu0, tu1 = 1 - u0, 1 - u1
                tex = texF
            else:                          # back: spine at the texture's left edge
                tu0, tu1 = u0, u1
                tex = texB
            tq = np.array([[tu0 * tw_, v0 * th_], [tu1 * tw_, v0 * th_], [tu1 * tw_, v1 * th_], [tu0 * tw_, v1 * th_]], F32)
            c = qs.mean(0)
            qd = c + (qs - c) * 1.06 + 0.0          # a hair larger: no cracks between quads
            for tri in ((0, 1, 2), (0, 2, 3)):
                dst = qd[list(tri)]
                src = tq[list(tri)]
                bx0, by0 = np.floor(dst.min(0)).astype(int) - 1
                bx1, by1 = np.ceil(dst.max(0)).astype(int) + 2
                bx0, by0, bx1, by1 = max(bx0, 0), max(by0, 0), min(bx1, bw), min(by1, bh)
                if bx1 - bx0 < 1 or by1 - by0 < 1:
                    continue
                M = cv2.getAffineTransform(src, (dst - np.float32([bx0, by0])).astype(F32))
                patch = cv2.warpAffine(tex, M, (bx1 - bx0, by1 - by0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                m = np.zeros((by1 - by0, bx1 - bx0), np.uint8)
                cv2.fillConvexPoly(m, np.round((dst - np.float32([bx0, by0])) * 16).astype(np.int32), 255, shift=4)
                mm = m > 0
                layer[by0:by1, bx0:bx1][mm] = patch[mm]
                alpha[by0:by1, bx0:bx1][mm] = 255
        a = cv2.resize(alpha.astype(F32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        rgb = cv2.resize(layer, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
        # un-premultiply the edge: layer is zero outside, so rgb is premultiplied by coverage
        reg = f[y0:y1, x0:x1]
        reg[:] = reg * (1 - a[..., None]) + rgb
        return f


def dust_motes(f, t, ctx, DUST, centre=(0.5, 0.53), spread=(0.33, 0.45)):
    """Specks turning in the torch beam, brightest where the pool is."""
    W, H = ctx.W, ctx.H
    cx, cy = W * centre[0], H * centre[1]
    sp = np.zeros((H, W), np.float32)
    for x, y, v, sz, ph, dr in DUST:
        px = (x * 1.2 - 0.1) * W + 14 * ctx.s * math.sin(0.6 * t + ph * 6.28) + dr * 8 * ctx.s * t
        py = ((y - 0.03 * v * t * 4 + 4) % 1.0) * H
        px = px % W
        r2 = ((px - cx) / (W * spread[0])) ** 2 + ((py - cy) / (H * spread[1])) ** 2
        a = math.exp(-r2) * (0.25 + 0.75 * (0.5 + 0.5 * math.sin(2.1 * t + ph * 9)))
        cv2.circle(sp, (int(px), int(py)), max(1, int(round((0.8 + 1.4 * sz) * ctx.s))), float(a * 0.55), -1, cv2.LINE_AA)
    sp = blur(sp, 0.7 * ctx.s)
    f += sp[..., None] * np.float32([1.0, 0.93, 0.78])[None, None] * 0.55
    return np.clip(f, 0, 1)

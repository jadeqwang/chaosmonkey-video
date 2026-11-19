// Terrain: an analytic heightfield of steep Huangshan-like granite pillars and ridges around one high central peak
// with a flat ledge (the root's) on its camera-facing (+z) side. Metres, y up.
import * as THREE from 'three';
import { makeNoise, hash2, clamp, lerp, smoothstep } from './rng.js';

export const TERRAIN_DEFAULTS = {
  seed: 7,
  extent: 5000,          // half-size of the mesh (m); the range itself sits inside `core`
  core: 2100,
  grid: 1280,            // vertices per side (the grid is warped: dense at the ledge, coarse at the rim)
  warp: 0.06,
  floor: -25,
  massif: { h: 560, r: 1850, freq: 0.0013, sharp: 1.25, warp: 300, mesa: [0.12, 0.85] },
  columns: [              // Voronoi columns (granite joints): cell size, height jitter, crack depth/width, dome
    { cell: 130, jit: 0.55, crack: 190, crackw: 17, dome: 55 },
    { cell: 45, jit: 0.3, crack: 35, crackw: 5, dome: 14 },
  ],
  spires: { cell: 150, p: 0.7, h: [170, 420], rad: 36 },
  terrace: { step: 11, amount: 0.25 },
  peak: { x: 0, z: 0, h: 735, r: 46 },
  ledge: { dx: 6, dz: 44, drop: 32, r: 7, blend: 4, col_r: 11 },
};

export function makeTerrain(cfg) {
  const P = deepMerge(structuredClone(TERRAIN_DEFAULTS), cfg || {});
  const N1 = makeNoise(P.seed), N2 = makeNoise(P.seed + 101), N3 = makeNoise(P.seed + 202);
  const pk = P.peak, L = P.ledge, MS = P.massif;
  const ledgeX = pk.x + L.dx, ledgeZ = pk.z + L.dz;
  const ledgeY = pk.h - L.drop;
  function smax(a, b, k) { const h = clamp(0.5 + 0.5 * (b - a) / k, 0, 1); return lerp(a, b, h) + k * h * (1 - h); }

  // the massif: ridges radiating from the central peak, sharpened, falling off to a cloud sea
  function massif(x, z) {
    const wx = x + MS.warp * N1.fbm(x * 0.0008, z * 0.0008, 3), wz = z + MS.warp * N1.fbm(x * 0.0008 + 5.2, z * 0.0008 + 1.3, 3);
    const r = Math.hypot(x - pk.x, z - pk.z);
    const mass = Math.exp(-Math.pow(r / MS.r, 2.4));
    const rid = Math.pow(N2.ridged(wx * MS.freq, wz * MS.freq, 4), MS.sharp);
    const big = 0.6 + 0.4 * N3.fbm(x * 0.0006, z * 0.0006, 2);
    const m = mass * (0.15 + 0.95 * rid * big) + 0.35 * Math.exp(-Math.pow(r / 330, 2));
    // mesa steepening: slopes become cliffs, tops become benches
    const st = smoothstep(MS.mesa[0], MS.mesa[1], m);
    return MS.h * (0.65 * st + 0.35 * m);
  }
  // Voronoi: nearest two feature points (F1, F2) and the nearest cell's centre
  function vor(x, z, c, seed) {
    const ci = Math.floor(x / c), cj = Math.floor(z / c);
    let f1 = 1e9, f2 = 1e9, bx = 0, bz = 0, bi = 0, bj = 0;
    for (let i = ci - 1; i <= ci + 1; i++) for (let j = cj - 1; j <= cj + 1; j++) {
      const px = (i + 0.1 + 0.8 * hash2(i, j, seed)) * c, pz = (j + 0.1 + 0.8 * hash2(i, j, seed + 1)) * c;
      const d = Math.hypot(x - px, z - pz);
      if (d < f1) { f2 = f1; f1 = d; bx = px; bz = pz; bi = i; bj = j; } else if (d < f2) f2 = d;
    }
    return { f1, f2, bx, bz, bi, bj };
  }
  function raw(x, z) {
    const r = Math.hypot(x - pk.x, z - pk.z);
    const wx = x + 12 * N1.n2(x * 0.02, z * 0.02), wz = z + 12 * N1.n2(x * 0.02 + 3.3, z * 0.02 + 7.1);
    let h = P.floor + 20 * N2.fbm(x * 0.003, z * 0.003, 3) - 60 * smoothstep(P.core, P.core * 1.6, r);
    // columns: each Voronoi cell a granite column whose height samples the massif at its centre
    let colH = massif(x, z);
    P.columns.forEach((C, k) => {
      const v = vor(wx, wz, C.cell, P.seed * 13 + k * 101);
      const base = k === 0 ? massif(v.bx, v.bz) : colH;
      const jit = 1 - C.jit * Math.pow(hash2(v.bi, v.bj, P.seed + k * 7 + 5), 0.7);
      const pkd = hash2(v.bi, v.bj, P.seed + k * 7 + 9);
      let ch = base * jit - C.dome * (pkd < 0.4 ? 2.4 * v.f1 / C.cell : 2 * Math.pow(v.f1 / C.cell, 2));
      const e = v.f2 - v.f1;
      ch -= C.crack * (1 - smoothstep(0, C.crackw, e)) * smoothstep(40, 200, base);
      colH = k === 0 ? ch : lerp(colH, Math.min(colH, ch + C.dome), 0.85) - C.crack * 0.4 * (1 - smoothstep(0, C.crackw, e)) * smoothstep(60, 250, base);
    });
    h = Math.max(h, colH);
    // free-standing spires
    {
      const S = P.spires, c = S.cell, ci = Math.floor(x / c), cj = Math.floor(z / c);
      for (let i = ci - 1; i <= ci + 1; i++) for (let j = cj - 1; j <= cj + 1; j++) {
        if (hash2(i, j, P.seed + 900) > S.p) continue;
        const px = (i + 0.2 + 0.6 * hash2(i, j, P.seed + 901)) * c, pz = (j + 0.2 + 0.6 * hash2(i, j, P.seed + 902)) * c;
        const pr = Math.hypot(px - pk.x, pz - pk.z); if (pr > P.core * 0.95 || pr < 120) continue;
        const dx = x - px, dz = z - pz, dl = Math.hypot(dx, dz) + 1e-6;
        const rr = S.rad * (0.6 + 0.8 * hash2(i, j, P.seed + 903));
        const fl = 1 + 0.18 * N3.n2(dx / dl * 3 + i, dz / dl * 3 + j);
        const t = dl / rr * fl;
        if (t > 1.15) continue;
        const hp = lerp(S.h[0], S.h[1], hash2(i, j, P.seed + 904)) * (0.4 + 0.6 * Math.exp(-Math.pow(pr / MS.r, 2)));
        const top = massif(px, pz) * 0.5 + hp;
        h = Math.max(h, top * (1 - 0.06 * t * t) * (1 - smoothstep(0.75, 1.0, t)) + h * smoothstep(0.75, 1.0, t));
      }
    }
    // the summit: a cluster of tall columns
    {
      const dx = x - pk.x, dz = z - pk.z, dl = Math.hypot(dx, dz) + 1e-6;
      const fl = 1 + 0.12 * N3.n2(dx / dl * 3 + 9, dz / dl * 3 + 2) + 0.06 * N3.n2(dx / dl * 9, dz / dl * 9);
      const t = dl / pk.r * fl;
      const v = vor(x, z, 22, P.seed + 444);
      const top = pk.h * (1 - 0.13 * hash2(v.bi, v.bj, 5)) - 8 * (1 - smoothstep(0, 2.5, v.f2 - v.f1)) - 9 * t * t;
      const sk = 1 - smoothstep(0.7, 1.0, t);
      h = Math.max(h, lerp(h, top, sk));
      // shoulder below the ledge side
      const sd = Math.hypot(x - (pk.x + L.dx * 1.4), z - (pk.z + L.dz * 1.9)) / (pk.r * 1.25) * fl;
      const s2 = 1 - smoothstep(0.65, 1.0, sd);
      h = Math.max(h, lerp(h, pk.h * 0.72 - 10 * sd * sd, s2));
    }
    // the ledge: a lower column top against the summit wall
    {
      const d = Math.hypot(x - ledgeX, z - ledgeZ) * (1 + 0.1 * N3.n2((x - ledgeX) * 0.3, (z - ledgeZ) * 0.3));
      const t = d / L.col_r;
      const top = ledgeY - 0.8 * t * t;
      h = Math.max(h, lerp(h, top, 1 - smoothstep(0.8, 1.05, t)));
    }
    void r;
    // terracing (soft), keeps column tops walkable
    if (P.terrace && P.terrace.amount > 0) {
      const T = P.terrace.step * (1 + 0.3 * N2.n2(x * 0.01, z * 0.01));
      const q = h / T, f = q - Math.floor(q);
      const hq = (Math.floor(q) + smoothstep(0.75, 1.0, f)) * T;
      h = lerp(h, hq, P.terrace.amount * smoothstep(20, 80, h));
    }
    return h;
  }
  function height(x, z) {
    let h = raw(x, z);
    const d = Math.hypot(x - ledgeX, z - ledgeZ);
    if (d < L.r) h = lerp(h, ledgeY + 0.15 * N3.n2(x * 0.8, z * 0.8), 1 - smoothstep(L.r - L.blend, L.r, d));
    return h;
  }

  // ---- mesh (warped grid, dense at the ledge)
  function buildMesh() {
    const N = P.grid, E = P.extent, a = P.warp;
    const pos = new Float32Array(N * N * 3);
    const wrp = (u) => E * (a * u + (1 - a) * u * u * u);
    for (let j = 0; j < N; j++) {
      const z = ledgeZ + wrp(j / (N - 1) * 2 - 1);
      for (let i = 0; i < N; i++) {
        const x = ledgeX + wrp(i / (N - 1) * 2 - 1);
        const o = (j * N + i) * 3;
        pos[o] = x; pos[o + 1] = height(x, z); pos[o + 2] = z;
      }
    }
    const idx = new Uint32Array((N - 1) * (N - 1) * 6);
    let k = 0;
    for (let j = 0; j < N - 1; j++) for (let i = 0; i < N - 1; i++) {
      const a0 = j * N + i, b0 = a0 + 1, c0 = a0 + N, d0 = c0 + 1;
      // split along the shorter diagonal in height (fewer slivers on walls)
      if (Math.abs(pos[a0 * 3 + 1] - pos[d0 * 3 + 1]) < Math.abs(pos[b0 * 3 + 1] - pos[c0 * 3 + 1])) {
        idx[k++] = a0; idx[k++] = c0; idx[k++] = d0; idx[k++] = a0; idx[k++] = d0; idx[k++] = b0;
      } else { idx[k++] = a0; idx[k++] = c0; idx[k++] = b0; idx[k++] = b0; idx[k++] = c0; idx[k++] = d0; }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setIndex(new THREE.BufferAttribute(idx, 1));
    g.computeVertexNormals();
    g.computeBoundingSphere();
    return g;
  }

  function normal(x, z, e = 1.0) {
    const hx = height(x + e, z) - height(x - e, z), hz = height(x, z + e) - height(x, z - e);
    const n = new THREE.Vector3(-hx, 2 * e, -hz); return n.normalize();
  }
  // march a ray into the heightfield; returns Vector3 or null
  function raycast(o, d, maxT = 20000) {
    let t = 0, prevT = 0;
    for (let it = 0; it < 4000 && t < maxT; it++) {
      const x = o.x + d.x * t, y = o.y + d.y * t, z = o.z + d.z * t;
      const dh = y - height(x, z);
      if (dh < 0) {
        let lo = prevT, hi = t;
        for (let b = 0; b < 24; b++) {
          const m = 0.5 * (lo + hi);
          if (o.y + d.y * m - height(o.x + d.x * m, o.z + d.z * m) < 0) hi = m; else lo = m;
        }
        return new THREE.Vector3(o.x + d.x * hi, o.y + d.y * hi, o.z + d.z * hi);
      }
      prevT = t;
      t += clamp(dh * 0.3, 0.4, 30);
    }
    return null;
  }
  return { P, height, normal, raycast, buildMesh, ledge: new THREE.Vector3(ledgeX, ledgeY, ledgeZ) };
}

export function deepMerge(a, b) {
  for (const k of Object.keys(b)) {
    if (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k] && typeof a[k] === 'object' && !Array.isArray(a[k])) deepMerge(a[k], b[k]);
    else a[k] = b[k];
  }
  return a;
}

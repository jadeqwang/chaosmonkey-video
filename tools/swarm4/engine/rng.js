// Seeded randomness and CPU noise. Everything in the engine is a pure function of (cand, frame).
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function hash2(i, j, seed = 0) {
  let h = (Math.imul(i | 0, 374761393) + Math.imul(j | 0, 668265263) + Math.imul(seed | 0, 2246822519)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
export const hash1 = (i, seed = 0) => hash2(i, 0x51ed, seed);

const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
// 2D gradient noise in [-1, 1]
export function makeNoise(seed) {
  const rnd = mulberry32(seed);
  const perm = new Uint16Array(512);
  const p = [...Array(256).keys()];
  for (let i = 255; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
  for (let i = 0; i < 512; i++) perm[i] = p[i & 255];
  const gx = new Float32Array(256), gy = new Float32Array(256);
  for (let i = 0; i < 256; i++) { const a = rnd() * Math.PI * 2; gx[i] = Math.cos(a); gy[i] = Math.sin(a); }
  function n2(x, y) {
    const xi = Math.floor(x), yi = Math.floor(y);
    const xf = x - xi, yf = y - yi;
    const X = xi & 255, Y = yi & 255;
    const a = perm[X + perm[Y]], b = perm[X + 1 + perm[Y]], c = perm[X + perm[Y + 1]], d = perm[X + 1 + perm[Y + 1]];
    const u = fade(xf), v = fade(yf);
    const va = gx[a] * xf + gy[a] * yf, vb = gx[b] * (xf - 1) + gy[b] * yf;
    const vc = gx[c] * xf + gy[c] * (yf - 1), vd = gx[d] * (xf - 1) + gy[d] * (yf - 1);
    return 1.414 * ((va + u * (vb - va)) + v * ((vc + u * (vd - vc)) - (va + u * (vb - va))));
  }
  function fbm(x, y, oct = 4, lac = 2.03, gain = 0.5) {
    let s = 0, a = 1, f = 1, n = 0;
    for (let i = 0; i < oct; i++) { s += a * n2(x * f + i * 17.3, y * f - i * 9.1); n += a; a *= gain; f *= lac; }
    return s / n;
  }
  function ridged(x, y, oct = 4) {
    let s = 0, a = 1, f = 1, n = 0;
    for (let i = 0; i < oct; i++) { const r = 1 - Math.abs(n2(x * f + i * 31.7, y * f + i * 5.3)); s += a * r * r; n += a; a *= 0.5; f *= 2.1; }
    return s / n;
  }
  return { n2, fbm, ridged };
}

export const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

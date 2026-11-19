// The 亮相 silhouette mask (alpha), its sampling (blue noise, denser along the outline).
import { mulberry32 } from './rng.js';

const SZ = 512;

// placeholder: Sun Wukong in 亮相 (golden-rooster stance, hand shading the eyes, staff held across, pheasant plumes, tail)
export function drawPlaceholderSilhouette() {
  const c = document.createElement('canvas'); c.width = c.height = SZ;
  const g = c.getContext('2d');
  g.fillStyle = '#000'; g.strokeStyle = '#000'; g.lineCap = 'round'; g.lineJoin = 'round';
  const S = SZ / 1000; g.save(); g.scale(S, S); g.translate(10, 15);
  const limb = (pts, w) => { g.lineWidth = w; g.beginPath(); g.moveTo(...pts[0]); for (const p of pts.slice(1)) g.lineTo(...p); g.stroke(); };
  const curve = (p0, c1, c2, p1, w0, w1, n = 24) => {          // tapered bezier stroke
    for (let i = 0; i < n; i++) {
      const t = i / n, t2 = (i + 1) / n;
      const B = (t) => [0, 1].map((k) => (1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * c1[k] + 3 * (1 - t) * t * t * c2[k] + t ** 3 * p1[k]);
      g.lineWidth = w0 + (w1 - w0) * t; g.beginPath(); g.moveTo(...B(t)); g.lineTo(...B(t2)); g.stroke();
    }
  };
  // staff, diagonal behind the body
  limb([[95, 640], [455, 70]], 15);
  // pheasant plumes arching back
  curve([500, 95], [430, -40], [300, -10], [180, 90], 16, 4);
  curve([540, 95], [620, -50], [760, -30], [850, 80], 16, 4);
  // head, cap, ears
  g.beginPath(); g.ellipse(520, 150, 62, 70, 0, 0, Math.PI * 2); g.fill();
  g.beginPath(); g.ellipse(456, 160, 20, 16, 0, 0, Math.PI * 2); g.fill();
  g.beginPath(); g.ellipse(585, 158, 20, 16, 0, 0, Math.PI * 2); g.fill();
  // neck + torso (chest out), tiger-skin skirt flaring
  g.beginPath(); g.moveTo(470, 205); g.lineTo(590, 205); g.lineTo(625, 260); g.lineTo(590, 450); g.lineTo(480, 455); g.lineTo(440, 260); g.closePath(); g.fill();
  g.beginPath(); g.moveTo(468, 440); g.lineTo(600, 440); g.lineTo(655, 575); g.lineTo(575, 560); g.lineTo(520, 590); g.lineTo(455, 560); g.lineTo(415, 575); g.closePath(); g.fill();
  // standing leg
  limb([[490, 540], [470, 745], [485, 925]], 50);
  limb([[485, 925], [415, 960]], 34);
  // raised leg: thigh forward-up, shin hanging, foot pointed
  limb([[575, 540], [715, 585]], 54);
  limb([[715, 585], [650, 760]], 40);
  limb([[650, 760], [600, 790]], 26);
  // arm shading the eyes
  limb([[600, 235], [735, 205], [600, 120]], 34);
  g.beginPath(); g.ellipse(585, 112, 34, 16, -0.25, 0, Math.PI * 2); g.fill();
  // arm holding the staff out
  limb([[455, 240], [350, 330], [290, 285]], 34);
  g.beginPath(); g.arc(285, 285, 24, 0, Math.PI * 2); g.fill();
  // tail
  curve([585, 515], [730, 560], [860, 470], [790, 340], 22, 9);
  g.restore();
  return c;
}

// mask: { w, h, a: Float32Array (0..1), canvas }
export async function loadMask(url, invert = false) {
  let c;
  if (url) {
    try {
      const img = new Image(); img.src = url; await img.decode();
      c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
      c.getContext('2d').drawImage(img, 0, 0);
    } catch (e) { console.warn('[swarm] silhouette ' + url + ' not loaded, placeholder'); c = null; }
  }
  const placeholder = !c;
  if (!c) c = drawPlaceholderSilhouette();
  const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
  const a = new Float32Array(c.width * c.height);
  // alpha if the image has any transparency, else darkness (black figure on white)
  let hasAlpha = false; for (let i = 3; i < d.length; i += 4) if (d[i] < 250) { hasAlpha = true; break; }
  // no alpha: the figure is whichever tone the border is not
  let border = 0, nb = 0;
  for (let x = 0; x < c.width; x++) for (const y of [0, c.height - 1]) { const i = (y * c.width + x) * 4; border += d[i] + d[i + 1] + d[i + 2]; nb++; }
  const darkBg = border / nb / 765 < 0.5;
  for (let i = 0; i < a.length; i++) {
    const lum = (d[i * 4] + d[i * 4 + 1] + d[i * 4 + 2]) / 765;
    a[i] = hasAlpha ? d[i * 4 + 3] / 255 : darkBg ? lum : 1 - lum;
  }
  if (invert) for (let i = 0; i < a.length; i++) a[i] = 1 - a[i];
  return { w: c.width, h: c.height, a, canvas: c, placeholder };
}

export function maskAt(m, u, v, dil = 0) {          // u, v in 0..1 (v down)
  if (u < 0 || v < 0 || u > 1 || v > 1) return 0;
  if (!dil) return m.a[Math.min(m.h - 1, Math.floor(v * m.h)) * m.w + Math.min(m.w - 1, Math.floor(u * m.w))];
  let mx = 0; const r = dil;
  for (let k = 0; k < 9; k++) { const a = k / 9 * Math.PI * 2; mx = Math.max(mx, maskAt(m, u + Math.cos(a) * r, v + Math.sin(a) * r)); }
  return Math.max(mx, maskAt(m, u, v));
}

// N points (u, v) inside the mask, a fraction `edgeFrac` of them on the outline band; blue noise (best candidate)
export function sampleMask(m, N, edgeFrac, seed, edgePx = 2.5) {
  const rnd = mulberry32(seed);
  const inside = [], edge = [];
  const R = Math.max(1, Math.round(edgePx * m.w / 512));
  for (let y = 0; y < m.h; y++) for (let x = 0; x < m.w; x++) {
    if (m.a[y * m.w + x] < 0.5) continue;
    let isE = false;
    for (let dy = -R; dy <= R && !isE; dy++) for (let dx = -R; dx <= R; dx++) {
      const xx = x + dx, yy = y + dy;
      if (xx < 0 || yy < 0 || xx >= m.w || yy >= m.h || m.a[yy * m.w + xx] < 0.5) { isE = true; break; }
    }
    (isE ? edge : inside).push([(x + 0.5) / m.w, (y + 0.5) / m.h]);
  }
  const pts = [];
  const pick = (pool, n, k) => {
    for (let i = 0; i < n; i++) {
      let best = null, bd = -1;
      for (let c = 0; c < k; c++) {
        const q = pool[Math.floor(rnd() * pool.length)];
        let dmin = 1e9;
        for (const p of pts) { const d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2; if (d < dmin) dmin = d; }
        if (dmin > bd) { bd = dmin; best = q; }
      }
      pts.push([best[0] + (rnd() - 0.5) / m.w, best[1] + (rnd() - 0.5) / m.h, pool === edge ? 1 : 0]);
    }
  };
  const nE = Math.round(N * edgeFrac);
  pick(edge, nE, 6);
  pick(inside, N - nE, 10);
  return pts;
}

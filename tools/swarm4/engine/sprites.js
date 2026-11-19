// Monkey sprites: placeholder figures drawn in canvas (until media/swarm4/sprites/sprites.json exists), packed into
// one atlas for the crowd; full-resolution single textures for the two heroes (root, second).
import * as THREE from 'three';

export const JOB_KEYS = { '读': 'read', '写': 'write', '算': 'reckon', '运': 'carry', '战': 'spar', '扫': 'sweep', '望': 'watch', '磨': 'grind' };
export const SPECIAL = ['stand', 'point', 'pluck', 'blow', 'sit', 'land', 'seal'];
export const DEFAULT_POSE_MAP = { stand: 'watch_B', point: 'liangxiang_q34', pluck: 'pluck', blow: 'blow', sit: 'seated_q34', land: 'land', seal: 'seal',
  read_0: 'read_A', read_1: 'read_B', write_0: 'write_A', write_1: 'write_B', reckon_0: 'abacus_A', reckon_1: 'abacus_B', carry_0: 'carry_A', carry_1: 'carry_B',
  spar_0: 'spar_A', spar_1: 'spar_B', sweep_0: 'sweep_A', sweep_1: 'sweep_B', watch_0: 'watch_A', watch_1: 'watch_B', grind_0: 'grind_A', grind_1: 'grind_B' };

const D = Math.PI / 180;
// pose table: arm angles (deg, 0 = straight down, + = forward/up toward the facing side), elbow bend, prop
const POSES = {
  stand: { a: [10, 20], e: [10, 15], lean: 0 }, land: { a: [40, 60], e: [10, 15], lean: 20 }, seal: { a: [40, 20], e: [30, 15], lean: 25 },
  point: { a: [95, 15], e: [5, 20], lean: 4 },
  pluck: { a: [160, 20], e: [70, 15], lean: -3 },
  blow: { a: [120, 30], e: [110, 20], lean: 6, blow: true },
  sit: { a: [60, 50], e: [60, 70], lean: 0, sit: true, palm: true },
  read_0: { a: [70, 60], e: [60, 60], prop: 'book' }, read_1: { a: [50, 75], e: [70, 40], prop: 'book', lean: 5 },
  write_0: { a: [100, 30], e: [40, 30], prop: 'brush' }, write_1: { a: [55, 30], e: [50, 30], prop: 'brush', lean: 8 },
  reckon_0: { a: [65, 65], e: [55, 55], prop: 'abacus' }, reckon_1: { a: [80, 50], e: [40, 70], prop: 'abacus', lean: 3 },
  carry_0: { a: [170, 150], e: [30, 40], prop: 'box', lean: -2 }, carry_1: { a: [120, 110], e: [80, 90], prop: 'box', lean: 6 },
  spar_0: { a: [80, 40], e: [80, 30], prop: 'staff', lean: -4 }, spar_1: { a: [100, 90], e: [0, 10], prop: 'staff', lean: 12 },
  sweep_0: { a: [40, 20], e: [30, 20], prop: 'broom', lean: 8 }, sweep_1: { a: [-20, -30], e: [30, 20], prop: 'broom', lean: -4 },
  watch_0: { a: [150, 15], e: [120, 15], prop: 'brow', lean: 3 }, watch_1: { a: [100, 15], e: [0, 15], prop: 'point', lean: 6 },
  grind_0: { a: [80, 80], e: [20, 20], prop: 'mill', lean: 18 }, grind_1: { a: [70, 70], e: [70, 70], prop: 'mill', lean: 4 },
};

// draw one monkey facing right into ctx; the figure's feet at (W/2, H*0.95), height H*0.88
export function drawMonkey(g, W, H, name, seed = 0) {
  const P = POSES[name] || POSES.stand;
  const u = H / 100;          // 1 unit = 1 % of the cell height
  const fx = W / 2, fy = H * 0.95;
  g.save(); g.translate(fx, fy); g.scale(u, u);
  g.lineJoin = 'round'; g.lineCap = 'round';
  const INK = '#15100c', FUR = '#a8743c', FURD = '#6e4524', FACE = '#e6b88a', RED = '#a8362a', GOLD = '#e0b050', CLOTH = '#2f5d58';
  const lean = (P.lean || 0) * D;
  const hipY = P.sit ? -14 : -38, hipX = 0;
  const sh = [hipX + Math.sin(lean) * 26, hipY - Math.cos(lean) * 26];
  const head = [sh[0] + Math.sin(lean) * 10 + 2, sh[1] - 12];
  const stroke = (w, c) => { g.lineWidth = w; g.strokeStyle = c; };
  // tail (behind)
  stroke(4.5, INK); g.beginPath(); g.moveTo(hipX - 4, hipY + 2); g.bezierCurveTo(-22, hipY + 6, -30, hipY - 20, -18, hipY - 30); g.stroke();
  stroke(2.6, FUR); g.stroke();
  // legs
  const leg = (dx, k) => {
    let knee, foot;
    if (P.sit) { knee = [hipX + dx * 2 + (k ? 14 : -10), hipY + 4]; foot = [hipX + (k ? -6 : 8), hipY + 10]; }
    else { knee = [hipX + dx + 3, hipY + 19]; foot = [hipX + dx + 1, -2]; }
    stroke(8.5, INK); g.beginPath(); g.moveTo(hipX + dx, hipY); g.lineTo(...knee); g.lineTo(...foot); g.stroke();
    stroke(6, FURD); g.stroke();
    stroke(3.2, INK); g.beginPath(); g.moveTo(foot[0] - 1, foot[1]); g.lineTo(foot[0] + 6, foot[1] + 0.5); g.stroke();
  };
  leg(-4, 0); leg(4, 1);
  // body: tunic + tiger skirt
  g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 1.6;
  g.beginPath();
  g.moveTo(sh[0] - 9, sh[1] + 1); g.lineTo(sh[0] + 9, sh[1] + 1); g.lineTo(hipX + 10, hipY + 2); g.lineTo(hipX - 10, hipY + 2); g.closePath(); g.fill(); g.stroke();
  g.fillStyle = '#c8903c'; g.beginPath(); g.moveTo(hipX - 11, hipY - 2); g.lineTo(hipX + 11, hipY - 2); g.lineTo(hipX + 13, hipY + 9); g.lineTo(hipX - 13, hipY + 9); g.closePath(); g.fill(); g.stroke();
  g.strokeStyle = INK; g.lineWidth = 1.2; for (let i = -9; i <= 9; i += 4.5) { g.beginPath(); g.moveTo(hipX + i, hipY - 1); g.lineTo(hipX + i + 1.5, hipY + 7); g.stroke(); }
  g.fillStyle = CLOTH; g.fillRect(hipX - 10.5, hipY - 3.5, 21, 3);
  // arms (back arm first)
  const arm = (k) => {
    const a = (P.a[k]) * D, e = (P.e[k]) * D;
    const s0 = [sh[0] + (k ? -5 : 5), sh[1] + 3];
    const el = [s0[0] + Math.sin(a) * 12, s0[1] + Math.cos(a) * 12];
    const hd = [el[0] + Math.sin(a + e) * 11, el[1] + Math.cos(a + e) * 11];
    stroke(6.5, INK); g.beginPath(); g.moveTo(...s0); g.lineTo(...el); g.lineTo(...hd); g.stroke();
    stroke(4.4, k ? FURD : FUR); g.stroke();
    g.fillStyle = FACE; g.beginPath(); g.arc(hd[0], hd[1], 2.4, 0, Math.PI * 2); g.fill(); g.strokeStyle = INK; g.lineWidth = 1; g.stroke();
    return hd;
  };
  const hb = arm(1);
  // head: fur, face, gold circlet, ears
  g.fillStyle = FUR; g.strokeStyle = INK; g.lineWidth = 1.8;
  g.beginPath(); g.ellipse(head[0], head[1], 9, 10, 0, 0, Math.PI * 2); g.fill(); g.stroke();
  g.fillStyle = FACE; g.beginPath(); g.ellipse(head[0] + 3.5, head[1] + 2, 5.2, 6.2, 0.15, 0, Math.PI * 2); g.fill(); g.stroke();
  g.fillStyle = INK; g.beginPath(); g.arc(head[0] + 5, head[1] - 0.5, 1.1, 0, Math.PI * 2); g.fill();
  g.beginPath(); g.ellipse(head[0] - 7, head[1] + 1, 2.4, 3.2, 0, 0, Math.PI * 2); g.fillStyle = FACE; g.fill(); g.stroke();
  g.strokeStyle = GOLD; g.lineWidth = 2.4; g.beginPath(); g.ellipse(head[0], head[1] - 3, 9.2, 3, 0, Math.PI * 1.05, Math.PI * 1.95, false); g.stroke();
  g.strokeStyle = INK; g.lineWidth = 0.8; g.stroke();
  if (P.blow) { g.strokeStyle = '#d8d2c0'; g.lineWidth = 1; for (let i = 0; i < 4; i++) { g.beginPath(); g.moveTo(head[0] + 10, head[1] + 3 + i * 0.6); g.quadraticCurveTo(head[0] + 18, head[1] - 2 + i * 2, head[0] + 26, head[1] - 6 + i * 3); g.stroke(); } }
  const hf = arm(0);
  // props
  g.strokeStyle = INK; g.lineWidth = 1.6;
  const prop = P.prop;
  if (prop === 'book') { g.fillStyle = '#e8dcc0'; g.save(); g.translate((hf[0] + hb[0]) / 2 + 2, (hf[1] + hb[1]) / 2 - 2); g.rotate(-0.3); g.fillRect(-7, -5, 14, 9); g.strokeRect(-7, -5, 14, 9); g.beginPath(); g.moveTo(0, -5); g.lineTo(0, 4); g.stroke(); g.restore(); }
  if (prop === 'brush') { g.lineWidth = 1.8; g.beginPath(); g.moveTo(hf[0] - 2, hf[1] + 4); g.lineTo(hf[0] + 3, hf[1] - 12); g.stroke(); g.fillStyle = INK; g.beginPath(); g.ellipse(hf[0] - 2.5, hf[1] + 5, 1.4, 3, 0.3, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#e8dcc0'; g.fillRect(8, -16, 16, 3); g.strokeRect(8, -16, 16, 3); }
  if (prop === 'abacus') { g.save(); g.translate((hf[0] + hb[0]) / 2 + 3, (hf[1] + hb[1]) / 2); g.fillStyle = '#5a3a20'; g.fillRect(-9, -5, 18, 10); g.strokeRect(-9, -5, 18, 10);
    g.fillStyle = '#d8c090'; for (let i = -7; i <= 7; i += 2.8) for (let j = -3; j <= 3; j += 2.2) { g.beginPath(); g.arc(i, j, 0.8, 0, Math.PI * 2); g.fill(); } g.restore(); }
  if (prop === 'box') { g.fillStyle = '#8a5a30'; g.save(); g.translate((hf[0] + hb[0]) / 2, Math.min(hf[1], hb[1]) - 5); g.fillRect(-9, -7, 18, 9); g.strokeRect(-9, -7, 18, 9); g.beginPath(); g.moveTo(-9, -3); g.lineTo(9, -3); g.stroke(); g.restore(); }
  if (prop === 'staff') { g.lineWidth = 3.2; g.strokeStyle = INK; g.beginPath(); g.moveTo(hf[0] - 22, hf[1] + 14); g.lineTo(hf[0] + 24, hf[1] - 16); g.stroke(); g.lineWidth = 1.8; g.strokeStyle = '#c03828'; g.stroke();
    g.strokeStyle = GOLD; g.lineWidth = 3.4; g.beginPath(); g.moveTo(hf[0] + 20, hf[1] - 13.4); g.lineTo(hf[0] + 24, hf[1] - 16); g.stroke(); g.beginPath(); g.moveTo(hf[0] - 18, hf[1] + 11.4); g.lineTo(hf[0] - 22, hf[1] + 14); g.stroke(); }
  if (prop === 'broom') { g.lineWidth = 2; g.beginPath(); g.moveTo(hf[0] + 3, hf[1] - 8); g.lineTo(hf[0] + 8, hf[1] + 22); g.stroke();
    g.fillStyle = '#b89a58'; g.beginPath(); g.moveTo(hf[0] + 5, hf[1] + 18); g.lineTo(hf[0] + 16, hf[1] + 30); g.lineTo(hf[0] + 1, hf[1] + 31); g.closePath(); g.fill(); g.stroke(); }
  if (prop === 'mill') { g.fillStyle = '#6a6a64'; g.beginPath(); g.ellipse(24, -6, 10, 4.5, 0, 0, Math.PI * 2); g.fill(); g.stroke(); g.fillRect(14, -6, 20, 5); g.strokeRect(14, -6, 20, 5);
    g.lineWidth = 2; g.beginPath(); g.moveTo(hf[0], hf[1]); g.lineTo(22, -9); g.stroke(); }
  if (P.palm) { g.fillStyle = FACE; g.beginPath(); g.ellipse(hf[0] + 1, hf[1] - 1, 4, 2, -0.2, 0, Math.PI * 2); g.fill(); g.stroke(); }
  g.restore();
}

export const CELL = [320, 400];
export async function buildSprites(cfg) {
  const A = cfg.assets || {};
  const loaded = {};
  let files = {};
  if (A.sprites) {
    try {
      const r = await fetch('/' + A.sprites);
      if (r.ok) {
        const js = await r.json();
        const base = A.sprites.replace(/[^/]+$/, '');
        const list = Array.isArray(js) ? js : Array.isArray(js.sprites) ? js.sprites : Object.entries(js).map(([name, v]) => (typeof v === 'string' ? { name, file: v } : { name, ...v }));
        for (const e of list) files[e.name || e.file] = { ...e, base };
      } else console.warn('[swarm] no sprites.json at ' + A.sprites + ' (placeholders)');
    } catch (e) { console.warn('[swarm] sprites: ' + e); }
  }
  const pmap = { ...DEFAULT_POSE_MAP, ...(A.pose_map || {}) };
  const facesLeft = new Set(A.faces_left || ['seated_q34', 'seated_front_never']);
  const refPx = A.ref_px || 830;        // sprite px of a standing monkey, cap to feet (same scale for every sprite)
  for (const nm of [...SPECIAL, ...Object.values(JOB_KEYS).flatMap((j) => [`${j}_0`, `${j}_1`])]) {
    const e = files[pmap[nm]] || files[nm];
    if (!e) continue;
    const img = new Image(); img.src = '/' + e.base + e.file;
    try { await img.decode(); } catch (err) { console.warn('[swarm] sprite ' + e.file + ' failed'); continue; }
    loaded[nm] = { img, anchor: e.anchor || [img.width / 2, img.height * 0.97], refPx: e.ref_px || refPx, left: e.faces === 'left' || facesLeft.has(pmap[nm] || nm) };
  }
  const names = [...SPECIAL, ...Object.values(JOB_KEYS).flatMap((j) => [`${j}_0`, `${j}_1`])];
  const cols = 8, rows = Math.ceil(names.length / cols);
  const [cw, ch] = CELL;
  const atlas = document.createElement('canvas'); atlas.width = cols * cw; atlas.height = rows * ch;
  const g = atlas.getContext('2d');
  const frames = []; const index = {};
  names.forEach((nm, i) => {
    const cx = (i % cols) * cw, cy = Math.floor(i / cols) * ch;
    const L = loaded[nm];
    let anchor = [0.5, 0.95], hfrac = 0.88;
    g.save(); g.beginPath(); g.rect(cx, cy, cw, ch); g.clip();
    if (L) {
      const sc = Math.min(cw / L.img.width, ch / L.img.height);
      const dw = L.img.width * sc, dh = L.img.height * sc, ox = cx + (cw - dw) / 2, oy = cy + (ch - dh);
      g.drawImage(L.img, ox, oy, dw, dh);
      anchor = [(ox - cx + L.anchor[0] * sc) / cw, (oy - cy + L.anchor[1] * sc) / ch];
      hfrac = L.refPx * sc / ch;
    } else { g.translate(cx, cy); drawMonkey(g, cw, ch, nm); }
    g.restore();
    index[nm] = frames.length;
    frames.push({ name: nm, rect: [cx / atlas.width, 1 - (cy + ch) / atlas.height, cw / atlas.width, ch / atlas.height], anchor, aspect: cw / ch, hfrac, loaded: !!L, left: !!(L && L.left) });
  });
  const tex = new THREE.CanvasTexture(atlas); tex.colorSpace = THREE.SRGBColorSpace; tex.generateMipmaps = true; tex.minFilter = THREE.LinearMipmapLinearFilter; tex.anisotropy = 8;
  tex.flipY = true;
  // hero textures (full res)
  const hero = {};
  for (const nm of names) {
    const L = loaded[nm];
    let c, anchor, hfrac;
    if (L) { c = L.img; anchor = [L.anchor[0] / L.img.width, L.anchor[1] / L.img.height]; hfrac = L.refPx / L.img.height; }
    else { c = document.createElement('canvas'); c.width = 820; c.height = 1024; drawMonkey(c.getContext('2d'), 820, 1024, nm); anchor = [0.5, 0.95]; hfrac = 0.88; }
    const t = new THREE.Texture(c); t.colorSpace = THREE.SRGBColorSpace; t.needsUpdate = true; t.anisotropy = 8;
    hero[nm] = { tex: t, anchor, aspect: c.width / c.height, hfrac, left: !!(L && L.left) };
  }
  const key = (job, pose) => index[`${JOB_KEYS[job] || job}_${pose}`] ?? index.stand;
  return { tex, frames, index, key, hero, names, placeholder: Object.keys(loaded).length === 0 };
}

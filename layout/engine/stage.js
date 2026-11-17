// Staging helpers shared by the sets: two-pass figure building (so hands can reach the book and each other),
// book placement relative to a figure, and the analytic projection of hand shadows onto the page.
import * as THREE from 'three';
import { buildFigure } from './mannequin.js';
import { buildBook } from './book.js';
import { V, rad, UP } from './core.js';

// words -> world directions in a figure's frame
export function figDir(word, P) {
  if (Array.isArray(word)) return V(word).normalize();
  const f = P.fwd.clone(), l = new THREE.Vector3(f.z, 0, -f.x); // figure's left: fwd rotated +90° about y
  return ({ fwd: f, back: f.clone().negate(), left: l, right: l.clone().negate(), up: UP.clone(), down: UP.clone().negate() })[word].clone();
}

export function placeBook(spec, figs, extra = {}) {
  if (!spec) return null;
  if (!spec.on) return buildBook(spec);
  const P = figs[spec.on].userData.P;
  const f = P.fwd.clone(), l = new THREE.Vector3(f.z, 0, -f.x);
  const base = (spec.anchor ? P[spec.anchor] : P.lap).clone();
  const o = spec.off || [0, 0, 0];
  const at = base.addScaledVector(l, o[0]).addScaledVector(UP, o[1]).addScaledVector(f, o[2]);
  // the face tips toward the reader by `tilt` degrees, then turns by `yaw` about the vertical
  const towards = spec.toward ? figDir(spec.toward, P) : f.clone().negate();
  const t = rad(spec.tilt ?? 20);
  let normal = UP.clone().multiplyScalar(Math.cos(t)).addScaledVector(towards, Math.sin(t)).normalize();
  let top = spec.top ? figDir(spec.top, P) : towards.clone().negate();
  if (spec.yaw) { const q = new THREE.Quaternion().setFromAxisAngle(UP, rad(spec.yaw)); normal.applyQuaternion(q); top.applyQuaternion(q); }
  if (spec.roll) { const ax = top.clone().addScaledVector(normal, -top.dot(normal)).normalize(); const q = new THREE.Quaternion().setFromAxisAngle(ax, rad(spec.roll)); normal.applyQuaternion(q); }
  return buildBook({ ...spec, at: at.toArray(), normal: normal.toArray(), top: top.toArray() });
}

// build figures in passes so that targets on the book and on other figures resolve. resolveExtra(name) may return a
// point for set-specific targets (e.g. 'flashlight', 'mirror').
export function stage(figSpecs, bookSpec, resolveExtra = () => null) {
  let figs = {}, book = null;
  const ctxFor = (pass) => ({
    resolve(t, P) {
      if (Array.isArray(t)) return V(t);
      if (t && t.isVector3) return t.clone();
      if (typeof t !== 'string') throw new Error('bad target ' + JSON.stringify(t));
      const ex = resolveExtra(t, figs, book); if (ex) return ex.clone();
      const [a, b] = t.split(':');
      if (a === 'book') { if (book) { const p = book.anchors[b || 'G']; if (!p) throw new Error('no book anchor ' + b); return p.clone(); } return P.shoulderC ? P.shoulderC.clone().addScaledVector(P.fwd, 0.3).addScaledVector(UP, -0.25) : P.head.clone().addScaledVector(P.fwd, 0.4); }
      if (a === 'self') return P[b].clone();
      if (figs[a]) { const p = figs[a].userData.P[b || 'head']; if (!p) throw new Error(`no part ${b} on ${a}`); return p.clone(); }
      if (pass === 0) return (P.head || P.shoulderC || P.hip).clone().addScaledVector(P.fwd, 0.5);
      throw new Error('unknown target ' + t);
    },
  });
  const run = (pass) => { const out = {}; for (const [who, s] of Object.entries(figSpecs || {})) out[who] = buildFigure({ who, ...s }, ctxFor(pass)); return out; };
  figs = run(0);
  if (bookSpec) book = placeBook(bookSpec, figs);
  figs = run(1); figs = run(1);
  if (bookSpec && bookSpec.on) book = placeBook(bookSpec, figs); // re-place on the final lap
  figs = run(1);
  return { figs, book };
}

// meshes of a named caster: 'who.handL' | 'who.handR' | 'who.head' | 'who.armL' ...
export function casterMeshes(name, figs) {
  const [who, part] = name.split('.'); const f = figs[who]; if (!f) return [];
  const P = f.userData.P;
  if (part === 'handL' || part === 'handR') return P.hands[part.slice(-1)].group.children.slice();
  if (part === 'head') { const out = []; f.traverse((o) => { if (o.isMesh) { const c = new THREE.Vector3(); new THREE.Box3().setFromObject(o).getCenter(c); if (c.distanceTo(P.head) < P.headH * 0.75) out.push(o); } }); return out; }
  throw new Error('caster ' + name);
}

function hull(pts) { // monotone chain, pts [[x,y]]
  const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]); if (p.length < 3) return p;
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.slice().reverse()) { while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}

// project caster meshes from a point light onto the open book's spread plane. Returns hull polygons in spread uv
// (u 0..1 left->right, v 0..1 top->bottom as the spread is read) and in world space.
export function projectShadow(lightPos, meshes, book) {
  const at = book.at, n = book.n, u = book.u, w = book.w;
  const pw = 0.206, ph = 0.274;
  const polys = []; const all = [];
  for (const m of meshes) {
    m.updateMatrixWorld(true); const pos = m.geometry.attributes.position; const pts = [];
    for (let i = 0; i < pos.count; i += 1) {
      const v = new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld);
      const d = v.clone().sub(lightPos); const den = d.dot(n); if (Math.abs(den) < 1e-9) continue;
      const t = at.clone().sub(lightPos).dot(n) / den; if (t <= 1) continue; // caster must lie between light and page
      const p = lightPos.clone().addScaledVector(d, t).sub(at);
      pts.push([(p.dot(u) + pw) / (2 * pw), 1 - (p.dot(w) + ph / 2) / ph]);
    }
    if (pts.length >= 3) { const h = hull(pts); polys.push(h); all.push(...h); }
  }
  const toWorld = ([a, b]) => at.clone().addScaledVector(u, a * 2 * pw - pw).addScaledVector(w, (1 - b) * ph - ph / 2);
  const xs = all.map((p) => p[0]), ys = all.map((p) => p[1]);
  const bbox = all.length ? [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)].map((x) => +x.toFixed(3)) : null;
  return { uv: polys.map((p) => p.map(([a, b]) => [+a.toFixed(4), +b.toFixed(4)])), world: polys.map((p) => p.map(toWorld)), bbox };
}

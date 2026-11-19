// The spawn tree: leaves from the silhouette (seen from the apex camera, cast into the terrain), hierarchy by
// recursive balanced k-means, parents on the highest ground of their cluster; plus every node's timing.
import * as THREE from 'three';
import { mulberry32, hash1 } from './rng.js';
import { maskAt, sampleMask } from './silhouette.js';

export function apexRay(apexCam, sil, u, v, aspect) {
  // mask uv -> NDC in the apex frame
  const h = sil.height, w = h * sil.mask_aspect / aspect;
  const nx = (sil.center[0] + (u - 0.5) * w) * 2 - 1;
  const ny = 1 - (sil.center[1] + (v - 0.5) * h) * 2;
  const p = new THREE.Vector3(nx, ny, 0.5).unproject(apexCam);
  return p.sub(apexCam.position).normalize();
}
export function apexUV(apexCam, sil, p, aspect) {   // world -> mask uv
  const q = p.clone().project(apexCam);
  const h = sil.height, w = h * sil.mask_aspect / aspect;
  const sx = (q.x + 1) / 2, sy = (1 - q.y) / 2;
  return [(sx - sil.center[0]) / w + 0.5, (sy - sil.center[1]) / h + 0.5];
}

function balancedKMeans(pts, idx, k, rnd, iters = 12) {
  const n = idx.length, cap = n / k;
  // k-means++ init
  const C = [pts[idx[Math.floor(rnd() * n)]].clone()];
  while (C.length < k) {
    const d2 = idx.map((i) => Math.min(...C.map((c) => c.distanceToSquared(pts[i]))));
    let s = d2.reduce((a, b) => a + b, 0) * rnd(), j = 0;
    for (; j < n - 1; j++) { s -= d2[j]; if (s <= 0) break; }
    C.push(pts[idx[j]].clone());
  }
  let groups;
  for (let it = 0; it < iters; it++) {
    const pairs = [];
    for (let a = 0; a < n; a++) for (let c = 0; c < k; c++) pairs.push([pts[idx[a]].distanceToSquared(C[c]), a, c]);
    pairs.sort((x, y) => x[0] - y[0]);
    const asg = new Int32Array(n).fill(-1), cnt = new Int32Array(k);
    groups = Array.from({ length: k }, () => []);
    for (const [, a, c] of pairs) {
      if (asg[a] >= 0 || cnt[c] >= cap) continue;
      asg[a] = c; cnt[c]++; groups[c].push(idx[a]);
    }
    for (let c = 0; c < k; c++) {
      const m = new THREE.Vector3(); for (const i of groups[c]) m.add(pts[i]); C[c] = m.divideScalar(groups[c].length);
    }
  }
  return groups.map((g, c) => ({ members: g, centroid: C[c] }));
}

export function buildTree(cfg, terrain, apexCam, mask, aspect) {
  const T = cfg.tree, S = cfg.silhouette;
  const sil = { ...S, mask_aspect: mask.w / mask.h };
  if (S.anchor_uv) {           // put this point of the figure (mask uv) on the root's ledge
    const q = terrain.ledge.clone().project(apexCam);
    const h = sil.height, w = h * sil.mask_aspect / aspect;
    const sx = (q.x + 1) / 2, sy = (1 - q.y) / 2;
    sil.center = [sx - (S.anchor_uv[0] - 0.5) * w, sy - (S.anchor_uv[1] - 0.5) * h];
  }
  const rnd = mulberry32(T.seed);
  const counts = T.counts, G = counts.length - 1;
  const nLeaves = counts[G];
  // ---- leaves
  const uvs = sampleMask(mask, Math.round(nLeaves * 1.08), T.edge_frac, T.seed + 1);
  const leaves = [];
  const grid = new Map(); const cell = T.min_sep;
  const key = (p) => `${Math.floor(p.x / cell)},${Math.floor(p.z / cell)}`;
  const tooClose = (p) => {
    const cx = Math.floor(p.x / cell), cz = Math.floor(p.z / cell);
    for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) for (const q of grid.get(`${cx + i},${cz + j}`) || []) if (q.distanceTo(p) < T.min_sep) return true;
    return false;
  };
  const leafEdge = [];
  for (const [u, v, e] of uvs) {
    if (leaves.length >= nLeaves) break;
    const d = apexRay(apexCam, sil, u, v, aspect);
    let p = terrain.raycast(apexCam.position, d);
    if (!p) continue;
    // prefer a foothold: look for flatter ground within a few metres
    const n0 = terrain.normal(p.x, p.z);
    if (n0.y < T.flat_min) {
      let best = p, bn = n0.y;
      for (let k = 0; k < 14; k++) {
        const a = rnd() * Math.PI * 2, r = T.flat_search * Math.sqrt(rnd());
        const x = p.x + Math.cos(a) * r, z = p.z + Math.sin(a) * r;
        const ny = terrain.normal(x, z).y - r * 0.02;
        if (ny > bn) { bn = ny; best = new THREE.Vector3(x, terrain.height(x, z), z); }
      }
      p = best;
    }
    for (let k = 0; k < 6 && tooClose(p); k++) {
      const a = rnd() * Math.PI * 2; p = new THREE.Vector3(p.x + Math.cos(a) * T.min_sep, 0, p.z + Math.sin(a) * T.min_sep); p.y = terrain.height(p.x, p.z);
    }
    if (tooClose(p)) continue;
    leaves.push(p); leafEdge.push(e); const kk = key(p); if (!grid.has(kk)) grid.set(kk, []); grid.get(kk).push(p);
  }
  while (leaves.length < nLeaves) leaves.push(leaves[leaves.length % Math.max(1, leaves.length)].clone().add(new THREE.Vector3(rnd() * 3, 0, rnd() * 3)));
  // ---- hierarchy, top-down
  const nodes = [];
  const add = (n) => { n.id = nodes.length; nodes.push(n); return n; };
  const root = add({ gen: 0, parent: -1, pos: terrain.ledge.clone(), children: [], job: 'root' });
  const usedTop = [];
  function placeParent(members, centroid, gen, gp) {
    const pull = (T.parent_pull || [])[gen] || 0, sfrac = (T.parent_search || [])[gen] ?? T.parent_search_frac;
    const pts = members.map((i) => leaves[i]);
    let rms = 0; for (const q of pts) rms += q.distanceToSquared(centroid); rms = Math.sqrt(rms / pts.length);
    const R = Math.max(4, rms * sfrac);
    const c0 = centroid.clone().lerp(gp, Math.min(0.8, pull));
    let best = null, by = -1e9;
    const cands = [...pts];
    for (let k = 0; k < 260; k++) {
      const a = rnd() * Math.PI * 2, r = R * Math.sqrt(rnd());
      const x = c0.x + Math.cos(a) * r, z = c0.z + Math.sin(a) * r;
      cands.push(new THREE.Vector3(x, terrain.height(x, z), z));
    }
    for (const q of cands) {
      const [u, v] = apexUV(apexCam, sil, q, aspect);
      if (maskAt(mask, u, v, 0.012) < 0.5) continue;
      if (terrain.normal(q.x, q.z).y < T.flat_min * 0.8) continue;
      if (usedTop.some((o) => o.distanceTo(q) < T.min_sep * 2)) continue;
      if (q.y > gp.y - ((T.parent_below || [])[gen] || 0)) continue;
      if (q.distanceTo(gp) < ((T.parent_min_dist || [])[gen] || 0)) continue;
      const score = q.y - 0.15 * q.distanceTo(centroid) - pull * q.distanceTo(gp);
      if (score > by) { by = score; best = q; }
    }
    if (!best) best = pts.reduce((a, b) => (b.y > a.y ? b : a)).clone().add(new THREE.Vector3(1.5, 0, 1.5));
    best.y = terrain.height(best.x, best.z);
    usedTop.push(best);
    return best.clone();
  }
  function recurse(parent, members, gen) {
    if (gen === G) {
      for (const i of members) { const n = add({ gen, parent: parent.id, pos: leaves[i].clone(), children: [], edge: leafEdge[i] ?? 0 }); parent.children.push(n.id); }
      return;
    }
    const k = counts[gen] / counts[gen - 1];
    const groups = balancedKMeans(leaves, members, k, rnd);
    // order the gen-1 branches around the root (by angle in the apex view) so branch 0..7 is a stable reading order
    if (gen === 1) groups.sort((a, b) => Math.atan2(a.centroid.x - root.pos.x, a.centroid.z - root.pos.z) - Math.atan2(b.centroid.x - root.pos.x, b.centroid.z - root.pos.z));
    for (const gr of groups) {
      const n = add({ gen, parent: parent.id, pos: placeParent(gr.members, gr.centroid, gen, parent.pos), children: [] });
      parent.children.push(n.id);
      recurse(n, gr.members, gen + 1);
    }
  }
  recurse(root, leaves.map((_, i) => i), 1);
  // ---- jobs (each gen-1 branch one job; ~20 % of descendants another)
  const jobs = T.jobs;
  const assign = (n, branch) => {
    n.branch = branch;
    if (n.gen === 1) n.job = jobs[branch % jobs.length];
    else if (n.gen > 1) n.job = rnd() < T.other_job_frac ? jobs[Math.floor(rnd() * jobs.length)] : jobs[branch % jobs.length];
    n.children.forEach((c) => assign(nodes[c], n.gen === 0 ? root.children.indexOf(c) : branch));
  };
  assign(root, -1);
  return { nodes, root, leaves, G, sil };
}

// ---- timing: spawn, work waves, seals, hair paths
export function timeTree(tree, cfg) {
  const { nodes, G } = tree;
  const Sp = cfg.spawn, Wk = cfg.work, Se = cfg.seal;
  const root = nodes[0];
  root.land = Sp.root_appear; root.blow = Sp.blow[0]; root.depart = Sp.root_hair.s0; root.flight = Sp.root_hair.land - Sp.root_hair.s0;
  const order = [root];
  for (let qi = 0; qi < order.length; qi++) {
    const p = order[qi];
    p.children.forEach((c, i) => {
      const n = nodes[c];
      const st = Sp.stagger[n.gen - 1] || 0;
      n.depart = p.blow + 0.6 + hash1(n.id, 77) * st;
      n.flight = Sp.flight[n.gen - 1] * (0.85 + 0.3 * hash1(n.id, 78));
      n.land = n.depart + n.flight;
      n.blow = n.gen < G ? Sp.blow[n.gen] : null;
      order.push(n);
    });
  }
  for (const n of nodes) {
    n.work = n.gen < G ? n.blow + 3 : n.land + 2;
    n.off = Wk.offsets[n.gen] ?? n.gen * 2;
    n.switches = Wk.beats.map((b) => b + n.off).filter((t) => t >= n.work && t < Wk.until + n.off);
  }
  // seals: leaves first on the beat, parents `hop` frames later
  const beatOf = {};
  Se.branches.forEach((bs, k) => bs.forEach((b) => { beatOf[b] = k; }));
  for (const n of nodes) {
    if (n.gen === 0) { n.seal = null; continue; }
    const k = beatOf[n.branch] ?? 0;
    n.sealBeat = k;
    n.seal = Se.beats[k] + (G - n.gen) * Se.hop + (n.gen === G ? hash1(n.id, 91) * Se.jitter : 0);
  }
  return tree;
}

// Camera keys -> camera at frame s. Points may be absolute [x,y,z] or references resolved against the scene.
import * as THREE from 'three';

const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);
export const EASE = {
  linear: (t) => t,
  in: (t) => t * t,
  out: (t) => 1 - (1 - t) * (1 - t),
  inout: (t) => t * t * (3 - 2 * t),
  in3: (t) => t * t * t,
  out3: (t) => 1 - Math.pow(1 - t, 3),
  inout5: (t) => t * t * t * (t * (t * 6 - 15) + 10),
};

// resolve a point spec. ctx: { refs: {name: Vector3}, nodes: [...], nearest(gen, to, rank, below) }
export function resolvePoint(spec, ctx) {
  if (Array.isArray(spec)) return V(spec);
  if (spec.orbit) {
    const o = spec.orbit, c = resolvePoint(o.around, ctx);
    const az = o.az * Math.PI / 180, el = o.el * Math.PI / 180;
    return c.add(new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)).multiplyScalar(o.dist));
  }
  let p;
  const r = spec.ref;
  if (r === 'nearest') p = ctx.nearest(spec.gen, resolvePoint(spec.to || { ref: 'ledge' }, ctx), spec.rank || 0, spec.below);
  else if (r.startsWith('node:')) p = ctx.nodes[Number(r.slice(5))].pos.clone();
  else if (r.startsWith('mid:')) { const [a, b] = r.slice(4).split(','); p = resolvePoint({ ref: a }, ctx).lerp(resolvePoint({ ref: b }, ctx), 0.5); }
  else if (ctx.refs[r]) p = ctx.refs[r].clone();
  else throw new Error('unknown point ref ' + r);
  if (spec.off) p.add(V(spec.off));
  if (spec.lerp) p.lerp(resolvePoint(spec.lerp.to, ctx), spec.lerp.t);
  return p;
}

export function makeCameraPath(C, ctx) {
  const keys = C.keys.map((k) => {
    if (k.apex) return { ...k, P: resolvePoint(C.apex.pos, ctx), T: resolvePoint(C.apex.target, ctx), fov: C.apex.fov, roll: 0 };
    return { ...k, P: resolvePoint(k.pos, ctx), T: resolvePoint(k.target, ctx), fov: k.fov ?? 40, roll: k.roll || 0 };
  });
  for (const k of keys) if (k.center) k.C = resolvePoint(k.center, ctx);

  function raw(s) {
    if (s <= keys[0].s) return keys[0];
    const last = keys[keys.length - 1];
    if (s >= last.s) return last;
    let i = 0; while (keys[i + 1].s <= s) i++;
    const a = keys[i], b = keys[i + 1];
    const u = (s - a.s) / (b.s - a.s);
    const ease = typeof b.ease === 'object' ? ((t) => (t < 0.5 ? 0.5 * Math.pow(2 * t, b.ease.pow) : 1 - 0.5 * Math.pow(2 - 2 * t, b.ease.pow))) : (EASE[b.ease || 'inout']);
    const t = ease(u);
    const T = a.T.clone().lerp(b.T, t);
    let P;
    const path = b.path || 'smooth';
    if (path === 'hold') P = a.P.clone();
    else if (path === 'linear') P = a.P.clone().lerp(b.P, t);
    else if (path === 'log') {
      const da = a.P.clone().sub(a.T), db = b.P.clone().sub(b.T);
      const la = Math.log(da.length()), lb = Math.log(db.length());
      const qa = new THREE.Quaternion(), dir = da.clone().normalize();
      qa.setFromUnitVectors(dir, db.clone().normalize());
      const q = new THREE.Quaternion().slerp(qa, t);
      const tl = EASE[b.log_ease || 'linear'](u);
      P = T.clone().add(dir.applyQuaternion(q).multiplyScalar(Math.exp(la + (lb - la) * (b.log_ease ? tl : t))));
    } else if (path === 'orbit') {
      const c = b.C || a.C || T;
      const pa = a.P.clone().sub(c), pb = b.P.clone().sub(c);
      let aa = Math.atan2(pa.x, pa.z), ab = Math.atan2(pb.x, pb.z);
      if (b.turns !== undefined) ab = aa + b.turns * Math.PI * 2;
      else { while (ab - aa > Math.PI) ab -= 2 * Math.PI; while (ab - aa < -Math.PI) ab += 2 * Math.PI; }
      const ra = Math.hypot(pa.x, pa.z), rb = Math.hypot(pb.x, pb.z);
      const ang = aa + (ab - aa) * t;
      const rr = Math.exp(Math.log(Math.max(ra, 1e-3)) + (Math.log(Math.max(rb, 1e-3)) - Math.log(Math.max(ra, 1e-3))) * t);
      P = new THREE.Vector3(c.x + Math.sin(ang) * rr, c.y + pa.y + (pb.y - pa.y) * (b.y_ease ? EASE[b.y_ease](u) : t), c.z + Math.cos(ang) * rr);
    } else {   // smooth: Catmull-Rom through the neighbouring keys
      const p0 = (keys[i - 1] || a).P, p3 = (keys[i + 2] || b).P;
      P = catmull(p0, a.P, b.P, p3, t);
    }
    return { P, T, fov: a.fov + (b.fov - a.fov) * t, roll: a.roll + (b.roll - a.roll) * t };
  }
  const sm = C.smooth_frames || 0;
  function at(s) {
    if (!sm) return raw(s);
    const P = new THREE.Vector3(), T = new THREE.Vector3(); let fov = 0, roll = 0, wsum = 0;
    const n = 8;
    for (let k = -n; k <= n; k++) {
      const ds = (k / n) * sm, w = Math.exp(-2.5 * (k / n) * (k / n));
      const r = raw(s + ds); P.addScaledVector(r.P, w); T.addScaledVector(r.T, w); fov += r.fov * w; roll += r.roll * w; wsum += w;
    }
    return { P: P.divideScalar(wsum), T: T.divideScalar(wsum), fov: fov / wsum, roll: roll / wsum };
  }
  function apply(cam, s) {
    const r = at(s);
    cam.position.copy(r.P); cam.fov = r.fov; cam.up.set(0, 1, 0);
    cam.lookAt(r.T);
    if (r.roll) cam.rotateZ(r.roll * Math.PI / 180);
    cam.updateProjectionMatrix(); cam.updateMatrixWorld(true);
    return r;
  }
  return { at, apply, keys };
}

function catmull(p0, p1, p2, p3, t) {
  const t2 = t * t, t3 = t2 * t;
  return new THREE.Vector3(
    0.5 * ((2 * p1.x) + (-p0.x + p2.x) * t + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3),
    0.5 * ((2 * p1.y) + (-p0.y + p2.y) * t + (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 + (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3),
    0.5 * ((2 * p1.z) + (-p0.z + p2.z) * t + (2 * p0.z - 5 * p1.z + 4 * p2.z - p3.z) * t2 + (-p0.z + 3 * p1.z - 3 * p2.z + p3.z) * t3));
}

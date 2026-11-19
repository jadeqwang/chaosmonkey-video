// Build one car26 shot: SUV cabin + road + passing streetlights + Jade (driving) + the daughter (car seat).
// Every window pane is a named quad (corners exported to the sidecar in screen space). One pane per shot may act as
// a mirror (shot.mirror = 'mirror' (rear-view) | 'rear_right' ...), rendered as a true reflection.
import * as THREE from 'three';
import { mk, box, cyl, ball, quad, slab, tag, V, rad, UP, basisQ } from '../../engine/core.js';
import { stage, solveCamera, hideParts, namedPoint } from '../../engine/stage.js';
import { aim } from '../../engine/aim.js';
import { CAR, ROAD, lampsAt, LIGHTS } from './layout.js';
import { buildBody } from '../../engine/body.js';

const TRIM = { grey: 0.45, col: 0x3a3a42 }, SEAT = { grey: 0.32, col: 0x2a2a30 }, HEADLINER = { grey: 0.7, col: 0x8a8890 }, DASH = { grey: 0.25, col: 0x202024 };

function mirrorPose() { // the rear-view mirror is angled so the driver sees the child seat
  const c = V(CAR.mirror.at), eye = V(-0.38, 1.2, 0.08), child = V(0.36, 1.02, 0.98);
  const n = eye.clone().sub(c).normalize().add(child.clone().sub(c).normalize()).normalize();
  return { c, n };
}

function cabin(shot = {}) {
  const g = new THREE.Group(); const C = CAR, W = C.halfW, panes = {};
  g.add(tag(box(2 * W, 0.04, 2.75, { grey: 0.3, col: 0x26262a }, [0, C.floorY - 0.02, 0.32]), 'cabin floor'));
  g.add(tag(box(2 * W - 0.1, 0.03, 1.85, HEADLINER, [0, C.roofY + 0.015, 0.7]), 'headliner (roof)'));
  // doors (below the beltline) and the side window openings between pillars
  for (const s of [-1, 1]) {
    g.add(tag(box(0.06, C.beltY - C.floorY, 2.5, TRIM, [s * (W + 0.03), (C.beltY + C.floorY) / 2, 0.42]), 'door panels'));
    g.add(tag(box(0.1, 0.05, 2.5, TRIM, [s * (W - 0.02), C.beltY, 0.42]), 'door panels'));
    // A pillar
    g.add(tag(slab(V(s * C.wind.base.halfW, C.wind.base.y, C.wind.base.z), V(s * C.wind.top.halfW, C.wind.top.y, C.wind.top.z), 0.09, 0.07, V(1, 0, 0), TRIM), 'A pillar'));
    for (const [nm, [z0, z1]] of Object.entries(C.pillars)) g.add(tag(box(0.08, C.roofY - C.beltY, z1 - z0, TRIM, [s * (W - 0.02), (C.roofY + C.beltY) / 2, (z0 + z1) / 2]), nm + ' pillar'));
    g.add(tag(box(0.08, C.roofY - C.sideWin.top, 1.9, TRIM, [s * (W - 0.02), (C.roofY + C.sideWin.top) / 2, 0.7]), 'roof rail'));
    // window panes (glass), named as seen from inside: TL, TR, BR, BL
    const side = s < 0 ? 'left' : 'right', x = s * (W - 0.03), y0 = C.beltY + 0.025, y1 = C.sideWin.top;
    const mkPane = (name, zf, zr, slantFront) => { // zf front edge z, zr rear edge z
      const ftop = slantFront ? V(x, y1, slantFront) : V(x, y1, zf), fbot = V(x, y0, zf), rtop = V(x, y1, zr), rbot = V(x, y0, zr);
      panes[name] = s > 0 ? [ftop, rtop, rbot, fbot] : [rtop, ftop, fbot, rbot];
    };
    mkPane(`front_${side}`, -0.72, C.pillars.B[0], -0.27);
    mkPane(`rear_${side}`, C.pillars.B[1], C.pillars.C[0]);
    mkPane(`quarter_${side}`, C.pillars.C[1], C.pillars.D[0]);
  }
  // windscreen and rear glass
  { const b = C.wind.base, t = C.wind.top; panes.windscreen = [V(-t.halfW, t.y, t.z), V(t.halfW, t.y, t.z), V(b.halfW, b.y + 0.02, b.z), V(-b.halfW, b.y + 0.02, b.z)];
    const r = C.rearWin; panes.rear_window = [V(r.halfW, r.y1, r.z1), V(-r.halfW, r.y1, r.z1), V(-r.halfW, r.y0, r.z0), V(r.halfW, r.y0, r.z0)];
    g.add(tag(box(2 * W, 0.06, 0.12, TRIM, [0, t.y + 0.03, t.z - 0.03]), 'windscreen header'));
    g.add(tag(box(2 * W, 0.35, 0.08, TRIM, [0, 0.82, 1.72]), 'tailgate'));
    g.add(tag(box(2 * W, 0.06, 0.1, TRIM, [0, r.y1 + 0.04, r.z1]), 'tailgate')); }
  // dashboard, instrument hood, console
  { const D = C.dash; const dm = box(2 * W, D.y1 - D.y0, D.z1 - D.z0, DASH, [0, (D.y0 + D.y1) / 2, (D.z0 + D.z1) / 2]); g.add(tag(dm, 'dashboard'));
    g.add(tag(box(0.42, 0.08, 0.2, DASH, [CAR.wheel.x, D.y1 + 0.03, -0.7]), 'dashboard'));
    g.add(tag(box(0.24, 0.07, 0.01, { grey: 0.6, col: 0x203050, emit: 0x405080, emitI: 0.6, flatEmit: 0.6 }, [0.0, 0.93, -0.615]), 'dashboard screen'));
    g.add(tag(box(0.24, 0.42, 0.95, DASH, [0, C.floorY + 0.21, -0.15]), 'centre console')); }
  // steering wheel
  { const S = C.wheel; const grp = new THREE.Group(); grp.position.set(S.x, S.y, S.z); grp.rotation.x = rad(-S.tiltDeg);
    const rim = mk(new THREE.TorusGeometry(S.r, 0.017, 10, 40), { grey: 0.15, col: 0x18181a }); grp.add(rim);
    grp.add(box(0.12, 0.08, 0.05, { grey: 0.2, col: 0x222226 }, [0, 0, 0])); grp.add(box(0.36, 0.03, 0.02, { grey: 0.15, col: 0x18181a }, [0, -0.02, 0]));
    g.add(tag(grp, 'steering wheel')); g.add(tag(cyl(0.03, 0.03, 0.3, DASH, [S.x, S.y - 0.06, S.z - 0.16], [62, 0, 0]), 'steering column')); }
  // seats
  const seat = (x, hp, front) => { const grp = new THREE.Group();
    grp.add(box(front ? 0.5 : 1.36, 0.13, 0.5, SEAT, [x, hp.y - 0.07, hp.z - 0.12]));
    const back = slab(V(x, hp.y, hp.z + 0.22), V(x, hp.y + 0.62, hp.z + 0.36), front ? 0.5 : 1.36, 0.12, V(1, 0, 0), SEAT); grp.add(back);
    if (front) grp.add(box(0.26, 0.17, 0.1, SEAT, [x, hp.y + 0.72, hp.z + 0.37]));
    grp.add(box(front ? 0.48 : 1.34, hp.y - 0.13 - C.floorY, 0.4, { grey: 0.2, col: 0x1a1a1e }, [x, (hp.y - 0.13 + C.floorY) / 2, hp.z - 0.12]));
    return grp; };
  g.add(tag(seat(-C.frontSeatX, C.frontHp, true), "driver's seat")); g.add(tag(seat(C.frontSeatX, C.frontHp, true), 'passenger seat'));
  g.add(tag(seat(0, C.rearHp, false), 'rear bench'));
  // child car seat(s), forward-facing. v1: one, behind the passenger. v3: TWO, outboard left and right; the daughter
  // rides in the right one (behind the passenger), the left one (behind the driver) is empty.
  for (const sx of (shot.v3 ? [1, -1] : [1])) { const K = C.carSeat, x = sx * K.x, grp = new THREE.Group(), SH = { grey: sx > 0 ? 0.55 : 0.62, col: sx > 0 ? 0x6a6a78 : 0x74747f };
    grp.add(box(K.w, 0.14, 0.46, SH, [x, C.rearHp.y + 0.03, K.z - 0.06]));
    grp.add(slab(V(x, K.cushionY, K.z + 0.2), V(x, K.backTop, K.z + 0.27), K.w, 0.06, V(1, 0, 0), SH));
    for (const s of [-1, 1]) { grp.add(box(0.04, 0.42, 0.34, SH, [x + s * K.w / 2, K.cushionY + 0.2, K.z + 0.06]));
      grp.add(box(0.05, 0.2, 0.2, SH, [x + s * 0.15, K.backTop - 0.13, K.z + 0.14])); }
    if (shot.v3 && sx < 0) { // the empty one: its harness hangs open against the shell, buckle on the cushion
      const ST = { grey: 0.2, col: 0x1c1c22 };
      for (const s of [-1, 1]) grp.add(slab(V(x + s * 0.07, K.backTop - 0.16, K.z + 0.215), V(x + s * 0.09, K.cushionY + 0.02, K.z + 0.165), 0.035, 0.008, V(1, 0, 0), ST));
      grp.add(box(0.06, 0.03, 0.08, ST, [x, K.cushionY + 0.085, K.z - 0.02])); }
    g.add(tag(grp, shot.v3 ? (sx > 0 ? 'child car seat (hers, rear right)' : 'EMPTY child car seat (rear left)') : 'child car seat')); }
  // rear-view mirror: housing + glass
  { const { c, n } = mirrorPose(); const M = C.mirror; let x = new THREE.Vector3().crossVectors(UP, n).normalize(); const y = new THREE.Vector3().crossVectors(n, x).normalize();
    const hous = mk(new THREE.BoxGeometry(M.w + 0.016, M.h + 0.016, 0.035), { grey: 0.2, col: 0x1a1a1c }); hous.position.copy(c).addScaledVector(n, -0.02); hous.quaternion.copy(basisQ(x, y, n)); g.add(tag(hous, 'rear-view mirror'));
    g.add(tag(cyl(0.008, 0.008, 0.1, { grey: 0.2, col: 0x1a1a1c }, [c.x, c.y + 0.07, c.z - 0.03], null, 8), 'rear-view mirror'));
    const P = (a, b) => c.clone().addScaledVector(x, a * M.w / 2).addScaledVector(y, b * M.h / 2).addScaledVector(n, 0.0005);
    // as seen by someone looking into it (from the cabin): left/right are the viewer's
    panes.mirror = [P(1, 1), P(-1, 1), P(-1, -1), P(1, -1)];
    const gm = quad(panes.mirror, { grey: 0.3, col: 0x9aa0b0, noCast: true }); gm.userData.mirrorGlass = true; g.add(tag(gm, 'rear-view mirror glass')); }
  // window glass (lit only)
  for (const [nm, cs] of Object.entries(panes)) if (nm !== 'mirror') g.add(tag(quad(cs, { glass: true, col: 0x6a6090, opacity: 0.1, noCast: true }), `glass: ${nm}`));
  return { g, panes };
}

function outside(t) {
  const g = new THREE.Group();
  g.add(tag(box(60, 0.02, 600, { grey: 0.38, col: 0x2a2a30, noCast: true }, [0, -0.01, 0]), 'highway'));
  for (const x of [-ROAD.laneW / 2 - 0.2, ROAD.laneW / 2 + 1.75]) for (let z = -280; z < 280; z += 12) g.add(tag(box(0.12, 0.012, 3, { grey: 0.9, col: 0xd0d0c0, noCast: true }, [x, 0.006, z - ((ROAD.speed * t) % 12)]), 'lane markings'));
  g.add(tag(box(0.1, 0.35, 600, { grey: 0.6, col: 0x707078 }, [ROAD.shoulderX + 0.6, 0.5, 0]), 'guard rail'));
  g.add(tag(box(0.6, 0.8, 600, { grey: 0.55, col: 0x5a5a60 }, [ROAD.medianX, 0.4, 0]), 'median barrier'));
  for (let z = -300; z < 300; z += 9) { const h = 5 + ((z * 7919) % 5 + 5) % 5; g.add(tag(box(5, h, 6, { grey: 0.22, col: 0x1a1a24, noCast: true }, [20 + ((z * 31) % 4), h / 2, z]), 'tree line'));
    g.add(tag(box(5, h, 6, { grey: 0.22, col: 0x1a1a24, noCast: true }, [-24 - ((z * 17) % 4), h / 2, z + 4]), 'tree line')); }
  for (const L of lampsAt(t, 12)) {
    const [px, , pz] = L.pole, [lx, ly, lz] = L.lamp;
    g.add(tag(cyl(0.09, 0.12, ROAD.poleH, { grey: 0.4, col: 0x4a4a50 }, [px, ROAD.poleH / 2, pz], null, 10), 'streetlight poles'));
    g.add(tag(box(Math.abs(lx - px) + 0.2, 0.08, 0.08, { grey: 0.4, col: 0x4a4a50 }, [(px + lx) / 2, ly + 0.08, lz]), 'streetlight poles'));
    g.add(tag(box(0.55, 0.1, 0.25, { grey: 1, col: 0xffd8a0, emit: ROAD.lampColor, emitI: 2.5, flatEmit: 0.98 }, [lx, ly, lz]), 'streetlight (lamp)'));
  }
  return g;
}

export function build(shot, { makeCam }) {
  const scene = new THREE.Scene(); const root = new THREE.Group(); scene.add(root);
  const t = shot.street?.t ?? 0;
  const { g: cab, panes } = cabin(shot); root.add(cab); root.add(outside(t));
  const { figs, book } = stage(shot.figs, null, () => null, shot.v4 ? { builder: buildBody } : {});
  for (const f of Object.values(figs)) root.add(f);
  hideParts(shot.hideParts, figs);
  // camera: 'mirror' search finds where a camera must stand to see both faces in the rear-view mirror
  let mirrorInfo = null;
  if (shot.mirror) {
    const cs = panes[shot.mirror]; const c = cs.reduce((a, v) => a.add(v), V(0, 0, 0)).multiplyScalar(0.25);
    let n = new THREE.Vector3().crossVectors(cs[1].clone().sub(cs[0]), cs[3].clone().sub(cs[0])).normalize();
    // the reflective face points into the cabin (toward the car's centre line / rear for the rear-view mirror)
    const into = shot.mirror === 'mirror' ? V(0, 0, 1) : V(-Math.sign(c.x), 0, 0); if (n.dot(into) < 0) n.negate();
    const d = n.dot(c);
    const R = new THREE.Matrix4().set(1 - 2 * n.x * n.x, -2 * n.x * n.y, -2 * n.x * n.z, 2 * d * n.x, -2 * n.y * n.x, 1 - 2 * n.y * n.y, -2 * n.y * n.z, 2 * d * n.y, -2 * n.z * n.x, -2 * n.z * n.y, 1 - 2 * n.z * n.z, 2 * d * n.z, 0, 0, 0, 1);
    mirrorInfo = { n, c, d, R, cs, meshes: [] };
    cab.traverse((o) => { if (o.isMesh && ((shot.mirror === 'mirror' && o.userData.mirrorGlass) || o.userData.label === `glass: ${shot.mirror}`)) mirrorInfo.meshes.push(o); });
    if (shot.mirror !== 'mirror') mirrorInfo.meshes.forEach((m) => { m.userData.look = { ...m.userData.look, glass: false, grey: 0.25, col: 0x302a48 }; });
  }
  if (shot.mirrorSearch && mirrorInfo) {
    // grid-search camera positions in the front cabin; score = how far inside the mirror both reflected faces land
    const heads = shot.mirrorSearch.faces.map((w) => figs[w].userData.P.eyes);
    const Mx = mirrorInfo.cs[1].clone().sub(mirrorInfo.cs[0]), My = mirrorInfo.cs[3].clone().sub(mirrorInfo.cs[0]);
    const inMirror = (C, H) => { // ray C -> R(H) hits the mirror plane at uv
      const Hr = H.clone().applyMatrix4(mirrorInfo.R); const dir = Hr.clone().sub(C); const den = dir.dot(mirrorInfo.n); if (Math.abs(den) < 1e-6) return -1;
      const s = (mirrorInfo.d - C.dot(mirrorInfo.n)) / den; if (s <= 0 || s >= 1) return -1; const p = C.clone().addScaledVector(dir, s).sub(mirrorInfo.cs[0]);
      const u = p.dot(Mx) / Mx.lengthSq(), v = p.dot(My) / My.lengthSq(); return Math.min(u, 1 - u, v, 1 - v); };
    let best = null; const [xr, yr, zr] = shot.mirrorSearch.box;
    for (let x = xr[0]; x <= xr[1] + 1e-9; x += 0.02) for (let y = yr[0]; y <= yr[1] + 1e-9; y += 0.02) for (let z = zr[0]; z <= zr[1] + 1e-9; z += 0.02) {
      const C = V(x, y, z); const sc = Math.min(...heads.map((H) => inMirror(C, H))); if (!best || sc > best.sc) best = { sc, C }; }
    shot.pos = best.C.toArray().map((v) => +v.toFixed(3)); shot.mirrorScore = +best.sc.toFixed(3);
  }
  Object.assign(shot, solveCamera(shot, figs, null, aim));
  const cam = makeCam(shot);
  // lights
  const lamps = lampsAt(t, 4);
  const lights = lamps.map((L, i) => ({ name: `streetlight_${i}`, kind: `sodium spot (${L.side})`, pos: V(L.lamp), aim: V(L.lamp[0], 0, L.lamp[2]), color: '#ffb468', on: true }));
  lights.push({ name: 'dusk_sky', kind: 'violet sky dome', pos: V(0, 40, -120), color: '#6a5a9a', on: true });
  const rig = (mode) => {
    const L = []; if (mode === 'none') return L; const white = mode !== 'lit';
    lamps.forEach((Lp, i) => { const s = new THREE.SpotLight(white ? 0xffffff : ROAD.lampColor, mode === 'lit' ? 900 : 60, 0, rad(62), 0.5, mode === 'lit' ? 1.6 : 1.0);
      s.position.set(...Lp.lamp); s.target.position.set(Lp.lamp[0] + (Lp.side === 'right' ? -1.5 : 1.5), 0, Lp.lamp[2]); s.castShadow = i < 2; s.shadow.camera.near = 1; s.shadow.camera.far = 40; s.shadow.bias = -0.0006; L.push(s); });
    if (mode === 'lit') { const h = new THREE.HemisphereLight(0x8a78c0, 0x201820, 0.9); L.push(h); const d = new THREE.DirectionalLight(0x9a88d0, 0.8); d.position.set(-20, 10, -60); L.push(d); }
    else { L.push(new THREE.AmbientLight(0xffffff, 1.6)); const d = new THREE.DirectionalLight(0xffffff, 0.9); d.position.set(-2, 4, -3); L.push(d); }
    return L;
  };
  const extraOut = (c, P) => {
    const out = { ...(shot.v3 ? { layout_version: 3, seating: { daughter: 'rear right (behind the front passenger seat), forward-facing child seat', empty_child_seat: 'rear left (behind the driver)', driver: 'Jade, front left (left-hand drive)', front_passenger_seat: 'empty',
      daughter_seat_px: P(V(CAR.carSeat.x, 1.05, CAR.carSeat.z + 0.2)), empty_seat_px: P(V(-CAR.carSeat.x, 1.05, CAR.carSeat.z + 0.2)), passenger_headrest_px: P(V(CAR.frontSeatX, CAR.frontHp.y + 0.72, CAR.frontHp.z + 0.37)), driver_headrest_px: P(V(-CAR.frontSeatX, CAR.frontHp.y + 0.72, CAR.frontHp.z + 0.37)) }, serves: shot.serves } : {}), streetlight_t: t, streetlights: lamps.map((L) => ({ side: L.side, lamp_world: L.lamp.map((v) => +v.toFixed(2)), lamp_px: P(V(L.lamp)) })) };
    // where each lamp's light falls through each pane: the direction from lamp to pane centre, in screen space
    out.pane_backlight = Object.fromEntries(Object.entries(panes).filter(([k]) => k !== 'mirror').map(([k, cs]) => { const cen = cs.reduce((a, v) => a.add(v), V(0, 0, 0)).multiplyScalar(0.25);
      const L0 = V(lamps[0].lamp); const a = P(cen), b = P(cen.clone().addScaledVector(cen.clone().sub(L0).normalize(), 0.1)); const dx = b[0] - a[0], dy = b[1] - a[1], n = Math.hypot(dx, dy) || 1;
      return [k, { nearest_lamp: lamps[0].side, light_travel_dir_px: [+(dx / n).toFixed(3), +(dy / n).toFixed(3)] }]; }));
    return out;
  };
  const built = { set: 'car26', scene, root, cam, rig, near: shot.near ?? 0.2, far: shot.far ?? 60, figs, book: null, panes, lights, header: shot.header || '',
    shadowLine: false, flatBg: 0xc8c8cc, litBg: 0x2a2442, extra: extraOut };
  if (mirrorInfo) {
    built.mirror = { R: mirrorInfo.R, meshes: mirrorInfo.meshes, clipPlane: new THREE.Plane(mirrorInfo.n.clone().negate(), mirrorInfo.d),
      quadPx: (cm) => mirrorInfo.cs.map((v) => { const p = v.clone().project(cm); return [(p.x + 1) / 2 * 1920, (1 - p.y) / 2 * 1080]; }),
      report: (cm, P) => { const out = { pane: shot.mirror, normal: mirrorInfo.n.toArray().map((v) => +v.toFixed(3)), search_score: shot.mirrorScore ?? null, reflected_faces: {} };
        for (const [w, f] of Object.entries(figs)) { const Hr = f.userData.P.eyes.clone().applyMatrix4(mirrorInfo.R); const px = P(Hr);
          const q = built.mirror.quadPx(cm); const inside = pointInQuad(px, q); out.reflected_faces[w] = { px, inside_mirror: inside }; }
        return out; } };
  }
  return built;
}
function pointInQuad(p, q) { let s = 0; for (let i = 0; i < 4; i++) { const a = q[i], b = q[(i + 1) % 4]; const c = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]); if (c !== 0) { if (s === 0) s = Math.sign(c); else if (Math.sign(c) !== s) return false; } } return true; }

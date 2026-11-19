// Build one bed26 shot: the child's bedroom (layout.js) + Jade + the daughter + book + flashlight + light rig.
import * as THREE from 'three';
import { mk, box, cyl, ball, quad, slab, tag, V, rad, UP, basisQ } from '../../engine/core.js';
import { stage, casterMeshes, projectShadow, solveCamera, hideParts, namedPoint } from '../../engine/stage.js';
import { aim } from '../../engine/aim.js';
import { ROOM, BED, BED_TOP, RUG, WINDOW, SHELF, NIGHTSTAND, LIGHTS } from './layout.js';
import { coverBlanket, cardOverPage, handShadows } from '../../engine/props.js';
import { pushEnd, levelRoll } from '../../engine/lap.js';
import { buildBody } from '../../engine/body.js';
import { room4, quiltOnBed, BED4_TOP, WINDOW4, ROOM4, DOOR4 } from './v4.js';

const WALL = { grey: 0.72, col: 0x5a5c70 }, FLOOR = { grey: 0.5, col: 0x4a3c34 }, WOOD = { grey: 0.6, col: 0x9a8a78 };

function room(shot = {}) {
  const g = new THREE.Group(); const { x0, x1, z0, z1, h } = ROOM;
  g.add(tag(box(x1 - x0, 0.02, z1 - z0, FLOOR, [0, -0.01, 0]), 'floor'));
  g.add(tag(box(x1 - x0, 0.02, z1 - z0, { grey: 0.8, col: 0x5a5c70 }, [0, h + 0.01, 0]), 'ceiling'));
  // back wall with the window opening (extruded shape with a hole)
  { const sh = new THREE.Shape(); sh.moveTo(x0, 0); sh.lineTo(x1, 0); sh.lineTo(x1, h); sh.lineTo(x0, h); sh.lineTo(x0, 0);
    const W = WINDOW, hole = new THREE.Path(); hole.moveTo(W.x - W.w / 2, W.sill); hole.lineTo(W.x + W.w / 2, W.sill); hole.lineTo(W.x + W.w / 2, W.sill + W.h); hole.lineTo(W.x - W.w / 2, W.sill + W.h); hole.lineTo(W.x - W.w / 2, W.sill); sh.holes.push(hole);
    const m = mk(new THREE.ExtrudeGeometry(sh, { depth: 0.1, bevelEnabled: false }), WALL); m.position.z = z0 - 0.1; g.add(tag(m, 'back wall')); }
  g.add(tag(box(0.1, h, z1 - z0, WALL, [x0 - 0.05, h / 2, 0]), 'left wall'));
  g.add(tag(box(0.1, h, z1 - z0, WALL, [x1 + 0.05, h / 2, 0]), 'right wall'));
  g.add(tag(box(x1 - x0, h, 0.1, WALL, [0, h / 2, z1 + 0.05]), 'front wall'));
  g.add(tag(box(x1 - x0, 0.08, 0.015, { grey: 0.85, col: 0xd0d0d0 }, [0, 0.04, z0 + 0.008]), 'skirting'));
  // window: frame, sill, the blind (slats, nearly closed), dusk-blue outside
  { const W = WINDOW, FR = { grey: 0.88, col: 0xe8e8e8 }, y0 = W.sill, y1 = W.sill + W.h;
    [box(W.w + 0.1, 0.05, 0.12, FR, [W.x, y0 - 0.025, z0 + 0.02]), box(W.w + 0.1, 0.05, 0.08, FR, [W.x, y1 + 0.025, z0]), box(0.05, W.h, 0.08, FR, [W.x - W.w / 2 - 0.025, (y0 + y1) / 2, z0]), box(0.05, W.h, 0.08, FR, [W.x + W.w / 2 + 0.025, (y0 + y1) / 2, z0])].forEach((m) => g.add(tag(m, 'window')));
    const n = W.slats; for (let i = 0; i < n; i++) { const s = box(W.w - 0.02, 0.003, 0.045, { grey: 0.82, col: 0xb8b4a8 }, [W.x, y1 - 0.03 - i * (W.h - 0.05) / n, z0 + 0.06]); s.rotation.x = rad(62); g.add(tag(s, 'window blind (slats)')); }
    g.add(tag(box(W.w - 0.02, 0.03, 0.05, { grey: 0.82, col: 0xb8b4a8 }, [W.x, y1 - 0.015, z0 + 0.06]), 'window blind (slats)'));
    g.add(tag(box(W.w + 0.4, W.h + 0.4, 0.02, { grey: 0.35, col: 0x2a3050, emit: 0x1c2444, emitI: 1, flatEmit: 0.4 }, [W.x, (y0 + y1) / 2, z0 - 0.6]), 'night sky (dusk blue)'));
  }
  // bed
  { const B = BED, cx = (B.x0 + B.x1) / 2, cz = (B.z0 + B.z1) / 2, L = B.z1 - B.z0, Wd = B.x1 - B.x0;
    g.add(tag(box(Wd, B.frameH - 0.04, L, WOOD, [cx, (B.frameH - 0.04) / 2 + 0.04, cz]), 'child bed'));
    g.add(tag(box(Wd, B.headH, 0.04, WOOD, [cx, B.headH / 2, B.z0 - 0.02]), 'child bed (headboard)'));
    g.add(tag(box(Wd, B.footH, 0.04, WOOD, [cx, B.footH / 2, B.z1 + 0.02]), 'child bed (footboard)'));
    g.add(tag(box(Wd - 0.03, B.mattress, L - 0.02, { grey: 0.9, col: 0xd8d4cc }, [cx, B.frameH + B.mattress / 2, cz]), 'mattress'));
    if (shot.bedBlanket !== false) {
    g.add(tag(box(Wd + 0.04, 0.03, L * 0.62, { grey: 0.78, col: 0x8fa2c0 }, [cx - 0.01, BED_TOP + 0.012, B.z1 - L * 0.31]), 'blanket'));
    g.add(tag(box(Wd + 0.02, 0.25, 0.012, { grey: 0.78, col: 0x8fa2c0 }, [cx - 0.01, BED_TOP - 0.11, B.z1 - L * 0.31]), 'blanket'));
    g.add(tag(box(0.012, 0.22, L * 0.62, { grey: 0.78, col: 0x8fa2c0 }, [B.x0 - 0.008, BED_TOP - 0.1, B.z1 - L * 0.31]), 'blanket'));
    }
    const p = box(0.45, 0.1, 0.3, { grey: 0.95, col: 0xe8e0e8 }, [cx, BED_TOP + 0.05, B.z0 + 0.2]); g.add(tag(p, 'pillow'));
    g.add(tag(ball(0.09, { grey: 0.55, col: 0x9a6a4a }, [cx + 0.18, BED_TOP + 0.16, B.z0 + 0.12], [1, 1.1, 0.9]), 'stuffed toy'));
  }
  // rug
  g.add(tag(box(RUG.w, 0.012, RUG.d, { grey: 0.62, col: 0x7a5a6a }, [RUG.x, 0.006, RUG.z]), 'rug'));
  // bookshelf on the left wall
  { const S = SHELF, gS = new THREE.Group(); gS.position.set(S.x + S.d / 2, 0, S.z); gS.rotation.y = rad(90);
    gS.add(box(S.w, S.h, 0.02, WOOD, [0, S.h / 2, -S.d / 2 + 0.01])); for (const s of [-1, 1]) gS.add(box(0.02, S.h, S.d, WOOD, [s * (S.w / 2 - 0.01), S.h / 2, 0]));
    for (let i = 0; i <= S.shelves; i++) gS.add(box(S.w, 0.02, S.d, WOOD, [0, 0.03 + i * (S.h - 0.05) / S.shelves, 0]));
    for (let i = 0; i < S.shelves; i++) { let x = -S.w / 2 + 0.04; let k = 0; while (x < S.w / 2 - 0.08) { const bw = 0.025 + ((i * 7 + k * 3) % 4) * 0.012, bh = 0.16 + ((i + k) % 3) * 0.04;
      gS.add(box(bw, bh, 0.2, { grey: 0.3 + ((i + k) % 5) * 0.1, col: [0xc05040, 0x4070a0, 0xe0b040, 0x50a070, 0x8060a0][(i + k) % 5] }, [x + bw / 2, 0.04 + i * (S.h - 0.05) / S.shelves + bh / 2, 0.02])); x += bw + 0.004; k++; } }
    g.add(tag(gS, 'bookshelf')); }
  // nightstand + night-light (off)
  { const N = NIGHTSTAND; g.add(tag(box(N.w, N.h, N.d, WOOD, [N.x, N.h / 2, N.z]), 'nightstand'));
    g.add(tag(cyl(0.06, 0.08, 0.14, { grey: 0.9, col: 0xf0e8d8 }, [N.x, N.h + 0.07, N.z]), 'night-light (off)'));
    g.add(tag(box(0.12, 0.03, 0.08, { grey: 0.3, col: 0x303040 }, [N.x - 0.1, N.h + 0.015, N.z + 0.08]), 'nightstand')); }
  return g;
}

// the flashlight: { aimAt: point, from: [dx,dy,dz] (lens = aim point + from), on, lying: bool }
function flashlightFor(spec, figs, book) {
  if (!spec) return null;
  const target = namedPoint(spec.aimAt, figs, book);
  const lens = spec.at ? V(spec.at) : target.clone().add(V(spec.from));
  const axis = target.clone().sub(lens).normalize();
  const body = lens.clone().addScaledVector(axis, -0.065);
  const g = new THREE.Group(); const q = new THREE.Quaternion().setFromUnitVectors(UP, axis);
  const b = cyl(0.014, 0.014, 0.11, { grey: 0.35, col: 0xe8792c }, body.toArray(), null, 16); b.quaternion.copy(q); g.add(b);
  const h = cyl(0.02, 0.016, 0.03, { grey: 0.3, col: 0x2a2a2a }, lens.clone().addScaledVector(axis, -0.012).toArray(), null, 16); h.quaternion.copy(q); g.add(h);
  const lensM = cyl(0.017, 0.017, 0.003, { grey: 1, col: 0xffffff, emit: spec.on === false ? undefined : 0xfff4e6, emitI: 0.9, flatEmit: 0.98 }, lens.toArray(), null, 16); lensM.quaternion.copy(q); g.add(lensM);
  // the switch: a small button on top near the tail
  let side = new THREE.Vector3().crossVectors(axis, UP); if (side.lengthSq() < 1e-4) side.set(1, 0, 0); side.normalize(); const topDir = new THREE.Vector3().crossVectors(side, axis).normalize();
  const sw = box(0.012, 0.006, 0.016, { grey: 0.1, col: 0x111111 }, body.clone().addScaledVector(axis, -0.025).addScaledVector(topDir, 0.015).toArray()); sw.quaternion.copy(basisQ(side, topDir, axis.clone().negate()).multiply(new THREE.Quaternion())); g.add(sw);
  tag(g, spec.on === false ? 'flashlight (off)' : 'flashlight (on)');
  return { group: g, lens, axis, body, grip: body.clone().addScaledVector(axis, -0.01), switchAt: body.clone().addScaledVector(axis, -0.025).addScaledVector(topDir, 0.015), on: spec.on !== false };
}

export function build(shot, ctx) { return shot.v3 ? buildV3(shot, ctx) : buildV1(shot, ctx); }
function buildV1(shot, { makeCam }) {
  const scene = new THREE.Scene(); const root = new THREE.Group(); scene.add(root);
  root.add(room());
  // targets: 'flash:grip', 'flash:switch', 'flash:lens', 'flash:axis' need the flashlight, which needs the book
  let flash = null;
  const extra = (t, figs, book) => {
    if (t.startsWith('flash:')) { if (!flash) { try { flash = flashlightFor(shot.flashlight, figs, book); } catch (e) { return null; } } if (!flash) return null;
      return ({ grip: flash.grip, switch: flash.switchAt, lens: flash.lens, front: flash.lens.clone().addScaledVector(flash.axis, 0.2) })[t.slice(6)]?.clone() || null; }
    if (t.startsWith('ray:') && flash) { const parts = t.split(':'); const d = Number(parts.pop()); const name = parts.slice(1).join(':');
      let p; try { p = namedPoint(name, figs, book); } catch (e) { return null; } return p.clone().addScaledVector(flash.lens.clone().sub(p).normalize(), d); }
    return null;
  };
  // pass 1: stage once to place the book; then make the flashlight against the final book; stage again
  let { figs, book } = stage(shot.figs, shot.book, (t) => (t.startsWith('flash:') || t.startsWith('ray:')) ? V(0.5, 0.65, -0.5) : null);
  flash = shot.flashlight ? flashlightFor(shot.flashlight, figs, book) : null;
  ({ figs, book } = stage(shot.figs, shot.book, (t, f, b) => extra(t, f, b || book)));
  if (shot.flashlight) flash = flashlightFor(shot.flashlight, figs, book);
  for (const f of Object.values(figs)) root.add(f);
  if (book) root.add(book.group);
  if (flash) root.add(flash.group);
  Object.assign(shot, solveCamera(shot, figs, book, aim));
  hideParts(shot.hideParts, figs);
  const cam = makeCam(shot);
  const on = flash && flash.on;
  const lights = [];
  if (flash) lights.push({ name: 'flashlight', kind: 'spot 16 deg (handheld)', pos: flash.lens, aim: flash.lens.clone().addScaledVector(flash.axis, 1), color: '#fff4e6', on });
  lights.push({ name: 'window_blind', kind: 'blue night glow through slats', pos: V(LIGHTS.moon.pos), color: '#6070a0', on: true });
  const rig = (mode) => {
    const L = []; if (mode === 'none') return L; const white = mode !== 'lit';
    if (on) { const s = new THREE.SpotLight(white ? 0xffffff : LIGHTS.flashlight.color, mode === 'lit' ? 9 : mode === 'mask' ? 6 : 2.4, 0, rad(shot.flashCone ?? 17), 0.35, mode === 'lit' ? 1.6 : 0);
      s.position.copy(flash.lens).addScaledVector(flash.axis, 0.03); s.target.position.copy(flash.lens).addScaledVector(flash.axis, 1); s.castShadow = true; s.shadow.camera.near = 0.02; s.shadow.camera.far = 6; s.shadow.bias = -0.0002; L.push(s);
      if (mode === 'lit' && book) { const b = new THREE.PointLight(0xfff0dc, 0.18, 1.6, 1.5); b.position.copy(book.at).addScaledVector(book.n, 0.08); L.push(b); } }   // bounce off the page
    if (mode === 'mask') return L;
    if (mode === 'lit') { const m = new THREE.SpotLight(0x5868a0, 1.2, 0, rad(40), 0.8, 1.2); m.position.set(...LIGHTS.moon.pos); m.target.position.set(0.4, 0.3, 0.2); L.push(m); }
    L.push(new THREE.AmbientLight(white ? 0xffffff : 0x1a2238, mode === 'lit' ? (shot.amb ?? 0.35) : (on ? 1.5 : 1.9)));
    if (white) { const d = new THREE.DirectionalLight(0xffffff, 1.0); d.position.set(-1, 3, 2); L.push(d); }
    return L;
  };
  let shadowPolys = null;
  if (shot.shadow && book && book.pages && on) {
    const meshes = shot.shadow.casters.flatMap((c) => casterMeshes(c, figs));
    const sp = projectShadow(flash.lens, meshes, book);
    const toPx = (v) => { const p = v.clone().project(cam); return [+((p.x + 1) / 2 * 1920).toFixed(1), +((1 - p.y) / 2 * 1080).toFixed(1)]; };
    shadowPolys = { light: 'flashlight', receiver: 'storybook spread', uv: sp.uv, px: sp.world.map((poly) => poly.map(toPx)), bbox: sp.bbox,
      note: `convex hull of each caster part (${shot.shadow.casters.join(', ')}) projected from the flashlight lens onto the spread plane; uv 0..1 across the spread, v down` };
  }
  const extraOut = (c, P) => flash ? { flashlight: { lens_px: P(flash.lens), switch_px: P(flash.switchAt), tail_px: P(flash.body.clone().addScaledVector(flash.axis, -0.055)), on } } : {};
  return { set: 'bed26', scene, root, cam, rig, near: shot.near ?? 0.2, far: shot.far ?? 5, figs, book, panes: { window: (() => { const W = WINDOW, z = ROOM.z0 + 0.04; return [V(W.x - W.w / 2, W.sill + W.h, z), V(W.x + W.w / 2, W.sill + W.h, z), V(W.x + W.w / 2, W.sill, z), V(W.x - W.w / 2, W.sill, z)]; })() }, lights,
    header: shot.header || '', shadowLine: !!shot.shadow && on, shadowPolys, subject: book ? book.at : null, litBg: 0x020204, extra: extraOut };
}

// ---------------------------------------------------------------- v3
// Lap storytime, hand-shadow cards lit by the real flashlight, push-end camera, the blanket being pulled up, richer sidecar.
function buildV3(shot, { makeCam }) {
  const scene = new THREE.Scene(); const root = new THREE.Group(); scene.add(root);
  if (shot.v4) { root.add(room4(shot)); if (shot.bedQuilt !== false) quiltOnBed(root); } else root.add(room(shot));
  let flash = null, cards = [];
  const extra = (t, figs, book) => {
    if (t.startsWith('flash:')) { if (!flash) return V(0.4, 0.6, 0.1); return ({ grip: flash.grip, switch: flash.switchAt, lens: flash.lens, front: flash.lens.clone().addScaledVector(flash.axis, 0.2) })[t.slice(6)]?.clone() || null; }
    if (t.startsWith('card:')) { const [, i, part] = t.split(':'); const c = cards[+i]; if (!c) return V(0.4, 0.5, 0); return (part === 'centre' ? c.centre : c.base).clone(); }
    if (t.startsWith('ray:')) { if (!flash) return V(0.4, 0.5, 0); const parts = t.split(':'); const d = Number(parts.pop()); const name = parts.slice(1).join(':');
      let p; try { p = namedPoint(name, figs, book); } catch (e) { return null; } return p.clone().addScaledVector(flash.lens.clone().sub(p).normalize(), d); }
    if (t.startsWith('lift:')) { if (!flash || !book || !book.pages) return V(0.4, 0.5, 0); const parts = t.split(':'); const hgt = Number(parts.pop());
      const p = parts[1] === 'page' ? book.pageAt(parts[2], Number(parts[3]), Number(parts[4])) : book.anchors[parts[1]].clone(); const dir = flash.lens.clone().sub(p).normalize();
      return p.addScaledVector(dir, hgt / Math.max(dir.dot(book.n), 0.05)); }
    return null;
  };
  const SO = shot.v4 ? { builder: buildBody } : {};
  let { figs, book } = stage(shot.figs, shot.book, extra, SO);
  for (let k = 0; k < 2; k++) { flash = shot.flashlight ? flashlightFor(shot.flashlight, figs, book) : null;
    cards = flash && book && book.pages ? (shot.cards || []).map((c) => cardOverPage(c, book, flash.lens)) : [];
    ({ figs, book } = stage(shot.figs, shot.book, extra, SO)); }
  if (shot.flashlight) flash = flashlightFor(shot.flashlight, figs, book);
  if (flash && book && book.pages) cards = (shot.cards || []).map((c) => cardOverPage(c, book, flash.lens));
  if (shot.hide) root.traverse((o) => { if (o.isMesh && shot.hide.includes(o.userData.label)) o.visible = false; });
  for (const f of Object.values(figs)) root.add(f);
  if (book) root.add(book.group);
  if (flash) root.add(flash.group);
  for (const c of cards) root.add(c.mesh);
  let blanketInfo = null;
  if (shot.pull && figs[shot.pull.who]) { blanketInfo = coverBlanket(figs[shot.pull.who].userData.P, shot.v4 ? BED4_TOP : BED_TOP, shot.v4 ? { grey: 0.8, col: 0xc8c0d8 } : { grey: 0.78, col: 0x8fa2c0 }, { upTo: shot.pull.upTo ?? 0.8, halfW: 0.3 }); root.add(blanketInfo.group); }
  if (shot.push) { const from = { ...shot.push.fromShot }; Object.assign(from, solveCamera(from, figs, book, aim)); const pe = pushEnd(from.pos, book, shot.lens, shot.push.fill); shot.pos = pe.pos; shot.target = pe.target;
    shot.pushInfo = { start_position: from.pos, start_target: from.target, start_distance_to_gutter_m: +pe.startDist.toFixed(3), end_distance_to_gutter_m: +pe.dist.toFixed(3), swing_onto_page_normal_deg: +pe.swing.toFixed(1) }; }
  else Object.assign(shot, solveCamera(shot, figs, book, aim));
  if (shot.push) shot.roll = levelRoll(shot.pos, shot.target, book, 1); else if (shot.levelBook && book) shot.roll = levelRoll(shot.pos, shot.target, book, shot.levelBook);
  hideParts(shot.hideParts, figs);
  const cam = makeCam(shot);
  const on = !!(flash && flash.on);
  const lights = [];
  if (flash) lights.push({ name: 'flashlight', kind: 'spot (small handheld LED)', pos: flash.lens, aim: flash.lens.clone().addScaledVector(flash.axis, 1), color: '#fff4e6', on });
  lights.push({ name: 'window_blind', kind: 'blue night glow through slats', pos: shot.v4 ? V(WINDOW4.x, 1.5, ROOM4.z0 - 0.8) : V(LIGHTS.moon.pos), color: '#6070a0', on: true });
  const DOORL = V(DOOR4.x + 1.0, 1.9, (DOOR4.z0 + DOOR4.z1) / 2);
  if (shot.v4) lights.push({ name: 'door_hall', kind: 'warm tungsten spill from the hallway through the open door (frame right in L2)', pos: DOORL, aim: V(0.2, 0.3, -0.6), color: '#ffb468', on: shot.doorLight !== false });
  const rig = (mode) => {
    const L = []; if (mode === 'none') return L; const white = mode !== 'lit';
    if (on) { const s = new THREE.SpotLight(white ? 0xffffff : LIGHTS.flashlight.color, mode === 'lit' ? 9 : mode === 'mask' ? 6 : 2.4, 0, rad(shot.flashCone ?? 24), 0.35, mode === 'lit' ? 1.6 : 0);
      s.position.copy(flash.lens).addScaledVector(flash.axis, 0.012); s.target.position.copy(flash.lens).addScaledVector(flash.axis, 1); s.castShadow = true; s.shadow.camera.near = 0.02; s.shadow.camera.far = 6; s.shadow.bias = -0.0002; L.push(s);
      if (mode === 'lit' && book) { const b = new THREE.PointLight(0xfff0dc, 0.22, 1.6, 1.5); b.position.copy(book.at).addScaledVector(book.n, 0.1); L.push(b); } }
    if (mode === 'mask') return L;
    if (mode === 'lit') { const m = new THREE.SpotLight(0x5868a0, 1.2, 0, rad(40), 0.8, 1.2); if (shot.v4) { m.position.set(WINDOW4.x, 1.5, ROOM4.z0 - 0.6); m.target.position.set(-0.2, 0.4, -0.2); } else { m.position.set(...LIGHTS.moon.pos); m.target.position.set(0.4, 0.3, 0.2); } L.push(m); }
    if (shot.v4 && shot.doorLight !== false) { const d = new THREE.SpotLight(white ? 0xffffff : 0xffb468, mode === 'lit' ? (shot.doorI ?? 7) : 0.9, 0, rad(55), 0.5, mode === 'lit' ? 1.3 : 0); d.position.copy(DOORL); d.target.position.set(0.2, 0.3, -0.6); d.castShadow = true; d.shadow.camera.near = 0.2; d.shadow.camera.far = 8; L.push(d); }
    L.push(new THREE.AmbientLight(white ? 0xffffff : 0x1a2238, mode === 'lit' ? (shot.amb ?? 0.35) : (on ? 1.5 : 1.9)));
    if (white) { const d = new THREE.DirectionalLight(0xffffff, 1.0); d.position.set(-1, 3, 2); L.push(d); }
    return L;
  };
  const toPx = (v) => { const p = v.clone().project(cam); return [+((p.x + 1) / 2 * 1920).toFixed(1), +((1 - p.y) / 2 * 1080).toFixed(1)]; };
  const shadow = on ? handShadows({ shot, figs, book, cards, lightPos: flash.lens, lightName: 'flashlight (lens)', toPx, lightSize: 0.02 }) : null;
  const extraOut = (c, P) => { const out = { layout_version: 3 };
    if (flash) out.flashlight = { lens_px: P(flash.lens), lens_world: flash.lens.toArray().map((x) => +x.toFixed(4)), axis: flash.axis.toArray().map((x) => +x.toFixed(3)), switch_px: P(flash.switchAt), tail_px: P(flash.body.clone().addScaledVector(flash.axis, -0.055)), on, cone_half_angle_deg: shot.flashCone ?? 24 };
    if (shadow) out.hand_shadow = shadow.sidecar;
    if (blanketInfo) out.blanket = { edge_centre_px: P(blanketInfo.edge), edge_centre_world: blanketInfo.edge.toArray().map((x) => +x.toFixed(3)), note: 'top edge of the blanket (where the hands grip); it travels toward the child\'s chin' };
    if (shot.pushInfo) out.push = { ...shot.pushInfo, note: 'end of the push that starts at v3_LAP_ots; book.spread px here is the target of the move' };
    if (shot.serves) out.serves = shot.serves;
    return out; };
  return { set: 'bed26', scene, root, cam, rig, near: shot.near ?? 0.2, far: shot.far ?? 6, figs, book, panes: { window: (() => { const W = shot.v4 ? { ...WINDOW4 } : WINDOW, z = (shot.v4 ? ROOM4.z0 : ROOM.z0) + 0.04; return [V(W.x - W.w / 2, W.sill + W.h, z), V(W.x + W.w / 2, W.sill + W.h, z), V(W.x + W.w / 2, W.sill, z), V(W.x - W.w / 2, W.sill, z)]; })() }, lights,
    header: shot.header || '', shadowLine: !!shadow, shadowPolys: shadow ? shadow.polys : null, subject: book ? book.at : null, litBg: 0x020204, extra: extraOut };
}

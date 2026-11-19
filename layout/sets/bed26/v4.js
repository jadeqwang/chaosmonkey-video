// BEDROOM 2026, v4 fixed set (SETS team, preview_v4): rebuilt to match shot L2 of preview_v3, the director's reference
// ("this scene blocking is actually reasonable here, let's make the others match it"). Every bedroom camera stands in
// this one room. Metres, y up, floor y = 0.
//   x: -2.8 left wall ... +1.6 right wall (the door)      z: -1.8 back wall (bed head, window) ... +1.8 front wall
// From the foot of the bed (L2's camera, looking -z): headboard on the back wall; the window with its slatted blind
// above and LEFT of the headboard; the nightstand at the head on the window side (left); the bunny on the far (right)
// side of the pillow; Jade kneels on the rug on the left; the open door is in the right wall, warm hall light from frame
// right. Storytime: Jade sits on the rug with her back against the bed's left (window-side) rail, facing -x.
import * as THREE from 'three';
import { mk, box, cyl, ball, tag, V, rad } from '../../engine/core.js';

export const ROOM4 = { x0: -2.8, x1: 1.6, z0: -1.8, z1: 1.8, h: 2.6 };
export const BED4 = { x0: -0.2, x1: 0.8, z0: -1.78, z1: 0.24, railH: 0.3, top: 0.5, head: { h: 0.86, t: 0.05 }, foot: { h: 0.56, t: 0.05 } };   // twin, wooden frame
export const BED4_TOP = BED4.top;
export const PILLOW4 = { x: 0.3, z: -1.48, w: 0.56, d: 0.34, t: 0.13 };
export const BUNNY4 = { x: 0.64, z: -1.32 };                         // sits on the mattress, far (right) side of the pillow
export const NIGHTSTAND4 = { x: -0.53, z: -1.58, w: 0.44, h: 0.58, d: 0.4 };
export const WINDOW4 = { x: -1.3, sill: 0.95, w: 1.0, h: 1.05, slats: 24 };
export const DOOR4 = { x: 1.6, z0: 0.55, z1: 1.4, h: 2.03, open: 62 };   // hinge at z1, opens into the room
export const RUG4 = { x0: -2.05, x1: -0.22, z0: -1.25, z1: 0.65 };
export const SHELF4 = { x: -2.05, z: 1.8, w: 0.9, h: 1.2, d: 0.3, shelves: 4 }; // against the front wall, left corner
export const LAP4 = { base: [-0.44, -0.42], yaw: -90, floor: 0.02 };
// the daughter asleep in her bed (head on the pillow toward -z)
export const DAUGHTER_LIE = { at: [0.3, BED4_TOP + 0.085, -0.96], legs: 'straight', pitch: -90, yaw: 0, spine: { bend: 6 }, head: { turn: -25 }, L: 'side', R: 'side' };

const WALL = { grey: 0.72, col: 0x4c4f66 }, FLOOR = { grey: 0.52, col: 0x5a4636 }, WOOD = { grey: 0.46, col: 0x6e4e34 };
export function room4(shot = {}) {
  const g = new THREE.Group(); const { x0, x1, z0, z1, h } = ROOM4;
  g.add(tag(box(x1 - x0, 0.02, z1 - z0, FLOOR, [(x0 + x1) / 2, -0.01, 0]), 'floor (wood)'));
  g.add(tag(box(x1 - x0, 0.02, z1 - z0, { grey: 0.82, col: 0x4c4f66 }, [(x0 + x1) / 2, h + 0.01, 0]), 'ceiling'));
  const wallWithHole = (len, hx0, hx1, hy0, hy1, look) => { const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(len, 0); sh.lineTo(len, h); sh.lineTo(0, h); sh.lineTo(0, 0);
    const p = new THREE.Path(); p.moveTo(hx0, hy0); p.lineTo(hx1, hy0); p.lineTo(hx1, hy1); p.lineTo(hx0, hy1); p.lineTo(hx0, hy0); sh.holes.push(p); return mk(new THREE.ExtrudeGeometry(sh, { depth: 0.1, bevelEnabled: false }), look); };
  { const W = WINDOW4; const m = wallWithHole(x1 - x0, W.x - W.w / 2 - x0, W.x + W.w / 2 - x0, W.sill, W.sill + W.h, WALL); m.position.set(x0, 0, z0 - 0.1); g.add(tag(m, 'back wall')); }
  { const D = DOOR4; const m = wallWithHole(z1 - z0, D.z0 - z0, D.z1 - z0, 0.001, D.h, WALL); m.rotation.y = rad(-90); m.position.set(x1, 0, z0); g.add(tag(m, 'right wall (door)')); }
  g.add(tag(box(0.1, h, z1 - z0, WALL, [x0 - 0.05, h / 2, 0]), 'left wall'));
  g.add(tag(box(x1 - x0, h, 0.1, WALL, [(x0 + x1) / 2, h / 2, z1 + 0.05]), 'front wall'));
  for (const [a, b, z, x] of [[x0, x1, z0 + 0.008, null], [z0, z1, null, x0 + 0.008]]) g.add(tag(z !== null ? box(b - a, 0.08, 0.015, { grey: 0.85, col: 0xd0d0d0 }, [(a + b) / 2, 0.04, z]) : box(0.015, 0.08, b - a, { grey: 0.85, col: 0xd0d0d0 }, [x, 0.04, (a + b) / 2]), 'skirting'));
  // window: white frame, slatted blind (nearly closed), dusk-blue night beyond
  { const W = WINDOW4, FR = { grey: 0.88, col: 0xe0e0e0 }, y0 = W.sill, y1 = W.sill + W.h;
    [box(W.w + 0.12, 0.05, 0.14, FR, [W.x, y0 - 0.025, z0 + 0.03]), box(W.w + 0.1, 0.05, 0.08, FR, [W.x, y1 + 0.025, z0]), box(0.05, W.h, 0.08, FR, [W.x - W.w / 2 - 0.025, (y0 + y1) / 2, z0]), box(0.05, W.h, 0.08, FR, [W.x + W.w / 2 + 0.025, (y0 + y1) / 2, z0])].forEach((m) => g.add(tag(m, 'window')));
    for (let i = 0; i < W.slats; i++) { const s = box(W.w - 0.02, 0.003, 0.045, { grey: 0.82, col: 0xb8b4a8 }, [W.x, y1 - 0.03 - i * (W.h - 0.05) / W.slats, z0 + 0.06]); s.rotation.x = rad(62); g.add(tag(s, 'window blind (slats)')); }
    g.add(tag(box(W.w - 0.02, 0.035, 0.05, { grey: 0.82, col: 0xb8b4a8 }, [W.x, y1 - 0.015, z0 + 0.06]), 'window blind (slats)'));
    g.add(tag(box(W.w + 0.4, W.h + 0.4, 0.02, { grey: 0.35, col: 0x2a3050, emit: 0x1c2444, emitI: 1, flatEmit: 0.4 }, [W.x, (y0 + y1) / 2, z0 - 0.6]), 'night sky (dusk blue)')); }
  // door: frame, leaf open into the room, lit hallway beyond
  { const D = DOOR4, FR = { grey: 0.85, col: 0xd8d4cc }, zc = (D.z0 + D.z1) / 2, wd = D.z1 - D.z0;
    g.add(tag(box(0.14, 0.06, wd + 0.12, FR, [x1, D.h + 0.03, zc]), 'door frame')); for (const z of [D.z0 - 0.03, D.z1 + 0.03]) g.add(tag(box(0.14, D.h, 0.06, FR, [x1, D.h / 2, z]), 'door frame'));
    const leaf = new THREE.Group(); leaf.position.set(x1 - 0.06, 0, D.z1); leaf.rotation.y = rad(-(shot.door4 ?? D.open)); leaf.add(box(0.04, D.h - 0.01, wd - 0.01, { grey: 0.88, col: 0xe0dcd4 }, [0, (D.h - 0.01) / 2, -(wd - 0.01) / 2])); leaf.add(ball(0.025, { grey: 0.3, col: 0x9a8a60 }, [-0.04, 1.0, -wd + 0.08])); g.add(tag(leaf, 'door (open)'));
    const warm = { grey: 0.92, col: 0xd9a46a, emit: 0xffb468, emitI: 0.8, flatEmit: 0.9 };
    g.add(tag(box(0.02, h, 2.4, warm, [x1 + 1.4, h / 2, zc]), 'hallway (lit)')); g.add(tag(box(1.4, 0.02, 2.4, { ...warm, emitI: 0.35 }, [x1 + 0.7, 0.0, zc]), 'hallway (lit)')); g.add(tag(box(1.4, h, 0.02, { ...warm, emitI: 0.5 }, [x1 + 0.7, h / 2, zc - 1.2]), 'hallway (lit)')); }
  // bed: wooden frame + headboard + low footboard, mattress, pillow, quilt (per shot), bunny
  { const B = BED4, cx = (B.x0 + B.x1) / 2, L = B.z1 - B.z0, Wd = B.x1 - B.x0;
    g.add(tag(box(Wd, B.railH - 0.06, L, WOOD, [cx, (B.railH - 0.06) / 2 + 0.06, (B.z0 + B.z1) / 2]), 'bed (wooden frame)'));
    for (const x of [B.x0 + 0.03, B.x1 - 0.03]) for (const z of [B.z0 + 0.03, B.z1 - 0.03]) g.add(tag(box(0.06, 0.06, 0.06, WOOD, [x, 0.03, z]), 'bed (wooden frame)'));
    g.add(tag(box(Wd + 0.06, B.head.h, B.head.t, WOOD, [cx, B.head.h / 2, B.z0 - B.head.t / 2 + 0.02]), 'headboard (wood)'));
    g.add(tag(box(Wd + 0.06, 0.05, B.head.t + 0.03, WOOD, [cx, B.head.h + 0.02, B.z0 - B.head.t / 2 + 0.02]), 'headboard (wood)'));
    g.add(tag(box(Wd + 0.04, B.foot.h, B.foot.t, WOOD, [cx, B.foot.h / 2, B.z1 + B.foot.t / 2]), 'footboard (wood)'));
    g.add(tag(box(Wd - 0.04, B.top - B.railH, L - 0.06, { grey: 0.9, col: 0xdcd8d0 }, [cx, (B.top + B.railH) / 2, (B.z0 + B.z1) / 2 + 0.01]), 'mattress'));
    const P = PILLOW4; const p = box(P.w, P.t, P.d, { grey: 0.95, col: 0xe8e4ec }, [P.x, B.top + P.t / 2, P.z]); p.rotation.y = rad(-3); g.add(tag(p, 'pillow'));
    // the bunny: sitting, ears up, facing the foot of the bed
    { const bg = new THREE.Group(), BL = { grey: 0.6, col: 0xb8a690 }; bg.position.set(BUNNY4.x, B.top, BUNNY4.z);
      bg.add(ball(0.075, BL, [0, 0.075, 0], [1, 1.05, 0.9])); bg.add(ball(0.06, BL, [0, 0.19, 0.015])); for (const s of [-1, 1]) { const e = cyl(0.016, 0.02, 0.12, BL, [s * 0.028, 0.29, 0.0], [0, 0, s * 10], 10); bg.add(e); bg.add(ball(0.025, BL, [s * 0.06, 0.03, 0.06])); }
      g.add(tag(bg, 'bunny (stuffed toy)')); }
  }
  // nightstand (head, window side) with a cup and a closed night-light
  { const N = NIGHTSTAND4; g.add(tag(box(N.w, N.h, N.d, WOOD, [N.x, N.h / 2, N.z]), 'nightstand'));
    g.add(tag(box(N.w - 0.04, 0.012, 0.01, { grey: 0.3, col: 0x3a2a1c }, [N.x, N.h * 0.62, N.z + N.d / 2 + 0.003]), 'nightstand'));
    g.add(tag(cyl(0.035, 0.03, 0.1, { grey: 0.85, col: 0xd0d8e0 }, [N.x + 0.08, N.h + 0.05, N.z + 0.06], null, 16), 'cup (on the nightstand)'));
    g.add(tag(cyl(0.05, 0.065, 0.12, { grey: 0.9, col: 0xf0e8d8 }, [N.x - 0.1, N.h + 0.06, N.z - 0.05], null, 16), 'night-light (off)')); }
  // rug: fluffy, on the left of the bed
  { const R = RUG4; g.add(tag(box(R.x1 - R.x0, 0.02, R.z1 - R.z0, { grey: 0.66, col: 0x8a7a90 }, [(R.x0 + R.x1) / 2, 0.01, (R.z0 + R.z1) / 2]), 'rug (fluffy)')); }
  // bookshelf: front wall, left corner
  { const S = SHELF4, gS = new THREE.Group(); gS.position.set(S.x, 0, S.z - S.d / 2); gS.rotation.y = rad(180);
    gS.add(box(S.w, S.h, 0.02, WOOD, [0, S.h / 2, -S.d / 2 + 0.01])); for (const s of [-1, 1]) gS.add(box(0.02, S.h, S.d, WOOD, [s * (S.w / 2 - 0.01), S.h / 2, 0]));
    for (let i = 0; i <= S.shelves; i++) gS.add(box(S.w, 0.02, S.d, WOOD, [0, 0.03 + i * (S.h - 0.05) / S.shelves, 0]));
    for (let i = 0; i < S.shelves; i++) { let x = -S.w / 2 + 0.04, k = 0; while (x < S.w / 2 - 0.08) { const bw = 0.025 + ((i * 7 + k * 3) % 4) * 0.012, bh = 0.16 + ((i + k) % 3) * 0.04;
      gS.add(box(bw, bh, 0.2, { grey: 0.3 + ((i + k) % 5) * 0.1, col: [0xc05040, 0x4070a0, 0xe0b040, 0x50a070, 0x8060a0][(i + k) % 5] }, [x + bw / 2, 0.04 + i * (S.h - 0.05) / S.shelves + bh / 2, 0.02])); x += bw + 0.004; k++; } }
    g.add(tag(gS, 'bookshelf')); }
  return g;
}
// the bed's quilt when nobody is under it (storytime shots): covering the lower two-thirds, turned down at the top
export function quiltOnBed(g) {
  const B = BED4, cx = (B.x0 + B.x1) / 2, L = B.z1 - B.z0, Q = { grey: 0.8, col: 0xc8c0d8 };
  g.add(tag(box(B.x1 - B.x0 + 0.06, 0.04, L * 0.66, Q, [cx, B.top + 0.02, B.z1 - L * 0.33]), 'quilt (on the bed)'));
  g.add(tag(box(B.x1 - B.x0 + 0.06, 0.07, 0.18, Q, [cx, B.top + 0.035, B.z1 - L * 0.66]), 'quilt (on the bed)'));
  for (const x of [B.x0 - 0.02, B.x1 + 0.02]) g.add(tag(box(0.015, 0.24, L * 0.66, Q, [x, B.top - 0.1, B.z1 - L * 0.33]), 'quilt (on the bed)'));
}
export const OBJECTS4 = [
  ['headboard (wood)', 'wooden headboard on the back wall, 1.06 m wide, top 0.86 m (a little above the pillow)', [0.3, 0.51, -1.78]],
  ['bed (wooden frame)', 'twin bed, wooden frame, 1.0 x 2.0 m, mattress top 0.50 m, head at the back wall', [0.3, 0.25, -0.77]],
  ['footboard (wood)', 'low wooden footboard 0.56 m', [0.3, 0.28, 0.26]],
  ['pillow', 'one pillow at the head', [0.3, 0.57, -1.48]],
  ['bunny (stuffed toy)', 'beige plush bunny, ears up, sitting on the mattress on the far (right, door-side) side of the pillow', [0.64, 0.62, -1.32]],
  ['quilt (on the bed)', 'pale lavender-white quilt', null],
  ['nightstand', 'wooden nightstand at the head of the bed on the window (left) side, 0.44 x 0.58 m, a cup and a night-light (off) on it', [-0.53, 0.29, -1.58]],
  ['window', 'window in the back wall above and left of the headboard, 1.0 x 1.05 m, sill 0.95 m', [-1.3, 1.47, -1.8]],
  ['window blind (slats)', 'white horizontal slatted blind, nearly closed; blue night between the slats', [-1.3, 1.47, -1.74]],
  ['door (open)', 'door in the right wall near the front, open into the room; warm hallway light', [1.6, 1.0, 0.97]],
  ['rug (fluffy)', 'fluffy mauve rug on the floor left of the bed, 1.8 x 1.9 m; storytime happens on it', [-1.13, 0.01, -0.3]],
  ['bookshelf', 'low bookshelf against the front wall in the left corner (behind the L2 camera)', [-2.05, 0.6, 1.65]],
  ['floor (wood)', 'wooden floor', null],
];

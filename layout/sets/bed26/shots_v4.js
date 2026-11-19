// BEDROOM 2026, v4 camera table (SETS team, preview_v4). The room is rebuilt to L2 (v4.js). Storytime: Jade on the rug,
// back against the bed's window-side rail, facing -x, the daughter in her lap, flashlight in Jade's left hand out to the
// left of the book (frame right from the front), as in v3. LAP_* cameras identical to attic88 v4 (engine/lap.js).
import { lapPose, lapCameras, lapFrame } from '../../engine/lap.js';
import { LAP4, BED4_TOP, DAUGHTER_LIE } from './v4.js';

const M = 'jade', C = 'daughter';
const CFG = { mother: M, child: C, base: LAP4.base, yaw: LAP4.yaw, floor: LAP4.floor, Hm: 1.65, Hc: 1.02 };
const F = lapFrame(LAP4.base, LAP4.yaw), CAM = lapCameras(M, C);
const T36 = 36 * Math.PI / 180, PAGE_DOWN = [F.f[0] * Math.sin(T36), -Math.cos(T36), F.f[1] * Math.sin(T36)], PAGE_TOP = [F.f[0] * Math.cos(T36), Math.sin(T36), F.f[1] * Math.cos(T36)];
const AHEAD = F.at3(0.1, 0.62, 2.2);
const FLASH = { aimAt: 'book:G', from: [0.06, 0.2, 0.3] };
const holdL = { to: 'flash:grip', hand: 'grip', thumb: 'to:flash:front', off: [0, -0.02, 0] };
const base = { v3: true, v4: true, flashlight: FLASH, amb: 0.3 };
const lap = (o = {}) => { const p = lapPose(CFG, { ...o, mother: { L: holdL, ...(o.mother || {}) } }); return { figs: p.figs, book: p.book }; };
const lapShot = (name, id, o, more = {}) => ({ id: 'v4_' + id, ...base, ...CAM[name], ...lap(o), ...more });
const plan = (id, header, more = {}) => ({ id, ...base, flashlight: null, ortho: { w: 6.8 }, lens: 'ortho', pos: [-0.6, 7, 0], up: [0, 0, -1], target: [-0.6, 0, 0], near: 1, far: 12, hide: ['ceiling'], header,
  figs: { daughter: DAUGHTER_LIE }, pull: { who: 'daughter', upTo: 0.8 }, bedQuilt: false, book: { state: 'closed', at: [-0.9, 0.021, -0.2], normal: [0, 1, 0], top: [1, 0, -0.2] }, ...more });

export const SHOTS = [
  // ---------------------------------------------------------------- set bible views (orthographic)
  plan('v4_PLAN', 'bed26 v4 plan (ceiling removed)'),
  plan('v4_ELEV_back', 'elevation: the back wall (bed head, window, nightstand), looking north (-z)', { pos: [-0.6, 1.3, 1.75], up: [0, 1, 0], target: [-0.6, 1.3, -3], ortho: { w: 4.8 }, hide: ['front wall'] }),
  plan('v4_ELEV_right', 'elevation: the right wall with the door, looking east (+x)', { pos: [-2.75, 1.3, 0], up: [0, 1, 0], target: [3, 1.3, 0], ortho: { w: 4.0 }, hide: ['left wall'] }),
  plan('v4_ELEV_left', 'elevation: the storytime side, looking west (-x) from the door wall', { pos: [1.55, 1.3, 0], up: [0, 1, 0], target: [-3, 1.3, 0], ortho: { w: 4.0 }, hide: ['right wall (door)', 'door (open)', 'door frame', 'hallway (lit)'] }),

  // ---------------------------------------------------------------- I, J, K: storytime
  lapShot('LAP_front', 'I1', { mother: { head: { look: `${C}:eyes`, tilt: -6 }, R: { to: `${C}:shoulderR`, off: [0, -0.02, 0.06], hand: 'relax', palm: 'in' } }, child: { head: { look: `${M}:eyes` } } }, { sync: 'lip', singers: [M], focus: [M, C], serves: ['I1'],
    intent: "LAP_front in the L2 room: the daughter in Jade's lap on the rug, their backs against the side of the bed; pillow, bunny and headboard behind them at frame left, the nightstand beyond the pillow at the far left; flashlight in Jade's left hand at frame right; warm door light far right. A squeeze on 'twin'." }),
  lapShot('LAP_child_cu', 'I3a', { mother: { head: { look: `${C}:headTop`, tilt: -6 } }, child: { head: { look: `${M}:eyes` } } }, { sync: 'lip', singers: [C], serves: ['I3a'],
    intent: "Close on the daughter's face; she looks at the page, then tips her head back to look up at her mother, really asking. Jade's chin and shoulder soft above. The bed side and the bunny out of focus behind." }),
  lapShot('LAP_mother_cu', 'I4', { mother: { head: { look: `${C}:eyes`, nod: 8, tilt: -4 } }, child: { head: { look: `${M}:eyes` } } }, { sync: 'lip', singers: [M], serves: ['I4 (no morph)'],
    intent: "Close on Jade from the first frame, looking down at her daughter: the secret confidence. The top of the daughter's head at the bottom of frame. Dark free area at frame left for the light-on-dark calligraphy." }),
  lapShot('LAP_hands', 'J1', { child: { L: { to: 'lift:page:L:0.6:0.25:0.01', hand: 'point', palm: PAGE_DOWN, fingers: PAGE_TOP } } }, { serves: ['J1'],
    intent: "Top-down onto the spread in the flashlight pool: the daughter's fingertip on one carved character in the middle of the left page." }),
  lapShot('LAP_front', 'J4R', { mother: { head: { look: 'book:GT', tilt: -6 } }, child: { head: { look: AHEAD } } }, { sync: 'lip', singers: [M, C], serves: ['J4 (right half)'],
    intent: 'Identical to attic88 v4_J4L in lens, distance and framing: the 2026 pair in the lap, flashlight white from frame right.' }),
  lapShot('LAP_front', 'K1', { mother: { spine: { bend: 14 }, head: { look: `${C}:earL`, tilt: -8 } }, child: { head: { look: AHEAD, nod: 6 } } }, { sync: 'lip', singers: [M], serves: ['K1 (room part)'],
    intent: "Jade lowers her voice and leans to the daughter's ear; the daughter is nodding before the question ends. Then cut to v4_K1_ots for the page." }),
  lapShot('LAP_ots', 'K1_ots', {}, { serves: ['K1 (page part, start of the push)', 'K2b entry'], intent: "Over Jade's left shoulder onto the spread in the flashlight pool." }),
  lapShot('LAP_34', 'K2a', { mother: { head: { look: 'book:G', tilt: -6 } }, child: { head: { look: 'book:Rmid' } } }, { lens: 35, orbit: { at: { mid: [`${M}:eyes`, `${C}:eyes`] }, relBody: M, az: 34, el: 30, dist: 1.45 }, aim: [{ mid: [`${C}:eyes`, 'book:G'] }, 0.5, 0.5], sync: 'lip', singers: [C], serves: ['K2a'],
    intent: "From the flashlight side and above: the daughter looks down at the page and says the line with relish; the lit spread large in the lower half." }),
  // ---------------------------------------------------------------- L
  { id: 'v4_L1', ...base, lens: 35, serves: ['L1'], header: 'L1 the daughter asleep in Jade\'s lap against the bed; flashlight on the rug, book closed', sync: 'none',
    intent: "Same place as the storytime, wider: Jade sits on the rug against the side of the bed, the daughter asleep across her lap, mouth open, one arm flung over Jade's arm; Jade looks down and breathes out. Behind them the bed: pillow and bunny at frame left, the nightstand at the far left; the door light at far right. The flashlight lies on the rug, still on; the book closed beside it.",
    orbit: { at: `${M}:chest`, relBody: M, az: 8, el: 9, dist: 2.3 }, aim: [`${M}:chest`, 0.5, 0.48],
    flashlight: { at: [-0.95, 0.04, -0.05], aimAt: [-1.5, 0.02, -0.25] },
    figs: { jade: { at: [LAP4.base[0], LAP4.floor + 0.12, LAP4.base[1]], legs: 'cross', yaw: LAP4.yaw, spine: { bend: 10 }, head: { look: `${C}:head`, nod: 10, tilt: -8 },
        L: { to: `${C}:shoulderL`, off: [0, 0.0, 0.05], hand: 'relax', palm: 'in', elbow: 'down' }, R: { to: `${C}:hip`, off: [0, 0.06, 0], hand: 'relax', palm: 'down' } },
      daughter: { at: F.at3(-0.02, LAP4.floor + 0.2, 0.2), legs: 'long', yaw: LAP4.yaw + 75, pitch: -55, spine: { bend: 8 }, head: { turn: 25, tilt: 20 },
        L: { to: `${M}:elbowL`, off: [0, 0.03, 0], hand: 'relax', palm: 'down' }, R: 'side' } },
    book: { state: 'closed', at: [-1.05, 0.021, -0.45], normal: [0, 1, 0], top: [1, 0, 0.3] } },
  { id: 'v4_L2', ...base, flashlight: null, bedQuilt: false, pull: { who: 'daughter', upTo: 0.7 }, lens: 40, pos: [0.68, 2.1, 0.76], target: [0.0, 0.7, -1.12], amb: 0.95, doorI: 14,
    header: 'L2 (the reference) Jade pulls the quilt up over the sleeping daughter (matches attic v4_L2b)', serves: ['L2'],
    intent: "The director's reference blocking. From the foot of the bed, a little left of its axis and 32 degrees above: the headboard upper right, the slatted blind upper left, the nightstand with its cup between them at the head on the window side, the bunny on the far side of the pillow; the daughter asleep; Jade kneels on the rug at frame left and draws the quilt up to her chin; warm door light from frame right.",
    figs: { daughter: DAUGHTER_LIE, jade: { at: [-0.52, -0.98], floor: 0.02, legs: 'kneel', yaw: 92, spine: { bend: 40 }, head: { look: 'daughter:head' },
      L: { to: [0.18, BED4_TOP + 0.2, -1.2], hand: 'grip', palm: 'down', fingers: [1, 0, 0], elbow: 'down' }, R: { to: [-0.02, BED4_TOP + 0.2, -1.02], hand: 'grip', palm: 'down', fingers: [1, 0, 0], elbow: 'down' } } },
    book: { state: 'closed', at: [-0.8, 0.021, -0.2], normal: [0, 1, 0], top: [0.3, 0, -1] } },
];
const dbgTop = (s, c, w = 3) => ({ ...s, id: s.id.replace('v4_', 'v4dbg_') + '_top', ortho: { w }, lens: 'ortho', pos: [c[0], 6, c[1]], up: [0, 0, -1], target: [c[0], 0, c[1]], orbit: undefined, aim: undefined, near: 1, far: 10, hide: ['ceiling'] });
SHOTS.push(dbgTop(SHOTS.find((s) => s.id === 'v4_L2'), [0, -0.7]));
// master-plate views: the empty room
SHOTS.push(
  { ...SHOTS.find((s) => s.id === 'v4_L2'), id: 'v4_MASTER', figs: {}, pull: undefined, bedQuilt: true, book: null, header: 'MASTER: the empty bedroom from the L2 camera', intent: 'Empty room for the master plate.' },
  { id: 'v4_MASTER_lap', ...base, flashlight: null, lens: 28, pos: [-2.45, 0.95, -0.25], target: [-0.3, 0.55, -0.45], figs: {}, book: null, amb: 0.95, doorI: 14, header: 'MASTER: the empty storytime side (from where LAP_front stands)', intent: 'Empty room toward the bed side where storytime happens: bed side, pillow, bunny, nightstand at left, door light at right.' },
);

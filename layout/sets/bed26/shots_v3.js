// BEDROOM 2026, v3 camera table. The same LAP storytime pose and eight setups as attic88 (engine/lap.js): Jade sits on
// the rug with her back against the side of the bed, the daughter in her lap, the book in front of both; the flashlight
// is in Jade's left hand, held out to the left of the book (the same side and about the same angle as the neon in the
// attic), so the two rooms cut and split-screen against each other. Plus the hand shadows from the real flashlight,
// and L2: the blanket.
import { BED_TOP } from './layout.js';
import { lapPose, lapCameras, lapFrame } from '../../engine/lap.js';

const M = 'jade', C = 'daughter';
export const LAP = { base: [0.82, -0.1], yaw: -90, floor: 0.012 };
const CFG = { mother: M, child: C, base: LAP.base, yaw: LAP.yaw, floor: LAP.floor, Hm: 1.65, Hc: 1.02 };
const F = lapFrame(LAP.base, LAP.yaw), CAM = lapCameras(M, C);
const T36 = 36 * Math.PI / 180, PAGE_DOWN = [F.f[0] * Math.sin(T36), -Math.cos(T36), F.f[1] * Math.sin(T36)], PAGE_TOP = [F.f[0] * Math.cos(T36), Math.sin(T36), F.f[1] * Math.cos(T36)];
const AHEAD = F.at3(0.1, 0.62, 2.2);
// the flashlight: lens 0.36 m from the gutter, to the left of the book and ~35 deg above the page (offsets: world x, y, z;
// Jade faces -x, her left is +z)
const FLASH = { aimAt: 'book:G', from: [0.06, 0.2, 0.3] };
const holdL = { to: 'flash:grip', hand: 'grip', thumb: 'to:flash:front', off: [0, -0.02, 0] };
const base = { v3: true, flashlight: FLASH };
const lap = (o = {}) => { const p = lapPose(CFG, { ...o, mother: { L: holdL, ...(o.mother || {}) } }); return { figs: p.figs, book: p.book }; };
const lapShot = (name, id, o, more = {}) => ({ id: 'v3_' + id, ...base, ...CAM[name], ...lap(o), ...more });
const NS = ['nightstand', 'night-light (off)'];
const asleep = { at: [1.32, BED_TOP + 0.085, -0.78], legs: 'straight', pitch: -90, yaw: 0, spine: { bend: 6 }, head: { turn: -28 }, L: 'side', R: 'side' };

export const SHOTS = [
  lapShot('LAP_front', 'LAP_front', { mother: { head: { look: 'book:GT', tilt: -6 } }, child: { head: { look: AHEAD } } }, { sync: 'lip', singers: [M, C], serves: ['I1', 'I3 (first 1.6 s)', 'K1', 'J4 (right half)'],
    intent: "The main singing setup, same framing as attic v3_LAP_front: the daughter in Jade's lap against the bed, both facing us, the book in front of them, flashlight from frame right." }),
  lapShot('LAP_34', 'LAP_34', { mother: { head: { look: 'book:GT', tilt: -6 } }, child: { head: { look: 'book:G' } } }, { sync: 'lip', singers: [M, C], serves: ['I1', 'K1'],
    intent: 'Three-quarter two-shot from the flashlight side; the lit page between us and their faces.' }),
  lapShot('LAP_ots', 'LAP_ots', {}, { serves: ['I1 (out of the white page)', 'K2 (start of the push)'],
    intent: "Over Jade's left shoulder, past the daughter's head, down onto the spread in the flashlight pool. Start frame of the push (page quads in the sidecar)." }),
  lapShot('LAP_ots_push_end', 'LAP_ots_push_end', {}, { push: { fromShot: CAM.LAP_ots, fill: 0.40 }, serves: ['K2 (end of the push)', 'I1 (reverse: start on the white page)'],
    intent: 'Same line, pushed in until the spread fills the frame.' }),
  lapShot('LAP_child_cu', 'LAP_child_cu', { mother: { head: { look: `${C}:headTop`, tilt: -6 } }, child: { head: { look: AHEAD } } }, { sync: 'lip', singers: [C], serves: ['I3', 'K2 (first 1.5 s)'],
    intent: "Close on the daughter's face, centred, Jade's chin and shoulder soft above: the eyebrow shot (I3)." }),
  lapShot('LAP_mother_cu', 'LAP_mother_cu', { mother: { head: { look: AHEAD, tilt: -4 } }, child: { head: { look: 'book:G' } } }, { sync: 'lip', singers: [M], serves: ['I4a', 'K1'],
    intent: "Close on Jade, the top of the daughter's head at the bottom of frame; lit from below by the page." }),
  lapShot('LAP_profile', 'LAP_profile', { mother: { spine: { bend: 30 }, head: { look: 'book:Rmid', pitchK: 0.8, tilt: 0 } }, child: { head: { look: 'book:Rmid' } } }, { hide: NS, serves: ['K1', 'parallel to attic C5'],
    intent: 'Profile two-shot matching attic v3_LAP_profile: Jade leans over the daughter\'s shoulder to the page. (The camera stands where the nightstand is; it is hidden in the guide.)' }),
  lapShot('LAP_hands', 'LAP_hands', {}, { serves: ['I2', 'I4b', 'J1'],
    intent: "Top-down onto the spread in the flashlight pool: Jade's right hand and the daughter's hands at the bottom of the pages; the flashlight in Jade's left hand just outside frame left." }),
  // ---------------------------------------------------------------- hand shadows from the real flashlight
  lapShot('LAP_hands', 'I2', { mother: { R: { to: 'card:1:base', off: [0.0, -0.03, 0], hand: 'fist', palm: 'down' } }, child: { L: { to: 'card:0:base', off: [-0.02, -0.02, 0], hand: 'fist', palm: 'down' }, R: { to: 'card:0:base', off: [0.02, -0.02, 0], hand: 'fist', palm: 'down' } } },
    { cards: [{ on: 'Lmid', h: 0.1, lift: 0.03, who: 'daughter' }, { on: 'Rmid', h: 0.13, lift: 0.04, who: 'jade' }], header: 'two hand-shadow monkeys in the flashlight', serves: ['I2'],
      intent: "Jade's hand (card) over the right page and the daughter's two hands (smaller card) over the left, both held flat a few cm up; the flashlight at frame left throws two matching monkeys, the nearer one larger." }),
  lapShot('LAP_hands', 'I4b', { child: { R: { to: 'lift:page:L:0.45:0.55:0.025', hand: 'point', palm: PAGE_DOWN, fingers: PAGE_TOP } } },
    { shadow: { casters: ['daughter.handR'] }, header: "the daughter's hand-shadow climbs onto the empty chair", serves: ['I4 (second half)'],
      intent: "The daughter's small hand in the beam 2-3 cm over the left page; its shadow walks up to the bare chair." }),
  lapShot('LAP_hands', 'J1', { child: { R: { to: 'book:Lmid', off: [0, 0.012, 0], hand: 'point', palm: PAGE_DOWN, fingers: PAGE_TOP } } },
    { header: "the daughter's fingertip on a carved character", serves: ['J1'],
      intent: "The daughter's fingertip touches one carved character in the middle of the left page; hand and shadow meet at the fingertip." }),
  // ---------------------------------------------------------------- L2: the blanket (matches attic v3_L2b)
  { id: 'v3_L2', v3: true, bedBlanket: false, pull: { who: 'daughter', upTo: 0.7 }, lens: 40, orbit: { at: 'daughter:chest', az: 8, el: 32, dist: 2.4 }, aim: ['daughter:chest', 0.6, 0.64], amb: 0.9,
    header: 'Jade pulls the blanket up over the sleeping daughter (matches attic v3_L2b)', serves: ['L2'],
    intent: 'Replaces the flashlight insert. The daughter asleep in her bed, head away from us; Jade kneels at frame left and draws the blanket up to her chin. Same lens, height, distance and screen direction as attic v3_L2b, so one cuts to the other.',
    figs: { daughter: asleep, jade: { at: [0.72, -0.74], floor: 0.012, legs: 'kneel', yaw: 92, spine: { bend: 36 }, head: { look: 'daughter:head' },
      L: { to: [1.25, BED_TOP + 0.22, -0.9], hand: 'grip', palm: 'down', fingers: [1, 0, 0], elbow: 'down' }, R: { to: [1.05, BED_TOP + 0.22, -0.84], hand: 'grip', palm: 'down', fingers: [1, 0, 0], elbow: 'down' } } },
    book: { state: 'closed', at: [0.5, 0.013, -0.2], normal: [0, 1, 0], top: [0.3, 0, -1] } },
];

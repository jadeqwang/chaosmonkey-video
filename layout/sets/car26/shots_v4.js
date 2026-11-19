// CAR 2026, v4 camera table (SETS team, preview_v4). The cabin is unchanged from v3 (build.js cabin(): two forward-facing
// child seats, the daughter rear right behind the empty front passenger seat, the rear-left seat empty); v4 puts the
// jointed bodies in it and fixes F1's arms (rap body language per REVISION_V4 §5 F1). Cameras = v3 cameras.
import { SHOTS as V3 } from './shots_v3.js';
import { CAR } from './layout.js';

const clone = (o) => JSON.parse(JSON.stringify(o));
const from = (id, more = {}) => { const s = clone(V3.find((x) => x.id === 'v3_' + id)); const o = { ...s, id: 'v4_' + id, v4: true, ...more };
  if (o.figs?.jade) for (const n of ['L', 'R']) if (o.figs.jade[n]?.hand === 'grip') o.figs.jade[n] = { ...o.figs.jade[n], fingers: [0, 0.45, -1], palm: [n === 'L' ? 1 : -1, 0, -0.3] };   // hands wrap the rim, wrists straight
  if (id === 'F3a') o.figs.daughter.L.elbow = 'out';
  return o; };
const K = CAR.carSeat;
const daughterSeat = (o = {}) => ({ at: [K.x, K.cushionY + 0.065, K.z + 0.02], legs: 'seat', legOpts: { ankleL: [0.07, -0.26, 0.24], ankleR: [0.07, -0.26, 0.24] }, yaw: 180, spine: { bend: -4 }, head: { look: [0.3, 1.05, -2] }, L: 'lap', R: 'lap', ...o });
// F1: her right hand counts the flow in front of her chest (index + middle out, chopping down); the left hand points at
// the listener (the front seat / lens); never both palms up beside the face.
const rap = { R: { to: 'self:chest', off: [0.04, 0.02, -0.2], hand: 'two', fingers: [0.15, 0.55, -0.82], palm: [-0.6, -0.3, -0.2] },
  L: { to: 'self:shoulderL', off: [0.02, -0.12, -0.3], hand: 'point', fingers: [-0.25, 0.15, -1], palm: [0.3, -1, 0] } };
const plan = (id, header, more = {}) => ({ ...from('F1'), id, ortho: { w: 4.2 }, lens: 'ortho', pos: [0, 6, 0.4], up: [0, 0, -1], target: [0, 0, 0.4], aim: undefined, near: 1, far: 12, hide: ['headliner (roof)'], header, sync: 'none', ...more });

export const SHOTS = [
  plan('v4_PLAN', 'car26 v4 plan (roof removed): the daughter rear right, the empty child seat rear left, Jade driving'),
  plan('v4_ELEV_side', 'car26 v4 section from the right side (looking -x, right doors removed)', { pos: [3, 1.0, 0.4], up: [0, 1, 0], target: [-3, 1.0, 0.4], ortho: { w: 3.6 }, hide: ['door panels', 'glass: rear_right', 'glass: front_right', 'glass: quarter_right'] }),
  from('F1', { figs: { daughter: daughterSeat({ head: { look: [0.0, 1.38, -0.2], nod: 6 }, spine: { bend: 2, side: 4 }, ...rap }), jade: clone(V3.find((x) => x.id === 'v3_F1').figs.jade) },
    intent: "From between the two front seats looking back, under the headliner: the front headrests frame both edges; the daughter in her car seat left of centre raps for the front seat, her right hand counting the flow in front of her chest (index and middle finger out, chopping down on the stresses), her left hand pointing at us on the line ends, chin leading; the second child seat, EMPTY, right of centre." }),
  from('F2'), from('F3a'), from('F4a'), from('F6b'),
];
SHOTS.push({ ...from('F1'), id: 'v4_MASTER', lens: 28, pos: [0.0, 1.43, -0.3], figs: {}, aim: undefined, target: [0.0, 1.0, 1.3], header: 'MASTER: the empty cabin from between the front seats, toward the two child seats', sync: 'none' },
  { ...from('F4b'), id: 'v4_MASTER_back', figs: {}, header: 'MASTER: the empty cabin from the tailgate', sync: 'none' });

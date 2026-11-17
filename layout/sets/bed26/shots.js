// BEDROOM 2026 camera table: one entry per bed26 shot in docs/shots.yaml (I4 split into a/b: the centred face, then the
// daughter's hand-shadow climbing onto the chair on the page). Fields as in attic88/shots.js, plus
// flashlight { aimAt: point, from: [dx,dy,dz] | at: [x,y,z], on } (the lens sits at aim point + from).
import { BED_TOP } from './layout.js';

const JADE_AT = [0.8, -0.55];
const jadeFloor = (o = {}) => ({ at: JADE_AT, legs: 'knees', yaw: -90, spine: { bend: 2 }, head: { look: 'book:G' }, ...o });
// the open book on Jade's knees, tipped up toward her
const bookKnees = (o = {}) => ({ state: 'open', on: 'jade', anchor: 'knees', off: [0, 0.035, -0.06], tilt: 40, v: 9, ...o });
// the daughter on her tummy on the bed, propped on her elbows, head over the edge by Jade's left shoulder
const daughterProne = (o = {}) => ({ at: [1.25, BED_TOP + 0.085, -0.15], pitch: 90, yaw: -62, legs: 'kick', spine: { bend: -34 }, headAt: [0.92, 0, -0.26],
  head: { look: 'book:G' }, L: { to: 'self:chin', off: [0.0, -0.06, 0.04], hand: 'relax', palm: 'up' }, R: { to: 'self:chin', off: [0.0, -0.06, -0.04], hand: 'relax', palm: 'up' }, ...o });
const FLASH_L = { aimAt: 'book:G', from: [0.16, 0.26, 0.2] };   // held in Jade's left hand, over her left shoulder side
const FLASH_R = { aimAt: 'book:G', from: [0.16, 0.26, -0.2] }; // held in her right hand
const holdL = { to: 'flash:grip', hand: 'grip', thumb: 'to:flash:front', off: [0, -0.02, 0] };
const holdR = { to: 'flash:grip', hand: 'grip', thumb: 'to:flash:front', off: [0, -0.02, 0] };
const bookHands = { L: { to: 'book:LO', hand: 'grip', palm: 'in', off: [0, -0.01, 0] }, R: { to: 'book:RO', hand: 'grip', palm: 'in', off: [0, -0.01, 0] } };

export const SHOTS = [
  { id: 'I1', lens: 35, orbit: { at: { mid: ['jade:eyes', 'daughter:eyes'] }, az: -62, el: 4, dist: 1.55 }, aim: [{ mid: ['jade:eyes', 'daughter:eyes'] }, 0.48, 0.4], header: 'Jade on the floor by the bed, book + flashlight; the daughter leans in', sync: 'lip', singers: ['jade'],
    intent: 'Out of the white of the page into the dark room: Jade (frame centre-left) on the floor against the bed, book on her knees in the flashlight; the daughter leans over the bed edge above her shoulder.',
    figs: { jade: jadeFloor({ head: { look: [-0.4, 0.8, -0.1] }, L: bookHands.L, R: holdR }), daughter: daughterProne() }, book: bookKnees(), flashlight: FLASH_R },
  { id: 'I2', lens: 40, orbit: { at: 'book:G', rel: 'jade', az: 180, el: 64, dist: 0.75 }, aim: ['book:G', 0.5, 0.52], hideParts: { jade: ['head'] }, header: 'two hand-shadow monkeys from the flashlight on the page',
    intent: "Jade's eyeline into the spread (her head hidden): her right hand throws a monkey on the right page, the daughter's hand a second identical one on the left page; both big, from the near flashlight.",
    figs: { jade: jadeFloor({ L: holdL, R: { to: 'ray:book:Rmid:0.1', hand: 'monkeyHead', fingers: 'up', thumb: 'to:flash:lens' } }),
      daughter: daughterProne({ R: { to: 'ray:book:Lmid:0.1', hand: 'monkeyHead', fingers: 'up', thumb: 'to:flash:lens' } }) },
    book: bookKnees(), flashlight: FLASH_L, shadow: { casters: ['jade.handR', 'daughter.handR'] } },
  { id: 'I4a', lens: 85, orbit: { at: 'jade:eyes', rel: 'jade', az: 0, el: 1, dist: 0.85 }, aim: ['jade:eyes', 0.5, 0.45], header: "'You're able': Jade's face dead centre", sync: 'lip', singers: ['jade'],
    intent: "Second centred face: Jade looks up from the book into the lens, certain, lit from below by the page's flashlight bounce. Nothing moves (Mama's 1988 face ghosts over it for 8 frames).",
    figs: { jade: jadeFloor({ head: { look: [-0.2, 0.86, -0.55] }, R: bookHands.R, L: holdL }), daughter: daughterProne() }, book: bookKnees(), flashlight: FLASH_L },
  { id: 'I4b', lens: 40, orbit: { at: 'book:G', rel: 'jade', az: 180, el: 64, dist: 0.75 }, aim: ['book:G', 0.5, 0.52], hideParts: { jade: ['head'] }, header: "insert: the daughter's hand-shadow climbs onto the empty chair (page)",
    intent: "Same eyeline as I2: the daughter's small hand in the beam, its shadow walking up the painted banquet to the bare chair on the left page.",
    figs: { jade: jadeFloor({ L: holdL, R: bookHands.R }), daughter: daughterProne({ R: { to: 'ray:book:Lmid:0.09', off: [0, 0.02, 0], hand: 'point', fingers: 'down', thumb: 'to:flash:lens' } }) },
    book: bookKnees(), flashlight: FLASH_L, shadow: { casters: ['daughter.handR'] } },
  { id: 'J1', lens: 50, orbit: { at: 'book:Lmid', rel: 'jade', az: 150, el: 62, dist: 0.6 }, aim: ['book:Lmid', 0.5, 0.55], header: "insert: the daughter's fingertip on a carved character",
    intent: "Close on the left page from Jade's left: the daughter's fingertip lands on one carved character; the flashlight pool around it. The flashes happen on the page.",
    figs: { jade: jadeFloor({ L: holdL, R: bookHands.R }), daughter: daughterProne({ R: { to: 'book:Lmid', off: [0.045, 0.05, 0.0], hand: 'point', fingers: 'to:book:Lmid' } }) },
    book: bookKnees(), flashlight: FLASH_L },
  { id: 'K1', lens: 35, orbit: { at: { mid: ['jade:eyes', 'daughter:eyes'] }, az: -68, el: 6, dist: 1.5 }, aim: [{ mid: ['jade:eyes', 'daughter:eyes'] }, 0.5, 0.42], header: 'Jade turns toward the last chapter; the daughter already nodding', sync: 'lip', singers: ['jade'],
    intent: 'Two-shot, softer: Jade (frame left) lifts the page corner toward the last chapter, flashlight in her other hand; the daughter sits beside her on the floor, nodding.',
    figs: { jade: jadeFloor({ head: { look: 'daughter:eyes', nod: 10 }, R: holdR, L: { to: 'book:LOT', hand: 'pinch', palm: 'in', off: [0, 0.01, 0] } }),
      daughter: { at: [0.62, -0.05], legs: 'cross', yaw: -110, spine: { bend: 10 }, head: { look: 'book:G', nod: 12 }, L: 'kneeL', R: 'kneeR' } },
    book: bookKnees(), flashlight: FLASH_R },
  { id: 'L1', lens: 24, pos: [-1.35, 1.55, 1.35], aim: [{ mid: ['jade:eyes', 'book:G'] }, 0.6, 0.55], header: 'pull-back end: the daughter asleep against Jade\'s arm; book open on the blanket; flashlight on',
    intent: 'End of the pull-back, wide and high from the door corner: the bed frame-right, Jade on the floor against it, the daughter asleep against her arm, the book open on the blanket in the flashlight pool.',
    figs: { jade: jadeFloor({ head: { look: 'daughter:head', nod: 8 }, L: { to: [0.98, BED_TOP + 0.06, -0.25], hand: 'relax', palm: 'down' }, R: 'kneeR' }),
      daughter: { at: [1.32, BED_TOP + 0.085, -0.35], pitch: 90, yaw: -80, legs: 'straight', spine: { bend: -6 }, headAt: [1.02, 0, -0.32], head: { turn: 70, tilt: 30 }, L: 'side', R: { to: 'jade:elbowL', off: [0.05, 0.03, 0], hand: 'relax', palm: 'down' } } },
    book: { state: 'open', at: [1.28, BED_TOP + 0.035, 0.0], normal: [0, 1, 0], top: [1, 0, 0], v: 5 }, flashlight: { aimAt: 'book:G', at: [1.42, BED_TOP + 0.05, -0.32] } },
  { id: 'L2', lens: 50, orbit: { at: 'jade:handR', az: -110, el: 18, dist: 0.42 }, aim: [{ mid: ['jade:handR', 'book:G'] }, 0.45, 0.5], header: "Jade's thumb on the flashlight switch; the pool of white on the blank column",
    intent: 'Close behind her hand: the flashlight foreground, thumb on the switch; beyond, the white pool on the open page (the blank column). Click: black.',
    figs: { jade: jadeFloor({ head: { look: 'book:G' }, R: { to: 'flash:grip', hand: 'switch', thumb: 'to:flash:front', off: [0, -0.02, 0] }, L: 'kneeL' }),
      daughter: { at: [1.32, BED_TOP + 0.085, -0.35], pitch: 90, yaw: -80, legs: 'straight', spine: { bend: -6 }, headAt: [1.02, 0, -0.32], head: { turn: 70, tilt: 30 }, L: 'side', R: 'side' } },
    book: { state: 'open', at: [1.28, BED_TOP + 0.035, 0.0], normal: [0, 1, 0], top: [1, 0, 0], v: 5 }, flashlight: { aimAt: 'book:G', from: [-0.32, 0.22, -0.18] } },
];

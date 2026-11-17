// CAR 2026 camera table: one entry per car26 shot in docs/shots.yaml (F3, F4, F6 split a/b). Extra fields:
//   street { t }  streetlight phase in seconds (lampsAt in layout.js): choose t for the light direction you want
//   mirror        pane that renders as a true reflection ('mirror' = rear-view mirror)
//   mirrorSearch  { faces, box } grid-search the camera position so those faces land inside the mirror
import { CAR } from './layout.js';

const K = CAR.carSeat;
const daughterSeat = (o = {}) => ({ at: [K.x, K.cushionY + 0.065, K.z + 0.02], legs: 'seat', legOpts: { ankleL: [0.07, -0.26, 0.24], ankleR: [0.07, -0.26, 0.24] }, yaw: 180, spine: { bend: -4 },
  head: { look: [0.3, 1.05, -2] }, L: 'lap', R: 'lap', ...o });
const jadeDrive = (o = {}) => ({ at: [-CAR.frontSeatX, CAR.frontHp.y + 0.05, CAR.frontHp.z + 0.02], legs: 'seat', legOpts: { ankleL: [0.1, -0.5, 0.66], ankleR: [0.1, -0.5, 0.62] }, yaw: 180, spine: { bend: -14 },
  head: { look: [-0.35, 1.1, -10] }, L: { to: [-0.55, 1.03, -0.41], hand: 'grip', fingers: 'up', palm: 'fwd' }, R: { to: [-0.21, 1.03, -0.41], hand: 'grip', fingers: 'up', palm: 'fwd' }, ...o });
// hands chopping the beat: both forearms up, hands flat, edges down
const chop = { L: { to: 'self:chest', off: [-0.1, 0.02, -0.2], hand: 'flat', fingers: [0.2, 0.3, -0.9], palm: [1, 0, 0] }, R: { to: 'self:chest', off: [0.1, 0.06, -0.2], hand: 'flat', fingers: [-0.2, 0.3, -0.9], palm: [-1, 0, 0] } };

export const SHOTS = [
  { id: 'F1', lens: 28, pos: [0.06, 1.13, 0.44], aim: ['daughter:eyes', 0.56, 0.4], header: 'the daughter raps from her car seat; streetlight sweeps', sync: 'lip', singers: ['daughter'], street: { t: 0.15 },
    intent: 'Between the front seats, looking back: the daughter in her forward-facing seat, deadpan, hands chopping; her side window behind her full of dusk; an amber streetlight sweeps across.',
    figs: { daughter: daughterSeat({ head: { look: [0.02, 1.08, 0.1] }, ...chop }), jade: jadeDrive() } },
  { id: 'F2', lens: 24, pos: [0.06, 1.16, 0.44], aim: [[0.71, 1.19, 0.91], 0.4, 0.45], header: 'her side window is a shadow screen (puppet monkey)', street: { t: 0.55 },
    intent: 'From the empty left rear seat across to the right rear window: the pane fills the frame as a lit screen; the daughter in profile at the right edge, looking at it.',
    figs: { daughter: daughterSeat({ head: { look: [0.9, 1.15, 0.9] } }), jade: jadeDrive() } },
  { id: 'F3a', lens: 38, pos: [0.06, 1.12, 0.44], aim: ['daughter:eyes', 0.6, 0.38], header: 'she plucks a hair and blows across her open palm (match cut out)', sync: 'lip', singers: ['daughter'], street: { t: 0.9 },
    intent: "Same screen place as F3b (little Jade's face 0.6/0.38): one hand at her hair, the other palm-up under her lips; she blows across it toward frame left.",
    figs: { daughter: daughterSeat({ head: { look: [0.02, 1.08, 0.1], nod: 6 }, L: { to: 'self:earL', off: [0.0, 0.05, 0.0], hand: 'pinch', fingers: 'up', palm: 'in' }, R: { to: 'self:mouth', off: [0.0, -0.07, -0.1], hand: 'palmUp', palm: 'up', fingers: [-0.6, 0.1, -0.8] } }), jade: jadeDrive() } },
  { id: 'F4a', lens: 26, mirror: 'mirror', mirrorSearch: { faces: ['jade', 'daughter'], box: [[-0.12, 0.3], [1.05, 1.3], [-0.2, 0.25]] }, aim: [[0, 1.33, -0.43], 0.52, 0.45],
    header: 'the rear-view mirror holds both faces singing', sync: 'lip', singers: ['jade', 'daughter'], street: { t: 1.2 },
    intent: "The mirror large, frame centre-right: in it, Jade's eyes and the daughter behind her, both singing. Camera position found by searching where both reflections fit the glass.",
    figs: { daughter: daughterSeat({ head: { look: [0, 1.33, -0.43] } }), jade: jadeDrive({ head: { look: [0, 1.33, -0.43] } }) } },
  { id: 'F4b', lens: 18, pos: [0.0, 1.38, 1.6], target: [0.0, 1.08, -0.8], header: 'every pane carries a puppet copy; the running-lantern ring', street: { t: 1.55 },
    intent: 'Wide from the back of the cabin: windscreen, all four side windows and the mirror in one frame, each pane its own lit screen; Jade and the daughter seen from behind.',
    figs: { daughter: daughterSeat(), jade: jadeDrive() } },
  { id: 'F5', lens: 18, pos: [0.0, 1.38, 0.42], target: [0.1, 1.05, 1.6], header: 'the lights pass; each copy goes dark; the glass empties to dusk', street: { t: 2.2 },
    intent: 'Reverse wide from the front, between the seats: rear window and both rear side windows, the daughter centre-right; panes go dark one per beat.',
    figs: { daughter: daughterSeat({ head: { look: [0.6, 1.1, 1.0] } }), jade: jadeDrive() } },
  { id: 'F6a', lens: 24, pos: [0.0, 1.13, 0.92], target: [0.0, 1.2, -0.6], header: 'two puppet monkeys face each other across the windscreen', street: { t: 2.6 },
    intent: 'From the rear centre seat: the windscreen is the stage, two mirror-posed puppets either side of the centre line; Jade (driving) lower left, passenger headrest lower right.',
    figs: { daughter: daughterSeat(), jade: jadeDrive() } },
  { id: 'F6b', lens: 24, mirror: 'rear_right', pos: [0.02, 1.14, 0.44], aim: ['daughter:eyes', 0.68, 0.45], header: 'the daughter and her reflection in the window wave at once', street: { t: 3.0 },
    intent: 'From the front, between the seats: the daughter waves; in her dark side window her reflection waves back at the same instant (true reflection rendered in the pane).',
    figs: { daughter: daughterSeat({ head: { look: [0.02, 1.08, 0.1] }, R: { to: 'self:shoulderR', off: [0.06, 0.2, -0.06], hand: 'flat', fingers: 'up', palm: 'fwd' } }), jade: jadeDrive() } },
];

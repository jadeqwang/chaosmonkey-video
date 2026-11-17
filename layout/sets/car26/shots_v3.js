// CAR 2026, v3 camera table. The rear bench now carries TWO forward-facing child seats, outboard left and right. The
// daughter rides in the right one (behind the empty front passenger seat); the left one, behind Jade, is empty.
// Every setup keeps something of the FRONT seats or the second child seat in frame so she reads as being in the back.
import { CAR } from './layout.js';

const K = CAR.carSeat;
const daughterSeat = (o = {}) => ({ at: [K.x, K.cushionY + 0.065, K.z + 0.02], legs: 'seat', legOpts: { ankleL: [0.07, -0.26, 0.24], ankleR: [0.07, -0.26, 0.24] }, yaw: 180, spine: { bend: -4 },
  head: { look: [0.3, 1.05, -2] }, L: 'lap', R: 'lap', ...o });
const jadeDrive = (o = {}) => ({ at: [-CAR.frontSeatX, CAR.frontHp.y + 0.05, CAR.frontHp.z + 0.02], legs: 'seat', legOpts: { ankleL: [0.1, -0.5, 0.66], ankleR: [0.1, -0.5, 0.62] }, yaw: 180, spine: { bend: -14 },
  head: { look: [-0.35, 1.1, -10] }, L: { to: [-0.55, 1.03, -0.41], hand: 'grip', fingers: 'up', palm: 'fwd' }, R: { to: [-0.21, 1.03, -0.41], hand: 'grip', fingers: 'up', palm: 'fwd' }, ...o });
const chop = { L: { to: 'self:chest', off: [-0.1, 0.02, -0.2], hand: 'flat', fingers: [0.2, 0.3, -0.9], palm: [1, 0, 0] }, R: { to: 'self:chest', off: [0.1, 0.06, -0.2], hand: 'flat', fingers: [-0.2, 0.3, -0.9], palm: [-1, 0, 0] } };
const FRONT = [0.0, 1.40, -0.2];   // high between the front seats (just under the headliner, ahead of the headrests), looking back and a little down:
// from any lower centreline position the front passenger seatback hides the child behind it

export const SHOTS = [
  { id: 'v3_F1', v3: true, lens: 28, pos: FRONT, aim: ['daughter:eyes', 0.32, 0.47], header: 'from between the front seats: the daughter back-left of frame in her seat, the EMPTY seat back-right', sync: 'lip', singers: ['daughter'], street: { t: 0.15 }, serves: ['F1'],
    intent: "From between the two front seats looking back. High between the front headrests, looking back and a little down over the seatbacks. The two front headrests frame the edges (the empty passenger seat at frame left, the driver's at frame right); between and beyond them the back bench: the daughter in her car seat left of centre, rapping, hands chopping; the second child seat, empty, right of centre.",
    figs: { daughter: daughterSeat({ head: { look: [0.0, 1.38, -0.2] }, ...chop }), jade: jadeDrive() } },
  { id: 'v3_F2', v3: true, lens: 24, pos: [0.06, 1.16, 0.44], aim: [[0.71, 1.19, 0.91], 0.4, 0.45], header: 'her side window is a shadow screen (puppet monkey)', street: { t: 0.55 }, serves: ['F2'],
    intent: 'As v1 F2 (she was already on this side): from the gap between the front seats toward her right rear window, the pane a lit screen, the daughter in profile at frame right in her car seat.',
    figs: { daughter: daughterSeat({ head: { look: [0.9, 1.15, 0.9] } }), jade: jadeDrive() } },
  { id: 'v3_F3a', v3: true, lens: 40, pos: [-0.05, 1.34, 0.1], aim: ['daughter:eyes', 0.6, 0.38], header: 'tighter, past the passenger seatback: she plucks a hair and blows across her palm (match cut out)', sync: 'lip', singers: ['daughter'], street: { t: 0.9 }, serves: ['F3'],
    intent: "Tighter on her, her face at 0.6/0.38 for the match cut to little Jade (F3b). The back of the empty front passenger seat is a soft dark shape down the left of frame, the wings of her car seat round her head: unmistakably the back seat.",
    figs: { daughter: daughterSeat({ head: { look: [0.02, 1.1, 0.1], nod: 6 }, L: { to: 'self:earL', off: [0.0, 0.05, 0.0], hand: 'pinch', fingers: 'up', palm: 'in' }, R: { to: 'self:mouth', off: [0.0, -0.07, -0.1], hand: 'palmUp', palm: 'up', fingers: [-0.6, 0.1, -0.8] } }), jade: jadeDrive() } },
  { id: 'v3_F4a', v3: true, lens: 26, mirror: 'mirror', mirrorSearch: { faces: ['jade', 'daughter'], box: [[-0.12, 0.3], [1.05, 1.3], [-0.2, 0.25]] }, aim: [[0, 1.33, -0.43], 0.52, 0.45],
    header: "the rear-view mirror: Jade's eyes, and the daughter behind in the back seat, off to the side", sync: 'lip', singers: ['jade', 'daughter'], street: { t: 1.2 }, serves: ['F4 (first half)'],
    intent: "The mirror large, frame centre: in it Jade's eyes at one end and, small and deeper, the daughter in her car seat on the back bench at the other, both singing. True reflection; the camera position is searched so both faces land in the glass.",
    figs: { daughter: daughterSeat({ head: { look: [0, 1.33, -0.43] } }), jade: jadeDrive({ head: { look: [0, 1.33, -0.43] } }) } },
  { id: 'v3_F4b', v3: true, lens: 18, pos: [0.0, 1.38, 1.6], target: [0.0, 1.08, -0.8], header: 'wide from the tailgate: two child seats from behind (hers right, the empty one left), every pane a screen', street: { t: 1.55 }, serves: ['F4 (second half)'],
    intent: 'Wide from the back of the cabin: the backs of the two child seats in the foreground (the daughter in the right one, the left one empty), Jade driving beyond on the left; windscreen, side windows and mirror each a lit screen.',
    figs: { daughter: daughterSeat(), jade: jadeDrive() } },
  { id: 'v3_F5', v3: true, lens: 18, pos: [0.0, 1.42, -0.3], target: [0.0, 0.95, 1.6], header: 'reverse wide from the dashboard: both front seats, then the back bench with her and the empty seat', street: { t: 2.2 }, serves: ['F5'],
    intent: 'Reverse wide from above the dashboard: the two front seats in the foreground (Jade at frame right), and between and beyond them the back bench: the daughter left, the empty child seat right; rear window and rear side windows go dark one per beat.',
    figs: { daughter: daughterSeat({ head: { look: [0.6, 1.1, 1.0] } }), jade: jadeDrive() } },
  { id: 'v3_F6a', v3: true, lens: 24, pos: [0.0, 1.13, 0.92], target: [0.0, 1.2, -0.6], header: 'from the middle of the back bench: the windscreen is the stage', street: { t: 2.6 }, serves: ['F6 (first half)'],
    intent: 'From between the two child seats on the back bench: the windscreen is the stage for the two mirror-posed puppets; Jade (driving) lower left, the empty passenger headrest lower right.',
    figs: { daughter: daughterSeat(), jade: jadeDrive() } },
  { id: 'v3_F6b', v3: true, lens: 24, mirror: 'rear_right', pos: [-0.12, 1.3, 0.3], aim: ['daughter:eyes', 0.62, 0.45], header: 'the daughter and her reflection in her side window wave at once', street: { t: 3.0 }, serves: ['F6 (end)'],
    intent: 'From between the front seats: the daughter in her car seat waves; in her dark side window her reflection waves back at the same instant (true reflection). Camera in the gap between the front seats on the driver side, so her window is clear of the passenger headrest (which sits at the left edge of frame).',
    figs: { daughter: daughterSeat({ head: { look: [0.02, 1.1, 0.1] }, R: { to: 'self:shoulderR', off: [0.06, 0.2, -0.06], hand: 'flat', fingers: 'up', palm: 'fwd' } }), jade: jadeDrive() } },
];

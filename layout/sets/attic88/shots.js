// ATTIC 1988 camera table: one entry per shot id from docs/shots.yaml whose world is attic88 (plus sub-setups a/b
// where the description has two beats, and F3b, the 1988 half of the F3 match cut).
// Fields: id, lens (mm, 36 mm frame), pos, target (or aim: [point, u, v] -> target), figs (mannequin poses),
// book, blankets, light { neon: 'red'|'blue'|'off', door: 0..1, floor: bool, neonI, amb }, shadow (hand-shadow
// casters projected from the neon onto the spread), sync/singers, intent, move (camera end for moving shots).
import { aim } from '../../engine/aim.js';

// ---------------------------------------------------------------- recurring positions
const MAMA = [1.85, -1.7], JADE = [2.5, -1.85];
const JADE_EYE = [2.47, 0.69, -1.8];

const mamaRead = (o = {}) => ({ at: MAMA, legs: 'cross', yaw: 14, spine: { bend: 14 }, head: { look: 'book:G' },
  L: { to: 'book:LO', hand: 'grip', palm: 'in', fingers: 'fwd', off: [0, -0.012, 0] }, R: { to: 'book:RO', hand: 'grip', palm: 'in', fingers: 'fwd', off: [0, -0.012, 0] }, ...o });
const jadeSit = (o = {}) => ({ at: JADE, legs: 'long', yaw: -28, spine: { bend: 10 }, head: { look: 'book:G' }, L: 'lap', R: 'lap', ...o });
const jadeLying = { at: [2.55, 0.13, -1.72], legs: 'straight', pitch: -90, yaw: 0, spine: { bend: 12 }, head: { turn: 25 }, L: 'side', R: 'side' };
// the book open across Mama's knees, tipped toward little Jade (her left) so both can see it
const bookLap = (o = {}) => ({ state: 'open', on: 'mama', off: [0.02, 0.04, 0.1], tilt: 16, toward: 'left', top: 'fwd', v: 8, ...o });
const bookOnPillow = { state: 'closed', at: [1.6, 0.171, -2.3], normal: [0.04, 1, 0.02], top: [0.25, 0, 1] };
const BLK_SIT = [{ who: 'littleJade', mode: 'legs' }, { who: 'mama', mode: 'folded' }];
const BLK_LIE = [{ who: 'littleJade', mode: 'cover' }, { who: 'mama', mode: 'flat' }];
const DOOR_AJAR = 0.06;

export const SHOTS = [
  // ---------------------------------------------------------------- A intro
  { id: 'A1', lens: 32, pos: [-1.7, 1.38, 1.55], aim: [[3.5, 0.8, -0.8], 0.8, 0.74], header: 'one lit opening, lower right',
    intent: 'Ma Lin night outing: the window is a small lit opening low right; everything else is night. Neon stutters on.',
    figs: { littleJade: jadeLying }, book: bookOnPillow, blankets: BLK_LIE, light: { neon: 'red', door: 0, floor: false, amb: 0.15 } },
  { id: 'A2', lens: 28, pos: [2.65, 0.42, 0.55], aim: [[2.0, 0.12, -1.6], 0.5, 0.62], header: 'low drift left across the floor in the neon spill',
    intent: 'Low across the floorboards: piano printout nearest, then mats, textbooks, the book on the pillow, the TV; warm lines between boards.',
    move: { end_pos: [1.6, 0.42, 0.55], end_target_note: 'keep the same heading; ~1 m left over the shot' },
    figs: { littleJade: jadeLying }, book: bookOnPillow, blankets: BLK_LIE, light: { neon: 'red', door: 0, floor: true } },
  { id: 'A3', lens: 24, pos: [3.3, 0.98, -1.15], aim: [[-3.5, 1.0, 0.0], 0.4, 0.5], header: 'tall slot of light, Mama small in it; little Jade back to us',
    intent: 'From behind little Jade (lower right, back to us) across the dark attic to the stair door: a tall warm slot with Mama small in it.',
    figs: { mama: { at: [-3.2, -0.08], legs: 'stand', yaw: 98, spine: { bend: 6 }, head: { look: JADE_EYE }, L: { to: 'self:waist', off: [0.15, -0.06, 0.06], hand: 'relax', palm: 'in' }, R: { to: 'self:waist', off: [0.14, -0.1, -0.04], hand: 'pinch', palm: 'in' } },
      littleJade: jadeSit({ yaw: -70, spine: { bend: 2, twist: -15 }, head: { look: [-3.2, 1.3, -0.08] }, L: 'lap', R: 'lap' }) },
    book: bookOnPillow, blankets: BLK_SIT, light: { neon: 'red', door: 0.42, floor: true } },
  { id: 'A4', lens: 55, pos: [0.98, 0.46, -1.92], aim: [[1.62, 0.33, -2.18], 0.46, 0.58], header: 'close: wet red hands lift the book from the pillow',
    intent: 'Close on the hands: Mama kneels at the pillow, both hands lift the closed book; its cover tips toward the window and catches the neon.',
    figs: { mama: { at: [1.62, -1.72], legs: 'kneel', yaw: 180, spine: { bend: 38 }, head: { look: 'book:cover' }, L: { to: 'book:L', hand: 'grip', palm: 'up', off: [0, -0.01, 0] }, R: { to: 'book:R', hand: 'grip', palm: 'up', off: [0, -0.01, 0] } },
      littleJade: jadeSit({ yaw: -40, head: { look: 'book:cover' } }) },
    book: { state: 'closed', at: [1.62, 0.3, -2.18], normal: [0.35, 1, 0.1], top: [0, 0, -1] }, blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- B verse 1
  { id: 'B1', lens: 55, pos: [1.62, 0.74, -0.95], aim: [JADE_EYE, 0.6, 0.38], header: 'little Jade three-quarter close; Mama soft in the foreground', sync: 'lip', singers: ['littleJade'],
    intent: 'Little Jade sits up on her mat, three-quarter to camera, deadpan, red on her face; Mama settling, out of focus, frame-left foreground.',
    figs: { mama: mamaRead({ yaw: 40, spine: { bend: 6, side: -6 }, head: { look: JADE_EYE }, L: 'lap', R: { to: 'kneeR', hand: 'relax' } }),
      littleJade: jadeSit({ yaw: -38, head: { look: 'mama:eyes' } }) },
    book: { state: 'closed', at: [1.62, 0.171, -2.3], normal: [0, 1, 0], top: [0.25, 0, 1] }, blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'B2', lens: 32, pos: [1.45, 1.32, 0.05], aim: [[2.1, 0.45, -1.7], 0.56, 0.52], header: 'two-shot from the foot of the mats; the spread is the brightest thing', sync: 'lip', singers: ['mama'],
    intent: 'From the foot of the mats, a little above: Mama sings with the book open across her knees, tipped toward little Jade; the spread glows.',
    figs: { mama: mamaRead({ head: { look: JADE_EYE, nod: 12 } }), littleJade: jadeSit() }, book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- C pre-chorus
  { id: 'C2', lens: 35, pos: [1.55, 1.12, -2.22], aim: [[1.95, 0.4, -1.42], 0.5, 0.55], header: 'THUMBNAIL: hand-shadow monkey thrown across the page',
    intent: "Over Mama's shoulder onto the spread: little Jade's two hands (frame left, from the window side) throw a big monkey shadow across the painting.",
    figs: { mama: mamaRead({ head: { look: 'book:G' } }),
      littleJade: jadeSit({ yaw: -50, spine: { bend: 24, side: -8 }, head: { look: 'book:Rmid' },
        L: { to: [2.12, 0.6, -1.3], hand: 'monkeyHead', fingers: [-0.25, 0.35, 0.9], palm: [-0.95, 0.0, -0.3] },
        R: { to: [2.15, 0.52, -1.24], hand: 'monkeyPaw', fingers: [-0.1, 0.95, 0.2], palm: [-0.9, -0.1, -0.3] } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR }, shadow: { casters: ['littleJade.handL', 'littleJade.handR'] } },
  { id: 'C3', lens: 45, pos: [2.62, 0.8, -0.72], aim: [[2.18, 0.62, -1.76], 0.5, 0.44], header: 'close two-shot: Mama lowers the hands with one finger', sync: 'lip', singers: ['mama'],
    intent: "Close two-shot from the window side: Mama, amused, presses little Jade's raised hands down with one finger; both faces in the 4:5 centre.",
    figs: { mama: mamaRead({ yaw: 30, head: { look: JADE_EYE }, L: { to: 'littleJade:handR', off: [0, 0.035, 0], hand: 'point', fingers: 'down', palm: 'back' } }),
      littleJade: jadeSit({ yaw: -40, spine: { bend: 18 }, head: { look: 'mama:eyes' }, L: { to: [2.2, 0.5, -1.4], hand: 'relax', palm: 'down' }, R: { to: [2.17, 0.47, -1.37], hand: 'relax', palm: 'down' } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'C5a', lens: 50, pos: [0.45, 0.62, -1.62], aim: [[1.85, 0.6, -1.45], 0.36, 0.5], header: 'Mama in profile blows on the page; dust in the beam behind',
    intent: 'Pure profile, contre-jour: Mama leans to the page and blows; the neon beam from the window behind her full of dust; she sits in the left third.',
    figs: { mama: mamaRead({ spine: { bend: 34 }, head: { look: 'book:Rmid', pitchK: 0.8 } }), littleJade: jadeSit({ head: { look: 'book:G' } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'C5b', lens: 40, pos: [1.82, 0.98, -1.86], aim: [[1.97, 0.42, -1.3], 0.5, 0.5], header: "insert: the spread from Mama's eye (mist over the egg)",
    intent: "Mama's eyeline straight into the spread; the cut goes inside the painting here. Page quads in the sidecar for the push.",
    figs: { mama: mamaRead({ spine: { bend: 30 }, head: { look: 'book:G' } }), littleJade: jadeSit() }, book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- D hook
  { id: 'D3a', lens: 50, pos: [1.9, 0.86, -1.82], aim: [[2.0, 0.42, -1.3], 0.5, 0.62], header: 'insert: top of the right page, dark room above it (gold beams leave the sheet)',
    intent: 'The right page low in frame, its top edge two-thirds up, dark attic above: the two gold beams shoot up off the top of the sheet.',
    figs: { mama: mamaRead({ head: { look: 'book:G' } }), littleJade: jadeSit() }, book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'D3b', lens: 30, pos: [2.0, 1.6, 0.25], aim: [[2.15, 0.35, -1.75], 0.5, 0.58], header: 'the attic floor: no crib, only mats; side by side, singing', sync: 'lip', singers: ['mama', 'littleJade'],
    intent: 'High from the foot of the mats: floorboards and two mats, no crib; Mama and little Jade side by side singing, the book open between them.',
    figs: { mama: { at: [1.8, -1.85], legs: 'cross', yaw: 8, spine: { bend: 4 }, head: { look: [2.0, 1.0, 0.0] }, L: { to: 'book:LO', hand: 'flat', palm: 'down' }, R: 'kneeR' },
      littleJade: { at: [2.42, -1.95], legs: 'cross', yaw: -6, spine: { bend: 2 }, head: { look: [2.2, 1.0, 0.0] }, L: 'kneeL', R: { to: 'book:RO', hand: 'flat', palm: 'down' } } },
    book: { state: 'open', at: [2.12, 0.068, -1.6], normal: [0, 1, 0], top: [0, 0, 1], v: 4 }, blankets: [{ who: 'mama', mode: 'folded' }, { who: 'littleJade', mode: 'folded' }], light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'D9', lens: 28, pos: [0.55, 0.95, 0.35], aim: [[2.5, 0.62, -1.75], 0.68, 0.5], header: 'little Jade copies the monkey: one leg up, hand shading her eyes; Mama laughing',
    intent: 'End of the pull-back: little Jade stands on her mat in the monkey pose (frame right), Mama on her mat laughing (frame centre-left).',
    figs: { mama: { at: [1.62, -1.85], legs: 'cross', yaw: 30, spine: { bend: -8, side: 4 }, head: { look: [2.5, 1.2, -1.8], nod: -15, tilt: 8 }, L: { to: 'self:mouth', off: [0.04, -0.05, 0.08], hand: 'relax', palm: 'back' }, R: 'kneeR' },
      littleJade: { at: [2.55, -1.62], legs: 'oneLegUp', legOpts: { upLeg: 'L' }, yaw: -30, spine: { bend: 4 }, head: { look: [0.6, 1.0, 1.0] },
        R: { to: 'self:forehead', off: [0, 0.045, 0.03], hand: 'flat', palm: 'down', fingers: 'left' }, L: { to: 'self:shoulderL', off: [0.22, -0.05, 0.12], hand: 'relax', palm: 'down' } } },
    book: { state: 'open', at: [1.95, 0.068, -1.25], normal: [0, 1, 0], top: [0, 0, 1], v: 4 }, blankets: BLK_SIT.slice(1).concat([{ who: 'littleJade', mode: 'flat' }]), light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- E memory verse
  { id: 'E1', lens: 50, pos: [2.15, 0.76, -0.78], aim: [[2.18, 0.68, -1.78], 0.5, 0.42], header: "close two-shot: Mama taps little Jade's nose", sync: 'lip', singers: ['mama'],
    intent: "Close two-shot in one pool of neon: Mama (left) turned to little Jade (right), her fingertip on little Jade's nose.",
    figs: { mama: mamaRead({ yaw: 40, spine: { bend: 10 }, head: { look: JADE_EYE }, L: { to: 'littleJade:nose', hand: 'point', fingers: 'to:littleJade:nose', palm: 'down', off: [-0.03, -0.01, 0] } }),
      littleJade: jadeSit({ yaw: -42, head: { look: 'mama:eyes' } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'E3', lens: 70, pos: [2.98, 0.72, -1.08], aim: [JADE_EYE, 0.6, 0.4], header: 'little Jade close; Mama a warm blur behind', sync: 'lip', singers: ['littleJade'],
    intent: 'Little Jade close from the window side, deadpan, a small shrug; Mama behind her frame-left is only a warm blur.',
    figs: { mama: mamaRead({ yaw: 32, head: { look: JADE_EYE } }), littleJade: jadeSit({ yaw: -15, head: { look: [2.9, 0.75, -0.9], turn: 0 }, L: { to: 'self:hip', off: [0.12, 0.12, 0.2], hand: 'palmUp', palm: 'up' }, R: { to: 'self:hip', off: [-0.02, 0.12, 0.22], hand: 'palmUp', palm: 'up' } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'E5', lens: 85, pos: [2.32, 0.74, -1.25], aim: [[2.38, 0.72, -1.86], 0.5, 0.45], header: "extreme close: Mama's cupped hand and lips at little Jade's ear",
    intent: "Extreme close: Mama's mouth behind her cupped hand at little Jade's ear; only the two heads and the hand.",
    figs: { mama: { at: [2.0, -1.78], legs: 'kneel', yaw: 60, spine: { bend: 18, side: 6 }, head: { look: 'littleJade:earR', nod: -5 }, L: { to: 'self:mouth', off: [0.05, -0.0, 0.05], hand: 'cup', palm: 'to:littleJade:earR', fingers: 'up' }, R: 'kneeR' },
      littleJade: jadeSit({ yaw: -12, head: { look: [2.3, 0.7, -0.5] } }) },
    book: bookLap({ on: null, state: 'open', at: [2.1, 0.068, -1.25], normal: [0, 1, 0], top: [0, 0, -1] }), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'E6', lens: 50, pos: [2.25, 0.74, -0.82], aim: [[2.2, 0.7, -1.82], 0.5, 0.42], header: 'little Jade looks at her sideways; Mama chuckles',
    intent: 'Two-shot: little Jade faces front, eyes slid sideways to Mama; Mama leans back chuckling, hand near her mouth.',
    figs: { mama: { at: [1.95, -1.82], legs: 'kneel', yaw: 40, spine: { bend: -4 }, head: { look: JADE_EYE, nod: -8, tilt: -6 }, L: { to: 'self:mouth', off: [0.03, -0.04, 0.07], hand: 'relax', palm: 'back' }, R: 'kneeR' },
      littleJade: jadeSit({ yaw: -10, head: { look: [1.6, 0.75, -0.9] } }) },
    book: { state: 'open', at: [2.15, 0.068, -1.2], normal: [0, 1, 0], top: [0, 0, -1] }, blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- F3b (1988 half of the match cut)
  { id: 'F3b', lens: 50, pos: [2.95, 0.66, -1.05], aim: [JADE_EYE, 0.6, 0.38], header: 'match cut: little Jade blows across her open palm',
    intent: 'Matches F3a: same screen place for face and palm. Little Jade blows across her flat open palm; hairs fly toward frame left.',
    figs: { mama: mamaRead({ head: { look: JADE_EYE } }), littleJade: jadeSit({ yaw: -20, spine: { bend: 6 }, head: { look: [2.62, 0.62, -1.6], pitchK: 0.5 }, R: { to: 'self:mouth', off: [0.09, -0.07, 0.1], hand: 'palmUp', palm: 'up', fingers: [0.6, 0.1, 0.8] } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- G the band (margins close; keep action in the centre column)
  { id: 'G1', lens: 60, pos: [2.32, 0.76, -0.95], aim: [JADE_EYE, 0.52, 0.42], header: 'little Jade touches her own forehead (centre column)', sync: 'lip', singers: ['littleJade'],
    intent: 'Margins close from left and right: face and hand in the centre column. Little Jade touches her forehead where the band would sit.',
    figs: { mama: mamaRead({ yaw: 30, head: { look: JADE_EYE } }), littleJade: jadeSit({ yaw: -18, head: { look: [2.3, 0.85, -0.9] }, R: { to: 'self:forehead', off: [0, 0.01, 0.04], hand: 'point', palm: 'back', fingers: 'up' } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },
  { id: 'G3', lens: 45, pos: [2.5, 0.98, -0.95], aim: [[2.1, 0.5, -1.55], 0.5, 0.5], header: 'small hand flat over the picture; its shadow covers the band (centre column)', sync: 'lip', singers: ['littleJade'],
    intent: "Vertical stack in the centre column: little Jade's face on top, her flat hand over the page, its shadow on the painted band.",
    figs: { mama: mamaRead({ head: { look: 'book:G' } }), littleJade: jadeSit({ yaw: -45, spine: { bend: 26 }, head: { look: 'book:Rmid', pitchK: 0.7 }, R: { to: 'book:Rmid', off: [0.03, 0.07, 0.0], hand: 'flat', palm: 'down', fingers: [-0.6, 0, 0.8] } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR }, shadow: { casters: ['littleJade.handR'] } },
  { id: 'G4', lens: 40, pos: [2.08, 1.15, -1.95], aim: [[1.98, 0.42, -1.38], 0.5, 0.56], header: "the ring's shadow lowers over the shadow of little Jade's head (centre column, ~15% strip)", sync: 'lip', singers: ['mama'],
    intent: "Over the spread: little Jade's head-shadow on the page, Mama's finger-and-thumb ring between the window and her head lowering its shadow onto it.",
    figs: { mama: mamaRead({ yaw: 18, head: { look: 'book:Rmid' }, L: { to: [2.28, 0.74, -1.38], hand: 'ring', fingers: [0.1, 0.3, 0.95], palm: [-0.2, -0.95, 0.2] } }),
      littleJade: jadeSit({ yaw: -55, spine: { bend: 32, side: -6 }, head: { look: 'book:Rmid', pitchK: 0.8 } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR }, shadow: { casters: ['mama.handL', 'littleJade.head'] } },
  { id: 'G5', lens: 85, pos: [2.17, 0.72, -1.2], aim: [JADE_EYE, 0.5, 0.45], header: "'Yes': little Jade's face dead centre", sync: 'lip', singers: ['littleJade'],
    intent: "First of two centred faces: little Jade holds Mama's look (Mama is just off-lens left). Nothing moves.",
    figs: { mama: mamaRead({ yaw: 30, head: { look: JADE_EYE } }), littleJade: jadeSit({ yaw: -30, spine: { bend: 4 }, head: { look: [2.12, 0.74, -1.25] } }) },
    book: bookLap(), blankets: BLK_SIT, light: { neon: 'red', door: DOOR_AJAR } },

  // ---------------------------------------------------------------- L end
  { id: 'L3', same: 'A1', header: 'the film’s first frame again; neon hums, then off',
    intent: 'Identical camera to A1. The window lower right, neon red; at 237.840 the neon goes off (render light.neon off for the end state).' },
];

// resolve aims and copies
for (const s of SHOTS) {
  if (s.same) { const o = SHOTS.find((x) => x.id === s.same); Object.assign(s, { ...o, ...s, id: s.id }); }
  if (s.aim && !s.target) s.target = aim(s.pos, s.aim[0], s.aim[1], s.aim[2], s.lens);
}

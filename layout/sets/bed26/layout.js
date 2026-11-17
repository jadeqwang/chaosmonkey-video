// BEDROOM 2026 (Austin) — single source of truth (metres, y up, floor y = 0). A child's bedroom at night.
//   x: -1.7 left wall (bookshelf) ... +1.7 right wall (the bed against it)
//   z: -1.6 back wall (window with a blind, the bed's head) ... +1.6 front wall (door, behind camera)
export const ROOM = { x0: -1.7, x1: 1.7, z0: -1.6, z1: 1.6, h: 2.6 };
// low toddler bed along the right wall, head at the back wall
export const BED = { x0: 0.95, x1: 1.7, z0: -1.45, z1: 0.05, frameH: 0.2, mattress: 0.13, headH: 0.62, footH: 0.38 };
export const BED_TOP = BED.frameH + BED.mattress;  // 0.33 m: top of the mattress (blanket on it)
export const RUG = { x: 0.05, z: -0.15, w: 1.7, d: 1.2 };
export const WINDOW = { z: -1.6, x: -0.45, sill: 0.82, w: 0.95, h: 1.15, slats: 22 };
export const SHELF = { x: -1.7, z: -0.75, w: 0.85, h: 1.15, d: 0.3, shelves: 4 };
export const NIGHTSTAND = { x: 0.62, z: -1.38, w: 0.42, h: 0.46, d: 0.34 };
export const LAMP = { on: false };  // a night-light on the nightstand, off
// lights
export const LIGHTS = {
  flashlight: { kind: 'small handheld LED flashlight (spot ~16 deg), per-shot position and aim', color: 0xfff4e6 },
  moon: { kind: 'blue-grey night glow through the blind slats', pos: [-0.45, 1.5, -2.6], color: 0x6070a0 },
  night: { kind: 'ambient night', color: 0x141a2c },
};

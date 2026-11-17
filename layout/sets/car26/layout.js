// CAR 2026 — compact SUV interior at dusk on an Austin highway. Single source of truth (metres, y up).
// The car is fixed in world space and faces -z (forward). Left-hand drive: the driver sits at x < 0.
// Ground (road surface) is y = 0; the cabin floor is at y = 0.32.
export const CAR = {
  floorY: 0.32, beltY: 0.98, roofY: 1.45, halfW: 0.74,
  dash: { z0: -1.02, z1: -0.62, y0: 0.6, y1: 1.0 },
  wind: { base: { z: -0.84, y: 1.0, halfW: 0.69 }, top: { z: -0.22, y: 1.43, halfW: 0.64 } },   // windscreen
  pillars: { B: [0.5, 0.6], C: [1.22, 1.32], D: [1.55, 1.66] },
  sideWin: { front: [-0.2, 0.5], rear: [0.6, 1.22], quarter: [1.32, 1.55], top: 1.40 },          // z ranges of the side openings
  rearWin: { z0: 1.68, y0: 1.0, z1: 1.56, y1: 1.4, halfW: 0.6 },                                  // tailgate glass
  frontSeatX: 0.38, frontHp: { y: 0.62, z: 0.02 }, rearHp: { y: 0.64, z: 0.95 },
  wheel: { x: -0.38, y: 0.95, z: -0.45, r: 0.19, tiltDeg: 28 },
  mirror: { at: [0.0, 1.33, -0.43], w: 0.26, h: 0.072 },
  carSeat: { x: 0.38, z: 0.95, w: 0.44, cushionY: 0.76, backTop: 1.32 },                       // forward-facing, behind the passenger
};
// the road: two lanes our way, the car in the right lane; streetlights on the right shoulder and the median
export const ROAD = { laneW: 3.7, carX: 0.0, shoulderX: 5.2, medianX: -6.4, speed: 29.0 /* m/s (65 mph) */, spacing: 42.0,
  poleH: 9.5, armL: 2.4, lampColor: 0xffb468 /* sodium-amber */, phase: 6.0 };
// streetlight lamp heads at time t (s): poles move +z past the car (the car drives -z)
export function lampsAt(t, n = 4) {
  const off = ((ROAD.speed * t + ROAD.phase) % ROAD.spacing + ROAD.spacing) % ROAD.spacing;
  const out = [];
  for (let k = -3; k <= 3; k++) {
    const z = -k * ROAD.spacing + off - 20;  // poles at z = ... the nearest ones bracket the car
    out.push({ side: 'right', pole: [ROAD.shoulderX, 0, z], lamp: [ROAD.shoulderX - ROAD.armL, ROAD.poleH, z] });
    out.push({ side: 'median', pole: [ROAD.medianX, 0, z + ROAD.spacing / 2], lamp: [ROAD.medianX + ROAD.armL, ROAD.poleH, z + ROAD.spacing / 2] });
  }
  return out.sort((a, b) => Math.hypot(a.lamp[0], a.lamp[2] - 0.5) - Math.hypot(b.lamp[0], b.lamp[2] - 0.5)).slice(0, n);
}
export const LIGHTS = {
  street: { kind: 'sodium-amber streetlights passing (parametrised by t, see lampsAt)', color: ROAD.lampColor },
  dusk: { kind: 'violet blue-hour sky', color: 0x6a5a9a },
  dash: { kind: 'faint dashboard glow', color: 0x80a0ff },
};

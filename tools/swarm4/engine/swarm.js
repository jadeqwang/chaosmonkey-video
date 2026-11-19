// The swarm: monkeys (instanced sprites + two hero billboards), lanterns, threads, beads, hairs, puffs, seals,
// name slips, the lantern light map. update(s) recomputes everything from the tree and the frame number.
import * as THREE from 'three';
import { NOISE, FOG } from './glsl.js';
import { buildSprites } from './sprites.js';
import { buildCards, loadFonts } from './text.js';
import { hash1, clamp, smoothstep, lerp } from './rng.js';
import { makeClips } from './clips.js';

const UP = new THREE.Vector3(0, 1, 0);
const ease = (t) => t * t * (3 - 2 * t);

export const SWARM_DEFAULTS = {
  monkeys: { height: [1.5, 1.35, 1.3, 1.25, 1.25], flip_frac: 0.5 },
  lantern: { radius: 0.55, min_px: 2.6, core: '#ffd29a', color: '#ff9a48', intensity: 3.2, gen_scale: [1.4, 1.25, 1.1, 1.0, 1.0],
    flare: 2.5, pulse: 1.4, interior: 0.55, light_radius: 11, light_gain: 1.0, hero_light: 0.3, hero_radius: 6, hero_size: 0.3, hero_i: 0.55, flicker: 0.06, body_px: 7 },
  threads: { color: '#e02814', intensity: 1.3, opacity: [1, 1, 0.8, 0.55, 0.38], width: 0.03, min_px: 1.2, coverage: 0.5, segments: 8,
    relax: 1.6, sag: 0.0, bow: 0.07, between_two: { color: '#ff4a26', intensity: 2.4, grow: 6, sag: 0.12 } },
  beads: { color: '#ffd080', intensity: 6, radius: 0.5, min_px: 2.4 },
  hairs: { color: '#0b0908', alpha: 0.95, width: 0.06, min_px: 1.3, glint: '#ffcf8a', glint_i: 0.9, glint_px: 1.6, wiggle: 0.6 },
  puffs: { life: 11, size: 1.5, min_px: 7, color: '#c9c6bb', ink: '#1a1716', seal_size: 0.7 },
  seals: { size: 0.55, min_px: 4.5, life: 8, emit: 1.6, true_size: 0.42 },
  slips: { from: 38, to: 82, fade: 5, n: 12, min_px: 18, size: 0.95 },
  vortex: { turns: [0.8, 2.2], column_r: [25, 140], lift: [40, 260] },
  ledge_lift: 0.05,
};

export function secondPlace(cfg, terrain, root) {
  const S2 = cfg.second;
  const ledgeOut = new THREE.Vector3(root.pos.x - terrain.P.peak.x, 0, root.pos.z - terrain.P.peak.z).normalize();
  const tang = new THREE.Vector3(ledgeOut.z, 0, -ledgeOut.x).applyAxisAngle(UP, (S2.az || 0) * Math.PI / 180);
  const pos = root.pos.clone().addScaledVector(tang, S2.dist);
  pos.y = terrain.height(pos.x, pos.z);
  return { pos, tang, out: ledgeOut };
}

function vec(a) { return new THREE.Vector3(a[0], a[1], a[2]); }

export async function makeSwarm(cfg, o) {
  const { scene, terrain, tree, shared, W, H, camPath } = o;
  const C = deepMergeLocal(structuredClone(SWARM_DEFAULTS), cfg.swarm || {});
  const Sp = cfg.spawn, Se = cfg.seal, Wk = cfg.work, S2 = cfg.second;
  const pxK = H / 540;
  await loadFonts(cfg);
  const spr = await buildSprites(cfg);
  const cards = buildCards(cfg);
  const clips = await makeClips(cfg);
  const nodes = tree.nodes, G = tree.G, root = nodes[0];
  const hgt = (n) => C.monkeys.height[n.gen] ?? 1.3;
  for (const n of nodes) {
    n.h = hgt(n);
    n.hand = n.pos.clone().addScaledVector(UP, n.h * 0.72);
    n.flip = hash1(n.id, 5) < C.monkeys.flip_frac ? -1 : 1;
    n.seed = hash1(n.id, 6);
  }
  const crowd = nodes.filter((n) => n.gen >= 1);
  crowd.forEach((n, i) => { n.ci = i; });
  // the second monkey: on the ledge, facing the root
  const { pos: secondPos, tang } = secondPlace(cfg, terrain, root);
  const second = { pos: secondPos, h: cfg.root.height, hand: secondPos.clone().addScaledVector(UP, cfg.root.height * 0.72), land: S2.land };
  root.h = cfg.root.height; root.hand = root.pos.clone().addScaledVector(UP, root.h * 0.72);
  // palm (where the hairs pour in)
  const palm = root.pos.clone().addScaledVector(UP, root.h * 0.42).addScaledVector(tang, root.h * 0.18);

  // ---------------------------------------------------------------- flight paths (spawn)
  const cam0 = new THREE.PerspectiveCamera(); camPath.apply(cam0, 0);
  const c0R = new THREE.Vector3().setFromMatrixColumn(cam0.matrixWorld, 0), c0F = new THREE.Vector3().setFromMatrixColumn(cam0.matrixWorld, 2).negate();
  const rf = Sp.root_hair.from;
  root.from = root.pos.clone().addScaledVector(c0R, rf[0]).addScaledVector(UP, rf[1]).addScaledVector(c0F, rf[2]);
  for (const n of nodes) {
    const A = n.gen === 0 ? root.from : nodes[n.parent].hand, B = n.pos.clone().addScaledVector(UP, n.h * 0.3);
    const d = A.distanceTo(B);
    const side = new THREE.Vector3().subVectors(B, A).cross(UP).normalize();
    n.fl = { A, B, arc: Sp.arc * d * (0.7 + 0.6 * hash1(n.id, 8)) + 0.5, sway: (hash1(n.id, 9) - 0.5) * 0.25 * d, side };
  }
  const flightAt = (n, u, relax = 1) => {
    const f = n.fl; const p = f.A.clone().lerp(f.B, u);
    const b = 4 * u * (1 - u) * relax;
    return p.addScaledVector(UP, f.arc * b).addScaledVector(f.side, f.sway * b);
  };
  const flightU = (n, s) => { const t = clamp((s - n.depart) / n.flight, 0, 1); return 1 - (1 - t) * (1 - t) * (1 - 0.35 * t); };

  // ---------------------------------------------------------------- dispersal hairs
  const lastBranch = Se.branches[Se.branches.length - 1][Se.branches[Se.branches.length - 1].length - 1];
  const hairs = [];
  const HPM = Se.hairs_per_monkey;
  for (const n of crowd) {
    for (let k = 0; k < HPM; k++) {
      const chain = []; let a = n;
      while (a.gen >= 1) { chain.push(a); if (a.gen === 1) break; a = nodes[a.parent]; }
      const g1 = chain[chain.length - 1];
      const jit = hash1(n.id * 7 + k, 31);
      const P = chain.map((c, i) => c.hand.clone().add(new THREE.Vector3((hash1(n.id + i, 40 + k) - 0.5), (hash1(n.id + i, 50 + k) - 0.3) * 0.6, (hash1(n.id + i, 60 + k) - 0.5)).multiplyScalar(i ? 0.8 : 0)));
      const T = chain.map((c, i) => (i === 0 ? c.seal : c.seal + jit * Math.min(i, 2) * 0.6));
      const V = (Se.vortex[g1.sealBeat] ?? 12) * (1 + (hash1(n.id * 3 + k, 33) - 0.5) * 2 * Se.vortex_jitter);
      const isLast = g1.branch === lastBranch && n === g1 && k === 0;
      const tv0 = T[T.length - 1];
      const end = isLast ? second.pos.clone().addScaledVector(UP, 0.4) : palm.clone().add(new THREE.Vector3((hash1(n.id, 70 + k) - 0.5) * 0.15, 0, (hash1(n.id, 80 + k) - 0.5) * 0.15));
      const tv1 = isLast ? S2.land : tv0 + V;
      const S0 = P[P.length - 1].clone();
      { const sp = 0.12 * S0.distanceTo(end); S0.add(new THREE.Vector3(hash1(n.id, 91 + k) - 0.5, (hash1(n.id, 92 + k) - 0.3) * 0.6, hash1(n.id, 93 + k) - 0.5).multiplyScalar(sp)); }
      const rel = S0.clone().sub(end);
      const VX = C.vortex;
      hairs.push({ node: n, k, P, T, tv0, tv1, end, isLast,
        a0: Math.atan2(rel.x, rel.z), r0: Math.hypot(rel.x, rel.z), y0: S0.y,
        turns: lerp(VX.turns[0], VX.turns[1], hash1(n.id + k * 977, 34)) * (cfg.vortex_dir ?? 1),
        rc: lerp(VX.column_r[0], VX.column_r[1], hash1(n.id + k * 131, 35)), lift: lerp(VX.lift[0], VX.lift[1], hash1(n.id + k * 71, 36)),
        ph: hash1(n.id + k, 37) * 6.28 });
    }
  }
  const secondHair = hairs.find((h) => h.isLast);
  const lastArrival = Math.max(...hairs.map((h) => h.tv1));
  function hairAt(h, t) {
    if (t < h.T[0]) return null;
    for (let i = 0; i < h.P.length - 1; i++) {
      if (t < h.T[i + 1]) {
        const u = ease((t - h.T[i]) / (h.T[i + 1] - h.T[i]));
        const p = h.P[i].clone().lerp(h.P[i + 1], u);
        const w = Math.sin(u * Math.PI) * C.hairs.wiggle * Math.min(1, h.P[i].distanceTo(h.P[i + 1]) * 0.05);
        return p.add(new THREE.Vector3(Math.sin(h.ph + t), Math.cos(h.ph * 1.3 + t * 0.7), Math.cos(h.ph + t * 1.1)).multiplyScalar(w));
      }
    }
    if (t < h.tv0) return h.P[h.P.length - 1].clone();
    if (t > h.tv1) return null;
    const u = clamp((t - h.tv0) / (h.tv1 - h.tv0), 0, 1);
    const ue = 1 - Math.pow(1 - u, 1.6);
    const ang = h.a0 + h.turns * Math.PI * 2 * ue;
    const rcol = lerp(h.r0, h.rc, smoothstep(0, 0.45, u));
    const r = rcol * (1 - smoothstep(0.62, 1, u));
    const yTop = h.end.y + h.lift;
    const y = u < 0.55 ? lerp(h.y0, yTop, smoothstep(0, 0.55, u)) : lerp(yTop, h.end.y, smoothstep(0.55, 1, u));
    const p = new THREE.Vector3(h.end.x + Math.sin(ang) * r, y, h.end.z + Math.cos(ang) * r);
    p.lerp(h.end, smoothstep(0.9, 1, u));
    return h.P[h.P.length - 1].clone().lerp(p, smoothstep(0, 0.12, u));
  }

  // ---------------------------------------------------------------- materials / meshes
  const quad = () => {
    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0]), 3));
    g.setIndex([0, 1, 2, 0, 2, 3]); return g;
  };
  const inst = (g, name, n, size) => { const a = new THREE.InstancedBufferAttribute(new Float32Array(n * size), size); a.setUsage(THREE.DynamicDrawUsage); g.setAttribute(name, a); return a; };
  const U = (v) => ({ value: v });
  const moonC = new THREE.Color(cfg.look.moon_col), ambC = new THREE.Color(cfg.look.amb_top), warmC = new THREE.Color(C.lantern.color);

  // crowd sprites
  const NC = crowd.length;
  const cg = quad();
  const cA = { pos: inst(cg, 'iPos', NC, 3), size: inst(cg, 'iSize', NC, 1), frame: inst(cg, 'iFrame', NC, 1), flip: inst(cg, 'iFlip', NC, 1), alpha: inst(cg, 'iAlpha', NC, 1), warm: inst(cg, 'iWarm', NC, 1), col: inst(cg, 'iIdc', NC, 3) };
  const rects = spr.frames.map((f) => new THREE.Vector4(...f.rect)), anch = spr.frames.map((f) => new THREE.Vector4(f.anchor[0], f.anchor[1], f.aspect, f.hfrac));
  const monkeyVS = /* glsl */`
    attribute vec3 iPos; attribute float iSize, iFrame, iFlip, iAlpha, iWarm; attribute vec3 iIdc;
    uniform vec4 uRects[${rects.length}]; uniform vec4 uAnch[${rects.length}];
    varying vec2 vUv; varying vec3 vW; varying float vA, vWarm; varying vec3 vIdc;
    void main(){
      int f = int(iFrame + .5); vec4 R = uRects[f]; vec4 A = uAnch[f];
      float sh = iSize / A.w, sw = sh * A.z;
      vec3 camR = vec3(viewMatrix[0][0], viewMatrix[1][0], viewMatrix[2][0]);
      vec3 camU = vec3(viewMatrix[0][1], viewMatrix[1][1], viewMatrix[2][1]);
      vec3 w = iPos + camR * (position.x - A.x) * sw * iFlip + camU * (position.y - (1. - A.y)) * sh;
      vW = w; vUv = R.xy + position.xy * R.zw; vA = iAlpha; vWarm = iWarm; vIdc = iIdc;
      vec4 mv = viewMatrix * vec4(w, 1.);
      mv.xyz += normalize(-mv.xyz) * iSize * .6;
      gl_Position = projectionMatrix * mv;
      if (iAlpha <= 0.) gl_Position = vec4(2., 2., 2., 1.);
    }`;
  const monkeyFS = /* glsl */`
    ${NOISE}
    ${FOG}
    uniform sampler2D uTex; uniform vec3 uMoon, uAmb, uWarmC; uniform float uRange, uIds;
    varying vec2 vUv; varying vec3 vW; varying float vA, vWarm; varying vec3 vIdc;
    void main(){
      vec4 t = texture2D(uTex, vUv);
      if (t.a < .35) discard;
      if (uIds > .5) { gl_FragColor = vec4(vIdc, 1.); return; }
      if (uIds < -.5) { gl_FragColor = vec4(t.rgb, 1.); return; }
      vec3 c = t.rgb * (uMoon * .55 + uAmb * .9) * mix(.55, 1., uRange) + t.rgb * uWarmC * vWarm * 1.1;
      c = applyFog(c, vW, vWarm * .3);
      gl_FragColor = vec4(c, t.a * vA);
    }`;
  const crowdMat = new THREE.ShaderMaterial({ uniforms: { ...shared, uTex: U(spr.tex), uRects: U(rects), uAnch: U(anch), uMoon: U(moonC), uAmb: U(ambC), uWarmC: U(warmC), uRange: U(1), uIds: U(0) },
    vertexShader: monkeyVS, fragmentShader: monkeyFS, transparent: true, depthWrite: true, side: THREE.DoubleSide });
  const crowdMesh = new THREE.Mesh(cg, crowdMat); crowdMesh.frustumCulled = false; crowdMesh.renderOrder = 20; scene.add(crowdMesh);

  // heroes: root + second, one quad each with its own full-res texture (or clip frame)
  const heroMat = () => new THREE.ShaderMaterial({
    uniforms: { ...shared, uTex: U(null), uAnchor: U(new THREE.Vector4(0.5, 0.95, 0.8, 0.88)), uPos: U(new THREE.Vector3()), uSize: U(1.5), uFlip: U(1), uAlpha: U(0), uWarm: U(1),
      uMoon: U(moonC), uAmb: U(ambC), uWarmC: U(warmC), uRange: U(1), uIds: U(0), uScale: U(1), uLPos: U(new THREE.Vector3()), uLI: U(0) },
    vertexShader: /* glsl */`
      uniform vec4 uAnchor; uniform vec3 uPos; uniform float uSize, uFlip, uScale;
      varying vec2 vUv; varying vec3 vW;
      void main(){
        float sh = uSize / uAnchor.w * uScale, sw = sh * uAnchor.z;
        vec3 camR = vec3(viewMatrix[0][0], viewMatrix[1][0], viewMatrix[2][0]);
        vec3 camU = normalize(mix(vec3(0., 1., 0.), vec3(viewMatrix[0][1], viewMatrix[1][1], viewMatrix[2][1]), .5));
        vec3 w = uPos + camR * (position.x - uAnchor.x) * sw * uFlip + camU * (position.y - (1. - uAnchor.y)) * sh;
        vW = w; vUv = position.xy;
        vec4 mv = viewMatrix * vec4(w, 1.); mv.xyz += normalize(-mv.xyz) * uSize * .35;
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: /* glsl */`
      ${NOISE}
      ${FOG}
      uniform sampler2D uTex; uniform vec3 uMoon, uAmb, uWarmC, uLPos; uniform float uRange, uIds, uAlpha, uWarm, uLI;
      varying vec2 vUv; varying vec3 vW;
      void main(){
        vec4 t = texture2D(uTex, vUv);
        if (t.a < .04 || uAlpha <= 0.) discard;
        if (uIds > .5) { if (t.a < .5) discard; gl_FragColor = vec4(1., .2, .2, 1.); return; }
        if (uIds < -.5) { gl_FragColor = vec4(t.rgb, t.a); return; }
        float dl = length(vW - uLPos);
        float side = clamp(.6 + .4 * sign(vW.x - uLPos.x), 0., 1.);
        vec3 warm = uWarmC * uLI * 1.3 / (1. + dl * dl * .7);
        vec3 c = t.rgb * (uMoon * .5 + uAmb * .8) * mix(.6, 1., uRange) + t.rgb * (warm + uWarmC * uWarm * .25);
        c = applyFog(c, vW, 0.);
        gl_FragColor = vec4(c, t.a * uAlpha);
      }`,
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
  });
  const heroes = [0, 1].map(() => { const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1).translate(0.5, 0.5, 0), heroMat()); m.frustumCulled = false; m.renderOrder = 22; scene.add(m); return m; });

  // glow sprites (lanterns, beads, glints, flashes): additive HDR
  const NG = nodes.length * 2 + hairs.length + 64;
  const gg = new THREE.InstancedBufferGeometry();
  gg.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]), 3)); gg.setIndex([0, 1, 2, 0, 2, 3]);
  const gA = { pos: inst(gg, 'iPos', NG, 3), rad: inst(gg, 'iRad', NG, 1), minpx: inst(gg, 'iMinPx', NG, 1), col: inst(gg, 'iCol', NG, 3), body: inst(gg, 'iBody', NG, 1) };
  const glowMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    uniforms: { uResY: U(H), uPxK: U(pxK), uBodyPx: U(C.lantern.body_px), uIds: U(0), uCore: U(new THREE.Color(C.lantern.core)) },
    vertexShader: /* glsl */`
      attribute vec3 iPos, iCol; attribute float iRad, iMinPx, iBody;
      uniform float uResY, uPxK, uBodyPx;
      varying vec2 vUv; varying vec3 vCol; varying float vBody, vK;
      void main(){
        vec4 mv = viewMatrix * vec4(iPos, 1.);
        float depth = max(-mv.z, .01);
        float ppm = projectionMatrix[1][1] * uResY * .5 / depth;
        float px = iRad * ppm, pxc = max(px, iMinPx * uPxK);
        float half_ = pxc / ppm;
        mv.xy += position.xy * half_;
        vUv = position.xy; vCol = iCol; vBody = iBody * smoothstep(uBodyPx * .6, uBodyPx * 1.4, px / uPxK);
        vK = clamp(px / max(pxc, 1e-4), 0., 1.);
        gl_Position = projectionMatrix * mv;
        if (iRad <= 0.) gl_Position = vec4(2., 2., 2., 1.);
      }`,
    fragmentShader: /* glsl */`
      uniform float uIds; uniform vec3 uCore;
      varying vec2 vUv; varying vec3 vCol; varying float vBody, vK;
      void main(){
        float r2 = dot(vUv, vUv);
        if (r2 > 1.) discard;
        float halo = exp(-r2 * 5.5) * .55 + exp(-r2 * 26.) * 1.4;
        // the paper lantern itself when it is big enough to see: a warm ellipse with ribs, dark caps
        vec2 q = vUv * vec2(1. / .34, 1. / .4);
        float e = dot(q, q);
        float bodyM = smoothstep(1.05, .9, e);
        float ribs = .75 + .25 * cos(vUv.x * 52.);
        float caps = step(.33, abs(vUv.y)) * step(abs(vUv.x), .16) * step(abs(vUv.y), .44);
        vec3 body = mix(vCol * .55, uCore * 3.2, smoothstep(1., .1, e)) * ribs;
        vec3 c = vCol * halo * (1. - vBody * .55);
        c = mix(c, body + vCol * halo * .35, vBody * bodyM);
        c = mix(c, vec3(.03, .02, .02), vBody * caps);
        if (uIds > .5) { c = vec3(1., .8, .2) * step(r2, .2); }
        gl_FragColor = vec4(c, 1.);
      }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const glowMesh = new THREE.Mesh(gg, glowMat); glowMesh.frustumCulled = false; glowMesh.renderOrder = 40; scene.add(glowMesh);

  // ribbons (threads: additive; ink: hairs + poles)
  const ribbon = (cap, additive, order) => {
    const M = 8; const pos = [];
    for (let i = 0; i <= M; i++) { pos.push(i / M, -1, 0, i / M, 1, 0); }
    const idx = []; for (let i = 0; i < M; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3)); g.setIndex(idx);
    const A = { a: inst(g, 'iA', cap, 3), b: inst(g, 'iB', cap, 3), w: inst(g, 'iW', cap, 3), col: inst(g, 'iCol', cap, 4), bend: inst(g, 'iBend', cap, 2) };
    const mat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
      uniforms: { uRes: U(new THREE.Vector2(W, H)), uPxK: U(pxK), uCov: U(C.threads.coverage), uNear: U(0.1) },
      vertexShader: /* glsl */`
        attribute vec3 iA, iB, iW; attribute vec4 iCol; attribute vec2 iBend;
        uniform vec2 uRes; uniform float uPxK, uCov, uNear;
        varying float vSide; varying vec4 vCol; varying float vT;
        void main(){
          vec4 a = viewMatrix * vec4(iA, 1.), b = viewMatrix * vec4(iB, 1.);
          float nz = -uNear * 2.;
          if ((a.z > nz && b.z > nz) || iCol.a <= 0.) { gl_Position = vec4(2., 2., 2., 1.); return; }
          if (a.z > nz) a = mix(a, b, (a.z - nz) / (a.z - b.z));
          if (b.z > nz) b = mix(b, a, (b.z - nz) / (b.z - a.z));
          vec4 ca = projectionMatrix * a, cb = projectionMatrix * b;
          vec2 sa = ca.xy / ca.w * .5 * uRes, sb = cb.xy / cb.w * .5 * uRes;
          float t = position.x;
          vec2 d = sb - sa; float L = length(d); vec2 dir = L > 1e-4 ? d / L : vec2(1., 0.); vec2 nrm = vec2(-dir.y, dir.x);
          float ppa = projectionMatrix[1][1] * uRes.y * .5 / -a.z, ppb = projectionMatrix[1][1] * uRes.y * .5 / -b.z;
          float wpx = iW.z * mix(ppa, ppb, t);
          float mpx = mix(iW.x, iW.y, t) * uPxK;
          float px = max(wpx, mpx);
          float taper = iBend.y > .5 ? sin(3.1416 * clamp(t * .9 + .1, 0., 1.)) * (.4 + .6 * t) : 1.;
          vec2 sp = mix(sa, sb, t) + nrm * (position.y * px * .5 * taper + iBend.x * sin(3.1416 * t) * L);
          float w = mix(ca.w, cb.w, t), z = mix(ca.z / ca.w, cb.z / cb.w, t);
          gl_Position = vec4(sp / (.5 * uRes) * w, z * w, w);
          vSide = position.y; vT = t;
          vCol = iCol; vCol.a *= mix(1., clamp(wpx / max(mpx, 1e-4), .08, 1.), uCov);
        }`,
      fragmentShader: /* glsl */`
        varying float vSide; varying vec4 vCol; varying float vT;
        void main(){ float e = 1. - smoothstep(.35, 1., abs(vSide)); gl_FragColor = vec4(vCol.rgb * ${additive ? 'vCol.a * e' : '1.'}, ${additive ? '1.' : 'vCol.a * e'}); }`,
      transparent: true, depthWrite: false, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
    });
    const m = new THREE.Mesh(g, mat); m.frustumCulled = false; m.renderOrder = order; scene.add(m);
    let n = 0;
    return {
      mesh: m, mat, reset() { n = 0; },
      push(a, b, wa, wb, ww, col, alpha, bend = 0, taper = 0) {
        if (n >= cap) return;
        A.a.array.set([a.x, a.y, a.z], n * 3); A.b.array.set([b.x, b.y, b.z], n * 3); A.w.array.set([wa, wb, ww], n * 3);
        A.col.array.set([col.r, col.g, col.b, alpha], n * 4); A.bend.array.set([bend, taper], n * 2); n++;
      },
      flush() { for (const k in A) A[k].needsUpdate = true; g.instanceCount = n; },
    };
  };
  const threadR = ribbon(nodes.length * 10 + 64, true, 30);
  const inkR = ribbon(nodes.length * 2 + hairs.length + 64, false, 25);

  // puffs (procedural ink-and-mist clouds)
  const NP = nodes.length * 2 + 16;
  const pg = new THREE.InstancedBufferGeometry();
  pg.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]), 3)); pg.setIndex([0, 1, 2, 0, 2, 3]);
  const pA = { pos: inst(pg, 'iPos', NP, 3), rad: inst(pg, 'iRad', NP, 1), age: inst(pg, 'iAge', NP, 1), seed: inst(pg, 'iSeed', NP, 1), minpx: inst(pg, 'iMinPx', NP, 1) };
  const puffMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    uniforms: { ...shared, uResY: U(H), uPxK: U(pxK), uCol: U(new THREE.Color(C.puffs.color)), uInk: U(new THREE.Color(C.puffs.ink)), uRange: U(1) },
    vertexShader: /* glsl */`
      attribute vec3 iPos; attribute float iRad, iAge, iSeed, iMinPx; uniform float uResY, uPxK;
      varying vec2 vUv; varying float vAge, vSeed; varying vec3 vW;
      void main(){
        vec4 mv = viewMatrix * vec4(iPos, 1.); float depth = max(-mv.z, .01);
        float ppm = projectionMatrix[1][1] * uResY * .5 / depth;
        float r = iRad * (.55 + .7 * sqrt(iAge));
        float px = max(r * ppm, iMinPx * uPxK);
        mv.xy += position.xy * px / ppm;
        vUv = position.xy; vAge = iAge; vSeed = iSeed; vW = iPos;
        gl_Position = projectionMatrix * mv;
        if (iRad <= 0.) gl_Position = vec4(2., 2., 2., 1.);
      }`,
    fragmentShader: /* glsl */`
      ${NOISE}
      uniform vec3 uCol, uInk; uniform float uRange;
      varying vec2 vUv; varying float vAge, vSeed; varying vec3 vW;
      void main(){
        float r = length(vUv);
        float n = fbm3(vec3(vUv * 2.2 + vSeed * 17., vSeed * 5. + vAge * 1.5));
        float edge = .62 + .3 * n;
        float m = smoothstep(edge, edge - .25, r) * smoothstep(1., .7, vAge);
        float core = smoothstep(edge * .65, 0., r);
        float rim = smoothstep(edge - .12, edge - .02, r) * m;
        vec3 c = mix(uCol * (.45 + .55 * uRange), uInk, rim * .8 + core * .15 * (1. - vAge));
        float a = m * (1. - vAge * .6) * (.6 + .4 * n);
        // curl wisps
        float sw = smoothstep(.1, .0, abs(sin(atan(vUv.y, vUv.x) * 3. + r * 9. - vAge * 4. + vSeed * 6.) * r - .1)) * smoothstep(.95, .4, r) * (1. - vAge);
        if (a < .01) discard;
        gl_FragColor = vec4(c, a);
      }`,
    transparent: true, depthWrite: false,
  });
  const puffMesh = new THREE.Mesh(pg, puffMat); puffMesh.frustumCulled = false; puffMesh.renderOrder = 35; scene.add(puffMesh);

  // cards: name slips + seals
  const NK = nodes.length + 32;
  const kg = quad();
  const kA = { pos: inst(kg, 'iPos', NK, 3), size: inst(kg, 'iSize', NK, 2), rect: inst(kg, 'iRect', NK, 4), alpha: inst(kg, 'iAlpha', NK, 1), minpx: inst(kg, 'iMinPx', NK, 1), emit: inst(kg, 'iEmit', NK, 1) };
  const cardMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    uniforms: { ...shared, uTex: U(cards.tex), uResY: U(H), uPxK: U(pxK), uMoon: U(moonC), uAmb: U(ambC), uWarmC: U(warmC) },
    vertexShader: /* glsl */`
      attribute vec3 iPos; attribute vec2 iSize; attribute vec4 iRect; attribute float iAlpha, iMinPx, iEmit; uniform float uResY, uPxK;
      varying vec2 vUv; varying float vA, vE; varying vec3 vW;
      void main(){
        vec4 mv = viewMatrix * vec4(iPos, 1.); float depth = max(-mv.z, .01);
        float ppm = projectionMatrix[1][1] * uResY * .5 / depth;
        float k = max(1., iMinPx * uPxK / max(iSize.y * ppm, 1e-4));
        mv.xy += (position.xy - vec2(.5, 0.)) * iSize * k;
        mv.xyz += normalize(-mv.xyz) * iSize.y * .8;
        vUv = iRect.xy + position.xy * iRect.zw; vA = iAlpha; vE = iEmit; vW = iPos;
        gl_Position = projectionMatrix * mv;
        if (iAlpha <= 0.) gl_Position = vec4(2., 2., 2., 1.);
      }`,
    fragmentShader: /* glsl */`
      uniform sampler2D uTex; uniform vec3 uMoon, uAmb, uWarmC;
      varying vec2 vUv; varying float vA, vE; varying vec3 vW;
      void main(){
        vec4 t = texture2D(uTex, vUv);
        if (t.a < .02) discard;
        vec3 c = t.rgb * (uMoon * .45 + uAmb * .6 + uWarmC * .35) + t.rgb * vE;
        gl_FragColor = vec4(c, t.a * vA);
      }`,
    transparent: true, depthWrite: false,
  });
  const cardMesh = new THREE.Mesh(kg, cardMat); cardMesh.frustumCulled = false; cardMesh.renderOrder = 45; scene.add(cardMesh);

  // ---------------------------------------------------------------- lantern light map (top-down, additive splats)
  const LMS = Math.max(3200, terrain.P.core * 2 + 400), lmc = root.pos;
  const lmBox = new THREE.Vector4(lmc.x - LMS / 2, lmc.z - LMS / 2, 1 / LMS, 0);
  const lmRT = new THREE.WebGLRenderTarget(1024, 1024, { type: THREE.HalfFloatType });
  const lmScene = new THREE.Scene();
  const lmCam = new THREE.OrthographicCamera(-LMS / 2, LMS / 2, LMS / 2, -LMS / 2, 1, 20000);
  lmCam.position.set(lmc.x, 10000, lmc.z); lmCam.up.set(0, 0, -1); lmCam.lookAt(lmc.x, 0, lmc.z); lmCam.updateMatrixWorld(true);
  // map uv = (x - x0)/S, (z - z0)/S; the ortho camera looks down with up = -z, so screen-y = -z: flip handled in shader via uLMBox
  const NL = nodes.length + 8;
  const lg = new THREE.InstancedBufferGeometry();
  lg.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]), 3)); lg.setIndex([0, 1, 2, 0, 2, 3]);
  const lA = { pos: inst(lg, 'iPos', NL, 3), rad: inst(lg, 'iRad', NL, 1), col: inst(lg, 'iCol', NL, 3) };
  const lmMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    uniforms: { uS: U(LMS), uO: U(new THREE.Vector2(lmBox.x, lmBox.y)) },
    vertexShader: /* glsl */`attribute vec3 iPos, iCol; attribute float iRad; uniform float uS; uniform vec2 uO; varying vec2 vUv; varying vec3 vCol; varying float vY;
      void main(){ vY = iPos.y; vec2 c = (iPos.xz - uO) / uS * 2. - 1.; vec2 p = c + position.xy * iRad / uS * 2.; vUv = position.xy; vCol = iCol;
        gl_Position = vec4(p, 0., 1.); if (iRad <= 0.) gl_Position = vec4(2., 2., 2., 1.); }`,
    fragmentShader: /* glsl */`varying vec2 vUv; varying vec3 vCol; varying float vY; void main(){ float r2 = dot(vUv, vUv); float g = exp(-r2 * 4.) * step(r2, 1.);
      gl_FragColor = vec4(vCol * g, dot(vCol, vec3(.3333)) * g * vY / 1000.); }`,
    transparent: true, depthTest: false, depthWrite: false, blending: THREE.CustomBlending, blendEquation: THREE.AddEquation,
    blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
  });
  Object.assign(lmMat, { blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendEquationAlpha: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor, premultipliedAlpha: false });
  const lmMesh = new THREE.Mesh(lg, lmMat); lmMesh.frustumCulled = false; lmScene.add(lmMesh);
  // NB: the splat shader maps (x, z) straight to clip (x, y), so the light map's uv is (x - x0)/S, (z - z0)/S, matching the terrain lookup

  // screen-space (deferred) lantern light on the terrain: each lantern a sphere, lit from the normal-depth buffer
  const lbRT = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: false });
  const lbg = new THREE.InstancedBufferGeometry();
  lbg.setAttribute('position', lg.getAttribute('position')); lbg.setIndex(lg.getIndex());
  lbg.setAttribute('iPos', lA.pos); lbg.setAttribute('iRad', lA.rad); lbg.setAttribute('iCol', lA.col);
  const lbMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    uniforms: { uND: U(null), uRes: U(new THREE.Vector2(W, H)), uP: U(new THREE.Vector2(1, 1)), uNear: U(0.1), uK: U(C.lantern.ground_gain ?? 1) },
    vertexShader: /* glsl */`attribute vec3 iPos, iCol; attribute float iRad; uniform float uNear; varying vec3 vLV, vCol; varying float vR;
      void main(){ vec4 mv = viewMatrix * vec4(iPos, 1.); vLV = mv.xyz; vCol = iCol; vR = iRad;
        if (-mv.z - iRad * 1.5 < uNear * 4.) gl_Position = vec4(position.xy, 0., 1.);
        else { mv.xy += position.xy * iRad * 1.5; gl_Position = projectionMatrix * mv; gl_Position.z = 0.; }
        if (iRad <= 0.) gl_Position = vec4(2., 2., 2., 1.); }`,
    fragmentShader: /* glsl */`uniform sampler2D uND; uniform vec2 uRes, uP; uniform float uK; varying vec3 vLV, vCol; varying float vR;
      void main(){ vec2 uv = gl_FragCoord.xy / uRes; vec4 nd = texture2D(uND, uv); float dep = nd.a; if (dep > 1e6) discard;
        vec2 ndc = uv * 2. - 1.; vec3 vp = vec3(ndc.x / uP.x * dep, ndc.y / uP.y * dep, -dep);
        vec3 L = vLV - vp; float d = length(L); if (d > vR) discard;
        float att = pow(1. - d / vR, 2.); vec3 n = nd.xyz * 2. - 1.;
        float ndl = .3 + .7 * clamp(dot(n, L / max(d, 1e-3)), 0., 1.);
        gl_FragColor = vec4(vCol * att * ndl * uK, 1.); }`,
    transparent: true, depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending });
  const lbMesh = new THREE.Mesh(lbg, lbMat); lbMesh.frustumCulled = false;
  const lbScene = new THREE.Scene(); lbScene.add(lbMesh);

  // ---------------------------------------------------------------- per-frame state
  const LT = C.lantern;
  const lanternCol = new THREE.Color(LT.color);
  const threadCol = new THREE.Color(C.threads.color).multiplyScalar(C.threads.intensity);
  const beadCol = new THREE.Color(C.beads.color).multiplyScalar(C.beads.intensity);
  const hairCol = new THREE.Color(C.hairs.color), glintCol = new THREE.Color(C.hairs.glint).multiplyScalar(C.hairs.glint_i);
  const inkCol = new THREE.Color('#0d0b0a');
  const twoCol = new THREE.Color(C.threads.between_two.color).multiplyScalar(C.threads.between_two.intensity);
  const sealFrame = cards.frames['seal:' + (cfg.text?.seal_done || '讫')], trueFrame = cards.frames['seal:' + (cfg.text?.seal_true || '真')];
  const _v = new THREE.Vector3(), _w = new THREE.Vector3();
  const state = { s: 0 };
  const heroLights = [{ pos: new THREE.Vector3(), i: 0 }, { pos: new THREE.Vector3(), i: 0 }];

  function poseName(n, s) {
    if (n.gen === 0 && s >= cfg.root.sit) return 'sit';
    if (n.blow != null) {
      if (s >= n.blow - Sp.pluck_lead && s < n.blow) return 'pluck';
      if (s >= n.blow && s < n.blow + Sp.blow_hold) return 'blow';
    }
    if (s >= n.land && s < n.land + 2.5 && n.gen > 0) return 'land';
    if (n.seal != null && s >= n.seal - 3.5 && s < n.seal) return 'seal';
    if (s < n.work) return 'stand';
    let k = 0; for (const t of n.switches) if (s >= t) k++;
    if (n.gen === 0) return k % 2 ? 'point' : 'stand';
    return `${n.job}|${k % 2}`;
  }
  const frameOf = (nm) => { if (nm.includes('|')) { const [j, p] = nm.split('|'); return spr.key(j, Number(p)); } return spr.index[nm] ?? spr.index.stand; };
  function lanternI(n, s) {
    if (s < n.land + 0.5) return 0;
    if (n.seal != null && s >= n.seal) return 0;
    let I = (n.gen === G && !n.edge ? LT.interior : 1) + LT.flare * Math.exp(-(s - n.land) / 2);
    for (const t of n.switches) if (s >= t) I += LT.pulse * Math.exp(-(s - t) / 2.5);
    I *= 1 + LT.flicker * Math.sin(s * 0.9 + n.seed * 40) * Math.sin(s * 0.37 + n.seed * 11);
    if (n.seal != null) I *= 1 + 1.5 * smoothstep(n.seal - 2, n.seal, s);       // a last flare as it seals
    return I;
  }

  function update(s, cam, range) {
    state.s = s;
    const camPos = cam.position;
    const camR = _v.setFromMatrixColumn(cam.matrixWorld, 0).clone(); camR.y = 0; camR.normalize();
    const vp = new THREE.Matrix4().multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
    const ppmAt = (p) => { const d = _w.copy(p).applyMatrix4(cam.matrixWorldInverse); return -d.z > 0.05 ? cam.projectionMatrix.elements[5] * H * 0.5 / -d.z : 0; };
    const onScreen = (p, m = 0.1) => { const q = p.clone().applyMatrix4(vp); return q.z < 1 && Math.abs(q.x) < 1 + m && Math.abs(q.y) < 1 + m; };
    let gi = 0, li = 0, pi = 0, ki = 0;
    const glow = (p, rad, minpx, col, k, body = 0) => {
      if (gi >= NG) return;
      gA.pos.array.set([p.x, p.y, p.z], gi * 3); gA.rad.array[gi] = rad; gA.minpx.array[gi] = minpx; gA.col.array.set([col.r * k, col.g * k, col.b * k], gi * 3); gA.body.array[gi] = body; gi++;
    };
    const splat = (p, rad, col, k) => { if (li >= NL) return; lA.pos.array.set([p.x, p.y, p.z], li * 3); lA.rad.array[li] = rad; lA.col.array.set([col.r * k, col.g * k, col.b * k], li * 3); li++; };
    const puff = (p, rad, age, seed, minpx) => { if (pi >= NP) return; pA.pos.array.set([p.x, p.y, p.z], pi * 3); pA.rad.array[pi] = rad; pA.age.array[pi] = age; pA.seed.array[pi] = seed; pA.minpx.array[pi] = minpx; pi++; };
    const card = (p, w, h, fr, alpha, minpx, emit) => { if (ki >= NK) return; kA.pos.array.set([p.x, p.y, p.z], ki * 3); kA.size.array.set([w, h], ki * 2); kA.rect.array.set(fr.rect, ki * 4); kA.alpha.array[ki] = alpha; kA.minpx.array[ki] = minpx; kA.emit.array[ki] = emit; ki++; };
    threadR.reset(); inkR.reset();
    const lanternPos = (n, h, flip) => n.pos.clone().addScaledVector(UP, h * 1.22).addScaledVector(camR, h * 0.42 * flip);
    const TH = C.threads;
    // ---- crowd
    const order = [];
    const pxH = new Float32Array(nodes.length);
    for (const n of crowd) {
      const vis = s >= n.land && (n.seal == null || s < n.seal);
      pxH[n.id] = vis ? n.h * ppmAt(n.pos) : 0;
      if (vis) order.push(n);
    }
    order.sort((a, b) => b.pos.distanceToSquared(camPos) - a.pos.distanceToSquared(camPos));
    let ci = 0;
    for (const n of order) {
      const pop = smoothstep(n.land, n.land + 2, s);
      const lit = lanternI(n, s) > 0 ? 1 : 0;
      cA.pos.array.set([n.pos.x, n.pos.y, n.pos.z], ci * 3);
      cA.size.array[ci] = n.h * (0.6 + 0.4 * pop);
      cA.frame.array[ci] = frameOf(poseName(n, s));
      cA.flip.array[ci] = n.flip;
      cA.alpha.array[ci] = 1;
      cA.warm.array[ci] = lit * Math.min(1.6, lanternI(n, s));
      const ic = new THREE.Color().setHSL(((n.branch ?? 0) / 8 + n.gen * 0.02) % 1, 0.8, 0.35 + 0.1 * n.gen);
      cA.col.array.set([ic.r, ic.g, ic.b], ci * 3);
      ci++;
    }
    cg.instanceCount = ci; for (const k in cA) cA[k].needsUpdate = true;
    // ---- lanterns, poles, light map
    const heroAt = [root, second];
    for (const n of crowd) {
      const I = lanternI(n, s); if (I <= 0) continue;
      const gsc = LT.gen_scale[n.gen] ?? 1;
      const lp = lanternPos(n, n.h, -n.flip);
      glow(lp, LT.radius * gsc, LT.min_px * Math.sqrt(gsc), lanternCol, LT.intensity * I, 1);
      splat(lp, LT.light_radius * gsc, lanternCol, LT.light_gain * Math.min(I, 2.5));
      if (pxH[n.id] > 5) {
        const foot = n.pos.clone().addScaledVector(camR, n.h * 0.42 * -n.flip);
        inkR.push(foot, lp.clone().addScaledVector(UP, n.h * 0.12), 0.0, 0.0, 0.035, inkCol, 0.9 * smoothstep(5, 9, pxH[n.id]));
      }
    }
    // heroes
    const heroOn = [s >= root.land, s >= second.land];
    const flips = [1, -1];
    if (s >= second.land - 3) {
      const a = root.pos.clone().project(cam).x, b = second.pos.clone().project(cam).x;
      flips[0] = a < b ? 1 : -1; flips[1] = -flips[0];
    }
    const heroPose = [poseName(root, s), 'sit'];
    for (let k = 0; k < 2; k++) {
      const hm = heroes[k], u = hm.material.uniforms, who = heroAt[k];
      const on = heroOn[k];
      const pop = on ? smoothstep(who.land, who.land + 2.5, s) : 0;
      u.uAlpha.value = on ? Math.min(1, pop * 1.5) : 0;
      u.uScale.value = 0.75 + 0.25 * pop;
      u.uPos.value.copy(who.pos).addScaledVector(UP, C.ledge_lift); u.uSize.value = who.h; u.uFlip.value = flips[k]; u.uRange.value = range;
      const clipTex = clips.frameFor(k === 0 ? 'root' : 'second', s, heroPose[k], who.h * ppmAt(who.pos));
      const hs = clipTex || spr.hero[heroPose[k]] || spr.hero.stand;
      if (hs.left) u.uFlip.value = -flips[k];
      u.uTex.value = hs.tex; u.uAnchor.value.set(hs.anchor[0], hs.anchor[1], hs.aspect, hs.hfrac);
      const lp = lanternPos(who, who.h, -flips[k]);
      const I = on ? 1 + LT.flare * Math.exp(-(s - who.land) / 2) : 0;
      u.uLPos.value.copy(lp); u.uLI.value = I * LT.hero_light; u.uWarm.value = on ? 1 : 0;
      heroLights[k].pos.copy(lp); heroLights[k].i = I * LT.hero_light;
      if (on) {
        glow(lp, LT.hero_size, LT.min_px * 1.3, lanternCol, LT.intensity * LT.hero_i * I, 1);
        splat(lp, LT.hero_radius, lanternCol, LT.light_gain * 0.22 * I);
        const foot = who.pos.clone().addScaledVector(camR, who.h * 0.42 * -flips[k]);
        inkR.push(foot, lp.clone().addScaledVector(UP, who.h * 0.12), 0.8, 0.8, 0.035, inkCol, 0.95);
      }
    }
    // ---- threads (spawn trails, taut lines, retracting with the hairs)
    for (const c of crowd) {
      if (s < c.depart) continue;
      const p = nodes[c.parent];
      const op = (TH.opacity[c.gen] ?? 0.5);
      let ww = TH.width, mp = TH.min_px;
      if (s < c.land) {
        const u = flightU(c, s), K = TH.segments;
        let prev = flightAt(c, 0);
        for (let i = 1; i <= K; i++) { const q = flightAt(c, u * i / K); threadR.push(prev, q, mp * (0.5 + 0.5 * i / K), mp, ww * (0.3 + 0.7 * i / K), threadCol, op * (0.15 + 0.85 * i / K)); prev = q; }
        continue;
      }
      if (c.seal == null || s < c.seal) {
        const relax = Math.exp(-(s - c.land) / TH.relax);
        const A = p.hand, B = c.hand;
        if (relax > 0.02) {
          const K = TH.segments; let prev = A;
          for (let i = 1; i <= K; i++) { const u = i / K; const q = A.clone().lerp(B, u).addScaledVector(UP, 4 * u * (1 - u) * (c.fl.arc * relax + (TH.bow - TH.sag) * A.distanceTo(B) * (1 - relax))).addScaledVector(c.fl.side, 4 * u * (1 - u) * c.fl.sway * relax); threadR.push(prev, q, mp, mp, ww, threadCol, op); prev = q; }
        } else {
          const bow = (TH.bow - TH.sag) * A.distanceTo(B);
          if (Math.abs(bow) > 0.3) { const K = 4; let prev = A; for (let i = 1; i <= K; i++) { const u = i / K; const q = A.clone().lerp(B, u).addScaledVector(UP, 4 * u * (1 - u) * bow); threadR.push(prev, q, mp, mp, ww, threadCol, op); prev = q; } }
          else threadR.push(A, B, mp, mp, ww, threadCol, op);
        }
        continue;
      }
      // retracting: from the parent's hand to the climbing hair
      const h = hairs[c.ci * HPM];
      if (h && s < h.T[1]) { const q = hairAt(h, s); if (q) threadR.push(p.hand, q, mp, mp, ww, threadCol, op * 0.9); }
      else if (c.gen === 1 && h && s < c.seal + 2.5) {
        // gen-1 threads to the root fade as their hairs leave
        threadR.push(p.hand, c.hand, mp, mp, ww, threadCol, op * (1 - smoothstep(c.seal, c.seal + 2.5, s)));
      }
    }
    // the thread between the two
    if (s >= second.land + 1) {
      const B2 = C.threads.between_two, g = smoothstep(second.land + 1, second.land + 1 + B2.grow, s);
      const A = root.hand, B = second.hand, K = 10; const pts = [];
      for (let i = 0; i <= K; i++) { const u = i / K; pts.push(A.clone().lerp(B, u).addScaledVector(UP, -B2.sag * A.distanceTo(B) * 4 * u * (1 - u))); }
      for (let i = 0; i < K; i++) {
        const u0 = i / K, u1 = (i + 1) / K;
        const vis = (x) => (x <= 0.5 ? x <= g * 0.5 : 1 - x <= g * 0.5);
        if (vis(u0) && vis(u1)) threadR.push(pts[i], pts[i + 1], 1.3, 1.3, 0.012, twoCol, 1);
      }
    }
    // ---- beads down the threads on every beat (parent switch -> child switch)
    for (const c of crowd) {
      const p = nodes[c.parent];
      if (c.seal != null && s >= c.seal) continue;
      for (const B of Wk.beats) {
        const tp = B + p.off, tc = B + c.off;
        if (s < tp || s > tc + 0.5 || tp < p.work || c.land > tp) continue;
        const u = clamp((s - tp) / Math.max(0.5, tc - tp), 0, 1);
        glow(p.hand.clone().lerp(c.hand, ease(u)), C.beads.radius, C.beads.min_px, beadCol, 1 - 0.5 * smoothstep(0.8, 1, u));
      }
    }
    // ---- hairs in flight (spawn) + the root's hair
    for (const n of nodes) {
      if (s < n.depart || s >= n.land + 0.3) continue;
      const u = flightU(n, s), u0 = flightU(n, s - (C.hairs.trail_spawn ?? 1.2));
      const hd = flightAt(n, u), tl = flightAt(n, Math.max(0, u0));
      inkR.push(tl, hd, C.hairs.min_px * 0.5, C.hairs.min_px, C.hairs.width, hairCol, C.hairs.alpha, 0.08, 1);
      glow(hd, 0.35, C.hairs.glint_px * 1.2, glintCol, 1.6);
    }
    // ---- dispersal hairs
    for (const h of hairs) {
      if (s < h.T[0] || s > h.tv1) continue;
      const hd = hairAt(h, s); if (!hd) continue;
      const tl = hairAt(h, Math.max(h.T[0], s - Se.hair_trail)) || hd;
      if (tl.distanceTo(hd) < 0.05) tl.add(new THREE.Vector3(0, -0.3, 0));
      inkR.push(tl, hd, C.hairs.min_px * 0.4, C.hairs.min_px, C.hairs.width, hairCol, C.hairs.alpha, (h.ph - 3) * 0.03, 1);
      const uu = s > h.tv0 ? (s - h.tv0) / (h.tv1 - h.tv0) : 0;
      glow(hd, 0.25, C.hairs.glint_px, glintCol, (1 - smoothstep(0.6, 0.9, uu)) * (h.k === 0 ? 1 : 0.4));
    }
    // ---- puffs: landings, seals
    const PF = C.puffs;
    for (const n of [...nodes]) {
      const a = (s - n.land) / PF.life;
      if (a >= 0 && a < 1) puff(n.pos.clone().addScaledVector(UP, n.h * 0.45), n.h * PF.size, a, n.seed, PF.min_px * (n.gen ? 1 : 1.5));
      if (n.seal != null) { const b = (s - n.seal) / (PF.life * 0.7); if (b >= 0 && b < 1) puff(n.pos.clone().addScaledVector(UP, n.h * 0.6), n.h * PF.seal_size, b, n.seed + 0.5, PF.min_px * 0.5); }
    }
    { const a = (s - second.land) / PF.life; if (a >= 0 && a < 1) puff(second.pos.clone().addScaledVector(UP, second.h * 0.45), second.h * PF.size, a, 0.77, PF.min_px * 1.5); }
    // the palm: a soft pulse each time a hair pours in
    // ---- seals 讫
    const SL = C.seals;
    for (const n of crowd) {
      if (n.seal == null) continue;
      const a = s - n.seal; if (a < 0 || a > SL.life) continue;
      const k = a < 1 ? 1.35 - 0.35 * a : 1;
      const al = 1 - smoothstep(SL.life * 0.5, SL.life, a);
      card(n.pos.clone().addScaledVector(UP, n.h * 0.55).addScaledVector(camR, n.h * 0.15 * n.flip), SL.size * n.h * k, SL.size * n.h * 2 * k, sealFrame, al, SL.min_px * 2, SL.emit * (1 + 2 * Math.exp(-a)));
    }
    // ---- name slips near the closest workers (movement 2)
    const SP = C.slips;
    const win = smoothstep(SP.from, SP.from + SP.fade, s) * (1 - smoothstep(SP.to - SP.fade, SP.to, s));
    if (win > 0) {
      const cand = order.filter((n) => pxH[n.id] > SP.min_px * pxK * 0.6 && onScreen(n.pos, -0.05) && n.work <= s).slice(-SP.n - 3).reverse();
      cand.forEach((n, rank) => {
        const w = (1 - smoothstep(SP.n - 2, SP.n + 1, rank)) * win * smoothstep(SP.min_px * pxK * 0.6, SP.min_px * pxK, pxH[n.id]);
        if (w <= 0.01) return;
        const fr = cards.frames['slip:' + n.job]; if (!fr) return;
        const hh = n.h * SP.size;
        card(n.pos.clone().addScaledVector(UP, n.h * 0.15).addScaledVector(camR, n.h * 0.55 * n.flip), hh * 0.5, hh, fr, w, 0, 0.1);
      });
    }
    // ---- seals 真 for the two
    const sealTimes = [S2.seal_left, S2.seal_right];
    for (let k = 0; k < 2; k++) {
      const t0 = sealTimes[k]; if (s < t0) continue;
      // k = 0 is the screen-left monkey
      const who = (flips[0] === 1) === (k === 0) ? root : second;
      const a = s - t0, sc = a < 2 ? 1.4 - 0.2 * a : 1;
      const side = (k === 0 ? -1 : 1);
      card(who.pos.clone().addScaledVector(UP, who.h * 0.55).addScaledVector(camR, who.h * 0.7 * side), SL.true_size * who.h * sc, SL.true_size * who.h * 2 * sc, trueFrame, smoothstep(0, 1.5, a), SL.min_px * 3, 0.4 + 1.2 * Math.exp(-a / 2));
    }
    for (const k in gA) gA[k].needsUpdate = true; gg.instanceCount = gi;
    for (const k in lA) lA[k].needsUpdate = true; lg.instanceCount = li;
    for (const k in pA) pA[k].needsUpdate = true; pg.instanceCount = pi;
    for (const k in kA) kA[k].needsUpdate = true; kg.instanceCount = ki;
    threadR.flush(); inkR.flush();
    crowdMat.uniforms.uRange.value = range; puffMat.uniforms.uRange.value = range;
  }

  return {
    lightmap: { texture: lmRT.texture, box: lmBox, rt: lmRT }, lmBox, secondPos, second, palm, heroLights, hairs, lastArrival, secondHair,
    update,
    async prepare(s) { await clips.prepare(s); },
    renderLightBuffer(r, cam, nd) {
      lbMat.uniforms.uND.value = nd.texture; lbMat.uniforms.uP.value.set(cam.projectionMatrix.elements[0], cam.projectionMatrix.elements[5]); lbMat.uniforms.uNear.value = cam.near;
      r.setRenderTarget(lbRT); r.setClearColor(0x000000, 0); r.clear(true, false, false); r.render(lbScene, cam);
    },
    lightBuffer: lbRT,
    renderLightmap(r) { r.setRenderTarget(lmRT); r.setClearColor(0x000000, 0); r.clear(true, false, false); r.render(lmScene, lmCam); },
    setGuide(on) { crowdMat.uniforms.uIds.value = on ? -1 : 0; heroes.forEach((h) => { h.material.uniforms.uIds.value = on ? -1 : 0; }); puffMesh.visible = !on; },
    setIds(on) {
      crowdMat.uniforms.uIds.value = on ? 1 : 0; glowMat.uniforms.uIds.value = on ? 1 : 0;
      heroes.forEach((h) => { h.material.uniforms.uIds.value = on ? 1 : 0; });
      threadR.mesh.visible = inkR.mesh.visible = puffMesh.visible = cardMesh.visible = !on;
    },
    sprites: spr, heroes,
  };
}

function deepMergeLocal(a, b) {
  for (const k of Object.keys(b)) {
    if (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k] && typeof a[k] === 'object' && !Array.isArray(a[k])) deepMergeLocal(a[k], b[k]);
    else a[k] = b[k];
  }
  return a;
}

// Huangshan pines on the pillar tops: ink-drawn sprites (procedural atlas), instanced, cylindrical billboards.
import * as THREE from 'three';
import { mulberry32 } from './rng.js';
import { NOISE, FOG } from './glsl.js';

function drawPines(n = 6, S = 256) {
  const c = document.createElement('canvas'); c.width = S * n; c.height = S;
  const g = c.getContext('2d');
  for (let k = 0; k < n; k++) {
    const rnd = mulberry32(100 + k);
    g.save(); g.translate(k * S, 0);
    // crooked trunk
    const pts = [[S * 0.5, S * 0.98]];
    let x = S * 0.5, y = S * 0.98;
    const lean = (rnd() - 0.5) * 0.9;
    for (let i = 0; i < 6; i++) { x += (lean + (rnd() - 0.5) * 0.8) * S * 0.07; y -= S * 0.12; pts.push([x, y]); }
    g.strokeStyle = '#120d0a'; g.lineCap = 'round'; g.lineJoin = 'round';
    for (let i = 0; i < pts.length - 1; i++) { g.lineWidth = S * (0.05 - i * 0.006); g.beginPath(); g.moveTo(...pts[i]); g.lineTo(...pts[i + 1]); g.stroke(); }
    // flat tiers of needles: pads, dark malachite with an ink rim, the Huangshan "welcoming" arm on one side
    const tiers = 3 + Math.floor(rnd() * 3);
    for (let t = 0; t < tiers; t++) {
      const p = pts[Math.min(pts.length - 1, 2 + t)];
      const side = t % 2 ? 1 : -1;
      const w = S * (0.22 + rnd() * 0.2) * (t === 0 ? 1.4 : 1), h = S * (0.06 + rnd() * 0.03);
      const cx = p[0] + side * w * 0.35 * rnd(), cy = p[1];
      g.lineWidth = S * 0.012; g.strokeStyle = '#120d0a';
      g.beginPath(); g.moveTo(p[0], p[1]); g.lineTo(cx + side * w * 0.4, cy - h * 0.3); g.stroke();
      for (let q = 0; q < 9; q++) {
        const ex = cx + (rnd() - 0.5) * w * 1.1, ey = cy + (rnd() - 0.6) * h;
        g.fillStyle = q < 3 ? '#0e1512' : (rnd() < 0.5 ? '#21483a' : '#1d3d4a');
        g.beginPath(); g.ellipse(ex, ey, w * (0.25 + rnd() * 0.18), h * (0.55 + rnd() * 0.3), 0, 0, Math.PI * 2); g.fill();
      }
      // needle ticks along the top
      g.strokeStyle = 'rgba(10,14,12,0.9)'; g.lineWidth = S * 0.006;
      for (let q = 0; q < 26; q++) { const ex = cx + (rnd() - 0.5) * w * 1.1, ey = cy - h * 0.5 + (rnd() - 0.5) * h * 0.5; g.beginPath(); g.moveTo(ex, ey); g.lineTo(ex + (rnd() - 0.5) * 6, ey - 6 - rnd() * 6); g.stroke(); }
    }
    g.restore();
  }
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { tex, n };
}

export function makePines(cfg, { scene, terrain, shared, lm }) {
  const P = cfg.pines, rnd = mulberry32(P.seed);
  const { tex, n } = drawPines();
  const pos = [], sz = [], fr = [];
  const core = terrain.P.core;
  let tries = 0;
  while (pos.length < P.count && tries < P.count * 60) {
    tries++;
    const x = terrain.ledge.x + (rnd() * 2 - 1) * core, z = terrain.ledge.z + (rnd() * 2 - 1) * core;
    const y = terrain.height(x, z);
    if (y < P.min_y) continue;
    const nn = terrain.normal(x, z, 1.5);
    if (nn.y < P.min_up) continue;
    // rims of tops prefer pines (the edge of a pillar), and keep the ledge clear
    const rim = terrain.normal(x, z, 9).y;
    if (rnd() > 0.35 + 0.65 * (1 - rim)) continue;
    if (Math.hypot(x - terrain.ledge.x, z - terrain.ledge.z) < 14) continue;
    pos.push(x, y - 0.5, z); sz.push(P.size[0] + (P.size[1] - P.size[0]) * rnd() ** 1.5); fr.push(Math.floor(rnd() * n) + (rnd() < 0.5 ? 0.5 : 0));
  }
  const g = new THREE.InstancedBufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([-0.5, 0, 0, 0.5, 0, 0, 0.5, 1, 0, -0.5, 1, 0]), 3));
  g.setIndex([0, 1, 2, 0, 2, 3]);
  g.setAttribute('iPos', new THREE.InstancedBufferAttribute(new Float32Array(pos), 3));
  g.setAttribute('iSize', new THREE.InstancedBufferAttribute(new Float32Array(sz), 1));
  g.setAttribute('iFrame', new THREE.InstancedBufferAttribute(new Float32Array(fr), 1));
  g.instanceCount = sz.length;
  const mat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
    uniforms: { ...shared, uTex: { value: tex }, uN: { value: n }, uRange: { value: 1 }, uLM: { value: lm.texture }, uLMBox: { value: lm.box },
      uMoon: { value: new THREE.Color(cfg.look.moon_col) }, uAmb: { value: new THREE.Color(cfg.look.amb_top) } },
    vertexShader: /* glsl */`
      attribute vec3 iPos; attribute float iSize; attribute float iFrame;
      varying vec2 vUv; varying vec3 vW;
      void main(){
        vec3 camR = vec3(viewMatrix[0][0], viewMatrix[1][0], viewMatrix[2][0]);
        vec3 r = normalize(vec3(camR.x, 0., camR.z) + 1e-5);
        float fl = fract(iFrame) > .25 ? -1. : 1.;
        vec3 w = iPos + r * position.x * iSize * fl + vec3(0., 1., 0.) * position.y * iSize;
        vW = w; vUv = vec2((floor(iFrame) + position.x + .5) , position.y);
        gl_Position = projectionMatrix * viewMatrix * vec4(w, 1.);
      }`,
    fragmentShader: /* glsl */`
      ${NOISE}
      ${FOG}
      uniform sampler2D uTex, uLM; uniform float uN, uRange; uniform vec4 uLMBox; uniform vec3 uMoon, uAmb;
      varying vec2 vUv; varying vec3 vW;
      void main(){
        vec4 t = texture2D(uTex, vec2(vUv.x / uN, 1. - vUv.y));
        if (t.a < .4) discard;
        vec2 lmuv = (vW.xz - uLMBox.xy) * uLMBox.z;
        vec4 lm4 = (lmuv.x > 0. && lmuv.x < 1. && lmuv.y > 0. && lmuv.y < 1.) ? texture2D(uLM, lmuv) : vec4(0.);
          float lmw = dot(lm4.rgb, vec3(.3333)); float lmY = lmw > 1e-4 ? lm4.a * 1000. / lmw : vW.y;
          vec3 lmv = lm4.rgb * exp(-max(0., abs(vW.y - lmY) - 3.) / 20.);
        vec3 c = (t.rgb * 1.6 + vec3(.02, .05, .05)) * (uMoon * .8 + uAmb * 1.2) * uRange + t.rgb * lmv * 2.;
        c = applyFog(c, vW, dot(lmv, vec3(.33)));
        gl_FragColor = vec4(c, 1.);
      }`,
  });
  const mesh = new THREE.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 1;
  scene.add(mesh);
  return { mesh, update(s, range) { mat.uniforms.uRange.value = range; }, count: sz.length };
}

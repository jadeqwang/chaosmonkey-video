// Layered mist planes between the ridges: bare paper tone, soft against the terrain (depth fade), drifting,
// lit faintly by the moon and warmly by lantern pools; optional video frames (PNG sequence) as the density field.
import * as THREE from 'three';
import { NOISE } from './glsl.js';

export async function makeMist(cfg, { scene, shared, nd, W, H, lm }) {
  const M = cfg.mist;
  let vid = null;
  if (M.video_frames && M.video_count) {
    vid = { dir: M.video_frames, n: M.video_count, cache: new Map(), tex: new THREE.Texture() };
    vid.tex.wrapS = vid.tex.wrapT = THREE.RepeatWrapping;
  }
  const mats = [];
  const group = new THREE.Group();
  M.layers.forEach((ly, i) => {
    const mat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, depthTest: true, side: THREE.DoubleSide,
      uniforms: {
        ...shared, uND: { value: nd.texture }, uRes: { value: new THREE.Vector2(W, H) }, uDen: { value: ly.density },
        uScale: { value: ly.scale }, uSpeed: { value: new THREE.Vector2(...ly.speed) }, uSoft: { value: ly.soft }, uSeed: { value: i * 13.7 },
        uCol: { value: new THREE.Color(M.color) }, uLit: { value: M.lit }, uRange: { value: 1 }, uLM: { value: lm.texture }, uLMBox: { value: new THREE.Vector4() },
        uVid: { value: vid ? vid.tex : null }, uFade: { value: new THREE.Vector2(...(ly.fade || [2800, 4600])) }, uThr: { value: ly.thr ?? 0.0 }, uVidOn: { value: vid ? 1 : 0 }, uY: { value: ly.y },
      },
      vertexShader: /* glsl */`varying vec3 vW; varying float vVZ;
        void main(){ vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; vec4 mv = viewMatrix * w; vVZ = -mv.z; gl_Position = projectionMatrix * mv; }`,
      fragmentShader: /* glsl */`
        ${NOISE}
        uniform vec3 uCamPos; uniform vec3 uHazeCol; uniform float uHazeDist, uHazeMax;
        float hazeAmt(vec3 wp){ float dist = length(wp - uCamPos); float H = 700.; float y0 = max(wp.y, 0.), y1 = max(uCamPos.y, 0.);
          float k = abs(y1 - y0) < 1. ? exp(-y0 / H) : H * (exp(-y0 / H) - exp(-y1 / H)) / (y1 - y0); return uHazeMax * (1. - exp(-dist / uHazeDist * abs(k) * 1.4)); }
        uniform sampler2D uND, uLM, uVid; uniform vec2 uRes, uSpeed; uniform vec2 uFade; uniform float uThr; uniform float uDen, uScale, uSoft, uSeed, uLit, uRange, uVidOn, uS, uY;
        uniform vec3 uCol; uniform vec4 uLMBox;
        varying vec3 vW; varying float vVZ;
        void main(){
          vec2 q = vW.xz * uScale + uSpeed * uS * .01 + uSeed;
          float far = smoothstep(2500., 9000., length(vW - uCamPos));
          float fwq = length(fwidth(q));
          float det = 1. - smoothstep(.015, .08, fwq);
          float n = fbm3(vec3(q, uS * .004 + uSeed)) + det * .12 * snoise(vec3(q * 9.1, uS * .01 + uSeed));
          float n2 = fbm3(vec3(q * 3.1, uS * .01)) * (1. - smoothstep(.01, .05, fwq));
          float d = smoothstep(uThr, uThr + .38, n + .3 * n2);
          d *= .75 + .25 * det * smoothstep(-.3, .5, snoise(vec3(q * 7.3, uSeed)));
          if (uVidOn > .5) d *= texture2D(uVid, vW.xz * uScale * .5).r * 1.4;
          // soft against the ground
          float sd = texture2D(uND, gl_FragCoord.xy / uRes).a;
          float soft = smoothstep(0., uSoft, sd - vVZ);
          float near = smoothstep(20., 300., vVZ);
          float edge = 1. - smoothstep(uFade.x, uFade.y, length(vW.xz));
          float a = d * uDen * soft * near * edge;
          // grazing view: planes thicken toward the horizon, like real banks
          vec3 v = normalize(vW - uCamPos);
          a *= mix(1., 1.8, 1. - abs(v.y)) * mix(1., .5, smoothstep(.4, .9, abs(v.y)));
          vec2 lmuv = (vW.xz - uLMBox.xy) * uLMBox.z;
          vec4 lm4 = (lmuv.x > 0. && lmuv.x < 1. && lmuv.y > 0. && lmuv.y < 1.) ? texture2D(uLM, lmuv) : vec4(0.);
          float lmw = dot(lm4.rgb, vec3(.3333)); float lmY = lmw > 1e-4 ? lm4.a * 1000. / lmw : vW.y;
          vec3 lmv = lm4.rgb * exp(-max(0., abs(vW.y - lmY) - 3.) / 20.);
          vec3 c = uCol * (uLit + (1. - uLit) * (.55 + .45 * n2)) * mix(.25, 1., uRange) + lmv * .5;
          float dist = length(vW - uCamPos);
          c = mix(c, uHazeCol, hazeAmt(vW));
          gl_FragColor = vec4(c, clamp(a, 0., .9));
        }`,
    });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(ly.size, ly.size, 1, 1).rotateX(-Math.PI / 2), mat);
    m.position.y = ly.y; m.frustumCulled = false; m.renderOrder = 5 + i;
    mats.push(mat); group.add(m);
  });
  scene.add(group);
  return {
    group,
    async prepare(s) {
      if (!vid) return;
      const k = 1 + (Math.floor(s) % vid.n);
      if (!vid.cache.has(k)) {
        const img = new Image(); img.src = `/${vid.dir}/${String(k).padStart(4, '0')}.png`; await img.decode(); vid.cache.set(k, img);
      }
      vid.tex.image = vid.cache.get(k); vid.tex.needsUpdate = true;
    },
    update(s, cam, range) {
      for (const m of mats) { m.uniforms.uRange.value = range; m.uniforms.uLMBox.value.copy(lm.box); }
      // draw far-to-near relative to the camera height
      group.children.forEach((m, i) => { m.renderOrder = 5 + (cam.position.y > m.position.y ? i : 20 - i); });
    },
  };
}

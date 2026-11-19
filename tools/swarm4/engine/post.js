// Post: bloom, tone map, grade, vignette, paper grain fixed to the screen, cheap ink bleed. Plus depth/ids output.
import * as THREE from 'three';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { NOISE } from './glsl.js';

export function makePost(renderer, W, H, P) {
  const hdr = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4, depthBuffer: true });
  const nd = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true });
  const acc = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), P.bloom, P.bloom_radius, P.bloom_threshold);
  const fin = new FullScreenQuad(new THREE.ShaderMaterial({
    uniforms: {
      tHdr: { value: hdr.texture }, uRes: { value: new THREE.Vector2(W, H) }, uExpo: { value: P.exposure },
      uGrain: { value: P.paper_grain }, uVig: { value: P.vignette }, uPaper: { value: new THREE.Color(P.paper_tint) },
      uSat: { value: P.saturation }, uLift: { value: new THREE.Color(P.lift) }, uSeed: { value: P.grain_seed || 3 }, uBleed: { value: P.ink_bleed },
      uFade: { value: 1 },
    },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
    fragmentShader: /* glsl */`
      ${NOISE}
      uniform sampler2D tHdr; uniform vec2 uRes; uniform float uExpo, uGrain, uVig, uSat, uSeed, uBleed, uFade; uniform vec3 uPaper, uLift;
      varying vec2 vUv;
      vec3 tone(vec3 x){ x *= uExpo; vec3 a = x * (2.51 * x + .03), b = x * (2.43 * x + .59) + .14; return clamp(a / b, 0., 1.); }
      void main(){
        vec2 px = 1. / uRes;
        vec3 c = texture2D(tHdr, vUv).rgb;
        // ink bleed: dark values creep outward a little, along the paper fibres
        float fib = snoise(vec3(vUv * uRes * vec2(.02, .09), uSeed));
        vec3 mn = c;
        for (int k = 0; k < 4; k++) { float a = float(k) * 1.5708 + fib; mn = min(mn, texture2D(tHdr, vUv + vec2(cos(a), sin(a)) * px * 1.3).rgb); }
        c = mix(c, mn, uBleed * smoothstep(.12, .0, dot(mn, vec3(.33))));
        vec3 t = tone(c);
        float l = dot(t, vec3(.299, .587, .114));
        t = mix(vec3(l), t, uSat);
        t = uLift + t * (1. - uLift);
        // paper: fixed to the screen. Fibres + tooth + a mottled sizing
        vec2 q = vUv * uRes / 1080.;
        float tooth = snoise(vec3(q * 900., uSeed)) * .5 + snoise(vec3(q * 380., uSeed + 4.)) * .5;
        float fibre = snoise(vec3(q.x * 60., q.y * 520., uSeed + 9.)) * snoise(vec3(q.x * 210., q.y * 40., uSeed + 2.));
        float mottle = fbm3(vec3(q * 3.5, uSeed + 1.));
        float paper = 1. + uGrain * (tooth * .55 + fibre * .5 + mottle * .7);
        t *= paper;
        t = mix(t, t * uPaper, .5);
        float vig = 1. - uVig * smoothstep(.35, 1.05, length((vUv - .5) * vec2(1.25, 1.)));
        t *= vig * uFade;
        gl_FragColor = vec4(pow(t, vec3(1.)), 1.);
      }`,
    depthWrite: false, depthTest: false,
  }));
  const dump = new FullScreenQuad(new THREE.ShaderMaterial({
    uniforms: { tND: { value: nd.texture }, uFar: { value: 6000 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
    fragmentShader: `uniform sampler2D tND; uniform float uFar; varying vec2 vUv;
      void main(){ float d = texture2D(tND, vUv).a; float v = 1. - clamp(log(1. + d) / log(1. + uFar), 0., 1.); gl_FragColor = vec4(vec3(v), 1.); }`,
  }));
  const copy = new FullScreenQuad(new THREE.ShaderMaterial({
    uniforms: { t: { value: acc.texture }, k: { value: 1 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
    fragmentShader: 'uniform sampler2D t; uniform float k; varying vec2 vUv; void main(){ gl_FragColor = vec4(texture2D(t, vUv).rgb * k, 1.); }',
    depthTest: false, depthWrite: false,
  }));
  return {
    hdr, nd, bloom, fin, dump, copy, acc,
    finish(toAcc, weight) {     // hdr -> bloom -> screen (or into the motion-blur accumulator)
      if (P.bloom > 0) bloom.render(renderer, null, hdr, 0, false);
      if (toAcc) {
        renderer.setRenderTarget(acc);
        fin.material.blending = THREE.AdditiveBlending; fin.material.transparent = true;
        fin.material.uniforms.uFade.value = weight;
        fin.render(renderer);
        fin.material.blending = THREE.NormalBlending; fin.material.transparent = false; fin.material.uniforms.uFade.value = 1;
      } else { renderer.setRenderTarget(null); fin.render(renderer); }
    },
  };
}

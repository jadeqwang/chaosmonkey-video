// Materials: terrain (青绿 night, ink contour, gold line, lantern light), normal-depth pass, sky.
import * as THREE from 'three';
import { NOISE, FOG } from './glsl.js';

export const col = (c) => new THREE.Color(c);
const v3 = (a) => new THREE.Vector3(...a);

export function fogUniforms(L) {
  return {
    uHazeCol: { value: col(L.haze_col) }, uHazeDist: { value: L.haze_dist }, uHazeMax: { value: L.haze_max },
    uMistCol: { value: col(L.mist_col) }, uMistY: { value: L.mist_y }, uMistH: { value: L.mist_h }, uMistAmt: { value: L.mist_amt },
    uS: { value: 0 }, uCamPos: { value: new THREE.Vector3() },
  };
}

const MAXPROJ = 4;
export function terrainMaterial(L, shared) {
  const u = {
    ...shared,
    uLightDir: { value: v3(L.light_dir).normalize() }, uMoonCol: { value: col(L.moon_col) }, uMoonI: { value: L.moon_i },
    uAmbTop: { value: col(L.amb_top) }, uAmbLow: { value: col(L.amb_low) },
    uAzur: { value: col(L.azurite) }, uMala: { value: col(L.malachite) }, uOchre: { value: col(L.ochre) }, uOchreD: { value: col(L.ochre_dark) },
    uInkCol: { value: col(L.ink) }, uGoldCol: { value: col(L.gold) }, uLantCol: { value: col(L.lantern_col) },
    uLM: { value: null }, uLB: { value: null }, uLMBox: { value: new THREE.Vector4() }, uLMGain: { value: L.lantern_ground },
    uND: { value: null }, uRes: { value: new THREE.Vector2(1, 1) }, uInkW: { value: L.ink_weight }, uGold: { value: L.gold_strength },
    uRange: { value: 1 }, uOutline: { value: 0 }, uCunAmt: { value: L.cun }, uGreenAmt: { value: L.green },
    uHeights: { value: new THREE.Vector2(L.valley_y, L.peak_y) }, uIds: { value: 0 }, uGuide: { value: 0 }, uPExpo: { value: 1.15 },
    uHLP: { value: [new THREE.Vector3(), new THREE.Vector3()] }, uHLI: { value: [0, 0] }, uHLR: { value: 6 },
    uPT0: { value: null }, uPD0: { value: null }, uPM0: { value: new THREE.Matrix4() }, uPP0: { value: new THREE.Vector3() }, uPA0: { value: 0 }, uPT1: { value: null }, uPD1: { value: null }, uPM1: { value: new THREE.Matrix4() }, uPP1: { value: new THREE.Vector3() }, uPA1: { value: 0 }, uPT2: { value: null }, uPD2: { value: null }, uPM2: { value: new THREE.Matrix4() }, uPP2: { value: new THREE.Vector3() }, uPA2: { value: 0 }, uPT3: { value: null }, uPD3: { value: null }, uPM3: { value: new THREE.Matrix4() }, uPP3: { value: new THREE.Vector3() }, uPA3: { value: 0 }, 
  };
  return new THREE.ShaderMaterial({
    uniforms: u,
    vertexShader: /* glsl */`
      varying vec3 vW; varying vec3 vN; varying float vVZ;
      void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; vN = normalize(mat3(modelMatrix) * normal);
        vec4 mv = viewMatrix * w; vVZ = -mv.z; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: /* glsl */`
      precision highp float;
      ${NOISE}
      ${FOG}
      uniform vec3 uLightDir, uMoonCol, uAmbTop, uAmbLow, uAzur, uMala, uOchre, uOchreD, uInkCol, uGoldCol, uLantCol;
      uniform float uIds, uGuide, uPExpo; uniform float uMoonI, uLMGain, uInkW, uGold, uRange, uOutline, uCunAmt, uGreenAmt;
      uniform vec3 uHLP[2]; uniform float uHLI[2]; uniform float uHLR;
      uniform sampler2D uLM; uniform sampler2D uLB; uniform vec4 uLMBox; uniform sampler2D uND; uniform vec2 uRes; uniform vec2 uHeights;
      uniform sampler2D uPT0, uPD0; uniform mat4 uPM0; uniform vec3 uPP0; uniform float uPA0;
      uniform sampler2D uPT1, uPD1; uniform mat4 uPM1; uniform vec3 uPP1; uniform float uPA1;
      uniform sampler2D uPT2, uPD2; uniform mat4 uPM2; uniform vec3 uPP2; uniform float uPA2;
      uniform sampler2D uPT3, uPD3; uniform mat4 uPM3; uniform vec3 uPP3; uniform float uPA3;
      varying vec3 vW; varying vec3 vN; varying float vVZ;
      vec4 nd(vec2 o){ return texture2D(uND, (gl_FragCoord.xy + o) / uRes); }
      void main(){
        vec3 n = normalize(vN);
        vec3 p = vW;
        float up = n.y;
        float hN = clamp((p.y - uHeights.x) / (uHeights.y - uHeights.x), 0., 1.);
        // ---- albedo: ochre underpaint, mineral green/blue laid on the upward faces, graded down the walls
        float nLo = fbm3(p * .009);
        float nMid = fbm3(p * .04 + 3.1);
        float nHi = snoise(p * .19);
        float nFine = snoise(p * .9);
        vec3 ochre = mix(uOchreD, uOchre, clamp(.45 + .5 * nLo + .3 * nMid + .3 * (up - .2), 0., 1.));
        float topness = up + .25 * nMid + .08 * nHi;
        // 青绿: mineral colour over most of the rock, graded by height; ochre at the feet and in the joints
        float gH = smoothstep(.0, .42, hN + .22 * nLo + .2 * (up - .3));
        float gm = max(gH * .8, smoothstep(.42, .72, topness) * smoothstep(-.1, .15, hN));
        float tongue = smoothstep(-.1, .45, fbm3(vec3(p.x * .035, p.y * .0045, p.z * .035) + 7.));
        gm *= mix(.55, 1., tongue);
        gm = clamp(gm * uGreenAmt, 0., 1.);
        vec3 green = mix(uMala, uAzur, smoothstep(.3, .8, hN + .3 * nLo + .2 * nMid));
        green *= .8 + .35 * smoothstep(-.5, .6, nMid) + .08 * nFine;
        vec3 alb = mix(ochre, green, gm);
        // 皴: texture strokes as iso-lines of stretched noise fields (pixel-width, antialiased), broken into
        // segments; coarse strokes read far, fine ones near
        float steep = 1. - smoothstep(.3, .8, up);
        float strokes = 0.;
        {
          float f = fbm3(vec3(p.x * .022, p.y * .0042, p.z * .022)) * 7. + nMid * .5;
          float fw = fwidth(f);
          float dd = abs(fract(f + .5) - .5) / max(fw, 1e-4);
          float seg = smoothstep(-.1, .35, snoise(vec3(p.x * .05, p.y * .012, p.z * .05) + 4.));
          strokes = max(strokes, (1. - smoothstep(.4, 1.6, dd)) * seg * (1. - smoothstep(.12, .35, fw)));
          float f2 = snoise(vec3(p.x * .12, p.y * .025, p.z * .12)) * 4. + nHi * .4;
          float fw2 = fwidth(f2);
          float dd2 = abs(fract(f2 + .5) - .5) / max(fw2, 1e-4);
          float seg2 = smoothstep(.0, .4, snoise(vec3(p.x * .2, p.y * .05, p.z * .2) + 9.));
          strokes = max(strokes, .8 * (1. - smoothstep(.3, 1.3, dd2)) * seg2 * (1. - smoothstep(.15, .4, fw2)));
          // axe-cut dark facets (wash strokes) on the walls
          float ax = smoothstep(.25, .5, fbm3(vec3(p.x * .06, p.y * .014, p.z * .06) + vec3(0., nMid, 0.)));
          alb = mix(alb, alb * .55, ax * steep * .6 * uCunAmt);
        }
        alb = mix(alb, uInkCol, clamp(strokes * (.35 + .65 * steep), 0., 1.) * .8 * uCunAmt);
        // 苔点 moss dots on the tops (size held in pixels)
        float dots = smoothstep(25., 90., vVZ) * smoothstep(.62, .74, snoise(p * 1.6)) * (1. - smoothstep(.05, .3, length(fwidth(p * 1.6)))) * smoothstep(.55, .85, up) * smoothstep(.15, .45, hN);
        alb = mix(alb, uInkCol, dots * .8 * uCunAmt);
        // pine clusters on the tops: dark green blotches that still read from the air
        float pinesM = smoothstep(.5, .68, snoise(p * .085) + .25 * snoise(p * .3)) * smoothstep(.72, .92, up) * smoothstep(.2, .45, hN);
        alb = mix(alb, mix(uMala * .35, uInkCol, .4), pinesM * .85);
        // ---- light: washes, not gradients. A cool moon in two or three soft bands, sky fill, lantern pools
        float lam = clamp(dot(n, uLightDir) * .75 + .25, 0., 1.);
        float bands = .18 + .45 * smoothstep(.28 - .1 * nMid, .42 + .08 * nMid, lam) + .37 * smoothstep(.62 - .1 * nLo, .8, lam);
        vec3 amb = mix(uAmbLow, uAmbTop, .5 + .5 * up);
        vec2 lmuv = (p.xz - uLMBox.xy) * uLMBox.z;
        vec4 lm4 = (lmuv.x > 0. && lmuv.x < 1. && lmuv.y > 0. && lmuv.y < 1.) ? texture2D(uLM, lmuv) : vec4(0.);
        float lmw = dot(lm4.rgb, vec3(.3333));
        float lmY = lmw > 1e-4 ? lm4.a * 1000. / lmw : p.y;
        vec3 lmv = texture2D(uLB, gl_FragCoord.xy / uRes).rgb;
        // the two hero lanterns on the ledge: real point lights
        for (int k = 0; k < 2; k++) {
          vec3 dl = uHLP[k] - p; float d2 = dot(dl, dl);
          float fall = uHLI[k] / (1. + d2 / (uHLR * uHLR) * 4.) * smoothstep(60. * uHLR, 0., d2);
          lmv += vec3(1., .6, .3) * fall * (.35 + .65 * clamp(dot(n, normalize(dl)), 0., 1.));
        }
        float lmI = dot(lmv, vec3(.33));
        vec3 lit = alb * (uMoonCol * bands * uMoonI + amb) * uRange;
        lit += alb * lmv * uLMGain * (.5 + .5 * clamp(up + .4, 0., 1.)) + lmv * uLMGain * .05;
        // ---- ink contour + gold line (screen-space, from the normal-depth pass)
        float d0 = vVZ;
        vec3 n0 = nd(vec2(0.)).xyz * 2. - 1.;
        float wob = .45 + 1.1 * smoothstep(-.5, .6, snoise(p * .015 + 11.) + .3 * nHi);
        float r1 = max(.7, uInkW * wob);
        float ink = 0., crease = 0., gold = 0., wash = 0.;
        float thr = .01 + .025 * smoothstep(50., 3000., d0);
        for (int k = 0; k < 8; k++) {
          float a = float(k) * .785398;
          vec2 dir = vec2(cos(a), sin(a));
          vec4 s1 = nd(dir * r1);
          vec4 s1b = nd(-dir * r1);
          float back = max(s1.a, s1b.a);
          float lap = abs(s1.a + s1b.a - 2. * d0) / d0;
          if (back > d0 * (1. + thr) && lap > thr && back - d0 > .35) ink = 1.;
          crease = max(crease, smoothstep(.45, .1, dot(n0, s1.xyz * 2. - 1.)));
          vec4 s2 = nd(dir * (r1 + 1.6));
          float lap2 = abs(s2.a + nd(-dir * (r1 + 1.6)).a - 2. * d0) / d0;
          if (s2.a > d0 * (1. + thr * 2.) && lap2 > thr * 2. && s2.a - d0 > .8) gold = 1.;
          vec4 s3 = nd(dir * r1 * 6.);
          float lap3 = abs(s3.a + nd(-dir * r1 * 6.).a - 2. * d0) / d0;
          if (s3.a > d0 * (1. + thr * 2.) && lap3 > thr * 3. && s3.a - d0 > .8) wash += .125;
        }
        float distK = 1. - .55 * smoothstep(500., 6000., d0);
        float lineA = max(ink, crease * .5) * distK;
        // gold (金碧): thin, just inside the ink contour of the tops, where light falls (moon a little, lanterns a lot)
        float goldLit = clamp(.35 * bands * uMoonI * uRange + lmI * 2.5, 0., 1.8);
        gold *= smoothstep(.15, .55, up + .2 * nMid) * (1. - ink);
        vec3 c = lit;
        c = mix(c, c * .6, wash * .45 * distK);                       // ink bleed: a pale wash beside the line
        c += uGoldCol * gold * goldLit * uGold * (.35 + .65 * wob);
        c = mix(c, uInkCol, lineA * .9);
        // outline mode (the dark range at the end): keep a faint moonlit contour only
        c += uGoldCol * ink * uOutline * .05;
        // painted plates projected back onto the geometry (phase 2): blended by facing and visibility
        vec3 pc = vec3(0.); float pw = 0.; {
        if (uPA0 > 0.) {
          vec4 q = uPM0 * vec4(p, 1.);
          if (q.w > 0.) { vec2 uv = q.xy / q.w * .5 + .5;
            if (uv.x > 0. && uv.x < 1. && uv.y > 0. && uv.y < 1.) {
              float dp = texture2D(uPD0, uv).a; float dz = q.w;
              float vis = 1. - smoothstep(.01, .03, (dz - dp) / max(dp, 1.));
              vec3 tp = normalize(uPP0 - p);
              float w = vis * pow(clamp(dot(n, tp), 0., 1.), 1.5) * smoothstep(0., .05, min(min(uv.x, 1. - uv.x), min(uv.y, 1. - uv.y))) * uPA0;
              pc += texture2D(uPT0, uv).rgb * w; pw += w; } } }
        if (uPA1 > 0.) {
          vec4 q = uPM1 * vec4(p, 1.);
          if (q.w > 0.) { vec2 uv = q.xy / q.w * .5 + .5;
            if (uv.x > 0. && uv.x < 1. && uv.y > 0. && uv.y < 1.) {
              float dp = texture2D(uPD1, uv).a; float dz = q.w;
              float vis = 1. - smoothstep(.01, .03, (dz - dp) / max(dp, 1.));
              vec3 tp = normalize(uPP1 - p);
              float w = vis * pow(clamp(dot(n, tp), 0., 1.), 1.5) * smoothstep(0., .05, min(min(uv.x, 1. - uv.x), min(uv.y, 1. - uv.y))) * uPA1;
              pc += texture2D(uPT1, uv).rgb * w; pw += w; } } }
        if (uPA2 > 0.) {
          vec4 q = uPM2 * vec4(p, 1.);
          if (q.w > 0.) { vec2 uv = q.xy / q.w * .5 + .5;
            if (uv.x > 0. && uv.x < 1. && uv.y > 0. && uv.y < 1.) {
              float dp = texture2D(uPD2, uv).a; float dz = q.w;
              float vis = 1. - smoothstep(.01, .03, (dz - dp) / max(dp, 1.));
              vec3 tp = normalize(uPP2 - p);
              float w = vis * pow(clamp(dot(n, tp), 0., 1.), 1.5) * smoothstep(0., .05, min(min(uv.x, 1. - uv.x), min(uv.y, 1. - uv.y))) * uPA2;
              pc += texture2D(uPT2, uv).rgb * w; pw += w; } } }
        if (uPA3 > 0.) {
          vec4 q = uPM3 * vec4(p, 1.);
          if (q.w > 0.) { vec2 uv = q.xy / q.w * .5 + .5;
            if (uv.x > 0. && uv.x < 1. && uv.y > 0. && uv.y < 1.) {
              float dp = texture2D(uPD3, uv).a; float dz = q.w;
              float vis = 1. - smoothstep(.01, .03, (dz - dp) / max(dp, 1.));
              vec3 tp = normalize(uPP3 - p);
              float w = vis * pow(clamp(dot(n, tp), 0., 1.), 1.5) * smoothstep(0., .05, min(min(uv.x, 1. - uv.x), min(uv.y, 1. - uv.y))) * uPA3;
              pc += texture2D(uPT3, uv).rgb * w; pw += w; } } }
        c = applyFog(c, p, lmI);
        if (pw > 0.) { vec3 y = clamp(pc / pw, 0., .98); vec3 A = 2.51 - 2.43 * y, B = .03 - .59 * y, Cc = -.14 * y;
          vec3 x = (-B + sqrt(B * B - 4. * A * Cc)) / (2. * A) / uPExpo;      // undo the display tone curve: plates are display-referred
          c = mix(c, x, clamp(pw, 0., 1.)); } }
        if (uGuide > .5) { float lg = .3 + .7 * clamp(dot(n, uLightDir), 0., 1.); c = mix(vec3(.72 * lg + .08 * up), vec3(0.), lineA * .95); }
        if (uIds > .5) c = vec3(.25 + .5 * clamp(dot(n, normalize(vec3(.3, 1., .4))), 0., 1.));
        gl_FragColor = vec4(c, 1.);
      }`,
  });
}

// normal (view space, packed) + linear depth (metres) for the edge detector
export function ndMaterial() {
  return new THREE.ShaderMaterial({
    vertexShader: /* glsl */`varying vec3 vN; varying float vVZ;
      void main(){ vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position,1.); vVZ = -mv.z; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: /* glsl */`varying vec3 vN; varying float vVZ;
      void main(){ gl_FragColor = vec4(normalize(vN) * .5 + .5, vVZ); }`,
  });
}

export function skyMaterial(L) {
  return new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: {
      uZen: { value: col(L.sky_zenith) }, uHor: { value: col(L.sky_horizon) }, uMoonDir: { value: v3(L.moon_dir).normalize() },
      uMoonCol: { value: col(L.moon_disc) }, uHaloI: { value: L.moon_halo }, uRange: { value: 1 }, uS: { value: 0 }, uGuide: { value: 0 },
    },
    vertexShader: /* glsl */`varying vec3 vD; void main(){ vD = normalize(position); vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.); gl_Position = p.xyww; }`,
    fragmentShader: /* glsl */`
      ${NOISE}
      uniform vec3 uZen, uHor, uMoonDir, uMoonCol; uniform float uHaloI, uRange, uS, uGuide; varying vec3 vD;
      void main(){
        vec3 d = normalize(vD);
        float h = clamp(d.y, -.2, 1.);
        vec3 c = mix(uHor, uZen, pow(smoothstep(-.05, .7, h), .7));
        float md = max(dot(d, uMoonDir), 0.);
        float halo = pow(md, 18.) * .55 + pow(md, 140.) * 1.2 + pow(md, 4.) * .12;
        // thin cloud bands drifting across the moon haze (ink-wash sky)
        float cl = fbm3(vec3(d.x * 3.5 + uS * .002, d.y * 14., d.z * 3.5));
        float band = smoothstep(.05, .5, cl) * smoothstep(-.05, .25, h) * (1. - smoothstep(.35, .8, h));
        c += uMoonCol * halo * uHaloI * (1. - .5 * band);
        c = mix(c, c * .72 + uHor * .1, band * .5);
        float disc = smoothstep(.99955, .99975, md);
        c = mix(c, uMoonCol * 1.6, disc);
        gl_FragColor = vec4(c * mix(.55, 1., uRange), 1.);
        if (uGuide > .5) gl_FragColor = vec4(vec3(.93), 1.);
      }`,
  });
}

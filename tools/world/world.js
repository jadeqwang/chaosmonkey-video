// tools/world/world.js: the painted world as a real 3D scene (REVISION_V4 §2). See tools/world/README.md.
// Page API (driven by tools/world/render.mjs): await window.loadScene(sceneJson); await window.renderFrame(i, pass) -> PNG data URL.
import * as THREE from 'three';

const q = new URLSearchParams(location.search);
const W = Number(q.get('w') || 1920), H = Number(q.get('h') || 1080);
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, alpha: false });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // values pass straight through: painted plates stay as painted
document.body.appendChild(renderer.domElement);
const MSAA = Number(q.get('msaa') || 4);
const rtA = new THREE.WebGLRenderTarget(W, H, { samples: 0, depthTexture: new THREE.DepthTexture(W, H, THREE.FloatType), type: THREE.HalfFloatType });
const rtB = new THREE.WebGLRenderTarget(W, H, { samples: 0, type: THREE.HalfFloatType });
// supersampling: scenes render at SS x the output size and are averaged down in the blit (clean thin lines and threads)
const SS = Number(q.get('ss') || 1);
if (SS > 1) { rtA.setSize(W * SS, H * SS); rtA.depthTexture.image.width = W * SS; rtA.depthTexture.image.height = H * SS; rtB.setSize(W * SS, H * SS); }

const NOISE = /* glsl */`
vec3 mod289(vec3 x){return x-floor(x*(1./289.))*289.;} vec4 mod289(vec4 x){return x-floor(x*(1./289.))*289.;}
vec4 permute(vec4 x){return mod289(((x*34.)+1.)*x);} vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){const vec2 C=vec2(1./6.,1./3.);const vec4 D=vec4(0.,.5,1.,2.);vec3 i=floor(v+dot(v,C.yyy));vec3 x0=v-i+dot(i,C.xxx);
vec3 g=step(x0.yzx,x0.xyz);vec3 l=1.-g;vec3 i1=min(g.xyz,l.zxy);vec3 i2=max(g.xyz,l.zxy);vec3 x1=x0-i1+C.xxx;vec3 x2=x0-i2+C.yyy;vec3 x3=x0-D.yyy;
i=mod289(i);vec4 p=permute(permute(permute(i.z+vec4(0.,i1.z,i2.z,1.))+i.y+vec4(0.,i1.y,i2.y,1.))+i.x+vec4(0.,i1.x,i2.x,1.));
float n_=.142857142857;vec3 ns=n_*D.wyz-D.xzx;vec4 j=p-49.*floor(p*ns.z*ns.z);vec4 x_=floor(j*ns.z);vec4 y_=floor(j-7.*x_);
vec4 x=x_*ns.x+ns.yyyy;vec4 y=y_*ns.x+ns.yyyy;vec4 h=1.-abs(x)-abs(y);vec4 b0=vec4(x.xy,y.xy);vec4 b1=vec4(x.zw,y.zw);
vec4 s0=floor(b0)*2.+1.;vec4 s1=floor(b1)*2.+1.;vec4 sh=-step(h,vec4(0.));vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy;vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
vec3 p0=vec3(a0.xy,h.x);vec3 p1=vec3(a0.zw,h.y);vec3 p2=vec3(a1.xy,h.z);vec3 p3=vec3(a1.zw,h.w);
vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.);m=m*m;return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));}
float fbm(vec3 p){float a=.5,s=0.;for(int i=0;i<5;i++){s+=a*snoise(p);p*=2.03;a*=.5;}return s*.5+.5;}
`;
const COMMON = /* glsl */`
uniform vec3 uPaper; uniform float uFogDensity, uFogStart, uSeaY, uSeaSoft, uSeaAmp, uSeaScale, uTime, uPass, uFogK, uSeaK;
uniform vec2 uSeaDrift;
float paperFog(vec3 wpos, vec3 cam){
  float dist = length(wpos - cam);
  float f = (1. - exp(-max(0., dist - uFogStart) * uFogDensity)) * uFogK;
  float n = fbm(vec3(wpos.xz * uSeaScale + uSeaDrift * uTime, uTime * 0.02));
  float h = (wpos.y - (uSeaY + (n - 0.5) * uSeaAmp)) / max(uSeaSoft, 1e-4);
  float s = (1. - smoothstep(-1., 1., h)) * uSeaK;
  return clamp(max(f, s), 0., 1.);
}
vec2 paperFog2(vec3 wpos, vec3 cam){   // (distance fog, cloud sea) separately
  float dist = length(wpos - cam);
  float f = (1. - exp(-max(0., dist - uFogStart) * uFogDensity)) * uFogK;
  float n = fbm(vec3(wpos.xz * uSeaScale + uSeaDrift * uTime, uTime * 0.02));
  float h = (wpos.y - (uSeaY + (n - 0.5) * uSeaAmp)) / max(uSeaSoft, 1e-4);
  return vec2(clamp(f, 0., 1.), clamp((1. - smoothstep(-1., 1., h)) * uSeaK, 0., 1.));
}
`;
const sharedU = {
  uPaper: { value: new THREE.Color(0.925, 0.886, 0.8) }, uFogDensity: { value: 0.0 }, uFogStart: { value: 0 },
  uSeaY: { value: -1e6 }, uSeaSoft: { value: 1 }, uSeaAmp: { value: 0 }, uSeaScale: { value: 0.05 }, uSeaDrift: { value: new THREE.Vector2(0.3, 0.1) },
  uTime: { value: 0 }, uPass: { value: 0 },
};

const CARD_VS = /* glsl */`
uniform sampler2D uDepth; uniform float uRelief, uBend, uHasDepth; uniform vec2 uSize; uniform vec4 uUvRect;
varying vec2 vUv; varying vec3 vWorld;
float unpack(vec4 c){ return (c.r * 255. * 256. + c.g * 255.) / 65535.; }
void main(){
  vUv = uv; vec2 tuv = mix(uUvRect.xy, uUvRect.zw, uv);
  vec3 p = position;
  float d = uHasDepth > 0.5 ? unpack(texture2D(uDepth, tuv)) : 0.5;
  p.z += (d - 0.5) * uRelief;
  float xn = p.x / (uSize.x * 0.5);
  p.z -= uBend * xn * xn * uSize.x * 0.5;
  vec4 w = modelMatrix * vec4(p, 1.); vWorld = w.xyz;
  gl_Position = projectionMatrix * viewMatrix * w;
}`;
const CARD_FS = /* glsl */`
${NOISE}${COMMON}
uniform sampler2D uMap; uniform float uOpacity, uInk, uEdge, uSeed, uAlphaMul, uLum;
uniform vec4 uUvRect; uniform vec3 uTint; uniform float uRound, uTypeset;
uniform float uHasCarve; uniform sampler2D uCarveCov, uCarveId, uLit; uniform float uFrame, uLitN; uniform vec3 uGlowCol, uCarveCol;
uniform float uCarveDark, uLitHold, uLitBase, uGlowFog, uReveal; uniform vec2 uCarveTexel;
uniform float uHasTrue, uScaleNow; uniform vec3 uTrue, uPosNow;
uniform float uLightOn; uniform vec4 uLight; // x: edge position (uv.x), y: softness, z: direction (+1 lit to the left of the edge), w: strength
uniform vec3 uLightCol;
varying vec2 vUv; varying vec3 vWorld;
#ifdef B4X
// optional (B4; compiled only for cards that use light.wig, light2 or carve.reveal 'light', so existing scenes compile
// the exact same shader): edge wiggle of the terminators [amp in u, noise cells per v], a second light, reveal by light
uniform vec2 uLightWig, uLight2Wig; uniform float uLight2On; uniform vec4 uLight2; uniform vec3 uLight2Col;
uniform vec3 uGlowCol2, uCarveCol2; uniform float uRevW, uFlashW, uBevelPx, uBevelK;
// distance (in u) that the terminator has passed this point: > 0 lit (behind the edge), < 0 ahead of it
float behindEdge(vec2 tuv, vec4 L, vec2 wig, float sd){
  float e = L.x;
  if (wig.x > 0.) e += (fbm(vec3(tuv.y * wig.y, tuv.x * wig.y * 0.15, sd)) - 0.5) * 2. * wig.x;
  return -(tuv.x - e) * L.z;
}
#endif
void main(){
  vec2 tuv = mix(uUvRect.xy, uUvRect.zw, vUv);
  vec4 c = texture2D(uMap, tuv);
  float a = c.a * uOpacity * uAlphaMul;
  if (uRound > 0.) { vec2 e = (vUv - 0.5) * 2.; float r = length(e); float n0 = fbm(vec3(vUv * 6., uSeed)); a *= 1. - smoothstep(1. - uRound, 1., r + (n0 - 0.5) * 0.25); }
  // wet wash edge: the translucent rim is eaten by a slow noise, so the edge is a brush edge, not a matte line
  if (uEdge > 0.) { float n = fbm(vec3(tuv * 40., uSeed + uTime * 0.05)); a *= smoothstep(0., uEdge, a + (n - 0.5) * uEdge * 0.8); }
  if (a < 0.01) discard;
  vec3 col = c.rgb;
  col = mix(uPaper, col, uInk) * uTint * uLum;
  vec3 glow = vec3(0.);
  float ts = uTypeset;   // typeset passes (R2): coverage of carved glyphs (or the whole card if typeset: true)
#ifndef B4X
  if (uLightOn > 0.5) {
    float side = (tuv.x - uLight.x) * uLight.z;
    float lit = smoothstep(-uLight.y, uLight.y, -side);
    col *= mix(1. - uLight.w * 0.55, 1. + uLight.w * 0.25, lit) * mix(vec3(1.), uLightCol, lit * uLight.w);
  }
#else
  float b1 = 1e6, b2 = -1e6;
  if (uLightOn > 0.5) {
    float side;
    if (uLightWig.x > 0.) { b1 = behindEdge(tuv, uLight, uLightWig, 3.7); side = -b1; }
    else side = (tuv.x - uLight.x) * uLight.z;
    float lit = smoothstep(-uLight.y, uLight.y, -side);
    col *= mix(1. - uLight.w * 0.55, 1. + uLight.w * 0.25, lit) * mix(vec3(1.), uLightCol, lit * uLight.w);
    b1 = -side;
  }
  if (uLight2On > 0.5) {
    b2 = behindEdge(tuv, uLight2, uLight2Wig, 7.3);
    float lit2 = smoothstep(-uLight2.y, uLight2.y, b2);
    col *= mix(1. - uLight2.w * 0.55, 1. + uLight2.w * 0.25, lit2) * mix(vec3(1.), uLight2Col, lit2 * uLight2.w);
  }
  if (uHasCarve > 0.5 && uReveal > 1.5) {
    // reveal by light (B4): a glyph's strokes exist only where its light's terminator has passed (per pixel, so one
    // stroke is cut as the edge crosses it); the fresh cut flashes near the edge and keeps 'base'. Layer (lit[3]) 0 is
    // cut by 'light', 1 by 'light2' (with glow2 / col2).
    float cov = texture2D(uCarveCov, vUv).r;
    if (cov > 0.002) {
      vec4 idc = texture2D(uCarveId, vUv);
      float id = floor(idc.r * 255. + 0.5) * 256. + floor(idc.g * 255. + 0.5);
      vec4 L = id > 0.5 ? texelFetch(uLit, ivec2(int(mod(id, 4096.)), int(id / 4096.)), 0) : vec4(-1.);
      float lay = L.b > 0.5 ? 1. : 0.;
      float bh = lay > 0.5 ? b2 : b1;
      float gain = L.g < 0. ? 1. : L.g;
      float rv = smoothstep(0., uRevW, bh);
      cov *= rv;
      if (cov > 0.002) {
        float off = texture2D(uCarveCov, vUv + uCarveTexel * vec2(uBevelPx, -uBevelPx)).r * rv;
        float bevel = (cov - off) * uBevelK / 0.35;
        vec3 cc = lay > 0.5 ? uCarveCol2 : uCarveCol;
        vec3 cut = col * (1. - uCarveDark * cov) * cc;
        cut += bevel * 0.35 * (1.0 - uCarveDark * 0.5);
        col = mix(col, cut, clamp(cov * 1.2, 0., 1.));
        ts = max(ts, clamp(cov * 1.2, 0., 1.));
        float amt = (exp(-max(bh, 0.) / uFlashW) * 1.4 + uLitBase) * gain;
        vec3 gc = lay > 0.5 ? uGlowCol2 : uGlowCol;
        col = mix(col, gc * 1.15, clamp(cov * amt * 0.3, 0., 1.));
        glow = gc * cov * amt;
      }
    }
  } else
#endif
  if (uHasCarve > 0.5) {
    float cov = texture2D(uCarveCov, vUv).r;
    float revealDt = 1e6;
    if (uReveal > 0.5 && cov > 0.002) {   // reveal mode: a glyph does not exist until its frame (cut by the light)
      vec4 idr = texture2D(uCarveId, vUv);
      float idv = floor(idr.r * 255. + 0.5) * 256. + floor(idr.g * 255. + 0.5);
      vec4 Lr = texelFetch(uLit, ivec2(int(mod(idv, 4096.)), int(idv / 4096.)), 0);
      revealDt = Lr.r < -1e5 ? -1. : uFrame - Lr.r;
      cov *= smoothstep(0., 2., revealDt);
    }
    if (cov > 0.002) {
      float off = texture2D(uCarveCov, vUv + uCarveTexel * vec2(1.5, -1.5)).r;
      float bevel = (cov - off);
      vec3 cut = col * (1. - uCarveDark * cov) * uCarveCol;
      cut += bevel * 0.35 * (1.0 - uCarveDark * 0.5);
      col = mix(col, cut, clamp(cov * 1.2, 0., 1.));
      ts = max(ts, clamp(cov * 1.2, 0., 1.));
      vec4 idc = texture2D(uCarveId, vUv);
      float id = floor(idc.r * 255. + 0.5) * 256. + floor(idc.g * 255. + 0.5);
      if (id > 0.5) {
        vec4 L = texelFetch(uLit, ivec2(int(mod(id, 4096.)), int(id / 4096.)), 0);
        float dt = uFrame - L.r;
        if (L.r > -1e5 && dt >= 0.) {   // unlit glyphs carry -1e6; negative frames = lit before the shot began
          float rise = smoothstep(0., 4., dt);
          float flare = exp(-dt / 6.) * 0.9;
          float flick = 0.06 * sin(dt * 1.7 + id) * exp(-dt / 30.);
          float amt = (rise * (uLitBase + flare + flick)) * L.g;
          if (uReveal > 0.5) amt = (exp(-dt / 5.) * 1.4 + uLitBase) * L.g;   // the cut flashes, then keeps a faint warmth
          col = mix(col, uGlowCol * 1.15, clamp(cov * amt, 0., 1.));
          glow = uGlowCol * cov * amt;
        }
      }
    }
  }
  vec3 wf = uHasTrue > 0.5 ? uTrue + (vWorld - uPosNow) / max(uScaleNow, 1e-4) : vWorld;   // fog/sea in the card's true place
  vec2 f2 = paperFog2(wf, cameraPosition);
  float f = max(f2.x, f2.y);
  col = mix(col, uPaper, f);
  glow *= (1. - f2.x * uGlowFog) * (1. - f2.y);     // the cloud sea swallows the light; distance only dims it
  if (uPass > 0.5 && uPass < 1.5) col = glow;
  else if (uPass > 1.5) { float tm = ts * (1. - f); col = uPass > 2.5 ? vec3(tm) : col * tm; }   // typeset / typeset_a
  gl_FragColor = vec4(col, a);
}`;

const SOFT = /* glsl */`
uniform sampler2D uSceneDepth; uniform vec2 uRes; uniform float uNear, uFar, uOrtho;
float sceneViewZ(){
  float d = texture2D(uSceneDepth, gl_FragCoord.xy / uRes).r;
  if (uOrtho > 0.5) return uNear + d * (uFar - uNear);
  float z = d * 2. - 1.;
  return 2. * uNear * uFar / ((uFar + uNear) - z * (uFar - uNear));
}`;
const MIST_VS = /* glsl */`
varying vec2 vUv; varying vec3 vWorld; varying float vViewZ;
void main(){ vUv = uv; vec4 w = modelMatrix * vec4(position, 1.); vWorld = w.xyz; vec4 mv = viewMatrix * w; vViewZ = -mv.z; gl_Position = projectionMatrix * mv; }`;
const MIST_FS = /* glsl */`
${NOISE}${COMMON}${SOFT}
uniform float uOpacity, uScale, uSeed, uSoft, uEdge, uThresh, uWash, uNearFade, uBand;
uniform vec2 uSpeed, uSize; uniform vec3 uTone;
varying vec2 vUv; varying vec3 vWorld; varying float vViewZ;
void main(){
  vec2 p = vUv * uSize * uScale;
  float warp = fbm(vec3(p * 0.5 + uSeed, uTime * 0.04));
  float n = fbm(vec3(p + uSpeed * uTime + warp * 1.2, uSeed + uTime * 0.03));
  vec2 e2 = (vUv - 0.5) * 2.;
  float r = uBand > 0.5 ? abs(e2.y) + 0.15 * smoothstep(0.6, 1.0, abs(e2.x)) * 4. : length(e2);
  float e = 1. - smoothstep(1. - uEdge, 1., r);
  float a = smoothstep(uThresh, uThresh + 0.3, n) * e * uOpacity;
  float sz = sceneViewZ();
  float diff = sz - vViewZ;
  if (diff < 0.) discard;
  a *= smoothstep(0., uSoft, diff);
  a *= smoothstep(uNearFade * 0.3, uNearFade, vViewZ);
  if (a < 0.003) discard;
  // the thin parts of a mist band carry a pale wash (a painter's grey), the dense parts are bare paper
  float wash = uWash * (1. - smoothstep(uThresh + 0.05, uThresh + 0.4, n)) * e;
  vec3 col = mix(uPaper, uTone, wash);
  if (uPass > 0.5) col = vec3(0.);
  gl_FragColor = vec4(col, a);
}`;
const THREAD_VS = /* glsl */`
attribute vec3 aPrev; attribute vec3 aNext; attribute float aSide; attribute float aU;
uniform vec2 uRes; uniform float uWidth;
uniform float uFrame, uF0, uFDraw, uHeadW;
varying float vU; varying float vSide; varying float vViewZ; varying vec3 vWorld;
void main(){
  vU = aU; vSide = aSide;
  mat4 pv = projectionMatrix * viewMatrix;
  vec4 c = pv * vec4(position, 1.), cp = pv * vec4(aPrev, 1.), cn = pv * vec4(aNext, 1.);
  vec2 s = c.xy / c.w, sp = cp.xy / cp.w, sn = cn.xy / cn.w;
  vec2 dir = normalize((sn - sp) * uRes + 1e-6);
  vec2 nrm = vec2(-dir.y, dir.x);
  float pd = clamp((uFrame - uF0) / max(uFDraw, 1e-3), 0., 1.);
  float hw = 1. + uHeadW * exp(-max(0., pd - aU) * 14.) * (pd < 1. ? 1. : 0.);   // R2: the drawing head swells (bead)
  c.xy += nrm * aSide * uWidth * hw / uRes * c.w;
  vec4 mv = viewMatrix * vec4(position, 1.); vViewZ = -mv.z; vWorld = position;
  gl_Position = c;
}`;
const THREAD_FS = /* glsl */`
${NOISE}${COMMON}${SOFT}
uniform float uFrame, uF0, uFDraw, uFHold, uFFade, uRest, uGlowK, uOpacity, uHeadG;
uniform vec3 uCol; uniform vec2 uDistFade;
varying float vU; varying float vSide; varying float vViewZ; varying vec3 vWorld;
void main(){
  float p = clamp((uFrame - uF0) / max(uFDraw, 1e-3), 0., 1.);
  if (uFrame < uF0 || vU > p) discard;
  float sz = sceneViewZ();
  float occl = smoothstep(-0.02 * vViewZ, 0.0, sz - vViewZ);  // behind rock: hidden (soft)
  float fade = 1. - clamp((uFrame - (uF0 + uFDraw + uFHold)) / max(uFFade, 1e-3), 0., 1.);
  float level = mix(uRest, 1., fade);
  float head = exp(-max(0., p - vU) * 14.) * (p < 1. ? 1. : fade);
  float prof = 1. - smoothstep(0.35, 1., abs(vSide));
  float a = prof * level * occl * uOpacity;
  float f = paperFog(vWorld, cameraPosition);
  a *= (1. - f * 0.85);
  if (uDistFade.y > 0.) a *= smoothstep(uDistFade.x, uDistFade.y, vViewZ);   // R2 veins: only read from afar
  if (a < 0.003) discard;
  vec3 col = mix(uCol * 0.55, uCol * 1.25, head);
  if (uPass > 0.5 && uPass < 1.5) col = uCol * (0.6 + 1.6 * head * (1. + uHeadG)) * level * uGlowK * (1. - f);
  else if (uPass > 2.5) col = vec3(1.);
  gl_FragColor = vec4(col, a);
}`;
// points (B4 dust): per particle [x, y, z, f0, vx, vy, vz, life (s), size (world units), seed]; position at t = p0 + v t
// + acc t^2 / 2 + sway; hidden behind rock (scene depth), fogged to paper; an irregular soft fleck, not a sparkle
const POINTS_VS = /* glsl */`
attribute float aF0, aLife, aSize, aSeed; attribute vec3 aVel;
uniform float uFrame, uFps, uSway, uSwayF, uMinPx, uMaxPx, uFadeIn, uFadeOut, uPxScale, uGrow; uniform vec3 uAcc;
varying float vA, vSeed, vViewZ; varying vec3 vWorld;
void main(){
  float t = (uFrame - aF0) / uFps;
  vSeed = aSeed;
  if (t < 0. || t > aLife) { gl_Position = vec4(2., 2., 2., 1.); gl_PointSize = 0.; vA = 0.; return; }
  vec3 p = position + aVel * t + 0.5 * uAcc * t * t;
  float ph = aSeed * 6.2832;
  p += vec3(sin(ph + t * uSwayF), 0., cos(ph * 1.3 + t * uSwayF * 0.8)) * uSway * min(t, 1.);
  vec4 mv = viewMatrix * vec4(p, 1.); vViewZ = -mv.z; vWorld = p;
  gl_Position = projectionMatrix * mv;
  float px = aSize * (1. + uGrow * t) * projectionMatrix[1][1] * uPxScale / max(vViewZ, 1e-3);
  float k = smoothstep(0., uFadeIn, t) * (1. - smoothstep(aLife * (1. - uFadeOut), aLife, t));
  vA = k * clamp(px / uMinPx, 0., 1.);
  gl_PointSize = clamp(px, uMinPx, uMaxPx);
}`;
const POINTS_FS = /* glsl */`
${NOISE}${COMMON}${SOFT}
uniform float uOpacity, uGlowK; uniform vec3 uCol, uGlowCol;
varying float vA, vSeed, vViewZ; varying vec3 vWorld;
void main(){
  if (vA < 0.003) discard;
  vec2 q = gl_PointCoord - 0.5;
  float n = snoise(vec3(q * 3.2, vSeed * 17.));
  float r = length(q) * 2. + n * 0.22;
  float a = (1. - smoothstep(0.15, 1., r)) * vA * uOpacity;
  float sz = sceneViewZ();
  a *= smoothstep(-0.02 * vViewZ, 0.0, sz - vViewZ);
  float f = paperFog(vWorld, cameraPosition);
  a *= 1. - f;
  if (a < 0.003) discard;
  vec3 col = uCol;
  if (uPass > 0.5 && uPass < 1.5) col = uGlowCol * uGlowK;
  else if (uPass > 2.5) col = vec3(1.);
  gl_FragColor = vec4(col, a);
}`;
const BLIT_FS = /* glsl */`
uniform sampler2D uTex; uniform vec2 uTexel; uniform float uSS; varying vec2 vUv;
void main(){
  if (uSS < 1.5) { gl_FragColor = vec4(texture2D(uTex, vUv).rgb, 1.); return; }
  vec3 s = vec3(0.); for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) { if (float(i) >= uSS || float(j) >= uSS) continue;
    s += texture2D(uTex, vUv + (vec2(float(i), float(j)) - (uSS - 1.) * 0.5) * uTexel).rgb; }
  gl_FragColor = vec4(s / (uSS * uSS), 1.);
}`;

const loader = new THREE.TextureLoader();
const texCache = new Map();
function loadTex(url, { nearest = false, mip = true } = {}) {
  const key = url + (nearest ? '#n' : '');
  if (texCache.has(key)) return Promise.resolve(texCache.get(key));
  return new Promise((res, rej) => loader.load('/repo/' + url, (t) => {
    t.colorSpace = THREE.NoColorSpace; t.flipY = true;
    if (nearest) { t.minFilter = THREE.NearestFilter; t.magFilter = THREE.NearestFilter; t.generateMipmaps = false; }
    else { t.minFilter = mip ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter; t.magFilter = THREE.LinearFilter; t.anisotropy = 16; }
    texCache.set(key, t); res(t);
  }, undefined, () => rej(new Error('texture ' + url))));
}
function dropTex(url) { for (const k of [url, url + '#n']) { const t = texCache.get(k); if (t) { t.dispose(); texCache.delete(k); } } }
const GREY = new THREE.DataTexture(new Uint8Array([128, 0, 0, 255]), 1, 1); GREY.needsUpdate = true;
const BLACK = new THREE.DataTexture(new Uint8Array([0, 0, 0, 0]), 1, 1); BLACK.needsUpdate = true;

let S = null;   // the loaded scene
const sceneA = new THREE.Scene(), sceneB = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 5000);
const ocam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 5000);
const blitMat = new THREE.ShaderMaterial({ uniforms: { uTex: { value: null }, uTexel: { value: new THREE.Vector2(1 / (W * SS), 1 / (H * SS)) }, uSS: { value: SS } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }', fragmentShader: BLIT_FS, depthTest: false, depthWrite: false });
const blitScene = new THREE.Scene(); blitScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), blitMat));
const blitCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const copyMat = new THREE.ShaderMaterial({ uniforms: { uTex: { value: null } }, vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
  fragmentShader: 'uniform sampler2D uTex; varying vec2 vUv; void main(){ gl_FragColor = texture2D(uTex, vUv); }', depthTest: false, depthWrite: false });
const copyScene = new THREE.Scene(); copyScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), copyMat));

function v3(a) { return new THREE.Vector3(a[0], a[1], a[2]); }
function lerpKeys(keys, f, field, dflt) {
  // keys: [[frame, {field: value}], ...] sorted; numbers or arrays interpolate linearly; holds at the ends
  const ks = keys.filter((k) => k[1][field] !== undefined);
  if (!ks.length) return dflt;
  if (f <= ks[0][0]) return ks[0][1][field];
  for (let i = 1; i < ks.length; i++) if (f <= ks[i][0]) {
    const [f0, a] = ks[i - 1], [f1, b] = ks[i]; const t = (f - f0) / Math.max(f1 - f0, 1e-6);
    const va = a[field], vb = b[field];
    return Array.isArray(va) ? va.map((x, j) => x + (vb[j] - x) * t) : va + (vb - va) * t;
  }
  return ks[ks.length - 1][1][field];
}
function place(mesh, o, f) {
  const k = o.keys || [];
  const pos = lerpKeys(k, f, 'pos', o.pos || [0, 0, 0]);
  const yaw = lerpKeys(k, f, 'yaw', o.yaw || 0), pitch = lerpKeys(k, f, 'pitch', o.pitch || 0), roll = lerpKeys(k, f, 'roll', o.roll || 0);
  // a mist's 'scale' is its noise scale, not a size: mists scale only through keys 'size' (never through o.scale)
  let sc = mesh.userData.kind === 'mist' ? lerpKeys(k, f, 'size_k', 1) : lerpKeys(k, f, 'scale', o.scale ?? 1); if (!Array.isArray(sc)) sc = [sc, sc, sc];
  mesh.position.set(pos[0], pos[1], pos[2]);
  mesh.rotation.set(pitch * Math.PI / 180, yaw * Math.PI / 180, roll * Math.PI / 180, 'YXZ');
  mesh.scale.set(sc[0], sc[1], sc[2] ?? sc[0]);
  if (o.billboard) {   // cylindrical: face the camera around the vertical
    const dx = camera.position.x - pos[0], dz = camera.position.z - pos[2];
    mesh.rotation.set(pitch * Math.PI / 180, Math.atan2(dx, dz), 0, 'YXZ');
  }
}

async function makeCard(o) {
  const [w, h] = o.size;
  const seg = o.seg || [Math.min(512, Math.max(8, Math.round(256 * w / Math.max(w, h)))), Math.min(512, Math.max(8, Math.round(256 * h / Math.max(w, h))))];
  const g = new THREE.PlaneGeometry(w, h, seg[0], seg[1]);
  const anchor = o.anchor || 'bottom';   // 'bottom' = pos is the bottom centre; 'center'
  if (anchor === 'bottom') g.translate(0, h / 2, 0);
  const map = o.tex ? await loadTex(o.tex) : BLACK;
  const dep = o.depth ? await loadTex(o.depth, { nearest: true }) : GREY;
  const u = {
    ...sharedU, uMap: { value: map }, uDepth: { value: dep }, uHasDepth: { value: o.depth ? 1 : 0 }, uRelief: { value: o.relief || 0 }, uBend: { value: o.bend || 0 },
    uSize: { value: new THREE.Vector2(w, h) }, uUvRect: { value: new THREE.Vector4(...(o.uvRect || [0, 0, 1, 1])) },
    uRound: { value: o.round ?? 0 }, uTypeset: { value: o.typeset ? 1 : 0 }, uOpacity: { value: o.opacity ?? 1 }, uAlphaMul: { value: 1 }, uInk: { value: o.ink ?? 1 }, uLum: { value: o.lum ?? 1 }, uEdge: { value: o.edge ?? 0.0 }, uSeed: { value: o.seed ?? Math.random() * 100 },
    uTint: { value: new THREE.Color(...(o.tint || [1, 1, 1])) }, uFogK: { value: o.fogk ?? 1 }, uSeaK: { value: o.seak ?? 1 },
    uHasCarve: { value: 0 }, uCarveCov: { value: BLACK }, uCarveId: { value: BLACK }, uLit: { value: BLACK }, uFrame: { value: 0 }, uLitN: { value: 0 },
    uGlowCol: { value: new THREE.Color(...(o.carve?.glow || [1.0, 0.72, 0.25])) }, uCarveCol: { value: new THREE.Color(...(o.carve?.col || [1, 1, 1])) },
    uCarveDark: { value: o.carve?.dark ?? 0.55 }, uGlowFog: { value: o.carve?.glowFog ?? 1.0 }, uReveal: { value: o.carve?.reveal === 'light' ? 2 : (o.carve?.reveal ? 1 : 0) }, uLitBase: { value: o.carve?.base ?? 0.75 }, uLitHold: { value: 0 }, uCarveTexel: { value: new THREE.Vector2(1 / 4096, 1 / 4096) },
    uHasTrue: { value: o.truePos ? 1 : 0 }, uTrue: { value: new THREE.Vector3(...(o.truePos || [0, 0, 0])) }, uPosNow: { value: new THREE.Vector3() }, uScaleNow: { value: 1 },
    uLightOn: { value: o.light ? 1 : 0 }, uLight: { value: new THREE.Vector4(0.5, 0.05, 1, 0) }, uLightCol: { value: new THREE.Color(...(o.light?.col || [1.0, 0.92, 0.78])) },
    // optional (B4): terminator wiggle, a second light, reveal-by-light parameters (all default off / unchanged)
    uLightWig: { value: new THREE.Vector2(...(o.light?.wig || [0, 1])) },
    uLight2On: { value: o.light2 ? 1 : 0 }, uLight2: { value: new THREE.Vector4(...(o.light2?.v || [0.5, 0.05, 1, 0])) },
    uLight2Col: { value: new THREE.Color(...(o.light2?.col || [0.82, 0.9, 1.0])) }, uLight2Wig: { value: new THREE.Vector2(...(o.light2?.wig || [0, 1])) },
    uGlowCol2: { value: new THREE.Color(...(o.carve?.glow2 || o.carve?.glow || [1.0, 0.72, 0.25])) }, uCarveCol2: { value: new THREE.Color(...(o.carve?.col2 || o.carve?.col || [1, 1, 1])) },
    uRevW: { value: o.carve?.revW ?? 0.002 }, uFlashW: { value: o.carve?.flashW ?? 0.01 }, uBevelPx: { value: o.carve?.bevelPx ?? 1.5 }, uBevelK: { value: o.carve?.bevelK ?? 0.35 },
  };
  if (o.carve) {
    u.uHasCarve.value = 1;
    u.uCarveCov.value = await loadTex(o.carve.cov);
    u.uCarveId.value = await loadTex(o.carve.id, { nearest: true });
    const n = Math.max(1, ...o.carve.lit.map((x) => x[0]));
    const rows = Math.ceil((n + 1) / 4096), data = new Float32Array(4096 * rows * 4).fill(-1e6);
    for (const [id, f, gain, layer] of o.carve.lit) { data[id * 4] = f; data[id * 4 + 1] = gain ?? 1; if (layer !== undefined) data[id * 4 + 2] = layer; }
    const lt = new THREE.DataTexture(data, 4096, rows, THREE.RGBAFormat, THREE.FloatType); lt.needsUpdate = true;
    u.uLit.value = lt;
    u.uCarveTexel.value.set(1 / u.uCarveCov.value.image.width, 1 / u.uCarveCov.value.image.height);
  }
  const b4x = !!(o.light2 || o.light?.wig || o.carve?.reveal === 'light');
  const m = new THREE.ShaderMaterial({ uniforms: u, vertexShader: CARD_VS, fragmentShader: CARD_FS, transparent: true, depthWrite: o.depthWrite ?? true,
    ...(b4x ? { defines: { B4X: 1 } } : {}),
    depthTest: o.depthTest ?? true, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(g, m);
  mesh.userData = { o, kind: 'card' };
  mesh.renderOrder = o.order || 0;
  return mesh;
}
function makeMist(o) {
  const [w, h] = o.size;
  const g = new THREE.PlaneGeometry(w, h, 1, 1);
  const u = { ...sharedU, ...softU(), uOpacity: { value: o.opacity ?? 0.9 }, uScale: { value: o.scale ?? 0.08 }, uSeed: { value: o.seed ?? Math.random() * 100 },
    uSoft: { value: o.soft ?? 2 }, uEdge: { value: o.edge ?? 0.5 }, uThresh: { value: o.thresh ?? 0.42 }, uWash: { value: o.wash ?? 0.25 },
    uNearFade: { value: o.nearFade ?? 1.0 }, uBand: { value: o.band ? 1 : 0 },
    uSpeed: { value: new THREE.Vector2(...(o.speed || [0.05, 0])) }, uSize: { value: new THREE.Vector2(w, h) }, uTone: { value: new THREE.Color(...(o.tone || [0.62, 0.62, 0.62])) },
    uFogK: { value: o.fogk ?? 0.5 }, uSeaK: { value: 0 } };
  const m = new THREE.ShaderMaterial({ uniforms: u, vertexShader: MIST_VS, fragmentShader: MIST_FS, transparent: true, depthWrite: false, depthTest: false, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(g, m); mesh.userData = { o, kind: 'mist' }; mesh.renderOrder = o.order || 0;
  return mesh;
}
function softU() { return { uSceneDepth: { value: rtA.depthTexture }, uRes: { value: new THREE.Vector2(W * SS, H * SS) }, uNear: { value: 0.1 }, uFar: { value: 5000 }, uOrtho: { value: 0 } }; }
function makeThread(o) {
  const P = o.pts.map(v3); const n = P.length;
  const pos = [], prev = [], next = [], side = [], uu = [], idx = [];
  let L = [0]; for (let i = 1; i < n; i++) L.push(L[i - 1] + P[i].distanceTo(P[i - 1]));
  for (let i = 0; i < n; i++) {
    const a = P[Math.max(0, i - 1)], b = P[Math.min(n - 1, i + 1)];
    for (const s of [-1, 1]) { pos.push(P[i].x, P[i].y, P[i].z); prev.push(a.x, a.y, a.z); next.push(b.x, b.y, b.z); side.push(s); uu.push(L[i] / Math.max(L[n - 1], 1e-6)); }
    if (i < n - 1) { const k = i * 2; idx.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aPrev', new THREE.Float32BufferAttribute(prev, 3));
  g.setAttribute('aNext', new THREE.Float32BufferAttribute(next, 3)); g.setAttribute('aSide', new THREE.Float32BufferAttribute(side, 1));
  g.setAttribute('aU', new THREE.Float32BufferAttribute(uu, 1)); g.setIndex(idx);
  const u = { ...sharedU, ...softU(), uWidth: { value: (o.width ?? 2) * SS }, uFrame: { value: 0 }, uF0: { value: o.f0 }, uFDraw: { value: o.fdraw ?? 3 }, uFHold: { value: o.fhold ?? 12 },
    uHeadW: { value: o.headW ?? 0 }, uHeadG: { value: o.headG ?? 0 }, uDistFade: { value: new THREE.Vector2(...(o.distFade || [0, 0])) },
    uFFade: { value: o.ffade ?? 12 }, uRest: { value: o.rest ?? 0.15 }, uGlowK: { value: o.glow ?? 1 }, uOpacity: { value: o.opacity ?? 1 },
    uCol: { value: new THREE.Color(...(o.col || [0.86, 0.62, 0.2])) }, uFogK: { value: o.fogk ?? 0.6 }, uSeaK: { value: o.seak ?? 0.5 } };
  const m = new THREE.ShaderMaterial({ uniforms: u, vertexShader: THREAD_VS, fragmentShader: THREAD_FS, transparent: true, depthWrite: false, depthTest: false, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(g, m); mesh.frustumCulled = false; mesh.userData = { o, kind: 'thread' }; mesh.renderOrder = o.order || 10;
  return mesh;
}

async function makePoints(o) {
  // o.file: raw little-endian float32, 10 per particle (or o.data: flat array)
  let D = o.data ? new Float32Array(o.data) : new Float32Array(await (await fetch('/repo/' + o.file)).arrayBuffer());
  const n = Math.floor(D.length / 10);
  const P = new Float32Array(n * 3), V = new Float32Array(n * 3), F0 = new Float32Array(n), L = new Float32Array(n), Z = new Float32Array(n), SD = new Float32Array(n);
  for (let i = 0; i < n; i++) { const b = i * 10; P.set([D[b], D[b + 1], D[b + 2]], i * 3); F0[i] = D[b + 3]; V.set([D[b + 4], D[b + 5], D[b + 6]], i * 3); L[i] = D[b + 7]; Z[i] = D[b + 8]; SD[i] = D[b + 9]; }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('aVel', new THREE.BufferAttribute(V, 3));
  g.setAttribute('aF0', new THREE.BufferAttribute(F0, 1)); g.setAttribute('aLife', new THREE.BufferAttribute(L, 1));
  g.setAttribute('aSize', new THREE.BufferAttribute(Z, 1)); g.setAttribute('aSeed', new THREE.BufferAttribute(SD, 1));
  const u = { ...sharedU, ...softU(), uFrame: { value: 0 }, uFps: { value: S.fps || 24 }, uOpacity: { value: o.opacity ?? 1 },
    uAcc: { value: new THREE.Vector3(...(o.acc || [0, 0, 0])) }, uSway: { value: o.sway ?? 0 }, uSwayF: { value: o.swayF ?? 1.5 },
    uMinPx: { value: (o.minPx ?? 1.2) * SS }, uMaxPx: { value: (o.maxPx ?? 24) * SS }, uFadeIn: { value: o.fadeIn ?? 0.15 }, uFadeOut: { value: o.fadeOut ?? 0.4 },
    uPxScale: { value: H * SS / 2 }, uGrow: { value: o.grow ?? 0 }, uGlowK: { value: o.glow ?? 1 },
    uCol: { value: new THREE.Color(...(o.col || [1.0, 0.97, 0.88])) }, uGlowCol: { value: new THREE.Color(...(o.glowCol || [1.0, 0.75, 0.35])) },
    uFogK: { value: o.fogk ?? 1 }, uSeaK: { value: o.seak ?? 0 } };
  const m = new THREE.ShaderMaterial({ uniforms: u, vertexShader: POINTS_VS, fragmentShader: POINTS_FS, transparent: true, depthWrite: false, depthTest: false });
  const mesh = new THREE.Points(g, m); mesh.frustumCulled = false; mesh.userData = { o, kind: 'points' }; mesh.renderOrder = o.order || 5;
  return mesh;
}
window.loadScene = async (scene) => {
  for (const sc of [sceneA, sceneB]) while (sc.children.length) { const c = sc.children.pop(); c.geometry?.dispose(); c.material?.dispose(); }
  S = scene;
  sharedU.uPaper.value.setRGB(...(S.paper || [0.925, 0.886, 0.8]));
  const fog = S.fog || {}; sharedU.uFogDensity.value = fog.density ?? 0; sharedU.uFogStart.value = fog.start ?? 0;
  const sea = S.sea || {}; sharedU.uSeaY.value = sea.y ?? -1e6; sharedU.uSeaSoft.value = sea.soft ?? 1; sharedU.uSeaAmp.value = sea.amp ?? 0;
  sharedU.uSeaScale.value = sea.scale ?? 0.05; sharedU.uSeaDrift.value.set(...(sea.drift || [0.3, 0.1]));
  for (const o of S.cards || []) sceneA.add(await makeCard(o));
  for (const o of S.mists || []) sceneB.add(makeMist(o));
  for (const o of S.threads || []) sceneB.add(makeThread(o));
  for (const o of S.points || []) sceneB.add(await makePoints(o));
  for (const o of S.overlays || []) { const m = await makeCard({ ...o, depthTest: false, depthWrite: false, fogk: o.fogk ?? 0, seak: o.seak ?? 0 }); m.userData.kind = 'overlay'; sceneB.add(m); }
  return { cards: sceneA.children.length, b: sceneB.children.length };
};

function setCamera(f) {
  const c = S.camera[Math.min(f, S.camera.length - 1)];
  const cam = c.ortho ? ocam : camera;
  cam.position.set(...c.p);
  cam.up.set(...(c.up || [0, 1, 0]));
  cam.lookAt(...c.t);
  if (c.roll) cam.rotateZ(c.roll * Math.PI / 180);
  cam.near = c.near ?? 0.1; cam.far = c.far ?? 5000;
  if (c.ortho) { const hh = c.ortho / 2, ww = hh * W / H; Object.assign(cam, { left: -ww, right: ww, top: hh, bottom: -hh }); }
  else { cam.fov = c.fov ?? 40; cam.aspect = W / H; if (c.shift) { cam.filmOffset = 0; } }
  cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  return cam;
}

async function animTex(mesh, o, f) {
  // video texture on a card: o.anim = {pattern: 'dir/%04d.png', n, start (frame of the scene where clip frame 0 shows), rate, loop: 'pingpong'|'loop'|'hold'}
  const A = o.anim; let k = (f - (A.start || 0)) * (A.rate ?? 1) + (A.offset || 0);
  const n = A.n;
  if (A.loop === 'pingpong') { const p = 2 * (n - 1); k = ((k % p) + p) % p; if (k > n - 1) k = p - k; }
  else if (A.loop === 'loop') k = ((k % n) + n) % n; else k = Math.min(Math.max(k, 0), n - 1);
  const i0 = Math.floor(k);
  const url = A.pattern.replace('%04d', String(i0).padStart(4, '0'));
  const prevUrl = mesh.userData.animUrl;
  if (url !== prevUrl) { mesh.material.uniforms.uMap.value = await loadTex(url, { mip: true }); if (prevUrl) dropTex(prevUrl); mesh.userData.animUrl = url; }
}

window.renderFrame = async (f, pass = 'beauty') => {
  const cam = setCamera(f);
  sharedU.uTime.value = f / (S.fps || 24); sharedU.uPass.value = pass === 'glow' ? 1 : pass === 'typeset' ? 2 : pass === 'typeset_a' ? 3 : 0;
  const c = S.camera[Math.min(f, S.camera.length - 1)];
  // per-frame environment overrides carried on the camera dict: seaY, seaSoft, fogDensity, fogStart, paper
  const sea = S.sea || {}, fog = S.fog || {};
  sharedU.uSeaY.value = c.seaY ?? sea.y ?? -1e6; sharedU.uSeaSoft.value = c.seaSoft ?? sea.soft ?? 1;
  sharedU.uFogDensity.value = c.fogDensity ?? fog.density ?? 0; sharedU.uFogStart.value = c.fogStart ?? fog.start ?? 0;
  sharedU.uPaper.value.setRGB(...(c.paper || S.paper || [0.925, 0.886, 0.8]));
  for (const sc of [sceneA, sceneB]) for (const mesh of sc.children) {
    const { o, kind } = mesh.userData;
    place(mesh, o, f);
    const U = mesh.material.uniforms;
    if (U.uFrame) U.uFrame.value = f;
    if (U.uNear) { U.uNear.value = cam.near; U.uFar.value = cam.far; U.uOrtho.value = c.ortho ? 1 : 0; }
    if (o.keys) {
      const op = lerpKeys(o.keys, f, 'opacity', o.opacity ?? (kind === 'mist' ? 0.9 : 1)); U.uOpacity.value = op;
      if (kind === 'card' || kind === 'overlay') { U.uRelief.value = lerpKeys(o.keys, f, 'relief', o.relief || 0); U.uInk.value = lerpKeys(o.keys, f, 'ink', o.ink ?? 1); U.uLum.value = lerpKeys(o.keys, f, 'lum', o.lum ?? 1);
        if (o.keys.some((k) => k[1].tint !== undefined)) U.uTint.value.setRGB(...lerpKeys(o.keys, f, 'tint', o.tint || [1, 1, 1]));
        U.uFogK.value = lerpKeys(o.keys, f, 'fogk', o.fogk ?? (kind === 'overlay' ? 0 : 1)); U.uSeaK.value = lerpKeys(o.keys, f, 'seak', o.seak ?? (kind === 'overlay' ? 0 : 1)); }
      if (o.light) U.uLight.value.set(...lerpKeys(o.keys, f, 'light', o.light.v || [0.5, 0.05, 1, 0]));
      if (o.light2) U.uLight2.value.set(...lerpKeys(o.keys, f, 'light2', o.light2.v || [0.5, 0.05, 1, 0]));
    } else if (o.light) U.uLight.value.set(...(o.light.v || [0.5, 0.05, 1, 0]));
    if (U.uHasTrue && U.uHasTrue.value > 0.5) { U.uPosNow.value.copy(mesh.position); U.uScaleNow.value = mesh.scale.x; }
    if (o.anim) await animTex(mesh, o, f);
    mesh.visible = U.uOpacity.value > 0.001 && (o.visible === undefined || (f >= o.visible[0] && f <= o.visible[1]));
  }
  const bg = pass !== 'beauty' ? [0, 0, 0] : (c.paper || S.paper || [0.925, 0.886, 0.8]);
  renderer.setClearColor(new THREE.Color(...bg), 1);
  renderer.setRenderTarget(rtA); renderer.clear(); renderer.render(sceneA, cam);
  renderer.setRenderTarget(rtB); renderer.clear(); copyMat.uniforms.uTex.value = rtA.texture; renderer.render(copyScene, blitCam);
  renderer.autoClear = false; renderer.render(sceneB, cam); renderer.autoClear = true;
  renderer.setRenderTarget(null); blitMat.uniforms.uTex.value = rtB.texture; renderer.render(blitScene, blitCam);
  return renderer.domElement.toDataURL('image/png');
};
window.__renderer = renderer;
window.__ready = Promise.resolve(true);

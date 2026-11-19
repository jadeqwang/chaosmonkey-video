// Shared GLSL chunks.
export const NOISE = /* glsl */`
vec3 mod289(vec3 x){return x-floor(x*(1./289.))*289.;}
vec4 mod289(vec4 x){return x-floor(x*(1./289.))*289.;}
vec4 permute(vec4 x){return mod289(((x*34.)+1.)*x);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){
  const vec2 C=vec2(1./6.,1./3.);const vec4 D=vec4(0.,.5,1.,2.);
  vec3 i=floor(v+dot(v,C.yyy));vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz);vec3 l=1.-g;vec3 i1=min(g.xyz,l.zxy);vec3 i2=max(g.xyz,l.zxy);
  vec3 x1=x0-i1+C.xxx;vec3 x2=x0-i2+C.yyy;vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=permute(permute(permute(i.z+vec4(0.,i1.z,i2.z,1.))+i.y+vec4(0.,i1.y,i2.y,1.))+i.x+vec4(0.,i1.x,i2.x,1.));
  float n_=0.142857142857;vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.*floor(p*ns.z*ns.z);vec4 x_=floor(j*ns.z);vec4 y_=floor(j-7.*x_);
  vec4 x=x_*ns.x+ns.yyyy;vec4 y=y_*ns.x+ns.yyyy;vec4 h=1.-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy);vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.+1.;vec4 s1=floor(b1)*2.+1.;vec4 sh=-step(h,vec4(0.));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy;vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x);vec3 p1=vec3(a0.zw,h.y);vec3 p2=vec3(a1.xy,h.z);vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
  p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
  vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.);m=m*m;
  return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}
float fbm3(vec3 p){float s=0.,a=.5;for(int i=0;i<4;i++){s+=a*snoise(p);p=p*2.03+vec3(1.7,9.2,3.1);a*=.5;}return s;}
float fbm5(vec3 p){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*snoise(p);p=p*2.03+vec3(1.7,9.2,3.1);a*=.5;}return s;}
float hash12(vec2 p){vec3 p3=fract(vec3(p.xyx)*.1031);p3+=dot(p3,p3.yzx+33.33);return fract((p3.x+p3.y)*p3.z);}
`;

// aerial haze + valley mist, applied to anything solid in the world (uniform names shared by every material)
export const FOG = /* glsl */`
uniform vec3 uHazeCol; uniform float uHazeDist; uniform float uHazeMax;
uniform vec3 uMistCol; uniform float uMistY; uniform float uMistH; uniform float uMistAmt; uniform float uS;
uniform vec3 uCamPos;
// exponential height fog: thick near the cloud sea, thin up high (so the apex view stays clear)
float hazeAmt(vec3 wp){
  float dist = length(wp - uCamPos);
  float H = 700.;
  float y0 = max(wp.y, 0.), y1 = max(uCamPos.y, 0.);
  float k = abs(y1 - y0) < 1. ? exp(-y0 / H) : H * (exp(-y0 / H) - exp(-y1 / H)) / (y1 - y0);
  k = abs(k);
  return uHazeMax * (1. - exp(-dist / uHazeDist * k * 1.4));
}
vec3 applyFog(vec3 col, vec3 wp, float lm){
  float dist = length(wp - uCamPos);
  float hz = hazeAmt(wp);
  // valley mist, broken by slow noise; thicker the lower
  float n = .5 + .5 * fbm3(vec3(wp.xz * .0021 + vec2(uS * .0016, uS * .0007), wp.y * .004));
  float m = exp(-max(0., wp.y - uMistY) / uMistH) * smoothstep(.15, .75, n);
  m = clamp(m * uMistAmt * smoothstep(5., 90., dist), 0., .96);
  vec3 mc = uMistCol + vec3(1., .62, .3) * lm * .25;
  col = mix(col, mc, m);
  return mix(col, uHazeCol, hz);
}
`;

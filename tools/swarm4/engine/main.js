// SWARM v4 page API: swarmInit(cand, w, h), renderFrame(s, pass, opts) -> PNG data URL, swarmTree(), swarmCamera(s)
import * as THREE from 'three';
import { DEFAULTS } from './config.js';
import { makeTerrain, deepMerge } from './terrain.js';
import { terrainMaterial, ndMaterial, skyMaterial, fogUniforms } from './look.js';
import { makePost } from './post.js';
import { makeCameraPath } from './camera.js';
import { loadMask } from './silhouette.js';
import { buildTree, timeTree } from './tree.js';
import { makeSwarm, secondPlace } from './swarm.js';
import { makeMist } from './mist.js';
import { makePines } from './pines.js';

let R = null;
const keyed = (arr, s) => {       // piecewise-linear [[s, v], ...]
  if (s <= arr[0][0]) return arr[0][1];
  for (let i = 0; i < arr.length - 1; i++) if (s < arr[i + 1][0]) { const t = (s - arr[i][0]) / (arr[i + 1][0] - arr[i][0]); const e = t * t * (3 - 2 * t); return arr[i][1] + (arr[i + 1][1] - arr[i][1]) * e; }
  return arr[arr.length - 1][1];
};

window.swarmInit = async function (cand, W, H) {
  const cfg = deepMerge(structuredClone(DEFAULTS), cand);
  const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H; document.body.appendChild(canvas);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false);
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
  renderer.autoClear = false;
  const gl = renderer.getContext(); const ext = gl.getExtension('WEBGL_debug_renderer_info');
  const rendererName = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'webgl';

  const terrain = makeTerrain(cfg.terrain);
  const L = cfg.look;
  const shared = fogUniforms(L);
  const scene = new THREE.Scene(), ndScene = new THREE.Scene();
  const geo = terrain.buildMesh();
  const tmat = terrainMaterial(L, shared);
  const tmesh = new THREE.Mesh(geo, tmat); tmesh.frustumCulled = false; scene.add(tmesh);
  const ndm = new THREE.Mesh(geo, ndMaterial()); ndm.frustumCulled = false; ndScene.add(ndm);
  const sky = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24), skyMaterial(L)); sky.scale.setScalar(20000); sky.frustumCulled = false; sky.renderOrder = -10;
  scene.add(sky);
  const cam = new THREE.PerspectiveCamera(40, cfg.aspect || W / H, 0.1, 30000);
  cam.aspect = W / H;

  // apex camera (the silhouette projection) and the tree
  const ap = cfg.camera.apex;
  const refs = { ledge: terrain.ledge.clone(), origin: new THREE.Vector3() };
  const apexCam = new THREE.PerspectiveCamera(ap.fov, cfg.aspect, 1, 30000);
  const resolveSimple = (p) => (Array.isArray(p) ? new THREE.Vector3(...p) : refs[p.ref].clone().add(new THREE.Vector3(...(p.off || [0, 0, 0]))));
  apexCam.position.copy(resolveSimple(ap.pos)); apexCam.lookAt(resolveSimple(ap.target)); apexCam.updateMatrixWorld(true); apexCam.updateProjectionMatrix();
  refs.apex = apexCam.position.clone(); refs.apex_target = resolveSimple(ap.target);
  const mask = await loadMask(cfg.silhouette.image ? '/' + cfg.silhouette.image : null, !!cfg.silhouette.invert);
  const tree = timeTree(buildTree(cfg, terrain, apexCam, mask, cfg.aspect), cfg);
  refs.root = tree.nodes[0].pos.clone();
  refs.second = secondPlace(cfg, terrain, tree.nodes[0]).pos;
  const ctx = {
    refs, nodes: tree.nodes,
    nearest(gen, to, rank, below) {
      const c = tree.nodes.filter((n) => n.gen === gen && (below === undefined || n.pos.y < to.y - below));
      c.sort((a, b) => a.pos.distanceTo(to) - b.pos.distanceTo(to));
      return c[Math.min(rank, c.length - 1)].pos.clone();
    },
  };
  const camPath = makeCameraPath(cfg.camera, ctx);

  const post = makePost(renderer, W, H, cfg.post);
  const swarm = await makeSwarm(cfg, { scene, terrain, tree, renderer, shared, cam, W, H, refs, camPath, apexCam });
  const mist = cfg.mist.on ? await makeMist(cfg, { scene, shared, nd: post.nd, W, H, lm: swarm.lightmap }) : null;
  const pines = cfg.pines.count > 0 ? makePines(cfg, { scene, terrain, shared, lm: swarm.lightmap, mask, apexCam, tree }) : null;
  tmat.uniforms.uLM.value = swarm.lightmap.texture; tmat.uniforms.uLB.value = swarm.lightBuffer.texture; tmat.uniforms.uLMBox.value.copy(swarm.lmBox);
  tmat.uniforms.uND.value = post.nd.texture; tmat.uniforms.uRes.value.set(W, H);

  // painted plates projected onto the terrain: [{ image, frame: s | camera: {pos, target, fov}, amount }]
  for (const [k, pj] of (cfg.projectors || []).slice(0, 4).entries()) {
    const img = new Image(); img.src = '/' + pj.image;
    try { await img.decode(); } catch (e) { console.warn('[swarm] projector image ' + pj.image + ' missing'); continue; }
    const pc = new THREE.PerspectiveCamera(40, img.width / img.height, 0.1, 30000);
    if (pj.frame !== undefined) { camPath.apply(pc, pj.frame); pc.aspect = img.width / img.height; pc.updateProjectionMatrix(); }
    else { const C = pj.camera; pc.fov = C.fov || 40; pc.position.copy(resolveSimple(C.pos)); pc.lookAt(resolveSimple(C.target)); pc.updateProjectionMatrix(); }
    pc.updateMatrixWorld(true);
    const rt = new THREE.WebGLRenderTarget(1024, Math.round(1024 * img.height / img.width), { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
    renderer.setRenderTarget(rt); renderer.setClearColor(new THREE.Color(0.5, 0.5, 1), 1e7); renderer.clear(); renderer.render(ndScene, pc); renderer.setRenderTarget(null);
    const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.needsUpdate = true;
    const U = tmat.uniforms;
    U['uPT' + k].value = tex; U['uPD' + k].value = rt.texture; U['uPM' + k].value.multiplyMatrices(pc.projectionMatrix, pc.matrixWorldInverse);
    U.uPExpo.value = cfg.post.exposure; U['uPP' + k].value.copy(pc.position); U['uPA' + k].value = pj.amount ?? 1;
  }
  window.__R = R = { cfg, renderer, scene, ndScene, cam, terrain, tmat, sky, post, camPath, tree, swarm, mist, pines, shared, W, H, rendererName, apexCam, mask };
  return { renderer: rendererName, nodes: tree.nodes.length, ledge: terrain.ledge.toArray() };
};

function applyCam(s) {
  const { cfg, cam, camPath, terrain } = R;
  camPath.apply(cam, s);
  const clr = cfg.camera.min_clear ?? 0.6;
  let hmax = -1e9;
  for (const [dx, dz] of [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1]]) hmax = Math.max(hmax, terrain.height(cam.position.x + dx, cam.position.z + dz));
  if (cam.position.y < hmax + clr) { cam.position.y = hmax + clr; cam.lookAt(camPath.at(s).T); cam.updateMatrixWorld(true); }
}

function drawFrame(s, pass) {
  const { cfg, renderer, scene, ndScene, cam, tmat, sky, post, camPath, swarm, mist, pines, shared } = R;
  applyCam(s);
  shared.uS.value = s; shared.uCamPos.value.copy(cam.position);
  const range = keyed(cfg.range_light, s), outline = keyed(cfg.outline, s);
  tmat.uniforms.uRange.value = range; tmat.uniforms.uOutline.value = outline;
  sky.material.uniforms.uRange.value = range; sky.material.uniforms.uS.value = s;
  sky.position.copy(cam.position);
  swarm.update(s, cam, range);
  if (mist) mist.update(s, cam, range);
  if (pines) pines.update(s, range);
  // normal + depth of the terrain (edge detector input; soft mist)
  renderer.setRenderTarget(post.nd); renderer.setClearColor(new THREE.Color(0.5, 0.5, 1), 1e7); renderer.clear(true, true, true);
  renderer.render(ndScene, cam);
  if (pass === 'depth') { renderer.setRenderTarget(null); post.dump.render(renderer); return; }
  swarm.renderLightmap(renderer);
  swarm.renderLightBuffer(renderer, cam, post.nd);
  renderer.setRenderTarget(post.hdr); renderer.setClearColor(0x000000, 1); renderer.clear(true, true, true);
  swarm.setIds(pass === 'ids');
  const guide = pass === 'guide';
  tmat.uniforms.uIds.value = pass === 'ids' ? 1 : 0; tmat.uniforms.uGuide.value = guide ? 1 : 0; sky.material.uniforms.uGuide.value = guide ? 1 : 0;
  sky.visible = pass !== 'ids'; if (mist) mist.group.visible = pass !== 'ids' && !guide; if (pines) pines.mesh.visible = pass !== 'ids';
  if (guide) { shared.uHazeMax.value = 0; shared.uMistAmt.value = 0; } else { shared.uHazeMax.value = cfg.look.haze_max; shared.uMistAmt.value = cfg.look.mist_amt; }
  swarm.setGuide(guide);
  swarm.heroLights.forEach((h, k) => { tmat.uniforms.uHLP.value[k].copy(h.pos); tmat.uniforms.uHLI.value[k] = h.i; });
  renderer.render(scene, cam);
}

window.renderFrame = async function (s, pass = 'beauty', opts = {}) {
  const { renderer, post, cfg } = R;
  await R.swarm.prepare(s); if (R.mist) await R.mist.prepare(s);
  const mb = Math.max(0, opts.mb || 0);
  if (mb > 1 && pass === 'beauty') {
    renderer.setRenderTarget(post.acc); renderer.setClearColor(0x000000, 1); renderer.clear(true, true, true);
    const shutter = cfg.motion_blur_shutter ?? 0.5;
    for (let i = 0; i < mb; i++) { drawFrame(s + ((i + 0.5) / mb - 0.5) * shutter, pass); post.finish(true, 1 / mb); }
    renderer.setRenderTarget(null); post.copy.render(renderer);
  } else {
    drawFrame(s, pass);
    if (pass === 'ids' || pass === 'guide') { renderer.setRenderTarget(null); post.copy.material.uniforms.t.value = post.hdr.texture; post.copy.render(renderer); post.copy.material.uniforms.t.value = post.acc.texture; }
    else if (pass !== 'depth') post.finish(false, 1);
  }
  return renderer.domElement.toDataURL('image/png');
};

window.swarmTree = function () {
  const r = (v) => Math.round(v * 100) / 100;
  return {
    cand: R.cfg.name, counts: R.cfg.tree.counts, ledge: R.terrain.ledge.toArray().map(r), second: R.swarm.secondPos.toArray().map(r),
    silhouette_placeholder: R.mask.placeholder,
    apex: { position: R.apexCam.position.toArray().map(r), matrixWorld: R.apexCam.matrixWorld.elements, projectionMatrix: R.apexCam.projectionMatrix.elements, fov: R.apexCam.fov, aspect: R.apexCam.aspect },
    nodes: R.tree.nodes.map((n) => ({ id: n.id, parent: n.parent, gen: n.gen, job: n.job, branch: n.branch, position: n.pos.toArray().map(r),
      depart: n.depart != null ? r(n.depart) : null, land: r(n.land), blow: n.blow != null ? r(n.blow) : null, seal: n.seal != null ? r(n.seal) : null,
      switches: n.switches.map(r) })),
  };
};

window.swarmCamera = function (s) {
  const c = R.cam; applyCam(s);
  return { s, t: R.cfg.t0 + s / R.cfg.fps, position: c.position.toArray(), quaternion: c.quaternion.toArray(), fov: c.fov, aspect: c.aspect,
    matrixWorld: c.matrixWorld.elements, projectionMatrix: c.projectionMatrix.elements, near: c.near, far: c.far };
};

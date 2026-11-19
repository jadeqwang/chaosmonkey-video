// Headless renderer for the 3D painted world (GPU: Chrome + ANGLE/Vulkan on the RTX 3090; --swiftshader to force CPU).
//   node tools/world/render.mjs --scene work/world/B3/scene.json --out work/world/B3/frames [--w 1920 --h 1080]
//        [--frames 0:76 | --frames 0,10,20] [--passes beauty,glow] [--ss 2]
// Writes <out>/<pass>/<frame:04d>.png. Texture paths in the scene are repo-relative.
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '../..');
const THREE_DIR = process.env.THREE_DIR || '/home/jade/Documents/merge-me-back-to-main/engine/node_modules/three';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE || '/home/jade/Documents/1-music-shipped/moongazing/render/node_modules/playwright-core');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };

const argv = process.argv.slice(2); const args = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) args[argv[i].slice(2)] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
const scenePath = path.resolve(REPO, args.scene);
const scene = JSON.parse(fs.readFileSync(scenePath, 'utf8'));
const W = Number(args.w || scene.w || 1920), H = Number(args.h || scene.h || 1080), SSx = Number(args.ss || scene.ss || 1);
const OUT = path.resolve(REPO, args.out || path.join(path.dirname(args.scene), 'frames'));
const passes = String(args.passes || scene.passes || 'beauty').split(',');
const N = scene.camera.length;
let frames = [...Array(N).keys()];
if (args.frames) {
  const s = String(args.frames);
  if (s.includes(':')) { const [a, b] = s.split(':').map(Number); frames = frames.filter((f) => f >= a && f < b); }
  else frames = s.split(',').map(Number);
}

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p === '/') p = '/index.html';
  let file;
  if (p.startsWith('/three/')) file = path.join(THREE_DIR, p.slice(7));
  else if (p.startsWith('/repo/')) file = path.join(REPO, p.slice(6));
  else file = path.join(HERE, p);
  if (!file.startsWith(REPO + path.sep) && !file.startsWith(THREE_DIR + path.sep)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(data);
  });
});
const port = 9300 + (process.pid % 500);
await new Promise((r) => server.listen(port, '127.0.0.1', r));
const gl = args.swiftshader ? ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader']
  : ['--use-gl=angle', '--use-angle=vulkan', '--enable-features=Vulkan', '--ignore-gpu-blocklist', '--enable-gpu'];
const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/google/chrome/chrome', args: [...gl, '--disable-gpu-sandbox', '--headless=new', '--force-color-profile=srgb'] });
let code = 0;
try {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type()) && !/GPU stall|swiftshader|WebGL: INVALID|Automatic fallback/i.test(m.text())) console.error('[page]', m.text()); });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html?w=${W}&h=${H}&ss=${SSx}`);
  await page.waitForFunction(() => window.__ready !== undefined, null, { timeout: 60000 });
  // ANGLE/Vulkan in headless Chrome loses the first context and restores it a moment later: wait until it is live
  await page.waitForFunction(() => !window.__renderer.getContext().isContextLost(), null, { timeout: 60000, polling: 100 });
  await new Promise((r) => setTimeout(r, 300));
  const t0 = Date.now();
  const info = await page.evaluate(async (s) => window.loadScene(s), scene);
  console.log(`world: loaded ${args.scene} (${JSON.stringify(info)}) in ${Date.now() - t0} ms; ${frames.length} frames x ${passes.join('+')} at ${W}x${H} ss${SSx}`);
  for (const ps of passes) fs.mkdirSync(path.join(OUT, ps), { recursive: true });
  const t1 = Date.now();
  for (const f of frames) for (const ps of passes) {
    const url = await page.evaluate(async ([i, p]) => window.renderFrame(i, p), [f, ps]);
    fs.writeFileSync(path.join(OUT, ps, String(f).padStart(4, '0') + '.png'), Buffer.from(url.split(',')[1], 'base64'));
  }
  console.log(`world: ${frames.length} frames in ${((Date.now() - t1) / 1000).toFixed(1)} s -> ${path.relative(REPO, OUT)}`);
} catch (e) { console.error('world: FAILED', e.message); code = 1; } finally { await browser.close(); server.close(); }
process.exit(code);

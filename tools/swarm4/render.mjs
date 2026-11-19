// SWARM v4: render the one 176-frame swarm shot headless.
//   node tools/swarm4/render.mjs --cand work/swarm/cand_A.json --out work/swarm/render/A [--w 960 --h 540]
//        [--frames 0-175 | --frames 0,40,80] [--pass beauty|depth|ids] [--mb 4] [--gl gpu|swiftshader] [--cams]
// Output: <out>/f0000.png ... (beauty) or <out>/<pass>_0000.png; work/swarm/tree_<cand>.json; with --cams, <out>/cams.json
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { serve, REPO } from './serve.mjs';

const require = createRequire(import.meta.url);
const PW = process.env.PLAYWRIGHT_CORE || '/home/jade/Documents/1-music-shipped/moongazing/render/node_modules/playwright-core';
const { chromium } = require(PW);
const argv = process.argv.slice(2); const args = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) args[argv[i].slice(2)] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
if (!args.cand) { console.error('need --cand'); process.exit(2); }
const candPath = path.resolve(args.cand);
const cand = JSON.parse(fs.readFileSync(candPath, 'utf8'));
const candName = cand.name || path.basename(candPath, '.json').replace(/^cand_/, '');
const W = Number(args.w || 960), H = Number(args.h || 540);
const PASSES = String(args.pass || 'beauty').split(',');
if (PASSES.includes('guide') && !PASSES.includes('depth')) PASSES.push('depth');
const OUT = path.resolve(args.out || path.join(REPO, 'work/swarm/render', candName));
fs.mkdirSync(OUT, { recursive: true });
const NF = cand.frames || 176;
function parseFrames(spec) {
  if (!spec || spec === true) return [...Array(NF).keys()];
  const out = [];
  for (const part of String(spec).split(',')) {
    const m = part.match(/^(\d+)-(\d+)$/);
    if (m) for (let i = +m[1]; i <= +m[2]; i++) out.push(i); else out.push(Number(part));
  }
  return out;
}
const frames = parseFrames(args.frames);

// mist video -> PNG frames (cached), so the page only ever loads stills
const mv = cand.mist && cand.mist.video;
if (mv && fs.existsSync(path.join(REPO, mv))) {
  const dir = path.join(REPO, 'work/swarm/cache', 'mist_' + path.basename(mv, path.extname(mv)));
  if (!fs.existsSync(path.join(dir, '0001.png'))) {
    fs.mkdirSync(dir, { recursive: true });
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', path.join(REPO, mv), '-vf', 'scale=512:-2,format=gray', path.join(dir, '%04d.png')]);
  }
  cand.mist.video_frames = path.relative(REPO, dir);
  cand.mist.video_count = fs.readdirSync(dir).filter((f) => f.endsWith('.png')).length;
} else if (mv) console.error(`[mist] ${mv} not found, procedural mist only`);

const GL = {
  gpu: ['--use-gl=angle', '--use-angle=gl', '--ignore-gpu-blocklist', '--enable-gpu'],
  vulkan: ['--use-gl=angle', '--use-angle=vulkan', '--enable-features=Vulkan', '--ignore-gpu-blocklist', '--enable-gpu'],
  swiftshader: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
};
const port = 9300 + (process.pid % 400);
const server = await serve(port);
const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/google/chrome/chrome',
  args: [...(GL[args.gl || 'gpu'] || GL.gpu), '--disable-gpu-sandbox', '--force-color-profile=srgb', '--js-flags=--max-old-space-size=8192'] });
let failed = 0;
try {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('console', (m) => { const t = m.text(); if (/GPU stall|swiftshader|Automatic fallback/i.test(t)) return; if (['error', 'warning'].includes(m.type()) || t.startsWith('[swarm]')) console.error('[page]', t); });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.goto(`http://127.0.0.1:${port}/tools/swarm4/index.html`);
  await page.waitForFunction(() => window.__loaded || window.__error, null, { timeout: 60000 });
  const t0 = Date.now();
  const info = await page.evaluate(async ([c, w, h]) => { try { return await window.swarmInit(c, w, h); } catch (e) { return { error: String(e && e.stack || e) }; } }, [cand, W, H]);
  if (info.error) throw new Error(info.error);
  console.log(`init ${Date.now() - t0} ms: ${info.renderer}; ${info.nodes} monkeys`);
  const tree = await page.evaluate(() => window.swarmTree());
  fs.writeFileSync(path.join(REPO, 'work/swarm', `tree_${candName}.json`), JSON.stringify(tree));
  const cams = {};
  let tot = 0;
  for (const s of frames) {
    try {
      const t = Date.now();
      for (const PASS of PASSES) {
        const url = await page.evaluate(([ss, p, mb]) => window.renderFrame(ss, p, { mb }), [s, PASS, Number(args.mb || 0)]);
        const name = PASS === 'beauty' ? `f${String(s).padStart(4, '0')}.png` : `${PASS}_${String(s).padStart(4, '0')}.png`;
        fs.writeFileSync(path.join(OUT, name), Buffer.from(url.split(',')[1], 'base64'));
      }
      const dt = Date.now() - t; tot += dt;
      if (args.cams) cams[s] = await page.evaluate((ss) => window.swarmCamera(ss), s);
      if (frames.length < 20 || s % 10 === 0) console.log(`s${s} ${PASSES.join('+')} ${dt} ms`);
    } catch (e) { failed++; console.error(`FAILED s${s}: ${e.message}`); }
  }
  console.log(`${frames.length} frames (${PASSES.join('+')}), mean ${(tot / Math.max(1, frames.length)).toFixed(0)} ms/frame at ${W}x${H}`);
  if (args.cams) fs.writeFileSync(path.join(OUT, 'cams.json'), JSON.stringify(cams, null, 1));
} finally { await browser.close(); server.close(); }
if (failed) { console.error(`${failed} frame(s) failed`); process.exit(1); }

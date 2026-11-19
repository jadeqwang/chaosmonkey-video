// Typeset text (never drawn by a model): 榜题 name slips and the seals 讫 / 真, drawn into one canvas atlas.
import * as THREE from 'three';
import { mulberry32 } from './rng.js';

export async function loadFonts(cfg) {
  const T = cfg.text || {};
  const fonts = [['SwarmBrush', T.font || 'refs/fonts/mashanzheng/MaShanZheng-Regular.ttf'], ['SwarmSeal', T.seal_font || T.font || 'refs/fonts/mashanzheng/MaShanZheng-Regular.ttf']];
  for (const [fam, url] of fonts) {
    try { const f = new FontFace(fam, `url(/${url})`); await f.load(); document.fonts.add(f); } catch (e) { console.warn('[swarm] font ' + url + ': ' + e); }
  }
}

// cell layout: [slip x 8 jobs][seal 讫][seal 真]
export function buildCards(cfg) {
  const jobs = cfg.tree.jobs;
  const CW = 256, CH = 512;
  const n = jobs.length + 2;
  const c = document.createElement('canvas'); c.width = CW * n; c.height = CH;
  const g = c.getContext('2d');
  const frames = {};
  const rnd = mulberry32(42);
  // name slips: pale paper, ink border, one job character (vertical slip, 1:3)
  jobs.forEach((j, i) => {
    const x0 = i * CW, w = CW * 0.62, h = CH * 0.94, ox = x0 + (CW - w) / 2, oy = (CH - h) / 2;
    g.fillStyle = '#e9dfc6'; g.fillRect(ox, oy, w, h);
    // paper tone mottling
    for (let k = 0; k < 140; k++) { g.fillStyle = `rgba(150,120,80,${0.03 + rnd() * 0.05})`; g.beginPath(); g.arc(ox + rnd() * w, oy + rnd() * h, 2 + rnd() * 10, 0, Math.PI * 2); g.fill(); }
    g.strokeStyle = '#17130f'; g.lineWidth = 7; g.strokeRect(ox + 6, oy + 6, w - 12, h - 12);
    g.lineWidth = 2; g.strokeRect(ox + 16, oy + 16, w - 32, h - 32);
    g.fillStyle = '#121010'; g.font = `${Math.round(w * 0.72)}px SwarmBrush`; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(j, ox + w / 2, oy + h * 0.36);
    frames['slip:' + j] = { rect: [x0 / c.width, 0, CW / c.width, 1], aspect: CW / CH };
  });
  // seals: cinnabar square, white (reserved) character, worn edge
  const seal = (ch, i, style) => {
    const x0 = i * CW, s = CW * 0.86, ox = x0 + (CW - s) / 2, oy = (CH - s) / 2;
    g.fillStyle = '#b8291f';
    g.beginPath();
    const jag = (k) => (rnd() - 0.5) * 6;
    g.moveTo(ox + jag(), oy + jag()); g.lineTo(ox + s + jag(), oy + jag()); g.lineTo(ox + s + jag(), oy + s + jag()); g.lineTo(ox + jag(), oy + s + jag()); g.closePath(); g.fill();
    g.fillStyle = '#f4ead8'; g.font = `${Math.round(s * 0.74)}px SwarmSeal`; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(ch, ox + s / 2, oy + s * 0.53);
    g.strokeStyle = '#f4ead8'; g.lineWidth = 5; g.strokeRect(ox + 12, oy + 12, s - 24, s - 24);
    // wear: knock out a few specks
    g.globalCompositeOperation = 'destination-out';
    for (let k = 0; k < 60; k++) { g.beginPath(); g.arc(ox + rnd() * s, oy + rnd() * s, rnd() * 3.5, 0, Math.PI * 2); g.fill(); }
    g.globalCompositeOperation = 'source-over';
    frames['seal:' + ch] = { rect: [x0 / c.width, 0, CW / c.width, 1], aspect: CW / CH };
  };
  seal(cfg.text?.seal_done || '讫', jobs.length);
  seal(cfg.text?.seal_true || '真', jobs.length + 1);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { tex, frames, canvas: c };
}

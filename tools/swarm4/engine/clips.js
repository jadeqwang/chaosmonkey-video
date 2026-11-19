// Video billboards for the heroes (root / second) near the camera: RGBA PNG frame sequences from
// media/swarm4/clips/<name>/ with clip.json {fps, anchor: [x, y] px (feet), top: px (head top, optional),
// frames: N, pattern: "%04d.png" (or files: [...]), first: 1}. Scheduled in cand.assets.clips:
// [{ who: "root" | "second", clip: "<name>", from: s, to: s, start: 0, speed: 1, min_px: 80, loop: false }]
import * as THREE from 'three';

export async function makeClips(cfg) {
  const A = cfg.assets || {};
  const dir = A.clips_dir || 'media/swarm4/clips';
  const sched = (A.clips || []).map((c) => ({ min_px: 80, start: 0, speed: 1, ...c }));
  const meta = {};
  for (const c of sched) {
    if (meta[c.clip] !== undefined) continue;
    try {
      const r = await fetch(`/${dir}/${c.clip}/clip.json`);
      meta[c.clip] = r.ok ? await r.json() : null;
      if (!r.ok) console.warn(`[swarm] clip ${c.clip} missing (sprite used instead)`);
    } catch (e) { meta[c.clip] = null; }
  }
  const cache = new Map();
  const tex = { root: new THREE.Texture(), second: new THREE.Texture() };
  for (const t of Object.values(tex)) t.colorSpace = THREE.SRGBColorSpace;
  const current = { root: null, second: null };
  const fileOf = (m, i) => {
    if (m.files) return m.files[Math.min(i, m.files.length - 1)];
    const pat = m.pattern || '%04d.png';
    return pat.replace(/%0(\d)d/, (_, w) => String(i + (m.first ?? 1)).padStart(Number(w), '0'));
  };
  function active(who, s) {
    return sched.find((c) => c.who === who && s >= c.from && s < c.to && meta[c.clip]);
  }
  async function prepare(s) {
    for (const who of ['root', 'second']) {
      const c = active(who, s);
      if (!c) { current[who] = null; continue; }
      const m = meta[c.clip], fps = m.fps || 24;
      const n = m.frames || (m.files ? m.files.length : 1);
      let i = Math.floor(c.start + (s - c.from) * c.speed * fps / (cfg.fps || 24));
      i = c.loop ? ((i % n) + n) % n : Math.min(n - 1, Math.max(0, i));
      const url = `/${dir}/${c.clip}/${fileOf(m, i)}`;
      if (!cache.has(url)) {
        const img = new Image(); img.src = url;
        try { await img.decode(); } catch (e) { console.warn('[swarm] clip frame ' + url + ' failed'); current[who] = null; continue; }
        cache.set(url, img);
        if (cache.size > 400) cache.delete(cache.keys().next().value);
      }
      const img = cache.get(url);
      tex[who].image = img; tex[who].needsUpdate = true;
      const an = m.anchor || [img.width / 2, img.height * 0.97];
      current[who] = { tex: tex[who], anchor: [an[0] / img.width, an[1] / img.height], aspect: img.width / img.height,
        hfrac: m.top != null ? (an[1] - m.top) / img.height : an[1] / img.height * 0.92, min_px: c.min_px };
    }
  }
  return {
    prepare,
    frameFor(who, s, pose, px = 1e9) { const c = current[who]; return c && px >= c.min_px ? c : null; },
    sched,
  };
}

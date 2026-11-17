#!/usr/bin/env python3
"""Build the local review page for a preview cut: timestamped notes, likeness notes, decisions.

  python tools/review/notes_page.py [--name preview_v2]

Writes review/<name>_notes.html and review/likeness/*.jpg (film stills and downscaled reference sheets).
Everything is local: the page reads the video from previews/ and keeps notes in the browser's localStorage.
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

# character -> her references, my canon sheets, and (shot, seconds into the shot) for the film stills
CHARS = [
    dict(id="little_jade", name="Little Jade, 1988 (age 5)", kind="girl",
         noted="Already noted (17 Nov): no bangs covering the forehead; hair curtained to the sides, almost like layers. The redrawn sheets are below; the film frames still show the old hair.",
         new=["design/characters/little_jade/lj_A_turnaround_v2.jpg", "design/characters/little_jade/lj_C_expressions_mouths_v2.jpg",
              "design/characters/little_jade/lj_B_poses_v2.jpg"],
         refs=["inputs/ref_merge_little_jade_face.jpg", "inputs/ref_merge_little_jade_fullbody.jpg"],
         canon=["design/characters/little_jade/lj_C_expressions_mouths.jpg",
                "design/characters/little_jade/lj_A_turnaround.jpg"],
         stills=[("A3", 1.5), ("B1", 1.5), ("B1", 5.0), ("B2", 2.0), ("C3", 1.5), ("D3", 2.2), ("D9", 1.5),
                 ("E1", 2.7), ("E3", 1.5), ("E3", 5.0), ("E6", 1.0), ("E6", 2.6), ("F3", 1.4), ("G1", 2.0), ("G3", 1.0), ("G3", 5.8),
                 ("G5", 1.0), ("G5", 2.4)]),
    dict(id="daughter", name="The daughter, 2026 (age 4)", kind="girl",
         refs=["inputs/ref_moongazing_daughter_strawberry_dress_sheet.jpg"],
         canon=["design/characters/daughter/daughter_A_turnaround.jpg",
                "design/characters/daughter/daughter_B_poses_mouths.jpg"],
         stills=[("F1", 0.4), ("F1", 1.3), ("F3", 0.4), ("F3", 0.9), ("F4", 0.8), ("I1", 1.5), ("I3", 0.4),
                 ("I3", 1.2), ("K1", 2.0), ("K1", 5.5), ("K2", 0.7), ("L1", 3.8)]),
    dict(id="mama", name="Mama, 1988 (about 30)", kind="adult",
         refs=["inputs/ref_moongazing_teahouse_jade_mom_daughter.png"],
         canon=["design/characters/mama/mama_A_turnaround.jpg", "design/characters/mama/mama_B_expressions.jpg"],
         stills=[("A3", 2.4), ("B2", 1.0), ("B2", 3.0), ("C3", 2.5), ("C5", 1.5), ("D3", 2.8), ("D9", 2.5),
                 ("E1", 1.2), ("E5", 0.5), ("E6", 1.8), ("I4", 0.15)]),
    dict(id="jade", name="Jade, 2026", kind="adult",
         noted="Already noted (17 Nov): no bangs covering the forehead; hair curtained to the sides, almost like layers. The redrawn sheets are below; the film frames still show the old hair.",
         new=["design/characters/jade/jade_A_turnaround_v2.jpg", "design/characters/jade/jade_B_expressions_details_v2.jpg"],
         refs=["inputs/ref_moongazing_jade_singing_watercolor_first_frame.jpg",
               "inputs/ref_moongazing_teahouse_jade_mom_daughter.png"],
         canon=["design/characters/jade/jade_A_turnaround.jpg", "design/characters/jade/jade_B_expressions_details.jpg"],
         stills=[("F4", 1.6), ("I1", 0.8), ("I1", 2.4), ("I4", 2.0), ("I4", 2.6), ("K1", 1.0), ("K1", 4.0),
                 ("L1", 4.2)]),
]

DECISIONS = [
    dict(id="direction", title="1. Is the direction right?",
         why="Three big calls: the paper becomes an opera stage in the loud sections; every glitch is done through "
             "a traditional twin (the frozen pose with a seal, mis-registered woodblock, rubbing flip, shadow "
             "puppets); people are painted in the storybook's line-and-wash hand.",
         opts=["Yes, keep going", "Mostly (say what to change)", "No (say why)"]),
    dict(id="lipsync", title="2. Lip-sync",
         why="The lip-sync model softens the painted faces toward a 3D-render look and the sync is loose. "
             "Three shots (3:23, 2:14, 1:52) play as an off-screen voice.",
         opts=["Keep singing faces; find a better method", "Cut more lines to hands, pages and shadows",
               "A mix (say which lines must be sung on screen)"]),
    dict(id="cliff_lyrics", title="3. Lyrics over the carved cliffs (0:29, 0:56, 1:10, 2:50)",
         why="On those four shots the lyric line sits on top of carved writing.",
         opts=["Keep the lyric there", "Drop the lyric on those four", "Drop on-screen lyrics everywhere"]),
    dict(id="ending", title="4. The ending's sound",
         why="The preview uses A. The others are media/sound/mix_v1_endB.wav and mix_v1_endC.wav.",
         opts=["A: the song's own hard cut", "B: the last note rings out for 3 more seconds",
               "C: hard cut, then 3 seconds of faint room tone", "Haven't compared yet"]),
    dict(id="neon", title="5. The opening's neon (0:00 to 0:15)",
         why="After a late change the attic is darker and the window stays mostly red; the earlier version cycled "
             "from red to cold blue.",
         opts=["Fine as it is", "Bring back the red-to-blue cycle"]),
    dict(id="rap_english", title="6. The English under the rap (1:47 to 2:01)",
         why="It is my working translation, not yours.",
         opts=["Fine", "I'll correct it (write the lines below)", "No English under the rap"]),
    dict(id="sound", title="7. The sound-design layer",
         why="47 cues sit under the song (seal thumps, brush, paper, neon hum, the flashlight click).",
         opts=["Good", "Too loud", "Too quiet, I barely heard it", "Remove (say which)"]),
    dict(id="next", title="8. What next",
         why="A third 540p pass with your notes, or go to the 1080p master.",
         opts=["Another 540p pass with my notes", "1080p master with my notes applied"]),
]

CAUSES = {
    "girl": ["Eyes too small, or no highlight in them", "Expression too flat or sullen (never soft, never smiling)",
             "Face too long or too old; head too small for the body", "Cheeks and blush lost; skin grey in the night light",
             "The singing shots change her face (3D look)", "Hair wrong", "It's the drawing style itself (line and wash vs. your watercolour)"],
    "adult": ["Doesn't look like the person", "Too old", "Too young", "Glasses or hair wrong",
              "The singing shots change the face (3D look)", "Clothes wrong"],
}

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chaos Monkey __NAME__: notes</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { color-scheme: dark; --bg:#121110; --panel:#1d1b19; --line:#3d3934; --ink:#f1e9d8; --dim:#b0a898; --acc:#e2572b; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.45 system-ui,sans-serif; }
  main { max-width:1560px; margin:0 auto; padding:16px; display:grid; grid-template-columns:minmax(0,1.5fr) minmax(340px,1fr); gap:18px; }
  @media (max-width:1050px){ main{ grid-template-columns:1fr; } }
  h1 { font-size:19px; margin:0 0 4px; } h2 { font-size:16px; margin:22px 0 8px; } h3 { font-size:14px; margin:0 0 6px; }
  p { margin:6px 0; color:var(--dim); }
  video { width:100%; background:#000; border-radius:6px; display:block; }
  .bar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:8px 0; }
  button, select, input[type=text], textarea { font:inherit; color:inherit; background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:7px 11px; }
  button { cursor:pointer; } button:hover { border-color:var(--acc); } button.primary { background:var(--acc); border-color:var(--acc); color:#160c08; font-weight:600; }
  textarea, input[type=text] { width:100%; }
  #pos { font:600 15px ui-monospace,monospace; }
  #lyric { color:var(--ink); min-height:1.45em; }
  #desc { font-size:13px; min-height:2.9em; }
  .note { display:grid; grid-template-columns:170px 1fr 30px; gap:8px; align-items:start; padding:6px 0; border-top:1px solid var(--line); }
  .note a, .jump { color:var(--acc); cursor:pointer; font:13px ui-monospace,monospace; text-decoration:none; }
  .note textarea { min-height:38px; resize:vertical; }
  .note button { padding:3px 8px; }
  .dec, .who { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px 14px; margin:10px 0; }
  .dec label, .who label { display:block; margin:4px 0; cursor:pointer; }
  kbd { background:#28251f; border:1px solid var(--line); border-radius:4px; padding:0 5px; font:12px ui-monospace,monospace; }
  #out { min-height:160px; font:12px ui-monospace,monospace; }
  .side { max-height:calc(100vh - 32px); overflow:auto; position:sticky; top:16px; }
  @media (max-width:1050px){ .side{ position:static; max-height:none; } }
  #like { max-width:1560px; margin:0 auto; padding:0 16px 60px; }
  .pair { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  @media (max-width:800px){ .pair{ grid-template-columns:1fr; } }
  .pair figure, .still { margin:0; }
  .pair img { max-width:100%; max-height:420px; border-radius:4px; display:block; margin-bottom:6px; }
  figcaption { font-size:12px; color:var(--dim); margin-bottom:4px; }
  .stills { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:12px; margin:12px 0; }
  .still img { width:100%; border-radius:4px; display:block; }
  .still textarea { min-height:34px; margin-top:4px; resize:vertical; font-size:13px; }
  .cols { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:0 18px; }
</style>
</head>
<body>
<main>
<section>
  <h1>Chaos Monkey, __NAME__: timestamped notes</h1>
  <p>Everything you type is kept in this browser and survives a reload. When you are done, press <b>Copy everything</b> in the right column and paste it to Claude, or download it as a file.</p>
  <div class="bar">
    <span>Video</span>
    <select id="src">__SOURCES__</select>
    <select id="rate"><option value="1">1x</option><option value="0.5">0.5x</option><option value="0.25">0.25x</option></select>
  </div>
  <video id="v" controls playsinline></video>
  <div class="bar"><span id="pos"></span></div>
  <div id="lyric"></div>
  <p id="desc"></p>
  <div class="bar">
    <button class="primary" id="add">Add note here (N)</button>
    <button id="ps">shot -</button><button id="b5">-5 s</button><button id="b1">-1 s</button><button id="pf">frame -</button>
    <button id="nf">frame +</button><button id="f1">+1 s</button><button id="f5">+5 s</button><button id="ns">shot +</button>
  </div>
  <p>Keys (when not typing): <kbd>N</kbd> add a note at the current time, <kbd>space</kbd> play or pause, <kbd>&larr;</kbd> <kbd>&rarr;</kbd> one second, <kbd>,</kbd> <kbd>.</kbd> one frame, <kbd>[</kbd> <kbd>]</kbd> previous or next shot, <kbd>Esc</kbd> leave a text box. Adding a note pauses the film and puts the cursor in the note.</p>
  <h2>Notes <span id="count" style="color:var(--dim);font-weight:400"></span></h2>
  <div id="notes"></div>
</section>

<section class="side">
  <h2 style="margin-top:0">Decisions Claude needs from you</h2>
  <div id="decisions"></div>
  <h2>Send it back</h2>
  <div class="bar"><button class="primary" id="copy">Copy everything</button><button id="dl">Download as a file</button><button id="clear">Clear all (asks first)</button></div>
  <textarea id="out" readonly></textarea>
</section>
</main>

<section id="like">
  <h2>Likenesses</h2>
  <p>For each person: your reference on the left, the sheet Claude drew from it on the right, then frames from this cut. Write under any frame. The time under a frame jumps the video there; clicking a picture opens it full size.</p>
  <div id="chars"></div>
</section>

<script>
const D = __DATA__;
const NEWOPTS = ['Use these','Close; fix what I wrote below','Not right'];
const FPS = 24, KEY = 'chaosmonkey___NAME___review';
let S = JSON.parse(localStorage.getItem(KEY) || '{}');
S.notes = S.notes || []; S.dec = S.dec || {}; S.like = S.like || {}; S.still = S.still || {};
const $ = id => document.getElementById(id);
const v = $('v'), src = $('src');
const save = () => { localStorage.setItem(KEY, JSON.stringify(S)); out(); };
function fmt(t){ const m=Math.floor(t/60), s=t-m*60; return m+':'+(s<10?'0':'')+s.toFixed(2); }
function shotAt(t){ let r=D.shots[0]; for(const s of D.shots) if(t>=s.in-1e-4) r=s; return r; }
function secAt(t){ let n=''; for(const [a,name] of D.sections) if(t>=a) n=name; return n; }
function lineAt(t){ return D.lines.filter(l=>t>=l.start-0.05 && t<=l.end+0.15).map(l=>l.text).join('  /  '); }
function label(t){ return fmt(t)+'  '+shotAt(t).id+'  '+secAt(t); }
let lastShot='';
function tick(){ const t=v.currentTime||0, s=shotAt(t);
  $('pos').textContent = fmt(t)+'   frame '+Math.floor(t*FPS+1e-3)+'   shot '+s.id+'   '+secAt(t);
  $('lyric').textContent = lineAt(t);
  if(s.id!==lastShot){ lastShot=s.id; $('desc').textContent = s.id+': '+s.desc; }
  requestAnimationFrame(tick); }
function load(){ const t=v.currentTime||0; v.src=src.value; v.playbackRate=+$('rate').value;
  v.addEventListener('loadedmetadata',()=>{ if(t>0 && t<v.duration) v.currentTime=t; },{once:true}); }
src.onchange=load; $('rate').onchange=e=>v.playbackRate=+e.target.value;
const seek=d=>{ v.currentTime=Math.max(0,v.currentTime+d); };
const frame=d=>{ v.pause(); v.currentTime=Math.max(0,(Math.round(v.currentTime*FPS)+d+0.5)/FPS); };
function shotStep(d){ const t=v.currentTime, i=D.shots.indexOf(shotAt(t));
  let j = d<0 ? (t-D.shots[i].in>0.5 ? i : i-1) : i+1; j=Math.max(0,Math.min(D.shots.length-1,j)); v.currentTime=D.shots[j].in+0.5/FPS; }
function jump(t){ v.currentTime=t; v.pause(); v.scrollIntoView({behavior:'smooth',block:'start'}); }
$('b5').onclick=()=>seek(-5); $('b1').onclick=()=>seek(-1); $('f1').onclick=()=>seek(1); $('f5').onclick=()=>seek(5);
$('pf').onclick=()=>frame(-1); $('nf').onclick=()=>frame(1); $('ps').onclick=()=>shotStep(-1); $('ns').onclick=()=>shotStep(1);

function addNote(){ v.pause(); const n={t:+v.currentTime.toFixed(2), text:''}; S.notes.push(n); S.notes.sort((a,b)=>a.t-b.t); save(); renderNotes(S.notes.indexOf(n)); }
$('add').onclick=addNote;
function renderNotes(focus){ const box=$('notes'); box.innerHTML=''; $('count').textContent=S.notes.length?'('+S.notes.length+')':'';
  S.notes.forEach((n,i)=>{ const row=document.createElement('div'); row.className='note';
    const a=document.createElement('a'); a.textContent=label(n.t); a.title='jump to this time'; a.onclick=()=>{ v.currentTime=n.t; };
    const ta=document.createElement('textarea'); ta.value=n.text; ta.placeholder='what you see, what you want'; ta.oninput=()=>{ n.text=ta.value; save(); };
    const x=document.createElement('button'); x.textContent='x'; x.title='delete this note'; x.onclick=()=>{ S.notes.splice(i,1); save(); renderNotes(); };
    row.append(a,ta,x); box.append(row); if(i===focus) ta.focus(); }); }

function choice(el, name, type, opts, st){ opts.forEach((o,i)=>{ const l=document.createElement('label'); const r=document.createElement('input'); r.type=type; r.name=name;
    if(type==='radio'){ r.checked=st.pick===i; r.onchange=()=>{ st.pick=i; save(); }; }
    else { st.picks=st.picks||[]; r.checked=st.picks.includes(i); r.onchange=()=>{ st.picks=st.picks.filter(k=>k!==i); if(r.checked) st.picks.push(i); st.picks.sort(); save(); }; }
    l.append(r,' '+o); el.append(l); }); }
function box(st, ph){ const ta=document.createElement('textarea'); ta.placeholder=ph; ta.value=st.text||''; ta.oninput=()=>{ st.text=ta.value; save(); }; return ta; }
function renderDec(){ const b=$('decisions'); b.innerHTML='';
  D.decisions.forEach(d=>{ const st=S.dec[d.id]||(S.dec[d.id]={pick:null,text:''}); const el=document.createElement('div'); el.className='dec';
    const h=document.createElement('h3'); h.textContent=d.title; const p=document.createElement('p'); p.textContent=d.why; el.append(h,p);
    choice(el,'dec_'+d.id,'radio',d.opts,st); el.append(box(st,'anything to add (optional)')); b.append(el); }); }
function fig(path, cap){ const f=document.createElement('figure'); const a=document.createElement('a'); a.href=path; a.target='_blank';
  const im=document.createElement('img'); im.src=path; im.loading='lazy'; a.append(im); const c=document.createElement('figcaption'); c.textContent=cap; f.append(c,a); return f; }
function renderLike(){ const b=$('chars'); b.innerHTML='';
  D.chars.forEach(c=>{ const st=S.like[c.id]||(S.like[c.id]={pick:null,picks:[],text:''}); const el=document.createElement('div'); el.className='who';
    const h=document.createElement('h2'); h.style.marginTop='0'; h.textContent=c.name; el.append(h);
    if(c.noted){ const n=document.createElement('p'); n.textContent=c.noted; el.append(n); }
    const pair=document.createElement('div'); pair.className='pair';
    const L=document.createElement('div'), R=document.createElement('div');
    c.refs.forEach(r=>L.append(fig(r,'Your reference'))); c.canon.forEach(r=>R.append(fig(r,"Claude's sheet (what every shot was drawn from)")));
    pair.append(L,R); el.append(pair);
    if(c.new.length){ const st2=S.like[c.id+'_new']||(S.like[c.id+'_new']={pick:null,text:''}); const nb=document.createElement('div');
      const hh=document.createElement('h3'); hh.textContent='Redrawn sheets (17 Nov): new hair, livelier faces'; nb.append(hh);
      const g2=document.createElement('div'); g2.className='pair'; c.new.forEach(r=>g2.append(fig(r,'Redrawn'))); nb.append(g2);
      choice(nb,'new_'+c.id,'radio',NEWOPTS,st2); nb.append(box(st2,'what to change in the redrawn sheets')); el.append(nb); }
    const cols=document.createElement('div'); cols.className='cols';
    const c1=document.createElement('div'), c2=document.createElement('div');
    const h1=document.createElement('h3'); h1.textContent='Where does it go wrong?'; c1.append(h1);
    choice(c1,'stage_'+c.id,'radio',["It's fine","Already in Claude's sheet","The sheet is fine; the film frames drift","Both"],st);
    const h2=document.createElement('h3'); h2.textContent="What's off (tick any)"; c2.append(h2);
    choice(c2,'cause_'+c.id,'checkbox',D.causes[c.kind],st);
    cols.append(c1,c2); el.append(cols); el.append(box(st,'in your words: what is she like in the reference that is missing here?'));
    const g=document.createElement('div'); g.className='stills';
    c.stills.forEach(s=>{ const k=c.id+'|'+s.shot+'|'+s.t.toFixed(2); const ss=S.still[k]||(S.still[k]={text:''}); const f=document.createElement('div'); f.className='still';
      const a=document.createElement('a'); a.href=s.img; a.target='_blank'; const im=document.createElement('img'); im.src=s.img; im.loading='lazy'; a.append(im);
      const j=document.createElement('a'); j.className='jump'; j.textContent=s.shot+'  '+fmt(s.t)+'  (show in video)'; j.onclick=()=>jump(s.t);
      const ta=box(ss,'note on this frame'); f.append(a,j,ta); g.append(f); });
    el.append(g); b.append(el); }); }

function text(){ let s='CHAOS MONKEY __NAME__: NOTES\n\nTIMESTAMPED NOTES ('+S.notes.length+')\n';
  S.notes.forEach(n=>{ s+='- '+label(n.t)+': '+(n.text.trim()||'(no text)')+'\n'; });
  s+='\nLIKENESSES\n';
  D.chars.forEach(c=>{ const st=S.like[c.id]||{}; const stage=["It's fine","Already in Claude's sheet","The sheet is fine; the film frames drift","Both"];
    s+='- '+c.name+': '+(st.pick==null?'(not answered)':stage[st.pick])+'\n';
    (st.picks||[]).forEach(i=>{ s+='    off: '+D.causes[c.kind][i]+'\n'; });
    if(st.text&&st.text.trim()) s+='    note: '+st.text.trim()+'\n';
    const sn=S.like[c.id+'_new']; if(c.new.length) s+='    redrawn sheets: '+(!sn||sn.pick==null?'(not answered)':NEWOPTS[sn.pick])+(sn&&sn.text&&sn.text.trim()?' — '+sn.text.trim():'')+'\n';
    c.stills.forEach(f=>{ const ss=S.still[c.id+'|'+f.shot+'|'+f.t.toFixed(2)]; if(ss&&ss.text&&ss.text.trim()) s+='    '+f.shot+' '+fmt(f.t)+': '+ss.text.trim()+'\n'; }); });
  s+='\nDECISIONS\n'; D.decisions.forEach(d=>{ const st=S.dec[d.id]||{}; s+='- '+d.title+': '+(st.pick==null?'(not answered)':d.opts[st.pick])+(st.text&&st.text.trim()?'\n    note: '+st.text.trim():'')+'\n'; });
  return s; }
function out(){ $('out').value=text(); }
$('copy').onclick=async()=>{ const o=$('out'); try{ await navigator.clipboard.writeText(o.value); }catch(e){ o.select(); document.execCommand('copy'); } $('copy').textContent='Copied'; setTimeout(()=>$('copy').textContent='Copy everything',1500); };
$('dl').onclick=()=>{ const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text()],{type:'text/plain'})); a.download='chaosmonkey___NAME___notes.txt'; a.click(); };
let armed=0; $('clear').onclick=()=>{ const c=$('clear'); if(Date.now()-armed<4000){ S={notes:[],dec:{},like:{},still:{}}; save(); renderNotes(); renderDec(); renderLike(); c.textContent='Clear all (asks first)'; } else { armed=Date.now(); c.textContent='Press again to clear everything'; setTimeout(()=>c.textContent='Clear all (asks first)',4000); } };
addEventListener('keydown',e=>{ const typing=/TEXTAREA|INPUT|SELECT/.test(document.activeElement.tagName);
  if(e.key==='Escape'){ document.activeElement.blur(); return; } if(typing || e.ctrlKey || e.metaKey || e.altKey) return;
  if(e.key==='n'||e.key==='N'){ e.preventDefault(); addNote(); } else if(e.key===' '){ e.preventDefault(); v.paused?v.play():v.pause(); }
  else if(e.key==='ArrowLeft') seek(-1); else if(e.key==='ArrowRight') seek(1); else if(e.key===',') frame(-1); else if(e.key==='.') frame(1);
  else if(e.key==='[') shotStep(-1); else if(e.key===']') shotStep(1); });
load(); renderNotes(); renderDec(); renderLike(); out(); tick();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="preview_v2")
    a = ap.parse_args()
    name = a.name
    clean = ROOT / f"previews/chaosmonkey_{name}_540p_nolyrics.mp4"
    lyr = ROOT / f"previews/chaosmonkey_{name}_540p.mp4"
    out_dir = ROOT / "review"
    img_dir = out_dir / "likeness"
    img_dir.mkdir(parents=True, exist_ok=True)

    shots = json.loads((ROOT / "docs/shots.json").read_text())["shots"]
    by_id = {s["id"]: s for s in shots}
    timing = json.loads((ROOT / "analysis/timing.json").read_text())

    def small(rel):
        src = ROOT / rel
        dst = img_dir / (src.stem + ".jpg")
        if not dst.exists():
            im = Image.open(src).convert("RGB")
            im.thumbnail((1800, 1800), Image.LANCZOS)
            im.save(dst, quality=90)
        return f"likeness/{dst.name}"

    chars = []
    for c in CHARS:
        stills = []
        for sid, dt in c["stills"]:
            s = by_id[sid]
            t = round(min(s["in"] + dt, s["out"] - 1 / 24), 3)
            dst = img_dir / f"{name}_{sid}_{int(round(t * 24)):05d}.jpg"
            if not dst.exists():
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(clean), "-frames:v", "1",
                                "-q:v", "2", str(dst)], check=True)
            stills.append(dict(shot=sid, t=t, img=f"likeness/{dst.name}"))
        chars.append(dict(id=c["id"], name=c["name"], kind=c["kind"], noted=c.get("noted", ""), new=[small(r) for r in c.get("new", [])], refs=[small(r) for r in c["refs"]],
                          canon=[small(r) for r in c["canon"]], stills=stills))

    data = dict(
        shots=[dict(id=s["id"], **{"in": round(s["in"], 4)}, desc=s["desc"]) for s in shots],
        sections=[[s["start"], s["name"]] for s in timing["sections"]],
        lines=[dict(start=l["start"], end=l["end"], text=l["text"]) for l in timing["lines"]],
        decisions=DECISIONS, causes=CAUSES, chars=chars,
    )
    sources = (f'<option value="../{lyr.relative_to(ROOT)}">{name}, lyrics on</option>'
               f'<option value="../{clean.relative_to(ROOT)}">{name}, no lyrics</option>')
    html = (HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__SOURCES__", sources).replace("__NAME__", name))
    out = out_dir / f"{name}_notes.html"
    out.write_text(html, encoding="utf-8")
    print(out, f"{len(html)//1024} KB,", sum(len(c['stills']) for c in chars), "stills")


if __name__ == "__main__":
    main()

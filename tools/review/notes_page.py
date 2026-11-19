#!/usr/bin/env python3
"""Build the local review page for a preview cut: timestamped notes, likeness notes, decisions.

  python tools/review/notes_page.py [--name preview_v3]
  python tools/review/notes_page.py --name preview_v4            # final cut (previews/chaosmonkey_preview_v4_540p*.mp4)
  python tools/review/notes_page.py --name preview_v4 --cut preview_v4_trial
      # test build against media/cut/preview_v4_trial*.mp4 + work/cut/preview_v4_trial/manifest.json;
      # writes review/_test_preview_v4_trial_notes.html (delete it afterwards)

A name containing "v4" selects the v4 data block (shot descriptions from work/cut/notes_v4/descriptions_v4.json,
decisions V4_DECISIONS, the proofread table of review/lyrics_zh_v4_proof.md, links to the singing and F1 pages, no
likeness section); any other name builds the v3 page as before. Stills are cut from media/cut/<cut>_clean.mp4 and
refreshed whenever that file is newer.

Writes review/<name>_notes.html and review/likeness/*.jpg (film stills and downscaled reference sheets).
Everything is local: the page reads the video from previews/ and keeps notes in the browser's localStorage.
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

# character -> her references, the accepted v3 head sheet, and (shot, seconds into the shot) for the film stills (preview_v3)
V3_NOTE = ("The sheet on the right is the v3 head sheet you accepted on 17 Nov; every room shot in this cut was re-shot "
           "from it. The frames below are from this cut.")
CHARS = [
    dict(id="little_jade", name="Little Jade, 1988 (age 5)", kind="girl", noted=V3_NOTE,
         refs=["inputs/ref_merge_little_jade_face.jpg", "inputs/ref_merge_little_jade_fullbody.jpg"],
         canon=["design/characters/little_jade/lj_H_heads_v3.jpg"],
         stills=[("A2", 2.5), ("A3", 1.0), ("A4", 1.5), ("B1", 1.5), ("B1", 5.0), ("B2", 1.5), ("C3", 1.5), ("C5", 1.6),
                 ("D3", 2.2), ("D9", 0.6), ("D9", 2.6), ("E1", 2.7), ("E3", 1.5), ("E3", 5.0), ("E5", 0.6), ("E6", 1.2),
                 ("F3", 1.4), ("G1", 2.0), ("G4", 3.0), ("G5", 1.0), ("G5", 2.4), ("J4", 3.6)]),
    dict(id="daughter", name="The daughter, 2026 (age 4)", kind="girl", noted=V3_NOTE,
         refs=["inputs/ref_moongazing_daughter_strawberry_dress_sheet.jpg"],
         canon=["design/characters/daughter/daughter_H_heads_v3.jpg"],
         stills=[("F1", 0.4), ("F1", 1.3), ("F3", 0.4), ("F3", 0.9), ("F4", 0.8), ("F6", 2.6), ("F6", 3.2), ("I1", 1.5),
                 ("I3", 0.4), ("I3", 1.2), ("K1", 0.8), ("K1", 1.8), ("L1", 3.8)]),
    dict(id="mama", name="Mama, 1988 (35)", kind="adult", noted=V3_NOTE,
         refs=["inputs/ref_moongazing_teahouse_jade_mom_daughter.png"],
         canon=["design/characters/mama/mama_H_heads_v3.jpg"],
         stills=[("A3", 2.4), ("B2", 1.0), ("C3", 2.5), ("C5", 1.5), ("D3", 2.8), ("D9", 2.8), ("E1", 1.2), ("E6", 1.8),
                 ("G4", 1.5), ("G4", 4.0), ("I4", 0.1), ("L3", 0.6)]),
    dict(id="jade", name="Jade, 2026", kind="adult", noted=V3_NOTE,
         refs=["inputs/ref_moongazing_jade_singing_watercolor_first_frame.jpg",
               "inputs/ref_moongazing_teahouse_jade_mom_daughter.png"],
         canon=["design/characters/jade/jade_H_heads_v3.jpg"],
         stills=[("F4", 0.8), ("I1", 0.8), ("I1", 1.8), ("I4", 1.2), ("I4", 2.0), ("K1", 1.0), ("L1", 2.0), ("L1", 4.2),
                 ("L2", 2.0)]),
]

# The questions open after preview_v3. imgs: [(path, caption)] shown under the question; times are in the cut.
DECISIONS = [
    dict(id="monkey_costume", title="1. The monkey's costume: A or B",
         why="You asked to try the Peking opera monkey in yellow. The cut uses A (all yellow, pompom cap, yellow scarf) in "
             "every stage shot: 0:58 to 1:22 (birth, four bows, the Buddha's palm, staff flower, look-out) and 3:12 to 3:16. "
             "B is the alternative from the costume research: key-fret pattern on the jacket, leopard-fur trim, red scarf. "
             "The dark ink monkey of preview_v2 can also be restored.",
         imgs=[("design/characters/monkey/v3/monkey_v3_model_sheet.jpg", "A: all yellow (in this cut)"),
               ("design/characters/monkey/v3/monkey_v3b_ALT_fret_leopard_redscarf.jpg", "B: key-fret, leopard trim, red scarf")],
         opts=["A: all yellow", "B: key-fret, leopard trim, red scarf", "Something between (say what)",
               "Go back to the dark ink monkey of preview_v2"]),
    dict(id="medium_switch", title="2. The medium switch (it replaces the glitch)",
         why="On the breakbeat chops the same pose is shown for 4 or 5 held frames as a red paper-cut, a stone rubbing "
             "(white on black, torn paper edge) or a leather shadow puppet, then back to ink. Look at 0:43 to 0:45 (the "
             "stone splits), 0:59 to 1:00 (birth), 1:15 to 1:21 (palm, staff, look-out), 2:30 to 2:49 (the faces) and "
             "3:20 to 3:21. You said the old glitch read as errors: does this read as intended?",
         opts=["Yes, it reads as intentional", "Sometimes (say where it still looks like a mistake)",
               "No, still reads as an error", "Too short to read: hold longer"]),
    dict(id="swarm", title="3. The swarm on an album leaf (1:54 to 2:00)",
         why="The brief asked for the copies in the car's windows. The stage team put them on a ruled album leaf instead, "
             "full frame, lit like passing streetlights: nine cells, one job and one name slip each (读 写 算 运 战 扫 望 磨), "
             "the original in the middle (我) with a red thread to each, a seal 讫 as each finishes. Their reason: in the "
             "panes the grid and the threads did not read. The car is kept only by the light and by the cuts before and after "
             "(the shadow on the window at 1:48, the mirror at 1:52).",
         opts=["Keep the album leaf", "Put it back in the car windows", "Leaf, but show the car around it",
               "Neither reads as an agent swarm yet (say why)"]),
    dict(id="lipsync", title="4. Lip-sync on the singing shots",
         why="New method (an acted take, then only the mouth is transferred), and every singing face was measured before it "
             "shipped. On camera: 0:16 little Jade, 0:46 and 1:26 Mama, 1:33 little Jade, 1:47 the daughter's rap, "
             "2:01 little Jade, 2:21 Mama (borderline), 2:28 'Yes', 2:57 you, 3:03 the daughter, 3:08 you. "
             "The teams judged stills and strips, not playback, so this needs your eye in motion.",
         opts=["Good enough everywhere", "Mostly; these are off (list the times)", "Still not acceptable",
               "Fewer singing faces: play more lines on hands, pages and listeners"]),
    dict(id="sound", title="5. The sound layer (mix v2) and ending B",
         why="The diegetic layer was raised (you barely heard it in v2) and new cues were added: apron and towel on the hook "
             "0:12, the breath in her hair 0:53, the book stack falling 1:23, the hair-puffs 1:52, abacus clicks and small "
             "seals 1:53 to 1:58, the page press 3:09, the blankets 3:55. The ending is B: the neon hum cuts at 3:57.8 "
             "and the last note rings about 3 s over black, to 4:01.9.",
         opts=["Good", "Still too quiet", "Too loud now", "Layer fine; change the ending (say how)",
               "Remove or change some cues (say which)"]),
    dict(id="inscriptions", title="6. The Chinese inscriptions: text and font",
         why="Every sung line over a book or stage page now has its inscription painted into the page (vertical, right to "
             "left, one seal 悟空), from your proofread file; the font is Ma Shan Zheng. Your parents were going to "
             "recheck the wording. The English lyric line was moved wherever it would have touched an inscription.",
         opts=["Text and font are right", "Font is right; text changes (write them below)",
               "Text is right; try another brush font", "Both need work", "Too many inscriptions: keep fewer (say which)"]),
    dict(id="next", title="7. What next",
         why="Every shot in this cut is a v3 shot. Either another 540p pass with your notes, or the 1080p master with "
             "the notes applied.",
         opts=["Another 540p pass with my notes", "1080p master with my notes applied"]),
]

# ---- v4 ---------------------------------------------------------------------------------------------------------------
# stills: ("cut", seconds_in_cut, caption) | ("clip", "media/...mp4", frame_number, caption). Times are in the cut (= song time).
V4_LINKS = [("review/sing_v4/index.html", "All singing shots, with a sync slider"),
            ("review/f1_ab/index.html", "F1 (1:47) A/B takes"),
            ("review/lyrics_zh_v4_proof.md", "The new Chinese lines as a text file")]

V4_DECISIONS = [
    dict(id="swarm", title="1. The swarm shot (1:52 to 2:00): night painting or ink on paper",
         why="F4, F5 and F6a are now one 7 s shot: a painted night landscape (青绿 greens, lanterns, gold line) made with a video "
             "model from painted keyframes, then retimed to the beats. A monkey plucks and blows, generations spawn down the "
             "terraces, lanterns flare in waves, sectors go dark with a 讫 seal, a twin appears, two 真 seals. It is a different "
             "look from the ink-on-paper pages around it. At the top of the rise the lanterns across the range draw the "
             "monkey himself in 亮相. Weak: the crowd reads as texture at this size; the twin's arrival (an ink puff) is quick.",
         stills=[("cut", 113.0, "1:53 spawn on the ledge"), ("cut", 115.0, "1:55 the terraces, name slips"),
                 ("cut", 117.0, "1:57 sectors dark, gale of hairs"), ("cut", 119.0, "1:59 the twin, two 真 seals")],
         opts=["Keep the night painting", "Make it ink on paper like the pages (a different shot, more work)",
               "Night painting, but darker or sparser", "Neither reads as an agent swarm yet (say why)"]),
    dict(id="flight", title="2. The whisper flight D4-D6 (1:08 to 1:16) and its hard cut into D7",
         why="The 3D flight was ranked below this one by a blind reviewer, so the lead replaced it with a painted flight (a video "
             "model over seven painted keyframes plus our typeset carving, jumps and threads): a macro of 通 lights, the "
             "light jumps by shared component, the range comes alight at dusk, up through cloud, five pillars read as the "
             "Buddha's hand and the monkey lands on the middle one. It ends dark blue, then cuts straight to D7 on bare pale "
             "paper at 1:16.4 (accepted as the medium switch, never watched at speed by the team). Weak: the carving is "
             "legible only in the first 30 frames; the monkey is small.",
         stills=[("cut", 69.0, "1:09 macro 通, the glow"), ("cut", 71.5, "1:11 the range lit"),
                 ("cut", 75.5, "1:15 the landing, rays"), ("cut", 77.0, "1:17 D7, bare paper")],
         opts=["Keep the flight and the hard cut", "Keep the flight, soften the cut into D7 (say how)",
               "The flight needs a legible carving through the whole shot", "Monkey too small: make him bigger on the landing",
               "Something else (say what)"]),
    dict(id="h6", title="3. H6 (2:52.8 to 2:57.2): the monkey growing from the strand",
         why="Her hair streams in the gale, one strand works loose, three wet ink strokes make a crouched monkey whose tail is "
             "the strand, then yellow floods in and he somersaults out. The ink-only monkey is on screen about 0.4 s (the model "
             "clip was sped up 3 to 5 times); the fully coloured render comes from about two thirds in. Is the growth right, "
             "and should he be fewer strokes held longer?",
         stills=[("cut", 173.5, "2:53 hair in the gale"), ("cut", 174.8, "2:55 the ink monkey, tail = strand"),
                 ("cut", 176.0, "2:56 coloured, somersaulting")],
         opts=["Right as it is", "Right idea, hold the ink monkey longer (fewer strokes, slower)",
               "Make him fewer, bolder strokes (say how)", "The strand is too big for his tail", "Not working (say why)"]),
    dict(id="wind", title="4. C5 wind (0:52.3 to 0:57.0): painterly layer or true fluid simulation",
         why="In the cut: a video model was asked what the wind does to the page, and that motion is used as a layer on our paper "
             "(ribbons rising left to right, dissolving). It is painterly and organic but the motion is the model's invention; "
             "lines cross the egg's face rather than parting round it. The fallback is a real 2D fluid solve with about 35 "
             "advected brush ribbons that wrap the egg, more physical but stiffer. Stills 3 and 4 are the fallback.",
         stills=[("cut", 53.2, "0:53 Mama blows (C5a, in the cut)"), ("cut", 55.2, "0:55 the wind layer (in the cut)"),
                 ("clip", "media/comp/_cand/C5b_A.mp4", 14, "Fluid fallback, early"),
                 ("clip", "media/comp/_cand/C5b_A.mp4", 30, "Fluid fallback, over the egg")],
         opts=["Keep the painterly layer (in the cut)", "Use the true fluid simulation", "Painterly, but make the egg part the lines",
               "Neither: more like a traditional wind-scroll (say how)"]),
    dict(id="e3", title="5. E3 second half (1:36 to 1:40): the held sword-hand, wider, mouth closed",
         why="You asked for a 小龙女-style cast on 'a spell I'd remember well'. The mouth-synced model could not do it (open palms), "
             "so the shot now cuts at 1:36.0 to a wider three-quarter angle where her mouth is closed: two fingers together as one "
             "blade past her ear, the other palm out, then she looks up to Mama laughing. Hands checked every frame. Weak: it is a "
             "held pose, no visible flourish; the pushing palm is edge-on; her face is small and frontal with the mouth closed "
             "while the line is sung; the cut jumps in scale.",
         stills=[("cut", 94.5, "1:34 E3a, 'Names and faces' (tight)"), ("cut", 97.0, "1:37 E3b, the cast"),
                 ("cut", 98.8, "1:39 E3b, looks up to Mama")],
         opts=["Good: keep it", "Keep the angle, ask for a flourish before the hold (another round)",
               "Same wide angle but let her mouth sing (accept the lip-sync risk)", "Revert to the single tight take",
               "Another approach (say what)"]),
    dict(id="j4", title="6. J4 (3:16.6 to 3:20.7): the 1988 half's arms go up 0.9 s early",
         why="Left half (1988, Mama and little Jade) has its arms fully up at about 197.8 s; the gong is at 198.74 and the 2026 "
             "half (right) goes up at 198.7. A join to a take with the arms down was tried on paper and cannot be done without a "
             "visible pop. Options: accept it, or re-make the 1988 half from a keyframe with the arms already raised on the gong "
             "(or framed so the faces are not the subject).",
         stills=[("cut", 197.0, "3:17.0 arms down"), ("cut", 198.0, "3:18.0 1988 arms up, 2026 still down"),
                 ("cut", 199.0, "3:19.0 both up")],
         opts=["Accept it", "Re-stage the 1988 half so it hits the gong (a new take)",
               "Re-time the whole shot's gong feel instead (say how)"]),
    dict(id="f3b", title="7. F3b (1:52.25 to 1:52.75): little Jade's puff, faint",
         why="The 12-frame match-cut on the blow is faint (the take was sped about 3x) and the blind judge asked for a retake. "
             "The retake submit was refused by the permission check, so it was not run. A two-take retake is a small spend.",
         stills=[("cut", 112.3, "1:52.3 F3b"), ("cut", 112.6, "1:52.6 F3b")],
         opts=["Approve a two-take retake", "Leave it as it is", "Cut the match entirely and stay with the daughter's puff"]),
    dict(id="tinghua", title="8. 听话 in G2's margin (2:07.5 to 2:14.4)",
         why="Your note: 听话 should appear somewhere. In G2 the margins are bare paper; a cinnabar 听话 inks in on the left on each "
             "sung echo (2:10.175 and 2:13.690) and stays, 1.6 times the size of the inscription. Placement was judged on stills "
             "only.",
         stills=[("cut", 128.0, "2:08 before"), ("cut", 131.0, "2:11 first 听话"), ("cut", 134.2, "2:14 second 听话")],
         opts=["Good as is", "Bigger or bolder", "Different place (say where)", "Not needed in the margin, put it in the inscription"]),
    dict(id="calli", title="9. Chinese calligraphy in the rooms (new in v4)",
         why="Every sung line now carries its Chinese as light-on-dark vertical calligraphy at a side of the frame (Ma Shan Zheng, "
             "one small seal), 26 px at 540p, placed where the picture is quiet. The new lines are in the proofread table "
             "below. Look at size, side, and the light-on-dark treatment.",
         stills=[("cut", 114.0, "F4 about 1:54"), ("cut", 143.0, "G4 about 2:23"),
                 ("cut", 188.1, "I4 about 3:08"), ("cut", 205.0, "K1 about 3:25")],
         opts=["Good as is", "Bigger", "Smaller or fainter", "Move to the other side (say which shots)",
               "Not light on dark: use ink where the room is bright", "Too many: fewer shots (say which)"]),
    dict(id="sound", title="10. Sound layer re-timed to the new picture (mix v3b)",
         why="You approved the moved 'Yes' in mix v3 by ear. This cut plays mix v3b: the song under it is bit-identical to v3's "
             "(same moved 'Yes'), loudness and peak are the same (-15.83 LUFS, -1.37 dBTP); only the effects layer differs: 28 "
             "cue rows re-timed or added for the v4 picture (listed in docs/SOUND.md, 'v3b mix'), e.g. the swarm's spawn and "
             "gale, the pop into depth at 3:10.9, the K4 pages turning in a draught, the C5 wind. Nobody has heard v3b. By "
             "measurement (a model, not ears) nine of the new cues sit faint under the loudest song passages: the rap "
             "(1:47-2:01) and drop 2 (3:10-3:20).",
         stills=[],
         opts=["Good", "Too much", "Go back to v3 (the mix you approved)"]),
    dict(id="next", title="11. What next",
         why="Every shot is now a v4 shot. Either another 540p pass with your notes (say which shots), or the 1080p master with "
             "specific fixes applied.",
         opts=["Another 540p pass with my notes", "1080p master with my notes applied", "1080p master as is",
               "Specific fixes first, then decide (list them in the notes)"]),
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
  #links a { color:var(--acc); }
  #proof { max-width:1560px; margin:0 auto; padding:0 16px 20px; }
  .pr { display:grid; grid-template-columns:150px minmax(180px,1fr) minmax(260px,1.3fr) 130px minmax(200px,1fr); gap:6px 14px; align-items:start; padding:10px 0; border-top:1px solid var(--line); }
  @media (max-width:1050px){ .pr{ grid-template-columns:1fr 1fr; } }
  .zh { font:34px/1.35 "Ma Shan Zheng","Noto Serif CJK SC","Noto Sans CJK SC","Source Han Sans SC","WenQuanYi Zen Hei",serif; color:var(--ink); }
  .zh span.sep { color:var(--dim); font-size:20px; padding:0 .25em; }
  .pr .en { color:var(--ink); } .pr .nt { font-size:13px; color:var(--dim); }
  .pr input[type=text] { font-size:20px; }
  .pr.ok { opacity:.55; }
  .cols { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:0 18px; }
</style>
</head>
<body>
<main>
<section>
  <h1>Chaos Monkey, __NAME__: timestamped notes</h1>
  <p>Everything you type is kept in this browser and survives a reload. When you are done, press <b>Copy everything</b> in the right column and paste it to Claude, or download it as a file.</p>
  <div class="bar" id="links"></div>
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

<section id="proof">
  <h2>New Chinese lines (proofread)</h2>
  <p id="proofintro"></p>
  <div id="prooflist"></div>
</section>

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
S.notes = S.notes || []; S.dec = S.dec || {}; S.like = S.like || {}; S.still = S.still || {}; S.proof = S.proof || {};
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
    if(d.imgs&&d.imgs.length){ const g=document.createElement('div'); g.className='pair'; d.imgs.forEach(([path,cap,t])=>g.append(fig(path,cap,t))); el.append(g); }
    choice(el,'dec_'+d.id,'radio',d.opts,st); el.append(box(st,'anything to add (optional)')); b.append(el); }); }
function fig(path, cap, t){ const f=document.createElement('figure'); const a=document.createElement('a'); a.href=path; a.target='_blank';
  const im=document.createElement('img'); im.src=path; im.loading='lazy'; a.append(im); const c=document.createElement('figcaption'); c.textContent=cap;
  if(t!=null){ const j=document.createElement('a'); j.className='jump'; j.textContent='  ('+fmt(t)+', show in video)'; j.onclick=()=>jump(t); c.append(j); }
  f.append(c,a); return f; }
function renderLinks(){ const b=$('links'); (D.links||[]).forEach(([h,t])=>{ const a=document.createElement('a'); a.href='../'+h; a.target='_blank'; a.textContent=t; b.append(a); b.append(' | '); }); if(!(D.proof&&D.proof.length) && b.lastChild) b.removeChild(b.lastChild); if(D.proof&&D.proof.length){ const a=document.createElement('a'); a.href='#proof'; a.textContent='Jump to the proofread Chinese lines'; b.append(a); } }
function renderProof(){ const sec=$('proof'); if(!(D.proof&&D.proof.length)){ sec.style.display='none'; return; }
  $('proofintro').textContent=D.proof_intro||''; const box=$('prooflist'); box.innerHTML='';
  D.proof.forEach(r=>{ const st=S.proof[r.n]||(S.proof[r.n]={ok:false,fix:''}); const row=document.createElement('div'); row.className='pr'+(st.ok?' ok':'');
    const a=document.createElement('div'); const j=document.createElement('a'); j.className='jump'; j.textContent='#'+r.n+'  '+r.shot+'  '+r.time; if(r.t!=null){ j.onclick=()=>jump(r.t); j.title='show in video'; } a.append(j);
    const lab=document.createElement('label'); const cb=document.createElement('input'); cb.type='checkbox'; cb.checked=st.ok; cb.onchange=()=>{ st.ok=cb.checked; row.className='pr'+(st.ok?' ok':''); save(); };
    lab.append(cb,' OK'); lab.style.display='block'; lab.style.marginTop='8px'; a.append(lab);
    const en=document.createElement('div'); en.className='en'; en.textContent=r.en;
    const zh=document.createElement('div'); zh.className='zh'; r.zh.split(' / ').forEach((c,i)=>{ if(i){ const sp=document.createElement('span'); sp.className='sep'; sp.textContent='/'; zh.append(sp); } zh.append(c); });
    const nt=document.createElement('div'); nt.className='nt'; nt.textContent=r.note||'';
    const fx=document.createElement('input'); fx.type='text'; fx.placeholder='correction (Chinese or a word)'; fx.value=st.fix; fx.oninput=()=>{ st.fix=fx.value; save(); };
    const lastc=document.createElement('div'); lastc.append(fx);
    row.append(a,en,zh,nt,lastc); box.append(row); }); }
function renderLike(){ const b=$('chars'); b.innerHTML=''; if(!D.chars.length){ $('like').style.display='none'; return; }
  D.chars.forEach(c=>{ const st=S.like[c.id]||(S.like[c.id]={pick:null,picks:[],text:''}); const el=document.createElement('div'); el.className='who';
    const h=document.createElement('h2'); h.style.marginTop='0'; h.textContent=c.name; el.append(h);
    if(c.noted){ const n=document.createElement('p'); n.textContent=c.noted; el.append(n); }
    const pair=document.createElement('div'); pair.className='pair';
    const L=document.createElement('div'), R=document.createElement('div');
    c.refs.forEach(r=>L.append(fig(r,'Your reference'))); c.canon.forEach(r=>R.append(fig(r,"Claude's sheet (what every shot was drawn from)")));
    pair.append(L,R); el.append(pair);
    if(c.new.length){ const st2=S.like[c.id+'_new']||(S.like[c.id+'_new']={pick:null,text:''}); const nb=document.createElement('div');
      const hh=document.createElement('h3'); hh.textContent='Redrawn sheets'; nb.append(hh);
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
  if(D.proof&&D.proof.length){ s+='\nNEW CHINESE LINES (proofread)\n';
    D.proof.forEach(r=>{ const st=S.proof[r.n]||{}; const fx=(st.fix||'').trim();
      s+='- #'+r.n+' '+r.shot+' '+r.time+'  '+r.zh+': '+(fx?'CORRECTION: '+fx+(st.ok?' (also ticked OK)':''):(st.ok?'OK':'(not checked)'))+'\n'; }); }
  if(D.chars.length) s+='\nLIKENESSES\n';
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
let armed=0; $('clear').onclick=()=>{ const c=$('clear'); if(Date.now()-armed<4000){ S={notes:[],dec:{},like:{},still:{},proof:{}}; save(); renderNotes(); renderDec(); renderLike(); renderProof(); c.textContent='Clear all (asks first)'; } else { armed=Date.now(); c.textContent='Press again to clear everything'; setTimeout(()=>c.textContent='Clear all (asks first)',4000); } };
addEventListener('keydown',e=>{ const typing=/TEXTAREA|INPUT|SELECT/.test(document.activeElement.tagName);
  if(e.key==='Escape'){ document.activeElement.blur(); return; } if(typing || e.ctrlKey || e.metaKey || e.altKey) return;
  if(e.key==='n'||e.key==='N'){ e.preventDefault(); addNote(); } else if(e.key===' '){ e.preventDefault(); v.paused?v.play():v.pause(); }
  else if(e.key==='ArrowLeft') seek(-1); else if(e.key==='ArrowRight') seek(1); else if(e.key===',') frame(-1); else if(e.key==='.') frame(1);
  else if(e.key==='[') shotStep(-1); else if(e.key===']') shotStep(1); });
load(); renderLinks(); renderNotes(); renderDec(); renderLike(); renderProof(); out(); tick();
</script>
</body>
</html>
"""


def v3_descriptions():
    """Shot descriptions shown under the video: the 'new direction' of docs/REVISION_V3.md section 5 (the brief the
    cut was shot to) in front of the shot list's own description."""
    import re
    out, text = {}, (ROOT / "docs/REVISION_V3.md").read_text()
    sec = text[text.index("## 5. Shot by shot"):text.index("## 6.")]
    for line in sec.splitlines():
        m = re.match(r"\|\s*([A-L]\d[^|]*)\|(.*)\|\s*$", line)
        if not m:
            continue
        ids = re.findall(r"\b([A-L]\d)\b", re.sub(r"\(.*?\)", "", m.group(1)))
        d = re.sub(r"\*\*|`", "", m.group(2)).strip()
        for i in ids:
            out[i] = d
    return out


def describe(shot, v3):
    """The v3 direction; where it only points elsewhere ('As v2', '3.2.') the shot list's description follows it."""
    d = v3.get(shot["id"])
    if not d:
        return shot["desc"]
    if len(d) < 90 or d.startswith("As v2"):
        return f"v3 brief: {d}  (Shot list: {shot['desc']})"
    return f"v3 brief: {d}"


def proof_rows():
    """Parse the markdown table of review/lyrics_zh_v4_proof.md into rows (n, shot, time, en, zh, note, t = first start)."""
    import re
    rows = []
    for line in (ROOT / "review/lyrics_zh_v4_proof.md").read_text().splitlines():
        if not re.match(r"\|\s*\d+\s*\|", line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 5:
            continue
        m = re.match(r"(\d+):(\d+(?:\.\d+)?)", c[2])
        rows.append(dict(n=int(c[0]), shot=c[1], time=c[2], en=c[3], zh=c[4], note=c[5] if len(c) > 5 else "",
                         t=int(m.group(1)) * 60 + float(m.group(2)) if m else None))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="preview_v3")
    ap.add_argument("--cut", help="test build: take video, stills and manifest from this cut in media/cut and work/cut "
                                  "(e.g. preview_v4_trial) and write review/_test_<cut>_notes.html")
    a = ap.parse_args()
    name = a.name
    v4 = "v4" in name
    if a.cut:
        clean = ROOT / f"media/cut/{a.cut}_clean.mp4"
        lyr = ROOT / f"media/cut/{a.cut}.mp4"
    else:
        clean = ROOT / f"previews/chaosmonkey_{name}_540p_nolyrics.mp4"
        lyr = ROOT / f"previews/chaosmonkey_{name}_540p.mp4"
    if v4:                                   # stills come from the cut named by --name (media/cut/<name>_clean.mp4) unless --cut
        clean_stills = ROOT / f"media/cut/{a.cut or name}_clean.mp4"
        if not clean_stills.exists():
            clean_stills = clean
    else:
        clean_stills = clean
    out_dir = ROOT / "review"
    img_dir = out_dir / "likeness"
    img_dir.mkdir(parents=True, exist_ok=True)
    tag = a.cut or name

    def still(t, label, src=None, frame=None):
        """One frame as a jpg under review/likeness, refreshed when the cut is newer."""
        src = src or clean_stills
        dst = img_dir / f"{tag}_{label}_{int(round(t * 24)):05d}.jpg" if frame is None else img_dir / f"{src.stem}_f{frame:03d}.jpg"
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:        # a rebuilt cut refreshes its stills
            at = t if frame is None else (frame + 0.5) / 24
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(int(round(at * 24)) + 0.5) / 24 if frame is None else at:.4f}",
                            "-i", str(src), "-frames:v", "1", "-q:v", "2", str(dst)], check=True)
        return f"likeness/{dst.name}"

    if v4:
        mf = ROOT / f"work/cut/{a.cut or name}/manifest.json"
        shots = json.loads(mf.read_text())["shots"]
        timing = json.loads((ROOT / "analysis/timing_v4.json").read_text())
        descs = json.loads((ROOT / "work/cut/notes_v4/descriptions_v4.json").read_text())
        desc_of = lambda s: descs.get(s["id"]) or s["desc"]
    else:
        shots = json.loads((ROOT / "docs/shots.json").read_text())["shots"]
        timing = json.loads((ROOT / "analysis/timing.json").read_text())
        v3 = v3_descriptions()
        desc_of = lambda s: describe(s, v3)
    by_id = {s["id"]: s for s in shots}

    def small(rel):
        src = ROOT / rel
        dst = img_dir / (src.stem + ".jpg")
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            im = Image.open(src).convert("RGB")
            im.thumbnail((1800, 1800), Image.LANCZOS)
            im.save(dst, quality=90)
        return f"likeness/{dst.name}"

    chars = []
    if not v4:
        for c in CHARS:
            stills = []
            for sid, dt in c["stills"]:
                s = by_id[sid]
                t = round(min(s["in"] + dt, s["out"] - 1 / 24), 3)
                stills.append(dict(shot=sid, t=t, img=still(t, sid)))
            chars.append(dict(id=c["id"], name=c["name"], kind=c["kind"], noted=c.get("noted", ""), new=[small(r) for r in c.get("new", [])],
                              refs=[small(r) for r in c["refs"]], canon=[small(r) for r in c["canon"]], stills=stills))

    if v4:
        decisions = []
        for d in V4_DECISIONS:
            imgs = []
            for st in d.get("stills", []):
                if st[0] == "cut":
                    t = st[1]
                    imgs.append([still(t, "q_" + d["id"]), st[2], t])
                else:
                    imgs.append([still(0, "q_" + d["id"], src=ROOT / st[1], frame=st[2]), st[3], None])
            decisions.append(dict(id=d["id"], title=d["title"], why=d["why"], opts=d["opts"], imgs=imgs))
    else:
        decisions = [dict(d, imgs=[[small(pth), cap] for pth, cap in d.get("imgs", [])]) for d in DECISIONS]
    end = max(s["out"] for s in shots)
    data = dict(
        shots=[dict(id=s["id"], **{"in": round(s["in"], 4)}, desc=desc_of(s)) for s in shots]
              + [dict(id="END", **{"in": round(end, 4)}, desc=(descs["END"] if v4 else "Black to the end of the audio: the last note rings out (ending B)."))],
        sections=[[s["start"], s["name"]] for s in timing["sections"]],
        lines=[dict(start=l["start"], end=l["end"], text=l["text"]) for l in timing["lines"]],
        decisions=decisions, causes=CAUSES, chars=chars,
        links=V4_LINKS if v4 else [], proof=proof_rows() if v4 else [],
        proof_intro=("Every new Chinese line in this cut, in the order of the film. Tick OK if it is right, or type your "
                     "correction in the box. The grey note is where the lead hesitated. Click the shot and time to jump there; "
                     "columns are separated by a slash and read right to left on screen.") if v4 else "",
    )
    sources = (f'<option value="../{lyr.relative_to(ROOT)}">{tag}, lyrics on</option>'
               f'<option value="../{clean.relative_to(ROOT)}">{tag}, no lyrics</option>')
    html = (HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__SOURCES__", sources).replace("__NAME__", name))
    out = out_dir / (f"_test_{a.cut}_notes.html" if a.cut else f"{name}_notes.html")
    out.write_text(html, encoding="utf-8")
    print(out, f"{len(html)//1024} KB,", sum(len(c['stills']) for c in chars), "likeness stills,",
          sum(len(d['imgs']) for d in decisions), "decision stills")


if __name__ == "__main__":
    main()

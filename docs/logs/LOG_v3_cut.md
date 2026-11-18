# LOG v3 CUT (assemble preview_v3)

## CHECKPOINT 00:45 (final, after the fix-round rebuild) nothing pending
- done: first complete build (17 Nov 20:30); fix-round rebuild (18 Nov 00:43): abacus clicks removed + mix_v2 rebuilt,
  leaf lyric band, `work/cut/build_v3.sh`, verification, sheets and the named cut points looked at, QA doc, notes page,
  previews. No background processes. Nothing committed. Spend $0. Nothing of mine left in `work/tmp/`.
- in progress: nothing.
- next (for whoever resumes): if any `media/comp` file or `media/sound/mix_v2.wav` is newer than
  `work/cut/preview_v3/sources.txt`, run `work/cut/build_v3.sh` (about 4 min) and look at the changed shots.
- decisions: L2 slot = BED+CAR's L2 alone, L3 slot = L2b + L3 (keeps shots.json counts; match cut on 5660); the black
  ending is an appended END unit (`assemble.py --tail black`), shots.json untouched; I2 slot = BOOK's `pages/I2_full`;
  K1 = BED+CAR's K1.mp4 alone; shot id burn-in kept on both cuts as in preview_v2; other teams' renders re-run only
  where their contracts say to (B2; I1, K1, K2a in the first build), scripts unedited, old files in `work/cut/bak_v3/`;
  leaf lyric: F4b baseline y 0.965 at 90 %, F5 and F6a y 0.985 at 80 % (the English must stay on one row to clear the
  leaf's bottom rule at y 0.817 / 0.806); only the two named abacus events were removed from the cue sheet.

## DONE 00:45 (final rebuild after the fix round)
**Delivered** (all rebuilt 18 Nov 00:43)
- `media/cut/preview_v3.mp4` (lyrics on), `media/cut/preview_v3_clean.mp4` (off); identical copies
  `previews/chaosmonkey_preview_v3_540p.mp4`, `..._nolyrics.mp4`.
- Contact sheets `work/cut/preview_v3/contact_A..L.jpg`; review frames in `work/cut/qa/`.
- `docs/QA_PREVIEW_V3.md` (re-ranked: fixed / remaining; my read of each named cut point in §5).
- `review/preview_v3_notes.html` (rebuilt; stills from the new cut; question 7 no longer says a shot is unrevised).
- `media/sound/mix_v2.wav` (rebuilt), previous kept as `media/sound/mix_v2_prev.wav` (+ `layer_v2_prev.wav`).

**Verification** (`work/cut/preview_v3/verify.txt`): both cuts 5806 frames, 960x540, 24 fps CFR, video 241.9167 s, audio
241.9160 s; audio = new mix_v2 (correlation 0.9999, offset 0; in 113.5-114.7 s it matches the new mix 0.9997 vs the
old 0.9988); 65 shots at their exact shots.json counts and in-frames + END 86 f; no slate; no black frame outside
A1's first 4 frames and after 5714; no duplicated frame at any cut or splice.

**Sound**: events 113.688 and 114.135 removed from cue `abacus_f4b`; `build_v2.py` re-run. True peak -1.37 dBTP,
-15.84 LUFS, ending B, 241.920 s. Song part bit-identical (mix minus layer unchanged). New vs old mix: identical
outside 113.590-116.272 s. Inside it the two clicks are gone, the other layer sounds under them are 0.7-1.4 dB
louder (the bus no longer rides down for the clicks), and the four remaining clicks moved by at most 0.2 dB. So the
difference is confined to the abacus cue's span, not strictly to the two clicks' windows. Not listened to.

**Lyrics**: F4b, F5, F6a now sit in the bare band under the leaf, touching nothing. Other placements re-checked on the
re-rendered shots (A1 title and sign, C2, C5a, D2d, F2, I4, J1; L2b/L3 have no lyric): unchanged.

**Cut points** (QA §5): 2612/2665 F2 is the same child, seat and night, alive; still cooler (blue-violet) than F1/F3
and its window goes from flat dusk blue to a bright cream screen with no road behind it. 2882 clean, both 真 seals
shown (2859, 2875). 4581 the peak and the lit character carry; J2 is brighter and the lit character sits at the very
bottom edge of J2's first frames. 5660 a real match in framing and gesture (1988 tighter, seen from behind; hands
already at the chin). 5686 continuous. Neon: one sign, one colour in all nine attic shots that show the window; in
the close shots it reads as a legible sign facing the window, not as a steep wedge.

**Remaining, ranked**: 1 F2's colour/window against its neighbours; 2 G2 margins 9 levels brighter than G1/G3-G5;
3 J2 opens with the lit character at the frame edge; 4 the sign is not a wedge in close attic shots; 5 tone steps of
3-5/255 at the page landings; 6 no push into I3b; 7 B1 Mama is a shoulder; 8 L2b's blanket cue plays over a quilt
that is already tucked; 9 long stills (K5, K3, A1); 10 smears in E2/I2; 11 lyric residue on B4, H3, C1's rubbing
holds, D6's 6-frame tail; 12 C6->D1 paper 4 levels.

**Not done**: nothing watched in motion or listened to; lip-sync not re-gated (I4 was re-rendered in the fix round).

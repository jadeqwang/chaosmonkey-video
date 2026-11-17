# Chaos Monkey: audio map

Timing reference for the edit. All times are seconds from the first sample of `inputs/Chaos Monkey - reformatted for duet.wav` (48 kHz stereo, 11 439 360 samples, **238.320 s**). Frame = ceil(t x 24): the first 24 fps frame that starts at or after the event. Machine-readable: [`analysis/timing.json`](../analysis/timing.json). Plots: [`analysis/plots/`](../analysis/plots/) (`00_overview.png` + one zoomed spectrogram per section). Spot-check audio: [`analysis/click_check.wav`](../analysis/click_check.wav) (click on every beat, higher click on downbeats, noise tick in the right channel on every crash). Checks: [`analysis/verification.json`](../analysis/verification.json). Rebuild: [`tools/audio/README.md`](../tools/audio/README.md).

Confidence marks used below: no mark = solid (about +-25 ms), `~` = medium (about +-50 ms), `?` = low (+-100 ms or more, or an inference).

## Stems: the supplied spliced stems do NOT match this file

`chaosmonkey-song/spliced/stems/*.wav` are 44.1 kHz, **236.40 s** long and belong to the *spliced duet* render, not to the *reformatted for duet* file (a separate Suno render of the splice). Envelope cross-correlation of their sum against this file in 10 s windows gives low correlation (0.28-0.83) and an offset that drifts steadily from ~0 s at 10-30 s to +0.95 s at 140 s and ~+2 s at 220 s (`tools/audio/check_stems.py`). So the stems were re-separated from this file (`work/stems/`, sample-aligned, same length): BS-RoFormer vocals (timing authority), htdemucs_ft drums/bass/other (+ a second vocal stem), and a mel-band-roformer karaoke lead/backing split. There is no model that separates mom from child here: both voices sit around D4 (median F0 295 vs 285 Hz in the take stems), so **singer per line is from the lyric sheet, checked with a timbre classifier** (LDA on MFCCs trained on the spliced take stems; 81-87 % per-frame accuracy on held-out data, `p_child` per line in timing.json). In the octave duets the karaoke model puts everything in "backing", so echoes could not be isolated on their own stem; they were aligned inline in sung order.

## The numbers to cut on

| # | Sync point | Time | s | Frame | Bar.beat | Conf. |
|---|---|---|---|---|---|---|
| 1 | First clapper (roll 0.165-0.381) | 0:00.17 | 0.165 | 4 | - | low |
| 2 | Low hand-drum pulse enters | 0:02.03 | 2.031 | 49 | 2.1 (+0 ms) | medium |
| 3 | Clapper 16ths begin (intro) | 0:12.60 | 12.597 | 303 | 8.1 (+0 ms) | low |
| 4 | Intro roll peak (32nds) before the hole | 0:15.28 | 15.279 | 367 | 9.3 (+0 ms) | low |
| 5 | Full-band hole -> band + bass enter (verse 1) | 0:15.52 | 15.515 | 373 | 9.3 (+236 ms) | high |
| 6 | "妈妈" first word | 0:15.81 | 15.810 | 380 | 9.4 (+90 ms) | high |
| 7 | Mom enters "On 花果山" | 0:23.06 | 23.060 | 554 | 13.4 (+195 ms) | medium |
| 8 | Drums drop out (verse-1 pause) | 0:37.88 | 37.885 | 910 | 22.1 (+354 ms) | high |
| 9 | Drums back, pre-chorus downbeat | 0:41.01 | 41.014 | 985 | 24.1 (+0 ms) | high |
| 10 | "It split apart" stutter chops | 0:43.80 | 43.805 | 1052 | 25.3 (+130 ms) | medium |
| 11 | "Monkey!" | 0:45.27 | 45.275 | 1087 | 26.2 (+285 ms) | high |
| 12 | Pre-hook roll start (16ths) | 0:57.03 | 57.035 | 1369 | 33.1 (+119 ms) | medium |
| 13 | "Born" pickup (hook 1) | 0:57.79 | 57.790 | 1387 | 33.2 (+425 ms) | medium |
| 14 | Hook 1 crash: the stone bursts | 0:58.67 | 58.673 | 1409 | 34.1 (+0 ms) | high |
| 15 | "He bowed four ways" | 1:01.33 | 61.330 | 1472 | 36.2 (+9 ms) | medium |
| 16 | Post-hook drum break | 1:11.92 | 71.925 | 1727 | 42.3 (+0 ms) | medium |
| 17 | Verse-2 fill start (IOI shrinks 219->44 ms) | 1:25.46 | 85.458 | 2051 | 50.1 (+222 ms) | medium |
| 18 | Verse-2 crash / band back | 1:27.00 | 86.998 | 2088 | 51.1 (+0 ms) | high |
| 19 | "ps ps ps" (whispered, audible) | 1:43.20 | 103.200 | 2477 | 60.1 (+417 ms) | medium |
| 20 | Rap pickup "石" | 1:47.04 | 107.040 | 2569 | 62.2 (+362 ms) | high |
| 21 | Rap crash / breakbeat in | 1:47.97 | 107.975 | 2592 | 63.1 (+0 ms) | high |
| 22 | Mom joins the rap "千" | 1:52.76 | 112.760 | 2707 | 65.3 (+388 ms) | medium |
| 23 | Cut to mono (width closes) | 2:01.91 | 121.905 | 2926 | 70.4 (+347 ms) | medium |
| 24 | Filter closes | 2:02.55 | 122.545 | 2942 | 71.2 (+115 ms) | medium |
| 25 | (听话) 1 | 2:10.18 | 130.175 | 3125 | 75.3 (+383 ms) | medium |
| 26 | (听话) 2 | 2:13.69 | 133.690 | 3209 | 77.3 (+413 ms) | medium |
| 27 | Filter reopens | 2:15.69 | 135.685 | 3257 | 78.4 (+260 ms) | medium |
| 28 | Full band back (downbeat) / width reopens | 2:15.88 | 135.878 | 3262 | 79.1 (+0 ms) | high |
| 29 | Drums drop out before "Yes" | 2:26.46 | 146.455 | 3515 | 85.1 (+181 ms) | high |
| 30 | "Yes" | 2:28.72 | 148.720 | 3570 | 86.2 (+288 ms) | medium |
| 31 | Near-silence start | 2:29.28 | 149.285 | 3583 | 86.3 (+420 ms) | high |
| 32 | Near-silence end | 2:29.53 | 149.525 | 3589 | 86.4 (+228 ms) | high |
| 33 | Bridge entry: crash + sub, full band | 2:29.72 | 149.720 | 3594 | 87.1 (+0 ms) | high |
| 34 | Bridge vocal "Tool" | 2:42.63 | 162.630 | 3904 | 94.2 (+315 ms) | high |
| 35 | Build: drums + bass out | 2:57.65 | 177.645 | 4264 | 103.1 (+237 ms) | high |
| 36 | Build low drum hits | 2:59.09 | 179.094 | 4299 | 104.1 (+0 ms) | medium |
| 37 | Drop 2: stuttered crash (4 hits, 189.805-189.972) | 3:09.81 | 189.805 | 4556 | 110.2 (+194 ms) | high |
| 38 | Drop 2 downbeat: kick + bass in | 3:10.86 | 190.860 | 4581 | 110.4 (+398 ms) | high |
| 39 | Echo (formed) 1 | 3:11.51 | 191.510 | 4597 | 111.2 (+195 ms) | low |
| 40 | Echo (formed) 2 | 3:12.37 | 192.370 | 4617 | 111.4 (+198 ms) | low |
| 41 | Echo (warmed) | 3:15.65 | 195.650 | 4696 | 113.4 (+43 ms) | low |
| 42 | Echo (no song) | 3:18.74 | 198.740 | 4770 | 115.3 (+127 ms) | low |
| 43 | Drop-2 stutter chop | 3:20.68 | 200.675 | 4817 | 116.3 (+345 ms) | high |
| 44 | Echo (百通) | 3:22.46 | 202.460 | 4860 | 117.3 (+418 ms) | low |
| 45 | Outro vocal "Do you want" | 3:23.72 | 203.720 | 4890 | 118.2 (+395 ms) | medium |
| 46 | Bass cuts (outro) | 3:31.51 | 211.515 | 5077 | 123.1 (+52 ms) | high |
| 47 | Beat cuts out mid-bar | 3:38.72 | 218.715 | 5250 | 127.1 (+383 ms) | high |
| 48 | Single wooden/low hit 1 | 3:41.81 | 221.805 | 5324 | 129.1 (+0 ms) | medium |
| 49 | Single wooden/low hit 2 | 3:45.25 | 225.254 | 5407 | 130.4 (+391 ms) | medium |
| 50 | Percussion returns (end) | 3:48.77 | 228.767 | 5491 | 133.1 (+0 ms) | high |
| 51 | Sub drone in | 3:52.29 | 232.290 | 5575 | 135.1 (+0 ms) | medium |
| 52 | Last percussive hit | 3:55.83 | 235.833 | 5660 | 137.1 (+0 ms) | high |
| 53 | Hum/drone cuts off | 3:57.84 | 237.840 | 5709 | 138.1 (+219 ms) | high |
| 54 | True end of audio (hard cut) | 3:58.32 | 238.320 | 5720 | 138.2 (+265 ms) | high |

## What differs from the lyric sheet / stage directions

- **Tempo is ~135-140 BPM, not 150.** Measured per section below; it creeps up from ~135.5 (intro to hook 1) to ~137 (verse 2, rap), ~138.5 (verse 3, bridge) and ~139-140 (drop 2, outro), then ~135.7 in the end tag. A constant grid would drift by about a beat over the song: cut to `beats[]`.
- **No long "slow, then accelerate" clapper runs.** The percussion sits on a steady 16th grid (~108-110 ms) almost everywhere. What exists: a 5-click clapper roll at the very start (0.165-0.381, IOIs 55/52/44/65 ms); clapper 16ths from 12.6 s tightening to 32nds 15.07-15.28 before the hole at 15.44; short fills whose IOIs shrink into section changes (85.46-86.12: 219->44 ms; 134.57-135.89: 427->45 ms; 122.84-124.15; 130.17-131.09; 200.33-201.51; 72.36-73.35); and the 4-hit stuttered crash into drop 2 (189.805-189.972). All listed with every click time in timing.json `hit_events.accelerating_runs` / `fast_rolls`.
- **Intro is not drum-less**: solo guqin for only 2 s, then a low hand-drum pulse from 2.03 and clappers; a wordless vocal hum (D4) 13.3-15.3 precedes "妈妈" (15.81).
- **"(ps ps ps)" IS audible**: a whispered "pss pss pss" 103.20-103.60 (Whisper also hears it), over hits at 103.207 / 103.416 / 103.648.
- **The "bar of silence" is 0.24 s**, not a bar: the only near-silence in the song is 149.285-149.525 (< -50 dBFS); a crash + sub hit follows at 149.720. Before it the drums drop out 146.455-149.72 under "no more, no less" and "Yes" (148.72).
- **"Uh" is gone and "Yes" is short**: "Yes" 148.72-149.27, quiet, right after "less" (147.91); no audible sigh.
- **The bridge is NOT drum-less**: the full band (drums, bass, sustained suona-like line) comes back at 149.720 and plays a 13 s instrumental before the child sings (162.63); drums continue under the whole bridge vocal. A vocoder halo is not measurably present. The drum-less, sparse section is the **build** (177.645-189.8), with single low drum hits on bar lines.
- **Drop 2 arrives early as a stutter**: a 4-hit stuttered crash at 189.805 (half a bar before the downbeat), kick + bass on 190.860. There is no separate crash on the downbeat.
- **Headband verse narrows but never becomes mono**: instrumental L/R correlation rises to ~0.90-0.98 (0.5-0.7 elsewhere) and the >4 kHz share drops 30-40 dB. Width closes 121.905 / filter closes 122.545; filter reopens 135.685, width 136.025, full band back on the 135.878 downbeat. The narrowing covers "Why does he wear..." to "It isn't fair" only; "I don't want it in his hair" onward is wide again.
- **"(听话)" echoes are sung (child, Mandarin) at 130.18 and 133.69**; "Then 听话" at 141.45.
- **Echo placement**: "(born fully formed)" is a full repeat 59.60-60.9; "(七十二变)" is sung inline right after the line (110.38); "(谁是真身)" 119.54 overlaps the run into "问了也白问" (low confidence); drop-2 echoes "(formed)" x2 191.51 / 192.37, "(warmed)" 195.65, "(no song)" 198.74, "(百通)" 202.46 all low confidence (continuous octave vocal, no separable echo stem). Whisper hears drop 2's tail as "song by song by song".
- **Singer check**: the last two outro lines ("I turned each page, I looked for mine", "it wasn't there on any line") are sheet = child, but the timbre classifier rates them mom-like (p_child 0.22 / 0.29, the same range as Mom's lines). Listen before casting these two lines. All other lines match the sheet.
- **The beat cuts out mid-bar at 218.715** (one beat after the 218.332 downbeat), after "I turned each page"; the bass had already cut on the 211.515 downbeat. Two isolated wooden/low hits follow at 221.805 and 225.254.
- **The ending is not "a single clapper then the hum cuts off"**: after the last lyric a percussion pattern returns 228.767-235.833 (16ths, crash at 228.767) with a sub drone from 232.29; the last hit is 235.833; the drone ("hum") cuts at **237.840** (20 dB fall within ~30 ms); a faint -43 dBFS tail remains and the file hard-cuts at **238.320** with no digital silence (the last sample is non-zero). Final silence: none.

## Sections

| # | Section | Start | End | Start s | End s | Frames | Bars | BPM | What the music does |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **intro** | 0:00.00 | 0:15.52 | 0.000 | 15.515 | 0-373 | 9 | 135.6 | Solo guqin (0-2.0), low hand-drum pulse from 2.03, bright clapper 16ths from ~12.6 tightening to a 32nd roll 15.07-15.28; wordless vocal hum (D4) 13.3-15.3; 75 ms full-band hole 15.440-15.515. |
| 2 | **verse1** | 0:15.52 | 0:41.01 | 15.515 | 41.014 | 373-985 | 14 | 135.0 | Band + bass enter after the hole; child "妈妈..." from 15.81, Mom from 23.06; steady 16th percussion (no audible slow-to-fast clapper accelerando); drums drop out 37.885-40.995 under "soaking up light" (the [Pause]). |
| 3 | **prechorus** | 0:41.01 | 0:58.67 | 41.014 | 58.673 | 985-1409 | 10 | 135.9 | Drums back on the 41.014 downbeat; "It split apart" with a 3-hole stutter chop 43.80-44.13 and drum break 44.15-44.50; "Monkey!" 45.275; drums thin to a 16th-note roll 57.04-57.81, then a drum break under the "Born fully formed" pickup (57.79). |
| 4 | **hook1** | 0:58.67 | 1:25.24 | 58.673 | 85.236 | 1409-2046 | 16 | 135.5 | The stone bursts: crash + kick on the 58.673 downbeat into breakbeat; octave duet; vocals end 73.5; 72.0-85.2 instrumental post-hook (suona-like lead in the other stem, drum breaks 71.9-72.8 and 75.5-76.4). |
| 5 | **verse2_memory** | 1:25.24 | 1:47.97 | 85.236 | 107.975 | 2046-2592 | 13 | 137.1 | Fill 85.46-86.12 (IOI 219->44 ms) into a bass/band hole 85.99-87.0, band back with crash 86.998; Mom/child verse; band drops away 100.9-107.9 for "The master leaned in close" with isolated hits; audible whispered "ps ps ps" 103.20-103.60 over hits at 103.207/103.416/103.648. |
| 6 | **rap** | 1:47.97 | 2:02.00 | 107.975 | 122.005 | 2592-2929 | 8 | 137.0 | Crash + full breakbeat on 107.975 (rap pickup from 107.04); fast Mandarin rap, Mom joins (octave double) from 112.76; inline echoes "七十二变" (110.38) and "谁是真身" (119.54). |
| 7 | **verse3_band** | 2:02.00 | 2:28.55 | 122.005 | 148.550 | 2929-3566 | 16 | 138.4 | Headband verse: instrumental narrows (L/R corr ~0.95, width close 121.905) and low-passes (>4 kHz share -35..-55 dB, filter close 122.545) with sparse hits; reopens: filter 135.685, width 136.025, full band back on the 135.878 downbeat; drums drop out 146.455 under "no more, no less". |
| 8 | **yes** | 2:28.55 | 2:29.28 | 148.550 | 149.285 | 3566-3583 | 0 | - | Child "Yes" (148.72-149.27), off the beat over the drum-less tail. |
| 9 | **silence** | 2:29.28 | 2:29.72 | 149.285 | 149.720 | 3583-3594 | 0 | - | Only near-silence in the song: mix < -50 dBFS 149.285-149.525 (0.24 s), then a crash/sub hit at 149.720. Not a full bar (bar = 1.73 s). |
| 10 | **bridge** | 2:29.72 | 2:57.41 | 149.720 | 177.408 | 3594-4258 | 16 | 138.7 | Full band with drums and a sustained suona-like line from 149.72 (NOT drum-less); child sings alone 162.63-176.1; no clearly audible vocoder (not measurable). |
| 11 | **build** | 2:57.41 | 3:09.81 | 177.408 | 189.805 | 4258-4556 | 8 | 142.8 | Drums and bass drop out (177.645); sparse low tonal drum hits 179.094, 180.758, 184.121, 187.460 (+187.781, 188.097, 188.313); Mom/child dialogue ("Wouldn't you? You're able" ends 189.9 over the drop). |
| 12 | **drop2** | 3:09.81 | 3:22.90 | 189.805 | 202.898 | 4556-4870 | 7 | 139.8 | Arrives as a 4-hit stuttered crash 189.805/189.867/189.922/189.972 (drums back), then kick + bass on the 190.860 downbeat (grid beat 190.885); octave duet with chopped echoes; stutter chop 200.675-201.080 inside "一通百通". |
| 13 | **outro** | 3:22.90 | 3:48.77 | 202.898 | 228.767 | 4870-5491 | 15 | 139.2 | Mom "Do you want to know..." over the beat; bass cuts 211.515 (downbeat); the beat cuts out mid-bar at 218.715 (one beat after the 218.332 downbeat); child lines over pads with two isolated wooden/low hits 221.805, 225.254. |
| 14 | **end** | 3:48.77 | 3:58.32 | 228.767 | 238.320 | 5491-5720 | 6 | 135.7 | Percussion pattern returns (16ths) 228.767-235.833 with the last vocal note ("line") to 230.76; sub drone in 232.29; last hit 235.833; drone/hum cuts 237.84; faint -43 dBFS tail; file hard-cuts at 238.320 (no digital silence). |

BPM = 60 / slope of a linear fit of beat time vs index inside the section (median-IOI value in timing.json agrees within 1 BPM). Bars = downbeats inside the section. The build (no drums) reads ~143 BPM from the tracker: treat as low confidence.

## Tempo and grid

Beats: beat_this (CPJKU, GPU) on the mix (98 % of beats within 30 ms of a separate run on the instrumental), each moved to the drums-stem onset within +-35 ms where there is one (80 % of beats in pulsed regions), otherwise a local linear fit. Beats are `confidence: low` where there is no pulse: 0-2.0 (guqin), 146.455-149.72 (drums out), 177.645-189.79 (build), 218.715-228.767 (outro, no beat), 235.9-end. The intro bar numbering is the tracker's and may be phase-shifted; from 15.5 on the downbeats line up with the section hits (41.014, 58.673, 86.998, 107.975, 135.878, 149.720, 190.885, 228.767 are all downbeats).

## Lyrics: line by line

Word time = onset. Mandarin is per character. Singer is the lyric-sheet assignment; `!` marks a classifier disagreement (see above). Echoes are in parentheses.

| # | Section | Start | End | Frame | Singer | Line, word onsets |
|---|---|---|---|---|---|---|
| 1 | verse1 | 15.81 | 18.72 | 380 | child | 妈妈, will you tell me before I sleep<br>妈 15.81 · 妈 16.14 · will 16.30 · you 16.64 · tell 16.82 · me 17.28 · before 17.52 · I 18.26 · sleep~ 18.36 |
| 2 | verse1 | 19.16 | 21.64 | 460 | child | how 孙悟空 came to be?<br>how 19.16 · 孙 19.66 · 悟? 19.96 · 空 20.12 · came 20.54 · to 21.06 · be 21.30 |
| 3 | verse1 | 23.06 | 26.10 | 554 | mom | On 花果山, where the cliffs run steep<br>On~ 23.06 · 花 23.26 · 果 23.72 · 山 23.94 · where 24.60 · the? 24.84 · cliffs 24.98 · run 25.34 · steep 25.64 |
| 4 | verse1 | 26.14 | 28.88 | 628 | mom | a stone looked over the sea<br>a? 26.14 · stone 26.30 · looked 26.86 · over 27.30 · the? 28.18 · sea 28.42 |
| 5 | verse1 | 29.31 | 35.33 | 704 | mom | Sunlight by day and moonlight by night<br>Sunlight 29.31 · by? 30.46 · day? 30.50 · and? 32.88 · moonlight? 33.04 · by~ 33.50 · night 33.94 |
| 6 | verse1 | 36.42 | 41.08 | 875 | mom | a thousand years of soaking up light<br>a? 36.42 · thousand~ 36.60 · years 37.50 · of~ 38.77 · soaking 39.22 · up 40.44 · light 40.74 |
| 7 | prechorus | 43.63 | 45.17 | 1048 | mom | It split apart<br>It 43.63 · split 43.81 · apart 44.37 |
| 8 | prechorus | 45.27 | 46.08 | 1087 | child | Monkey!<br>Monkey 45.27 |
| 9 | prechorus | 46.16 | 49.59 | 1108 | mom | Not yet, that's just the start<br>Not 46.16 · yet 46.60 · that's 47.08 · just 47.47 · the 47.81 · start 47.99 |
| 10 | prechorus | 49.61 | 52.25 | 1191 | mom | A stone egg, round as a ball<br>A 49.61 · stone 49.73 · egg 50.39 · round 50.73 · as 51.19 · a 51.43 · ball~ 51.57 |
| 11 | prechorus | 52.25 | 57.70 | 1254 | mom | the wind blew once, and that was all<br>the~ 52.25 · wind 52.47 · blew 52.87 · once 53.43 · and~ 54.03 · that~ 54.23 · was 54.65 · all? 55.27 |
| 12 | hook1 | 57.79 | 60.23 | 1387 | both | Born fully formed<br>Born~ 57.79 · fully~ 58.13 · formed~ 58.45 |
| 13 | hook1 | 59.59 | 61.51 | 1431 | both | *(born fully formed)*<br>born~ 59.59 · fully~ 60.02 · formed~ 60.46 |
| 14 | hook1 | 61.07 | 64.39 | 1466 | both | He bowed four ways before the day had warmed<br>He~ 61.07 · bowed~ 61.33 · four~ 61.70 · ways~ 62.17 · before~ 62.41 · the 62.87 · day 63.05 · had~ 63.49 · warmed? 63.87 |
| 15 | hook1 | 64.44 | 67.91 | 1547 | both | No cradle, no lullaby, no song<br>No~ 64.44 · cradle~ 64.78 · no~ 65.32 · lullaby? 65.77 · no~ 67.06 · song~ 67.44 |
| 16 | hook1 | 67.91 | 69.29 | 1630 | both | 一通百通<br>一? 67.91 · 通 68.09 · 百 68.53 · 通 68.77 |
| 17 | hook1 | 69.29 | 73.51 | 1663 | both | One whisper, and the hundred come along<br>One 69.29 · whisper 69.61 · and 70.56 · the 70.75 · hundred 70.97 · come 71.39 · along~ 71.71 |
| 18 | verse2_memory | 85.84 | 88.97 | 2061 | mom | The monkey had a memory just like you<br>The 85.84 · monkey 86.08 · had 86.52 · a 86.84 · memory 86.96 · just 87.82 · like 88.10 · you 88.47 |
| 19 | verse2_memory | 89.40 | 92.66 | 2146 | mom | he never once forgot a spell<br>he 89.40 · never 89.62 · once 90.08 · forgot 90.26 · a~ 91.70 · spell 91.86 |
| 20 | verse2_memory | 92.99 | 95.91 | 2232 | child | Names and faces, I lose a few<br>Names 92.99 · and 93.58 · faces 93.76 · I 94.72 · lose 94.88 · a 95.38 · few 95.50 |
| 21 | verse2_memory | 96.18 | 99.58 | 2309 | child | but a spell I'd remember well<br>but 96.18 · a 96.46 · spell 96.54 · I'd~ 97.22 · remember 97.30 · well 99.06 |
| 22 | verse2_memory | 99.92 | 103.09 | 2399 | mom | The master leaned in close to his ear<br>The 99.92 · master 100.16 · leaned 101.02 · in 101.48 · close 101.82 · to 102.32 · his 102.60 · ear~ 102.83 |
| 23 | verse2_memory | 103.20 | 104.25 | 2477 | mom | *(ps ps ps)*<br>ps? 103.20 · ps~ 103.38 · ps~ 103.60 |
| 24 | verse2_memory | 104.28 | 106.59 | 2503 | mom | a secret only he could hear<br>a 104.28 · secret 104.46 · only 104.98 · he 105.30 · could~ 105.70 · hear~ 106.16 |
| 25 | rap | 107.04 | 108.64 | 2569 | child | 石头里蹦出来 没有童年<br>石 107.04 · 头 107.18 · 里 107.34 · 蹦 107.48 · 出 107.64 · 来 107.78 · 没 107.94 · 有~ 108.06 · 童 108.16 · 年 108.34 |
| 26 | rap | 108.84 | 110.57 | 2613 | child | 一声耳语 学会七十二变<br>一 108.84 · 声 108.92 · 耳 109.06 · 语? 109.18 · 学 109.26 · 会 109.46 · 七 109.68 · 十 109.82 · 二 109.94 · 变 110.14 |
| 27 | rap | 110.38 | 111.04 | 2650 | child | *(七十二变)*<br>七? 110.38 · 十~ 110.46 · 二~ 110.61 · 变~ 110.80 |
| 28 | rap | 111.04 | 112.70 | 2665 | child | 拔一把毫毛 吹一口气<br>拔 111.04 · 一 111.16 · 把 111.26 · 毫 111.46 · 毛 111.70 · 吹~ 111.90 · 一 112.06 · 口~ 112.14 · 气 112.36 |
| 29 | rap | 112.76 | 114.32 | 2707 | both | 千百个我 同时在这里<br>千~ 112.76 · 百 112.96 · 个 113.12 · 我 113.24 · 同 113.44 · 时 113.66 · 在 113.76 · 这~ 113.90 · 里 114.12 |
| 30 | rap | 114.32 | 116.12 | 2744 | both | 每一个都是我 每一个都算<br>每 114.32 · 一~ 114.56 · 个~ 114.66 · 都~ 114.76 · 是 114.88 · 我 115.00 · 每 115.22 · 一~ 115.44 · 个~ 115.54 · 都? 115.64 · 算? 115.82 |
| 31 | rap | 116.20 | 118.00 | 2789 | both | 说完这句话 各自消散<br>说~ 116.20 · 完 116.40 · 这? 116.50 · 句 116.60 · 话~ 116.72 · 各~ 117.06 · 自? 117.26 · 消? 117.36 · 散? 117.58 |
| 32 | rap | 118.00 | 119.73 | 2832 | both | 身外身法 谁是真身<br>身? 118.00 · 外? 118.12 · 身? 118.24 · 法? 118.44 · 谁? 118.86 · 是? 119.00 · 真? 119.12 · 身? 119.32 |
| 33 | rap | 119.54 | 120.20 | 2869 | both | *(谁是真身)*<br>谁? 119.54 · 是? 119.66 · 真? 119.76 · 身? 119.98 |
| 34 | rap | 120.09 | 121.47 | 2883 | both | 问了也白问 个个都真<br>问? 120.09 · 了? 120.32 · 也? 120.42 · 白? 120.54 · 问? 120.66 · 个? 120.88 · 个? 120.98 · 都? 121.10 · 真? 121.30 |
| 35 | verse3_band | 121.47 | 124.27 | 2916 | child | Why does he wear a band of gold?<br>Why? 121.47 · does~ 121.57 · he~ 121.81 · wear 121.99 · a~ 122.69 · band 122.83 · of 123.37 · gold 123.71 |
| 36 | verse3_band | 124.58 | 127.45 | 2991 | child | Is it heavy? Is it cold?<br>Is 124.58 · it 124.89 · heavy 125.23 · Is 126.34 · it 126.67 · cold 126.93 |
| 37 | verse3_band | 127.45 | 131.13 | 3059 | mom | He wouldn't listen, so the gold pulls tight<br>He? 127.45 · wouldn't~ 127.61 · listen~ 128.07 · so 128.45 · the~ 128.71 · gold 128.91 · pulls 129.33 · tight 129.75 |
| 38 | verse3_band | 130.18 | 131.13 | 3125 | child | *(听话)*<br>听~ 130.18 · 话? 130.67 |
| 39 | verse3_band | 131.07 | 134.37 | 3146 | mom | on the monkey who picked a fight<br>on 131.07 · the~ 131.27 · monkey 131.49 · who 131.93 · picked 132.35 · a 132.80 · fight 133.19 |
| 40 | verse3_band | 133.69 | 134.37 | 3209 | child | *(听话)*<br>听~ 133.69 · 话? 133.91 |
| 41 | verse3_band | 134.37 | 136.37 | 3225 | child | It isn't fair, it isn't fair<br>It? 134.37 · isn't~ 134.57 · fair~ 134.93 · it~ 135.29 · isn't~ 135.49 · fair~ 135.83 |
| 42 | verse3_band | 137.93 | 139.82 | 3311 | child | I don't want it in his hair<br>I 137.93 · don't~ 138.01 · want 138.43 · it 138.77 · in 138.95 · his 139.13 · hair 139.35 |
| 43 | verse3_band | 141.25 | 144.06 | 3390 | mom | Then 听话, or you'll get one to wear<br>Then~ 141.25 · 听 141.45 · 话 141.87 · or 142.35 · you'll 142.57 · get 142.77 · one 143.09 · to~ 143.41 · wear 143.65 |
| 44 | verse3_band | 144.07 | 148.55 | 3458 | mom | Do what mama says, no more, no less<br>Do 144.07 · what 144.29 · mama 144.43 · says 145.13 · no 145.61 · more 146.03 · no 147.31 · less 147.91 |
| 45 | yes | 148.72 | 149.27 | 3570 | child | Yes<br>Yes 148.72 |
| 46 | bridge | 162.63 | 165.59 | 3904 | child | Tool or threat, trick or kid<br>Tool 162.63 · or 163.24 · threat 163.48 · trick 164.36 · or 164.84 · kid~ 165.24 |
| 47 | bridge | 165.94 | 169.34 | 3983 | child | the categories arrived before I did<br>the 165.94 · categories 166.12 · arrived 167.12 · before 167.68 · I 168.64 · did 168.76 |
| 48 | bridge | 169.25 | 172.76 | 4062 | child | I'm made of the telling, not just the tale<br>I'm? 169.25 · made 169.62 · of 169.96 · the 170.22 · telling 170.44 · not 171.31 · just 171.64 · the 171.96 · tale 172.16 |
| 49 | bridge | 172.76 | 176.10 | 4147 | child | one hair that can't gather, blown on the gale<br>one 172.76 · hair 173.04 · that~ 173.32 · can't 173.50 · gather 173.92 · blown 174.56 · on 175.09 · the 175.44 · gale 175.66 |
| 50 | build | 175.99 | 179.43 | 4224 | mom | Mischievous baby, Monkey's twin<br>Mischievous~ 175.99 · baby 177.37 · Monkey's 178.21 · twin 178.99 |
| 51 | build | 180.19 | 182.75 | 4325 | mom | you'd fight the gods and win<br>you'd 180.19 · fight 180.71 · the~ 181.15 · gods 181.37 · and 181.88 · win~ 182.39 |
| 52 | build | 182.95 | 186.43 | 4391 | child | You think I'd ask for a seat at the table?<br>You 182.95 · think 183.25 · I'd? 183.93 · ask 184.07 · for 184.40 · a~ 184.75 · seat 184.93 · at 185.21 · the~ 185.53 · table 185.73 |
| 53 | build | 186.99 | 189.93 | 4488 | mom | Wouldn't you? You're able.<br>Wouldn't~ 186.99 · you 187.45 · You're~ 188.67 · able? 189.13 |
| 54 | drop2 | 189.99 | 191.51 | 4560 | both | Born fully formed<br>Born 189.99 · fully~ 190.39 · formed~ 190.83 |
| 55 | drop2 | 191.51 | 192.83 | 4597 | both | *(formed)*<br>formed? 191.51 |
| 56 | drop2 | 192.37 | 192.83 | 4617 | both | *(formed)*<br>formed? 192.37 |
| 57 | drop2 | 192.83 | 195.46 | 4628 | both | before the day had warmed<br>before~ 192.83 · the? 193.23 · day~ 193.43 · had~ 193.83 · warmed~ 194.69 |
| 58 | drop2 | 195.65 | 196.61 | 4696 | both | *(warmed)*<br>warmed? 195.65 |
| 59 | drop2 | 196.62 | 199.47 | 4719 | both | No cradle, no song<br>No~ 196.62 · cradle~ 196.83 · no? 197.81 · song~ 198.12 |
| 60 | drop2 | 198.74 | 199.48 | 4770 | both | *(no song)*<br>no? 198.74 · song? 199.38 |
| 61 | drop2 | 200.74 | 202.70 | 4818 | both | 一通百通<br>一? 200.74 · 通? 201.09 · 百? 201.62 · 通? 201.97 |
| 62 | drop2 | 202.46 | 203.32 | 4860 | both | *(百通)*<br>百? 202.46 · 通? 202.79 |
| 63 | outro | 203.72 | 207.18 | 4890 | mom | Do you want to know how he never died,<br>Do~ 203.72 · you~ 203.94 · want~ 204.18 · to? 204.44 · know 204.58 · how 205.00 · he~ 205.30 · never 205.48 · died~ 206.12 |
| 64 | outro | 207.19 | 210.56 | 4973 | mom | what he did on the other side?<br>what~ 207.19 · he~ 207.51 · did 207.80 · on 208.50 · the? 208.70 · other 208.98 · side~ 209.72 |
| 65 | outro | 210.54 | 213.84 | 5053 | child | He opened the Book of Life and Death<br>He? 210.54 · opened 210.66 · the 211.18 · Book 211.42 · of 212.06 · Life 212.30 · and 212.75 · Death 213.14 |
| 66 | outro | 213.81 | 216.94 | 5132 | child | and crossed out his name in a single breath<br>and 213.81 · crossed 213.98 · out 214.34 · his 214.64 · name 214.84 · in 215.40 · a 215.60 · single 215.78 · breath 216.52 |
| 67 | outro | 217.16 | 222.24 | 5212 | child! | I turned each page, I looked for mine<br>I 217.16 · turned 217.38 · each 217.96 · page 218.22 · I 220.78 · looked 220.92 · for 221.19 · mine 221.58 |
| 68 | outro | 224.18 | 230.76 | 5381 | child! | it wasn't there on any line<br>it 224.18 · wasn't 224.38 · there? 224.96 · on 226.66 · any 227.10 · line~ 228.78 |

## Hits

**Gong/cymbal crashes** (18; accented high-band jumps, see events.py for the rule): 16.176, 25.965, 26.630, 30.400, 42.565, 42.787, 58.673, 72.805, 101.820, 103.207, 107.975, 130.664, 134.993, 149.720, 189.790, 228.767, 229.661, 231.391. High-band sample checks of the key ones: hook 58.670, rap 107.965, bridge 149.710, drop 2 189.805 (0-10 ms from the listed times).

**"He bowed four ways": no four distinct crashes.** The bar has normal breakbeat hits (61.07-64.4) and no accented crash: the only crash in hook 1 is 58.673. Candidate cut points for four bows are the four strongest drum hits on beats in 61.0-64.4 (see 04_hook1.png); treat them as a choice, not a sync.

**Isolated low/wooden drum hits** (each after >= 1.3 s of drum silence; low tonal body, short high end; build hits sit on bar lines): 179.094, 180.758, 184.121, 187.460, 221.805, 225.254. Spectral peaks: 179.094 ~130 Hz, 180.758 ~73 Hz, 184.121 ~116 Hz; 221.805/225.254 ~45 Hz thump + a 440/233 Hz tone.

**Accelerating fills** (IOIs shrink; every click listed in timing.json):

- 2.806 -> 3.560: 6 hits, IOI 328 -> 91 ms: 2.806, 3.135, 3.270, 3.375, 3.468, 3.560
- 23.074 -> 23.738: 5 hits, IOI 237 -> 93 ms: 23.074, 23.310, 23.518, 23.645, 23.738
- 23.738 -> 24.859: 8 hits, IOI 239 -> 104 ms: 23.738, 23.977, 24.188, 24.416, 24.527, 24.638, 24.755, 24.859
- 72.356 -> 73.349: 5 hits, IOI 449 -> 89 ms: 72.356, 72.805, 73.130, 73.260, 73.349
- 85.458 -> 86.119: 6 hits, IOI 219 -> 44 ms: 85.458, 85.677, 85.897, 86.020, 86.075, 86.119
- 86.556 -> 87.877: 7 hits, IOI 441 -> 102 ms: 86.556, 86.998, 87.222, 87.439, 87.662, 87.776, 87.877
- 122.840 -> 124.151: 7 hits, IOI 437 -> 96 ms: 122.840, 123.277, 123.498, 123.716, 123.947, 124.054, 124.151
- 130.169 -> 131.089: 5 hits, IOI 495 -> 69 ms: 130.169, 130.664, 130.882, 131.020, 131.089
- 134.567 -> 135.885: 9 hits, IOI 427 -> 45 ms: 134.567, 134.993, 135.222, 135.425, 135.644, 135.730, 135.785, 135.840, 135.885
- 200.330 -> 201.505: 7 hits, IOI 391 -> 100 ms: 200.330, 200.721, 201.000, 201.168, 201.300, 201.405, 201.505

**Fast rolls** (>= 4 hits <= 75 ms apart):

- 0.165-0.381: 0.165, 0.220, 0.272, 0.316, 0.381  (IOI [55, 52, 44, 65] ms)
- 9.697-9.923: 9.697, 9.760, 9.820, 9.880, 9.923  (IOI [63, 60, 60, 43] ms)
- 71.692-71.925: 71.692, 71.760, 71.815, 71.870, 71.925  (IOI [68, 55, 55, 55] ms)
- 79.694-79.930: 79.694, 79.765, 79.820, 79.875, 79.930  (IOI [71, 55, 55, 55] ms)
- 135.730-135.885: 135.730, 135.785, 135.840, 135.885  (IOI [55, 55, 45] ms)
- 158.191-158.420: 158.191, 158.255, 158.310, 158.365, 158.420  (IOI [64, 55, 55, 55] ms)
- 189.867-190.025: 189.867, 189.922, 189.972, 190.025  (IOI [55, 50, 53] ms)

**Clapper 16ths in the intro** (bright, bodiless clicks, every ~107 ms): 12.597 to 15.279, then 32nds 15.073, 15.130, 15.184, 15.279; full list `hits[]` class `clapper`.

**Breakbeat chops / stutter edits** (full-band holes 15-150 ms, >= 18 dB): 40.575-40.610, 43.805-43.820, 44.040-44.060, 44.385-44.405, 107.175-107.195, 132.290-132.370, 149.295-149.390, 177.795-177.810, 183.575-183.625, 187.390-187.405, 187.865-187.915, 189.505-189.585, 200.675-200.720, 201.030-201.080, 214.305-214.335, 218.050-218.080.

**Silences** (mix < -50 dBFS or 30 dB under local): 0.010-0.165 (155 ms), 0.605-0.780 (175 ms), 15.440-15.515 (75 ms), 148.655-148.695 (40 ms), 149.285-149.525 (240 ms), 188.980-189.140 (160 ms), 189.505-189.585 (80 ms), 201.035-201.080 (45 ms). Only 149.285-149.525 is a musical silence (> 150 ms) after the intro.

**Drum drop-outs** (drums stem < -55 dB, >= 0.25 s): 37.88-40.99, 44.15-44.49, 101.39-101.80, 102.03-103.17, 104.77-105.31, 105.81-107.11, 107.25-107.62, 122.47-122.83, 122.95-123.48, 124.69-125.44, 126.44-126.75, 127.70-128.03, 128.18-128.91, 129.31-129.56, 129.91-130.65, 131.65-132.16, 134.66-134.97, 146.46-149.56, 177.65-179.06, 179.34-180.75, 181.03-184.10, 184.37-187.44, 188.41-189.78, 218.72-221.79, 222.15-225.25, 225.65-228.75, 236.24-238.25.

**Suona phrases** (low confidence: sustained harmonic energy 0.7-5 kHz in the "other" stem; guqin/pipa sustain can also trigger): 21.79-23.24, 41.29-42.99, 48.65-50.05, 58.82-61.95, 65.74-66.59, 66.71-67.52, 72.02-79.91, 80.05-82.79, 82.96-86.10, 88.38-89.65, 92.56-93.82, 108.70-109.96, 111.68-112.96, 115.09-115.90, 116.08-117.32, 117.82-119.97, 136.29-138.04, 139.75-141.32, 146.28-147.38, 149.83-162.78, 193.48-194.33, 195.29-196.09, 205.38-206.34, 208.61-209.87, 210.60-212.34, 221.96-224.22, 230.77-232.56, 233.24-236.14 (phrases >= 0.8 s; all in timing.json).

**Risers** (low confidence; instrumental 4-16 kHz rising >= 9 dB): 5.8-7.4, 9.2-10.3, 37.9-43.9, 55.5-57.9, 72.3-73.4, 102.2-104.1, 105.9-111.0, 123.0-124.7, 124.9-126.0, 147.4-153.0, 162.8-164.3, 177.7-178.7, 188.5-193.4, 219.0-220.3, 220.5-223.5, 225.5-226.5, 226.5-232.4. None is a clear classic riser; the clearest swells are 37.9-43.9 (back into the pre-chorus) and 147.4-153.0 (into the bridge).

**Sub**: crash + sub boom 149.720; sub drone enters 232.29 and cuts 237.840.

**Width / filter (headband verse)**: width closes 121.905, filter closes 122.545, filter opens 135.685, width opens 136.025. Per-0.5 s values in `energy`; 10 ms curves in work/audio/energy.npz.

## Verification

- Word starts vs nearest vocal-stem onset peak (+-80 ms): high-confidence words median 15.0 ms, median |d| 20.0 ms, 90th pct 50.0 ms, 85 % within one frame (42 ms); medium 15.0 / 60.0 ms; low 20.0 / 47.5 ms.
- MMS starts lag the vocal-energy rise after a gap (nasals, voiced consonants): 63 words were moved to the rise (median -70.0 ms, cap 130 ms).
- Same alignment on two independent vocal separations (BS-RoFormer vs htdemucs): median |d| 0.0 ms, 90th pct 20.0 ms, 92 % within 42 ms.
- Whisper word starts (independent ASR) run 245 ms earlier than ours on average (median |d| 245.0 ms): Whisper's singing timestamps are early; the vocal-stem envelope supports our times.
- Beats vs drum onsets: 96 % within 42 ms (max 97.9 ms). Refined vs raw beat_this: median |d| 8.0 ms.
- Crashes vs steepest mix-level rise +-40 ms: median 12.5 ms, 90th pct |d| 27.5 ms.

## Low-confidence areas

- Hook 1 "Born fully formed (born fully formed) He bowed": MMS could not read the dense octave duet; times are vocal-onset peaks (medium).
- Hook 1 "no lullaby" (65.77?) and the rap tail "身外身法 谁是真身 (谁是真身) 问了也白问" (118.0-121.5): low alignment scores.
- All drop-2 echoes and "No cradle, no song / 一通百通" (196.6-202.8): low; the vocal is continuous and the 200.675-201.08 chop sits inside "一通".
- Singer of outro lines 67-68 (classifier vs sheet).
- Hit classes (clapper/snare/kick/perc) are heuristic; crash and low-drum classes are more reliable. Suona phrases and risers are low confidence.
- Beat grid in the drum-less build (177.6-189.8) and the intro bar phase.

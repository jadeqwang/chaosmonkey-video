# LOG v4 LIPSYNC

## DONE (final): two-pass recipe (Kling act calm -> p-video-animate with the song), 8/20 takes PASS by eye, every test line has a
passing take (F1 rap a soft pass, 1 in 5 seeds with --rap). Spend $43.78. Full report: docs/LIPSYNC_V4.md sections 4-9.

## READY, RECIPE CHANGED (see docs/LIPSYNC_V4.md): Kling act (calm) -> pruna/p-video-animate with the song window, frame 0 = t0, shift 0.
Wrapper `tools/gen/lipsync_v4.py act | anim | measure | eye`. Seedance (below) is now the fallback: about 1 take in 6 passes.

## READY (provisional recipe, 1st batch; superseded)
**Seedance 2.5, first frame = the shot keyframe, `reference_audios` = the vocal stem window with 1 s of digital silence before and after,
`generate_audio:true`, 720p, acting AND singing in the prompt, 6 takes per line; each take placed in the cut by its lag measured from
the face (`tools/review/ls4_lag.py`), judged on the 2x face strip. Wrapper: `tools/gen/lipsync_v4.py sing | measure | eye`.**
Passing by eye so far: adult Mama C3 (ls4_C3_sd_3), adult Jade I4 (ls4_I4_sd_2), child B1 (ls4_B1_sd_3, borderline-pass).
Rap F1: no pass yet. Pass rate so far about 3 of 12 takes (25 %) under the measure-and-place rule. Face at least ~240 px in the cut.
p-video-avatar as picture: FAIL on all 5 (reframes, off-model, eyes, sway). v2v two-pass: not working yet (7003).

Team lead: Claude (Opus 5.5). Brief: REVISION_V4 §1.2, §6. Ceiling $90. Spend tag prefix `ls4_`. Project total at start: $361.81.

## CHECKPOINT 1 (start)
- done: read REVISION_V4, TEAMS_V4, LIPSYNC_V3, VIDEO_BAKEOFF (catalog, V5), LOG_v3_lipsync, tools.
- finding: relay results for Kling (and other providers) carry the provider's public signed output URL in `res:<job>`
  (`media[0].url`, Kling CDN, expiry about 30 days). That URL can be passed to Seedance `reference_videos` with no bucket and
  no Worker change. To be tested (avenue 4).
- in progress: catalog refresh + probe; test-line set-up (B1c, C3, F1, I4_jade keyframes, windows from analysis/timing.json).
- next: Seedance 2.5 image+audio many takes; p-video-avatar from the shot keyframe; Seedance v2v from Kling URL; visual strip tool.
- pending relay jobs: none.
- questions for the lead: none yet.

## CHECKPOINT 2
- done: catalog refreshed (cards @ a4144c7, 18 Nov). New video models: seedance-1-pro/-fast/1.5-pro (own audio only, no audio
  input), kling-v2.6 / v2-6 & v3 motion-control (image_url + video_url, public URLs), ltx-2-3-fast/pro (no audio input). Audio-or-video
  input + first frame: seedance-2.5 (reference_audios, reference_videos), pruna p-video-avatar (audio), pruna p-video-animate
  (video + image, uses the source's audio), gemini-omni (audio field; v3: "not enabled"), kling motion-control (video).
- tools: `tools/gen/ls4_bake.py` (spec writer, all methods), `tools/review/lipsync_v4.py` (audiolag: placement from the take's own
  soundtrack, validated 0 ms on the bit-aligned avatar; strip: 2x lower-face strip every 2nd frame + jaw_r). Calibration strip of
  the v3 C3 transfer: `work/review/lipsync_v4/v3_C3_take1_face.jpg` (pasted grin shapes, teeth popping, little jaw travel = what Jade saw).
- in progress: batch 1 (22 jobs, ids in work/lipsync4/b1.txt; wait log work/lipsync4/b1_wait.log): Seedance 2.5 image+audio
  with generate_audio:true x3 on B1/C3/F1(tight)/I4; p-video-avatar from shot keyframes (holding prompt) + tight crops;
  p-video-animate on acted Kling takes + stem; Seedance reference_videos = Kling provider URL + audio (B1, C3).

## CHECKPOINT 3
- done: batch 1 measured and judged (my eye on B1_sd_2, C3_sd_3; fresh Sonnet judge on all 18: work/review/lipsync_v4/judge_batch1.md).
  Seedance output audio = our reference passed through at offset 0 (raw xcorr peak exactly at t0) -> it says nothing about the mouth;
  lag must come from the face. New `tools/review/ls4_lag.py` (phrase-structure xcorr + viseme refine) validated on avatar takes
  (+1/+2 f = the known mouth lead) but FAILS on continuous rap (F1 avatar -20 f): hence the 1 s silence pads in batch 2.
  Gate got `--scan N` (default 12 as before). READY written (provisional). Wrapper `tools/gen/lipsync_v4.py`.
- two-pass v2v (Seedance reference_videos = Kling CDN URL): gateway accepts the URL, provider rejects after ~40 s (7003, reason not
  stored). One direct call to read the reason timed out client-side at 25 s; logged at $1.72 to be safe (probably not billed).
  p-video-animate: "Request size limit exceeded" (fixed: 480p crf 30 source).
- in progress: batch 2 (work/lipsync4/b2.txt + ls4_C3_omni_1): padded shot windows x3 per line, B1 full 7 s line, vocal stem vs full
  mix (B1, C3), animate x2, v2v with a ByteDance-hosted reference URL (is the Kling URL the problem?), gemini-omni image+audio.
- spend: about $42 by pre-charge estimates (includes v2vsd assumed 15 s; refined on collect).

## CHECKPOINT 4
- batch 2 results: padded-silence Seedance takes are NOT better: the model sings into the silent pad (I4_sdp_2 opens 13 f before the
  first word) and re-sings at its own tempo inside a take (same take holds "able" ~25 f late): Seedance treats reference audio as
  something to re-perform, not as a frame-locked driver. Numeric lag is not certifiable on these lines: the viseme scan is flat and
  multimodal (on an avatar take with true lag 0 its top peak is -11 f). Plot: work/review/lipsync_v4/gap_vs_audio.png.
  v2v with a ByteDance-hosted reference URL: same 7003 -> the URL was not the problem; reference_videos + reference_audios is refused.
  gemini-omni image+audio: 7003 again (audio not enabled). C3_sdp_2 7003 (unexplained, one-off).
- **p-video-animate works as an audio-driven re-render**: source = acted Kling take with the vocal window muxed in, image = keyframe.
  C3: source FAIL (env -285 ms r 0.26, open 0.56) -> animate in sync at shift 0 (env +48 ms r 0.63, open 1.0), on-model, Kling's
  acting kept (my eye: work/review/lipsync_v4/ls4_C3_anim_C3_1_face.jpg). B1: good f0-86, face SMEARS f92-112 during the source's
  double bounce -> source acting must be calm (no bounce, no fast head turns).
- in progress (work/lipsync4/b3.txt): Kling acted takes x2 per line with a CALM clause (B1 7 s, C3, F1 tight, I4), then animate on
  each; animate seed variance on C3 act1/act2 (x2 each).
- spend: $40.78 (ls4_ tags, refunds applied).

## CHECKPOINT 5 (resumed after usage-limit stop)
- batch 2 judged (fresh Sonnet, work/review/lipsync_v4/judge_batch2.md): Seedance with 1 s silence pads passes 1 of 14 (F1_sdp_2,
  marginal); skips words, sings into the pad, drifts; full mix no better than the vocal stem; the 7 s B1 line breaks after "sleep".
- batch 3: Kling acted takes x2 per line with the CALM clause (all good acting; F1 has real rap body language: two-finger count,
  point at lens). Animate seeds on C3 v3 acted takes: 5 of 5 land at +7..+48 ms (trusted envelope r 0.59-0.64, viseme 0 +-1 f),
  4 of 5 pass the numbers -> animate timing is locked, unlike Seedance.
- batch 4 (work/lipsync4/b4.txt): animate x2 seeds on every new acted take: 15 done, 1 provider error (B1_animK2_1, 2002).
- next: gate at shift 0 + face strips for all animate takes (Sonnet), fresh-eye judgement, then finalise LIPSYNC_V4.md with
  animate (two-pass) as THE recipe, Seedance as fallback, table of pass rates.
- wrapper tools/gen/lipsync_v4.py now has act | anim | seedance | measure | eye.
- pending relay jobs: none. spend ~ $46 (to re-sum).

## CHECKPOINT 6
- done: LIPSYNC_V4.md rewritten with the two-pass recipe, conditions, tools, partial table (animate rows PENDING). READY block updated.
- in progress: Sonnet subagent measuring + judging the 15 animate takes (ls4_*_animK*); its notes file
  work/review/lipsync_v4/judge_anim_notes.md, result work/review/lipsync_v4/judge_anim.md. Earlier judges: judge_batch1.md, judge_batch2.md.
- next: my own look at the best animate strip per line; fill table + best takes; final report.
- pending relay jobs: none. spend $43.03.
- b5 (F1 rap instruction prompt, animate x5): ids work/lipsync4/b5.txt, specs media/gen/specs/ls4_F1_animR*_*.json

## CHECKPOINT 7
- done: animate judged (judge_anim.md, notes judge_anim_notes.md): 8 PASS / 6 BORDERLINE / 1 FAIL by the judge; I overrode
  F1_animK2_2 to BORDERLINE (first phrase mouthed small) -> 7/15. LIPSYNC_V4.md sections 1-8 written with real numbers.
- in progress: b5 = F1 animate x5 with a rap instruction prompt (work/lipsync4/b5.txt, wait log b5_wait.log).
- next: judge b5 (subagent), update F1 rows, final report. Spend $43.03 + b5 ~$0.75.

## DONE
- F1 rap batch (b5, --rap instruction prompt): 1 soft PASS (ls4_F1_animR2_3, judge + my eye), 2 borderline, 2 fail (judge_rap.md).
- Final picks: B1 ls4_B1_animK1_1 (frame0 15.31), C3 ls4_C3_animK1_1 (45.67), F1 ls4_F1_animR2_3 (106.54, frames 12-55), I4
  ls4_I4_animK2_2 (186.49). Wrapper docstring fixed (tools/gen/lipsync_v4.py); lipsync_take.py marked retired.
- No pending relay jobs. Nothing committed. Temp files in work/tmp, work/lipsync4.

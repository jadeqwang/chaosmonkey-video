# Pipeline recon: what earlier productions built, and how to reuse it

Written 2026-11-16 for the Chaos Monkey production, read-only against earlier projects. Nothing was generated and nothing
was spent. Abbreviations: **HV** = /home/jade/Documents/halys-video (Nov 2026, the newest), **HF** = 1-music-shipped/holdfire,
**MG** = 1-music-shipped/moongazing, **MGP** = 1-music-shipped/moongazing-public-version, **RW2** = 1-music-shipped/rewind-take-two,
**OS** = 1-music-shipped/orbital-sunrise-video, **RE** = 1-music-shipped/rare-earth-techno-remix, **MM** = merge-me-back-to-main.
`S/` = /home/jade/Documents/1-music-shipped.

**Best single source:** `HV/docs/HARVEST.md` (480 lines). It already distils HF, HMV, MG, RW2 and OS into model notes, tooling,
encode recipes, sound rules and the end-card spec. Read its sections 1 and 3 to 6 before starting work.

Status of the copy: `tools/gen/`, `tools/review/` and `tools/edit/` were copied from HV on 2026-11-16, with the obvious
renames applied (section 12). `docs/gen_catalog/` was copied too, because without it cf.py cannot price a call and the spend
cap reads the call as $0.

---

## 1. Cloudflare auth and transport

**Provider.** Everything goes through Jade's Cloudflare account. There are no fal, Replicate, OpenAI or Google keys
anywhere (MM/docs/prior_pipeline_brief.md §1).

**Credentials** are read at call time by `tools/gen/cfauth.py`. Values are never printed or written.
- Token, in order of preference:
  1. env `CLOUDFLARE_API_TOKEN`, if set.
  2. Otherwise the wrangler OAuth token, keys `oauth_token` and `expiration_time` in `~/.config/.wrangler/config/default.toml`
     (path override: env `WRANGLER_CONFIG`).
  - If the token expires within 2 minutes, cfauth runs `npx -y wrangler whoami` (180 s timeout), which uses the stored
    `refresh_token`, then re-reads the file. If that fails, Jade has to run `npx wrangler login`.
- Account id: env `CF_ACCOUNT_ID` (or `CLOUDFLARE_ACCOUNT_ID`), else the first token of `<repo>/work/cf_account_id.txt`.
- Relay KV namespace id: env `GEN_KV_NS`, else `<repo>/work/gen_kv_ns.txt`.
- Cloud sessions: `CF_AUTH_VIA_PROXY=1`, set automatically when there is no wrangler file. The egress proxy injects the token
  and no Authorization header is sent.

**Auth status today (2026-11-16):**
- The wrangler file exists (mode 600) and holds a refresh token. Its access token expired 2026-11-15 07:20Z. It will
  auto-refresh on the first call; I did not run `wrangler whoami`, because that writes outside this repo.
- `HV/work/cf_account_id.txt` and `HV/work/gen_kv_ns.txt` exist. **Chaos Monkey's `work/` has neither yet.** This blocks
  every paid call until the lead runs:
  `cp /home/jade/Documents/halys-video/work/{cf_account_id.txt,gen_kv_ns.txt} /home/jade/Documents/chaosmonkey-video/work/`
  (both must stay gitignored; there is no .gitignore here yet), or exports the two env vars.
- `HF/tools/t2/restore_media.py:19-21` hardcodes the ids in code. Don't copy that file into a public repo.

**Endpoints** (`tools/gen/cf.py`):
- Unified catalog (google/*, openai/*, bytedance/*, klingai/*, alibaba/* ...):
  `POST https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run` with body `{"model": ID, "input": {...}}`.
  The response is `{"result":{"state":"Completed","result":{"image"|"video":url|data-uri}}}`.
- Workers AI: `POST .../ai/run/@cf/<model>` with the input as the body.
- `"file:<path>"` strings inside an input become data: URIs.
- Every call is logged to `media/genlog.jsonl`. Billing rows are also written to `docs/spend_ledger.jsonl`, which is
  committed and union-merged so the cap holds across machines.

**Async video, via the relay** (`tools/gen/gen.py`). The model run can't be polled: `GET /ai/runs/{id}` returns 405. So
jobs go through Jade's existing Worker **`rare-earth-v3-relay`** (cron every minute, bindings AI + KV `rare-earth-v3-jobs`).
**Never deploy, modify or delete Workers or KV namespaces.** Only write and read your own keys.
1. The client PUTs `job:<minuteBucket>:<PREFIX><tag>-<hex>` = `{"model","input"}`.
   - The first bucket is now + 2 min.
   - 2 jobs start per minute (`GEN_PER_MINUTE`), shared with every other project.
   - The body must be ≤ 24 MiB (the KV limit is 25 MiB). Use `gen.py ref-image` to shrink references.
2. The cron for that minute deletes the job key and writes `state:<id>`, runs `env.AI.run` (no HTTP timeout), mirrors
   outputs to `media:<id>:<n>[:<chunk>]` (20 MB chunks, **TTL 21 days**) and writes `res:<id>`.
3. The client polls `res:`, then downloads the `media:` chunks, falling back to the provider URL (h3 returns a raw task URL).
   - Files land in `media/gen/<tag>_<hex>.mp4`.
   - Job state is kept in `media/gen/manifest.json`, under a file lock.
- The prefix is `chaosmonkey/` in the copy. Taken prefixes: halys/, holdfire/, moongazing/, rewind/, rewind2/, mergemain/,
  vibesong/.
- Images: use the direct sync call. In a cloud session, `GEN_IMAGES_VIA_RELAY=1` routes them through the relay, because
  direct calls die at about 30 s there.

**Failure modes and retries:**
- `run_model` retries 2× with 5 s and 10 s backoff. It never retries HTTP 400/404, 7003 or "User Input Error".
- Relay jobs that are `stale` (cron minute missed, > 10 min): `gen.py requeue ID`, or leave `python3 tools/gen/watchdog.py`
  running.
- A job `running` for more than 30 min hit the wall limit: count it and resubmit once (HV/HANDOFF_ROUND8.md:92).
- Errored jobs are normally not billed; vgen logs them as refunds.
- 2047 "Invalid User Credentials" is intermittent and refunded: resubmit.
- 6 parallel image calls gave 6001 / HTTP 500. Keep to ≤ 3 image calls in parallel, 1 for edits
  (HV/docs/HARVEST.md §4; HV/docs/KEYFRAME_BRIEF.md: "One paid call at a time").
- Model-specific errors:
  - `reference_videos` given as a data: URI fails with 7003; it needs a public URL.
  - Veo `image_input` must be raw base64; gen.py strips the data: header.
  - xai/grok-imagine-video is unsupported (it needs a presigned upload URL).
  - MiniMax h3 failed 5 of 5 in HV's bake-off with 7003.
  - The Seedance privacy filter (`PrivacyInformation`) fires on photoreal face sheets; `use_virtual_avatar:true` gets past it.
  - OS once hit a gateway "Insufficient balance".
- Latency: median 8.9 min submit-to-file (p90 15.6, max 30.8). Nano Banana Pro takes 21–64 s direct, 2–7 min via the relay
  (HARVEST §3, §4).
- Collect within 21 days and back up `media/gen/`: the mirror expires.

## 2. Model catalog (Cloudflare unified catalog, cards @ cloudflare-docs c678d0b, 2026-11-13; all live on the 2026-11-14 probe)

Full cards with JSON schemas are in `docs/gen_catalog/<author>-<model>.json`, prices in `docs/gen_catalog/INDEX.tsv` and live
fields in `LIVE.tsv`. Refresh both for free with `tools/gen/catalog.py` (an invalid-input probe; nothing runs).

### Video
| id | $/s (list) | inputs (live fields) | verdict, with source |
|---|---|---|---|
| `klingai/kling-v4` | 720p .157, 1080p .235 | first_frame, middle_frames (≤9, **untested**), last_frame, 3–30 s, 16:9 | **HV all-rounder**: faces, wide plates, identity. With first + last frame it holds a whole 8 s scene; first frame only holds 3–4 s. Prompt overcrank ("filmed at 120 fps, played back at 24") gives real slow motion. Frames 0 and 1 of a chained link are near-duplicates (HV/docs/BAKEOFF.md:8, :281; HV/docs/ROUND4_TESTS.md §1, §3.1) |
| `klingai/kling-v4-flash` | 720p .094 | text only (no image) | untested |
| `klingai/kling-v3` / `-v3-omni` | .112 / .113 (.168 / .145 with sound) | image_input, sound | untested |
| `alibaba/hh1.1-i2v` (HappyHorse 1.1) | 720p .14, 1080p .18 | image, 3–15 s | **HV combat winner**: blows land with weight and weapons keep their shape. Cheapest per usable second ($0.28). No end frame, no slow motion (it re-stages instead); invents after about 3.5 s (BAKEOFF.md:278, :300; ROUND4_TESTS §2.2, §3.2) |
| `alibaba/hh1.1-r2v`, `hh1.1-t2v`, `hh1-*` | .14–.28 | r2v: `images` (references) | untested |
| `google/veo-3.1` | .20 (.40 with audio); 4K .40 | image_input (raw b64), duration "4s"/"6s"/"8s", generate_audio (**defaults to true**: set false) | **Quiet precise shots**: macro hands, true slow motion, locked stares. "Never use Veo for multi-figure action" (morphing weapons, merged bodies). Can pull back unasked; ignores "no blink" (BAKEOFF.md:289; HARVEST §3) |
| `google/veo-3.1-fast` | 720p .08, 1080p .10 | same | could not place fine contacts: 9 takes, none usable (HARVEST §3) |
| `bytedance/seedance-2.0` (`-fast`, `-mini`) | 480p .07 / 720p .15 / 1080p .37 (fast .06/.12; mini .04/.09) | image, last_frame_image, ≤4 reference_images, reference_video; **mini also takes reference_audio** | HV backup for locked plates and slow motion; redraws frame 0, so grade-match at the cut. Once returned 21:9. HF's non-sung workhorse (BAKEOFF.md:10; HARVEST §3) |
| `bytedance/seedance-2.5` | 480p .1028, 720p .2312 (video refs .43 / .97) | image, last_frame, reference_images, reference_videos, **reference_audios (≤10 clips, ≤30 s)**, 4–30 s, 480p/720p only | **The lip-sync model of every sung project** (section 6). Does not hold the first frame; random aspect (use an explicit 16:9 guard); `camera_fixed` is ignored; `generate_audio` trips the copyright filter. HV: "consistently unacceptable" for photoreal i2v (BAKEOFF.md:294; HARVEST §3) |
| `minimax/h3` / `h3-max` / `h3-lite` / `h3-highspeed` | .08 (2K .13) / .05–.08 / .025–.04 / .06 | `content` list (gen.py converts the simple keys) | MG/RW2: holds the keyframe better than 2.5, but stutters (frames repeated 2–3×) and carries an AAC track. HV: 0/5 accepted (7003). h3-max rejected first + last (HARVEST §3) |
| `minimax/hailuo-2.3` / `-fast` | 6 s@768p $0.28 / $0.19 | first_frame_image | untested |
| `alibaba/wan-2.7-i2v` | 720p .10, 1080p .15 | image | HV: drop. 30 fps, head turns, grins, blade morphs (BAKEOFF.md:296) |
| `alibaba/wan-3.0` / `-prime` | .05–.20 / .068–.28 | **text only** | untested |
| `runwayml/gen-4.5` | .12 (720p) | image_input | HV: drop. Breaks obedience (BAKEOFF.md:295) |
| `runwayml/aleph-2` | .336 | video_uri, keyframes (v2v) | error 2047 in MG |
| `vidu/q3-pro` / `q3-turbo` | 540p .05 … 1080p .15 / .04–.07 | start_image, end_image | HV: emergency fallback only. Unrequested camera moves, invents props (BAKEOFF.md:299) |
| `google/gemini-omni-1.2-flash` (1.1, plain) | tokens (out video $12/1M) | text, image, last_frame, reference_images, video, audio | HV: drop. Invented costume; defaults to 10 s (BAKEOFF.md:297) |
| `lightricks/ltx-2-5-fast` | .09–.37 | image_uri, last_frame_uri, fps | untested |
| `pixverse/v6`, `v5.6` | .025–.09 | image_input, audio | untested |
| `black-forest-labs/flux-3-video` | hd .15, fhd .24, v2v | mode t2v/i2v/v2v | untested |
| `pruna/p-video-avatar` | 720p .025, 1080p .045 | image + audio (talking head) | MG: the only model that really followed the phrase (audio corr 0.998), but grins with full teeth, tilts the head, reframes; not used (section 6) |
| `pruna/p-video`, `-animate`, `-replace` | .005–.06 | | p-video-replace gave 7003 in MG |
| `veed/fabric-1.0` (`-fast`) | 480p .08, 720p .15 | image_url + audio_url (talking head) | untested; a lip-sync candidate |
| `black-forest-labs/flux-video-upscale` | precise $0.07/MP·s, creative .10 | input_video ≤ 20 s / 50 MB, factor 1.5–3 | HF: **best 720p→1080p upscale for cel art** ("keeps the look … no invented detail"), 23 clips $16.11. Logs as $0: log it by hand (HARVEST §6) |
| `topaz/starlight-fast-2`, `-precise-2-6` | $0.12/unit | HTTPS video_uri only | HF: Starlight Fast "smeared lineart, blobbed lashes" |
| `bria/v-rmbg-3.0` | .0225 | video background removal | untested; useful for cut-out elements |

### Image
| id | price | inputs | verdict |
|---|---|---|---|
| `google/nano-banana-pro` | ≈ $0.134 at 1K/2K, $0.24 at 4K | ≤ **3** image_input, image_size 1K/2K/4K, 16:9 2K = 2752×1536 | The HV/HF keyframe workhorse (329 calls, $44 in HV). Best multi-reference identity; also the standard blockout-to-render tool (section 5). Returns the old picture when it is among the inputs; mangles small text; resists identity-level edits. A crude paint-over plus "clean this up" carries edits best (HARVEST §4) |
| `google/nano-banana-2` / `-2.1` / `-2-lite` / `nano-banana` | token-priced, cheaper | `resolution` instead of image_size | untested in HV |
| `openai/gpt-image-2` | ≈ $0.19–0.24 with refs | up to 16 refs, native 2048×1152 | follows left/right best; good with text; caps references at 1280 px (HARVEST §4) |
| `openai/gpt-image-2.5-sunburst` / `-flare` | ≈ $0.19 high | ≤ 16 refs, **3:2 only** | **RE: best for the canonical anime character sheet**; MM canon face v4 edits. Edit mode near-copies (RE/docs/PROCESS.md:29, 121-131) |
| `bytedance/seedream-5-pro` / `5-lite` / `4.5` / `4.0` | $0.045 + $0.03/ref / .035 / .04 / .03 | ≤ 10 refs, 2560×1440 | "the most painterly oil": wrong for photoreal. **Worth testing for ink/gouache plates here** |
| `black-forest-labs/flux-2-max` / `-pro-preview` / `-flex`, `flux-1-kontext-pro`/`-max`, `flux-3-image-klein` | .03–.08 | input_images / input_image | FLUX.2 max lost on noisy detail (HV boards) |
| `xai/grok-imagine-image(-2.0/-quality)` | .02–.05 | | cheap probes, 8.5 s; "goes kitsch on 'cinematic/epic'" |
| `alibaba/qwen-image-3.0-pro`, `wan-2.6-image`, `krea/krea-2-*`, `krea-3`, `recraft/*` (incl. vector), `kling-v3-image`, `bria/fibo-*`, `pruna/p-image*` | .005–.30 | | untested. Recraft vector variants are an option for seal and stamp art; Qwen-Image is reputed for CJK text (untested; text is set in code anyway) |
| `pruna/p-image-upscale` | $0.005 at 1–4 MP | | HF upscaled 1376×768 relay keyframes with it |
| `bria/remove-background` | .018 | | cut-outs (or local BiRefNet, section 11) |

**Free image generation:** codex's built-in `image_gen` tool (section 8). MG used it for Jade-likeness repaints, and every
prompt file in `/home/jade/Documents/character sheets/*.md` says "Mode: built-in image_gen".

**Audio models seen:** `elevenlabs/music-v2` ($0.0025/s, also used for SFX), `minimax/music-2.6`, eleven-v3 TTS,
grok-stt.

**HV spend by model** (`HV/docs/spend_ledger.jsonl`, $316.68 total):

| Model | Spend | Calls |
|---|---|---|
| kling-v4 | $181.66 | 152 |
| nano-banana-pro | $44.22 | 329 |
| hh1.1-i2v | $42.48 | 50 |
| veo-3.1 | $26.40 | 28 |
| seedance-2.0 | $9.25 | — |
| seedance-2.5 | $5.78 | — |
| vidu-q3-pro | $3.75 | — |
| wan-2.7 | $1.50 | — |
| gen-4.5 | $1.20 | — |
| gpt-image-2.5-sunburst | $0.37 | — |
| flux-2-max | $0.07 | — |

**Price per usable second** (HV/docs/BAKEOFF.md:303):

| Model | $ per usable second |
|---|---|
| HappyHorse | $0.28 |
| Kling v4 | $0.32 |
| Veo 3.1 | $0.36 (Veo in its own lane: $0.22) |
| Seedance 2.0 | $0.56 |

**Caveat for this film:** every HV verdict is for *photoreal* footage. Chaos Monkey is ink-on-paper and cel-shaded, and the
brainstorm asks the video model to animate only one element (mist, water, a figure) on a still plate. Re-run a small
bake-off on a paper plate, using the brief's "Motion, from a still plate" prompt:
- candidates: Kling v4, HappyHorse 1.1, Veo 3.1, Seedance 2.0 at 1080p, and Seedance 2.5 for any sung face;
- judge on whether paper and rock stay static, and on ink-coverage drift (brief, "Prompting for whitespace").

## 3. Running the tools (copied into `tools/`)

**Python:** `PY=/home/jade/Documents/halys-video/.venv/bin/python`.
- It has torch 2.6 cu124, torchvision, jsonschema, av, cv2, PIL, numpy, yaml, demucs, faster_whisper, beat_this, librosa and
  transformers (verified).
- The docstrings now point to it. There is no `.venv` in chaosmonkey-video yet; make one with uv, or keep borrowing HV's.
- Run from the repo root. ffmpeg is `/usr/bin/ffmpeg` (env `FFMPEG` overrides).

**Images (sync).**
```
$PY tools/gen/cf.py google/nano-banana-pro media/kf/S01_nbp_v1.jpg \
  '{"prompt":"...","aspect_ratio":"16:9","image_size":"2K","output_format":"jpg","image_input":["file:design/sheet.jpg"]}' --tag=kf_S01
$PY tools/gen/cf.py MODEL OUT --prompt "..." --set key=value ... [--dry-run]     # dry run = schema check + price, no call
```
Save the prompt beside each image as `<name>.txt` and keep the rejects (KEYFRAME_BRIEF.md).

**Video (relay).**
```
$PY tools/gen/gen.py spec TAG MODEL --prompt "..." [--image KF] [--last-frame KF2] [--ref-image R ...] \
      [--audio SRC@START+DUR ...] [--set key=json ...]           # -> media/gen/specs/TAG.json
$PY tools/gen/gen.py submit media/gen/specs/TAG.json --dry-run   # validate + estimate, nothing queued
$PY tools/gen/gen.py submit media/gen/specs/TAG.json             # prints chaosmonkey/TAG-<hex>
$PY tools/gen/gen.py wait ID [ID ...] --timeout=3000             # poll + collect -> media/gen/TAG_<hex>.mp4
$PY tools/gen/gen.py status | collect [ID] | requeue ID
$PY tools/gen/gen.py audio-ref SRC START DUR OUT.mp3             # exact audio window (adds ~25 ms mp3 delay)
$PY tools/gen/gen.py ref-image SRC OUT.jpg --max=2048
```
- Spec format: `{"model","tag","notes","input":{...}}`.
- `DEFAULTS` in gen.py fill required keys for seedance-2.0/2.5, h3 and hailuo. **Seedance 2.5 defaults to 480p**: pass
  `--set resolution=720p`.
- Veo has no defaults: pass `image_input`, `duration=8s`, `aspect_ratio`, `resolution=1080p` and `generate_audio=false`.
- Kling v4 first + last frame: write the spec by hand.
  `{"model":"klingai/kling-v4","input":{"prompt","first_frame":"file:..","last_frame":"file:..","duration":8,"aspect_ratio":"16:9","resolution":"1080p"}}`
  Prompt: "The video starts exactly on @image_1 and ends exactly on @image_2 …" (ROUND4_TESTS.md §3.1).

**Bake-off.** `tools/gen/bakeoff.py` writes one spec per model from the same keyframe and prompt. Model keys: veo31, kling4,
sd20, sd25, hh11, wan27, omni12, gen45, vidu3, h3.
```
$PY tools/gen/bakeoff.py SHOT media/kf/SHOT_pick_1080.jpg "prompt" --models kling4,hh11,veo31 --dur 5 --suffix t1
$PY tools/gen/gen.py submit media/gen/specs/bk_SHOT_*_t1.json
```

**Review** (`tools/review/`). Output goes to `work/review/bakeoff/`.
- `bakeoff_intake.py` probes clips, matches the first frame (corr/SSIM), and measures Farneback motion and camera drift.
- `bakeoff_sheets.py` subcommands: sheets (10 frames), `compare SHOT t...`, `crop SHOT name x y w h t...`.
- `bakeoff_grid.py` makes a synced 3-across labelled grid mp4.
- `sheet.py`, for any clip:
  - `sheet CLIP OUT.jpg [--n=10] [--t=..]`
  - `crop CLIP OUT x y w h t1 t2..`
  - `frame CLIP OUT.png t`

**Round-based takes.** Register shots in `tools/gen/shots.py`: `SHOTS = {"NAME": dict(model=, image=, duration=, prompt=, refs=, audio=)}`.
Each take lands in `media/gen/<SHOT>/take_N.{spec.json,json,mp4,_sheet.jpg}`.
```
$PY tools/gen/vgen.py submit SHOT --takes=2 --res=720p [--dry-run]
$PY tools/gen/vgen.py wait
$PY tools/gen/vgen.py sheet OUT.jpg
$PY tools/gen/vgen.py spend
```

**Spend and cap.** `$PY tools/gen/spend.py [--tags]` adds up `media/genlog.jsonl`, `docs/spend_ledger.jsonl` and
`media/gen/spend.jsonl`, deduplicated.
- `cf.generate`, `gen.submit` and `vgen.submit` all call `spend.check()` and refuse to go over the cap.
- Cap = env `CHAOSMONKEY_CAP`, else `DEFAULT_CAP_USD` in `tools/gen/spend.py` (**placeholder $200: Jade must confirm**).
- Failed sync calls aren't counted; relay jobs count from submit and are refunded on error.
- The figures are list-price estimates; the real bill can't be read with the wrangler token.

**Edit / assemble** (`tools/edit/README.md`). Inputs: `docs/shots_src.yaml` → `docs/shots.json`, `analysis/timing.json` (beat,
word and hit anchors), `docs/picks.json`.
```
$PY tools/edit/build_shots.py            # cut: "<typed s> @ <anchor>"  (anchors: bar N, beat T, word LINE WORD, event KIND T, section "X")
$PY tools/edit/check_cuts.py             # exit 1 if any cut is >1 frame off its anchor, gaps, overlaps
$PY tools/edit/animatic_picks.py         # still picks with a 4 % push-in for every keyframe (the animatic)
$PY tools/edit/assemble.py --name animatic_v0 --profile animatic    # 960x540, CRF 20, burn-in, no grain
$PY tools/edit/assemble.py --name preview_v1 --profile preview      # 960x540, CRF 18, grain 0.035
$PY tools/edit/assemble.py --name master_v1 --profile master --audio work/sound/mix.wav   # 1920x1080 CRF 14, AAC 320k
#   --range C1:D4 | --only C3,G4 | --letterbox-open N | --no-phase-grade | --grain-mode static
$PY tools/edit/contact.py --name preview_v1 [--range ..]     # first/mid/last of each shot + one frame every 0.5 s
$PY tools/edit/slowmo.py SRC OUT --in=.5 --out=2 --slow=3 | --ramp="0.2:1,0.55:1,0.7:3,1.0:3,1.15:1,2.0:1"  # RAFT on GPU
$PY tools/edit/merge_picks.py            # lays docs/picks_<group>.json fragments over picks.json
```
- What assemble guarantees: per-shot exact frame counts at 24 fps CFR; caching in `work/edit/<name>/shots/`; a stream-copy
  join that is verified (frame count, 1/24 s steps, A/V within one frame, bt709/tv tags, yuv420p); `.partial` files renamed
  only on success.
- Pick kinds: `still` (crop + `move` zoom/pan: **the multiplane / push-in tool for this film**), `video` (`in`, `rate`, `interp`),
  and `frames` (a PNG sequence, RGBA over black), plus `overlay` with blend over, screen or add.
- It never freezes or loops: a short pick becomes a red slate and the run exits with code 3.

**Typesetting.** `tools/edit/typeset.py` handles variable fonts, tracking, fitting to a safe width, and a shade halo and glow
after HF's `render/src/type.js`. `title_card.py` and `credits.py` produce the title and end card plus the honest-credits walk.
Fonts come from `design/fonts/`, which doesn't exist here yet. Subtitle tools are in section 9.

## 4. Rotoscope over generated video (HF take one; MG, RE, OS, RW2)

**What it does.** The generated footage is only *read*, never shown. HF/docs/take1/STYLE_BIBLE.md:8-9: "The Seedance and
image-model footage is only ever read, as guide maps: edges, tone, mattes, flow, landmarks. It never appears."

**HF take-one chain** (HF/README.md:268-298):
1. Keyframes: `tools/sd/keyframes.py SHOT --model=nbp|gpt`. Here `tools/sd` means Seedance, not Stable Diffusion.
2. Seedance 2.5 first-frame takes with the vocal-stem slice: `tools/sd/takes.py submit SHOT`.
3. Pick: `tools/sd/picks.py pick K4 2 --lag=0.0`.
4. Guides: `tools/roto/prep.py TAKE.mp4 CLIP KIND [--start --dur]` writes `work/guides/<CLIP>/`. It calls:
   - `tools/roto/engrave.py`: 1280×720 processing; structure-tensor isophote streamlines; XDoG edges `edge_NNNN.png`;
     bilateral tone; seeds advected by OpenCV DIS optical flow for temporal coherence; person matte from rembg `u2net_human_seg`.
   - `constellation.py`: flow-carried stipple points.
   - `face.py`: MediaPipe FaceMesh landmarks, run in a py3.12 mediapipe venv.
   - `preview_engrave.py`: a quick preview.
5. The JS renderer (Three.js + Canvas in headless Chromium/SwiftShader, `window.renderAt(t)`, HF/docs/RENDERER.md) redraws
   everything from the guides.

**Other projects' variants** (HF/docs/research/pipeline_lessons.md:141-152):
- RE: riso lines via `roto_extract.py` (XDoG σ .9, k 1.6, τ .985, ε −.012, φ 60).
- MG: ink and gold.
- OS: pencil.
- RW2: Escher engraving (`RW2/tools/engrave/matte.py`, BiRefNet + Real-ESRGAN).
- MM: re-draws plates as a WebGL lattice from rgb + Depth-Anything-V2-L + BiRefNet mattes (`MM/tools/prep/prep.py`).

**When it was needed and when not.**
- HF take two reversed it: "generated stills and video ARE shown (graded and composited), with JavaScript painted over them"
  (HF/docs/take2/CONVENTIONS.md:11).
- Roto survived only for targeted jobs:
  - green-screen walk composites (`tools/t2/comp_walk.py`);
  - a GrabCut hand moved along a designed path, because "No video model on the relay takes coordinates"
    (HF/docs/take2/LYRICS.md:100-112).
- Roto mouths read "puppet-like if overused"; Gemini flagged "repetitive, rotoscoped mouth movement" (pipeline_lessons.md:127;
  HF/docs/reviews/gemini_anim1_183.md:22).
- Jade (MG/docs/REVISION_NOTES_OCT7.md:47): "run a check that whatever the video model returns makes sense before
  rotoscoping it... cut into the scene when movement has already started."

**For Chaos Monkey.** The brief's "build the blank in code" is the cut-out-and-place cousin of this. Generate elements on
plain paper, matte them (local BiRefNet, or SAM 2.1 for video), and place them on a paper canvas. Full roto redraws are only
worth it if the ink look can't be got from the model directly.

## 5. A 3D scene as layout reference for the model (Three.js; no Blender in any project)

"No Blender or Remotion was used in any project" (RW2/docs/recon/pipeline.md:156). A local Blender 4.5.3 exists at
`/home/jade/Documents/1-software/blender_experimentation/.tools/blender-4.5.3-linux-x64/blender`, but it isn't on PATH and was
never used.

**MG Guanghan moonbase, the canonical case.**
- Layout model: `MG/render/scenes/guanghan3d/{layout.js,build.js,shots.js}`. layout.js is the single source of truth for
  numbers.
- Render: `cd render && node scenes/guanghan3d/render_guides.mjs --shots 5.2o` writes
  `media/guanghan/guides/<shot>_{line,depth,flat}.png`.
- Generate: `render/scenes/guanghan3d/gen_keyframes.py` calls `cf.generate("google/nano-banana-pro", {image_input:[guide, detail crop, style ref], image_size:"2K"})`.
- **How the render is passed:** as image_input #1, a *plain layout reference image*. There is no ControlNet and no depth
  conditioning; the depth and flat modes are passed as images too.
  - The `*_line.png` mode works best.
  - Prompt: "Image 1 is a plain 3D blockout render... Render this exact layout and camera: keep every structure's position,
    size, count and silhouette... Use image 1 ONLY for geometry: do not copy its plain plastic shading."
  - Image 2 must be a detail crop, "never the full K_7.A from the same camera: nano-banana-pro overlays the two and doubles the
    masts" (MG/docs/guanghan_layout.md:215-218).
- The keyframe then goes to h3 or Seedance 2.0 as the first frame.

**MG mannequin blockouts.**
- Location: `MG/render/scenes/blockouts/<shot>/` (mannequins at true heights: Jade 165 cm, child M 109 cm).
- Render: `node scenes/blockouts/7.E1/render_views.mjs --views ... --modes flat,line,label,guide`.
- Results (MG/docs/reviews/rev3_crew_report.md §4):
  - The winner was a "fresh painting from the blockout guide with a people-free style detail".
  - Rejected: "the image model kept returning the old arms whenever the old painting was among its inputs".
- The toy robot dog sheet was itself a Three.js render, because "image models add a head every time".
- Jade's request (REVISION_NOTES_OCT7.md:73): "build 3D models if you have to."

**RW2 car mirror** (RW2/docs/revisions/v9/fix_2_round3_threejs.md). A Three.js car interior with a grey mannequin; Nano Banana
Pro draws anime Jade over the layout render, laid on a card in the frustum. Jade's verdicts:
- round 5: "very good improvement, the staging is very good";
- round 7: "the placement feels unnaturally high".
- Cost $0.54–2.69 per round.

**RW2 Bean reflection** (RW2/docs/revisions/v10/f4_reflection.md). A ray-traced SDF used as ground truth for a composite,
not fed to a model: "VIDEO MODELS DON'T GET REFLECTIONS RIGHT" (S/shorts/DECISIONS.md:114). Jade's rule: "fix motion glitches
with a new video take or Three.js, never hand patches" (RW2/docs/recon/pipeline.md:99).

**For Chaos Monkey.** Block the 1988 attic and the 2026 bedroom and car in Three.js. Render line guides from each camera, and
pass guide + character sheet + style detail to Nano Banana Pro (≤ 3 refs), so the rooms stay consistent across shots.

## 6. Lip-sync: every method and its verdict

1. **Seedance 2.5 with `reference_audios`.** The main method in OS, MG, RW2, RE and HF.
   - Settings: chest-up centred first frame; vocal-stem window starting about 0.3 s before the first word; 480p or 720p; 5–6 s;
     `generate_audio:false`. Prompt: "She sings the words of the reference audio with precise lip sync."
     (MM/docs/prior_pipeline_brief.md §3).
   - The lag is random per take, −0.42 to +1.13 s (HF/docs/take2/LIPSYNC.md:139). "Seedance 2.5 does not sync to the file (it
     re-sings it)" (MG/docs/HANDOFF.md:257).
   - Results: OS approved; MG "pretty borked" (REVISION_NOTES_OCT7.md:49; Gemini scored it 2/10).
   - HF shipped it with lag picking. RE re-shot 3 shots with audio cut to start at frame 0 (15 takes, about $14;
     RE/docs/PROCESS.md:434).
   - Anime faces: `use_virtual_avatar:false` (HF GENERATION.md).
2. **Lag picking by Jade's ear.** HF's picker page `HF/tools/t2/lipsync/hold_fire_lipsync.html` offers 13 variants per shot,
   ±24 even frames. "Jade's ear beats every metric: she picked +0.90 against a measured +0.10" (pipeline_lessons.md:114).
   "When the strip can't decide between two lags, take the larger one" (LIPSYNC.md:23-28).
3. **Measurement tools.**
   - `HF/tools/sync/` (wordstrip, lipmeasure, mouthline, lag_curve).
   - `MM/tools/sync/{lipsync,wordstrip,pb_wordstrip,labial,lagreel}.py`.
   - `MG/tools/sync/viseme_check.py`.
   - Envelope correlation is "useless on legato"; word strips are more reliable.
4. **Mouth transplant inside the take** (RE, shipped).
   - Tools: `pipeline/sync/remouth.py` → `relip.py`. An exposure sheet, then a DP choice of a donor mouth from the same take,
     ECC registration and a Poisson clone, with LivePortrait ONNX as the fallback.
   - Result: 68 wrong drawings fixed down to 6 (RE/docs/PROCESS.md:315-401; RE/CLAUDE.md:158-173).
   - HF: remouth "can't rescue small, cool-lit faces… fix those by regenerating" (LIPSYNC.md:142).
5. **pruna/p-video-avatar** ($0.025/s). Tight sync (corr 0.998), but "a wide grin with full rows of teeth" and head tilts
   (MG/docs/reviews/rev2_ls_report.md:69-100); VS: "reframes … burns garbled captions". Not used.
6. **Procedural JS mouth** (MG `render/src/roto/mouth.js`, OS `tools/mouth_track.py`): "an isolated ellipse... without jaw"
   (MG/docs/reviews/glitch_sweep_v3.md:47). Retired.
7. **Rejected untried:** Wav2Lip, LatentSync and MuseTalk are trained on photographed faces and work at low resolution (96 px)
   (RE/PROCESS.md:338-346). Not installed.
8. **Never tried:** Hedra, OmniHuman, sync.so, veed/fabric. Kling was not in the catalog at MG time; it is now. Veo can't take
   audio.

**For Chaos Monkey.** Sung faces are cel-shaded, so this is Seedance 2.5 with a reference-audio window, followed by Jade's
lag picker. Given the brief, keep singing faces few. The two centred faces ("Yes", "You're able") are still shots by rule.

## 7. Character consistency and canonical sheets

**Anime Jade.** The canon is a 4-view sheet.
- Sheets:
  - `/home/jade/Documents/character sheets/character_sheet.png`, the same as `MM/inputs/character_sheet.png`, "newest 4-view
    anime Jade, hair down, full costume canon";
  - `RW2/media/design/jade_canon_turnaround.png`;
  - `HF/refs/dot_character_sheet.jpg` + `HF/design/take2/dot_ref_16x9.jpg`.
- Rules: curtain bangs, "never a hime cut" (HF GENERATION.md:8-20).
- Method: every keyframe = the 16:9 sheet crop + one set or style frame, through Nano Banana Pro (≤ 3 refs) or GPT Image 2.5.
  RE: GPT Image 2.5 is "best for the character sheet, which is canonical"; Nano Banana "ignored the instruction" on a hair
  edit (RE/PROCESS.md:29, 121-131).
- Video: Seedance first-frame "Animate the first frame exactly…", never naming a shot size.

**Rare Earth jacket canon** (MM/docs/prior_pipeline_brief.md §9; costume art in `RE/costume/{artwork,spec}`).
- Jacket: white cropped racer jacket, band collar, snap tab; one orange band per upper arm plus one across the chest.
- Front: pale-blue dot on her LEFT chest; round b/w 1420 MHz patch on the left sleeve.
- Back: big pale-blue dot with RARE EARTH.
- Rest of the outfit: black mock-neck crop top, navy cargo pants with orange straps, white sneakers. Pencils are yellow with
  pink and pale-blue erasers.
- **Lettering and patches are always repaired in code:** RE `pipeline/plate_fixes/fix_lettering.py` and `fix_backdot.py`;
  MM `tools/plates/fix_patch.py`; RW2 `tools/v9/{rare_earth,sleeve_band}.py`. "Never paste a rigid disc."
- HF mirror rule: generate in the canon jacket and flip in the renderer.

**Children and Mama.**
- MG daughter M: `MG/media/chars/M/SHEET.jpg` (side Dutch braid, pink elastics, **strawberry dress**, 109 cm), made by a gpt
  edit. Also T: `MG/media/chars/T/SHEET.jpg`; grandma: `MG/media/chars/grandma_V/SHEET.jpg`; cast board:
  `MG/media/chars/CAST_BOARD.jpg`.
- `MG/tools/char_gen.py` appends `media/chars/STYLE_BLOCK.txt` to every prompt.
- Rules: "Never trace the kids' real faces"; Jade's own photos may go to models, her kids' never (MM/HANDOFF.md:7;
  pipeline_lessons.md:249).
- Mama-likeness edit pattern (`MGP/media/keyframes/jade/PROMPTS_LS1_MOM.md`, `PROMPTS_D.md`): "Image 1 is the EXISTING
  FINISHED … KEYFRAME, EDIT TARGET. Image 2 and image 3 are appearance references ONLY."
- Already in this repo's `inputs/`: ref_merge_little_jade_{face,fullbody}.jpg, ref_moongazing_daughter_strawberry_dress_sheet.jpg,
  ref_moongazing_jade_singing_watercolor_first_frame.jpg, ref_moongazing_teahouse_jade_mom_daughter.png.

**Real-photo likeness.**
- OS: "Nano Banana tracing photo 3 with nothing changed" → `jade_trace_base.jpg`. Pasted faces were "demented"/"monsters"
  (OS/docs/HANDOFF_JADE.md:50-80).
- MM canon face v4: `tools/plates/canonprop.py`.

**`/home/jade/Documents/character sheets/`:**
- Root:
  - character_sheet.png, collar_detail.png, sleeve_patch_1420MHz.png, lyric-background.png;
  - jade_ref_image{,2}{,_music_video,_music_video_long_hair,_music_video_pencils}.png;
  - jade_trace_base.jpg, jade_trace_jacket_hp_2.jpg;
  - light_makeup_irl.png, nomakeup_selfie.png, selfie_hair{down,up}.jpg, selfie_hair{down,up}_jade_jacket_retouch_v2.png;
  - prompt files: jacket_glowup_prompt.md, jacket_retouch_v2_prompt.md, jacket_selfie_prompts.md, upperlip_retouch_prompt.md,
    yellow_pencils_prompt.md (codex image_gen identity-preserve edits).
- `selfies/`: 19 pasted images.
- `wip/`: jade_anime.png, jade_anime_jacket.png, jade_ref_image{,2}_jacket{,_mockneck,_mockneck_collar}.png, and jacket
  variants (glowup, yellow_pencils, clean_upperlip).

## 8. Codex via tmux

**Setup.** Codex is `/home/jade/.local/bin/codex` (codex-cli 0.166.0); tmux is `/usr/bin/tmux` 3.5a.
- `~/.codex/config.toml`: model `gpt-6.1-sol`, reasoning `medium`. chaosmonkey-video is **not yet a trusted project** there.
- No tmux server is running now.
- Jade's permission: HV/HANDOFF.md:99, "access to Codex thru tmux for boring/mechanical tasks and image gen"; codex is
  "basically free".

**Interactive pattern** (MG/docs/HANDOFF.md:295; ~/.claude/projects/-home-jade-Documents/memory/codex-tmux-submit-quirk.md):
```
tmux new-session -d -s chaos ; tmux split-window -h -t chaos     # codex in chaos:0.1; tell Jade: tmux attach -t chaos
tmux send-keys -t chaos:0.1 "cd /home/jade/Documents/chaosmonkey-video && codex" Enter
tmux load-buffer -b cx /abs/path/work/codex/job_X.md.prompt ; tmux paste-buffer -p -b cx -t chaos:0.1
sleep 1; tmux send-keys -t chaos:0.1 Enter        # a SEPARATE delayed Enter (sometimes twice): send-keys "text" Enter does NOT submit
tmux capture-pane -p -t chaos:0.1 | tail          # expect "Working (esc to interrupt)"
```

**Headless.**
- `flock /tmp/chaosmonkey-codex.lock codex exec -s workspace-write '<prompt>'`, adding
  `-c sandbox_workspace_write.network_access=true` if it needs the network (MG/docs/REVISION_NOTES_OCT8.md:92).
- No `--full-auto` and no `-m` are used anywhere; the model comes from config.toml.

**Image generation, free.** `codex exec -s workspace-write -i ref1.jpg -i ref2.jpg "…prompt… Use the built-in image_gen tool. Save the result to media/kf/<name>.png"`
(MG/docs/REVISION_NOTES_OCT7.md:88-90). Outputs also land in `~/.codex/generated_images/`. Pass the old keyframe as the
edit target, plus the sheets and the blockout view.

**File handoff.** Write `work/codex/job_<NAME>.md` with numbered commands, a check after each, "STOP and append <NAME>_FAILED
step N" on failure, and `<NAME>_DONE` appended to a log at the end. Paste only a pointer.
- Templates: `MGP/work/codex/{job_render_v10.md,job_hair.md,wait.sh,wait_prompt.sh,approve_script.sh}`. wait.sh hardcodes
  moongazing paths: adapt it.

**Tasks codex was given:** encodes, probes, contact sheets, luma and cut checks, audio master, beat/lyric analysis,
karaoke videos, comment scrubs, 9 repaints, 4 vignettes, hair-only edits and keyframe edits.

**Gotchas.**
- **Never launch codex with sandbox-bypass flags.** It trips the auto-mode classifier and blocks Claude's Bash
  (MG/docs/HANDOFF.md:396). Don't ask it to leave its sandbox either.
- The sandbox hides the GPU, and local servers fail with `listen EPERM`. Run renders and GPU jobs from Claude's shell.
- It stops for approval before network use, deletions and Chrome: read each command, then `send-keys Enter`.
- Run one codex job at a time. Three xhigh jobs drained the quota in 25 minutes.
- Never let it edit the same files as Claude concurrently: a comment scrub undid 4 edits. Don't run image_gen while another
  codex session works in the same repo.
- Always give absolute paths. `npx tsc` resolves to a joke package: use `npx --yes --package typescript tsc`.
- `pkill -f` / `pgrep -f` with a pattern that also appears in your own command line kills your own shell: use `[x]yz`.

## 9. Final render stack, deliverables, review loop

**Picture.**
- 1920×1080, 24 fps CFR (explicit `-r 24` / `fps=24` on every intermediate).
- H.264 High, yuv420p, **tagged BT.709 limited** (`scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p`
  + `-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv`). This avoids the colour-matrix trap; HF's
  JS-renderer master was untagged full-range BT.601.
- Master CRF 14, preset slow, `-tune grain`, AAC 320k, `+faststart`: the "Upload this to YouTube" file. OS went further:
  4K Lanczos, CRF 12, High@5.1, 45 Mb/s for upload (`OS/tools/encode_youtube.sh`, `tools/encode_uploads.py youtube|x`).

**Other encodes.**
- X: 2-pass `-b:v 12M -maxrate 16M -bufsize 24M -profile:v high -level:v 4.1 -tune grain`, AAC 256k.
- 31 s hook: 0.5 s fade.
- GitHub/preview copy: 1080p at 2.8 Mb/s under 100 MB, or 540p at 1.4 Mb/s (HARVEST §6).

**Renderer options.**
- HF: JS (Three.js r186 + Canvas in Chromium/SwiftShader, Playwright 1.63.0, `cd render && node tools/render.mjs --from A --to B --fps 24 --jobs 3 --crf 14`;
  restart-safe `tools/t2/render_segments.sh`).
- HV: Python/ffmpeg `tools/edit/assemble.py` (copied here).
- MM: `node engine/render.mjs ... --workers 3 --crf 17`.

**Audio.**
- The song is never normalised; the mix equals song + layer, bit-identical outside cues.
- Mix integrated loudness within 0.01–1 LU of the song (HF −15.67 vs −15.68 LUFS), layer peak ≤ −14 dBFS, true peak
  ≤ −0.5 dBTP, 24-bit/48 kHz WAV. Check `ebur128` on the final file (HF/docs/SOUND.md; HARVEST §6–7).

**Subtitles.**
- SRT, from `HF/tools/t2/subtitles.py`; validate with `check_subtitles.py`.
- A cue runs from the first word to 0.8 s after the last word, minimum 1 s; wrap at 42 characters (18 for Chinese).
- Collected sets: `S/youtube-subtitles/<film>/<film>.{en,zh-Hans,zh-Hant,ru,uk,fr,es,pt-BR,ar,hi,id}.srt`.

**RedNote zh-Hans cut.**
- Burned-in `.ass` from `HF/tools/t2/rednote_zh.py --track --render`, or `S/<film>/rednote/make_ass.py`.
- Style: PlayRes 1920×1080, Noto Sans CJK SC Medium (`HF/work/rednote/fonts/NotoSansCJKsc-Medium.otf`, via `--fontsdir`),
  size 70, outline 4, speaker colours.
- Encode: CRF 17, BT.709.
- Outputs collected in `S/rednote-subtitles/` (`*_rednote_zh-Hans_1080p.mp4`, `*_post_text.txt`, covers 3:4).
- ffmpeg 7.1.5 has libass.

**Vertical.** Shorts are 1080×1920 CRF 18 (`S/shorts/tools/build_short.py`). Never stretch non-uniformly.

**Thumbnails.** 1280×720 (`HF/tools/t2/thumbnails.py`).

**On-screen text (HF rules, adopted by the brief).**
- Sung words only. Big type for key words; everything else as a lower-third subtitle.
- About 3 words per second, never under 0.6 s for one word (checker: `HF/render/tools/check_cuts.mjs`).
- No punctuation, no exclamation marks; break the line where the punctuation was.
- Never over a face. Faces and big type stay inside the centred 4:5 area, x 528–1392.
- Nothing under 22 design px.
- No model-made lettering, ever (HF/docs/PLAN_TAKE_TWO.md:27-31; HF/docs/take2/LYRICS.md:9-31; CONVENTIONS.md:18).

**End card.** HF's layout, reproduced in `tools/edit/title_card.py` (HARVEST §8):
- title in Archivo 800, a gold rule, Open Sans credits;
- an honest model walk (`tools/edit/credits.py`);
- **held, no fade, to the last frame**.

**Review loop.**
- Order: animatic → 540p preview → Jade → full size.
- Contact sheets: every 0.5 s, plus first/mid/last frame of each shot; 1:1 crops of faces and type; per-take 10-frame
  sheets.
- QA pass (HF QA_RC1/RC2): `blackdetect`, `freezedetect`, `ebur128`, an A/V cross-correlation, and a ranked findings list
  with evidence frames. Example: `HV/docs/QA_PREVIEW_V4.md`, judged from frames with a stats.json of motion per shot.
- Outside model: `google/gemini-3.8-flash` on 35–60 s chunks at 480×270 (`HF/tools/review/gemini_review.py`). Only 18 of
  its 58 claims checked out.
- Review pages: HF's HLS review page with time-stamped notes in an artifact db (`HF/tools/t2/review/hold_fire_review.html`)
  and a takes picker (`tablet_takes.html`).
- Bake-offs are judged blind by a Fable or Opus agent (HV/HANDOFF.md:100).

## 10. Lessons learned / hard rules

1. Look before you report: render stills or clips of every change and look at them; subagent visual verdicts were wrong more
   than once. (HF/CLAUDE.md:41; MM prior_pipeline_brief lesson 14)
2. Take Jade's notes literally. (HV/HANDOFF.md:74; HMV REVISION_V2 §3)
3. Never commit or push unless asked; log every paid call; nothing over 95 MB in git; never commit tokens or ids.
   (HARVEST §1; HF/CLAUDE.md:43)
4. Keyframes or sheets before any expensive run; one decision per card; refer to moments by timestamp, not ID; a
   low-resolution preview before any full-size render. (HARVEST §1; HV/HANDOFF.md:104)
5. Every cut lands on a measured beat, word or hit, never a typed number; Suno drifts, so never cut to a constant BPM.
   (HV/HANDOFF_ROUND8.md:48; HF README)
6. Stage every shot as a locked still before the video model: "the video model is animating a decision and not making one".
   Choose models by bake-off. (HV/HANDOFF.md:54-58)
7. Never name a shot size in a first-frame prompt ("Close-up of…" recomposed all 6 takes). Start with "Animate the first
   frame exactly…". (HARVEST §3)
8. Models invent after about 4 s: ask for 5–6 s, cut at 4, never use the first 0.5 s. Use first + last frame (Kling v4) for
   longer holds. (BAKEOFF.md:356; ROUND4_TESTS §1)
9. Prompts state intent and consequence, not a list of moves or prohibitions; put guards in a short tail. (HV/HANDOFF.md:174;
   HANDOFF_ROUND8.md:87)
10. No freezes, loops or held frames: "frozen zoom call"; stillness reads as fake. Never stretch a take past its end.
    (HV/HANDOFF.md:249; HARVEST §1, §3)
11. No model lettering: text, seals and patches are set in code. "Models invent glyphs ('PACE EARTH')". (MM lesson 15;
    HF README:57)
12. Never generate the Sun, Earth or other computed facts; composite them. The same applies here to carved characters and
    seals. (HV/docs/KEYFRAME_BRIEF.md; MG guanghan_layout §7)
13. Left/right can't be fixed by prompt: mirror the image or edit per region. (HARVEST §4)
14. An image model returns the old picture whenever it is among the inputs: give a reference, not the target, or paint over
    the target and say "clean this up". (HARVEST §4; MG rev3_crew_report)
15. Reflections and mirrors fail in every video model: build them in Three.js. (S/shorts/DECISIONS.md:114)
16. Jade's catches: grins at the end of takes, alien or cross-eyed eyes, 3 hands or 3 legs, wrong hair length ("did the
    image model not receive the character sheet?"), pencils coloured wrong, gibberish 1420 patches, squished 9:16, "a
    language model freestyled it without movement". (MG REVISION_NOTES_OCT7.md:57-72; RW2 v9; MM §8)
17. Lip sync: give Jade variants, not a number; take the larger lag when unsure. (pipeline_lessons.md:114; LIPSYNC.md)
18. Never photograph or trace the kids' real faces; Jade's own selfies are OK. The daughter here is an original character.
    (MM/HANDOFF.md:7; brief Guardrails)
19. `generate_audio:false` always: song audio trips the copyright filter, and Veo's default doubles the price. (HARVEST §3)
20. Keep the credits on screen with no fade; video models on one or two lines; no ragged lists. (HF REVIEW_NOTES v6)
21. If someone pauses, it must be true: real cuneiform, legal chess. Here, the real novel text in the carvings.
    (HF REVIEW_NOTES:260-263)
22. Concurrency limits: ≤ 3–4 subagents and 1 codex job at a time ("thirteen subagents exhausted the session limit in an
    hour"); ≤ 3 image calls in parallel. (MG/docs/HANDOFF.md:337)
23. Checkpoint: each agent writes its state to its notes file after every batch. (HV/HANDOFF_ROUND8.md:33)
24. Do not edit `docs/picks.json` concurrently; producers write fragments and the lead merges. (HV/docs/PRODUCER_BRIEF.md:96)

## 11. Local resources

**GPU.** RTX 3090, 24 GB, driver 550.163, CUDA 12.4. Install torch from the cu124 index (`HV/tools/audio/README.md`).
System python3 is 3.13 with no numpy, torch, cv2 or PIL. `uv` is at `~/.local/bin/uv`.

**Venvs:**
- `HV/.venv` (3.12): torch 2.6, torchvision, torchaudio, transformers 5.23, demucs 4.1, audio_separator 0.48, beat_this 1.1,
  faster_whisper 1.2.1, librosa, pyloudnorm, opencv, av, jsonschema. **Use this one.**
- `S/moongazing/.venv` (3.12): adds openai-whisper, stable_whisper, pypinyin (useful for Mandarin), and an ffmpeg in its bin.
- `MM/.venv` (3.12): timm, kornia. BiRefNet mattes and Depth-Anything-V2 (`MM/tools/prep/prep.py:45,51`).
- `HF/.venv` (audio_separator, librosa); HF `work/venv/mp312` (mediapipe 0.10.21).

**Model weights:**
- `~/.cache/huggingface/hub`: HTDemucs-ft, Depth-Anything-V2-Large-hf, sam2.1-hiera-large, faster-whisper-large-v3,
  BiRefNet, AST audioset, ECAPA.
- `~/.cache/whisper/large-v3.pt`.
- `~/.cache/torch/hub/checkpoints`: beat_this final0, RAFT-large, wav2vec2.
- `~/.cache/engrave`: RealESRGAN x4plus, anime_6B, animevideov3 (.pth).
- `HV/work/models`: BS-RoFormer 317 ckpt, sherpa-onnx NeMo CTC. Already copied to this repo's `work/models/`, along with a
  karaoke Mel-RoFormer.

**How HV invokes them** (`$PY` = HV venv):
- stems: `tools/audio/stems.py` (BS-RoFormer via audio_separator, then `-m demucs -n htdemucs_ft -d cuda --shifts 4`);
- beats: `tools/audio/beat_this_run.py` (`File2Beats('final0', device='cuda')`);
- ASR: `tools/audio/asr_whisper.py` (`WhisperModel('large-v3', 'cuda', float16)`);
- alignment: `align.py`/`fuse.py` (torchaudio MMS_FA + NeMo CTC);
- mattes: `tools/comp/seg.py` (transformers `Sam2VideoModel` sam2.1-hiera-large, bf16);
- slow motion: `tools/edit/slowmo.py` (RAFT).

**Not installed:** ComfyUI or Stable Diffusion, RIFE (Jade's approval needed: HV/docs/ROUND4_TESTS.md §7), LatentSync,
Wav2Lip, MatAnyone, CoTracker, rembg, sox, ncnn binaries.

**Binaries:**
- ffmpeg 7.1.5: libass, freetype, harfbuzz, x264, x265, svtav1, nvenc, prores; no fdk-aac.
- node 22, Google Chrome 156, Playwright chromium-1243, ImageMagick.

**Fonts.** System CJK coverage is only Droid Sans Fallback, so **always use font files by path**.
- This repo's `refs/fonts/`:
  - seal: chongxi-seal 崇羲篆体.otf;
  - clerical: alimama-daoli 刀隶, aoyagi-reisho 青柳隶书, linhai-lishu 临海隶书;
  - regular and old-style: guangekai 館閣楷, qzqz 全字庫正楷體, keshilu 刻石录明/顏/鋼筆鶴, huiwen-mincho 匯文明朝, kinghwa-oldsong
    京華老宋, lxgw-wenkai 霞鹜文楷, noto-serif-sc, zcool-xiaowei;
  - Latin: eb-garamond, libre-caslon, im-fell;
  - liushu-wenmai/ls.zip is not unzipped.
- Elsewhere:
  - nine-fold seal 九叠篆: `S/moongazing/media/chars/seal/font/字悦九叠印篆.ttf`;
  - MaShanZheng, LiuJianMaoCao, ZhiMangXing, NotoSerifSC-VF: `S/moongazing/render/fonts/`;
  - NotoSansCJKsc-Medium (RedNote): `HF/work/rednote/fonts/`;
  - NotoSerifSC-Bold, NotoSansSC-Black, LXGWWenKai-Medium: `S/shorts/fonts/`;
  - end-card Latin (Archivo, Cormorant Italic, Open Sans, Plex Mono): `HV/design/fonts/`, with OFL texts in
    `HF/render/assets/fonts/`.

## 12. Recommendation and the state of the copied tools

**Copied as-is from HV, then lightly renamed (done 2026-11-16):** `tools/gen/*`, `tools/review/*`, `tools/edit/*`
(`__pycache__` removed), plus `docs/gen_catalog/` (required for pricing and the cap).

**Also worth copying later**, adapting each as noted:
- `HV/tools/audio/` (stems, beatgrid, asr_whisper, align, fuse, build_timing, events: everything needed for
  `analysis/timing.json`; a parallel session has already begun `tools/audio/stems.py` here);
- `HV/tools/grade/` (look/LUT build and SAM mattes: assemble reads `docs/grade.json` LUTs);
- `HV/tools/comp/seg.py` (SAM 2.1 video mattes for cut-out elements);
- `HV/design/fonts/` + OFL texts (title_card.py and typeset.py need them);
- `HF/tools/t2/{subtitles.py,check_subtitles.py,rednote_zh.py,thumbnails.py}`;
- `HF/tools/t2/lipsync/` (lag picker page);
- `HF/tools/review/gemini_review.py`;
- `MG/render/scenes/guanghan3d/gen_keyframes.py` (blockout-to-NBP pattern) and `MG/render/scenes/blockouts/*/mannequin.js`;
- `MM/tools/prep/prep.py` (BiRefNet + depth);
- `MGP/work/codex/` templates.

**Fixed in the copies** (trivially safe):
- `tools/gen/gen.py:58`: `PREFIX = "chaosmonkey/"`; docstring :15 updated.
- `tools/gen/spend.py:13,28-33`: cap env is now `CHAOSMONKEY_CAP` with a clearly marked `DEFAULT_CAP_USD = 200.0`
  **PLACEHOLDER**. The ledger and log paths are repo-relative, so they start empty here.
- `tools/gen/vgen.py:11,13`, `cf.py:2,29-30`, `catalog.py:15-17`, `gen.py:18`, `cfauth.py:1`: names and the venv path (now the
  HV venv; the old moongazing path doesn't exist).
- `tools/edit/common.py:16`: `SONG = inputs/'Chaos Monkey - reformatted for duet.wav'`.
- `tools/edit/assemble.py:924`, `:840` and `tools/edit/contact.py:77,94-95`: output names `chaosmonkey_<name>.mp4`.
- All files `py_compile` cleanly. Nothing was run against the network.

**Still Halys-specific; change when the project gets there** (file:line in the copies):
- `tools/gen/gen.py:56-57`: `RELAY = "rare-earth-v3-relay"`, the shared relay. Keep it; never modify the Worker.
- `tools/gen/gen.py:61-75`: `DEFAULTS` covers no Kling, HappyHorse or Veo. Add entries, or pass every key.
- `tools/gen/bakeoff.py:19-40`: Kling has no last_frame/middle_frames mapping; `resolution` is 1080p everywhere; Seedance 2.0
  is `use_virtual_avatar: True` (set False for anime faces); sd25 has no aspect guard (add `aspect_ratio: "16:9"`).
- `tools/gen/shots.py:1`: `SHOTS = {}`. Fill it with the vgen registry.
- `tools/edit/common.py:12-19`: `analysis/timing.json`, `docs/shots_src.yaml`, `design/fonts`, `FPS = 24`. These need the
  timing map and fonts from the audio step.
- `tools/edit/assemble.py`:
  - `:2` docstring "HALYS";
  - `:41-50` PROFILES (fine);
  - `:51` and `:99-110` the **2.39:1 letterbox logic**, driven by `letterbox_until` in shots_src (`build_shots.py:26,70,86`,
    `check_cuts.py:87-93`). Set `letterbox_until` to `start` to disable it, or remove it;
  - `:533` slate font Archivo;
  - grain and print-LUT defaults suit film, not paper: use `--grain` small or 0.
- `tools/edit/merge_picks.py:18-21`: the HV fragment order (picks_r4_*, r5, r6). Replace it with this project's groups.
- `tools/edit/title_card.py:28,34,188` and `typeset.py:13-26`: the Archivo/OpenSans/Cormorant faces, the holdfire palette
  and the "date card". Rewrite for a seal/brush title card with CJK fonts from `refs/fonts`.
- `tools/edit/credits.py:48-57`: the SUPPORT list cites tools/sky, DE441 and Skyfield (dropped automatically when the evidence
  file is missing, but tidy it). The walk assumes `media/kf/<ID>_<token>_v*.jpg` naming.
- `tools/review/bakeoff_intake.py:12,67-90,163`: `SHOTS = ["A1","C2","C7","C9","F1"]` and the C7 sun tracker. Generalise it.
- `tools/review/bakeoff_sheets.py:20,35` and `bakeoff_intake.py:186`: the model NAMES map and the glob `bk_<SHOT>_*_t1_*.mp4`
  (`t1` only).
- `tools/edit/README.md`: HALYS numbers (121.840 s, 2924 frames, the 40.98 s hit).

**Blockers before the first paid call:**
1. Copy or export the account id and KV namespace id (section 1).
2. Jade confirms the spend cap.
3. Add a `.gitignore` for `work/`, `media/` and `previews/`.
4. Optionally add chaosmonkey-video to `~/.codex/config.toml` trusted projects (Jade's call).

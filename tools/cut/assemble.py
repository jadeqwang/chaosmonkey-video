#!/home/jade/Documents/halys-video/.venv/bin/python
"""Render exact-frame shots and assemble them with song-clock audio."""
import argparse
import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from common import ROOT, FPS, FFMPEG, FONT, SONG, run, probe, tc, wrap, font, safe_name
import numpy as np
import lyrics as lyric_layer


def resolve_source(shot, picks):
    sid = shot['id']
    if sid in picks:
        pick = picks[sid]
        path = Path(pick['src'])
        path = path if path.is_absolute() else ROOT / path
        if not path.is_file():
            raise ValueError(f'{sid}: missing pick {path}')
        start, rate = float(pick.get('in', 0)), float(pick.get('rate', 1))
        if not math.isfinite(start) or not math.isfinite(rate) or start < 0 or rate <= 0:
            raise ValueError(f'{sid}: invalid pick in/rate')
        return 'pick', path, start, rate
    for kind, path in [('comp', ROOT/f'media/comp/{sid}.mp4'),
                       ('still', ROOT/f'media/kf/{sid}.jpg'), ('still', ROOT/f'media/kf/{sid}.png')]:
        if path.is_file():
            return kind, path, 0, 1
    return 'slate', None, 0, 1


def slate(shot, path, width, height):
    im = Image.new('RGB', (width, height), '#211f1c')
    d = ImageDraw.Draw(im)
    scale = width / 960
    d.text((int(40*scale), int(27*scale)), shot['id'], font=font(int(68*scale)), fill='#dccdb2')
    d.text((int(190*scale), int(48*scale)),
           f"{shot['world']}  ·  {tc(shot['in_frame'])}  ·  {shot['dur']:.3f}s / {shot['frames']}f",
           font=font(int(23*scale)), fill='#bdb09b')
    size = int(25*scale)
    while True:
        f = font(size)
        lines = wrap(shot['desc'], f, width-80*scale)
        if len(lines)*(size+5*scale) < height-225*scale or size <= 12*scale:
            break
        size -= 1
    for i, line in enumerate(lines):
        d.text((int(40*scale), int(134*scale+i*(size+5*scale))), line, font=f, fill='#e1d7c5')
    im.save(path)


def burn_in(shot, args, width, height, short, kind):
    """Prepare Pillow overlays once; all timestamps use the song frame clock."""
    scale = width / 960
    id_font = font(round(24 * scale))
    clock_font = font(round(22 * scale))
    lyric_font = font(round(25 * scale))
    short_font = font(round(30 * scale))

    def label(text, face):
        # Multiline bounds include line spacing and CJK ascenders/descenders.
        scratch = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        bounds = scratch.multiline_textbbox((0, 0), text, font=face, spacing=4)
        pad = round(5 * scale)
        layer = Image.new('RGBA', (bounds[2]-bounds[0]+2*pad,
                                   bounds[3]-bounds[1]+2*pad), (0, 0, 0, 166))
        ImageDraw.Draw(layer).multiline_text((pad-bounds[0], pad-bounds[1]), text,
                                            font=face, fill='white', spacing=4)
        return layer

    fixed = []
    if short:
        layer = label('SHORT', short_font)
        fixed.append((layer, (width-layer.width-20, 20)))
    if args.profile == 'animatic' or (args.profile == 'preview' and not args.clean):
        fixed.append((label(shot['id'], id_font), (20, 18)))
    lyrics = []
    if args.profile == 'animatic':
        for line in shot['lyrics']:
            layer = label('\n'.join(wrap(line['text'], lyric_font, width-100*scale)), lyric_font)
            lyrics.append((line['start'], line['end'], layer,
                           ((width-layer.width)//2, height-layer.height-round(62*scale))))

    def paint(im, index):
        for layer, pos in fixed:
            im.paste(layer, pos, layer)
        if args.profile == 'animatic':
            clock = label(tc(shot['in_frame'] + index), clock_font)
            im.paste(clock, (width-clock.width-20, height-clock.height-12), clock)
            timestamp = (shot['in_frame'] + index) / FPS
            for start, end, layer, pos in lyrics:
                if start <= timestamp < end:
                    im.paste(layer, pos, layer)
        if kind == 'slate':
            length = round(width * (index+1) / shot['frames'])
            ImageDraw.Draw(im).rectangle((0, height-8, length-1, height-5), fill='#b9674c')
        return im

    return paint


def encode_frames(decode_cmd, encode_cmd, paint, width, height, count):
    """Stream bounded-memory RGB frames through Pillow, checking both processes."""
    decoder = encoder = None
    with tempfile.TemporaryFile() as decode_log, tempfile.TemporaryFile() as encode_log:
        try:
            decoder = subprocess.Popen([str(a) for a in decode_cmd], stdout=subprocess.PIPE,
                                       stderr=decode_log)
            encoder = subprocess.Popen([str(a) for a in encode_cmd], stdin=subprocess.PIPE,
                                       stderr=encode_log)
            frame_size = width * height * 3
            for index in range(count):
                data = decoder.stdout.read(frame_size)
                if len(data) != frame_size:
                    raise RuntimeError(f'Decoder ended at frame {index}/{count} '
                                       f'({len(data)}/{frame_size} bytes)')
                im = Image.frombytes('RGB', (width, height), data)
                encoder.stdin.write(paint(im, index).tobytes())
            decoder.stdout.close()
            encoder.stdin.close()
            if decoder.wait() != 0:
                raise RuntimeError('Frame decoder failed')
            if encoder.wait() != 0:
                raise RuntimeError('Frame encoder failed')
        except BaseException as exc:
            for process in (decoder, encoder):
                if process is not None:
                    if process.poll() is None:
                        process.kill()
                    process.wait()
            details = []
            for name, log in [('decoder', decode_log), ('encoder', encode_log)]:
                log.seek(0)
                details.append(f'{name}: {log.read().decode(errors="replace")[-8000:]}')
            if isinstance(exc, Exception):
                raise RuntimeError(f'{exc}\n' + '\n'.join(details)) from exc
            raise
        finally:
            for pipe in (decoder.stdout if decoder else None, encoder.stdin if encoder else None):
                if pipe is not None and not pipe.closed:
                    try:
                        pipe.close()
                    except OSError:
                        pass  # Preserve the original pipe/process error and its logs.


def measure_frames(decode_cmd, width, height, count, fn):
    """Decode the shot once (same filters as the render) and call fn(rgb_u8, index) on each frame."""
    with tempfile.TemporaryFile() as log:
        decoder = subprocess.Popen([str(a) for a in decode_cmd], stdout=subprocess.PIPE, stderr=log)
        try:
            frame_size = width * height * 3
            for index in range(count):
                data = decoder.stdout.read(frame_size)
                if len(data) != frame_size:
                    raise RuntimeError(f'Decoder ended at frame {index}/{count}')
                fn(np.frombuffer(data, np.uint8).reshape(height, width, 3), index)
            decoder.stdout.close()
            if decoder.wait() != 0:
                raise RuntimeError('Frame decoder failed')
        except BaseException:
            if decoder.poll() is None:
                decoder.kill()
            decoder.wait()
            log.seek(0)
            raise


def render(shot, source, args, work, width, height, crf, short, layer=None, state_in=None):
    """Returns (path, lyric state out). With a lyric layer, the shot's lyrics are composited after the picture."""
    kind, path, start, rate = source
    plan = layer.plan(shot) if layer is not None else None
    params = {'shot': shot, 'source': str(path), 'mtime': path.stat().st_mtime_ns if path else None,
              'size': path.stat().st_size if path else None, 'start': start, 'rate': rate,
              'profile': args.profile, 'clean': args.clean, 'short': short,
              'font': FONT.stat().st_mtime_ns,
              'lyrics': (lyric_layer.code_hash(), layer.signature(plan, state_in)) if layer is not None else None,
              'code': hashlib.sha256(Path(__file__).read_bytes() + (ROOT/'tools/cut/common.py').read_bytes()).hexdigest()}
    key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:20]
    directory = work / f"{shot['id']}_{key}"
    directory.mkdir(exist_ok=True)
    output = directory / 'shot.mp4'
    look_file = directory / 'lyrics.json'
    if output.exists():
        look = json.loads(look_file.read_text()) if look_file.exists() else None
        return output, (look['ground'] if look else state_in)
    n = shot['frames']
    cmd = [FFMPEG, '-v', 'error', '-y', '-threads', '2']
    if kind == 'slate':
        path = directory/'slate.png'
        slate(shot, path, width, height)
    if kind in ('slate', 'still'):
        cmd += ['-loop', '1', '-framerate', '24', '-i', path]
    else:
        cmd += ['-i', path]
    scale = f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1'
    if kind == 'still':
        base = (f'scale={width*2}:{height*2}:force_original_aspect_ratio=increase,crop={width*2}:{height*2},'
                f"zoompan=z='1+0.04*on/{max(n-1,1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s={width}x{height}:fps=24,setsar=1")
    elif kind == 'slate':
        base = scale
    else:
        base = f'trim=start={start},setpts=(PTS-STARTPTS)/{rate},fps=24,{scale},tpad=stop_mode=clone:stop_duration={shot["dur"]}'
    filters = [base, f'trim=end_frame={n}', 'setpts=N/(24*TB)']
    temp = directory/'rendering.mp4'
    # FFmpeg handles source timing/geometry only; text never enters its filters.
    # passthrough: the raw pipe must carry exactly the filtered frames. With the default (cfr) the muxer re-timed
    # frames whose source PTS jitter (spliced files) and duplicated/dropped frames (the v1 splice "+2", QA fix 5).
    cmd += ['-filter_threads', '1', '-vf', ','.join(filters), '-an',
            '-frames:v', str(n), '-fps_mode', 'passthrough', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1']
    encode_cmd = [FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                  '-s:v', f'{width}x{height}', '-r', str(FPS), '-i', 'pipe:0',
                  '-an', '-frames:v', str(n),
                  '-vf', 'scale=out_color_matrix=bt709,format=yuv420p,setsar=1,'
                         'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                  '-c:v', 'libx264', '-preset', 'fast',
                  '-crf', str(crf), '-threads', '2', '-pix_fmt', 'yuv420p',
                  '-r', str(FPS), '-fps_mode', 'cfr', '-color_primaries', 'bt709',
                  '-color_trc', 'bt709', '-colorspace', 'bt709', temp]
    paint = burn_in(shot, args, width, height, short, kind)
    state_out, look = state_in, None
    if plan is not None:
        stats = []
        measure_frames(cmd, width, height, n, lambda rgb, i: stats.append(layer.measure(plan, rgb, i)))
        look = layer.decide(plan, stats, state_in)
        state_out = look['ground']
        lyr = layer.painter(plan, look)
        burn = paint
        paint = lambda im, i: burn(lyr(im, i), i)          # the lyric goes on the laid shot; burn-ins on top
    encode_frames(cmd, encode_cmd, paint, width, height, n)
    stream = next(s for s in probe(temp, True)['streams'] if s['codec_type'] == 'video')
    if int(stream['nb_read_frames']) != n:
        raise RuntimeError(f"{shot['id']}: render frame count mismatch")
    temp.replace(output)
    if look is not None:
        look_file.write_text(json.dumps({**look, 'state_in': state_in, 'place': plan['place'],
                                         'lines': [[l.text, u['id'], a, b] for l, s, a, b, u in plan['items']]}, ensure_ascii=False) + '\n')
    return output, state_out


TAIL_FADE = 8      # frames: the last shot's final frame (the dark room after the neon) sinks to true black, then holds


def render_tail(prev, n, work, width, height, crf):
    """n frames after the last shot: its last frame fades to black over TAIL_FADE frames, then black."""
    import av
    with av.open(str(prev)) as container:
        for fr in container.decode(video=0):
            last = fr
    base = np.asarray(last.to_image().convert('RGB'), np.float32)
    key = hashlib.sha256(json.dumps([str(prev), prev.stat().st_mtime_ns, n, width, height, crf, TAIL_FADE]).encode()).hexdigest()[:20]
    directory = work / f'END_{key}'
    directory.mkdir(exist_ok=True)
    output = directory / 'shot.mp4'
    if output.exists():
        return output
    temp = directory / 'rendering.mp4'
    enc = subprocess.Popen([FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s:v', f'{width}x{height}',
                            '-r', str(FPS), '-i', 'pipe:0', '-an', '-frames:v', str(n),
                            '-vf', 'scale=out_color_matrix=bt709,format=yuv420p,setsar=1,'
                                   'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                            '-c:v', 'libx264', '-preset', 'fast', '-crf', str(crf), '-threads', '2', '-pix_fmt', 'yuv420p',
                            '-r', str(FPS), '-fps_mode', 'cfr', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                            '-colorspace', 'bt709', str(temp)], stdin=subprocess.PIPE)
    for i in range(n):
        k = max(0.0, 1 - (i + 1) / TAIL_FADE)
        enc.stdin.write((base * k + 0.5).astype(np.uint8).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError('tail encoder failed')
    stream = next(s for s in probe(temp, True)['streams'] if s['codec_type'] == 'video')
    if int(stream['nb_read_frames']) != n:
        raise RuntimeError('END: tail frame count mismatch')
    temp.replace(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True, type=safe_name)
    parser.add_argument('--profile', choices=['animatic', 'preview', 'master'], required=True)
    parser.add_argument('--range')
    parser.add_argument('--only')
    parser.add_argument('--audio', type=Path, default=SONG)
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--tail', choices=['none', 'black'], default='none',
                        help="black: after the film's last shot, hold black to the end of the audio (ending B: the last "
                             "note rings over black). The tail is listed in the manifest as END; shot frame counts "
                             "in docs/shots.json are unchanged.")
    parser.add_argument('--lyrics', choices=['on', 'off'],
                        help='the film lyric layer (tools/cut/lyrics.py); default on for preview/master, off for animatic')
    args = parser.parse_args()
    if args.lyrics is None:
        args.lyrics = 'off' if args.profile == 'animatic' else 'on'
    data = json.loads((ROOT/'docs/shots.json').read_text())
    shots = all_shots = data['shots']
    ids = [s['id'] for s in shots]
    if args.range:
        first, last = args.range.split(':')
        a, b = ids.index(first), ids.index(last)
        if b < a:
            raise ValueError('Range is reversed')
        shots = shots[a:b+1]
    if args.only:
        wanted = set(args.only.split(','))
        if wanted-set(ids):
            raise ValueError(f'Unknown shot ids: {wanted-set(ids)}')
        shots = [s for s in shots if s['id'] in wanted]
    if not shots:
        raise ValueError('No selected shots')
    if not args.audio.is_file():
        raise ValueError(f'Missing audio: {args.audio}')
    audio_info = probe(args.audio)
    if float(audio_info['format']['duration']) + 1/FPS < max(s['out'] for s in shots):
        raise ValueError('Audio is too short for selected song-clock range')
    picks_path = ROOT/'docs/picks.json'
    picks = json.loads(picks_path.read_text()) if picks_path.exists() else {}
    sources = [resolve_source(s, picks) for s in shots]
    shorts = []
    for shot, (kind, path, start, rate) in zip(shots, sources):
        short = False
        if kind in ('pick', 'comp'):
            v = next(s for s in probe(path, True)['streams'] if s['codec_type'] == 'video')
            from fractions import Fraction
            duration = float(v.get('duration', float(v['nb_read_frames'])/float(Fraction(v['avg_frame_rate']))))
            if start >= duration:
                raise ValueError(f"{shot['id']}: source has no frames at requested in-point")
            short = (duration-start)/rate + 1e-6 < shot['dur']
            if kind == 'comp':
                short = short or int(v['nb_read_frames']) < shot['frames']
        shorts.append(short)
    if args.profile == 'master' and any(shorts):
        raise ValueError('Short sources in master: '+', '.join(s['id'] for s, short in zip(shots, shorts) if short))
    work = ROOT/'work/cut'/args.name
    work.mkdir(parents=True, exist_ok=True)
    width, height, crf = (1920,1080,14) if args.profile == 'master' else (960,540,20 if args.profile == 'animatic' else 18)
    renders = []
    manifest = []
    frame = 0
    layer = lyric_layer.LyricLayer(all_shots, width, height) if args.lyrics == 'on' else None
    state = None
    for shot, source, short in zip(shots, sources, shorts):
        out, state = render(shot, source, args, work, width, height, crf, short, layer, state)
        renders.append(out)
        manifest.append({**shot, 'cut_in_frame': frame, 'source_kind': source[0], 'short': short})
        frame += shot['frames']
        print(f"{shot['id']} {source[0]} {shot['frames']} frames" + (' SHORT' if short else ''), flush=True)
    if args.tail == 'black' and shots[-1]['id'] == all_shots[-1]['id']:
        last = shots[-1]
        total = round(float(audio_info['format']['duration']) * FPS)       # mix_v2: 241.920 s x 24 = 5806
        n_tail = total - last['out_frame']
        if n_tail > 0:
            out = render_tail(renders[-1], n_tail, work, width, height, crf)
            renders.append(out)
            manifest.append({'id': 'END', 'seq': last['seq'], 'in': last['out'], 'out': total / FPS,
                             'in_frame': last['out_frame'], 'out_frame': total, 'frames': n_tail, 'dur': n_tail / FPS,
                             'world': 'blank', 'desc': 'Black to the end of the audio.', 'lyrics': [],
                             'cut_in_frame': frame, 'source_kind': 'tail', 'short': False})
            shots = shots + [{'in_frame': last['out_frame'], 'out_frame': total}]   # audio span only
            frame += n_tail
            print(f'END tail {n_tail} frames (to {total} = {total/FPS:.3f} s)', flush=True)
    listing = work/'concat.txt'
    listing.write_text(''.join(f"file '{p}'\n" for p in renders))
    # Merge contiguous selections to keep audio continuous; disjoint --only shots
    # concatenate their corresponding song-clock intervals in shot-list order.
    spans = []
    for s in shots:
        if spans and spans[-1][1] == s['in_frame']:
            spans[-1][1] = s['out_frame']
        else:
            spans.append([s['in_frame'], s['out_frame']])
    audio_filters = []
    for i, (a,b) in enumerate(spans):
        audio_filters.append(f'[1:a]atrim=start={a/FPS}:end={b/FPS},asetpts=PTS-STARTPTS[a{i}]')
    audio_filters.append(''.join(f'[a{i}]' for i in range(len(spans)))+f'concat=n={len(spans)}:v=0:a=1,apad,atrim=duration={frame/FPS}[audio]')
    destination = ROOT/'media/cut'/f'{args.name}.mp4'
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = work/'assembled.mp4'
    run([FFMPEG, '-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',args.audio,
         '-filter_complex',';'.join(audio_filters),'-map','0:v:0','-map','[audio]', '-c:v','copy',
         '-c:a','aac','-b:a','320k','-movflags','+faststart',temp])
    info = probe(temp, True)
    video = next(s for s in info['streams'] if s['codec_type']=='video')
    audio = next(s for s in info['streams'] if s['codec_type']=='audio')
    if int(video['nb_read_frames']) != frame or abs(float(video['duration'])-float(audio['duration'])) > 1/FPS:
        raise RuntimeError('Final verification failed: frame count or A/V duration mismatch')
    if video['avg_frame_rate'] != '24/1' or video['pix_fmt'] != 'yuv420p' or any(video.get(k) != 'bt709' for k in ('color_space','color_transfer','color_primaries')):
        raise RuntimeError('Final verification failed: video format/tags')
    temp.replace(destination)
    (work/'manifest.json').write_text(json.dumps({'name':args.name, 'profile':args.profile,'fps':FPS,'frames':frame,
                                                'lyrics':args.lyrics,
                                                'shots':manifest},ensure_ascii=False,indent=2)+'\n')
    print(f'Verified {destination}: {frame} frames, video {video["duration"]}s, audio {audio["duration"]}s')


if __name__ == '__main__':
    main()

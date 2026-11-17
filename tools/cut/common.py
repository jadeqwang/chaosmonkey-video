"""Shared cut constants, checked subprocesses, typography and probing."""
from pathlib import Path
import json
import subprocess
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[2]
FPS = 24
FFMPEG = '/usr/bin/ffmpeg'
FFPROBE = '/usr/bin/ffprobe'
FONT = next((ROOT / 'refs/fonts/lxgw-wenkai').glob('*.ttf'))
SONG = ROOT / 'inputs/Chaos Monkey - reformatted for duet.wav'


def run(args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {args[0]}\n{result.stderr[-8000:]}")
    return result.stdout


def probe(path, count=False):
    args = [FFPROBE, '-v', 'error']
    if count:
        args += ['-count_frames']
    return json.loads(run(args + ['-show_streams', '-show_format', '-of', 'json', path]))


def tc(frame):
    sec, fr = divmod(frame, FPS)
    minute, sec = divmod(sec, 60)
    return f'{minute}:{sec:02d}.{fr:02d}'


def wrap(text, font, width):
    """Wrap on words when possible, with character-level fallback for CJK."""
    result = []
    for paragraph in text.split('\n'):
        line = ''
        for char in paragraph:
            if font.getlength(line + char) > width and line:
                split = line.rfind(' ')
                if split > len(line) // 2:
                    result.append(line[:split])
                    line = line[split + 1:] + char
                else:
                    result.append(line)
                    line = char
            else:
                line += char
        result.append(line.strip())
    return result


def font(size):
    return ImageFont.truetype(str(FONT), size)


def safe_name(value):
    import re
    if not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise ValueError('Name must contain only letters, numbers, underscores and hyphens')
    return value

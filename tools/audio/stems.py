"""Stems for the Chaos Monkey track -> work/stems/ (48 kHz, sample-aligned to inputs/ wav, same length).
Adapted from halys-video/tools/audio/stems.py. The supplied spliced stems (chaosmonkey-song/spliced/stems) belong to a
different render (44.1 kHz, 236.40 s, drifting 0..+2 s vs this file; see check_stems.py), so we separate again.

  vocals.wav        BS-RoFormer ep_317 (audio-separator, GPU)
  instrumental.wav  song - vocals (sample exact)
  drums/bass/other.wav, vocals_demucs.wav   htdemucs_ft
  lead.wav, backing.wav   mel_band_roformer_karaoke (aufr33/viperx) run on vocals.wav (lead vs backing/echo split)
Run: /home/jade/Documents/halys-video/.venv/bin/python tools/audio/stems.py
"""
import glob, os, shutil, subprocess, sys
import numpy as np, soundfile as sf, soxr
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W = os.path.join(ROOT, 'work'); ST = os.path.join(W, 'stems'); MODELS = os.path.join(W, 'models')
SRC = os.path.join(ROOT, 'inputs', 'Chaos Monkey - reformatted for duet.wav')
SONG = os.path.join(W, 'audio', 'song.wav')
RF_MODEL = 'model_bs_roformer_ep_317_sdr_12.9755.ckpt'
KAR = 'mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt'
SRCM = {RF_MODEL: '/home/jade/Documents/halys-video/work/models',
        KAR: '/home/jade/Documents/1-music-shipped/moongazing/render/out/lyric_video/models'}
BIN = os.path.dirname(sys.executable)
for d in (os.path.dirname(SONG), ST, MODELS): os.makedirs(d, exist_ok=True)
if not os.path.exists(SONG):
    y, sr = sf.read(SRC, dtype='float32'); assert sr == 48000
    sf.write(SONG, y, sr, subtype='FLOAT')
mix, sr = sf.read(SONG, dtype='float64'); n = len(mix)
for m, d in SRCM.items():
    for f in os.listdir(d):
        if f.startswith(m.replace('.ckpt', '')) or f == 'download_checks.json':
            if not os.path.exists(os.path.join(MODELS, f)):
                try: os.link(os.path.join(d, f), os.path.join(MODELS, f))
                except OSError: shutil.copy(os.path.join(d, f), MODELS)

def fit(x, sr_in):
    x = soxr.resample(x, sr_in, 48000, quality='VHQ') if sr_in != 48000 else x
    return np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n]

def sep(inp, model, out):
    if not glob.glob(os.path.join(out, '*.wav')):
        os.makedirs(out, exist_ok=True)
        subprocess.run([os.path.join(BIN, 'audio-separator'), inp, '-m', model, '--model_file_dir', MODELS, '--output_dir', out,
                        '--output_format', 'WAV', '--normalization', '1.0', '--mdxc_overlap', '8', '--use_soundfile',
                        '--log_level', 'info'], check=True)
    return sorted(glob.glob(os.path.join(out, '*.wav')))

voc = [f for f in sep(SONG, RF_MODEL, os.path.join(ST, 'roformer')) if '(Vocals)' in f][0]
v, vsr = sf.read(voc, dtype='float64'); v = fit(v, vsr)
sf.write(os.path.join(ST, 'vocals.wav'), v, 48000, subtype='FLOAT')
sf.write(os.path.join(ST, 'instrumental.wav'), mix - v, 48000, subtype='FLOAT')

kf = sep(os.path.join(ST, 'vocals.wav'), KAR, os.path.join(ST, 'karaoke'))
print(kf)
for f in kf:
    x, xsr = sf.read(f, dtype='float64'); x = fit(x, xsr)
    name = 'lead.wav' if '(Vocals)' in f or '(vocals)' in f.lower() and 'instrumental' not in f.lower() else 'backing.wav'
    sf.write(os.path.join(ST, name), x, 48000, subtype='FLOAT')

DM = os.path.join(ST, 'demucs'); dd = os.path.join(DM, 'htdemucs_ft', 'song')
if not os.path.exists(os.path.join(dd, 'drums.wav')):
    subprocess.run([sys.executable, '-m', 'demucs', '-n', 'htdemucs_ft', '-d', 'cuda', '--float32', '--shifts', '4',
                    '--overlap', '0.5', '-o', DM, SONG], check=True)
for s in ('drums', 'bass', 'other', 'vocals'):
    x, xsr = sf.read(os.path.join(dd, f'{s}.wav'), dtype='float64')
    sf.write(os.path.join(ST, f'{s}_demucs.wav' if s == 'vocals' else f'{s}.wav'), fit(x, xsr), 48000, subtype='FLOAT')
for f in sorted(os.listdir(ST)):
    if f.endswith('.wav'):
        x, _ = sf.read(os.path.join(ST, f)); print(f'{f:22s} n={len(x)} rms {20*np.log10(np.sqrt((x**2).mean())+1e-12):6.1f} dBFS')

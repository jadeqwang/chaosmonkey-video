"""ROOMS-88: measure every lip-sync take (tools/review/lipsync.py), keep the better score, and write the clip picks
media/comp/rooms88/clips.json that the shot scripts read (RoomShot -> clip_pick).

    $PY shots/_r88_pick.py            # measure what has arrived (cached in media/comp/rooms88/lipsync.json), write picks
Lip-sync: clip frame 0 is placed at song time  T(window start) - lag_vs_synced  (lipsync.py's suggested retime).
Kling: frame 0 at the shot's in-point unless KLING below says otherwise (t_clip0 / rate / src_range).
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from shots._r88_gen import LIP  # noqa: E402

PY = sys.executable
OUT = 'media/comp/rooms88'
CACHE = f'{OUT}/lipsync.json'
SH = {s['id']: s for s in json.load(open('docs/shots.json'))['shots']}
BOX = {'C3': '415,215,60,45'}             # shot -> "x,y,w,h" mouth box in clip px when FaceMesh fails (wide shots)
MAXLAG = {'G5': 0.6}   # G5: one word after 2.8 s of silence; at 1.2 s the correlation locks onto noise (+1018 ms, checked by eye: wrong)
FORCE = {'E1': 't1', 'G1': 't1', 'G3': 't2'}           # shot -> take tag to use regardless of score (with a reason in the log)

# Kling picks: shot -> dict(t_clip0=song time of clip frame 0, rate, src_range=(a, b) in clip seconds, twos)
KLING = {
    'A3': dict(t_clip0=SH['A3']['in'] - 0.06, rate=1.0),
    'A4': dict(t_clip0=SH['A4']['in'] - 0.04, rate=1.0),
    'C5a': dict(t_clip0=SH['C5']['in'] - 0.3, rate=1.0),
    'D9': dict(t_clip0=SH['D9']['in'] - 0.3, rate=1.0),
    'E5': dict(t_clip0=SH['E5']['in'] - 0.4, rate=1.0),
    'E6': dict(t_clip0=SH['E6']['in'] - 0.25, rate=1.0),
    'F3b': dict(t_clip0=112.25 - 0.55, rate=1.0),   # the hairs fly from clip 0.55 s
    # 'G4': dict(t_clip0=SH['G4']['in'], rate=0.5, src_range=(0.0, 2.6))   # later the hands double: first 2.6 s, half speed,
}


def measure(path, t0, box=None, maxlag=None):
    args = [PY, 'tools/review/lipsync.py', path, '--audio', 'work/stems/vocals.wav', '--t0', str(t0), '--json']
    if box:
        args += ['--box', box]
    if maxlag:
        args += ['--maxlag', str(maxlag)]
    r = subprocess.run(args, capture_output=True, text=True)
    lines = [l for l in r.stdout.strip().splitlines() if l.startswith('{')]
    return json.loads(lines[-1]) if lines else {'error': (r.stderr or r.stdout)[-400:]}


def main():
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    picks = json.load(open(f'{OUT}/clips.json')) if os.path.exists(f'{OUT}/clips.json') else {}
    for shot, (t0, dur, who, words, extra, takes) in LIP.items():
        best = None
        for path in sorted(glob.glob(f'media/gen/r88_{shot}_sd25_t*.mp4')):
            key = f'{path}|{BOX.get(shot)}|{MAXLAG.get(shot)}'
            if key not in cache:
                cache[key] = measure(path, t0, BOX.get(shot), MAXLAG.get(shot))
                json.dump(cache, open(CACHE, 'w'), indent=1)
            m = cache[key]
            if 'r_best' not in m:
                print(shot, path, 'ERROR', m.get('error', '')[:200])
                continue
            tag = os.path.basename(path).split('_sd25_')[1][:2]
            print(f"{shot:4s} {tag} r={m['r_best']:.2f} sharp={m['sharp']:.2f} lag_vs_synced={m['lag_vs_synced_ms']:+5d} ms "
                  f"face={m.get('face_found_pct')}% drift={m.get('head_drift_px')} roll={m.get('roll_range_deg')} {m['verdict']}")
            if FORCE.get(shot) == tag or (shot not in FORCE and (best is None or m['r_best'] > best[1]['r_best'])):
                best = (path, m)
        if best:
            path, m = best
            picks[shot] = dict(path=path, t_clip0=round(t0 - m['lag_vs_synced_ms'] / 1000.0, 4), rate=1.0, twos=False,
                               kind='lip', r=m['r_best'], sharp=m['sharp'], lag_vs_synced_ms=m['lag_vs_synced_ms'],
                               weak=m['r_best'] < 0.3)
    picks.pop('C2', None)       # Kling painted its own flat hand shadow and lost the fingers: C2 = keyframe + comp
    for shot, kw in KLING.items():
        g = sorted(glob.glob(f'media/gen/r88_{shot}_kling4_t*.mp4'))
        if g:
            picks[shot] = dict(path=g[-1], kind='kling', twos=True, **kw)
    json.dump(picks, open(f'{OUT}/clips.json', 'w'), indent=1)
    print('picks:', ', '.join(sorted(picks)))


if __name__ == '__main__':
    main()

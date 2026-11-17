"""Local sequential MMS re-alignment of a window (main lines + echoes in sung order) on a stem.
    python tools/audio/local_align.py STEM a b "tok tok ..."   (tokens romanized; prints word times + scores)
Used for drop 2 (echoes follow each phrase; continuous vocal) and the rap (dense Mandarin)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align
y = align.load16(sys.argv[1]); a, b = float(sys.argv[2]), float(sys.argv[3]); toks = sys.argv[4].split()
E = align.emissions(y[int(a * 16000):int(b * 16000)], win=min(30, b - a), hop=min(20, b - a))
for t, w in zip(toks, align.fa(E, toks, t0=a)): print(f"{t:10s} {w['start']:8.2f} {w['end']:8.2f} {w['score']:.2f}")

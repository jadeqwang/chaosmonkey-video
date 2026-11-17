"""Diagnostic: greedy CTC decode of MMS_FA emissions on a stem (what characters it hears, with times).
    python tools/audio/greedy.py work/stems/vocals.wav a b   -> prints char runs"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align
y = align.load16(sys.argv[1]); a, b = float(sys.argv[2]), float(sys.argv[3])
E = align.emissions(y[int(a*16000):int(b*16000)], win=min(30, b-a), hop=min(20, b-a))
inv = {v: k for k, v in align.DIC.items()}
am = E.argmax(1); out = []; prev = 0
for i, k in enumerate(am):
    if k != prev and k != 0: out.append(f"{a+i*0.02:.2f}{inv.get(int(k),'?')}")
    prev = k
print(' '.join(out))

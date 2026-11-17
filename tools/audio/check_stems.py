"""Cross-correlate the supplied spliced stems (sum) against the input wav, globally and in 10 s windows."""
import numpy as np, soundfile as sf, soxr, json, sys
IN="/home/jade/Documents/chaosmonkey-video/inputs/Chaos Monkey - reformatted for duet.wav"
SD="/home/jade/Documents/chaosmonkey-song/spliced/stems/"
SR=8000
x,sr=sf.read(IN); xm=soxr.resample(x.mean(1),sr,SR)
st=[sf.read(SD+f)[0] for f in ("mom vocal.wav","child vocal.wav","instrumental.wav")]
s=sum(a.mean(1) for a in st); s=soxr.resample(s,44100,SR)
print("input dur",len(x)/sr,"stems dur",len(st[0])/44100)
def env(y,h=80):  # 10ms envelope
    n=len(y)//h; return np.sqrt((y[:n*h].reshape(n,h)**2).mean(1))
def xc(a,b,maxlag):
    a=(a-a.mean())/(a.std()+1e-9); b=(b-b.mean())/(b.std()+1e-9)
    best=(-9,0)
    for L in range(-maxlag,maxlag+1):
        if L>=0: aa,bb=a[L:],b[:len(a)-L]
        else: aa,bb=a[:L],b[-L:]
        n=min(len(aa),len(bb)); c=np.dot(aa[:n],bb[:n])/n
        if c>best[0]: best=(c,L)
    return best
ex,es=env(xm),env(s)
print("global env xcorr (corr, lag s; +lag = input later):",[(round(c,3),L*0.01) for c,L in [xc(ex,es,800)]])
res=[]
for t0 in range(0,230,10):
    a=ex[t0*100:(t0+10)*100]; 
    c,L=xc(a, es[max(0,t0*100-1000):(t0+20)*100] if False else es, 0) if False else (None,None)
    # local search: find best lag of input window within stems +-10 s
    best=(-9,0)
    for L in range(-1000,1001,1):
        j=t0*100+L
        if j<0 or j+1000>len(es): continue
        b=es[j:j+1000]; aa=(a-a.mean())/(a.std()+1e-9); bb=(b-b.mean())/(b.std()+1e-9)
        cc=np.dot(aa,bb)/len(aa)
        if cc>best[0]: best=(cc,L)
    res.append((t0,round(best[0],3),best[1]*0.01))
    print(f"input {t0:3d}-{t0+10:3d}s  best corr {best[0]:.3f} at stems time = input + {best[1]*0.01:+.2f}s")

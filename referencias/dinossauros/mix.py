import numpy as np, wave
SR=48000
frames=[300,305,410,360,656,272,480]
starts=np.cumsum([0]+frames[:-1])/30.0
T=sum(frames)/30.0
n=int(T*SR); out=np.zeros(n)
def rd(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768; return a
for i in range(7):
    a=rd(f"aud/n{i}.wav"); a=a/np.abs(a).max()*0.85
    s=int((starts[i]+0.3)*SR); out[s:s+len(a)]+=a[:n-s]
t=np.arange(n)/SR
rng=np.random.default_rng(1)
def lp(x,a):  # one-pole lowpass
    from scipy.signal import lfilter
    return lfilter([1-a],[1,-a],x)
# ambient pad, mood darkens after impact
pad=np.zeros(n)
for f,amp in ((55,1),(82.4,0.6),(110,0.5),(130.8,0.35),(164.8,0.25)):
    pad+=amp*np.sin(2*np.pi*f*t+rng.random()*6)*(0.7+0.3*np.sin(2*np.pi*t/(7+f%5)))
pad*=0.035
env=np.clip(t/2,0,1)*np.clip((T-1.0-t)/2.5,0,1)
out+=pad*env
# impact boom
ti=starts[3]+23/30
s=int(ti*SR); L=int(4*SR); tt=np.arange(L)/SR
noise=lp(rng.standard_normal(L),0.985)
boom=(noise*6+np.sin(2*np.pi*(55*np.exp(-tt*0.8))*tt))*np.exp(-tt*1.4)
boom=boom/np.abs(boom).max()*0.7
out[s:s+L]+=boom
# asteroid whoosh in scene 0 & rumble during fire rain
for t0,dur,g in ((starts[0]+0.5,9,0.10),(starts[3]+0.0,0.8,0.25),(starts[4]+2.5,7,0.12)):
    s=int(t0*SR);L=int(dur*SR);tt=np.arange(L)/SR
    r=lp(rng.standard_normal(L),0.97); r=r/np.abs(r).max()
    e=np.sin(np.pi*tt/dur)**1.5
    out[s:s+L]+=r*e*g
# fade last
out*=np.clip((T-0.3-t)/1.0,0,1)
out=out/max(1,np.abs(out).max()/0.95)
w=wave.open("aud/mix.wav","wb");w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
print(T)

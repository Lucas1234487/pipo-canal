"""Gerador procedural de efeitos e trilha do ShoShortz (numpy puro, 100% original, sem direitos de terceiros).
Uso: python3 sfx_procedural.py <pasta_saida> [seed]"""
import numpy as np, sys, os, wave
SR=48000
def save(path,x):
    x=np.clip(x,-1,1); x=(x*32767).astype(np.int16)
    if x.ndim==1: x=np.stack([x,x],1)
    with wave.open(path,"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())
def t(d): return np.arange(int(SR*d))/SR
def env(n,a=0.005,r=0.1):
    e=np.ones(n); na=max(1,int(a*SR)); e[:na]=np.linspace(0,1,na)
    e*=np.exp(-np.arange(n)/(r*SR)); return e
def lp(x,alpha):  # passa-baixa de 1 polo (alpha pode ser vetor)
    y=np.zeros_like(x); s=0.0; a=np.broadcast_to(alpha,x.shape)
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def norm(x,peak=0.9): return x/ (np.max(np.abs(x))+1e-9)*peak
rng=np.random.default_rng(int(sys.argv[2]) if len(sys.argv)>2 else 7)

def pop():      # bolha/"plop" de massinha: seno com queda rápida de frequência
    tt=t(0.12); f=900*np.exp(-tt*35)+180
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(tt),0.001,0.03))
def whoosh(d=0.45): # ruído filtrado com varredura (transição)
    n=int(SR*d); x=rng.standard_normal(n); s=np.sin(np.linspace(0,np.pi,n))
    y=lp(x,0.02+0.25*s**2)*s**1.5
    st=np.stack([y*np.linspace(1,0.3,n),y*np.linspace(0.3,1,n)],1)  # pan esquerda->direita
    return norm(st,0.8)
def ding(f0=1318.5): # sino/"curiosidade": parciais inarmônicos
    tt=t(1.2); y=sum(a*np.sin(2*np.pi*f0*m*tt)*np.exp(-tt*k) for m,a,k in [(1,1,3),(2.76,.5,5),(5.4,.25,8),(8.93,.12,12)])
    return norm(y*env(len(tt),0.002,10))
def boing():    # mola cômica: vibrato rápido decaindo
    tt=t(0.6); f=220+120*np.sin(2*np.pi*14*tt)*np.exp(-tt*4)
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*env(len(tt),0.002,0.25))
def riser(d=1.5): # subida de tensão antes da revelação
    tt=t(d); f=200*2**(tt/d*3); y=np.sin(2*np.pi*np.cumsum(f)/SR)*0.4+lp(rng.standard_normal(len(tt)),0.05+0.4*tt/d)*0.6
    return norm(y*(tt/d)**2)
def thump():    # impacto grave (revelação/corte)
    tt=t(0.4); f=110*np.exp(-tt*12)+42
    return norm(np.tanh(3*np.sin(2*np.pi*np.cumsum(f)/SR))*env(len(tt),0.001,0.12))
def click():    # tique de UI / texto aparecendo
    tt=t(0.03); return norm(lp(rng.standard_normal(len(tt)),0.5)*env(len(tt),0.0005,0.004)+0.5*np.sin(2*np.pi*2500*tt)*env(len(tt),0.0005,0.006))
def squish():   # amassar massinha
    n=int(SR*0.25); x=rng.standard_normal(n); y=lp(x,np.linspace(0.3,0.02,n))*np.sin(np.linspace(0,np.pi,n))
    return norm(y)
def vinheta():  # assinatura sonora do canal (~1,2 s): pop + arpejo marimba + ding. Sem voz: igual em PT e EN
    out=np.zeros(int(SR*1.3))
    p=pop(); out[:len(p)]+=p*0.7
    for i,f in enumerate([523.25,659.25,783.99]):
        tt=t(0.35); m=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*4*f*tt)*np.exp(-tt*30))*env(len(tt),0.002,0.12)
        s=int(SR*(0.10+i*0.09)); out[s:s+len(tt)]+=m*0.6
    d=ding(1046.5); s=int(SR*0.38); out[s:]+= d[:len(out)-s]*0.5
    return norm(out)

def trilha(bpm=96,compassos=16,tom=0,clima="leve"):
    """Loop instrumental simples: acordes (pad), baixo, bumbo/caixa/chimbal e melodia pentatônica aleatória.
    clima='leve' (maior, alegre) ou 'serio' (menor, tenso)."""
    beat=60/bpm; bar=4*beat; n=int(SR*bar*compassos); out=np.zeros(n)
    base=261.63*2**(tom/12)
    prog=[[0,4,7],[9,12,16],[5,9,12],[7,11,14]] if clima=="leve" else [[0,3,7],[8,12,15],[3,7,10],[10,14,17]]
    escala=[0,2,4,7,9] if clima=="leve" else [0,3,5,7,10]
    for b in range(compassos):
        ch=prog[b%4]; s=int(SR*b*bar); tt=t(bar)
        pad=sum(np.sin(2*np.pi*base*2**(k/12)*tt)+0.3*np.sin(2*np.pi*2*base*2**(k/12)*tt) for k in ch)
        out[s:s+len(tt)]+=pad*0.05*np.minimum(1,tt/0.3)*np.minimum(1,(bar-tt)/0.3)
        fb=base/2*2**(ch[0]/12)
        for q in range(4):  # baixo em semínimas
            s2=s+int(SR*q*beat); tb=t(beat*0.9); out[s2:s2+len(tb)]+=np.tanh(2*np.sin(2*np.pi*fb*tb))*env(len(tb),0.005,0.25)*0.12
        for q in range(8):  # bateria em colcheias
            s2=s+int(SR*q*beat/2)
            if q in (0,4) or (q==6 and b%2): k=thump()[:int(SR*0.3)]*0.35; out[s2:s2+len(k)]+=k[:n-s2]
            if q in (2,6): sn=lp(rng.standard_normal(int(SR*0.15)),0.6)*env(int(SR*0.15),0.001,0.04)*0.12; out[s2:s2+len(sn)]+=sn[:n-s2]
            hh=np.diff(rng.standard_normal(int(SR*0.04)+1))*env(int(SR*0.04),0.0005,0.01)*0.05; out[s2:s2+len(hh)]+=hh[:n-s2]
            if rng.random()<0.45:  # melodia
                f=base*2*2**(escala[rng.integers(5)]/12); tm=t(beat/2*0.95)
                out[s2:s2+len(tm)]+=(np.sin(2*np.pi*f*tm)+0.2*np.sin(2*np.pi*3*f*tm))*env(len(tm),0.003,0.08)*0.07
    return norm(np.tanh(out*1.5),0.8)

if __name__=="__main__":
    o=sys.argv[1] if len(sys.argv)>1 else "."; os.makedirs(o,exist_ok=True)
    for nome,f in [("pop",pop),("whoosh",whoosh),("ding",ding),("boing",boing),("riser",riser),("thump",thump),("click",click),("squish",squish),("vinheta",vinheta)]:
        save(f"{o}/{nome}.wav",f())
    save(f"{o}/trilha_leve_96bpm.wav",trilha(96,8,0,"leve"))
    save(f"{o}/trilha_seria_84bpm.wav",trilha(84,8,-3,"serio"))
    print("ok")

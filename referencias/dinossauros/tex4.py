import numpy as np
from global_land_mask import globe
from PIL import Image, ImageFilter
W,H=4096,2048
lon=np.linspace(-180,180,W,endpoint=False)+180/W
lat=np.linspace(90,-90,H,endpoint=False)-90/H   # row0 = north (PIL top)
LO,LA=np.meshgrid(lon,lat)
land=globe.is_land(np.clip(LA,-89.9,89.9),np.clip(LO,-179.99,179.99)).astype(np.float32)
rng=np.random.default_rng(3)
def noise(sc,oct=5):
  out=np.zeros((H,W),np.float32);a=1
  for o in range(oct):
    n=rng.random((max(2,int(H/sc)),max(2,int(W/sc)))).astype(np.float32)
    n=np.array(Image.fromarray((n*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255
    out+=n*a;a*=0.5;sc/=2
  return out/1.9
n=noise(128)
landS=np.array(Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)),np.float32)/255
al=np.abs(LA)
green=np.array([0.20,0.42,0.16]);dry=np.array([0.62,0.52,0.30]);dark=np.array([0.10,0.30,0.12])
desert=np.clip((1-np.abs(al-24)/14)*1.2*(n+0.3),0,1)[...,None]
lc=green*(1-desert)+dry*desert
lc=lc*(0.75+0.5*n[...,None])
tw=np.clip((16-al)/8,0,1)[...,None]
lc=dark*(0.8+0.4*n[...,None])*tw+lc*(1-tw)
deep=np.array([0.02,0.10,0.30]);shallow=np.array([0.05,0.35,0.55])
coast=np.array(Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20)),np.float32)/255
oc=deep*(1-coast[...,None]*1.6)+shallow*np.clip(coast[...,None]*1.6,0,1)
col=lc*landS[...,None]+oc*(1-landS[...,None])
ice=np.maximum(np.clip((LA-72)/5,0,1),np.clip((-LA-60)/4,0,1))[...,None]
col=col*(1-ice)+np.array([0.92,0.95,1.0])*ice
Image.fromarray((np.clip(col,0,1)**(1/2.2)*255).astype(np.uint8)).save("tex4k/earth.png")
Image.fromarray((landS*255).astype(np.uint8)).save("tex4k/land.png")
c=noise(80,6); c=np.clip((c-0.52)*3.5,0,1)
Image.fromarray((c*255).astype(np.uint8)).save("tex4k/clouds.png")
print("ok")

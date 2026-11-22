import sys,glob
from PIL import Image
fs=sorted(glob.glob(f"/home/claude/v/prev/{sys.argv[1]}_*.png"))
ims=[Image.open(f) for f in fs]
w=Image.new('RGB',(540*len(ims),960));[w.paste(im,(i*540,0)) for i,im in enumerate(ims)]
w.save(f'/tmp/{sys.argv[1]}.jpg')

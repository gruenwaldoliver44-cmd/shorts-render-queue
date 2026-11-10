import glob,sys
from PIL import Image,ImageDraw
fs=sorted(glob.glob('work/st/*.jpg'));c=int(sys.argv[1]) if len(sys.argv)>1 else 6
per=int(sys.argv[2]) if len(sys.argv)>2 else 42
for k in range(0,len(fs),per):
    g=fs[k:k+per];im0=Image.open(g[0]);W,H=320,180
    sh=Image.new('RGB',(c*W,((len(g)+c-1)//c)*H))
    d=ImageDraw.Draw(sh)
    for i,f in enumerate(g):
        im=Image.open(f).resize((W,H));sh.paste(im,((i%c)*W,(i//c)*H));d.text(((i%c)*W+3,(i//c)*H+3),f[8:-4],fill=(255,255,0))
    sh.save(f'/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/s{k//per}.jpg',quality=80)
print(len(fs)//per+1)

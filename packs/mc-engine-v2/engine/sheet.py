import sys,glob,os
from PIL import Image,ImageDraw
fs=sorted(glob.glob('work/st/*.jpg'));cols=int(sys.argv[1]) if len(sys.argv)>1 else 4
ims=[Image.open(f) for f in fs];w,h=ims[0].size
per=int(sys.argv[2]) if len(sys.argv)>2 else 16
os.makedirs('work/sheets',exist_ok=True)
for k in range(0,len(ims),per):
    part=ims[k:k+per];rows=(len(part)+cols-1)//cols
    c=Image.new('RGB',(cols*w,rows*(h+18)),'#222');d=ImageDraw.Draw(c)
    for i,(im,f) in enumerate(zip(part,fs[k:k+per])):
        x,y=(i%cols)*w,(i//cols)*(h+18);c.paste(im,(x,y));fr=int(os.path.basename(f)[:5]);d.text((x+4,y+h+2),f'{fr} = {fr/30:.1f}s',fill='white')
    c.save(f'work/sheets/s{k//per:02d}.jpg',quality=80)
print(len(ims))

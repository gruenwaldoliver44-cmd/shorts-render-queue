import sys
from PIL import Image,ImageDraw,ImageFont
names=sys.argv[2:];out=sys.argv[1]
T=300;c=6
sh=Image.new('RGB',(c*T,((len(names)+c-1)//c)*(T+20)),(90,120,140));d=ImageDraw.Draw(sh)
for i,n in enumerate(names):
    im=Image.open(f'public/{n}.png').convert('RGBA');W,H=im.size
    # Kopfbereich: obere 36 % (Sitzfiguren 60 %)
    hb=.62 if n[:2] in('kb','kg') else .36
    x0=0;bb=im.crop((0,0,W,int(H*hb)))
    k=T/max(W,H*hb);r=bb.resize((int(W*k),int(H*hb*k)))
    X=(i%c)*T;Y=(i//c)*(T+20)+20;sh.paste(r,(X,Y),r)
    d.text((X+3,Y-16),n,fill='white')
    for f in range(1,10):
        xx=X+f/10*W*k;d.line([xx,Y,xx,Y+H*hb*k],fill=(0,255,255) if f==5 else (0,160,160),width=1)
        d.text((xx+1,Y+1),str(f),fill=(255,255,0))
    for f in range(1,int(hb*20)+1):
        yy=Y+f/20*H*k;d.line([X,yy,X+W*k,yy],fill=(255,0,255) if f%2==0 else (150,0,150),width=1)
        d.text((X+1,yy+1),str(f*5),fill=(255,255,255))
sh.save(out,quality=88)

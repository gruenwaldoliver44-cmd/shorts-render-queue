from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
F=lambda s:ImageFont.truetype('work/AB.ttf',s)
P='public/'
def spr(n,h,flip=0):
    im=Image.open(P+n+'.png').convert('RGBA');k=h/im.height;im=im.resize((int(im.width*k),h),Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
def glow(bg,im,x,y,col=(255,210,60),r=46):
    p=r*3;c=Image.new('RGBA',(im.width+2*p,im.height+2*p),(0,0,0,0));c.alpha_composite(im,(p,p));im=c;x-=p;y-=p
    a=im.split()[3].filter(ImageFilter.GaussianBlur(r));g=Image.new('RGBA',im.size,col+(0,));g.putalpha(a.point(lambda v:min(255,int(v*1.5))))
    bg.alpha_composite(g,(x,y));bg.alpha_composite(im,(x,y))
def text(d,xy,t,s,fill=(255,255,255),st=14,sc=(20,16,12),anchor='mm'):
    d.text(xy,t,font=F(s),fill=fill,stroke_width=st,stroke_fill=sc,anchor=anchor)
def sticker(bg,xy,t,s,rot=-4,fill=(194,65,45),tc=(255,245,230)):
    f=F(s);l,tp,r,b=f.getbbox(t);w,h=r-l+s,b-tp+s*.6
    im=Image.new('RGBA',(int(w),int(h)),fill+(255,));ImageDraw.Draw(im).text((w/2,h/2),t,font=f,fill=tc,anchor='mm')
    fr=Image.new('RGBA',(im.width+16,im.height+16),(20,16,12,255));fr.paste(im,(8,8));fr=fr.rotate(rot,expand=True,resample=Image.BICUBIC)
    bg.alpha_composite(fr,(int(xy[0]-fr.width/2),int(xy[1]-fr.height/2)))

def tagg(bg,xy,t,s_,red=0,rot=-5):
    sticker(bg,xy,t,s_,rot,fill=(194,65,45) if red else (243,236,220),tc=(255,255,255) if red else (20,16,12))
# A: zwei Nachbarinnen, gleicher Wagen, anderer Preis
bg=Image.open(P+'s_aisle.jpg').convert('RGBA');bg=ImageEnhance.Brightness(bg.convert('RGB')).enhance(.72).convert('RGBA')
a_=spr('li_cart',860);b=spr('ca_cart',860,1);bg.alpha_composite(a_,(-60,240));bg.alpha_composite(b,(1060,240))
tagg(bg,(430,170),'$72',150,1,-6);tagg(bg,(1490,170),'$67',150,0,5);sticker(bg,(960,940),'SAME CART',120,-2,fill=(28,23,18))
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/pr_a.jpg',quality=92)
# B: Haendler mit Lupe schaut aufs Handy
bg=Image.open(P+'s_inside.jpg').convert('RGBA');bg=ImageEnhance.Brightness(bg.convert('RGB')).enhance(.7).convert('RGBA')
k=spr('ke_glass',1000);ph=spr('pr_phone',640);bg.alpha_composite(k,(160,120));glow(bg,ph,1250,230,(120,200,255),40)
d=ImageDraw.Draw(bg);text(d,(1426,540),'$72',110,(194,65,45),st=0);sticker(bg,(1426,160),'YOUR PRICE',84,3)
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/pr_b.jpg',quality=92)
# C: Parkplatz: Preis springt
bg=Image.open(P+'s_lot.jpg').convert('RGBA');bg=ImageEnhance.Brightness(bg.convert('RGB')).enhance(.8).convert('RGBA')
m=spr('mi_mad',900);bg.alpha_composite(m,(1000,200));ph=spr('pr_phone',760);glow(bg,ph,190,170,(255,210,60),40)
d=ImageDraw.Draw(bg);text(d,(400,470),'$499',120,(20,16,12),st=0);text(d,(400,640),'$599',130,(194,65,45),st=0);d.line([(270,470),(530,470)],fill=(194,65,45),width=14);sticker(bg,(1360,120),'SAME TV',100,3)
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/pr_c.jpg',quality=92)
ims=[Image.open(f'th/pr_{x}.jpg') for x in 'abc']
sh=Image.new('RGB',(1920,360));[sh.paste(i.resize((640,360)),(k*640,0)) for k,i in enumerate(ims)]
sh.save('/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/th.jpg',quality=88)

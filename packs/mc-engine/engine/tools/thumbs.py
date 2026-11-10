from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
F=lambda s:ImageFont.truetype('work/AB.ttf',s)
P='public/'
def spr(n,h,flip=0):
    im=Image.open(P+n+'.png').convert('RGBA');k=h/im.height;im=im.resize((int(im.width*k),h),Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
def glow(bg,im,x,y,col=(255,210,60),r=46):
    a=im.split()[3].filter(ImageFilter.GaussianBlur(r));g=Image.new('RGBA',im.size,col+(0,));g.putalpha(a.point(lambda v:min(255,int(v*1.5))))
    bg.alpha_composite(g,(x,y));bg.alpha_composite(im,(x,y))
def text(d,xy,t,s,fill=(255,255,255),st=14,sc=(20,16,12),anchor='mm'):
    d.text(xy,t,font=F(s),fill=fill,stroke_width=st,stroke_fill=sc,anchor=anchor)
def sticker(bg,xy,t,s,rot=-4,fill=(194,65,45),tc=(255,245,230)):
    f=F(s);l,tp,r,b=f.getbbox(t);w,h=r-l+s,b-tp+s*.6
    im=Image.new('RGBA',(int(w),int(h)),fill+(255,));ImageDraw.Draw(im).text((w/2,h/2),t,font=f,fill=tc,anchor='mm')
    fr=Image.new('RGBA',(im.width+16,im.height+16),(20,16,12,255));fr.paste(im,(8,8));fr=fr.rotate(rot,expand=True,resample=Image.BICUBIC)
    bg.alpha_composite(fr,(int(xy[0]-fr.width/2),int(xy[1]-fr.height/2)))
# A: Der Laden besass den PC
bg=Image.open(P+'s_store25.jpg').convert('RGBA');bg=ImageEnhance.Brightness(bg.convert('RGB')).enhance(.8).convert('RGBA')
pc=spr('ob_pc',640);glow(bg,pc,620,380)
s=spr('rs_shock',640,1);bg.alpha_composite(s,(70,470))
sticker(bg,(1370,880),'THEY OWNED IT',96,-4)
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/sears_a.jpg',quality=92)
# B: Tresor/Verkauft: PC mit SOLD
bg=Image.open(P+'s_closed.jpg').convert('RGBA');pc=spr('ob_pc',700);glow(bg,pc,610,250)
d=ImageDraw.Draw(bg);sticker(bg,(960,600),'SOLD',190,-8)
sticker(bg,(960,950),'IN 1996',96,2,fill=(28,23,18))
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/sears_b.jpg',quality=92)
# C: Katalog plus Monitor, Verbindung fehlt
bg=Image.new('RGBA',(1920,1080),(194,65,45,255));c=spr('ob_cat',620);p=spr('ob_pc',680);bg.alpha_composite(c,(60,120));glow(bg,p,1090,90,(255,255,255),30)
d=ImageDraw.Draw(bg);text(d,(960,440),'+',260,(255,255,255),st=20)
sticker(bg,(960,950),'NEVER CONNECTED',104,-2,fill=(28,23,18))
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/sears_c.jpg',quality=92)
ims=[Image.open(f'th/sears_{x}.jpg') for x in 'abc']
sh=Image.new('RGB',(1920,360));[sh.paste(i.resize((640,360)),(k*640,0)) for k,i in enumerate(ims)]
sh.save('/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/th.jpg',quality=88)

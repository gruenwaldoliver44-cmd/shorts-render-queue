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


d0=None
# A: Das letzte Haus
bg=Image.open(P+'s_street.jpg').convert('RGBA');bg=ImageEnhance.Brightness(bg.convert('RGB')).enhance(.72).convert('RGBA')
l=spr('li_talk__c',880,1);glow(bg,l,1180,220,(255,210,60),36);c=spr('pr_contract',640);c=c.rotate(5,expand=True,resample=Image.BICUBIC);bg.alpha_composite(c,(90,300));sticker(bg,(470,150),'THE LAST HOUSE',84,-3)
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/ki_a.jpg',quality=92)
# B: NO
bg=Image.open(P+'s_street.jpg').convert('RGBA');bg=ImageEnhance.Brightness(bg.convert('RGB')).enhance(.55).convert('RGBA')
l=spr('li_talk',900);bg.alpha_composite(l,(90,190));d=ImageDraw.Draw(bg);text(d,(1270,470),'NO',420,fill=(255,210,60),st=20);sticker(bg,(1270,800),'142 SAID YES',80,-2)
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/ki_b.jpg',quality=92)
# C: Mast im Garten
bg=Image.open(P+'s_yard2.jpg').convert('RGBA');l=spr('li_bill',760);bg.alpha_composite(l,(1250,330));m=spr('mi_hips',720);bg.alpha_composite(m,(60,370));sticker(bg,(960,130),'THEY SAID NO',96,-2)
bg.convert('RGB').resize((1280,720),Image.LANCZOS).save('th/ki_c.jpg',quality=92)
ims=[Image.open(f'th/ki_{x}.jpg') for x in 'abc']
sh=Image.new('RGB',(1920,360));[sh.paste(i.resize((640,360)),(k*640,0)) for k,i in enumerate(ims)]
sh.save('/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/th.jpg',quality=88)

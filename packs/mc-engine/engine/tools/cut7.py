import numpy as np,json,sys
from PIL import Image,ImageFilter,ImageDraw
from scipy import ndimage as ni
A='art/';OUT='public/'
SH={'pr2':(2,['mc_rear','mc_side','mc_lap','mc_mouse','mc_letter','mc_crate','mc_pin','mc_coupon','mc_note','mc_env'])}
meta=json.load(open('src/sprites.json'))
for name,(rows,names) in SH.items():
    im=Image.open(A+name+'.png').convert('RGB');a=np.asarray(im).astype(int)
    nw=(a.min(axis=2)<238)|(a.max(axis=2)-a.min(axis=2)>16)
    lab,n=ni.label(~nw);bgl=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
    fg=~np.isin(lab,list(bgl))
    jo=ni.binary_dilation(fg,iterations={'prop':14,'linda':20,'carol':20,'mike':20,'keep':8,'old':6}.get(name,12));l2,m=ni.label(jo);obs=ni.find_objects(l2);it=[]
    for i,o in enumerate(obs):
        h=o[0].stop-o[0].start;w=o[1].stop-o[1].start
        if h*w<20000:continue
        it.append((o,i+1))
    H=a.shape[0]
    it.sort(key=lambda t:(int(((t[0][0].start+t[0][0].stop)/2)//(H/rows)),t[0][1].start))
    print(name,len(it),len(names),im.size)
    al=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.7));rgba=im.copy();rgba.putalpha(al)
    for k,(o,l) in enumerate(it):
        lm=l2[o]==l;c=rgba.crop((o[1].start,o[0].start,o[1].stop,o[0].stop));ca=np.asarray(c).copy();ca[...,3]=(ca[...,3]*lm).astype('uint8');c=Image.fromarray(ca);c=c.crop(c.getbbox())
        nm=names[k] if k<len(names) else f'{name}_x{k}'
        c.save(OUT+nm+'.png');meta[nm]=[round(c.width*700/c.height),700]
json.dump(meta,open('src/sprites.json','w'))
ns=[k for s in SH.values() for k in s[1] if k in meta]
c=12;W=H=170;sh=Image.new('RGB',(c*W,(len(ns)//c+1)*H),(90,120,140));d=ImageDraw.Draw(sh)
for i,n in enumerate(ns):
    p=Image.open(OUT+n+'.png');p.thumbnail((W-8,H-22));x,y=(i%c)*W+4,(i//c)*H+18;sh.paste(p,(x,y),p);d.text((x,y-15),n,fill='white')
sh.save('/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/cut.jpg',quality=85)

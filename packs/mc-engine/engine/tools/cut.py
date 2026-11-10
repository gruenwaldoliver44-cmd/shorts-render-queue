import numpy as np,json,sys
from PIL import Image,ImageFilter
from scipy import ndimage as ni
A='/home/claude/ys/ponzi/art/'
OUT='public/'
SHEETS={
 'ponzi1':(2,['p_grin','p_talk','p_open','p_point','p_laugh','p_shock','p_sweat','p_angry']),
 'ponzi2':(2,['p_jump','p_w1','p_w2','p_sit','p_back','p_count','p_sad','p_bow']),
 'young':(2,['y_hope','y_walk','y_coins','j_talk','d_tired','d_plate','d_scold','y_bed']),
 'women':(2,['r_talk','r_cross','r_laugh','r_cry','l_talk','l_cash','l_shock','l_sit']),
 'news':(2,['ba_talk','ba_angry','du_talk','du_shock','re_run','re_photo','mc_talk','mc_walk']),
 'cast':(2,['ins_note','ins_money','dk_point','dk_laugh','za_smile','za_run','do_urgent','do_hands','mo_soap','mo_grin','bk_no','bk_sweat']),'crowd':(3,['cr_a','cr_b','cr_c','cr_d','bk_a','bk_b','bk_c','bk_d','an_a','an_b','an_c','an_d']),'objs':(3,['ob_coupon','ob_donuts','ob_urn','ob_cash','ob_case','ob_stamps','ob_soap','ob_phone','ob_cane','ob_paper','ob_cart','ob_car'])}
meta={}
def cut(name,rows,names):
    im=Image.open(A+name+'.png').convert('RGB');a=np.asarray(im).astype(int)
    nw=(a.min(axis=2)<236)|(a.max(axis=2)-a.min(axis=2)>18)
    lab,n=ni.label(~nw);bgl=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
    bg=np.isin(lab,list(bgl))
    # kleine eingeschlossene weisse Flaechen zwischen Armen: gross genug = Hintergrund
    sz=ni.sum(~nw,lab,index=np.arange(n+1))
    for l in np.where(sz>2500)[0]:
        if l and l not in bgl:
            m=lab==l;
            if a[m].min(axis=1).mean()>246: pass
    fg=~bg
    jo=ni.binary_dilation(fg,iterations=7)
    l2,m=ni.label(jo);obs=ni.find_objects(l2);items=[]
    for i,o in enumerate(obs):
        h=o[0].stop-o[0].start;w=o[1].stop-o[1].start
        if h*w<9000: continue
        items.append((o[0].start,o[1].start,o,i+1))
    print(name,len(items))
    H=a.shape[0]
    yc=[(it[2][0].start+it[2][0].stop)/2 for it in items]
    rowh=H/rows
    items.sort(key=lambda t:(int(((t[2][0].start+t[2][0].stop)/2)//rowh),t[1]))
    al=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.8))
    rgba=im.copy();rgba.putalpha(al)
    res=[]
    for k,it in enumerate(items):
        o=it[2];lm=(l2[o]==it[3])
        c=rgba.crop((o[1].start,o[0].start,o[1].stop,o[0].stop))
        ca=np.asarray(c).copy();ca[...,3]=(ca[...,3]*lm).astype('uint8');c=Image.fromarray(ca)
        nm=names[k] if names and k<len(names) else f'{name}{k}'
        c=c.crop(c.getbbox())
        c.save(OUT+nm+'.png');res.append(nm);meta[nm]=[c.width,c.height]
    return res
for s,(r,n) in SHEETS.items():print(cut(s,r,n))
json.dump(meta,open('tools/sprites.json','w'))
# Kontaktbogen
import math
names=list(meta);c=12;W=H=210
sh=Image.new('RGB',(c*W,math.ceil(len(names)/c)*H),(90,120,140))
from PIL import ImageDraw
d=ImageDraw.Draw(sh)
for i,n in enumerate(names):
    im=Image.open(OUT+n+'.png');im.thumbnail((W-8,H-22));x,y=(i%c)*W+4,(i//c)*H+18
    sh.paste(im,(x,y),im);d.text((x,y-16),n,fill='white')
sh.save(sys.argv[1],quality=85)

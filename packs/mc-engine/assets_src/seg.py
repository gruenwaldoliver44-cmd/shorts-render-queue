from PIL import Image,ImageDraw
import numpy as np,json,sys
from scipy import ndimage as ni
def seg(src,minfrac=.08,flood=236):
    a=np.array(Image.open(src).convert('RGB'),float)
    w=a.min(2)>flood;l,c=ni.label(w);bg=np.zeros_like(w)
    for e in (l[0,:],l[-1,:],l[:,0],l[:,-1]):
        for i in set(e):
            if i:bg|=l==i
    fg=ni.binary_closing(~bg,iterations=2)
    L,n=ni.label(fg);obs=ni.find_objects(L)
    H=a.shape[0];it=[]
    for i,s in enumerate(obs):
        h=s[0].stop-s[0].start;wd=s[1].stop-s[1].start
        if max(h,wd)>H*minfrac:it.append(dict(i=i+1,y0=s[0].start,y1=s[0].stop,x0=s[1].start,x1=s[1].stop))
    it.sort(key=lambda q:(q['y0']+q['y1'])/2)
    rows=[]
    for q in it:
        cy=(q['y0']+q['y1'])/2
        if rows and abs(cy-rows[-1][0])<H*.18:rows[-1][1].append(q)
        else:rows.append([cy,[q]])
    out=[]
    for _,r in rows:out+=sorted(r,key=lambda q:q['x0'])
    return a,L,out
if __name__=='__main__':
    SP='/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/'
    for f in sys.argv[1:]:
        a,L,o=seg(f);im=Image.fromarray(a.astype('uint8')).resize((a.shape[1]//4,a.shape[0]//4));d=ImageDraw.Draw(im)
        for k,q in enumerate(o):d.rectangle((q['x0']//4,q['y0']//4,q['x1']//4,q['y1']//4),outline='red',width=2);d.text((q['x0']//4+3,q['y0']//4+2),str(k),fill='red')
        im.save(SP+'seg_'+f[:-4]+'.jpg');print(f,len(o))

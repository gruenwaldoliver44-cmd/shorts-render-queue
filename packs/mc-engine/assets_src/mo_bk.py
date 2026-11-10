from PIL import Image
import numpy as np,cv2,json
from scipy import ndimage as ni
P='/home/claude/ys/bk/eng/public/';VJ='/home/claude/ys/bk/eng/src/var.json'
SP='/tmp/claude-0/-home-claude/95541d93-a6b2-5be8-a916-f4d88c6fec50/scratchpad/'
BOX=json.load(open('box.json'));var={}
import os
TALK={'js_talk':'m_jess','js_shock':'m_jess','js_call':'m_jess2','js_ask':'m_jess2','js_stand':'m_jess','js_dead':'m_jess','js_smile':'m_jess2','js_sad':'m_jess2','gl_talk':'m_gloria','gl_point':'m_gloria','gl_cross':'m_gloria','gl_smug':'m_gloria','gl_glasses':'m_gloria','gl_stand':'m_gloria','er_shrug':'m_earl','er_stand':'m_earl','er_door':'m_earl','rp_talk':'m_earl','wt_talk':'m_wn','wt_stand':'m_wn','nu_talk':'m_wn','nu_stand':'m_wn','fl_talk':'m_fe','fl_stand':'m_fe','en_sit':'m_fe','ks_talk':'m_wk','ks_stand':'m_wk','pr_bow':'m_pruitt','pr_stand':'m_pruitt','pr_sweat':'m_pruitt','pr_box':'m_pruitt'}
HEAD={'en_sit':.4}
L=lambda f:np.array(Image.open(f).convert('RGB'))
tiles=[]
for nm,mf in TALK.items():
    if not os.path.exists(mf+'.png'):print('skip',nm);continue
    src,x0,x1,y0,y1=BOX[nm];A=L(src);Bm=L(mf+'.png')
    if Bm.shape!=A.shape:Bm=cv2.resize(Bm,(A.shape[1],A.shape[0]))
    hf=HEAD.get(nm,.3);H=y1-y0;hy=y0+int(H*hf);M=20
    ya,yb,xa,xb=max(0,y0-M),hy,max(0,x0-M),min(A.shape[1],x1+M)
    ref=cv2.cvtColor(A[ya:yb,xa:xb],cv2.COLOR_RGB2GRAY).astype('float32');g=cv2.cvtColor(Bm[ya:yb,xa:xb],cv2.COLOR_RGB2GRAY).astype('float32')
    W=np.eye(2,3,dtype='float32')
    try:cc,W=cv2.findTransformECC(cv2.GaussianBlur(ref,(0,0),2),cv2.GaussianBlur(g,(0,0),2),W,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,300,1e-6),None,5)
    except Exception as e:print('ECC fail',nm,e);cc=0
    Cb=Bm[ya:yb,xa:xb];w=cv2.warpAffine(Cb,W,(Cb.shape[1],Cb.shape[0]),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderValue=(255,255,255))
    C=A[ya:yb,xa:xb]
    d=np.abs(cv2.GaussianBlur(w.astype('float32'),(0,0),1.5)-cv2.GaussianBlur(C.astype('float32'),(0,0),1.5)).sum(2)>60
    d=ni.binary_opening(d,iterations=1);l,n=ni.label(d)
    if n==0:print('no diff',nm);continue
    sz=ni.sum(d,l,range(1,n+1));
    # bevorzugt Blob in der unteren Kopfhaelfte, nahe Mitte
    best=None;bs=0
    for i in range(n):
        ys,xs=np.where(l==i+1)
        if ys.mean()<d.shape[0]*.25 or sz[i]<30:continue
        sc=sz[i]
        if sc>bs:bs=sc;best=i+1
    if best is None:print('no mouth',nm);continue
    m=l==best;ys,xs=np.where(m)
    if (ys.max()-ys.min())>d.shape[0]*.45 or (xs.max()-xs.min())>d.shape[1]*.5:print('mouth too big',nm,np.ptp(ys),np.ptp(xs))
    U=ni.binary_dilation(m,iterations=6);F=ni.gaussian_filter(U.astype(float),3)[...,None]
    o=C*(1-F)+w*F
    base=np.array(Image.open(P+nm+'.png').convert('RGBA'),float)
    ox,oy=xa-x0,ya-y0
    tx0,ty0=max(0,ox),max(0,oy);sx0,sy0=max(0,-ox),max(0,-oy)
    nx=min(o.shape[1]-sx0,base.shape[1]-tx0);ny=min(o.shape[0]-sy0,base.shape[0]-ty0)
    out=base.copy();out[ty0:ty0+ny,tx0:tx0+nx,:3]=o[sy0:sy0+ny,sx0:sx0+nx]
    Image.fromarray(out.astype('uint8'),'RGBA').save(P+nm+'__c.png');var[nm]='c'
    print(nm,'cc',round(float(cc),3),'mouth px',int(m.sum()))
    th=C.shape[0];tiles.append(np.hstack([cv2.resize(C,(int(C.shape[1]*260/th),260)),cv2.resize(o.astype('uint8'),(int(C.shape[1]*260/th),260))]))
json.dump(var,open(VJ,'w'))
W_=max(t.shape[1] for t in tiles);rows=[];row=[];wsum=0
for t in tiles:
    if wsum+t.shape[1]>1800:rows.append(row);row=[];wsum=0
    row.append(t);wsum+=t.shape[1]
rows.append(row)
R=[np.hstack(r+[np.full((260,1800-sum(x.shape[1] for x in r),3),40,'uint8')]) for r in rows]
Image.fromarray(np.vstack(R)).save(SP+'mouths.jpg',quality=80)

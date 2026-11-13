"""Hand-placed mouth variants where ECC edit failed. open->closed: inpaint + closed lips; closed->open: draw open mouth."""
import cv2, numpy as np
from PIL import Image, ImageDraw
P='../engine/public/'
def load(n): return np.array(Image.open(P+n+'.png').convert('RGBA'))
def close(n, box, lip=(176,108,104)):
    a=load(n); x0,y0,x1,y1=box; rgb=a[...,:3].copy()
    m=np.zeros(a.shape[:2],np.uint8); cv2.ellipse(m,((x0+x1)//2,(y0+y1)//2),((x1-x0)//2+4,(y1-y0)//2+4),0,0,360,255,-1)
    rgb=cv2.inpaint(rgb,m,7,cv2.INPAINT_TELEA)
    im=Image.fromarray(np.dstack([rgb,a[...,3]])); d=ImageDraw.Draw(im)
    cx=(x0+x1)/2; cy=(y0+y1)/2+2; w=(x1-x0)*0.42
    d.ellipse([cx-w,cy-6,cx+w,cy+9],fill=lip+(255,))
    d.line([(cx-w-3,cy-1),(cx-w*0.4,cy+2),(cx+w*0.4,cy+2),(cx+w+3,cy-1)],fill=(20,14,14,255),width=4,joint='curve')
    im.save(P+n+'__c.png')
def openm(n, box):
    a=load(n); x0,y0,x1,y1=box; im=Image.fromarray(a); d=ImageDraw.Draw(im)
    cx=(x0+x1)/2; cy=(y0+y1)/2+3; w=(x1-x0)*0.36; h=13
    d.ellipse([cx-w-4,cy-h-4,cx+w+4,cy+h+4],fill=(176,108,104,255),outline=(20,14,14,255),width=4)
    d.ellipse([cx-w+4,cy-h+3,cx+w-4,cy+h-3],fill=(92,30,36,255))
    d.rectangle([cx-w*0.6,cy-h+3,cx+w*0.6,cy-h+8],fill=(250,250,250,255))
    d.ellipse([cx-w*0.5,cy+1,cx+w*0.5,cy+h-3],fill=(196,96,100,255))
    im.save(P+n+'__c.png')
close('mg_paper',(231,269,282,311))
close('tl_calm',(266,192,312,232),lip=(190,120,112))
openm('mg_talk',(219,265,286,290))
# better: swap mouths between the two manager busts (same character, same scale)
import scipy.ndimage as ni
def swap(dst, src, cd, cs, rx=40, ry=26, out=None):
    A=load(dst).astype(float); B=load(src).astype(float)
    if B.shape!=A.shape:
        Z=np.zeros_like(A); h=min(A.shape[0],B.shape[0]); w=min(A.shape[1],B.shape[1]); Z[:h,:w]=B[:h,:w]; B=Z
    H,W=A.shape[:2]; yy,xx=np.mgrid[0:H,0:W]
    m=(((xx-cd[0])/rx)**2+((yy-cd[1])/ry)**2<=1).astype(float); m=ni.gaussian_filter(m,3)[...,None]
    Bs=np.roll(np.roll(B,cd[1]-cs[1],0),cd[0]-cs[0],1)
    A[...,:3]=A[...,:3]*(1-m)+Bs[...,:3]*m
    Image.fromarray(A.astype('uint8')).save(P+(out or dst+'__c')+'.png')
swap('mg_talk','mg_paper',(252,278),(257,291))
swap('mg_paper','mg_talk',(257,291),(252,278))

import numpy as np,json
from PIL import Image,ImageDraw,ImageFilter
P='public/'
def mk(name,polys=(),thresh=None):
    im=Image.open(P+name+'.jpg').convert('RGBA');m=Image.new('L',im.size,0);d=ImageDraw.Draw(m)
    for p in polys:d.polygon(p,fill=255)
    a=np.asarray(m).copy()
    if thresh is not None:
        g=np.asarray(im.convert('L'));a=a*(g<thresh)
    m=Image.fromarray(a.astype('uint8')).filter(ImageFilter.GaussianBlur(.7));im.putalpha(m);im.save(P+'fg_'+name[2:]+'.png')
R=lambda x,y,w,h:[(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
mk('s_office',[[(378,802),(1582,802),(1690,930),(1690,1080),(262,1080),(262,930)],R(398,700,282,220),[(1336,752),(1580,752),(1580,920),(1336,920)],R(0,1000,230,80)])
mk('s_bank',[[(0,645),(1432,645),(1478,668),(1470,1000),(0,1000)]])
mk('s_kitchen',[[(652,636),(1270,636),(1270,700),(1150,700),(1150,1000),(1100,1040),(760,1040),(700,1000),(700,700),(652,700)]])
mk('s_cell',[R(0,0,1920,1080)],thresh=62)
mk('s_news',[R(0,705,1520,240),R(130,625,190,90),R(640,625,180,90),R(1160,625,170,90)])
mk('s_hanover',[R(0,700,1920,380)])
mk('s_galley',[R(140,800,1650,280)])
mk('s_swamp',[[(1062,866),(1780,920),(1740,1010),(1640,1040),(1200,1020),(1100,960)]])
mk('s_rio',[[(740,900),(1180,900),(1180,1100),(740,1100)]])
mk('s_street',[])

import json
from PIL import Image
m=json.load(open('tools/sprites.json'))
names='p_talk p_open p_point p_grin p_laugh p_shock p_angry p_sweat p_sad y_hope y_coins j_talk d_scold d_tired r_talk r_cross r_laugh l_talk l_shock ba_talk ba_angry du_talk du_shock re_photo mc_talk ins_note ins_money dk_point dk_laugh za_smile mo_grin do_urgent bk_no bk_sweat cr_a bk_a cr_c an_b an_c an_d'.split()
B=[(118,108,26,26),(120,72,18,12),(136,78,16,6),(137,104,56,20),(125,100,60,36),(120,128,40,46),(118,95,40,16),(116,110,24,8),
(148,135,16,6),(158,95,44,20),(95,100,20,6),(142,105,26,20),(168,120,44,24),(150,132,24,10),(82,105,18,9),(120,157,34,10),
(118,165,76,44),(87,96,18,10),(117,165,30,34),(105,65,24,7),(103,77,24,8),(130,85,20,6),(82,78,20,12),(80,102,36,22),
(135,108,30,12),(122,125,22,5),(100,92,34,14),(125,108,20,5),(125,80,66,38),(120,146,30,6),(118,123,70,26),(115,112,36,10),
(120,117,20,5),(122,123,32,8),(98,90,40,22),(135,92,34,16),(88,118,30,14),(82,103,36,18),(86,108,34,18),(90,108,32,18)]
assert len(B)==len(names)
out={}
S=240
for n,b in zip(names,B):
    W,H=m[n];head=.40 if n[0]=='r' else .34
    k=S/max(W,H*head)
    cx,cy,w,h=b[0]/k,b[1]/k,b[2]/k,b[3]/k
    pad=1.25;w*=pad;h*=pad
    im=Image.open(f'public/{n}.png').convert('RGBA')
    # Hautfarbe seitlich neben dem Mund
    sx=int(min(W-1,cx+w*.62));sy=int(cy);p=im.getpixel((sx,sy));q=im.getpixel((int(max(0,cx-w*.62)),sy))
    c=q if sum(q[:3])>sum(p[:3]) else p
    out[n]=[round(cx/W,4),round(cy/H,4),round(w/W,4),round(h/H,4),'#%02x%02x%02x'%c[:3]]
json.dump(out,open('src_mouth.json','w'))
print(len(out))

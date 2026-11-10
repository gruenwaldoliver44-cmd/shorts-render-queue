import json,numpy as np,sys
sys.argv=['x','/dev/null']
src=open('tools/cut.py').read().split("for s,(r,n) in SHEETS")[0]
src=src.replace("A='/home/claude/ys/ponzi/art/'","A='/home/claude/ys/sears/art/'")
exec(src)
try: old=json.load(open('src/sprites.json'))
except: old={}
meta.update(old)
S={'sears1':(2,'rs_grin rs_talk rs_scheme rs_point rs_watch rs_w1 rs_w2 rs_shock'),
'sears2':(2,'sr_talk sr_wide sr_shrug sr_book jr_talk jr_cross jr_bill jr_think'),
'wood':(2,'wo_talk wo_chart wo_fist wo_read wo_w1 wo_w2 wb_wave wb_door'),
'farm':(2,'fa_laugh fa_talk fa_shock fa_book wi_read wi_talk wi_cross wi_happy'),
'c70':(2,'ch_smug ch_talk ch_up ch_laugh di_talk di_sweat di_shock di_chart br_socks br_chart ol_conf ol_sad'),
'execs':(2,'ea_talk ea_mad eb_talk eb_mad mg_talk mg_lap cl_sad cl_shrug'),
'crowd50':(2,'sh_a sh_b sh_c sh_d sh_e sh_f sh_g sh_h sh_i sh_j sh_k sh_l'),
'kids':(1,'kb_a kb_b kg_a kg_b'),
'ob1':(3,'ob_crate ob_watch ob_cat ob_wish ob_crayon ob_house ob_auto ob_piano ob_plow ob_fridge ob_wrench ob_plan'),
'ob2':(3,'ob_pc ob_modem ob_mail ob_quarter ob_box ob_socks ob_chart ob_bucket ob_screen ob_shelf ob_bag ob_trolley')}
import os
if os.path.exists(A+'dad.png'):S['dad']=(1,'da_up da_mad da_talk op_flat')
_src=src
for k,(r,n) in S.items():
    if k=='sears1':
        exec(_src.replace('iterations=7','iterations=1').replace("meta={}","")) 
    else:
        exec(_src.replace("meta={}",""))
    print(cut(k,r,n.split()))
json.dump(meta,open('src/sprites.json','w'))
# sears1 entwirren
from PIL import Image
import os,json
P='public/'
m=Image.open(P+'rs_w2.png').copy();wa=Image.open(P+'rs_watch.png').copy();wb=Image.open(P+'rs_w1.png').copy();wt=Image.open(P+'rs_point.png').copy()
wt.save(P+'rs_watch.png');wa.save(P+'rs_w1.png');wb.save(P+'rs_w2.png')
a=np.asarray(m.convert('RGBA'))
# Trennzeile: dort wo die opake Breite minimal ist, im Bereich 45-65 % der Hoehe
H=a.shape[0];w=[(a[y,:,3]>40).sum() for y in range(H)]
y0=int(H*.42);y1=int(H*.68);ys=min(range(y0,y1),key=lambda y:w[y]);print('split',ys,w[ys],H)
top=m.crop((0,0,m.width,ys));bot=m.crop((0,ys,m.width,H));top=top.crop(top.getbbox());bot=bot.crop(bot.getbbox())
top.save(P+'rs_point.png');bot.save(P+'rs_shock.png')
meta=json.load(open('src/sprites.json'))
for n in ('rs_point','rs_shock','rs_watch','rs_w1','rs_w2'):
    im=Image.open(P+n+'.png');meta[n]=[im.width,im.height]
# Hoehe normieren (Sprite rechnet mit nativ 700)
for n,(w_,h_) in list(meta.items()):
    if n[:3]=='ob_' or n.startswith('kb_') or n.startswith('kg_') or n in ('clip',):continue
    if h_!=700 and n[:2] in('rs','sr','jr','wo','wb','fa','wi','ch','di','br','ol','ea','eb','mg','cl','sh','da','op'):
        meta[n]=[round(w_*700/h_),700]
json.dump(meta,open('src/sprites.json','w'))

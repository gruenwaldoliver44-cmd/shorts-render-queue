from PIL import Image
import numpy as np,json,os
from scipy import ndimage as ni
from seg import seg
P='/home/claude/ys/bk/eng/public/';SJ='/home/claude/ys/bk/eng/src/sprites.json'
S={};BOX={}
def cut(src,names):
    a,L,o=seg(src)
    assert len(o)==len(names),(src,len(o))
    for q,nm in zip(o,names):
        if nm is None:continue
        s=(slice(q['y0'],q['y1']),slice(q['x0'],q['x1']))
        m=(L==q['i'])[s];al=ni.gaussian_filter(m.astype(float),.7)
        im=Image.fromarray(np.dstack([a[s],al*255]).astype('uint8'),'RGBA');im.save(P+nm+'.png')
        S[nm]=[round(im.width*700/im.height),700];BOX[nm]=(src,q['x0'],q['x1'],q['y0'],q['y1'])
cut('c_jess.png','js_stand js_talk js_phone js_shock js_walk js_dead'.split())
cut('c_jess2.png','js_call js_smile js_type js_ask js_sad js_sit'.split())
cut('c_gloria.png','gl_cross gl_talk gl_point gl_stand gl_glasses gl_smug'.split())
cut('c_earl.png','er_stand er_shrug er_door rp_talk rp_stand'.split())
cut('c_pruitt.png','pr_stand pr_run pr_bow pr_walk pr_sweat pr_box pp_shoe'.split())
cut('c_wn.png','wt_stand wt_talk wt_jaw nu_stand nu_talk nu_wave'.split())
cut('c_fe.png','fl_stand fl_talk fl_glance en_walk en_sit'.split())
cut('c_wk.png','wh_sit wh_stand ks_walk ks_stand ks_talk kid_phone'.split())
cut('c_extras.png','ex_a ex_b ex_c ex_d ex_e ex_f'.split())
if os.path.exists('c_props.png'):
    a,L,o=seg('c_props.png');print('props',len(o))
    nm='pp_chain pp_silver pp_jar pp_esp pp_pastry pp_cup pp_stock pp_gift pp_nozzle pp_phone pp_loan pp_check'.split()
    if len(o)==len(nm):cut('c_props.png',nm)
json.dump(S,open(SJ,'w'));json.dump(BOX,open('box.json','w'))
print(len(S))

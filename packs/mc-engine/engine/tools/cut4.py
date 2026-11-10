import re
s=open('tools/cut3.py').read()
a=s.index("SH={");b=s.index("meta=json.load")
new='''SH={'linda':(2,['li_stand','li_w1','li_w2','li_cart','li_conf','li_shock','li_joy','li_sit']),
'carol':(2,['ca_stand','ca_w1','ca_w2','ca_cart','ca_look','ca_show','ca_laugh','ca_sit']),
'mike':(2,['mi_stand','mi_w1','mi_w2','mi_cart','mi_phone','mi_mad','mi_shrug','mi_jump']),
'keep':(2,['ke_stand','ke_w1','ke_w2','ke_glass','ke_sly','ke_point','ke_cross','ke_read']),
'old':(2,['ri_watch','ri_w1','ri_w2','ri_shock','fa_hips','fm_w1','fm_egg','fm_x','fm_y','fm_z','qu_stand','qu_x','qu_w','qu_card']),
'prop':(3,['pr_tag','pr_dig','pr_eggs','pr_stapler','pr_dvd','pr_box','pr_tv','pr_phone','pr_folder','pr_therm','pr_receipt','pr_shoe','pr_boot','pr_glass','pr_cart'])}
'''
s=s[:a]+new+s[b:]
s=s.replace("{'wise1':22,'bowl':34,'obj':22,'cast':16}.get(name,4)","{'prop':14,'linda':20,'carol':20,'mike':20,'keep':20,'old':6}.get(name,14)")
open('tools/cut5.py','w').write(s)

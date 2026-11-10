import json
from PIL import Image
B={'rs_grin':(.50,.225,.26,.07),'rs_talk':(.56,.25,.16,.06),'rs_scheme':(.50,.245,.30,.06),'sr_talk':(.50,.215,.14,.04),'sr_wide':(.50,.19,.07,.04),
'jr_talk':(.44,.23,.13,.04),'jr_bill':(.53,.245,.06,.04),'wo_talk':(.50,.275,.12,.04),'wo_fist':(.45,.275,.10,.02),'wb_wave':(.45,.24,.10,.03),
'fa_talk':(.52,.295,.15,.05),'fa_laugh':(.55,.25,.22,.08),'wi_talk':(.55,.24,.13,.05),'wi_read':(.54,.24,.08,.02),'ch_talk':(.50,.255,.16,.05),'ch_smug':(.50,.26,.30,.06),
'di_talk':(.50,.30,.18,.06),'di_sweat':(.54,.27,.18,.06),'br_socks':(.45,.22,.22,.06),'br_chart':(.45,.25,.20,.05),'ol_conf':(.47,.37,.10,.02),'ol_sad':(.47,.365,.10,.02),
'ea_talk':(.46,.27,.13,.03),'ea_mad':(.44,.25,.12,.05),'eb_talk':(.55,.255,.13,.03),'eb_mad':(.335,.25,.09,.04),'mg_talk':(.47,.25,.13,.03),'mg_lap':(.50,.235,.13,.02),
'kb_b':(.46,.35,.13,.04),'kg_b':(.46,.36,.13,.04),'da_up':(.53,.22,.06,.03),'da_mad':(.50,.20,.10,.02),'da_talk':(.30,.20,.06,.04),'op_flat':(.40,.245,.13,.02)}
m=json.load(open('src/mouth.json'))
for n,(cx,cy,w,h) in B.items():
    im=Image.open(f'public/{n}.png').convert('RGBA');W,H=im.size
    px=[im.getpixel((int(max(0,min(W-1,(cx+s*w*.75)*W))),int((cy-h*.6)*H))) for s in(-1,1)]
    c=max(px,key=lambda p:sum(p[:3]))
    m[n]=[cx,cy,round(w*1.25,4),round(h*1.25,4),'#%02x%02x%02x'%c[:3]]
json.dump(m,open('src/mouth.json','w'));print(len(m))

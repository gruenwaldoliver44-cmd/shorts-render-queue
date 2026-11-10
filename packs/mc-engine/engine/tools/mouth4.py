import json
from PIL import Image
B={'li_stand':(.50,.197,.11,.018),'li_conf':(.50,.197,.07,.015),'li_shock':(.42,.20,.09,.025),'li_joy':(.55,.165,.08,.025),
'ca_stand':(.50,.212,.11,.018),'ca_look':(.565,.217,.10,.018),'ca_show':(.37,.20,.08,.018),'ca_laugh':(.48,.20,.09,.03),
'mi_stand':(.50,.232,.08,.014),'mi_phone':(.54,.22,.07,.014),'mi_mad':(.535,.26,.08,.025),'mi_shrug':(.50,.25,.055,.012),
'ke_stand':(.50,.242,.07,.012),'ke_sly':(.65,.225,.10,.018),'ke_point':(.45,.225,.05,.014)}
m=json.load(open('src/mouth.json'))
for n,(cx,cy,w,h) in B.items():
    im=Image.open(f'public/{n}.png').convert('RGBA');W,H=im.size
    px=[im.getpixel((int(max(0,min(W-1,(cx+s*w*.75)*W))),int((cy-h*.6)*H))) for s in(-1,1)]
    c=max(px,key=lambda p:sum(p[:3]))
    m[n]=[cx,cy,round(w*1.25,4),round(h*1.25,4),'#%02x%02x%02x'%c[:3]]
json.dump(m,open('src/mouth.json','w'));print(len(m),{k:m[k][4] for k in B})

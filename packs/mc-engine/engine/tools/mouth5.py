import json
from PIL import Image
B={'li_talk':(.52,.25,.10,.028),'li_lap':(.345,.25,.10,.03),'li_bill':(.38,.25,.08,.02),'mi_hips':(.53,.225,.06,.012),'mi_call':(.48,.255,.10,.035),'mt_stand':(.50,.22,.10,.015),'mi_up':(.48,.245,.05,.02),'ke_gavel':(.45,.31,.10,.03)}
m=json.load(open('src/mouth.json'))
for n,(cx,cy,w,h) in B.items():
    im=Image.open(f'public/{n}.png').convert('RGBA');W,H=im.size
    px=[im.getpixel((int(max(0,min(W-1,(cx+s*w*.75)*W))),int((cy-h*.6)*H))) for s in(-1,1)]
    c=max(px,key=lambda p:sum(p[:3]))
    m[n]=[cx,cy,round(w*1.25,4),round(h*1.25,4),'#%02x%02x%02x'%c[:3]]
json.dump(m,open('src/mouth.json','w'));print(len(m),{k:m[k][4] for k in B})

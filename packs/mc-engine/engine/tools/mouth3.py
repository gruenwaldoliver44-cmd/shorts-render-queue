import json
from PIL import Image
B={'bw_talk':(.485,.268,.09,.035),'bw_mic':(.565,.272,.075,.03),'bw_phone':(.515,.285,.12,.045),'bw_hips':(.505,.283,.10,.02),'bw_lump':(.385,.267,.07,.02),'bw_old':(.525,.295,.09,.02),
'et_talk':(.625,.213,.11,.03),'et_stiff':(.275,.21,.08,.015),'et_phone':(.52,.22,.09,.03),'et_angry':(.405,.222,.06,.02),
'dl_catch':(.58,.305,.045,.015),'wk_baff':(.50,.33,.045,.015),'ck_shrug':(.495,.32,.05,.01),'sp_hand':(.725,.34,.08,.015),'pz_fat':(.535,.27,.07,.02)}
m=json.load(open('src/mouth.json'))
for n,(cx,cy,w,h) in B.items():
    im=Image.open(f'public/{n}.png').convert('RGBA');W,H=im.size
    px=[im.getpixel((int(max(0,min(W-1,(cx+s*w*.75)*W))),int((cy-h*.6)*H))) for s in(-1,1)]
    c=max(px,key=lambda p:sum(p[:3]))
    m[n]=[cx,cy,round(w*1.25,4),round(h*1.25,4),'#%02x%02x%02x'%c[:3]]
json.dump(m,open('src/mouth.json','w'));print(len(m),{k:m[k][4] for k in B})

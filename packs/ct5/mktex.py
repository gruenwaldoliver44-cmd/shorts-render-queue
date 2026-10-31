import random, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(3)
W,H=1000,1600
F=lambda s,b=True: ImageFont.truetype('tex/Inter800.ttf' if b else 'tex/Inter500.ttf', s)
# --- numbers: 8 grids of 3x3 from 1..39; singletons rare; grid 5 middle row = three singletons
while True:
    pool=list(range(1,40))
    sing_row=random.sample(pool,3)
    rest=[n for n in pool if n not in sing_row]
    others_single=random.sample(rest,3)            # a few scattered singletons (not in a line)
    dup=[n for n in rest if n not in others_single]
    cells=[]
    need=72-3-3
    seq=[]
    for n in dup: seq+= [n,n]
    random.shuffle(seq); seq=seq[:need]
    # make sure every number in seq appears >=2
    from collections import Counter
    c=Counter(seq)
    if any(v<2 for v in c.values()): continue
    fill=seq+others_single; random.shuffle(fill)
    grids=[]; k=0
    for g in range(8):
        gr=[]
        for r in range(3):
            if g==5 and r==1: gr.append(sing_row[:]); continue
            gr.append(fill[k:k+3]); k+=3
        grids.append(gr)
    allv=Counter(v for gr in grids for row in gr for v in row)
    singles={v for v,n in allv.items() if n==1}
    # no other line (row/col/diag) of three singletons
    bad=False
    for gi,gr in enumerate(grids):
        lines=[gr[r] for r in range(3)]+[[gr[r][c] for r in range(3)] for c in range(3)]+[[gr[i][i] for i in range(3)],[gr[i][2-i] for i in range(3)]]
        for li,l in enumerate(lines):
            if all(v in singles for v in l) and not (gi==5 and li==1): bad=True
    if not bad and set(sing_row)<=singles: break
# --- layout
def base(revealed):
    im=Image.new('RGB',(W,H),(250,246,236)); d=ImageDraw.Draw(im)
    for y in range(0,190):
        u=y/190; d.line([(0,y),(W,y)],fill=(int(40+30*u),int(22+40*u),int(90+30*u)))
    d.text((W/2,70),'LUCKY GRID',font=F(92),anchor='mm',fill=(255,214,90))
    d.text((W/2,145),'TIC  ·  TAC  ·  TOE        $3',font=F(40,False),anchor='mm',fill=(230,230,250))
    d.rounded_rectangle([40,210,W-40,520],24,fill=(232,228,218),outline=(60,40,110),width=5)
    d.text((W/2,240),'YOUR NUMBERS',font=F(34),anchor='mm',fill=(60,40,110))
    yours=sing_row+random.Random(9).sample([n for n in range(1,40) if n not in sing_row],21)
    random.Random(4).shuffle(yours)
    for i in range(24):
        cx=110+(i%8)*112; cy=310+(i//8)*80
        if revealed:
            d.text((cx,cy),str(yours[i]),font=F(46),anchor='mm',fill=(30,30,40))

    if not revealed:
        lat=Image.new('RGB',(W-120,237),(178,180,186)); ld=ImageDraw.Draw(lat)
        for x in range(-300,W,26): ld.line([(x,0),(x+240,237)],fill=(190,192,198),width=9)
        mk=Image.new('L',(W-120,237),0); ImageDraw.Draw(mk).rounded_rectangle([0,0,W-121,236],16,fill=255)
        im.paste(lat,(60,268),mk); d=ImageDraw.Draw(im)
        d.text((W/2,388),'SCRATCH',font=F(76),anchor='mm',fill=(150,152,160))
    pos={}
    for g in range(8):
        gx=60+(g%2)*470; gy=560+(g//2)*240
        d.rounded_rectangle([gx,gy,gx+410,gy+220],18,fill=(255,255,255),outline=(60,40,110),width=4)
        for r in range(3):
            for c in range(3):
                x=gx+70+c*135; y=gy+40+r*70
                if c: d.line([(x-67,gy+12),(x-67,gy+208)],fill=(200,195,215),width=3)
                if r: d.line([(gx+12,y-35),(gx+398,y-35)],fill=(200,195,215),width=3)
                d.text((x,y),str(grids[g][r][c]),font=F(52),anchor='mm',fill=(20,20,30))
                pos['%d_%d_%d'%(g,r,c)]=(x/W,y/H)
    d.text((W/2,1545),'MATCH 3 IN A ROW  ·  WIN UP TO $50,000',font=F(30,False),anchor='mm',fill=(90,80,110))
    return im,pos
a,pos=base(False); a.save('tex/ticket_cov.png')
b,_=base(True); b.save('tex/ticket_rev.png')
singles_pos=[pos['%d_%d_%d'%(g,r,c)] for g in range(8) for r in range(3) for c in range(3) if grids[g][r][c] in singles]
win=[pos['5_1_%d'%c] for c in range(3)]
json.dump({'singles':singles_pos,'win':win},open('tex/ticket.json','w'))
# red marker circle (transparent)
ci=Image.new('RGBA',(256,256),(0,0,0,0)); cd=ImageDraw.Draw(ci)
cd.ellipse([18,30,238,226],outline=(210,24,30,255),width=14); ci=ci.filter(ImageFilter.GaussianBlur(1.2)); ci.save('tex/circle.png')
print('singles',sorted(singles),'row',sing_row,len(singles_pos))

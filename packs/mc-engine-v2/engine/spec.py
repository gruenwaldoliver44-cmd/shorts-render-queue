# Sears: Regie als fortlaufende Welt. Figuren leben in Szenen ueber mehrere Zeilen.
import json
INK='#1c1712';PAPER='#efe8dc';RED='#c2412d'
SCN=[];SFX=[];LI={};CARDS=[]
def R(t):
    if isinstance(t,dict):return t['abs']
    if isinstance(t,int):return LI[t]['from_']
    l=LI[t[0]];r=t[1];off=t[2] if len(t)>2 else 0
    if isinstance(r,float):return l['from_']+int(r*l['vf'])+off
    if isinstance(r,int):return l['from_']+r+off
    i=l['txt'].find(r);assert i>=0,(t,l['txt'])
    return l['from_']+max(0,round(l['vf']*i/len(l['txt']))-2)+off
def sfx(n,t,g=1,rep=1,gap=8):
    f=R(t)
    for i in range(rep):SFX.append((f+i*gap,n,g))
OFF=dict(set='s_office',fg='fg_office',depth=[800,400,1000,640],door=dict(x=1022,y=352,w=228,h=448,hinge='r'))
KIT=dict(set='s_kitchen',fg='fg_kitchen',depth=[860,620,1000,800],door=dict(x=115,y=250,w=292,h=610,hinge='l'))
DIG=dict(set='s_dig',depth=[545,110,1060,600],door=dict(x=924,y=403,w=104,h=108,dbl=1))
BCK=dict(set='s_back',depth=[590,250,1060,760],door=dict(x=905,y=360,w=115,h=216,hinge='r'))
SLG=dict(set='s_slag',depth=[820,520,1060,760],door=dict(x=1356,y=288,w=228,h=516,hinge='r'))
DPT=dict(set='s_dept',depth=[880,600,1060,800])
STG=dict(set='s_stage',depth=[720,480,890,640])
STS=dict(STG,set='s_stS');STC=dict(STG,set='s_stC');STB=dict(STG,set='s_stB')
LAK=dict(set='s_lake',depth=[700,130,1060,720],door=dict(x=1368,y=564,w=72,h=132,hinge='l'))
BOX=dict(set='s_bigbox',depth=[620,60,1070,760])
ISL=dict(set='s_island')
LIV=dict(set='s_liv60')
SWP=dict(set='s_swamp',fg='fg_swamp')
BNK=dict(set='s_bank',fg='fg_bank',depth=[640,330,1040,800])
MAP=dict(set='s_map')
class A:
    def __init__(s,sc,id,ch,x,y,sp,**k):
        s.d=dict(key=len(sc.actors)+len(SCN)*100,id=id,ch=ch,pos=[[0,x,y,0]],sp=[[0,sp]],fl=[[0,k.pop('flip',0)]],hop=[],shk=[],rock=[],t0=0,shadow=k.pop('shadow',True))
        for q in ('lt','dt','drop','pop','t0'):
            if q in k and k[q] is not None and not (q=='t0' and k[q]==0):k[q]=R(k[q])
        s.d.update(k);s.sc=sc
    def go(s,t,x,y,dur,ease=0):
        f=R(t);s.d['pos'].append([f,x,y,dur,ease])
        if s.d.get('walk') or s.d.get('steps'):
            sfx('step',{'abs':f},s.d.get('sg',.22),rep=max(1,dur//14),gap=14)
        return s
    def p(s,t,n):s.d['sp'].append([R(t),n]);return s
    def f(s,t,v):s.d['fl'].append([R(t),v]);return s
    def hop(s,t,snd=1):
        f=R(t);s.d['hop'].append(f)
        if snd:sfx('whoosh',{'abs':f},.4)
        return s
    def shake(s,t,dur):f=R(t);s.d['shk'].append([f,f+dur]);return s
    def rock(s,t,dur,a=3):f=R(t);s.d['rock'].append([f,f+dur,a]);return s
    def show(s,t):s.d['t0']=R(t);return s
    def gone(s,t):s.d['t1']=R(t);return s
    def tg(s,t,txt,red=0,snd=1):
        s.d.setdefault('tag',[]).append([R(t),txt,red])
        if snd and txt:sfx('pop',t,.45)
        return s
    def set(s,**k):
        for a,b in k.items():s.d[a]=R(b) if a in('lt','dt','drop','pop') else b
        return s
class S:
    def __init__(s,t,base=None,z=1,cx=960,cy=540,**k):
        d=dict(base or {});d.update(k);s.d=d;s.start=R(t);s.actors=[];s.cam_=[[s.start,z,cx,cy,0]];s.over=[];s.bub_off=set();s.shk=[];s.bx=[]
        if 'door' in d:d['door']=dict(d['door'],ev=[]);
        SCN.append(s)
    def a(s,id,x,y,sp,ch=None,**k):
        o=A(s,id,ch,x,y,sp,**k);s.actors.append(o);return o
    def P(s,x,y,sp,**k):
        k.setdefault('still',1);k.setdefault('shadow',False);return s.a('p',x,y,sp,**k)
    def cam(s,t,z,cx,cy,dur=0):s.cam_.append([R(t),z,cx,cy,dur]);return s
    def door(s,t,v=1,dur=12,snd=1):
        f=R(t);ev=s.d['door']['ev'];prev=ev[-1][1] if ev else 0;ev.append([f,v,dur,prev])
        if snd:sfx('door',{'abs':f+(dur-4 if v==0 else 0)},.7 if v==0 else .45)
        return s
    def shk_(s,t,a=14):s.shk.append([R(t),a]);return s
    def o(self,k,t,t1=None,**kw):
        d=dict(k=k,t=R(t))
        if t1 is not None:d['t1']=R(t1)
        d.update(kw);self.over.append(d);return self
    def u(self,k,t=None,t1=None,**kw):
        d=dict(k=k,t=self.start if t is None else R(t))
        if t1 is not None:d['t1']=R(t1)
        d.update(kw);self.d.setdefault('under',[]).append(d);return self
    def top(self,k,t=None,t1=None,**kw):
        d=dict(k=k,t=self.start if t is None else R(t))
        if t1 is not None:d['t1']=R(t1)
        d.update(kw);self.d.setdefault('top',[]).append(d);return self
    def say(self,t,t1,ch,txt,**kw):
        self.bx.append(dict(ch=ch,t=R(t),t1=R(t1),txt=txt,**kw));return self
    def chip(s,t,txt,x,y,size=48,red=0,rot=0,t1=None,snd='pop'):
        s.o('chip',t,t1,txt=txt,x=x,y=y,size=size,red=red,rot=rot)
        if snd:sfx(snd,t,.5)
        return s
    def stamp(s,t,txt,x=960,y=540,size=90,rot=-6,t1=None):
        s.o('stamp',t,t1,txt=txt,x=x,y=y,size=size,rot=rot);sfx('stampx',t,.95);s.shk_(t,10);return s
    def loc(s,t,txt,t1=None):
        f=R(t);s.o('loc',t,None,txt=txt);s.over[-1]['t1']=f+100;sfx('paper',t,.4);return s
    def nob(s,*l):s.bub_off|=set(l);return s
def queue(sc,t,n=12,x0=1000,y0=790,x1=1700,y1=1060,rows=1,names=('bk_b','bk_c','bk_d','an_a'),gap=0):
    out=[]
    for i in range(n):
        for r in range(rows):
            p=i/(max(1,n-1));x=x0+(x1-x0)*p+(r-(rows-1)/2)*(60+150*p);y=y0+(y1-y0)*p
            nm=names[(i*3+r*5)%len(names)]
            a=sc.a('q%d_%d'%(i,r),x,y,nm,ws=11);a.d['q']=1
            if gap:a.go(t,x,y,gap)
            out.append(a)
    return out
exec(open('scenes.py').read())
REAL={}
def run(lines,cards,total):
    global LI
    for l in lines:LI[l['i']]=l
    CARDS.extend(cards)
    direct()
    # Sound fuer jede Einblendung
    drop=set()
    for s_ in SCN:
        for o in s_.over:
            k,t0=o.get('k'),o.get('t',0)
            if k in('paper','doc'):
                SFX.append((max(0,t0-3),'news',1.0));drop.add(t0)
            elif k=='app':SFX.append((t0,'swipe',.8))
            elif k=='pic' and not o.get('drop') and not o.get('to'):SFX.append((t0,'pop',.7))
            elif k=='pic' and o.get('drop'):SFX.append((t0+2,'land',.7))
            elif k=='num' and o.get('a')!=o.get('b') and o.get('dur',0)>=10 and o.get('dur',0)<200:
                n_=min(12,o['dur']//3)
                for i in range(n_):SFX.append((t0+i*3,'tick',.35))
                SFX.append((t0+o['dur'],'pop',.8))
        for p in s_.d.get('under',[]):
            if p.get('k')=='card' and p.get('t',0)>s_.start+2:SFX.append((p['t'],'pin',.8))
    SFX[:]=[q for q in SFX if not(q[1]=='paper' and any(abs(q[0]-d_)<9 for d_ in drop))]
    # Chapter-Karten als eigene Szenen
    CT={1:'The Deal',2:'The Boom',3:'The Spies',4:'The Order Book',5:'The Rule',6:'The Runway',7:'The Seat'}
    for n,f,d in cards:
        s=S({'abs':f},dict(set='#c2412d'));s.o('paper',{'abs':f},None,head=CT[n],spin=1,mast='Money Classics',date='Chapter %d'%n,fs=150,w=1500);SFX.append((f,'whoosh',.8));SFX.append((f+15,'wood',.6))
    SCN.sort(key=lambda s:s.start)
    for a,b in zip(SCN,SCN[1:]):
        if a.d.get('set')!=b.d.get('set'):SFX.append((b.start,'whoosh',.3))
    out=[]
    for i,s in enumerate(SCN):
        end=SCN[i+1].start if i+1<len(SCN) else total
        d=dict(s.d);d['from']=s.start;d['dur']=end-s.start
        cam=[]
        c=s.cam_
        for j,k in enumerate(c):
            cam.append(k)
            he=k[0]+k[4];nx=c[j+1][0] if j+1<len(c) else end
            if nx-he>6:
                drift=1+min(.09,(nx-he)/30*.018)
                cam.append([he,k[1]*drift,k[2]+(8 if j%2 else -8),k[3]-5,nx-he-1])
        d['cam']=cam;d['shk']=s.shk;d['over']=s.over
        d['actors']=[a.d for a in s.actors]
        for a in d['actors']:
            for x in ('pos',):a[x]=[[s.start if q==0 and x=='pos' else q[0]]+q[1:] if False else q for q in a[x]]
            a['t0']=a['t0'] or 0
        ch={a.d['ch'] for a in s.actors if a.d['ch']}
        d['bub']=[]
        for l in lines:
            if False and l['ch'] in ch and s.start<=l['from_']<end and l['i'] not in s.bub_off:
                d['bub'].append(dict(ch=l['ch'],t=l['from_'],t1=l['from_']+l['vf']+3,txt=l['txt']))
        d['bub']+=s.bx
        out.append(d)
    tags={}
    for l in lines:
        if l['ch'] in('NARRATOR','CLIPBOARD'):continue
        tags[l['i']]=REAL.get(l['i'],'Dramatized')
    def inp(P,x,y):
        c=False;n=len(P)
        for i in range(n):
            a,b=P[i],P[(i+1)%n]
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
        return c
    bad=0
    for s in SCN:
        P=s.d.get('floor')
        if not P:continue
        for a in s.actors:
            if a.d.get('veh') or a.d.get('nolint'):continue
            for q in a.d['pos']:
                if not inp(P,q[1],q[2]):
                    bad+=1;print('FLOOR',s.d['set'],s.start,a.d['id'],q[1],q[2])
    print('floor violations',bad)
    SFX.sort()
    return out,SFX,tags

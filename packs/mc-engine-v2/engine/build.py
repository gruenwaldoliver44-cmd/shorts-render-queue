import subprocess,json,numpy as np,sys,os,importlib
from scipy.signal import butter,lfilter
SR=44100;FPS=30
LN=json.load(open('lines.json'))
exec(open('audio_lib.py').read())
os.makedirs('work',exist_ok=True)
GAP={9:.9,14:.6,18:.6,23:.6,26:.3,27:.7,33:.6,36:.6,39:.5,40:1.2,44:.7,50:.4,53:.8,54:.4,56:.9}
PHONE={27}
CARD=1.7
lines=[];clips=[];t=.15;cur=0;cards=[]
for i,x in enumerate(LN):
    if x['ch']!=cur:
        cur=x['ch'];t+=.25
    p=f"v/{x['i']:03d}.mp3";N=x['sp']=='NARRATOR'
    y=norm(trim(rd(p,'atempo=1.10' if N else ('highpass=f=260,lowpass=f=5200,acompressor=threshold=-18dB:ratio=3' if x['i'] in PHONE else None))),-20);d=len(y)/SR;nx=LN[i+1] if i+1<len(LN) else None
    g=.14 if nx and nx['sp']==x['sp'] else .2
    if nx and nx['ch']!=x['ch']:g=.35
    g=GAP.get(x['i'],g)
    if nx is None:g=6
    f0=round(t*FPS);clips.append((t,y));t+=d+g
    e=env(y) if not N else []
    lines.append(dict(i=x['i'],ch=x['sp'],from_=f0,vf=round(d*FPS),dur=round(t*FPS)-f0,env=e,mx=max(e) if e else 1,txt=x['t']))
T=t;N=int(T*SR)+SR;mix=np.zeros(N)
def put(x,at,g=1.):
    i=int(at*SR)
    if i<0 or i>=N:return
    e=min(N,i+len(x));mix[i:e]+=x[:e-i]*g
for a,y in clips:put(y,a)
import spec
scenes,sfxs,tags=spec.run(lines,cards,round(T*FPS))
for l in lines:l['tag']=tags.get(l['i'])
_c={};used=0
def playsfx(n,at,g):
    global used
    if n=='pop':n='pop%d'%(used%4)
    if n not in _c and os.path.exists('sfx/'+n+'.wav'):_c[n]=norm(rd('sfx/'+n+'.wav'),-20)
    if n not in _c:
        _c[n]=norm(trim(rd('work/'+n+'.mp3')),-19) if n in('moo','moo2') else (norm(rd('../sfxk/'+SF[n]+'.mp3'),-20) if n in SF else norm(synth(n),-20 if n in('news','stampx','swipe','land','pin') or n.startswith('pop') else -23))
    put(_c[n],at,g*.5);used+=1
for f,n,g in sfxs:playsfx(n,f/FPS,g)
print('sfx',used)
exec(open('music.py').read())
tl=dict(dur=round(T*FPS),lines=[dict(ch=l['ch'],**{'from':l['from_']},vf=l['vf'],env=l['env'],mx=l['mx'],tag=l['tag']) for l in lines],scenes=scenes,glob=getattr(spec,'GLOB',[]))
json.dump(tl,open('src/timeline.json','w'),separators=(',',':'),ensure_ascii=False)
print(round(T,1),round(T/60,2),len(scenes))

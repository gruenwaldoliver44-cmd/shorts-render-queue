def rd(p,af=None):
    c=['ffmpeg','-v','error','-i',p]+(['-af',af] if af else [])+['-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(c,capture_output=True).stdout,'f4').copy()
def trim(x):
    w=int(.01*SR);e=np.array([np.sqrt((x[i:i+w]**2).mean()) for i in range(0,len(x)-w,w)]);idx=np.where(e>e.max()*.03)[0]
    a=max(0,idx[0]*w-int(.02*SR));b=min(len(x),(idx[-1]+1)*w+int(.08*SR));y=x[a:b].copy();f=int(.02*SR);y[-f:]*=np.linspace(1,0,f);return y
def norm(x,db):return x*10**(db/20)/(np.sqrt((x**2)[np.abs(x)>.01].mean())+1e-9)
def env(x):
    n=int(np.ceil(len(x)/SR*FPS));s=SR//FPS;return [round(float(np.sqrt((x[i*s:(i+1)*s]**2).mean())),4) if i*s<len(x) else 0 for i in range(n)]
rng=np.random.default_rng(3)
def lp(x,fc):b,a=butter(2,fc/(SR/2));return lfilter(b,a,x)
SF={'door':'doorClose_1','paper':'card-slide-2','coin':'handleCoins2','metal':'impactMetal_heavy_000','wood':'impactWood_heavy_000','soft':'impactSoft_heavy_001','drop':'drop_001','scratch':'scratch_001','pluck':'pluck_001','step':'footstep_concrete_000','bell':'impactBell_heavy_000','switch':'switch_002','err':'error_001','q':'question_001','glass':'impactGlass_heavy_001','punch':'impactPunch_heavy_000','latch':'metalLatch','plate':'impactPlate_heavy_001','up':'powerUp1','shovel':'impactMining_001'}

from scipy.signal import butter as _bt,lfilter as _lf
def _swoosh(d=.32,f0=260,f1=3200,bias=0):
    m=int(d*SR);x=rng.standard_normal(m);t=np.linspace(0,1,m);o=np.zeros(m);B=np.geomspace(f0,f1,6)
    for i,fc in enumerate(B):
        b,a_=_bt(2,[fc/1.45/(SR/2),min(.98,fc*1.45/(SR/2))],'band');y=_lf(b,a_,x);c=.22+.5*i/5+bias;o+=y*np.exp(-((t-c)/.2)**2)
    return o/np.abs(o).max()
def _kf(f,af=None,g=1):
    y=rd('/home/claude/ys/sfxk/pick/'+f+'.mp3',af);return y/(np.abs(y).max()+1e-6)*g
def _lay(*P):
    n=max(int(at*SR)+len(y) for y,at in P);o=np.zeros(n)
    for y,at in P:
        i=int(at*SR);o[i:i+len(y)]+=y
    return o/np.abs(o).max()
def _rate(k):return f'asetrate={int(44100*k)},aresample=44100'
def synth2(n):
    if n=='whoosh':return _swoosh(.34)
    if n=='news':return _lay((_swoosh(.34,300,3600)*.55,0),(_kf('card-fan-2',None,.8),.26),(_kf('impactSoft_heavy_001',None,.75),.29))
    if n.startswith('pop'):
        k=[1.0,1.12,.92,1.22][int(n[3:] or 0)];return _lay((_swoosh(.11,900,5000)*.28,0),(_kf('pluck_001',_rate(k),.9),.07),(_kf('impactSoft_heavy_003',_rate(1.3),.28),.07))
    if n=='stampx':return _lay((_kf('impactPunch_heavy_000',None,.9),0),(_kf('impactPlank_medium_002',None,.6),.005))
    if n=='swipe':return _lay((_swoosh(.26,350,2600)*.6,0),(_kf('card-slide-4',None,.7),.12))
    if n=='pin':return _lay((_kf('impactPlank_medium_000',_rate(1.25),.7),0),(_kf('switch_002',None,.5),.01))
    if n=='tick':return _kf('switch_002',_rate(1.4),.6)[:int(.05*SR)]
    if n=='land':return _lay((_swoosh(.2,200,1500)*.4,0),(_kf('impactSoft_heavy_001',None,.9),.16))
    if n=='water':
        d=4.;m=int(d*SR);tt=np.arange(m)/SR;x=lp(rng.standard_normal(m),1500)*(1+.35*np.sin(2*np.pi*.7*tt))
        for i in range(26):
            at=rng.uniform(0,d-.1);f=rng.uniform(300,800);q=int(.07*SR);b=np.sin(2*np.pi*(f+f*2*np.arange(q)/q)*np.arange(q)/SR)*np.hanning(q)*.5;j=int(at*SR);x[j:j+q]+=b
        return x*np.minimum(1,tt/.4)*np.minimum(1,(d-tt)/.6)
    return None

def thump(f=70,d=.3):
    n=int(d*SR);tt=np.arange(n)/SR;ff=f*(1+1.8*np.exp(-tt*22));return np.sin(2*np.pi*np.cumsum(ff)/SR)*np.exp(-tt*9)
def synth(n):
    _s=synth2(n)
    if _s is not None:return _s
    if n=='burp':
        d=.62;tt=np.arange(int(d*SR))/SR;f=118-46*tt/d+9*np.sin(2*np.pi*23*tt);w=2*((np.cumsum(f)/SR)%1)-1;return lp(w+.25*rng.standard_normal(len(tt)),900)*(.55+.45*np.sin(2*np.pi*27*tt))*np.minimum(1,tt/.03)*np.minimum(1,(d-tt)/.18)*1.0
    if n=='dig':
        d=.2;tt=np.arange(int(d*SR))/SR;return lp(rng.standard_normal(len(tt)),1300)*np.exp(-tt*20)*.9+thump(110,d)*.5
    if n=='whistle':
        d=1.5;tt=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*392*tt)+np.sin(2*np.pi*494*tt)+.7*np.sin(2*np.pi*587*tt))*np.minimum(1,tt/.08)*np.minimum(1,(d-tt)/.3)*.2
    if n=='bark':
        d=.16;tt=np.arange(int(d*SR))/SR;return lp(np.sign(np.sin(2*np.pi*(420-900*tt)*tt))+.5*rng.standard_normal(len(tt)),1800)*np.exp(-tt*14)*.7
    if n=='gull':
        d=.5;tt=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*np.cumsum(1500-900*tt+300*np.sin(2*np.pi*11*tt))/SR)*np.minimum(1,tt/.03)*np.minimum(1,(d-tt)/.12)*.3
    if n=='cluck':
        d=.11;tt=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*(780-1800*tt)*tt)*np.exp(-tt*26)*.6
    if n=='engine':
        d=2.4;tt=np.arange(int(d*SR))/SR;return lp(np.sign(np.sin(2*np.pi*34*tt))*(1+.4*np.sin(2*np.pi*7*tt)),420)*np.minimum(1,tt/.2)*np.minimum(1,(d-tt)/.5)*.5
    if n=='boing':
        d=.5;tt=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*np.cumsum(180+420*tt*(1+np.sin(2*np.pi*14*tt)*.3))/SR)*np.exp(-tt*5)*.5
    if n=='modem':
        d=1.6;tt=np.arange(int(d*SR))/SR;return (np.sin(2*np.pi*np.where(np.sin(2*np.pi*9*tt)>0,1200,2100)*tt)*.18+rng.standard_normal(len(tt))*.05)*np.minimum(1,(d-tt)/.2)
    if n=='crickets':
        d=2.2;tt=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*4300*tt)*(np.sin(2*np.pi*17*tt)>.2)*(np.sin(2*np.pi*2.4*tt)>-.1)*.18
    if n=='flat':
        d=1.6;tt=np.arange(int(d*SR))/SR;return np.sin(2*np.pi*980*tt)*np.minimum(1,tt/.02)*np.minimum(1,(d-tt)/.1)*.22
    if n=='fire':
        d=4;x=np.zeros(int(d*SR));ev=rng.integers(0,len(x)-400,120)
        for e in ev:x[e:e+300]+=rng.standard_normal(300)*np.exp(-np.arange(300)/60)*rng.random()
        return lp(x,3500)*.5+lp(rng.standard_normal(len(x)),400)*.1
    if n in('wind','wave'):
        d=3;x=lp(rng.standard_normal(int(d*SR)),500 if n=='wind' else 900);tt=np.arange(len(x))/SR;return x*np.sin(np.pi*tt/d)**2*1.5
    if n=='rain':
        d=4;x=lfilter([1,-.9],[1],rng.standard_normal(int(d*SR)));tt=np.arange(len(x))/SR;return x*np.minimum(1,tt/.4)*np.minimum(1,(d-tt)/.6)*.5
    if n=='static':
        d=2;return lfilter([1,-.95],[1],rng.standard_normal(int(d*SR)))*.3
    if n=='snap':
        d=.09;x=rng.standard_normal(int(d*SR));return x*np.exp(-np.arange(len(x))/SR*70)
    if n=='ring':
        tt=np.arange(int(1.1*SR))/SR;return (np.sin(2*np.pi*440*tt)+np.sin(2*np.pi*480*tt))*(np.sin(2*np.pi*20*tt)>0)*.3
    if n=='horn':
        tt=np.arange(int(1.2*SR))/SR;return (np.sign(np.sin(2*np.pi*110*tt))*.2+np.sign(np.sin(2*np.pi*138*tt))*.2)*np.minimum(1,tt/.05)*np.minimum(1,(1.2-tt)/.2)
    if n=='alarm':
        tt=np.arange(int(.9*SR))/SR;return np.sin(2*np.pi*(650+250*np.sin(2*np.pi*2*tt))*tt)*.3
    if n=='thunder':
        x=lp(rng.standard_normal(int(2.5*SR)),180);tt=np.arange(len(x))/SR;return x*np.exp(-tt*1.4)*2.5
    if n=='crowd':
        x=lp(rng.standard_normal(int(2.6*SR)),900)-lp(rng.standard_normal(int(2.6*SR)),250);tt=np.arange(len(x))/SR;return x*(.6+.4*np.sin(2*np.pi*3.1*tt))*np.minimum(1,tt/.3)*np.minimum(1,(2.6-tt)/.5)
    if n=='riser':
        d=1.8;tt=np.arange(int(d*SR))/SR;f=120*np.exp(tt*1.5);return (np.sin(2*np.pi*np.cumsum(f)/SR)*.5+lp(rng.standard_normal(len(tt)),2500)*.7)*(tt/d)**2
    if n=='whoosh':
        d=.3;m=int(d*SR);x=rng.standard_normal(m);return lp(x,2500)*np.sin(np.pi*np.linspace(0,1,m))**1.5
    if n=='pop':
        d=.07;m=int(d*SR);tt=np.arange(m)/SR;return np.sin(2*np.pi*(900-5000*tt)*tt)*np.exp(-tt*50)

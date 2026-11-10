FL=lambda y:[(-600,y),(2600,y),(2600,1500),(-600,1500)]
COOL='saturate(.85) brightness(.92) hue-rotate(-6deg)'
GRAY='saturate(.6) brightness(.97)'
DAY='saturate(1.05)'
WARM='saturate(1.12) sepia(.12)'
AMBER='saturate(1.15) sepia(.22) brightness(1.02)'
GOLDF='saturate(1.25) sepia(.28) brightness(1.05)'
EVE='saturate(.8) brightness(.78) sepia(.15)'
GASN=dict(set='s_gasn',depth=[650,230,1080,700],floor=FL(640))
GASD=dict(set='s_gasd',depth=[650,230,1080,700],floor=FL(640))
CAR=dict(set='s_car')
LOB=dict(set='s_lobby',depth=[650,230,1080,640],floor=FL(615),door=dict(x=1203,y=402,w=150,h=246,hinge='l'))
WIN=dict(set='s_window',fg='fg_window')
BRK=dict(set='s_break',depth=[700,330,1080,700],floor=FL(690))
LNG=dict(set='s_lounge',depth=[760,330,1080,620],floor=FL(750))
OFF=dict(set='s_office',depth=[760,430,1080,700],floor=FL(740))
STR=dict(set='s_street',depth=[760,280,1080,620],floor=FL(740))
TER=dict(set='s_terrace',depth=[820,420,1080,700],floor=FL(800))
DK=dict(set='#15171d');NAVY=dict(set='#1b2340');PPR=dict(set='#efe8dc');RD=dict(set='#7a1f14');GD=dict(set='#3a2a06')
LAB=['−$59','$300','$5K','$160K','$1M','$10M','$50M']
def fig(s,c,x,y,sp,ch=None,**k):
    return s.a(c,x,y,sp,ch=ch,**k)
def teller(s,c,x,sp,ch=None,h=1000,y=1150,**k):
    k.setdefault('shadow',False);return s.a(c,x,y,sp,ch=ch,h=h,nolint=1,**k)
def cust(s,c,x,sp,ch=None,flip=0,h=1180,y=1360,**k):
    k.setdefault('shadow',False);return s.a(c,x,y,sp,ch=ch,h=h,nolint=1,layer=1,flip=flip,**k)
def W_(t,z=1.0,cx=960,cy=540,filt=None,**k):
    s=S(t,WIN,z=z,cx=cx,cy=cy,**k)
    if filt:s.d['filter']=filt
    return s
def ladder(s,t,act,t1=None,build=None,prev=None):
    A=[[0,prev if prev is not None else act]]
    if prev is not None:A.append([R(t)+14,act])
    s.o('ladder',t,t1,act=A,lab=LAB,build=R(build) if build is not None else None,chip=0)
    if prev is not None:sfx('up',t,.5)
def emo(a,t,txt,dur=40,col='#fff',dx=0,snd='pop'):
    a.d.setdefault('emo',[]).append([R(t),txt,dur,col,dx])
    if snd:sfx(snd,t,.45)
    return a
def phone(s,t,t1=None,**k):
    s.o('phone',t,t1,**k);sfx('swipe',t,.6);return s
def screen(s,t,t1=None,**k):
    s.o('screen',t,t1,**k);sfx('swipe',t,.6);return s
def slam(s,t,txt,x=960,y=540,size=150,t1=None,**k):
    s.o('slam',t,t1,txt=txt,x=x,y=y,size=size,**k);sfx('punch',t,.7);s.shk_(t,14);return s

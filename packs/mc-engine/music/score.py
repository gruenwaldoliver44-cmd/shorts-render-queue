"""Vertont ein Video aus einer Cue-Liste mit echten Stuecken. Aufruf: python3 score.py <videoordner> <cues.json> <out.m4a>
cue: {"datei":..,"von":sek im Video,"bis":sek,"ab":sek im Stueck,"gain":dB,"ein":s,"aus":s}"""
import numpy as np,subprocess,json,sys
from scipy.signal import butter,sosfiltfilt
SR=44100
vid,cf,out=sys.argv[1:4]
T=json.load(open(vid+'/src/timeline.json'));TT=T['dur']/30;N=int(TT*SR)
v=np.load(vid+'/work/voice.npy');v=np.pad(v,(0,max(0,N-len(v))))[:N]
def rd(p,ss,dur):
    o=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-t',str(dur),'-i',p,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(o,'f4').astype(float).reshape(-1,2)
def glatt(x,w):
    return np.convolve(x,np.ones(w)/w,'same')
b=np.zeros((N,2));C=json.load(open(cf))
for c in C:
    n=int((c['bis']-c['von'])*SR);x=rd('lib/'+c['datei'],c['ab'],c['bis']-c['von']+1)
    assert len(x)>=n,(c['datei'],len(x)/SR,n)
    x=x[:n]
    # sanfte Angleichung: laute und leise Stellen des Stuecks halb ausgleichen, damit das Bett unter der Stimme ruhig bleibt
    m=x.mean(1);e=np.sqrt(glatt(m[::441]**2,300)+1e-9);e=np.interp(np.arange(n),np.arange(len(e))*441,e)
    x=x/(e[:,None]**.55);x=x/np.sqrt((x**2).mean())
    ein,aus=int(c.get('ein',1.2)*SR),int(c.get('aus',1.8)*SR)
    x[:ein]*=np.sin(np.linspace(0,np.pi/2,ein))[:,None]**2
    x[-aus:]*=np.cos(np.linspace(0,np.pi/2,aus))[:,None]**2
    a=int(c['von']*SR);b[a:a+n]+=x*10**(c.get('gain',0)/20)
# Stimme erkennen, tiefe und helle Musik unterschiedlich zuruecknehmen
vo=glatt(np.abs(v),int(.05*SR));ds=np.interp(np.arange(N),np.arange(0,N,441),(vo[::441]>.02).astype(float))
vor=int(.12*SR);ds=np.maximum(ds,np.roll(ds,-vor));ds=glatt(ds,int(.3*SR))
sos=butter(4,500,'low',fs=SR,output='sos');lo=sosfiltfilt(sos,b,axis=0);hi=b-lo
BED=float(C[0].get('bett',-30)) if False else -30
g=10**(BED/20)
lo*=(1-.55*ds)[:,None];hi*=(1-.80*ds)[:,None]   # tief -5 dB, hell -11 dB unter Sprache
bb=(lo+hi)*g
fe=int(2.5*SR);bb[-fe:]*=np.linspace(1,0,fe)[:,None]
m=np.stack([v,v],1)+bb
pk=np.abs(m).max();m=np.tanh(m/pk*1.1)/np.tanh(1.1)*.89
np.save('bett.npy',bb.astype('f4'))
subprocess.run(['ffmpeg','-y','-v','error','-f','s16le','-ar',str(SR),'-ac','2','-i','-','-af','volume=1.2dB,alimiter=limit=0.79:level=false','-c:a','aac','-b:a','224k',out],input=(m*32767).astype('i2').tobytes())
# Kontrolle
sp=ds>.8;print('Stimme rms',20*np.log10(np.sqrt((v[sp]**2).mean())),'Musik unter Stimme',20*np.log10(np.sqrt((bb[sp]**2).mean())),'Musik in Pausen',20*np.log10(np.sqrt((bb[~sp]**2).mean())))

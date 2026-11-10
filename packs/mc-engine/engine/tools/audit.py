# Prueft VOR dem Rendern: wo passiert waehrend gesprochen wird nichts Neues?
import json,sys
T=json.load(open('src/timeline.json'));L=json.load(open('lines.json'))
ev=set();D=T['dur']
def span(a,b,st=20):
    for f in range(int(a),int(b),st):ev.add(f)
for s in T['scenes']:
    ev.add(s['from'])
    for c in s['cam']:
        if len(c)>4 and c[4]>0 and c[4]<400 and abs(c[1]-1)>=0:
            pass
    for i,c in enumerate(s['cam']):
        if c[0]>=s['from'] and i%2==0:ev.add(c[0])
    for o in s['over']:
        ev.add(o['t'])
        if o.get('td'):span(o['t'],o['t']+o['td'])
        if o['k'] in('bills','confetti','stamps','rain','flick'):span(o['t'],o.get('t1',s['from']+s['dur']))
    for u in s.get('under',[]):
        if u['k'] in('belt','birds','steam','drip','cloud','crt','flick'):
            pass
    for a in s['actors']:
        for k in a['pos'][1:]:span(k[0],k[0]+k[3])
        for k in a['sp'][1:]:ev.add(k[0])
        for k in a.get('hop',[]):ev.add(k)
        for k in a.get('shk',[])+a.get('rock',[]):span(k[0],k[1])
        for q in('pop','drop','t0'):
            if a.get(q):ev.add(a[q])
    for b in s.get('bub',[]):ev.add(b['t'])
    if s.get('door'):
        for e in s['door']['ev']:ev.add(e[0])
ev=sorted(x for x in ev if x<D)
out=[]
for a,b in zip(ev,ev[1:]+[D]):
    if b-a>=int(float(sys.argv[1] if len(sys.argv)>1 else 2.2)*30):
        li=0
        for l,x in zip(T['lines'],L):
            if l['from']<=a:li=x['i']
        out.append((round(a/30,1),round((b-a)/30,1),li))
print(len(out),'Luecken',sum(x[1] for x in out),'s')
print(' '.join(f"{t}s+{d}(L{l})" for t,d,l in out))

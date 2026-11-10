import json
T=json.load(open('src/timeline.json'))
fr=[]
for s in T['scenes']:
    for p in (.12,.5,.88):fr.append(s['from']+int(s['dur']*p))
open('work/all.txt','w').write(' '.join(map(str,fr)))

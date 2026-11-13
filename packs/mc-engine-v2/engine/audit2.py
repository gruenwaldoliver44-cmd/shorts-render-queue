# Event audit incl. motion-graphics internals: where does nothing NEW happen on screen for > N seconds?
import json, sys
T = json.load(open('src/timeline.json')); D = T['dur']; ev = set()
def span(a, b, st=15):
    for f in range(int(a), int(b), st): ev.add(f)
def times(o):
    k = o.get('k'); t = o.get('t', 0); out = [t]
    for q in ('t1', 'at', 'fail', 'tw', 'wat', 'subAt'):
        if isinstance(o.get(q), (int, float)): out.append(o[q])
    for it in o.get('items', []) or []:
        if k == 'chips': out.append(it[1])
        elif k == 'icons': out += [x for x in (it[3], it[5], it[6]) if x]
        elif k == 'clocks': out += [x for x in it[4:6] if x]
        elif k == 'checks': out.append(it[1])
    for key in ('keys', 'count', 'sub', 'cam'):
        for q in o.get(key, []) or []: out.append(q[0])
    for q in o.get('arcs', []) or []: out.append(q[2]); span(q[2], q[2] + 30)
    for q in o.get('cities', []) or []: out += [x for x in q[1:3] if x]
    for q in (o.get('hot', []) or []) + (o.get('rings', []) or []): out.append(q[1])
    for q in o.get('rows', []) or []:
        if k == 'receipt': out.append(q[2])
        if k == 'score': out.append(q[3]); out += [c[1] for c in q[2] if c]
        if k == 'lines2': out.append(q[3]); span(q[3], q[3] + 40)
    for q in o.get('years', []) or []: out.append(q[2])
    for q in o.get('data', []) or []:
        if isinstance(q[1], list): out += [x[0] for x in q[1]]
        elif q[3]: out.append(q[3])
    if o.get('slash'): out.append(o['slash'][0])
    if o.get('lock'): out += [x for x in o['lock'] if x]
    if k == 'chart': span(t + o.get('delay', 6), t + o.get('delay', 6) + o.get('d', 50))
    if k == 'map':
        for q in o.get('cam', [])[1:]: span(q[0], q[0] + (q[3] if len(q) > 3 else 26))
    if k == 'count' or o.get('count'): span(o['count'][0][0], o['count'][-1][0] + o.get('cd', 30))
    if k in ('stack',): span(t + 8, t + 8 + o.get('d', 60))
    if k == 'flow': span(o.get('at', t + 10), o.get('at', t + 10) + o.get('d', 30))
    if k == 'flagrow' and o.get('spin'): span(*o['spin'])
    if k == 'term2': span(t + 10, o.get('fail', t))
    return [x for x in out if x is not None]
for s in T['scenes']:
    ev.add(s['from'])
    for c in s['cam']:
        if len(c) > 4 and 0 < c[4] < 400: span(c[0], c[0] + c[4], 20)
        ev.add(c[0])
    for o in s['over'] + s.get('wo', []):
        for x in times(o): ev.add(x)
    for u in s.get('under', []) + s.get('top', []):
        ev.add(u.get('t', 0))
        if u['k'] in ('belt', 'flick'): span(u['t'], u.get('t1', s['from'] + s['dur']))
    for a in s['actors']:
        for k in a['pos'][1:]: span(k[0], k[0] + k[3])
        for k in a['sp'][1:]: ev.add(k[0])
        for k in a.get('hop', []): ev.add(k)
        for k in a.get('shk', []) + a.get('rock', []): span(k[0], k[1])
    for b in s.get('bub', []): ev.add(b['t'])
    if s.get('door'):
        for e in s['door']['ev']: ev.add(e[0])
for g in T.get('glob', []): ev.add(g['t'])
for l in T['lines']:
    if l['ch'] != 'NARRATOR': span(l['from'], l['from'] + l['vf'], 20)  # talking mouths
ev = sorted(x for x in ev if isinstance(x, (int, float)) and 0 <= x < D)
th = float(sys.argv[1]) if len(sys.argv) > 1 else 3.5
gaps = [(a / 30, (b - a) / 30) for a, b in zip(ev, ev[1:] + [D]) if b - a >= th * 30]
print(len(gaps), 'gaps >', th, 's, total', round(sum(g[1] for g in gaps), 1))
print('  '.join(f'{a:.1f}+{d:.1f}' for a, d in gaps))

# ===== Weltkrise: "What If the AI Bubble Crashed the Whole World?" — direction =====
# Sets: depth=[y_far, h_far, y_near, h_near] (standing height by floor y). Doors: x,y,w,h (roll=open doorway clip, sh=shutter).
KIT = dict(set='s_kitchen2', fg='fg_kitchen', depth=[800, 465, 1080, 818], door=dict(x=88, y=64, w=228, h=876, hinge='r'))
DC = dict(set='s_dc', depth=[525, 112, 1050, 508], door=dict(x=1482, y=398, w=318, h=456, roll=1, ext=0))
TOK = dict(set='s_tokyo')
JEW = dict(set='s_jewel', fg='fg_jewel', depth=[905, 690, 1080, 780], door=dict(x=156, y=40, w=194, h=866, roll=1, ext=0))
BAK = dict(set='s_bakery', fg='fg_bakery', depth=[760, 580, 1080, 760], door=dict(x=1520, y=80, w=220, h=668, roll=1, ext=0))
SHIP = dict(set='s_ship', depth=[700, 290, 1000, 400])
OHIO = dict(set='s_ohio', depth=[665, 120, 1080, 600], door=dict(x=1003, y=395, w=300, h=270, roll=1, sh=[1003, 395, 300, 270], dark=1))
BANK = dict(set='s_bank', depth=[693, 350, 1080, 865], door=dict(x=953, y=167, w=347, h=526, dbl=1, max=70))
MKT = dict(set='s_market')
HOT = dict(set='s_hotel', depth=[600, 58, 1080, 560], door=dict(x=935, y=520, w=52, h=67, dbl=1))
MGB = dict(set='#mg')
NIGHT = 'saturate(.9) brightness(.82) hue-rotate(-8deg)'
DARK = 'saturate(.55) brightness(.42) hue-rotate(-10deg)'
CY = '#38E1FF'; AMB = '#FFB224'; RD_ = '#FF3D57'; GR = '#2FE6A0'; GD_ = '#F5C451'; TX = '#EEF2FF'; DIM = '#8C9AC4'
GLOB = []
WALK_R = ['yo_walkR1', 'yo_walkR2']; WALK_L = ['yo_wl1', 'yo_wl2', 'yo_wl3', 'yo_wl4']; WALK_F = ['yo_wf1', 'yo_wf2']

def ab(f): return {'abs': f}
def M(t, **k): return S(t, MGB, **k)
def mg(sc, k, t, t1=None, snd=None, g=.5, **kw):
    sc.o(k, t, t1, **kw)
    if snd: sfx(snd, t, g)
    return sc
def wo(s, k, t, t1=None, **kw):
    d = dict(k=k, t=R(t)); d.update(kw)
    if t1 is not None: d['t1'] = R(t1)
    s.d.setdefault('wo', []).append(d); return s
def tick(s, t, txt, sub=None, col=RD_, t1=None):
    mg(s, 'tick', t, t1 if t1 is not None else ab(R(t) + 170), 'scan', .45, txt=txt, sub=sub, col=col, size=40, x=70, y=84)
def chap(t0, t1, txt):  # small persistent chapter tag (red thread)
    GLOB.append(dict(k='tick', t=R(t0) + 175, t1=R(t1), txt=txt, size=20, x=40, y=22, col=RD_))
def hud(s, t, keys, t1=None, big=False, x=None, y=None, sub=None, lock=None, snd='digits', **k):
    K = [[R(a), v] for a, v in keys]
    d = dict(keys=K, big=big, sub=[[R(a), v] for a, v in (sub or [])], **k)
    if x is not None: d['x'] = x
    if y is not None: d['y'] = y
    if lock: d['lock'] = [R(lock[0]), R(lock[1]) if lock[1] is not None else None]
    mg(s, 'hud', t, t1, None, **d)
    for a, v in keys[1:]: sfx(snd, a, .45); sfx('blip_down' if v < 10000 else 'blip_up', a, .35)
    return s
def term(s, t, term_, def_, t1=None, **k): mg(s, 'term', t, t1, 'whoosh_short', .4, term=term_, def_=None, **k); s.over[-1]['def'] = def_
def icons(sc, t, items, t1=None, **k):
    it = [[a, b, c, R(d) if d is not None else None, e, R(f) if f is not None else None, R(o_) if o_ is not None else None] for a, b, c, d, e, f, o_ in items]
    mg(sc, 'icons', t, t1, None, items=it, **k)
    for q in it:
        if q[3] is not None: sfx('pop', ab(q[3]), .4)
        if q[6] is not None: sfx('blip_down', ab(q[6]), .4)
def chips(s, t, items, t1=None, **k):
    it = [[a, R(b), c] for a, b, c in items]; mg(s, 'chips', t, t1, None, items=it, **k)
    for q in it: sfx('pop', ab(q[1]), .4)
def stat(s, t, t1=None, snd='pop', **k): return mg(s, 'stat', t, t1, snd, .5, **k)
def tagl(s, t, txt, t1=None, snd='stamp', **k): return mg(s, 'tagl', t, t1, snd, .6, txt=txt, **k)
def mapw(s, t, cam, t1=None, cities=(), arcs=(), hot=(), rings=(), **k):
    C_ = [[R(a), c, z] + ([d] if d else []) for a, c, z, *dd in cam for d in [dd[0] if dd else None]]
    ci = [[c, R(a), R(h) if h is not None else None, sd] for c, a, h, sd in cities]
    ar = [[a, b, R(t_), col] for a, b, t_, col in arcs]
    ho = [[i, R(t_), col] for i, t_, col in hot]
    ri = [[c, R(t_), col] for c, t_, col in rings]
    mg(s, 'map', t, t1, None, cam=C_, cities=ci, arcs=ar, hot=ho, rings=ri, **k)
    for q in C_[1:]: sfx('whoosh', ab(q[0]), .45)
    for q in ci: sfx('pop', ab(q[1]), .35)
    for q in ar: sfx('swish', ab(q[2]), .3)
def say(s, t, t1, ch, txt, **k): s.say(t, t1, ch, txt, **k); sfx('pop2', t, .3)
def wipe(t, col=CY): GLOB.append(dict(k='wipe', t=R(t) - 7, d=14, col=col)); sfx('whoosh_short', ab(R(t) - 6), .35)
def glitch(t, d=8): GLOB.append(dict(k='glitch', t=R(t), d=d)); sfx('glitch', t, .45)

def direct():
    for i in range(1, 58): REAL[i] = 'Scenario · dramatized'
    # ================= HOOK · DAY 1 =================
    s = M(1)
    mapw(s, 1, [(1, [960, 600], 1.0), ((1, 'Tokyo'), 'tokyo', 1.7, 30), ((1, 'London'), 'london', 1.9, 30), ((1, 'New York'), 'ny', 1.9, 30), ((1, 'And by the end'), [960, 560], 1.05, 40)],
         cities=[('tokyo', (1, 'Tokyo'), None, 'r'), ('london', (1, 'London'), None, 'r'), ('ny', (1, 'New York'), (1, 'about to open', 10), 'l')],
         hot=[('840', (1, 'fall apart'), RD_), ('392', (1, 'fall apart', 6), RD_), ('826', (1, 'fall apart', 10), RD_), ('276', (1, 'fall apart', 14), RD_), ('156', (1, 'fall apart', 18), RD_), ('356', (1, 'fall apart', 22), RD_), ('076', (1, 'fall apart', 26), RD_), ('818', (1, 'fall apart', 30), RD_)],
         rings=[('sydney', (1, 'wakes up'), CY), ('mumbai', (1, 'wakes up', 8), CY), ('saopaulo', (1, 'wakes up', 16), CY), ('lagos', (1, 'normal', 0), CY), ('ny', (1, 'fall apart'), RD_), ('tokyo', (1, 'fall apart', 8), RD_), ('london', (1, 'fall apart', 14), RD_)])
    mg(s, 'clocks', (1, 'Tokyo'), None, None, x=110, y=40, items=[['TOKYO', 'jp', 23, 29, R((1, 'Tokyo')), R((1, 'about to open', 8))], ['LONDON', 'gb', 14, 29, R((1, 'London')), R((1, 'about to open', 8))], ['NEW YORK', 'us', 9, 29, R((1, 'New York')), R((1, 'about to open', 8))]])
    for w in ('Tokyo', 'London', 'New York'): sfx('tick', (1, w), .5)
    sfx('tick', (1, 'about to open', 8), .7); sfx('warn', (1, 'about to open', 9), .35)
    tick(s, 1, 'DAY 1 · MONDAY', 'THE AI BUBBLE POPS', t1=(1, 'Tokyo'))
    sfx('riser', (1, 'And by the end'), .4); sfx('impact', (1, 'fall apart'), .9); glitch((1, 'fall apart'), 10); s.shk_((1, 'fall apart'), 10)
    # 2: what you'll find out
    s = M(2)
    mapw(s, 2, [(2, [960, 560], 1.05), ((2, 'ruins'), [1100, 480], 1.25, 60)], hot=[(c, 2, RD_) for c in ('840', '392', '826', '276', '156', '356', '076', '818')],
         rings=[('frankfurt', (2, 'ruins'), RD_), ('cairo', (2, 'ruins', 10), RD_), ('tokyo', (2, 'ruins', 20), RD_)], t1=(2, "you'll"))
    s = M((2, "you'll"))
    mg(s, 'big', (2, "you'll"), (2, 'and one country'), 'blip_down', .5, txt='$ ?', size=260, pre='THE MONEY IN YOUR ACCOUNT', pulse=1, col=TX, y=330)
    glitch((2, 'worth anything'), 6)
    s = M((2, 'and one country'))
    icons(s, (2, 'and one country'), [('trophy', '', None, (2, 'and one country'), GD_, None, None)], s=320, y=200)
    mg(s, 'flagrow', (2, 'sitting on top'), None, None, flags=['us', 'cn', 'eu', 'jp', 'in', 'ru'], y=720, spin=[R((2, 'sitting on top')), R((2, 'Which country'))], q=R((2, 'Which country')))
    sfx('digits', (2, 'sitting on top'), .4); sfx('digits', (2, 'writing'), .4); sfx('lowboom', (2, 'Which country'), .6)
    mg(s, 'chips', (2, 'new rules'), None, None, items=[['NEW RULES · FOR EVERYONE ELSE', R((2, 'new rules')), GD_]], y=980)
    # 3: fiction vs real
    s = M(3); wipe(3)
    icons(s, 3, [('chip', 'CORVANE', None, 3, CY, None, None)], s=150, y=110, t1=(3, 'made up', 4))
    tagl(s, (3, 'made up'), 'CORVANE · A FICTIONAL COMPANY', size=58, y=330, col=AMB)
    chips(s, (3, 'every step'), [('1929', (3, 'really happened'), None), ('1931', (3, 'really happened', 5), None), ('2008', (3, 'really happened', 10), None), ('2022', (3, 'somewhere', 0), None), ('2023', (3, 'somewhere', 5), None), ('2024', (3, 'before', 0), None), ('2026', (3, 'this year'), AMB)], y=620, gap=230)
    mg(s, 'big', (3, 'every step'), None, None, txt='', pre='EVERY STEP AFTER IT · REAL', pcol=GR, ps=34, y=520)
    # 4: world on edge — three warnings, camera flies between panels
    s = M(4); wipe(4)
    mapw(s, (4, 'A war'), [((4, 'A war'), 'hormuz', 1.6), ((4, 'A war', 4), 'hormuz', 3.6, 45)], cities=[('hormuz', (4, 'Strait'), (4, 'Strait'), 'r')], hot=[('364', (4, 'Iran'), AMB)],
         rings=[('hormuz', (4, 'Strait'), AMB)], t1=(4, 'so filling'))
    tick(s, 4, 'BEFORE IT STARTS', 'THE WORLD IS ALREADY ON EDGE', col=AMB, t1=(4, 'A war'))
    icons(s, (4, 'tankers'), [('ship', 'TANKERS', 'BLOCKED', (4, 'tankers'), AMB, (4, 'out of'), (4, 'for months'))], s=150, x=560, y=620, xmark=1)
    s = M((4, 'so filling'), ocam=None)
    s.d['ocam'] = [[R((4, 'so filling')), 1, 960, 540], [R((4, 'Interest rates')), 1, 2880, 540, 26], [R((4, 'And tech')), 1, 4800, 540, 26], [R((4, 'And tech')) + 30, 1.0, 4800, 540, 200]]
    icons(s, (4, 'so filling'), [('pump', 'GAS', '↑ vs LAST WINTER', (4, 'so filling'), AMB, (4, 'costs more'), None)], s=300, x=960, y=280, ts=52)
    mg(s, 'gauge', (4, 'Interest rates'), None, None, x=2880 - 390, y=200, keys=[[R((4, 'Interest rates')), -80], [R((4, 'went up')), -20]], sub='FIRST RISE IN 3 YEARS', subAt=R((4, 'first time')))
    sfx('whoosh', (4, 'Interest rates'), .45); sfx('blip_up', (4, 'went up'), .5)
    icons(s, (4, 'every loan'), [('house', 'MORTGAGE', '↑', (4, 'every loan'), None, None, None), ('car', 'CAR LOAN', '↑', (4, 'every loan', 4), None, None, None), ('card', 'CARD', '↑', (4, 'every loan', 8), None, None, None)], s=110, x=2880 - 220, y=800, gap=220, ls=22, ts=40)
    sfx('whoosh', (4, 'And tech'), .45)
    stat(s, (4, 'And tech'), None, x=4800, y=250, center=1, w=1300, label='AI BORROWING · TECH COMPANIES · 2026 SO FAR', count=[[R((4, 'And tech')), 0], [R((4, 'billion')), 500]], cd=40, pre='~$', fmt='raw', suf='B', size=200, col=AMB, glow=1, sub='TO BUILD AI DATA CENTERS', subAt=R((4, 'data centers')))
    sfx('digits', (4, 'borrowed'), .5); sfx('digits', (4, 'hundred'), .5); sfx('slam', (4, 'billion', 30), .5)
    icons(s, (4, 'build AI'), [('chip', '', None, (4, 'build AI'), CY, None, None), ('chip', '', None, (4, 'build AI', 3), CY, None, None), ('chip', '', None, (4, 'build AI', 6), CY, None, None), ('chip', '', None, (4, 'build AI', 9), CY, None, None), ('chip', '', None, (4, 'build AI', 12), CY, None, None)], s=110, x=4800 - 340, y=760, gap=170)
    chap((4, 'so filling'), 10, 'DAY 1 · MONDAY')

    # ================= CORVANE (Virginia data center) =================
    s = S(5, DC, z=1.0); s.d['filter'] = 'saturate(1.05)'
    s.cam(5, 1.0, 960, 540, 0); s.cam((5, 'It owns'), 1.18, 960, 600, 140); s.cam((5, 'To buy'), 1.0, 960, 540, 24)
    s.u('blink', 5, n=90, y0=60, h=820, w=1900, xc=960, gap=520)
    sfx('hum', 5, .25); sfx('hum', (5, 'rents'), .22)
    te = s.a('te', 905, 560, 'te_cart', flip=0, ws=12); te.go((5, 'giant'), 1180, 760, R((5, 'To buy')) - R((5, 'giant')), 1)
    sfx('step', (5, 'giant'), .2, rep=8, gap=16)
    tw = s.a('tw', 640, 640, 'te_box', flip=1); tw.show((5, 'chips')); tw.go((5, 'chips'), 520, 700, 60, 1).p((5, 'rents'), 'te_hands').p((5, 'AI companies'), 'te_scratch')
    mg(s, 'tick', 5, (5, 'To buy'), 'scan', .4, txt='VIRGINIA · CORVANE DATA CENTER', sub='FICTIONAL', col=CY, size=30, x=70, y=84)
    icons(s, (5, 'AI chips'), [('chip', 'AI CHIP', None, (5, 'AI chips'), CY, None, None)], s=150, x=1640, y=120, t1=(5, 'To buy'))
    # scene inside a window + loan panel
    s = S((5, 'To buy'), DC, z=1.0); s.d['win'] = [80, 170, 1000, 562]; s.d['wlab'] = 'CORVANE · VIRGINIA'; s.d['wflag'] = 'us'
    s.cam((5, 'To buy'), 1.12, 1100, 640, 0); s.cam((5, 'To buy', 2), 1.0, 960, 560, 160)
    s.u('blink', (5, 'To buy'), n=90, y0=60, h=820, w=1900, xc=960, gap=520)
    te = s.a('te', 1180, 760, 'te_box', flip=0); te.go((5, 'promised'), 1360, 880, 50, 1)
    mg(s, 'stat', (5, 'twelve billion'), None, 'slam', .55, x=1180, y=250, label='LOAN · BORROWED BY CORVANE', val='$12B', size=150, col=TX)
    icons(s, (5, 'take the chips'), [('chip', 'THE CHIPS', None, (5, 'take the chips'), CY, None, None), ('bank', 'LENDERS', None, (5, 'take the chips', 8), AMB, None, None)], s=130, x=1300, y=560, gap=330, arrows=1, ls=24)
    term(s, (5, 'stopped paying'), 'COLLATERAL', 'What the lender can take if you stop paying.', x=1150, y=870, w=680, t1=None)

    # 6: the payment fails
    s = M(6); wipe(6)
    mg(s, 'term2', 6, (6, 'Its biggest'), None, fail=R((6, 'fails to arrive')), load=R((6, 'fails')) - R(6), stop=.74, time='MON 10:17', amt='$400,000,000', y=260)
    sfx('scan', 6, .45); sfx('err', (6, 'fails to arrive'), .7); sfx('slam', (6, 'fails to arrive'), .5); s.shk_((6, 'fails to arrive'), 8)
    s = M((6, 'Its biggest'))
    mg(s, 'stat', (6, 'Its biggest'), None, 'whoosh_short', .4, x=960, y=300, center=1, w=1400, label="CORVANE'S BIGGEST CUSTOMER · AN AI LAB", val='PROFIT EVER: $0', size=120, col=TX, sub='', ls=28)
    mg(s, 'tagl', (6, 'stopped paying'), None, 'stamp', .6, txt='BILLS UNPAID SINCE FRIDAY', y=700, col=RD_, size=56, rot=-3)
    s.shk_((6, 'stopped paying'), 8)

    # 7: lenders come for the chips
    s = S(7, DC, z=1.0); s.cam(7, 1.0, 960, 540, 0); s.cam((7, "that's when"), 1.1, 1100, 560, 60)
    s.u('blink', 7, n=90, y0=60, h=820, w=1900, xc=960, gap=520)
    la = s.a('la', 1880, 830, 'ld_aR1', flip=1, layer='door', lt=(7, 'lenders', 40)); la.go(7, 1400, 900, 60, 0)
    lb = s.a('lb', 1960, 800, 'ld_bR1', flip=1, layer='door', walk=['ld_bR1', 'ld_bR2'], ws=8, lt=(7, 'lenders', 50)); lb.go((7, 0, 10), 1250, 820, 64, 0).p((7, 'finds out'), 'ld_bstick').f((7, 'finds out'), 1)
    lc = s.a('lc', 2040, 860, 'ld_cR1', flip=1, layer='door', walk=['ld_cR1', 'ld_cw'], ws=9, lt=(7, 'lenders', 58)); lc.go((7, 0, 20), 1560, 980, 66, 0).p((7, 'really worth'), 'ld_ccross')
    la.p((7, 'finds out'), 'ld_aread')
    for t_ in (7, (7, 0, 10), (7, 0, 20)): sfx('step', t_, .2, rep=5, gap=13)
    wo(s, 'pic', (7, 'finds out', 6), None, n='pp_sticker', x=1172, y=515, h=34, rot=-8)
    sfx('sticker', (7, 'finds out', 4), .6)
    s = S((7, 'On paper'), DC, z=1.6); s.cam((7, 'On paper'), 1.6, 1050, 470, 0); s.cam((7, 'On paper', 2), 1.9, 1080, 470, 120)
    s.u('blink', (7, 'On paper'), n=90, y0=60, h=820, w=1900, xc=960, gap=520)
    lb = s.a('lb', 1250, 820, 'ld_bpress', flip=1)
    wo(s, 'pic', (7, 'On paper'), None, n='pp_sticker', x=1172, y=515, h=34, rot=-8)
    mg(s, 'stat', (7, 'forty'), None, 'pop', .5, x=700, y=200, label='VALUE PER CHIP · ON PAPER', val='$40,000', size=130, col=TX, slash=[R((7, 'maybe five')), '$5,000', 'FIRE SALE · EVERY LENDER SELLING'])
    sfx('slam', (7, 'maybe five'), .7); sfx('whoosh_down', (7, 'maybe five', 4), .4); s.shk_((7, 'maybe five'), 8)

    # 8: it reaches you
    s = M(8); wipe(8)
    mg(s, 'spbar', (8, "America's"), (8, 'Say your job'), None, y=200, red=R((8, 'third')), pct=36, txt='7 GIANTS · 1/3+')
    sfx('swish', (8, "America's"), .4); sfx('blip_down', (8, 'third'), .45)
    icons(s, (8, 'millions'), [('chip', '', None, (8, 'millions'), CY, None, None), ('chip', '', None, (8, 'millions', 3), CY, None, None), ('chip', '', None, (8, 'millions', 6), CY, None, None)], s=90, x=1560, y=80, gap=110, t1=(8, 'Say your job'))
    term(s, (8, 'the list'), 'S&P 500', "The 500 biggest US companies. Most retirement funds own a slice of all of them.", x=120, y=620, w=760, t1=(8, 'Say your job'))
    icons(s, (8, 'retirement'), [('job', 'YOU', None, (8, 'retirement'), TX, None, None), ('stocks', 'YOUR FUND', None, (8, 'retirement', 6), CY, None, None)], s=150, x=1300, y=600, gap=330, arrows=1, t1=(8, 'Say your job'))
    s = S((8, 'Say your job'), KIT, z=1.0); s.cam((8, 'Say your job'), 1.0, 960, 540, 0); s.cam((8, 'You open'), 1.25, 980, 520, 30); s.cam((8, 'By Friday'), 1.45, 990, 500, 24)
    s.door((8, 'Say your job'), 1, 14)
    yo = s.a('yo', 210, 940, 'yo_walkR1', ch=None, layer='door', lt=(8, 'Say your job', 24), walk=WALK_R, ws=8)
    yo.go((8, 'Say your job', 8), 560, 890, 46).go((8, 'Say your job', 54), 930, 900, 30, 1).p((8, 'Say your job', 84), 'yo_sitdn').p((8, 'Say your job', 96), 'yo_eat')
    s.door((8, 'Say your job', 40), 0, 14)
    hud(s, (8, 'ten thousand'), [((8, 'ten thousand'), 10000), ((8, 'nine thousand'), 9100), ((8, 'By Friday'), 8000)], x=1380, y=60,
        sub=[((8, 'ten thousand'), 'MON 09:00'), ((8, 'at lunch'), 'MON 12:10'), ((8, 'By Friday'), 'FRI 16:00')])
    yo.p((8, 'You open'), 'yo_shock').p((8, 'By Friday'), 'yo_head')
    sfx('vibrate', (8, 'You open'), .5)
    s.u('sweat', (8, 'By Friday', 6), x=1000, y=470, s=.9, t1=9)
    # 9: remember that number (open loop)
    s = M(9); s.d['ocam'] = [[R(9), 1.0, 960, 540], [R(9) + 1, 1.0, 960, 540], [R((9, 'almost')), 1.08, 960, 520, R((9, 'almost')) - R(9)]]
    hud(s, 9, [(9, 8000)], big=True, x=530, y=210, now=1, lock=[(9, 'Remember', 8), None], sub=[(9, 'FROZEN HERE')], snd='tick', pulse=[R(9), R((9, 'In a few'))])
    sfx('lock', (9, 'Remember', 8), .7); sfx('heart', (9, 'number'), .7); sfx('heart', (9, 'tempted'), .55)
    icons(s, (9, 'almost everybody'), [('job', '', None, (9, 'almost everybody', i * 3), TX, None, (9, 'does it', i * 2) if i < 4 else None) for i in range(5)], s=90, y=760, gap=150)
    chap(10, 15, 'DAY 2 · TOKYO')

    # ================= DAY 2 · TOKYO =================
    s = M(10); wipe(10)
    tick(s, 10, 'DAY 2 · TUESDAY', 'TOKYO')
    mapw(s, 10, [(10, 'ny', 1.6), ((10, 'detour'), [1500, 450], 1.5, 34)], cities=[('ny', 10, 10, 'l'), ('tokyo', (10, 'Tokyo'), (10, 'Tokyo', 6), 'r')], arcs=[('ny', 'tokyo', (10, 'detour'), RD_)], hot=[('840', 10, RD_), ('392', (10, 'Tokyo'), RD_)])
    icons(s, (10, 'car loan'), [('car', 'YOUR CAR LOAN', None, (10, 'car loan'), AMB, None, None)], s=170, x=1580, y=640)
    s = M(11)
    term(s, (11, 'Japan'), 'YEN', "Japan's money.", x=110, y=820, w=420, t1=(11, 'Now'))
    icons(s, 11, [('sack', 'YEN LOAN', '~0%', (11, 0, 6), GR, (11, 'almost nothing'), (11, 'paid back')), ('dollar', 'SWAP', None, (11, 'used it'), TX, None, (11, 'paid back', 4)),
                               ('stocks', 'US STOCKS', None, (11, 'American stocks'), CY, None, (11, 'falling'))], s=190, y=300, gap=480, arrows=1, xmark=0)
    tagl(s, (11, 'same exit'), 'EVERYONE → EXIT', y=820, col=RD_, size=60)
    glitch((11, 'falling'), 6); s.shk_((11, 'same exit'), 10)
    # 12: trader
    s = S(12, TOK, z=1.0); s.d['filter'] = 'saturate(1.08)'; s.cam(12, 1.0, 960, 540, 0); s.cam((12, 'So is'), 1.12, 960, 520, 40); s.cam((12, "who's"), 1.3, 960, 470, 30)
    co = s.a('co', 330, 900, 'tr_coll', h=520, shadow=False, nolint=1)
    cw = s.a('cw', 1660, 930, 'tr_woman', h=560, shadow=False, nolint=1, flip=1)
    tr = s.a('tr', 960, 1150, 'tr_type', ch='TRADER', h=900, shadow=False, nolint=1)
    dk = s.a('dk', 960, 1180, 'pp_desk', h=380, still=1, shadow=False, nolint=1)
    tr.p((12, 'So is'), 'tr_turn').p((12, "who's"), 'tr_hands')
    sfx('keys', 12, .5); sfx('keys', (12, 'to pay'), .45); sfx('slam', (12, 'So is', -4), .4)
    say(s, (12, "who's", -6), (12, 0, R((12, "who's")) - R(12) + 60), 'TRADER', "So who's buying?")
    mg(s, 'tick', 12, (12, 'So is'), None, txt='TOKYO · TRADING FLOOR · 23:40', col=RD_, size=26, x=70, y=84)
    # 13: nobody — real chart
    s = S(13, TOK, z=1.3); s.cam(13, 1.3, 960, 470, 0); s.cam((13, 'On August'), 1.0, 960, 540, 14)
    tr = s.a('tr', 960, 1150, 'tr_hands', ch=None, h=900, shadow=False, nolint=1)
    dk = s.a('dk', 960, 1180, 'pp_desk', h=380, still=1, shadow=False, nolint=1)
    s = M((13, 'On August')); wipe((13, 'On August'))
    mg(s, 'chart', (13, 'On August'), None, None, title='JAPAN · NIKKEI 225 · DAILY CLOSE', pts=[['JUL 31', 39102], ['AUG 1', 38126], ['AUG 2', 35909], ['AUG 5', 31458], ['AUG 6', 34675]], lo=30000, hi=40000, d=R((13, 'twelve')) - R((13, 'On August')), delay=4,
       marks=[[3, 'AUG 5, 2024 · −12.4%', RD_, 'r']], xl=[[0, 'JUL 31'], [1, 'AUG 1'], [2, 'AUG 2'], [3, 'AUG 5'], [4, 'AUG 6']], live=1, fmt='{}', x=230, y=250, w=1450, h=560)
    sfx('digits', (13, 'On August'), .4); sfx('impact', (13, 'twelve'), .7); s.shk_((13, 'twelve'), 8)
    # 14: IOUs -> your loans
    s = M(14); wipe(14)
    s.d['ocam'] = [[R(14), 1, 960, 540], [R((14, 'When lots')), 1, 2880, 540, 28], [R((14, 'Japan sold')), 1, 4800, 540, 28], [R((14, 'In our crash')), 1, 6720, 540, 28], [R((14, 'In our crash')) + 30, 1.0, 6720, 540, 300]]
    mg(s, 'chips', (14, 'Japan owns'), None, None, items=[['JAPAN · NO.1 FOREIGN OWNER', R((14, 'Japan owns')), CY]], x=960, y=250)
    mg(s, 'flagrow', 14, (14, 'When lots'), None, flags=['jp'], x=380, y=480)
    icons(s, (14, 'IOUs'), [('paycheck', 'US IOUs', None, (14, 'IOUs'), CY, None, None), ('paycheck', '', None, (14, 'IOUs', 4), CY, None, None), ('paycheck', '', None, (14, 'IOUs', 8), CY, None, None)], s=160, x=760, y=400, gap=200)
    term(s, (14, 'any other'), 'IOU = GOVERNMENT BOND', 'A piece of paper that says: America owes you this money, plus interest.', x=180, y=760, w=820)
    mg(s, 'flow', (14, 'they sell'), None, 'whoosh', .45, at=R((14, 'they sell')), d=30, frm=None, ic='paycheck', col=CY, s=110, lab='SOLD', ends=[['bank', 'MARKET', 1520, 560, TX]])
    s.over[-1]['from'] = [1160, 460]; s.over[-1]['to'] = [1500, 480]
    mg(s, 'gauge', (14, 'When lots'), None, None, x=2880 - 390, y=200, keys=[[R((14, 'When lots')), -60], [R((14, 'higher interest')), 30]], label='US INTEREST RATES', sub='TO KEEP BORROWING', subAt=R((14, 'keep borrowing')))
    sfx('blip_up', (14, 'higher interest'), .5)
    icons(s, (14, 'spreads'), [('house', '', None, (14, 'spreads'), None, None, None), ('car', '', None, (14, 'spreads', 4), None, None, None), ('card', '', None, (14, 'spreads', 8), None, None, None)], s=100, x=2880 - 200, y=800, gap=200)
    mg(s, 'stat', (14, 'Japan sold'), None, 'slam', .5, x=4800, y=260, center=1, w=1400, label='JAPAN SOLD · JAN–MAR 2026', count=[[R((14, 'Japan sold')), 0], [R((14, 'thirty billion')), 30]], cd=30, fmt='raw', pre='~$', suf='B', size=190, col=CY, sub='US RATES WENT UP', subAt=R((14, 'rates went up')))
    sfx('digits', (14, 'thirty'), .45)
    mg(s, 'gauge', (14, 'rates went up'), None, None, x=4800 - 300, y=560, keys=[[R((14, 'rates went up')), -40], [R((14, 'rates went up', 8)), 10]], label='', sub='')
    sfx('blip_up', (14, 'rates went up'), .5)
    mg(s, 'chips', (14, 'In our crash'), None, None, items=[['OUR CRASH · MANY TIMES THAT', R((14, 'In our crash')), RD_]], x=6720, y=170)
    icons(s, (14, 'your mortgage'), [('house', 'MORTGAGE', '↑', (14, 'your mortgage'), AMB, None, None), ('car', 'CAR LOAN', '↑', (14, 'car loan'), AMB, None, None), ('card', 'CREDIT CARD', '↑', (14, 'credit card'), AMB, None, None)], s=200, x=6720 - 360, y=330, gap=360)
    hud(s, (14, 'same week'), [((14, 'same week'), 8000)], x=6720 + 520, y=780, now=1, snd='tick')
    chap(15, 19, 'DAY 3 · MUMBAI')

    # ================= DAY 3 · MUMBAI =================
    s = M(15); wipe(15, GD_)
    tick(s, 15, 'DAY 3 · WEDNESDAY', 'MUMBAI', col=GD_)
    mg(s, 'flow', 15, None, None, at=R((15, 'starts falling')), d=26, frm=None, ic='gold', col=GD_, s=230, lab='SAFE?', arc=-40)
    s.over[-1]['from'] = [960, 430]; s.over[-1]['to'] = [960, 760]
    sfx('whoosh_down', (15, 'starts falling'), .5); sfx('thud', (15, 'starts falling', 24), .5)
    s = S(16, JEW, z=1.0); s.d['filter'] = 'saturate(1.08)'; s.cam(16, 1.0, 960, 540, 0); s.cam((16, 'bring their'), 1.12, 1040, 560, 60); s.cam((16, 'They expect'), 1.22, 1120, 540, 50)
    mg(s, 'tick', 16, (16, 'families'), 'scan', .4, txt='MUMBAI · INDIA', sub='GOLD MARKET', col=GD_, size=30, x=70, y=84)
    jw = s.a('jw', 1760, 890, 'jw_talk', ch='JEWELER', h=640, shadow=False, nolint=1, flip=1)
    cu = s.a('cu', 250, 900, 'cu2_walk', layer='door', lt=(16, 'families', 20), walk=None, ws=10)
    cu.go((16, 'families'), 640, 1000, 50, 1).p((16, 'jeweler'), 'cu2_sad').p((16, 'They expect'), 'cu2_walk')
    sfx('doorbell', (16, 'families'), .5); sfx('step', (16, 'families'), .22, rep=4, gap=13)
    cu.p((16, 'bring their', -10), 'cu2_walk')
    wo(s, 'pic', (16, 'gold to'), None, n='pp_chain', x=850, y=528, h=46, rot=-10)
    sfx('coins', (16, 'gold to'), .5)
    jw.p((16, 'great price'), 'jw_scale'); sfx('coin', (16, 'great price', 6), .4)
    wo(s, 'chart', (16, 'They expect'), None, tv=1, pts=[[0, 4280], [1, 4260], [2, 4270], [3, 4240]], lo=3900, hi=4350, d=60, x=1150, y=120, w=480, h=250, col=GD_, live=1, fmt='GOLD ${}', lsz=34)
    # 17: jeweler speaks, the TV drops twice
    s = S(17, JEW, z=1.25); s.cam(17, 1.25, 1160, 520, 0); s.cam((17, 'The world'), 1.12, 1100, 470, 30); s.cam((17, 'Twice'), 1.35, 1180, 430, 20)
    jw = s.a('jw', 1760, 890, 'jw_talk', ch='JEWELER', h=640, shadow=False, nolint=1, flip=1); jw.p((17, 'The world'), 'jw_point').p((17, 'Twice', 20), 'jw_talk')
    cu = s.a('cu', 640, 1000, 'cu2_walk'); cu.p((17, 'Twice'), 'cu2_shock').p((17, 'since', 10), 'cu2_sad')
    wo(s, 'pic', 17, None, n='pp_chain', x=850, y=528, h=46, rot=-10)
    wo(s, 'chart', 17, None, tv=1, pts=[[0, 4280], [1, 4240], [2, 4150], [3, 4080], [4, 3960]], lo=3900, hi=4350, d=R((17, 'since')) - R(17), delay=0, lin=1, x=1150, y=120, w=480, h=250, col=RD_, live=1, fmt='GOLD ${}', lsz=34)
    sfx('blip_down', (17, 'Twice'), .5); sfx('blip_down', (17, 'since'), .5)
    say(s, (17, 'Twice', -4), (17, 0, R((17, 'Twice')) - R(17) + 70), 'JEWELER', 'Twice, since you walked in.', side=-1)
    # 18: why gold falls
    s = M(18); wipe(18, GD_)
    icons(s, 18, [('stocks', 'STOCKS FALL', None, (18, 'big investors'), RD_, None, None), ('card', 'LOANS DUE', 'TODAY', (18, 'pay those'), AMB, (18, 'today'), None),
                  ('gold', 'SELL GOLD', None, (18, 'gold is the'), GD_, None, None), ('dollar', 'CASH', None, (18, 'into cash'), GR, None, None)], s=170, y=330, gap=420, arrows=1, t1=(18, 'It happened'))
    s = M((18, 'It happened'))
    mg(s, 'chart', (18, 'It happened'), None, None, title='GOLD · US$ PER OUNCE · 2026', pts=[['JAN', 5589], ['OCT', 3960]], lo=3500, hi=5800, d=R((18, 'almost thirty')) - R((18, 'It happened')), delay=6,
       marks=[[0, 'JAN · RECORD $5,589', GD_, 'r'], [1, 'OCT · BELOW $4,000 · −29%', RD_, 'l']], xl=[[0, 'JAN 2026'], [1, 'OCT 2026']], x=300, y=280, w=1300, h=520, col=RD_)
    sfx('blip_down', (18, 'gold dropped'), .5); sfx('slam', (18, 'almost thirty'), .5)
    icons(s, (18, 'So if'), [('gold', 'YOUR EMERGENCY PLAN', '↓ THE WEEK YOU NEED IT', (18, 'So if'), GD_, (18, 'very week'), None)], s=150, x=1500, y=60, ts=30, ls=22)
    chap(19, 24, 'WEEK 1 · CAIRO')

    # ================= WEEK 1 · DOLLARS · CAIRO =================
    s = M(19); wipe(19, GR)
    tick(s, 19, 'END OF WEEK 1', 'EVERYONE WANTS DOLLARS', col=GR)
    mg(s, 'converge', (19, 'spreads'), None, 'riser', .3, flags=['eu', 'jp', 'in', 'eg', 'cn', 'gb', 'br', 'mx', 'kr', 'au'])
    s = M(20)
    mg(s, 'seesaw', 20, (20, 'And because'), None, keys=[[R(20), 0], [R((20, 'runs into')), -9], [R((20, 'stronger')), -14]], y=600, lab='THE DOLLAR GETS STRONGER, THE OTHERS WEAKER')
    sfx('whoosh_down', (20, 'runs into'), .4); sfx('thud', (20, 'stronger'), .5)
    s = M((20, 'And because'))
    icons(s, (20, 'oil'), [('oil', 'OIL', 'PRICED IN $', (20, 'oil'), TX, (20, 'paid for'), None), ('wheat', 'WHEAT', 'PRICED IN $', (20, 'wheat'), TX, (20, 'paid for'), None)], s=180, x=600, y=250, gap=380)
    icons(s, (20, 'your gas'), [('pump', 'YOUR GAS', '↑', (20, 'your gas'), AMB, (20, 'cost more'), None), ('cart', 'YOUR GROCERIES', '↑', (20, 'groceries'), AMB, (20, 'cost more'), None)], s=180, x=1300, y=250, gap=380)
    mg(s, 'chips', (20, 'outside America'), None, None, items=[['IF YOU LIVE OUTSIDE THE US', R((20, 'outside America')), AMB]], y=760)
    s = M(21)
    mapw(s, 21, [(21, [1100, 500], 1.4), ((21, 'Cairo'), 'cairo', 3.0, 26)], cities=[('cairo', (21, 'Cairo'), (21, 'Cairo', 4), 'r')], hot=[('818', (21, 'Cairo'), AMB)])
    icons(s, (21, 'wheat buyers'), [('wheat', 'EGYPT · A TOP WHEAT IMPORTER', None, (21, 'wheat buyers'), AMB, None, None)], s=160, x=1450, y=640, ls=24)
    # 22: baker
    s = S(22, BAK, z=1.0); s.d['filter'] = 'saturate(1.1) sepia(.08)'; s.cam(22, 1.0, 960, 540, 0); s.cam((22, 'Today'), 1.2, 820, 480, 26); s.cam((22, 'My customers'), 1.05, 960, 520, 26)
    mg(s, 'tick', 22, (22, 'Today'), None, txt='CAIRO · EGYPT', sub='BAKERY', col=AMB, size=28, x=70, y=84)
    bk = s.a('bk', 520, 860, 'bk_wipe', ch='BAKER', flip=0); bk.p((22, 'Today', -8), 'bk_write').p((22, 'My customers'), 'bk_turn').p((22, 'getting rich'), 'bk_arms')
    wo(s, 'chalk', 22, None, txt='FLOUR\n900 E£', x=740, y=310, size=74, wipe=R((22, 'Today', -12)))
    wo(s, 'chalk', (22, 'Today'), None, txt='FLOUR\n1,100 E£', x=740, y=310, size=74, d=26)
    sfx('wipe', (22, 'Today', -14), .5); sfx('chalk', (22, 'Today'), .55)
    cu = s.a('cu', 1500, 1060, 'bkcu_shake', flip=1); cu.p((22, 'getting rich', 10), 'bkcu_leave').go((22, 'getting rich', 14), 2150, 1070, 60, 0)
    cu.d['rock'] = [[R((22, 'My customers')), R((22, 'getting rich')), 2.2]]
    say(s, (22, 'My customers'), (22, 1.0, 20), 'BAKER', "My customers think I'm the one getting rich.", side=1)
    # 23: 2011, then a calendar invite
    s = M(23); wipe(23)
    mg(s, 'chips', 23, None, None, items=[['JAN 25, 2011', R((23, 'In 2011')), AMB], ['→', R((23, 'eighteen')), DIM], ['FEB 11, 2011', R((23, 'president was gone')), RD_]], y=300, gap=420)
    stat(s, (23, 'eighteen'), None, x=960, y=420, center=1, w=900, label='EGYPT', val='18 DAYS', size=170, col=TX)
    icons(s, 23, [('bread', 'FOOD PRICES', '↑', (23, 0, 8), AMB, None, None), ('people', 'STREETS', None, (23, 'into the streets'), RD_, None, None)], s=130, x=760, y=720, gap=400, arrows=1)
    s = S((23, 'In America'), KIT, z=1.15); s.cam((23, 'In America'), 1.15, 1300, 520, 0); s.cam((23, 'calendar'), 1.35, 1380, 480, 30)
    yo = s.a('yo', 1480, 985, 'yo_stand'); yo.p((23, 'different way'), 'yo_phone').p((23, 'calendar'), 'yo_frown')
    sfx('notify', (23, 'calendar'), .6); sfx('vibrate', (23, 'calendar'), .4)
    mg(s, 'stat', (23, 'calendar'), None, None, x=170, y=280, label='CALENDAR INVITE', val='Quick sync', size=96, col=TX, sub='15 min · Friday · from: HR', ss=34, panel=1)
    chap(24, 28, 'WEEK 3 · SHANGHAI')

    # ================= WEEK 3 · SHANGHAI · OHIO =================
    s = M(24); wipe(24)
    tick(s, 24, 'WEEK 3', 'SHANGHAI')
    mapw(s, 24, [(24, [1400, 520], 1.6), ((24, 'Shanghai'), 'shanghai', 3.2, 30)], cities=[('shanghai', (24, 'Shanghai'), (24, 'stop ordering'), 'r')], hot=[('156', (24, 'Shanghai'), RD_)],
         arcs=[('shanghai', 'ny', (24, 'factories'), GR), ('shanghai', 'frankfurt', (24, 'factories', 8), GR), ('shanghai', 'saopaulo', (24, 'factories', 14), GR)], rings=[('shanghai', (24, 'stop ordering'), RD_)], t1=(24, 'goes quiet'))
    icons(s, (24, 'factories'), [('factory', 'MADE IN CHINA', None, (24, 'factories'), TX, None, (24, 'stop ordering'))], s=150, x=430, y=650, xmark=1)
    s = S((24, 'goes quiet'), SHIP, z=1.0); s.d['filter'] = 'saturate(.85) brightness(.97)'; s.cam((24, 'goes quiet'), 1.0, 960, 540, 0); s.cam((24, 'goes quiet', 2), 1.12, 960, 560, 160)
    sfx('horn', (24, 'goes quiet'), .4)
    s.u('birds', (24, 'goes quiet'), n=4, y=180, per=420)
    s.a('sa', 860, 790, 'sl_b2'); s.a('sb', 1090, 790, 'sl_a2', flip=1)
    # 25: captain
    s = S(25, SHIP, z=1.25); s.d['filter'] = 'saturate(.88)'; s.cam(25, 1.25, 960, 600, 0); s.cam((25, 'card tournament'), 1.4, 960, 620, 30)
    cp = s.a('cp', 845, 800, 'cp_cards', ch='CAPTAIN'); cp.p((25, 'card tournament'), 'cp_laugh').p((25, 1.0, 6), 'cp_throw')
    sa = s.a('sa', 1105, 790, 'sl_a', flip=1); sa.p((25, 'card tournament', 8), 'sl_a2')
    sb = s.a('sb', 1010, 860, 'sl_b'); sb.p((25, 'empty'), 'sl_b2')
    sfx('cards', 25, .5); sfx('cards', (25, 'card tournament'), .5)
    mg(s, 'tick', 25, None, None, txt='DAY 18 AT ANCHOR', sub='SHANGHAI', col=AMB, size=30, x=1150, y=70)
    say(s, (25, 'card tournament', -10), (25, 1.0, 16), 'CAPTAIN', 'My crew has started a card tournament.', side=-1)
    # 26: chain reaction -> Ohio -> 9 million jobs
    s = M(26); wipe(26)
    icons(s, 26, [('ship', 'SHIPS', None, 26, CY, None, (26, 'Fewer ships')), ('truck', 'TRUCKS', None, (26, 'trucks'), CY, None, (26, 'trucks', 8)), ('warehouse', 'WAREHOUSES', None, (26, 'warehouses'), CY, None, (26, 'warehouses', 8)),
                  ('job', 'JOBS', None, (26, 'warehouses', 6), CY, None, (26, 'In Ohio'))], s=170, y=360, gap=400, arrows=1, xmark=1, t1=(26, 'In Ohio'))
    s = S((26, 'In Ohio'), OHIO, z=1.0); s.d['filter'] = NIGHT; s.cam((26, 'In Ohio'), 1.0, 960, 540, 0); s.cam((26, 'night shift'), 1.18, 760, 480, 40)
    mg(s, 'tick', (26, 'In Ohio'), None, None, txt='OHIO · WAREHOUSE · 22:00', col=AMB, size=26, x=70, y=84)
    wo(s, 'chalk', (26, 'In Ohio'), None, txt='NIGHT SHIFT\n22:00 – 06:00', x=245, y=320, size=58, col='#2a2f3a', rot=0, d=1, wipe=R((26, 'whole night'), ) + 26)
    wk = s.a('wk', 300, 1010, 'wk_sign'); wk.p((26, 'whole night', 30), 'wk_carry').go((26, 'whole night', 34), -300, 900, 70, 0)
    w2 = s.a('w2', 1180, 760, 'wk_shrug'); w2.p((26, 'night shift', 20), 'wk_carry').f((26, 'night shift', 20), 0).go((26, 'night shift', 24), 1150, 674, 60, 0); w2.d['fade'] = [R((26, 'night shift', 70)), R((26, 'night shift', 86)), 1, 0]
    sfx('papers', (26, 'whole night', 20), .5)
    s.top('flick', (26, 'night shift', 30), sl=4, th=.6, v=.5, t1=(26, 'In the last'))
    sfx('bulb', (26, 'night shift', 30), .5)
    s.door((26, 'night shift'), 1, 30, snd=0); sfx('shutter', (26, 'night shift'), .4)
    s = M((26, 'In the last'))
    stat(s, (26, 'In the last'), None, x=960, y=260, center=1, w=1400, label='US JOBS LOST · 2008–2010', count=[[R((26, 'In the last')), 0], [R((26, 'nine million')), 8.7]], cd=36, fmt=None, val=None, size=210, col=RD_, glow=1)
    s.over[-1].update(fmt='raw', pre='~', suf='')
    s.over[-1]['count'] = [[R((26, 'In the last')), 0], [R((26, 'nine million')), 8700000]]
    sfx('digits', (26, 'almost'), .5); sfx('slam', (26, 'million', 20), .5)
    tagl(s, (26, 'quick sync'), 'MEETING: “QUICK SYNC” · 15 MIN', y=760, col=AMB, size=46)
    # 27: manager video call
    s = S(27, KIT, z=1.0); s.cam(27, 1.15, 1000, 500, 0); s.cam((27, 'This'), 1.3, 1020, 470, 30)
    yo = s.a('yo', 930, 905, 'yo_laptop'); yo.p((27, 'This', 10), 'yo_lean')
    mg(s, 'call', 27, None, None, ch='MANAGER', sp=[[0, 'mg_talk']], x=1420, y=420, w=640, title='QUICK SYNC · 15 MIN')
    sfx('notify', (27, 0, -10), .5)
    chap(28, 34, 'MONTH 2 · THE BANKS')

    # ================= MONTH 2 · BANKS =================
    s = M(28); wipe(28)
    tick(s, 28, 'MONTH 2', 'THE QUESTION NOBODY ASKS OUT LOUD')
    icons(s, 28, [('bank', 'YOUR BANK', None, (28, 0, 10), TX, None, None)], s=300, y=300)
    mg(s, 'big', (28, 'is my money'), None, 'heart', .7, txt='SAFE?', size=150, col=AMB, y=740, pulse=1)
    s.shk_((28, 'safe'), 6)
    s = S(29, BANK, z=1.0); s.d['filter'] = 'saturate(.9) brightness(.96)'; s.cam(29, 1.0, 960, 540, 0); s.cam((29, 'on a Monday'), 1.2, 1100, 520, 60)
    mg(s, 'tick', 29, (29, 'on a Monday'), 'scan', .4, txt='FRANKFURT · EUROPE', sub='MON 08:00 · SCENARIO', col=CY, size=28, x=70, y=84)
    icons(s, (29, 'lent heavily'), [('chip', 'LENT TO AI DATA CENTERS', None, (29, 'lent heavily'), CY, None, None)], s=110, x=420, y=780, ls=22, t1=(29, 'on a Monday'))
    co = s.a('co', 300, 1000, 'cu_old', ws=12); co.go(29, 720, 900, 120, 1)
    cr = s.a('cr', -150, 980, 'cu_rattle', ws=9); cr.go(29, 1060, 760, 140, 1).p((29, 'doors locked', -10), 'cu_rattle')
    cr.d['shk'] = [[R((29, 'find the doors')), R((29, 0, R((29, 'doors locked')) - R(29) + 50))]]
    sfx('step', 29, .2, rep=9, gap=14); sfx('rattle', (29, 'doors locked', -6), .6)
    wo(s, 'tagl', (29, 'locked', 4), None, txt='GESCHLOSSEN · CLOSED', x=1030, y=300, col=RD_, size=24, rot=-2)
    # 30: teller cracks the door
    s = S(30, BANK, z=1.15); s.cam(30, 1.15, 1080, 520, 0); s.cam((30, "I'm sorry"), 1.3, 1120, 480, 30)
    tl = s.a('tl', 1128, 700, 'tl_peek', ch='TELLER', layer='door', flip=1, shadow=False)
    cr = s.a('cr', 900, 800, 'cu_rattle', flip=0); co = s.a('co', 720, 900, 'cu_old')
    s.door((30, 0, -6), .42, 10); s.door((30, 1.0, 10), 0, 10)
    tl.p((30, "I'm sorry"), 'tl_talk' if False else 'tl_peek')
    wo(s, 'tagl', 30, None, txt='GESCHLOSSEN · CLOSED', x=1030, y=300, col=RD_, size=24, rot=-2)
    say(s, (30, 'No, I'), (30, 1.0, 22), 'TELLER', "No, I don't know if that's true.", side=-1)
    # 31: the shield
    s = M(31); wipe(31, GR)
    mg(s, 'shield', 31, None, 'shield', .5, x=640, y=120, s=340, icon='bank', label='', sub='USA · FDIC')
    mg(s, 'stat', (31, 'two hundred'), None, 'digits', .45, x=640, y=520, center=1, w=900, label='INSURED', count=[[R((31, 'two hundred')), 0], [R((31, 'thousand dollars')), 250000]], cd=30, fmt='raw', pre='$', size=110, col=GR)
    mg(s, 'flagrow', (31, 'In America'), (31, 'In Europe'), None, flags=['us'], x=1000, y=210)
    icons(s, (31, 'your own'), [('card', 'YOUR ACCOUNT', None, (31, 'your own'), TX, None, None)], s=110, x=230, y=150, ls=20)
    chips(s, (31, 'per person'), [('PER PERSON', (31, 'per person'), GR), ('PER BANK', (31, 'at each bank'), GR)], x=640, y=720, gap=300)
    icons(s, (31, 'when a bank'), [('bank', 'BANK FAILS', None, (31, 'when a bank'), TX, None, (31, 'fails'))], s=150, x=1500, y=200, xmark=1, t1=(31, 'In Europe'))
    mg(s, 'flow', (31, 'get that money'), (31, 'In Europe'), 'coin', .5, at=R((31, 'get that money')), d=30, ic='coin', col=GR, s=90, lab='')
    s.over[-1]['from'] = [1500, 300]; s.over[-1]['to'] = [760, 560]
    mg(s, 'chips', (31, 'within days'), None, None, items=[['USUALLY BACK WITHIN DAYS', R((31, 'within days')), GR]], x=640, y=860)
    mg(s, 'shield', (31, 'In Europe'), None, 'shield', .5, x=1400, y=200, s=300, icon='bank', label='€100,000', sub='PER PERSON · PER BANK · EU', col=CY, size=56)
    # 32: paycheck outside the shield
    s = M(32)
    mg(s, 'shield', 32, None, None, x=560, y=170, s=360, icon='bank', label='YOUR SAVINGS', size=40)
    icons(s, (32, 'paycheck'), [('paycheck', 'YOUR PAYCHECK', 'NOT COVERED', (32, 'paycheck'), AMB, (32, 'paycheck', 8), None)], s=220, x=1360, y=240, ls=30, ts=40)
    chips(s, (32, 'March 2023'), [('MAR 10, 2023 · SILICON VALLEY BANK', (32, 'March 2023'), RD_)], y=170, x=1360)
    icons(s, (32, 'collapsed'), [('bank', 'SVB', None, (32, 'Silicon'), RD_, None, (32, 'collapsed'))], s=130, x=1360, y=560, xmark=1, ls=24, t1=(32, 'thousands'))
    icons(s, (32, 'thousands'), [('factory', '', None, (32, 'thousands', i * 3), TX, None, None) for i in range(5)] + [('paycheck', 'PAYROLL', None, (32, 'payroll'), AMB, None, None)], s=90, x=1100, y=560, gap=130, ls=20)
    icons(s, (32, 'For a few days'), [('calendar', 'A FEW DAYS', None, (32, 'For a few days'), AMB, None, None)], s=110, x=1660, y=760, ls=20)
    mg(s, 'chips', (32, "Friday's"), None, None, items=[['FRIDAY PAYDAY?', R((32, "Friday's")), AMB]], x=1300, y=930)
    sfx('warn', (32, "Friday's"), .4)
    # 33: 1931 — the sepia map
    s = M(33); wipe(33, AMB)
    mapw(s, 33, [(33, 'ny', 2.6), ((33, 'but in 1931'), 'vienna', 4.2, 30), ((33, 'panic ran'), [960, 330], 3.0, 40)], sepia=1,
         cities=[('ny', (33, 'New York'), (33, 'New York'), 'l'), ('vienna', (33, 'Creditanstalt'), (33, 'collapsed'), 'r'), ('berlin', (33, 'Germany'), (33, 'closed all'), 'r')],
         arcs=[('vienna', 'berlin', (33, 'panic ran'), RD_), ('vienna', 'paris', (33, 'across'), RD_), ('vienna', 'london', (33, 'Europe'), RD_)], hot=[('040', (33, 'collapsed'), RD_), ('276', (33, 'closed all'), RD_)],
         rings=[('vienna', (33, 'collapsed'), RD_)])
    mg(s, 'chips', (33, 'one bank'), (33, '1929'), None, items=[['ONE BANK → A WORLD DEPRESSION', R((33, 'one bank')), AMB]], y=200)
    chips(s, (33, '1929'), [('1929 · NEW YORK', (33, '1929'), None), ('MAY 1931 · VIENNA', (33, 'Creditanstalt'), AMB), ('JULY 1931 · GERMAN BANKS CLOSED', (33, 'closed all'), RD_)], y=940, gap=620, size=30)
    icons(s, (33, 'by law'), [('lock', '', None, (33, 'by law'), RD_, None, None)], s=110, x=1260, y=300)
    sfx('lock', (33, 'by law'), .6); sfx('spark', (33, 'collapsed'), .5)
    chap(34, 37, 'MONTH 3 · TARIFFS')

    # ================= MONTH 3 · TARIFFS =================
    s = M(34); wipe(34)
    tick(s, 34, 'MONTH 3', 'TARIFFS')
    hud(s, 34, [(34, 8000), ((34, 'seven thousand'), 7500)], big=True, x=180, y=300, sub=[(34, 'MONTH 3')])
    mg(s, 'receipt', (34, 'grocery'), None, 'printer', .4, x=1450, y=150, rows=[['RICE 2KG', 4.29, R((34, 'grocery'))], ['BREAD', 3.49, R((34, 'grocery', 6))]], head='SUPERMARKET', date='MONTH 3 · SCENARIO')
    s = S(35, MKT, z=1.0); s.cam(35, 1.0, 960, 540, 0); s.cam((35, 'at the checkout'), 1.12, 900, 520, 40)
    yo = s.a('yo', 300, 1500, 'yo_bag', h=1250, shadow=False, nolint=1, flip=0); yo.p((35, 'Governments'), 'yo_rice').p((35, 'and you pay'), 'yo_bag')
    s.u('belt', (35, 'Governments'), x0=500, x1=990, y0=900, y1=480, h0=170, h1=70, n=['pp_rice', 'pp_bread'], c=4, per=120, fade=1, t1=(35, 'Some countries'))
    for i in range(5): sfx('beep', (35, 'Governments', 30 + i * 30), .4)
    sfx('register', (35, 'checkout'), .5)
    mg(s, 'receipt', (35, 'taxes'), (35, 'Some countries'), 'printer', .4, x=1480, y=110, rows=[['RICE 2KG', 4.29, R(35)], ['BREAD', 3.49, R(35)], ['IMPORTED GOODS', 12.80, R((35, 'foreign goods'))], ['IMPORT TAX (TARIFF)', 1.92, R((35, 'you pay')), 1]], head='SUPERMARKET', date='MONTH 3 · SCENARIO', note='* EXAMPLE VALUES')
    term(s, (35, 'taxes'), 'TARIFF', 'A tax on goods from other countries.', x=90, y=90, w=520, t1=(35, 'Some countries'))
    s = M((35, 'Some countries'))
    mapw(s, (35, 'Some countries'), [((35, 'Some countries'), [1300, 520], 1.5), ((35, 'India'), 'mumbai', 2.8, 30)], cities=[('mumbai', (35, 'India'), None, 'r')], hot=[('356', (35, 'India'), AMB)], rings=[('mumbai', (35, 'banned'), AMB)])
    chips(s, (35, '2023'), [('JULY 2023 · INDIA BANS MOST RICE EXPORTS', (35, 'banned'), AMB)], y=200, x=960)
    icons(s, (35, 'rice prices'), [('sack', 'WORLD RICE PRICE', '↑', (35, 'rice prices'), AMB, (35, 'jumped'), None)], s=170, x=1500, y=620)
    # 36: world trade shrinks, crowd outside the bakery
    s = M(36); wipe(36)
    mg(s, 'cmp2', 36, (36, 'And in Cairo'), None, title='WORLD TRADE', data=[['1929', 100, CY, R((36, 'Between')), '100%', 'ship'], ['1933', [[R((36, 'Between')), 100], [R((36, 'two thirds')), 34]], RD_, None, '~1/3', 'ship']], max=100, h=480, y=900, gap=560)
    sfx('whoosh_down', (36, 'two thirds'), .5)
    s = S((36, 'And in Cairo'), BAK, z=1.0); s.d['filter'] = 'saturate(1.05) sepia(.1) brightness(.95)'; s.cam((36, 'And in Cairo'), 1.0, 960, 540, 0); s.cam((36, 'a crowd'), 1.2, 1300, 460, 40)
    bk = s.a('bk', 520, 860, 'bk_write', ch=None); bk.p((36, 'this time'), 'bk_turn')
    wo(s, 'chalk', (36, 'And in Cairo'), None, txt='FLOUR\n1,100 E£', x=740, y=310, size=74, d=1, wipe=R((36, 'one more')))
    wo(s, 'chalk', (36, 'one more', 10), None, txt='FLOUR\n1,100 E£ ↑↑', x=750, y=310, size=74, d=20)
    sfx('chalk', (36, 'one more', 10), .5)
    for i, (c_, x_) in enumerate([('cr_1', 1560), ('cr_2', 1640), ('cr_3', 1700), ('cr_4', 1600), ('cr_1b', 1680)]):
        a = s.a('c%d' % i, x_ + 200, 520 + i * 6, c_, h=240 + i * 6, layer='door', shadow=False, nolint=1, flip=1); a.go((36, 'a crowd', i * 6), x_, 520 + i * 6, 40, 1)
    sfx('crowd', (36, 'a crowd'), .5)
    chap(37, 41, 'MONTH 4 · THE RALLY')

    # ================= MONTH 4 · THE RALLY =================
    s = M(37); wipe(37, GR)
    tick(s, 37, 'MONTH 4', 'GOOD NEWS', col=GR)
    mg(s, 'chart', 37, None, None, title='STOCKS · SCENARIO', pts=[[0, 60], [1, 58], [2, 66], [3, 74], [4, 82]], lo=40, hi=90, d=60, x=360, y=330, w=1200, h=420, col=GR)
    icons(s, (37, 'worst mistake'), [('warn', '', None, (37, 'worst mistake'), RD_, None, None)], s=200, x=1560, y=200)
    sfx('warn', (37, 'worst mistake'), .5)
    s = M(38)
    mg(s, 'press', (38, 'print'), (38, 'Stocks jump'), 'printer', .4, x=520, y=430, fast=1, lab='CENTRAL BANK')
    mg(s, 'gauge', (38, 'cut interest'), (38, 'Stocks jump'), None, x=1000, y=230, keys=[[R((38, 'cut interest')), 30], [R((38, 'cut interest', 10)), -70]], label='INTEREST RATES', sub='CUT', subAt=R((38, 'cut interest', 10)))
    sfx('blip_down', (38, 'cut interest', 8), .5)
    mg(s, 'chart', (38, 'Stocks jump'), (38, 'and on TV'), None, title='STOCKS · 2 WEEKS · SCENARIO', pts=[[0, 100], [1, 104], [2, 109], [3, 113], [4, 117], [5, 120]], lo=95, hi=124, d=40, marks=[[5, '+20%', GR, 'l']], x=300, y=280, w=1300, h=500, col=GR)
    sfx('blip_up', (38, 'twenty'), .5); sfx('cheer', (38, 'twenty'), .3)
    hud(s, (38, 'Your fund'), [((38, 'Your fund'), 7500), ((38, 'nine thousand'), 9000)], x=1380, y=60, t1=(38, 'and on TV'))
    s = S((38, 'and on TV'), KIT, z=1.15); s.cam((38, 'and on TV'), 1.15, 1300, 520, 0); s.cam((38, 'worst is over'), 1.3, 1380, 480, 30)
    yo = s.a('yo', 1480, 990, 'yo_relief')
    mg(s, 'banner', (38, 'on TV'), None, 'notify', .5, txt='“THE WORST IS OVER”', tag='LIVE')
    hud(s, (38, 'on TV'), [((38, 'on TV'), 9000)], x=1380, y=60, now=1, snd='tick')
    # 39: November 1929, real Dow
    s = M(39); wipe(39, AMB)
    dow = [198.7, 248, 267, 272, 286, 294.1, 274, 226, 233, 240, 204, 183, 164, 168, 190, 172, 150, 155, 136, 96, 105, 78, 76, 82, 73, 56, 45, 41.2]
    mg(s, 'chart', (39, 'November'), (39, 'And our rally'), None, title='DOW JONES · NOV 1929 → JUL 1932', pts=[[i, v] for i, v in enumerate(dow)], lo=0, hi=320, d=R((39, 'eighty-six')) - R((39, 'November')) - 6, delay=0,
       marks=[[0, 'NOV 1929 · 199', TX, 'u'], [5, 'APR 1930 · 294 · +48%', GR, 'u'], [27, 'JUL 1932 · 41 · −86%', RD_, 'l']], xl=[[0, '1929'], [2, '1930'], [14, '1931'], [26, '1932']], x=230, y=240, w=1460, h=560, col=AMB)
    sfx('blip_up', (39, 'climbed'), .5); sfx('whoosh_down', (39, 'then fell'), .5); sfx('impact', (39, 'eighty-six'), .7)
    s = M((39, 'And our rally'))
    mg(s, 'stat', (39, 'And our rally'), None, 'hammer', .8, x=170, y=180, label='AUCTION · CORVANE CHIPS · PER CHIP', val='< $5,000', size=150, col=RD_)
    icons(s, (39, 'auction'), [('hammer', '', None, (39, 'auction'), RD_, None, None)], s=200, x=1500, y=140)
    chips(s, (39, 'two more'), [('AI COMPANY #2 · MISSED PAYMENT', (39, 'two more'), RD_), ('AI COMPANY #3 · MISSED PAYMENT', (39, 'miss payments'), RD_)], y=600, gap=800)
    hud(s, (39, 'your fund'), [((39, 'your fund'), 9000), ((39, 'six thousand'), 6000)], x=730, y=760)
    s.shk_((39, 'six thousand'), 10)
    # 40: would you sell?
    s = M(40); s.d['ocam'] = [[R(40), 1.0, 960, 540], [R((40, 'Would you')), 1.0, 960, 540], [R((40, 'Would you')) + 1, 1.12, 960, 520, R((40, 'Most people')) - R((40, 'Would you'))]]
    hud(s, 40, [(40, 6000)], big=True, x=530, y=170, now=1, lock=[(40, 0), None], snd='tick')
    mg(s, 'big', (40, 'Would you'), (40, 'People who'), 'heart', .8, txt='WOULD YOU SELL?', size=130, col=TX, y=700, pulse=1)
    sfx('heart', (40, 'Would you', 26), .7); sfx('lowboom', (40, 'Most people'), .5)
    icons(s, (40, 'Most people'), [('job', '', None, (40, 'Most people', i * 2), TX, None, (40, 'Most people', 6 + i * 3) if i < 4 else None) for i in range(5)], s=80, y=920, gap=130, t1=(40, 'People who'))
    s = M((40, 'People who'))
    mg(s, 'chart', (40, 'People who'), None, None, title='A TYPICAL CRASH · TWO DROPS', pts=[[0, 100], [1, 80], [2, 74], [3, 90], [4, 70], [5, 58], [6, 62], [7, 75], [8, 90], [9, 104]], lo=50, hi=110, d=R((40, 'real one')) - R((40, 'People who')) + 20, delay=4,
       marks=[[2, 'STAYED CALM', TX, 'r'], [5, 'SOLD HERE', RD_, 'r'], [9, 'RECOVERY', GR, 'l']], x=260, y=260, w=1400, h=480, col=AMB, lin=1)
    tagl(s, (40, 'real one'), 'SCREEN LOSS → REAL LOSS', y=900, col=RD_, size=46)
    hud(s, (40, 'Hold on'), [((40, 'Hold on'), 6000)], x=1380, y=60, now=1, lock=[(40, 'Hold on'), None], snd='lock')
    chap(41, 45, 'IS YOUR MONEY WORTH ANYTHING?')

    # ================= WILL MONEY BE WORTH ANYTHING? =================
    s = M(41); wipe(41, GR)
    tick(s, 41, 'THE QUESTION UNDERNEATH', col=GR)
    icons(s, (41, 'worth anything'), [('dollar', '', None, 41, GR, None, None)], s=380, y=250)
    glitch((41, 'worth anything'), 8)
    s = M(42)
    icons(s, (42, 'prices drop'), [('bread', 'BREAD', '↓', (42, 'prices drop'), TX, (42, 'prices drop', 4), None), ('cart', 'GROCERIES', '↓', (42, 'prices drop', 6), TX, (42, 'prices drop', 10), None), ('house', 'RENT', '↓', (42, 'prices drop', 12), TX, (42, 'prices drop', 16), None)], s=170, y=250, gap=400, tcol=GR)
    icons(s, (42, 'every dollar'), [('dollar', 'YOUR $1 BUYS MORE', None, (42, 'every dollar'), GR, None, None)], s=200, x=960, y=600, ls=26, t1=(42, 'During'))
    chips(s, (42, 'Great Depression'), [('1929–1933 · US PRICES ≈ −25%', (42, 'fell by'), GR)], y=900)
    s = M(43); wipe(43, GD_)
    mg(s, 'press', 43, (43, 'In 1933'), 'printer', .4, x=760, y=430, lab='MORE MONEY · EACH DOLLAR WORTH LESS')
    mg(s, 'flow', (43, 'hand in'), None, 'coin', .6, at=R((43, 'hand in')), d=36, ic='coin', col=GD_, s=130, lab='$20.67/OZ', ends=[['people', 'CITIZENS', 420, 520, TX], ['bank', 'GOVERNMENT', 1500, 520, TX]])
    s.over[-1]['from'] = [560, 470]; s.over[-1]['to'] = [1290, 470]
    icons(s, (43, 'worth less'), [('dollar', 'EACH DOLLAR', 'WORTH LESS', (43, 'worth less'), GR, (43, 'worth less', 6), (43, 'worth less', 12))], s=160, x=1450, y=300, t1=(43, 'In 1933'))
    icons(s, (43, 'less than a year'), [('calendar', '< 1 YEAR LATER', None, (43, 'less than a year'), GD_, None, None)], s=110, x=960, y=160, ls=22)
    chips(s, (43, 'In 1933'), [('APRIL 1933 · HAND IN YOUR GOLD', (43, 'In 1933'), GD_)], y=820)
    tagl(s, (43, 'thirty-five'), '1934 · GOLD = $35/OZ', y=330, col=GD_, size=54)
    mg(s, 'stat', (43, 'sixty-nine'), None, 'slam', .5, x=1080, y=760, label='GOVERNMENT', val='+69%', size=130, col=GR)
    mg(s, 'stat', (43, 'made nothing'), None, 'thud', .5, x=300, y=760, label='PEOPLE WHO HANDED IT IN', val='$0', size=130, col=RD_)
    s = M(44)
    mg(s, 'basket', 44, None, None, years=[['2027', 1, R(44)], ['2028', .96, R((44, 'little less'))], ['2029', .92, R((44, 'every year'))], ['2030', .88, R((44, 'every year', 12))]])
    for w in ('buys a little', 'little less', 'every year'): sfx('tick', (44, w), .5)
    icons(s, (44, 'letter'), [('mail', 'NO LETTER', None, (44, 'letter'), DIM, None, None)], s=110, x=1720, y=70, ls=20)
    chap(45, 51, 'WHO WINS?')

    # ================= WHO WINS? =================
    s = M(45); wipe(45, GD_)
    tick(s, 45, 'WHERE THE MONEY LANDS', col=GD_)
    mapw(s, 45, [(45, [960, 560], 1.6), ((45, 'Now let'), [960, 560], 1.0, 60)], hot=[(c, 45, RD_) for c in ('840', '392', '826', '276', '156', '356', '818', '040', '250')])
    tagl(s, (45, 'new boss'), 'A NEW BOSS', y=880, col=GD_, size=60)
    COLS = [['wheat', 'FOOD'], ['oil', 'ENERGY'], ['factory', 'FACTORIES'], ['army', 'ARMY'], ['trust', 'TRUST']]
    def board(s, t, t1, rows, focus=None, y=110):
        rr = [[f, n, [[c[0], R(c[1])] if c else None for c in cells], R(a)] for f, n, cells, a in rows]
        mg(s, 'score', t, t1, None, cols=COLS, rows=rr, x=120, y=y, cw=230, rh=118, scl=1.2, focus=[[R(a), v] for a, v in (focus or [])])
    s = M(46)
    tagl(s, 46, 'STOCK PRICES · DON’T MATTER', y=170, col=DIM, size=40, rot=-2)
    icons(s, (46, 'food'), [(k, n, None, (46, w), TX, None, None) for (k, n), w in zip(COLS, ('food', 'energy', 'factories', 'army', 'trusts'))], s=150, y=420, gap=320)
    R47 = [['eu', 'EUROPE', [None, (0, (47, 'energy from')), (2, (47, 'factories')), None, None], (47, 'Europe')], ['jp', 'JAPAN', [(0, (47, 'Japan')), (0, (47, 'import their energy')), None, None, None], (47, 'Japan')],
           ['sa', 'GULF STATES', [(0, (47, 'or their food')), (1, (47, 'Gulf')), None, None, None], (47, 'Gulf')]]
    s = M(47); board(s, 47, None, R47)
    icons(s, (47, 'heating bills'), [('heater', 'HEATING BILLS', '↑', (47, 'heating bills'), AMB, None, None)], s=110, x=1720, y=180, ls=18, ts=34)
    R48 = R47 + [['cn', 'CHINA', [(1, (48, "world's wheat")), (0, (48, 'Strait of Hormuz')), (1, (48, 'manufactured')), (2, (48, 'gold')), (2, (48, 'broke'))], (48, 'China')]]
    s = M(48); board(s, 48, (48, 'But our captain'), R48, focus=[(48, 3)])
    chips(s, (48, 'a third'), [('~1/3 OF WORLD MANUFACTURING', (48, 'a third'), GR), ('~1/2 OF WORLD WHEAT STOCKS', (48, 'half'), GR), ('BUYING GOLD', (48, 'buying gold'), GD_)], y=1000, gap=560, size=28)
    s = S((48, 'But our captain'), SHIP, z=1.25); s.d['win'] = [260, 160, 1400, 788]; s.d['wlab'] = 'SHANGHAI · STILL AT ANCHOR'; s.d['wflag'] = 'cn'; s.d['filter'] = 'saturate(.8) brightness(.95)'
    s.cam((48, 'But our captain'), 1.25, 960, 600, 0); s.cam((48, 'But our captain', 2), 1.35, 960, 620, 120)
    cp = s.a('cp', 845, 800, 'cp_cards'); cp.p((48, 'broke'), 'cp_throw'); s.a('sa', 1105, 790, 'sl_a2', flip=1); s.a('sb', 1010, 860, 'sl_b')
    sfx('cards', (48, 'broke'), .4); sfx('horn', (48, 'But our captain'), .25)
    icons(s, (48, 'oil comes'), [('oil', 'OIL VIA HORMUZ', None, (48, 'oil comes'), RD_, None, None)], s=110, x=1760, y=820, ls=18)
    R49 = R48 + [['us', 'USA', [(1, (49, 'grain')), (1, (49, 'pumps')), (2, (49, 'domino')), (1, (49, 'military')), (1, (49, 'ocean'))], (49, 'And then')]]
    s = M(49); board(s, 49, None, R49, focus=[(49, 4)])
    icons(s, (49, 'domino'), [('flame', '', None, (49, 'domino'), RD_, None, None)], s=70, x=60, y=110 + (130 + 4 * 118) * 1.2 + 10)
    for w in ('pumps', 'grain', 'ocean', 'military'): sfx('check', (49, w), .5)
    # 50: the burning house
    s = M(50); wipe(50, GR)
    mapw(s, 50, [(50, [960, 560], 1.1), ((50, 'comes out'), 'ny', 1.8, 40)], hot=[('840', 50, GR)], arcs=[(c, 'ny', (50, 'comes out', i * 4), GR) for i, c in enumerate(('london', 'frankfurt', 'tokyo', 'shanghai', 'mumbai', 'saopaulo', 'lagos', 'sydney'))], t1=(50, 'In 2008'))
    s = M((50, 'In 2008'))
    stat(s, (50, 'In 2008'), None, x=960, y=200, center=1, w=1500, label='2008 · CRISIS STARTS IN US BANKS', val='DOLLAR +20%+', size=140, col=GR)
    chips(s, (50, 'This October'), [('OCT 2026 · AMERICA AT WAR · DOLLAR AT 18-MONTH HIGH', (50, 'highest point'), GR)], y=640)
    s = M((50, 'The fire'))
    mg(s, 'fire', (50, 'The fire'), None, 'fire', .35, x=960, y=640)
    sfx('whoosh', (50, 'runs into'), .4)
    mg(s, 'chips', (50, 'strongest house'), None, None, items=[['STILL THE STRONGEST HOUSE ON THE STREET', R((50, 'strongest house')), GR]], y=960)
    chap(51, 54, 'THE NEXT CRASH')

    # ================= THE NEXT CRASH =================
    s = M(51); wipe(51, GD_)
    icons(s, 51, [('trophy', 'THIS CRASH', None, 51, GR, None, None), ('trophy', 'THE NEXT ONE?', None, (51, 'But the people'), DIM, None, None)], s=260, y=260, gap=620)
    mg(s, 'flagrow', 51, None, None, flags=['us'], x=650, y=740)
    s = M(52)
    mg(s, 'cmp2', 52, (52, 'And between'), None, title="WORLD'S CENTRAL BANKS · RESERVES", data=[['GOLD', [[R(52), 20], [R((52, 'more of their savings')), 52]], GD_, None, 'GOLD', 'gold'], ['US IOUs', [[R(52), 60], [R((52, 'more of their savings')), 48]], CY, None, 'US IOUs', 'paycheck']], max=70, h=460, y=860, gap=560)
    chips(s, (52, '1996'), [('FIRST TIME SINCE 1996', (52, '1996'), GD_)], y=180)
    s = M((52, 'And between'))
    mg(s, 'stack', (52, 'And between'), None, 'gold', .5, x=760, y=820, n=36, d=R((52, 'roughly')) - R((52, 'bought about')), tons=320, txt='~{} TONS · JUL–SEP 2026', wat=R((52, 'two blue whales')))
    for i in range(6): sfx('gold', (52, 'bought about', i * 14), .35)
    s = M(53); wipe(53, GD_)
    mg(s, 'press', 53, (53, 'Because in 2022'), None, x=520, y=430, lab='THEY CAN PRINT THIS')
    icons(s, (53, "can't print"), [('gold', "THEY CAN'T PRINT THIS", None, (53, "can't print"), GD_, None, None)], s=260, x=1360, y=300, t1=(53, 'Because in 2022'))
    s = M((53, 'Because in 2022'))
    mapw(s, (53, 'Because in 2022'), [((53, 'Because in 2022'), [1200, 380], 1.8), ((53, 'Russia'), 'moscow', 3.2, 30), ((53, 'every central bank'), [1100, 500], 1.2, 40)], cities=[('moscow', (53, 'Russia'), (53, 'frozen'), 'r')], hot=[('643', (53, 'Russia'), CY)], t1=(53, 'Every ton'))
    mg(s, 'stat', (53, 'three hundred'), (53, 'every central bank'), 'ice', .7, x=960, y=640, center=1, w=1300, label='2022 · RUSSIA · SAVINGS FROZEN BY THE WEST', val='~$300B', size=160, col=CY, glow=1)
    mg(s, 'flagrow', (53, 'every central bank'), (53, 'Every ton'), None, flags=['cn', 'in', 'sa', 'br', 'tr' if False else 'ae', 'mx'], y=760, q=R((53, "what if")))
    mg(s, 'big', (53, 'what if'), (53, 'Every ton'), 'heart', .6, txt="WHAT IF WE'RE NEXT?", size=80, col=TX, y=240)
    s = M((53, 'Every ton'))
    mg(s, 'fork', (53, 'Every ton'), None, 'whoosh', .4, tw=R((53, 'somewhere else')), lean=18, l='THE DOLLAR', r='GOLD')
    mg(s, 'flagrow', (53, 'like China'), None, None, flags=['cn'], x=1340, y=700)
    chap(54, (57, 1.0, 150), 'YOUR ANSWER')

    # ================= YOUR ANSWER · THE ENDING =================
    s = M(54); wipe(54, GR)
    hud(s, 54, [(54, 6000), ((54, 'back to even'), 10000)], big=True, x=180, y=250, lock=[(54, 0), (54, 'your answer')], sub=[(54, 'YOUR ANSWER'), ((54, 'back to even'), 'BACK TO EVEN')], t1=(54, 'The people who came'))
    sfx('lock', (54, 'your answer'), .7)
    mg(s, 'lines2', (54, 'After 2008'), (54, 'The people who came'), None, x=1110, y=380, w=700, yrs=10, title='BACK TO EVEN AFTER 2008', rows=[['2008: HELD AN INDEX FUND', 5, GR, R((54, 'within about'))]])
    tagl(s, (54, 'sold in the panic'), 'SOLD IN THE PANIC = LOSS LOCKED IN', y=900, col=RD_, size=40)
    s = M((54, 'The people who came'))
    mg(s, 'big', (54, 'The people who came'), (54, 'In 1932'), None, txt='', pre='WHO CAME THROUGH BEST', pcol=GR, ps=34, y=170)
    mg(s, 'checks', (54, 'three things'), (54, 'In 1932'), None, x=330, y=300, items=[['Cash you can reach', R((54, 'some cash'))], ['No debt that can be called in', R((54, 'no debt'))], ["The nerve not to sell at the bottom", R((54, 'the nerve'))]], size=60)
    for w in ('some cash', 'no debt', 'the nerve'): sfx('check', (54, w), .6)
    s = S((54, 'In 1932'), OHIO, z=1.0); s.d['filter'] = DARK; s.cam((54, 'In 1932'), 1.0, 960, 540, 0); s.cam((54, 'skill'), 1.3, 620, 420, 60)
    mg(s, 'tick', (54, 'In 1932'), None, None, txt='1932 · AND TODAY', sub='SKILLS EVERYONE STILL NEEDS', col=GR, size=28, x=70, y=84)
    el = s.a('el', 520, 1060, 'el_fix', flip=0); el.p((54, 'everyone still'), 'el_switch').p((54, 'lights working'), 'el_down')
    sfx('scratch', (54, 'skill'), .4)
    s = S((54, 'lights working'), OHIO, z=1.15); s.cam((54, 'lights working'), 1.3, 620, 420, 0); s.cam((54, 'lights working', 2), 1.0, 960, 540, 60)
    el = s.a('el', 520, 1060, 'el_down')
    s.o('flash', (54, 'lights working'), None, a=.45, col='#fff7d0'); sfx('bulb', (54, 'lights working'), .7); sfx('chime', (54, 'lights working', 4), .4)
    # 55: Bretton Woods
    s = S(55, HOT, z=1.0); s.d['filter'] = 'sepia(.35) saturate(.85)'; s.cam(55, 1.0, 960, 540, 0); s.cam((55, 'In July'), 1.5, 960, 560, 80)
    mg(s, 'tick', 55, (55, 'In July'), 'scan', .4, txt='NEW HAMPSHIRE · MOUNT WASHINGTON HOTEL', sub='BRETTON WOODS', col=GD_, size=26, x=70, y=84)
    for i, (c_, x0, y0) in enumerate([('dl_1', 820, 1040), ('dl_2', 1120, 1070), ('dl_3', 700, 1000), ('dl_4', 1260, 1000), ('dl_1b', 980, 1120)]):
        a = s.a('d%d' % i, x0, y0, c_, ws=11, flip=1 if x0 > 960 else 0); a.go((55, 'hotel', i * 10), 960 + (i - 2) * 8, 600, 230, 0)
        a.d['fade'] = [R((55, 'hotel', i * 10 + 210)), R((55, 'hotel', i * 10 + 232)), 1, 0]
    s.door((55, 'hotel', 200), 1, 14, snd=0); sfx('step', (55, 'hotel'), .2, rep=14, gap=15)
    chips(s, (55, 'July 1944'), [('JULY 1944', (55, 'July 1944'), GD_), ('44 COUNTRIES', (55, 'forty-four'), None), ('3 WEEKS', (55, 'three weeks'), None)], y=960, gap=420)
    s = M((55, 'and put the dollar')); wipe((55, 'and put the dollar'), GD_)
    mg(s, 'converge', (55, 'and put the dollar'), None, None, flags=['gb', 'fr', 'cn', 'in', 'br', 'mx', 'ca', 'au'])
    mg(s, 'stat', (55, 'two thirds'), None, 'gold', .6, x=960, y=830, center=1, w=1400, label='USA · 1944', val='~2/3 OF THE WORLD’S GOLD', size=70, col=GD_)
    s = M(56)
    mg(s, 'envs', 56, (56, 'The central banks'), 'whoosh', .4, from_=None, n=12)
    s.over[-1]['from'] = 'FROM: WASHINGTON'
    sfx('papers', (56, 'went out'), .5)
    s = M((56, 'The central banks'))
    mg(s, 'envs', (56, 'The central banks'), None, None, n=0, col=GD_)
    s.over[-1]['from'] = 'FROM: ?'
    mg(s, 'stack', (56, 'buying gold'), None, None, x=1500, y=900, n=24, d=30, tons=0, txt='')
    s = M(57); wipe(57, GD_)
    mg(s, 'flagrow', 57, None, None, flags=['us', 'cn', 'eu', 'jp', 'in', 'gb', 'br'], y=380, gap=240, pulse=1, names=['USA', 'CHINA', 'EUROPE', 'JAPAN', 'INDIA', 'UK', 'BRAZIL'])
    mg(s, 'big', (57, 'Tell me'), None, 'notify', .5, txt='Which country would you bet on?', size=72, col=TX, y=680, sub='COMMENT: WHERE ARE YOU WATCHING FROM?', subAt=R((57, 'where')))
    sfx('chime', (57, 'watching'), .4)

    # default slow push for MG pages without their own overlay camera
    SCN.sort(key=lambda q: q.start)
    for i, q in enumerate(SCN):
        if q.d.get('set') == '#mg' and 'ocam' not in q.d:
            end = SCN[i + 1].start if i + 1 < len(SCN) else q.start + 300
            q.d['ocam'] = [[q.start, 1.0, 960, 540], [q.start + 1, 1.0, 960, 540, 1], [q.start + 2, 1.035, 960, 528, max(10, end - q.start)]]

# Layered SFX library: Kenney samples + synthesis + short room/hall reverb. Output: sfx/<name>.wav (mono 44.1k)
import numpy as np, subprocess, os
from scipy.signal import butter, lfilter, fftconvolve
SR = 44100; rng = np.random.default_rng(7); K = '../sfxk/'
os.makedirs('sfx', exist_ok=True)
def rd(p, af=None):
    c = ['ffmpeg', '-v', 'error', '-i', p] + (['-af', af] if af else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(c, capture_output=True).stdout, 'f4').copy()
def kf(n, rate=1.0, g=1.0):
    y = rd(K + n + '.mp3', f'asetrate={int(SR*rate)},aresample={SR}' if rate != 1 else None); return y / (np.abs(y).max() + 1e-9) * g
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), min(.99, hi / (SR / 2))], 'band'); return lfilter(b, a, x)
def lp(x, f, o=2): b, a = butter(o, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f, o=2): b, a = butter(o, f / (SR / 2), 'high'); return lfilter(b, a, x)
def T(d): return np.arange(int(d * SR)) / SR
def env(t, a, d): return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
def verb(x, size=.6, mix=.25, tone=5000):
    n = int(size * SR); t = np.arange(n) / SR; ir = rng.standard_normal(n) * np.exp(-t / (size / 5)); ir = lp(ir, tone); ir /= np.abs(ir).sum() ** .5 * 6
    w = fftconvolve(x, ir)[:len(x) + n]; y = np.zeros(len(w)); y[:len(x)] = x; return y * (1 - mix) + w * mix * 3
def lay(*P):
    n = max(int(at * SR) + len(y) for y, at in P); o = np.zeros(n)
    for y, at in P: i = int(at * SR); o[i:i + len(y)] += y
    return o
def sweep(d, f0, f1, shape=.5, bands=8, q=1.35):
    t = T(d); x = rng.standard_normal(len(t)); o = np.zeros(len(t)); B = np.geomspace(min(f0, f1), max(f0, f1), bands)
    if f1 < f0: B = B[::-1]
    for i, fc in enumerate(B):
        c = (i + .5) / bands * shape * 2 if shape < .5 else i / bands * 0.8 + .1
        y = bp(x, fc / q, fc * q); o += y * np.exp(-((t / d - c) / .22) ** 2)
    return o
def tone(d, f, a=.002, dec=.2, h=(1, .4, .2), fm=0):
    t = T(d); s = sum(w * np.sin(2 * np.pi * f * (k + 1) * t + fm * np.sin(2 * np.pi * f * 1.41 * t)) for k, w in enumerate(h)); return s * env(t, a, dec)
def sub(d=.6, f0=120, f1=38, dec=.35):
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t * 18); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(t, .003, dec)
def norm(x, pk=.89):
    x = x - x.mean(); f = int(.004 * SR); x[:f] *= np.linspace(0, 1, f); f2 = int(.03 * SR); x[-f2:] *= np.linspace(1, 0, f2); return x / (np.abs(x).max() + 1e-9) * pk
def save(n, x): x = norm(x); import wave; w = wave.open(f'sfx/{n}.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes()); w.close()

L = {}
# --- motion ---
L['whoosh'] = verb(sweep(.42, 300, 5200) * .9 + bp(rng.standard_normal(int(.42 * SR)), 80, 260) * np.hanning(int(.42 * SR)) * .5, .5, .2)
L['whoosh_short'] = verb(sweep(.22, 600, 7000), .3, .15)
L['whoosh_down'] = verb(sweep(.5, 4200, 220) + sub(.5, 90, 40, .3) * .5, .6, .25)
L['whip'] = lay((sweep(.16, 900, 9000) * 1.1, 0), (kf('impactSoft_heavy_003', 1.6, .35), .12))
L['swish'] = verb(sweep(.28, 1200, 8000, bands=6), .3, .18)
# --- UI ---
L['tick'] = lay((hp(kf('switch_002', 1.35)[:int(.06 * SR)], 400), 0), (tone(.05, 3200, .001, .01, (1,)) * .25, 0))
L['tick_low'] = kf('switch_004', .9)[:int(.07 * SR)]
L['digits'] = lay(*[(hp(kf('switch_006', 1.4 + (i % 3) * .1)[:int(.04 * SR)], 500) * (.6 + .4 * (i % 2)), i * .045) for i in range(10)])
L['blip_up'] = verb(lay((tone(.16, 880, .003, .08, (1, .3), .6), 0), (tone(.22, 1318, .003, .12, (1, .3), .6), .07)), .5, .3, 7000)
L['blip_down'] = verb(lay((tone(.16, 988, .003, .08, (1, .3), .6), 0), (tone(.26, 659, .003, .14, (1, .3), .6), .08)), .5, .3, 7000)
L['pop'] = lay((kf('pluck_001', 1.15, .9), 0), (sweep(.08, 2000, 7000) * .25, 0), (tone(.12, 1500, .001, .03, (1,)) * .25, 0))
L['pop2'] = lay((kf('pluck_001', 1.3, .9), 0), (tone(.12, 1800, .001, .03, (1,)) * .25, 0))
L['scan'] = verb(lay((bp(rng.standard_normal(int(.7 * SR)), 2500, 9000) * np.sin(np.linspace(0, np.pi, int(.7 * SR))) * .5, 0),
                     *[(tone(.05, 2400 + i * 200, .001, .02, (1,)) * .35, .08 + i * .09) for i in range(6)]), .4, .2, 8000)
L['warn'] = verb(lay((tone(.22, 740, .004, .2, (1, .5, .3, .2)), 0), (tone(.3, 554, .004, .25, (1, .5, .3, .2)), .2)), .6, .3)
L['err'] = lay((kf('error_005', 1.0, .9), 0), (tone(.25, 220, .005, .15, (1, .6, .4)) * .4, 0))
L['notify'] = verb(lay((tone(.18, 1046, .002, .12, (1, .25), .3), 0), (tone(.3, 1568, .002, .2, (1, .25), .3), .1)), .5, .3, 8000)
L['vibrate'] = lay(*[(lp(np.sign(np.sin(2 * np.pi * 160 * T(.22))) * env(T(.22), .01, .5) * .6, 600), i * .34) for i in range(2)])
L['check'] = lay((tone(.12, 1320, .002, .05, (1, .3)), 0), (tone(.2, 1760, .002, .12, (1, .3)), .06), (kf('switch_002', 1.2, .4)[:int(.05 * SR)], 0))
# --- impacts ---
L['impact'] = verb(lay((sub(1.1, 140, 34, .5) * 1.1, 0), (kf('impactPunch_heavy_004', .7, .7), 0), (kf('impactMetal_heavy_002', .55, .35), .005),
                       (lp(rng.standard_normal(int(.3 * SR)), 1200) * env(T(.3), .001, .05) * .4, 0)), 1.4, .32, 3500)
L['slam'] = verb(lay((kf('impactPunch_heavy_000', .85, .9), 0), (kf('impactPlate_heavy_001', .8, .45), .004), (sub(.6, 160, 45, .25) * .8, 0)), .8, .22, 4000)
L['thud'] = verb(lay((sub(.4, 110, 50, .15), 0), (kf('impactSoft_heavy_001', .9, .7), 0)), .4, .15, 3000)
L['heart'] = lay((sub(.35, 70, 40, .09), 0), (sub(.35, 64, 38, .11) * .7, .2))
def _riser(d=1.6):
    t=T(d);x=rng.standard_normal(len(t));o=np.zeros(len(t));B=int(.04*SR)
    for a in range(0,len(t),B):
        q=t[min(a,len(t)-1)]/d;o[a:a+B]=lp(x[a:a+B+400],600+7000*q*q)[:len(o[a:a+B])]
    o=o*(t/d)**2*.7+np.sin(2*np.pi*np.cumsum(200+700*(t/d)**2)/SR)*(t/d)**3*.25
    return verb(o,1.0,.35)
L['riser']=_riser()
L['glitch'] = lay((kf('glitch_003', 1.0, .8), 0), (np.round(bp(rng.standard_normal(int(.25 * SR)), 300, 6000) * 4) / 4 * .3, .02))
L['stamp'] = verb(lay((kf('impactPunch_heavy_002', 1.0, .9), 0), (kf('impactPlank_medium_002', 1.0, .6), .004)), .4, .15)
L['hammer'] = verb(lay((kf('impactWood_heavy_002', .9, .9), 0), (kf('impactWood_heavy_000', 1.0, .6), .004), (sub(.3, 120, 60, .1) * .5, 0)), .9, .3)
L['shield'] = verb(lay((sweep(.5, 200, 3000) * .5, 0), (tone(1.2, 220, .3, .5, (1, .5, .3, .2), .4) * .4, .05), (tone(1.0, 330, .3, .5, (1, .4), .4) * .3, .1)), 1.2, .4)
# --- money/things ---
L['coin'] = lay((kf('handleCoins2', 1.0, .9), 0), (tone(.6, 2637, .001, .25, (1, .5, .2), 1.5) * .25, .01))
L['coins'] = lay((kf('chips-stack-4', 1.0, .9), 0), (kf('handleCoins2', 1.1, .6), .05))
L['gold'] = verb(lay((kf('chips-handle-4', .7, .9), 0), (kf('impactMetal_heavy_000', 1.6, .3), 0)), .5, .2)
L['paper'] = kf('card-slide-6', 1.0, .9)
L['papers'] = lay((kf('card-fan-2', 1.0, .9), 0), (kf('card-slide-2', 1.0, .6), .15))
L['register'] = lay((tone(.12, 2093, .002, .08, (1, .2)), 0), (kf('switch_004', 1.0, .6), .0))
L['beep'] = tone(.14, 1880, .002, .2, (1,)) * np.minimum(1, (0.14 - T(.14)) / .02)
L['printer'] = (lambda t: lp(np.sign(np.sin(2 * np.pi * 95 * t)) * .5 + rng.standard_normal(len(t)) * .3, 2200) * (1 + .5 * np.sign(np.sin(2 * np.pi * 9 * t))) * np.minimum(1, t / .05) * np.minimum(1, (t[-1] - t) / .05))(T(1.1))
L['ice'] = verb(lay((kf('impactGlass_heavy_003', .55, .9), 0), *[(hp(rng.standard_normal(int(.02 * SR)), 2000) * env(T(.02), .0005, .004) * .6, .05 + i * .03 + rng.uniform(0, .02)) for i in range(16)],
                     (sub(.5, 90, 40, .2) * .5, 0)), 1.0, .3, 6000)
L['fire'] = (lambda t: lp(rng.standard_normal(len(t)), 900) * .35 * (1 + .3 * np.sin(2 * np.pi * .7 * t)) + sum(hp(np.where(np.abs(t - rng.uniform(0, t[-1])) < .002, rng.standard_normal(len(t)), 0), 1500) for _ in range(40)) * .5)(T(2.5))
L['spark'] = lay(*[(hp(rng.standard_normal(int(.015 * SR)), 3000) * env(T(.015), .0003, .003), rng.uniform(0, .8)) for _ in range(30)])
L['lock'] = lay((kf('metalLatch', 1.0, .9), 0), (kf('switch_006', .8, .4), .05))
L['horn'] = (lambda t: verb(lp(sum(np.sign(np.sin(2 * np.pi * f * t)) * w for f, w in ((73, 1), (110, .6), (146.8, .3))), 700) * np.minimum(1, t / .2) * np.minimum(1, (t[-1] - t) / .5) * .5, 2.0, .45, 2000))(T(2.4))
L['crowd'] = (lambda t: sum(bp(rng.standard_normal(len(t)), f, f * 1.6) * (1 + .6 * np.sin(2 * np.pi * rng.uniform(1.5, 4) * t + rng.uniform(0, 6))) for f in (220, 340, 520, 800)) * np.minimum(1, t / .6) * np.minimum(1, (t[-1] - t) / .8))(T(4.0))
L['cheer'] = (lambda t: verb(sum(bp(rng.standard_normal(len(t)), f, f * 1.5) for f in (400, 700, 1100, 1800)) * np.minimum(1, t / .2) * np.exp(-t / 1.2), 1.0, .3))(T(2.2))
L['hum'] = (lambda t: (sum(np.sin(2 * np.pi * 60 * k * t) / k for k in range(1, 6)) * .3 + lp(rng.standard_normal(len(t)), 400) * .25) * np.minimum(1, t / .5) * np.minimum(1, (t[-1] - t) / .5))(T(5.0))
L['keys'] = lay(*[(kf('switch_00' + str(2 + 2 * (i % 3)), 1.2 + rng.uniform(-.1, .1), .5 + .4 * rng.random())[:int(.05 * SR)], i * .075 + rng.uniform(0, .03)) for i in range(18)])
L['doorbell'] = verb(lay((tone(1.0, 1318, .002, .5, (1, .3, .15), 2.0), 0), (tone(1.0, 1046, .002, .5, (1, .3, .15), 2.0) * .8, .14)), .8, .3, 8000)
L['shutter'] = (lambda t: lp(rng.standard_normal(len(t)), 1800) * (1 + .8 * np.sign(np.sin(2 * np.pi * 22 * t))) * .4 * np.minimum(1, t / .05) * np.minimum(1, (t[-1] - t) / .2))(T(1.4))
L['rattle'] = lay(*[(kf('metalLatch', 1.0 + .1 * (i % 2), .7), i * .16) for i in range(4)])
L['chalk'] = lay(*[(hp(rng.standard_normal(int(.08 * SR)), 2500) * env(T(.08), .01, .03) * .7, i * .12 + rng.uniform(0, .03)) for i in range(7)])
L['wipe'] = (lambda t: bp(rng.standard_normal(len(t)), 500, 3000) * np.abs(np.sin(2 * np.pi * 2.2 * t)) * .7)(T(1.0))
L['cards'] = lay((kf('card-shove-2', 1.0, .9), 0), (kf('card-slide-8', 1.0, .6), .12))
L['sticker'] = lay((kf('scratch_003', 1.4, .7), 0), (kf('impactSoft_heavy_003', 1.4, .5), .1))
L['step'] = kf('footstep_concrete_002', 1.0, .7)
L['bulb'] = lay((kf('switch_002', .8, .9)[:int(.08 * SR)], 0), (tone(1.2, 120, .05, .8, (1, .5)) * .15, .03))
L['chime'] = verb(lay(*[(tone(1.4, f, .002, .7, (1, .3, .1), .8) * .6, i * .12) for i, f in enumerate((784, 988, 1175, 1568))]), 1.4, .4, 9000)
L['lowboom'] = verb(sub(2.2, 80, 30, 1.0), 2.0, .4, 1500)
for n, x in L.items(): save(n, x)
print(len(L), 'sfx')

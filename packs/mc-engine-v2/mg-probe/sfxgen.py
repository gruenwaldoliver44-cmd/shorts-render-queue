"""Synthesized modern UI / motion-graphics SFX set (48 kHz, 16-bit WAV).
Family: clean, short, punchy; all share the same air/sub character so the video has one sonic identity."""
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf, os
SR = 48000
OUT = os.path.join(os.path.dirname(__file__), 'public', 'sfx')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def t(d): return np.arange(int(SR * d)) / SR
def env(n, a=0.005, r=0.2, shape=3.0):
    x = np.linspace(0, 1, n)
    at = int(SR * a); e = np.ones(n)
    if at: e[:at] = np.linspace(0, 1, at)
    e *= (1 - x) ** shape if r is None else np.exp(-x * (1 / max(r, 1e-3)) * 0.2 * n / SR * 10)
    return e
def norm(x, peak=0.9): return x / (np.max(np.abs(x)) + 1e-9) * peak
def save(name, x, peak=0.9):
    x = norm(x, peak); st = np.stack([x, x], 1)
    wf.write(os.path.join(OUT, name + '.wav'), SR, (st * 32767).astype(np.int16))

def bp_sweep(noise, f0, f1, q=2.0, steps=64):
    out = np.zeros_like(noise); n = len(noise); seg = n // steps
    for i in range(steps):
        f = f0 * (f1 / f0) ** (i / (steps - 1))
        lo, hi = max(f / (1 + 1 / q), 30), min(f * (1 + 1 / q), SR / 2 - 100)
        b, a = sg.butter(2, [lo, hi], btype='band', fs=SR)
        s, e = i * seg, (i + 1) * seg if i < steps - 1 else n
        out[s:e] = sg.lfilter(b, a, noise[max(0, s - 512):e])[-(e - s):]
    return out

def whoosh(d=0.45, f0=300, f1=4500, name='whoosh'):
    n = int(SR * d); nz = rng.standard_normal(n)
    x = bp_sweep(nz, f0, f1, q=1.6)
    w = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    save(name, x * w)

def swish(d=0.18, name='swish'):
    n = int(SR * d); nz = rng.standard_normal(n)
    x = bp_sweep(nz, 1500, 9000, q=2.2, steps=24)
    w = np.sin(np.linspace(0, np.pi, n)) ** 0.8 * np.linspace(1, 0.3, n)
    save(name, x * w, 0.7)

def tick(name='tick', f=3200, d=0.03):
    tt = t(d); x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 180) + 0.3 * rng.standard_normal(len(tt)) * np.exp(-tt * 400)
    save(name, x, 0.6)

def blip(name, f0, f1, d=0.12):
    tt = t(d); f = np.linspace(f0, f1, len(tt)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.exp(-tt * 22)
    save(name, x, 0.6)

def impact(name='impact', d=1.4, f0=90, f1=32):
    tt = t(d); f = f0 * (f1 / f0) ** (tt / d); ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-tt * 3.2)
    nz = rng.standard_normal(len(tt)); b, a = sg.butter(2, 900, fs=SR); click = sg.lfilter(b, a, nz) * np.exp(-tt * 40)
    x = sub + 0.6 * click
    x = np.tanh(x * 1.8)
    save(name, x, 0.95)

def slam(name='slam', d=0.6):
    tt = t(d); nz = rng.standard_normal(len(tt)); b, a = sg.butter(2, [120, 2500], btype='band', fs=SR)
    body = sg.lfilter(b, a, nz) * np.exp(-tt * 14)
    sub = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 7)
    save(name, np.tanh(1.5 * (body + sub)), 0.95)

def riser(name='riser', d=1.6):
    tt = t(d); nz = rng.standard_normal(len(tt)); x = bp_sweep(nz, 400, 7000, q=3, steps=80)
    tone = np.sin(2 * np.pi * np.cumsum(np.linspace(180, 720, len(tt))) / SR) * 0.35
    w = (tt / d) ** 2.2
    save(name, (x + tone) * w, 0.8)

def glitch(name='glitch', d=0.35):
    n = int(SR * d); x = np.zeros(n); i = 0
    while i < n:
        L = int(rng.uniform(0.008, 0.04) * SR); kind = rng.integers(0, 3); seg = np.arange(min(L, n - i))
        if kind == 0: x[i:i + len(seg)] = np.sign(np.sin(2 * np.pi * rng.uniform(200, 2000) * seg / SR)) * 0.6
        elif kind == 1: x[i:i + len(seg)] = np.round(rng.standard_normal(len(seg)) * 3) / 3 * 0.5
        else: x[i:i + len(seg)] = 0
        i += len(seg)
    b, a = sg.butter(2, 6000, fs=SR); save(name, sg.lfilter(b, a, x), 0.55)

def digits(name='digits', d=0.6, rate=26):
    n = int(SR * d); x = np.zeros(n); k = int(SR / rate)
    for j in range(0, n - 800, k):
        tt = np.arange(700) / SR; x[j:j + 700] += np.sin(2 * np.pi * rng.uniform(2600, 3400) * tt) * np.exp(-tt * 260)
    save(name, x * np.linspace(1, 0.6, n), 0.45)

def scan(name='scan', d=0.7):
    tt = t(d); f = np.linspace(900, 2400, len(tt)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 30 * tt))) * np.sin(np.linspace(0, np.pi, len(tt)))
    save(name, x, 0.35)

def alarm(name='warn', d=0.9):
    tt = t(d); x = np.sin(2 * np.pi * 880 * tt) * (np.sin(2 * np.pi * 4 * tt) > 0) * np.exp(-tt * 2)
    save(name, x, 0.4)

def heartbeat(name='heart', d=1.0):
    tt = t(d); x = np.zeros_like(tt)
    for s in (0.0, 0.22):
        m = tt >= s; tl = tt[m] - s; x[m] += np.sin(2 * np.pi * 55 * tl) * np.exp(-tl * 18)
    save(name, x, 0.9)

def cash(name='coin', d=0.5):
    tt = t(d); x = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * k) for f, k in ((2093, 8), (3136, 10), (4186, 14)))
    save(name, x, 0.5)

whoosh(); whoosh(0.3, 600, 7000, 'whoosh_short'); whoosh(0.7, 2500, 200, 'whoosh_down')
swish(); tick(); tick('tick_low', 1600, 0.04)
blip('blip_up', 700, 1500); blip('blip_down', 1400, 600); blip('pop', 900, 1300, 0.07)
impact(); slam(); riser(); glitch(); digits(); scan(); alarm(); heartbeat(); cash()
print(sorted(os.listdir(OUT)))

"""Vermisst jedes Stueck der Bibliothek: Lautheit ueber die Zeit, Helligkeit, Dynamik.
Ausgabe analyse.json: pro Stueck rms (dB je 2 s), hell (Spektralschwerpunkt je 2 s)."""
import numpy as np, subprocess, json, glob, os, sys
SR = 22050
out = {}
for f in sorted(glob.glob(sys.argv[1] + '/?_*/*.mp3')):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(o, 'f4').astype(float)
    if len(x) < SR * 5:
        print('kaputt', f); continue
    w = 2 * SR
    n = len(x) // w
    rms, hell = [], []
    for i in range(n):
        s = x[i * w:(i + 1) * w]
        rms.append(20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-6))
        S = np.abs(np.fft.rfft(s * np.hanning(len(s))))
        fr = np.fft.rfftfreq(len(s), 1 / SR)
        hell.append(float((S * fr).sum() / (S.sum() + 1e-9)))
    r = np.array(rms); h = np.array(hell)
    laut = r[r > r.max() - 30]
    out[os.path.relpath(f, sys.argv[1])] = {
        'sek': round(len(x) / SR, 1), 'rms': [round(float(v), 1) for v in r], 'hell': [round(v) for v in h],
        'mittel': round(float(laut.mean()), 1), 'spitze': round(float(r.max()), 1), 'range': round(float(np.percentile(laut, 95) - np.percentile(laut, 10)), 1),
        'hellm': round(float(np.median(h)))}
json.dump(out, open('analyse.json', 'w'))
for k, v in out.items():
    print(f"{k:52} {v['sek']:6.0f}s  {v['mittel']:6.1f} dB  range {v['range']:4.1f}  hell {v['hellm']}")

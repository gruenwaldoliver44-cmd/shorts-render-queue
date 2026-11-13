import {staticFile, Easing, interpolate} from 'remotion';

// "Money Classics OPS" design system: futuristic but disciplined.
// Dark navy world, crisp 1px lines, one accent per meaning, glow only on the single focal element.
export const C = {
  bg0: '#070B16', bg1: '#0C1326', grid: 'rgba(140,170,255,0.06)',
  panel: 'rgba(16,24,46,0.92)', line: '#26345A', lineHi: '#3A4C80',
  text: '#EEF2FF', dim: '#8C9AC4',
  money: '#38E1FF',  // cyan = money moving
  warn: '#FFB224',   // amber = warning / cost
  loss: '#FF3D57',   // red = loss / crash
  gain: '#2FE6A0',   // green = gain / safety
  gold: '#F5C451',
};
export const F = {head: 'SG, sans-serif', mono: 'JBM, monospace'};

export const FontFaces = () => (
  <style>{`
  @font-face{font-family:SG;src:url(${staticFile('fonts/space-grotesk-latin-500-normal.woff2')});font-weight:500}
  @font-face{font-family:SG;src:url(${staticFile('fonts/space-grotesk-latin-700-normal.woff2')});font-weight:700}
  @font-face{font-family:JBM;src:url(${staticFile('fonts/jetbrains-mono-latin-500-normal.woff2')});font-weight:500}
  @font-face{font-family:JBM;src:url(${staticFile('fonts/jetbrains-mono-latin-700-normal.woff2')});font-weight:700}
  `}</style>
);

export const outExpo = Easing.bezier(0.16, 1, 0.3, 1);
export const inOut = Easing.bezier(0.65, 0, 0.35, 1);
// fast snap-in 0..1 over d frames starting at s
export const snap = (f, s, d = 10) => interpolate(f, [s, s + d], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: outExpo});
export const ramp = (f, s, d, e = inOut) => interpolate(f, [s, s + d], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
export const lerp = (a, b, k) => a + (b - a) * k;
export const usd = (v) => '$' + Math.round(v).toLocaleString('en-US');

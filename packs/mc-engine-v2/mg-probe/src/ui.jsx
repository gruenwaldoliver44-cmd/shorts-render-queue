import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate, staticFile, Img} from 'remotion';
import {geoNaturalEarth1, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import world from '../public/countries-110m.json';
import {C, F, snap, ramp, lerp, usd, outExpo} from './theme.js';

/* ---------- background: deep navy, fine grid, slow drift, vignette ---------- */
export const Bg = ({drift = true}) => {
  const f = useCurrentFrame();
  const o = drift ? (f * 0.4) % 60 : 0;
  return (
    <AbsoluteFill style={{background: `radial-gradient(120% 90% at 50% 40%, ${C.bg1} 0%, ${C.bg0} 70%)`}}>
      <AbsoluteFill style={{
        backgroundImage: `linear-gradient(${C.grid} 1px, transparent 1px), linear-gradient(90deg, ${C.grid} 1px, transparent 1px)`,
        backgroundSize: '60px 60px', backgroundPosition: `${o}px ${o}px`,
      }}/>
      <AbsoluteFill style={{background: 'radial-gradient(80% 70% at 50% 50%, transparent 60%, rgba(0,0,0,0.55) 100%)'}}/>
    </AbsoluteFill>
  );
};

/* ---------- HUD panel with corner brackets ---------- */
export const Panel = ({x, y, w, h, k = 1, accent = C.lineHi, children, style}) => {
  const b = 18; const op = k;
  const corner = (pos) => {
    const s = {position: 'absolute', width: b, height: b, borderColor: accent, borderStyle: 'solid', borderWidth: 0};
    if (pos.includes('t')) {s.top = -1; s.borderTopWidth = 2;} else {s.bottom = -1; s.borderBottomWidth = 2;}
    if (pos.includes('l')) {s.left = -1; s.borderLeftWidth = 2;} else {s.right = -1; s.borderRightWidth = 2;}
    return <div style={s}/>;
  };
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: op,
      transform: `translateY(${(1 - k) * 24}px) scale(${0.97 + 0.03 * k})`,
      background: C.panel, border: `1px solid ${C.line}`, borderRadius: 6, ...style}}>
      {corner('tl')}{corner('tr')}{corner('bl')}{corner('br')}
      {children}
    </div>
  );
};

export const Label = ({children, color = C.dim, size = 20, style}) => (
  <div style={{fontFamily: F.mono, fontWeight: 500, fontSize: size, letterSpacing: 3, color, textTransform: 'uppercase', ...style}}>{children}</div>
);

/* ---------- rolling money counter ---------- */
export const Counter = ({keys, size = 96, color = C.text, style}) => {
  // keys: [[frame, value], ...]
  const f = useCurrentFrame();
  let v = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [f0, v0] = keys[i - 1]; const [f1, v1] = keys[i];
    if (f >= f0) v = lerp(v0, v1, ramp(f, f0, Math.max(1, f1 - f0), outExpo));
  }
  return <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: size, color, letterSpacing: -2, ...style}}>{usd(v)}</div>;
};

/* ---------- world map (vector, offline) ---------- */
const land = feature(world, world.objects.countries);
export const W = 1920, H = 1080;
export const proj = geoNaturalEarth1().fitExtent([[60, 120], [1860, 1040]], land);
const pathGen = geoPath(proj);
export const CITIES = {
  ny: {name: 'NEW YORK', ll: [-74.0, 40.7], flag: 'us'},
  tokyo: {name: 'TOKYO', ll: [139.7, 35.7], flag: 'jp'},
  mumbai: {name: 'MUMBAI', ll: [72.9, 19.1], flag: 'in'},
  cairo: {name: 'CAIRO', ll: [31.2, 30.0], flag: 'eg'},
  shanghai: {name: 'SHANGHAI', ll: [121.5, 31.2], flag: 'cn'},
  frankfurt: {name: 'FRANKFURT', ll: [8.7, 50.1], flag: 'eu'},
};
export const pt = (id) => proj(CITIES[id].ll);

export const WorldMap = ({hot = []}) => (
  <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
    {land.features.map((ft, i) => (
      <path key={i} d={pathGen(ft)} fill={hot.includes(ft.id) ? 'rgba(255,61,87,0.25)' : '#121C36'} stroke="#2A3A66" strokeWidth={0.8}/>
    ))}
  </svg>
);

/* arc between two cities, drawn progressively, k 0..1 */
export const Arc = ({a, b, k, color = C.loss, lift = 0.28}) => {
  const [x1, y1] = pt(a), [x2, y2] = pt(b);
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - Math.hypot(x2 - x1, y2 - y1) * lift;
  const d = `M${x1},${y1} Q${mx},${my} ${x2},${y2}`;
  const L = Math.hypot(x2 - x1, y2 - y1) * 1.25;
  // moving head
  const tt = Math.min(1, k);
  const hx = (1 - tt) ** 2 * x1 + 2 * (1 - tt) * tt * mx + tt ** 2 * x2;
  const hy = (1 - tt) ** 2 * y1 + 2 * (1 - tt) * tt * my + tt ** 2 * y2;
  return (
    <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <path d={d} fill="none" stroke={color} strokeWidth={3} strokeDasharray={L} strokeDashoffset={L * (1 - k)} strokeLinecap="round" opacity={0.95}/>
      {k > 0 && k < 1 && <circle cx={hx} cy={hy} r={7} fill={color} style={{filter: `drop-shadow(0 0 10px ${color})`}}/>}
    </svg>
  );
};

/* city node with flag + label, pops in at k, pulses when hot */
export const City = ({id, k = 1, hot = 0, labelSide = 'r'}) => {
  const f = useCurrentFrame();
  const [x, y] = pt(id); const c = CITIES[id];
  const pulse = hot ? (f % 30) / 30 : 0;
  const col = hot ? C.loss : C.money;
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: k, transform: `scale(${0.6 + 0.4 * k})`}}>
      {hot ? <div style={{position: 'absolute', left: -6 - 30 * pulse, top: -6 - 30 * pulse, width: 12 + 60 * pulse, height: 12 + 60 * pulse,
        borderRadius: '50%', border: `2px solid ${col}`, opacity: 1 - pulse}}/> : null}
      <div style={{position: 'absolute', left: -7, top: -7, width: 14, height: 14, borderRadius: '50%', background: col, boxShadow: hot ? `0 0 16px ${col}` : 'none'}}/>
      <div style={{position: 'absolute', top: -22, [labelSide === 'r' ? 'left' : 'right']: 18, display: 'flex', alignItems: 'center', gap: 10,
        flexDirection: labelSide === 'r' ? 'row' : 'row-reverse', whiteSpace: 'nowrap'}}>
        <Img src={staticFile(`flags/${c.flag}.svg`)} style={{width: 44, height: 33, borderRadius: 3, border: '1px solid rgba(255,255,255,0.25)'}}/>
        <Label color={C.text} size={22}>{c.name}</Label>
      </div>
    </div>
  );
};

/* term explainer tag: short definition card with pointer line */
export const Term = ({x, y, k, term, def, color = C.money, w = 520}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, opacity: k, transform: `translateX(${(1 - k) * -30}px)`}}>
    <div style={{borderLeft: `4px solid ${color}`, background: 'rgba(8,14,30,0.94)', padding: '16px 22px', borderRadius: 4}}>
      <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: 24, color, letterSpacing: 3}}>{term}</div>
      <div style={{fontFamily: F.head, fontWeight: 500, fontSize: 28, color: C.text, marginTop: 6, lineHeight: 1.25}}>{def}</div>
    </div>
  </div>
);

/* scan-line wipe transition overlay: bright line sweeping left->right over d frames from s */
export const ScanWipe = ({s, d = 14, color = C.money}) => {
  const f = useCurrentFrame(); const k = ramp(f, s, d, outExpo);
  if (f < s || f > s + d + 4) return null;
  const x = k * (W + 200) - 100;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: x, height: H, background: 'rgba(7,11,22,0.0)'}}/>
      <div style={{position: 'absolute', left: x - 2, top: 0, width: 4, height: H, background: color, boxShadow: `0 0 30px 6px ${color}`}}/>
      <div style={{position: 'absolute', left: x - 160, top: 0, width: 160, height: H, background: `linear-gradient(90deg, transparent, ${color}22)`}}/>
    </AbsoluteFill>
  );
};

/* glitch slice for crash moments */
export const Glitch = ({s, d = 8, children}) => {
  const f = useCurrentFrame(); const on = f >= s && f < s + d;
  const off = on ? ((f * 37) % 23) - 11 : 0;
  return <div style={{position: 'absolute', inset: 0, transform: `translateX(${off}px)`, filter: on ? 'hue-rotate(-20deg) saturate(1.6)' : 'none'}}>{children}</div>;
};

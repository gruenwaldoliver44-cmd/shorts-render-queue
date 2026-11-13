import React from 'react';
import {AbsoluteFill, Img, staticFile, interpolate} from 'remotion';
import {geoNaturalEarth1, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import world from '../public/countries-110m.json';
import {C, F, outExpo, inOut} from './theme.js';

/* ================= helpers (all take absolute frame g) ================= */
const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
export const sn = (g, s, d = 10) => interpolate(g, [s, s + d], [0, 1], {...cl, easing: outExpo});
export const rp = (g, s, d, e = inOut) => interpolate(g, [s, s + Math.max(1, d)], [0, 1], {...cl, easing: e});
const lerp = (a, b, k) => a + (b - a) * k;
const usd = (v) => '$' + Math.round(v).toLocaleString('en-US');
// keyframes [[g,v],...] eased
export const kv = (K, g, e = outExpo, d = null) => {
  let v = K[0][1];
  for (let i = 1; i < K.length; i++) {
    const [f0, v0] = K[i - 1], [f1, v1] = K[i];
    const dd = d || Math.max(1, Math.min(24, f1 - f0));
    if (g >= f1) v = lerp(v0, v1, rp(g, f1, dd, e)); else break;
  }
  return v;
};
const lastOf = (K, g, def) => {let v = def; for (const k of K || []) {if (g >= k[0]) v = k[1]; else break;} return v;};
const outk = (o, g) => (o.t1 ? 1 - sn(g, o.t1 - 8, 8) : 1);
const vis = (o, g) => g >= o.t && !(o.t1 && g >= o.t1);

/* ================= background ================= */
export const MgBg = ({g}) => {
  const o = (g * 0.4) % 60;
  return (
    <AbsoluteFill style={{background: `radial-gradient(120% 90% at 50% 40%, ${C.bg1} 0%, ${C.bg0} 70%)`}}>
      <AbsoluteFill style={{backgroundImage: `linear-gradient(${C.grid} 1px, transparent 1px), linear-gradient(90deg, ${C.grid} 1px, transparent 1px)`,
        backgroundSize: '60px 60px', backgroundPosition: `${o}px ${o}px`}}/>
      <AbsoluteFill style={{background: 'radial-gradient(80% 70% at 50% 50%, transparent 60%, rgba(0,0,0,0.55) 100%)'}}/>
    </AbsoluteFill>
  );
};

export const Lbl = ({children, color = C.dim, size = 22, style}) => (
  <div style={{fontFamily: F.mono, fontWeight: 500, fontSize: size, letterSpacing: size * 0.14, color, textTransform: 'uppercase', whiteSpace: 'nowrap', ...style}}>{children}</div>
);
export const Pnl = ({x, y, w, h, k = 1, accent = C.lineHi, children, style, glow}) => {
  const b = 18;
  const corner = (pos) => {
    const s = {position: 'absolute', width: b, height: b, borderColor: accent, borderStyle: 'solid', borderWidth: 0};
    if (pos[0] === 't') {s.top = -1; s.borderTopWidth = 3;} else {s.bottom = -1; s.borderBottomWidth = 3;}
    if (pos[1] === 'l') {s.left = -1; s.borderLeftWidth = 3;} else {s.right = -1; s.borderRightWidth = 3;}
    return <div key={pos} style={s}/>;
  };
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: k,
      transform: `translateY(${(1 - k) * 24}px) scale(${0.97 + 0.03 * k})`, background: C.panel, border: `1px solid ${C.line}`,
      borderRadius: 6, boxShadow: glow ? `0 0 34px ${glow}55` : '0 18px 40px rgba(0,0,0,.45)', ...style}}>
      {['tl', 'tr', 'bl', 'br'].map(corner)}{children}
    </div>
  );
};

/* ================= icons (100x100 line art) ================= */
const IP = {
  house: 'M10 46 L50 12 L90 46 M20 38 L20 90 L80 90 L80 38 M40 90 L40 64 L60 64 L60 90',
  car: 'M8 64 L18 40 Q22 32 32 32 L68 32 Q78 32 82 40 L92 64 L92 78 L8 78 Z M18 64 L82 64 M26 78 a9 9 0 1 0 0.1 0 M74 78 a9 9 0 1 0 0.1 0',
  card: 'M6 24 L94 24 Q98 24 98 28 L98 76 Q98 80 94 80 L6 80 Q2 80 2 76 L2 28 Q2 24 6 24 Z M2 38 L98 38 M12 64 L36 64',
  chip: 'M24 24 H76 V76 H24 Z M36 36 H64 V64 H36 Z M32 24 V12 M44 24 V12 M56 24 V12 M68 24 V12 M32 76 V88 M44 76 V88 M56 76 V88 M68 76 V88 M24 32 H12 M24 44 H12 M24 56 H12 M24 68 H12 M76 32 H88 M76 44 H88 M76 56 H88 M76 68 H88',
  gold: 'M10 76 L24 50 L76 50 L90 76 Z M28 50 L38 30 L62 30 L72 50 M10 76 L90 76',
  bread: 'M12 62 Q12 34 50 34 Q88 34 88 62 L88 72 Q88 76 84 76 L16 76 Q12 76 12 72 Z M34 42 L40 54 M50 40 L54 54 M66 42 L68 54',
  ship: 'M8 64 L92 64 L80 84 L20 84 Z M20 64 L20 50 L44 50 L44 64 M44 64 L44 44 L66 44 L66 64 M70 64 V34 H82 V64',
  truck: 'M6 30 H60 V70 H6 Z M60 44 H80 L92 58 V70 H60 M22 76 a8 8 0 1 0 0.1 0 M76 76 a8 8 0 1 0 0.1 0',
  warehouse: 'M8 40 L50 16 L92 40 V88 H8 Z M24 88 V56 H76 V88 M24 66 H76 M24 76 H76',
  job: 'M50 14 a14 14 0 1 0 0.1 0 M24 88 Q24 52 50 52 Q76 52 76 88 Z M34 22 Q50 4 66 22',
  oil: 'M26 16 H74 V88 H26 Z M26 34 H74 M26 70 H74 M44 16 V10 H56 V16',
  wheat: 'M50 92 V30 M50 30 Q38 22 40 10 Q52 16 50 30 M50 46 Q36 40 34 28 Q48 30 50 46 M50 46 Q64 40 66 28 Q52 30 50 46 M50 62 Q36 56 34 44 Q48 46 50 62 M50 62 Q64 56 66 44 Q52 46 50 62',
  factory: 'M8 88 V44 L30 56 V44 L52 56 V44 L74 56 V20 H88 V88 Z M20 74 H32 M44 74 H56 M68 74 H80',
  army: 'M50 8 L86 22 V48 Q86 76 50 92 Q14 76 14 48 V22 Z M36 50 L46 60 L66 38',
  trust: 'M8 52 L28 34 L46 44 L56 38 L92 56 M28 34 L8 34 M92 56 L92 40 L72 34 M40 58 L50 66 M48 52 L60 62 M58 48 L70 58 M30 62 L40 70',
  bank: 'M8 34 L50 12 L92 34 Z M14 40 H86 M20 46 V78 M38 46 V78 M62 46 V78 M80 46 V78 M10 84 H90',
  shield: 'M50 8 L86 22 V48 Q86 76 50 92 Q14 76 14 48 V22 Z',
  printer: 'M24 40 V12 H76 V40 M12 40 H88 V74 H12 Z M24 62 H76 V92 H24 Z M34 72 H66 M34 82 H58',
  coin: 'M50 14 a36 36 0 1 0 0.1 0 M50 24 a26 26 0 1 0 0.1 0 M50 34 V66 M60 40 Q50 32 42 40 Q38 50 50 50 Q62 50 58 60 Q50 68 40 60',
  basket: 'M10 40 H90 L80 86 H20 Z M30 40 L44 14 M70 40 L56 14 M36 52 L38 76 M50 52 V76 M64 52 L62 76',
  mail: 'M6 24 H94 V80 H6 Z M6 24 L50 56 L94 24',
  trophy: 'M30 12 H70 V36 Q70 58 50 58 Q30 58 30 36 Z M30 20 H14 Q14 42 32 44 M70 20 H86 Q86 42 68 44 M50 58 V74 M34 88 H66 V74 H34 Z',
  lock: 'M24 46 H76 V88 H24 Z M34 46 V32 Q34 14 50 14 Q66 14 66 32 V46 M50 60 V72',
  unlock: 'M24 46 H76 V88 H24 Z M34 46 V32 Q34 14 50 14 Q66 14 66 28 M50 60 V72',
  pump: 'M18 90 V18 Q18 12 24 12 H56 Q62 12 62 18 V90 Z M14 90 H66 M26 22 H54 V42 H26 Z M62 36 L76 42 V74 Q76 80 82 80 Q88 80 88 74 V40 L80 30',
  cart: 'M6 18 H20 L32 66 H80 L90 32 H24 M36 80 a6 6 0 1 0 0.1 0 M74 80 a6 6 0 1 0 0.1 0',
  heater: 'M12 26 V80 M88 26 V80 M12 30 H88 M12 76 H88 M24 30 V76 M38 30 V76 M50 30 V76 M62 30 V76 M76 30 V76 M18 80 V88 M82 80 V88',
  flame: 'M50 8 Q72 34 70 56 Q68 86 50 90 Q32 86 30 60 Q30 46 40 36 Q42 52 50 54 Q46 32 50 8 Z',
  sack: 'M36 18 H64 L58 30 Q86 44 84 70 Q82 90 50 90 Q18 90 16 70 Q14 44 42 30 Z M40 30 H60',
  dollar: 'M50 8 V92 M70 26 Q62 16 50 16 Q30 16 30 32 Q30 46 50 50 Q70 54 70 68 Q70 84 50 84 Q36 84 28 74',
  people: 'M30 22 a11 11 0 1 0 0.1 0 M70 22 a11 11 0 1 0 0.1 0 M10 80 Q10 48 30 48 Q50 48 50 80 M50 80 Q50 48 70 48 Q90 48 90 80',
  paycheck: 'M8 22 H92 V78 H8 Z M18 36 H54 M18 48 H44 M18 64 H82 M66 36 H82 V50 H66 Z',
  hammer: 'M16 30 L46 10 L60 30 L30 50 Z M44 40 L84 88',
  globe: 'M50 10 a40 40 0 1 0 0.1 0 M10 50 H90 M50 10 Q28 50 50 90 M50 10 Q72 50 50 90 M18 28 H82 M18 72 H82',
  plane: 'M50 8 Q56 8 56 18 V40 L90 60 V68 L56 58 V80 L66 88 V92 L50 88 L34 92 V88 L44 80 V58 L10 68 V60 L44 40 V18 Q44 8 50 8 Z',
  phone: 'M28 6 H72 V94 H28 Z M28 16 H72 M28 82 H72 M46 88 H54',
  stocks: 'M10 90 H92 M18 90 V60 H32 V90 M40 90 V44 H54 V90 M62 90 V30 H76 V90 M14 52 L38 34 L58 42 L88 12 M74 12 H88 V26',
  calendar: 'M10 20 H90 V90 H10 Z M10 38 H90 M30 10 V28 M70 10 V28 M24 52 H36 M46 52 H58 M68 52 H80 M24 70 H36 M46 70 H58',
  arrowup: 'M50 90 V14 M24 40 L50 12 L76 40',
  arrowdn: 'M50 10 V86 M24 60 L50 88 L76 60',
  warn: 'M50 10 L92 86 H8 Z M50 38 V62 M50 72 V76',
  bulb: 'M50 10 Q76 10 76 38 Q76 52 62 64 V74 H38 V64 Q24 52 24 38 Q24 10 50 10 Z M38 82 H62 M42 90 H58',
};
export const Ico = ({k, s = 120, col = C.text, sw = 4, fill}) => (
  <svg width={s} height={s} viewBox="0 0 100 100" style={{overflow: 'visible'}}>
    <path d={IP[k] || IP.dollar} fill={fill || 'none'} stroke={col} strokeWidth={sw} strokeLinejoin="round" strokeLinecap="round"/>
  </svg>
);

/* ================= map ================= */
const land = feature(world, world.objects.countries);
export const proj = geoNaturalEarth1().fitExtent([[60, 120], [1860, 1040]], land);
const pathGen = geoPath(proj);
const PATHS = land.features.map((ft) => [ft.id, pathGen(ft)]);
export const CITIES = {
  ny: ['NEW YORK', [-74.0, 40.7], 'us'], tokyo: ['TOKYO', [139.7, 35.7], 'jp'], mumbai: ['MUMBAI', [72.9, 19.1], 'in'],
  cairo: ['CAIRO', [31.2, 30.0], 'eg'], shanghai: ['SHANGHAI', [121.5, 31.2], 'cn'], frankfurt: ['FRANKFURT', [8.7, 50.1], 'de'],
  london: ['LONDON', [-0.1, 51.5], 'gb'], virginia: ['VIRGINIA', [-77.5, 39.0], 'us'], ohio: ['OHIO', [-82.9, 40.0], 'us'],
  vienna: ['VIENNA', [16.4, 48.2], 'at'], berlin: ['BERLIN', [13.4, 52.5], 'de'], moscow: ['MOSCOW', [37.6, 55.8], 'ru'],
  washington: ['WASHINGTON', [-77.0, 38.9], 'us'], brettonwoods: ['BRETTON WOODS', [-71.4, 44.26], 'us'], riyadh: ['RIYADH', [46.7, 24.7], 'sa'],
  paris: ['PARIS', [2.35, 48.86], 'fr'], hormuz: ['STRAIT OF HORMUZ', [56.3, 26.6], 'ir'], sydney: ['SYDNEY', [151.2, -33.9], 'au'],
  saopaulo: ['SÃO PAULO', [-46.6, -23.5], 'br'], lagos: ['LAGOS', [3.4, 6.5], 'ng'], mexico: ['MEXICO CITY', [-99.1, 19.4], 'mx'], toronto: ['TORONTO', [-79.4, 43.7], 'ca'],
};
export const pt = (id) => (Array.isArray(id) ? id : proj(CITIES[id][1]));

export const MapW = ({o, g}) => {
  if (!vis(o, g)) return null;
  const K = o.cam || [[o.t, [960, 560], 1]];
  // camera: eased between keys
  let fx = pt(K[0][1])[0], fy = pt(K[0][1])[1], z = K[0][2];
  for (let i = 1; i < K.length; i++) {
    const [g1, c1, z1, d1] = K[i]; if (g < g1) break;
    const k = rp(g, g1, d1 || 26); const p = pt(c1);
    fx = lerp(fx, p[0], k); fy = lerp(fy, p[1], k); z = lerp(z, z1, k);
  }
  const hot = {}; for (const [id, at, col] of o.hot || []) if (g >= at) hot[id] = [col || C.loss, sn(g, at, 14)];
  const op = sn(g, o.t, 12) * outk(o, g);
  const sep = o.sepia;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: op, filter: sep ? 'sepia(.85) saturate(.7) brightness(.95)' : undefined}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0',
        transform: `translate(${960 - fx * z}px, ${540 - fy * z}px) scale(${z})`}}>
        <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
          {PATHS.map(([id, d], i) => {
            const h = hot[id];
            return <path key={i} d={d} fill={h ? h[0] : '#121C36'} fillOpacity={h ? 0.12 + 0.2 * h[1] : 1} stroke={h ? h[0] : '#2A3A66'} strokeWidth={(h ? 1.6 : 0.8) / Math.sqrt(z)}/>;
          })}
          {(o.arcs || []).map(([a, b, at, col, d], i) => {
            const k = rp(g, at, d || 30); if (k <= 0) return null;
            const [x1, y1] = pt(a), [x2, y2] = pt(b);
            const L0 = Math.hypot(x2 - x1, y2 - y1), mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - L0 * 0.28;
            const L = L0 * 1.25, cc = col || C.loss;
            const hx = (1 - k) ** 2 * x1 + 2 * (1 - k) * k * mx + k * k * x2, hy = (1 - k) ** 2 * y1 + 2 * (1 - k) * k * my + k * k * y2;
            return <g key={i}><path d={`M${x1},${y1} Q${mx},${my} ${x2},${y2}`} fill="none" stroke={cc} strokeWidth={3 / Math.sqrt(z)} strokeDasharray={L} strokeDashoffset={L * (1 - k)} strokeLinecap="round"/>
              {k < 1 ? <circle cx={hx} cy={hy} r={7 / Math.sqrt(z)} fill={cc} style={{filter: `drop-shadow(0 0 10px ${cc})`}}/> : null}</g>;
          })}
          {(o.rings || []).map(([c, at, col], i) => {
            const [x, y] = pt(c); const out = [];
            for (let j = 0; j < 3; j++) {const d = (g - at - j * 12); if (d < 0) continue; const q = (d % 48) / 48; out.push(<circle key={j} cx={x} cy={y} r={(10 + q * 140) / Math.sqrt(z)} fill="none" stroke={col || C.loss} strokeWidth={2.5 / Math.sqrt(z)} opacity={1 - q}/>);}
            return <g key={i}>{out}</g>;
          })}
        </svg>
        {(o.cities || []).map(([id, at, hotAt, side, col], i) => {
          const k = sn(g, at, 10); if (k <= 0) return null;
          const [x, y] = pt(id); const c = CITIES[id] || [id, null, null];
          const isHot = hotAt != null && g >= hotAt; const cc = col || (isHot ? C.loss : C.money);
          const pulse = isHot ? ((g - hotAt) % 30) / 30 : 0; const s = 1 / z;
          return (
            <div key={i} style={{position: 'absolute', left: x, top: y, opacity: k, transform: `scale(${s * (0.6 + 0.4 * k)})`, transformOrigin: '0 0'}}>
              {isHot ? <div style={{position: 'absolute', left: -6 - 30 * pulse, top: -6 - 30 * pulse, width: 12 + 60 * pulse, height: 12 + 60 * pulse, borderRadius: '50%', border: `2px solid ${cc}`, opacity: 1 - pulse}}/> : null}
              <div style={{position: 'absolute', left: -8, top: -8, width: 16, height: 16, borderRadius: '50%', background: cc, boxShadow: `0 0 16px ${cc}`}}/>
              <div style={{position: 'absolute', top: -24, [side === 'l' ? 'right' : 'left']: 20, display: 'flex', alignItems: 'center', gap: 10, flexDirection: side === 'l' ? 'row-reverse' : 'row', whiteSpace: 'nowrap'}}>
                {c[2] ? <Img src={staticFile(`flags/${c[2]}.svg`)} style={{width: 48, height: 36, borderRadius: 3, border: '1px solid rgba(255,255,255,0.3)'}}/> : null}
                <Lbl color={C.text} size={24}>{c[0]}</Lbl>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/* ================= HUD: your fund (persistent red thread) ================= */
export const Hud = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = o.now ? 1 : sn(g, o.t, 12); const v = kv(o.keys, g, outExpo, 22);
  const big = o.big; const W = o.w || (big ? 860 : 460), H = big ? 400 : 168;
  const base = o.base || 10000; const col = v < base - 1 ? C.loss : C.text;
  const d = v - base; const sub = lastOf(o.sub, g, '');
  const lock = o.lock; const lk = lock ? (g >= lock[0] ? (lock[1] != null && g >= lock[1] ? 'unlock' : 'lock') : null) : null;
  const pulse = o.pulse && g >= o.pulse[0] && g < o.pulse[1] ? 1 + Math.sin((g - o.pulse[0]) * 0.22) * 0.025 : 1;
  const spark = o.spark;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: outk(o, g)}}>
      <Pnl x={o.x ?? 1400} y={o.y ?? 48} w={W} h={H} k={k} accent={col === C.loss ? C.loss : C.lineHi} glow={col === C.loss ? C.loss : null} style={{transform: `scale(${pulse})`}}>
        <Lbl style={{position: 'absolute', left: 26, top: big ? 30 : 20}} size={big ? 28 : 19}>{o.label || 'YOUR RETIREMENT FUND'}</Lbl>
        {lk ? <div style={{position: 'absolute', right: 20, top: big ? 22 : 14, display: 'flex', alignItems: 'center', gap: 8}}>
          <Lbl color={C.warn} size={big ? 24 : 17}>{lk === 'lock' ? 'REMEMBER' : 'UNLOCKED'}</Lbl><Ico k={lk} s={big ? 46 : 34} col={C.warn} sw={7}/></div> : null}
        <div style={{position: 'absolute', left: 26, top: big ? 80 : 50, fontFamily: F.mono, fontWeight: 700, fontSize: big ? 150 : 74, color: col, letterSpacing: -2}}>{usd(v)}</div>
        <div style={{position: 'absolute', left: 30, top: big ? 268 : 130, fontFamily: F.mono, fontSize: big ? 36 : 20, color: d < -1 ? C.loss : d > 1 ? C.gain : C.dim}}>
          {Math.abs(d) < 1 ? 'START' : (d < 0 ? '▼ ' : '▲ ') + usd(Math.abs(d))}{sub ? <span style={{color: C.dim}}>{'  ·  ' + sub}</span> : null}
        </div>
        {spark && big ? <svg width={W - 60} height={70} style={{position: 'absolute', left: 30, top: 318}} viewBox="0 0 480 60" preserveAspectRatio="none">
          <polyline fill="none" stroke={col} strokeWidth="3" strokeDasharray="700" strokeDashoffset={700 * (1 - rp(g, o.t + 6, 50))} points="0,8 60,12 100,8 160,28 220,24 280,40 340,36 400,52 480,56"/></svg> : null}
      </Pnl>
    </div>
  );
};

/* ================= chapter ticker ================= */
export const Tick = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 12); const wipe = rp(g, o.t, 14, outExpo);
  const blink = g - o.t < 30 ? (Math.floor((g - o.t) / 4) % 2) : 1;
  return (
    <div style={{position: 'absolute', left: o.x ?? 56, top: o.y ?? 50, opacity: k * outk(o, g), display: 'flex', alignItems: 'center', gap: 14,
      clipPath: `inset(0 ${100 - wipe * 100}% 0 0)`}}>
      <div style={{width: 14, height: 14, borderRadius: '50%', background: o.col || C.loss, opacity: blink, boxShadow: `0 0 12px ${o.col || C.loss}`}}/>
      <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: o.size || 34, color: C.text, letterSpacing: 5, background: 'rgba(7,11,22,.86)', padding: '8px 18px', border: `1px solid ${C.lineHi}`, borderLeft: `4px solid ${o.col || C.loss}`}}>{o.txt}</div>
      {o.sub ? <Lbl color={C.dim} size={22}>{o.sub}</Lbl> : null}
    </div>
  );
};

/* ================= term explainer card ================= */
export const TermC = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 12) * outk(o, g); const col = o.col || C.money;
  return (
    <div style={{position: 'absolute', left: o.x ?? 90, top: o.y ?? 790, width: o.w || 620, opacity: k, transform: `translateX(${(1 - k) * -40}px)`}}>
      <div style={{borderLeft: `5px solid ${col}`, background: 'rgba(8,14,30,0.95)', padding: '18px 24px', borderRadius: 4, boxShadow: '0 16px 40px rgba(0,0,0,.5)'}}>
        <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: 26, color: col, letterSpacing: 3}}>{o.term}</div>
        <div style={{fontFamily: F.head, fontWeight: 500, fontSize: o.fs || 30, color: C.text, marginTop: 8, lineHeight: 1.25}}>{o.def}</div>
      </div>
    </div>
  );
};

/* ================= generic stat panel with optional slash to new value ================= */
export const Stat = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 12) * outk(o, g); const col = o.col || C.text;
  const sl = o.slash ? rp(g, o.slash[0], 8, outExpo) : 0; const nk = o.slash ? sn(g, o.slash[0] + 6, 10) : 0;
  const cnt = o.count ? kv(o.count, g, outExpo, o.cd || 30) : null;
  const val = cnt != null ? (o.fmt === 'pct' ? Math.round(cnt) + '%' : o.fmt === 'raw' ? (o.pre || '') + Math.round(cnt).toLocaleString('en-US') + (o.suf || '') : (o.pre || '') + usd(cnt).slice(1) + (o.suf || '')) : o.val;
  const S = o.size || 120;
  return (
    <div style={{position: 'absolute', left: o.x, top: o.y, opacity: k, transform: `translateY(${(1 - k) * 30}px)`, textAlign: o.center ? 'center' : 'left', ...(o.panel ? {background: C.panel, border: `1px solid ${C.lineHi}`, borderLeft: `5px solid ${C.money}`, padding: '26px 36px', borderRadius: 6, boxShadow: '0 20px 50px rgba(0,0,0,.5)'} : {}), width: o.center ? o.w || 900 : undefined, marginLeft: o.center ? -(o.w || 900) / 2 : 0}}>
      {o.label ? <Lbl color={o.lcol || C.dim} size={o.ls || 26}>{o.label}</Lbl> : null}
      <div style={{position: 'relative', display: 'inline-block', marginTop: 6}}>
        <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: S, color: sl > 0.5 ? C.dim : col, letterSpacing: -2, lineHeight: 1.05, textShadow: o.glow ? `0 0 30px ${col}88` : 'none'}}>{val}</div>
        {o.slash ? <div style={{position: 'absolute', left: -10, top: S * 0.5, height: S * 0.08, width: `${sl * 106}%`, background: C.loss, transform: 'rotate(-6deg)', boxShadow: `0 0 18px ${C.loss}`}}/> : null}
      </div>
      {o.slash ? <div style={{opacity: nk, transform: `translateY(${(1 - nk) * 24}px)`, marginTop: 6}}>
        {o.slash[2] ? <Lbl color={C.loss} size={o.ls || 26}>{o.slash[2]}</Lbl> : null}
        <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: S * 1.3, color: C.loss, letterSpacing: -2, lineHeight: 1.05}}>{o.slash[1]}</div></div> : null}
      {o.sub ? <div style={{fontFamily: F.head, fontWeight: 500, fontSize: o.ss || 32, color: o.scol || C.dim, marginTop: 8, opacity: o.subAt ? sn(g, o.subAt, 10) : 1}}>{o.sub}</div> : null}
    </div>
  );
};

/* ================= clocks row ================= */
export const Clocks = ({o, g}) => {
  if (!vis(o, g)) return null;
  return <>{o.items.map(([city, flag, h, m, at, jumpAt, hotCol], i) => {
    const k = sn(g, at, 10) * outk(o, g); const jumped = jumpAt != null && g >= jumpAt; const mm = jumped ? m + 1 : m;
    const hot = jumped; const x = (o.x ?? 110) + i * (o.gap || 590);
    const sc = jumped ? 1 + 0.06 * (1 - sn(g, jumpAt, 10)) : 1;
    return (
      <Pnl key={i} x={x} y={o.y ?? 60} w={520} h={150} k={k} accent={hot ? (hotCol || C.loss) : C.lineHi} glow={hot ? (hotCol || C.loss) : null} style={{transform: `scale(${sc})`}}>
        <div style={{position: 'absolute', left: 28, top: 24, display: 'flex', alignItems: 'center', gap: 14}}>
          <Img src={staticFile(`flags/${flag}.svg`)} style={{width: 48, height: 36, borderRadius: 3}}/><Lbl color={C.dim} size={23}>{city}</Lbl>
        </div>
        <div style={{position: 'absolute', left: 28, top: 64, fontFamily: F.mono, fontWeight: 700, fontSize: 66, color: hot ? (hotCol || C.loss) : C.text}}>
          {String(h).padStart(2, '0')}<span style={{opacity: (g % 30) < 15 ? 1 : 0.35}}>:</span>{String(mm).padStart(2, '0')}
        </div>
        {o.tags && o.tags[i] ? <div style={{position: 'absolute', right: 22, top: 84, opacity: sn(g, o.tags[i][1], 8)}}><Lbl color={o.tags[i][2] || C.dim} size={22}>{o.tags[i][0]}</Lbl></div> : null}
      </Pnl>
    );
  })}</>;
};

/* ================= S&P concentration bar ================= */
export const SpBar = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const fill = rp(g, o.t + 8, 36, outExpo); const red = o.red && g >= o.red;
  const P = o.pct || 36;
  return (
    <div style={{position: 'absolute', left: 120, top: o.y ?? 160, opacity: k}}>
      <Lbl size={28}>{o.label || 'S&P 500 · 500 BIGGEST US COMPANIES · BY SIZE'}</Lbl>
      <div style={{marginTop: 16, width: 1680, height: 170, display: 'flex', borderRadius: 6, overflow: 'hidden', border: `1px solid ${C.line}`}}>
        <div style={{width: `${P * fill}%`, background: `linear-gradient(90deg, ${red ? C.loss : C.money}, ${red ? '#b02a3e' : '#1d8fb0'})`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <span style={{fontFamily: F.mono, fontWeight: 700, fontSize: 44, whiteSpace: 'nowrap', color: '#04101c', opacity: sn(g, o.t + 36)}}>{o.txt || '7 COMPANIES · 36%'}</span>
        </div>
        <div style={{flex: 1, backgroundImage: 'repeating-linear-gradient(90deg, #1a2648 0 3px, transparent 3px 6px)'}}/>
      </div>
      <Lbl style={{marginLeft: 1680 * P / 100 + 24, marginTop: 14, opacity: sn(g, o.t + 44)}} color={C.dim} size={22}>{o.rest || 'THE OTHER 493'}</Lbl>
    </div>
  );
};

/* ================= line chart ================= */
export const Chart = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const P = o.pts; const W = o.w || 1500, H = o.h || 560; const X = o.x ?? 210, Y = o.y ?? 260;
  const ys = P.map((p) => p[1]); const lo = o.lo ?? Math.min(...ys), hi = o.hi ?? Math.max(...ys);
  const px = (i) => (i / (P.length - 1)) * W, py = (v) => H - ((v - lo) / (hi - lo || 1)) * H;
  const prog = rp(g, o.t + (o.delay || 6), o.d || 50, o.lin ? (x) => x : inOut);
  const n = prog * (P.length - 1); const ni = Math.floor(n);
  let pts = []; for (let i = 0; i <= ni; i++) pts.push([px(i), py(P[i][1])]);
  if (ni < P.length - 1) {const f = n - ni; pts.push([lerp(px(ni), px(ni + 1), f), lerp(py(P[ni][1]), py(P[ni + 1][1]), f)]);}
  const head = pts[pts.length - 1]; const col = o.col || C.loss;
  const curV = ni < P.length - 1 ? lerp(P[ni][1], P[ni + 1][1], n - ni) : P[P.length - 1][1];
  const fmt = (v) => (o.fmt ? o.fmt.replace('{}', (o.dec != null ? v.toFixed(o.dec) : Math.round(v).toLocaleString('en-US'))) : Math.round(v).toLocaleString('en-US'));
  const tv = o.tv; // tv mode: compact, no frame labels
  return (
    <div style={{position: 'absolute', left: X, top: Y, width: W, height: H, opacity: k}}>
      {!tv ? <Lbl style={{position: 'absolute', left: 0, top: -64}} size={28} color={C.dim}>{o.title}</Lbl> : null}
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {[0, 0.25, 0.5, 0.75, 1].map((q, i) => <line key={i} x1={0} x2={W} y1={H * q} y2={H * q} stroke={C.line} strokeWidth={1}/>)}
        {o.base != null ? <line x1={0} x2={W} y1={py(o.base)} y2={py(o.base)} stroke={C.dim} strokeWidth={2} strokeDasharray="8 8"/> : null}
        {o.ghost ? <polyline fill="none" stroke={C.dim} strokeOpacity={0.45} strokeWidth={3} points={o.ghost.map((v, i) => `${(i / (o.ghost.length - 1)) * W},${py(v)}`).join(' ')}/> : null}
        <polygon points={`0,${H} ${pts.map((p) => p.join(',')).join(' ')} ${head[0]},${H}`} fill={col} fillOpacity={0.12}/>
        <polyline fill="none" stroke={col} strokeWidth={tv ? 6 : 5} strokeLinejoin="round" points={pts.map((p) => p.join(',')).join(' ')} style={{filter: `drop-shadow(0 0 8px ${col})`}}/>
        <circle cx={head[0]} cy={head[1]} r={tv ? 11 : 9} fill={col}/>
      </svg>
      {(o.marks || []).map(([i, txt, mc, side], j) => {
        if (n < i - 0.01) return null; const mk = sn(g, o.t + (o.delay || 6) + (o.d || 50) * i / (P.length - 1), 8);
        const x = px(i), y = py(P[i][1]); const up = side === 'u';
        return <div key={j} style={{position: 'absolute', left: x, top: y, opacity: mk}}>
          <div style={{position: 'absolute', left: -6, top: -6, width: 12, height: 12, borderRadius: '50%', background: mc || C.text}}/>
          <div style={{position: 'absolute', left: side === 'l' ? undefined : 16, right: side === 'l' ? 16 : undefined, top: up ? -70 : 12, background: 'rgba(7,11,22,.9)', border: `1px solid ${mc || C.lineHi}`, padding: '6px 12px', whiteSpace: 'nowrap', fontFamily: F.mono, fontWeight: 700, fontSize: tv ? 34 : 28, color: mc || C.text}}>{txt}</div>
        </div>;
      })}
      {(o.xl || []).map(([i, txt], j) => <div key={'x' + j} style={{position: 'absolute', left: px(i), top: H + 14, transform: 'translateX(-50%)', opacity: k}}><Lbl size={22} color={C.dim}>{txt}</Lbl></div>)}
      {o.live ? <div style={{position: 'absolute', left: tv ? 6 : Math.min(W - 40, head[0] + 20), top: tv ? -4 : head[1] - 30, fontFamily: F.mono, fontWeight: 700, fontSize: o.lsz || 44, color: col, whiteSpace: 'nowrap', textShadow: '0 2px 8px #000'}}>{fmt(curV)}</div> : null}
    </div>
  );
};

/* ================= gauge ================= */
export const Gauge = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const nd = kv(o.keys || [[o.t, -70], [o.t + 10, 40]], g, outExpo, 34);
  return (
    <div style={{position: 'absolute', left: o.x ?? 90, top: o.y ?? 230, opacity: k}}>
      <Lbl style={{marginLeft: 60}} size={30}>{o.label || 'US INTEREST RATES'}</Lbl>
      <svg width="780" height="470" viewBox="0 0 600 360">
        <path d="M60 320 A240 240 0 0 1 540 320" fill="none" stroke={C.line} strokeWidth="26"/>
        <path d="M60 320 A240 240 0 0 1 540 320" fill="none" stroke={C.warn} strokeWidth="26" strokeDasharray="754" strokeDashoffset={754 * (1 - (nd + 90) / 180)}/>
        <g transform={`translate(300 320) rotate(${nd})`}><line x1="0" y1="0" x2="0" y2="-210" stroke={C.text} strokeWidth="6" strokeLinecap="round"/></g>
        <circle cx="300" cy="320" r="16" fill={C.text}/>
      </svg>
      {o.sub ? <Lbl style={{marginLeft: 120, marginTop: -10, opacity: sn(g, o.subAt || o.t + 30)}} color={C.warn} size={32}>{o.sub}</Lbl> : null}
    </div>
  );
};

/* ================= icon row ================= */
export const Icons = ({o, g}) => {
  if (!vis(o, g)) return null;
  const S = o.s || 200; const gap = o.gap || 320; const N = o.items.length;
  const x0 = o.x ?? 960 - ((N - 1) * gap) / 2;
  return <div style={{position: 'absolute', inset: 0, opacity: outk(o, g)}}>{o.items.map((it, i) => {
    const [kind, name, tag, at, col, tagAt, off] = it; const a = sn(g, at ?? o.t + i * 6, 10);
    const dead = off != null && g >= off; const dk = dead ? sn(g, off, 8) : 0;
    const cc = dead ? C.loss : (col || C.text);
    const bob = Math.sin((g + i * 13) * 0.08) * 4;
    return (
      <div key={i} style={{position: 'absolute', left: x0 + i * gap - S / 2 - 30, top: (o.y ?? 360) + bob, width: S + 60, textAlign: 'center', opacity: a * (dead ? 1 - 0.55 * dk : 1), transform: `translateY(${(1 - a) * 40}px) scale(${1 + (dead ? -0.06 * dk : 0)})`}}>
        <div style={{display: 'inline-block', filter: col && !dead ? `drop-shadow(0 0 14px ${col}66)` : undefined}}><Ico k={kind} s={S} col={cc} sw={o.sw || 4}/></div>
        {name ? <Lbl color={dead ? C.loss : C.text} size={o.ls || 28} style={{marginTop: 10}}>{name}</Lbl> : null}
        {tag ? <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: o.ts || 46, color: o.tcol || C.warn, marginTop: 8, opacity: sn(g, tagAt ?? (at ?? o.t) + 8, 8)}}>{tag}</div> : null}
        {dead && o.xmark ? <svg width={S} height={S} style={{position: 'absolute', left: 30, top: 0}}><line x1="10" y1="10" x2={S - 10} y2={S - 10} stroke={C.loss} strokeWidth="8" strokeDasharray={S * 1.5} strokeDashoffset={S * 1.5 * (1 - dk)}/></svg> : null}
      </div>
    );
  })}
    {o.arrows ? o.items.slice(0, -1).map((_, i) => {const at = o.items[i + 1][3] ?? o.t; const a = rp(g, at - 4, 10);
      const off = o.items[i + 1][6]; const dead = off != null && g >= off;
      return <svg key={'a' + i} width={gap} height={40} style={{position: 'absolute', left: x0 + i * gap + S / 2 - 10, top: (o.y ?? 360) + S / 2 - 20, overflow: 'visible'}}>
        <line x1={0} y1={20} x2={(gap - S - 20) * a} y2={20} stroke={dead ? C.loss : C.dim} strokeWidth={4} strokeDasharray="10 8"/>
        {a >= 1 ? <path d={`M${gap - S - 34} 8 L${gap - S - 20} 20 L${gap - S - 34} 32`} fill="none" stroke={dead ? C.loss : C.dim} strokeWidth={4}/> : null}</svg>;}) : null}
  </div>;
};

/* ================= big centered text / question ================= */
export const Big = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 12) * outk(o, g); const col = o.col || C.text;
  const pulse = o.pulse ? 1 + Math.sin((g - o.t) * 0.2) * 0.012 : 1;
  const chars = o.type ? Math.floor(rp(g, o.t, o.txt.length * 1.2, (x) => x) * o.txt.length) : o.txt.length;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: o.y ?? 400, textAlign: 'center', opacity: k, transform: `scale(${(0.94 + 0.06 * k) * pulse})`}}>
      {o.pre ? <Lbl color={o.pcol || C.dim} size={o.ps || 30} style={{marginBottom: 14}}>{o.pre}</Lbl> : null}
      <div style={{fontFamily: F.head, fontWeight: 700, fontSize: o.size || 110, color: col, lineHeight: 1.05, letterSpacing: -1, textShadow: o.glow ? `0 0 40px ${col}66` : 'none', padding: '0 80px'}}>
        {o.txt.slice(0, chars)}<span style={{opacity: 0}}>{o.txt.slice(chars)}</span></div>
      {o.sub ? <div style={{fontFamily: F.mono, fontWeight: 500, fontSize: o.ss || 34, color: o.scol || C.dim, marginTop: 20, letterSpacing: 3, opacity: o.subAt ? sn(g, o.subAt, 10) : 1}}>{o.sub}</div> : null}
    </div>
  );
};

/* ================= chips row ================= */
export const Chips = ({o, g}) => {
  if (!vis(o, g)) return null;
  const N = o.items.length; const gap = o.gap || 260; const x0 = o.x ?? 960 - ((N - 1) * gap) / 2;
  return <div style={{position: 'absolute', inset: 0, opacity: outk(o, g)}}>{o.items.map(([txt, at, col], i) => {
    const a = sn(g, at, 8); const pop = a < 1 ? 0.7 + 0.3 * a + Math.sin(a * Math.PI) * 0.12 : 1;
    return <div key={i} style={{position: 'absolute', left: x0 + i * gap, top: o.y ?? 640, transform: `translate(-50%,-50%) scale(${pop})`, opacity: a, fontFamily: F.mono, fontWeight: 700, fontSize: o.size || 40,
      color: col || C.text, border: `2px solid ${col || C.lineHi}`, background: 'rgba(8,14,30,.92)', padding: '10px 22px', borderRadius: 4, whiteSpace: 'nowrap', boxShadow: col ? `0 0 18px ${col}44` : 'none'}}>{txt}</div>;
  })}</div>;
};

/* ================= tag (outlined stamp label) ================= */
export const TagL = ({o, g}) => {
  if (!vis(o, g)) return null;
  const d = g - o.t; const s = interpolate(d, [0, 4, 7, 10], [1.8, 0.95, 1.03, 1], cl); const col = o.col || C.warn;
  return <div style={{position: 'absolute', left: o.x ?? 960, top: o.y ?? 540, transform: `translate(-50%,-50%) rotate(${o.rot || 0}deg) scale(${s})`, opacity: Math.min(1, d / 3) * outk(o, g),
    border: `4px solid ${col}`, color: col, fontFamily: F.mono, fontWeight: 700, fontSize: o.size || 52, padding: '12px 30px', letterSpacing: 4, background: 'rgba(7,11,22,.9)', whiteSpace: 'nowrap', boxShadow: `0 0 26px ${col}55`}}>{o.txt}
    {o.sub ? <div style={{fontSize: (o.size || 52) * 0.5, color: C.text, letterSpacing: 3, marginTop: 6, textAlign: 'center'}}>{o.sub}</div> : null}</div>;
};

/* ================= seesaw ================= */
export const Seesaw = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const a = kv(o.keys, g, inOut, 30); // degrees; negative = left (dollar) down
  const L = 1100; const cx = 960, cy = o.y ?? 640;
  const L2 = o.right || [['€', 'eu'], ['¥', 'jp'], ['₹', 'in'], ['E£', 'eg']];
  return (
    <div style={{position: 'absolute', inset: 0, opacity: k}}>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <path d={`M${cx - 60} ${cy + 170} L${cx} ${cy + 14} L${cx + 60} ${cy + 170} Z`} fill="#0E1A33" stroke={C.lineHi} strokeWidth={3}/>
      </svg>
      <div style={{position: 'absolute', left: cx - L / 2, top: cy - 6, width: L, height: 12, background: C.lineHi, borderRadius: 6, transform: `rotate(${a}deg)`, transformOrigin: '50% 50%'}}>
        <div style={{position: 'absolute', left: 30, bottom: 12, transform: `rotate(${-a}deg)`, transformOrigin: '50% 100%', textAlign: 'center'}}>
          <div style={{width: 230, height: 230, borderRadius: '50%', border: `6px solid ${C.gain}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.head, fontWeight: 700, fontSize: 150, color: C.gain, background: 'rgba(8,14,30,.9)', boxShadow: `0 0 40px ${C.gain}55`}}>$</div>
        </div>
        <div style={{position: 'absolute', right: 20, bottom: 12, transform: `rotate(${-a}deg)`, transformOrigin: '50% 100%', display: 'flex', gap: 12}}>
          {L2.map(([s, f], i) => <div key={i} style={{width: 104, height: 104, borderRadius: '50%', border: `4px solid ${C.loss}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.head, fontWeight: 700, fontSize: s.length > 1 ? 40 : 56, color: C.text, background: 'rgba(8,14,30,.9)', opacity: sn(g, o.t + 8 + i * 4)}}>{s}</div>)}
        </div>
      </div>
      {o.lab ? <Lbl style={{position: 'absolute', left: 0, right: 0, top: cy + 210, textAlign: 'center'}} size={30} color={C.dim}>{o.lab}</Lbl> : null}
    </div>
  );
};

/* ================= shield ================= */
export const Shield = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 14) * outk(o, g); const col = o.col || C.gain; const draw = rp(g, o.t, 26, outExpo);
  const S = o.s || 380; const X = o.x ?? 520, Y = o.y ?? 160;
  return (
    <div style={{position: 'absolute', left: X - S / 2, top: Y, width: S, opacity: k}}>
      <svg width={S} height={S} viewBox="0 0 100 100" style={{overflow: 'visible', filter: `drop-shadow(0 0 22px ${col}88)`}}>
        <path d="M50 6 L88 20 V48 Q88 78 50 94 Q12 78 12 48 V20 Z" fill={col} fillOpacity={0.12 * draw} stroke={col} strokeWidth={3} strokeDasharray={300} strokeDashoffset={300 * (1 - draw)}/>
        {o.icon ? <g transform="translate(25 24) scale(.5)"><path d={IP[o.icon]} fill="none" stroke={C.text} strokeWidth={6} strokeLinejoin="round" opacity={sn(g, o.t + 16)}/></g> : null}
      </svg>
      {o.label ? <div style={{textAlign: 'center', marginTop: 10, fontFamily: F.mono, fontWeight: 700, fontSize: o.size || 64, color: col, opacity: sn(g, o.t + 18)}}>{o.label}</div> : null}
      {o.sub ? <div style={{textAlign: 'center', marginTop: 6, opacity: sn(g, o.t + 24)}}><Lbl size={24} color={C.text}>{o.sub}</Lbl></div> : null}
    </div>
  );
};

/* ================= receipt ================= */
export const Receipt = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 14) * outk(o, g); const W = o.w || 560; const R = o.rows;
  let tot = 0; for (const r of R) if (g >= r[2]) tot += r[1];
  const shown = R.filter((r) => g >= r[2]).length;
  return (
    <div style={{position: 'absolute', left: (o.x ?? 1300) - W / 2, top: o.y ?? 120, width: W, opacity: k, transform: `translateY(${(1 - k) * -200}px) rotate(${o.rot ?? 2}deg)`}}>
      <div style={{background: '#F4F1EA', padding: '30px 34px 40px', boxShadow: '0 30px 60px rgba(0,0,0,.6)', fontFamily: F.mono, color: '#161B2A',
        clipPath: 'polygon(0 0,100% 0,100% 97%,95% 100%,90% 97%,85% 100%,80% 97%,75% 100%,70% 97%,65% 100%,60% 97%,55% 100%,50% 97%,45% 100%,40% 97%,35% 100%,30% 97%,25% 100%,20% 97%,15% 100%,10% 97%,5% 100%,0 97%)'}}>
        <div style={{textAlign: 'center', fontWeight: 700, fontSize: 30, letterSpacing: 4}}>{o.head || 'SUPERMARKET'}</div>
        <div style={{textAlign: 'center', fontSize: 18, marginBottom: 16, opacity: 0.7}}>{o.date || 'MONTH 3 · SCENARIO'}</div>
        {R.map((r, i) => {const a = sn(g, r[2], 6); if (a <= 0) return null; return <div key={i} style={{display: 'flex', justifyContent: 'space-between', fontSize: 30, fontWeight: r[3] ? 700 : 500, color: r[3] ? '#D41F3B' : '#161B2A', padding: '6px 0', opacity: a, borderBottom: '1px dashed #b9b4a8'}}><span>{r[0]}</span><span>{(r[1] < 0 ? '-' : '') + '$' + Math.abs(r[1]).toFixed(2)}</span></div>;})}
        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 40, fontWeight: 700, marginTop: 14}}><span>TOTAL</span><span>{'$' + tot.toFixed(2)}</span></div>
        {o.note && shown === R.length ? <div style={{marginTop: 12, fontSize: 20, color: '#D41F3B', opacity: sn(g, R[R.length - 1][2] + 8)}}>{o.note}</div> : null}
      </div>
    </div>
  );
};

/* ================= scoreboard ================= */
export const Score = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 12) * outk(o, g); const cols = o.cols; const CW = o.cw || 210, RH = o.rh || 112; const X = o.x ?? 520, Y = o.y ?? 200;
  const hiRow = lastOf(o.focus, g, -1);
  return (
    <div style={{position: 'absolute', left: X, top: Y, opacity: k, transform: `scale(${o.scl || 1})`, transformOrigin: '0 0'}}>
      {cols.map(([ic, name], j) => <div key={j} style={{position: 'absolute', left: 290 + j * CW, top: 0, width: CW, textAlign: 'center', opacity: sn(g, o.t + j * 5)}}>
        <Ico k={ic} s={74} col={C.text} sw={5}/><Lbl size={20} color={C.dim} style={{marginTop: 4}}>{name}</Lbl></div>)}
      {o.rows.map(([flag, name, cells, at], i) => {
        const a = sn(g, at, 10); const y = 130 + i * RH; const dim = hiRow >= 0 && hiRow !== i;
        return <div key={i} style={{position: 'absolute', left: 0, top: y, opacity: a * (dim ? 0.45 : 1), transform: `translateX(${(1 - a) * -40}px)`}}>
          <div style={{position: 'absolute', left: 0, top: 18, display: 'flex', alignItems: 'center', gap: 14, width: 280}}>
            <Img src={staticFile(`flags/${flag}.svg`)} style={{width: 66, height: 50, borderRadius: 4, border: '1px solid rgba(255,255,255,.3)'}}/><Lbl size={26} color={C.text}>{name}</Lbl></div>
          {cells.map((c, j) => {
            if (!c) return null; const [st, ct] = c; const ck = sn(g, ct, 8); const col = st === 1 ? C.gain : st === 0 ? C.loss : C.warn;
            return <div key={j} style={{position: 'absolute', left: 290 + j * CW + 20, top: 8, width: CW - 40, height: RH - 30, borderRadius: 6, background: col, opacity: 0.18 + 0.7 * ck, transform: `scale(${0.6 + 0.4 * ck})`,
              boxShadow: ck > 0.5 ? `0 0 20px ${col}77` : 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.mono, fontWeight: 700, fontSize: 42, color: '#071020'}}>{st === 1 ? '✓' : st === 0 ? '✕' : '~'}</div>;
          })}
        </div>;
      })}
    </div>
  );
};

/* ================= two bars compare ================= */
export const Cmp2 = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const D = o.data; const mx = o.max || Math.max(...D.map((d) => d[1])); const H = o.h || 520; const BW = o.bw || 260; const gap = o.gap || 420;
  const x0 = o.x ?? 960 - ((D.length - 1) * gap) / 2; const base = o.y ?? 880;
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>
    {o.title ? <Lbl style={{position: 'absolute', left: 0, right: 0, top: base - H - 150, textAlign: 'center'}} size={30}>{o.title}</Lbl> : null}
    <div style={{position: 'absolute', left: x0 - BW, top: base, width: (D.length - 1) * gap + BW * 2, height: 3, background: C.lineHi}}/>
    {D.map(([lab, v, col, at, txt, ic], i) => {
      const val = Array.isArray(v) ? kv(v, g, inOut, 40) : v * rp(g, at ?? o.t + 8 + i * 10, 30, outExpo); const h = (val / mx) * H; const cc = col || C.money;
      return <div key={i}>
        <div style={{position: 'absolute', left: x0 + i * gap - BW / 2, top: base - h, width: BW, height: h, background: `linear-gradient(${cc}, ${cc}55)`, boxShadow: `0 0 30px ${cc}44`, borderRadius: '6px 6px 0 0'}}/>
        <div style={{position: 'absolute', left: x0 + i * gap - 300, width: 600, top: base - h - 76, textAlign: 'center', fontFamily: F.mono, fontWeight: 700, fontSize: 54, color: cc}}>{txt || ''}</div>
        <div style={{position: 'absolute', left: x0 + i * gap - 300, width: 600, top: base + 20, textAlign: 'center'}}>{ic ? <div><Ico k={ic} s={70} col={cc} sw={6}/></div> : null}<Lbl size={28} color={C.text}>{lab}</Lbl></div>
      </div>;
    })}
  </div>;
};

/* ================= timelines (recovery) ================= */
export const Lines2 = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const W = o.w || 1300; const yrs = o.yrs || 26;
  return <div style={{position: 'absolute', left: o.x ?? 300, top: o.y ?? 300, opacity: k}}>
    <div style={{position: 'absolute', left: 0, top: -60}}><Lbl size={26}>{o.title || 'YEARS UNTIL A SIMPLE INDEX FUND WAS BACK TO EVEN'}</Lbl></div>
    {o.rows.map(([lab, y, col, at], i) => {
      const p = rp(g, at, 40, outExpo); const w = (y / yrs) * W * p;
      return <div key={i} style={{position: 'absolute', left: 0, top: 30 + i * 170}}>
        <Lbl size={30} color={C.text}>{lab}</Lbl>
        <div style={{marginTop: 12, width: W, height: 58, background: '#0E1A33', border: `1px solid ${C.line}`, position: 'relative'}}>
          <div style={{position: 'absolute', left: 0, top: 0, height: '100%', width: w, background: `linear-gradient(90deg, ${col}, ${col}aa)`, boxShadow: `0 0 20px ${col}66`}}/>
          <div style={{position: 'absolute', left: w + 18, top: 4, fontFamily: F.mono, fontWeight: 700, fontSize: 40, color: col, whiteSpace: 'nowrap', opacity: p}}>{'~' + Math.round(y * p) + ' YEARS'}</div>
        </div>
      </div>;
    })}
  </div>;
};

/* ================= check list ================= */
export const Checks = ({o, g}) => {
  if (!vis(o, g)) return null;
  return <div style={{position: 'absolute', left: o.x ?? 300, top: o.y ?? 420, opacity: outk(o, g)}}>{o.items.map(([txt, at], i) => {
    const a = sn(g, at, 10); const d = rp(g, at + 2, 10, outExpo);
    return <div key={i} style={{display: 'flex', alignItems: 'center', gap: 26, marginBottom: 34, opacity: a, transform: `translateX(${(1 - a) * -40}px)`}}>
      <svg width={70} height={70} viewBox="0 0 70 70"><rect x={3} y={3} width={64} height={64} rx={8} fill="none" stroke={C.gain} strokeWidth={4}/>
        <path d="M16 36 L30 50 L54 20" fill="none" stroke={C.gain} strokeWidth={7} strokeLinecap="round" strokeDasharray={60} strokeDashoffset={60 * (1 - d)}/></svg>
      <div style={{fontFamily: F.head, fontWeight: 700, fontSize: o.size || 54, color: C.text}}>{txt}</div>
    </div>;
  })}</div>;
};

/* ================= terminal (payment line) ================= */
export const Term2 = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const p = rp(g, o.t + 10, o.load || 50, (x) => x); const fail = g >= o.fail; const fk = fail ? sn(g, o.fail, 6) : 0;
  const shake = fail && g - o.fail < 12 ? Math.sin((g - o.fail) * 2.6) * (12 - (g - o.fail)) : 0;
  return (
    <Pnl x={260 + shake} y={o.y ?? 280} w={1400} h={460} k={k} accent={fail ? C.loss : C.lineHi} glow={fail ? C.loss : null}>
      <Lbl style={{position: 'absolute', left: 36, top: 30}} size={24}>{o.head || 'BANK TERMINAL · INCOMING WIRE'}</Lbl>
      <div style={{position: 'absolute', right: 36, top: 24, fontFamily: F.mono, fontWeight: 700, fontSize: 40, color: C.warn}}>{o.time || 'MON 10:17'}</div>
      <div style={{position: 'absolute', left: 36, top: 92, fontFamily: F.mono, fontWeight: 700, fontSize: 80, color: C.text}}>{o.amt || '$400,000,000'}</div>
      <div style={{position: 'absolute', left: 40, top: 196}}><Lbl size={28} color={C.dim}>{o.from || 'FROM: CORVANE · VIRGINIA'}</Lbl></div>
      <div style={{position: 'absolute', left: 36, top: 262, width: 1328, height: 34, background: '#0E1A33', border: `1px solid ${C.line}`}}>
        <div style={{width: `${(fail ? Math.min(p, (o.stop || 0.74)) : Math.min(p, o.stop || 0.74)) * 100}%`, height: '100%', background: fail ? C.loss : C.money, boxShadow: `0 0 16px ${fail ? C.loss : C.money}`}}/>
      </div>
      <div style={{position: 'absolute', left: 36, top: 330, fontFamily: F.mono, fontWeight: 700, fontSize: 70, color: fail ? C.loss : C.dim, opacity: fail ? fk : (Math.floor(g / 10) % 2 ? 1 : 0.4)}}>{fail ? (o.ftxt || '✕ NOT RECEIVED') : 'WAITING…'}</div>
    </Pnl>
  );
};

/* ================= gold stack + whales ================= */
export const Stack = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const N = o.n || 32; const p = rp(g, o.t + 8, o.d || 60, (x) => x); const m = Math.round(N * p);
  const bars = []; for (let i = 0; i < m; i++) {const row = Math.floor(i / 6), col = i % 6; bars.push(<div key={i} style={{position: 'absolute', left: (col - 3) * 66 + (row % 2) * 33, top: -row * 34 - 34, width: 62, height: 32,
    background: 'linear-gradient(#FFE08A, #C9952B)', border: '2px solid #7a5a10', borderRadius: 3, transform: 'perspective(200px) rotateX(18deg)'}}/>);}
  const whale = (x, i) => <svg key={i} width={420} height={150} viewBox="0 0 420 150" style={{position: 'absolute', left: x, top: -150, opacity: sn(g, o.wat + i * 8)}}>
    <path d="M10 90 Q40 40 140 40 Q260 36 330 70 L380 40 Q392 70 380 100 L330 96 Q260 130 140 126 Q40 124 10 90 Z" fill="#1d3a6b" stroke="#5aa0ff" strokeWidth="3"/><circle cx="70" cy="80" r="5" fill="#cde"/></svg>;
  return (
    <div style={{position: 'absolute', left: o.x ?? 760, top: o.y ?? 860, opacity: k}}>
      {bars}
      <div style={{position: 'absolute', left: -450, top: 40, width: 900, textAlign: 'center', fontFamily: F.mono, fontWeight: 700, fontSize: 54, color: C.gold, whiteSpace: 'nowrap'}}>{o.txt ? o.txt.replace('{}', Math.round((o.tons || 320) * p)) : ''}</div>
      {o.wat ? <div style={{position: 'absolute', left: 300, top: 0}}>{whale(0, 0)}{whale(80, 1)}<div style={{position: 'absolute', left: 20, top: 40, width: 600, opacity: sn(g, o.wat + 14)}}><Lbl size={24} color={C.dim}>{o.wl || '≈ TWO BLUE WHALES WEIGH ABOUT 300 TONS'}</Lbl></div></div> : null}
    </div>
  );
};

/* ================= burning house with flag, money flowing in ================= */
export const Fire = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const cx = o.x ?? 960, cy = o.y ?? 620;
  const fl = []; for (let i = 0; i < 9; i++) {const ph = g * 0.25 + i * 1.7; const h = 80 + 40 * Math.sin(ph) + i % 3 * 20; fl.push(<div key={i} style={{position: 'absolute', left: cx - 170 + i * 40, top: cy - 230 - h * 0.6, width: 46, height: h,
    background: `radial-gradient(ellipse at 50% 90%, #FFE08A, ${C.warn} 45%, ${C.loss}00 75%)`, borderRadius: '50% 50% 40% 40%', filter: 'blur(2px)', opacity: 0.9}}/>);}
  const dots = []; const src = [[-800, -300], [-820, 120], [-600, 380], [820, -320], [840, 160], [600, 400], [0, -460]];
  for (let s = 0; s < src.length; s++) for (let j = 0; j < 4; j++) {const q = ((g - o.t) * 0.018 + j / 4 + s * 0.13) % 1; const x = cx + src[s][0] * (1 - q), y = cy - 60 + src[s][1] * (1 - q);
    dots.push(<div key={s + '_' + j} style={{position: 'absolute', left: x - 18, top: y - 18, width: 36, height: 36, borderRadius: '50%', background: C.gain, color: '#06210f', fontFamily: F.head, fontWeight: 700, fontSize: 26, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: sn(g, o.t + 20) * Math.min(1, q * 5), boxShadow: `0 0 14px ${C.gain}`}}>$</div>);}
  return (
    <div style={{position: 'absolute', inset: 0, opacity: k}}>
      {dots}{fl}
      <div style={{position: 'absolute', left: cx - 190, top: cy - 230}}><Ico k="house" s={380} col={C.text} sw={3}/></div>
      <Img src={staticFile('flags/us.svg')} style={{position: 'absolute', left: cx - 70, top: cy - 60, width: 140, height: 105, borderRadius: 4, border: '2px solid #fff'}}/>
    </div>
  );
};

/* ================= envelopes ================= */
export const Envs = ({o, g}) => {
  if (!vis(o, g)) return null;
  const out = []; const N = o.n || 10; const cx = o.x ?? 960, cy = o.y ?? 560;
  for (let i = 0; i < N; i++) {
    const at = o.t + 10 + i * 5; const p = rp(g, at, 40, outExpo); if (p <= 0) continue; const ang = (i / N) * Math.PI * 2 + 0.3;
    const x = cx + Math.cos(ang) * 820 * p, y = cy + Math.sin(ang) * 420 * p; const op = 1 - rp(g, at + 30, 14);
    out.push(<div key={i} style={{position: 'absolute', left: x - 60, top: y - 40, width: 120, height: 80, opacity: op, transform: `rotate(${Math.sin(i) * 20 + p * 30}deg)`}}><Ico k="mail" s={120} col={C.gold} sw={5}/></div>);
  }
  const stamp = sn(g, o.t, 10);
  return <div style={{position: 'absolute', inset: 0, opacity: outk(o, g)}}>{out}
    <div style={{position: 'absolute', left: cx - 160, top: cy - 110, width: 320, height: 220, opacity: stamp, transform: `scale(${0.8 + 0.2 * stamp})`}}>
      <Ico k="mail" s={320} col={o.col || C.gold} sw={3}/>
      <div style={{position: 'absolute', left: -100, right: -100, top: 250, textAlign: 'center'}}><Lbl size={34} color={o.col || C.gold}>{o.from || 'FROM: WASHINGTON'}</Lbl></div>
    </div></div>;
};

/* ================= fork (dollar vs gold) ================= */
export const Fork = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const d = rp(g, o.t + 4, 30, outExpo); const tw = o.tw ? Math.sin((g - o.tw) * 0.25) * 6 * Math.min(1, Math.max(0, (g - o.tw) / 10)) : 0;
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
      <path d="M960 1000 L960 640 Q960 520 600 380" fill="none" stroke={C.money} strokeWidth={14} strokeDasharray={1100} strokeDashoffset={1100 * (1 - d)} strokeLinecap="round"/>
      <path d="M960 640 Q960 520 1320 380" fill="none" stroke={C.gold} strokeWidth={14} strokeDasharray={700} strokeDashoffset={700 * (1 - d)} strokeLinecap="round"/>
      <g transform={`translate(960 760) rotate(${tw + (o.lean || 0)})`}><path d="M0 60 L0 -60 M-22 -36 L0 -62 L22 -36" fill="none" stroke={C.text} strokeWidth={10} strokeLinecap="round"/></g>
    </svg>
    <div style={{position: 'absolute', left: 380, top: 250, textAlign: 'center', width: 400, opacity: sn(g, o.t + 20)}}><Ico k="dollar" s={120} col={C.money} sw={6}/><Lbl size={34} color={C.money}>{o.l || 'DOLLAR'}</Lbl></div>
    <div style={{position: 'absolute', left: 1140, top: 250, textAlign: 'center', width: 400, opacity: sn(g, o.t + 24)}}><Ico k="gold" s={120} col={C.gold} sw={6}/><Lbl size={34} color={C.gold}>{o.r || 'GOLD'}</Lbl></div>
  </div>;
};

/* ================= flow: object moves from A to B ================= */
export const Flow = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const p = rp(g, o.at ?? o.t + 10, o.d || 30, inOut);
  const [x0, y0] = o.from, [x1, y1] = o.to; const x = lerp(x0, x1, p), y = lerp(y0, y1, p) - Math.sin(p * Math.PI) * (o.arc || 120);
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>
    {(o.ends || []).map(([ic, lab, ex, ey, col], i) => <div key={i} style={{position: 'absolute', left: ex - 150, top: ey - 110, width: 300, textAlign: 'center'}}><Ico k={ic} s={170} col={col || C.text} sw={4}/><Lbl size={28} color={col || C.text}>{lab}</Lbl></div>)}
    <div style={{position: 'absolute', left: x - (o.s || 120) / 2, top: y - (o.s || 120) / 2, filter: `drop-shadow(0 0 18px ${o.col || C.gold})`}}><Ico k={o.ic || 'coin'} s={o.s || 120} col={o.col || C.gold} sw={6}/></div>
    {o.lab ? <div style={{position: 'absolute', left: x - 200, top: y + (o.s || 120) / 2 + 6, width: 400, textAlign: 'center', fontFamily: F.mono, fontWeight: 700, fontSize: 44, color: o.col || C.gold}}>{o.lab}</div> : null}
  </div>;
};

/* ================= particles converging to a symbol ================= */
export const Converge = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const cx = o.x ?? 960, cy = o.y ?? 560; const fl = o.flags || ['eu', 'jp', 'in', 'eg', 'cn', 'gb', 'br', 'mx'];
  const out = [];
  fl.forEach((f, i) => {const a = (i / fl.length) * Math.PI * 2; const fx = cx + Math.cos(a) * 700, fy = cy + Math.sin(a) * 380;
    out.push(<Img key={'f' + i} src={staticFile(`flags/${f}.svg`)} style={{position: 'absolute', left: fx - 45, top: fy - 34, width: 90, height: 68, borderRadius: 4, opacity: sn(g, o.t + i * 3)}}/>);
    for (let j = 0; j < 5; j++) {const q = ((g - o.t) * 0.02 + j / 5 + i * 0.07) % 1; out.push(<div key={i + '_' + j} style={{position: 'absolute', left: lerp(fx, cx, q) - 6, top: lerp(fy, cy, q) - 6, width: 12, height: 12, borderRadius: '50%', background: C.money, boxShadow: `0 0 10px ${C.money}`, opacity: sn(g, o.t + 16) * (1 - q * 0.6)}}/>);}
  });
  const pulse = 1 + Math.sin(g * 0.15) * 0.04;
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>{out}
    <div style={{position: 'absolute', left: cx - 150, top: cy - 150, width: 300, height: 300, borderRadius: '50%', border: `6px solid ${C.gain}`, background: 'rgba(8,14,30,.95)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.head, fontWeight: 700, fontSize: 200, color: C.gain, transform: `scale(${pulse})`, boxShadow: `0 0 60px ${C.gain}66`}}>$</div>
  </div>;
};

/* ================= basket shrinking each year ================= */
export const Basket = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const Y = o.years || [['2027', 1], ['2028', 0.93], ['2029', 0.86], ['2030', 0.8]];
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>{Y.map(([yr, s, at], i) => {
    const a = sn(g, at ?? o.t + i * 18, 10); const S = 300 * s;
    return <div key={i} style={{position: 'absolute', left: 300 + i * 360 - S / 2 + 150, top: 520 - S, width: S, textAlign: 'center', opacity: a}}>
      <Ico k="basket" s={S} col={i ? C.warn : C.text} sw={4}/>
      <div style={{position: 'absolute', left: -100, right: -100, top: S + 20}}><Lbl size={32} color={C.text}>{yr}</Lbl><div style={{fontFamily: F.mono, fontWeight: 700, fontSize: 30, color: i ? C.warn : C.dim}}>{'$100 BUYS ' + Math.round(s * 100) + '%'}</div></div>
    </div>;
  })}</div>;
};

/* ================= printing press ================= */
export const Press = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = sn(g, o.t, 10) * outk(o, g); const cx = o.x ?? 520, cy = o.y ?? 460; const sp = o.fast ? 0.06 : 0.03;
  const bills = []; for (let i = 0; i < 8; i++) {const q = ((g - o.t) * sp + i / 8) % 1; bills.push(<div key={i} style={{position: 'absolute', left: cx + 60 + q * 380, top: cy + 120 - Math.sin(q * Math.PI) * 80 + q * 120, width: 110, height: 52,
    background: '#1f6b45', border: `2px solid ${C.gain}`, borderRadius: 3, transform: `rotate(${q * 140 - 20}deg)`, opacity: 1 - q * 0.6, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.head, fontWeight: 700, color: C.gain, fontSize: 30}}>$</div>);}
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>
    <div style={{position: 'absolute', left: cx - 150, top: cy - 120, transform: `translateY(${Math.sin(g * 0.6) * 3}px)`}}><Ico k="printer" s={300} col={C.text} sw={3}/></div>{bills}
    {o.lab ? <Lbl style={{position: 'absolute', left: cx - 300, top: cy + 330, width: 600, textAlign: 'center'}} size={26} color={C.dim}>{o.lab}</Lbl> : null}
  </div>;
};

/* ================= TV banner (in-scene news) ================= */
export const Banner = ({o, g}) => {
  if (!vis(o, g)) return null;
  const k = rp(g, o.t, 12, outExpo) * outk(o, g);
  return <div style={{position: 'absolute', left: o.x ?? 0, top: o.y ?? 880, width: o.w || 1920, height: 120, overflow: 'hidden', opacity: k}}>
    <div style={{position: 'absolute', left: 0, top: 0, height: 120, width: `${k * 100}%`, background: o.col || C.loss, display: 'flex', alignItems: 'center'}}>
      <div style={{background: '#fff', color: o.col || C.loss, fontFamily: F.mono, fontWeight: 700, fontSize: 36, padding: '0 22px', height: '100%', display: 'flex', alignItems: 'center', letterSpacing: 3}}>{o.tag || 'BREAKING'}</div>
      <div style={{fontFamily: F.head, fontWeight: 700, fontSize: 58, color: '#fff', marginLeft: 30, whiteSpace: 'nowrap'}}>{o.txt}</div>
    </div>
  </div>;
};

/* ================= transitions ================= */
export const Wipe = ({o, g}) => {
  const d = o.d || 14; if (g < o.t || g > o.t + d + 4) return null; const k = rp(g, o.t, d, outExpo); const x = k * 2120 - 100; const col = o.col || C.money;
  return <AbsoluteFill style={{pointerEvents: 'none'}}>
    <div style={{position: 'absolute', left: x - 2, top: 0, width: 5, height: 1080, background: col, boxShadow: `0 0 34px 8px ${col}`}}/>
    <div style={{position: 'absolute', left: x - 220, top: 0, width: 220, height: 1080, background: `linear-gradient(90deg, transparent, ${col}33)`}}/>
  </AbsoluteFill>;
};
export const GlitchO = ({o, g}) => {
  const d = o.d || 8; if (g < o.t || g >= o.t + d) return null; const r = (s) => ((Math.sin(g * 12.9898 + s) * 43758.5453) % 1 + 1) % 1;
  const bars = []; for (let i = 0; i < 7; i++) bars.push(<div key={i} style={{position: 'absolute', left: 0, right: 0, top: r(i) * 1080, height: 6 + r(i + 9) * 40, background: i % 2 ? `${C.loss}55` : `${C.money}44`, transform: `translateX(${(r(i + 3) - 0.5) * 120}px)`, mixBlendMode: 'screen'}}/>);
  return <AbsoluteFill style={{pointerEvents: 'none'}}>{bars}<div style={{position: 'absolute', inset: 0, background: `${C.loss}18`}}/></AbsoluteFill>;
};

/* ================= frame around a scene shown inside the MG world ================= */
export const WinFrame = ({w, g, sc}) => {
  const [x, y, W, H] = w;
  return <div style={{position: 'absolute', left: x, top: y, width: W, height: H, pointerEvents: 'none'}}>
    {['tl', 'tr', 'bl', 'br'].map((p) => <div key={p} style={{position: 'absolute', width: 34, height: 34, borderColor: sc.wcol || C.money, borderStyle: 'solid', borderWidth: 0,
      [p[0] === 't' ? 'top' : 'bottom']: -8, [p[1] === 'l' ? 'left' : 'right']: -8, [p[0] === 't' ? 'borderTopWidth' : 'borderBottomWidth']: 4, [p[1] === 'l' ? 'borderLeftWidth' : 'borderRightWidth']: 4}}/>)}
    <div style={{position: 'absolute', inset: 0, border: `1px solid ${C.lineHi}`}}/>
    {sc.wlab ? <div style={{position: 'absolute', left: 0, top: -46, display: 'flex', alignItems: 'center', gap: 12}}>
      {sc.wflag ? <Img src={staticFile(`flags/${sc.wflag}.svg`)} style={{width: 44, height: 33, borderRadius: 3}}/> : null}
      <Lbl color={C.text} size={24}>{sc.wlab}</Lbl><div style={{width: 10, height: 10, borderRadius: '50%', background: C.loss, opacity: Math.floor(g / 12) % 2 ? 1 : 0.3}}/><Lbl color={C.loss} size={18}>LIVE</Lbl></div> : null}
  </div>;
};

export const Chalk = ({o, g}) => {
  if (!vis(o, g)) return null; const p = rp(g, o.t, o.d || 24, (x) => x); const wipe = o.wipe ? 1 - rp(g, o.wipe, 14) : 1;
  return <div style={{position: 'absolute', left: o.x, top: o.y, transform: `translate(-50%,-50%) rotate(${o.rot || -2}deg)`, clipPath: `inset(0 ${100 - p * 100}% 0 0)`, opacity: wipe * outk(o, g),
    fontFamily: 'IS, serif', fontSize: o.size || 90, color: o.col || '#F1EFE4', whiteSpace: 'pre', textAlign: 'center', lineHeight: 1.0, textShadow: '0 0 2px rgba(255,255,255,.5)', filter: 'blur(.3px)'}}>{o.txt}</div>;
};
export const FlagRow = ({o, g}) => {
  if (!vis(o, g)) return null; const F_ = o.flags; const N = F_.length; const gap = o.gap || 230; const x0 = (o.x ?? 960) - ((N - 1) * gap) / 2; const k = outk(o, g);
  const spin = o.spin ? Math.floor((g - o.spin[0]) / 4) % N : -1; const spinning = o.spin && g >= o.spin[0] && g < o.spin[1];
  return <div style={{position: 'absolute', inset: 0, opacity: k}}>{F_.map((f, i) => {
    const a = sn(g, o.t + i * (o.st || 4), 10); const hl = spinning ? spin === i : (o.hl != null && g >= o.hl[0] ? o.hl[1] === i || o.hl[1] === 'all' : false);
    const q = o.q != null && g >= o.q; const pulse = o.pulse ? 1 + 0.05 * Math.sin((g + i * 9) * 0.18) : 1;
    return <div key={i} style={{position: 'absolute', left: x0 + i * gap - 85, top: (o.y ?? 470) - 64, width: 170, height: 128, opacity: a * (spinning && !hl ? 0.45 : 1), transform: `scale(${(hl ? 1.14 : 1) * pulse * (0.7 + 0.3 * a)})`}}>
      <Img src={staticFile(`flags/${f}.svg`)} style={{width: 170, height: 128, borderRadius: 6, border: `3px solid ${hl ? C.gold : 'rgba(255,255,255,.25)'}`, boxShadow: hl ? `0 0 30px ${C.gold}` : 'none', filter: q ? 'blur(10px) brightness(.5)' : 'none'}}/>
      {q ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.head, fontWeight: 700, fontSize: 90, color: C.gold}}>?</div> : null}
      {o.names ? <div style={{position: 'absolute', left: -40, right: -40, top: 140, textAlign: 'center'}}><Lbl size={22} color={C.text}>{o.names[i]}</Lbl></div> : null}
    </div>;
  })}</div>;
};
export const MG = {chalk: Chalk, flagrow: FlagRow, map: MapW, hud: Hud, tick: Tick, term: TermC, stat: Stat, clocks: Clocks, spbar: SpBar, chart: Chart, gauge: Gauge, icons: Icons, big: Big, chips: Chips,
  tagl: TagL, seesaw: Seesaw, shield: Shield, receipt: Receipt, score: Score, cmp2: Cmp2, lines2: Lines2, checks: Checks, term2: Term2, stack: Stack, fire: Fire,
  envs: Envs, fork: Fork, flow: Flow, converge: Converge, basket: Basket, press: Press, banner: Banner, wipe: Wipe, glitch: GlitchO};

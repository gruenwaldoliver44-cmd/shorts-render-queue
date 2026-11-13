import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, interpolate, staticFile, Audio, Img} from 'remotion';
import {C, F, FontFaces, snap, ramp, lerp, usd, outExpo, inOut} from './theme.js';
import {Bg, Panel, Label, Counter, WorldMap, Arc, City, Term, ScanWipe, Glitch, pt, W, H} from './ui.jsx';

const S = (name, at, vol = 0.8) => (
  <Sequence from={at} durationInFrames={90} key={name + at}><Audio src={staticFile(`sfx/${name}.wav`)} volume={vol}/></Sequence>
);

/* ---------------- 1: three clocks + world, New York goes red ---------------- */
const Clock = ({x, city, flag, h, m, k, hot}) => (
  <Panel x={x} y={60} w={520} h={150} k={k} accent={hot ? C.loss : C.lineHi}>
    <div style={{position: 'absolute', left: 28, top: 26, display: 'flex', alignItems: 'center', gap: 14}}>
      <Img src={staticFile(`flags/${flag}.svg`)} style={{width: 46, height: 34, borderRadius: 3}}/>
      <Label color={C.dim} size={22}>{city}</Label>
    </div>
    <div style={{position: 'absolute', left: 28, top: 66, fontFamily: F.mono, fontWeight: 700, fontSize: 64, color: hot ? C.loss : C.text}}>
      {String(h).padStart(2, '0')}:{String(m).padStart(2, '0')}
    </div>
  </Panel>
);
const Scene1 = () => {
  const f = useCurrentFrame();
  const nyMin = f < 75 ? 29 : 30;
  const hot = f >= 75;
  const crack = ramp(f, 80, 50, outExpo);
  const [nx, ny] = pt('ny');
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', inset: 0, opacity: snap(f, 0, 20), transform: `scale(${lerp(1.08, 1, ramp(f, 0, 140))})`}}>
        <WorldMap hot={hot ? ['840'] : []}/>
        {/* crack lines spreading from New York */}
        <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
          {[[-260, -120], [-120, 210], [420, -90], [640, 60], [980, 40], [260, 260]].map(([dx, dy], i) => {
            const L = Math.hypot(dx, dy);
            const k = Math.max(0, Math.min(1, crack * 1.4 - i * 0.12));
            const mx = nx + dx * 0.45 + (i % 2 ? 30 : -30), my = ny + dy * 0.45 + (i % 2 ? -25 : 25);
            return <path key={i} d={`M${nx},${ny} L${mx},${my} L${nx + dx},${ny + dy}`} fill="none" stroke={C.loss}
              strokeWidth={2.5} strokeDasharray={L * 1.2} strokeDashoffset={L * 1.2 * (1 - k)} opacity={0.85}/>;
          })}
        </svg>
        <City id="ny" k={snap(f, 40)} hot={hot}/>
      </div>
      <Clock x={110} city="TOKYO" flag="jp" h={23} m={nyMin} k={snap(f, 6)}/>
      <Clock x={700} city="LONDON" flag="gb" h={14} m={nyMin} k={snap(f, 12)}/>
      <Clock x={1290} city="NEW YORK" flag="us" h={9} m={nyMin} k={snap(f, 18)} hot={hot}/>
      <Glitch s={75} d={8}><div/></Glitch>
    </AbsoluteFill>
  );
};

/* ---------------- 2: the chip, the loan, the fire sale ---------------- */
const Chip = ({size = 220, col = C.money}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="18" y="18" width="64" height="64" rx="6" fill="#0E1A33" stroke={col} strokeWidth="2.5"/>
    <rect x="32" y="32" width="36" height="36" rx="3" fill="none" stroke={col} strokeWidth="1.5" opacity="0.7"/>
    {Array.from({length: 7}).map((_, i) => (
      <g key={i} stroke={col} strokeWidth="2">
        <line x1={24 + i * 8.6} y1="18" x2={24 + i * 8.6} y2="8"/><line x1={24 + i * 8.6} y1="82" x2={24 + i * 8.6} y2="92"/>
        <line x1="18" y1={24 + i * 8.6} x2="8" y2={24 + i * 8.6}/><line x1="82" y1={24 + i * 8.6} x2="92" y2={24 + i * 8.6}/>
      </g>
    ))}
    <text x="50" y="55" textAnchor="middle" fontFamily="JBM" fontWeight="700" fontSize="10" fill={col}>AI</text>
  </svg>
);
const Scene2 = () => {
  const f = useCurrentFrame();
  const slash = ramp(f, 66, 8, outExpo);
  const newP = snap(f, 74, 10);
  const chain = snap(f, 14, 14);
  return (
    <AbsoluteFill>
      {/* collateral chain: chip -> loan */}
      <div style={{position: 'absolute', left: 260, top: 170, opacity: snap(f, 0, 12), transform: `scale(${lerp(0.8, 1, snap(f, 0, 14))})`}}>
        <Chip size={340} col={f > 70 ? C.loss : C.money}/>
      </div>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <line x1="620" y1="340" x2={620 + 440 * chain} y2="340" stroke={C.dim} strokeWidth="3" strokeDasharray="10 10"/>
      </svg>
      <Panel x={1080} y={230} w={600} h={220} k={snap(f, 22)}>
        <Label style={{position: 'absolute', left: 26, top: 22}}>LOAN · SECURED BY CHIPS</Label>
        <div style={{position: 'absolute', left: 30, top: 70, fontFamily: F.mono, fontWeight: 700, fontSize: 110, color: C.text}}>$12B</div>
      </Panel>
      {/* price tag */}
      <div style={{position: 'absolute', left: 260, top: 620, opacity: snap(f, 34)}}>
        <Label>VALUE PER CHIP · ON PAPER</Label>
        <div style={{position: 'relative', display: 'inline-block', marginTop: 8}}>
          <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: 130, color: f > 70 ? C.dim : C.text}}>$40,000</div>
          <div style={{position: 'absolute', left: -10, top: 76, height: 10, width: `${slash * 105}%`, background: C.loss, transform: 'rotate(-6deg)', boxShadow: `0 0 18px ${C.loss}`}}/>
        </div>
      </div>
      <div style={{position: 'absolute', left: 1080, top: 600, opacity: newP, transform: `translateY(${(1 - newP) * 30}px)`}}>
        <Label color={C.loss}>FIRE SALE · EVERY LENDER SELLING</Label>
        <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: 190, color: C.loss, marginTop: 4}}>$5,000</div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- 3: S&P 500 concentration + your fund ---------------- */
const Scene3 = () => {
  const f = useCurrentFrame();
  const fill = ramp(f, 10, 40, outExpo);
  const drop = f > 70;
  const cells = 500;
  return (
    <AbsoluteFill>
      <Label style={{position: 'absolute', left: 120, top: 110}} size={28}>S&amp;P 500 · 500 COMPANIES · BY SIZE</Label>
      <div style={{position: 'absolute', left: 120, top: 160, width: 1680, height: 170, display: 'flex', borderRadius: 6, overflow: 'hidden', border: `1px solid ${C.line}`}}>
        <div style={{width: `${35.7 * fill}%`, background: `linear-gradient(90deg, ${drop ? C.loss : C.money}, ${drop ? '#b02a3e' : '#1d8fb0'})`,
          display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <span style={{fontFamily: F.mono, fontWeight: 700, fontSize: 44, whiteSpace: 'nowrap', color: '#04101c', opacity: snap(f, 40)}}>7 COMPANIES · 36%</span>
        </div>
        <div style={{flex: 1, backgroundImage: `repeating-linear-gradient(90deg, #1a2648 0 3px, transparent 3px 6px)`, opacity: snap(f, 6)}}/>
      </div>
      <Label style={{position: 'absolute', left: 120 + 1680 * 0.357 + 24, top: 345, opacity: snap(f, 46)}} color={C.dim} size={20}>THE OTHER 493</Label>
      {/* your fund HUD */}
      <Panel x={560} y={450} w={800} h={420} k={snap(f, 50)} accent={drop ? C.loss : C.lineHi}>
        <Label style={{position: 'absolute', left: 30, top: 28}}>YOUR RETIREMENT FUND</Label>
        <Counter keys={[[60, 10000], [80, 9100], [120, 8000]]} size={150} color={drop ? C.loss : C.text} style={{position: 'absolute', left: 34, top: 76}}/>
        <div style={{position: 'absolute', left: 36, top: 262, fontFamily: F.mono, fontSize: 36, color: C.loss, opacity: snap(f, 82)}}>
          ▼ {usd(lerp(0, 2000, ramp(f, 80, 40, outExpo)))} · {f < 118 ? 'MON 12:10' : 'FRI 16:00'}
        </div>
        <svg width="730" height="70" style={{position: 'absolute', left: 36, top: 330}} viewBox="0 0 480 60" preserveAspectRatio="none">
          <polyline fill="none" stroke={C.loss} strokeWidth="3" strokeDasharray="600" strokeDashoffset={600 * (1 - ramp(f, 70, 60))}
            points="0,10 60,14 100,8 160,28 220,24 280,40 340,36 400,52 480,56"/>
        </svg>
      </Panel>
    </AbsoluteFill>
  );
};

/* ---------------- 4: the crash travels: camera over the world ---------------- */
const route = [['ny', 'tokyo', 20], ['tokyo', 'mumbai', 70], ['mumbai', 'cairo', 110], ['cairo', 'shanghai', 150]];
const Scene4 = () => {
  const f = useCurrentFrame();
  // camera keys: focus point + zoom
  const KT = [0, 20, 60, 80, 110, 140, 175];
  const pts = [pt('ny'), pt('ny'), pt('tokyo'), pt('mumbai'), pt('cairo'), pt('shanghai'), [960, 560]];
  const zs = [1.0, 1.6, 1.9, 1.9, 1.9, 1.7, 1.0];
  const fx = interpolate(f, KT, pts.map((p) => p[0]), {extrapolateRight: 'clamp', easing: inOut});
  const fy = interpolate(f, KT, pts.map((p) => p[1]), {extrapolateRight: 'clamp', easing: inOut});
  const z = interpolate(f, KT, zs, {extrapolateRight: 'clamp', easing: inOut});
  const lit = (t) => f >= t;
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transformOrigin: '0 0',
        transform: `translate(${W / 2 - fx * z}px, ${H / 2 - fy * z}px) scale(${z})`}}>
        <WorldMap hot={['840', ...(lit(60) ? ['392'] : []), ...(lit(100) ? ['356'] : []), ...(lit(140) ? ['818'] : []), ...(lit(175) ? ['156'] : [])]}/>
        {route.map(([a, b, s]) => <Arc key={a + b} a={a} b={b} k={ramp(f, s, 34, inOut)} lift={a === 'ny' ? 0.18 : 0.3}/>)}
        <City id="ny" hot/>
        <City id="tokyo" k={snap(f, 50)} hot={lit(54)}/>
        <City id="mumbai" k={snap(f, 98)} hot={lit(102)} labelSide="l"/>
        <City id="cairo" k={snap(f, 138)} hot={lit(142)} labelSide="l"/>
        <City id="shanghai" k={snap(f, 176)} hot={lit(180)}/>
      </div>
      {/* term card for a word the viewer may not know */}
      <Term x={110} y={760} k={snap(f, 66) * (1 - snap(f, 120, 8))} term="IOU = GOVERNMENT BOND"
        def="A piece of paper that says: America owes you this money, plus interest."/>
    </AbsoluteFill>
  );
};

/* ---------------- 5: rates up -> your loans cost more ---------------- */
const Icon = ({kind, col}) => {
  const p = {house: 'M10 46 L50 12 L90 46 L90 90 L10 90 Z M38 90 L38 62 L62 62 L62 90',
    car: 'M8 64 L18 40 Q22 32 32 32 L68 32 Q78 32 82 40 L92 64 L92 80 L8 80 Z M24 80 a8 8 0 1 0 0.1 0 M76 80 a8 8 0 1 0 0.1 0',
    card: 'M6 24 L94 24 Q98 24 98 28 L98 76 Q98 80 94 80 L6 80 Q2 80 2 76 L2 28 Q2 24 6 24 Z M2 38 L98 38 M2 48 L98 48'}[kind];
  return <svg width="220" height="220" viewBox="0 0 100 100"><path d={p} fill="none" stroke={col} strokeWidth="4" strokeLinejoin="round"/></svg>;
};
const Scene5 = () => {
  const f = useCurrentFrame();
  const needle = interpolate(f, [10, 50], [-70, 40], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: outExpo});
  const items = [['house', 'MORTGAGE', '+$310/MO', 60], ['car', 'CAR LOAN', '+$45/MO', 72], ['card', 'CREDIT CARD', '+4%', 84]];
  return (
    <AbsoluteFill>
      <Label style={{position: 'absolute', left: 150, top: 160}} size={30}>US INTEREST RATES</Label>
      <svg width="780" height="470" viewBox="0 0 600 360" style={{position: 'absolute', left: 90, top: 230}}>
        <path d="M60 320 A240 240 0 0 1 540 320" fill="none" stroke={C.line} strokeWidth="26"/>
        <path d="M60 320 A240 240 0 0 1 540 320" fill="none" stroke={C.warn} strokeWidth="26" strokeDasharray="754" strokeDashoffset={754 * (1 - (needle + 70) / 180)}/>
        <g transform={`translate(300 320) rotate(${needle})`}><line x1="0" y1="0" x2="0" y2="-210" stroke={C.text} strokeWidth="6" strokeLinecap="round"/></g>
        <circle cx="300" cy="320" r="16" fill={C.text}/>
      </svg>
      <Label style={{position: 'absolute', left: 230, top: 730, opacity: snap(f, 40)}} color={C.warn} size={34}>JAPAN SELLS → RATES ↑</Label>
      {items.map(([k, name, tag, s], i) => {
        const a = snap(f, s, 10);
        return (
          <div key={k} style={{position: 'absolute', left: 930 + i * 320, top: 330, opacity: a, transform: `translateY(${(1 - a) * 40}px)`, textAlign: 'center', width: 260}}>
            <Icon kind={k} col={C.text}/>
            <Label color={C.text} size={28} style={{marginTop: 10}}>{name}</Label>
            <div style={{fontFamily: F.mono, fontWeight: 700, fontSize: 52, color: C.warn, marginTop: 10, opacity: snap(f, s + 8)}}>{tag}</div>
          </div>
        );
      })}
      <div style={{position: 'absolute', left: 900, top: 700, width: 900, fontFamily: F.mono, fontSize: 22, color: C.dim, opacity: snap(f, 110)}}>
        EXAMPLE VALUES · SCENARIO
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- composition ---------------- */
export const PROBE_LEN = 780;
export const Probe = () => (
  <AbsoluteFill style={{backgroundColor: C.bg0}}>
    <FontFaces/>
    <Bg/>
    <Sequence from={0} durationInFrames={150}><Scene1/></Sequence>
    <Sequence from={150} durationInFrames={150}><Scene2/></Sequence>
    <Sequence from={300} durationInFrames={150}><Scene3/></Sequence>
    <Sequence from={450} durationInFrames={190}><Scene4/></Sequence>
    <Sequence from={640} durationInFrames={140}><Scene5/></Sequence>
    {[150, 300, 450, 640].map((s) => <ScanWipe key={s} s={s - 6} d={14}/>)}
    {/* music bed */}
    <Audio src={staticFile('music/Cipher.mp3')} volume={(f) => interpolate(f, [0, 20, 740, 780], [0, 0.22, 0.22, 0], {extrapolateRight: 'clamp'})}/>
    {/* SFX: one family, every movement */}
    {S('tick', 6, 0.5)}{S('tick', 12, 0.5)}{S('tick', 18, 0.5)}{S('pop', 40, 0.6)}
    {S('impact', 75, 0.9)}{S('glitch', 75, 0.6)}{S('riser', 100, 0.35)}
    {[144, 294, 444, 634].map((s) => S('whoosh', s, 0.7))}
    {S('blip_up', 150, 0.5)}{S('swish', 164, 0.5)}{S('pop', 172, 0.6)}{S('pop', 184, 0.5)}
    {S('slam', 216, 0.85)}{S('whoosh_down', 222, 0.5)}{S('blip_down', 224, 0.6)}
    {S('scan', 310, 0.5)}{S('pop', 350, 0.5)}{S('digits', 360, 0.6)}{S('blip_down', 370, 0.6)}{S('digits', 420, 0.6)}{S('warn', 420, 0.35)}
    {S('whoosh_short', 470, 0.6)}{S('pop', 500, 0.6)}{S('impact', 504, 0.4)}{S('swish', 516, 0.5)}
    {S('whoosh_short', 520, 0.6)}{S('pop', 548, 0.6)}{S('impact', 552, 0.35)}{S('whoosh_short', 560, 0.6)}
    {S('pop', 588, 0.6)}{S('impact', 592, 0.35)}{S('whoosh_short', 600, 0.6)}{S('pop', 626, 0.6)}{S('impact', 630, 0.4)}
    {S('riser', 640, 0.3)}{S('blip_up', 660, 0.5)}{S('tick', 700, 0.5)}{S('coin', 708, 0.5)}{S('tick', 712, 0.5)}{S('coin', 720, 0.5)}{S('tick', 724, 0.5)}{S('coin', 732, 0.5)}
  </AbsoluteFill>
);

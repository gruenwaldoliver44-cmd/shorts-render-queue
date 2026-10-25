// Live dashboard for Oliver's Mac: http://localhost:8765
// Started automatically by agent.mjs (copied to ~/ShortsRenderAgent/dashboard.mjs). Reads only local state; no secrets.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";

const A = path.join(os.homedir(), "ShortsRenderAgent");
const STATE = path.join(A, "state");
const PORT = 8765;
const CH = { "21": "CT", "22": "MT", "23": "MC", "24": "FT" };
const CHN = { CT: "Compound Times", MT: "Machine Times", MC: "Money Classics", FT: "Future Tender" };
const sh = (c) => (spawnSync("/bin/bash", ["-c", c], { encoding: "utf8", timeout: 4000 }).stdout || "").trim();
const readJSON = (f) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return null; } };
const readTxt = (f) => { try { return fs.readFileSync(f, "utf8").trim(); } catch { return ""; } };
const countFiles = (d) => { try { return fs.readdirSync(d).filter((f) => !f.startsWith(".")).length; } catch { return 0; } };
// frames finished according to a Blender log (works when Blender writes one video file instead of single frames)
const countLog = (f) => { try { return (fs.readFileSync(f, "utf8").match(/Video append frame|Saved: '|Saved: "/g) || []).length; } catch { return 0; } };

let lastCpu = os.cpus();
const cpuPct = () => {
  const now = os.cpus(); let idle = 0, total = 0;
  now.forEach((c, i) => { const p = lastCpu[i] || c; for (const k in c.times) total += c.times[k] - p.times[k]; idle += c.times.idle - p.times.idle; });
  lastCpu = now; return total > 0 ? Math.round(100 * (1 - idle / total)) : 0;
};
const progHist = {};

const collect = () => {
  const st = readJSON(path.join(STATE, "status.json")) || {};
  const gpu = Number((sh("ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '\"Device Utilization %\"=[0-9]*' | head -1 | grep -o '[0-9]*$'") || "0"));
  const memFree = Number((sh("memory_pressure -Q 2>/dev/null | grep -o '[0-9]*%' | tail -1 | tr -d '%'") || "0"));
  const therm = sh("pmset -g therm 2>/dev/null | grep -i 'CPU_Speed_Limit' | grep -o '[0-9]*'");
  const diskGB = Math.round(Number(sh("df -k \"$HOME\" | tail -1 | awk '{print $4}'") || 0) / 1048576);
  // real Blender processes only (binary path first). A render has "-b"/"--background"; Blender also starts its own
  // helper processes (e.g. shader compilation) without "-b": those are shown as helpers, not as a second render.
  const bl = sh("ps -axo pid=,pcpu=,rss=,etime=,command=").split("\n").map((l) => l.trim().split(/\s+/)).filter((m) => (m[4] || "").endsWith("Blender.app/Contents/MacOS/Blender")).map((m) => {
    const args = m.slice(5);
    return { pid: m[0], cpu: Number(String(m[1]).replace(",", ".")) || 0, ram_gb: Math.round(Number(m[2]) / 104857.6) / 10, time: m[3], render: args.includes("-b") || args.includes("--background") };
  });
  const agentRunning = sh("pgrep -f '[a]gent/agent.mjs' | wc -l") !== "0";
  const hb = readTxt(path.join(STATE, "hb_result"));
  const loopBeat = readTxt(path.join(A, "heartbeat"));
  let progress = null;
  if (st.state === "busy" && st.progress && st.progress.total) {
    const n = st.progress.log ? countLog(st.progress.log) : countFiles(st.progress.dir); const key = st.progress.log || st.progress.dir; const h = (progHist[key] ||= []); h.push({ t: Date.now(), n }); while (h.length > 60) h.shift();
    let eta_min = null; if (h.length > 5 && h[h.length - 1].n > h[0].n) eta_min = Math.round(((h[h.length - 1].t - h[0].t) / (h[h.length - 1].n - h[0].n)) * (st.progress.total - n) / 60000);
    progress = { n, total: st.progress.total, eta_min };
  }
  const jobsDir = path.join(A, "repo", "jobs"); let queue = [];
  try {
    for (const f of fs.readdirSync(jobsDir).filter((x) => x.endsWith(".json")).sort()) {
      const j = readJSON(path.join(jobsDir, f)) || {}; const id = j.id || f.replace(/\.json$/, "");
      if (fs.existsSync(path.join(STATE, "done", id))) continue;
      const fail = Number(readTxt(path.join(STATE, "failed", id)) || 0); if (fail >= (j.retries ?? 2)) continue;
      if (j.expires && Date.now() > Date.parse(j.expires)) continue;
      if (st.state === "busy" && st.job === id) continue;
      queue.push({ id, ch: CH[id.slice(0, 2)] || "", title: j.title || id });
    }
  } catch {}
  const recent = (d) => { try { return fs.readdirSync(path.join(STATE, d)).map((f) => ({ id: f, t: fs.statSync(path.join(STATE, d, f)).mtimeMs })).sort((a, b) => b.t - a.t).slice(0, 6); } catch { return []; } };
  // one file per channel (status/CT.json ...) so the four build agents never edit the same file
  const pipeline = { channels: {}, updated: 0 };
  for (const k of ["CT", "MT", "MC", "FT"]) { const x = readJSON(path.join(A, "repo", "status", k + ".json")); if (x) { pipeline.channels[k] = x; const u = Date.parse(x.updated || 0) || 0; if (u > pipeline.updated) pipeline.updated = u; } }
  return { now: Date.now(), st, cpu: cpuPct(), gpu, memFree, therm: therm ? Number(therm) : null, diskGB, blender: bl, agentRunning, hb, loopBeat, progress, queue, done: recent("done"), failed: recent("failed"), pipeline };
};

const HTML = `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shorts Kommandozentrale</title><style>
:root{--bg:#0b111a;--card:#141c28;--line:#223044;--ink:#e8eef6;--mut:#8a9bb3;--ok:#3ddc97;--warn:#ffc04d;--bad:#ff5e6c;--acc:#5ab4ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:20px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.card h2{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin:0 0 10px}
.big{font-size:22px;font-weight:700}.mut{color:var(--mut)}.row{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid var(--line)}.row:last-child{border:0}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:8px;vertical-align:middle}
.ok{background:var(--ok);box-shadow:0 0 10px var(--ok)}.warn{background:var(--warn);box-shadow:0 0 10px var(--warn)}.bad{background:var(--bad);box-shadow:0 0 10px var(--bad)}.idle{background:var(--mut)}
.meter{height:10px;background:#0d1520;border-radius:6px;overflow:hidden;margin-top:6px}.meter>i{display:block;height:100%;background:var(--acc);transition:width .6s}
.hero{grid-column:1/-1}.hero .big{font-size:26px}.steps{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}.steps span{padding:4px 10px;border-radius:20px;border:1px solid var(--line);color:var(--mut);font-size:13px}
.steps .done{border-color:var(--ok);color:var(--ok)}.steps .now{border-color:var(--acc);color:#fff;background:#173250}.steps .err{border-color:var(--bad);color:var(--bad)}
.tag{font-size:12px;padding:2px 8px;border-radius:10px;background:#1d2a3b;color:var(--acc);margin-right:6px}
.vids{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(560px,1fr));margin-bottom:14px}
.vc{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;display:flex;gap:16px}
.vc .main{flex:1;min-width:0}.vc .ph{width:150px;flex:none}
.vc .ph img,.vc .ph video{width:150px;aspect-ratio:9/16;object-fit:cover;border-radius:10px;border:1px solid var(--line);background:#0d1520;display:block;cursor:pointer}
.vc .ph .none{width:150px;aspect-ratio:9/16;border-radius:10px;border:1px dashed var(--line);display:flex;align-items:center;justify-content:center;text-align:center;color:var(--mut);font-size:13px;padding:10px}
.vh{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.vh .t{font-size:18px;font-weight:700}
.chip{font-size:12px;padding:3px 9px;border-radius:12px;font-weight:600}.c-run{background:#173250;color:#9fd2ff}.c-wait{background:#2a2f3a;color:#b9c4d4}.c-err{background:#3a1a20;color:#ff9aa4}.c-done{background:#123526;color:#7ff0bd}
.pct{display:flex;align-items:baseline;gap:10px;margin:12px 0 4px}.pct b{font-size:30px}
.pbar{height:14px;background:#0d1520;border-radius:8px;overflow:hidden}.pbar>i{display:block;height:100%;background:linear-gradient(90deg,#3a8dde,#5ab4ff 60%,#3ddc97);border-radius:8px;transition:width .8s}
.stp{display:flex;justify-content:space-between;margin:14px 0 6px;position:relative}.stp:before{content:"";position:absolute;left:8px;right:8px;top:7px;height:2px;background:var(--line)}
.stp div{position:relative;text-align:center;flex:1;min-width:0;font-size:12px;color:var(--mut)}.stp i{display:block;width:16px;height:16px;border-radius:50%;margin:0 auto 4px;background:#0d1520;border:2px solid var(--line)}
.stp .d i{background:var(--ok);border-color:var(--ok)}.stp .d{color:var(--ok)}.stp .n i{background:var(--acc);border-color:var(--acc);box-shadow:0 0 0 4px #5ab4ff33;animation:pl 1.6s infinite}.stp .n{color:#fff;font-weight:600}.stp .e i{background:var(--bad);border-color:var(--bad)}.stp .e{color:var(--bad)}
@keyframes pl{50%{box-shadow:0 0 0 8px #5ab4ff11}}
.kv{display:grid;grid-template-columns:110px 1fr;gap:4px 10px;margin-top:10px;font-size:14px}.kv span:nth-child(odd){color:var(--mut)}
.live{margin-top:10px;padding:8px 10px;border-radius:10px;background:#10233a;font-size:13px}
</style></head><body><h1>Shorts Kommandozentrale</h1><div class="sub" id="sub">lädt …</div><div class="vids" id="v"></div><div class="grid" id="g"></div>
<script>
const CHN={CT:"Compound Times",MT:"Machine Times",MC:"Money Classics",FT:"Future Tender"};
const ch=id=>({"21":"CT","22":"MT","23":"MC","24":"FT"})[String(id).slice(0,2)]||"";
const mins=ms=>{const m=Math.max(0,Math.round(ms/60000));return m<60?m+" Min":Math.floor(m/60)+" h "+(m%60)+" Min"};
const hm=t=>new Date(t).toLocaleTimeString("de-AT",{hour:"2-digit",minute:"2-digit"});
const dot=c=>'<span class="dot '+c+'"></span>';
const meter=(p,c)=>'<div class="meter"><i style="width:'+Math.min(100,p)+'%;'+(c?'background:'+c:'')+'"></i></div>';
const lvl=(v,w,b)=>v>=b?"var(--bad)":v>=w?"var(--warn)":"var(--ok)";
async function tick(){let d;try{d=await (await fetch("/api")).json()}catch(e){document.getElementById("sub").innerHTML=dot("bad")+"Dashboard nicht erreichbar";return}
const s=d.st||{},g=[];const busy=s.state==="busy"&&d.agentRunning;const nb=d.blender.filter(x=>x.render).length;
let mood="ok",msg="Alles in Ordnung";
if(nb>1){mood="bad";msg="Mehr als ein Blender gleichzeitig – Claude Bescheid geben"}
else if(!d.agentRunning&&nb>0){mood="bad";msg="Blender läuft ohne Auftrag"}
else if(d.memFree&&d.memFree<10){mood="warn";msg="Arbeitsspeicher knapp"}
else if(d.hb&&!/ (200|201)$/.test(d.hb)){mood="warn";msg="Verbindung zu Claude gestört"}
else if(d.diskGB<10){mood="warn";msg="Speicherplatz knapp"}
else if(d.therm&&d.therm<80){mood="warn";msg="Mac drosselt wegen Hitze"}
document.getElementById("sub").innerHTML=dot(mood)+msg+' · aktualisiert '+new Date(d.now).toLocaleTimeString("de-AT");
// video cards (rebuilt only when their data changes, so preview images and videos do not flicker)
const P=["Skript","Stimme","Szenen","Vorschau","Final","Ton & Prüfung","Geplant"],PS=["Skript","Stimme","Szenen","Vorschau","Final","Ton","Geplant"],PW=[8,15,30,45,80,92,100];
const src=u=>!u?"":u.startsWith("local:")?"/local/"+u.slice(6):u;
const live=(busy&&d.progress)?{ch:ch(s.job),n:d.progress.n,t:d.progress.total,eta:d.progress.eta_min,label:s.label,title:s.title}:(busy?{ch:ch(s.job),label:s.label,title:s.title}:null);
const vkey=JSON.stringify([d.pipeline,live&&[live.ch,live.n,live.label]]);
if(vkey!==window._vk){window._vk=vkey;let v="";
 for(const k of ["CT","MT","MC","FT"]){const x=(d.pipeline&&d.pipeline.channels||{})[k];if(!x)continue;let i=P.indexOf(x.stage);if(i<0)i=0;
  const pc=Math.max(0,Math.min(100,typeof x.progress==="number"?x.progress:(i?PW[i-1]:0)));
  const st=x.error?["c-err","Problem"]:x.stage==="Geplant"?["c-done","Geplant"]:(live&&live.ch===k)?["c-run","Mac rendert"]:["c-wait","in Arbeit"];
  let ph=x.preview_img?'<img src="'+src(x.preview_img)+'" title="Klicken zum Abspielen" onclick="'+(x.preview_video?"window.open('"+src(x.preview_video)+"')":"window.open(this.src)")+'">':x.preview_video?'<video src="'+src(x.preview_video)+'" muted loop autoplay playsinline onclick="window.open(this.src)"></video>':'<div class="none">Noch keine Vorschau</div>';
  if(x.preview_note)ph+='<div class="mut" style="font-size:12px;margin-top:6px">'+x.preview_note+'</div>';
  v+='<div class="vc"><div class="main"><div class="vh"><span class="tag">'+k+'</span><span class="t">'+(x.title||k)+'</span><span class="chip '+st[0]+'">'+st[1]+'</span></div><div class="mut">'+CHN[k]+(x.topic?' · '+x.topic:'')+'</div>';
  v+='<div class="pct"><b>'+Math.round(pc)+' %</b><span class="mut">fertig</span></div><div class="pbar"><i style="width:'+pc+'%"></i></div>';
  v+='<div class="stp">'+P.map((n,j)=>'<div class="'+(x.error&&j===i?"e":(j<i||x.stage==="Geplant")?"d":j===i?"n":"")+'"><i></i>'+PS[j]+'</div>').join("")+'</div>';
  v+='<div class="kv"><span>Jetzt</span><span>'+(x.note||"–")+'</span>'+(x.next?'<span>Als Nächstes</span><span>'+x.next+'</span>':'')+'<span>Fertig ca.</span><span><b style="color:var(--acc)">'+(x.eta||"wird berechnet")+'</b></span>'+(x.slot?'<span>Post</span><span>'+x.slot+'</span>':'')+'</div>';
  if(live&&live.ch===k)v+='<div class="live">Mac rendert gerade: <b>'+(live.label||"")+'</b>'+(live.t?' · '+live.n+' von '+live.t+' Bildern'+(live.eta!=null?' · noch ca. '+live.eta+' Min':''):'')+(live.t?meter(Math.round(100*live.n/live.t)):'')+'</div>';
  v+='<div class="mut" style="font-size:12px;margin-top:10px">Stand '+(x.updated?new Date(x.updated).toLocaleTimeString("de-AT",{hour:"2-digit",minute:"2-digit"}):"–")+'</div></div><div class="ph">'+ph+'</div></div>'}
 document.getElementById("v").innerHTML=v||'<div class="card mut">Noch keine Videos gemeldet.</div>'}
// hero
let h='<div class="card hero"><h2>Gerade jetzt</h2>';
if(busy){h+='<div class="big">'+dot("ok")+(CHN[ch(s.job)]||"System")+' – '+(s.title||s.job)+'</div>';
 h+='<div class="mut">Schritt '+(s.step||0)+' von '+(s.steps||"?")+': <b style="color:#fff">'+(s.label||"")+'</b>'+(s.step_since?' · seit '+mins(d.now-Date.parse(s.step_since)):'')+' · Auftrag seit '+hm(s.job_since)+' ('+mins(d.now-Date.parse(s.job_since))+' von max. '+s.timeout_min+' Min)</div>';
 if(d.progress){const p=Math.round(100*d.progress.n/d.progress.total);h+='<div style="margin-top:10px">'+d.progress.n+' von '+d.progress.total+' Bildern · '+p+' %'+(d.progress.eta_min!=null?' · noch ca. '+d.progress.eta_min+' Min':'')+'</div>'+meter(p)}
 const tl=Date.parse(s.job_since)+s.timeout_min*60000-d.now;if(tl<10*60000)h+='<div style="color:var(--warn);margin-top:8px">Zeitlimit in '+mins(tl)+'</div>';
}else if(d.agentRunning){h+='<div class="big">'+dot("ok")+'Prüft die Auftragsliste …</div>'}
else{h+='<div class="big">'+dot("idle")+'Bereit – wartet auf den nächsten Auftrag</div><div class="mut">Der Mac schaut jede Minute nach neuen Aufträgen.</div>'}
if(s.last)h+='<div class="mut" style="margin-top:8px">Zuletzt: '+(CHN[ch(s.last.job)]||"")+' – '+s.last.title+': <b style="color:'+(s.last.result==="fertig"?"var(--ok)":"var(--bad)")+'">'+s.last.result+'</b> um '+hm(s.last.at)+'</div>';
g.push(h+'</div>');
// machine
g.push('<div class="card"><h2>Prozessor</h2><div class="big">'+d.cpu+' %</div>'+meter(d.cpu,lvl(d.cpu,95,101))+'</div>');
g.push('<div class="card"><h2>Grafikkarte</h2><div class="big">'+d.gpu+' %</div>'+meter(d.gpu)+'<div class="mut" style="margin-top:6px">'+(d.gpu>20?"rechnet":"wenig Last")+'</div></div>');
g.push('<div class="card"><h2>Arbeitsspeicher frei</h2><div class="big">'+(d.memFree||"?")+' %</div>'+meter(d.memFree,lvl(100-d.memFree,80,90))+'</div>');
g.push('<div class="card"><h2>Festplatte frei</h2><div class="big">'+d.diskGB+' GB</div>'+meter(Math.min(100,d.diskGB),lvl(100-Math.min(100,d.diskGB),85,92))+(d.therm!=null?'<div class="mut" style="margin-top:6px">Leistung: '+d.therm+' %'+(d.therm<100?' (Hitzebremse)':'')+'</div>':'')+'</div>');
// blender
let b='<div class="card"><h2>Blender</h2>';if(!d.blender.length)b+='<div class="big">'+dot("idle")+'aus</div>';else d.blender.forEach(x=>{b+='<div class="row"><span>'+dot(!x.render?"idle":nb>1?"bad":"ok")+(x.render?'Render':'Hilfsprozess')+' '+x.pid+'</span><span>'+Math.round(x.cpu)+' % CPU · '+x.ram_gb+' GB · '+x.time+'</span></div>'});g.push(b+'</div>');
// connection
const hbok=/ (200|201)$/.test(d.hb);g.push('<div class="card"><h2>Verbindung zu Claude</h2><div class="big">'+dot(hbok?"ok":d.hb?"bad":"warn")+(hbok?"verbunden":d.hb?"gestört":"noch keine Meldung")+'</div><div class="mut">'+(d.hb?"letzte Meldung "+hm(d.hb.split(" ")[0]):"")+'</div></div>');
// queue
let q='<div class="card"><h2>Warteschlange ('+d.queue.length+')</h2>';q+=d.queue.length?d.queue.slice(0,8).map(x=>'<div class="row"><span><span class="tag">'+(x.ch||"SYS")+'</span>'+x.title+'</span></div>').join(""):'<div class="mut">leer</div>';g.push(q+'</div>');
// history
let r='<div class="card"><h2>Zuletzt erledigt</h2>';r+=d.done.map(x=>'<div class="row"><span>'+dot("ok")+x.id+'</span><span class="mut">'+hm(x.t)+'</span></div>').join("")+d.failed.slice(0,3).map(x=>'<div class="row"><span>'+dot("bad")+x.id+'</span><span class="mut">'+hm(x.t)+'</span></div>').join("");g.push(r+'</div>');
document.getElementById("g").innerHTML=g.join("")}
tick();setInterval(tick,3000);
</script></body></html>`;

const TYPES = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp", ".mp4": "video/mp4" };
http.createServer((req, res) => {
  if (req.url.startsWith("/local/")) {
    // serve preview files from the Mac's work folders only (images and mp4)
    const rel = decodeURIComponent(req.url.slice(7).split("?")[0]); const f = path.resolve(A, rel); const t = TYPES[path.extname(f).toLowerCase()];
    if (!t || !f.startsWith(path.join(A, "work") + path.sep) || !fs.existsSync(f)) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "Content-Type": t, "Cache-Control": "max-age=60" }); fs.createReadStream(f).pipe(res); return;
  }
  if (req.url.startsWith("/api")) { res.writeHead(200, { "Content-Type": "application/json", "Cache-Control": "no-store" }); res.end(JSON.stringify(collect())); return; }
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); res.end(HTML);
}).listen(PORT, "127.0.0.1");

// heartbeat every 2 min while the dashboard runs (the agent itself is blocked during long jobs).
// Same file and branch as agent.mjs; token stays on the Mac. Best effort.
const beat = async () => {
  try {
    const tf = path.join(A, "token"); if (!fs.existsSync(tf)) return;
    const d = collect(); const recent = (x) => x.map((r) => r.id);
    const status = { ts: new Date().toISOString(), source: "dashboard", current: readTxt(path.join(STATE, "current")), busy: d.st.state === "busy" && d.agentRunning, free_gb: d.diskGB, blender_procs: d.blender.filter((x) => x.render).length, cpu: d.cpu, gpu: d.gpu, mem_free_pct: d.memFree, progress: d.progress, done: recent(d.done), failed: recent(d.failed), status: d.st, queue: d.queue.map((q) => q.id) };
    // keep the full done/failed lists the agent writes
    const h = { Authorization: `Bearer ${fs.readFileSync(tf, "utf8").trim()}`, "User-Agent": "shorts-dashboard", Accept: "application/vnd.github+json" };
    const api = "https://api.github.com/repos/gruenwaldoliver44-cmd/shorts-render-queue/contents/heartbeat.json";
    const g = await fetch(api + "?ref=heartbeat", { headers: h, signal: AbortSignal.timeout(15000) });
    let sha; if (g.ok) { const j = await g.json(); sha = j.sha; try { const old = JSON.parse(Buffer.from(j.content, "base64").toString()); status.done = [...new Set([...status.done, ...(old.done || [])])].slice(0, 60); status.failed = [...new Set([...status.failed, ...(old.failed || [])])].slice(0, 60); } catch {} }
    const p = await fetch(api, { method: "PUT", headers: h, signal: AbortSignal.timeout(15000), body: JSON.stringify({ message: "heartbeat", branch: "heartbeat", content: Buffer.from(JSON.stringify(status, null, 1)).toString("base64"), ...(sha ? { sha } : {}) }) });
    fs.writeFileSync(path.join(STATE, "hb_result"), `${new Date().toISOString()} ${p.status}`);
  } catch (e) { try { fs.writeFileSync(path.join(STATE, "hb_result"), `${new Date().toISOString()} error`); } catch {} }
};
setTimeout(beat, 5000); setInterval(beat, 120000);

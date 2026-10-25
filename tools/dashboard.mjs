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
  // only real Blender processes (command starts with the Blender binary), not shell wrappers that mention it
  const bl = sh("ps -axo pid=,pcpu=,rss=,etime=,command=").split("\n").map((l) => l.trim().split(/\s+/)).filter((m) => (m[4] || "").endsWith("Blender.app/Contents/MacOS/Blender")).map((m) => (
    { pid: m[0], cpu: Number(String(m[1]).replace(",", ".")) || 0, ram_gb: Math.round(Number(m[2]) / 104857.6) / 10, time: m[3] }
  ));
  const agentRunning = sh("pgrep -f '[a]gent/agent.mjs' | wc -l") !== "0";
  const hb = readTxt(path.join(STATE, "hb_result"));
  const loopBeat = readTxt(path.join(A, "heartbeat"));
  let progress = null;
  if (st.state === "busy" && st.progress && st.progress.total) {
    const n = countFiles(st.progress.dir); const h = (progHist[st.progress.dir] ||= []); h.push({ t: Date.now(), n }); while (h.length > 60) h.shift();
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
</style></head><body><h1>Shorts Kommandozentrale</h1><div class="sub" id="sub">lädt …</div><div class="grid" id="g"></div>
<script>
const CHN={CT:"Compound Times",MT:"Machine Times",MC:"Money Classics",FT:"Future Tender"};
const ch=id=>({"21":"CT","22":"MT","23":"MC","24":"FT"})[String(id).slice(0,2)]||"";
const mins=ms=>{const m=Math.max(0,Math.round(ms/60000));return m<60?m+" Min":Math.floor(m/60)+" h "+(m%60)+" Min"};
const hm=t=>new Date(t).toLocaleTimeString("de-AT",{hour:"2-digit",minute:"2-digit"});
const dot=c=>'<span class="dot '+c+'"></span>';
const meter=(p,c)=>'<div class="meter"><i style="width:'+Math.min(100,p)+'%;'+(c?'background:'+c:'')+'"></i></div>';
const lvl=(v,w,b)=>v>=b?"var(--bad)":v>=w?"var(--warn)":"var(--ok)";
async function tick(){let d;try{d=await (await fetch("/api")).json()}catch(e){document.getElementById("sub").innerHTML=dot("bad")+"Dashboard nicht erreichbar";return}
const s=d.st||{},g=[];const busy=s.state==="busy"&&d.agentRunning;const nb=d.blender.length;
let mood="ok",msg="Alles in Ordnung";
if(nb>1){mood="bad";msg="Mehr als ein Blender gleichzeitig – Claude Bescheid geben"}
else if(!d.agentRunning&&nb>0){mood="bad";msg="Blender läuft ohne Auftrag"}
else if(d.memFree&&d.memFree<10){mood="warn";msg="Arbeitsspeicher knapp"}
else if(d.hb&&!/ (200|201)$/.test(d.hb)){mood="warn";msg="Verbindung zu Claude gestört"}
else if(d.diskGB<10){mood="warn";msg="Speicherplatz knapp"}
else if(d.therm&&d.therm<80){mood="warn";msg="Mac drosselt wegen Hitze"}
document.getElementById("sub").innerHTML=dot(mood)+msg+' · aktualisiert '+new Date(d.now).toLocaleTimeString("de-AT");
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
// pipeline per channel
if(d.pipeline&&d.pipeline.channels){const P=["Skript","Stimme","Szenen","Vorschau","Final","Ton & Prüfung","Geplant"];
 let c='<div class="card hero"><h2>Videos in Arbeit</h2>';
 for(const k of ["CT","MT","MC","FT"]){const x=d.pipeline.channels[k];if(!x)continue;const i=P.indexOf(x.stage);
  c+='<div style="margin:10px 0 14px"><span class="tag">'+k+'</span><b>'+(x.title||CHN[k])+'</b> <span class="mut">'+(x.note||"")+'</span><div class="steps">'+P.map((n,j)=>'<span class="'+(x.error&&j===i?"err":j<i||(j===i&&x.stage==="Geplant")?"done":j===i?"now":"")+'">'+n+'</span>').join("")+'</div>'+(x.slot?'<div class="mut" style="margin-top:6px">Post: '+x.slot+'</div>':'')+'</div>'}
 g.push(c+'<div class="mut">Stand von Claude: '+(d.pipeline.updated?new Date(d.pipeline.updated).toLocaleString("de-AT"):"–")+'</div></div>')}
// machine
g.push('<div class="card"><h2>Prozessor</h2><div class="big">'+d.cpu+' %</div>'+meter(d.cpu,lvl(d.cpu,95,101))+'</div>');
g.push('<div class="card"><h2>Grafikkarte</h2><div class="big">'+d.gpu+' %</div>'+meter(d.gpu)+'<div class="mut" style="margin-top:6px">'+(d.gpu>20?"rechnet":"wenig Last")+'</div></div>');
g.push('<div class="card"><h2>Arbeitsspeicher frei</h2><div class="big">'+(d.memFree||"?")+' %</div>'+meter(d.memFree,lvl(100-d.memFree,80,90))+'</div>');
g.push('<div class="card"><h2>Festplatte frei</h2><div class="big">'+d.diskGB+' GB</div>'+meter(Math.min(100,d.diskGB),lvl(100-Math.min(100,d.diskGB),85,92))+(d.therm!=null?'<div class="mut" style="margin-top:6px">Leistung: '+d.therm+' %'+(d.therm<100?' (Hitzebremse)':'')+'</div>':'')+'</div>');
// blender
let b='<div class="card"><h2>Blender</h2>';if(!nb)b+='<div class="big">'+dot("idle")+'aus</div>';else d.blender.forEach(x=>{b+='<div class="row"><span>'+dot(nb>1?"bad":"ok")+'Prozess '+x.pid+'</span><span>'+Math.round(x.cpu)+' % CPU · '+x.ram_gb+' GB · '+x.time+'</span></div>'});g.push(b+'</div>');
// connection
const hbok=/ (200|201)$/.test(d.hb);g.push('<div class="card"><h2>Verbindung zu Claude</h2><div class="big">'+dot(hbok?"ok":d.hb?"bad":"warn")+(hbok?"verbunden":d.hb?"gestört":"noch keine Meldung")+'</div><div class="mut">'+(d.hb?"letzte Meldung "+hm(d.hb.split(" ")[0]):"")+'</div></div>');
// queue
let q='<div class="card"><h2>Warteschlange ('+d.queue.length+')</h2>';q+=d.queue.length?d.queue.slice(0,8).map(x=>'<div class="row"><span><span class="tag">'+(x.ch||"SYS")+'</span>'+x.title+'</span></div>').join(""):'<div class="mut">leer</div>';g.push(q+'</div>');
// history
let r='<div class="card"><h2>Zuletzt erledigt</h2>';r+=d.done.map(x=>'<div class="row"><span>'+dot("ok")+x.id+'</span><span class="mut">'+hm(x.t)+'</span></div>').join("")+d.failed.slice(0,3).map(x=>'<div class="row"><span>'+dot("bad")+x.id+'</span><span class="mut">'+hm(x.t)+'</span></div>').join("");g.push(r+'</div>');
document.getElementById("g").innerHTML=g.join("")}
tick();setInterval(tick,3000);
</script></body></html>`;

http.createServer((req, res) => {
  if (req.url.startsWith("/api")) { res.writeHead(200, { "Content-Type": "application/json", "Cache-Control": "no-store" }); res.end(JSON.stringify(collect())); return; }
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }); res.end(HTML);
}).listen(PORT, "127.0.0.1");

// heartbeat every 2 min while the dashboard runs (the agent itself is blocked during long jobs).
// Same file and branch as agent.mjs; token stays on the Mac. Best effort.
const beat = async () => {
  try {
    const tf = path.join(A, "token"); if (!fs.existsSync(tf)) return;
    const d = collect(); const recent = (x) => x.map((r) => r.id);
    const status = { ts: new Date().toISOString(), source: "dashboard", current: readTxt(path.join(STATE, "current")), busy: d.st.state === "busy" && d.agentRunning, free_gb: d.diskGB, blender_procs: d.blender.length, cpu: d.cpu, gpu: d.gpu, mem_free_pct: d.memFree, progress: d.progress, done: recent(d.done), failed: recent(d.failed), status: d.st, queue: d.queue.map((q) => q.id) };
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

// Shorts render agent: runs on Oliver's Mac (launched every ~60 s by loop.sh).
// Reads jobs/*.json from the freshly downloaded queue repo, runs each job once, uploads results
// to the presigned URLs inside the job. Local state lives in ~/ShortsRenderAgent/state.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync, spawn } from "node:child_process";

const A = path.join(os.homedir(), "ShortsRenderAgent");
const REPO = path.join(A, "repo");
const STATE = path.join(A, "state");
const LOCK = path.join(STATE, "lock");
for (const d of ["done", "failed", "logs"]) fs.mkdirSync(path.join(STATE, d), { recursive: true });

const now = () => new Date().toISOString().replace("T", " ").slice(0, 19);
let LOG = null;
const log = (...a) => { const s = `[${now()}] ${a.join(" ")}`; console.log(s); if (LOG) fs.appendFileSync(LOG, s + "\n"); };

// heartbeat: writes heartbeat.json to the "heartbeat" branch (every 5 min, and right after every job) so the
// cloud side can wait for events instead of polling the CDN. Needs a token with Contents: write. Best effort.
const CUR = path.join(STATE, "current");
const heartbeat = async (force = false) => {
  try {
    const last = path.join(STATE, "hb_last"), tf = path.join(A, "token");
    if (!fs.existsSync(tf)) return;
    if (!force && fs.existsSync(last) && Date.now() - Number(fs.readFileSync(last, "utf8")) < 5 * 60000) return;
    fs.writeFileSync(last, String(Date.now()));
    const r = spawnSync("/bin/bash", ["-c", "df -k \"$HOME\" | tail -1 | awk '{print $4}'; pgrep -f '[B]lender.app/Contents/MacOS/Blender' | wc -l"], { encoding: "utf8" });
    const [kb, nb] = (r.stdout || "").trim().split("\n");
    const recent = (d) => fs.readdirSync(path.join(STATE, d)).map((f) => [f, fs.statSync(path.join(STATE, d, f)).mtimeMs]).sort((a, b) => b[1] - a[1]).slice(0, 40).map((x) => x[0]);
    const status = { ts: new Date().toISOString(), current: fs.existsSync(CUR) ? fs.readFileSync(CUR, "utf8") : "", busy: fs.existsSync(LOCK), free_gb: Math.round(Number(kb) / 1048576), blender_procs: Number(nb) || 0, done: recent("done"), failed: recent("failed"), status: (() => { try { return JSON.parse(fs.readFileSync(path.join(STATE, "status.json"), "utf8")); } catch { return null; } })() };
    const h = { Authorization: `Bearer ${fs.readFileSync(tf, "utf8").trim()}`, "User-Agent": "shorts-render-agent", Accept: "application/vnd.github+json" };
    const api = "https://api.github.com/repos/gruenwaldoliver44-cmd/shorts-render-queue/contents/heartbeat.json";
    const g = await fetch(api + "?ref=heartbeat", { headers: h, signal: AbortSignal.timeout(15000) });
    const sha = g.ok ? (await g.json()).sha : undefined;
    const p = await fetch(api, { method: "PUT", headers: h, signal: AbortSignal.timeout(15000), body: JSON.stringify({ message: "heartbeat", branch: "heartbeat", content: Buffer.from(JSON.stringify(status, null, 1)).toString("base64"), ...(sha ? { sha } : {}) }) });
    fs.writeFileSync(path.join(STATE, "hb_result"), `${new Date().toISOString()} ${p.status}`);
  } catch (e) { try { fs.writeFileSync(path.join(STATE, "hb_result"), `${new Date().toISOString()} error ${e}`); } catch {} }
};
await heartbeat();

// Telegram notifications: every notify/*.txt in the repo is sent once to Oliver's Telegram bot chat
// (token and chat id live only on the Mac: ~/ShortsRenderAgent/telegram_token, telegram_chat). Best effort.
await (async () => {
  try {
    const tf = path.join(A, "telegram_token"), cf = path.join(A, "telegram_chat"), dir = path.join(REPO, "notify");
    if (!fs.existsSync(tf) || !fs.existsSync(cf) || !fs.existsSync(dir)) return;
    const sentDir = path.join(STATE, "notified"); fs.mkdirSync(sentDir, { recursive: true });
    const tok = fs.readFileSync(tf, "utf8").trim(), chat = fs.readFileSync(cf, "utf8").trim();
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".txt")).sort()) {
      if (fs.existsSync(path.join(sentDir, f))) continue;
      fs.writeFileSync(path.join(sentDir, f), now());
      const text = fs.readFileSync(path.join(dir, f), "utf8").slice(0, 4000);
      await fetch(`https://api.telegram.org/bot${tok}/sendMessage`, { method: "POST", headers: { "Content-Type": "application/json" }, signal: AbortSignal.timeout(15000), body: JSON.stringify({ chat_id: chat, text, disable_web_page_preview: false }) });
    }
  } catch { /* ignore */ }
})();

// live dashboard on http://localhost:8765 (tools/dashboard.mjs): keep a copy outside repo/ (repo is replaced every loop)
// and (re)start it when it is not running or its code changed. Best effort.
try {
  const src = path.join(REPO, "tools", "dashboard.mjs"), dst = path.join(A, "dashboard.mjs"), pidf = path.join(STATE, "dashboard.pid");
  if (fs.existsSync(src)) {
    const changed = !fs.existsSync(dst) || fs.readFileSync(src, "utf8") !== fs.readFileSync(dst, "utf8");
    let alive = false;
    if (fs.existsSync(pidf)) { try { process.kill(Number(fs.readFileSync(pidf, "utf8")), 0); alive = true; } catch {} }
    if (changed || !alive) {
      if (alive) { try { process.kill(Number(fs.readFileSync(pidf, "utf8"))); } catch {} await new Promise((r) => setTimeout(r, 500)); }
      fs.copyFileSync(src, dst);
      const c = spawn(process.execPath, [dst], { detached: true, stdio: "ignore" });
      c.unref(); fs.writeFileSync(pidf, String(c.pid));
    }
  }
} catch { /* ignore */ }

// single instance
if (fs.existsSync(LOCK)) {
  const pid = Number(fs.readFileSync(LOCK, "utf8"));
  try { process.kill(pid, 0); process.exit(0); } catch { /* stale */ }
}
fs.writeFileSync(LOCK, String(process.pid));
process.on("exit", () => { try { fs.unlinkSync(LOCK); } catch {} });

// per-job time limit (job.timeout_min, default 100 min): a hung or runaway job is killed so the queue keeps moving
let JOB_DEADLINE = 0, TIMED_OUT = false;
const killRenders = () => spawnSync("/bin/bash", ["-c", "pkill -9 -f 'Blender.app/Contents/MacOS/Blender -b' ; pkill -9 -f 'Blender.app/Contents/MacOS/Blender --background' ; true"]);
const sh = (cmd, cwd, extraEnv = {}) => {
  log("$", cmd.length > 300 ? cmd.slice(0, 300) + " ..." : cmd);
  const left = JOB_DEADLINE ? JOB_DEADLINE - Date.now() : 0;
  if (JOB_DEADLINE && left <= 0) { TIMED_OUT = true; log("TIMEOUT: job time limit reached, skipping step"); return false; }
  const r = spawnSync("/bin/bash", ["-c", cmd], { cwd, env: { ...process.env, ...extraEnv }, encoding: "utf8", maxBuffer: 1 << 28, ...(JOB_DEADLINE ? { timeout: left, killSignal: "SIGKILL" } : {}) });
  if (r.error && r.error.code === "ETIMEDOUT") { TIMED_OUT = true; killRenders(); log("TIMEOUT: step killed after job time limit"); return false; }
  const out = ((r.stdout || "") + (r.stderr || "")).trim();
  if (out) log(out.split("\n").slice(-25).join("\n"));
  return r.status === 0;
};
const q = (s) => "'" + String(s).replace(/'/g, "'\\''") + "'";

const upload = (file, url, type) => {
  if (!url) return true;
  const ok = sh(`curl -sS -o /dev/null -w '%{http_code}' -X PUT -H ${q("Content-Type: " + type)} -H 'If-None-Match: *' --upload-file ${q(file)} ${q(url)} | grep -Eq '^(200|412)$'`, A);
  log(ok ? "uploaded " + path.basename(file) : "UPLOAD FAILED " + path.basename(file));
  return ok;
};

const runRemotion = (job, wd) => {
  const proj = path.join(A, "proj");
  fs.mkdirSync(proj, { recursive: true });
  if (!sh(`curl -fsSL -o job.zip ${q(job.zip)} && rm -rf src && unzip -oq job.zip`, proj)) return false;
  if (!sh(`npm install --no-audit --no-fund --loglevel=error`, proj, { npm_config_cache: path.join(A, "npm-cache") })) return false;
  fs.mkdirSync(path.join(proj, "out"), { recursive: true });
  let all = true;
  for (const it of job.items) {
    const out = path.join("out", `${it.comp}.mp4`);
    const props = it.props ? `--props=${q(JSON.stringify(it.props))}` : "";
    const flags = [
      `--gl=${it.gl || "angle"}`, "--muted", `--crf=${it.crf ?? 14}`, "--image-format=jpeg", `--jpeg-quality=${it.jpeg ?? 95}`,
      `--concurrency=${it.concurrency ?? 4}`, `--scale=${it.scale ?? 1}`, "--timeout=180000", "--log=error", props, ...(it.flags || []),
    ].join(" ");
    const t0 = Date.now();
    const ok = sh(`rm -f ${q(out)} && npx remotion render ${q(it.entry)} ${q(it.comp)} ${q(out)} ${flags}`, proj);
    log(`${it.comp} render ${ok ? "ok" : "FAILED"} in ${Math.round((Date.now() - t0) / 1000)} s`);
    if (!ok || !upload(path.join(proj, out), it.upload, "video/mp4")) all = false;
    else if (!job.keep) { try { fs.unlinkSync(path.join(proj, out)); } catch {} }
  }
  return all;
};

// plain-language status for Oliver's live view (tools/status.mjs) and the heartbeat
const STATUS = path.join(STATE, "status.json");
const setStatus = (o) => { try { fs.writeFileSync(STATUS, JSON.stringify({ ...o, updated: new Date().toISOString() })); } catch {} };
let JOB_INFO = {};

// a step is a shell string or { run, label, progress: { dir, total } } (dir relative to the job folder, counts files)
const runShell = (job, wd) => {
  const steps = job.steps || [];
  for (let i = 0; i < steps.length; i++) {
    const st = typeof steps[i] === "string" ? { run: steps[i] } : steps[i];
    setStatus({ ...JOB_INFO, step: i + 1, steps: steps.length, label: st.label || `Schritt ${i + 1}`, step_since: new Date().toISOString(), progress: st.progress ? { dir: path.join(wd, st.progress.dir), total: st.progress.total } : null });
    if (!sh(st.run, wd, { AGENT_HOME: A, JOB_DIR: wd })) return false;
  }
  setStatus({ ...JOB_INFO, step: steps.length, steps: steps.length, label: "Lade Ergebnisse hoch", step_since: new Date().toISOString(), progress: null });
  for (const u of job.uploads || []) if (!upload(path.join(wd, u.file), u.url, u.type || "application/octet-stream")) return false;
  return true;
};

// free disk guard (GB)
const freeGB = (() => { const r = spawnSync("/bin/bash", ["-c", "df -k \"$HOME\" | tail -1 | awk '{print $4}'"], { encoding: "utf8" }); return Number(r.stdout) / 1048576; })();
const files = fs.existsSync(path.join(REPO, "jobs")) ? fs.readdirSync(path.join(REPO, "jobs")).filter((f) => f.endsWith(".json")).sort() : [];
for (const f of files) {
  let job;
  try { job = JSON.parse(fs.readFileSync(path.join(REPO, "jobs", f), "utf8")); } catch (e) { console.log("bad job json", f); continue; }
  const id = job.id || f.replace(/\.json$/, "");
  if (fs.existsSync(path.join(STATE, "done", id))) continue;
  if (job.expires && Date.now() > Date.parse(job.expires)) continue;
  const failN = fs.existsSync(path.join(STATE, "failed", id)) ? Number(fs.readFileSync(path.join(STATE, "failed", id), "utf8")) : 0;
  if (failN >= (job.retries ?? 2)) continue;
  if (freeGB < (job.min_free_gb ?? 4)) { console.log(`[${now()}] skip ${id}: only ${freeGB.toFixed(1)} GB free`); continue; }
  LOG = path.join(STATE, "logs", `${id}.log`);
  const wd = path.join(A, "work", id);
  fs.mkdirSync(wd, { recursive: true });
  log(`=== job ${id} (${job.type}) start, attempt ${failN + 1}`);
  let ok = false;
  JOB_DEADLINE = Date.now() + (job.timeout_min ?? 100) * 60000; TIMED_OUT = false;
  fs.writeFileSync(CUR, `${id} since ${now()}`);
  JOB_INFO = { state: "busy", job: id, title: job.title || id, job_since: new Date().toISOString(), timeout_min: job.timeout_min ?? 100 };
  setStatus({ ...JOB_INFO, step: 0, steps: (job.steps || job.items || []).length, label: "Startet", progress: null });
  await heartbeat(true);
  try { ok = job.type === "remotion" ? runRemotion(job, wd) : job.type === "shell" ? runShell(job, wd) : false; }
  catch (e) { log("EXCEPTION " + (e && e.stack || e)); }
  JOB_DEADLINE = 0;
  try { fs.unlinkSync(CUR); } catch {}
  log(`=== job ${id} ${ok ? "DONE" : TIMED_OUT ? "TIMED OUT (no retry)" : "FAILED"}`);
  setStatus({ state: "idle", last: { job: id, title: job.title || id, result: ok ? "fertig" : TIMED_OUT ? "Zeitlimit erreicht" : "Fehler", at: new Date().toISOString() } });
  if (ok) fs.writeFileSync(path.join(STATE, "done", id), now());
  else fs.writeFileSync(path.join(STATE, "failed", id), String(TIMED_OUT ? 99 : failN + 1));
  if (job.log_upload) upload(LOG, job.log_upload, job.log_type || "application/octet-stream"); // presigned .txt URLs are signed as octet-stream
  LOG = null;
  await heartbeat(true);
}

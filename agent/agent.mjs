// Shorts render agent: runs on Oliver's Mac (launched every ~60 s by loop.sh).
// Reads jobs/*.json from the freshly downloaded queue repo, runs each job once, uploads results
// to the presigned URLs inside the job. Local state lives in ~/ShortsRenderAgent/state.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";

const A = path.join(os.homedir(), "ShortsRenderAgent");
const REPO = path.join(A, "repo");
const STATE = path.join(A, "state");
const LOCK = path.join(STATE, "lock");
for (const d of ["done", "failed", "logs"]) fs.mkdirSync(path.join(STATE, d), { recursive: true });

const now = () => new Date().toISOString().replace("T", " ").slice(0, 19);
let LOG = null;
const log = (...a) => { const s = `[${now()}] ${a.join(" ")}`; console.log(s); if (LOG) fs.appendFileSync(LOG, s + "\n"); };

// single instance
if (fs.existsSync(LOCK)) {
  const pid = Number(fs.readFileSync(LOCK, "utf8"));
  try { process.kill(pid, 0); process.exit(0); } catch { /* stale */ }
}
fs.writeFileSync(LOCK, String(process.pid));
process.on("exit", () => { try { fs.unlinkSync(LOCK); } catch {} });

const sh = (cmd, cwd, extraEnv = {}) => {
  log("$", cmd.length > 300 ? cmd.slice(0, 300) + " ..." : cmd);
  const r = spawnSync("/bin/bash", ["-c", cmd], { cwd, env: { ...process.env, ...extraEnv }, encoding: "utf8", maxBuffer: 1 << 28 });
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
  }
  return all;
};

const runShell = (job, wd) => {
  for (const step of job.steps || []) if (!sh(step, wd, { AGENT_HOME: A, JOB_DIR: wd })) return false;
  for (const u of job.uploads || []) if (!upload(path.join(wd, u.file), u.url, u.type || "application/octet-stream")) return false;
  return true;
};

const files = fs.existsSync(path.join(REPO, "jobs")) ? fs.readdirSync(path.join(REPO, "jobs")).filter((f) => f.endsWith(".json")).sort() : [];
for (const f of files) {
  let job;
  try { job = JSON.parse(fs.readFileSync(path.join(REPO, "jobs", f), "utf8")); } catch (e) { console.log("bad job json", f); continue; }
  const id = job.id || f.replace(/\.json$/, "");
  if (fs.existsSync(path.join(STATE, "done", id))) continue;
  if (job.expires && Date.now() > Date.parse(job.expires)) continue;
  const failN = fs.existsSync(path.join(STATE, "failed", id)) ? Number(fs.readFileSync(path.join(STATE, "failed", id), "utf8")) : 0;
  if (failN >= (job.retries ?? 2)) continue;
  LOG = path.join(STATE, "logs", `${id}.log`);
  const wd = path.join(A, "work", id);
  fs.mkdirSync(wd, { recursive: true });
  log(`=== job ${id} (${job.type}) start, attempt ${failN + 1}`);
  let ok = false;
  try { ok = job.type === "remotion" ? runRemotion(job, wd) : job.type === "shell" ? runShell(job, wd) : false; }
  catch (e) { log("EXCEPTION " + (e && e.stack || e)); }
  log(`=== job ${id} ${ok ? "DONE" : "FAILED"}`);
  if (ok) fs.writeFileSync(path.join(STATE, "done", id), now());
  else fs.writeFileSync(path.join(STATE, "failed", id), String(failN + 1));
  if (job.log_upload) upload(LOG, job.log_upload, "text/plain");
  LOG = null;
}

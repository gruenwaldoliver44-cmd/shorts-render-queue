// Live view for Oliver: shows in plain German what the Mac is doing right now.
// Start: ~/ShortsRenderAgent/node/bin/node ~/ShortsRenderAgent/repo/tools/status.mjs   (stop with Ctrl+C)
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";

const A = path.join(os.homedir(), "ShortsRenderAgent");
const STATE = path.join(A, "state");
const CH = { "21": "Compound Times (CT)", "22": "Machine Times (MT)", "23": "Money Classics (MC)", "24": "Future Tender (FT)" };
const channel = (id) => CH[String(id).slice(0, 2)] || "System";
const hm = (d) => new Date(d).toLocaleTimeString("de-AT", { hour: "2-digit", minute: "2-digit" });
const mins = (ms) => { const m = Math.max(0, Math.round(ms / 60000)); return m < 60 ? `${m} Min` : `${Math.floor(m / 60)} h ${m % 60} Min`; };
const readJSON = (f) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return null; } };
const countFiles = (d) => { try { return fs.readdirSync(d).filter((f) => !f.startsWith(".")).length; } catch { return 0; } };
const bar = (p) => { const n = Math.round(p * 30); return "[" + "#".repeat(n) + "-".repeat(30 - n) + "]"; };
const rate = {}; // progress dir -> [{t, n}]

const queue = () => {
  const dir = path.join(A, "repo", "jobs");
  let files = [];
  try { files = fs.readdirSync(dir).filter((f) => f.endsWith(".json")).sort(); } catch {}
  const out = [];
  for (const f of files) {
    const j = readJSON(path.join(dir, f)) || {};
    const id = j.id || f.replace(/\.json$/, "");
    if (fs.existsSync(path.join(STATE, "done", id))) continue;
    const fail = Number((() => { try { return fs.readFileSync(path.join(STATE, "failed", id), "utf8"); } catch { return 0; } })());
    if (fail >= Math.max(1, j.retries ?? 2)) continue;
    if (j.expires && Date.now() > Date.parse(j.expires)) continue;
    out.push(`${channel(id)}: ${j.title || id}`);
  }
  return out;
};

const draw = () => {
  const st = readJSON(path.join(STATE, "status.json")) || {};
  const blender = Number((spawnSync("/bin/bash", ["-c", "pgrep -f '[B]lender.app/Contents/MacOS/Blender' | wc -l"], { encoding: "utf8" }).stdout || "0").trim());
  const agent = Number((spawnSync("/bin/bash", ["-c", "pgrep -f '[a]gent/agent.mjs' | wc -l"], { encoding: "utf8" }).stdout || "0").trim());
  const hb = (() => { try { return fs.readFileSync(path.join(STATE, "hb_result"), "utf8").trim(); } catch { return ""; } })();
  const L = [];
  L.push(`SHORTS-MAC  ·  ${new Date().toLocaleString("de-AT")}`);
  L.push("");
  if (st.state === "busy" && agent > 0) {
    L.push(`ARBEITET AN:   ${channel(st.job)}  –  ${st.title}`);
    L.push(`Auftrag seit:  ${hm(st.job_since)} (${mins(Date.now() - Date.parse(st.job_since))}), Zeitlimit ${st.timeout_min} Min`);
    L.push(`Schritt:       ${st.step || 0} von ${st.steps || "?"}  –  ${st.label || ""}${st.step_since ? `  (seit ${mins(Date.now() - Date.parse(st.step_since))})` : ""}`);
    if (st.progress && st.progress.total) {
      const n = countFiles(st.progress.dir), p = Math.min(1, n / st.progress.total);
      const r = (rate[st.progress.dir] ||= []); r.push({ t: Date.now(), n }); while (r.length > 40) r.shift();
      let eta = "";
      if (r.length > 3 && r[r.length - 1].n > r[0].n) { const per = (r[r.length - 1].t - r[0].t) / (r[r.length - 1].n - r[0].n); eta = `, noch ca. ${mins(per * (st.progress.total - n))}`; }
      L.push(`Fortschritt:   ${bar(p)} ${n} von ${st.progress.total} Bildern (${Math.round(p * 100)} %)${eta}`);
    }
    L.push(`Blender:       ${blender > 0 ? `rechnet (${blender} Prozess${blender > 1 ? "e – ACHTUNG, sollte nur 1 sein" : ""})` : "gerade nicht aktiv (Vorbereitung, Download oder Upload)"}`);
  } else if (agent > 0) {
    L.push("ARBEITET AN:   startet gerade / prüft die Auftragsliste");
  } else {
    L.push("BEREIT:        wartet auf neue Aufträge (prüft jede Minute)");
    if (blender > 0) L.push(`WARNUNG:       ${blender} Blender läuft ohne Auftrag – bitte Claude Bescheid geben`);
  }
  if (st.last) L.push(`Zuletzt:       ${channel(st.last.job)} – ${st.last.title}: ${st.last.result} um ${hm(st.last.at)}`);
  L.push("");
  const q = queue().filter((x) => !(st.state === "busy" && x.endsWith(st.title)));
  L.push(`WARTESCHLANGE (${q.length}):`);
  for (const x of q.slice(0, 8)) L.push(`  · ${x}`);
  if (!q.length) L.push("  (leer)");
  L.push("");
  L.push(`Verbindung zu Claude: ${hb.includes(" 200") || hb.includes(" 201") ? "OK" : hb ? "GESTÖRT (" + hb + ")" : "noch keine Meldung"}`);
  L.push("");
  L.push("Beenden der Anzeige: Ctrl+C  (das Rendern läuft weiter)");
  process.stdout.write("\x1b[2J\x1b[H" + L.join("\n") + "\n");
};

draw();
setInterval(draw, 3000);

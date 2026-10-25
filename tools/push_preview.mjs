// Push small result files (contact sheets, logs, thumbnails) from a Mac job to the "previews" branch,
// so cloud agents can inspect them without CDN access.  Use ONLY from inside a Mac job step:
//   ~/ShortsRenderAgent/node/bin/node "$AGENT_HOME/repo/tools/push_preview.mjs" LOCAL_FILE REPO_PATH [...more pairs]
// Needs ~/ShortsRenderAgent/token (Contents: write). Files up to ~40 MB. Exit code 0 even on failure (best effort, logged).
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
const A = path.join(os.homedir(), "ShortsRenderAgent");
const tok = fs.readFileSync(path.join(A, "token"), "utf8").trim();
const H = { Authorization: `Bearer ${tok}`, "User-Agent": "shorts-render-agent", Accept: "application/vnd.github+json" };
const API = "https://api.github.com/repos/gruenwaldoliver44-cmd/shorts-render-queue/contents/";
const args = process.argv.slice(2);
for (let i = 0; i + 1 < args.length; i += 2) {
  const [file, rp] = [args[i], args[i + 1]];
  try {
    const st = fs.statSync(file);
    if (st.size > 40 * 1024 * 1024) { console.log(`preview SKIP ${rp}: ${st.size} bytes`); continue; }
    const g = await fetch(API + rp + "?ref=previews", { headers: H, signal: AbortSignal.timeout(30000) });
    const sha = g.ok ? (await g.json()).sha : undefined;
    const p = await fetch(API + rp, { method: "PUT", headers: H, signal: AbortSignal.timeout(180000), body: JSON.stringify({ message: "preview " + rp, branch: "previews", content: fs.readFileSync(file).toString("base64"), ...(sha ? { sha } : {}) }) });
    console.log(`preview ${p.status} ${rp} (${st.size} bytes)`);
  } catch (e) { console.log(`preview FAIL ${rp} ${e}`); }
}

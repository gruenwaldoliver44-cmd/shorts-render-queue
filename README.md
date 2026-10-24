# shorts-render-queue

Private render queue for the Shorts autopilot.

- `agent/agent.mjs` runs on Oliver's Mac every ~60 s (installed as LaunchAgent `com.shortsautopilot.render`, files in `~/ShortsRenderAgent`). It downloads this repo, runs every job in `jobs/` once and uploads the results to the presigned URLs inside the job.
- Job types: `remotion` (zip of the Remotion project + list of compositions, rendered with GPU `--gl=angle`) and `shell` (steps run in `~/ShortsRenderAgent/work/<id>`, e.g. Blender).
- Only Oliver and Claude can write here. Never put API keys in this repo; upload URLs expire after 24 h.

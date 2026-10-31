import json, sys
jid, pack, times, title, zipname, uzip, ulog = sys.argv[1:8]
B = '/Applications/Blender.app/Contents/MacOS/Blender'
j = {"id": jid, "type": "shell", "title": title, "retries": 0, "min_free_gb": 4, "timeout_min": 90, "expires": "2026-11-02T22:00:00Z",
 "steps": [{"label": "Pack", "run": "rm -rf ct tex && cp -R \"$HOME/ShortsRenderAgent/repo/packs/%s/ct\" \"$HOME/ShortsRenderAgent/repo/packs/%s/tex\" . && ls ct" % (pack, pack)},
  {"label": "Szene bauen", "run": "CT_ROOT=$PWD " + B + " -b -P ct/scene.py > build.log 2>&1; grep -v -i -E 'bearer|api_key|deprecat|use_nodes' build.log | tail -30; grep -q 'SCENE OK' build.log"},
  {"label": "Standbilder", "run": "CT_ROOT=$PWD " + B + " -b ct/scene.blend -P ct/stills.py -- $PWD/o " + times + " > stills.log 2>&1; tail -40 stills.log | grep -v -i blendkit; ls o/*.jpg >/dev/null 2>&1 || { echo RETRY_CPU; CPU_ONLY=1 CT_ROOT=$PWD " + B + " -b ct/scene.blend -P ct/stills.py -- $PWD/o " + times + " > stills_cpu.log 2>&1; tail -30 stills_cpu.log | grep -v -i blendkit; }; cd o && zip -q -j ../" + zipname + " *.jpg; cd ..; ls -la " + zipname + "; true"}],
 "uploads": [{"file": zipname, "type": "application/octet-stream", "url": uzip}], "log_upload": ulog}
json.dump(j, open('jobs/%s.json' % jid, 'w'), indent=1)

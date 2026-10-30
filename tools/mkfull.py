import json, sys
# usage: mkfull.py JOBID PACK TITLE NFRAMES SPP ZIPNAME UZIP UPROJ ULOG
jid, pack, title, nfr, spp, zipname, uzip, uproj, ulog = sys.argv[1:10]
B = '/Applications/Blender.app/Contents/MacOS/Blender'
j = {"id": jid, "type": "shell", "title": title, "retries": 0, "min_free_gb": 6, "timeout_min": 600, "expires": "2026-11-03T22:00:00Z",
 "steps": [{"label": "Pack", "run": "mkdir -p frames && rm -rf ct tex && cp -R \"$HOME/ShortsRenderAgent/repo/packs/%s/ct\" \"$HOME/ShortsRenderAgent/repo/packs/%s/tex\" . && ls ct" % (pack, pack)},
  {"label": "Szene bauen", "run": "CT_ROOT=$PWD " + B + " -b -P ct/scene.py > build.log 2>&1; grep -v -i -E 'bearer|api_key|deprecat|use_nodes' build.log | tail -20; grep -q 'SCENE OK' build.log && cp ct/proj.json proj.txt"},
  {"label": "Vollrender 1080x1920", "progress": {"dir": "frames", "total": int(nfr)}, "run": "CT_ROOT=$PWD " + B + " -b ct/scene.blend -P ct/render.py -- seq $PWD/frames " + spp + " > render.log 2>&1; tail -3 render.log; ls frames | wc -l"},
  {"label": "Packen", "run": "cd frames && zip -q -0 ../" + zipname + " f*.jpg; cd ..; ls -la " + zipname}],
 "uploads": [{"file": zipname, "type": "application/octet-stream", "url": uzip}, {"file": "proj.txt", "type": "application/octet-stream", "url": uproj}],
 "log_upload": ulog}
json.dump(j, open('jobs/%s.json' % jid, 'w'), indent=1)

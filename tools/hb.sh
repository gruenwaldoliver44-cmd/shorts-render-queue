#!/bin/bash
# reliable heartbeat read (plain 'git fetch origin heartbeat' does NOT update origin/heartbeat here)
cd "$(dirname "$0")/.." && git fetch -q origin +heartbeat:refs/remotes/origin/heartbeat && git show origin/heartbeat:heartbeat.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['ts'],d.get('current'),(d.get('status') or {}).get('label'),d.get('progress'),'done',d['done'][:5],'failed',d['failed'][:4],'queue',d.get('queue'))"

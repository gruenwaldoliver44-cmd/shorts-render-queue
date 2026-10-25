#!/bin/bash
# Usage: bash tools/wait_job.sh JOB_ID [MAX_MIN]   (run from a clone of this repo, in the background)
# Waits without model calls until the Mac reports JOB_ID as done or failed on the heartbeat branch,
# then prints one line and exits. Also exits if the heartbeat is older than 12 min (Mac asleep or stuck).
id="$1"; max="${2:-240}"; t0=$(date +%s)
while :; do
  git fetch -q origin +heartbeat:refs/remotes/origin/heartbeat 2>/dev/null
  hb=$(git show origin/heartbeat:heartbeat.json 2>/dev/null)
  if [ -n "$hb" ]; then
    r=$(printf '%s' "$hb" | python3 -c '
import json,sys,datetime
h=json.load(sys.stdin); j=sys.argv[1]
age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(h["ts"].replace("Z","+00:00"))).total_seconds()/60
if j in h.get("done",[]): print("DONE")
elif j in h.get("failed",[]): print("FAILED")
elif age>12: print("STALE %d min, current: %s" % (age, h.get("current","")))
' "$id")
    if [ -n "$r" ]; then echo "$id $r $(date -u +%H:%M)"; exit 0; fi
  fi
  [ $(( $(date +%s) - t0 )) -gt $((max*60)) ] && { echo "$id WAIT TIMEOUT after $max min"; exit 0; }
  sleep 60
done

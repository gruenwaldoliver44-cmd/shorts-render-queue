#!/bin/bash
# Parallel render with a memory guard (Oliver's Mac). Use ONLY from inside a Mac job step.
#
#   bash "$AGENT_HOME/repo/tools/par_render.sh" N FIRST LAST -- command with {S} and {E}
#
# Splits frames FIRST..LAST into N contiguous chunks and runs the command once per chunk, with {S}/{E}
# replaced by the chunk's first/last frame (e.g. Blender -b scene.blend -P final.py -- {S} {E} out/f_).
# Memory guard (macOS memory_pressure "free percentage"): below 20 % free, the newest running worker is
# paused (SIGSTOP); above 35 % free, paused workers resume. Workers are started one by one, 60 s apart,
# (PAR_STAGGER seconds) and only while at least 40 % is free, so the scene load peaks never overlap.
# The script exits non-zero if any worker failed. Render scripts should skip frames that already exist,
# so a re-run only fills the gaps. Each worker logs to par_<n>.log in the current folder.
set -u
N="$1"; FIRST="$2"; LAST="$3"; shift 3; [ "${1:-}" = "--" ] && shift
# 25 Oct 19:30: two parallel Blenders exhausted the Mac (macOS "no application memory", swap filled the disk). Parallel is OFF until a safer guard exists.
PAR_MAX="${PAR_MAX:-1}"; [ "$N" -gt "$PAR_MAX" ] && N=$PAR_MAX
CMD="$*"
free_pct() { local v; v=$(memory_pressure -Q 2>/dev/null | grep -o '[0-9]*%' | tail -1 | tr -d '%'); echo "${v:-100}"; }
TOTAL=$(( LAST - FIRST + 1 )); [ "$N" -lt 1 ] && N=1; [ "$N" -gt "$TOTAL" ] && N=$TOTAL
PIDS=(); PAUSED=()
cleanup() { for p in "${PIDS[@]}"; do kill -CONT "$p" 2>/dev/null; kill "$p" 2>/dev/null; done; }
trap cleanup INT TERM
echo "par_render: $N workers, frames $FIRST-$LAST, free memory $(free_pct)%"
for ((i=0; i<N; i++)); do
  S=$(( FIRST + i * TOTAL / N )); E=$(( FIRST + (i + 1) * TOTAL / N - 1 ))
  if [ "$i" -gt 0 ]; then
    sleep "${PAR_STAGGER:-60}"
    while [ "$(free_pct)" -lt 40 ]; do echo "par_render: waiting for memory before worker $i ($(free_pct)% free)"; sleep 15; done
  fi
  C="${CMD//\{S\}/$S}"; C="${C//\{E\}/$E}"
  ( eval "$C" ) > "par_$i.log" 2>&1 &
  PIDS+=($!); echo "par_render: worker $i frames $S-$E pid $!"
done
# guard loop
while :; do
  alive=0; for p in "${PIDS[@]}"; do kill -0 "$p" 2>/dev/null && alive=$((alive+1)); done
  [ "$alive" -eq 0 ] && break
  f=$(free_pct)
  if [ "$f" -lt 20 ]; then
    for ((j=${#PIDS[@]}-1; j>0; j--)); do p=${PIDS[$j]}
      if kill -0 "$p" 2>/dev/null && [[ ! " ${PAUSED[*]:-} " =~ " $p " ]]; then pkill -STOP -P "$p" 2>/dev/null; kill -STOP "$p" 2>/dev/null; PAUSED+=("$p"); echo "par_render: memory $f% free, paused worker pid $p"; break; fi
    done
  elif [ "$f" -gt 35 ] && [ "${#PAUSED[@]}" -gt 0 ]; then
    p=${PAUSED[0]}; pkill -CONT -P "$p" 2>/dev/null; kill -CONT "$p" 2>/dev/null; PAUSED=("${PAUSED[@]:1}"); echo "par_render: memory $f% free, resumed worker pid $p"
  fi
  sleep 10
done
rc=0; for p in "${PIDS[@]}"; do wait "$p" || rc=1; done
echo "par_render: done rc=$rc"
exit $rc

#!/bin/bash
# usage: bash stills.sh FRAMES PCT TAG   (run inside the job dir after copying the pack)
set -e
BL=/Applications/Blender.app/Contents/MacOS/Blender
FR="$1"; PCT="$2"; TAG="$3"
$BL -b -P euv.py -- save > build1.log 2>&1 || { tail -30 build1.log; exit 1; }
grep -a "EUV SAVED" build1.log | cut -c1-600
$BL -b euv.blend -P euv_render.py -- stills 100 184 > scr.log 2>&1 || { tail -20 scr.log; exit 1; }
cp s/f0184.jpg screen.jpg
$BL -b -P euv.py -- save > build2.log 2>&1 || { tail -30 build2.log; exit 1; }
grep -a "EUV SAVED" build2.log | cut -c1-600
$BL -b euv.blend -P euv_render.py -- stills "$PCT" "$FR" > st.log 2>&1 || { tail -20 st.log; exit 1; }
grep -a "^FRAME" st.log | tr '\n' ' '

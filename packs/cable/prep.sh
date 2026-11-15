#!/bin/bash
# build -> render screen images -> rebuild -> test stills
set -e
BL=/Applications/Blender.app/Contents/MacOS/Blender
rm -f screen_a.jpg screen_b.jpg
$BL -b -P cable.py -- save > b1.log 2>&1 || { tail -40 b1.log; exit 1; }
grep -a "CABLE SAVED" b1.log | cut -c1-1500
$BL -b cable.blend -P cable_render.py -- stills 100 155,1281 > s1.log 2>&1 || { tail -30 s1.log; exit 1; }
cp s/f0155.jpg screen_a.jpg; cp s/f1281.jpg screen_b.jpg; rm -f s/*.jpg
$BL -b -P cable.py -- save > b2.log 2>&1 || { tail -40 b2.log; exit 1; }
grep -a "CABLE SAVED" b2.log | cut -c1-400

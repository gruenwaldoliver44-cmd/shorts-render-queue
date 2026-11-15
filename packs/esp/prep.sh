#!/bin/bash
BL=/Applications/Blender.app/Contents/MacOS/Blender
$BL -b -P esp.py -- save > b1.log 2>&1 || { tail -40 b1.log; exit 1; }
grep -a "ESP SAVED" b1.log | cut -c1-2500 || tail -30 b1.log

#!/bin/bash
set -e
BL=/Applications/Blender.app/Contents/MacOS/Blender
$BL -b -P ink.py -- save > b1.log 2>&1 || { tail -40 b1.log; exit 1; }
grep -a "INK SAVED" b1.log | cut -c1-1500

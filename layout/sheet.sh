#!/bin/sh
# sheet.sh <set> <mode> <out.jpg> [shots...] : quick review grid (3 across, 460 px)
SET=$1; MODE=$2; OUT=$3; shift 3
D=$(dirname "$0")/../media/layout/$SET; files=""
for s in "$@"; do files="$files -label $s $D/${s}_$MODE.png"; done
montage $files -tile 3x -geometry 460x259+3+3 -pointsize 18 -background '#444' -fill white "$OUT"

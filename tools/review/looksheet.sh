#!/bin/bash
# looksheet.sh OUT.jpg TILE_W COLS img1 img2 ...   labelled montage (label = file stem + coverage if given via LABEL_<n>)
out=$1; tw=$2; cols=$3; shift 3
montage -label '%t' "$@" -font DejaVu-Sans -pointsize 26 -geometry ${tw}x+8+8 -tile ${cols}x -background '#333' -fill white "$out"
convert "$out" -resize '3000x>' -quality 88 "$out"

#!/bin/sh
# v4 contact sheets (SETS team). After `node layout/render.mjs --set <set> --prefix v4_`:
#   sh layout/sheets_v4.sh [mode]   (mode: label (default) | line | lit | flat)
#   -> media/layout/_sheets/v4_<set>[_<mode>].jpg : every v4 shot camera of the set (not the debug / bible views)
#   -> media/layout/_sheets/v4_<set>_bible.jpg     : plan + elevations (label mode)
cd "$(dirname "$0")/.." || exit 1
MODE=${1:-label}; M=media/layout; O=$M/_sheets; mkdir -p $O
for SET in attic88 bed26 car26; do
  files=""; bible=""
  for f in $(ls $M/$SET/v4_*_${MODE}.png 2>/dev/null | sort); do
    id=$(basename $f _${MODE}.png); case $id in v4_PLAN*|v4_ELEV*|v4_SEC*) bible="$bible -label ${id#v4_} $M/$SET/${id}_label.png";; *) files="$files -label ${id#v4_} $f";; esac
  done
  [ -n "$files" ] || continue
  suf=""; [ "$MODE" = label ] || suf="_$MODE"
  montage $files -tile 5x -geometry 480x270+5+5 -pointsize 20 -background '#2a2a2a' -fill white -title "$SET layout v4 ($MODE)" $O/v4_${SET}${suf}.jpg && echo $O/v4_${SET}${suf}.jpg
  [ "$MODE" = label ] && [ -n "$bible" ] && montage $bible -tile 2x -geometry 960x540+6+6 -pointsize 22 -background '#2a2a2a' -fill white -title "$SET v4 set bible views" $O/v4_${SET}_bible.jpg && echo $O/v4_${SET}_bible.jpg
done

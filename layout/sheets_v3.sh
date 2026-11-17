#!/bin/sh
# v3 contact sheets (after `node layout/render.mjs --set <set> --prefix v3_` for the three sets):
#   media/layout/_sheets/v3_{attic88,bed26,car26}.jpg   label renders of the v3 setups
#   media/layout/_sheets/v3_neon_options.jpg            the blade sign: five placements x (A1 view, window zoom, lit, plan, from the mat)
#   media/layout/_sheets/v3_lap_parallel.jpg            the eight LAP setups, attic vs bedroom (flat + lit)
#   media/layout/_sheets/v3_hand_shadows.jpg            hand-shadow setups, label + lit
#   media/layout/_sheets/v3_J4_split_{line,flat,lit}.png + v3_J4_split.jpg   left half attic LAP_front, right half bedroom LAP_front
cd "$(dirname "$0")/.." || exit 1
M=media/layout; O=$M/_sheets; mkdir -p $O; T=$(mktemp -d)
sheet() { # sheet <set> <title> shots...
  SET=$1; TITLE=$2; shift 2; files=""
  for s in "$@"; do files="$files -label $s $M/$SET/v3_${s}_label.png"; done
  montage $files -tile 4x -geometry 600x338+6+6 -pointsize 24 -background '#2a2a2a' -fill white -title "$TITLE" $O/v3_$SET.jpg; echo $O/v3_$SET.jpg
}
sheet attic88 "attic88 layout v3 (label mode)" A1 A2 A3a A3b LAP_front LAP_34 LAP_ots LAP_ots_push_end LAP_child_cu LAP_mother_cu LAP_profile LAP_hands C2 G3 G4 F3b D9_a D9_b D9_c L2b L3 L3_off
sheet bed26 "bed26 layout v3 (label mode)" LAP_front LAP_34 LAP_ots LAP_ots_push_end LAP_child_cu LAP_mother_cu LAP_profile LAP_hands I2 I4b J1 L2
sheet car26 "car26 layout v3 (label mode): two child seats, she is rear right" F1 F2 F3a F4a F4b F5 F6a F6b

# neon options
A=$M/attic88; cols=""
for k in A B C D E; do
  case $k in
    A) cap="A  in front of the far third\nof the window  (RECOMMENDED)";;
    B) cap="B  in front of the near third\n(the mats' side)";;
    C) cap="C  beside the window, far side,\nclear of the glass";;
    D) cap="D  beside the window, mats' side,\nclear of the glass";;
    E) cap="E  as A, hung 0.6 m\nfurther out";;
  esac
  convert -background '#2a2a2a' -fill white -pointsize 22 -size 480x64 -gravity center label:"$cap" $T/cap_$k.png
  convert $A/v3_neonopt_${k}_flat.png -resize 480x $T/a_$k.png
  convert $A/v3_neonopt_${k}_line.png -crop 420x340+1330+630 +repage -resize 480x $T/b_$k.png
  convert $A/v3_neonopt_${k}_lit.png -crop 420x340+1330+630 +repage -resize 480x $T/b2_$k.png
  convert $A/v3_neonopt_${k}_lit.png -resize 480x $T/c_$k.png
  convert $A/v3_neonopt_${k}_plan_lit.png -resize 480x $T/d_$k.png
  convert $A/v3_neonopt_${k}_mat_label.png -resize 480x $T/e_$k.png
  convert $A/v3_neonopt_${k}_mat_lit.png -resize 480x $T/f_$k.png
  convert $T/cap_$k.png $T/a_$k.png $T/b_$k.png $T/b2_$k.png $T/c_$k.png $T/d_$k.png $T/e_$k.png $T/f_$k.png -background '#2a2a2a' -splice 0x6 -append $T/col_$k.png
  cols="$cols $T/col_$k.png"
done
rows=""; i=0
for t in " " "A1 / L3 wide (flat)" "the window in A1,\nzoomed (line guide)" "the window in A1,\nzoomed (lit)" "A1 / L3 wide (lit):\nhow the red rakes in" "plan from above, roof off:\nwhere the light lands\n(mats upper right)" "from the mat,\nlooking out (label)" "from the mat (lit)"; do
  h=270; [ $i = 0 ] && h=64; [ $i = 2 ] && h=389; [ $i = 3 ] && h=389
  if [ $i = 0 ]; then convert -size 200x$h xc:'#2a2a2a' $T/r_$i.png; else convert -background '#2a2a2a' -fill '#dddddd' -pointsize 18 -size 200x$h -gravity center label:"$t" $T/r_$i.png; fi; rows="$rows $T/r_$i.png"; i=$((i+1))
done
convert $rows -background '#2a2a2a' -splice 0x6 -append $T/rowcol.png
convert $T/rowcol.png $cols -background '#2a2a2a' -splice 6x0 +append -bordercolor '#2a2a2a' -border 10 -quality 88 $O/v3_neon_options.jpg; echo $O/v3_neon_options.jpg

# lap parallel
files=""
for s in LAP_front LAP_34 LAP_ots LAP_ots_push_end LAP_child_cu LAP_mother_cu LAP_profile LAP_hands; do
  files="$files -label attic88_$s $M/attic88/v3_${s}_flat.png -label bed26_$s $M/bed26/v3_${s}_flat.png -label attic88_${s}_(lit) $M/attic88/v3_${s}_lit.png -label bed26_${s}_(lit) $M/bed26/v3_${s}_lit.png"
done
montage $files -tile 4x -geometry 480x270+5+5 -pointsize 18 -background '#2a2a2a' -fill white -title "LAP storytime: the same eight setups in the attic (1988) and the bedroom (2026)" -quality 88 $O/v3_lap_parallel.jpg; echo $O/v3_lap_parallel.jpg

# hand shadows
files=""
for p in attic88:C2 attic88:G3 attic88:G4 bed26:I2 bed26:I4b bed26:J1; do s=${p#*:}; d=${p%%:*}
  files="$files -label ${d}_$s $M/$d/v3_${s}_label.png -label ${s}_(line_guide) $M/$d/v3_${s}_line.png -label ${s}_(lit) $M/$d/v3_${s}_lit.png"; done
montage $files -tile 3x -geometry 640x360+5+5 -pointsize 20 -background '#2a2a2a' -fill white -title "Hand shadows from the real light (attic: blade sign; bedroom: flashlight). Purple = computed shadow polygon" -quality 88 $O/v3_hand_shadows.jpg; echo $O/v3_hand_shadows.jpg

# J4 split screen preview: centre 960 px of each LAP_front
for m in line flat lit; do
  convert \( $M/attic88/v3_LAP_front_$m.png -crop 960x1080+480+0 +repage \) \( $M/bed26/v3_LAP_front_$m.png -crop 960x1080+480+0 +repage \) +append -fill white -draw "rectangle 958,0 961,1080" $O/v3_J4_split_$m.png
done
montage -label "J4_split (flat)" $O/v3_J4_split_flat.png -label "J4_split (lit)" $O/v3_J4_split_lit.png -label "J4_split (line guide)" $O/v3_J4_split_line.png -tile 3x -geometry 640x360+5+5 -pointsize 20 -background '#2a2a2a' -fill white -title "J4 split screen: attic LAP_front | bedroom LAP_front" -quality 90 $O/v3_J4_split.jpg; echo $O/v3_J4_split.jpg
rm -rf $T

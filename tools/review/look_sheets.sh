#!/bin/bash
# look_sheets.sh N  -> media/look/_sheets/L<N>.jpg  (labels: model_variant [+ coverage for L1-L3])
cd /home/jade/Documents/chaosmonkey-video
PY=/home/jade/Documents/halys-video/.venv/bin/python
n=$1; d=media/look/L$n; tmp=$(mktemp -d)
for f in $d/*.jpg; do
  s=$(basename $f .jpg); lab="$s"
  if [ $n -le 3 ]; then c=$($PY tools/review/coverage.py $f | grep -o 'cov= *[0-9.]*%' | tr -d ' '); lab="$s  $c"; fi
  convert $f -resize 900x -background '#222' -fill white -font DejaVu-Sans -pointsize 34 label:"$lab" -gravity center -append $tmp/$s.jpg
done
montage $tmp/*.jpg -geometry +8+8 -tile 3x -background '#222' media/look/_sheets/L$n.jpg
convert media/look/_sheets/L$n.jpg -resize '3000x>' -quality 85 media/look/_sheets/L$n.jpg
rm -r $tmp; identify media/look/_sheets/L$n.jpg

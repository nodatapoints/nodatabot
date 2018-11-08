#!/bin/zsh

# ja das geht auch mit bash.

working_dir=$(mktemp -d)
cd $working_dir

cat - > main.tex
if ! latexmk main.tex &>/dev/null; then
  echo "FAILED."
  exit 3
fi
if true; then
	DVI_SWITCH_FLAGS="-bg 'rgb 0 0 0' -fg 'rgb 1 1 1'"
	BORDERCOLOR=black
fi
dvipng -D 900 main.dvi $DVI_SWITCH_FLAGS &>/dev/null
convert	main*.png -bordercolor ${BORDERCOLOR-white} -border x20% -resize x500 main.png
echo $working_dir/main.png
